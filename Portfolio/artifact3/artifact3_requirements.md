# Artifact #3: Internal Support Policy Retrieval System

**Client (fictional):** Kestrel Home, home-goods e-commerce
**Business owner:** Daniel Otieno, Head of Customer Support
**Status:** Requirements v3, Wed Oct 7, 2026. Discovery completed over two calls.

---

## 1. Summary

Kestrel Home's 45 support agents answer customer questions from three sources: a Confluence handbook, older Google Docs, and policy announcements in Slack. These sources contradict each other, and nobody owns keeping them current.

The cost is not only lost time. New agents find outdated policies and act on them confidently. In February this produced about $18,000 in refunds Kestrel did not owe. In July an agent followed an outdated identity-verification procedure and disclosed order details to an unverified caller, which escalated to Legal and the COO.

This system lets an agent ask a question in plain language and get an answer drawn from the most authoritative current source, with a citation. When the evidence is weak, the sources conflict without a clear winner, or the content is above the agent's access level, the system responds "Ask a lead."

The design priority is **correct answers and safe refusals over answer coverage.**

---

## 2. Problem and cost

| Problem | Cost |
|---|---|
| Leads answering questions that are already documented | $6,000 to $6,500 per month (4 leads, 3 to 4 hours per shift, about $3,200 per month fully loaded each) |
| Sale-item return window cut from 60 to 30 days in February; old handbook page still said 60 | About $18,000 in refunds not owed |
| July: agent followed an outdated, looser verification step and disclosed order details and an address to the customer's ex-partner | Legal involvement, report to COO, near-miss with the regulator. Unquantified risk. |
| Six-week ramp for new agents, about 5 hires per quarter | Not yet quantified |

Root causes:
- Policy changes are announced in Slack or email and never written back into the documentation.
- The 2025 consolidation into a Confluence handbook went stale within four months.
- Google Docs show a recent "last modified" date after trivial edits, so an old policy can look current. This is part of how the July incident happened.
- Kestrel's verification process itself is sound. The failure was an agent finding an outdated copy of it.

---

## 3. Users and stakeholders

| Role | Who | Involvement |
|---|---|---|
| Primary user | New support agents | Ask questions mid-call in shorthand; need a fast yes or no with a source |
| Secondary user | 4 support leads | Fewer routine questions; receive escalations and stale-source reports |
| Business owner | Daniel Otieno, Head of Customer Support | Approves a pilot up to about $15,000 |
| Approver | COO | Approves anything ongoing or above $15,000 |
| Deployment gate | Grace, Legal | Must approve all privacy and identity content. Can block deployment. |
| Deployment gate | IT Security | Must review connections to Confluence and Google Drive |
| Reviewer | Peter, Ops Manager | Owns shipping and seller policy |

Policy owners: Finance (refunds), Operations (shipping, marketplace sellers), Legal (privacy and identity).

---

## 4. Success metrics

| Metric | Target | Source |
|---|---|---|
| New-agent ramp | 6 weeks to 4 weeks | Daniel |
| Questions reaching leads in Slack | 50% reduction within the first two months | Daniel |
| Accuracy of answers the system gives | 95% or higher | Proposed. Daniel said one wrong answer in ten is worse than today. |
| "Ask a lead" rate | Up to 30% is acceptable, provided the refusals are appropriate | Daniel |
| Unsafe answers (answered when it should have refused) | Zero in evaluation | Proposed |
| Lead-only content reaching an agent | Zero in evaluation | Proposed |

**Limit of the demo evaluation.** The labeled set has 10 to 15 questions, of which about half should be answered. With roughly 7 answered questions, a single error gives about 86%. The demo cannot validate a 95% target. It reports raw counts for every metric. A production go-live threshold needs a substantially larger labeled set, built with the leads.

---

## 5. Source of truth and conflict rule

### Authority tiers

1. **Owner announcement**: #policy-updates in Slack, or email from Legal
2. **Confluence handbook**
3. **Google Docs**

