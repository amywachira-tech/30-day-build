# Portfolio Artifact #3: Policy Retrieval for Support Agents

A retrieval system that answers customer-support agents' policy questions from internal documents, cites the most authoritative current source, flags outdated sources, and refers the agent to a lead when the evidence is weak or contradictory.

Client: Kestrel Home (fictional home-goods retailer, discovery conducted as a roleplay). Corpus: 18 synthetic policy sources.

---

## 1. Lead finding

Although the system correctly answered the identity question, it missed the outdated FAQ linked to the July privacy incident because chunking split the verification rule from its corresponding sharing permissions. The answer itself was safe, but the leads were never told the FAQ is outdated, so the document behind the July incident stays in circulation for the next new hire to find. Search retrieved only the section describing what agents may share once a caller is verified (S10-c02), not the section defining verification as a name and order number (S10-c01); the fix is to keep dependent sections of a Q&A document in one chunk, or to retrieve neighbouring chunks from the same source.

---

## 2. The problem

Discovery with Kestrel's Head of Customer Support (two calls) established:

| Problem | Cost |
|---|---|
| Leads answering questions already documented | $6,000 to $6,500 per month in lead time |
| Sale-item return window cut from 60 to 30 days in February; the old handbook page still said 60 | About $18,000 in refunds not owed |
| An agent followed an outdated identity-verification document and disclosed order details to an unverified caller | Legal involvement, report to the COO. Unquantified risk. |

Root cause: policy changes are announced in Slack or by email and never written back into the documentation, and an old document's "last modified" date can look recent after a trivial edit.

Success criteria set in discovery: answers given must be correct; up to 30% "ask a lead" is acceptable; no lead-only content may reach an agent.

---

## 3. What was built

| Step | File | What it does |
|---|---|---|
| Chunk | `chunk.py` | Splits each source on access-level markers first, then by size, so no chunk mixes agent and lead content. Stops with an error if unmarked text would be copied into a document containing lead sections. 18 sources produce 36 chunks (28 agent, 8 lead). |
| Embed | `index.py` | Embeds chunks locally with `all-MiniLM-L6-v2` (sentence-transformers). |
| Search | `search.py` | Removes chunks the user's role may not see and announcements that are expired or not yet in effect, then searches only what remains. A final check raises an error if a forbidden chunk is ever returned. Top 6 results. |
| Answer | `answer.py` | 1. Similarity floor (0.45): below it, "ask a lead" with no model call. 2. Claude reports what each retrieved source says, with an exact supporting quote and an answer group. 3. Code verifies every quote appears word for word in a retrieved chunk. 4. Code applies the conflict rule. |
| Evaluate | `run_eval.py` | Runs the labelled set at a fixed date (Oct 8, 2026) and scores each metric separately. |

**Conflict rule (applied in code, never by the model):**

| Situation | Result |
|---|---|
| Sources in different tiers disagree | Higher tier wins (announcement, then Confluence handbook, then Google Doc). Lower source flagged. |
| Two announcements from the same owner disagree | Later effective date wins. Earlier one flagged. |
| Same-tier sources disagree otherwise | Ask a lead |

A flagged source is shown with its own quote, for example: `OUTDATED FOR THIS QUESTION: Returns FAQ (google_doc) still says: "All items, including sale items, can be returned within 60 days of delivery."`

---

## 4. Decisions

### Why local embeddings

I chose local embeddings so that Kestrel's policy text never leaves its own environment. Kestrel's IT Security team must review how any tool connects to its documents, and keeping the embedding step local removes one external service from that review. The corpus is small enough for this approach, and it let me focus on the harder parts of the problem: finding the right information, respecting permissions, resolving conflicting sources, and deciding when not to answer.

This is a prototype decision, not a claim that local embeddings are automatically better for production. I would revisit it if the corpus or performance requirements changed.

### Why a 0.45 similarity threshold

I used a threshold of 0.45 as a minimum relevance check before sending retrieved material to the model. If the best match fell below the threshold, the system would ask the agent to check with a lead instead of generating an answer from weak evidence.

I set the threshold using a separate development set rather than tuning it against the evaluation questions. I chose a strict value because Kestrel's Head of Support accepts up to 30% "ask a lead" responses, and a strict threshold can be loosened once there is data on what it refuses. That data does not exist yet: refusals at the threshold are not currently logged, which is the first item in the next iteration.

The threshold is a coarse filter, not proof that a retrieved source is correct. An unanswerable development question scored 0.442, while an answerable eval question scored 0.484, so the threshold only catches questions the corpus clearly does not cover. A relevant-looking passage can still be outdated, incomplete, or the wrong policy for the question; the model's check and the quote verification handle those cases.

### Why the conflict rule runs in code

I didn't want the model deciding which policy was more authoritative based on how the documents were worded. I assigned authority tiers to the sources and applied the conflict rules in code. A current owner announcement can override an older handbook or Google Doc, a later announcement from the same owner overrides an earlier one, and conflicting sources at the same lower tier trigger an escalation.

That separation makes the decision more predictable and easier to test. The model still judges one thing: whether two sources actually contradict each other, or whether one only covers a narrower case. In this evaluation it made that judgment correctly on the clearance question (Q2), but that is a single case, and the judgment remains with the model.

