from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
import Levenshtein
import logging

import Levenshtein
import jiwer
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util
from nltk.metrics import jaccard_distance

from utils import FileHandler


class TranscriptionAnalyzer:

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Initialize analyzer with sentence transformer model."""
        self.model = SentenceTransformer(model_name)

    def compute_tfidf_cosine_similarity(self, text1: str, text2: str) -> float:
        """Computes various textual analysis metrics for transcriptions."""
        try:
            vectorizer = TfidfVectorizer(lowercase=False)  # Already cleaned
            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return float(cosine_sim[0][0])
        except Exception as e:
            logging.warning(f"TF-IDF computation failed: {e}")
            return 0.0
        
    def compute_levenshtein_similarity(self, text1: str, text2: str) -> float:
        """Compute normalized Levenshtein similarity (0-1 scale)."""
        try:
            distance = Levenshtein.distance(text1, text2)
            max_length = max(len(text1), len(text2))
            if max_length == 0:
                return 1.0
            # Normalized distance proportionally to the length of the longer string to make it more meaningful
            similarity = 1.0 - (distance / max_length)
            return float(similarity)
        except Exception as e:
            logging.warning(f"Levenshtein computation failed: {e}")
            return 0.0
        
    def compute_embedding_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity using sentence transformers."""
        try:
            embeddings = self.model.encode([text1, text2], convert_to_tensor=True)
            cosine_sim = util.pytorch_cos_sim(embeddings[0], embeddings[1])
            return float(cosine_sim.item())
        except Exception as e:
            logging.warning(f"Embedding computation failed: {e}")
            return 0.0
        
    def compute_jaccard_similarity(self, ref: str, hyp: str) -> float:
        """Compute Jaccard similarity using NLTK jaccard_distance."""
        try:
            ref_words = set(ref.split())
            hyp_words = set(hyp.split())
            
            if not ref_words and not hyp_words:
                return 1.0
            if not ref_words or not hyp_words:
                return 0.0
                
            distance = jaccard_distance(ref_words, hyp_words)
            return 1.0 - distance
        except Exception as e:
            logging.warning(f"Jaccard computation failed: {e}")
            return 0.0
        
    def compute_word_error_rate(self, reference: str, hypothesis: str) -> float:
        """Compute Word Error Rate using jiwer."""
        try:
            return jiwer.wer(reference, hypothesis)
        except Exception as e:
            logging.warning(f"WER computation failed: {e}")
            return 1.0
        
    def compute_token_error_rate(self, reference: str, hypothesis: str) -> float:
        """Compute Token Error Rate using jiwer."""
        try:
            return jiwer.cer(reference, hypothesis)
        except Exception as e:
            logging.warning(f"TER computation failed: {e}")
            return 1.0
    
    def compute_all_metrics(self, reference: str, hypothesis: str) -> dict:
        """Compute all quality metrics for a transcription pair."""
        return {
            'tfidf_similarity': self.compute_tfidf_cosine_similarity(reference, hypothesis),
            'levenshtein_similarity': self.compute_levenshtein_similarity(reference, hypothesis),
            'embedding_similarity': self.compute_embedding_similarity(reference, hypothesis),
            'jaccard_similarity': self.compute_jaccard_similarity(reference, hypothesis),
            'word_error_rate': self.compute_word_error_rate(reference, hypothesis),
            'character_error_rate': self.compute_token_error_rate(reference, hypothesis)
        }
        

def main():
    # Initialize analyzer
    analyzer = TranscriptionAnalyzer()
    
    # Test multiple transcript pairs
    test_pairs = [
        ("texts/transcript_gt.txt", "texts/transcript1.txt", "Transcript 1"),
        ("texts/transcript_gt.txt", "texts/transcript2.txt", "Transcript 2"),
        ("texts/transcript_gt.txt", "texts/transcript3.txt", "Transcript 3"),
    ]
    
    print("=" * 80)
    print("TRANSCRIPTION QUALITY METRICS REPORT")
    print("=" * 80)
    
    for ref_path, hyp_path, name in test_pairs:
        try:
            # Load and clean texts
            reference = FileHandler.clean(FileHandler.read_text_file(ref_path))
            hypothesis = FileHandler.clean(FileHandler.read_text_file(hyp_path))
            
            # Compute all metrics
            metrics = analyzer.compute_all_metrics(reference, hypothesis)
            
            # Print results
            print(f"\n📄 {name}")
            print("-" * 50)
            
            print("📊 Computed Metrics:")
            print(f"  TF-IDF Similarity:      {metrics['tfidf_similarity']:.3f}")
            print(f"  Levenshtein Similarity: {metrics['levenshtein_similarity']:.3f}")
            print(f"  Embedding Similarity:   {metrics['embedding_similarity']:.3f}")
            print(f"  Jaccard Similarity:     {metrics['jaccard_similarity']:.3f}")
            print(f"  Word Error Rate:        {metrics['word_error_rate']:.3f}")
            print(f"  Character Error Rate:   {metrics['character_error_rate']:.3f}")
                
        except Exception as e:
            print(f"\n❌ Error evaluating {name}: {e}")


if __name__ == "__main__":
    main()

   
 