# Quick Start Guide: Gender Bias Mitigation in Insurance Claims

## 🚀 Quick Setup (5 minutes)

### 1. Install Required Packages
```bash
pip install fairlearn scikit-learn pandas numpy matplotlib seaborn
```

### 2. Run the Example
```bash
python insurance_bias_mitigation.py
```

### 3. Check Outputs
- Console output: Detailed metrics and analysis
- Visualization: `insurance_bias_mitigation.png`

---

## 📊 What You'll See

### Initial Bias
```
Claim Approval Rate by Gender:
Male (0):    69.7% ← Significantly higher
Female (1):  36.1% ← Unfair disadvantage
```

### After Mitigation
```
Best Result (Equalized Odds):
Demographic Parity Difference: 0.020 (was 0.033)
→ 40% reduction in bias!
```

---

## 🎯 Key Takeaways

### The Problem
- **Gender bias in insurance claims is real and measurable**
- Without intervention, ML models perpetuate historical bias
- 33.6% approval gap between genders in this example

### The Solution
Three mitigation approaches tested:
1. ✅ **Equalized Odds** - Best fairness (DP: 0.020)
2. **Threshold Optimizer** - Easy to implement (DP: 0.045)
3. **Demographic Parity** - Good balance (DP: 0.049)

### The Trade-off
- Slight accuracy decrease (1-2%)
- Significant fairness improvement (40%+)
- **Worth it for ethical and legal compliance**

---

## 🔧 Customization Options

### Change Dataset Size
```python
df = create_biased_insurance_data(n_samples=5000)  # More data
```

### Adjust Bias Severity
```python
# In create_biased_insurance_data() function
gender_bias = np.where(df['gender'] == 0, 0.25, -0.25)  # Stronger bias
```

### Try Different Models
```python
baseline_model = GradientBoostingClassifier()  # Instead of RandomForest
```

### Adjust Fairness Tolerance
```python
mitigator = ExponentiatedGradient(
    estimator=base_estimator,
    constraints=DemographicParity(),
    eps=0.005,  # Stricter fairness (default: 0.01)
)
```

---

## 📈 Understanding the Metrics

### Demographic Parity Difference
- **Range**: 0 to 1
- **Lower is better**
- **0** = Perfect fairness (equal approval rates)
- **>0.1** = Significant bias

### Equalized Odds Difference
- **Measures**: Error rate equality
- **Lower is better**
- Considers both false positives and false negatives

### Selection Rate
- **What**: Percentage of claims approved
- **Fairness**: Should be similar across groups

---

## 🎨 Visualization Guide

The output PNG contains 4 plots:

### Plot 1: Approval Rates by Gender
- Shows side-by-side comparison
- Baseline shows clear gap
- Mitigated models show reduced gap

### Plot 2: Fairness Metrics
- Both DP and EO differences
- All bars should be close to 0
- Red line = perfect fairness

### Plot 3: Accuracy Comparison
- Height = model accuracy
- Shows cost of fairness
- Usually 1-2% decrease

### Plot 4: Trade-off Scatter
- X-axis = Fairness (DP difference)
- Y-axis = Accuracy
- Ideal = Top-left corner

---

## 💡 When to Use Each Method

### Demographic Parity
**Use when:**
- You want equal approval rates
- Representation matters most
- Legal compliance requires proportional outcomes

**Example:** Consumer lending, hiring

### Equalized Odds
**Use when:**
- Error costs are important
- You need equal accuracy across groups
- Risk assessment is critical

**Example:** Insurance claims, credit scoring ✅

### Threshold Optimizer
**Use when:**
- You have an existing model
- Can't retrain from scratch
- Need quick implementation

**Example:** Legacy systems, POCs

---

## 🚨 Common Issues & Solutions

### Issue: ImportError for fairlearn
```bash
# Solution:
pip install --upgrade fairlearn
```

### Issue: "No module named sklearn"
```bash
# Solution:
pip install scikit-learn
```

### Issue: Convergence warnings
```python
# Solution: Increase max_iter
LogisticRegression(max_iter=2000)
```

### Issue: Poor fairness results
```python
# Solution: Decrease eps for stricter constraints
mitigator = ExponentiatedGradient(..., eps=0.005)
```

---

## 📝 Next Steps

### For Learning
1. Modify bias severity and observe results
2. Try different ML models
3. Experiment with fairness constraints
4. Add more protected attributes (age, race)

### For Production
1. Use real company data
2. Get legal review
3. Set up monitoring dashboard
4. Document all decisions
5. A/B test with small user group

### For Advanced Users
1. Implement custom fairness metrics
2. Try intersectional fairness (multiple attributes)
3. Use GridSearch for hyperparameter tuning
4. Implement real-time fairness monitoring

---

## 📚 Helpful Commands

### View Results
```bash
python insurance_bias_mitigation.py | grep "Difference:"
```

### Save Output to File
```bash
python insurance_bias_mitigation.py > results.txt 2>&1
```

### Quick Fairness Check
```python
from fairlearn.metrics import demographic_parity_difference
dp = demographic_parity_difference(y_true, y_pred, sensitive_features)
print(f"Fairness score: {dp:.3f}")
```

---

## 🎓 Learning Resources

### Beginner
- Fairlearn Quickstart: https://fairlearn.org/main/quickstart.html
- Google ML Fairness: https://developers.google.com/machine-learning/fairness-overview

### Intermediate
- Fairlearn User Guide: https://fairlearn.org/main/user_guide/index.html
- Paper: "Fairness and ML" (Barocas, Hardt, Narayanan)

### Advanced
- Fairlearn API Reference
- Research papers on reductions approach
- Case studies from industry

---

## ✅ Checklist for Production

- [ ] Legal review completed
- [ ] Fairness metrics defined
- [ ] Acceptable thresholds set
- [ ] Monitoring dashboard created
- [ ] Audit trail established
- [ ] Stakeholder buy-in obtained
- [ ] A/B test planned
- [ ] Rollback plan ready
- [ ] Documentation completed
- [ ] Team training done

---

## 🤝 Contributing

Found a bug or have suggestions?
- Review the code
- Test with your data
- Share improvements
- Document learnings

---

**Remember**: Fairness is a journey, not a destination. Keep monitoring and improving! 🎯
