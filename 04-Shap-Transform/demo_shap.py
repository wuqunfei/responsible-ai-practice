"""
SHAP Visualization Demo with GPT-2
Demonstrates the SHAP explanation and export capabilities
"""
import os
from claim_classifier import GPT2ClaimClassifier


def demo_shap_visualization():
    """Run a focused demo of SHAP visualization capabilities"""
    
    print("="*80)
    print("SHAP Visualization Demo for Insurance Claim Classification")
    print("Using GPT-2 Language Model")
    print("="*80)
    
    # Create outputs directory
    os.makedirs('outputs', exist_ok=True)
    
    # Initialize classifier
    print("\n📦 Initializing GPT-2 model...")
    classifier = GPT2ClaimClassifier()
    
    # Define test claims with different characteristics
    test_claims = [
        {
            'name': 'High Approval Case',
            'text': """
Claim ID: CLM-APPROVE-001
Policy Type: Health Insurance
Claim Amount: $12,000
Description: Emergency surgery for appendicitis at hospital emergency room
Medical Reports: Confirmed diagnosis by Dr. Johnson, necessary emergency procedure, patient admitted with severe abdominal pain
Previous Claims: 1
Policy Duration: 36 months
Treatment: Surgical appendectomy performed immediately, 2-day hospital stay required
"""
        },
        {
            'name': 'High Rejection Case',
            'text': """
Claim ID: CLM-REJECT-001
Policy Type: Health Insurance
Claim Amount: $250,000
Description: Elective cosmetic surgery for facial enhancement
Medical Reports: Non-emergency procedure, patient request for aesthetic purposes, unnecessary for medical treatment
Previous Claims: 8
Policy Duration: 3 months
Treatment: Cosmetic facial reconstruction, not medically required
"""
        },
        {
            'name': 'Borderline Case',
            'text': """
Claim ID: CLM-BORDERLINE-001
Policy Type: Health Insurance
Claim Amount: $45,000
Description: Surgical procedure following accident
Medical Reports: Injury from vehicle accident, treatment recommended but not immediately life-threatening
Previous Claims: 4
Policy Duration: 18 months
Treatment: Orthopedic surgery for fracture repair
"""
        }
    ]
    
    # Process each claim
    for i, claim in enumerate(test_claims, 1):
        print("\n" + "="*80)
        print(f"Claim {i}/{len(test_claims)}: {claim['name']}")
        print("="*80)
        
        # Get prediction
        print("\n1️⃣ Running prediction...")
        probs = classifier.predict(claim['text'])
        decision = "APPROVED" if probs[1] > 0.5 else "REJECTED"
        confidence = max(probs)
        
        print(f"   Decision: {decision}")
        print(f"   Confidence: {confidence:.1%}")
        print(f"   Probabilities: Reject={probs[0]:.2%}, Approve={probs[1]:.2%}")
        
        # Get SHAP explanation
        print("\n2️⃣ Generating SHAP explanation (this takes ~1-2 minutes)...")
        explanation = classifier.get_shap_explanation(claim['text'], num_samples=80)
        
        print("\n3️⃣ Top features influencing the decision:")
        for j, feature in enumerate(explanation['top_features'][:8], 1):
            impact_dir = "→ APPROVE" if feature['shap_value'] > 0 else "→ REJECT"
            bar_length = int(abs(feature['shap_value']) * 20)
            bar = "█" * bar_length
            print(f"   {j}. {feature['feature']:20s} {feature['shap_value']:+.3f}  {bar} {impact_dir}")
        
        # Show export paths
        print("\n4️⃣ Visualization exports:")
        if explanation.get('html_path'):
            print(f"   📄 HTML (interactive): {explanation['html_path']}")
            print(f"      → Open this file in your web browser")
        if explanation.get('image_path'):
            print(f"   📊 PNG (static chart): {explanation['image_path']}")
            print(f"      → Use this for reports and presentations")
        
        print()
    
    # Summary
    print("="*80)
    print("Demo Complete! 🎉")
    print("="*80)
    
    print("\n📁 Check the outputs/ directory for:")
    print("   • shap_explanation.html - Interactive SHAP visualization")
    print("   • shap_explanation.png  - Static feature importance chart")
    
    print("\n💡 Understanding SHAP Values:")
    print("   • Positive values (green) = Features supporting APPROVAL")
    print("   • Negative values (red)   = Features supporting REJECTION")
    print("   • Larger magnitude        = Stronger influence on decision")
    
    print("\n🔍 How to interpret the HTML visualization:")
    print("   1. Open 'outputs/shap_explanation.html' in your browser")
    print("   2. Words highlighted in RED push toward rejection")
    print("   3. Words highlighted in GREEN push toward approval")
    print("   4. Intensity of color shows strength of influence")
    
    print("\n🎨 Using the PNG chart:")
    print("   • Bar chart shows top influential features")
    print("   • Green bars = positive impact (approval)")
    print("   • Red bars = negative impact (rejection)")
    print("   • Longer bars = stronger influence")
    
    print("\n⚙️  Customization options:")
    print("   • Adjust num_samples for speed vs accuracy trade-off")
    print("   • Lower values (50) = faster, less accurate")
    print("   • Higher values (200) = slower, more accurate")
    
    print("\n🚀 Next steps:")
    print("   1. Run main.py for full workflow demo")
    print("   2. Integrate into your production system")
    print("   3. Fine-tune the model on your actual claim data")
    
    print("\n" + "="*80 + "\n")


def demo_simple_explanation():
    """Demo the fast rule-based explanation"""
    
    print("="*80)
    print("Quick Rule-Based Explanation Demo (No SHAP)")
    print("Using GPT-2 Model")
    print("="*80)
    
    classifier = GPT2ClaimClassifier()
    
    test_text = """
Emergency surgery for appendicitis at hospital.
Confirmed diagnosis by doctor.
Necessary treatment required immediately.
"""
    
    print("\nClaim text:")
    print(test_text)
    
    print("\nGenerating rule-based explanation...")
    explanation = classifier.get_simple_explanation(test_text)
    
    print(f"\nMethod: {explanation['method']}")
    print("\nKey features detected:")
    for i, feature in enumerate(explanation['top_features'], 1):
        impact = "APPROVE" if feature['shap_value'] > 0 else "REJECT"
        print(f"   {i}. '{feature['feature']}': {feature['shap_value']:+.2f} → {impact}")
    
    print("\n💨 Rule-based explanations are:")
    print("   ✓ Very fast (instant results)")
    print("   ✓ Easy to understand")
    print("   ✗ Less accurate than SHAP")
    print("   ✗ Based on predefined keywords")
    
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    import sys
    
    print("\nSHAP Demo Options:")
    print("  1. Full SHAP visualization demo (recommended)")
    print("  2. Quick rule-based explanation demo")
    
    try:
        choice = input("\nSelect option (1/2, default=1): ").strip()
        if not choice:
            choice = "1"
        
        if choice == "2":
            demo_simple_explanation()
        else:
            demo_shap_visualization()
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
