"""
SHAP Visualization Demo with GPT-2
Demonstrates the SHAP explanation and export capabilities
"""
import os
import json
from loguru import logger
from claim_classifier import GPT2ClaimClassifier


def load_claims_from_directory(directory_path):
    """Loads all claim files from a directory."""
    claims = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r') as f:
                claims.append(json.load(f))
    return claims


def demo_shap_visualization():
    """Run a focused demo of SHAP visualization capabilities"""
    
    logger.info("="*80)
    logger.info("SHAP Visualization Demo for Insurance Claim Classification")
    logger.info("Using GPT-2 Language Model")
    logger.info("="*80)
    
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, 'outputs')
    claims_dir = os.path.join(script_dir, 'claims')
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize classifier
    logger.info("\n📦 Initializing GPT-2 model...")
    classifier = GPT2ClaimClassifier(cache_dir=os.path.join(script_dir, "cached_models"))
    
    # Load test claims from the 'claims' directory
    logger.info(f"\n📂 Loading claims from: {claims_dir}")
    test_claims = load_claims_from_directory(claims_dir)
    logger.info(f"   Found {len(test_claims)} claims to process.")
    
    # Process each claim
    for i, claim in enumerate(test_claims, 1):
        logger.info("\n" + "="*80)
        logger.info(f"Claim {i}/{len(test_claims)}: {claim['name']}")
        logger.info("="*80)
        
        # Get prediction
        logger.info("\n1️⃣ Running prediction...")
        probs = classifier.predict(claim['text'])
        decision = "APPROVED" if probs[1] > 0.5 else "REJECTED"
        confidence = max(probs)
        
        logger.info(f"   Decision: {decision}")
        logger.info(f"   Confidence: {confidence:.1%}")
        logger.info(f"   Probabilities: Reject={probs[0]:.2%}, Approve={probs[1]:.2%}")
        
        # Get SHAP explanation
        logger.info("\n2️⃣ Generating SHAP explanation (this takes ~1-2 minutes)...")
        explanation = classifier.get_shap_explanation(claim['text'], claim_id=claim['id'], num_samples=80)
        
        logger.info("\n3️⃣ Top features influencing the decision:")
        for j, feature in enumerate(explanation['top_features'][:8], 1):
            impact_dir = "→ APPROVE" if feature['shap_value'] > 0 else "→ REJECT"
            bar_length = int(abs(feature['shap_value']) * 20)
            bar = "█" * bar_length
            logger.info(f"   {j}. {feature['feature']:20s} {feature['shap_value']:+.3f}  {bar} {impact_dir}")
        
        # Show export paths
        logger.info("\n4️⃣ Visualization exports:")
        if explanation.get('html_path'):
            logger.info(f"   📄 HTML (interactive): {explanation['html_path']}")
            logger.info(f"      → Open this file in your web browser")
        if explanation.get('image_path'):
            logger.info(f"   📊 PNG (static chart): {explanation['image_path']}")
            logger.info(f"      → Use this for reports and presentations")
        
        logger.info("")
    
    # Summary
    logger.success("="*80)
    logger.success("Demo Complete! 🎉")
    logger.success("="*80)
    
    logger.info("\n📁 Check the outputs/ directory for:")
    logger.info("   • shap_explanation.html - Interactive SHAP visualization")
    logger.info("   • shap_explanation.png  - Static feature importance chart")
    
    logger.info("\n💡 Understanding SHAP Values:")
    logger.info("   • Positive values (green) = Features supporting APPROVAL")
    logger.info("   • Negative values (red)   = Features supporting REJECTION")
    logger.info("   • Larger magnitude        = Stronger influence on decision")
    
    logger.info("\n🔍 How to interpret the HTML visualization:")
    logger.info("   1. Open 'outputs/shap_explanation.html' in your browser")
    logger.info("   2. Words highlighted in RED push toward rejection")
    logger.info("   3. Words highlighted in GREEN push toward approval")
    logger.info("   4. Intensity of color shows strength of influence")
    
    logger.info("\n🎨 Using the PNG chart:")
    logger.info("   • Bar chart shows top influential features")
    logger.info("   • Green bars = positive impact (approval)")
    logger.info("   • Red bars = negative impact (rejection)")
    logger.info("   • Longer bars = stronger influence")
    
    logger.info("\n⚙️  Customization options:")
    logger.info("   • Adjust num_samples for speed vs accuracy trade-off")
    logger.info("   • Lower values (50) = faster, less accurate")
    logger.info("   • Higher values (200) = slower, more accurate")
    
    logger.info("\n🚀 Next steps:")
    logger.info("   1. Run main.py for full workflow demo")
    logger.info("   2. Integrate into your production system")
    logger.info("   3. Fine-tune the model on your actual claim data")
    
    logger.info("\n" + "="*80 + "\n")


def demo_simple_explanation():
    """Demo the fast rule-based explanation"""
    
    logger.info("="*80)
    logger.info("Quick Rule-Based Explanation Demo (No SHAP)")
    logger.info("="*80)
    
    classifier = GPT2ClaimClassifier()
    
    # Load a specific claim for the simple explanation demo
    script_dir = os.path.dirname(os.path.abspath(__file__))
    claim_path = os.path.join(script_dir, 'claims', 'CLM-APPROVE-001.json')
    
    with open(claim_path, 'r') as f:
        claim = json.load(f)
    
    test_text = claim['text']
    
    logger.info("\nClaim text:")
    logger.info(test_text)
    
    logger.info("\nGenerating rule-based explanation...")
    explanation = classifier.get_simple_explanation(test_text)
    
    logger.info(f"\nMethod: {explanation['method']}")
    logger.info("\nKey features detected:")
    for i, feature in enumerate(explanation['top_features'], 1):
        impact = "APPROVE" if feature['shap_value'] > 0 else "REJECT"
        logger.info(f"   {i}. '{feature['feature']}': {feature['shap_value']:+.2f} → {impact}")
    
    logger.info("\n💨 Rule-based explanations are:")
    logger.info("   ✓ Very fast (instant results)")
    logger.info("   ✓ Easy to understand")
    logger.info("   ✗ Less accurate than SHAP")
    logger.info("   ✗ Based on predefined keywords")
    
    logger.info("\n" + "="*80 + "\n")


if __name__ == "__main__":
    import sys
    
    logger.info("\nSHAP Demo Options:")
    logger.info("  1. Full SHAP visualization demo (recommended)")
    logger.info("  2. Quick rule-based explanation demo")
    
    try:
        choice = input("\nSelect option (1/2, default=1): ").strip()
        if not choice:
            choice = "1"
        
        if choice == "2":
            demo_simple_explanation()
        else:
            demo_shap_visualization()
            
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Demo interrupted")
    except Exception as e:
        logger.error(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
