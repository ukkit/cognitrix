#!/bin/bash

echo "🧠 Starting Cognitrix..."

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Start the application
echo "🌐 Starting Flask app on http://localhost:3001"
echo "   Press Ctrl+C to stop"
cd app
python app.py