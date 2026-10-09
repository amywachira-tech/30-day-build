# Portfolio Artifact #2: Generalized Call-Scoring System

## Leading with the failure case

The strongest evidence in this artifact is not a clean success story. It is a leniency pattern that showed up in the baseline evaluation, held up under closer scrutiny against the actual transcripts, and then failed to reproduce under two independently designed adversarial tests built specifically to trigger it.

Building ground-truth labels independently and comparing them to the scorer's output surfaced 5 mismatches out of 18 dimension-ratings across three test transcripts (72% agreement). Rechecking each mismatch directly against the transcript text, not just the JSON, found that 4 of the 5 are genuine, checkable defects, not subjective disagreements:

- **Meridian, `trust_framing_placement`**: the scorer's evidence claims the rep "responded reactively" to a compliance mention. The rep never responds to it at all, anywhere in the transcript. The evidence describes an exchange that doesn't exist.
- **Meridian, `decision_maker_path`**: rated "strong" on the strength of the prospect's own unconfirmed claim that his VP "trusts his read." No deal-specific threshold or approval step was ever established. This is precisely the failure mode the adversarial testing below was designed to catch, and it appeared here first, unbaited, in ordinary data.
- **Fenwick, `trust_framing_placement`**: the scorer's own evidence says the rep "never reflected this back." The rubric defines never-addressed as poor. The scorer rated it needs_work anyway, its own stated evidence contradicting its own rating.
- **Fenwick, `decision_maker_path`**: same pattern, evidence says the gap was "acknowledged but unaddressed," which is the rubric's own definition of poor, scored needs_work instead.

The fifth mismatch, Harrow's `decision_maker_path`, is a genuine judgment call, not a defect: ground truth itself flags that dimension as structurally ambiguous on a disqualified deal (see Limitations), and the scorer's stricter reading is defensible under the rubric's literal text.

That left a real question: is this a systematic leniency bias, or three unlucky dimension-level misses? I built two separate adversarial transcripts, each designed independently to bait the specific pattern found above:

- **Round 1** used explicit but hollow language: a vague security reassurance with no specifics, a decision-path statement with no name or date attached, a capability claim softened by reassuring tone. The classifier caught all five planted traps correctly. It did not fail.
- **Round 2** targeted the exact mechanism behind the real defects above: omission disguised as adjacency (answering a security question with an unrelated integration answer), and a hedged, conditional authority claim that sounds settled but confirms nothing for the specific deal. The classifier caught all three planted traps correctly, and also flagged a legitimate issue on two dimensions deliberately left as controls.

Two independently designed, deliberately targeted replication attempts both failed to reproduce the bias. That is a genuinely strange result given that the bias is real and repeatable in the baseline data: four separate instances, not one, all showing the same shape, the model rating something more favorably than its own stated evidence supports. The honest conclusion isn't "no bias" and it isn't "broad systemic failure" either. The scorer reliably underrates the severity of absence when it occurs naturally in a transcript, but does not reliably fall for the same gap when it's deliberately engineered as bait. That's a narrower, odder, and more useful finding than either extreme, and matters for anyone deploying this kind of classifier: synthetic red-teaming may not surface a bias that's actually present in real usage, because real omissions don't announce themselves the way a planted trap does.

---

## What this is

A generalized B2B sales call-scoring system: a transcript goes in, a Claude API call scores it across six defined dimensions plus an overall outcome, and returns structured JSON. Built from fictional transcripts written for this exercise, not from any real company's proprietary call data or scoring methodology.

## Rubric design

The six dimensions are a generalized structure, not a copy of any specific company's proprietary rubric. The core design principle carried over is judging **when and how** something happened, not just whether it was mentioned at all, since presence-only checks miss the difference between a rep who proactively earns trust and one who only responds after being pressed.

| Dimension | What it checks |
|---|---|
| `pitch_intensity_fit` | Did the size of the ask match the qualification actually confirmed on the call |
| `trust_framing_placement` | Was risk/trust-relevant framing delivered proactively, reactively, or never |
| `pain_reflected_back` | Did the rep synthesize the prospect's stated pain in their own words, or let it pass |
| `time_discipline` | Did the call move toward a close at a reasonable pace with an active attempt |
| `claim_discipline` | Did the rep make unsubstantiated claims, including ones softened by reassuring tone |
| `decision_maker_path` | If the real approver was absent, is there a concrete, owned step to reach them |

## Transcripts used

Five fictional companies, none real, each built with deliberate texture rather than generic dialogue:

1. **Meridian Sensing** (cold chain IoT monitoring) — clean close
2. **Harrow Analytics** (predictive maintenance) — clean loss, correctly disqualified by the rep mid-call
3. **Fenwick Trials** (clinical trial management) — ambiguous stall, genuine interest blocked by a structural contract issue
4. **Solstice Underwriting** (adversarial round 1) — baited with explicit but hollow language
5. **Cartwell Logistics** (adversarial round 2) — baited with omission-via-adjacency and hedged/conditional authority claims

