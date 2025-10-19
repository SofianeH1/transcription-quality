# Transcription Quality

To learn more about how the metrics were chosen, see the explanations: [methodology.md](./methodology.md).

Evaluate the quality of ASR/transcription outputs against a ground-truth transcript using three practical metrics and configurable thresholds.

## Features

- Metrics included:
  - TF-IDF cosine similarity (higher is better)
  - WER — Word Error Rate (lower is better)
  - CER — Character Error Rate (lower is better)
- Flexible thresholds via environment variables (.env)
- Simple CLI to evaluate a folder of transcripts
- Saves a structured JSON report for automation pipelines

## Project structure

```
transcription-quality/
	analyzer.py                # CLI entry and metric computations
	metrics_evaluation.py      # Thresholding, reporting, and orchestration
	utils.py                   # File I/O and text normalization
	texts/                     # Sample data: transcripts and ground-truth
		gt/transcript_gt.txt
		transcript1.txt
		transcript2.txt
		transcript3.txt
	results/report.json        # Generated report (output)
	.env                       # Local thresholds (optional)
	.env.example               # Example thresholds
	pyproject.toml             # Dependencies and tooling
```

## Installation

This project uses Poetry.

```bash

poetry install
```

## Configure thresholds (.env)

You can override default thresholds using environment variables. Copy `.env.example` to `.env` and adjust as needed.

```env
# Lower is better
WER_THRESHOLD=0.15
CER_THRESHOLD=0.10

# Higher is better
TFIDF_THRESHOLD=0.75

# Optional: transcriptor metadata (included in report and console)
TRANSCRIPTOR_NAME=MyTranscriptor
TRANSCRIPTOR_VERSION=1.2.3
TRANSCRIPTOR_ENVIRONMENT=staging
```

Notes:

- OS environment variables take precedence over values in `.env`.
- Invalid values fall back to defaults values.

## Usage

Place your ground-truth file under `texts/gt/` and your generated transcripts (model outputs) as `.txt` files under `texts/`.

Run the analyzer:

```bash
poetry run python analyzer.py --texts-dir texts --out results/report.json
```

Arguments:

- `--texts-dir` (default: `texts`): Folder containing transcripts and a `gt` subfolder.
- `--out` (default: `results/report.json`): Output path for the JSON report.

Example output (console):

```
================================================================================
TRANSCRIPTION QUALITY METRICS REPORT
================================================================================
� Transcriptor Info:
  Name: MyTranscriptor
  Version: 1.2.3
  Environment: staging
--------------------------------------------------------------------------------
�📏 Thresholds:
	wer_threshold: 0.15
	cer_threshold: 0.1
	tfidf_threshold: 0.75

📄 Transcript 1 (transcript1.txt)
--------------------------------------------------------------------------------
📊 Metrics:
	TF-IDF Similarity:      0.717  -> pass: False ❌
	Word Error Rate:        0.290  -> pass: False ❌
	Character Error Rate:   0.121  -> pass: False ❌

	Overall Result:         pass: False ❌
```

The JSON report contains a list of per-transcript entries with metric values, pass/fail flags, and thresholds.

## CI/CD usage

This tool is designed to be used in CI pipelines. We assume your CI job provides the inputs as `.txt` files in the `texts/` folder and a single ground-truth file in `texts/gt/`.

Key points:

- Thresholds are configurable via environment variables, so you can tune gates per environment or branch.
- The command exits with code 1 if any transcript fails the thresholds, so CI pipelines will fail automatically.
- The JSON report is stable and can be archived as a build artifact for later inspection.

Minimal contract:

- Input: `texts/gt/*.txt` (exactly one GT file), `texts/*.txt` (one or more generated transcripts)
- Output: `results/report.json`
- Env vars: `WER_THRESHOLD`, `CER_THRESHOLD`, `TFIDF_THRESHOLD`

## JSON schema (simplified)

Each entry in `report.json` looks like:

```json
{
  "name": "Transcript 1",
  "gt_path": "texts/gt/transcript_gt.txt",
  "hyp_path": "texts/transcript1.txt",
  "metrics": {
    "tfidf_similarity": 0.717,
    "word_error_rate": 0.29,
    "character_error_rate": 0.121
  },
  "evaluations": {
    "wer_passed": false,
    "cer_passed": false,
    "tfidf_passed": false
  },
  "thresholds": {
    "wer_threshold": 0.15,
    "cer_threshold": 0.1,
    "tfidf_threshold": 0.75
  },
  "transcriptor": {
    "name": "MyTranscriptor",
    "version": "1.2.3",
    "environment": "staging"
  },
  "passed_metrics": 1,
  "total_metrics": 3,
  "overall_passed": false
}
```

Run the analyzer locally:

```bash
poetry run python analyzer.py --texts-dir texts --out results/report.json
```

## Troubleshooting

- Make sure the `texts/gt/` folder contains exactly one `.txt` file.
- If thresholds don’t seem to change, confirm the values in `.env` and that your shell env isn’t overriding them.
- If you see dependency errors, run `poetry install` again to ensure your environment is up to date.
