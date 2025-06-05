# Cognitrix Auto-Categorization HOWTO

## 📋 Overview

This guide covers all command line options and usage scenarios for the Cognitrix Auto-Categorization system. The system uses AI (via Ollama) to automatically categorize your prompts into organized folders.

## 🚀 Quick Start

```bash
# 1. Setup (run once)
./setup_categorization.sh

# 2. Test it out
python3 scripts/categorize.py --dry-run

# 3. Categorize all prompts
python3 scripts/categorize.py
```

## 📁 File Structure

```
cognitrix/
├── app/app.py                              # Main Flask application
├── prompts/                                # Your prompt files
│   ├── coding/                            # Auto-generated categories
│   ├── writing/
│   └── ...
├── config/categorization_config.json      # Configuration file
├── cache/categorization_cache.json        # Categorization cache
├── scripts/categorize.py                  # CLI categorization tool
├── categorizer.py                         # Core categorization module
└── HOWTO.md                              # This file
```

## ⚙️ Configuration

### Configuration File (`config/categorization_config.json`)

```json
{
  "ollama": {
    "host": "localhost",
    "port": 11434,
    "model": "llama3.2:1b",
    "timeout": 30,
    "connect_timeout": 10
  },
  "categorization": {
    "confidence_threshold": 0.7,
    "use_llm_categorization": true,
    "use_keyword_fallback": true,
    "auto_approve_high_confidence": true,
    "batch_size": 10
  },
  "model_options": {
    "temperature": 0.1,
    "num_predict": 50,
    "top_p": 0.9,
    "top_k": 40
  }
}
```

### Configuration Sections

**`ollama` section:**
- `host`: Ollama server hostname (default: "localhost")
- `port`: Ollama server port (default: 11434)
- `model`: Model to use for categorization (default: "llama3.2:1b")
- `timeout`: Response timeout in seconds (default: 30)
- `connect_timeout`: Connection timeout in seconds (default: 10)

**`categorization` section:**
- `confidence_threshold`: Minimum confidence to accept LLM categorization (0.0-1.0)
- `use_llm_categorization`: Enable AI-powered categorization (true/false)
- `use_keyword_fallback`: Fall back to keyword matching if LLM fails (true/false)
- `auto_approve_high_confidence`: Automatically apply high-confidence results (true/false)
- `batch_size`: Number of prompts to process in each batch (default: 10)

**`model_options` section:**
- `temperature`: Creativity level (0.1 = focused, 1.0 = creative)
- `num_predict`: Maximum tokens to generate (default: 50)
- `top_p`: Nucleus sampling threshold (default: 0.9)
- `top_k`: Top-k sampling limit (default: 40)

## 🖥️ Command Line Interface

### Basic Usage

```bash
python3 scripts/categorize.py [OPTIONS]
```

### Command Line Options

#### Core Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--help` | Show help message and exit | - | `--help` |
| `--config PATH` | Path to custom configuration file | `config/categorization_config.json` | `--config /path/to/custom.json` |
| `--dry-run` | Show what would be done without making changes | false | `--dry-run` |
| `--force` | Force recategorization of already categorized prompts | false | `--force` |
| `--analyze` | Just analyze current category distribution | false | `--analyze` |

#### Ollama Server Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--host HOST` | Override Ollama server hostname | From config | `--host myserver.local` |
| `--port PORT` | Override Ollama server port | From config | `--port 11434` |
| `--model MODEL` | Override model name | From config | `--model phi3:mini` |

### Usage Examples

#### 1. Basic Categorization

```bash
# Categorize all uncategorized prompts
python3 scripts/categorize.py

# Force recategorization of all prompts
python3 scripts/categorize.py --force

# Test run without making changes
python3 scripts/categorize.py --dry-run
```

#### 2. Analysis and Statistics

```bash
# View current category distribution
python3 scripts/categorize.py --analyze

# Sample output:
# Category Analysis (234 total prompts):
# ----------------------------------------
# coding          87 ( 37.2%)
# writing         45 ( 19.2%)
# analysis        32 ( 13.7%)
# business        28 ( 12.0%)
# uncategorized   42 ( 17.9%)
```

#### 3. Custom Ollama Server

```bash
# Use remote Ollama server
python3 scripts/categorize.py --host ollama.company.com --port 11434

# Use different model
python3 scripts/categorize.py --model phi3:mini

# Combine server and model options
python3 scripts/categorize.py --host myserver --port 8080 --model qwen2.5:0.5b
```

#### 4. Custom Configuration

```bash
# Use custom config file
python3 scripts/categorize.py --config /path/to/production.json

# Combine custom config with overrides
python3 scripts/categorize.py --config custom.json --model llama3.2:3b --force
```

#### 5. Environment Variables

```bash
# Set Ollama server via environment
export OLLAMA_HOST=myserver.local
export OLLAMA_PORT=11434
python3 scripts/categorize.py

# Or inline
OLLAMA_HOST=server.local python3 scripts/categorize.py
```

## 🏷️ Categories

The system recognizes these categories:

| Category | Keywords/Triggers | Examples |
|----------|------------------|----------|
| **coding** | code, programming, python, javascript, debug, function, api, database | Code review, debugging help, API documentation |
| **writing** | write, essay, article, blog, story, content, copy, creative | Blog posts, articles, creative writing |
| **analysis** | analyze, compare, evaluate, research, data, report, study | Data analysis, research reports, comparisons |
| **business** | business, strategy, marketing, sales, plan, proposal, meeting | Business plans, marketing copy, proposals |
| **education** | explain, teach, learn, tutorial, lesson, study, homework | Tutorials, explanations, educational content |
| **creative** | creative, idea, brainstorm, design, art, music, poem | Creative writing, brainstorming, design |
| **technical** | technical, system, architecture, documentation, specification | Technical docs, system design, specifications |
| **communication** | email, message, letter, communication, response, reply | Emails, messages, social media |
| **productivity** | organize, schedule, plan, todo, task, workflow, automation | Task management, scheduling, workflows |
| **general** | (fallback category) | Anything that doesn't fit other categories |

