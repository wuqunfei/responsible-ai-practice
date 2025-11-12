"""
Lightweight Demo Version - Insurance Claim AI Agent
No heavy dependencies required - demonstrates the architecture
"""
import json
import random
from datetime import datetime
from typing import Dict, List, Literal, TypedDict
import operator


class ClaimState(TypedDict):
    """State object for the claim processing workflow"""
    claim_data: dict
    claim_text: str
    prediction: str
    confidence: float
    shap_explanation: dict
    decision_reasoning: str
    messages: list
    requires_human_review: bool


class MockClassifier:
    """Mock classifier for demo purposes"""
    
    def __init__(self):
        print("Initializing Mock Classifier (Demo Mode)...")
        self.keywords = {
            'emergency': 0.3,
            'surgery': 0.25,
            'accident': 0.2,
            'hospital': 0.15,
            'diagnosis': 0.15,
            'necessary': 0.1,
            'confirmed': 0.1,
            'fraud': -0.5,
            'suspicious': -0.4,
            'elective': -0.3,
            'cosmetic': -0.35,
            'unauthorized': -0.35
        }
    
    def predict(self, text: str) -> tuple:
        """Simulate prediction based on keywords"""
        text_lower = text.lower()
        score = 0.5  # Base score
        
        # Adjust based on keywords
        for word, weight in self.keywords.items():
            if word in text_lower:
                score += weight
        
        # Adjust based on claim amount (from text)
        if '$' in text:
            try:
                amount_str = text.split('$')[1].split()[0].replace(',', '')
                amount = float(amount_str)
                if amount > 100000:
                    score -= 0.2  # High claims are riskier
                elif amount < 5000:
                    score += 0.1  # Low claims easier to approve
            except:
                pass
        
        # Clip to valid probability range
        score = max(0.1, min(0.9, score))
        
        # Add some randomness for realism
        score += random.uniform(-0.05, 0.05)
        score = max(0.1, min(0.9, score))
        
        return (1 - score, score)  # (reject_prob, approve_prob)
    
    def get_explanation(self, text: str) -> Dict:
        """Generate explanation based on keywords found"""
        text_lower = text.lower()
        features = []
        
        for word, impact in self.keywords.items():
            if word in text_lower:
                features.append({
                    'feature': word,
                    'shap_value': impact,
                    'impact': 'positive' if impact > 0 else 'negative'
                })
        
        # Sort by absolute impact
        features.sort(key=lambda x: abs(x['shap_value']), reverse=True)
        
        return {
            'top_features': features,
            'base_value': 0.5,
            'method': 'keyword_based'
        }


