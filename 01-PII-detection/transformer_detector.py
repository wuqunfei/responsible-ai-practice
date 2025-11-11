"""
Transformer-based PII Detector (ab-ai/pii_model style)
Context-aware AI detection using token classification
"""

import re
from collections import defaultdict
import os



class TransformerPIIDetector:
    def __init__(self, model_name="lakshyakh93/deberta_finetuned_pii", local_model_path="models/transformer_pii"):
        """
        Initialize transformer-based PII detector
        
        Args:
            model_name: HuggingFace model identifier
            local_model_path: Path to save/load the model locally
        """
        self.model_loaded = False
        
        try:
            from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
            import torch
            
            # Ensure the local model directory exists
            os.makedirs(local_model_path, exist_ok=True)

            self.device = 0 if torch.cuda.is_available() else -1
            
            print(f"Attempting to load transformer model from: {local_model_path}")

            try:
                # Try to load from local path
                self.tokenizer = AutoTokenizer.from_pretrained(local_model_path)
                self.model = AutoModelForTokenClassification.from_pretrained(local_model_path)
                print("✓ Model loaded successfully from local path.")
            except (OSError, ValueError):
                # If it fails, download from Hugging Face and save locally
                print(f"Could not load from local path. Downloading from Hugging Face: {model_name}")
                print("This may take a minute...")
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForTokenClassification.from_pretrained(model_name)
                
                print(f"Saving model to {local_model_path} for future use.")
                self.tokenizer.save_pretrained(local_model_path)
                self.model.save_pretrained(local_model_path)
                print("✓ Model downloaded and saved locally.")

            
            self.pipeline = pipeline(
                "token-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                aggregation_strategy="simple",
                device=self.device
            )
            
            self.model_loaded = True
            device_name = "GPU" if self.device == 0 else "CPU"
            print(f"✓ Transformer model ready on {device_name}")
            
        except Exception as e:
            print(f"⚠ Could not load transformer model: {e}")
            print("✓ Using fallback regex-based detection")
            self.model_loaded = False
    
    def detect(self, text, threshold=0.5):
        """
        Detect PII using transformer model or fallback
        
        Args:
            text: Input text to analyze
            threshold: Minimum confidence score (0-1)
            
        Returns:
            List of detected entities
        """
        if not self.model_loaded:
            return self._fallback_detect(text)
        
        # Split text into chunks due to token limits
        max_length = 450  # Leave room for special tokens
        chunks = self._split_text(text, max_length)
        
        all_entities = []
        offset = 0
        
        for chunk in chunks:
            try:
                results = self.pipeline(chunk)
                
                # Adjust positions based on offset
                for entity in results:
                    if entity['score'] >= threshold:
                        entity['start'] += offset
                        entity['end'] += offset
                        all_entities.append(entity)
                
                offset += len(chunk)
            except Exception as e:
                print(f"⚠ Error processing chunk: {e}")
                continue
        
        return all_entities
    
    def _split_text(self, text, max_length):
        """
        Split text into chunks that fit model's token limit
        
        Args:
            text: Text to split
            max_length: Maximum characters per chunk
            
        Returns:
            List of text chunks
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for space
            
            if current_length + word_length > max_length:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _fallback_detect(self, text):
        """
        Regex-based fallback detection when model unavailable
        
        Args:
            text: Input text
            
        Returns:
            List of detected entities
        """
        patterns = {
            'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'PHONE': r'[\+]?[(]?\d{1,3}[)]?[-\s\.]?\(?\d{3}\)?[-\s\.]?\d{3}[-\s\.]?\d{4}',
            'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
            'CREDIT_CARD': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'IP_ADDRESS': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'DATE': r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b',
            'URL': r'https?://[^\s]+',
            'ZIPCODE': r'\b\d{5}(?:-\d{4})?\b',
        }
        
        entities = []
        for entity_type, pattern in patterns.items():
            for match in re.finditer(pattern, text):
                entities.append({
                    'entity_group': entity_type,
                    'word': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'score': 1.0
                })
        
        return entities
    
    def anonymize(self, text, threshold=0.5, show_type=True):
        """
        Detect and anonymize PII
        
        Args:
            text: Input text
            threshold: Confidence threshold
            show_type: Show entity type in replacement
            
        Returns:
            Tuple of (anonymized_text, detection_results)
        """
        entities = self.detect(text, threshold)
        
        # Sort by start position in reverse
        entities = sorted(entities, key=lambda x: x['start'], reverse=True)
        
        anonymized_text = text
        for entity in entities:
            start = entity['start']
            end = entity['end']
            entity_type = entity['entity_group']
            
            if show_type:
                replacement = f"<{entity_type}>"
            else:
                replacement = "<REDACTED>"
            
            anonymized_text = anonymized_text[:start] + replacement + anonymized_text[end:]
        
        return anonymized_text, entities
    
    def get_summary(self, entities):
        """
        Get summary statistics of detected entities
        
        Args:
            entities: List of detected entities
            
        Returns:
            Dictionary with entity type counts
        """
        summary = defaultdict(int)
        for entity in entities:
            summary[entity['entity_group']] += 1
        return dict(summary)
    
    def get_detailed_results(self, entities):
        """
        Get detailed information about each detection
        
        Args:
            entities: Detection results
            
        Returns:
            List of dictionaries with detection details
        """
        detailed = []
        for entity in entities:
            detailed.append({
                'type': entity['entity_group'],
                'text': entity['word'],
                'start': entity['start'],
                'end': entity['end'],
                'score': entity['score']
            })
        return detailed


if __name__ == "__main__":
    # Quick test
    detector = TransformerPIIDetector()
    
    test_text = "John Smith's email is john@example.com and phone is 555-1234"
    
    print("\nTest Detection:")
    results = detector.detect(test_text)
    for result in results:
        print(f"  {result['entity_group']}: {result['word']}")
    
    print("\nTest Anonymization:")
    anonymized, _ = detector.anonymize(test_text)
    print(f"  {anonymized}")
