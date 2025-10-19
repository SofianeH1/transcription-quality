import logging
import os
from pathlib import Path
from typing import Any

from utils import FileHandler
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()


class MetricsEvaluator:
    """Evaluates transcription quality metrics against predefined thresholds."""

    def __init__(self):
        self.wer_threshold: float = self._get_env_float("WER_THRESHOLD", 0.15)
        self.cer_threshold: float = self._get_env_float("CER_THRESHOLD", 0.1)
        self.tfidf_threshold: float = self._get_env_float("TFIDF_THRESHOLD", 0.75)

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

    def evaluate_all_metrics(self, metrics: dict[str, float]) -> dict[str, bool]:
        """
        Evaluate all metrics against their thresholds.

        Args:
            metrics: Dictionary containing metric values

        Returns:
            Dictionary with boolean results for each metric
        """
        return {
            "wer_passed": self.evaluate_wer(metrics.get("word_error_rate", 1.0)),
            "cer_passed": self.evaluate_cer(metrics.get("character_error_rate", 1.0)),
            "tfidf_passed": self.evaluate_tfidf(metrics.get("tfidf_similarity", 0.0)),
        }

    def get_detailed_report(self, metrics: dict[str, float]) -> dict[str, Any]:
        """
        Generate detailed evaluation report.

        Args:
            metrics: Dictionary containing metric values

        Returns:
            Detailed report with scores, evaluations, and overall status
        """
        evaluations = self.evaluate_all_metrics(metrics)
        global_ok = (
            evaluations["tfidf_passed"]
            and evaluations["wer_passed"]
            and evaluations["cer_passed"]
        )
        return {
            "metrics": metrics,
            "evaluations": evaluations,
            "thresholds": {
                "wer_threshold": self.wer_threshold,
                "cer_threshold": self.cer_threshold,
                "tfidf_threshold": self.tfidf_threshold,
            },
            "transcriptor": {
                "name": self.transcriptor_name,
                "version": self.transcriptor_version,
                "environment": self.transcriptor_environment,
            },
            "passed_metrics": sum(evaluations.values()),
            "total_metrics": len(evaluations),
            "overall_passed": global_ok,
        }

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
        tfidf_ok = evaluations["tfidf_passed"]
        wer_ok = evaluations["wer_passed"]
        cer_ok = evaluations["cer_passed"]

        print(
            f"  TF-IDF Similarity:      {metrics['tfidf_similarity']:.3f}  -> pass: {tfidf_ok} {_icon(tfidf_ok)}"
        )
        print(
            f"  Word Error Rate:        {metrics['word_error_rate']:.3f}  -> pass: {wer_ok} {_icon(wer_ok)}"
        )
        print(
            f"  Character Error Rate:   {metrics['character_error_rate']:.3f}  -> pass: {cer_ok} {_icon(cer_ok)}"
        )
        print(f"\n  Overall Result:         pass: {overall_ok} {_icon(overall_ok)}")

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
