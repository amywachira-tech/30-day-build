# Portfolio Artifact #1: AI-Enabled Revenue Workflow (VOYGR-Anchored)
## Section 1: Requirements Document

---

### Problem Statement

VOYGR is testing outbound sales of real-time place intelligence data across 11 distinct verticals (finance/insurance, retail, real estate, logistics, telecom, climate, and others) with no structured sales system underneath it. The team sends roughly 200 emails per week but captures no structured data on replies or calls. A CRM was adopted once and abandoned within weeks due to manual data-entry overhead. The team is a single SDR plus the founder, with no backup coverage.

### Stakeholders & Impact

- **The SDR** manages prospecting, outreach, calls, and follow-up alone, with no assistance and no backup when unavailable.
- **The founder and team** cannot see which verticals, messages, or approaches are actually working, decisions are made on instinct rather than data.

### Current-State Process

The SDR manually researches prospects, writes outreach (a shared base template with light manual tweaks), handles calls, and follows up, all unaided. Roughly 200 emails go out weekly across all 11 verticals combined, using a purchased contact list that was not built with VOYGR's specific buyer profile in mind.

### Root Cause / Actual Bottleneck

Useful signal from calls and email replies dies in the SDR's memory instead of being captured anywhere structured. There is no vertical-level performance data feeding back into targeting decisions, meaning the team cannot tell which of the 11 verticals are actually worth pursuing versus which are a poor fit.

### Proposed AI Scope

**In scope, AI-assisted:**
- Persona-level personalization drafting, to reduce the SDR's manual research time per lead.
- Suggesting a sentiment tag (positive/neutral/negative) on email replies, based on message content.
- Auto-enriching lead information at list-build time.

**Explicitly out of scope for AI:**
- Generating insights or recommendations on messaging strategy changes.
- Sending messages on the SDR's behalf.
- Auto-tagging positive replies and advancing them to next steps without confirmation.
- Filling deal information or pipeline progress directly.

### Data Requirements

- LinkedIn company/contact pages (enrichment input)
- Call notes (currently uncaptured, needs a structured entry point)
- Email reply log
- The existing purchased contact list

### Systems That Need to Connect

- **Enrichment tool (Clay)**: for list-building and lead data enrichment.
- **Sales engagement/sequencing platform** (e.g. Instantly or Smartlead): for sending, and for auto-tracking sends, opens, and replies; this is a distinct system from Clay, not the same tool.
- **Call notes capture**: a lightweight entry point for the SDR, not a full transcription tool at current volume.
- **Central log/database**: where enrichment, reply sentiment, and call notes converge into one place per account, replacing the failed CRM's role without recreating its manual burden.

### Where a Human Must Intervene

- Filling in call notes and sales pipeline progress.
- Making the actual calls.
- Confirming AI-suggested sentiment tags on email replies before they're treated as real.
- Confirming AI-generated personalization per lead before it goes out.

### Success Metrics

- **Primary (assumption, not yet validated):** 10-15% positive reply rate within a few weeks of the system going live. *Flagged as an estimate, not a sourced benchmark, needs validating against real data once the system is running, not treated as a committed target.*
- **Process metric:** percentage of calls and replies with structured outcome data actually logged. This measures whether the real bottleneck, signal capture, is fixed, independent of whether reply rate itself moves yet.

### Simplest Non-AI Baseline

A shared spreadsheet tracking customer/lead data, queried manually to calculate reply rate and review call sentiment, provided a human keeps it consistently up to date. This is the fallback that should be explicitly ruled out (or adopted as the actual solution) before any AI component is justified.

### Acceptance Criteria

Given 20 test email replies, the system suggests a sentiment tag (positive/neutral/negative) for every reply, never leaves one untagged, and any reply below a set confidence threshold is flagged for the SDR to review manually rather than auto-classified.

---

## Section 2: Architecture

### Pipeline overview

