"""
Insurance Claim AI Agent - Main Demo
Run this to see the complete system in action
"""
import json
from agent import create_agent
from datetime import datetime


def print_section(title: str):
    """Print a formatted section header"""
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
    """Save result to JSON file"""
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
    
    print(f"\n✓ Result saved to: {filename}")


def main():
    """Run the demo"""
    print_section("Insurance Claim AI Agent with SHAP Explainability")
    
    print("\nInitializing agent...")
    print("- Model: DistilBERT (proxy for Qwen)")
    print("- Framework: LangGraph")
    print("- Explainability: SHAP + Rule-based")
    print("- Confidence Threshold: 70%")
    
    # Create agent
    agent = create_agent(confidence_threshold=0.7, use_shap=True)
    
    # Define test claims
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
            'description': 'Elective cosmetic surgery',
            'medical_reports': 'Non-emergency procedure, patient request',
            'previous_claims': 5,
            'policy_duration_months': 6
        }
    ]
    
    results = []
    
    # Process each claim
    for i, claim in enumerate(test_claims, 1):
        print_section(f"Claim {i}/{len(test_claims)}: {claim['claim_id']}")
        
        result = agent.process_claim(claim)
        results.append(result)
        
        print_result(result)
        
        # Save individual result
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
    print("\nNext steps:")
    print("  1. Check the 'outputs' folder for detailed results")
    print("  2. Modify claims in this script to test different scenarios")
    print("  3. Set use_shap=True for SHAP analysis (slower but more accurate)")
    print("  4. Fine-tune the model on your actual claim data")
    print("\n")


if __name__ == "__main__":
    import os
    os.makedirs('outputs', exist_ok=True)
    main()