## 🔧 Advanced Usage

### Performance Optimization

#### For Fast Processing (Dell Optiplex 3070)
```json
{
  "ollama": {
    "model": "llama3.2:1b"
  },
  "model_options": {
    "temperature": 0.1,
    "num_predict": 30,
    "num_ctx": 2048
  }
}
```

#### For Better Accuracy (Higher-end hardware)
```json
{
  "ollama": {
    "model": "llama3.2:3b"
  },
  "model_options": {
    "temperature": 0.2,
    "num_predict": 100,
    "num_ctx": 4096
  }
}
```

### Batch Processing

```bash
# Process in smaller batches for memory-constrained systems
# Edit config: "batch_size": 5
python3 scripts/categorize.py

# For high-memory systems, increase batch size
# Edit config: "batch_size": 25
```

### Debugging

```bash
# Enable verbose logging
export PYTHONPATH=.
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from categorizer import PromptCategorizer
c = PromptCategorizer()
c.categorize_all_prompts()
"
```

## 🌐 Web API Integration

When integrated with your Cognitrix Flask app, these endpoints become available:

### API Endpoints

#### POST `/api/categorize`
Categorize a single prompt.

**Request:**
```json
{
  "content": "Write a Python function to sort a list",
  "title": "Sorting Helper"
}
```

**Response:**
```json
{
  "category": "coding",
  "confidence": 0.92,
  "from_cache": false,
  "suggestions": ["coding", "writing", "analysis", "..."]
}
```

#### POST `/api/recategorize`
Batch categorize all prompts.

**Request:**
```json
{
  "force": false
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "processed": 150,
    "updated": 75,
    "cached": 45,
    "existing": 30,
    "errors": 0,
    "categories": {
      "coding": 50,
      "writing": 30,
      "analysis": 25
    }
  }
}
```

#### GET `/api/categories/stats`
Get category statistics.

**Response:**
```json
{
  "total_prompts": 150,
  "categories": {
    "coding": 50,
    "writing": 30,
    "analysis": 25,
    "business": 20,
    "general": 25
  },
  "available_categories": [
    "coding", "writing", "analysis", "business", 
    "education", "creative", "technical", 
    "communication", "productivity", "general"
  ]
}
```

## 📊 Monitoring and Maintenance

### Cache Management

```bash
# View cache statistics
ls -la cache/categorization_cache.json

# Clear cache to force fresh categorization
rm cache/categorization_cache.json
python3 scripts/categorize.py
```

### Performance Monitoring

```bash
# Time categorization process
time python3 scripts/categorize.py

# Monitor Ollama server
curl http://localhost:11434/api/tags
```

### Regular Maintenance

```bash
# Weekly: Recategorize new prompts
python3 scripts/categorize.py

# Monthly: Full recategorization
python3 scripts/categorize.py --force

# As needed: Analysis
python3 scripts/categorize.py --analyze
```

## 🚨 Troubleshooting

### Common Issues

#### "Connection refused" error
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

#### "Model not found" error
```bash
# List available models
ollama list

# Pull missing model
ollama pull llama3.2:1b
```

#### "Permission denied" errors
```bash
# Fix file permissions
chmod +x scripts/categorize.py
chmod 755 categorizer.py
```

#### Slow performance
```bash
# Use smaller model
python3 scripts/categorize.py --model llama3.2:1b

# Reduce prediction length
# Edit config: "num_predict": 30
```

#### Memory issues
```bash
# Reduce batch size
# Edit config: "batch_size": 5

# Use smaller context
# Edit config: "num_ctx": 2048
```

### Debug Mode

```bash
# Enable debug logging
export PYTHONPATH=.
python3 -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from scripts.categorize import main
main()
" --dry-run
```

## 🔄 Migration and Backup

### Backup Configuration

```bash
# Backup current config
cp config/categorization_config.json config/categorization_config.json.backup

# Backup cache
cp cache/categorization_cache.json cache/categorization_cache.json.backup
```

### Migration Between Servers

```bash
# Export current setup
tar -czf cognitrix-categorization.tar.gz config/ cache/ categorizer.py scripts/

# Import on new server
tar -xzf cognitrix-categorization.tar.gz

# Update server settings
python3 scripts/categorize.py --host newserver --port 11434 --analyze
```

## 📚 Best Practices

### 1. Model Selection
- **Dell Optiplex 3070**: Use `llama3.2:1b` (fast, 1.3GB)
- **Higher-end CPU**: Use `llama3.2:3b` (better accuracy)
- **GPU available**: Use `llama3.1:8b` (best accuracy)

### 2. Configuration Tuning
- Start with defaults
- Adjust `confidence_threshold` based on accuracy needs
- Tune `batch_size` based on available memory
- Lower `temperature` for more consistent categorization

### 3. Workflow Integration
- Run categorization after adding new prompts
- Use `--dry-run` to preview changes
- Periodically use `--force` for cleanup
- Monitor category distribution with `--analyze`

### 4. Performance Tips
- Enable caching for repeated categorization
- Use keyword fallback for reliability
- Batch process for efficiency
- Monitor Ollama server performance

---

## 📞 Need Help?

- Check the troubleshooting section above
- Review configuration settings
- Test with `--dry-run` first
- Use `--analyze` to understand current state
- Check Ollama server status and logs