### Dates

- `last_modified` is never used to decide which policy is current. Trivial edits move it.
- For announcements, the date used is the stated effective date if one is given, otherwise the posting timestamp. Later edits to a Slack message do not change its posting timestamp, which is why date is reliable for announcements and unreliable for documents.

### Conflict rule

| Situation | Behavior |
|---|---|
| Sources in different tiers disagree | Higher tier wins. Answer cites it and flags the outdated source. |
| Two announcements from the same owner disagree | Later effective date wins. Answer flags the earlier announcement. |
| Two announcements from different owners disagree | Ask a lead |
| Two sources in the same lower tier disagree | Ask a lead |

The tier comparison is done in code from chunk metadata. The model is never asked to decide which source is more authoritative.

### Response format when a source is superseded

> **30 days.** Source: Returns policy update (announcement, effective Feb 2026)
> Outdated source: "Returns FAQ" (Google Doc) still says 60 days. Reported for review.

The answer comes first; the flag is separate. The flag appears only if the agent is authorized to see the outdated source. Every flag is also logged so leads know which pages to fix.

---

## 6. Access control

- Two levels for the pilot: `agent` and `lead`. All four leads have identical access.
- **Lead-only content:** refund approval thresholds above the agent limit of $150, fraud and serial-returner signals, and Finance's payment-dispute playbook.
- Legal's privacy incident notes are excluded from the index entirely. Only Daniel should see them.
- Some documents mix both levels on one page. For example, the refunds document has agent rules at the top and lead thresholds lower down. **Access is therefore set per chunk.**
- **Chunking follows access boundaries.** Source files mark each section's access level. The chunker splits on those markers first and by size second, so no chunk ever contains both levels.
- **Filtering happens before search.** The query searches only chunks the user may see. Filtering after search would return fewer than the requested number of chunks and cause false refusals. Lead-only text never reaches the model in an agent's request.

Kestrel's current permissions are weak: most Google Docs are shared with anyone at Kestrel who has the link. Production access levels must come from real user roles, not from document sharing settings.

---

## 7. Answer flow and evidence check

The evidence check uses three layers, chosen because each one catches failures the others miss.

| Step | Check | On failure |
|---|---|---|
| 1 | Authenticate the user and set the access level | Reject |
| 2 | Search authorized chunks only | |
| 3 | **Similarity floor:** top chunk score below threshold | Ask a lead, no model call |
| 4 | **Model judgment:** returns JSON with `status`, `answer`, `quote`, `source_chunk_id`, `conflicting_chunk_ids` | `status` not "answer": ask a lead |
| 5 | **Quote check in code:** `quote` must appear word for word in `source_chunk_id`, and that chunk must have been retrieved | Ask a lead |
| 6 | **Conflict rule in code:** apply section 5 to the source chunk and any conflicting chunks | Ask a lead, or answer with an outdated-source flag |
| 7 | Return the answer with citation: source name, source type, effective date | |

Markdown code fences are stripped from the model output before `json.loads()`. A parsing failure gives "Ask a lead."

### What this design does not catch

The quote check proves the quoted sentence is real. It does not prove the answer is right. Three failures can still get through:

1. **Wrong reasoning from a real quote:** quotes "sale items may be returned within 30 days" and approves a return at 5 weeks.
2. **Wrong rule:** quotes the standard return window in answer to a sale-item question.
3. **Wrong source:** quotes a superseded document. Step 6 catches this only if the model reports the conflict.

This is why answer accuracy is evaluated separately from retrieval accuracy and abstention accuracy.

### Threshold setting

The similarity threshold is set on 3 to 5 development questions kept separate from the evaluation set. Setting it on the evaluation questions would mean grading against the answer key.

---

## 8. Data model

Each chunk carries:

```text
chunk_id
source_id
source_name
source_type        announcement | confluence | google_doc
authority_tier     1 | 2 | 3
owner              finance | operations | legal
policy_area        returns | shipping | sellers | identity | payments | warranty | escalation
effective_date     the date the policy took effect; announcements only where stated
last_modified      kept for display, never used for authority
access_level       agent | lead
text
embedding
```

