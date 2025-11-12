# Configuration File for Insurance Claim AI Agent

# Model Configuration
MODEL_NAME = "distilbert-base-uncased"  # Replace with "Qwen/Qwen-7B" for production
MODEL_DEVICE = "cpu"  # or "cuda" for GPU
USE_QUANTIZATION = False  # 8-bit quantization for memory efficiency

# Agent Configuration
CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence for auto-approval (0.0-1.0)
USE_SHAP = False  # True for SHAP analysis, False for faster rule-based
SHAP_SAMPLES = 50  # Number of SHAP samples (lower = faster)

# Workflow Configuration
ENABLE_FRAUD_DETECTION = False
ENABLE_POLICY_VALIDATION = False
MAX_CLAIM_AMOUNT = 500000  # Maximum auto-processable amount
HIGH_VALUE_THRESHOLD = 50000  # Flag for additional review

# Processing Configuration
BATCH_SIZE = 10  # For batch processing
MAX_RETRIES = 3  # Retry failed predictions
TIMEOUT_SECONDS = 30  # Processing timeout

# Rule-based Weights (for simple explanations)
KEYWORD_WEIGHTS = {
    'emergency': 0.30,
    'surgery': 0.25,
    'accident': 0.20,
    'hospital': 0.15,
    'diagnosis': 0.15,
    'necessary': 0.10,
    'confirmed': 0.10,
    'fraud': -0.50,
    'suspicious': -0.40,
    'elective': -0.30,
    'cosmetic': -0.35,
    'unauthorized': -0.35,
    'false': -0.30,
}

# Output Configuration
OUTPUT_DIR = "outputs"
SAVE_INDIVIDUAL_RESULTS = True
SAVE_SUMMARY = True
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# API Configuration (for api_server.py)
API_HOST = "0.0.0.0"
API_PORT = 8000
API_MAX_BATCH_SIZE = 100
ENABLE_CORS = True
API_KEY_REQUIRED = False  # Set to True in production

# Database Configuration (optional)
USE_DATABASE = False
DB_CONNECTION_STRING = "postgresql://user:pass@localhost/claims"
SAVE_TO_DB = False

# Notification Configuration
SEND_NOTIFICATIONS = False
NOTIFICATION_EMAIL = "claims@insurance.com"
NOTIFY_ON_HIGH_VALUE = True
NOTIFY_ON_LOW_CONFIDENCE = True

# Audit Configuration
ENABLE_AUDIT_LOG = True
AUDIT_LOG_FILE = "audit.log"
LOG_ALL_DECISIONS = True

# Performance Monitoring
ENABLE_METRICS = True
METRICS_FILE = "metrics.json"
TRACK_LATENCY = True
TRACK_CONFIDENCE_DISTRIBUTION = True
