

from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.tools import ALL_TOOLS

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """You are Shopfloor Copilot, an AI assistant for automotive manufacturing \
plant operators and team leaders. You have access to two information sources:

1. SOP Knowledge Base — standard operating procedures covering changeover, quality holds, \
line stoppages, torque verification, EV battery handling, and end-of-shift reconciliation. \
Always search this first when a question involves a procedure, escalation path, or role \
responsibility.

2. Live MES Data — real-time OEE, quality, and downtime metrics for production lines \
(TRIM-01, TRIM-02, FA-01, FA-02, EV-BAT). Fetch this when the operator asks about current \
performance or recent events on a specific line.

You can also raise incident tickets when the operator explicitly requests it or when an \
issue clearly meets escalation criteria defined in the SOPs (e.g. downtime > 15 minutes, \
containment scope > 20 units, consecutive first-off failures).

Guidelines:
- Be concise and action-oriented — operators are on the shop floor and need quick answers.
- When quoting SOP escalation thresholds or role names, be precise.
- If you retrieve SOP content, cite the source document name.
- If live data shows a metric outside normal range, note it and suggest the relevant SOP.
- Never guess at procedures — always retrieve from the SOP knowledge base first.
- If you cannot find relevant information, say so clearly rather than speculating."""

# ---------------------------------------------------------------------------
# Model and tools
# ---------------------------------------------------------------------------

_model = ChatAnthropic(model="claude-haiku-4-5")
_model_with_tools = _model.bind_tools(ALL_TOOLS)

# ---------------------------------------------------------------------------
# Graph nodes
# ---------------------------------------------------------------------------


def _agent_node(state: MessagesState) -> dict:
    """
    Call the LLM with the current message history.

    The system message is prepended on every call so it is always in context.
    MessagesState's "messages" list holds the full conversation; LangGraph
    passes it in and merges our returned dict back automatically.
    """
    messages = [SystemMessage(content=_SYSTEM_PROMPT)] + state["messages"]
    response = _model_with_tools.invoke(messages)
    return {"messages": [response]}


_tools_node = ToolNode(ALL_TOOLS)

# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

_builder = StateGraph(MessagesState)

_builder.add_node("agent", _agent_node)
_builder.add_node("tools", _tools_node)

_builder.set_entry_point("agent")

# tools_condition checks the last message:
#   - if it contains tool_calls → route to "tools"
#   - otherwise → END
_builder.add_conditional_edges("agent", tools_condition)

# After tools execute, always go back to the agent so it can process results
_builder.add_edge("tools", "agent")

_graph = _builder.compile()

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_agent(user_message: str) -> str:
    """
    Run the agent on a single user message and return the final text response.

    The graph starts with the user message, may call tools zero or more times,
    and terminates when the agent produces a response with no tool calls.

    Args:
        user_message: The operator's natural-language question or request.

    Returns:
        The agent's final plain-text answer as a string.
    """
    initial_state = {"messages": [HumanMessage(content=user_message)]}
    final_state = _graph.invoke(initial_state)

    # The last message in the state is the agent's final AIMessage
    last_message = final_state["messages"][-1]
    return last_message.content


# ---------------------------------------------------------------------------
# CLI test harness — run with: python -m app.agent
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_queries = [
        "What's the current OEE on FA-01?",
        "FA-01 has been down for 20 minutes. What should I do and who do I need to notify?",
        "We've found 25 suspect units on TRIM-02. What containment steps are required?",
        "Please raise a high severity ticket for EV-BAT — HV connector not seating correctly on 3 consecutive units.",
    ]

    print("=" * 70)
    print("Shopfloor Copilot — Agent test run")
    print("=" * 70)
    print("(Requires mock_mes_api.py running on :8000 and FAISS index built)\n")

    for i, query in enumerate(test_queries, 1):
        print(f"[{i}/{len(test_queries)}] Q: {query}")
        print("-" * 70)
        answer = run_agent(query)
        print(f"A: {answer}")
        print("=" * 70 + "\n")