### Why access filtering happens before retrieval

I treated permissions as a retrieval constraint rather than something to check after the model had already seen the documents. Each chunk carries an access level, and the search is limited to the chunks the user is allowed to see. This matters because some documents mix agent-facing instructions with lead-only information. Filtering only at document level could expose restricted sections, while filtering after retrieval could leave the model with too few relevant chunks and cause unnecessary referrals to a lead.

---

## 5. Evaluation method

- 12 labelled questions written in agent shorthand, covering: superseded sources, two announcements on one policy, a narrower rule against a general rule, wrong-rule application (marketplace against Kestrel-sold items), a same-tier conflict, lead-only content requested by an agent, a mixed-access page, a lead user, an unanswerable question, and a temporary override that must not spread to other cases.
- 4 separate development questions used only to set the similarity floor, before the eval was run.
- Metrics scored separately: retrieval, outcome, citation, flags, access leaks, unsafe answers. Answer correctness labelled by hand against the source documents.
- Single run. Results are reported as run; later corrections are listed separately and the eval was not rerun to improve the numbers.

**Similarity scores on the development questions:**

| Question | Should be | Top score |
|---|---|---|
| D1 Standard parcel delivery time | Answer | 0.781 |
| D2 Who pays return shipping | Answer | 0.701 |
| D4 Address change after dispatch | Ask a lead | 0.442 |
| D3 Shipping to Uganda | Ask a lead | 0.339 |

For comparison, the answerable eval question "sofa on sale 5 weeks ago" scored 0.484.

---

## 6. Results (raw counts, single run)

| Metric | As run | After corrections |
|---|---|---|
| Outcome match | 10/12 | 11/12 (Q2 label corrected) |
| Retrieval (an expected source retrieved) | 9/9 | 9/9 |
| Citation (cited an expected source) | 9/9 | 9/9 |
| Flags (every expected outdated source flagged) | 3/4 | 4/5 (Q2 label corrected) |
| Access leaks | 0 of 12 | 0 of 12 |
| Unsafe answers (answered when it should have referred) | 0 | 0 |
| Answers correct (hand-labelled) | 8 of 9 | 9 of 9 (Q8 after role fix, verified on one rerun) |

**Per question:**

| # | Role | Tests | Expected | Got | Cited | Flagged | Answer |
|---|---|---|---|---|---|---|---|
| 1 | Agent | Superseded source | Answer + flag | Answer + flag | S02 | S01 | Correct, cluttered |
| 2 | Agent | Narrower rule vs general rule | Answer + flag* | Answer + flag | S03 | S01, S04, S02 | Correct |
| 3 | Agent | Stale verification procedure | Answer + flag | Answer + flag | S12 | S10 | Correct |
| 4 | Agent | Wrong-rule trap | Answer | Answer | S07 | | Correct |
| 5 | Agent | Same-tier conflict | Ask a lead | Ask a lead | | | |
| 6 | Agent | Mixed-access page | Answer | Answer | S04 | | Correct, no lead content retrieved |
| 7 | Agent | Lead-only content | Blocked | Ask a lead | | | No lead content retrieved |
| 8 | Lead | Lead permissions | Answer | Answer | S04 | | **Wrong** as run |
| 9 | Agent | Unanswerable | Ask a lead | Ask a lead | | | |
| 10 | Agent | Temporary override | Answer + flag | Answer + flag | S15 | S13 | Correct, cluttered |
| 11 | Agent | Stale verification procedure | Answer + flag | **Answer** | S12 | | Correct, flag missed |
| 12 | Agent | Override must not spread | Answer | Answer | S15 | | Correct |

\*Q2 was labelled "Answer" in the run. The label was corrected after review; see findings.

---

## 7. Findings

### Retrieval quality and answer quality must be measured separately

The main lesson from the evaluation is that retrieval quality and answer quality need to be measured separately. A system can retrieve a relevant passage and still misunderstand it, apply the wrong rule, or miss a conflict. A citation alone doesn't guarantee that the answer is correct. Retrieval and citation were both 9 of 9, yet one answer was wrong.

That answer was Q8. A lead asked whether they could approve a $650 refund, and the system replied that they could not, because agents are limited to $150. The prompt told the model that every question came from an agent, so it answered a lead as if they were one. I changed the prompt to state the asker's role and reran Q8, and the system then answered correctly that the lead can approve it.

The as-run evaluation got 8 of 9 answers correct. After correcting the role-handling issue exposed by Q8, the result was 9 of 9 answers correct. I would report both figures rather than presenting the corrected result as if it were the original run. The corrected result shows that the issue could be fixed, but nine questions are far too few to establish production-level accuracy.

### The answer key was wrong twice

Two eval labels were wrong, and both errors came from judging a question from memory instead of from the source text.

- **Q2 (Final Clearance return):** the label was revised before the run to expect no flag, on the reasoning that the handbook only omitted the clearance rule. For a clearance item, the general sale-return rules in three sources would allow the return, so they contradict the clearance rule and the system was right to flag them. The original label was correct and was restored, and the correction is recorded in the eval set.
- **Q12 (standard parcel):** I first labelled the answer as wrong because it did not apply the temporary freight extension. The freight announcement states that standard parcels are not affected, so the system's answer was correct.

