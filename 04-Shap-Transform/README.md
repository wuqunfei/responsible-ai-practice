# Insurance Claim AI Agent with SHAP Explainability

An intelligent agent system for processing insurance claims using transformer models (Qwen/DistilBERT) with SHAP explainability, orchestrated by LangGraph.

## 🎯 Features

- **AI-Powered Decision Making**: Uses transformer models for claim classification
- **Explainable AI**: SHAP-based explanations for transparency and auditability
- **Agent Orchestration**: LangGraph workflow for complex decision routing
- **Human-in-the-Loop**: Automatic flagging of low-confidence decisions
- **Production Ready**: Modular architecture for easy deployment

## 📋 Architecture

```
Claim Input → Preprocessing → Classification → Explanation → Decision Routing
                                    ↓              ↓
                              Qwen Model      SHAP Analysis
                                                   ↓
                                    ┌──────────────┴──────────────┐
                                    ↓                             ↓
                            High Confidence                Low Confidence
                                    ↓                             ↓
                            Auto-Approve/Reject          Human Review Required
```

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the demo
python main.py
```

### Basic Usage

```python
from agent import create_agent

# Create agent
agent = create_agent(confidence_threshold=0.7, use_shap=False)

# Process a claim
claim = {
    'claim_id': 'CLM-001',
    'policy_type': 'Health Insurance',
    'amount': 15000,
    'description': 'Emergency surgery for appendicitis',
    'medical_reports': 'Confirmed diagnosis',
    'previous_claims': 2,
    'policy_duration_months': 24
}

result = agent.process_claim(claim)

print(f"Decision: {result['prediction']}")
print(f"Confidence: {result['confidence']:.1%}")
print(f"Reasoning:\n{result['decision_reasoning']}")
```

## 📁 Project Structure

```
insurance_claim_agent/
├── claim_classifier.py    # Qwen model wrapper with SHAP
├── agent.py              # LangGraph agent workflow
├── main.py               # Demo script
├── requirements.txt      # Dependencies
├── README.md            # This file
└── outputs/             # Results and logs
    ├── result_*.json    # Individual claim results
    └── summary.json     # Processing summary
```

## 🔧 Configuration

### Agent Parameters

- **confidence_threshold** (float, default=0.7): Minimum confidence for auto-approval
- **use_shap** (bool, default=False): Use SHAP (slower) vs rule-based explanations (faster)

### Model Selection

The demo uses DistilBERT as a lightweight proxy. For production:

```python
# In claim_classifier.py, replace with:
classifier = QwenClaimClassifier(model_name="Qwen/Qwen-7B")

# Or your fine-tuned model:
classifier = QwenClaimClassifier(model_name="your-org/qwen-insurance-claims")
```

## 📊 Understanding the Output

### Decision States

1. **APPROVED** - Claim automatically approved (high confidence)
2. **REJECTED** - Claim automatically rejected (high confidence)
3. **PENDING HUMAN REVIEW** - Requires manual review (low confidence)

### Explanation Format

```
Decision: APPROVED
Confidence: 85.3%

Key factors influencing this decision:
  • 'emergency' (impact: 0.300, supporting approval)
  • 'surgery' (impact: 0.250, supporting approval)
  • 'hospital' (impact: 0.150, supporting approval)
```

### SHAP Values

- **Positive values** → Push toward approval
- **Negative values** → Push toward rejection
- **Magnitude** → Strength of influence

## 🔬 Advanced: Using Real SHAP

Enable SHAP for more accurate feature attribution:

```python
agent = create_agent(use_shap=True)  # Slower but more accurate
```

SHAP provides:
- Token-level importance scores
- Model-agnostic explanations
- Mathematically grounded attributions

## 🛠️ Extending the Agent

### Add Custom Nodes

```python
def fraud_detection_node(state: ClaimState) -> ClaimState:
    """Custom fraud detection logic"""
    if state['claim_data']['amount'] > 100000:
        state['messages'].append({
            'role': 'system',
            'content': 'High-value claim flagged for fraud review'
        })
    return state

# Add to workflow
workflow.add_node("fraud_check", fraud_detection_node)
workflow.add_edge("classify", "fraud_check")
workflow.add_edge("fraud_check", "explain")
```

### Custom Routing Logic

```python
def custom_router(state: ClaimState) -> str:
    """Route based on multiple factors"""
    if state['claim_data']['amount'] > 50000:
        return "executive_review"
    elif state['confidence'] < 0.6:
        return "human_review"
    else:
        return "finalize"
```

## 📈 Training Your Own Model

### Fine-tune Qwen for Claims

```python
from transformers import AutoModelForSequenceClassification, Trainer

# Load your claim dataset
train_data = load_claim_dataset('claims_train.csv')

# Fine-tune
model = AutoModelForSequenceClassification.from_pretrained(
    "Qwen/Qwen-7B",
    num_labels=2
)

trainer = Trainer(
    model=model,
    train_dataset=train_data,
    # ... training arguments
)

trainer.train()
model.save_pretrained("models/qwen-insurance-claims")
```

## 🔒 Production Considerations

1. **Security**: Sanitize claim data, implement access controls
2. **Scalability**: Use batch processing, deploy on GPU infrastructure
3. **Monitoring**: Log all decisions, track confidence distributions
4. **Compliance**: Ensure explanations meet regulatory requirements (GDPR, etc.)
5. **Human Review**: Implement proper review queue system

## 📝 Sample Claims for Testing

The demo includes 3 test claims:

1. **CLM-2024-001**: Emergency surgery (likely approved)
2. **CLM-2024-002**: Auto accident (moderate confidence)
3. **CLM-2024-003**: Elective cosmetic surgery (likely rejected)

Modify these in `main.py` to test different scenarios.

## 🐛 Troubleshooting

### Model Download Issues

```bash
# Pre-download models
python -c "from transformers import AutoModel; AutoModel.from_pretrained('distilbert-base-uncased')"
```

### SHAP Errors

If SHAP fails, the system automatically falls back to rule-based explanations.

### Memory Issues

For large models like Qwen-7B:
- Use GPU acceleration
- Reduce batch size
- Consider quantization (8-bit, 4-bit)

## 📚 References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [SHAP Documentation](https://shap.readthedocs.io/)
- [Qwen Models](https://github.com/QwenLM/Qwen)
- [Transformers Library](https://huggingface.co/docs/transformers/)

## 📄 License

MIT License - Feel free to use for commercial projects

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional claim types (life, property, etc.)
- Multi-language support
- Real-time processing APIs
- Enhanced visualization of SHAP values
- Integration with claim management systems

## 📧 Support

For questions or issues:
1. Check the troubleshooting section
2. Review the code comments
3. Test with the demo claims first

---

**Note**: This is a demo system. For production use, replace DistilBERT with a properly fine-tuned Qwen model on your actual claim data.
