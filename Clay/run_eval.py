import json
from sentiment_classifier import classify_reply

# Categorize each miss into one of the four buckets from the Week 5 plan.
# This mapping is a starting point, not gospel, you should read each miss
# yourself and override the category if the automatic guess looks wrong.
ERROR_CATEGORIES = ["bad_data", "ambiguous_input", "model_overconfidence", "prompt_issue"]


def run_eval(eval_set_path="eval_set.json"):
    with open(eval_set_path, "r") as f:
        eval_set = json.load(f)

    results = []
    correct_count = 0

    for example in eval_set:
        reply_text = example["reply_text"]
        correct_tag = example["correct_tag"]

        classification = classify_reply(reply_text)
        predicted_tag = classification.get("tag")

        is_correct = (predicted_tag == correct_tag)
        if is_correct:
            correct_count += 1

        results.append({
            "id": example["id"],
            "reply_text": reply_text,
            "correct_tag": correct_tag,
            "predicted_tag": predicted_tag,
            "model_reasoning": classification.get("reasoning"),
            "is_correct": is_correct,
            "note": example.get("note", "")
        })

    accuracy = correct_count / len(eval_set)

    return results, accuracy


def print_report(results, accuracy):
    print("=" * 70)
    print(f"ACCURACY: {correct_count_from(results)}/{len(results)} = {accuracy:.1%}")
    print("=" * 70)

    misses = [r for r in results if not r["is_correct"]]

    if not misses:
        print("\nNo misses. Every example was classified correctly.")
        return

    print(f"\n{len(misses)} MISSES, for manual error categorization:\n")
    for r in misses:
        print(f"--- Example {r['id']} ---")
        print(f"Reply: {r['reply_text']!r}")
        print(f"Correct tag: {r['correct_tag']}")
        print(f"Model predicted: {r['predicted_tag']}")
        print(f"Model reasoning: {r['model_reasoning']}")
        print(f"Eval set note: {r['note']}")
        print("Assign category manually: bad_data / ambiguous_input / model_overconfidence / prompt_issue")
        print()


def correct_count_from(results):
    return sum(1 for r in results if r["is_correct"])


if __name__ == "__main__":
    results, accuracy = run_eval()
    print_report(results, accuracy)

    # Save full results to a file so the misses can be reviewed and
    # categorized without rerunning the API calls.
    with open("eval_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\nFull results saved to eval_results.json")