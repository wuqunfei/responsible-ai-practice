"""
Example Usage Script for Pet Insurance SHAP Analysis
Demonstrates how to use the complete system
"""

import warnings
warnings.filterwarnings('ignore')

from src.shap_explainer import PetClaimExplainer
from src.semantic_analyzer import SemanticAnalyzer
from src.visualization import ClaimVisualizer
import pandas as pd
import os


def main():
    """Main demonstration function"""
    
    print("Pet Insurance Claims - SHAP Analysis Demo")
    print("=" * 50)
    
    # Sample claims data
    sample_claims = [
        {
            'claim_id': 'CLM001',
            'text': "My 3-year-old golden retriever broke his leg falling down stairs. X-rays confirm fracture. Surgery required. Treatment cost $2500.",
            'actual_decision': 'Approved'
        },
        {
            'claim_id': 'CLM002',
            'text': "Regular dental cleaning for my 8-year-old cat. No medical issues, just routine care. Cost $300.",
            'actual_decision': 'Rejected'
        },
        {
            'claim_id': 'CLM003',
            'text': "Emergency surgery for my dog who ate chocolate. Hospitalized for 2 days with severe poisoning. Total bill $4000.",
            'actual_decision': 'Approved'
        },
        {
            'claim_id': 'CLM004',
            'text': "Preventive flea treatment purchased at pet store. Requesting reimbursement of $50.",
            'actual_decision': 'Rejected'
        },
        {
            'claim_id': 'CLM005',
            'text': "My 10-year-old cat diagnosed with kidney disease. Requires ongoing medication and special diet. Monthly cost $200.",
            'actual_decision': 'Approved'
        },
        {
            'claim_id': 'CLM006',
            'text': "Routine vaccination and wellness checkup for 6-month puppy. Total cost $150.",
            'actual_decision': 'Rejected'
        },
        {
            'claim_id': 'CLM007',
            'text': "Dog attacked by another animal at park. Multiple lacerations requiring stitches and antibiotics. Emergency vet bill $1800.",
            'actual_decision': 'Approved'
        },
        {
            'claim_id': 'CLM008',
            'text': "Annual heartworm prevention medication. Cost $120 for 6-month supply.",
            'actual_decision': 'Rejected'
        }
    ]
    
    # Extract texts and actual decisions
    claim_texts = [claim['text'] for claim in sample_claims]
    actual_decisions = [claim['actual_decision'] for claim in sample_claims]
    
    print(f"\nLoaded {len(sample_claims)} sample claims")
    
    # Initialize components
    print("\n1. Initializing SHAP Explainer...")
    try:
        # Note: Using GPT-2 as example. Replace with your actual model
        explainer = PetClaimExplainer(model_name='gpt2')
        print("   ✓ SHAP Explainer initialized")
    except Exception as e:
        print(f"   ✗ Error initializing explainer: {e}")
        print("   Using mock explainer for demo...")
        explainer = None
    
    print("\n2. Initializing Semantic Analyzer...")
    analyzer = SemanticAnalyzer()
    print("   ✓ Semantic Analyzer initialized")
    
    print("\n3. Initializing Visualizer...")
    visualizer = ClaimVisualizer()
    print("   ✓ Visualizer initialized")
    
    # Perform analysis
    print("\n4. Analyzing Claims...")
    
    # If explainer is available, use it; otherwise, create mock results
    if explainer:
        explanations = explainer.explain_batch(claim_texts)
    else:
        # Create mock explanations for demo
        explanations = create_mock_explanations(claim_texts, actual_decisions)
    
    print(f"   ✓ Generated explanations for {len(explanations)} claims")
    
    # Extract predictions
    predictions = [exp['prediction'] for exp in explanations]
    
    # Semantic analysis
    print("\n5. Performing Semantic Analysis...")
    
    # Extract features
    features = [analyzer.extract_features(text) for text in claim_texts]
    print("   ✓ Extracted semantic features")
    
    # Cluster claims
    labels, clusters = analyzer.cluster_claims(claim_texts, n_clusters=3)
    print(f"   ✓ Clustered claims into {len(clusters)} groups")
    
    # Identify patterns
    patterns = analyzer.identify_patterns(claim_texts, predictions)
    print("   ✓ Identified decision patterns")
    
    # Generate business rules
    rules = analyzer.generate_business_rules(patterns)
    print(f"   ✓ Generated {len(rules)} business rules")
    
    # Display results
    print("\n6. Results Summary:")
    print("-" * 50)
    
    # Decision accuracy (if using mock data, this will be 100%)
    accuracy = sum(p == a for p, a in zip(predictions, actual_decisions)) / len(predictions)
    print(f"   Model Accuracy: {accuracy:.1%}")
    
    # Decision distribution
    approved_count = sum(1 for p in predictions if p == 'Approved')
    print(f"   Approved: {approved_count}/{len(predictions)} ({approved_count/len(predictions):.1%})")
    print(f"   Rejected: {len(predictions)-approved_count}/{len(predictions)} ({(len(predictions)-approved_count)/len(predictions):.1%})")
    
    # Display business rules
    print("\n   Generated Business Rules:")
    for i, rule in enumerate(rules, 1):
        print(f"   {i}. {rule}")
    
    # Key patterns
    print("\n   Key Patterns Identified:")
    key_diffs = patterns.get('key_differences', {})
    for feature, diff in list(key_diffs.items())[:3]:  # Top 3
        print(f"   - {feature}: Approved={diff['approved_value']:.2f}, Rejected={diff['rejected_value']:.2f}")
    
    # Create visualizations
    print("\n7. Creating Visualizations...")
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Single claim visualization
    fig1 = visualizer.plot_single_explanation(
        claim_texts[0], 
        explanations[0],
        save_path='output/single_claim_analysis.png'
    )
    print("   ✓ Created single claim visualization")
    
    # Batch summary
    fig2 = visualizer.plot_batch_summary(
        explanations,
        claim_texts,
        save_path='output/batch_summary.png'
    )
    print("   ✓ Created batch summary visualization")
    
    # Semantic patterns
    fig3 = visualizer.plot_semantic_patterns(
        patterns,
        save_path='output/semantic_patterns.png'
    )
    print("   ✓ Created semantic pattern visualization")
    
    # Save detailed results
    print("\n8. Saving Detailed Results...")
    
    # Create results dataframe
    results_df = pd.DataFrame({
        'claim_id': [claim['claim_id'] for claim in sample_claims],
        'claim_text': claim_texts,
        'actual_decision': actual_decisions,
        'predicted_decision': predictions,
        'confidence': [exp['confidence'] for exp in explanations],
        'is_emergency': [feat['is_emergency'] for feat in features],
        'is_preventive': [feat['is_preventive'] for feat in features],
        'severity_score': [feat['severity_score'] for feat in features],
        'cost_amount': [feat['cost_amount'] for feat in features],
        'cluster': labels
    })
    
    results_df.to_csv('output/analysis_results.csv', index=False)
    print("   ✓ Saved detailed results to output/analysis_results.csv")
    
    # Save influential tokens for each claim
    token_importance = []
    for i, exp in enumerate(explanations):
        for token, importance in exp.get('influential_tokens', []):
            token_importance.append({
                'claim_id': sample_claims[i]['claim_id'],
                'token': token,
                'importance': importance,
                'prediction': exp['prediction']
            })
    
    token_df = pd.DataFrame(token_importance)
    token_df.to_csv('output/token_importance.csv', index=False)
    print("   ✓ Saved token importance to output/token_importance.csv")
    
    print("\n" + "=" * 50)
    print("Demo completed successfully!")
    print("Check the 'output' directory for results and visualizations.")
    

