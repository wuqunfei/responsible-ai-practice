"""
LangGraph Agent for Insurance Claim Processing with GPT-2
"""
import operator
import os
from typing import TypedDict, Annotated, Literal

from langgraph.graph import StateGraph, END
from loguru import logger

from claim_classifier import GPT2ClaimClassifier
from langfuse.langchain import CallbackHandler

class ClaimState(TypedDict):
    """State object for the claim processing workflow"""
    claim_data: dict
    claim_text: str
    prediction: str
    confidence: float
    shap_explanation: dict
    decision_reasoning: str
    messages: Annotated[list, operator.add]
    requires_human_review: bool


class ClaimProcessingAgent:
    """LangGraph agent for processing insurance claims with explainability"""

    def __init__(self, confidence_threshold: float = 0.7, use_shap: bool = False):
        """
        Initialize the claim processing agent.
        
        Args:
            confidence_threshold: Minimum confidence for auto-approval
            use_shap: Whether to use SHAP (slower, more accurate) or simple explanations (faster)
        """
        self.classifier = GPT2ClaimClassifier()
        self.confidence_threshold = confidence_threshold
        self.use_shap = use_shap
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(ClaimState)

        # Add nodes
        workflow.add_node("preprocess", self.preprocess_claim)
        workflow.add_node("classify", self.classify_claim)
        workflow.add_node("explain", self.explain_decision)
        workflow.add_node("human_review", self.request_human_review)
        workflow.add_node("finalize", self.finalize_decision)

        # Define edges
        workflow.set_entry_point("preprocess")
        workflow.add_edge("preprocess", "classify")
        workflow.add_edge("classify", "explain")

        # Conditional routing based on confidence
        workflow.add_conditional_edges(
            "explain",
            self.check_confidence_threshold,
            {
                "human_review": "human_review",
                "finalize": "finalize"
            }
        )

        workflow.add_edge("human_review", END)
        workflow.add_edge("finalize", END)

        return workflow.compile()

    def preprocess_claim(self, state: ClaimState) -> ClaimState:
        """Extract and format claim information"""
        claim_data = state['claim_data']

        # Format claim as text for model
        claim_text = f"""
Claim ID: {claim_data.get('id', 'N/A')}
Policy Type: {claim_data.get('policy_type', 'N/A')}
Claim Amount: ${claim_data.get('amount', 0):,.2f}
Description: {claim_data.get('description', 'N/A')}
Medical Reports: {claim_data.get('medical_reports', 'None provided')}
Previous Claims: {claim_data.get('previous_claims', 0)}
Policy Duration: {claim_data.get('policy_duration_months', 0)} months
"""

        state['claim_text'] = claim_text.strip()
        state['messages'] = state.get('messages', [])
        state['messages'].append({
            'role': 'system',
            'content': f"Processing claim: {claim_data.get('id', 'Unknown')}"
        })

        logger.info(f"✓ Preprocessed claim {claim_data.get('id')}")
        return state

    def classify_claim(self, state: ClaimState) -> ClaimState:
        """Run classification with the GPT-2 model"""
        claim_text = state['claim_text']

        logger.info("  Running GPT-2 classification...")
        # Get prediction
        probs = self.classifier.predict(claim_text)
        prediction = "APPROVED" if probs[1] > 0.5 else "REJECTED"
        confidence = float(max(probs))

        state['prediction'] = prediction
        state['confidence'] = confidence
        state['messages'].append({
            'role': 'assistant',
            'content': f"Classification: {prediction} (confidence: {confidence:.1%})"
        })

        logger.success(f"✓ Classification: {prediction} with {confidence:.1%} confidence")
        return state

    def explain_decision(self, state: ClaimState) -> ClaimState:
        """Generate explanation using SHAP or simple rules"""
        claim_text = state['claim_text']
        claim_id = state['claim_data'].get('claim_id', 'unknown_claim')

        # Get explanation
        if self.use_shap:
            logger.info("  Using SHAP for detailed explanation...")
            try:
                explanation = self.classifier.get_shap_explanation(claim_text, claim_id=claim_id, num_samples=100)
            except Exception as e:
                logger.warning(f"  Warning: SHAP failed, using simple explanation: {e}")
                explanation = self.classifier.get_simple_explanation(claim_text)
        else:
            logger.info("  Using rule-based explanation (fast mode)...")
            explanation = self.classifier.get_simple_explanation(claim_text)

        state['shap_explanation'] = explanation

        # Format reasoning
        top_features = explanation.get('top_features', [])

        reasoning_parts = [
            f"Decision: {state['prediction']}",
            f"Confidence: {state['confidence']:.1%}",
            f"Explanation Method: {explanation.get('method', 'unknown')}",
            "",
            "Key factors influencing this decision:"
        ]

        for i, feature in enumerate(top_features[:8], 1):
            impact = "supporting approval" if feature['shap_value'] > 0 else "supporting rejection"
            reasoning_parts.append(
                f"  {i}. '{feature['feature']}' (impact: {abs(feature['shap_value']):.3f}, {impact})"
            )

        # Add visualization info if available
        if explanation.get('html_path'):
            reasoning_parts.append("")
            reasoning_parts.append(f"📊 SHAP visualization saved to: {explanation['html_path']}")
        if explanation.get('image_path'):
            reasoning_parts.append(f"📈 SHAP chart saved to: {explanation['image_path']}")

        reasoning = "\n".join(reasoning_parts)
        state['decision_reasoning'] = reasoning
        state['messages'].append({
            'role': 'assistant',
            'content': reasoning
        })

        logger.success("✓ Generated explanation")
        return state

    def check_confidence_threshold(self, state: ClaimState) -> Literal["human_review", "finalize"]:
        """Route based on confidence level"""
        if state['confidence'] < self.confidence_threshold:
            return "human_review"
        return "finalize"

    def request_human_review(self, state: ClaimState) -> ClaimState:
        """Flag for human review when confidence is low"""
        state['requires_human_review'] = True
        state['messages'].append({
            'role': 'system',
            'content': f"⚠️ Confidence ({state['confidence']:.1%}) below threshold ({self.confidence_threshold:.1%}). Flagging for human review."
        })
        state['prediction'] = f"{state['prediction']} - PENDING HUMAN REVIEW"
        
        # Set status for human review cases
        state['status'] = f"{state['prediction']}"
        
        logger.warning(f"⚠️  Flagged for human review (confidence: {state['confidence']:.1%})")
        logger.info(f"DEBUG: Status set to: {state['status']}")
        return state

    def finalize_decision(self, state: ClaimState) -> ClaimState:
        """Finalize the claim decision"""
        state['requires_human_review'] = False
        state['messages'].append({
            'role': 'system',
            'content': f"✓ Claim decision finalized: {state['prediction']}"
        })

        # Set status based on prediction (this is for high confidence cases)
        state['status'] = state['prediction']
        
        logger.info(f"DEBUG: Finalize decision - Status set to: {state['status']}")
        logger.success(f"✓ Decision: {state['status']}")
        return state

    def process_claim(self, claim_data: dict) -> dict:
        """
        Process a single claim through the workflow.
        
        Args:
            claim_data: Dictionary containing claim information
            
        Returns:
            Final state with decision and explanation
        """
        logger.info("\n" + "=" * 70)
        logger.info(f"🔍 Processing Claim: {claim_data.get('id', 'Unknown')}")
        logger.info("=" * 70)

        initial_state = {
            'claim_data': claim_data,
            'claim_text': '',
            'prediction': '',
            'confidence': 0.0,
            'shap_explanation': {},
            'decision_reasoning': '',
            'messages': [],
            'requires_human_review': False,
            'status': 'Unknown'
        }
        langfuse_callback_handler = CallbackHandler()
        result = self.workflow.invoke(
            initial_state,
            config={"callbacks": [langfuse_callback_handler]}
        )

        
        logger.info(f"DEBUG: Final result keys: {list(result.keys())}")
        logger.info(f"DEBUG: Final result status: {result.get('status', 'NOT FOUND')}")
        
        # Ensure status is included in the final result (LangGraph workflow issue)
        if 'status' not in result:
            # Try to determine status from prediction and confidence
            if result['confidence'] >= self.confidence_threshold:
                result['status'] = result['prediction']
            else:
                # Check if prediction already contains "PENDING HUMAN REVIEW" to avoid duplicate suffix
                if "PENDING HUMAN REVIEW" in result['prediction']:
                    result['status'] = result['prediction']
                else:
                    result['status'] = f"{result['prediction']} - PENDING HUMAN REVIEW"
            logger.info(f"DEBUG: Added missing status: {result['status']}")

        logger.info("=" * 70)
        logger.success("✅ Processing complete!")
        logger.info("=" * 70 + "\n")

        return result


