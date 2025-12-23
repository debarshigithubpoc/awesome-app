#!/usr/bin/env python3
"""
DevOps AI Assistant Backend
A lightweight HTTP server for the DevOps AI Assistant
"""

import http.server
import socketserver
import json
import urllib.parse
import re
from typing import Dict, List

PORT = 8000

# Simple in-memory storage
rag_database = []
solution_counter = 0

def validate_claude_api_key():
    """Mock Claude API key validation"""
    return True  # For demo purposes

def search_rag_database(query: str) -> dict:
    """Search for solutions in the RAG database"""
    for item in rag_database:
        if query.lower() in item["error"].lower():
            return {
                "id": item["id"],
                "description": item["error"][:100] + "...",
                "confidence": 0.95,
                "solution_text": item["solution"]
            }
    return None

def get_claude_recommendations(error_text: str) -> List[dict]:
    """Mock Claude AI recommendations"""
    mock_solutions = [
        {
            "description": "Configuration Error: Missing environment variables",
            "confidence": 0.9,
            "solution_text": "Check your environment variables:\n1. Verify all required ENV vars are set\n2. Check .env file syntax\n3. Restart the application after changes"
        },
        {
            "description": "Dependency Conflict: Package version mismatch",
            "confidence": 0.85,
            "solution_text": "Resolve dependency conflicts:\n1. Update package.json/requirements.txt\n2. Clear cache (npm ci / pip install --force-reinstall)\n3. Check for breaking changes in dependencies"
        },
        {
            "description": "Build Error: Compilation failure",
            "confidence": 0.8,
            "solution_text": "Fix build issues:\n1. Check for syntax errors in code\n2. Verify all imports are correct\n3. Ensure build tools are properly configured"
        },
        {
            "description": "Network Error: Connection timeout",
            "confidence": 0.75,
            "solution_text": "Network connectivity issues:\n1. Check firewall settings\n2. Verify network configuration\n3. Test connectivity to external services"
        },
        {
            "description": "Permission Error: Access denied",
            "confidence": 0.7,
            "solution_text": "Permission problems:\n1. Check file/directory permissions\n2. Verify user has required access\n3. Check SELinux/AppArmor policies if applicable"
        }
    ]
    
    # Return solutions based on error text keywords
    if "npm" in error_text.lower() or "node" in error_text.lower():
        return [mock_solutions[1], mock_solutions[2], mock_solutions[0]]
    elif "docker" in error_text.lower():
        return [mock_solutions[2], mock_solutions[4], mock_solutions[3]]
    elif "permission" in error_text.lower():
        return [mock_solutions[4], mock_solutions[0], mock_solutions[3]]
    else:
        return mock_solutions[:3]

def extract_github_repo_info(github_url: str) -> tuple:
    """Extract owner and repo from GitHub URL"""
    pattern = r'github\.com/([^/]+)/([^/]+)'
    match = re.search(pattern, github_url)
    if match:
        return match.group(1), match.group(2).replace('.git', '')
    raise ValueError("Invalid GitHub URL format")

def get_github_failed_pipelines(owner: str, repo: str) -> List[dict]:
    """Mock GitHub failed pipelines"""
    return [
        {
            "workflow_name": "CI/CD Pipeline",
            "run_id": "12345",
            "failure_reason": "Build failed: npm test failed",
            "logs": "Error: Test suite failed with 3 failing tests\n\tat test/app.test.js:15:1\nnpm ERR! Test failed. See details above."
        },
        {
            "workflow_name": "Deploy to Production",
            "run_id": "12346", 
            "failure_reason": "Deployment failed: Docker build error",
            "logs": "Step 5/10 : RUN npm install\n---> Running in abc123\nnpm ERR! code ENOENT\nnpm ERR! syscall open"
        }
    ]

class DevOpsAIHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self._send_json_response({"message": "DevOps AI Assistant API"})
        elif self.path == '/health':
            claude_valid = validate_claude_api_key()
            self._send_json_response({
                "status": "healthy",
                "claude_api_valid": claude_valid
            })
        elif self.path == '/rag-stats':
            self._send_json_response({
                "total_solutions": len(rag_database),
                "database_entries": len(rag_database)
            })
        else:
            self.send_error(404)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        if self.path == '/search-logs':
            try:
                data = json.loads(post_data.decode('utf-8'))
                log_content = data.get('log_content', '')
                
                # Check RAG database first
                rag_solution = search_rag_database(log_content)
                if rag_solution:
                    self._send_json_response({"solutions": [rag_solution], "source": "rag"})
                else:
                    # Get Claude recommendations
                    claude_solutions = get_claude_recommendations(log_content)
                    self._send_json_response({"solutions": claude_solutions, "source": "claude"})
            except Exception as e:
                self.send_error(400, f"Error processing request: {str(e)}")
        
        elif self.path == '/analyze-github':
            try:
                data = json.loads(post_data.decode('utf-8'))
                github_url = data.get('github_url', '')
                
                owner, repo = extract_github_repo_info(github_url)
                failed_pipelines = get_github_failed_pipelines(owner, repo)
                
                all_solutions = []
                for pipeline in failed_pipelines:
                    error_text = f"{pipeline['failure_reason']}\n{pipeline['logs']}"
                    
                    # Check RAG first
                    rag_solution = search_rag_database(error_text)
                    if rag_solution:
                        all_solutions.append({
                            "pipeline": pipeline,
                            "solutions": [rag_solution],
                            "source": "rag"
                        })
                    else:
                        # Get Claude recommendations
                        claude_solutions = get_claude_recommendations(error_text)
                        all_solutions.append({
                            "pipeline": pipeline,
                            "solutions": claude_solutions,
                            "source": "claude"
                        })
                
                self._send_json_response({"results": all_solutions})
                
            except Exception as e:
                self.send_error(400, f"Error processing GitHub URL: {str(e)}")
        
        elif self.path == '/mark-solution':
            try:
                global solution_counter
                data = json.loads(post_data.decode('utf-8'))
                
                new_entry = {
                    "id": solution_counter,
                    "error": data.get('error_text', ''),
                    "solution": data.get('solution_text', '')
                }
                rag_database.append(new_entry)
                solution_counter += 1
                
                self._send_json_response({
                    "message": "Solution marked as correct and stored in database",
                    "entry_id": new_entry["id"]
                })
                
            except Exception as e:
                self.send_error(400, f"Error marking solution: {str(e)}")
        
        elif self.path == '/upload-logs':
            # For file upload, we'd need to parse multipart data
            # For now, return a mock response
            self._send_json_response({
                "solutions": get_claude_recommendations("uploaded log file"),
                "source": "claude"
            })
        
        else:
            self.send_error(404)

    def _send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def main():
    with socketserver.TCPServer(("", PORT), DevOpsAIHandler) as httpd:
        print(f"🚀 DevOps AI Assistant Backend running on http://localhost:{PORT}")
        print("📊 Health check: http://localhost:8000/health")
        print("📖 API docs: Available endpoints - /, /health, /search-logs, /analyze-github, /mark-solution")
        httpd.serve_forever()

if __name__ == "__main__":
    main()