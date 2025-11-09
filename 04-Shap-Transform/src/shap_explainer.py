"""
SHAP Explainer for GPT-based Pet Insurance Claims
Main module for model explanation and interpretation
"""

import shap
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class PetClaimExplainer:
    """Main class for explaining pet insurance claim decisions using SHAP"""
    
    def __init__(self, model_name: str = "gpt2", device: str = None):
        """
        Initialize the explainer with a GPT model
        
        Args:
            model_name: HuggingFace model name or path
            device: Device to run model on (cuda/cpu)
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_name, num_labels=2
        ).to(self.device)
        
        # Set pad token if not exists
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Initialize SHAP explainer
        self.explainer = None
        self._setup_explainer()
    
    def _setup_explainer(self):
        """Setup SHAP explainer for the model"""
        def predict_proba(texts: List[str]) -> np.ndarray:
            """Prediction function for SHAP"""
            inputs = self.tokenizer(
                texts, 
                return_tensors="pt", 
                padding=True, 
                truncation=True,
                max_length=512
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)
            
            return probs.cpu().numpy()
        
        # Create SHAP explainer
        self.explainer = shap.Explainer(
            predict_proba,
            self.tokenizer,
            output_names=["Reject", "Approve"]
        )
    
    def explain_claim(self, claim_text: str) -> Dict:
        """
        Generate SHAP explanation for a single claim
        
        Args:
            claim_text: Text of the insurance claim
            
        Returns:
            Dictionary containing explanation details
        """
        # Get SHAP values
        shap_values = self.explainer([claim_text])
        
        # Get prediction
        inputs = self.tokenizer(
            claim_text, 
            return_tensors="pt", 
            truncation=True
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            prediction = torch.argmax(probs, dim=-1).item()
            confidence = probs[0][prediction].item()
        
        # Extract token importance
        tokens = self.tokenizer.tokenize(claim_text)
        token_importance = shap_values[0].values[:, 1]  # For approval class
        
        # Find most influential tokens
        important_tokens = [
            (token, float(imp)) 
            for token, imp in zip(tokens, token_importance) 
            if abs(imp) > 0.1
        ]
        important_tokens.sort(key=lambda x: abs(x[1]), reverse=True)
        
        return {
            'prediction': 'Approved' if prediction == 1 else 'Rejected',
            'confidence': float(confidence),
            'shap_values': shap_values,
            'influential_tokens': important_tokens[:5],  # Top 5
            'raw_tokens': tokens,
            'raw_importance': token_importance.tolist()
        }
    
    def explain_batch(self, claims: List[str], batch_size: int = 8) -> List[Dict]:
        """
        Generate explanations for multiple claims
        
        Args:
            claims: List of claim texts
            batch_size: Batch size for processing
            
        Returns:
            List of explanation dictionaries
        """
        explanations = []
        
        for i in range(0, len(claims), batch_size):
            batch = claims[i:i + batch_size]
            for claim in batch:
                try:
                    explanation = self.explain_claim(claim)
                    explanations.append(explanation)
                except Exception as e:
                    print(f"Error processing claim: {e}")
                    explanations.append({
                        'error': str(e),
                        'prediction': None,
                        'confidence': 0.0
                    })
        
        return explanations
    
    def get_decision_rules(self, explanations: List[Dict], min_support: float = 0.1) -> Dict:
        """
        Extract decision rules from multiple explanations
        
        Args:
            explanations: List of explanation dictionaries
            min_support: Minimum support threshold for rules
            
        Returns:
            Dictionary of decision patterns
        """
        approved_tokens = []
        rejected_tokens = []
        
        for exp in explanations:
            if exp.get('prediction') == 'Approved':
                approved_tokens.extend([
                    (token, imp) 
                    for token, imp in exp.get('influential_tokens', [])
                    if imp > 0
                ])
            elif exp.get('prediction') == 'Rejected':
                rejected_tokens.extend([
                    (token, imp) 
                    for token, imp in exp.get('influential_tokens', [])
                    if imp < 0
                ])
        
        # Aggregate token importance
        def aggregate_tokens(token_list):
            token_dict = {}
            for token, imp in token_list:
                if token in token_dict:
                    token_dict[token].append(imp)
                else:
                    token_dict[token] = [imp]
            
            # Calculate average importance
            aggregated = {
                token: {
                    'avg_importance': np.mean(imps),
                    'frequency': len(imps),
                    'support': len(imps) / len(explanations)
                }
                for token, imps in token_dict.items()
            }
            
            # Filter by minimum support
            return {
                k: v for k, v in aggregated.items() 
                if v['support'] >= min_support
            }
        
        rules = {
            'approval_indicators': aggregate_tokens(approved_tokens),
            'rejection_indicators': aggregate_tokens(rejected_tokens),
            'total_claims_analyzed': len(explanations)
        }
        
        return rules
