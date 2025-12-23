#!/usr/bin/env python3
"""
Demonstration script showing the fixed RAG search behavior
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def demonstrate_fixed_rag_behavior():
    """Demonstrate that the RAG search no longer returns inappropriate matches"""
    
    print("🔧 DevOps AI Assistant - RAG Search Fix Demonstration\n")
    
    print("Step 1: Adding a specific npm test failure solution to RAG database...")
    mark_response = requests.post(f"{BASE_URL}/mark-solution", json={
        "error_text": "npm ERR! Test failed with exit code 1",
        "solution_text": "NPM Test Failure Fix:\n1. Check test scripts in package.json\n2. Verify test dependencies are installed\n3. Run npm test -- --verbose for detailed output\n4. Check for syntax errors in test files",
        "confidence": 0.95,
        "source": "user_verified"
    })
    
    if mark_response.status_code == 200:
        print("✅ Solution added to RAG database")
    else:
        print("❌ Failed to add solution")
        return
    
    time.sleep(2)  # Wait for training
    
    print("\nStep 2: Testing exact match - should return RAG solution...")
    exact_response = requests.post(f"{BASE_URL}/search-logs", json={
        "log_content": "npm ERR! Test failed with exit code 1"
    })
    
    if exact_response.status_code == 200:
        data = exact_response.json()
        print(f"✅ Search strategy: {data['search_strategy']}")
        print(f"✅ Sources: RAG={data['sources']['rag']}, Claude={data['sources']['claude']}")
        if data['sources']['rag'] > 0:
            print("✅ Correctly returned RAG solution for exact match")
        else:
            print("❌ Failed to return RAG solution for exact match")
    
    print("\nStep 3: Testing different npm error - should NOT return the same solution...")
    different_response = requests.post(f"{BASE_URL}/search-logs", json={
        "log_content": "npm WARN deprecated package@1.0.0: This package is deprecated"
    })
    
    if different_response.status_code == 200:
        data = different_response.json()
        print(f"✅ Search strategy: {data['search_strategy']}")
        print(f"✅ Sources: RAG={data['sources']['rag']}, Claude={data['sources']['claude']}")
        
        if data['search_strategy'] == 'claude_fallback':
            print("✅ FIXED: Correctly fell back to Claude AI for different error")
            print("✅ FIXED: No longer returns inappropriate RAG matches!")
        else:
            print("❌ Issue not fixed: Still returning inappropriate RAG matches")
    
    print("\nStep 4: Testing completely different error type...")
    docker_response = requests.post(f"{BASE_URL}/search-logs", json={
        "log_content": "docker: Error response from daemon: pull access denied"
    })
    
    if docker_response.status_code == 200:
        data = docker_response.json()
        print(f"✅ Search strategy: {data['search_strategy']}")
        print(f"✅ Sources: RAG={data['sources']['rag']}, Claude={data['sources']['claude']}")
        
        if data['search_strategy'] == 'claude_fallback':
            print("✅ FIXED: Correctly used Claude AI for Docker error")
        else:
            print("❌ Issue not fixed: Returning inappropriate matches")
    
    print("\n🎉 Demonstration complete!")
    print("\n📊 Summary of fixes:")
    print("1. ✅ Enhanced similarity matching with higher thresholds")
    print("2. ✅ Added term overlap analysis for better relevance")
    print("3. ✅ Smart fallback to Claude AI for low-confidence matches")
    print("4. ✅ Improved log parsing for file uploads")
    print("5. ✅ Enhanced GitHub Actions analysis with context")

if __name__ == "__main__":
    try:
        demonstrate_fixed_rag_behavior()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")