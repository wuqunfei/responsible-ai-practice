# Project Structure

```
insurance_claim_agent/
│
├── 📄 Core Files
│   ├── claim_classifier.py      # Qwen/DistilBERT classifier with SHAP
│   ├── agent.py                 # LangGraph agent workflow
│   ├── config.py                # Configuration settings
│   └── requirements.txt         # Python dependencies
│
├── 🚀 Demo & Testing
│   ├── main.py                  # Full demo with dependencies
│   ├── demo_lightweight.py      # Lightweight demo (no dependencies)
│   └── test_agent.py           # Unit tests
│
├── 🌐 Deployment
│   ├── api_server.py           # FastAPI REST API server
│   └── setup.sh                # Installation script
│
├── 📊 Visualization
│   └── visualize.py            # SHAP and results visualization
│
├── 📚 Documentation
│   ├── README.md               # Comprehensive documentation
│   ├── QUICKSTART.md           # Quick start guide
│   ├── CHANGELOG.md            # Version history
│   ├── API_EXAMPLES.md         # API usage examples
│   └── PROJECT_STRUCTURE.md    # This file
│
└── 📁 Output Directory
    └── outputs/                # Results and logs
        ├── result_*.json       # Individual claim results
        ├── summary.json        # Processing summary
        └── *.png              # Visualizations (when generated)
```

## File Descriptions

### Core Components

**claim_classifier.py** (140 lines)
- Qwen model wrapper with SHAP integration
- Batch prediction support
- Simple rule-based fallback explanations
- Configurable model selection

**agent.py** (200 lines)
- LangGraph state machine implementation
- Preprocessing, classification, explanation nodes
- Confidence-based routing
- Human-in-the-loop integration
- Message history tracking

**config.py** (90 lines)
- Centralized configuration
- Model settings
- Threshold parameters
- API configuration
- Database settings

### Demo & Testing

**main.py** (150 lines)
- Production-ready demo
- Multiple test scenarios
- JSON output generation
- Summary statistics
- Requires full dependencies

**demo_lightweight.py** (350 lines)
- No dependencies required
- Mock classifier for testing
- Same workflow as production
- Perfect for development
- Instant feedback

**test_agent.py** (180 lines)
- Comprehensive unit tests
- Classifier tests
- Workflow tests
- Output validation
- Threshold testing

### Deployment

**api_server.py** (250 lines)
- FastAPI REST API
- Single claim processing
- Batch processing endpoint
- Health checks
- OpenAPI documentation
- Production-ready

**setup.sh** (70 lines)
- Automated setup script
- Dependency installation
- Virtual environment creation
- Quick start instructions

### Visualization

**visualize.py** (200 lines)
- SHAP feature importance plots
- Confidence distribution charts
- Decision reports
- Matplotlib visualizations
- Batch visualization support

### Documentation

**README.md** (400+ lines)
- Complete project overview
- Architecture explanation
- Installation instructions
- Usage examples
- Troubleshooting guide
- Production considerations

**QUICKSTART.md** (250 lines)
- 5-minute quick start
- Basic usage examples
- Customization guide
- Common issues
- Next steps

**CHANGELOG.md** (300 lines)
- Version history
- Feature list
- Known limitations
- Future roadmap
- Migration guides

**API_EXAMPLES.md** (400 lines)
- cURL examples
- Python examples
- JavaScript examples
- Error handling
- Integration patterns
- Production tips

## Dependencies

### Required (for full version)
- torch >= 2.0.0
- transformers >= 4.30.0
- shap >= 0.42.0
- langgraph >= 0.0.20
- langchain >= 0.1.0

### Optional (for API server)
- fastapi
- uvicorn

### Optional (for visualization)
- matplotlib >= 3.7.0
- pandas >= 2.0.0

### Lightweight Demo
- **None!** Pure Python implementation

## Usage Patterns

### Pattern 1: Quick Testing
```bash
python demo_lightweight.py
```
No installation needed, instant results.

### Pattern 2: Full Development
```bash
pip install -r requirements.txt
python main.py
```
Full SHAP analysis, all features.

### Pattern 3: Production API
```bash
pip install fastapi uvicorn
python api_server.py
```
RESTful API for integration.

### Pattern 4: Custom Integration
```python
from agent import create_agent
agent = create_agent()
result = agent.process_claim(your_claim)
```
Import as library.

## Data Flow

```
User Input (Claim Data)
    ↓
Preprocessing Node
    ↓
Classification Node (Qwen/DistilBERT)
    ↓
Explanation Node (SHAP/Rules)
    ↓
Confidence Check
    ↓
    ├─→ High Confidence → Auto-Decision
    └─→ Low Confidence → Human Review
    ↓
Output (JSON/API Response)
```

## State Management

The agent uses TypedDict for state:

```python
{
    'claim_data': dict,          # Input claim
    'claim_text': str,           # Formatted text
    'prediction': str,           # APPROVED/REJECTED
    'confidence': float,         # 0.0-1.0
    'shap_explanation': dict,    # Feature importance
    'decision_reasoning': str,   # Human-readable
    'messages': list,            # Workflow history
    'requires_human_review': bool
}
```

## Extension Points

1. **Add Custom Nodes**: Extend agent.py workflow
2. **Custom Classifiers**: Replace in claim_classifier.py
3. **New Explainers**: Add to explanation methods
4. **API Endpoints**: Extend api_server.py
5. **Visualizations**: Add to visualize.py

## Performance

- **Lightweight Demo**: < 100ms per claim
- **Full SHAP**: 2-5s per claim
- **Batch Processing**: 10-50 claims/second
- **Memory**: 500MB (lightweight), 16GB+ (Qwen-7B)

## Output Files

All results saved to `outputs/` directory:

- `result_CLM-*.json` - Individual decisions
- `summary.json` - Aggregate statistics
- `*.png` - Visualizations (optional)
- `audit.log` - Audit trail (optional)

## Integration Examples

### With Database
```python
result = agent.process_claim(claim)
db.save_result(result)
```

### With Queue System
```python
while True:
    claim = queue.get()
    result = agent.process_claim(claim)
    queue.ack(claim)
```

### With Notification System
```python
result = agent.process_claim(claim)
if result['requires_human_review']:
    notify_reviewer(result)
```

## Testing Strategy

1. **Unit Tests**: `test_agent.py`
2. **Integration Tests**: API endpoint tests
3. **Load Tests**: Batch processing
4. **Accuracy Tests**: Compare with human decisions

## Deployment Options

1. **Local**: Run directly on server
2. **Docker**: Containerize with Dockerfile
3. **Cloud**: Deploy to AWS/GCP/Azure
4. **Kubernetes**: Scale horizontally
5. **Serverless**: Lambda/Cloud Functions

## Monitoring

Recommended metrics to track:
- Prediction latency
- Confidence distribution
- Human review rate
- Approval/rejection ratio
- Model accuracy over time

## Security Considerations

1. Validate all input data
2. Sanitize claim descriptions
3. Implement rate limiting
4. Use API authentication
5. Log all access
6. Encrypt sensitive data
7. Regular security audits

## License

MIT License - Free for commercial use

## Support

- Documentation: README.md
- Quick Start: QUICKSTART.md
- API Docs: API_EXAMPLES.md
- Issues: Report bugs in repository
