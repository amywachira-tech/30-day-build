# Artifact 2: Generalized Call-Scoring System

A B2B sales-call scoring system built on fictional transcripts written for this exercise. A transcript goes in, a Claude API call scores it on six dimensions plus an overall outcome, and structured JSON comes out.

Dimensions: `pitch_intensity_fit`, `trust_framing_placement`, `pain_reflected_back`, `time_discipline`, `claim_discipline`, `decision_maker_path`.

## Leading with the failure case

Ground-truth labels were written independently, before comparing them with the scorer's output. Across three transcripts (18 dimension ratings), the scorer matched **13 of 18** ratings and **3 of 3** overall outcomes.

Of the 5 mismatches, **4 are genuine, checkable defects**, concentrated on `trust_framing_placement` and `decision_maker_path`. In three of the four, the scorer's own evidence describes something as absent or unconfirmed, and its rating is still one level more favourable than that evidence supports. The fifth mismatch is a defensible judgment call.

Two adversarial transcripts were then written specifically to trigger this leniency. The scorer caught every planted trap in both rounds. The bias appears in ordinary transcripts but did not reproduce when deliberately engineered, which suggests synthetic red-teaming can miss a bias that is present in real use.

## Files

| File | Contents |
|---|---|
| `PORTFOLIO_ARTIFACT_2_WRITEUP.md` | The full write-up: rubric, transcripts, method, adversarial testing, limitations and next iteration |
| `call_scorer.py` | The scoring script: one Claude call per transcript, structured JSON output, markdown-fence stripping, empty-input guard |
| `transcript_1` to `transcript_5` | Five fictional calls: a clean close, a clean loss, an ambiguous stall and two adversarial rounds |
| `ground_truth.json` | Independently reasoned labels, written before comparison |
| `scoring_results.json` | The scorer's output for all five transcripts |

## Next iteration

Tighten the prompt so that evidence stating something was never addressed forces a poor rating.

## Running it

```
cd Portfolio/artifact2
python call_scorer.py
```

Requires an `ANTHROPIC_API_KEY` environment variable.
