#!/usr/bin/env python3
"""
Fix Unicode issues in Python scripts for Windows compatibility
"""

import os
import re
from pathlib import Path


def fix_file(filepath):
    """Fix Unicode characters in a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace Unicode symbols with ASCII equivalents
    replacements = {
        '[OK]': '[OK]',
        '[OK]': '[OK]',
        '[FAIL]': '[FAIL]',
        '[WARN]': '[WARN]',
        '[PACKAGE]': '[PACKAGE]',
        '[MAGNIFY]': '[SEARCH]',
        '[ROCKET]': '[ROCKET]',
        '[TOOL]': '[TOOL]',
        '[CHART]': '[CHART]',
        '[LOCK]': '[LOCK]',
        '[UNLOCK]': '[UNLOCK]',
        '[NOTE]': '[NOTE]',
        '[GEAR]': '[GEAR]',
        '[BELL]': '[BELL]',
        '[UP]': '[UP]',
        '[DOWN]': '[DOWN]',
        '[LINK]': '[LINK]',
        '[TARGET]': '[TARGET]',
        '[SPARKLE]': '[SPARKLE]',
        '[FIRE]': '[FIRE]',
        '[BULB]': '[BULB]',
        '[BOOKS]': '[BOOKS]',
        '[MAGNIFY]': '[MAGNIFY]',
        '[ALERT]': '[ALERT]',
        '[REFRESH]': '[REFRESH]',
        '[CLIPBOARD]': '[CLIPBOARD]',
        '[KEY]': '[KEY]',
        '[OLDKEY]': '[OLDKEY]',
        '[LOCKED]': '[LOCKED]',
        '[GLOBE]': '[GLOBE]',
        '[COMPUTER]': '[COMPUTER]',
        '[PHONE]': '[PHONE]',
        '[DESKTOP]': '[DESKTOP]',
        '[CARDS]': '[CARDS]',
        '[FOLDER]': '[FOLDER]',
        '[OPENFOLDER]': '[OPENFOLDER]',
        '[CABINET]': '[CABINET]',
        '[CALENDAR]': '[CALENDAR]',
        '[CLOCK]': '[CLOCK]',
        '[HOURGLASS]': '[HOURGLASS]',
        '[HOURGLASS2]': '[HOURGLASS2]',
        '[BATTERY]': '[BATTERY]',
        '[PLUG]': '[PLUG]',
        '[FLOPPY]': '[FLOPPY]',
        '[CD]': '[CD]',
        '[DVD]': '[DVD]',
        '[MUSIC]': '[MUSIC]',
        '[NOTES]': '[NOTES]',
        '[TROPHY]': '[TROPHY]',
        '[MEDAL]': '[MEDAL]',
        '[MILITARY]': '[MILITARY]',
        '[FLAG]': '[FLAG]',
        '[FLAG2]': '[FLAG2]',
        '[FLAGS]': '[FLAGS]',
        '[BLACKFLAG]': '[BLACKFLAG]',
        '[WHITEFLAG]': '[WHITEFLAG]',
        '[WHITEFLAG]‍🌈': '[RAINBOW]',
        '[BLACKFLAG]‍☠️': '[PIRATE]',
    }
    
    for unicode_char, ascii_replacement in replacements.items():
        content = content.replace(unicode_char, ascii_replacement)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return len(replacements)


def main():
    """Main function"""
    script_dir = Path(__file__).parent
    python_files = list(script_dir.glob("*.py"))
    
    print(f"Found {len(python_files)} Python files to check")
    
    total_replacements = 0
    for filepath in python_files:
        print(f"Processing: {filepath.name}")
        replacements = fix_file(filepath)
        if replacements > 0:
            print(f"  Fixed {replacements} Unicode characters")
            total_replacements += replacements
    
    print(f"\nTotal replacements: {total_replacements}")
    print("Done!")


if __name__ == "__main__":
    main()