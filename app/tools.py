

import json
import os

import httpx
from langchain_core.tools import tool

from app.rag import retrieve_simple

# In Docker Compose the MES API is reachable at http://mes-api:8000.
# Locally it runs on localhost. MES_BASE_URL env var lets docker-compose.yml
# override the default without touching code.
_MES_BASE = os.getenv("MES_BASE_URL", "http://localhost:8000")


@tool
def retrieve_sop(query: str) -> str:
    """
    Search the manufacturing SOP knowledge base for procedures, escalation criteria,
    and role responsibilities. Use this whenever the operator's question relates to
    how something should be done, who is responsible, or what the escalation path is.

    Args:
        query: A natural-language description of the procedure or policy to look up.

    Returns:
        Up to three relevant SOP excerpts with source document names and similarity scores.
    """
    results = retrieve_simple(query, k=3)
    if not results:
        return "No relevant SOP content found for that query."

    lines = []
    for i, r in enumerate(results, 1):
        lines.append(
            f"[{i}] Source: {r.source}  (score={r.score:.3f})\n{r.text}"
        )
    return "\n\n---\n\n".join(lines)


@tool
def get_live_line_data(line_id: str, data_type: str) -> str:
    """
    Fetch live production data for a specific manufacturing line from the MES system.
    Use this when the question concerns current performance, recent quality defects,
    or recent downtime events on a named line.

    Args:
        line_id:   The production line identifier, e.g. "FA-01", "TRIM-02", "EV-BAT".
        data_type: One of "oee", "quality", or "downtime".
                   - "oee"      → Overall Equipment Effectiveness and sub-metrics
                   - "quality"  → Defect counts and pass rate for the current shift
                   - "downtime" → Downtime events in the last 24 hours

    Returns:
        A JSON string with the requested metrics, or an error message if the request fails.
    """
    valid_types = {"oee", "quality", "downtime"}
    if data_type not in valid_types:
        return (
            f"Invalid data_type '{data_type}'. "
            f"Must be one of: {', '.join(sorted(valid_types))}."
        )

    url = f"{_MES_BASE}/{data_type}/{line_id}"
    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2, default=str)
    except httpx.HTTPStatusError as exc:
        try:
            detail = exc.response.json().get("detail", exc.response.text)
        except Exception:
            detail = exc.response.text
        return f"MES API error {exc.response.status_code}: {detail}"
    except httpx.RequestError as exc:
        return (
            f"Could not reach the MES API at {_MES_BASE}. "
            f"Is mock_mes_api.py running? Error: {exc}"
        )


@tool
def create_incident_ticket(
    line_id: str,
    issue_description: str,
    severity: str,
) -> str:
    """
    Raise a maintenance or quality incident ticket for a production line in the MES system.
    Only call this when the operator explicitly asks to raise a ticket, or when an issue
    clearly requires formal escalation (e.g. safety risk, extended unplanned downtime).

    Args:
        line_id:           The production line ID, e.g. "FA-01", "TRIM-02", "EV-BAT".
        issue_description: A clear description of the issue (10-1000 characters).
        severity:          One of "low", "medium", or "high".

    Returns:
        A summary of the created ticket including the ticket ID and status,
        or an error message if creation fails.
    """
    valid_severities = {"low", "medium", "high"}
    if severity not in valid_severities:
        return (
            f"Invalid severity '{severity}'. "
            f"Must be one of: {', '.join(sorted(valid_severities))}."
        )

    payload = {
        "line_id": line_id,
        "issue_description": issue_description,
        "severity": severity,
    }
    url = f"{_MES_BASE}/tickets"
    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        ticket = response.json()
        return (
            f"Ticket raised successfully.\n"
            f"  Ticket ID : {ticket['ticket_id']}\n"
            f"  Line      : {ticket['line_id']}\n"
            f"  Severity  : {ticket['severity']}\n"
            f"  Status    : {ticket['status']}\n"
            f"  Created   : {ticket['created_at']}\n"
            f"  Issue     : {ticket['issue_description']}"
        )
    except httpx.HTTPStatusError as exc:
        try:
            detail = exc.response.json().get("detail", exc.response.text)
        except Exception:
            detail = exc.response.text
        return f"MES API error {exc.response.status_code}: {detail}"
    except httpx.RequestError as exc:
        return (
            f"Could not reach the MES API at {_MES_BASE}. "
            f"Is mock_mes_api.py running? Error: {exc}"
        )


# Exported list — used in agent.py when binding tools to the model
ALL_TOOLS = [retrieve_sop, get_live_line_data, create_incident_ticket]


if __name__ == "__main__":
    # Quick smoke-test for each tool (requires mock_mes_api.py running on :8000
    # and the FAISS index already built via `python -m app.rag`).
    print("=" * 60)
    print("Tool smoke-test")
    print("=" * 60)

    print("\n[1] retrieve_sop — HV battery handling")
    print(retrieve_sop.invoke({"query": "steps before handling a high-voltage battery pack"}))

    print("\n[2] get_live_line_data — FA-01 OEE")
    print(get_live_line_data.invoke({"line_id": "FA-01", "data_type": "oee"}))

    print("\n[3] create_incident_ticket — test ticket")
    print(create_incident_ticket.invoke({
        "line_id": "TRIM-01",
        "issue_description": "Repeated clip engagement failures detected on the door trim station.",
        "severity": "medium",
    }))
