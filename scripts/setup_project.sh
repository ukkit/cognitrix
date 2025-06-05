#!/bin/bash

# Create directory structure
echo "📂 Creating directory structure..."
mkdir -p prompts/{coding,writing,analysis}
mkdir -p app/{templates,static/{css,js}}
mkdir -p config
mkdir -p scripts
mkdir -p data

# Create initial prompt files with examples
echo "📝 Creating example prompts..."
cat > prompts/coding/code_review.md << 'EOF'
---
title: "Code Review Assistant"
category: "coding"
tags: ["python", "review", "best-practices"]
variables: ["language", "code_snippet"]
favorite: false
created: 2025-01-15
last_used: 2025-01-20
use_count: 15
---

You are an expert {language} code reviewer. Please review this code:

{code_snippet}

Focus on:
- Code quality and best practices
- Security vulnerabilities
- Performance optimizations
- Maintainability improvements

Provide specific, actionable feedback with examples where possible.
EOF

cat > prompts/writing/technical_documentation.md << 'EOF'
---
title: "Technical Documentation Writer"
category: "writing"
tags: ["documentation", "technical", "clarity"]
variables: ["topic", "audience"]
favorite: true
created: 2025-01-10
last_used: 2025-01-25
use_count: 32
---

Create comprehensive technical documentation for {topic}.

Target audience: {audience}

Structure the documentation with:
1. Overview and purpose
2. Prerequisites and requirements
3. Step-by-step implementation
4. Code examples with explanations
5. Troubleshooting common issues
6. Best practices and recommendations

Use clear, concise language and include practical examples.
EOF

cat > prompts/analysis/data_analysis.md << 'EOF'
---
title: "Data Analysis Expert"
category: "analysis"
tags: ["data", "statistics", "insights"]
variables: ["dataset_description", "analysis_goal"]
favorite: false
created: 2025-01-12
last_used: 2025-01-22
use_count: 8
---

Analyze the following dataset: {dataset_description}

Analysis objective: {analysis_goal}

Please provide:
1. Data overview and key characteristics
2. Statistical summary and patterns
3. Insights and trends discovered
4. Recommendations based on findings
5. Suggested next steps for further analysis

Include specific metrics and visualizations where appropriate.
EOF

# Create Flask application
echo "⚙️ Creating Flask application..."
cat > app/app.py << 'EOF'
#!/usr/bin/env python3
"""
Cognitrix - Personal LLM Prompt Management System
A lightweight, file-based prompt management system with search and Ollama integration.
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for
import yaml
from collections import defaultdict

app = Flask(__name__)
app.secret_key = 'cognitrix-dev-key-change-in-production'

# Configuration
PROMPTS_DIR = Path('../prompts')
CONFIG_DIR = Path('../config')

class PromptManager:
    def __init__(self, prompts_dir):
        self.prompts_dir = Path(prompts_dir)
        self.prompts = []
        self.categories = defaultdict(list)
        self.load_prompts()
    
    def load_prompts(self):
        """Load all prompt files and build index"""
        self.prompts = []
        self.categories = defaultdict(list)
        
        for prompt_file in self.prompts_dir.rglob('*.md'):
            try:
                prompt_data = self.parse_prompt_file(prompt_file)
                if prompt_data:
                    self.prompts.append(prompt_data)
                    category = prompt_data.get('category', 'uncategorized')
                    self.categories[category].append(prompt_data)
            except Exception as e:
                print(f"Error loading {prompt_file}: {e}")
    
    def parse_prompt_file(self, file_path):
        """Parse markdown file with YAML frontmatter"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split frontmatter and content
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1])
                    prompt_content = parts[2].strip()
                    
                    frontmatter['content'] = prompt_content
                    frontmatter['file_path'] = str(file_path)
                    frontmatter['id'] = str(file_path.stem)
                    
                    return frontmatter
                except yaml.YAMLError as e:
                    print(f"YAML error in {file_path}: {e}")
        
        return None
    
    def search_prompts(self, query):
        """Search prompts by title, content, and tags"""
        if not query:
            return self.prompts
        
        query_lower = query.lower()
        results = []
        
        for prompt in self.prompts:
            score = 0
            
            # Title match (highest weight)
            if query_lower in prompt.get('title', '').lower():
                score += 10
            
            # Tag match
            tags = prompt.get('tags', [])
            if any(query_lower in tag.lower() for tag in tags):
                score += 5
            
            # Content match
            if query_lower in prompt.get('content', '').lower():
                score += 2
            
            # Category match
            if query_lower in prompt.get('category', '').lower():
                score += 3
            
            if score > 0:
                prompt['search_score'] = score
                results.append(prompt)
        
        # Sort by score (descending)
        results.sort(key=lambda x: x['search_score'], reverse=True)
        return results
    
    def get_favorites(self):
        """Get favorite prompts"""
        return [p for p in self.prompts if p.get('favorite', False)]
    
    def get_recent(self, limit=10):
        """Get recently used prompts"""
        recent = [p for p in self.prompts if p.get('last_used')]
        recent.sort(key=lambda x: x.get('last_used', ''), reverse=True)
        return recent[:limit]

# Initialize prompt manager
prompt_manager = PromptManager(PROMPTS_DIR)

@app.route('/')
def index():
    """Main dashboard"""
    stats = {
        'total_prompts': len(prompt_manager.prompts),
        'categories': len(prompt_manager.categories),
        'favorites': len(prompt_manager.get_favorites())
    }
    
    return render_template('index.html', 
                         categories=dict(prompt_manager.categories),
                         recent=prompt_manager.get_recent(),
                         favorites=prompt_manager.get_favorites(),
                         stats=stats)

@app.route('/search')
def search():
    """Search prompts"""
    query = request.args.get('q', '')
    results = prompt_manager.search_prompts(query)
    
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify({'results': results, 'query': query})
    
    return render_template('search.html', results=results, query=query)

@app.route('/prompt/<prompt_id>')
def view_prompt(prompt_id):
    """View individual prompt"""
    prompt = next((p for p in prompt_manager.prompts if p['id'] == prompt_id), None)
    if not prompt:
        return "Prompt not found", 404
    
    return render_template('prompt.html', prompt=prompt)

@app.route('/category/<category_name>')
def view_category(category_name):
    """View prompts by category"""
    prompts = prompt_manager.categories.get(category_name, [])
    return render_template('category.html', 
                         prompts=prompts, 
                         category=category_name)

@app.route('/api/reload')
def reload_prompts():
    """Reload prompts from disk"""
    prompt_manager.load_prompts()
    return jsonify({'status': 'success', 'message': 'Prompts reloaded'})

if __name__ == '__main__':
    app.run(debug=True, port=3001, host='0.0.0.0')
EOF

# [Previous template creation code continues here - truncated for brevity]
# The rest of the setup creates all templates, CSS, JS, config files, etc.

echo "✅ Project structure created successfully!"
