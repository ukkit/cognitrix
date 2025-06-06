#!/usr/bin/env python3
"""
debug_variables.py - Debug Cognitrix variables display issues
Find the exact cause of the "</> Variables: {text:" problem
"""

import os
import re
import yaml
from pathlib import Path

def analyze_prompt_file(file_path):
    """Analyze a single prompt file for variables issues"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    analysis = {
        'file': file_path.name,
        'has_frontmatter': False,
        'frontmatter_valid': False,
        'variables_field': None,
        'variables_type': None,
        'variables_content': None,
        'content_variables': [],
        'issue_found': False,
        'issue_description': None
    }
    
    # Check for frontmatter
    if content.startswith('---'):
        analysis['has_frontmatter'] = True
        parts = content.split('---', 2)
        
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                prompt_content = parts[2].strip()
                analysis['frontmatter_valid'] = True
                
                # Analyze variables field
                if 'variables' in frontmatter:
                    variables = frontmatter['variables']
                    analysis['variables_field'] = True
                    analysis['variables_type'] = type(variables).__name__
                    analysis['variables_content'] = str(variables)[:100]  # First 100 chars
                    
                    # Check for issues
                    if isinstance(variables, str):
                        if '{' in variables or ':' in variables or variables.startswith('</'):
                            analysis['issue_found'] = True
                            analysis['issue_description'] = f"Variables is malformed string: {variables}"
                    
                    elif isinstance(variables, dict):
                        analysis['issue_found'] = True
                        analysis['issue_description'] = f"Variables is dict instead of list: {variables}"
                    
                    elif not isinstance(variables, list):
                        analysis['issue_found'] = True
                        analysis['issue_description'] = f"Variables is {type(variables).__name__} instead of list"
                
                else:
                    analysis['variables_field'] = False
                
                # Find variables in content
                content_vars = re.findall(r'\{([^}]+)\}', prompt_content)
                analysis['content_variables'] = list(set(content_vars))
                
                # Check if content has variables but frontmatter doesn't
                if content_vars and not analysis['variables_field']:
                    analysis['issue_found'] = True
                    analysis['issue_description'] = f"Content has variables {content_vars} but no variables field in frontmatter"
                
            except yaml.YAMLError as e:
                analysis['frontmatter_valid'] = False
                analysis['issue_found'] = True
                analysis['issue_description'] = f"YAML parsing error: {e}"
    
    return analysis

def find_problem_files():
    """Find all files with variables display issues"""
    
    prompts_dir = Path("prompts")
    
    if not prompts_dir.exists():
        print("[ERROR] Prompts directory not found")
        return
    
    print("[INFO] Analyzing Cognitrix prompt files for variables issues...")
    print(f"[INFO] Scanning directory: {prompts_dir.absolute()}")
    print()
    
    problem_files = []
    total_files = 0
    files_with_variables = 0
    
    for md_file in prompts_dir.rglob("*.md"):
        total_files += 1
        analysis = analyze_prompt_file(md_file)
        
        if analysis['variables_field']:
            files_with_variables += 1
        
        if analysis['issue_found']:
            problem_files.append(analysis)
            print(f"[PROBLEM] {analysis['file']}")
            try:
                issue_desc = analysis['issue_description'].encode('ascii', 'ignore').decode('ascii')
                var_content = analysis['variables_content'].encode('ascii', 'ignore').decode('ascii')
                print(f"          Issue: {issue_desc}")
                print(f"          Variables type: {analysis['variables_type']}")
                print(f"          Variables content: {var_content}")
            except:
                print(f"          Issue: [contains special characters]")
                print(f"          Variables type: {analysis['variables_type']}")
                print(f"          Variables content: [special characters]")
            print()
        
        elif analysis['variables_field']:
            # Safe printing for Windows
            try:
                var_content = analysis['variables_content']
                # Ensure ASCII-safe output
                var_content = var_content.encode('ascii', 'ignore').decode('ascii')
                print(f"[OK] {analysis['file']} - Variables: {var_content}")
            except:
                print(f"[OK] {analysis['file']} - Variables: [contains special characters]")
    
    print(f"\n[SUMMARY] Analysis completed:")
    print(f"[SUMMARY] Total files: {total_files}")
    print(f"[SUMMARY] Files with variables: {files_with_variables}")
    print(f"[SUMMARY] Problem files: {len(problem_files)}")
    
    if problem_files:
        print(f"\n[ACTION] Found {len(problem_files)} files with issues!")
        print("[ACTION] These files need manual inspection:")
        for analysis in problem_files:
            print(f"         - {analysis['file']}: {analysis['issue_description']}")
    else:
        print(f"\n[INFO] No obvious YAML issues found.")
        print("[INFO] The problem might be in:")
        print("[INFO] 1. Template rendering (check browser developer tools)")
        print("[INFO] 2. Flask backend processing")
        print("[INFO] 3. Specific prompt content formatting")
    
    return problem_files

def check_specific_prompt(filename):
    """Check a specific prompt file in detail"""
    
    prompts_dir = Path("prompts")
    
    # Find the file
    target_file = None
    for md_file in prompts_dir.rglob("*.md"):
        if md_file.name == filename or md_file.stem == filename:
            target_file = md_file
            break
    
    if not target_file:
        print(f"[ERROR] File '{filename}' not found")
        return
    
    print(f"[INFO] Detailed analysis of: {target_file}")
    print("-" * 50)
    
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("[RAW CONTENT]")
    print(content[:500])
    print("..." if len(content) > 500 else "")
    print()
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            print("[FRONTMATTER]")
            print(parts[1])
            print()
            
            try:
                frontmatter = yaml.safe_load(parts[1])
                print("[PARSED FRONTMATTER]")
                for key, value in frontmatter.items():
                    print(f"  {key}: {value} (type: {type(value).__name__})")
                print()
                
                if 'variables' in frontmatter:
                    print("[VARIABLES ANALYSIS]")
                    variables = frontmatter['variables']
                    print(f"  Type: {type(variables).__name__}")
                    print(f"  Value: {repr(variables)}")
                    print(f"  Length: {len(variables) if hasattr(variables, '__len__') else 'N/A'}")
                    
                    if isinstance(variables, str):
                        print(f"  Contains '{{': {'{{' in variables}")
                        print(f"  Contains ':': {':' in variables}")
                        print(f"  Starts with '</': {variables.startswith('</')}")
                
            except Exception as e:
                print(f"[ERROR] Failed to parse frontmatter: {e}")

def main():
    """Main debug function"""
    import sys
    
    if len(sys.argv) > 1:
        # Check specific file
        filename = sys.argv[1]
        check_specific_prompt(filename)
    else:
        # Find all problem files
        find_problem_files()

if __name__ == "__main__":
    main()