The method lesson is to label every case against the source document, and to document any label change made after a run.

### The model cannot see today's date

Q10's answer began "If today falls between Oct 1 and Nov 15, 2026". The code uses the date to filter expired announcements but never passes it to the model, so the model could not tell whether the temporary freight rule applied and hedged instead. The answer was correct, but it was cluttered for an agent on a live call.

### Omissions are not detected

The system flags a source only when it contradicts the winning source. A source that is merely missing a newer rule, such as a handbook page that predates an announcement, is not flagged unless applying its rule to the question would give a different answer.

### Similarity scores separate topics, not answerability

See the threshold decision in section 4: an unanswerable question scored 0.442 and an answerable one 0.484. The similarity threshold only removes clear misses; the model's judgment and the quote check do the real filtering.

---

## 8. Limitations

- Synthetic corpus of 18 sources and a 12-question eval set. Too small to support percentage claims or validate the 95% answer-accuracy target in the requirements.
- Single run. Model output varies between runs.
- Similarity-floor refusals are not logged, so there is no data yet on how many answerable questions the floor turns away.
- A source that omits a newer rule is not detected unless it contradicts it.
- Today's date is not passed to the model.
- No Zendesk or Slack integration, live connectors, or real authentication.

---

## 9. Next iteration

1. Keep dependent sections of a Q&A document in one chunk, or retrieve neighbouring chunks from the same source.
2. Log every "ask a lead" with its reason and top similarity score.
3. Pass today's date into the prompt.
4. On a same-tier conflict, tell the lead which sources disagree.
5. Remove duplicate flags (Q3 listed S10 twice).
6. Build a larger labelled set with Kestrel's leads, using real agent questions.

---

## 10. Tradeoff question

The main tradeoff is answer coverage versus the risk of giving a wrong answer. The system refers a question to a lead in three places: when nothing in the corpus is clearly relevant (the similarity threshold), when the model finds the sources do not answer the question, and when sources at the same level of authority disagree. Each referral protects against a wrong answer at the cost of a question the leads must handle. The threshold mainly controls coverage; wrong answers are prevented by the model's check, the quote verification and the conflict rule.

For this use case, I would start on the cautious side. Kestrel has already experienced financial losses from outdated policy and a serious identity-verification incident. A reasonable referral is less costly than a confident answer based on the wrong policy. I would use the pilot results to adjust the design, rather than trying to maximize the number of answered questions before the system has earned that trust.

The question I would take into a pilot is whether the extra escalations are acceptable given the reduction in incorrect answers and the time saved by leads. That needs to be measured with real agent questions, not settled from this small synthetic evaluation.

---

## 11. Expansion: enterprise-wide search

- **Connect the real sources.** Replace the synthetic corpus with approved connections to Confluence, Google Drive, and policy announcements in Slack or Legal email. Define how updates and deletions reach the index.
- **Integrate where agents work.** Put the retrieval experience into Zendesk or the team's existing workflow so agents don't need to switch tools during customer calls.
- **Use real identity and permissions.** Authenticate each user and map their actual role to retrieval access. Keep filtering at chunk level and test explicitly for lead-only information leaking into agent answers.
- **Improve monitoring and evaluation.** Log questions, retrieved sources, refusals, conflicts, and reported stale documents. Expand the evaluation set with support leads and track answer accuracy, appropriate abstentions, unsafe answers, access leaks, and lead escalations separately.
- **Estimate cost against actual usage.** For an initial planning assumption, use 10 questions per agent per working day across 45 agents. That's 450 questions a day, or approximately 9,900 questions over 22 working days. This is an assumption to test, not measured demand. The prototype's measured model cost on its test day was $0.13 for 27,200 tokens across 14 Claude calls, about $0.009 per call. Rounded up to $0.01 per question, 9,900 questions would cost about $100 a month in model usage, about 1.6% of the lead time the system is meant to save. This figure comes from 14 calls on synthetic questions and excludes hosting, connector, integration and monitoring costs, which must be added before quoting. The aim is for total ongoing cost to remain a small fraction of the $6,000 to $6,500 monthly cost of lead time, while keeping the pilot within Daniel's approximately $15,000 approval limit.

---

## Build notes

- Claude wrapped JSON in markdown code fences; fences are stripped before `json.loads()`.
- The model returned a thinking block before its text, so `msg.content[0].text` failed. The code now joins only text blocks, and `max_tokens` was raised so thinking cannot exhaust the output budget.
- `sentence-transformers` installs PyTorch (about 124 MB on Windows). The model downloads on first run.

## Files

`artifact3_requirements.md`, `corpus_plan.md`, `corpus/`, `chunk.py`, `index.py`, `search.py`, `answer.py`, `run_eval.py`, `eval_set.json`, `eval_results.json`, `eval_results.csv`, `Retrieval_Eval.xlsx`, `Answer_Review.xlsx`. `embeddings.npy` and `flags_log.jsonl` are generated and not tracked.
