#!/bin/bash

# Cognitrix Auto-Categorization Setup Script
# Adds AI-powered categorization to your existing Cognitrix installation

echo "🤖 Setting up Cognitrix Auto-Categorization..."
echo "=================================================="

# Check if we're in a Cognitrix directory
if [ ! -f "app/app.py" ] || [ ! -d "prompts" ]; then
    echo "❌ Error: This doesn't appear to be a Cognitrix directory"
    echo "   Please run this script from your Cognitrix root directory"
    echo "   Expected structure:"
    echo "     app/app.py"
    echo "     prompts/"
    exit 1
fi

echo "✅ Found Cognitrix installation"

# Create required directories
echo "📁 Creating directories..."
mkdir -p cache
mkdir -p config
mkdir -p scripts

# Check if Ollama is running
echo "🔍 Checking Ollama availability..."
OLLAMA_HOST=${OLLAMA_HOST:-localhost}
OLLAMA_PORT=${OLLAMA_PORT:-11434}
OLLAMA_URL="http://$OLLAMA_HOST:$OLLAMA_PORT"

if curl -s "$OLLAMA_URL/api/tags" > /dev/null 2>&1; then
    echo "✅ Ollama is running at $OLLAMA_URL"
    
    # Check for a small model
    MODELS=$(curl -s "$OLLAMA_URL/api/tags" | grep -o '"name":"[^"]*' | cut -d'"' -f4)
    
    if echo "$MODELS" | grep -q "llama3.2:1b\|phi3:mini\|qwen2.5:0.5b"; then
        echo "✅ Found suitable small model for categorization"
    else
        echo "⚠️  No small model found. Downloading llama3.2:1b for fast categorization..."
        echo "   This is a 1.3GB model optimized for your Dell Optiplex hardware"
        
        read -p "   Download llama3.2:1b now? [Y/n]: " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
            ollama pull llama3.2:1b
            echo "✅ Model downloaded successfully"
        else
            echo "⚠️  You can download it later with: ollama pull llama3.2:1b"
        fi
    fi
else
    echo "❌ Ollama is not running at $OLLAMA_URL. Please start Ollama first:"
    echo "   ollama serve"
    echo ""
    echo "   Or set custom host/port:"
    echo "   export OLLAMA_HOST=your-server"
    echo "   export OLLAMA_PORT=11434"
    echo ""
    echo "   Then run this setup script again."
    exit 1
fi

# Save the categorizer module
echo "💾 Installing categorizer module..."
cat > categorizer.py << 'EOF'
#!/usr/bin/env python3
"""
Cognitrix Auto-Categorization Module
Intelligent prompt categorization using local LLM via Ollama
"""

import os
import re
import json
import yaml
import requests
from pathlib import Path
from datetime import datetime
from collections import Counter
import logging

