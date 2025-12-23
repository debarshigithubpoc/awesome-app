#!/bin/bash

echo "🚀 DevOps AI Assistant Setup Script"
echo "===================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 18+"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup backend
echo "📦 Setting up backend..."
cd backend

# For production, you might want to use FastAPI instead
echo "📋 Backend ready to start with: python3 simple_server.py"

# Setup frontend
echo "📦 Setting up frontend..."
cd ../frontend

# Install dependencies if not already installed
if [ ! -d "node_modules" ]; then
    echo "📥 Installing frontend dependencies..."
    npm install
fi

echo "📋 Frontend ready to start with: npm start"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend:  cd backend && python3 simple_server.py"
echo "2. Frontend: cd frontend && npm start"
echo ""
echo "Then visit: http://localhost:3000"