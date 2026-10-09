# Artifact 1: AI-Enabled Revenue Workflow (VOYGR)

An end-to-end solution design applied to the stated problem of a real company: VOYGR, a location and POI data validation and enrichment company selling across 11 verticals with no structured sales system behind its outbound motion.

The work follows one diagnosis through to a deployed system: two mock discovery conversations, a requirements document, a scored architecture, a security review, an ROI estimate, a build, a deployment, and a record of what was and was not finished.

## The system

```
Lead → Clay enrichment → AI-drafted personalization → human confirms →
send → reply arrives → AI suggests sentiment → human confirms →
call logged → data written to database
```

Each step is classified as rule-based automation, AI judgment, or a required human checkpoint. Where a fixed rule does the job (enrichment, tier scoring), a rule is used. Where judgment on unstructured text is required (personalization drafts, reply sentiment), AI makes the first pass and a person confirms it.

## What was built and tested

- A Flask API over a SQLite database, deployed to Render, tested with deliberately malformed input and confirmed to recover.
- An n8n cloud workflow that writes records to the deployed API. Five test records, spanning five verticals, were pushed through the n8n to Render to database chain, each returning a new, correctly incrementing ID.
- A Claude reply-sentiment classifier evaluated on 15 independently labelled replies: **13 of 15 correct**, after the label set was redesigned from three tags to four.

## A real build failure

The original plan had n8n call a local Python script through an Execute Command node. Testing showed n8n's cloud tier does not allow local shell execution at all. The fix was an HTTP bridge to the deployed API, which is what runs today. Section 5 of the requirements document records this as it happened.

## Not finished

- The full chain from Clay to the database write has not been run as one unbroken pass; each segment was proven separately.
- The database sits on Render's free, ephemeral disk and does not survive a restart.
- The end-to-end test used 5 records instead of the planned 20 to 30, a deliberate time trade-off.
- The API endpoint has no authentication.

## Files

| File | Contents |
|---|---|
| `VOYGR_Requirements_Doc.md` | The full write-up in ten sections: requirements, architecture, security, ROI, build notes, deployment, result, limitations, next iteration, and the Friday tradeoff question |
| `voygr_pipeline_architecture.png` | Pipeline diagram, each stage marked as rule-based, AI judgment or human action |
| `sentiment_classifier.py`, `run_eval.py` | The classifier and its evaluation script |
| `eval_set.json`, `eval_results.json` | The 15 labelled replies and the measured results |

Supporting work lives at the repository root: `Database/` (SQLite scripts and the deployed Flask API), `n8n/` (exported workflows from Days 9 and 10) and `Clay/` (a screenshot of the Day 11 enrichment table).

## Running the evaluation

```
cd Portfolio/artifact1
python run_eval.py
```

Requires an `ANTHROPIC_API_KEY` environment variable.