def create_agent(confidence_threshold: float = 0.7, use_shap: bool = True) -> ClaimProcessingAgent:
    """
    Factory function to create an agent.
    
    Args:
        confidence_threshold: Minimum confidence for auto-approval (default: 0.7)
        use_shap: Use SHAP explanations (slower, more accurate) vs rule-based (faster)
    """
    return ClaimProcessingAgent(
        confidence_threshold=confidence_threshold,
        use_shap=use_shap
    )


if __name__ == "__main__":
    # Test the agent
    logger.info("="*70)
    logger.info("Testing Insurance Claim Agent with GPT-2")
    logger.info("="*70)
    
    os.makedirs('outputs', exist_ok=True)
    
    agent = create_agent(confidence_threshold=0.7, use_shap=True)

    test_claim = {
        'claim_id': 'CLM-2024-TEST',
        'policy_type': 'Health Insurance',
        'amount': 15000,
        'description': 'Emergency surgery for appendicitis with 3-day hospital stay',
        'medical_reports': 'Confirmed diagnosis, necessary procedure',
        'previous_claims': 2,
        'policy_duration_months': 24
    }

    result = agent.process_claim(test_claim)

    logger.info(f"\n{'='*70}")
    logger.info("FINAL RESULTS")
    logger.info(f"{'='*70}")
    logger.info(f"Decision: {result['prediction']}")
    logger.info(f"Confidence: {result['confidence']:.1%}")
    logger.info(f"Requires Review: {result['requires_human_review']}")
    logger.info(f"\n{result['decision_reasoning']}")
