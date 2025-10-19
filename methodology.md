# ASR quality metrics, explained like a human

Here’s a simple way to think about how we’re judging transcription quality. We look at three things that complement each other:

- WER (Word Error Rate)
- CER (Character Error Rate)
- TF‑IDF cosine similarity

We also use clear pass/fail thresholds:

```
WER_THRESHOLD = 0.15
CER_THRESHOLD = 0.10
TFIDF_THRESHOLD = 0.75
```

If a transcript stays under the WER/CER limits and at or above the TF‑IDF score, it’s in good shape.

---

## 1) WER — how many words are off

What it tells you:
- How many words are wrong compared to the ground truth, counting insertions, deletions, and substitutions.

Why it matters:
- It’s the most familiar ASR metric and maps well to human readability. If WER is 10%, roughly 1 in 10 words is wrong.

Quick example:
- Ground truth: “The weather is nice today.”
- System: “The weather nice today.”
- We’re missing “is” (a deletion) → 1 error / 5 words = WER = 0.20 (20%).

Threshold: WER ≤ 0.15 → at least ~85% word‑level accuracy.

---

## 2) CER — when spelling and tiny slips matter

What it tells you:
- The same idea as WER but at the character level. Great for catching small spelling changes and punctuation issues.

Why it matters:
- Sensitive to subtle errors WER can gloss over.
- Helpful for short snippets or languages without spaces.

Quick example:
- Ground truth: “colour”
- System: “color”
- One character difference (“u”) → 1 error / 6 chars = CER ≈ 0.17 (17%). WER could be 0% here, but CER flags the misspelling.

Threshold: CER ≤ 0.10 → the text should be cleanly and precisely spelled.

---

## 3) TF‑IDF cosine — are we saying the same thing?

What it tells you:
- Measures semantic overlap using TF‑IDF and cosine similarity. In other words: do the two texts talk about the same content, even if the wording differs?

Why it matters:
- Captures meaning beyond exact word matches. Useful when there’s paraphrasing or synonyms (e.g., “kids” vs “children”).

Quick example:
- Ground truth: “The cat sat on the mat.”
- System: “A cat was sitting on a mat.”
- Wording changes, but meaning is intact → TF‑IDF cosine ≈ 0.85.

Threshold: TF‑IDF ≥ 0.75 → wording can vary, meaning should stay solid.

---

## How to read these together

- WER/CER tell you about surface correctness: wrong or missing words and small textual slips.
- TF‑IDF tells you about meaning: are we conveying the same ideas?

When all three look good, the transcript is both accurate and faithful to the content. If WER/CER are high but TF‑IDF is fine, you likely have paraphrasing with too many literal errors. If TF‑IDF is low but WER/CER are okay, the words are mostly right but the content may be off-topic or missing key pieces.

---

## What “good” looks like at a glance 

- WER ≤ 0.15
- CER ≤ 0.10
- TF‑IDF ≥ 0.75
