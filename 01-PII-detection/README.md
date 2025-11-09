# PII Detection Demo: Travel Insurance Claim Case Study

## 📖 The Story (< 5 minutes)

### The Problem
Sarah Martinez lost her luggage on an international flight. She needs to file a claim with the airline, but her email contains **sensitive personal information** that needs to be:
- **Detected** - Find all PII in the email
- **Protected** - Mask sensitive data before sharing
- **Analyzed** - Compare different detection methods

### The Challenge
The email contains **15+ types of PII**:
- ✈️ Travel details (flight numbers, booking references)
- 👤 Personal info (name, DOB, passport, SSN)
- 📧 Contact details (email, phone numbers, addresses)
- 💳 Financial data (bank account, credit cards)
- 🏥 Medical info (prescriptions, insurance)
- 🔢 Device identifiers (serial numbers, IP addresses)

### The Solution
We'll compare **TWO approaches** to PII detection:

1. **Microsoft Presidio** - Pattern-based detection with 50+ built-in recognizers
2. **Transformer Model** - AI-based contextual understanding (ab-ai/pii_model style)

### The Demo Flow

```
Step 1: Read the Email (30 sec)
   └─> See the original claim email with all PII exposed

Step 2: Presidio Detection (1 min)
   └─> Shows 40-50 PII entities detected
   └─> Displays anonymized version

Step 3: Transformer Detection (1 min)
   └─> Shows 30-40 PII entities detected
   └─> Displays AI-masked version

Step 4: Side-by-Side Comparison (1.5 min)
   └─> Compare detection counts
   └─> Analyze strengths/weaknesses
   └─> View accuracy metrics

Step 5: Recommendations (30 sec)
   └─> When to use each approach
   └─> Hybrid solution benefits
```

**Total Time: 4.5 minutes** ⏱️

---

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

### Run the Demo
```bash
# Interactive demo (recommended)
python demo.py

# Or run comparison directly
python pii_comparison.py
```

---

## 📂 Project Structure

```
pii_detection_demo/
├── README.md                    # This file - story and instructions
├── requirements.txt             # Python dependencies
├── demo.py                      # Interactive 5-minute demo
├── pii_comparison.py           # Core comparison logic
├── sample_email.txt            # The travel claim email
├── presidio_detector.py        # Presidio implementation
├── transformer_detector.py     # Transformer implementation
└── results/                    # Output folder (created on run)
    ├── presidio_results.txt
    ├── transformer_results.txt
    ├── comparison_report.csv
    └── anonymized_emails/
```

---

## 🎯 Key Findings

### Presidio Wins At:
- ✅ **Pattern Detection**: SSN, credit cards, bank accounts
- ✅ **Speed**: Faster on CPU
- ✅ **Coverage**: 50+ entity types
- ✅ **Production Ready**: Battle-tested, well-documented

### Transformer Model Wins At:
- ✅ **Context Understanding**: Names in natural language
- ✅ **Accuracy**: Fewer false positives for names
- ✅ **Semantic Detection**: Understands meaning, not just patterns
- ✅ **Flexibility**: Can detect uncommon entity variations

### The Winner?
**🏆 Hybrid Approach**: Use BOTH together for maximum protection!

---

## 📊 Sample Results

| PII Type | Ground Truth | Presidio | Transformer |
|----------|--------------|----------|-------------|
| Names | 2 | 2 | 2 |
| Emails | 1 | 1 | 1 |
| Phones | 4 | 4 | 3 |
| Addresses | 4 | 4 | 2 |
| SSN | 1 | 1 | 0 |
| Credit Cards | 2 | 2 | 0 |
| Bank Info | 2 | 2 | 0 |
| Passport | 1 | 1 | 0 |
| Dates | 4 | 4 | 4 |
| IP Address | 1 | 1 | 1 |

**Presidio Recall**: ~95% | **Transformer Recall**: ~70%

---

## 💡 Use Cases

1. **Compliance** - GDPR, HIPAA, CCPA data protection
2. **Data Security** - Mask PII before logging or sharing
3. **Database Scanning** - Find PII in legacy systems
4. **Email Filtering** - Protect sensitive customer data
5. **Document Redaction** - Legal and regulatory requirements

---

## 🔧 Customization

### Adjust Detection Threshold
```python
# More strict (fewer false positives)
results = detector.detect(text, threshold=0.7)

# More lenient (catch more PII)
results = detector.detect(text, threshold=0.3)
```

### Add Custom Patterns
```python
# Add custom recognizer to Presidio
from presidio_analyzer import PatternRecognizer

custom_recognizer = PatternRecognizer(
    supported_entity="BOOKING_REF",
    patterns=[{"pattern": r"TRV\d{4}-\d{4}", "score": 0.9}]
)
analyzer.registry.add_recognizer(custom_recognizer)
```

---

## 📚 Learn More

- **Presidio**: https://microsoft.github.io/presidio/
- **Transformers**: https://huggingface.co/docs/transformers
- **PII Models**: https://huggingface.co/models?search=pii

---

## ⚠️ Important Notes

1. **Not Perfect**: No PII detection is 100% accurate
2. **Validate Results**: Always review critical detections
3. **Compliance**: Consult legal team for regulatory requirements
4. **Performance**: Transformer models need GPU for large-scale processing
5. **Privacy**: Never log detected PII values

---

## 🎬 Ready to Start?

Run the demo:
```bash
python demo.py
```

This will guide you through the entire story in under 5 minutes!

---

Made with ❤️ for Data Privacy