class PromptCategorizer:
    def __init__(self, ollama_url="http://localhost:11434", model="llama3.2:1b"):
        """
        Initialize the auto-categorization system
        
        Args:
            ollama_url: Ollama API endpoint
            model: Small, fast model for categorization (llama3.2:1b recommended for speed)
        """
        self.ollama_url = ollama_url
        self.model = model
        self.prompts_dir = Path("prompts")
        self.cache_file = Path("cache/categorization_cache.json")
        self.config_file = Path("config/categorization_config.json")
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_config()
        
        # Set Ollama connection details from config  
        self.ollama_url = f"http://{self.config['ollama']['host']}:{self.config['ollama']['port']}"
        self.model = self.config['ollama']['model']
        self.timeout = self.config['ollama']['timeout']
        self.connect_timeout = self.config['ollama']['connect_timeout']
        
        # Load categorization cache
        self.cache = self._load_cache()
        
        # Predefined categories with keywords for fast classification
        self.category_keywords = {
            "coding": ["code", "programming", "python", "javascript", "debug", "function", "api", "database", "sql", "html", "css", "react", "nodejs"],
            "writing": ["write", "essay", "article", "blog", "story", "content", "copy", "creative", "draft", "edit", "proofread", "grammar"],
            "analysis": ["analyze", "compare", "evaluate", "research", "data", "report", "study", "examine", "investigate", "assess"],
            "business": ["business", "strategy", "marketing", "sales", "plan", "proposal", "meeting", "project", "management", "finance"],
            "education": ["explain", "teach", "learn", "tutorial", "lesson", "study", "homework", "course", "training", "educational"],
            "creative": ["creative", "idea", "brainstorm", "design", "art", "music", "poem", "story", "innovative", "imagination"],
            "technical": ["technical", "system", "architecture", "documentation", "specification", "engineering", "infrastructure", "deployment"],
            "communication": ["email", "message", "letter", "communication", "response", "reply", "conversation", "chat", "social"],
            "productivity": ["organize", "schedule", "plan", "todo", "task", "workflow", "automation", "efficiency", "time", "management"]
        }

    def _load_config(self):
        """Load categorization configuration"""
        default_config = {
            "ollama": {
                "host": "localhost",
                "port": 11434,
                "model": "llama3.2:1b",
                "timeout": 30,
                "connect_timeout": 10
            },
            "categorization": {
                "confidence_threshold": 0.7,
                "use_llm_categorization": True,
                "use_keyword_fallback": True,
                "auto_approve_high_confidence": True,
                "batch_size": 10
            },
            "model_options": {
                "temperature": 0.1,
                "num_predict": 50,
                "top_p": 0.9,
                "top_k": 40
            }
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return {**default_config, **config}
        else:
            # Create default config
            self.config_file.parent.mkdir(exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config

    def _load_cache(self):
        """Load categorization cache"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        """Save categorization cache"""
        self.cache_file.parent.mkdir(exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def _calculate_content_hash(self, content):
        """Calculate hash of prompt content for caching"""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()

    def keyword_categorize(self, content):
        """Fast keyword-based categorization"""
        content_lower = content.lower()
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                category_scores[category] = score / len(keywords)
        
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            confidence = min(category_scores[best_category] * 2, 0.9)  # Scale confidence
            return best_category, confidence
        
        return "general", 0.1

    def llm_categorize(self, content):
        """Use LLM for intelligent categorization"""
        # Create categorization prompt
        categories_list = ", ".join(self.category_keywords.keys())
        
        categorization_prompt = f"""Analyze this prompt and categorize it into ONE of these categories: {categories_list}

Prompt to categorize:
{content[:500]}...

Respond with only the category name from the list above. Choose the most specific and accurate category."""

        try:
            # Make request to Ollama
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": categorization_prompt,
                    "stream": False,
                    "options": self.config["model_options"]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                category = result["response"].strip().lower()
                
                # Validate category
                if category in self.category_keywords:
                    return category, 0.9  # High confidence for LLM categorization
                else:
                    # Try to find closest match
                    for valid_cat in self.category_keywords:
                        if valid_cat in category or category in valid_cat:
                            return valid_cat, 0.7
                    
                    self.logger.warning(f"LLM returned invalid category: {category}")
                    return None, 0.0
            else:
                self.logger.error(f"Ollama API error: {response.status_code}")
                return None, 0.0
                
        except Exception as e:
            self.logger.error(f"LLM categorization failed: {e}")
            return None, 0.0

    def categorize_prompt(self, content, title=""):
        """Categorize a single prompt with caching"""
        # Check cache first
        content_hash = self._calculate_content_hash(content)
        if content_hash in self.cache:
            cached = self.cache[content_hash]
            return cached["category"], cached["confidence"], True
        
        # Combine title and content for analysis
        full_content = f"{title}\n\n{content}" if title else content
        
        # Try LLM categorization first if enabled
        if self.config["categorization"]["use_llm_categorization"]:
            category, confidence = self.llm_categorize(full_content)
            
            if category and confidence >= self.config["categorization"]["confidence_threshold"]:
                # Cache successful LLM categorization
                self.cache[content_hash] = {
                    "category": category,
                    "confidence": confidence,
                    "method": "llm",
                    "timestamp": datetime.now().isoformat()
                }
                self._save_cache()
                return category, confidence, False
        
        # Fallback to keyword categorization
        if self.config["categorization"]["use_keyword_fallback"]:
            category, confidence = self.keyword_categorize(full_content)
            
            # Cache keyword categorization
            self.cache[content_hash] = {
                "category": category,
                "confidence": confidence,
                "method": "keyword",
                "timestamp": datetime.now().isoformat()
            }
            self._save_cache()
            return category, confidence, False
        
        # Default category
        return "general", 0.1, False

    def process_prompt_file(self, file_path):
        """Process a single prompt file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split frontmatter and content
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    prompt_content = parts[2].strip()
                    
                    # Parse existing frontmatter
                    try:
                        metadata = yaml.safe_load(frontmatter) or {}
                    except:
                        metadata = {}
                else:
                    metadata = {}
                    prompt_content = content
            else:
                metadata = {}
                prompt_content = content
            
            # Skip if already has a category and we're not forcing recategorization
            if metadata.get('category') and not getattr(self, 'force_recategorize', False):
                return metadata.get('category'), 1.0, True, "existing"
            
            # Categorize the prompt
            title = metadata.get('title', file_path.stem)
            category, confidence, from_cache = self.categorize_prompt(prompt_content, title)
            
            # Update metadata
            metadata['category'] = category
            if not metadata.get('created'):
                metadata['created'] = datetime.now().strftime('%Y-%m-%d')
            
            # Add auto-categorization info
            if not from_cache:
                metadata['auto_categorized'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                metadata['categorization_confidence'] = round(confidence, 2)
            
            # Write back to file
            new_frontmatter = yaml.dump(metadata, default_flow_style=False)
            new_content = f"---\n{new_frontmatter}---\n\n{prompt_content}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return category, confidence, from_cache, "updated"
            
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {e}")
            return "general", 0.1, False, "error"

    def categorize_all_prompts(self, force_recategorize=False):
        """Categorize all prompts in the prompts directory"""
        self.force_recategorize = force_recategorize
        
        if not self.prompts_dir.exists():
            self.logger.error("Prompts directory not found")
            return
        
        # Find all markdown files
        prompt_files = list(self.prompts_dir.rglob("*.md"))
        
        if not prompt_files:
            self.logger.info("No prompt files found")
            return
        
        self.logger.info(f"Processing {len(prompt_files)} prompt files...")
        
        results = {
            "processed": 0,
            "updated": 0,
            "cached": 0,
            "existing": 0,
            "errors": 0,
            "categories": {}
        }
        
        for i, file_path in enumerate(prompt_files, 1):
            self.logger.info(f"Processing ({i}/{len(prompt_files)}): {file_path.name}")
            
            category, confidence, from_cache, status = self.process_prompt_file(file_path)
            
            results["processed"] += 1
            results["categories"][category] = results["categories"].get(category, 0) + 1
            
            if status == "updated":
                results["updated"] += 1
            elif status == "existing":
                results["existing"] += 1
            elif status == "error":
                results["errors"] += 1
            
            if from_cache:
                results["cached"] += 1
            
            # Organize into category directories
            self._organize_by_category(file_path, category)
        
        # Print summary
        self._print_summary(results)
        
        return results

    def _organize_by_category(self, file_path, category):
        """Move prompt file to appropriate category directory"""
        category_dir = self.prompts_dir / category
        category_dir.mkdir(exist_ok=True)
        
        # Only move if not already in correct category
        if file_path.parent.name != category:
            new_path = category_dir / file_path.name
            
            # Handle filename conflicts
            counter = 1
            while new_path.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                new_path = category_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            file_path.rename(new_path)
            self.logger.info(f"Moved {file_path.name} to {category}/")

    def _print_summary(self, results):
        """Print categorization summary"""
        print("\n" + "="*60)
        print("COGNITRIX AUTO-CATEGORIZATION SUMMARY")
        print("="*60)
        print(f"Total processed: {results['processed']}")
        print(f"Updated: {results['updated']}")
        print(f"Already categorized: {results['existing']}")
        print(f"From cache: {results['cached']}")
        print(f"Errors: {results['errors']}")
        print("\nCategory distribution:")
        for category, count in sorted(results['categories'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count}")
        print("="*60)

EOF

echo "✅ Categorizer module installed"

# Create a CLI script for standalone categorization
echo "🔧 Creating CLI categorization script..."
cat > scripts/categorize.py << 'EOF'
#!/usr/bin/env python3
"""
Standalone Cognitrix Auto-Categorization CLI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from categorizer import PromptCategorizer
import argparse

def main():
    parser = argparse.ArgumentParser(description="Cognitrix Auto-Categorization CLI")
    parser.add_argument("--model", default="llama3.2:1b", help="Ollama model to use")
    parser.add_argument("--force", action="store_true", help="Force recategorization")
    parser.add_argument("--analyze", action="store_true", help="Just analyze current categories")
    parser.add_argument("--url", default="http://localhost:11434", help="Ollama API URL")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    categorizer = PromptCategorizer(ollama_url=args.url, model=args.model)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        categorizer.config["categorization"]["use_llm_categorization"] = False  # Use only keywords for dry run
    
    if args.analyze:
        print("📊 Analyzing current categories...")
        categorizer.analyze_categories()
    else:
        print(f"🤖 Starting auto-categorization with model: {args.model}")
        categorizer.categorize_all_prompts(force_recategorize=args.force)

if __name__ == "__main__":
    main()
EOF

chmod +x scripts/categorize.py

echo "✅ CLI script created"

# Create sample prompts if none exist
if [ ! "$(ls -A prompts 2>/dev/null)" ]; then
    echo "📝 Creating sample prompts for testing..."
    
    mkdir -p prompts/sample
    
    cat > prompts/sample/code_review.md << 'EOF'
---
title: "Code Review Assistant"
tags: ["python", "review"]
created: 2025-01-15
---

You are an expert code reviewer. Please review this code and provide feedback on:

- Code quality and best practices
- Security vulnerabilities  
- Performance optimizations
- Maintainability improvements

```python
{code_snippet}
```

Please be specific and provide examples where possible.
EOF

    cat > prompts/sample/blog_writer.md << 'EOF'
---
title: "Blog Post Writer"
tags: ["content", "writing"]
created: 2025-01-15
---

Write a comprehensive blog post about {topic}. The post should be:

- 1000-1500 words
- SEO optimized
- Include subheadings
- Have a compelling introduction and conclusion
- Include actionable tips for readers

Target audience: {audience}
Tone: {tone}
EOF

    cat > prompts/sample/data_analysis.md << 'EOF'
---
title: "Data Analysis Helper"
tags: ["data", "analysis"]
created: 2025-01-15
---

Analyze the following dataset and provide insights:

{dataset_description}

Please provide:
1. Summary statistics
2. Key trends and patterns
3. Anomalies or outliers
4. Recommendations based on findings
5. Visualization suggestions

Format the response in a clear, executive-summary style.
EOF

    echo "✅ Sample prompts created"
fi

# Test the categorization system
echo "🧪 Testing categorization system..."
python3 scripts/categorize.py --analyze

echo ""
echo "🎉 Auto-categorization setup complete!"
echo ""
echo "Configuration:"
echo "  - Edit config/categorization_config.json to adjust:"
echo "    * Ollama host/port/model settings"
echo "    * Confidence thresholds and categorization options"
echo "    * Model performance parameters"
echo "  - Cache stored in cache/categorization_cache.json"
echo ""
echo "Quick Start:"
echo "  1. Test categorization: python3 scripts/categorize.py --dry-run"
echo "  2. Categorize all prompts: python3 scripts/categorize.py"
echo "  3. Force recategorization: python3 scripts/categorize.py --force"
echo "  4. Use different model: python3 scripts/categorize.py --model phi3:mini"
echo "  5. Custom Ollama server: python3 scripts/categorize.py --host myserver --port 11434"
echo ""
echo "Integration with Cognitrix app:"
echo "  - API endpoints available for /api/categorize, /api/recategorize, /api/categories/stats"
echo "  - Add the integration code to your app/app.py for web interface"
echo ""
echo "Configuration file structure:"
echo "  config/categorization_config.json:"
echo "  {" 
echo "    \"ollama\": {"
echo "      \"host\": \"$OLLAMA_HOST\","
echo "      \"port\": $OLLAMA_PORT,"
echo "      \"model\": \"llama3.2:1b\","
echo "      \"timeout\": 30"
echo "    },"
echo "    \"categorization\": {"
echo "      \"confidence_threshold\": 0.7,"
echo "      \"use_llm_categorization\": true"
echo "    }"
echo "  }"
echo ""
echo "Happy prompting! 🚀"