class SimpleLangGraphAgent:
    """Simplified LangGraph-style agent"""
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.classifier = MockClassifier()
        self.confidence_threshold = confidence_threshold
    
    def preprocess_claim(self, state: ClaimState) -> ClaimState:
        """Extract and format claim information"""
        claim_data = state['claim_data']
        
        claim_text = f"""
Claim ID: {claim_data.get('claim_id', 'N/A')}
Policy Type: {claim_data.get('policy_type', 'N/A')}
Claim Amount: ${claim_data.get('amount', 0):,.2f}
Description: {claim_data.get('description', 'N/A')}
Medical Reports: {claim_data.get('medical_reports', 'None provided')}
Previous Claims: {claim_data.get('previous_claims', 0)}
Policy Duration: {claim_data.get('policy_duration_months', 0)} months
"""
        
        state['claim_text'] = claim_text.strip()
        state['messages'].append({
            'role': 'system',
            'content': f"✓ Preprocessed claim {claim_data.get('claim_id')}"
        })
        
        print(f"✓ Preprocessed claim {claim_data.get('claim_id')}")
        return state
    
    def classify_claim(self, state: ClaimState) -> ClaimState:
        """Run classification"""
        probs = self.classifier.predict(state['claim_text'])
        prediction = "APPROVED" if probs[1] > 0.5 else "REJECTED"
        confidence = float(max(probs))
        
        state['prediction'] = prediction
        state['confidence'] = confidence
        state['messages'].append({
            'role': 'assistant',
            'content': f"✓ Classification: {prediction} (confidence: {confidence:.1%})"
        })
        
        print(f"✓ Classification: {prediction} with {confidence:.1%} confidence")
        return state
    
    def explain_decision(self, state: ClaimState) -> ClaimState:
        """Generate explanation"""
        explanation = self.classifier.get_explanation(state['claim_text'])
        state['shap_explanation'] = explanation
        
        top_features = explanation.get('top_features', [])
        
        reasoning_parts = [
            f"Decision: {state['prediction']}",
            f"Confidence: {state['confidence']:.1%}",
            "",
            "Key factors influencing this decision:"
        ]
        
        for feature in top_features[:5]:
            impact = "supporting approval" if feature['shap_value'] > 0 else "supporting rejection"
            reasoning_parts.append(
                f"  • '{feature['feature']}' (impact: {abs(feature['shap_value']):.3f}, {impact})"
            )
        
        reasoning = "\n".join(reasoning_parts)
        state['decision_reasoning'] = reasoning
        state['messages'].append({
            'role': 'assistant',
            'content': reasoning
        })
        
        print("✓ Generated explanation")
        return state
    
    def check_confidence(self, state: ClaimState) -> str:
        """Route based on confidence"""
        if state['confidence'] < self.confidence_threshold:
            return "human_review"
        return "finalize"
    
    def request_human_review(self, state: ClaimState) -> ClaimState:
        """Flag for human review"""
        state['requires_human_review'] = True
        state['messages'].append({
            'role': 'system',
            'content': f"⚠️ Confidence ({state['confidence']:.1%}) below threshold. Flagging for human review."
        })
        state['prediction'] = f"{state['prediction']} - PENDING HUMAN REVIEW"
        
        print(f"⚠️ Flagged for human review (confidence: {state['confidence']:.1%})")
        return state
    
    def finalize_decision(self, state: ClaimState) -> ClaimState:
        """Finalize decision"""
        state['requires_human_review'] = False
        state['messages'].append({
            'role': 'system',
            'content': f"✓ Claim decision finalized: {state['prediction']}"
        })
        
        print(f"✓ Decision finalized: {state['prediction']}")
        return state
    
    def process_claim(self, claim_data: dict) -> dict:
        """Process a claim through the workflow"""
        print("\n" + "="*60)
        print(f"Processing Claim: {claim_data.get('claim_id', 'Unknown')}")
        print("="*60)
        
        # Initialize state
        state = {
            'claim_data': claim_data,
            'claim_text': '',
            'prediction': '',
            'confidence': 0.0,
            'shap_explanation': {},
            'decision_reasoning': '',
            'messages': [],
            'requires_human_review': False
        }
        
        # Run workflow
        state = self.preprocess_claim(state)
        state = self.classify_claim(state)
        state = self.explain_decision(state)
        
        # Route based on confidence
        if self.check_confidence(state) == "human_review":
            state = self.request_human_review(state)
        else:
            state = self.finalize_decision(state)
        
        print("="*60)
        print("Processing complete!")
        print("="*60 + "\n")
        
        return state


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def print_result(result: dict):
    """Print formatted result"""
    print(f"\n{'Decision:':<20} {result['prediction']}")
    print(f"{'Confidence:':<20} {result['confidence']:.1%}")
    print(f"{'Human Review:':<20} {'Yes' if result['requires_human_review'] else 'No'}")
    print(f"\n{result['decision_reasoning']}")


def save_result(result: dict, filename: str):
    """Save result to JSON"""
    output = {
        'claim_id': result['claim_data']['claim_id'],
        'prediction': result['prediction'],
        'confidence': result['confidence'],
        'requires_human_review': result['requires_human_review'],
        'reasoning': result['decision_reasoning'],
        'timestamp': datetime.now().isoformat(),
        'top_features': result['shap_explanation'].get('top_features', [])
    }
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✓ Result saved to: {filename}")


