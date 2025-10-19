# ASR quality metrics explained

Here’s a simple way to think about how we’re judging transcription quality. We look at three things that complement each other:

- WER (Word Error Rate)
- CER (Character Error Rate)
- TF‑IDF cosine similarity
- Latency (ms): total processing time per file (lower is better)
- Real‑Time Factor (RTF = processing_time / audio_duration): lower is better; ≤ 1 means real‑time

We also use clear pass/fail thresholds:

```
WER_THRESHOLD = 0.15
CER_THRESHOLD = 0.10
TFIDF_THRESHOLD = 0.75
LATENCY_THRESHOLD_MS=500
RTF_THRESHOLD=0.8
```

If a transcript stays under the WER/CER limits and at or above the TF‑IDF score, it’s in good shape.

---

## 1) WER -- how many words are off

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

## 2) CER -- when spelling and tiny slips matter

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

## 3) TF‑IDF cosine -- are we saying the same thing?

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

---

## What “good” looks like at a glance

- WER ≤ 0.15
- CER ≤ 0.10
- TF‑IDF ≥ 0.75
- LATENCY_THRESHOLD_MS ≤ 500
- RTF_THRESHOLD ≤ 0.8

## Text Transcription Results & Analyse

After running the analyzer script, the following results were obtained:

📄 **Transcript 1**

**Accuracy:**
TF-IDF (0.717), WER (0.290), and CER (0.121) all fall below acceptable levels.
This means the transcript contains frequent recognition errors, including missing or substituted words and some spelling issues.

**Performance:**
Latency (450 ms) ✅ and RTF (0.8) ✅ are within limits, showing good speed.

🧩 **Interpretation:**
The system runs efficiently but sacrifices accuracy.
It's fast but unreliable -- likely needs better language modeling or post-processing.

---

📄 **Transcript 2**

**Accuracy:**
TF-IDF (0.723), WER (0.226), and CER (0.279) are all well below thresholds, indicating poor transcription quality.
Many small and large recognition errors occur.

**Performance:**
Latency (1200 ms) ❌ and RTF (0.95) ❌ both fail, meaning the system is too slow and not suitable for real-time use.

🧩 **Interpretation:**
This version struggles both in accuracy and responsiveness.
It likely suffers from a heavier model or unstable decoding under test conditions.

---

📄 **Transcript 3**

**Accuracy:**
TF-IDF (0.933) ✅, WER (0.065) ✅, and CER (0.030) ✅ -- excellent performance across all metrics.
The text is semantically faithful and nearly error-free.

**Performance:**
Latency (400 ms) ✅ and RTF (0.45) ✅ -- fast, responsive, and clearly under all thresholds.

🧩 **Interpretation:**
This configuration delivers both high accuracy and real-time speed.
It's clearly the best result and meets all acceptance criteria.

## References

- https://milvus.io/ai-quick-reference/what-are-common-metrics-for-evaluating-tts-quality
- https://learn.microsoft.com/fr-fr/azure/ai-services/speech-service/how-to-custom-speech-evaluate-data?pivots=ai-foundry-portal
- https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-ai/speech-service/speech-to-text/transparency-note
  https://www.toolify.ai/fr/ai-new-fr/comprendre-et-matriser-tfidf-guide-complet-pour-le-nlp-3514839