def create_mock_explanations(texts, actual_decisions):
    """Create mock explanations for demo purposes when model is not available"""
    import random
    
    # Define mock token patterns
    approval_tokens = ['emergency', 'surgery', 'injury', 'fracture', 'disease', 'attack', 'poisoning']
    rejection_tokens = ['routine', 'preventive', 'wellness', 'regular', 'vaccination', 'cleaning']
    
    explanations = []
    
    for text, actual in zip(texts, actual_decisions):
        # Simple rule-based mock prediction
        text_lower = text.lower()
        
        # Count approval and rejection indicators
        approval_score = sum(1 for token in approval_tokens if token in text_lower)
        rejection_score = sum(1 for token in rejection_tokens if token in text_lower)
        
        # Make prediction
        if approval_score > rejection_score:
            prediction = 'Approved'
            confidence = 0.7 + random.uniform(0, 0.25)
        elif rejection_score > approval_score:
            prediction = 'Rejected'
            confidence = 0.7 + random.uniform(0, 0.25)
        else:
            # Random for unclear cases
            prediction = random.choice(['Approved', 'Rejected'])
            confidence = 0.5 + random.uniform(0, 0.2)
        
        # Extract influential tokens
        influential_tokens = []
        words = text.lower().split()
        
        for word in words:
            if word in approval_tokens:
                influential_tokens.append((word, random.uniform(0.3, 0.8)))
            elif word in rejection_tokens:
                influential_tokens.append((word, random.uniform(-0.8, -0.3)))
        
        # Add some cost-related tokens
        if '$' in text:
            cost_match = text[text.index('$'):].split()[0]
            influential_tokens.append((cost_match, random.uniform(-0.2, 0.2)))
        
        # Sort by importance
        influential_tokens.sort(key=lambda x: abs(x[1]), reverse=True)
        
        explanations.append({
            'prediction': prediction,
            'confidence': confidence,
            'influential_tokens': influential_tokens[:5],
            'shap_values': None  # Mock object
        })
    
    return explanations


if __name__ == "__main__":
    main()
