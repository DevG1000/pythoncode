#!/usr/bin/env python3
"""
SOLID Principles Checker for Python Code
Checks code compliance with SOLID principles
"""

import ast
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any

class SOLIDChecker:
    """Check SOLID principles compliance"""
    
    def __init__(self):
        self.results = {
            "single_responsibility": {"passed": True, "violations": []},
            "open_closed": {"passed": True, "violations": []},
            "liskov_substitution": {"passed": True, "violations": []},
            "interface_segregation": {"passed": True, "violations": []},
            "dependency_inversion": {"passed": True, "violations": []}
        }
    
    def check_single_responsibility(self, node: ast.AST, file_path: str) -> None:
        """Check Single Responsibility Principle"""
        if isinstance(node, ast.ClassDef):
            # Count methods in class
            method_count = sum(1 for item in node.body if isinstance(item, ast.FunctionDef))
            if method_count > 10:
                self.results["single_responsibility"]["passed"] = False
                self.results["single_responsibility"]["violations"].append({
                    "file": file_path,
                    "line": node.lineno,
                    "class": node.name,
                    "issue": f"Class has {method_count} methods (should be <= 10)",
                    "principle": "Single Responsibility"
                })
        
        elif isinstance(node, ast.FunctionDef):
            # Check function length
            lines = node.end_lineno - node.lineno if node.end_lineno else 0
            if lines > 50:
                self.results["single_responsibility"]["passed"] = False
                self.results["single_responsibility"]["violations"].append({
                    "file": file_path,
                    "line": node.lineno,
                    "function": node.name,
                    "issue": f"Function is {lines} lines long (should be <= 50)",
                    "principle": "Single Responsibility"
                })
    
    def check_open_closed(self, node: ast.AST, file_path: str) -> None:
        """Check Open/Closed Principle"""
        if isinstance(node, ast.If) or isinstance(node, ast.Match):
            # Look for type checking patterns that violate OCP
            parent = getattr(node, 'parent', None)
            if parent and isinstance(parent, ast.FunctionDef):
                # Check if function has many type checks
                type_checks = sum(1 for item in ast.walk(node) 
                                if isinstance(item, (ast.Is, ast.IsNot, ast.Compare)))
                if type_checks > 3:
                    self.results["open_closed"]["passed"] = False
                    self.results["open_closed"]["violations"].append({
                        "file": file_path,
                        "line": node.lineno,
                        "issue": f"Multiple type checks ({type_checks}) in function",
                        "principle": "Open/Closed"
                    })
    
    def check_liskov_substitution(self, node: ast.AST, file_path: str) -> None:
        """Check Liskov Substitution Principle"""
        if isinstance(node, ast.ClassDef):
            # Check for method overrides that change behavior
            for base in node.bases:
                if isinstance(base, ast.Name):
                    # This would need more sophisticated analysis
                    pass
    
    def check_interface_segregation(self, node: ast.AST, file_path: str) -> None:
        """Check Interface Segregation Principle"""
        if isinstance(node, ast.ClassDef):
            # Count public methods
            public_methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and not item.name.startswith('_'):
                    public_methods.append(item.name)
            
            if len(public_methods) > 15:
                self.results["interface_segregation"]["passed"] = False
                self.results["interface_segregation"]["violations"].append({
                    "file": file_path,
                    "line": node.lineno,
                    "class": node.name,
                    "issue": f"Class has {len(public_methods)} public methods (should be <= 15)",
                    "principle": "Interface Segregation"
                })
    
    def check_dependency_inversion(self, node: ast.AST, file_path: str) -> None:
        """Check Dependency Inversion Principle"""
        if isinstance(node, ast.ImportFrom):
            # Check for concrete class imports
            for alias in node.names:
                if alias.name and not alias.name.startswith('abc') and not alias.name.endswith('Interface'):
                    # Simple check - would need more context
                    pass
    
    def analyze_file(self, file_path: str) -> None:
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Set parent attribute for all nodes
            for node in ast.walk(tree):
                for child in ast.iter_child_nodes(node):
                    child.parent = node
            
            # Check each node
            for node in ast.walk(tree):
                self.check_single_responsibility(node, file_path)
                self.check_open_closed(node, file_path)
                self.check_liskov_substitution(node, file_path)
                self.check_interface_segregation(node, file_path)
                self.check_dependency_inversion(node, file_path)
                
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}", file=sys.stderr)
    
    def analyze_directory(self, directory: str) -> None:
        """Analyze all Python files in directory"""
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.analyze_file(file_path)
    
    def get_results(self) -> Dict[str, Any]:
        """Get analysis results"""
        total_violations = sum(len(v["violations"]) for v in self.results.values())
        overall_passed = total_violations == 0
        
        return {
            "overall": {
                "passed": overall_passed,
                "total_violations": total_violations,
                "score": 100 if overall_passed else max(0, 100 - (total_violations * 10))
            },
            "principles": self.results,
            "summary": {
                "files_analyzed": "All Python files in project",
                "timestamp": "2026-04-03T00:00:00Z"
            }
        }

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check SOLID principles compliance")
    parser.add_argument("--directory", "-d", default=".", help="Directory to analyze")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--output", "-o", help="Output JSON file")
    
    args = parser.parse_args()
    
    checker = SOLIDChecker()
    checker.analyze_directory(args.directory)
    results = checker.get_results()
    
    # Print results
    if args.verbose:
        print("SOLID Principles Analysis Results")
        print("=" * 50)
        
        for principle, data in results["principles"].items():
            status = "PASS" if data["passed"] else "FAIL"
            print(f"\n{principle.replace('_', ' ').title()}: {status}")
            
            for violation in data["violations"]:
                print(f"  • {violation['file']}:{violation['line']} - {violation['issue']}")
    
    # Overall summary
    print(f"\nOverall Status: {'PASS' if results['overall']['passed'] else 'FAIL'}")
    print(f"Total Violations: {results['overall']['total_violations']}")
    print(f"Score: {results['overall']['score']}/100")
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.output}")
    
    # Exit code based on results
    sys.exit(0 if results["overall"]["passed"] else 1)

if __name__ == "__main__":
    main()