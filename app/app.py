#!/usr/bin/env python3
"""
Cognitrix - Personal LLM Prompt Management System
A lightweight, file-based prompt management system with search and Ollama integration.
"""

import requests
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


def find_prompt_file(prompt_id):
    """Centralized prompt file finder"""
    for prompt_file in PROMPTS_DIR.rglob('*.md'):
        relative_path = str(prompt_file.relative_to(
            PROMPTS_DIR)).replace('\\', '/')
        if relative_path == prompt_id or prompt_file.stem == prompt_id:
            return prompt_file
    return None


def get_template_context():
    """Get common template context for all routes"""
    return {
        'categories': dict(prompt_manager.categories)
    }


@app.route('/')
def index():
    """Main dashboard"""
    stats = {
        'total_prompts': len(prompt_manager.prompts),
        'categories': len(prompt_manager.categories),
        'favorites': len(prompt_manager.get_favorites())
    }

    context = get_template_context()
    context.update({
        'recent': prompt_manager.get_recent(),
        'favorites': prompt_manager.get_favorites(),
        'stats': stats
    })

    return render_template('index.html', **context)


@app.route('/search')
def search():
    """Search prompts"""
    query = request.args.get('q', '')
    results = prompt_manager.search_prompts(query)

    if request.headers.get('Content-Type') == 'application/json':
        return jsonify({'results': results, 'query': query})

    context = get_template_context()
    context.update({
        'results': results,
        'query': query
    })

    return render_template('search.html', **context)


@app.route('/prompt/<prompt_id>')
def view_prompt(prompt_id):
    """View individual prompt"""
    prompt = next(
        (p for p in prompt_manager.prompts if p['id'] == prompt_id), None)
    if not prompt:
        return "Prompt not found", 404

    context = get_template_context()
    context.update({
        'prompt': prompt
    })

    return render_template('prompt.html', **context)


@app.route('/category/<category_name>')
def view_category(category_name):
    """View prompts by category"""
    prompts = prompt_manager.categories.get(category_name, [])

    context = get_template_context()
    context.update({
        'prompts': prompts,
        'category': category_name  # Ensure this is a string
    })

    return render_template('category.html', **context)


@app.route('/api/reload')
def reload_prompts():
    """Reload prompts from disk"""
    prompt_manager.load_prompts()
    return jsonify({'status': 'success', 'message': 'Prompts reloaded'})


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    context = get_template_context()
    return render_template('404.html', **context), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    context = get_template_context()
    return render_template('500.html', **context), 500


# Route to track prompt usage analytics
@app.route('/api/track-usage', methods=['POST'])
def track_usage():
    """Track prompt usage for analytics"""
    try:
        data = request.get_json()
        prompt_id = data.get('prompt_id')
        action = data.get('action')
        timestamp = data.get('timestamp')

        if not prompt_id or not action:
            return jsonify({'error': 'Missing required fields'}), 400

        # Create usage log entry
        usage_entry = {
            'prompt_id': prompt_id,
            'action': action,
            'timestamp': timestamp or datetime.now().isoformat(),
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr
        }

        # Save to usage log file
        usage_log_path = os.path.join('data', 'usage_log.jsonl')
        os.makedirs('data', exist_ok=True)

        with open(usage_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(usage_entry) + '\n')

        return jsonify({'status': 'success'})

    except Exception as e:
        print(f"Usage tracking error: {e}")
        return jsonify({'error': 'Failed to track usage'}), 500

# Route to get prompt content with variable processing


