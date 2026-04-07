#!/usr/bin/env python3
"""
Debug workflow trigger configuration
"""

import yaml
from pathlib import Path

workflows_dir = Path(".github/workflows")

for workflow_file in workflows_dir.glob("*.yml"):
    print(f"\nChecking {workflow_file.name}:")
    try:
        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
            workflow = yaml.safe_load(content)
        
        print(f"  Type: {type(workflow)}")
        print(f"  Keys: {list(workflow.keys()) if isinstance(workflow, dict) else 'Not a dict'}")
        
        # Check for 'on' trigger
        if isinstance(workflow, dict):
            for key in workflow.keys():
                print(f"  Key: '{key}' (type: {type(key)})")
                if isinstance(key, str):
                    print(f"    Stripped: '{key.strip()}'")
                    print(f"    Without quotes: '{key.strip('\"\'')}'")
        
        # Also check the raw content
        if 'on:' in content or '"on":' in content:
            print("  Found 'on:' or '\"on\":' in raw content")
        else:
            print("  NOT FOUND: 'on:' or '\"on\":' in raw content")
            
    except Exception as e:
        print(f"  Error: {e}")