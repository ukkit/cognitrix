#!/usr/bin/env python3
"""
fix_unclosed_braces_robust.py - Robust fix for unclosed variable braces
Actually fixes the content by adding missing closing braces
"""

import os
import re
from pathlib import Path

def fix_unclosed_braces_content(content):
    """Fix unclosed braces in content using multiple approaches"""
    
    original_content = content
    fixes_made = []
    
    # Approach 1: Fix {variable at end of line
    pattern1 = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\s*$'
    matches1 = list(re.finditer(pattern1, content, re.MULTILINE))
    for match in reversed(matches1):  # Reverse to avoid position shifts
        var_name = match.group(1)
        start = match.start()
        end = match.end()
        
        # Replace {variable with {variable}
        content = content[:start] + f'{{{var_name}}}' + content[end:]
        fixes_made.append(f"{var_name} (end of line)")
    
    # Approach 2: Fix {variable at end of content
    pattern2 = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\s*\Z'
    matches2 = list(re.finditer(pattern2, content))
    for match in reversed(matches2):
        var_name = match.group(1)
        start = match.start()
        end = match.end()
        
        content = content[:start] + f'{{{var_name}}}' + content[end:]
        fixes_made.append(f"{var_name} (end of content)")
    
    # Approach 3: Fix {variable followed by newline
    pattern3 = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\s*\n'
    matches3 = list(re.finditer(pattern3, content))
    for match in reversed(matches3):
        var_name = match.group(1)
        start = match.start()
        
        # Find the newline position
        newline_pos = content.find('\n', start)
        if newline_pos > start:
            # Replace content up to newline
            content = content[:start] + f'{{{var_name}}}' + content[newline_pos:]
            fixes_made.append(f"{var_name} (before newline)")
    
    # Approach 4: Fix {variable followed by space and non-word character
    pattern4 = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\s+([^a-zA-Z0-9_}])'
    matches4 = list(re.finditer(pattern4, content))
    for match in reversed(matches4):
        var_name = match.group(1)
        following_char = match.group(2)
        start = match.start()
        end = match.end()
        
        # Replace {variable following_char with {variable}following_char
        content = content[:start] + f'{{{var_name}}}{following_char}' + content[end:]
        fixes_made.append(f"{var_name} (before '{following_char}')")
    
    # Approach 5: Simple replacement of common patterns
    simple_patterns = [
        (r'\{text\s*(?=[^}])', r'{text}'),
        (r'\{code\s*(?=[^}])', r'{code}'),
        (r'\{input\s*(?=[^}])', r'{input}'),
        (r'\{output\s*(?=[^}])', r'{output}'),
        (r'\{question\s*(?=[^}])', r'{question}'),
        (r'\{answer\s*(?=[^}])', r'{answer}'),
        (r'\{topic\s*(?=[^}])', r'{topic}'),
        (r'\{context\s*(?=[^}])', r'{context}'),
        (r'\{language\s*(?=[^}])', r'{language}'),
        (r'\{variable\s*(?=[^}])', r'{variable}'),
    ]
    
    for pattern, replacement in simple_patterns:
        old_content = content
        content = re.sub(pattern, replacement, content)
        if content != old_content:
            var_name = pattern.split(r'\{')[1].split(r'\s')[0]
            fixes_made.append(f"{var_name} (simple pattern)")
    
    return content, fixes_made

