import argparse
import logging

import jiwer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from metrics_evaluation import MetricsEvaluator
from utils import FileHandler


class TranscriptionAnalyzer:

    def compute_tfidf_cosine_similarity(self, text1: str, text2: str) -> float:
        """Compute TF-IDF cosine similarity"""
        try:
            vectorizer = TfidfVectorizer(lowercase=False)
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(cosine_sim[0][0])
        except Exception as e:
            logging.warning(f"TF-IDF computation failed: {e}")
            return 0.0

    def compute_word_error_rate(self, reference: str, generated_transcription: str) -> float:
        """Compute Word Error Rate using jiwer."""
        try:
            return float(jiwer.wer(reference, generated_transcription))
        except Exception as e:
            logging.warning(f"WER computation failed: {e}")
            return 1.0

    def compute_character_error_rate(self, reference: str, generated_transcription: str) -> float:
        """Compute Character Error Rate using jiwer (CER)."""
        try:
            return float(jiwer.cer(reference, generated_transcription))
        except Exception as e:
            logging.warning(f"CER computation failed: {e}")
            return 1.0

    def compute_all_metrics(self, reference: str, generated_transcription: str) -> dict[str, float]:
        """Compute all quality metrics for a transcription pair."""
        return {
            "tfidf_similarity": self.compute_tfidf_cosine_similarity(
                reference, generated_transcription
            ),
            "word_error_rate": self.compute_word_error_rate(reference, generated_transcription),
            "character_error_rate": self.compute_character_error_rate(
                reference, generated_transcription
            ),
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate transcription quality against a ground-truth transcript."
    )
    parser.add_argument(
        "--texts-dir",
        default="texts",
        help="Directory containing transcripts and a 'gt' subfolder.",
    )
    parser.add_argument(
        "--out", default="results/report.json", help="Output path for the JSON report."
    )
    args = parser.parse_args()

    evaluator = MetricsEvaluator()
    reports = evaluator.evaluate_transcriptions(args.texts_dir, analyzer=TranscriptionAnalyzer())
    out_path = FileHandler.write_json_report(reports, out_path=args.out)
    print(f"\n📝 Saved JSON report to: {out_path}")
    for report in reports:
        global_ok = report["overall_passed"]
        if not global_ok:
            exit(1)
    
