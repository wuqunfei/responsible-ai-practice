"""
PII Detection Comparison Tool
Compares Microsoft Presidio vs Transformer-based detection
"""

import pandas as pd
from collections import defaultdict
import os
import sys

# Import custom detectors
from presidio_detector import PresidioPIIDetector
from transformer_detector import TransformerPIIDetector


def load_email(filepath='sample_email.txt'):
    """Load the sample email"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Could not find {filepath}")
        sys.exit(1)


def print_header(title, char='='):
    """Print a formatted header"""
    print(f"\n{char * 80}")
    print(f"{title.center(80)}")
    print(f"{char * 80}\n")


def compare_detectors(text, threshold=0.5):
    """
    Compare both PII detection methods
    
    Args:
        text: Input text to analyze
        threshold: Detection confidence threshold
        
    Returns:
        Dictionary with comparison results
    """
    
    print_header("PII DETECTION COMPARISON", '=')
    print("Analyzing travel insurance claim email...")
    print(f"Email length: {len(text)} characters")
    print(f"Detection threshold: {threshold}")
    
    # Initialize detectors
    print("\n" + "-" * 80)
    print("Initializing Detectors...")
    print("-" * 80)
    
    presidio = PresidioPIIDetector()
    transformer = TransformerPIIDetector()
    
    # -------------------------------------------------------------------------
    # PRESIDIO DETECTION
    # -------------------------------------------------------------------------
    print_header("1. MICROSOFT PRESIDIO RESULTS", '=')
    
    presidio_results = presidio.detect(text, threshold=threshold)
    presidio_anonymized, _ = presidio.anonymize(text, threshold=threshold)
    presidio_summary = presidio.get_summary(presidio_results)
    presidio_detailed = presidio.get_detailed_results(text, presidio_results)
    
    print(f"✓ Detection complete!")
    print(f"\nTotal PII Entities Detected: {len(presidio_results)}")
    
    print("\n📊 PII Types Summary:")
    print("-" * 60)
    for pii_type, count in sorted(presidio_summary.items(), key=lambda x: -x[1]):
        bar = '█' * min(count, 30)
        print(f"  {pii_type:20} : {count:3} {bar}")
    
    print("\n📝 Sample Detections (First 15):")
    print("-" * 80)
    print(f"{'#':<4} {'Type':<20} {'Confidence':<12} {'Detected Text':<40}")
    print("-" * 80)
    
    for i, item in enumerate(presidio_detailed[:15], 1):
        text_preview = item['text'][:40]
        print(f"{i:<4} {item['type']:<20} {item['score']:<12.3f} {text_preview:<40}")
    
    if len(presidio_results) > 15:
        print(f"\n... and {len(presidio_results) - 15} more detections")
    
    # -------------------------------------------------------------------------
    # TRANSFORMER MODEL DETECTION
    # -------------------------------------------------------------------------
    print_header("2. TRANSFORMER MODEL RESULTS", '=')
    
    transformer_results = transformer.detect(text, threshold=threshold)
    transformer_anonymized, _ = transformer.anonymize(text, threshold=threshold)
    transformer_summary = transformer.get_summary(transformer_results)
    transformer_detailed = transformer.get_detailed_results(transformer_results)
    
    print(f"✓ Detection complete!")
    print(f"\nTotal PII Entities Detected: {len(transformer_results)}")
    
    print("\n📊 PII Types Summary:")
    print("-" * 60)
    for pii_type, count in sorted(transformer_summary.items(), key=lambda x: -x[1]):
        bar = '█' * min(count, 30)
        print(f"  {pii_type:20} : {count:3} {bar}")
    
    print("\n📝 Sample Detections (First 15):")
    print("-" * 80)
    print(f"{'#':<4} {'Type':<20} {'Confidence':<12} {'Detected Text':<40}")
    print("-" * 80)
    
    for i, item in enumerate(transformer_detailed[:15], 1):
        text_preview = item['text'][:40]
        print(f"{i:<4} {item['type']:<20} {item['score']:<12.3f} {text_preview:<40}")
    
    if len(transformer_results) > 15:
        print(f"\n... and {len(transformer_results) - 15} more detections")
    
    # -------------------------------------------------------------------------
    # SIDE-BY-SIDE COMPARISON
    # -------------------------------------------------------------------------
    print_header("3. SIDE-BY-SIDE COMPARISON", '=')
    
    # Create comparison table
    all_types = sorted(set(presidio_summary.keys()) | set(transformer_summary.keys()))
    
    print(f"{'PII Type':<25} | {'Presidio':>10} | {'Transformer':>12} | {'Difference':>12}")
    print("-" * 80)
    
    for pii_type in all_types:
        p_count = presidio_summary.get(pii_type, 0)
        t_count = transformer_summary.get(pii_type, 0)
        diff = abs(p_count - t_count)
        
        print(f"{pii_type:<25} | {p_count:>10} | {t_count:>12} | {diff:>12}")
    
    print("-" * 80)
    print(f"{'TOTAL':<25} | {len(presidio_results):>10} | {len(transformer_results):>12} | {abs(len(presidio_results) - len(transformer_results)):>12}")
    
    # -------------------------------------------------------------------------
    # ANONYMIZED TEXT SAMPLES
    # -------------------------------------------------------------------------
    print_header("4. ANONYMIZED TEXT PREVIEW", '=')
    
    sample_length = 500
    
    print("📄 Presidio Anonymized (First 500 chars):")
    print("-" * 80)
    print(presidio_anonymized[:sample_length])
    if len(presidio_anonymized) > sample_length:
        print("...")
    
    print("\n📄 Transformer Anonymized (First 500 chars):")
    print("-" * 80)
    print(transformer_anonymized[:sample_length])
    if len(transformer_anonymized) > sample_length:
        print("...")
    
    # -------------------------------------------------------------------------
    # KEY FINDINGS
    # -------------------------------------------------------------------------
    print_header("5. KEY FINDINGS & RECOMMENDATIONS", '=')
    
    print("🏆 PRESIDIO STRENGTHS:")
    print("  ✓ More comprehensive entity type coverage")
    print("  ✓ Better at structured patterns (SSN, credit cards, bank numbers)")
    print("  ✓ Faster processing on CPU")
    print("  ✓ Production-ready with excellent documentation")
    print("  ✓ Highly configurable with custom recognizers")
    
    print("\n🏆 TRANSFORMER MODEL STRENGTHS:")
    print("  ✓ Better context-aware detection")
    print("  ✓ More accurate for names and natural language entities")
    print("  ✓ Understands semantic meaning, not just patterns")
    print("  ✓ Generally fewer false positives for person names")
    
    print("\n💡 RECOMMENDATION:")
    print("  Use a HYBRID APPROACH combining both detectors for maximum coverage!")
    print("  - Presidio for structured data and patterns")
    print("  - Transformer for contextual and semantic understanding")
    
    # Create results directory
    os.makedirs('results', exist_ok=True)
    os.makedirs('results/anonymized_emails', exist_ok=True)
    
    # Save results
    print("\n💾 Saving results...")
    
    # Save anonymized versions
    with open('results/anonymized_emails/presidio_anonymized.txt', 'w') as f:
        f.write(presidio_anonymized)
    
    with open('results/anonymized_emails/transformer_anonymized.txt', 'w') as f:
        f.write(transformer_anonymized)
    
    # Save detailed results
    with open('results/presidio_results.txt', 'w') as f:
        f.write(f"Presidio Detection Results\n")
        f.write(f"{'=' * 80}\n\n")
        f.write(f"Total detections: {len(presidio_results)}\n\n")
        for item in presidio_detailed:
            f.write(f"{item['type']}: {item['text']} (score: {item['score']:.3f})\n")
    
    with open('results/transformer_results.txt', 'w') as f:
        f.write(f"Transformer Detection Results\n")
        f.write(f"{'=' * 80}\n\n")
        f.write(f"Total detections: {len(transformer_results)}\n\n")
        for item in transformer_detailed:
            f.write(f"{item['type']}: {item['text']} (score: {item['score']:.3f})\n")
    
    # Create comparison CSV
    comparison_data = []
    for pii_type in all_types:
        comparison_data.append({
            'PII_Type': pii_type,
            'Presidio_Count': presidio_summary.get(pii_type, 0),
            'Transformer_Count': transformer_summary.get(pii_type, 0),
            'Difference': abs(presidio_summary.get(pii_type, 0) - transformer_summary.get(pii_type, 0))
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    comparison_df.to_csv('results/comparison_report.csv', index=False)
    
    print("  ✓ Results saved to 'results/' directory")
    print("  ✓ Anonymized emails saved to 'results/anonymized_emails/'")
    print("  ✓ Comparison report saved to 'results/comparison_report.csv'")
    
    print_header("ANALYSIS COMPLETE", '=')
    
    return {
        'presidio': {
            'results': presidio_results,
            'anonymized': presidio_anonymized,
            'summary': presidio_summary,
            'detailed': presidio_detailed
        },
        'transformer': {
            'results': transformer_results,
            'anonymized': transformer_anonymized,
            'summary': transformer_summary,
            'detailed': transformer_detailed
        }
    }


if __name__ == "__main__":
    # Load the sample email
    email_text = load_email('sample_email.txt')
    
    # Run comparison
    results = compare_detectors(email_text, threshold=0.5)
    
    print("\n✨ Done! Check the 'results/' folder for detailed output.\n")
