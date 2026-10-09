# AI Workflow Portfolio

Three AI-enabled systems built in Python, covering APIs, SQL, workflow automation and applied AI. Each has working code, a labelled evaluation, and a written account of what failed and why.

## Portfolio

| # | Artifact | What it does | Evaluation |
|---|---|---|---|
| 1 | [AI-enabled revenue workflow](Portfolio/artifact1/) | Case study: an outbound sales workflow designed around VOYGR, a location-data company selling across 11 verticals. Clay enrichment, n8n automation, and a Flask API over SQLite deployed on Render, with human checkpoints on every AI step. | Claude reply-sentiment classifier: 13 of 15 correct on a labelled set |
| 2 | [Call-scoring system](Portfolio/artifact2/) | Scores B2B sales-call transcripts on six dimensions with the Claude API and returns structured JSON. | 13 of 18 dimension ratings matched independent labels; 4 of the 5 mismatches traced to a leniency pattern |
| 3 | [Policy retrieval for support agents](Portfolio/artifact3/) | Answers support agents' policy questions from internal documents, with permission filtering, source-conflict rules and verified citations. | 12 labelled questions: 0 access leaks, 0 unsafe answers; 8 of 9 answers correct as run, and the other 3 correctly referred to a lead |

Start with any artifact's README. Each one links to its full write-up.

## Repository layout

| Path | Contents |
|---|---|
| `Portfolio/` | The three artifacts, one folder each |
| `Database/` | SQLite scripts and the Flask API deployed to Render for Artifact 1 |
| `n8n/` | Exported n8n workflows: a basic workflow, and branching with error handling |
| `Clay/` | Screenshot of a Clay enrichment table |
| `Groundwork/` | Python, JSON, SQL and API groundwork, including a Claude tool-calling agent loop |
