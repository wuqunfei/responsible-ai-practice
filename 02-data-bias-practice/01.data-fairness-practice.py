"""
Travel Insurance Claims - Gender Bias Detection and Mitigation
Using Fairlearn Framework

This example demonstrates:
1. Creating a synthetic dataset with gender bias
2. Training a biased model
3. Detecting bias using fairness metrics
4. Mitigating bias using Fairlearn techniques
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# Fairlearn imports
from fairlearn.metrics import MetricFrame, selection_rate, false_positive_rate, false_negative_rate
from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference
from fairlearn.reductions import ExponentiatedGradient, DemographicParity, EqualizedOdds
from fairlearn.postprocessing import ThresholdOptimizer

# Set random seed for reproducibility
np.random.seed(42)


# ==========================================
# 1. CREATE SYNTHETIC BIASED DATASET
# ==========================================

def create_biased_insurance_data(n_samples=2000):
    """
    Create synthetic travel insurance claim data with inherent gender bias.
    The dataset simulates lost package claims with gender-based disparities.
    """

    # Generate features
    data = {
        'age': np.random.randint(18, 75, n_samples),
        'trip_duration': np.random.randint(1, 30, n_samples),
        'package_value': np.random.uniform(50, 2000, n_samples),
        'claim_amount': np.random.uniform(20, 1500, n_samples),
        'previous_claims': np.random.poisson(0.5, n_samples),
        'travel_frequency': np.random.randint(1, 20, n_samples),
        'destination_risk': np.random.choice([0, 1, 2], n_samples, p=[0.5, 0.3, 0.2]),
    }

    # Gender: 0 = Male, 1 = Female
    data['gender'] = np.random.choice([0, 1], n_samples, p=[0.5, 0.5])

    df = pd.DataFrame(data)

    # Create target variable with BIAS
    # Legitimate claim probability based on features
    legitimate_prob = (
            0.3 +
            0.1 * (df['claim_amount'] / df['package_value'] < 0.8) +
            0.1 * (df['previous_claims'] == 0) +
            0.1 * (df['destination_risk'] == 0) +
            0.05 * (df['age'] > 30) +
            0.05 * (df['trip_duration'] < 14)
    )

    # INTRODUCE GENDER BIAS:
    # - Male claims are approved more easily (bias in their favor)
    # - Female claims face stricter scrutiny
    gender_bias = np.where(df['gender'] == 0, 0.15, -0.15)  # +15% for males, -15% for females

    biased_prob = np.clip(legitimate_prob + gender_bias, 0, 1)

    # Generate claims (1 = Approved, 0 = Rejected)
    df['claim_approved'] = (np.random.random(n_samples) < biased_prob).astype(int)

    return df


# Create dataset
print("=" * 70)
print("CREATING BIASED TRAVEL INSURANCE DATASET")
print("=" * 70)

df = create_biased_insurance_data(2000)

print("\nDataset Overview:")
print(df.head(10))
print(f"\nDataset Shape: {df.shape}")
print(f"\nGender Distribution:")
print(df['gender'].value_counts())
print(f"\nClaim Approval Rate by Gender:")
print(df.groupby('gender')['claim_approved'].mean())

# ==========================================
# 2. PREPARE DATA FOR MODELING
# ==========================================

# Features and target
X = df.drop(['claim_approved', 'gender'], axis=1)
y = df['claim_approved']
sensitive_feature = df['gender']

# Split data
X_train, X_test, y_train, y_test, sf_train, sf_test = train_test_split(
    X, y, sensitive_feature, test_size=0.3, random_state=42, stratify=sensitive_feature
)

print("\n" + "=" * 70)
print("TRAIN/TEST SPLIT")
print("=" * 70)
print(f"Training samples: {len(X_train)}")
print(f"Test samples: {len(X_test)}")

# ==========================================
# 3. TRAIN BIASED MODEL (Baseline)
# ==========================================

print("\n" + "=" * 70)
print("TRAINING BASELINE (BIASED) MODEL")
print("=" * 70)

baseline_model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
baseline_model.fit(X_train, y_train)

y_pred_baseline = baseline_model.predict(X_test)
baseline_accuracy = accuracy_score(y_test, y_pred_baseline)

print(f"\nBaseline Model Accuracy: {baseline_accuracy:.4f}")

# ==========================================
# 4. DETECT BIAS USING FAIRLEARN METRICS
# ==========================================

print("\n" + "=" * 70)
print("BIAS DETECTION - FAIRNESS METRICS")
print("=" * 70)

# Create MetricFrame for detailed analysis
metrics = {
    'accuracy': accuracy_score,
    'selection_rate': selection_rate,
    'false_positive_rate': false_positive_rate,
    'false_negative_rate': false_negative_rate,
}

metric_frame_baseline = MetricFrame(
    metrics=metrics,
    y_true=y_test,
    y_pred=y_pred_baseline,
    sensitive_features=sf_test
)

print("\n--- Performance by Gender ---")
print(metric_frame_baseline.by_group)

# Calculate fairness metrics
dp_diff_baseline = demographic_parity_difference(
    y_true=y_test,
    y_pred=y_pred_baseline,
    sensitive_features=sf_test
)

eo_diff_baseline = equalized_odds_difference(
    y_true=y_test,
    y_pred=y_pred_baseline,
    sensitive_features=sf_test
)

print(f"\n--- Fairness Metrics ---")
print(f"Demographic Parity Difference: {dp_diff_baseline:.4f}")
print(f"  (Ideal = 0, measures difference in approval rates)")
print(f"Equalized Odds Difference: {eo_diff_baseline:.4f}")
print(f"  (Ideal = 0, measures difference in error rates)")

# ==========================================
# 5. BIAS MITIGATION - METHOD 1: Reductions
# ==========================================

print("\n" + "=" * 70)
print("BIAS MITIGATION - EXPONENTIATED GRADIENT (REDUCTIONS)")
print("=" * 70)

# Using Demographic Parity constraint
base_estimator = LogisticRegression(solver='liblinear', max_iter=1000)

# Mitigator with Demographic Parity
mitigator_dp = ExponentiatedGradient(
    estimator=base_estimator,
    constraints=DemographicParity(),
    eps=0.01,
    max_iter=50
)

mitigator_dp.fit(X_train, y_train, sensitive_features=sf_train)
y_pred_mitigated_dp = mitigator_dp.predict(X_test)

accuracy_mitigated_dp = accuracy_score(y_test, y_pred_mitigated_dp)

print(f"\nMitigated Model (Demographic Parity) Accuracy: {accuracy_mitigated_dp:.4f}")

# Evaluate fairness of mitigated model
metric_frame_mitigated_dp = MetricFrame(
    metrics=metrics,
    y_true=y_test,
    y_pred=y_pred_mitigated_dp,
    sensitive_features=sf_test
)

print("\n--- Performance by Gender (Mitigated - DP) ---")
print(metric_frame_mitigated_dp.by_group)

dp_diff_mitigated = demographic_parity_difference(
    y_true=y_test,
    y_pred=y_pred_mitigated_dp,
    sensitive_features=sf_test
)

print(f"\nDemographic Parity Difference (Mitigated): {dp_diff_mitigated:.4f}")

# ==========================================
# 6. BIAS MITIGATION - METHOD 2: Equalized Odds
# ==========================================

print("\n" + "=" * 70)
print("BIAS MITIGATION - EQUALIZED ODDS")
print("=" * 70)

# Mitigator with Equalized Odds constraint
mitigator_eo = ExponentiatedGradient(
    estimator=base_estimator,
    constraints=EqualizedOdds(),
    eps=0.01,
    max_iter=50
)

mitigator_eo.fit(X_train, y_train, sensitive_features=sf_train)
y_pred_mitigated_eo = mitigator_eo.predict(X_test)

accuracy_mitigated_eo = accuracy_score(y_test, y_pred_mitigated_eo)

print(f"\nMitigated Model (Equalized Odds) Accuracy: {accuracy_mitigated_eo:.4f}")

metric_frame_mitigated_eo = MetricFrame(
    metrics=metrics,
    y_true=y_test,
    y_pred=y_pred_mitigated_eo,
    sensitive_features=sf_test
)

print("\n--- Performance by Gender (Mitigated - EO) ---")
print(metric_frame_mitigated_eo.by_group)

eo_diff_mitigated = equalized_odds_difference(
    y_true=y_test,
    y_pred=y_pred_mitigated_eo,
    sensitive_features=sf_test
)

print(f"\nEqualized Odds Difference (Mitigated): {eo_diff_mitigated:.4f}")

# ==========================================
# 7. BIAS MITIGATION - METHOD 3: Threshold Optimizer
# ==========================================

print("\n" + "=" * 70)
print("BIAS MITIGATION - THRESHOLD OPTIMIZER (POST-PROCESSING)")
print("=" * 70)

# Train a base model first
base_model = LogisticRegression(solver='liblinear', max_iter=1000)
base_model.fit(X_train, y_train)

# Apply threshold optimization
threshold_optimizer = ThresholdOptimizer(
    estimator=base_model,
    constraints="demographic_parity",
    predict_method='predict_proba'
)

threshold_optimizer.fit(X_train, y_train, sensitive_features=sf_train)
y_pred_threshold = threshold_optimizer.predict(X_test, sensitive_features=sf_test)

accuracy_threshold = accuracy_score(y_test, y_pred_threshold)

print(f"\nThreshold Optimized Model Accuracy: {accuracy_threshold:.4f}")

metric_frame_threshold = MetricFrame(
    metrics=metrics,
    y_true=y_test,
    y_pred=y_pred_threshold,
    sensitive_features=sf_test
)

print("\n--- Performance by Gender (Threshold Optimized) ---")
print(metric_frame_threshold.by_group)

dp_diff_threshold = demographic_parity_difference(
    y_true=y_test,
    y_pred=y_pred_threshold,
    sensitive_features=sf_test
)

print(f"\nDemographic Parity Difference (Threshold): {dp_diff_threshold:.4f}")

# ==========================================
# 8. COMPARISON SUMMARY
# ==========================================

print("\n" + "=" * 70)
print("COMPARISON SUMMARY")
print("=" * 70)

summary_df = pd.DataFrame({
    'Model': ['Baseline (Biased)', 'Demographic Parity', 'Equalized Odds', 'Threshold Optimizer'],
    'Accuracy': [baseline_accuracy, accuracy_mitigated_dp, accuracy_mitigated_eo, accuracy_threshold],
    'DP Difference': [dp_diff_baseline, dp_diff_mitigated,
                      demographic_parity_difference(y_true=y_test, y_pred=y_pred_mitigated_eo,
                                                    sensitive_features=sf_test),
                      dp_diff_threshold],
    'EO Difference': [eo_diff_baseline,
                      equalized_odds_difference(y_true=y_test, y_pred=y_pred_mitigated_dp, sensitive_features=sf_test),
                      eo_diff_mitigated,
                      equalized_odds_difference(y_true=y_test, y_pred=y_pred_threshold, sensitive_features=sf_test)]
})

print("\n", summary_df.to_string(index=False))

print("\n" + "=" * 70)
print("INTERPRETATION:")
print("=" * 70)
print("""
1. DEMOGRAPHIC PARITY DIFFERENCE: 
   - Measures difference in approval rates between groups
   - Closer to 0 is better (means similar approval rates)

