"""
Insurance Claim Classifier with SHAP Explainability
"""
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import shap
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt

class QwenClaimClassifier:
    """
    Qwen-based classifier for insurance claim approval/rejection with SHAP explanations.
    For this demo, we'll use a smaller distilbert model as a proxy since Qwen requires substantial resources.
    """
    
    def __init__(self, model_name: str = "distilbert-base-uncased"):
        """
        Initialize the classifier. Using DistilBERT for demo purposes.
        In production, replace with: "Qwen/Qwen-7B" or fine-tuned version.
        """
        print(f"Loading model: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # For demo: we'll use a simple model and simulate binary classification
        # In production, this would be your fine-tuned Qwen model
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name,
            num_labels=2,
            ignore_mismatched_sizes=True
        )
        self.model.eval()
        print("Model loaded successfully!")
        
    def predict(self, text: str) -> np.ndarray:
        """
        Predict claim approval probability.
        
        Args:
            text: Formatted claim text
            
        Returns:
            Array of probabilities [reject_prob, approve_prob]
        """
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            max_length=512,
            padding=True
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        return probs.numpy()[0]
    
    def predict_batch(self, texts: List[str]) -> np.ndarray:
        """Batch prediction for SHAP"""
        predictions = []
        for text in texts:
            prob = self.predict(text)
            predictions.append(prob)
        return np.array(predictions)
    
    def get_shap_explanation(self, text: str, num_samples: int = 50) -> Dict:
        """
        Generate SHAP explanations for the prediction.
        
        Args:
            text: Input claim text
            num_samples: Number of samples for SHAP (lower = faster)
            
        Returns:
            Dictionary with SHAP values and metadata
        """
        print("Generating SHAP explanation...")
        
        # Tokenize the input
        tokens = self.tokenizer.tokenize(text)
        
        # Create a masker for text data
        masker = shap.maskers.Text(self.tokenizer)
        
        # Create explainer
        explainer = shap.Explainer(
            lambda x: self.predict_batch(x)[:, 1],  # Explain "approve" class
            masker,
            algorithm="permutation"
        )
        
        # Get SHAP values
        shap_values = explainer([text])

        # shap value to display
        shap.plots.text(shap_values, display=False)

        # Save the figure
        plt.savefig('shap_text_plot.png', bbox_inches='tight', dpi=300)
        plt.close()

        display_html = shap.plots.text(shap_values)

        # Save as HTML file
        with open('shap_explain_plot.html', 'w', encoding='utf-8') as f:
            f.write(display_html.html())

        # Extract top features
        values = shap_values.values[0]
        data = shap_values.data[0]
        
        # Get top contributing tokens
        if isinstance(data, str):
            words = data.split()
        else:
            words = [str(d) for d in data]
        
        top_indices = np.argsort(np.abs(values))[-10:][::-1]
        
        top_features = []
        for idx in top_indices:
            if idx < len(words) and idx < len(values):
                top_features.append({
                    'feature': words[idx],
                    'shap_value': float(values[idx]),
                    'impact': 'positive' if values[idx] > 0 else 'negative'
                })
        
        return {
            'shap_values': values,
            'base_value': float(shap_values.base_values[0]) if hasattr(shap_values, 'base_values') else 0.5,
            'top_features': top_features,
            'data': words
        }
    
    def get_simple_explanation(self, text: str) -> Dict:
        """
        Simplified explanation based on keyword matching (fallback method).
        Faster than SHAP, useful for production.
        """
        # Simple rule-based importance (demo)
        keywords = {
            'emergency': 0.3,
            'surgery': 0.25,
            'accident': 0.2,
            'hospital': 0.15,
            'diagnosis': 0.15,
            'fraud': -0.5,
            'suspicious': -0.4,
            'false': -0.3,
            'unauthorized': -0.35
        }
        
        words = text.lower().split()
        features = []
        
        for word, score in keywords.items():
            if word in text.lower():
                features.append({
                    'feature': word,
                    'shap_value': score,
                    'impact': 'positive' if score > 0 else 'negative'
                })
        
        return {
            'top_features': sorted(features, key=lambda x: abs(x['shap_value']), reverse=True),
            'method': 'rule_based'
        }


if __name__ == "__main__":
    # Quick test
    classifier = QwenClaimClassifier()
    
    test_text = """
    Claim ID: CLM-001
    Policy Type: Health Insurance
    Claim Amount: $15000
    Description: Emergency surgery for appendicitis
    """
    
    probs = classifier.predict(test_text)
    print(f"\nPrediction: Approve={probs[1]:.2%}, Reject={probs[0]:.2%}")
    
    explanation = classifier.get_simple_explanation(test_text)
    print(f"\nTop features: {explanation['top_features'][:3]}")
