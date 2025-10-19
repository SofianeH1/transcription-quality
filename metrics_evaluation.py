import logging
import os
from pathlib import Path
from typing import Any

from utils import FileHandler

def _safe_load_dotenv() -> None:
    """Load environment variables from a .env file if python-dotenv is available."""
    try:
        from dotenv import load_dotenv as _load  # type: ignore
        _load()
    except Exception:
        # Dotenv not installed or failed; ignore silently.
        pass

# Load environment variables from a .env file if present
_safe_load_dotenv()


class MetricsEvaluator:
    """Evaluates transcription quality metrics against predefined thresholds."""

    def __init__(self):
        self.wer_threshold: float = self._get_env_float("WER_THRESHOLD", 0.15)
        self.cer_threshold: float = self._get_env_float("CER_THRESHOLD", 0.1)
        self.tfidf_threshold: float = self._get_env_float("TFIDF_THRESHOLD", 0.75)
        self.latency_threshold_ms: float = self._get_env_float("LATENCY_THRESHOLD_MS", 800.0)
        self.rtf_threshold: float = self._get_env_float("RTF_THRESHOLD", 0.8)

        self.transcriptor_version: str = os.getenv("TRANSCRIPTOR_VERSION", "unknown")
        self.transcriptor_name: str = os.getenv("TRANSCRIPTOR_NAME", "unknown")
        self.transcriptor_environment: str = os.getenv("TRANSCRIPTOR_ENVIRONMENT", "unknown")

    @staticmethod
    def _get_env_float(var_name: str, default: float) -> float:
        """Read an environment variable as float with a safe fallback.

        Args:
            var_name: Name of the environment variable to read.
            default: Default value if the variable is not set or invalid.

        Returns:
            The parsed float value or the default.
        """
        raw = os.getenv(var_name)
        if raw is None or raw.strip() == "":
            return default
        try:
            return float(raw)
        except Exception:
            logging.warning(
                f"Invalid value for {var_name}='{raw}', falling back to default {default}."
            )
            return default

    def evaluate_wer(self, wer_value: float) -> bool:
        """Evaluate if Word Error Rate passes threshold (lower is better)."""
        return wer_value <= self.wer_threshold

    def evaluate_cer(self, cer_value: float) -> bool:
        """Evaluate if Character Error Rate passes threshold (lower is better)."""
        return cer_value <= self.cer_threshold

    def evaluate_tfidf(self, tfidf_value: float) -> bool:
        """Evaluate if TF-IDF similarity passes threshold (higher is better)."""
        return tfidf_value >= self.tfidf_threshold

    def evaluate_latency_ms(self, latency_ms: float) -> bool:
        """Evaluate if latency in milliseconds passes threshold (lower is better).

        Requires LATENCY_THRESHOLD_MS to be configured; if not set, callers
        should skip adding this evaluation.
        """
        return latency_ms <= self.latency_threshold_ms

    def evaluate_rtf(self, rtf_value: float) -> bool:
        """Evaluate if Real-Time Factor passes threshold (lower is better).

        Requires RTF_THRESHOLD to be configured; if not set, callers
        should skip adding this evaluation.
        """
        return rtf_value <= self.rtf_threshold

    def evaluate_all_metrics(self, metrics: dict[str, float]) -> dict[str, bool]:
        """
        Evaluate all metrics against their thresholds.

        Args:
            metrics: Dictionary containing metric values

        Returns:
            Dictionary with boolean results for each applicable metric
        """
        evaluations: dict[str, bool] = {
            "wer_passed": self.evaluate_wer(metrics.get("word_error_rate", 1.0)),
            "cer_passed": self.evaluate_cer(metrics.get("character_error_rate", 1.0)),
            "tfidf_passed": self.evaluate_tfidf(metrics.get("tfidf_similarity", 0.0)),
            "latency_passed": self.evaluate_latency_ms(
                float(metrics.get("latency_ms", float("inf")))
            ),
            "rtf_passed": self.evaluate_rtf(float(metrics.get("rtf", float("inf")))),
        }
        return evaluations

    def get_detailed_report(self, metrics: dict[str, float]) -> dict[str, Any]:
        """
        Generate detailed evaluation report.

        Args:
            metrics: Dictionary containing metric values

        Returns:
            Detailed report with scores, evaluations, and overall status
        """
        evaluations = self.evaluate_all_metrics(metrics)
        # All included evaluations must pass
        global_ok = all(bool(v) for v in evaluations.values())
        result = {
            "metrics": metrics,
            "evaluations": evaluations,
            "thresholds": {
                "wer_threshold": self.wer_threshold,
                "cer_threshold": self.cer_threshold,
                "tfidf_threshold": self.tfidf_threshold,
                "latency_threshold_ms": self.latency_threshold_ms,
                "rtf_threshold": self.rtf_threshold,
            },
            "transcriptor": {
                "name": self.transcriptor_name,
                "version": self.transcriptor_version,
                "environment": self.transcriptor_environment,
            },
            "passed_metrics": sum(1 for v in evaluations.values() if v),
            "total_metrics": len(evaluations),
            "overall_passed": global_ok,
        }
        return result

    def _print_transcriptor_info(self) -> None:
        """Print transcriptor info used to generate the transcriptions."""
        print("📝 Transcriptor Info:")
        print(f"  Name: {self.transcriptor_name}")
        print(f"  Version: {self.transcriptor_version}")
        print(f"  Environment: {self.transcriptor_environment}")
        print("-" * 80)

    def _print_thresholds(self) -> None:
        """Print configured thresholds in a readable format (internal use)."""
        print("📏 Thresholds:")
        print(f"  wer_threshold: {self.wer_threshold}")
        print(f"  cer_threshold: {self.cer_threshold}")
        print(f"  tfidf_threshold: {self.tfidf_threshold}")
        print(f"  latency_threshold_ms: {self.latency_threshold_ms}")
        print(f"  rtf_threshold: {self.rtf_threshold}")

    @staticmethod
    def _print_metrics_and_results(
        name: str,
        hyp_path: str,
        metrics: dict[str, float],
        evaluations: dict[str, bool],
        overall_ok: bool,
    ) -> None:
        
        def _icon(passed: bool) -> str:
            return "✅" if passed else "❌"

        print(f"\n📄 {name} ({Path(hyp_path).name})")
        print("-" * 80)
        print("📊 Metrics:")
        def _print_line(label: str, value: object, ok: bool) -> None:
            # Render value as number when possible, otherwise N/A
            try:
                fv = float(value)  # type: ignore[arg-type]
                text = f"{fv:.3f}"
            except Exception:
                text = "N/A"
            print(f"  {label:<22} {text}  -> pass: {ok} {_icon(ok)}")

        _print_line("TF-IDF Similarity:", metrics.get("tfidf_similarity"), evaluations["tfidf_passed"])  # type: ignore[arg-type]
        _print_line("Word Error Rate:", metrics.get("word_error_rate"), evaluations["wer_passed"])  # type: ignore[arg-type]
        _print_line("Character Error Rate:", metrics.get("character_error_rate"), evaluations["cer_passed"])  # type: ignore[arg-type]
        _print_line("Latency (ms):", metrics.get("latency_ms"), evaluations["latency_passed"])  # type: ignore[arg-type]
        _print_line("Real-Time Factor:", metrics.get("rtf"), evaluations["rtf_passed"])  # type: ignore[arg-type]
        print(f"\n  Overall Result:         pass: {overall_ok} {_icon(overall_ok)}")

    @staticmethod
    def _enrich_with_latency(metrics: dict[str, float], hyp_path: str, latency_map: dict[str, Any]) -> None:
        """Attach latency/rtf values from latency_map to metrics in-place.

        Assumes each entry is of the form: {"latency_ms": <number>, "rtf": <number>}.
        """
        try:
            meta = latency_map[Path(hyp_path).name]
            metrics["latency_ms"] = float(meta["latency_ms"])  # type: ignore[index]
            metrics["rtf"] = float(meta["rtf"])  # type: ignore[index]
        except Exception as e:
            logging.warning(
                f"Could not attach latency/rtf for {Path(hyp_path).name}: {e}"
            )

    def evaluate_transcriptions(
        self, texts_dir: str = "texts", analyzer: Any | None = None
    ) -> list[dict[str, Any]]:
        """
        Evaluate all transcripts in texts_dir against the ground truth and print a report.

        Args:
            texts_dir: Directory containing transcripts and a 'gt' subfolder with ground truth.
            analyzer: Optional TranscriptionAnalyzer instance. If not provided, a local import will be attempted.

        Returns:
            A list of detailed reports, one per transcript.
        """
        pairs = FileHandler.scan_texts_folder(texts_dir)
        latency_map = FileHandler.read_latency_mapping(texts_dir)

        print("=" * 80)
        print("TRANSCRIPTION QUALITY METRICS REPORT")
        print("=" * 80)

        self._print_transcriptor_info()
        self._print_thresholds()

        reports: list[dict[str, Any]] = []
        base_dir = Path(__file__).parent

        for gt_path, hyp_path, name in pairs:
            try:
                abs_gt = (base_dir / gt_path).as_posix()
                abs_hyp = (base_dir / hyp_path).as_posix()
                reference = FileHandler.clean(FileHandler.read_text_file(abs_gt))
                generated_transcription = FileHandler.clean(FileHandler.read_text_file(abs_hyp))

                if analyzer is None:
                    raise ValueError(
                        "No analyzer provided. Pass an instance of TranscriptionAnalyzer "
                        "to evaluate_transcriptions(analyzer=...)."
                    )
                metrics = analyzer.compute_all_metrics(reference, generated_transcription)
                MetricsEvaluator._enrich_with_latency(metrics, hyp_path, latency_map)
                detailed = self.get_detailed_report(metrics)
                MetricsEvaluator._print_metrics_and_results(
                    name,
                    hyp_path,
                    metrics,
                    detailed["evaluations"],
                    detailed["overall_passed"],
                )

                detailed_with_name = {
                    "name": name,
                    "gt_path": gt_path,
                    "hyp_path": hyp_path,
                    **detailed,
                }
                reports.append(detailed_with_name)
            except Exception as e:
                logging.exception(f"Error evaluating {name} ({hyp_path}): {e}")
                print(f"\n❌ Error evaluating {name}: {e}")
        return reports
