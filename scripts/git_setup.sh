#!/bin/bash
echo "🔧 Setting up Git repository for Cognitrix..."

if [ ! -d ".git" ]; then
    git init
    echo "✅ Git repository initialized"
fi

cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
ENV/
env.bak/
venv.bak/

# Flask
instance/
.webassets-cache

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Configuration (sensitive)
config/local.json
config/secrets.json

# Temporary files
*.tmp
*.bak
temp/
GITIGNORE

git add .
git commit -m "Initial Cognitrix setup - Phase 1 MVP

Features:
- Basic Flask application with search functionality
- File-based prompt storage with YAML frontmatter
- Bootstrap UI with responsive design
- Category browsing and favorites system
- Copy to clipboard functionality
- Ready for Phase 2 Ollama integration"

echo "✅ Initial Git commit created"
echo "📝 To connect to GitHub:"
echo "   git remote add origin https://github.com/yourusername/cognitrix.git"
echo "   git branch -M main" 
echo "   git push -u origin main"
