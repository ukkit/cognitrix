#!/usr/bin/env python3
"""
repair_variables.py - Fix malformed variables in Cognitrix prompt files
Windows-compatible version without Unicode emojis
"""

import os
import re
import yaml
from pathlib import Path


def repair_prompt_file(file_path):
    """Repair malformed variables in a single prompt file"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.startswith('---'):
        return False, "No frontmatter"

    parts = content.split('---', 2)
    if len(parts) < 3:
        return False, "Invalid frontmatter structure"

    try:
        # Try to load existing frontmatter
        frontmatter = yaml.safe_load(parts[1])
        prompt_content = parts[2].strip()

        if not frontmatter:
            return False, "Empty frontmatter"

        # Check if variables field needs repair
        if 'variables' in frontmatter:
            variables = frontmatter['variables']

            if isinstance(variables, str) and ('{' in variables or ':' in variables):
                print(
                    f"[REPAIR] Fixing variables in {file_path.name}: {variables}")

                # Extract variable names from malformed format
                extracted = re.findall(r'(\w+):', variables)
                if extracted:
                    frontmatter['variables'] = extracted
                else:
                    # Try to extract from {variable} format in content
                    content_vars = re.findall(r'\{([^}]+)\}', prompt_content)
                    frontmatter['variables'] = sorted(list(set(content_vars)))

                # Write back to file
                new_frontmatter = yaml.dump(
                    frontmatter, default_flow_style=False, sort_keys=False)
                new_content = f"---\n{new_frontmatter}---\n\n{prompt_content}"

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                return True, f"Fixed variables: {frontmatter['variables']}"

            elif not isinstance(variables, list):
                print(
                    f"[REPAIR] Converting non-list variables in {file_path.name}")

                # Convert to list if it's not already
                if isinstance(variables, str):
                    frontmatter['variables'] = [
                        variables] if variables.strip() else []
                else:
                    # Extract from content as fallback
                    content_vars = re.findall(r'\{([^}]+)\}', prompt_content)
                    frontmatter['variables'] = sorted(list(set(content_vars)))

                # Write back to file
                new_frontmatter = yaml.dump(
                    frontmatter, default_flow_style=False, sort_keys=False)
                new_content = f"---\n{new_frontmatter}---\n\n{prompt_content}"

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                return True, f"Converted to list: {frontmatter['variables']}"

        # If no variables field but variables exist in content, add them
        elif '{' in prompt_content and '}' in prompt_content:
            content_vars = re.findall(r'\{([^}]+)\}', prompt_content)
            if content_vars:
                frontmatter['variables'] = sorted(list(set(content_vars)))

                # Write back to file
                new_frontmatter = yaml.dump(
                    frontmatter, default_flow_style=False, sort_keys=False)
                new_content = f"---\n{new_frontmatter}---\n\n{prompt_content}"

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                return True, f"Added missing variables: {frontmatter['variables']}"

        return False, "No repair needed"

    except yaml.YAMLError as e:
        return False, f"YAML Error: {e}"
    except Exception as e:
        return False, f"Error: {e}"


def main():
    """Repair all prompt files in the prompts directory"""
    prompts_dir = Path("prompts")

    if not prompts_dir.exists():
        print("[ERROR] Prompts directory not found")
        return

    print("[INFO] Starting repair of Cognitrix prompt files...")
    print(f"[INFO] Scanning directory: {prompts_dir.absolute()}")

    repaired = 0
    total = 0
    errors = 0

    for md_file in prompts_dir.rglob("*.md"):
        total += 1
        success, message = repair_prompt_file(md_file)

        if success:
            repaired += 1
            print(f"[OK] {md_file.name}: {message}")
        elif "No repair needed" not in message:
            errors += 1
            print(f"[ERROR] {md_file.name}: {message}")
        else:
            print(f"[SKIP] {md_file.name}: {message}")

    print(f"\n[SUMMARY] Repair completed:")
    print(f"[SUMMARY] Total files: {total}")
    print(f"[SUMMARY] Repaired: {repaired}")
    print(f"[SUMMARY] Errors: {errors}")
    print(f"[SUMMARY] Skipped: {total - repaired - errors}")

    if repaired > 0:
        print(f"\n[SUCCESS] {repaired} files were repaired successfully!")
        print("[INFO] Please restart Cognitrix to see the changes:")
        print("[INFO] ./cognitrix-manager.sh restart")
    else:
        print("\n[INFO] No files needed repair.")


if __name__ == "__main__":
    main()