def main():
    """Run the demo"""
    print_section("Insurance Claim AI Agent - Lightweight Demo")
    
    print("\nNote: This is a lightweight demo using mock predictions.")
    print("In production, replace MockClassifier with actual Qwen model.")
    print("\nConfiguration:")
    print("- Model: Mock Classifier (keyword-based)")
    print("- Framework: Simplified LangGraph")
    print("- Explainability: Keyword-based (SHAP simulation)")
    print("- Confidence Threshold: 70%")
    
    # Create agent
    agent = SimpleLangGraphAgent(confidence_threshold=0.7)
    
    # Test claims
    test_claims = [
        {
            'claim_id': 'CLM-2024-001',
            'policy_type': 'Health Insurance',
            'amount': 15000,
            'description': 'Emergency surgery for appendicitis with 3-day hospital stay',
            'medical_reports': 'Confirmed diagnosis by Dr. Smith, emergency procedure was necessary',
            'previous_claims': 2,
            'policy_duration_months': 24
        },
        {
            'claim_id': 'CLM-2024-002',
            'policy_type': 'Auto Insurance',
            'amount': 8500,
            'description': 'Vehicle accident resulting in significant damage',
            'medical_reports': 'Minor injuries treated at hospital',
            'previous_claims': 0,
            'policy_duration_months': 36
        },
        {
            'claim_id': 'CLM-2024-003',
            'policy_type': 'Health Insurance',
            'amount': 250000,
            'description': 'Elective cosmetic surgery procedure',
            'medical_reports': 'Non-emergency procedure, patient request',
            'previous_claims': 5,
            'policy_duration_months': 6
        }
    ]
    
    import os
    os.makedirs('outputs', exist_ok=True)
    
    results = []
    
    # Process claims
    for i, claim in enumerate(test_claims, 1):
        print_section(f"Claim {i}/{len(test_claims)}: {claim['claim_id']}")
        
        result = agent.process_claim(claim)
        results.append(result)
        
        print_result(result)
        save_result(result, f"outputs/result_{claim['claim_id']}.json")
    
    # Summary
    print_section("Processing Summary")
    
    approved = sum(1 for r in results if 'APPROVED' in r['prediction'])
    rejected = sum(1 for r in results if 'REJECTED' in r['prediction'])
    review_needed = sum(1 for r in results if r['requires_human_review'])
    
    print(f"\nTotal Claims Processed: {len(results)}")
    print(f"  ✓ Approved: {approved}")
    print(f"  ✗ Rejected: {rejected}")
    print(f"  ⚠ Human Review Required: {review_needed}")
    
    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    print(f"\nAverage Confidence: {avg_confidence:.1%}")
    
    # Save summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'total_claims': len(results),
        'approved': approved,
        'rejected': rejected,
        'human_review_needed': review_needed,
        'average_confidence': avg_confidence,
        'claims': [
            {
                'claim_id': r['claim_data']['claim_id'],
                'decision': r['prediction'],
                'confidence': r['confidence']
            }
            for r in results
        ]
    }
    
    with open('outputs/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n✓ Summary saved to: outputs/summary.json")
    
    print_section("Demo Complete!")
    print("\nGenerated files in 'outputs/' directory:")
    print("  - result_CLM-2024-001.json")
    print("  - result_CLM-2024-002.json")
    print("  - result_CLM-2024-003.json")
    print("  - summary.json")
    
    print("\nNext steps:")
    print("  1. Install full dependencies: pip install -r requirements.txt")
    print("  2. Replace MockClassifier with actual Qwen model")
    print("  3. Run main.py for full SHAP analysis")
    print("  4. Deploy api_server.py for production use")
    print("\n")


if __name__ == "__main__":
    main()
