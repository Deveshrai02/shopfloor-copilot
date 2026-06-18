"""
Shopfloor Copilot — Evaluation harness.

Loads test_questions.json, runs each question through the agent, compares the
tool(s) actually called against the expected_tool, and writes a detailed report
to eval/results.json.

Usage:
    # from the project root, with venv active and MES API running on :8000:
    python -m eval.run_eval

    # or limit to a subset of IDs for quick iteration:
    python -m eval.run_eval --ids 1,2,9,17

Output:
    - Coloured summary table printed to stdout
    - eval/results.json  — machine-readable, referenced in README / resume
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is on sys.path when run as `python -m eval.run_eval`
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(_REPO_ROOT / ".env")

from app.agent import run_agent_traced  # noqa: E402

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_EVAL_DIR       = _REPO_ROOT / "eval"
_QUESTIONS_FILE = _EVAL_DIR / "test_questions.json"
_RESULTS_FILE   = _EVAL_DIR / "results.json"

# ---------------------------------------------------------------------------
# ANSI colours (degrade gracefully on non-TTY)
# ---------------------------------------------------------------------------

_IS_TTY = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _IS_TTY else text


GREEN  = lambda t: _c("32", t)
RED    = lambda t: _c("31", t)
YELLOW = lambda t: _c("33", t)
BOLD   = lambda t: _c("1",  t)
DIM    = lambda t: _c("2",  t)

# ---------------------------------------------------------------------------
# Tool-match logic
# ---------------------------------------------------------------------------

# "expected_tool" == "none" means we expect NO tool call at all.
# The agent may call multiple tools in one turn (e.g. retrieve_sop then
# get_live_line_data). We count a match when:
#   - expected is "none"  → tools_called must be empty
#   - expected is a name  → that name appears anywhere in tools_called

def _is_match(expected: str, tools_called: list[str]) -> bool:
    if expected == "none":
        return len(tools_called) == 0
    return expected in tools_called

# ---------------------------------------------------------------------------
# Category labels
# ---------------------------------------------------------------------------

_CATEGORY_LABELS = {
    "sop":          "SOP / Document",
    "live_data":    "Live MES Data",
    "ticket":       "Ticket Creation",
    "out_of_scope": "Out-of-Scope",
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_eval(question_ids: list[int] | None = None) -> None:
    questions = json.loads(_QUESTIONS_FILE.read_text())

    if question_ids:
        questions = [q for q in questions if q["id"] in question_ids]
        if not questions:
            print(RED(f"No questions matched IDs: {question_ids}"))
            sys.exit(1)

    total = len(questions)
    print(BOLD(f"\nShopfloor Copilot — Evaluation harness"))
    print(f"Running {total} questions  •  {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    print("-" * 80)

    results = []
    correct = 0
    category_stats: dict[str, dict] = {}

    for i, q in enumerate(questions, 1):
        qid       = q["id"]
        category  = q["category"]
        question  = q["question"]
        expected  = q["expected_tool"]
        hint      = q["correct_answer_should_reference"]

        cat_label = _CATEGORY_LABELS.get(category, category)
        if category not in category_stats:
            category_stats[category] = {"label": cat_label, "total": 0, "correct": 0}
        category_stats[category]["total"] += 1

        print(f"[{i:02d}/{total}] {DIM(f'#{qid} · {cat_label}')}")
        print(f"  Q: {question}")

        t0 = time.perf_counter()
        try:
            answer, tools_called = run_agent_traced(question)
            elapsed = time.perf_counter() - t0
            error = None
        except Exception as exc:
            elapsed = time.perf_counter() - t0
            answer = ""
            tools_called = []
            error = str(exc)

        match = _is_match(expected, tools_called)
        if match:
            correct += 1
            category_stats[category]["correct"] += 1
            status_str = GREEN("✓ PASS")
        else:
            status_str = RED("✗ FAIL")

        tools_str = ", ".join(tools_called) if tools_called else "none"
        exp_str   = expected

        print(f"  Tools called : {tools_str}")
        print(f"  Expected     : {exp_str}")
        print(f"  Result       : {status_str}  ({elapsed:.1f}s)")
        if error:
            print(f"  Error        : {RED(error)}")
        print()

        results.append({
            "id":           qid,
            "category":     category,
            "question":     question,
            "expected_tool": expected,
            "tools_called": tools_called,
            "match":        match,
            "answer":       answer,
            "hint":         hint,
            "elapsed_s":    round(elapsed, 2),
            "error":        error,
        })

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------

    accuracy = correct / total * 100

    print("=" * 80)
    print(BOLD("RESULTS SUMMARY"))
    print("=" * 80)
    print(f"  Overall tool-selection accuracy : {BOLD(f'{accuracy:.1f}%')}  ({correct}/{total})")
    print()
    print(f"  {'Category':<22}  {'Correct':>7}  {'Total':>5}  {'Accuracy':>9}")
    print(f"  {'-'*22}  {'-'*7}  {'-'*5}  {'-'*9}")
    for cat, s in category_stats.items():
        acc = s["correct"] / s["total"] * 100
        colour = GREEN if acc >= 80 else (YELLOW if acc >= 50 else RED)
        acc_str = colour(f"{acc:.0f}%")
        print(
            f"  {s['label']:<22}  {s['correct']:>7}  {s['total']:>5}  "
            f"{acc_str:>9}"
        )
    print("=" * 80)

    # -----------------------------------------------------------------------
    # Write results.json
    # -----------------------------------------------------------------------

    output = {
        "run_at":          datetime.now(timezone.utc).isoformat(),
        "model":           "claude-haiku-4-5",
        "total_questions": total,
        "correct":         correct,
        "accuracy_pct":    round(accuracy, 1),
        "category_breakdown": {
            cat: {
                "label":        s["label"],
                "correct":      s["correct"],
                "total":        s["total"],
                "accuracy_pct": round(s["correct"] / s["total"] * 100, 1),
            }
            for cat, s in category_stats.items()
        },
        "questions": results,
    }

    _RESULTS_FILE.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\n  Detailed results saved → {_RESULTS_FILE.relative_to(_REPO_ROOT)}")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Shopfloor Copilot eval")
    parser.add_argument(
        "--ids",
        help="Comma-separated question IDs to run (e.g. --ids 1,2,9). Runs all if omitted.",
        default=None,
    )
    args = parser.parse_args()

    ids = [int(x.strip()) for x in args.ids.split(",")] if args.ids else None
    run_eval(ids)
