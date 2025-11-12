"""
FastAPI server for insurance claim processing
Optional production deployment component
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict
from agent import create_agent
import uvicorn
from datetime import datetime

app = FastAPI(
    title="Insurance Claim AI Agent API",
    description="Process insurance claims with AI-powered decision making and explainability",
    version="1.0.0"
)

# Initialize agent (singleton)
agent = None


class ClaimRequest(BaseModel):
    """Request model for claim processing"""
    claim_id: str = Field(..., description="Unique claim identifier")
    policy_type: str = Field(..., description="Type of insurance policy")
    amount: float = Field(..., gt=0, description="Claim amount in USD")
    description: str = Field(..., description="Claim description")
    medical_reports: Optional[str] = Field(None, description="Medical reports or evidence")
    previous_claims: Optional[int] = Field(0, ge=0, description="Number of previous claims")
    policy_duration_months: Optional[int] = Field(0, ge=0, description="Policy duration in months")
    
    class Config:
        schema_extra = {
            "example": {
                "claim_id": "CLM-2024-001",
                "policy_type": "Health Insurance",
                "amount": 15000.00,
                "description": "Emergency surgery for appendicitis",
                "medical_reports": "Confirmed diagnosis, necessary procedure",
                "previous_claims": 2,
                "policy_duration_months": 24
            }
        }


class ClaimResponse(BaseModel):
    """Response model for claim processing"""
    claim_id: str
    prediction: str
    confidence: float
    requires_human_review: bool
    reasoning: str
    top_features: list
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    global agent
    print("Initializing Insurance Claim AI Agent...")
    agent = create_agent(confidence_threshold=0.7, use_shap=False)
    print("Agent initialized successfully!")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Insurance Claim AI Agent",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/v1/process-claim", response_model=ClaimResponse)
async def process_claim(claim: ClaimRequest):
    """
    Process an insurance claim and return decision with explanation.
    
    Args:
        claim: Claim information
        
    Returns:
        Decision, confidence, and explanation
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        # Convert to dict
        claim_data = claim.dict()
        
        # Process claim
        result = agent.process_claim(claim_data)
        
        # Format response
        response = ClaimResponse(
            claim_id=result['claim_data']['claim_id'],
            prediction=result['prediction'],
            confidence=result['confidence'],
            requires_human_review=result['requires_human_review'],
            reasoning=result['decision_reasoning'],
            top_features=result['shap_explanation'].get('top_features', []),
            timestamp=datetime.now().isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing claim: {str(e)}")


@app.post("/api/v1/batch-process")
async def batch_process_claims(claims: list[ClaimRequest]):
    """
    Process multiple claims in batch.
    
    Args:
        claims: List of claims to process
        
    Returns:
        List of results
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    if len(claims) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 claims per batch")
    
    results = []
    
    for claim in claims:
        try:
            claim_data = claim.dict()
            result = agent.process_claim(claim_data)
            
            results.append({
                "claim_id": result['claim_data']['claim_id'],
                "prediction": result['prediction'],
                "confidence": result['confidence'],
                "requires_human_review": result['requires_human_review']
            })
        except Exception as e:
            results.append({
                "claim_id": claim.claim_id,
                "error": str(e)
            })
    
    return {
        "total": len(claims),
        "processed": len(results),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/v1/stats")
async def get_stats():
    """
    Get processing statistics.
    
    Returns:
        Statistics about processed claims
    """
    # In production, this would query a database
    return {
        "message": "Statistics endpoint - implement with database in production",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("="*70)
    print("  Starting Insurance Claim AI Agent API Server")
    print("="*70)
    print("\nEndpoints:")
    print("  - GET  /           - Health check")
    print("  - GET  /health     - Detailed health check")
    print("  - POST /api/v1/process-claim - Process single claim")
    print("  - POST /api/v1/batch-process - Process multiple claims")
    print("  - GET  /api/v1/stats - Get statistics")
    print("\nAPI Documentation:")
    print("  - http://localhost:8000/docs")
    print("="*70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
