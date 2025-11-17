"""
Insurance Claim Classifier with SHAP Explainability using GPT-2
"""
import torch
import numpy as np
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import shap
from typing import Dict, List
import warnings
import re
import os
warnings.filterwarnings('ignore')
import matplotlib.pyplot as plt


class GPT2ClaimClassifier:
    """
    GPT-2-based classifier for insurance claim approval/rejection with SHAP explanations.
    """
    
    def __init__(self, model_name: str = "gpt2"):
        """
        Initialize the classifier with GPT-2 model.
        
        Available models:
        - "gpt2" (124M params) - Fastest, lightweight
        - "gpt2-medium" (355M params) - Balanced
        - "gpt2-large" (774M params) - Better accuracy
        - "gpt2-xl" (1.5B params) - Best accuracy
        """
        print(f"Loading model: {model_name}...")
        print("This may take a moment for the first run...")
        
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        
        # Set pad token (GPT-2 doesn't have one by default)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model.config.pad_token_id = self.model.config.eos_token_id
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = self.model.to(self.device)
        self.model.eval()
        
        print(f"Model loaded successfully on {self.device}!")
        print(f"Model size: {model_name} ({self._get_model_params()}M parameters)")
        
    def _get_model_params(self) -> int:
        """Get number of model parameters in millions"""
        return sum(p.numel() for p in self.model.parameters()) // 1_000_000
        
    def _create_classification_prompt(self, claim_text: str) -> str:
        """Create a prompt for GPT-2 to classify claims"""
        prompt = f"""Insurance Claim Classification Task:

{claim_text}

Based on the above claim information, this claim should be:
Decision: """
        return prompt
        print(f"Model size: {model_name} ({self._get_model_params()}M parameters)")
    
    def predict(self, text: str) -> np.ndarray:
        """
        Predict claim approval probability using GPT-2.
        
        Args:
            text: Formatted claim text
            
        Returns:
            Array of probabilities [reject_prob, approve_prob]
        """
        prompt = self._create_classification_prompt(text)
        
        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=30,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                num_return_sequences=1
            )
        
        # Decode response
        response = self.tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:], 
            skip_special_tokens=True
        ).strip()
        
        # Parse response
        return self._parse_response(response, text)
    
    def _parse_response(self, response: str, claim_text: str) -> np.ndarray:
        """
        Parse model response to extract decision and confidence.
        Uses both GPT-2 output and rule-based analysis.
        """
        response_upper = response.upper().strip()
        
        # Check explicit approval/rejection in response
        has_approve = "APPROVE" in response_upper or "ACCEPT" in response_upper or "YES" in response_upper
        has_reject = "REJECT" in response_upper or "DENY" in response_upper or "DENIED" in response_upper or "NO" in response_upper
        
        # Rule-based scoring as backup
        approval_score = self._calculate_approval_score(claim_text)
        
        # Combine GPT-2 output with rule-based analysis
        if has_approve and not has_reject:
            # Model says approve
            confidence = min(0.6 + approval_score * 0.3, 0.95)
        elif has_reject and not has_approve:
            # Model says reject
            confidence = min(0.6 + (1 - approval_score) * 0.3, 0.95)
        else:
            # Unclear or both mentioned, use rule-based score
            confidence = approval_score
        
        # Determine final decision
        is_approved = confidence > 0.5
        
        if is_approved:
            return np.array([1 - confidence, confidence])  # [reject_prob, approve_prob]
        else:
            return np.array([confidence, 1 - confidence])
    
    def _calculate_approval_score(self, text: str) -> float:
        """Calculate approval probability based on keywords"""
        text_lower = text.lower()
        
        # Positive indicators (support approval)
        positive_keywords = {
            'emergency': 0.15,
            'urgent': 0.12,
            'necessary': 0.12,
            'required': 0.10,
            'surgery': 0.12,
            'accident': 0.10,
            'injury': 0.10,
            'hospital': 0.08,
            'diagnosis': 0.08,
            'doctor': 0.06,
            'physician': 0.06,
            'treatment': 0.08,
            'confirmed': 0.08,
            'medical': 0.05,
        }
        
        # Negative indicators (support rejection)
        negative_keywords = {
            'elective': -0.15,
            'cosmetic': -0.18,
            'unnecessary': -0.15,
            'optional': -0.12,
            'fraud': -0.25,
            'suspicious': -0.20,
            'false': -0.18,
            'unauthorized': -0.18,
            'excessive': -0.12,
            'unreasonable': -0.12,
        }
        
        score = 0.5  # Start neutral
        
        # Add positive scores
        for keyword, weight in positive_keywords.items():
            if keyword in text_lower:
                score += weight
        
        # Add negative scores
        for keyword, weight in negative_keywords.items():
            if keyword in text_lower:
                score += weight
        
        # Check amount (if very high, slightly reduce confidence)
        amount_match = re.search(r'\$?\s*(\d+,?\d*)', text)
        if amount_match:
            try:
                amount = int(amount_match.group(1).replace(',', ''))
                if amount > 100000:
                    score -= 0.05
                elif amount > 250000:
                    score -= 0.10
            except:
                pass
        
        # Clamp between 0.2 and 0.95
        return max(0.2, min(0.95, score))
    
    def predict_batch(self, texts: List[str]) -> np.ndarray:
        """Batch prediction for SHAP"""
        predictions = []
        for text in texts:
            prob = self.predict(text)
            predictions.append(prob)
        return np.array(predictions)
    
    def _simple_predict_function(self, texts):
        """Simplified prediction function for SHAP (returns only approve probability)"""
        if isinstance(texts, str):
            texts = [texts]
        
        results = []
        for text in texts:
            probs = self.predict(text)
            results.append(probs[1])  # Return approve probability
        
        return np.array(results)
    
    def get_shap_explanation(self, text: str, num_samples: int = 100) -> Dict:
        """
        Generate SHAP explanations for the prediction with visualization export.
        
        Args:
            text: Input claim text
            num_samples: Number of samples for SHAP (lower = faster)
            
        Returns:
            Dictionary with SHAP values, metadata, and file paths
        """
        print("Generating SHAP explanation (this may take 1-2 minutes)...")
        
        # Create output directory
        os.makedirs('outputs', exist_ok=True)
        
        # Create a partition explainer for text
        explainer = shap.Explainer(
            self._simple_predict_function,
            self.tokenizer
        )
        
        # Get SHAP values
        shap_values = explainer([text], max_evals=num_samples)
        
        # Generate and save text plot as HTML
        print("Generating SHAP visualization...")
        html_output = shap.plots.text(shap_values[0], display=False)
        
        # Save HTML
        html_path = 'outputs/shap_explanation.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>SHAP Explanation - Insurance Claim</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>SHAP Explanation for Insurance Claim</h1>
        <p><strong>Generated:</strong> {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <div id="shap-plot">
            {html_output.html() if hasattr(html_output, 'html') else str(html_output)}
        </div>
    </div>
</body>
</html>""")
        
        print(f"✓ SHAP HTML saved to: {html_path}")
        
        # Try to save as image using matplotlib
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Create a simple bar plot of top features
            values = shap_values.values[0]
            data = shap_values.data[0]
            
            if isinstance(data, str):
                words = data.split()
            else:
                words = [str(d) for d in data]
            
            # Get top 10 features by absolute SHAP value
            top_indices = np.argsort(np.abs(values))[-10:][::-1]
            top_words = [words[i] if i < len(words) else f"token_{i}" for i in top_indices]
            top_values = [values[i] for i in top_indices]
            
            colors = ['green' if v > 0 else 'red' for v in top_values]
            
            ax.barh(range(len(top_words)), top_values, color=colors, alpha=0.6)
            ax.set_yticks(range(len(top_words)))
            ax.set_yticklabels(top_words)
            ax.set_xlabel('SHAP Value (Impact on Approval)', fontsize=12)
            ax.set_title('Top Features Influencing Claim Decision', fontsize=14, fontweight='bold')
            ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
            ax.grid(axis='x', alpha=0.3)
            
            plt.tight_layout()
            
            img_path = 'outputs/shap_explanation.png'
            plt.savefig(img_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✓ SHAP image saved to: {img_path}")
            
        except Exception as e:
            print(f"Warning: Could not save image plot: {e}")
            img_path = None
        
        # Extract top features
        values = shap_values.values[0]
        data = shap_values.data[0]
        
        if isinstance(data, str):
            words = data.split()
        else:
            words = [str(d) for d in data]
        
        top_indices = np.argsort(np.abs(values))[-15:][::-1]
        
        top_features = []
        for idx in top_indices:
            if idx < len(words) and idx < len(values):
                top_features.append({
                    'feature': words[idx],
                    'shap_value': float(values[idx]),
                    'impact': 'positive' if values[idx] > 0 else 'negative'
                })
        
        return {
            'shap_values': values.tolist() if hasattr(values, 'tolist') else values,
            'base_value': float(shap_values.base_values[0]) if hasattr(shap_values, 'base_values') else 0.5,
            'top_features': top_features,
            'data': words,
            'html_path': html_path,
            'image_path': img_path,
            'method': 'shap'
        }
    
    def get_simple_explanation(self, text: str) -> Dict:
        """
        Simplified explanation based on keyword matching (fallback method).
        Faster than SHAP, useful for quick processing.
        """
        print("Generating simple rule-based explanation...")
        
        # Enhanced rule-based importance scoring
        keywords = {
            'emergency': 0.35,
            'surgery': 0.30,
            'accident': 0.25,
            'hospital': 0.20,
            'diagnosis': 0.18,
            'necessary': 0.15,
            'confirmed': 0.15,
            'doctor': 0.12,
            'treatment': 0.12,
            'injury': 0.15,
            'fraud': -0.50,
            'suspicious': -0.45,
            'false': -0.40,
            'unauthorized': -0.40,
            'elective': -0.25,
            'cosmetic': -0.30,
            'unnecessary': -0.25,
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
        
        # Add some amount-based heuristics
        amount_match = re.search(r'\$?([\d,]+)', text)
        if amount_match:
            amount = int(amount_match.group(1).replace(',', ''))
            if amount > 100000:
                features.append({
                    'feature': f'high_amount_${amount:,}',
                    'shap_value': -0.20,
                    'impact': 'negative'
                })
        
        return {
            'top_features': sorted(features, key=lambda x: abs(x['shap_value']), reverse=True),
            'method': 'rule_based',
            'html_path': None,
            'image_path': None
        }


if __name__ == "__main__":
    # Quick test
    print("="*70)
    print("Testing GPT-2 Claim Classifier with SHAP")
    print("="*70)
    
    classifier = GPT2ClaimClassifier()
    
    test_text = """
Claim ID: CLM-001
Policy Type: Health Insurance
Claim Amount: $15,000
Description: Emergency surgery for appendicitis with necessary hospital stay
Medical Reports: Confirmed diagnosis by physician, emergency procedure required
Previous Claims: 2
Policy Duration: 24 months
"""
    
    print("\nRunning prediction...")
    probs = classifier.predict(test_text)
    print(f"Prediction: Approve={probs[1]:.2%}, Reject={probs[0]:.2%}")
    
    print("\nGenerating SHAP explanation...")
    explanation = classifier.get_shap_explanation(test_text, num_samples=50)
    
    print(f"\nTop features influencing decision:")
    for feat in explanation['top_features'][:5]:
        direction = "→ APPROVE" if feat['shap_value'] > 0 else "→ REJECT"
        print(f"  • {feat['feature']}: {feat['shap_value']:+.3f} {direction}")
    
    print(f"\nVisualization files:")
    print(f"  • HTML: {explanation.get('html_path', 'N/A')}")
    print(f"  • Image: {explanation.get('image_path', 'N/A')}")
