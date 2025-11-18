"""
SHAP Visualization Demo with GPT-2
Demonstrates the SHAP explanation and export capabilities
"""
import os
import unittest
import json
from claim_classifier import GPT2ClaimClassifier
from loguru import logger


class TestShapExplainer(unittest.TestCase):
    """Test suite for SHAP and rule-based explanations."""

    def setUp(self):
        """Set up the test environment."""
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(self.script_dir, 'outputs')
        os.makedirs(self.output_dir, exist_ok=True)

        # Initialize classifier
        self.classifier = GPT2ClaimClassifier(cache_dir=os.path.join(self.script_dir, "cached_models"))

    def test_full_shap_visualization(self):
        """Test the full SHAP visualization demo."""
        claims_dir = os.path.join(self.script_dir, 'claims')
        test_claims = []
        for filename in os.listdir(claims_dir):
            if filename.endswith('.json'):
                with open(os.path.join(claims_dir, filename)) as f:
                    test_claims.append(json.load(f))

        for claim in test_claims:
            with self.subTest(claim_id=claim['id']):
                explanation = self.classifier.get_shap_explanation(claim['text'], claim_id=claim['id'], num_samples=80)

                # Check for HTML and PNG output files
                self.assertIn('html_path', explanation)
                self.assertIn('image_path', explanation)
                self.assertTrue(os.path.exists(explanation['html_path']))
                self.assertTrue(os.path.exists(explanation['image_path']))

    def test_quick_rule_based_explanation(self):
        """Test the quick rule-based explanation demo."""
        test_text = """
    Emergency surgery for appendicitis at hospital.
    Confirmed diagnosis by doctor.
    Necessary treatment required immediately.
    """

        explanation = self.classifier.get_simple_explanation(test_text)

        logger.info(f"Explanation for customer: {explanation}")

        # Check for expected keys in the explanation
        self.assertIn('method', explanation)
        self.assertIn('top_features', explanation)
        self.assertEqual(explanation['method'], 'rule_based')
        self.assertIsInstance(explanation['top_features'], list)


if __name__ == "__main__":
    unittest.main()
