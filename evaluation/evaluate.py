"""Before/after evaluation of the tutor's system prompts.

Compares two responses for each test case:
  - BEFORE: the raw model with no system prompt (no tutoring instruction)
  - AFTER:  the model with our mode-specific system prompt from tutor/modes.py

Each response is scored with BERTScore F1 — its semantic similarity to a
gold-standard reference answer. Scores are baseline-rescaled so unrelated
text sits near 0. A higher AFTER score shows the prompt engineering moves
responses closer to ideal tutoring answers.

Run from the project root:  python -m evaluation.evaluate
This makes real API calls (2 per test case) and needs ANTHROPIC_API_KEY set.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tutor.client import MODEL, TutorAPIError, chat
from tutor.modes import MODES
from tutor.tokens import calculate_cost, format_cost, format_tokens
from evaluation.dataset import TEST_CASES

# bert-base-uncased keeps the one-time model download to ~440MB.
# Swap to "roberta-large" for the highest-fidelity BERTScore.
BERTSCORE_MODEL = "bert-base-uncased"
RESULTS_PATH = Path(__file__).resolve().parent / "results.md"


def _generate_responses() -> tuple[list[dict], list[tuple[str, str]], int, int]:
    """Query the model with and without system prompts for every test case."""
    results: list[dict] = []
    errors: list[tuple[str, str]] = []
    total_input = total_output = 0

    for case in TEST_CASES:
        messages = [{"role": "user", "content": case["prompt"]}]
        print(f"  {case['id']} ...", flush=True)
        try:
            before, b_in, b_out = chat(system_prompt=None, messages=messages)
            after, a_in, a_out = chat(system_prompt=MODES[case["mode"]], messages=messages)
        except TutorAPIError as e:
            print(f"    skipped — {e}")
            errors.append((case["id"], str(e)))
            continue
        total_input += b_in + a_in
        total_output += b_out + a_out
        results.append({"case": case, "before": before, "after": after})

    return results, errors, total_input, total_output


def _build_report(results: list[dict], before_f1, after_f1) -> tuple[str, dict]:
    """Build the per-case markdown table and compute summary averages."""
    lines = [
        "| Test case | Mode | BERTScore before | BERTScore after |",
        "|---|---|---|---|",
    ]
    sums = {"bf": 0.0, "af": 0.0}

    for i, item in enumerate(results):
        case = item["case"]
        bf = before_f1[i].item()
        af = after_f1[i].item()
        sums["bf"] += bf
        sums["af"] += af
        lines.append(f"| {case['id']} | {case['mode']} | {bf:.3f} | {af:.3f} |")

    n = len(results)
    avg = {k: v / n for k, v in sums.items()}
    lines.append(f"| **Average** | | **{avg['bf']:.3f}** | **{avg['af']:.3f}** |")
    return "\n".join(lines), avg


def run() -> None:
    try:
        from bert_score import score as bert_score
    except ImportError:
        print("bert-score is not installed.")
        print("Install evaluation dependencies:  pip install -r requirements-eval.txt")
        sys.exit(1)

    print(f"Evaluating {len(TEST_CASES)} test cases (2 API calls each)...")
    results, errors, total_input, total_output = _generate_responses()

    if not results:
        print("\nNo responses were produced — every case errored. Fix the issue and re-run.")
        sys.exit(1)

    references = [item["case"]["reference"] for item in results]
    before_texts = [item["before"] for item in results]
    after_texts = [item["after"] for item in results]

    print(f"\nScoring with BERTScore ({BERTSCORE_MODEL}) — first run downloads the model...")
    # rescale_with_baseline rebases scores so unrelated text sits near 0, making
    # the numbers human-readable; lang is required for the baseline lookup.
    _, _, before_f1 = bert_score(
        before_texts, references, model_type=BERTSCORE_MODEL,
        lang="en", rescale_with_baseline=True, verbose=False,
    )
    _, _, after_f1 = bert_score(
        after_texts, references, model_type=BERTSCORE_MODEL,
        lang="en", rescale_with_baseline=True, verbose=False,
    )

    table, avg = _build_report(results, before_f1, after_f1)
    total_cost = calculate_cost(total_input, total_output)

    summary = [
        "# Evaluation Results — Before vs. After System Prompts",
        "",
        f"Model: `{MODEL}` | "
        f"BERTScore model: `{BERTSCORE_MODEL}` | Test cases scored: {len(results)}",
        "",
        table,
        "",
        "## Summary",
        "",
        f"- **BERTScore F1:** {avg['bf']:.3f} -> {avg['af']:.3f} "
        f"(+{avg['af'] - avg['bf']:.3f})",
        f"- **Evaluation cost:** {format_tokens(total_input + total_output)} tokens, "
        f"{format_cost(total_cost)}",
        "",
        "The AFTER column uses the tutoring system prompts; the BEFORE column is the "
        "raw model with no instructions. Scores are baseline-rescaled, so unrelated "
        "text sits near 0. The BERTScore gain shows the prompt engineering moves "
        "responses closer to ideal tutoring answers.",
    ]
    if errors:
        summary.append("")
        summary.append("## Skipped cases")
        summary.append("")
        for case_id, message in errors:
            summary.append(f"- `{case_id}`: {message}")

    report = "\n".join(summary) + "\n"
    RESULTS_PATH.write_text(report, encoding="utf-8")

    print()
    print(report)
    print(f"Saved to {RESULTS_PATH}")


if __name__ == "__main__":
    run()
