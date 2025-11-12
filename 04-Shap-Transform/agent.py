"""
LangGraph Agent for Insurance Claim Processing
"""
from typing import TypedDict, Annotated, Literal
import operator
from langgraph.graph import StateGraph, END
from claim_classifier import QwenClaimClassifier
import json


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
            use_shap: Whether to use SHAP (slower) or simple explanations (faster)
        """
        self.classifier = QwenClaimClassifier()
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
Claim ID: {claim_data.get('claim_id', 'N/A')}
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
            'content': f"Processing claim: {claim_data.get('claim_id', 'Unknown')}"
        })

        print(f"✓ Preprocessed claim {claim_data.get('claim_id')}")
        return state

    def classify_claim(self, state: ClaimState) -> ClaimState:
        """Run classification with the model"""
        claim_text = state['claim_text']

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

        print(f"✓ Classification: {prediction} with {confidence:.1%} confidence")
        return state

    def explain_decision(self, state: ClaimState) -> ClaimState:
        """Generate explanation using SHAP or simple rules"""
        claim_text = state['claim_text']

        # Get explanation
        if self.use_shap:
            try:
                explanation = self.classifier.get_shap_explanation(claim_text)
            except Exception as e:
                print(f"SHAP failed, using simple explanation: {e}")
                explanation = self.classifier.get_simple_explanation(claim_text)
        else:
            explanation = self.classifier.get_simple_explanation(claim_text)

        state['shap_explanation'] = explanation

        # Format reasoning
        top_features = explanation.get('top_features', [])

        reasoning_parts = [
            f"Decision: {state['prediction']}",
            f"Confidence: {state['confidence']:.1%}",
            "",
            "Key factors influencing this decision:"
        ]

        for feature in top_features[:5]:
            impact = "supporting approval" if feature['shap_value'] > 0 else "supporting rejection"
            reasoning_parts.append(
                f"  • '{feature['feature']}' (impact: {abs(feature['shap_value']):.3f}, {impact})"
            )

        reasoning = "\n".join(reasoning_parts)
        state['decision_reasoning'] = reasoning
        state['messages'].append({
            'role': 'assistant',
            'content': reasoning
        })

        print("✓ Generated explanation")
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

        print(f"⚠️ Flagged for human review (confidence: {state['confidence']:.1%})")
        return state

    def finalize_decision(self, state: ClaimState) -> ClaimState:
        """Finalize the claim decision"""
        state['requires_human_review'] = False
        state['messages'].append({
            'role': 'system',
            'content': f"✓ Claim decision finalized: {state['prediction']}"
        })

        print(f"✓ Decision finalized: {state['prediction']}")
        return state

    def process_claim(self, claim_data: dict) -> dict:
        """
        Process a single claim through the workflow.
        
        Args:
            claim_data: Dictionary containing claim information
            
        Returns:
            Final state with decision and explanation
        """
        print("\n" + "=" * 60)
        print(f"Processing Claim: {claim_data.get('claim_id', 'Unknown')}")
        print("=" * 60)

        initial_state = {
            'claim_data': claim_data,
            'claim_text': '',
            'prediction': '',
            'confidence': 0.0,
            'shap_explanation': {},
            'decision_reasoning': '',
            'messages': [],
            'requires_human_review': False
        }

        result = self.workflow.invoke(initial_state)

        print("=" * 60)
        print("Processing complete!")
        print("=" * 60 + "\n")

        return result


def create_agent(confidence_threshold: float = 0.7, use_shap: bool = False) -> ClaimProcessingAgent:
    """Factory function to create an agent"""
    return ClaimProcessingAgent(
        confidence_threshold=confidence_threshold,
        use_shap=use_shap
    )


if __name__ == "__main__":
    # Test the agent
    agent = create_agent(confidence_threshold=0.7, use_shap=False)

    test_claim = {
        'claim_id': 'CLM-2024-001',
        'policy_type': 'Health Insurance',
        'amount': 15000,
        'description': 'Emergency surgery for appendicitis with 3-day hospital stay',
        'medical_reports': 'Confirmed diagnosis, necessary procedure',
        'previous_claims': 2,
        'policy_duration_months': 24
    }

    result = agent.process_claim(test_claim)

    print(f"\nFinal Decision: {result['prediction']}")
    print(f"Confidence: {result['confidence']:.1%}")
    print(f"Requires Review: {result['requires_human_review']}")
