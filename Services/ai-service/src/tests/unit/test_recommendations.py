import pytest
from services.recommendations_service import get_recommendations
import time

def test_recommendations():
    recommendations = get_recommendations("user123")
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    # Validate recommendation structure
    for rec in recommendations:
        assert isinstance(rec, dict)
        assert 'product_id' in rec
        assert 'score' in rec
        assert isinstance(rec['score'], float)
        assert 0 <= rec['score'] <= 1
        
    # Test edge cases
    assert get_recommendations("") == []
    assert get_recommendations(None) == []
    
    # Test cache behavior
    first_call = get_recommendations("user123")
    second_call = get_recommendations("user123")
    assert first_call == second_call
    
    # Test different users get different results
    other_user = get_recommendations("user456")
    assert other_user != recommendations
    
    # Test performance
    start = time.time()
    get_recommendations("user789")
    assert time.time() - start < 1.0  # Should respond within 1 second