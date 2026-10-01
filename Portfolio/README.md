# Portfolio Artifact #1: AI-Enabled Revenue Workflow (VOYGR-Anchored)

An end-to-end solution-design cycle applied to a real, named company's stated problem: VOYGR, a location/POI data validation and enrichment company selling across 11 verticals with no structured sales system behind its outbound motion.

This isn't a generic "GTM automation" demo. It follows one real diagnosis through to a working, deployed system: two mock discovery conversations, a full requirements document, a scored architecture, a security pass, an ROI estimate, a build, a deployment, and an honest accounting of what did and didn't get finished in the time available.

## What's in this repo

- **`portfolio/VOYGR_Requirements_Doc.md`** — the full artifact. Ten sections: Problem, Requirements, Architecture, Security, ROI, Build Notes, Deployment, Result, Limitations, and Next Iteration, plus the Friday tradeoff analysis (why sentiment tagging is AI and tier-scoring isn't).
- **`portfolio/voygr_pipeline_architecture.png`** — the pipeline diagram, eleven stages color-coded by category: rule-based automation, AI judgment, or human action.
- **`clay/`** — the Clay tables: enrichment, rule-based tier scoring, and the scoped AI personalization/sentiment columns (Days 11-12).
- **`n8n/`** — exported n8n workflows: branching and error handling (Day 10), the Clay-to-n8n webhook integration (Day 13), and the database-write pipeline (Day 16-17).
- **`Database/`** — the SQLite schema and scripts (`setup_db.py`, `insert_record.py`), the Flask API wrapper deployed to Render (`api_server.py`), and the pipeline log.
- **`sentiment_classifier.py`, `eval_set.json`, `eval_results.json`, `run_eval.py`** — the labeled evaluation behind the 86.7% (13/15) sentiment-tagging accuracy figure cited in the requirements doc: independently written test cases, measured output, categorized errors.

## The system, in short

```
Lead → Clay enrichment → AI-drafted personalization → human confirms →
send → reply arrives → AI suggests sentiment → human confirms →
call logged → data written to database
```

Every step is explicitly categorized as rule-based automation, genuine AI judgment, or a required human checkpoint, not by default, but by asking at each step whether a fixed rule could do the job just as well. Where it could (enrichment, tier scoring), it does. Where real judgment on unstructured text is required (personalization drafting, sentiment interpretation), AI does the first pass and a human confirms before anything is treated as final.

## What's actually running

- The Clay enrichment and scoring pipeline: built and tested.
- The n8n branching, error-handling, and database-write workflow: built and tested.
- A live database-write API, deployed to Render (`https://three0-day-build.onrender.com`), tested with a deliberate break (malformed input) and confirmed recovery.
- Five end-to-end test records pushed through the full n8n-to-Render-to-database chain, spanning five different verticals.

## What's honestly not finished

Documented in full in the artifact's Limitations section, in short: the database is on Render's free ephemeral disk (won't survive a restart), the full chain hasn't been run as one single unbroken pass from Clay through to the database write, and the sample size was deliberately trimmed from 20-30 records to 5 given a compressed week, a stated trade-off, not a hidden one.

## A real build failure, documented as it happened

The original plan assumed n8n could call a local Python script directly via an Execute Command node. Testing that assumption directly showed n8n's cloud tier doesn't support local shell execution at all, a deliberate security boundary, not a bug. The fix, an HTTP-based bridge instead of a local command, is documented in the artifact's Build Notes section and is what's actually deployed and running today.
---

# Portfolio Artifact #2: Generalized Call-Scoring System

A generalized B2B sales call-scoring system, built from fictional transcripts written for this exercise, not any real company's proprietary call data or scoring methodology. A transcript goes in, a Claude API call scores it across six defined dimensions plus an overall outcome, and returns structured JSON.

**The strongest evidence in this artifact is the failure case, not the success rate.** A hypothesized systematic leniency bias, found while building ground-truth labels, was tested twice with independently designed adversarial transcripts. Both replication attempts failed to reproduce the bias. Revisiting the original mismatches under real scrutiny found only one genuine, checkable defect, not a broad pattern, a narrower and more honest claim than the one the investigation started with. Full detail in `PORTFOLIO_ARTIFACT_2_WRITEUP.md`.

## What's in this repo

- **`PORTFOLIO_ARTIFACT_2_WRITEUP.md`** — the full write-up, leading with the failure-case investigation.
- **`call_scorer.py`** — the scoring script: one function per transcript call, structured JSON output, defensive markdown-fence stripping, empty-input guard.
- **`transcript_1_clean_close.txt`** through **`transcript_5_adversarial2_CLEAN.txt`** — five fictional call transcripts spanning a clean close, a clean loss, an ambiguous stall, and two adversarial rounds.
- **`ground_truth.json`** — independently reasoned labels, written before comparing to model output.
- **`scoring_results.json`** — the scorer's actual output against all five transcripts.

## Result

13/18 dimension-level agreement (72%) against independent ground truth, 3/3 overall-outcome agreement. Four of five mismatches were genuine, checkable defects, not subjective disagreements, concentrated specifically on `trust_framing_placement` and `decision_maker_path`. Two independently designed adversarial tests, built to deliberately trigger the same pattern, both failed to reproduce it, a real finding about the limits of synthetic red-teaming against a bias that's actually present in ordinary data.