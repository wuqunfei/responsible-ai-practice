"""
Visualization utilities for SHAP explanations
"""
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List
import json


def plot_feature_importance(explanation: Dict, output_file: str = 'feature_importance.png'):
    """
    Plot feature importance from SHAP explanation.
    
    Args:
        explanation: SHAP explanation dictionary
        output_file: Path to save the plot
    """
    top_features = explanation.get('top_features', [])
    
    if not top_features:
        print("No features to plot")
        return
    
    # Extract data
    features = [f['feature'] for f in top_features[:10]]
    values = [f['shap_value'] for f in top_features[:10]]
    colors = ['green' if v > 0 else 'red' for v in values]
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    y_pos = np.arange(len(features))
    ax.barh(y_pos, values, color=colors, alpha=0.7)
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(features)
    ax.invert_yaxis()
    ax.set_xlabel('SHAP Value (Impact on Approval)')
    ax.set_title('Top Features Influencing Claim Decision')
    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
    
    # Add legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', alpha=0.7, label='Supports Approval'),
        Patch(facecolor='red', alpha=0.7, label='Supports Rejection')
    ]
    ax.legend(handles=legend_elements, loc='lower right')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Feature importance plot saved to: {output_file}")


def plot_confidence_distribution(results: List[Dict], output_file: str = 'confidence_dist.png'):
    """
    Plot confidence score distribution across multiple claims.
    
    Args:
        results: List of result dictionaries
        output_file: Path to save the plot
    """
    confidences = [r['confidence'] for r in results]
    predictions = [r['prediction'] for r in results]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Histogram
    ax1.hist(confidences, bins=10, color='steelblue', alpha=0.7, edgecolor='black')
    ax1.axvline(x=0.7, color='red', linestyle='--', label='Review Threshold (70%)')
    ax1.set_xlabel('Confidence Score')
    ax1.set_ylabel('Number of Claims')
    ax1.set_title('Distribution of Confidence Scores')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Decision counts
    approved = sum(1 for p in predictions if 'APPROVED' in p and 'REVIEW' not in p)
    rejected = sum(1 for p in predictions if 'REJECTED' in p and 'REVIEW' not in p)
    review = sum(1 for p in predictions if 'REVIEW' in p)
    
    ax2.bar(['Approved', 'Rejected', 'Human Review'], 
            [approved, rejected, review],
            color=['green', 'red', 'orange'],
            alpha=0.7,
            edgecolor='black')
    ax2.set_ylabel('Number of Claims')
    ax2.set_title('Decision Distribution')
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Confidence distribution plot saved to: {output_file}")


def create_decision_report(result: Dict, output_file: str = 'decision_report.txt'):
    """
    Create a formatted text report for a claim decision.
    
    Args:
        result: Result dictionary from agent
        output_file: Path to save the report
    """
    claim_data = result['claim_data']
    
    report = f"""
{'='*70}
                    CLAIM DECISION REPORT
{'='*70}

CLAIM INFORMATION
{'-'*70}
Claim ID:           {claim_data.get('claim_id', 'N/A')}
Policy Type:        {claim_data.get('policy_type', 'N/A')}
Claim Amount:       ${claim_data.get('amount', 0):,.2f}
Previous Claims:    {claim_data.get('previous_claims', 0)}
Policy Duration:    {claim_data.get('policy_duration_months', 0)} months

Description:
{claim_data.get('description', 'N/A')}

Medical Reports:
{claim_data.get('medical_reports', 'None provided')}

DECISION
{'-'*70}
Status:             {result['prediction']}
Confidence:         {result['confidence']:.1%}
Human Review:       {'Required' if result['requires_human_review'] else 'Not Required'}

EXPLANATION
{'-'*70}
{result['decision_reasoning']}

KEY FACTORS
{'-'*70}
"""
    
    top_features = result['shap_explanation'].get('top_features', [])
    for i, feature in enumerate(top_features[:5], 1):
        impact_type = feature['impact']
        impact_value = abs(feature['shap_value'])
        report += f"{i}. {feature['feature']:20s} → {impact_type:8s} (strength: {impact_value:.3f})\n"
    
    report += f"\n{'='*70}\n"
    report += f"Report generated: {result.get('timestamp', 'N/A')}\n"
    report += f"{'='*70}\n"
    
    with open(output_file, 'w') as f:
        f.write(report)
    
    print(f"✓ Decision report saved to: {output_file}")


def visualize_results(results_file: str = 'outputs/summary.json'):
    """
    Create all visualizations from results file.
    
    Args:
        results_file: Path to summary JSON file
    """
    try:
        with open(results_file, 'r') as f:
            summary = json.load(f)
        
        print("\nGenerating visualizations...")
        
        # Create confidence distribution plot
        if summary.get('claims'):
            # Load individual results for detailed plots
            results = []
            for claim in summary['claims']:
                try:
                    result_file = f"outputs/result_{claim['claim_id']}.json"
                    with open(result_file, 'r') as f:
                        results.append(json.load(f))
                except FileNotFoundError:
                    continue
            
            if results:
                plot_confidence_distribution(results, 'outputs/confidence_distribution.png')
                
                # Create individual feature importance plots
                for result in results:
                    claim_id = result['claim_id']
                    plot_feature_importance(
                        {'top_features': result.get('top_features', [])},
                        f'outputs/features_{claim_id}.png'
                    )
        
        print("\n✓ All visualizations generated successfully!")
        
    except FileNotFoundError:
        print(f"Error: Results file not found: {results_file}")
        print("Run main.py first to generate results.")
    except Exception as e:
        print(f"Error generating visualizations: {e}")


if __name__ == "__main__":
    import os
    os.makedirs('outputs', exist_ok=True)
    
    print("="*70)
    print("  Insurance Claim Decision Visualizations")
    print("="*70)
    
    visualize_results()
