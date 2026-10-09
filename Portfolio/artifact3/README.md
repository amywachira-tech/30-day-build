# Artifact 3: Policy Retrieval for Support Agents

A retrieval system that answers customer-support agents' policy questions from internal documents. It cites the most authoritative current source, flags outdated sources, and refers the agent to a lead when the evidence is weak or contradictory.

Built for a fictional retailer, Kestrel Home, from a two-call discovery roleplay with its Head of Customer Support, on an 18-source synthetic policy corpus. The client's problem: contradictory, unmaintained policy documents had led to about $18,000 in refunds not owed and a privacy incident in which an agent followed an outdated identity-verification procedure.

## Lead finding

The system answered an identity-verification question correctly, but did not flag the outdated FAQ behind the client's privacy incident. Chunking had separated that FAQ's verification rule from what it allowed agents to share, and search retrieved only the second part. The fix is to keep dependent sections of a Q&A document together, or to retrieve neighbouring chunks from the same source.

## How it works

1. **Chunk** (`chunk.py`): splits each source on access-level markers first, so no chunk mixes agent and lead content. Stops with an error if unmarked text could leak into a document with lead sections.
2. **Embed** (`index.py`): local embeddings with sentence-transformers, so policy text never leaves the client's environment.
3. **Search** (`search.py`): removes chunks the user's role may not see, and expired announcements, before searching.
4. **Answer** (`answer.py`): a similarity floor; Claude reports what each source says with an exact quote; code verifies every quote word for word; code applies the conflict rule (announcement over handbook over Google Doc, later announcement over earlier).

## Results (12 labelled questions, single run)

| Metric | Result |
|---|---|
| Access leaks | 0 |
| Unsafe answers | 0 |
| Retrieval | 9 of 9 |
| Answers correct | 8 of 9 answered questions correct as run |
| Questions correctly referred to a lead | 3 of 3 |
| Outcome match | 10 of 12 as run; 11 of 12 after one label correction |

The one wrong answer came from a prompt that assumed every user was an agent. It was fixed and verified on a single rerun. Corrections are reported separately from the as-run results.

## Files

| File | Contents |
|---|---|
| `ARTIFACT_3_WRITEUP.md` | Full write-up: problem, design decisions, evaluation, findings, limitations, tradeoff question, expansion plan and cost estimate |
| `artifact3_requirements.md` | Requirements document from discovery |
| `corpus_plan.md`, `corpus/` | Corpus design with the ground-truth facts, and the 18 source files |
| `chunk.py`, `index.py`, `search.py`, `answer.py` | The pipeline |
| `run_eval.py`, `eval_set.json` | Evaluation runner, 12 eval questions and 4 development questions |
| `eval_results.json`, `eval_results.csv` | Results of the run |
| `Retrieval_Eval.xlsx`, `Answer_Review.xlsx` | The eval set and the hand-labelled answer review |

## Running it

```
cd Portfolio/artifact3
pip install pyyaml sentence-transformers anthropic
python chunk.py
python index.py
python answer.py agent "cust bought sofa on sale 5 wks ago wants return, ok?"
python run_eval.py
```

`answer.py` and `run_eval.py` require an `ANTHROPIC_API_KEY` environment variable.