def fix_prompt_file(file_path):
    """Fix unclosed braces in a single prompt file"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        return False, f"Error reading file: {e}"
    
    # Split frontmatter and content
    if original_content.startswith('---'):
        parts = original_content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1]
            prompt_content = parts[2]
            has_frontmatter = True
        else:
            return False, "Invalid frontmatter structure"
    else:
        frontmatter_text = ""
        prompt_content = original_content
        has_frontmatter = False
    
    # Fix the content
    fixed_content, fixes_made = fix_unclosed_braces_content(prompt_content)
    
    if not fixes_made:
        return False, "No unclosed braces found"
    
    # Reconstruct the file
    if has_frontmatter:
        new_content = f"---{frontmatter_text}---{fixed_content}"
    else:
        new_content = fixed_content
    
    # Only write if content actually changed
    if new_content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, f"Fixed: {', '.join(fixes_made)}"
        except Exception as e:
            return False, f"Error writing file: {e}"
    else:
        return False, "No changes made"

def preview_fixes(file_path):
    """Preview what fixes would be made without actually changing the file"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        return f"Error reading file: {e}"
    
    # Split frontmatter and content
    if original_content.startswith('---'):
        parts = original_content.split('---', 2)
        if len(parts) >= 3:
            prompt_content = parts[2]
        else:
            prompt_content = original_content
    else:
        prompt_content = original_content
    
    print(f"\n[PREVIEW] {file_path.name}")
    print("-" * 50)
    
    # Find potential issues
    unclosed_patterns = [
        r'\{([a-zA-Z_][a-zA-Z0-9_]*)\s*$',
        r'\{([a-zA-Z_][a-zA-Z0-9_]*)\s*\n',
        r'\{([a-zA-Z_][a-zA-Z0-9_]*)\s+[^a-zA-Z0-9_}]',
    ]
    
    found_issues = []
    for pattern in unclosed_patterns:
        matches = re.finditer(pattern, prompt_content, re.MULTILINE)
        for match in matches:
            var_name = match.group(1)
            context_start = max(0, match.start() - 20)
            context_end = min(len(prompt_content), match.end() + 20)
            context = prompt_content[context_start:context_end].replace('\n', '\\n')
            found_issues.append((var_name, context))
    
    if found_issues:
        print("UNCLOSED BRACES FOUND:")
        for i, (var_name, context) in enumerate(found_issues, 1):
            print(f"  {i}. Variable: {var_name}")
            print(f"     Context: ...{context}...")
            print()
    else:
        print("No unclosed braces found")
    
    # Preview the fix
    fixed_content, fixes_made = fix_unclosed_braces_content(prompt_content)
    
    if fixes_made:
        print("FIXES THAT WOULD BE MADE:")
        for fix in fixes_made:
            print(f"  - {fix}")
        print()
        
        # Show before/after for first few changes
        if len(prompt_content) < 1000:  # Only for small files
            print("CONTENT DIFF:")
            print("BEFORE:")
            print(prompt_content[:200] + "..." if len(prompt_content) > 200 else prompt_content)
            print("\nAFTER:")
            print(fixed_content[:200] + "..." if len(fixed_content) > 200 else fixed_content)
    else:
        print("No fixes would be made")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--preview":
            # Preview mode for all files
            prompts_dir = Path("prompts")
            for md_file in prompts_dir.rglob("*.md"):
                preview_fixes(md_file)
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
                preview_fixes(target_file)
            else:
                print(f"[ERROR] File '{filename}' not found")
    
    else:
        # Fix all files
        prompts_dir = Path("prompts")
        
        if not prompts_dir.exists():
            print("[ERROR] Prompts directory not found")
            return
        
        print("[INFO] Fixing unclosed variable braces...")
        print(f"[INFO] Directory: {prompts_dir.absolute()}")
        print()
        
        fixed = 0
        total = 0
        
        for md_file in prompts_dir.rglob("*.md"):
            total += 1
            
            success, message = fix_prompt_file(md_file)
            
            if success:
                fixed += 1
                print(f"[FIXED] {md_file.name}: {message}")
            elif "No unclosed braces" not in message and "No changes made" not in message:
                print(f"[ERROR] {md_file.name}: {message}")
        
        print(f"\n[SUMMARY] Fix completed:")
        print(f"[SUMMARY] Total files: {total}")
        print(f"[SUMMARY] Files fixed: {fixed}")
        
        if fixed > 0:
            print(f"\n[SUCCESS] Fixed unclosed braces in {fixed} files!")
            print("[INFO] Please restart Cognitrix to see the changes.")
        else:
            print("\n[INFO] No files needed fixing.")

if __name__ == "__main__":
    main()