#!/usr/bin/env python3
"""
Test suite for enhanced RAG search functionality and log parsing
"""

import requests
import json
import time
import tempfile
import os

# Test configuration
BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test API health endpoint"""
    print("Testing API health...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ API health check passed")

def test_rag_search_precision():
    """Test that RAG search doesn't return inappropriate matches"""
    print("\nTesting RAG search precision...")
    
    # First, add a specific solution to RAG
    mark_response = requests.post(f"{BASE_URL}/mark-solution", json={
        "error_text": "npm ERR! Test failed with exit code 1",
        "solution_text": "Test failure solution: Check your test scripts and dependencies",
        "confidence": 0.95,
        "source": "user_verified"
    })
    assert mark_response.status_code == 200
    print("✅ Added test solution to RAG database")
    
    # Wait for training to complete
    time.sleep(2)
    
    # Test exact match - should return RAG solution
    exact_response = requests.post(f"{BASE_URL}/search-logs", json={
        "log_content": "npm ERR! Test failed with exit code 1"
    })
    assert exact_response.status_code == 200
    exact_data = exact_response.json()
    assert exact_data["sources"]["rag"] > 0
    assert exact_data["search_strategy"] == "high_confidence_rag"
    print("✅ Exact match returns RAG solution")
    
    # Test different error - should NOT return the same RAG solution
    different_response = requests.post(f"{BASE_URL}/search-logs", json={
        "log_content": "npm WARN deprecated package@1.0.0: This package is deprecated"
    })
    assert different_response.status_code == 200
    different_data = different_response.json()
    
    # Should fall back to Claude, not return inappropriate RAG match
    assert different_data["search_strategy"] == "claude_fallback"
    assert different_data["sources"]["claude"] > 0
    print("✅ Different error correctly falls back to Claude AI")

def test_log_file_upload():
    """Test log file upload and parsing functionality"""
    print("\nTesting log file upload...")
    
    # Create a test log file
    test_log_content = """2024-01-01 10:00:00 [INFO] Application starting
2024-01-01 10:00:01 [ERROR] Database connection failed
2024-01-01 10:00:02 [ERROR] Unable to connect to PostgreSQL
2024-01-01 10:00:03 [WARN] Retrying connection in 5 seconds
2024-01-01 10:00:08 [ERROR] Max retries exceeded
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        f.write(test_log_content)
        log_file_path = f.name
    
    try:
        # Upload the log file
        with open(log_file_path, 'rb') as f:
            files = {'file': ('test.log', f, 'text/plain')}
            response = requests.post(f"{BASE_URL}/upload-logs", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "solutions" in data
        assert data["total_count"] > 0
        assert "Database connection failed" in data["parsed_content_preview"] or "PostgreSQL" in data["parsed_content_preview"]
        print("✅ Log file upload and parsing successful")
        
    finally:
        # Clean up
        os.unlink(log_file_path)

def test_github_analysis():
    """Test GitHub repository analysis"""
    print("\nTesting GitHub repository analysis...")
    
    # Test with this repository (should handle rate limiting gracefully)
    response = requests.post(f"{BASE_URL}/analyze-github", json={
        "github_url": "https://github.com/DLTKDebarshi/devopsaiassistant"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) > 0
    
    # Should handle rate limiting gracefully
    first_result = data["results"][0]
    assert "solutions" in first_result
    assert first_result["solution_count"] > 0
    print("✅ GitHub analysis handled gracefully (rate limited or successful)")

def test_rag_stats():
    """Test RAG statistics endpoint"""
    print("\nTesting RAG statistics...")
    
    response = requests.get(f"{BASE_URL}/rag-stats")
    assert response.status_code == 200
    data = response.json()
    
    assert "total_entries" in data
    assert "accuracy" in data
    assert "model_version" in data
    assert data["total_entries"] > 0  # We added at least one solution
    print("✅ RAG statistics retrieved successfully")

def test_dashboard_data():
    """Test dashboard data endpoint"""
    print("\nTesting dashboard data...")
    
    response = requests.get(f"{BASE_URL}/dashboard-data")
    assert response.status_code == 200
    data = response.json()
    
    assert "overview" in data
    assert "training_status" in data
    assert "performance_metrics" in data
    assert data["overview"]["total_solutions"] > 0
    print("✅ Dashboard data retrieved successfully")

def test_search_strategy_logic():
    """Test the search strategy logic works correctly"""
    print("\nTesting search strategy logic...")
    
    # Test with a completely new error type
    response = requests.post(f"{BASE_URL}/search-logs", json={
        "log_content": "java.lang.OutOfMemoryError: Java heap space"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    # Should fall back to Claude for new error types
    assert data["search_strategy"] == "claude_fallback"
    assert data["sources"]["claude"] > 0
    print("✅ Search strategy correctly handles new error types")

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting enhanced functionality tests...\n")
    
    try:
        test_api_health()
        test_rag_search_precision()
        test_log_file_upload()
        test_github_analysis()
        test_rag_stats()
        test_dashboard_data()
        test_search_strategy_logic()
        
        print("\n🎉 All tests passed! The enhanced functionality is working correctly.")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the API. Make sure the server is running on http://localhost:8000")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)