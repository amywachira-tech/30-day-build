# Portfolio Artifact #1: AI-Enabled Revenue Workflow (VOYGR-Anchored)

An end-to-end solution-design cycle applied to a real, named company's stated problem: VOYGR, a location/POI data validation and enrichment company selling across 11 verticals with no structured sales system behind its outbound motion.

This isn't a generic "GTM automation" demo. It follows one real diagnosis through to a working, deployed system: two mock discovery conversations, a full requirements document, a scored architecture, a security pass, an ROI estimate, a build, a deployment, and an honest accounting of what did and didn't get finished in the time available.

## What's in this repo

- **`portfolio/VOYGR_Requirements_Doc.md`** — the full artifact. Ten sections: Problem, Requirements, Architecture, Security, ROI, Build Notes, Deployment, Result, Limitations, and Next Iteration, plus the Friday tradeoff analysis (why sentiment tagging is AI and tier-scoring isn't).
- **`portfolio/voygr_pipeline_architecture.png`** — the pipeline diagram, eleven stages color-coded by category: rule-based automation, AI judgment, or human action.
- **`clay/`** — the Clay tables: enrichment, rule-based tier scoring, and the scoped AI personalization/sentiment columns (Days 11-12).
- **`n8n/`** — exported n8n workflows: branching and error handling (Day 10), the Clay-to-n8n webhook integration (Day 13), and the database-write pipeline (Day 16-17).
- **`Database/`** — the SQLite schema and scripts (`setup_db.py`, `insert_record.py`), the Flask API wrapper deployed to Render (`api_server.py`), and the pipeline log.

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
