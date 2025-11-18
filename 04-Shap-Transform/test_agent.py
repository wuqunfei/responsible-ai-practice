"""
Insurance Claim AI Agent - Main Demo with GPT-2
Run this to see the complete system with SHAP explanations
"""
import json
from agent import create_agent
from datetime import datetime
import os
from claim_classifier import GPT2ClaimClassifier
from loguru import logger


def print_section(title: str):
    """Print a formatted section header"""
    logger.info("\n" + "="*70)
    logger.info(f"  {title}")
    logger.info("="*70)


def print_result(result: dict):
    """Print formatted result"""
    logger.info(f"\n{'Decision:':<20} {result['prediction']}")
    logger.info(f"{'Confidence:':<20} {result['confidence']:.1%}")
    logger.info(f"{'Human Review:':<20} {'Yes' if result['requires_human_review'] else 'No'}")
    logger.info(f"\n{result['decision_reasoning']}")


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
    
    logger.info(f"\n✓ Result saved to: {filename}")


def main():
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    claims_dir = os.path.join(script_dir, 'claims')
    output_dir = os.path.join(script_dir, 'outputs')
    os.makedirs(output_dir, exist_ok=True)

    # Initialize the classifier with caching
    logger.info("\n📦 Initializing GPT-2 Claim Classifier...")
    classifier = GPT2ClaimClassifier(model_name="gpt2", cache_dir=os.path.join(script_dir, "cached_models"))
    
    # --- Get Claims to Process ---
    claim_files = sorted([f for f in os.listdir(claims_dir) if f.endswith('.json')])
    if not claim_files:
        logger.error(f"❌ No claim files found in {claims_dir}.")
        return

    logger.info(f"Found {len(claim_files)} claims to process: {claim_files}")

    # --- Process Each Claim ---
    all_results = []
    for i, file_name in enumerate(claim_files):
        claim_id = file_name.replace('.json', '')
        logger.info("="*80)
        logger.info(f"Processing Claim {i+1}/{len(claim_files)}: {claim_id}")
        logger.info("="*80)

        with open(os.path.join(claims_dir, file_name), 'r') as f:
            claim_data = json.load(f)
        
        claim_text = claim_data['claim_details']

        # --- 1. Prediction ---
        logger.info("\n1️⃣ Running prediction...")
        probabilities = classifier.predict(claim_text)
        decision = "APPROVED" if probabilities[1] > 0.5 else "REJECTED"
        confidence = probabilities[1] if decision == "APPROVED" else 1 - probabilities[1]
        logger.info(f"   → Decision: {decision} (Confidence: {confidence:.1%})")

        # --- 2. SHAP Explanation ---
        logger.info("\n2️⃣ Generating SHAP explanation...")
        explanation = classifier.get_shap_explanation(
            claim_text, 
            claim_id=claim_id, 
            num_samples=100  # Higher samples for better accuracy
        )

        # --- 3. Store Results ---
        result = {
            "claim_id": claim_id,
            "decision": decision,
            "confidence": confidence,
            "probabilities": {
                "approve": probabilities[1],
                "reject": probabilities[0]
            },
            "explanation": explanation
        }
        all_results.append(result)

        # Save individual result
        output_filename = os.path.join(output_dir, f"summary_{claim_id}.json")
        with open(output_filename, 'w') as f:
            json.dump(result, f, indent=4)
        logger.info(f"\n💾 Individual result saved to {output_filename}")

    # --- Final Summary ---
    logger.info("="*80)
    logger.info("\n🏁 All claims processed. Generating final summary...")
    summary_data = {
        "total_claims_processed": len(all_results),
        "processed_at": __import__('datetime').datetime.now().isoformat(),
        "results": all_results
    }

    summary_filename = os.path.join(output_dir, "summary_report.json")
    with open(summary_filename, 'w') as f:
        json.dump(summary_data, f, indent=4)
    
    logger.info(f"\n✅ Final summary report saved to {summary_filename}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        logger.error(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