Every step in the pipeline is categorized as one of three types, kept deliberately coarse for this design-level document (a real team's tooling would subdivide automation further, e.g. scheduled job vs. webhook-triggered, but that belongs in an implementation spec, not here):

- **Automation**: rule-based, no judgment involved (Clay enrichment, Instantly sending, inbox receiving a reply, the database write itself).
- **AI**: genuine judgment or generation (drafting personalization, suggesting a sentiment tag).
- **Human**: cannot or should not be automated at this stage (pulling the lead, entering it into Clay, confirming personalization, confirming the sentiment tag, making the call and logging notes).

### Pipeline stages

1. Pull lead from contact list: Human
2. Add lead into Clay: Human
3. Clay enrichment (company/profile data): Automation
4. AI drafts personalization: AI
5. SDR confirms personalization: Human
6. Instantly sends email: Automation
7. Reply arrives in inbox: Automation
8. AI suggests sentiment tag (positive/neutral/negative): AI
9. Human confirms tag: Human
10. Call happens, notes logged: Human
11. Data written to database: Automation

Feeds back into the next list-building round (vertical-level performance data informs which verticals get prioritized).

*See attached diagram: voygr_pipeline_architecture.*

### Database design

Two linked tables, same pattern as the earlier SQLite work, not a new tool.

**`accounts`**: one row per company: `account_id`, `company_name`, `vertical`, `source`, `enriched_data`, `date_added`.

**`interactions`**: one row per email reply or call, linked to `accounts` via `account_id`: `interaction_id`, `type` (email_reply/call), `date`, `notes`, `sentiment_tag`, `human_confirmed`, `outcome`.

Plain-language explanation (for non-technical stakeholders): think of it like two connected spreadsheets. The first is a simple list of companies, one row each, with basic info about who they are. The second is a log of everything that happens with each company, every reply, every call, each entry pointing back to which company it belongs to. Keeping them separate (the same way you'd keep a customer list separate from a call log) means questions like "which industry replies most positively" can be answered by counting log entries per company, without manually tallying anything. It's the same idea as a CRM, just lightweight enough that a two-person team will actually keep it updated, which is what killed their last CRM attempt.

### Data transfer: what's automated vs. manual

- **Accounts table fills itself**: Clay's enrichment output is pushed in via API the moment a lead is enriched, no typing.
- **Email interactions are mostly automated**: the sequencing platform logs sends and replies automatically, AI suggests the sentiment tag automatically. The SDR's only action is one click to confirm or correct the tag.
- **Call notes are the one genuinely manual entry point, by design, not a gap**: nothing currently captures call content, so the SDR types a short note after each call. The old CRM asked for 8-9 fields per interaction and collapsed under that load; this asks for one field, with everything else auto-populated around it.

---

## Section 3: Security

### Data inventory by stage

Two stages actually send PII to the LLM, not the whole pipeline: the personalization draft (name, title, company, enrichment snippet) and the sentiment tag suggestion (full reply text). Every other stage either handles PII without AI involvement (Clay enrichment, Instantly sending, database write) or doesn't touch PII at all.

### What gets sent to the LLM

Personalization needs name, title, company, industry, and at most one enrichment fact, not the full enriched record or contact details like email/phone. Sentiment tagging needs message body only, the signature block (phone numbers, addresses, assistant names) should be stripped before the API call since it carries no classification value. Clean rule for the deck: message body only, header and signature dropped before the call.

### Hard boundary: what never goes to the LLM

- No payment, contract, or pricing details, stated now even though not in the pipeline today, since a founder is likely to ask to log deal value in `interactions.notes` eventually.
- No raw signature blocks, direct-dial numbers, or physical addresses.
- No unverified enrichment data forwarded into a generative step, a stale or wrong Clay-sourced title becoming a false claim in a draft is a data-quality risk wearing a security costume, worth naming since nothing currently verifies Clay's source data before it reaches a draft.
- No freeform notes about a prospect's personal circumstances or leverage, a real risk given `interactions.notes` is unstructured text with nothing currently preventing drift in that direction.

### Human checkpoints as a security control, not just QA

Two checkpoints exist, personalization confirmation and sentiment-tag confirmation, and both do double duty. Confirming personalization catches AI inventing or misstating a fact (a hallucinated funding round, a wrong exec name) before it reaches a real inbox, that's not a tone issue, it's telling a prospect something false. Confirming the sentiment tag catches a manipulated or adversarial reply, a prospect's reply is untrusted external text, the same caution level as a webform submission, not the same trust level as internal Clay input. Blast radius is small today since nothing auto-advances on tag alone, but the two checkpoints should be understood explicitly as workflow accuracy and a security backstop, not one or the other.

### Minimum access per tool

- **Clay**: insert-only into `accounts`. No read or write access to `interactions`, it has no reason to see call notes, sentiment history, or deal outcomes.
- **Sequencing platform (Instantly/Smartlead)**: read access to name/email/company for sending, write access to log sends and raw replies into `interactions`. No access to confirmed sentiment tags, call notes, or anything downstream of SDR review, data flows one direction, out of sequencing into the database, not back.
- **Claude API**: called per request with only the fields that task needs, payload built and stripped before each call, no standing connection or broad read scope.
- **Database**: access split by function, not by person. Clay's connector inserts into `accounts` only; the sequencing platform writes to `interactions` send/reply fields only; the SDR's entry surface reads and writes call notes and confirmation fields. Nobody defaults to admin access just because the schema is small, that habit is how small systems end up with no real access control once they scale.

### Retention and deletion

Not yet answered anywhere in this design, and worth deciding before build rather than after. Two open questions to bring to the founder: how long does `interactions` data live (options range from indefinite retention for trend analysis, to archiving/anonymizing records past a set point after a lead goes cold), and what happens if a prospect asks to be removed. The two-table schema makes deletion mechanically simple, delete by `account_id` across both tables, but the *policy* (how long, under what trigger) is still an open decision, not a technical one.

### Third-party vendor risk

Separate from internal access control: Clay, the sequencing platform, and Anthropic are all third parties who receive this data simply by being SaaS tools in the pipeline, a different risk category from "who on our team can see what."

Specifically on the Claude API: commercial/API usage does not train on customer data by default, and inputs/outputs are automatically deleted within 30 days; Zero Data Retention is available by agreement for eligible organizations if that's ever required. One real caveat worth flagging given VOYGR's verticals include finance/insurance and real estate: the direct Anthropic API currently offers only US and global inference regions, no dedicated EU-only option, worth revisiting if EU-based contacts become a meaningful share of the pipeline.

Clay and the sequencing platform's own data-handling terms haven't been individually audited here, accepted as a reasonable risk for a lean two-person team at this stage rather than something requiring a full vendor security review, but worth naming as a conscious tradeoff, not a silent gap.

---

## Section 4: ROI Framing

### Current manual cost (assumption, not measured)

Based on 200 emails/week and the process described in discovery, not VOYGR's actual time-tracking data:

- Research and personalization: ~3 min/email × 200 = ~10 hours/week
- Reading and interpreting replies: ~5 min × 20-30 replies (10-15% reply rate) = ~2 hours/week
- Call handling and recall (no captured notes today): ~1.5-2 hours/week

**Total current manual cost: roughly 13-15 hours/week**, stated as an assumption based on volume and task type.

### Proposed system cost (checked against public 2026 pricing pages)

- Clay, Launch tier: $185/month (2,500 data credits, 15,000 actions), sufficient at ~800 enrichments/month.
- Instantly, Growth tier: $47/month (5,000 emails, 1,000 contacts/month), fits 800 sends/month comfortably.
- Claude API: ~$10-20/month, personalization drafts (Sonnet) plus sentiment tagging (Haiku) at current volume, including buffer for retries.
- Database (SQLite): $0, no additional cost.

**Total recurring cost estimate: roughly $240-250/month.** An estimate from public pricing, not a vendor quote, actual Clay credit use could push this toward the Growth tier if enrichment needs more than one data source per lead.

### Human review time under the new system

- Confirming personalization: ~1 min/email × 200 = ~3.3 hours/week (vs. ~3 min writing from scratch today)
- Confirming sentiment tags: ~30 sec × 20-30 replies = under 0.3 hours/week
- Call notes: unchanged, ~1-1.5 hours/week, the one deliberate manual entry point, not a savings line

**Total new time: roughly 4.5-5 hours/week.**

### Estimated gross saving

13-15 hours/week minus 4.5-5 hours/week is an estimated **8-10 hours/week saved**, stated as a range given the underlying assumptions.

What this buys VOYGR matters more than the raw hour count. Since 200 emails/week already looks like a bandwidth ceiling for one person doing research, sending, and follow-up, the more realistic outcome isn't "she works 8-10 fewer hours," it's that the freed time converts into more prospecting volume, more calls, or better-targeted list-building. That's the framing to bring to the founder, not pure hours saved.

### Uncertainty, named explicitly

This estimate rests on assumptions that can't be verified against VOYGR's real data. The current 200 emails/week may already reflect a hard bandwidth ceiling rather than a choice, meaning freed time is more likely to convert into higher volume than fewer hours worked, which changes what "saving" means here. Reply and call volume, and therefore the sentiment-tagging and call-logging time estimates, are based on an assumed 10-15% reply rate that Section 1 already flags as unvalidated, so actual API cost and review time could move meaningfully once real data exists.

---

## Section 5: Build Notes and Known Limitations

### Observability

Every call to `insert_record.py` now logs to `pipeline_log.txt`, one line per attempt: timestamp, status (SUCCESS/FAILED), record type, and a detail message (the new `account_id`/`interaction_id` on success, or the specific error on failure). This directly answers the plan's own test: if something ran overnight and a share of records failed, the log file shows exactly how many and why, rather than requiring a guess.

### Execute Command finding (real build failure, documented as it happened)

The original architecture assumed n8n could call `insert_record.py` directly via an Execute Command node. Testing this directly (`python --version` as a minimal check) showed that **Execute Command is not available on n8n's cloud tier**, the node doesn't appear in the cloud instance's node picker at all. This is a deliberate security boundary, not a bug, a cloud service cannot be permitted to run arbitrary shell commands on its own servers.

**Correct fix, identified but not yet built**: since n8n cloud communicates over HTTP (already proven via the Clay-to-n8n webhook), the database-write step needs the same pattern in reverse: a small local API (Flask) wrapping the insert logic, exposed via a tunnel or, more durably, deployed to a free-tier host. This was scoped into the deployment step that followed, which ran the Python component on a free-tier host (Render), so it was handled as part of the build rather than left as unfinished work.

**Why this is documented rather than silently worked around**: correctly diagnosing a hosting constraint and identifying the right architectural fix is a genuine systems-integration finding, not just a blocker. Noting it here, with the reasoning, is stronger evidence of understanding than building the workaround without explaining why it was necessary.

---

## Section 6: Deployment

### What was deployed

The database-write component (`api_server.py`, a Flask wrapper around the SQLite insert logic) was deployed to Render's free tier, replacing the original Execute Command plan documented in Section 5. The service runs at a public URL (`https://three0-day-build.onrender.com`) and is reachable independent of the local machine, confirmed by closing the local development environment entirely and re-querying the live URL successfully.

n8n itself required no separate deployment step: it already runs on n8n's own cloud tier (`amyw.app.n8n.cloud`), which is precisely why the original Execute Command approach failed, cloud n8n has no local shell or file-system access, the finding documented in Section 5.

### Break-and-recover test

Two deliberate failure tests were run against the live Render service, both via direct HTTP calls, not through n8n:

1. **Valid JSON, missing required field** (`{"not_valid": true}`, no `record_type`): the service returned a structured error response (`{"status": "error", "message": "Unknown record_type 'None'"}`) rather than crashing.
2. **Genuinely malformed JSON** (a plain string, not valid JSON at all): Flask's own request parser rejected it with an HTTP 400, again without crashing the service.

After both failure tests, the live health-check endpoint (`GET /`) was re-queried and returned `{"status": "running"}` cleanly, confirming the service survived both bad inputs and continued serving normally, no restart required. This break/recover sequence happened *between* pipeline test runs (after the first 2 successful n8n-to-Render inserts, before the final 3), not as an isolated test run in a vacuum, confirming the service recovers mid-operation, not only from a clean idle state.

---

## Section 7: Result

Five records were pushed through the full live pipeline (n8n Manual Trigger → Edit Fields → HTTP Request → Render → SQLite), spanning five different verticals (logistics, transportation/logistics, retail, finance/insurance, real estate) to exercise the vertical-tagging logic deliberately, not just prove a single happy path. Each run returned a distinct, correctly incrementing `account_id` (4 through 8), confirming genuine new inserts rather than a cached or repeated response.

Note on numbering: `account_id` 1-3 came from earlier manual, file-based testing of `insert_record.py` during local development, before the live n8n-to-Render pipeline existed. IDs 4-8 are the actual end-to-end pipeline test, the number that matters for this Result section.

Sample size was deliberately trimmed from the plan's original 20-30 records to 5, a time-boxed decision made explicitly during the build and recorded here, not a hidden shortcut. Five records were judged sufficient to prove the mechanism works correctly; they are not sufficient to draw any conclusion about real-world reply or sentiment distribution, which was never the goal of this test.

---

## Section 8: Limitations

- **Render free tier has an ephemeral filesystem.** `voygr.db` as deployed to Render is not guaranteed to persist across service restarts or redeploys. This is acceptable for proving the deployment mechanism today, but a real production deployment would need a persistent database (Render's paid disk tier, or an external hosted database) rather than a SQLite file on ephemeral storage.
- **Flask's built-in development server is running in production.** Render's logs explicitly warn against this ("do not use it in a production deployment, use a production WSGI server instead"). Acceptable for a time-boxed prototype; a real deployment would use Gunicorn or similar.
- **Sample size was 5 records, not the planned 20-30**, a deliberate, stated time trade-off (see Section 7), not a quality concession, but genuinely too small to validate real reply-rate or sentiment-distribution assumptions from Section 4's ROI estimate.
- **The Clay-to-n8n-to-Render chain has not been tested as one single unbroken run.** Clay's enrichment/AI columns (Sections 1-4) and the n8n-to-Render database write (this section) have each been proven working, but a single end-to-end run starting from Clay and finishing at the database write has not yet been executed in one pass.
- **No authentication on the Render endpoint.** `/insert` is currently open to any caller with the URL. Acceptable for a prototype; a real deployment would need at minimum an API key check.

---

## Section 9: Next Iteration

- Move `voygr.db` to a persistent, non-ephemeral store (Render paid disk tier, or a hosted Postgres instance) to survive restarts.
- Replace Flask's development server with a production WSGI server (Gunicorn) for the Render deployment.
- Run the full Clay → n8n → Render chain as one genuinely unbroken pipeline, not three separately-proven segments.
- Scale the end-to-end test from 5 records to the originally planned 20-30 once time allows, to get a real (if still small) read on reply and sentiment distribution.
- Add basic authentication to the `/insert` endpoint before any real, non-test data would touch it.
- Build the deferred `interactions` write path end to end (currently only `accounts` inserts have been tested live via n8n/Render; the `interactions` table and its account_id linkage were proven locally but not yet through the live deployed pipeline).

---

## Section 10: Tradeoff Question, Applied

**Component: sentiment tagging on email replies.**

This is genuinely AI, not a fixed rule, and the reasoning is the same three-way split established during the Clay enrichment work and reused throughout this artifact: enrichment and enumeration steps (Clay pulling company data, Render logging a row) are rule-based automation, no judgment required. Sentiment tagging is different because it requires interpreting open-ended, unstructured human text, a reply that says "not right now, check back in Q2" is not a keyword match away from "not interested," it requires understanding intent, which a fixed rule or keyword list cannot reliably do. This is precisely why Section 3 (Security) scoped the AI call narrowly to message-body text only, and why Section 1 (Requirements) explicitly requires human confirmation on every AI-suggested tag before it's treated as ground truth, the AI narrows and suggests, a person still makes the final call on anything that isn't a clear-cut automatable pattern.

By contrast, the tier-scoring logic built in Section 2's architecture (Enterprise/Mid-Market/SMB, based on headcount and site count thresholds) is correctly a fixed rule, not AI, because it's a deterministic numeric comparison with no ambiguity to interpret, exactly the distinction this design applies throughout.

---
*Document status: Portfolio Artifact #1 complete. All ten sections written: Problem, Discovery/Requirements, Architecture, Security, ROI, Build Notes, Deployment, Result, Limitations, Next Iteration, plus the tradeoff analysis. Ready for README and final push.*
