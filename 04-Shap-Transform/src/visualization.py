"""
Visualization Utilities for SHAP Explanations
Creates business-friendly visualizations of model decisions
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
import shap
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches


class ClaimVisualizer:
    """Visualizes SHAP explanations for pet insurance claims"""
    
    def __init__(self, style: str = 'seaborn'):
        """
        Initialize visualizer with style settings
        
        Args:
            style: Matplotlib style to use
        """
        plt.style.use(style)
        self.colors = {
            'approve': '#2ECC71',
            'reject': '#E74C3C',
            'neutral': '#95A5A6',
            'emergency': '#F39C12',
            'preventive': '#3498DB'
        }
    
    def plot_single_explanation(self, 
                              claim_text: str,
                              explanation: Dict,
                              save_path: Optional[str] = None) -> plt.Figure:
        """
        Create a comprehensive visualization for a single claim
        
        Args:
            claim_text: Original claim text
            explanation: Explanation dictionary from shap_explainer
            save_path: Path to save the figure
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(f"Claim Analysis: {explanation['prediction']}", fontsize=16, fontweight='bold')
        
        # 1. Token importance bar chart
        ax1 = axes[0, 0]
        tokens, importances = zip(*explanation['influential_tokens'][:10])
        colors = [self.colors['approve'] if imp > 0 else self.colors['reject'] for imp in importances]
        
        y_pos = np.arange(len(tokens))
        ax1.barh(y_pos, importances, color=colors, alpha=0.8)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(tokens)
        ax1.set_xlabel('Impact on Decision')
        ax1.set_title('Most Influential Words')
        ax1.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        # 2. Confidence meter
        ax2 = axes[0, 1]
        confidence = explanation['confidence']
        self._plot_confidence_meter(ax2, confidence, explanation['prediction'])
        
        # 3. Decision breakdown pie chart
        ax3 = axes[1, 0]
        positive_impact = sum(imp for _, imp in explanation['influential_tokens'] if imp > 0)
        negative_impact = abs(sum(imp for _, imp in explanation['influential_tokens'] if imp < 0))
        
        if positive_impact + negative_impact > 0:
            sizes = [positive_impact, negative_impact]
            labels = ['Approval Factors', 'Rejection Factors']
            colors = [self.colors['approve'], self.colors['reject']]
            ax3.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax3.set_title('Decision Factor Balance')
        else:
            ax3.text(0.5, 0.5, 'No significant factors', ha='center', va='center')
            ax3.set_xlim(0, 1)
            ax3.set_ylim(0, 1)
        
        # 4. Claim summary
        ax4 = axes[1, 1]
        ax4.axis('off')
        summary_text = f"Claim Summary:\n\n{claim_text[:200]}{'...' if len(claim_text) > 200 else ''}\n\n"
        summary_text += f"Decision: {explanation['prediction']}\n"
        summary_text += f"Confidence: {confidence:.1%}\n"
        summary_text += f"Key Factors: {len(explanation['influential_tokens'])}"
        
        ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, 
                fontsize=10, verticalalignment='top', wrap=True,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def _plot_confidence_meter(self, ax, confidence: float, prediction: str):
        """Plot a confidence meter"""
        ax.clear()
        
        # Create meter background
        meter_width = 0.8
        meter_height = 0.2
        meter_x = 0.1
        meter_y = 0.4
        
        # Background
        ax.add_patch(Rectangle((meter_x, meter_y), meter_width, meter_height, 
                              facecolor='lightgray', edgecolor='black'))
        
        # Confidence fill
        fill_color = self.colors['approve'] if prediction == 'Approved' else self.colors['reject']
        ax.add_patch(Rectangle((meter_x, meter_y), meter_width * confidence, meter_height,
                              facecolor=fill_color, alpha=0.8))
        
        # Add text
        ax.text(0.5, 0.7, f'{confidence:.1%}', ha='center', va='center', 
               fontsize=20, fontweight='bold')
        ax.text(0.5, 0.2, 'Model Confidence', ha='center', va='center', fontsize=12)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    
    def plot_batch_summary(self,
                          explanations: List[Dict],
                          claims: List[str],
                          save_path: Optional[str] = None) -> plt.Figure:
        """
        Create summary visualization for multiple claims
        
        Args:
            explanations: List of explanations
            claims: List of claim texts
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Batch Claim Analysis Summary', fontsize=16, fontweight='bold')
        
        # 1. Decision distribution
        ax1 = axes[0, 0]
        decisions = [exp['prediction'] for exp in explanations if 'prediction' in exp]
        decision_counts = pd.Series(decisions).value_counts()
        
        ax1.bar(decision_counts.index, decision_counts.values,
                color=[self.colors['approve'], self.colors['reject']])
        ax1.set_title('Decision Distribution')
        ax1.set_ylabel('Number of Claims')
        
        # Add percentage labels
        for i, (idx, val) in enumerate(decision_counts.items()):
            ax1.text(i, val + 0.5, f'{val/len(decisions)*100:.1f}%', 
                    ha='center', va='bottom')
        
        # 2. Confidence distribution
        ax2 = axes[0, 1]
        confidences = [exp['confidence'] for exp in explanations if 'confidence' in exp]
        approved_conf = [exp['confidence'] for exp in explanations 
                        if exp.get('prediction') == 'Approved']
        rejected_conf = [exp['confidence'] for exp in explanations 
                        if exp.get('prediction') == 'Rejected']
        
        if approved_conf:
            ax2.hist(approved_conf, bins=20, alpha=0.6, label='Approved',
                    color=self.colors['approve'], density=True)
        if rejected_conf:
            ax2.hist(rejected_conf, bins=20, alpha=0.6, label='Rejected',
                    color=self.colors['reject'], density=True)
        
        ax2.set_xlabel('Confidence Score')
        ax2.set_ylabel('Density')
        ax2.set_title('Confidence Distribution by Decision')
        ax2.legend()
        
        # 3. Top influential tokens across all claims
        ax3 = axes[1, 0]
        all_tokens = {}
        for exp in explanations:
            for token, imp in exp.get('influential_tokens', []):
                if token not in all_tokens:
                    all_tokens[token] = []
                all_tokens[token].append(imp)
        
        # Calculate average importance
        avg_importance = {
            token: np.mean(imps) for token, imps in all_tokens.items()
        }
        
        # Get top 10 by absolute importance
        top_tokens = sorted(avg_importance.items(), 
                          key=lambda x: abs(x[1]), 
                          reverse=True)[:10]
        
        tokens, importances = zip(*top_tokens)
        colors = [self.colors['approve'] if imp > 0 else self.colors['reject'] 
                 for imp in importances]
        
        y_pos = np.arange(len(tokens))
        ax3.barh(y_pos, importances, color=colors, alpha=0.8)
        ax3.set_yticks(y_pos)
        ax3.set_yticklabels(tokens)
        ax3.set_xlabel('Average Impact')
        ax3.set_title('Most Influential Terms (Overall)')
        ax3.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        # 4. Error analysis
        ax4 = axes[1, 1]
        error_types = self._analyze_errors(explanations)
        
        if error_types:
            labels, sizes = zip(*error_types.items())
            ax4.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax4.set_title('Error Distribution')
        else:
            ax4.text(0.5, 0.5, 'No errors detected', ha='center', va='center')
            ax4.set_xlim(0, 1)
            ax4.set_ylim(0, 1)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def _analyze_errors(self, explanations: List[Dict]) -> Dict[str, int]:
        """Analyze types of errors in explanations"""
        error_types = {}
        
        for exp in explanations:
            if 'error' in exp:
                error_msg = exp['error']
                # Categorize error
                if 'token' in error_msg.lower():
                    error_type = 'Tokenization Error'
                elif 'model' in error_msg.lower():
                    error_type = 'Model Error'
                else:
                    error_type = 'Other Error'
                
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return error_types
    
    def plot_semantic_patterns(self,
                             patterns: Dict,
                             save_path: Optional[str] = None) -> plt.Figure:
        """
        Visualize semantic patterns in claims
        
        Args:
            patterns: Pattern dictionary from semantic analyzer
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Semantic Pattern Analysis', fontsize=16, fontweight='bold')
        
        # 1. Feature rates comparison
        ax1 = axes[0, 0]
        approved = patterns.get('approved_patterns', {})
        rejected = patterns.get('rejected_patterns', {})
        
        features = ['is_emergency_rate', 'is_preventive_rate', 'has_procedure_rate', 'has_condition_rate']
        feature_labels = ['Emergency', 'Preventive', 'Procedure', 'Condition']
        
        x = np.arange(len(feature_labels))
        width = 0.35
        
        approved_rates = [approved.get(f, 0) for f in features]
        rejected_rates = [rejected.get(f, 0) for f in features]
        
        ax1.bar(x - width/2, approved_rates, width, label='Approved', color=self.colors['approve'], alpha=0.8)
        ax1.bar(x + width/2, rejected_rates, width, label='Rejected', color=self.colors['reject'], alpha=0.8)
        
        ax1.set_xlabel('Feature Type')
        ax1.set_ylabel('Occurrence Rate')
        ax1.set_title('Feature Occurrence by Decision')
        ax1.set_xticks(x)
        ax1.set_xticklabels(feature_labels)
        ax1.legend()
        
        # 2. Key differences visualization
        ax2 = axes[0, 1]
        differences = patterns.get('key_differences', {})
        
        if differences:
            diff_names = []
            diff_values = []
            
            for key, diff_data in differences.items():
                diff_names.append(key.replace('_', ' ').title())
                diff_values.append(diff_data['difference'])
            
            y_pos = np.arange(len(diff_names))
            colors = [self.colors['approve'] if val > 0 else self.colors['reject'] 
                     for val in diff_values]
            
            ax2.barh(y_pos, diff_values, color=colors, alpha=0.8)
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels(diff_names)
            ax2.set_xlabel('Difference (Approved - Rejected)')
            ax2.set_title('Key Decision Factors')
            ax2.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        # 3. Cost distribution
        ax3 = axes[1, 0]
        if 'cost_amount_mean' in approved:
            costs = {
                'Approved': approved.get('cost_amount_mean', 0),
                'Rejected': rejected.get('cost_amount_mean', 0)
            }
            
            ax3.bar(costs.keys(), costs.values(), 
                   color=[self.colors['approve'], self.colors['reject']], alpha=0.8)
            ax3.set_ylabel('Average Cost ($)')
            ax3.set_title('Average Claim Cost by Decision')
            
            # Add value labels
            for i, (k, v) in enumerate(costs.items()):
                ax3.text(i, v + 50, f'${v:,.0f}', ha='center', va='bottom')
        
        # 4. Rules summary
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        # Generate some example rules based on patterns
        rules = self._generate_visual_rules(patterns)
        rules_text = "Generated Business Rules:\n\n"
        for i, rule in enumerate(rules[:5], 1):  # Top 5 rules
            rules_text += f"{i}. {rule}\n"
        
        ax4.text(0.05, 0.95, rules_text, transform=ax4.transAxes,
                fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def _generate_visual_rules(self, patterns: Dict) -> List[str]:
        """Generate visual rules from patterns"""
        rules = []
        
        approved = patterns.get('approved_patterns', {})
        rejected = patterns.get('rejected_patterns', {})
        
        if approved.get('is_emergency_rate', 0) > 0.7:
            rules.append("Emergency claims: 70%+ approval rate")
        
        if rejected.get('is_preventive_rate', 0) > 0.6:
            rules.append("Preventive care: 60%+ rejection rate")
        
        if 'cost_amount_mean' in approved and 'cost_amount_mean' in rejected:
            threshold = (approved['cost_amount_mean'] + rejected['cost_amount_mean']) / 2
            rules.append(f"Cost threshold: ~${threshold:,.0f}")
        
        if approved.get('severity_score_mean', 0) > 0.6:
            rules.append("High severity → likely approval")
        
        if approved.get('medical_term_count_mean', 0) > 3:
            rules.append("Multiple medical terms → higher approval")
        
        return rules
    
    def create_shap_waterfall(self,
                            shap_values,
                            max_display: int = 10,
                            save_path: Optional[str] = None) -> plt.Figure:
        """
        Create SHAP waterfall plot
        
        Args:
            shap_values: SHAP values object
            max_display: Maximum features to display
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure
        """
        plt.figure(figsize=(10, 6))
        shap.waterfall_plot(shap_values[0], max_display=max_display, show=False)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return plt.gcf()
