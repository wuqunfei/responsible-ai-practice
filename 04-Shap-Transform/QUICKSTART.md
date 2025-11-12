# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies (Optional)

For the full version with SHAP:
```bash
pip install -r requirements.txt
```

For the lightweight demo (no dependencies needed):
```bash
python demo_lightweight.py
```

### Step 2: Run the Demo

**Lightweight Demo (Recommended for first run):**
```bash
python demo_lightweight.py
```

**Full Demo (requires dependencies):**
```bash
python main.py
```

### Step 3: Check Results

Results are saved in the `outputs/` directory:
- Individual claim results: `result_CLM-*.json`
- Summary statistics: `summary.json`

## 📊 Understanding the Output

### Claim Decision
```json
{
  "claim_id": "CLM-2024-001",
  "prediction": "APPROVED",
  "confidence": 0.90,
  "requires_human_review": false
}
```

### Explanation
The `top_features` show which factors influenced the decision:
- **Positive SHAP values** → Support approval
- **Negative SHAP values** → Support rejection
- **Magnitude** → Strength of influence

## 🔧 Customization

### Adjust Confidence Threshold

Edit the threshold in the code:
```python
agent = SimpleLangGraphAgent(confidence_threshold=0.8)  # More conservative
```

### Add Custom Claims

Edit the test claims in `demo_lightweight.py`:
```python
test_claims = [
    {
        'claim_id': 'YOUR-CLAIM-ID',
        'policy_type': 'Health Insurance',
        'amount': 25000,
        'description': 'Your claim description',
        # ... other fields
    }
]
```

### Switch to Real Model

Replace the MockClassifier with your trained model in `claim_classifier.py`:
```python
classifier = QwenClaimClassifier(model_name="Qwen/Qwen-7B")
```

## 📈 Production Deployment

### Option 1: API Server

```bash
# Install FastAPI
pip install fastapi uvicorn

# Run server
python api_server.py

# Test with curl
curl -X POST "http://localhost:8000/api/v1/process-claim" \
  -H "Content-Type: application/json" \
  -d '{"claim_id": "TEST-001", "policy_type": "Health", "amount": 10000, ...}'
```

### Option 2: Batch Processing

```python
from agent import create_agent

agent = create_agent()

# Process multiple claims
claims = load_claims_from_database()
for claim in claims:
    result = agent.process_claim(claim)
    save_to_database(result)
```

## 🎯 Key Features Explained

### 1. LangGraph Workflow
The agent follows a state machine pattern:
```
Preprocess → Classify → Explain → Route (Human Review / Finalize)
```

### 2. SHAP Explainability
- Provides feature-level importance
- Model-agnostic explanations
- Mathematically grounded

### 3. Human-in-the-Loop
- Low-confidence claims flagged automatically
- Configurable threshold
- Full audit trail

## 🐛 Common Issues

### "Module not found" Error
```bash
pip install -r requirements.txt
# or use lightweight demo:
python demo_lightweight.py
```

### Memory Issues with Large Models
```python
# Use smaller model or enable quantization
classifier = QwenClaimClassifier(model_name="distilbert-base-uncased")
```

### Slow SHAP Analysis
```python
# Use faster rule-based explanations
agent = create_agent(use_shap=False)
```

## 📚 Next Steps

1. ✅ Run the lightweight demo
2. ✅ Examine the output files
3. ✅ Try custom claims
4. 🔄 Train on your data
5. 🚀 Deploy to production

## 💡 Tips

- Start with `confidence_threshold=0.7` and adjust based on false positive/negative rates
- Use rule-based explanations in production for speed
- Log all decisions for audit and model improvement
- Regularly retrain on new claim data

## 🆘 Need Help?

1. Check the README.md for detailed documentation
2. Review the code comments
3. Examine the example outputs
4. Modify the test claims to understand behavior

Happy claim processing! 🎉
