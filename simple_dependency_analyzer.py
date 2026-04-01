#!/usr/bin/env python3
"""
Simple Dependency Analyzer
Analyzes module dependencies and coupling in the PythonCode project
"""

import os
import ast
import sys
from collections import defaultdict, Counter
import json

class SimpleDependencyAnalyzer:
    def __init__(self, project_root):
        self.project_root = project_root
        self.dependencies = defaultdict(set)
        self.module_files = {}
        self.imports_by_file = defaultdict(set)
        
    def find_python_files(self):
        """Find all Python files in the project"""
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip virtual environments and hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env', '.venv']]
            
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, self.project_root)
                    python_files.append((full_path, rel_path))
                    
                    # Store module name mapping
                    module_name = rel_path.replace('\\', '.').replace('/', '.').replace('.py', '')
                    self.module_files[module_name] = full_path
                    
        return python_files
    
    def extract_imports(self, file_path):
        """Extract imports from a Python file"""
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
                        
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"Warning: Could not parse {file_path}: {e}")
            
        return imports
    
    def analyze(self):
        """Analyze all Python files in the project"""
        print("Analyzing project dependencies...")
        
        python_files = self.find_python_files()
        print(f"Found {len(python_files)} Python files")
        
        # Extract imports from each file
        for full_path, rel_path in python_files:
            imports = self.extract_imports(full_path)
            self.imports_by_file[rel_path] = imports
            
            # Convert file path to module name
            module_name = rel_path.replace('\\', '.').replace('/', '.').replace('.py', '')
            
            # Filter out standard library imports
            project_imports = set()
            for imp in imports:
                # Check if this is a project module
                if imp in self.module_files:
                    project_imports.add(imp)
                # Also check for relative imports within our project
                elif any(imp.startswith(proj_mod.split('.')[0]) for proj_mod in self.module_files.keys()):
                    # Find matching project modules
                    for proj_mod in self.module_files.keys():
                        if proj_mod.startswith(imp) or imp.startswith(proj_mod.split('.')[0]):
                            project_imports.add(proj_mod)
                            
            self.dependencies[module_name] = project_imports
            
        return self.dependencies
    
    def find_circular_dependencies(self):
        """Find circular dependencies using DFS"""
        visited = set()
        stack = set()
        cycles = []
        
        def dfs(node, path):
            if node in stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:]
                if cycle not in cycles:
                    cycles.append(cycle)
                return
                
            if node in visited:
                return
                
            visited.add(node)
            stack.add(node)
            
            for neighbor in self.dependencies.get(node, set()):
                dfs(neighbor, path + [neighbor])
                
            stack.remove(node)
            
        for node in self.dependencies:
            if node not in visited:
                dfs(node, [node])
                
        return cycles
    
    def calculate_coupling_metrics(self):
        """Calculate coupling metrics"""
        metrics = {
            'total_modules': len(self.dependencies),
            'total_dependencies': sum(len(deps) for deps in self.dependencies.values()),
            'avg_dependencies_per_module': 0,
            'high_coupling_modules': [],
            'module_coupling': {}
        }
        
        if metrics['total_modules'] > 0:
            metrics['avg_dependencies_per_module'] = metrics['total_dependencies'] / metrics['total_modules']
            
        # Calculate coupling for each module
        for module, deps in self.dependencies.items():
            coupling_score = len(deps)
            metrics['module_coupling'][module] = coupling_score
            
            # Flag high coupling (more than 5 dependencies)
            if coupling_score > 5:
                metrics['high_coupling_modules'].append((module, coupling_score))
                
        return metrics
    
    def generate_report(self):
        """Generate a comprehensive dependency report"""
        print("\n" + "="*60)
        print("DEPENDENCY ANALYSIS REPORT")
        print("="*60)
        
        # Calculate metrics
        metrics = self.calculate_coupling_metrics()
        
        print(f"\nProject: {self.project_root}")
        print(f"Total modules: {metrics['total_modules']}")
        print(f"Total dependencies: {metrics['total_dependencies']}")
        print(f"Average dependencies per module: {metrics['avg_dependencies_per_module']:.2f}")
        
        # Find circular dependencies
        cycles = self.find_circular_dependencies()
        print(f"\nCircular dependencies found: {len(cycles)}")
        
        if cycles:
            print("\nCircular dependency chains:")
            for i, cycle in enumerate(cycles, 1):
                print(f"  {i}. {' -> '.join(cycle)} -> {cycle[0]}")
        
        # High coupling modules
        print(f"\nHigh coupling modules (>5 dependencies): {len(metrics['high_coupling_modules'])}")
        if metrics['high_coupling_modules']:
            print("\nHigh coupling modules:")
            for module, score in sorted(metrics['high_coupling_modules'], key=lambda x: x[1], reverse=True):
                print(f"  {module}: {score} dependencies")
        
        # Top 10 most coupled modules
        print("\nTop 10 most coupled modules:")
        sorted_modules = sorted(metrics['module_coupling'].items(), key=lambda x: x[1], reverse=True)[:10]
        for module, score in sorted_modules:
            print(f"  {module}: {score} dependencies")
        
        # Generate recommendations
        print("\n" + "="*60)
        print("RECOMMENDATIONS")
        print("="*60)
        
        recommendations = []
        
        if cycles:
            recommendations.append("Fix circular dependencies to improve maintainability")
            
        if metrics['high_coupling_modules']:
            recommendations.append("Refactor high-coupling modules to reduce dependencies")
            
        if metrics['avg_dependencies_per_module'] > 3:
            recommendations.append("Consider implementing dependency injection to reduce coupling")
            
        # Check for specific problematic patterns
        for module, deps in self.dependencies.items():
            if 'api' in module and 'command_system' in deps:
                recommendations.append(f"Module '{module}' depends on command_system - consider abstraction")
            if 'command_system' in module and 'api' in deps:
                recommendations.append(f"Module '{module}' depends on api - consider abstraction")
                
        if not recommendations:
            recommendations.append("Dependency structure looks good! Maintain current practices.")
            
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
            
        # Save detailed report
        report = {
            'project': self.project_root,
            'metrics': metrics,
            'circular_dependencies': cycles,
            'high_coupling_modules': metrics['high_coupling_modules'],
            'all_dependencies': {k: list(v) for k, v in self.dependencies.items()},
            'recommendations': recommendations
        }
        
        with open('dependency_analysis_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"\nDetailed report saved to: dependency_analysis_report.json")
        
        return report

def main():
    """Main function"""
    project_root = "D:/pythoncode"
    
    if not os.path.exists(project_root):
        print(f"Error: Project path does not exist: {project_root}")
        return
        
    analyzer = SimpleDependencyAnalyzer(project_root)
    analyzer.analyze()
    report = analyzer.generate_report()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()