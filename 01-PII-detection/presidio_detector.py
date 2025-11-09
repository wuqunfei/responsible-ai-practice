"""
Microsoft Presidio PII Detector
Pattern-based detection with 50+ built-in recognizers
"""

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from collections import defaultdict


class PresidioPIIDetector:
    def __init__(self):
        """Initialize Presidio analyzer and anonymizer"""
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        print("✓ Presidio initialized successfully")
        
    def detect(self, text, language='en', threshold=0.5):
        """
        Detect PII using Presidio
        
        Args:
            text: Input text to analyze
            language: Language code (default: 'en')
            threshold: Minimum confidence score (0-1)
            
        Returns:
            List of RecognizerResult objects
        """
        results = self.analyzer.analyze(
            text=text,
            language=language,
            score_threshold=threshold
        )
        return results
    
    def anonymize(self, text, language='en', threshold=0.5, mask_char='*'):
        """
        Detect and anonymize PII
        
        Args:
            text: Input text to anonymize
            language: Language code
            threshold: Minimum confidence score
            mask_char: Character to use for masking
            
        Returns:
            Tuple of (anonymized_text, detection_results)
        """
        analyzer_results = self.detect(text, language, threshold)
        
        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results
        )
        
        return anonymized.text, analyzer_results
    
    def get_summary(self, results):
        """
        Get summary statistics of detected PII
        
        Args:
            results: List of RecognizerResult objects
            
        Returns:
            Dictionary with PII type counts
        """
        summary = defaultdict(int)
        for result in results:
            summary[result.entity_type] += 1
        return dict(summary)
    
    def get_detailed_results(self, text, results):
        """
        Get detailed information about each detection
        
        Args:
            text: Original text
            results: Detection results
            
        Returns:
            List of dictionaries with detection details
        """
        detailed = []
        for result in results:
            detected_text = text[result.start:result.end]
            detailed.append({
                'type': result.entity_type,
                'text': detected_text,
                'start': result.start,
                'end': result.end,
                'score': result.score
            })
        return detailed
    
    def mask_with_type(self, text, language='en', threshold=0.5):
        """
        Mask PII but show the type of entity
        
        Args:
            text: Input text
            language: Language code
            threshold: Confidence threshold
            
        Returns:
            Masked text with entity types shown
        """
        results = self.detect(text, language, threshold)
        
        # Sort by start position in reverse to avoid index shifting
        results = sorted(results, key=lambda x: x.start, reverse=True)
        
        masked_text = text
        for result in results:
            start = result.start
            end = result.end
            entity_type = result.entity_type
            
            replacement = f"<{entity_type}>"
            masked_text = masked_text[:start] + replacement + masked_text[end:]
        
        return masked_text


if __name__ == "__main__":
    # Quick test
    detector = PresidioPIIDetector()
    
    test_text = "John Smith's email is john@example.com and phone is 555-1234"
    
    print("\nTest Detection:")
    results = detector.detect(test_text)
    for result in results:
        print(f"  {result.entity_type}: {test_text[result.start:result.end]}")
    
    print("\nTest Anonymization:")
    anonymized, _ = detector.anonymize(test_text)
    print(f"  {anonymized}")
