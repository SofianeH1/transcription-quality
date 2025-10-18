
from pathlib import Path
import logging
import re
import unicodedata

class FileHandler:
    """File I/O utilities for transcription analysis."""
    
    @staticmethod
    def read_text_file(file_path: str, encoding: str = 'utf-8') -> str:
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
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        text = text.replace("'", "'").replace("–", "-")
        return text