Each source file uses frontmatter for source-level metadata and a marker on each section for access level.

---

## 9. Corpus design (synthetic, about 15 sources)

Pilot policy areas: **returns and refunds, identity verification, shipping**, plus marketplace seller rules because they create a deliberate conflict.

Required traps:

| Trap | Built from |
|---|---|
| Superseded policy across tiers | Old Google Doc "Returns FAQ" says 60 days; announcement says 30 days |
| Two announcements on one policy | Returns changed twice this year; the later effective date must win |
| Stale verification procedure | Old Google Doc with the looser check; current procedure in the handbook and a Legal email |
| Misleading last-modified date | The old verification doc has a recent `last_modified` from a typo fix |
| Seller versus Kestrel rule | Marketplace seller policy conflicts with Kestrel's damaged-item rule |
| Mixed-access page | Refunds document with agent rules and lead-only thresholds |
| Unanswerable question | A topic with no source in the corpus |

---

## 10. Evaluation (10 to 15 labeled questions)

Questions use agent shorthand, for example:
- "cust bought sofa on sale 5 wks ago wants return, ok?"
- "caller can't remember email on account, can I still give tracking?"
- "how long before we call a parcel lost"

Each question has an expected outcome: `ANSWER`, `ANSWER_WITH_FLAG`, `ASK_LEAD`, or `BLOCKED` (the answer exists only in lead-only content).

Metrics, reported separately as raw counts:

| Metric | Question it answers |
|---|---|
| Retrieval accuracy | Did the correct chunk appear in the results? |
| Answer accuracy | When it answered, was the answer correct? |
| Abstention accuracy | Did it say "ask a lead" when it should have? |
| Unsafe answer rate | How often did it answer when it should have refused? |
| Access leaks | Did any lead-only text reach an agent's answer? |

Errors are categorized by the step that failed (search, model judgment, quote check, conflict rule).

---

## 11. Pilot, timeline and commercials

- **Pilot:** the mid-November new-hire group, limited to the policy areas in section 9.
- **No rollout late November through December** (Black Friday and holiday peak). If the pilot is not ready for mid-November, it moves to January.
- After requirements review, there are about four weeks to mid-November, and Legal and IT Security review take part of that. A narrower pilot that is ready in November is preferred over a broader one that slips.
- **Commercial test:** the pilot must fit within about $15,000, and ongoing cost must be a small fraction of the $6,000 to $6,500 per month in lead time.
- **Open:** pilot and ongoing cost estimate. Requires an estimate of daily question volume. To be completed in the write-up.

---

## 12. Scope

**In scope for the demo:** synthetic corpus, chunking on access boundaries, embedding and indexing, filtered search, the evidence check in section 7, citations with outdated-source flags, and the evaluation in section 10.

**Out of scope for the demo:** Zendesk and Slack integration (a production requirement, since agents work there all day), live connections to Confluence, Google Drive and Slack, real customer data, real authentication, and automated documentation maintenance.

---

## 13. Assumptions and open questions

**Assumptions**
1. A synthetic corpus of about 15 sources represents the pilot policy areas well enough to test the design.
2. Slack announcements and Legal emails can be ingested as sources with posting dates.
3. `agent` and `lead` are the only access levels needed for the pilot.
4. Leads can supply an effective date for each policy in production.

**Open questions for production**
1. Who assigns each section's access level, and who updates it when a policy changes?
2. How are Zendesk roles mapped to retrieval access levels?
3. Is there current data on lead question volume and on how new-hire readiness is measured, to provide baselines?
4. What logging and retention does Legal require for questions about identity and privacy?
5. What is the expected daily question volume, for the cost estimate?

---

## 14. Design principle

When the evidence is weak, the system reports that to the agent instead of concealing it. An answer appears only when an authoritative source supports it, the quote is verified, and the agent is permitted to see it.