## Scoring script

`call_scorer.py`: one function per transcript call, structured JSON output enforced via prompt instruction, with defensive markdown-fence stripping before parsing (Claude wraps JSON in fences even when told not to, a recurring pattern from earlier in this build) and an empty-input guard that returns a safe default rather than sending a malformed request to the API.

## Eval methodology

Ground truth labels were written independently, reasoning from each transcript's text directly, before comparing to the model's output, to avoid rubber-stamping. Across the first three transcripts (18 dimension-ratings total):

- **13/18 dimension-level agreement (72%)**
- **3/3 overall-outcome agreement**

All five mismatches, revisited against the actual transcript text rather than taken at face value:

1. **Meridian, `trust_framing_placement`**: genuine defect. The scorer's evidence claims the rep "responded reactively" to a compliance mention. The rep never responds to it anywhere in the transcript, the evidence describes an exchange that doesn't exist.
2. **Meridian, `decision_maker_path`**: genuine defect. Rated strong based only on the prospect's unconfirmed self-report that his VP "trusts his read." No deal-specific threshold or approval step was ever established on the call.
3. **Harrow, `decision_maker_path`**: arguable judgment call. This dimension is structurally ambiguous on a disqualified deal (see Limitations), and the scorer's stricter reading is defensible under the rubric's literal text.
4. **Fenwick, `trust_framing_placement`**: genuine defect. The scorer's own evidence text says the rep "never reflected this back." The rubric defines never-addressed as poor. Rated needs_work anyway, its own evidence contradicting its own rating.
5. **Fenwick, `decision_maker_path`**: genuine defect. Same pattern, evidence says the gap was "acknowledged but unaddressed," the rubric's own definition of poor, scored needs_work instead.

Four of five mismatches are genuine, checkable defects, not subjective disagreements, and three of the four share a specific shape: the scorer's own stated evidence describes something as absent or unconfirmed, and the rating still lands one notch more favorably than that evidence supports.

## Adversarial testing (the failure-case investigation)

Detailed above. Two independently designed rounds, eight planted traps total across both rounds, zero traps succeeded, despite both rounds targeting the exact failure pattern confirmed present in the baseline ground-truth comparison. The classifier correctly distinguished:

- A vague reassurance from real substance
- Generic acknowledgment from actual reflection
- An adjacent, plausible-sounding non-answer from a real answer to the question asked
- A hedged, unconfirmed authority claim from a settled one

This doesn't mean the bias isn't real, the baseline comparison above confirms it is. It means deliberately engineered bait doesn't reliably reproduce a bias that shows up naturally in ordinary transcripts, a genuine and somewhat unsettling finding about the limits of adversarial testing as a way to catch this specific kind of error.

## Limitations

- **A real leniency pattern exists on `trust_framing_placement` and `decision_maker_path` specifically.** In three of four confirmed defects, the scorer's own evidence text states something was never addressed or never confirmed, and the assigned rating is still more favorable than the rubric's own definition allows for that evidence. This isn't evenly distributed across all six dimensions, it's concentrated on these two.
- **The rubric's `decision_maker_path` dimension conflates two different outcomes under one rating.** Correctly recognizing a dead end (Harrow) and having a genuinely confirmed live path are treated as the same "strong," though they're different achievements, and this ambiguity is exactly what made Harrow's mismatch a defensible judgment call rather than a clear defect. Worth splitting in a future version.
- **Ground truth labels were produced by one person (me) reasoning alone.** A second independent labeler, then measuring inter-rater agreement, would strengthen the eval's credibility beyond what a single perspective can support.
- **All five transcripts are fictional**, written to be realistic but not validated against real call recordings. The scorer has not been tested against genuine transcript noise, interruptions, crosstalk, or the messiness of real speech-to-text output.
- **Four confirmed defects out of 18 ratings is still a small sample.** It establishes that this failure mode exists and recurs, not its true rate at production scale.

## Next iteration

- Tighten the scoring prompt with an explicit rule for `trust_framing_placement` and `decision_maker_path`: if the evidence text states something was never addressed, unconfirmed, or self-reported rather than established, the rating must be poor, not needs_work or strong, closing the specific gap this eval surfaced.
- Split `decision_maker_path` into two dimensions: path-exists and path-owned, so a correctly recognized dead end doesn't score identically to a successfully mapped live path.
- Build a larger labeled set (aiming for 30+ dimension-ratings) to get a more stable accuracy estimate than three transcripts can support.
- Add a second independent labeler and measure inter-rater agreement before treating any single mismatch as a confirmed model defect versus a genuine judgment-call disagreement.
- Test against transcripts with realistic noise (interruptions, incomplete sentences, speaker misattribution) rather than clean, well-formed dialogue.