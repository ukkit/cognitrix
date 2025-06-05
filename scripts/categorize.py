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
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--model", help="Override Ollama model")
    parser.add_argument("--host", help="Override Ollama host")
    parser.add_argument("--port", type=int, help="Override Ollama port")
    parser.add_argument("--force", action="store_true", help="Force recategorization")
    parser.add_argument("--analyze", action="store_true", help="Just analyze current categories")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    
    args = parser.parse_args()
    
    categorizer = PromptCategorizer(config_path=args.config)
    
    # Override config with command line arguments
    if args.model:
        categorizer.model = args.model
        categorizer.config['ollama']['model'] = args.model
    if args.host:
        categorizer.config['ollama']['host'] = args.host
        categorizer.ollama_url = f"http://{args.host}:{categorizer.config['ollama']['port']}"
    if args.port:
        categorizer.config['ollama']['port'] = args.port
        categorizer.ollama_url = f"http://{categorizer.config['ollama']['host']}:{args.port}"
    
    if args.dry_run:
        print("[SCAN] DRY RUN MODE - No changes will be made")
        categorizer.config["categorization"]["use_llm_categorization"] = False  # Use only keywords for dry run
    
    if args.analyze:
        print("[STATS] Analyzing current categories...")
        categorizer.analyze_categories()
    else:
        print(f"[AI] Connecting to Ollama at: {categorizer.ollama_url}")
        print(f"[AI] Using model: {categorizer.model}")
        categorizer.categorize_all_prompts(force_recategorize=args.force)

if __name__ == "__main__":
    main()
