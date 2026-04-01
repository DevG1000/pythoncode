#!/usr/bin/env python3
"""
设计原则检查脚本
检查PythonCode项目的SOLID原则遵循情况
"""

import ast
import os
from pathlib import Path
from collections import defaultdict

class DesignPrincipleChecker:
    def __init__(self):
        self.issues = defaultdict(list)
        self.stats = {
            'files_analyzed': 0,
            'classes_found': 0,
            'methods_found': 0,
            'functions_found': 0
        }
        
    def check_file(self, filepath: Path):
        """检查单个文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            self.stats['files_analyzed'] += 1
            
            # 遍历AST
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self._check_class(node, filepath)
                elif isinstance(node, ast.FunctionDef):
                    # 检查是否是类方法
                    if not self._is_class_method(node, tree):
                        self._check_function(node, filepath)
                        
        except (SyntaxError, UnicodeDecodeError) as e:
            print(f"警告: 无法解析文件 {filepath}: {e}")
    
    def _is_class_method(self, node, tree):
        """检查函数是否是类的方法"""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.ClassDef):
                for item in parent.body:
                    if item == node:
                        return True
        return False
    
    def _check_class(self, node: ast.ClassDef, filepath: Path):
        """检查类设计"""
        self.stats['classes_found'] += 1
        class_name = node.name
        
        # 统计方法数量
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        self.stats['methods_found'] += len(methods)
        
        # SRP检查：类方法过多
        if len(methods) > 12:
            self.issues['SRP'].append(
                f"{filepath}: 类 '{class_name}' 有 {len(methods)} 个方法，"
                "可能违反单一职责原则"
            )
        
        # 检查每个方法
        for method in methods:
            self._check_method(method, class_name, filepath)
    
    def _check_method(self, node: ast.FunctionDef, class_name: str, filepath: Path):
        """检查方法设计"""
        method_name = node.name
        
        # ISP检查：参数过多
        args_count = len(node.args.args)
        if args_count > 6:
            self.issues['ISP'].append(
                f"{filepath}: 方法 '{class_name}.{method_name}' 有 {args_count} 个参数，"
                "可能违反接口隔离原则"
            )
        
        # 粗略估计方法长度（行数）
        method_text = ast.unparse(node) if hasattr(ast, 'unparse') else ''
        if method_text:
            lines = method_text.count('\n') + 1
            if lines > 80:
                self.issues['SRP'].append(
                    f"{filepath}: 方法 '{class_name}.{method_name}' 过长 ({lines} 行)，"
                    "可能违反单一职责原则"
                )
    
    def _check_function(self, node: ast.FunctionDef, filepath: Path):
        """检查模块级函数"""
        self.stats['functions_found'] += 1
        func_name = node.name
        
        # ISP检查：参数过多
        args_count = len(node.args.args)
        if args_count > 8:
            self.issues['ISP'].append(
                f"{filepath}: 函数 '{func_name}' 有 {args_count} 个参数，"
                "可能违反接口隔离原则"
            )
        
        # 粗略估计函数长度
        func_text = ast.unparse(node) if hasattr(ast, 'unparse') else ''
        if func_text:
            lines = func_text.count('\n') + 1
            if lines > 100:
                self.issues['SRP'].append(
                    f"{filepath}: 函数 '{func_name}' 过长 ({lines} 行)，"
                    "可能违反单一职责原则"
                )
    
    def check_dependencies(self, project_root: Path):
        """检查依赖关系（DIP原则）"""
        print("\n检查依赖关系...")
        
        # 简单检查：高层模块是否直接依赖低层模块
        high_level_modules = ['api']
        low_level_modules = ['command_system', 'utils']
        
        for root, dirs, files in os.walk(project_root):
            for file in files:
                if file.endswith('.py'):
                    filepath = Path(root) / file
                    
                    # 检查是否是高层模块文件
                    if any(module in str(filepath) for module in high_level_modules):
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                            # 检查是否直接导入低层模块
                            for low_module in low_level_modules:
                                if f"import {low_module}" in content or f"from {low_module}" in content:
                                    self.issues['DIP'].append(
                                        f"{filepath}: 直接导入低层模块 '{low_module}'，"
                                        "可能违反依赖倒置原则"
                                    )
    
    def generate_report(self):
        """生成检查报告"""
        print("=" * 70)
        print("PythonCode项目设计原则检查报告")
        print("=" * 70)
        
        print(f"\n分析统计:")
        print(f"  分析文件数: {self.stats['files_analyzed']}")
        print(f"  发现类数: {self.stats['classes_found']}")
        print(f"  发现方法数: {self.stats['methods_found']}")
        print(f"  发现函数数: {self.stats['functions_found']}")
        
        print("\n" + "=" * 70)
        print("设计原则问题汇总:")
        print("=" * 70)
        
        total_issues = 0
        principles = ['SRP', 'ISP', 'DIP']
        
        for principle in principles:
            issues = self.issues.get(principle, [])
            if issues:
                print(f"\n{principle}原则问题 ({len(issues)}个):")
                for issue in issues[:5]:  # 只显示前5个
                    print(f"  [ISSUE] {issue}")
                if len(issues) > 5:
                    print(f"  ... 还有{len(issues)-5}个问题未显示")
                total_issues += len(issues)
            else:
                print(f"\n{principle}原则: ✅ 未发现问题")
        
        print("\n" + "=" * 70)
        print(f"总计发现 {total_issues} 个设计原则问题")
        
        # 给出建议
        if total_issues > 0:
            print("\n改进建议:")
            if 'SRP' in self.issues:
                print("  1. 考虑拆分职责过多的类和方法")
            if 'ISP' in self.issues:
                print("  2. 减少方法参数数量，考虑使用参数对象")
            if 'DIP' in self.issues:
                print("  3. 引入依赖注入，高层模块应依赖抽象而非具体实现")
        
        print("=" * 70)

def main():
    """主函数"""
    project_root = Path('.')
    checker = DesignPrincipleChecker()
    
    print("开始设计原则检查...")
    
    # 检查所有Python文件
    python_files = list(project_root.rglob('*.py'))
    
    # 排除测试文件和缓存
    python_files = [
        f for f in python_files 
        if 'test' not in str(f) and '__pycache__' not in str(f)
    ]
    
    print(f"找到 {len(python_files)} 个Python文件")
    
    for filepath in python_files:
        checker.check_file(filepath)
    
    # 检查依赖关系
    checker.check_dependencies(project_root)
    
    # 生成报告
    checker.generate_report()

if __name__ == '__main__':
    main()