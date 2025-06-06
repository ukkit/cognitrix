#!/usr/bin/env python3
"""
fix_yaml_variables.py - Fix malformed variables in YAML frontmatter
Specifically fixes cases like variables: ['{text'] to variables: ['text']
"""

import os
import re
import yaml
from pathlib import Path

def fix_yaml_variables(file_path):
    """Fix malformed variables in YAML frontmatter"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        return False, f"Error reading file: {e}"
    
    if not original_content.startswith('---'):
        return False, "No frontmatter found"
    
    parts = original_content.split('---', 2)
    if len(parts) < 3:
        return False, "Invalid frontmatter structure"
    
    frontmatter_text = parts[1]
    prompt_content = parts[2]
    
    try:
        # Parse the YAML
        frontmatter = yaml.safe_load(frontmatter_text)
        if not frontmatter:
            return False, "Empty frontmatter"
        
        # Check if variables field exists and needs fixing
        if 'variables' not in frontmatter:
            return False, "No variables field"
        
        variables = frontmatter['variables']
        original_variables = variables.copy() if isinstance(variables, list) else variables
        fixes_made = []
        
        # Fix malformed variables
        if isinstance(variables, list):
            fixed_variables = []
            for var in variables:
                if isinstance(var, str):
                    # Fix unclosed braces in variable names
                    if var.startswith('{') and not var.endswith('}'):
                        # Remove opening brace and any trailing characters
                        clean_var = var.lstrip('{').rstrip(':').strip()
                        fixed_variables.append(clean_var)
                        fixes_made.append(f"'{var}' -> '{clean_var}'")
                    elif var.startswith('{') and var.endswith('}'):
                        # Remove both braces - variables should just be names
                        clean_var = var.strip('{}')
                        fixed_variables.append(clean_var)
                        fixes_made.append(f"'{var}' -> '{clean_var}'")
                    else:
                        # Keep as-is if already clean
                        fixed_variables.append(var)
                else:
                    # Non-string variables, keep as-is
                    fixed_variables.append(var)
            
            if fixes_made:
                frontmatter['variables'] = fixed_variables
        
        elif isinstance(variables, str):
            # Handle case where variables is a single string
            if variables.startswith('{') and not variables.endswith('}'):
                clean_var = variables.lstrip('{').rstrip(':').strip()
                frontmatter['variables'] = [clean_var]
                fixes_made.append(f"String '{variables}' -> List ['{clean_var}']")
            elif variables.startswith('{') and variables.endswith('}'):
                clean_var = variables.strip('{}')
                frontmatter['variables'] = [clean_var]
                fixes_made.append(f"String '{variables}' -> List ['{clean_var}']")
        
        if not fixes_made:
            return False, "No fixes needed"
        
        # Write back the fixed YAML
        try:
            new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            new_content = f"---\n{new_frontmatter}---{prompt_content}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True, f"Fixed variables: {', '.join(fixes_made)}"
            
        except Exception as e:
            return False, f"Error writing file: {e}"
    
    except yaml.YAMLError as e:
        return False, f"YAML parsing error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

def preview_yaml_fixes(file_path):
    """Preview what YAML fixes would be made"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    print(f"\n[PREVIEW] {file_path.name}")
    print("-" * 50)
    
    if not content.startswith('---'):
        print("No frontmatter found")
        return
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        print("Invalid frontmatter structure")
        return
    
    frontmatter_text = parts[1]
    
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        
        if 'variables' in frontmatter:
            variables = frontmatter['variables']
            print(f"Current variables: {variables}")
            print(f"Variables type: {type(variables).__name__}")
            
            # Check what would be fixed
            issues_found = []
            
            if isinstance(variables, list):
                for var in variables:
                    if isinstance(var, str):
                        if var.startswith('{') and not var.endswith('}'):
                            clean_var = var.lstrip('{').rstrip(':').strip()
                            issues_found.append(f"'{var}' -> '{clean_var}'")
                        elif var.startswith('{') and var.endswith('}'):
                            clean_var = var.strip('{}')
                            issues_found.append(f"'{var}' -> '{clean_var}'")
            
            elif isinstance(variables, str):
                if variables.startswith('{'):
                    clean_var = variables.lstrip('{').rstrip(':').strip()
                    issues_found.append(f"String '{variables}' -> List ['{clean_var}']")
            
            if issues_found:
                print("FIXES THAT WOULD BE MADE:")
                for issue in issues_found:
                    print(f"  - {issue}")
            else:
                print("No fixes needed")
        else:
            print("No variables field found")
    
    except yaml.YAMLError as e:
        print(f"YAML parsing error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--preview":
            # Preview mode for all files
            prompts_dir = Path("prompts")
            if not prompts_dir.exists():
                print("[ERROR] Prompts directory not found")
                return
                
            for md_file in prompts_dir.rglob("*.md"):
                preview_yaml_fixes(md_file)
        else:
            # Check specific file
            filename = sys.argv[1]
            prompts_dir = Path("prompts")
            
            target_file = None
            for md_file in prompts_dir.rglob("*.md"):
                if md_file.name == filename or md_file.stem == filename:
                    target_file = md_file
                    break
            
            if target_file:
                preview_yaml_fixes(target_file)
            else:
                print(f"[ERROR] File '{filename}' not found")
    
    else:
        # Fix all files
        prompts_dir = Path("prompts")
        
        if not prompts_dir.exists():
            print("[ERROR] Prompts directory not found")
            return
        
        print("[INFO] Fixing YAML variables fields...")
        print(f"[INFO] Directory: {prompts_dir.absolute()}")
        print()
        
        fixed = 0
        total = 0
        
        for md_file in prompts_dir.rglob("*.md"):
            total += 1
            
            success, message = fix_yaml_variables(md_file)
            
            if success:
                fixed += 1
                print(f"[FIXED] {md_file.name}: {message}")
            elif "No fixes needed" not in message and "No variables field" not in message:
                print(f"[ERROR] {md_file.name}: {message}")
        
        print(f"\n[SUMMARY] Fix completed:")
        print(f"[SUMMARY] Total files: {total}")
        print(f"[SUMMARY] Files fixed: {fixed}")
        
        if fixed > 0:
            print(f"\n[SUCCESS] Fixed YAML variables in {fixed} files!")
            print("[INFO] Please restart Cognitrix to see the changes.")
        else:
            print("\n[INFO] No files needed fixing.")

if __name__ == "__main__":
    main()