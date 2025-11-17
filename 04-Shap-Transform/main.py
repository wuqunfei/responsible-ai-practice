"""
Insurance Claim AI Agent - Main Demo with GPT-2
Run this to see the complete system with SHAP explanations
"""
import json
from agent import create_agent
from datetime import datetime
import os


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
        'top_features': result['shap_explanation'].get('top_features', []),
        'explanation_method': result['shap_explanation'].get('method', 'unknown'),
        'visualization_files': {
            'html': result['shap_explanation'].get('html_path'),
            'image': result['shap_explanation'].get('image_path')
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✓ Result saved to: {filename}")


def main():
    """Run the demo"""
    print_section("Insurance Claim AI Agent with GPT-2 & SHAP")
    
    print("\nInitializing agent...")
    print("- Model: GPT-2 (124M parameters)")
    print("- Framework: LangGraph")
    print("- Explainability: SHAP + Rule-based")
    print("- Confidence Threshold: 70%")
    print("- Visualization: HTML + PNG exports")
    
    # Create output directory
    os.makedirs('outputs', exist_ok=True)
    
    # Create agent with SHAP enabled
    print("\nNote: SHAP analysis may take 1-2 minutes per claim for detailed explanations")
    use_shap_choice = input("Use SHAP for detailed explanations? (y/n, default=y): ").strip().lower()
    use_shap = use_shap_choice != 'n'
    
    agent = create_agent(confidence_threshold=0.7, use_shap=use_shap)
    
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
            'description': 'Vehicle accident resulting in significant damage to front bumper',
            'medical_reports': 'Minor injuries treated at hospital emergency room',
            'previous_claims': 0,
            'policy_duration_months': 36
        },
        {
            'claim_id': 'CLM-2024-003',
            'policy_type': 'Health Insurance',
            'amount': 250000,
            'description': 'Elective cosmetic surgery for facial reconstruction',
            'medical_reports': 'Non-emergency procedure, patient request, not medically necessary',
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
    
    approved = sum(1 for r in results if 'APPROVED' in r['prediction'] and 'PENDING' not in r['prediction'])
    rejected = sum(1 for r in results if 'REJECTED' in r['prediction'] and 'PENDING' not in r['prediction'])
    review_needed = sum(1 for r in results if r['requires_human_review'])
    
    print(f"\nTotal Claims Processed: {len(results)}")
    print(f"  ✓ Approved: {approved}")
    print(f"  ✗ Rejected: {rejected}")
    print(f"  ⚠  Human Review Required: {review_needed}")
    
    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    print(f"\nAverage Confidence: {avg_confidence:.1%}")
    
    # List generated visualization files
    print(f"\n📊 Generated Visualizations:")
    viz_files = []
    for r in results:
        html_path = r['shap_explanation'].get('html_path')
        img_path = r['shap_explanation'].get('image_path')
        if html_path:
            viz_files.append(html_path)
        if img_path:
            viz_files.append(img_path)
    
    if viz_files:
        for f in set(viz_files):  # Remove duplicates
            if os.path.exists(f):
                print(f"  • {f}")
    else:
        print("  (No SHAP visualizations generated - rule-based mode used)")
    
    # Save summary
    summary = {
        'timestamp': datetime.now().isoformat(),
        'model': 'GPT-2 (124M parameters)',
        'explanation_method': 'SHAP' if use_shap else 'Rule-based',
        'total_claims': len(results),
        'approved': approved,
        'rejected': rejected,
        'human_review_needed': review_needed,
        'average_confidence': avg_confidence,
        'claims': [
            {
                'claim_id': r['claim_data']['claim_id'],
                'decision': r['prediction'],
                'confidence': r['confidence'],
                'visualization_files': {
                    'html': r['shap_explanation'].get('html_path'),
                    'image': r['shap_explanation'].get('image_path')
                }
            }
            for r in results
        ]
    }
    
    with open('outputs/summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n✓ Summary saved to: outputs/summary.json")
    
    print_section("Demo Complete!")
    print("\nNext steps:")
    print("  1. Check the 'outputs' folder for:")
    print("     - Individual claim results (JSON)")
    print("     - SHAP visualizations (HTML + PNG)")
    print("     - Processing summary")
    print("  2. Open 'outputs/shap_explanation.html' in your browser for interactive visualization")
    print("  3. Modify claims in this script to test different scenarios")
    print("  4. Set use_shap=True for detailed SHAP analysis")
    print("  5. Fine-tune GPT-2 on your actual claim data for production use")
    print("\n" + "="*70)
    print("Model Options:")
    print("  - 'gpt2' (124M) - Current, fastest")
    print("  - 'gpt2-medium' (355M) - Better accuracy")
    print("  - 'gpt2-large' (774M) - Even better")
    print("  - 'gpt2-xl' (1.5B) - Best accuracy")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
