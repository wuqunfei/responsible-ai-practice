"""
Insurance Claim AI Agent - Main Demo with GPT-2
Run this to see the complete system with SHAP explanations
"""
import json
from datetime import datetime
import os
from agent import create_agent
from loguru import logger

os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-6f92e45b-0a31-4a22-a8f9-bbd794dff2ed"
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-7d4a7388-b2ad-41db-899c-2e30c9e977e3"
os.environ["LANGFUSE_BASE_URL"] = "https://cloud.langfuse.com"

def langfuse_auth():
    from langfuse import get_client
    langfuse = get_client()
    # Verify connection
    if langfuse.auth_check():
        logger.success("Langfuse client is authenticated and ready!")
    else:
        logger.error("Authentication failed. Please check your credentials and host.")


def print_section(title: str):
    """Print a formatted section header"""
    logger.info("\n" + "="*70)
    logger.info(f"  {title}")
    logger.info("="*70)


def print_result(result: dict):
    """Print formatted result"""
    logger.info(f"\n{'Decision:':<20} {result['prediction']}")
    logger.info(f"{'Confidence:':<20} {result['confidence']:.1%}")
    logger.info(f"{'Human Review:':<20} {'Yes' if result['requires_human_review'] else 'No'}")
    logger.info(f"{'Status:':<20} {result.get('status', 'Unknown')}")
    if 'decision_reasoning' in result:
        logger.info(f"\n{result['decision_reasoning']}")


def save_result(result: dict, filename: str, claim_data: dict):
    """Save result to JSON file"""
    output = {
        'claim_id': claim_data['id'],
        'prediction': result['prediction'],
        'confidence': result['confidence'],
        'requires_human_review': result['requires_human_review'],
        'status': result.get('status', 'Unknown'),
        'timestamp': datetime.now().isoformat()
    }
    
    # Add reasoning if available
    if 'decision_reasoning' in result:
        output['reasoning'] = result['decision_reasoning']
    
    # Add SHAP explanation if available
    if 'shap_explanation' in result and result['shap_explanation']:
        output['top_features'] = result['shap_explanation'].get('top_features', [])
        output['explanation_method'] = result['shap_explanation'].get('method', 'unknown')
        output['visualization_files'] = {
            'html': result['shap_explanation'].get('html_path'),
            'image': result['shap_explanation'].get('image_path')
        }
    
    with open(filename, 'w') as f:
        json.dump(output, f, indent=2)
    
    logger.info(f"\n✓ Result saved to: {filename}")


def main():
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    claims_dir = os.path.join(script_dir, 'claims')
    output_dir = os.path.join(script_dir, 'outputs')
    os.makedirs(output_dir, exist_ok=True)

    # Initialize the agent
    logger.info("\n📦 Initializing Claim Processing Agent...")
    agent = create_agent(confidence_threshold=0.7, use_shap=True)
    
    # --- Get Claims to Process ---
    claim_files = sorted([f for f in os.listdir(claims_dir) if f.endswith('.json')])
    if not claim_files:
        logger.error(f"❌ No claim files found in {claims_dir}.")
        return

    logger.info(f"Found {len(claim_files)} claims to process: {claim_files}")

    # --- Process Each Claim ---
    all_results = []
    for file_name in claim_files:
        with open(os.path.join(claims_dir, file_name), 'r') as f:
            claim_data = json.load(f)
        
        # Handle different claim ID field names
        claim_id = claim_data.get('id')
        claim_name = claim_data.get('name', 'Unknown Claim')
        claim_data['id'] = claim_id  # Ensure consistent ID field
        
        # Process the claim using the agent
        result = agent.process_claim(claim_data)
        all_results.append(result)
        
        # Print the result
        print_section(f"Claim {claim_id} - {claim_name}")
        print_result(result)
        
        # Save the result
        output_filename = os.path.join(output_dir, f"summary_{claim_id}.json")
        save_result(result, output_filename, claim_data)



    # --- Final Summary ---
    print_section("Final Summary Report")
    logger.info(f"Total claims processed: {len(all_results)}")
    
    for res in all_results:
        claim_id = res['claim_data'].get('id', 'Unknown')
        claim_name = res['claim_data'].get('name', 'Unknown Claim')
        logger.info(f"  - {claim_id} ({claim_name}): {res['prediction']} (Confidence: {res['confidence']:.1%}) - Status: {res.get('status', 'Unknown')}")

    logger.info(f"\n✅ Final summary report saved in the '{output_dir}' directory.")


if __name__ == "__main__":
    langfuse_auth()
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        logger.error(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