2. EQUALIZED ODDS DIFFERENCE:
   - Measures difference in error rates (FPR and FNR) between groups
   - Closer to 0 is better (means similar error patterns)

3. TRADE-OFFS:
   - Mitigation reduces bias but may slightly reduce accuracy
   - Different constraints optimize for different fairness notions
   - Choose based on your fairness requirements and regulatory needs
""")

# ==========================================
# 9. VISUALIZATION
# ==========================================

print("\n" + "=" * 70)
print("CREATING VISUALIZATIONS")
print("=" * 70)

fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Plot 1: Approval Rates by Gender
models = ['Baseline', 'Demographic\nParity', 'Equalized\nOdds', 'Threshold\nOptimizer']
predictions = [y_pred_baseline, y_pred_mitigated_dp, y_pred_mitigated_eo, y_pred_threshold]

approval_rates_male = []
approval_rates_female = []

for pred in predictions:
    male_mask = sf_test == 0
    female_mask = sf_test == 1
    approval_rates_male.append(pred[male_mask].mean())
    approval_rates_female.append(pred[female_mask].mean())

x = np.arange(len(models))
width = 0.35

axes[0, 0].bar(x - width / 2, approval_rates_male, width, label='Male', alpha=0.8)
axes[0, 0].bar(x + width / 2, approval_rates_female, width, label='Female', alpha=0.8)
axes[0, 0].set_xlabel('Model')
axes[0, 0].set_ylabel('Approval Rate')
axes[0, 0].set_title('Claim Approval Rates by Gender')
axes[0, 0].set_xticks(x)
axes[0, 0].set_xticklabels(models)
axes[0, 0].legend()
axes[0, 0].grid(axis='y', alpha=0.3)

# Plot 2: Fairness Metrics Comparison
axes[0, 1].bar(summary_df['Model'], summary_df['DP Difference'], alpha=0.7, label='DP Difference')
axes[0, 1].bar(summary_df['Model'], summary_df['EO Difference'], alpha=0.7, label='EO Difference')
axes[0, 1].set_xlabel('Model')
axes[0, 1].set_ylabel('Difference')
axes[0, 1].set_title('Fairness Metrics (Lower is Better)')
axes[0, 1].legend()
axes[0, 1].tick_params(axis='x', rotation=45)
axes[0, 1].axhline(y=0, color='r', linestyle='--', alpha=0.5)
axes[0, 1].grid(axis='y', alpha=0.3)

# Plot 3: Accuracy Comparison
axes[1, 0].bar(summary_df['Model'], summary_df['Accuracy'], color='skyblue', alpha=0.8)
axes[1, 0].set_xlabel('Model')
axes[1, 0].set_ylabel('Accuracy')
axes[1, 0].set_title('Model Accuracy Comparison')
axes[1, 0].tick_params(axis='x', rotation=45)
axes[1, 0].set_ylim([0, 1])
axes[1, 0].grid(axis='y', alpha=0.3)

# Plot 4: Trade-off visualization
axes[1, 1].scatter(summary_df['DP Difference'].abs(), summary_df['Accuracy'], s=200, alpha=0.6)
for idx, model in enumerate(summary_df['Model']):
    axes[1, 1].annotate(model,
                        (summary_df['DP Difference'].abs().iloc[idx],
                         summary_df['Accuracy'].iloc[idx]),
                        fontsize=9, ha='right')
axes[1, 1].set_xlabel('Demographic Parity Difference (abs)')
axes[1, 1].set_ylabel('Accuracy')
axes[1, 1].set_title('Fairness-Accuracy Trade-off')
axes[1, 1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('insurance_bias_mitigation.png', dpi=300, bbox_inches='tight')
print("Visualization saved!")

# ==========================================
# 10. RECOMMENDATIONS
# ==========================================

print("\n" + "=" * 70)
print("RECOMMENDATIONS FOR INSURANCE COMPANIES")
print("=" * 70)
print("""
1. REGULAR BIAS AUDITS:
   - Monitor approval rates across gender and other protected attributes
   - Set up automated fairness metric tracking

2. CHOOSE APPROPRIATE FAIRNESS CONSTRAINTS:
   - Demographic Parity: If you want equal approval rates
   - Equalized Odds: If you want equal error rates (recommended for insurance)

3. IMPLEMENT MITIGATION STRATEGIES:
   - Use Fairlearn's reductions approach during model training
   - Apply post-processing threshold optimization for existing models

4. DOCUMENTATION & COMPLIANCE:
   - Document all fairness decisions and trade-offs
   - Ensure compliance with anti-discrimination regulations

5. CONTINUOUS MONITORING:
   - Track fairness metrics in production
   - Retrain and adjust as patterns change over time
""")

print("\n" + "=" * 70)
print("SCRIPT COMPLETED SUCCESSFULLY!")
print("=" * 70)
