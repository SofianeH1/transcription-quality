# Transcription Quality

To learn more about how the metrics were chosen, see the explanations: [methodology.md](./methodology.md).

Evaluate the quality of ASR/transcription outputs against a ground-truth transcript using practical accuracy metrics and performance gates (latency/RTF), all with configurable thresholds.

## Features

- Metrics included:
  - TF-IDF cosine similarity (higher is better)
  - WER -- Word Error Rate (lower is better)
  - CER -- Character Error Rate (lower is better)
  - Latency (ms) and Real-Time Factor (RTF)
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
    texts/latency.json         # Per-file latency/RTF metadata (required)
```

## Assumptions

- Texts are located in the `texts/` folder.
- Ground truth is a single `.txt` file under `texts/gt/`.
- Each generated transcript under `texts/` has a corresponding entry in `texts/latency.json` providing its latency:
  - Either a number in milliseconds, e.g., `"transcript1.txt": 650`, or
  - An object with `latency_ms` and optionally `rtf`, e.g., `"transcript2.txt": { "latency_ms": 1200, "rtf": 0.95 }`.
    .env # Local thresholds (optional)
    .env.example # Example thresholds
    pyproject.toml # Dependencies and tooling

## Installation

This project uses Poetry.

```bash

poetry install
```

## Configure thresholds (.env)

You can override default thresholds using environment variables. Copy `.env.example` to `.env` and adjust as needed.

```env
# Threshold configuration for transcription-quality

#WER_THRESHOLD=0.15
#CER_THRESHOLD=0.10
#TFIDF_THRESHOLD=0.75
#LATENCY_THRESHOLD_MS=1000
#RTF_THRESHOLD=1.0

# Optional: transcriptor metadata (included in report) 
#TRANSCRIPTOR_NAME=MyTranscriptor
#TRANSCRIPTOR_VERSION=1.2.3
#TRANSCRIPTOR_ENVIRONMENT=staging

# Performance gates (lower is better). Override defaults if needed.
# Defaults: LATENCY_THRESHOLD_MS=500, RTF_THRESHOLD=0.8
#LATENCY_THRESHOLD_MS=800
#RTF_THRESHOLD=0.8
```

Notes:

- Invalid values fall back to defaults values.

## Usage

Place your ground-truth file under `texts/gt/` and your generated transcripts (model outputs) as `.txt` files under `texts/`.

Provide per-file latency/RTF metadata in `texts/latency.json` (assume that it's provided by transcription system):

```
{
  "transcript1.txt": { "latency_ms": 510, "rtf": 0.8 }               
  "transcript2.txt": { "latency_ms": 1200, "rtf": 0.95 }
}
```

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
� Thresholds:
	wer_threshold: 0.15
	cer_threshold: 0.1
  tfidf_threshold: 0.75
  latency_threshold_ms: 800
  rtf_threshold: 0.8

📄 Transcript 1 (transcript1.txt)
--------------------------------------------------------------------------------
📊 Metrics:
	TF-IDF Similarity:      0.717  -> pass: False ❌
	Word Error Rate:        0.290  -> pass: False ❌
  Character Error Rate:   0.121  -> pass: False ❌
  Latency (ms):           650    -> pass: True ✅
  Real-Time Factor:       0.720  -> pass: True ✅

	Overall Result:         pass: False ❌
```

The JSON report contains a list of per-transcript entries with metric values, pass/fail flags, and thresholds. Latency/RTF are included.

## CI/CD usage
This tool is designed to be used in CI pipelines. **We assume** the CI job provides the inputs as `.txt` files in the `texts/` folder and a single ground-truth file in `texts/gt/`.

Key points:

- Thresholds are configurable via environment variables, so you can tune gates per environment or branch.
- The command exits with code 1 if any transcript fails the thresholds, so CI pipelines will fail automatically.
- The JSON report is stable and can be archived as a build artifact for later inspection.

Minimal contract:

- Input: `texts/gt/*.txt` (exactly one GT file), `texts/*.txt` (one or more generated transcripts)
- Output: `results/report.json`
- Env vars: `WER_THRESHOLD`, `CER_THRESHOLD`, `TFIDF_THRESHOLD`, `LATENCY_THRESHOLD_MS`, `RTF_THRESHOLD`
- `texts/latency.json` must contain an entry for each transcript in `texts/`.

## Troubleshooting

- Make sure the `texts/gt/` folder contains exactly one `.txt` file.
- If thresholds don’t seem to change, confirm the values in `.env` and that your shell env isn’t overriding them.
- If you see dependency errors, run `poetry install` again to ensure your environment is up to date.

## Possible evolutions

- implement CI and integate in projects
- have the possibility to make metrics optional (more felxibility)
- Generate Html report using jinja template (more readability)

## Possible evolutions

- **CI/CD Integration**: Implement continuous integration workflows and provide integration guides for various CI platforms
- **Configurable Metrics**: Add the ability to make individual metrics optional for greater flexibility in evaluation scenarios
- **HTML Reporting**: Generate comprehensive HTML reports using Jinja2 templates for improved readability and visualizationript using practical accuracy metrics and performance gates (latency/RTF), all with configurable thresholds.
