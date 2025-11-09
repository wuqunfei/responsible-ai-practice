# 📓 Jupyter Notebook Guide
## Insurance Bias Mitigation Notebook

---

## 🚀 Quick Start

### Option 1: Local Jupyter
```bash
# Install Jupyter if needed
pip install jupyter notebook

# Navigate to the folder with the notebook
cd /path/to/notebook

# Launch Jupyter
jupyter notebook

# Open: insurance_bias_mitigation.ipynb
```

### Option 2: Google Colab
1. Go to [Google Colab](https://colab.research.google.com/)
2. Click **File** → **Upload notebook**
3. Upload `insurance_bias_mitigation.ipynb`
4. Run all cells!

### Option 3: VS Code
1. Open VS Code
2. Install "Jupyter" extension
3. Open `insurance_bias_mitigation.ipynb`
4. Click "Run All" or run cells individually

---

## 📋 Notebook Structure

The notebook contains **10 main sections**:

### Section 1: Setup & Installation
- Import required libraries
- Install packages if needed

### Section 2: Create Biased Dataset
- Generate synthetic travel insurance data
- Introduce intentional gender bias
- Visualize the problem

### Section 3: Data Preparation
- Split into train/test sets
- Separate features and target

### Section 4: Train Baseline Model
- Train RandomForest without fairness constraints
- Establish performance benchmark

### Section 5: Detect Bias
- Use Fairlearn metrics to measure bias
- Calculate DP and EO differences

### Section 6-8: Bias Mitigation (3 Methods)
- **Method 1**: Demographic Parity
- **Method 2**: Equalized Odds (⭐ Best)
- **Method 3**: Threshold Optimizer

### Section 9: Compare Results
- Side-by-side comparison table
- Identify best approach

### Section 10: Visualizations
- 4 comprehensive charts
- Before/after comparisons

### Section 11: Recommendations
- Best practices
- Implementation guidelines

---

## 🎯 How to Use This Notebook

### For Learning:
1. **Run cells sequentially** from top to bottom
2. **Read markdown cells** for explanations
3. **Examine outputs** after each code cell
4. **Experiment** by changing parameters

### For Experimentation:
```python
# Try different bias levels
gender_bias = np.where(df['gender'] == 0, 0.25, -0.25)  # Stronger bias

# Try different sample sizes
df = create_biased_insurance_data(5000)  # More data

# Try different fairness thresholds
mitigator = ExponentiatedGradient(
    estimator=base_estimator,
    constraints=DemographicParity(),
    eps=0.005,  # Stricter fairness
    max_iter=50
)
```

### For Your Own Data:
Replace the synthetic data generation with your actual data:

```python
# Instead of:
# df = create_biased_insurance_data(2000)

# Use:
df = pd.read_csv('your_insurance_data.csv')

# Make sure your data has:
# - Features for modeling
# - A target variable (approved/rejected)
# - A sensitive attribute (gender, race, etc.)
```

---

## 💡 Key Features

### Interactive Elements:
- ✅ **Run cells individually** - Test each step
- ✅ **Modify parameters** - See immediate impact
- ✅ **Visualizations** - Charts update automatically
- ✅ **Print statements** - Track progress

### Learning Benefits:
- 📚 **Rich markdown explanations**
- 📊 **Visual outputs**
- 🎯 **Step-by-step workflow**
- 💡 **Best practice recommendations**

---

## 🔧 Troubleshooting

### Issue: "Module not found" error
```bash
# Solution: Install the package
!pip install fairlearn scikit-learn pandas numpy matplotlib seaborn
```

### Issue: Kernel keeps restarting
```python
# Solution: Reduce sample size
df = create_biased_insurance_data(1000)  # Instead of 2000
```

### Issue: Plots not showing
```python
# Solution: Add matplotlib inline
%matplotlib inline
```

### Issue: Warnings about convergence
```python
# Solution: Increase max_iter
LogisticRegression(max_iter=2000)  # Instead of 1000
```

---

## 📊 Expected Outputs

### After Running the Full Notebook:

1. **Dataset Overview**
   - 2,000 rows × 9 columns
   - Clear gender bias visible

2. **Baseline Results**
   - ~59% accuracy
   - 3.3% demographic parity difference

3. **Mitigated Results**
   - ~57% accuracy (small drop)
   - 2.0% demographic parity difference (40% improvement!)

4. **Visualizations**
   - Approval rate comparison charts
   - Fairness metrics bar charts
   - Trade-off scatter plots

5. **Summary Table**
   - Side-by-side model comparison
   - Clear winner identified

---

## 🎨 Customization Ideas

### 1. Try Different Protected Attributes
```python
# Instead of gender, try age groups
df['age_group'] = pd.cut(df['age'], bins=[0, 30, 50, 100], labels=[0, 1, 2])
sensitive_feature = df['age_group']
```

### 2. Add More Features
```python
data['insurance_tier'] = np.random.choice(['basic', 'premium'], n_samples)
data['claim_history'] = np.random.exponential(2, n_samples)
```

### 3. Test Different Models
```python
# Instead of RandomForest
from sklearn.ensemble import GradientBoostingClassifier
baseline_model = GradientBoostingClassifier(n_estimators=100)
```

### 4. Adjust Fairness Constraints
```python
# Try different epsilon values
mitigator = ExponentiatedGradient(
    estimator=base_estimator,
    constraints=DemographicParity(),
    eps=0.001,  # Very strict
    max_iter=100
)
```

---

## 📈 Performance Tips

### For Faster Execution:
1. Reduce sample size for testing: `n_samples=500`
2. Use fewer estimators: `n_estimators=50`
3. Limit max_iter: `max_iter=25`

### For Better Results:
1. Increase sample size: `n_samples=5000`
2. More estimators: `n_estimators=200`
3. More iterations: `max_iter=100`
4. Cross-validation for robust estimates

---

## 🎓 Learning Path

### Beginner:
1. Run all cells without modifications
2. Read all markdown explanations
3. Examine each output
4. Understand the bias problem

### Intermediate:
1. Modify dataset size
2. Adjust bias parameters
3. Try different fairness constraints
4. Interpret trade-offs

### Advanced:
1. Use your own dataset
2. Add multiple protected attributes
3. Implement custom fairness metrics
4. Create production-ready pipeline

---

## 📚 Additional Resources

### Documentation:
- **Fairlearn**: https://fairlearn.org/
- **Scikit-learn**: https://scikit-learn.org/
- **Pandas**: https://pandas.pydata.org/

### Tutorials:
- Fairlearn Quickstart Guide
- Bias Mitigation Best Practices
- Fair ML Research Papers

### Tools:
- **Jupyter**: Interactive Python notebooks
- **Google Colab**: Free cloud notebooks
- **VS Code**: Local development environment

---

## ✅ Checklist for Success

Before you start:
- [ ] Jupyter or Colab environment ready
- [ ] Required packages installed
- [ ] Notebook downloaded and opened

While running:
- [ ] Run cells in order (top to bottom)
- [ ] Read markdown explanations
- [ ] Check outputs after each cell
- [ ] Note any warnings or errors

After completion:
- [ ] Understand the bias problem
- [ ] Know 3 mitigation methods
- [ ] Can interpret fairness metrics
- [ ] Ready to apply to real data

---

## 🤝 Contributing

Found an issue or have suggestions?
- Test the notebook thoroughly
- Document any bugs
- Share improvements
- Help others learn

---

## 🎉 Happy Learning!

This notebook is designed to be:
- **Educational** - Clear explanations
- **Interactive** - Hands-on experience
- **Practical** - Real-world application
- **Comprehensive** - End-to-end workflow

**Questions?** Review the markdown cells or check the documentation!

---

**Last Updated:** November 2025  
**Version:** 1.0  
**Compatibility:** Python 3.7+, Jupyter, Google Colab, VS Code
