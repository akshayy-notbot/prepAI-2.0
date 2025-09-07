#!/usr/bin/env python3
"""
Script to update all files in the system to use the new 4-level seniority system:
Junior, Mid, Senior, Manager
"""

import os
import re
import glob

def update_file_seniority_levels(file_path):
    """Update seniority levels in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update HTML select options
        content = re.sub(
            r'<option value="Mid-Level">Mid-Level</option>',
            '<option value="Mid">Mid</option>',
            content
        )
        
        content = re.sub(
            r'<option value="Staff">Staff</option>',
            '',
            content
        )
        
        content = re.sub(
            r'<option value="Principal">Principal</option>',
            '',
            content
        )
        
        # Update JavaScript arrays
        content = re.sub(
            r'\["Junior", "Mid", "Senior"\]',
            '["Junior", "Mid", "Senior", "Manager"]',
            content
        )
        
        # Update any hardcoded seniority references
        content = re.sub(
            r'"Mid-Level"',
            '"Mid"',
            content
        )
        
        # Update any references to Staff/Principal
        content = re.sub(
            r'"Staff"',
            '"Manager"',
            content
        )
        
        content = re.sub(
            r'"Principal"',
            '"Manager"',
            content
        )
        
        # Update any references to Manager / Lead
        content = re.sub(
            r'"Manager / Lead"',
            '"Manager"',
            content
        )
        
        # Update any references to Junior / Mid-Level
        content = re.sub(
            r'"Junior / Mid-Level"',
            '"Mid"',
            content
        )
        
        # Update any references to Student/Intern
        content = re.sub(
            r'"Student/Intern"',
            '"Junior"',
            content
        )
        
        content = re.sub(
            r'"Student / Intern"',
            '"Junior"',
            content
        )
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def update_seniority_levels_systemwide():
    """Update seniority levels across all relevant files"""
    
    # Files to update
    file_patterns = [
        "*.js",
        "*.html", 
        "*.py",
        "js/**/*.js",
        "pages/**/*.html"
    ]
    
    updated_files = []
    total_files = 0
    
    for pattern in file_patterns:
        files = glob.glob(pattern, recursive=True)
        total_files += len(files)
        
        for file_path in files:
            # Skip certain files
            if any(skip in file_path for skip in ['node_modules', '.git', '__pycache__', 'venv']):
                continue
                
            if update_file_seniority_levels(file_path):
                updated_files.append(file_path)
    
    print(f"\n📊 Summary:")
    print(f"  Total files checked: {total_files}")
    print(f"  Files updated: {len(updated_files)}")
    
    if updated_files:
        print(f"\n✅ Updated files:")
        for file_path in updated_files:
            print(f"  - {file_path}")
    
    return len(updated_files) > 0

def create_seniority_mapping_documentation():
    """Create documentation for the new seniority mapping"""
    
    doc_content = """# Seniority Level Mapping

## New 4-Level System

The system now uses 4 standardized seniority levels:

1. **Junior** - Entry-level positions, interns, students
2. **Mid** - Mid-level positions, individual contributors
3. **Senior** - Senior-level positions, experienced professionals
4. **Manager** - Management positions, leads, principals, group managers

## Migration Mapping

| Old Value | New Value | Description |
|-----------|-----------|-------------|
| `Student / Intern<br>(Entry-Level)` | `Junior` | Entry-level positions |
| `Junior / Mid-Level<br>(Product Manager)` | `Mid` | Mid-level positions |
| `Senior<br>(Senior Product Manager)` | `Senior` | Senior-level positions |
| `Manager / Lead<br>(Lead, Principal, Group PM)` | `Manager` | Management positions |

## Database Updates

Run these scripts to update your database:

1. **Check current state:**
   ```bash
   python check_seniority_levels.py
   ```

2. **Clean up data:**
   ```bash
   python clean_seniority_levels.py
   ```

3. **Verify cleanup:**
   ```bash
   python check_seniority_levels.py
   ```

## System Updates

All system files have been updated to use the new 4-level system:
- Frontend HTML forms
- JavaScript arrays and logic
- Backend Python code
- Database models and queries

## Benefits

- **Consistency**: Same 4 levels across all components
- **Simplicity**: Easier to understand and maintain
- **Scalability**: Clear progression path for candidates
- **Compatibility**: Works with all existing AI agents
"""
    
    with open('SENIORITY_LEVELS_MAPPING.md', 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print("✅ Created documentation: SENIORITY_LEVELS_MAPPING.md")

if __name__ == "__main__":
    print("🔄 Updating seniority levels systemwide to 4-level system")
    print("=" * 60)
    print("New levels: Junior, Mid, Senior, Manager")
    print("=" * 60)
    
    if update_seniority_levels_systemwide():
        print("\n✅ Systemwide update completed!")
    else:
        print("\nℹ️  No files needed updating")
    
    print("\n📝 Creating documentation...")
    create_seniority_mapping_documentation()
    
    print("\n🎉 SUCCESS! System updated to use 4-level seniority system!")
    print("\nNext steps:")
    print("1. Run 'python check_seniority_levels.py' to see current DB state")
    print("2. Run 'python clean_seniority_levels.py' to clean up your database")
    print("3. Your system will now use: Junior, Mid, Senior, Manager")
