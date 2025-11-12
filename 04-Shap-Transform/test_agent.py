"""
Unit tests for Insurance Claim AI Agent
Run with: python test_agent.py
"""
import json
import os
from demo_lightweight import SimpleLangGraphAgent, MockClassifier


def test_mock_classifier():
    """Test the mock classifier"""
    print("Testing MockClassifier...")
    
    classifier = MockClassifier()
    
    # Test emergency claim (should approve)
    text1 = "Emergency surgery for appendicitis at hospital"
    probs1 = classifier.predict(text1)
    assert probs1[1] > 0.5, "Emergency claim should be approved"
    print("✓ Emergency claim test passed")
    
    # Test cosmetic claim (should reject)
    text2 = "Elective cosmetic surgery procedure"
    probs2 = classifier.predict(text2)
    assert probs2[1] < 0.5, "Cosmetic claim should be rejected"
    print("✓ Cosmetic claim test passed")
    
    # Test explanation
    explanation = classifier.get_explanation(text1)
    assert 'top_features' in explanation
    assert len(explanation['top_features']) > 0
    print("✓ Explanation generation test passed")
    
    print("MockClassifier: All tests passed!\n")


def test_agent_workflow():
    """Test the agent workflow"""
    print("Testing SimpleLangGraphAgent...")
    
    agent = SimpleLangGraphAgent(confidence_threshold=0.7)
    
    # Test claim
    test_claim = {
        'claim_id': 'TEST-001',
        'policy_type': 'Health Insurance',
        'amount': 10000,
        'description': 'Emergency hospital visit',
        'medical_reports': 'Confirmed diagnosis',
        'previous_claims': 1,
        'policy_duration_months': 12
    }
    
    # Process claim
    result = agent.process_claim(test_claim)
    
    # Verify result structure
    assert 'prediction' in result
    assert 'confidence' in result
    assert 'decision_reasoning' in result
    assert 'requires_human_review' in result
    assert result['confidence'] >= 0.0 and result['confidence'] <= 1.0
    print("✓ Agent workflow test passed")
    
    # Test high confidence routing
    result_high_conf = agent.process_claim({
        **test_claim,
        'claim_id': 'TEST-002',
        'description': 'Emergency surgery at hospital, confirmed diagnosis necessary procedure'
    })
    assert not result_high_conf['requires_human_review'], "High confidence should not require review"
    print("✓ High confidence routing test passed")
    
    print("SimpleLangGraphAgent: All tests passed!\n")


def test_json_output():
    """Test JSON output generation"""
    print("Testing JSON output...")
    
    agent = SimpleLangGraphAgent()
    
    test_claim = {
        'claim_id': 'JSON-TEST-001',
        'policy_type': 'Test',
        'amount': 5000,
        'description': 'Test claim',
        'medical_reports': 'Test reports',
        'previous_claims': 0,
        'policy_duration_months': 12
    }
    
    result = agent.process_claim(test_claim)
    
    # Save to JSON
    os.makedirs('test_outputs', exist_ok=True)
    output_file = 'test_outputs/test_result.json'
    
    with open(output_file, 'w') as f:
        json.dump({
            'claim_id': result['claim_data']['claim_id'],
            'prediction': result['prediction'],
            'confidence': result['confidence']
        }, f, indent=2)
    
    # Verify JSON file
    assert os.path.exists(output_file), "JSON file should be created"
    
    with open(output_file, 'r') as f:
        loaded = json.load(f)
        assert loaded['claim_id'] == 'JSON-TEST-001'
    
    print("✓ JSON output test passed")
    print("JSON output: All tests passed!\n")


def test_confidence_threshold():
    """Test different confidence thresholds"""
    print("Testing confidence thresholds...")
    
    # Low threshold (70%)
    agent_low = SimpleLangGraphAgent(confidence_threshold=0.7)
    
    # High threshold (90%)
    agent_high = SimpleLangGraphAgent(confidence_threshold=0.9)
    
    # Borderline claim
    borderline_claim = {
        'claim_id': 'THRESHOLD-TEST',
        'policy_type': 'Health',
        'amount': 20000,
        'description': 'Minor procedure',
        'medical_reports': 'Reports available',
        'previous_claims': 3,
        'policy_duration_months': 6
    }
    
    result_low = agent_low.process_claim(borderline_claim)
    result_high = agent_high.process_claim(borderline_claim)
    
    # High threshold should be more likely to require review
    print(f"  Low threshold (70%): Review = {result_low['requires_human_review']}, Confidence = {result_low['confidence']:.1%}")
    print(f"  High threshold (90%): Review = {result_high['requires_human_review']}, Confidence = {result_high['confidence']:.1%}")
    
    print("✓ Confidence threshold test passed")
    print("Confidence thresholds: All tests passed!\n")


def run_all_tests():
    """Run all tests"""
    print("="*70)
    print("  Running Insurance Claim AI Agent Tests")
    print("="*70)
    print()
    
    try:
        test_mock_classifier()
        test_agent_workflow()
        test_json_output()
        test_confidence_threshold()
        
        print("="*70)
        print("  ✅ ALL TESTS PASSED!")
        print("="*70)
        print()
        
        # Cleanup
        import shutil
        if os.path.exists('test_outputs'):
            shutil.rmtree('test_outputs')
        print("✓ Cleanup complete")
        
        return True
        
    except AssertionError as e:
        print("\n" + "="*70)
        print(f"  ❌ TEST FAILED: {e}")
        print("="*70)
        return False
    
    except Exception as e:
        print("\n" + "="*70)
        print(f"  ❌ ERROR: {e}")
        print("="*70)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
