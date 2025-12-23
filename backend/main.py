from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import os
from typing import List, Optional
import requests
import re

# ⚠️ DEPRECATED: This is the simplified version with mock data
# For production use, please use enhanced_server.py which has:
# - Real Claude AI API integration
# - Real GitHub API integration  
# - Advanced RAG model with ChromaDB
# - Better error handling and logging

# Initialize FastAPI app
app = FastAPI(title="DevOps AI Assistant (Simple)", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class LogSearchRequest(BaseModel):
    log_content: str
    
class GitHubUrlRequest(BaseModel):
    github_url: str

class Solution(BaseModel):
    id: int
    description: str
    confidence: float
    solution_text: str

class MarkSolutionRequest(BaseModel):
    solution_id: int
    error_text: str
    solution_text: str

# Simple in-memory RAG database (replace with proper vector database in production)
rag_database = []

# Claude AI API configuration
CLAUDE_API_KEY = "your-claude-api-key"
CLAUDE_API_URL = "https://api.anthropic.com/v1/messages"

def validate_claude_api_key():
    """Validate Claude API key"""
    headers = {
        "Authorization": f"Bearer {CLAUDE_API_KEY}",
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    test_payload = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Hi"}]
    }
    
    try:
        response = requests.post(CLAUDE_API_URL, headers=headers, json=test_payload, timeout=10)
        return response.status_code == 200
    except:
        return False

def search_rag_database(query: str) -> Optional[Solution]:
    """Search for solutions in the RAG database"""
    for item in rag_database:
        if query.lower() in item["error"].lower():
            return Solution(
                id=item["id"],
                description=item["error"][:100] + "...",
                confidence=0.95,
                solution_text=item["solution"]
            )
    return None

def get_claude_recommendations(error_text: str) -> List[Solution]:
    """Get recommendations from Claude AI"""
    headers = {
        "Authorization": f"Bearer {CLAUDE_API_KEY}",
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    prompt = f"""
    You are a DevOps expert. Analyze this error and provide up to 10 specific solutions.
    
    Error: {error_text}
    
    For each solution, provide:
    1. A clear description of the problem
    2. Step-by-step solution
    3. A confidence rating (0.0-1.0)
    
    Format as JSON array with fields: description, solution_text, confidence
    """
    
    payload = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 2000,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(CLAUDE_API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            content = response.json()["content"][0]["text"]
            # Extract JSON from the response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                solutions_data = json.loads(json_match.group())
                solutions = []
                for i, sol in enumerate(solutions_data[:10]):  # Limit to 10
                    solutions.append(Solution(
                        id=i,
                        description=sol.get("description", ""),
                        confidence=sol.get("confidence", 0.5),
                        solution_text=sol.get("solution_text", "")
                    ))
                return solutions
    except Exception as e:
        print(f"Claude API error: {e}")
    
    # Fallback mock solutions if API fails
    return [
        Solution(
            id=0,
            description="Common deployment issue",
            confidence=0.8,
            solution_text="Check your deployment configuration and ensure all environment variables are set correctly."
        )
    ]

def extract_github_repo_info(github_url: str) -> tuple:
    """Extract owner and repo from GitHub URL"""
    pattern = r'github\.com/([^/]+)/([^/]+)'
    match = re.search(pattern, github_url)
    if match:
        return match.group(1), match.group(2).replace('.git', '')
    raise ValueError("Invalid GitHub URL format")

def get_github_failed_pipelines(owner: str, repo: str) -> List[dict]:
    """Get failed GitHub Actions workflows (mock implementation)"""
    # This would integrate with GitHub API in production
    # For now, return mock data
    return [
        {
            "workflow_name": "CI/CD Pipeline",
            "run_id": "12345",
            "failure_reason": "Build failed: npm test failed",
            "logs": "Error: Test suite failed with 3 failing tests\n\tat test/app.test.js:15:1"
        },
        {
            "workflow_name": "Deploy to Production",
            "run_id": "12346", 
            "failure_reason": "Deployment failed: Docker build error",
            "logs": "Step 5/10 : RUN npm install\n---> Running in abc123\nnpm ERR! code ENOENT"
        }
    ]

@app.get("/")
async def root():
    return {"message": "DevOps AI Assistant API"}

@app.get("/health")
async def health_check():
    claude_valid = validate_claude_api_key()
    return {
        "status": "healthy",
        "claude_api_valid": claude_valid
    }

@app.post("/search-logs")
async def search_logs(request: LogSearchRequest):
    """Search for solutions based on log content"""
    # First check RAG database
    rag_solution = search_rag_database(request.log_content)
    if rag_solution:
        return {"solutions": [rag_solution], "source": "rag"}
    
    # If not found, get recommendations from Claude
    claude_solutions = get_claude_recommendations(request.log_content)
    return {"solutions": claude_solutions, "source": "claude"}

@app.post("/upload-logs")
async def upload_logs(file: UploadFile = File(...)):
    """Upload and analyze log files"""
    if not file.filename.endswith(('.log', '.txt')):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload .log or .txt files.")
    
    content = await file.read()
    log_content = content.decode('utf-8')
    
    # Process the same way as search logs
    rag_solution = search_rag_database(log_content)
    if rag_solution:
        return {"solutions": [rag_solution], "source": "rag"}
    
    claude_solutions = get_claude_recommendations(log_content)
    return {"solutions": claude_solutions, "source": "claude"}

@app.post("/analyze-github")
async def analyze_github(request: GitHubUrlRequest):
    """Analyze GitHub repository for failed pipelines"""
    try:
        owner, repo = extract_github_repo_info(request.github_url)
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
        
        return {"results": all_solutions}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/mark-solution")
async def mark_solution(request: MarkSolutionRequest):
    """Mark a solution as correct and store in RAG database"""
    # Add to RAG database
    new_entry = {
        "id": len(rag_database),
        "error": request.error_text,
        "solution": request.solution_text
    }
    rag_database.append(new_entry)
    
    return {"message": "Solution marked as correct and stored in database", "entry_id": new_entry["id"]}

@app.get("/rag-stats")
async def get_rag_stats():
    """Get RAG database statistics"""
    return {
        "total_solutions": len(rag_database),
        "database_entries": len(rag_database)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)