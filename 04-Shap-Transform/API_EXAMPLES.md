# API Usage Examples

## Starting the API Server

```bash
python api_server.py
```

Server will start at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

## Example 1: Process Single Claim

### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/process-claim" \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "CLM-2024-001",
    "policy_type": "Health Insurance",
    "amount": 15000.00,
    "description": "Emergency surgery for appendicitis",
    "medical_reports": "Confirmed diagnosis, necessary procedure",
    "previous_claims": 2,
    "policy_duration_months": 24
  }'
```

### Python
```python
import requests

claim = {
    "claim_id": "CLM-2024-001",
    "policy_type": "Health Insurance",
    "amount": 15000.00,
    "description": "Emergency surgery for appendicitis",
    "medical_reports": "Confirmed diagnosis, necessary procedure",
    "previous_claims": 2,
    "policy_duration_months": 24
}

response = requests.post(
    "http://localhost:8000/api/v1/process-claim",
    json=claim
)

result = response.json()
print(f"Decision: {result['prediction']}")
print(f"Confidence: {result['confidence']:.1%}")
```

### JavaScript
```javascript
const claim = {
  claim_id: "CLM-2024-001",
  policy_type: "Health Insurance",
  amount: 15000.00,
  description: "Emergency surgery for appendicitis",
  medical_reports: "Confirmed diagnosis, necessary procedure",
  previous_claims: 2,
  policy_duration_months: 24
};

fetch('http://localhost:8000/api/v1/process-claim', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(claim)
})
.then(res => res.json())
.then(data => {
  console.log('Decision:', data.prediction);
  console.log('Confidence:', data.confidence);
});
```

## Example 2: Batch Processing

### Python
```python
import requests

claims = [
    {
        "claim_id": "CLM-001",
        "policy_type": "Health Insurance",
        "amount": 15000,
        "description": "Emergency surgery",
        "previous_claims": 2,
        "policy_duration_months": 24
    },
    {
        "claim_id": "CLM-002",
        "policy_type": "Auto Insurance",
        "amount": 8500,
        "description": "Vehicle accident",
        "previous_claims": 0,
        "policy_duration_months": 36
    }
]

response = requests.post(
    "http://localhost:8000/api/v1/batch-process",
    json=claims
)

results = response.json()
print(f"Processed {results['total']} claims")
for result in results['results']:
    print(f"  {result['claim_id']}: {result['prediction']}")
```

## Example 3: Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "timestamp": "2025-11-12T10:30:00.000000"
}
```

## Example 4: Integration with Database

```python
import requests
import sqlite3

# Fetch claims from database
conn = sqlite3.connect('claims.db')
cursor = conn.execute('SELECT * FROM pending_claims')

for row in cursor:
    claim = {
        'claim_id': row[0],
        'policy_type': row[1],
        'amount': row[2],
        'description': row[3],
        'medical_reports': row[4],
        'previous_claims': row[5],
        'policy_duration_months': row[6]
    }
    
    # Process claim
    response = requests.post(
        'http://localhost:8000/api/v1/process-claim',
        json=claim
    )
    
    result = response.json()
    
    # Update database
    conn.execute('''
        UPDATE pending_claims 
        SET status = ?, confidence = ?, reasoning = ?
        WHERE claim_id = ?
    ''', (result['prediction'], result['confidence'], 
          result['reasoning'], claim['claim_id']))

conn.commit()
conn.close()
```

## Example 5: Asynchronous Processing

```python
import asyncio
import aiohttp

async def process_claim(session, claim):
    async with session.post(
        'http://localhost:8000/api/v1/process-claim',
        json=claim
    ) as response:
        return await response.json()

async def process_multiple_claims(claims):
    async with aiohttp.ClientSession() as session:
        tasks = [process_claim(session, claim) for claim in claims]
        results = await asyncio.gather(*tasks)
        return results

# Usage
claims = [...]  # Your claims list
results = asyncio.run(process_multiple_claims(claims))
```

## Example 6: Error Handling

```python
import requests

def process_claim_safe(claim):
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/process-claim',
            json=claim,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.Timeout:
        print(f"Timeout processing claim {claim['claim_id']}")
        return None
    
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None
    
    except Exception as e:
        print(f"Error: {e}")
        return None

# Usage
result = process_claim_safe(claim)
if result:
    print(f"Decision: {result['prediction']}")
else:
    print("Processing failed, flagging for manual review")
```

## Example 7: Webhook Integration

```python
from flask import Flask, request
import requests

app = Flask(__name__)

@app.route('/webhook/new-claim', methods=['POST'])
def handle_new_claim():
    claim = request.json
    
    # Process with AI agent
    response = requests.post(
        'http://localhost:8000/api/v1/process-claim',
        json=claim
    )
    
    result = response.json()
    
    # Send notification if review needed
    if result['requires_human_review']:
        send_notification(claim['claim_id'], result)
    
    return {'status': 'processed', 'result': result}

def send_notification(claim_id, result):
    # Send email/SMS notification
    print(f"Notification: Claim {claim_id} needs review")

if __name__ == '__main__':
    app.run(port=5000)
```

## Example 8: Monitoring and Logging

```python
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_and_log(claim):
    start_time = datetime.now()
    
    logger.info(f"Processing claim {claim['claim_id']}")
    
    response = requests.post(
        'http://localhost:8000/api/v1/process-claim',
        json=claim
    )
    
    duration = (datetime.now() - start_time).total_seconds()
    result = response.json()
    
    logger.info(
        f"Claim {claim['claim_id']}: "
        f"{result['prediction']} "
        f"(confidence: {result['confidence']:.1%}, "
        f"duration: {duration:.2f}s)"
    )
    
    return result
```

## API Response Format

```json
{
  "claim_id": "CLM-2024-001",
  "prediction": "APPROVED",
  "confidence": 0.85,
  "requires_human_review": false,
  "reasoning": "Decision: APPROVED\nConfidence: 85.0%\n\nKey factors...",
  "top_features": [
    {
      "feature": "emergency",
      "shap_value": 0.3,
      "impact": "positive"
    }
  ],
  "timestamp": "2025-11-12T10:30:00.000000"
}
```

## Error Responses

```json
{
  "detail": "Agent not initialized"
}
```

```json
{
  "detail": "Error processing claim: Invalid claim data"
}
```

## Rate Limiting (Production)

For production deployments, add rate limiting:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/process-claim")
@limiter.limit("100/minute")
async def process_claim(claim: ClaimRequest):
    # ... processing logic
```

## Authentication (Production)

For production deployments, add API key authentication:

```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header()):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.post("/api/v1/process-claim", dependencies=[Depends(verify_api_key)])
async def process_claim(claim: ClaimRequest):
    # ... processing logic
```

## Tips

1. **Always validate claim data before sending to API**
2. **Implement retry logic for network failures**
3. **Log all API calls for audit purposes**
4. **Use batch processing for multiple claims**
5. **Monitor response times and set appropriate timeouts**
6. **Handle human review cases in your workflow**
7. **Store results in a database for tracking**

## Support

For issues or questions:
- Check API documentation at `/docs`
- Review error messages in response
- Check server logs
- Verify claim data format
