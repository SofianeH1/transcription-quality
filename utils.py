import json
import logging
import re
import unicodedata
from pathlib import Path
from typing import Any


class FileHandler:
    """File I/O utilities for transcription analysis."""

    @staticmethod
    def read_text_file(file_path: str, encoding: str = "utf-8") -> str:
        """
        Read text file with error handling.
        Args:
            file_path (str): Path to the text file.
            encoding (str): File encoding format.
        Returns:
            str: Content of the file.
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            return path.read_text(encoding=encoding).strip()
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            raise

    @staticmethod
    def clean(text: str) -> str:
        """
        Apply configured cleaning operations to text.

        Args:
            text: Input text to clean

        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        text = text.lower()
        # Normalize accents/diacritics to ASCII
        text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode()
        # Remove punctuation characters
        text = re.sub(r"[^\w\s]", "", text)
        # Collapse multiple spaces
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def scan_texts_folder(texts_dir: str = "texts") -> list[tuple[str, str, str]]:
        """Scan the texts folder to produce (gt_path, transcript_path, name) tuples.

        Assumptions:
        - texts/gt contains exactly one ground-truth .txt file.
        - texts/ contains only model-generated .txt files at its root.
        """
        base = Path(texts_dir)
        gt_dir = base / "gt"

        if not gt_dir.exists():
            raise FileNotFoundError(f"Missing ground-truth folder: {gt_dir}")

        gt_files = sorted(gt_dir.glob("*.txt"))
        if not gt_files:
            raise FileNotFoundError(f"No ground-truth .txt file found in {gt_dir}")
        if len(gt_files) > 1:
            logging.warning(
                f"Multiple GT files found in {gt_dir}, using the first: {gt_files[0].name}"
            )
        gt_path = gt_files[0]  # Take the first GT file found

        transcript_files = sorted(p for p in base.glob("*.txt") if p.is_file())
        if not transcript_files:
            logging.warning(f"No transcript files found in {base}")

        pairs: list[tuple[str, str, str]] = []

        texts_dir_str = Path(texts_dir).as_posix().rstrip("/")
        gt_path = f"{texts_dir_str}/gt/{gt_path.name}"
        for idx, hyp in enumerate(transcript_files, start=1):
            name = f"Transcript {idx}"
            hyp_rel = f"{texts_dir_str}/{hyp.name}"
            pairs.append((gt_path, hyp_rel, name))

        return pairs

    @staticmethod
    def write_json_report(
        reports: list[dict[str, Any]], out_path: str = "results/report.json"
    ) -> str:
        """Write evaluation reports to JSON for reuse and automation pipelines.

        Args:
            reports: List of report dictionaries to serialize
            out_path: Destination file path for the JSON report

        Returns:
            The path to the written JSON file as a POSIX string.
        """
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(reports, indent=2), encoding="utf-8")
        logging.info(f"JSON report written to {out.as_posix()}")
        return out.as_posix()
