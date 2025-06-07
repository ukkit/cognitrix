#!/usr/bin/env python3
"""
Cognitrix Auto-Categorization Module
Intelligent prompt categorization using local LLM via Ollama
Now uses unified config.json instead of separate configuration files
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
    def __init__(self, config_path=None):
        """
        Initialize the auto-categorization system

        Args:
            config_path: Path to unified configuration file (optional)
        """
        self.prompts_dir = Path("prompts")
        self.cache_file = Path("cache/categorization_cache.json")

        # Use unified config.json instead of separate files
        self.config_file = Path(config_path) if config_path else Path(
            "config/config.json")

        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Load unified configuration
        self.config = self._load_config()

        # Extract relevant sections from unified config
        self.ollama_config = self.config.get('ollama', {})
        self.categorization_config = self.config.get('categorization', {})

        # Set Ollama connection details from unified config
        self.ollama_url = f"http://{self.ollama_config.get('host', 'localhost')}:{self.ollama_config.get('port', 11434)}"
        self.model = self.categorization_config.get(
            'model', self.ollama_config.get('default_model', 'llama3.2:1b'))
        self.timeout = self.ollama_config.get('timeout', 30)
        self.connect_timeout = self.ollama_config.get('connect_timeout', 10)

        # Load categorization cache
        self.cache = self._load_cache()

        # Get category keywords from unified config or use defaults
        self.category_keywords = self.categorization_config.get(
            'categories', self._get_default_categories())

    def _get_default_categories(self):
        """Default category keywords if not specified in config"""
        return {
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
        """Load unified configuration from config.json"""
        default_config = {
            "ollama": {
                "host": "localhost",
                "port": 11434,
                "enabled": True,
                "timeout": 30,
                "connect_timeout": 10,
                "default_model": "llama3.2:1b",
                "model_options": {
                    "temperature": 0.1,
                    "num_predict": 50,
                    "top_p": 0.9,
                    "top_k": 40
                }
            },
            "categorization": {
                "enabled": True,
                "model": "llama3.2:1b",
                "confidence_threshold": 0.7,
                "use_llm_categorization": True,
                "use_keyword_fallback": True,
                "auto_approve_high_confidence": True,
                "batch_size": 10,
                "max_retries": 3,
                "retry_delay": 5
            },
            "storage": {
                "cache_dir": "cache",
                "logs_dir": "logs"
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults, preserving existing values
                    merged_config = self._deep_merge(default_config, config)
                    return merged_config
            except (json.JSONDecodeError, FileNotFoundError) as e:
                self.logger.warning(
                    f"Error loading config file: {e}. Using defaults.")
                return default_config
        else:
            # Create default config file
            self.config_file.parent.mkdir(exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            self.logger.info(
                f"Created default config file: {self.config_file}")
            return default_config

    def _deep_merge(self, base, override):
        """Deep merge two dictionaries"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _load_cache(self):
        """Load categorization cache"""
        cache_dir = self.config.get('storage', {}).get('cache_dir', 'cache')
        cache_file = Path(cache_dir) / "categorization_cache.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}

    def _save_cache(self):
        """Save categorization cache"""
        cache_dir = self.config.get('storage', {}).get('cache_dir', 'cache')
        cache_file = Path(cache_dir) / "categorization_cache.json"
        cache_file.parent.mkdir(exist_ok=True)

        with open(cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def _calculate_content_hash(self, content):
        """Calculate hash of prompt content for caching"""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()

    def _extract_variables_from_content(self, content):
        """Extract variable placeholders from prompt content"""
        variables = re.findall(r'\{([^}]+)\}', content)
        return sorted(list(set(variables)))

    def _generate_tags_from_content(self, content, category):
        """Generate relevant tags based on content and category"""
        content_lower = content.lower()

        # Base tags from category
        category_base_tags = {
            "coding": ["programming", "development"],
            "writing": ["content", "text"],
            "analysis": ["research", "data"],
            "business": ["strategy", "planning"],
            "education": ["learning", "tutorial"],
            "creative": ["brainstorming", "ideas"],
            "technical": ["documentation", "systems"],
            "communication": ["messaging", "social"],
            "productivity": ["workflow", "organization"],
            "general": ["assistant", "helper"]
        }

        tags = category_base_tags.get(category, ["general"])

        # Add specific technology/topic tags based on keywords
        tech_keywords = {
            "python": "python",
            "javascript": "javascript",
            "react": "react",
            "html": "html",
            "css": "css",
            "sql": "sql",
            "api": "api",
            "database": "database",
            "email": "email",
            "blog": "blog",
            "article": "article",
            "story": "story",
            "poem": "poem",
            "code review": "review",
            "debug": "debugging",
            "test": "testing",
            "documentation": "docs",
            "tutorial": "tutorial",
            "explain": "explanation",
            "analyze": "analysis",
            "compare": "comparison",
            "research": "research",
            "report": "reporting",
            "plan": "planning",
            "strategy": "strategy",
            "meeting": "meetings",
            "proposal": "proposals",
            "design": "design",
            "creative": "creativity",
            "brainstorm": "brainstorming"
        }

        for keyword, tag in tech_keywords.items():
            if keyword in content_lower and tag not in tags:
                tags.append(tag)

        return tags[:5]

    def _generate_title_from_content(self, content, filename):
        """Generate a descriptive title from prompt content"""
        lines = content.strip().split('\n')
        first_line = lines[0].strip()

        if len(first_line) < 80 and not first_line.startswith(('You are', 'Act as', 'Write', 'Create', 'Generate')):
            if first_line.endswith('.'):
                first_line = first_line[:-1]
            return first_line.title()

        # Extract title patterns from content
        title_patterns = [
            r'(?:create|write|generate|build|make)\s+(?:a|an)?\s*([^.!?\n]+)',
            r'(?:you are|act as)\s+(?:a|an)?\s*([^.!?\n]+)',
            r'help.*?(?:with|for)\s+([^.!?\n]+)',
            r'assist.*?(?:with|in|for)\s+([^.!?\n]+)',
            r'(?:please|can you)\s+([^.!?\n]+)',
        ]

        for pattern in title_patterns:
            match = re.search(pattern, content.lower())
            if match:
                title = match.group(1).strip()
                if len(title) > 10 and len(title) < 60:
                    return title.title()

        # Fallback: clean up filename
        title = filename.replace('_', ' ').replace('-', ' ')
        title = re.sub(r'\.md$', '', title)
        return title.title()

    def _detect_prompt_type(self, content):
        """Detect if prompt has variables and what type it is"""
        variables = self._extract_variables_from_content(content)

        if variables:
            return "template"
        elif any(keyword in content.lower() for keyword in ["step by step", "workflow", "process", "first", "then", "next"]):
            return "workflow"
        else:
            return "simple"

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
            confidence = min(category_scores[best_category] * 2, 0.9)
            return best_category, confidence

        return "general", 0.1

    def llm_categorize(self, content):
        """Use LLM for intelligent categorization"""
        if not self.ollama_config.get('enabled', True):
            return None, 0.0

        categories_list = ", ".join(self.category_keywords.keys())
        system_prompt = self.categorization_config.get('system_prompt',
                                                       "You are an expert at categorizing text prompts. Analyze the prompt and respond with only the most appropriate category name from the provided list.")

        categorization_prompt = f"""{system_prompt}

Categories: {categories_list}

Prompt to categorize:
{content[:500]}...

Respond with only the category name from the list above."""

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": categorization_prompt,
                    "stream": False,
                    "options": self.ollama_config.get('model_options', {})
                },
                timeout=self.timeout,
                headers={'Connection': 'close'}
            )

            if response.status_code == 200:
                result = response.json()
                category = result["response"].strip().lower()

                if category in self.category_keywords:
                    return category, 0.9
                else:
                    for valid_cat in self.category_keywords:
                        if valid_cat in category or category in valid_cat:
                            return valid_cat, 0.7

                    self.logger.warning(
                        f"LLM returned invalid category: {category}")
                    return None, 0.0
            else:
                self.logger.error(f"Ollama API error: {response.status_code}")
                return None, 0.0

        except Exception as e:
            self.logger.error(f"LLM categorization failed: {e}")
            return None, 0.0

    def categorize_prompt(self, content, title=""):
        """Categorize a single prompt with caching"""
        content_hash = self._calculate_content_hash(content)
        if content_hash in self.cache:
            cached = self.cache[content_hash]
            return cached["category"], cached["confidence"], True

        full_content = f"{title}\n\n{content}" if title else content

        # Try LLM categorization first if enabled
        if self.categorization_config.get("use_llm_categorization", True):
            category, confidence = self.llm_categorize(full_content)

            if category and confidence >= self.categorization_config.get("confidence_threshold", 0.7):
                self.cache[content_hash] = {
                    "category": category,
                    "confidence": confidence,
                    "method": "llm",
                    "timestamp": datetime.now().isoformat()
                }
                self._save_cache()
                return category, confidence, False

        # Fallback to keyword categorization
        if self.categorization_config.get("use_keyword_fallback", True):
            category, confidence = self.keyword_categorize(full_content)

            self.cache[content_hash] = {
                "category": category,
                "confidence": confidence,
                "method": "keyword",
                "timestamp": datetime.now().isoformat()
            }
            self._save_cache()
            return category, confidence, False

        return "general", 0.1, False

    def _create_complete_frontmatter(self, content, filename, existing_metadata=None):
        """Create complete YAML frontmatter with all standard Cognitrix fields"""
        metadata = existing_metadata.copy() if existing_metadata else {}

        if not metadata.get('title'):
            metadata['title'] = self._generate_title_from_content(
                content, filename)

        category, confidence, from_cache = self.categorize_prompt(
            content, metadata.get('title', ''))
        metadata['category'] = category

        if not metadata.get('tags'):
            metadata['tags'] = self._generate_tags_from_content(
                content, category)
        else:
            generated_tags = self._generate_tags_from_content(
                content, category)
            existing_tags = metadata['tags'] if isinstance(
                metadata['tags'], list) else []
            all_tags = list(set(existing_tags + generated_tags))
            metadata['tags'] = sorted(all_tags)[:5]

        variables = self._extract_variables_from_content(content)
        if variables:
            metadata['variables'] = variables
        elif 'variables' in metadata and not variables:
            del metadata['variables']

        metadata['type'] = self._detect_prompt_type(content)

        if not metadata.get('created'):
            metadata['created'] = datetime.now().strftime('%Y-%m-%d')

        if not metadata.get('favorite'):
            metadata['favorite'] = False

        if 'last_used' not in metadata:
            metadata['last_used'] = None
        if 'use_count' not in metadata:
            metadata['use_count'] = 0

        if not from_cache:
            metadata['auto_categorized'] = datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S')
            metadata['categorization_confidence'] = round(confidence, 2)

        # Order fields for consistent output
        ordered_fields = [
            'title', 'category', 'type', 'tags', 'variables', 'favorite',
            'created', 'last_used', 'use_count', 'auto_categorized',
            'categorization_confidence'
        ]

        ordered_metadata = {}
        for field in ordered_fields:
            if field in metadata and metadata[field] is not None:
                ordered_metadata[field] = metadata[field]

        for key, value in metadata.items():
            if key not in ordered_metadata:
                ordered_metadata[key] = value

        return ordered_metadata, category, confidence, from_cache

    def process_prompt_file(self, file_path):
        """Process a single prompt file and normalize its format"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    prompt_content = parts[2].strip()

                    try:
                        existing_metadata = yaml.safe_load(frontmatter) or {}
                    except:
                        existing_metadata = {}
                else:
                    existing_metadata = {}
                    prompt_content = content
            else:
                existing_metadata = {}
                prompt_content = content.strip()

            if (existing_metadata.get('category') and
                not getattr(self, 'force_recategorize', False) and
                existing_metadata.get('title') and
                    existing_metadata.get('tags')):
                return existing_metadata.get('category'), 1.0, True, "existing"

            complete_metadata, category, confidence, from_cache = self._create_complete_frontmatter(
                prompt_content, file_path.stem, existing_metadata
            )

            new_frontmatter = yaml.dump(
                complete_metadata, default_flow_style=False, sort_keys=False)
            new_content = f"---\n{new_frontmatter}---\n\n{prompt_content}"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            updates = []
            if not existing_metadata.get('title'):
                updates.append("title")
            if not existing_metadata.get('category'):
                updates.append("category")
            if not existing_metadata.get('tags'):
                updates.append("tags")
            if complete_metadata.get('variables') and not existing_metadata.get('variables'):
                updates.append("variables")
            if not existing_metadata.get('type'):
                updates.append("type")

            if updates:
                self.logger.info(
                    f"Updated {file_path.name}: {', '.join(updates)}")

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
            "categories": {},
            "fields_updated": {}
        }

        for i, file_path in enumerate(prompt_files, 1):
            self.logger.info(
                f"Processing ({i}/{len(prompt_files)}): {file_path.name}")

            category, confidence, from_cache, status = self.process_prompt_file(
                file_path)

            results["processed"] += 1
            results["categories"][category] = results["categories"].get(
                category, 0) + 1

            if status == "updated":
                results["updated"] += 1
            elif status == "existing":
                results["existing"] += 1
            elif status == "error":
                results["errors"] += 1

            if from_cache:
                results["cached"] += 1

            self._organize_by_category(file_path, category)

        self._print_summary(results)
        return results

    def _organize_by_category(self, file_path, category):
        """Move prompt file to appropriate category directory"""
        category_dir = self.prompts_dir / category
        category_dir.mkdir(exist_ok=True)

        if file_path.parent.name != category:
            new_path = category_dir / file_path.name

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

        if results.get('fields_updated'):
            print(f"\nFields updated:")
            for field, count in results['fields_updated'].items():
                print(f"  {field}: {count} files")

        print("\nCategory distribution:")
        for category, count in sorted(results['categories'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: {count}")
        print("="*60)

    def analyze_categories(self):
        """Analyze current category distribution"""
        if not self.prompts_dir.exists():
            return

        categories = Counter()
        total_prompts = 0

        for md_file in self.prompts_dir.rglob("*.md"):
            total_prompts += 1
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 3:
                        metadata = yaml.safe_load(parts[1]) or {}
                        category = metadata.get('category', 'uncategorized')
                        categories[category] += 1
                    else:
                        categories['uncategorized'] += 1
                else:
                    categories['uncategorized'] += 1
            except:
                categories['error'] += 1

        print(f"\nCategory Analysis ({total_prompts} total prompts):")
        print("-" * 40)
        for category, count in categories.most_common():
            percentage = (count / total_prompts) * 100
            print(f"{category:15} {count:4} ({percentage:5.1f}%)")


def main():
    """Main CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Cognitrix Auto-Categorization")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--model", help="Override Ollama model")
    parser.add_argument("--host", help="Override Ollama host")
    parser.add_argument("--port", type=int, help="Override Ollama port")
    parser.add_argument("--force", action="store_true",
                        help="Force recategorization")
    parser.add_argument("--analyze", action="store_true",
                        help="Just analyze current categories")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without making changes")

    args = parser.parse_args()

    categorizer = PromptCategorizer(config_path=args.config)

    # Override config with command line arguments
    if args.model:
        categorizer.model = args.model
        categorizer.categorization_config['model'] = args.model
    if args.host:
        categorizer.ollama_config['host'] = args.host
        categorizer.ollama_url = f"http://{args.host}:{categorizer.ollama_config['port']}"
    if args.port:
        categorizer.ollama_config['port'] = args.port
        categorizer.ollama_url = f"http://{categorizer.ollama_config['host']}:{args.port}"

    if args.dry_run:
        print("[SCAN] DRY RUN MODE - No changes will be made")
        # Use only keywords for dry run
        categorizer.categorization_config["use_llm_categorization"] = False

    if args.analyze:
        categorizer.analyze_categories()
    else:
        print(f"[AI] Connecting to Ollama at: {categorizer.ollama_url}")
        print(f"[AI] Using model: {categorizer.model}")
        categorizer.categorize_all_prompts(force_recategorize=args.force)


if __name__ == "__main__":
    main()
