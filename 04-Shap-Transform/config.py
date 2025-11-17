"""
Configuration and Model Selection Script
Use this to easily switch between different Qwen models
"""
from typing import Dict
import json


# Available model configurations
MODEL_CONFIGS: Dict[str, Dict] = {
    "qwen3-4b-instruct": {
        "model_name": "Qwen/Qwen3-4B-Instruct-2507",
        "description": "Full Qwen3-4B model - Best accuracy",
        "vram_required": "8GB",
        "ram_required": "16GB",
        "speed": "Medium",
        "accuracy": "High"
     },
    # "qwen2.5-3b-instruct": {
    #     "model_name": "Qwen/Qwen2.5-3B-Instruct",
    #     "description": "Qwen2.5-3B - Good balance",
    #     "vram_required": "6GB",
    #     "ram_required": "12GB",
    #     "speed": "Medium-Fast",
    #     "accuracy": "Medium-High"
    # },
    # "qwen2.5-1.5b-instruct": {
    #     "model_name": "Qwen/Qwen2.5-1.5B-Instruct",
    #     "description": "Qwen2.5-1.5B - Faster processing",
    #     "vram_required": "4GB",
    #     "ram_required": "8GB",
    #     "speed": "Fast",
    #     "accuracy": "Medium"
    # },
    # "qwen2.5-0.5b-instruct": {
    #     "model_name": "Qwen/Qwen2.5-0.5B-Instruct",
    #     "description": "Qwen2.5-0.5B - Lightweight demo",
    #     "vram_required": "2GB",
    #     "ram_required": "4GB",
    #     "speed": "Very Fast",
    #     "accuracy": "Medium-Low"
    # }
}


def print_model_info():
    """Print information about available models"""
    print("\n" + "="*80)
    print("Available Qwen Models for Insurance Claim Classification")
    print("="*80 + "\n")
    
    for key, config in MODEL_CONFIGS.items():
        print(f"🔹 {key.upper()}")
        print(f"   Model: {config['model_name']}")
        print(f"   Description: {config['description']}")
        print(f"   Requirements: {config['vram_required']} VRAM / {config['ram_required']} RAM")
        print(f"   Speed: {config['speed']} | Accuracy: {config['accuracy']}")
        print()


def get_model_name(model_key: str = "qwen2.5-0.5b-instruct") -> str:
    """
    Get the Hugging Face model name for the specified configuration.
    
    Args:
        model_key: One of the keys from MODEL_CONFIGS
        
    Returns:
        Full Hugging Face model name
    """
    if model_key not in MODEL_CONFIGS:
        print(f"⚠️  Warning: Unknown model key '{model_key}'. Using default.")
        model_key = "qwen2.5-0.5b-instruct"
    
    return MODEL_CONFIGS[model_key]["model_name"]


def create_config_file(model_key: str = "qwen2.5-0.5b-instruct", 
                       confidence_threshold: float = 0.7,
                       use_shap: bool = True):
    """
    Create a configuration file for the agent.
    
    Args:
        model_key: Which model to use
        confidence_threshold: Minimum confidence for auto-approval
        use_shap: Whether to use SHAP explanations
    """
    config = {
        "model": {
            "key": model_key,
            "name": get_model_name(model_key),
            "info": MODEL_CONFIGS.get(model_key, {})
        },
        "agent": {
            "confidence_threshold": confidence_threshold,
            "use_shap": use_shap
        }
    }
    
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Configuration saved to config.json")
    print(f"   Model: {config['model']['name']}")
    print(f"   Confidence threshold: {confidence_threshold:.0%}")
    print(f"   SHAP enabled: {use_shap}")


def load_config() -> Dict:
    """Load configuration from file"""
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  No config.json found. Creating default configuration...")
        create_config_file()
        with open("config.json", "r") as f:
            return json.load(f)


def test_model_loading(model_key: str = "qwen2.5-0.5b-instruct"):
    """
    Test if a model can be loaded successfully.
    
    Args:
        model_key: Model configuration key to test
    """
    print(f"\n{'='*80}")
    print(f"Testing Model: {model_key.upper()}")
    print(f"{'='*80}\n")
    
    model_name = get_model_name(model_key)
    print(f"Model name: {model_name}")
    print(f"Requirements: {MODEL_CONFIGS[model_key]['vram_required']} VRAM / "
          f"{MODEL_CONFIGS[model_key]['ram_required']} RAM\n")
    
    try:
        from claim_classifier import QwenClaimClassifier
        import time
        
        print("Loading model...")
        start_time = time.time()
        
        classifier = QwenClaimClassifier(model_name=model_name)
        
        load_time = time.time() - start_time
        print(f"✓ Model loaded successfully in {load_time:.2f} seconds\n")
        
        # Test prediction
        print("Running test prediction...")
        test_text = """
Claim ID: TEST-001
Policy Type: Health Insurance
Claim Amount: $15,000
Description: Emergency surgery
Medical Reports: Confirmed diagnosis
Previous Claims: 2
Policy Duration: 24 months
"""
        
        start_time = time.time()
        probs = classifier.predict(test_text)
        predict_time = time.time() - start_time
        
        print(f"✓ Prediction completed in {predict_time:.2f} seconds")
        print(f"   Results: Approve={probs[1]:.2%}, Reject={probs[0]:.2%}\n")
        
        print("="*80)
        print("✅ Model test PASSED")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"❌ Model test FAILED")
        print(f"{'='*80}")
        print(f"Error: {e}\n")
        return False


if __name__ == "__main__":
    import sys
    
    print_model_info()
    
    # Interactive model selection
    if len(sys.argv) > 1:
        model_key = sys.argv[1].lower()
    else:
        print("Select a model:")
        for i, key in enumerate(MODEL_CONFIGS.keys(), 1):
            print(f"  {i}. {key}")
        print(f"  {len(MODEL_CONFIGS)+1}. Skip test, just create config")
        
        try:
            choice = input(f"\nEnter choice (1-{len(MODEL_CONFIGS)+1}, default=4): ").strip()
            if not choice:
                choice = "4"
            
            choice_idx = int(choice) - 1
            
            if choice_idx == len(MODEL_CONFIGS):
                # Just create config
                model_key = "qwen2.5-0.5b-instruct"
                print(f"\nCreating configuration for: {model_key}")
                create_config_file(model_key)
                sys.exit(0)
            elif 0 <= choice_idx < len(MODEL_CONFIGS):
                model_key = list(MODEL_CONFIGS.keys())[choice_idx]
            else:
                print("Invalid choice. Using default.")
                model_key = "qwen2.5-0.5b-instruct"
        except (ValueError, IndexError):
            print("Invalid input. Using default.")
            model_key = "qwen2.5-0.5b-instruct"
    
    # Test the selected model
    success = test_model_loading(model_key)
    
    if success:
        # Create config file
        print("\nCreating configuration file...")
        create_config_file(
            model_key=model_key,
            confidence_threshold=0.7,
            use_shap=True
        )
        
        print("\n" + "="*80)
        print("Next steps:")
        print("  1. Run 'python main.py' to process claims with this configuration")
        print("  2. Edit 'config.json' to adjust settings")
        print("  3. Import and use in your code:")
        print(f"     from config import load_config")
        print(f"     config = load_config()")
        print(f"     model_name = config['model']['name']")
        print("="*80 + "\n")
