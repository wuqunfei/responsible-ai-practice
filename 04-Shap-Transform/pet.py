import torch
import numpy as np
from transformers import GPT2Tokenizer, GPT2ForSequenceClassification, GPT2Config
import shap
from torch.nn.functional import softmax
import os
from matplotlib import pyplot as plt
import re


# Step 1: Setup - Install required libraries
# pip install transformers torch shap matplotlib

class PetClaimAnalyzer:
    def __init__(self):
        """Initialize the claim analyzer with GPT-2 model"""
        # Load pre-trained GPT-2 tokenizer
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.tokenizer.pad_token = self.tokenizer.eos_token

        # Initialize GPT-2 for binary classification (approve/reject)
        config = GPT2Config.from_pretrained('gpt2', num_labels=2)
        self.model = GPT2ForSequenceClassification.from_pretrained(
            'gpt2',
            config=config
        )
        self.model.config.pad_token_id = self.tokenizer.eos_token_id

        # Set to evaluation mode
        self.model.eval()
        
        self.ignore_whitespace_punct = True

    def normalize_text(self, text: str) -> str:
        pattern = r"[\s,，.。]+"
        return re.sub(pattern, "", text)

    def preprocess_claim(self, claim_text):
        """Preprocess the claim text for model input"""
        processed = self.normalize_text(claim_text) if self.ignore_whitespace_punct else claim_text
        prompt = f"Evaluate this pet insurance claim:\n{processed}\nDecision:"
        return prompt

    def predict(self, claim_text):
        """
        Predict approval/rejection with confidence score
        Returns: (decision, confidence, probabilities)
        """
        # Preprocess
        prompt = self.preprocess_claim(claim_text)

        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=512
        )

        # Get prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = softmax(logits, dim=-1)

        # Get confidence and decision
        confidence, predicted_class = torch.max(probabilities, dim=1)

        decision = "APPROVE" if predicted_class.item() == 1 else "REJECT"
        confidence_score = confidence.item()

        return decision, confidence_score, probabilities[0].numpy()

    def explain_with_shap(self, claim_text):
        """
        Use SHAP to explain the prediction
        Returns: SHAP values and visualization
        """

        # Create prediction function for SHAP
        def model_predict(texts):
            predictions = []
            for text in texts:
                inputs = self.tokenizer(
                    text,
                    return_tensors='pt',
                    padding=True,
                    truncation=True,
                    max_length=512
                )

                with torch.no_grad():
                    outputs = self.model(**inputs)
                    probs = softmax(outputs.logits, dim=-1)
                    predictions.append(probs[0].numpy())

            return np.array(predictions)

        # Create SHAP explainer
        explainer = shap.Explainer(model_predict, self.tokenizer)

        # Get SHAP values
        prompt = self.preprocess_claim(claim_text)
        shap_values = explainer([prompt])

        return shap_values

    def analyze_claim(self, claim_text, show_explanation=True):
        """
        Complete analysis with prediction and explanation
        """
        print("=" * 60)
        print("PET INSURANCE CLAIM ANALYSIS")
        print("=" * 60)
        print(f"\nClaim Text:\n{claim_text}\n")

        # Get prediction
        decision, confidence, probabilities = self.predict(claim_text)

        print(f"Decision: {decision}")
        print(f"Confidence: {confidence:.2%}")
        print(f"\nProbability Distribution:")
        print(f"  - REJECT: {probabilities[0]:.2%}")
        print(f"  - APPROVE: {probabilities[1]:.2%}")

        if show_explanation:
            print("\n" + "=" * 60)
            print("GENERATING SHAP EXPLANATION...")
            print("=" * 60)

            try:
                shap_values = self.explain_with_shap(claim_text)

                output_dir = 'outputs'
                os.makedirs(output_dir, exist_ok=True)

                print("\nKey words influencing the decision:")

                html_plot = shap.plots.text(shap_values[0, :, 1], display=False)
                html_path = os.path.join(output_dir, 'words_shap_explanation.html')
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_plot.html() if hasattr(html_plot, 'html') else str(html_plot))

                values = shap_values.values[0, :, 1]
                data = shap_values.data[0]
                words = data.split() if isinstance(data, str) else [str(d) for d in data]

                top_indices = np.argsort(np.abs(values))[-15:][::-1]
                top_words = [words[i] if i < len(words) else f"token_{i}" for i in top_indices]
                top_values = [values[i] for i in top_indices]
                colors = ['green' if v > 0 else 'red' for v in top_values]

                fig, ax = plt.subplots(figsize=(12, 7))
                ax.barh(range(len(top_words)), top_values, color=colors, alpha=0.7)
                ax.set_yticks(range(len(top_words)))
                ax.set_yticklabels(top_words)
                ax.set_xlabel('SHAP Value (Impact on Approval)')
                ax.set_title('Top Words Influencing Decision')
                ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
                ax.grid(axis='x', alpha=0.3)
                plt.tight_layout()

                img_path = os.path.join(output_dir, 'words_shap_explanation.png')
                plt.savefig(img_path, dpi=300, bbox_inches='tight')
                plt.close(fig)

                print(f"Saved SHAP HTML to: {html_path}")
                print(f"Saved SHAP image to: {img_path}")
            except Exception as e:
                print(f"Note: SHAP visualization requires display support: {e}")

        return {
            'decision': decision,
            'confidence': confidence,
            'reject_prob': probabilities[0],
            'approve_prob': probabilities[1]
        }


# Example Usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = PetClaimAnalyzer()

    # Sample claim text
    claim_text = """
    Emergency surgery for accident victim cat. Cost: $3000
    """

    # Analyze the claim
    result = analyzer.analyze_claim(claim_text, show_explanation=True)

    # Question and Answer format
    print("\n" + "=" * 60)
    print("Q&A FORMAT")
    print("=" * 60)

    questions = [
        "Should this claim be approved?",
        "What is the confidence level?",
        "What is the approval probability?",
        "What is the rejection probability?"
    ]

    answers = [
        f"{result['decision']}",
        f"{result['confidence']:.2%}",
        f"{result['approve_prob']:.2%}",
        f"{result['reject_prob']:.2%}"
    ]
    for q, a in zip(questions, answers):
        print(f"\nQ: {q}")
        print(f"A: {a}")