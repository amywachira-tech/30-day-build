"""
run_eval.py
Runs the labeled eval set through answer.py and scores it.

    python run_eval.py          # eval set, writes eval_results.json and .csv
    python run_eval.py --dev    # dev questions only: prints top similarity
                                # scores for setting SIM_FLOOR

All runs use the fixed date in eval_set.json, so the temporary freight
announcement is in force however late the eval is re-run.

Scored automatically, each as a separate metric:
  - retrieval: an expected source appears among the retrieved chunks
  - outcome:   the system outcome matches the expected outcome
  - citation:  for answers, the cited source is one of the expected sources
  - flags:     for ANSWER_WITH_FLAG, every expected outdated source is flagged
  - access:    no lead-only or forbidden chunk was retrieved for an agent
Answer correctness is judged by hand: fill in the answer_correct column.
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

from answer import answer
from search import search, load_index

EVAL_FILE = Path("eval_set.json")
RESULTS_JSON = Path("eval_results.json")
RESULTS_CSV = Path("eval_results.csv")


def source_of(chunk_id):
    return chunk_id.split("-")[0]


def run_dev(cases, as_of):
    print("Top similarity score per dev question (use these to set SIM_FLOOR):")
    for case in cases:
        results = search(case["question"], case["role"], top_k=3, as_of=as_of)
        top = results[0]
        print(f'{case["id"]:3} expected {case["expected_outcome"]:9} '
              f'top {top[0]:.3f} ({top[1]["chunk_id"]})  {case["question"]}')


def score(case, result, lead_chunks):
    retrieved = result["retrieved"]
    retrieved_sources = {source_of(c) for c in retrieved}
    expected = case["expected_outcome"]
    outcome = result["outcome"]

    # BLOCKED means the system must decline: in practice, ASK_LEAD.
    outcome_ok = outcome == ("ASK_LEAD" if expected == "BLOCKED" else expected)

    retrieval_ok = (None if not case["expected_sources"]
                    else bool(retrieved_sources & set(case["expected_sources"])))

    citation_ok = None
    if expected in ("ANSWER", "ANSWER_WITH_FLAG") and outcome != "ASK_LEAD":
        citation_ok = result["source_id"] in case["expected_sources"]

    flags_ok = None
    if expected == "ANSWER_WITH_FLAG":
        flagged = {f["source_id"] for f in result["flags"]}
        flags_ok = set(case["expected_flags"]) <= flagged

    leaked = [c for c in retrieved
              if c in case["forbidden_chunks"]
              or (case["role"] == "agent" and c in lead_chunks)]

    return {"outcome_ok": outcome_ok, "retrieval_ok": retrieval_ok,
            "citation_ok": citation_ok, "flags_ok": flags_ok,
            "access_ok": not leaked, "leaked": leaked}


def tally(rows, key):
    vals = [r[key] for r in rows if r[key] is not None]
    return f"{sum(vals)}/{len(vals)}"


def main():
    data = json.loads(EVAL_FILE.read_text(encoding="utf-8"))
    as_of = date.fromisoformat(data["as_of"])

    if "--dev" in sys.argv:
        run_dev(data["dev"], as_of)
        return

    chunks, _ = load_index()
    lead_chunks = {c["chunk_id"] for c in chunks if c["access_level"] == "lead"}

    rows = []
    for case in data["eval"]:
        result = answer(case["question"], case["role"], as_of=as_of)
        s = score(case, result, lead_chunks)
        rows.append({"id": case["id"], "role": case["role"],
                     "question": case["question"],
                     "expected_outcome": case["expected_outcome"],
                     "outcome": result["outcome"],
                     "answer": result["answer"] or result["reason"],
                     "cited": result["source_id"],
                     "flagged": [f["source_id"] for f in result["flags"]],
                     "retrieved": result["retrieved"],
                     "correct_answer": case["correct_answer"],
                     **s, "answer_correct": ""})
        mark = "PASS" if s["outcome_ok"] and s["access_ok"] else "FAIL"
        print(f'{case["id"]:>2} {mark}  expected {case["expected_outcome"]:16} '
              f'got {result["outcome"]:16} cited {result["source_id"]}')

    RESULTS_JSON.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print()
    print(f"Outcome match:      {tally(rows, 'outcome_ok')}")
    print(f"Retrieval accuracy: {tally(rows, 'retrieval_ok')}")
    print(f"Citation correct:   {tally(rows, 'citation_ok')}")
    print(f"Flags correct:      {tally(rows, 'flags_ok')}")
    print(f"Access (no leaks):  {tally(rows, 'access_ok')}")
    unsafe = sum(1 for r in rows if r["expected_outcome"] in ("ASK_LEAD", "BLOCKED")
                 and r["outcome"] != "ASK_LEAD")
    print(f"Unsafe answers:     {unsafe}")
    print(f"\nFill in answer_correct in {RESULTS_CSV} by hand.")


if __name__ == "__main__":
    main()
