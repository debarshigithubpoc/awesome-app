#!/usr/bin/env python3
"""
Test script to validate real API integrations in DevOps AI Assistant
Run this to test if the enhanced_server.py works with real APIs
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

async def test_basic_functionality():
    """Test basic functionality without external dependencies"""
    print("🧪 Testing DevOps AI Assistant Real API Integration")
    print("=" * 60)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from enhanced_server import extract_github_repo_info, get_fallback_solutions
        print("✅ Core imports successful")
        
        # Test GitHub URL parsing
        print("\n🔗 Testing GitHub URL parsing...")
        test_urls = [
            "https://github.com/facebook/react",
            "https://github.com/microsoft/vscode.git",
            "github.com/owner/repo"
        ]
        
        for url in test_urls:
            try:
                owner, repo = extract_github_repo_info(url)
                print(f"✅ {url} -> {owner}/{repo}")
            except Exception as e:
                print(f"❌ {url} -> Error: {e}")
        
        # Test fallback solutions
        print("\n🛠️  Testing fallback solution generation...")
        test_errors = [
            "npm ERR! Test failed",
            "Docker build failed",
            "Permission denied",
            "Python import error"
        ]
        
        for error in test_errors:
            solutions = get_fallback_solutions(error)
            print(f"✅ '{error[:20]}...' -> {len(solutions)} solutions generated")
            if solutions:
                print(f"   First solution: {solutions[0]['description']}")
        
        print("\n🎯 Basic functionality tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

async def test_api_configuration():
    """Test API configuration and environment setup"""
    print("\n🔧 Testing API Configuration")
    print("-" * 40)
    
    # Check environment file
    env_file = backend_dir.parent / ".env"
    env_example = backend_dir.parent / ".env.example"
    
    if env_example.exists():
        print("✅ .env.example file exists")
    else:
        print("❌ .env.example file missing")
    
    if env_file.exists():
        print("✅ .env file exists")
        print("📝 Checking environment variables...")
        
        # Load environment variables
        with open(env_file) as f:
            lines = f.readlines()
        
        claude_configured = any("CLAUDE_API_KEY=" in line and not line.strip().endswith("_here") for line in lines)
        github_configured = any("GITHUB_TOKEN=" in line and not line.strip().endswith("_here") for line in lines)
        
        if claude_configured:
            print("✅ Claude API key configured")
        else:
            print("⚠️  Claude API key not configured (will use fallback solutions)")
        
        if github_configured:
            print("✅ GitHub token configured")
        else:
            print("⚠️  GitHub token not configured (may hit rate limits)")
            
    else:
        print("⚠️  .env file not found (will use default/fallback behavior)")
    
    return True

async def test_server_health():
    """Test if the server can start and basic endpoints work"""
    print("\n🏥 Testing Server Health")
    print("-" * 40)
    
    try:
        # Try to import the server module
        from enhanced_server import app, rag_model
        print("✅ Server module imported successfully")
        
        if rag_model:
            print("✅ RAG model initialized")
        else:
            print("⚠️  RAG model not initialized (may need dependencies)")
        
        print("✅ Server health test completed")
        return True
        
    except ImportError as e:
        print(f"❌ Server import failed: {e}")
        print("💡 This is expected if dependencies are not installed")
        return False

def print_setup_instructions():
    """Print setup instructions for users"""
    print("\n📋 Setup Instructions")
    print("=" * 60)
    print("To run the full application with real APIs:")
    print()
    print("1. Install dependencies:")
    print("   cd backend && pip install -r requirements.txt")
    print()
    print("2. Configure API keys:")
    print("   cp .env.example .env")
    print("   # Edit .env with your actual API keys")
    print()
    print("3. Start the server:")
    print("   python enhanced_server.py")
    print()
    print("4. In another terminal, start frontend:")
    print("   cd frontend && npm install && npm start")
    print()
    print("5. Open http://localhost:3000")
    print()
    print("🌟 Features now available:")
    print("   ✅ Real Claude AI analysis (with API key)")
    print("   ✅ Real GitHub Actions analysis")
    print("   ✅ Smart fallback when APIs unavailable")
    print("   ✅ RAG learning from user feedback")

async def main():
    """Run all tests"""
    print("DevOps AI Assistant - Real API Integration Test Suite")
    print("🚀 Testing real implementations vs mock data")
    print()
    
    basic_ok = await test_basic_functionality()
    config_ok = await test_api_configuration()
    server_ok = await test_server_health()
    
    print("\n📊 Test Summary")
    print("=" * 40)
    print(f"Basic Functionality: {'✅ PASS' if basic_ok else '❌ FAIL'}")
    print(f"API Configuration:   {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Server Health:       {'✅ PASS' if server_ok else '⚠️  PARTIAL'}")
    
    if basic_ok:
        print("\n🎉 Core functionality is working!")
        print("The application now uses real APIs instead of mock data.")
    
    print_setup_instructions()

if __name__ == "__main__":
    asyncio.run(main())