@app.route('/api/prompt/<path:prompt_id>')
def get_prompt_content(prompt_id):
    """Get prompt content for copying with optional variable substitution"""
    try:
        # Find the prompt file
        prompt_file = None
        for root, dirs, files in os.walk(PROMPTS_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    if file_path.replace('\\', '/').replace('prompts/', '') == prompt_id:
                        prompt_file = file_path
                        break
            if prompt_file:
                break

        if not prompt_file:
            return jsonify({'error': 'Prompt not found'}), 404

        # Read and parse the prompt
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                import yaml
                try:
                    metadata = yaml.safe_load(parts[1])
                    prompt_content = parts[2].strip()
                except yaml.YAMLError:
                    metadata = {}
                    prompt_content = content
            else:
                metadata = {}
                prompt_content = content
        else:
            metadata = {}
            prompt_content = content

        # Get variables from query parameters for substitution
        variables = {}
        for key, value in request.args.items():
            if key.startswith('var_'):
                var_name = key[4:]  # Remove 'var_' prefix
                variables[var_name] = value

        # Substitute variables if provided
        processed_content = prompt_content
        if variables:
            for var_name, var_value in variables.items():
                placeholder = f'{{{var_name}}}'
                processed_content = processed_content.replace(
                    placeholder, var_value)

        return jsonify({
            'content': processed_content,
            'original_content': prompt_content,
            'metadata': metadata,
            'variables_used': variables
        })

    except Exception as e:
        print(f"Error getting prompt content: {e}")
        return jsonify({'error': 'Failed to get prompt content'}), 500

# Route to get usage statistics


@app.route('/api/usage-stats')
def get_usage_stats():
    """Get usage statistics for dashboard"""
    try:
        usage_log_path = os.path.join('data', 'usage_log.jsonl')

        if not os.path.exists(usage_log_path):
            return jsonify({
                'total_copies': 0,
                'today_copies': 0,
                'most_used_prompts': [],
                'recent_activity': []
            })

        usage_data = []
        today = datetime.now().date()

        with open(usage_log_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    usage_data.append(entry)
                except json.JSONDecodeError:
                    continue

        # Calculate statistics
        total_copies = len(
            [entry for entry in usage_data if entry.get('action') == 'copy'])

        today_copies = len([
            entry for entry in usage_data
            if entry.get('action') == 'copy' and
            datetime.fromisoformat(entry.get('timestamp', '')).date() == today
        ])

        # Most used prompts (last 30 days)
        from collections import Counter
        recent_copies = [
            entry['prompt_id'] for entry in usage_data
            if entry.get('action') == 'copy' and
            (datetime.now() - datetime.fromisoformat(entry.get('timestamp', ''))).days <= 30
        ]
        most_used = Counter(recent_copies).most_common(5)

        # Recent activity (last 10 actions)
        recent_activity = sorted(
            usage_data,
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )[:10]

        return jsonify({
            'total_copies': total_copies,
            'today_copies': today_copies,
            'most_used_prompts': [{'prompt_id': pid, 'count': count} for pid, count in most_used],
            'recent_activity': recent_activity
        })

    except Exception as e:
        print(f"Error getting usage stats: {e}")
        return jsonify({'error': 'Failed to get usage stats'}), 500

# Helper function to update prompt metadata (last_used, use_count)


def update_prompt_usage(prompt_file_path):
    """Update prompt file with usage statistics"""
    try:
        with open(prompt_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                import yaml
                try:
                    metadata = yaml.safe_load(parts[1]) or {}
                    prompt_content = parts[2].strip()

                    # Update usage metadata
                    metadata['last_used'] = datetime.now().strftime('%Y-%m-%d')
                    metadata['use_count'] = metadata.get('use_count', 0) + 1

                    # Write back to file
                    new_content = f"---\n{yaml.dump(metadata, default_flow_style=False)}---\n{prompt_content}"

                    with open(prompt_file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                except yaml.YAMLError:
                    pass  # Skip if YAML is malformed

    except Exception as e:
        print(f"Error updating prompt usage: {e}")

# Enhanced route with usage tracking


@app.route('/api/copy-prompt', methods=['POST'])
def copy_prompt():
    """Enhanced copy endpoint that tracks usage and updates metadata"""
    try:
        data = request.get_json()
        prompt_id = data.get('prompt_id')
        variables = data.get('variables', {})

        if not prompt_id:
            return jsonify({'error': 'Missing prompt_id'}), 400

        # Find and process the prompt
        prompt_file = None
        for root, dirs, files in os.walk(PROMPTS_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    if file_path.replace('\\', '/').replace('prompts/', '') == prompt_id:
                        prompt_file = file_path
                        break
            if prompt_file:
                break

        if not prompt_file:
            return jsonify({'error': 'Prompt not found'}), 404

        # Read prompt content
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse content
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                prompt_content = parts[2].strip()
            else:
                prompt_content = content
        else:
            prompt_content = content

        # Process variables
        processed_content = prompt_content
        if variables:
            for var_name, var_value in variables.items():
                placeholder = f'{{{var_name}}}'
                processed_content = processed_content.replace(
                    placeholder, var_value)

        # Update usage metadata
        update_prompt_usage(prompt_file)

        # Track usage
        usage_entry = {
            'prompt_id': prompt_id,
            'action': 'copy',
            'timestamp': datetime.now().isoformat(),
            'variables_used': variables,
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr
        }

        usage_log_path = os.path.join('data', 'usage_log.jsonl')
        os.makedirs('data', exist_ok=True)

        with open(usage_log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(usage_entry) + '\n')

        return jsonify({
            'content': processed_content,
            'status': 'success',
            'variables_processed': len(variables)
        })

    except Exception as e:
        print(f"Error in copy-prompt: {e}")
        return jsonify({'error': 'Failed to process prompt'}), 500


@app.route('/api/toggle-favorite', methods=['POST'])
def toggle_favorite():
    """Toggle favorite status of a prompt - FIXED VERSION"""
    try:
        data = request.get_json()
        prompt_id = data.get('prompt_id')

        if not prompt_id:
            return jsonify({'error': 'Missing prompt_id'}), 400

        print(f"Toggling favorite for prompt_id: {prompt_id}")  # Debug logging

        # Use the centralized finder function
        prompt_file = find_prompt_file(prompt_id)

        if not prompt_file:
            # Debug logging
            print(f"Prompt file not found for ID: {prompt_id}")
            # List available files for debugging
            available_files = list(PROMPTS_DIR.rglob('*.md'))
            print(
                f"Available files: {[str(f.relative_to(PROMPTS_DIR)) for f in available_files[:5]]}")
            return jsonify({'error': 'Prompt not found'}), 404

        print(f"Found prompt file: {prompt_file}")  # Debug logging

        # Read and update the prompt file
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1]) or {}
                    prompt_content = parts[2].strip()

                    # Toggle favorite status
                    current_favorite = metadata.get('favorite', False)
                    metadata['favorite'] = not current_favorite

                    # Update last_modified
                    metadata['last_modified'] = datetime.now().strftime(
                        '%Y-%m-%d')

                    # Write back to file
                    new_content = f"---\n{yaml.dump(metadata, default_flow_style=False)}---\n{prompt_content}"

                    with open(prompt_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)

                    # Debug logging
                    print(
                        f"Updated favorite status to: {metadata['favorite']}")

                    # Reload prompts to update the in-memory index
                    prompt_manager.load_prompts()

                    return jsonify({
                        'status': 'success',
                        'is_favorite': metadata['favorite']
                    })

                except yaml.YAMLError as e:
                    print(f"YAML parsing error: {e}")  # Debug logging
                    return jsonify({'error': f'YAML parsing error: {str(e)}'}), 500
            else:
                return jsonify({'error': 'Invalid file format'}), 400
        else:
            # Add frontmatter to file without it
            metadata = {
                'favorite': True,
                'last_modified': datetime.now().strftime('%Y-%m-%d')
            }

            new_content = f"---\n{yaml.dump(metadata, default_flow_style=False)}---\n{content}"

            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # Reload prompts to update the in-memory index
            prompt_manager.load_prompts()

            return jsonify({
                'status': 'success',
                'is_favorite': True
            })

    except Exception as e:
        print(f"Error toggling favorite: {e}")  # Debug logging
        import traceback
        traceback.print_exc()  # Print full traceback for debugging
        return jsonify({'error': 'Failed to toggle favorite'}), 500


@app.route('/api/test-ollama', methods=['POST'])
def test_ollama():
    """Test prompt with Ollama (Phase 2 feature)"""
    try:
        data = request.get_json()
        prompt_id = data.get('prompt_id')
        variables = data.get('variables', {})

        if not prompt_id:
            return jsonify({'error': 'Missing prompt_id'}), 400

        # Find and read the prompt
        prompt_file = None
        for root, dirs, files in os.walk(PROMPTS_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    relative_path = file_path.replace(
                        '\\', '/').replace('prompts/', '')
                    if relative_path == prompt_id:
                        prompt_file = file_path
                        break
            if prompt_file:
                break

        if not prompt_file:
            return jsonify({'error': 'Prompt not found'}), 404

        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse content
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                prompt_content = parts[2].strip()
            else:
                prompt_content = content
        else:
            prompt_content = content

        # Process variables
        processed_content = prompt_content
        if variables:
            for var_name, var_value in variables.items():
                placeholder = f'{{{var_name}}}'
                processed_content = processed_content.replace(
                    placeholder, var_value)

        # Test with Ollama
        import requests
        import time

        start_time = time.time()

        # Get Ollama configuration (you'll need to implement this)
        ollama_config = get_ollama_config()

        ollama_url = f"http://{ollama_config.get('host', 'localhost')}:{ollama_config.get('port', 11434)}/api/generate"

        payload = {
            "model": ollama_config.get('model', 'llama3.2:1b'),
            "prompt": processed_content,
            "stream": False,
            "options": ollama_config.get('options', {})
        }

        response = requests.post(
            ollama_url,
            json=payload,
            timeout=ollama_config.get('timeout', 120)
        )

        response_time = int((time.time() - start_time) * 1000)

        if response.status_code == 200:
            result = response.json()

            return jsonify({
                'status': 'success',
                'response': result.get('response', ''),
                'processed_prompt': processed_content,
                'model': payload['model'],
                'response_time': response_time,
                'variables_used': variables
            })
        else:
            return jsonify({
                'error': f'Ollama request failed: {response.status_code}',
                'details': response.text
            }), 500

    except requests.RequestException as e:
        return jsonify({
            'error': 'Failed to connect to Ollama',
            'details': str(e)
        }), 503
    except Exception as e:
        print(f"Error testing with Ollama: {e}")
        return jsonify({'error': 'Failed to test prompt'}), 500


def get_ollama_config():
    """Get Ollama configuration from config file or defaults"""
    config_path = 'config/ollama.json'

    default_config = {
        'host': 'localhost',
        'port': 11434,
        'model': 'llama3.2:1b',
        'timeout': 120,
        'options': {
            'temperature': 0.7,
            'num_predict': 1024,
            'num_ctx': 2048,
            'top_k': 20,
            'top_p': 0.8
        }
    }

    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except (json.JSONDecodeError, FileNotFoundError):
            pass

    return default_config


@app.route('/api/search-prompts')
def search_prompts():
    """Enhanced search API with filtering"""
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        tags = request.args.get('tags', '').strip()
        favorites_only = request.args.get('favorites', '').lower() == 'true'

        prompts = []

        # Walk through prompt files
        for root, dirs, files in os.walk(PROMPTS_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)

                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Parse metadata
                    metadata = {}
                    prompt_content = content

                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            try:
                                metadata = yaml.safe_load(parts[1]) or {}
                                prompt_content = parts[2].strip()
                            except yaml.YAMLError:
                                pass

                    # Apply filters
                    if favorites_only and not metadata.get('favorite', False):
                        continue

                    if category and metadata.get('category', '').lower() != category.lower():
                        continue

                    if tags:
                        prompt_tags = [tag.lower()
                                       for tag in metadata.get('tags', [])]
                        search_tags = [tag.strip().lower()
                                       for tag in tags.split(',')]
                        if not any(tag in prompt_tags for tag in search_tags):
                            continue

                    # Search in content and metadata
                    if query:
                        search_text = f"{metadata.get('title', '')} {prompt_content} {' '.join(metadata.get('tags', []))}".lower(
                        )
                        if query.lower() not in search_text:
                            continue

                    # Build prompt object
                    prompt = {
                        'id': file_path.replace('\\', '/').replace('prompts/', ''),
                        'filename': file,
                        'title': metadata.get('title', file.replace('.md', '')),
                        'category': metadata.get('category', 'uncategorized'),
                        'tags': metadata.get('tags', []),
                        'content': prompt_content,
                        'variables': metadata.get('variables', []),
                        'favorite': metadata.get('favorite', False),
                        'use_count': metadata.get('use_count', 0),
                        'last_used': metadata.get('last_used', ''),
                        'created': metadata.get('created', ''),
                        'file_path': file_path
                    }

                    prompts.append(prompt)

        # Sort by relevance, favorites, then usage
        def sort_key(p):
            score = 0
            if p['favorite']:
                score += 1000
            score += p['use_count'] * 10
            if query and query.lower() in p['title'].lower():
                score += 100
            return score

        prompts.sort(key=sort_key, reverse=True)

        return jsonify({
            PROMPTS_DIR: prompts,
            'total': len(prompts),
            'query': query,
            'filters': {
                'category': category,
                'tags': tags,
                'favorites_only': favorites_only
            }
        })

    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({'error': 'Search failed'}), 500


@app.route('/api/categories')
def get_categories():
    """Get all available categories with counts"""
    try:
        categories = {}

        for root, dirs, files in os.walk(PROMPTS_DIR):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)

                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    metadata = {}
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            try:
                                metadata = yaml.safe_load(parts[1]) or {}
                            except yaml.YAMLError:
                                pass

                    category = metadata.get('category', 'uncategorized')
                    categories[category] = categories.get(category, 0) + 1

        return jsonify({
            'categories': [
                {'name': name, 'count': count}
                for name, count in sorted(categories.items())
            ],
            'total_categories': len(categories)
        })

    except Exception as e:
        print(f"Categories error: {e}")
        return jsonify({'error': 'Failed to get categories'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=3001, host='0.0.0.0')
