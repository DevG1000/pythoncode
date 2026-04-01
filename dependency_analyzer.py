#!/usr/bin/env python
"""
依赖分析器
分析PythonCode项目的模块依赖关系
"""

import ast
import os
import re
from pathlib import Path
from collections import defaultdict, Counter
import json
from typing import Dict, List, Set, Tuple
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime


class DependencyAnalyzer:
    """依赖分析器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.dependencies = defaultdict(set)  # 模块 -> 依赖的模块
        self.reverse_dependencies = defaultdict(set)  # 模块 -> 被哪些模块依赖
        self.external_dependencies = defaultdict(set)  # 模块 -> 外部依赖
        self.circular_dependencies = []  # 循环依赖
        self.module_info = {}  # 模块详细信息
        
    def analyze_project(self):
        """分析整个项目"""
        print("[ANALYZE] 开始分析项目依赖关系...")
        
        # 1. 扫描所有Python文件
        python_files = list(self.project_root.rglob("*.py"))
        print(f"找到 {len(python_files)} 个Python文件")
        
        # 2. 分析每个文件的依赖
        for file_path in python_files:
            if self._should_skip_file(file_path):
                continue
            
            module_name = self._get_module_name(file_path)
            self.module_info[module_name] = {
                "file_path": str(file_path),
                "lines_of_code": self._count_lines(file_path),
                "imports": set()
            }
            
            try:
                imports = self._analyze_file_imports(file_path)
                self.dependencies[module_name] = imports
                self.module_info[module_name]["imports"] = imports
                
                # 更新反向依赖
                for imported_module in imports:
                    self.reverse_dependencies[imported_module].add(module_name)
                    
            except Exception as e:
                print(f"警告: 分析文件 {file_path} 时出错: {e}")
        
        # 3. 检测循环依赖
        self._detect_circular_dependencies()
        
        # 4. 分析外部依赖
        self._analyze_external_dependencies()
        
        print("[OK] 依赖分析完成")
        return self._generate_report()
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = [
            "__pycache__",
            ".pyc",
            "test_",
            "setup.py",
            "__init__.py"
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)
    
    def _get_module_name(self, file_path: Path) -> str:
        """获取模块名称"""
        # 相对于项目根的路径
        relative_path = file_path.relative_to(self.project_root)
        # 转换为模块路径（去掉.py，用.替换/）
        module_name = str(relative_path).replace(".py", "").replace("\\", ".")
        return module_name
    
    def _count_lines(self, file_path: Path) -> int:
        """统计文件行数"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def _analyze_file_imports(self, file_path: Path) -> Set[str]:
        """分析文件的导入语句"""
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 使用AST分析导入
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_name = alias.name.split('.')[0]
                        if self._is_internal_module(module_name):
                            imports.add(module_name)
                        else:
                            # 外部依赖
                            external_module = alias.name
                            module_key = self._get_module_name(file_path)
                            self.external_dependencies[module_key].add(external_module)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        module_name = node.module.split('.')[0]
                        if self._is_internal_module(module_name):
                            imports.add(module_name)
                        else:
                            # 外部依赖
                            module_key = self._get_module_name(file_path)
                            self.external_dependencies[module_key].add(node.module)
        
        except SyntaxError:
            # 如果AST解析失败，使用正则表达式
            imports.update(self._analyze_imports_with_regex(content, file_path))
        
        return imports
    
    def _analyze_imports_with_regex(self, content: str, file_path: Path) -> Set[str]:
        """使用正则表达式分析导入"""
        imports = set()
        
        # 匹配 import 语句
        import_pattern = r'^\s*import\s+([a-zA-Z0-9_.]+)'
        for match in re.finditer(import_pattern, content, re.MULTILINE):
            module_name = match.group(1).split('.')[0]
            if self._is_internal_module(module_name):
                imports.add(module_name)
            else:
                module_key = self._get_module_name(file_path)
                self.external_dependencies[module_key].add(match.group(1))
        
        # 匹配 from ... import 语句
        from_pattern = r'^\s*from\s+([a-zA-Z0-9_.]+)\s+import'
        for match in re.finditer(from_pattern, content, re.MULTILINE):
            module_name = match.group(1).split('.')[0]
            if self._is_internal_module(module_name):
                imports.add(module_name)
            else:
                module_key = self._get_module_name(file_path)
                self.external_dependencies[module_key].add(match.group(1))
        
        return imports
    
    def _is_internal_module(self, module_name: str) -> bool:
        """判断是否是内部模块"""
        # 检查模块是否在项目中
        internal_modules = ["api", "command_system", "card_generator", "config", "scripts", "utils"]
        return module_name in internal_modules
    
    def _detect_circular_dependencies(self):
        """检测循环依赖"""
        print("[CHECK] 检测循环依赖...")
        
        # 构建有向图
        graph = nx.DiGraph()
        
        # 添加节点和边
        for module, deps in self.dependencies.items():
            graph.add_node(module)
            for dep in deps:
                if dep in self.dependencies:  # 只考虑内部模块
                    graph.add_edge(module, dep)
        
        # 查找循环
        try:
            cycles = list(nx.simple_cycles(graph))
            self.circular_dependencies = cycles
        except:
            # 如果networkx不可用，使用简单算法
            self._detect_circular_dependencies_simple()
    
    def _detect_circular_dependencies_simple(self):
        """简单的循环依赖检测算法"""
        visited = set()
        recursion_stack = set()
        
        def dfs(module, path):
            if module in recursion_stack:
                # 找到循环
                cycle_start = path.index(module)
                cycle = path[cycle_start:]
                if cycle not in self.circular_dependencies:
                    self.circular_dependencies.append(cycle)
                return
            
            if module in visited:
                return
            
            visited.add(module)
            recursion_stack.add(module)
            
            for dep in self.dependencies.get(module, set()):
                if dep in self.dependencies:  # 只考虑内部模块
                    dfs(dep, path + [module])
            
            recursion_stack.remove(module)
        
        for module in self.dependencies:
            if module not in visited:
                dfs(module, [])
    
    def _analyze_external_dependencies(self):
        """分析外部依赖"""
        print("📦 分析外部依赖...")
        
        # 读取requirements.txt
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            print(f"找到 {len(requirements)} 个requirements.txt中的依赖")
    
    def _generate_report(self) -> Dict:
        """生成分析报告"""
        print("[REPORT] 生成依赖分析报告...")
        
        # 计算耦合度指标
        coupling_metrics = self._calculate_coupling_metrics()
        
        # 生成模块依赖矩阵
        dependency_matrix = self._generate_dependency_matrix()
        
        # 识别问题依赖
        problem_dependencies = self._identify_problem_dependencies()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "project": str(self.project_root),
            "module_count": len(self.dependencies),
            "total_dependencies": sum(len(deps) for deps in self.dependencies.values()),
            "coupling_metrics": coupling_metrics,
            "circular_dependencies": self.circular_dependencies,
            "problem_dependencies": problem_dependencies,
            "external_dependencies": dict(self.external_dependencies),
            "module_info": self.module_info,
            "dependency_matrix": dependency_matrix,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _calculate_coupling_metrics(self) -> Dict:
        """计算耦合度指标"""
        metrics = {
            "afferent_coupling": {},  # 传入耦合（被多少模块依赖）
            "efferent_coupling": {},  # 传出耦合（依赖多少模块）
            "instability": {}         # 不稳定性
        }
        
        for module in self.dependencies:
            # 传出耦合（Ce）
            efferent = len(self.dependencies[module])
            
            # 传入耦合（Ca）
            afferent = len(self.reverse_dependencies.get(module, set()))
            
            # 不稳定性 I = Ce / (Ce + Ca)
            instability = efferent / (efferent + afferent) if (efferent + afferent) > 0 else 0
            
            metrics["afferent_coupling"][module] = afferent
            metrics["efferent_coupling"][module] = efferent
            metrics["instability"][module] = round(instability, 3)
        
        # 整体统计
        metrics["summary"] = {
            "avg_afferent": round(sum(metrics["afferent_coupling"].values()) / len(metrics["afferent_coupling"]), 2),
            "avg_efferent": round(sum(metrics["efferent_coupling"].values()) / len(metrics["efferent_coupling"]), 2),
            "avg_instability": round(sum(metrics["instability"].values()) / len(metrics["instability"]), 3),
            "high_coupling_modules": self._identify_high_coupling_modules(metrics)
        }
        
        return metrics
    
    def _identify_high_coupling_modules(self, metrics: Dict) -> List[Dict]:
        """识别高耦合模块"""
        high_coupling = []
        
        for module, instability in metrics["instability"].items():
            afferent = metrics["afferent_coupling"][module]
            efferent = metrics["efferent_coupling"][module]
            
            # 高耦合标准：不稳定性>0.7 或 总耦合度>5
            total_coupling = afferent + efferent
            if instability > 0.7 or total_coupling > 5:
                high_coupling.append({
                    "module": module,
                    "instability": instability,
                    "afferent_coupling": afferent,
                    "efferent_coupling": efferent,
                    "total_coupling": total_coupling,
                    "issue": "高不稳定性" if instability > 0.7 else "高耦合度"
                })
        
        return sorted(high_coupling, key=lambda x: x["instability"], reverse=True)
    
    def _generate_dependency_matrix(self) -> List[List]:
        """生成依赖矩阵"""
        modules = sorted(self.dependencies.keys())
        matrix = []
        
        # 表头
        header = [""] + modules
        matrix.append(header)
        
        # 矩阵行
        for module_from in modules:
            row = [module_from]
            for module_to in modules:
                if module_to in self.dependencies[module_from]:
                    row.append("✓")
                else:
                    row.append("")
            matrix.append(row)
        
        return matrix
    
    def _identify_problem_dependencies(self) -> List[Dict]:
        """识别问题依赖"""
        problems = []
        
        # 1. 检查跨层依赖（如果存在分层）
        for module, deps in self.dependencies.items():
            for dep in deps:
                # 检查是否违反依赖方向（示例规则）
                if self._is_dependency_violation(module, dep):
                    problems.append({
                        "type": "dependency_direction_violation",
                        "from": module,
                        "to": dep,
                        "description": f"{module} 不应该依赖 {dep}（违反依赖方向）",
                        "severity": "medium"
                    })
        
        # 2. 检查过度依赖
        for module, deps in self.dependencies.items():
            if len(deps) > 5:  # 依赖超过5个模块
                problems.append({
                    "type": "excessive_dependencies",
                    "module": module,
                    "dependency_count": len(deps),
                    "description": f"{module} 依赖 {len(deps)} 个模块，可能职责过多",
                    "severity": "low"
                })
        
        # 3. 检查被过度依赖的模块
        for module, dependents in self.reverse_dependencies.items():
            if len(dependents) > 3:  # 被超过3个模块依赖
                problems.append({
                    "type": "highly_coupled_module",
                    "module": module,
                    "dependent_count": len(dependents),
                    "dependents": list(dependents),
                    "description": f"{module} 被 {len(dependents)} 个模块依赖，是架构关键点",
                    "severity": "info"
                })
        
        return problems
    
    def _is_dependency_violation(self, from_module: str, to_module: str) -> bool:
        """检查是否违反依赖方向规则"""
        # 简单规则：api不应该依赖具体实现细节
        if from_module.startswith("api.") and to_module.startswith("command_system."):
            # 检查是否依赖具体实现而非接口
            if "cmd_agent" in to_module or "async_tasks" in to_module:
                return True
        return False
    
    def _generate_recommendations(self) -> List[Dict]:
        """生成改进建议"""
        recommendations = []
        
        # 1. 循环依赖建议
        if self.circular_dependencies:
            recommendations.append({
                "type": "circular_dependency",
                "priority": "high",
                "description": f"发现 {len(self.circular_dependencies)} 个循环依赖",
                "suggestions": [
                    "引入依赖注入打破循环",
                    "提取公共接口",
                    "使用事件驱动架构"
                ],
                "examples": self.circular_dependencies[:3]  # 只显示前3个
            })
        
        # 2. 高耦合模块建议
        coupling_metrics = self._calculate_coupling_metrics()
        high_coupling = coupling_metrics["summary"]["high_coupling_modules"]
        
        if high_coupling:
            recommendations.append({
                "type": "high_coupling",
                "priority": "medium",
                "description": f"发现 {len(high_coupling)} 个高耦合模块",
                "suggestions": [
                    "拆分职责过多的模块",
                    "引入接口抽象",
                    "使用依赖倒置原则"
                ],
                "examples": [h["module"] for h in high_coupling[:3]]
            })
        
        # 3. 依赖方向建议
        if any(p["type"] == "dependency_direction_violation" for p in self._identify_problem_dependencies()):
            recommendations.append({
                "type": "dependency_direction",
                "priority": "medium",
                "description": "发现违反依赖方向的依赖关系",
                "suggestions": [
                    "高层模块应该依赖抽象而非具体实现",
                    "实现依赖注入容器",
                    "定义清晰的接口契约"
                ]
            })
        
        return recommendations
    
    def print_summary_report(self, report: Dict):
        """打印摘要报告"""
        print("\n" + "="*70)
        print("依赖分析报告摘要")
        print("="*70)
        
        print(f"\n📁 项目: {report['project']}")
        print(f"📅 分析时间: {report['timestamp']}")
        print(f"📦 分析模块: {report['module_count']} 个")
        print(f"🔗 总依赖关系: {report['total_dependencies']} 个")
        
        # 耦合度统计
        metrics = report["coupling_metrics"]["summary"]
        print(f"\n📊 耦合度统计:")
        print(f"  平均传入耦合: {metrics['avg_afferent']}")
        print(f"  平均传出耦合: {metrics['avg_efferent']}")
        print(f"  平均不稳定性: {metrics['avg_instability']}")
        
        # 循环依赖
        circular_count = len(report["circular_dependencies"])
        if circular_count > 0:
            print(f"\n⚠️ 发现 {circular_count} 个循环依赖:")
            for i, cycle in enumerate(report["circular_dependencies"][:3], 1):
                print(f"  {i}. {' → '.join(cycle)} → ...")
            if circular_count > 3:
                print(f"  ... 还有 {circular_count - 3} 个循环依赖")
        else:
            print(f"\n✅ 未发现循环依赖")
        
        # 高耦合模块
        high_coupling = metrics["high_coupling_modules"]
        if high_coupling:
            print(f"\n⚠️ 高耦合模块 ({len(high_coupling)} 个):")
            for module in high_coupling[:5]:
                print(f"  • {module['module']}: 不稳定性={module['instability']}, 总耦合度={module['total_coupling']}")
        
        # 问题依赖
        problems = report["problem_dependencies"]
        if problems:
            print(f"\n🔧 发现 {len(problems)} 个依赖问题:")
            problem_types = Counter(p["type"] for p in problems)
            for ptype, count in problem_types.items():
                print(f"  • {ptype}: {count} 个")
        
        # 建议
        recommendations = report["recommendations"]
        if recommendations:
            print(f"\n💡 改进建议 ({len(recommendations)} 条):")
            for i, rec in enumerate(recommendations, 1):
                print(f"\n  {i}. {rec['type']} ({rec['priority']}优先级)")
                print(f"     描述: {rec['description']}")
                print(f"     建议: {', '.join(rec['suggestions'][:2])}")
        
        print("\n" + "="*70)
        print("详细报告已保存到: dependency_analysis_report.json")
        print("="*70)
    
    def save_report(self, report: Dict, output_file: str = "dependency_analysis_report.json"):
        """保存报告到文件"""
        # 转换set为list以便JSON序列化
        serializable_report = json.loads(
            json.dumps(report, default=lambda x: list(x) if isinstance(x, set) else x)
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 详细报告已保存到: {output_file}")
        return output_file


def main():
    """主函数"""
    print("DEPENDENCY ANALYZER STARTED")
    print("="*50)
    
    # 设置项目路径
    project_root = "D:/pythoncode"
    
    # 检查项目是否存在
    if not os.path.exists(project_root):
        print(f"❌ 项目路径不存在: {project_root}")
        return
    
    # 创建分析器并执行分析
    analyzer = DependencyAnalyzer(project_root)
    report = analyzer.analyze_project()
    
    # 打印摘要
    analyzer.print_summary_report(report)
    
    # 保存详细报告
    analyzer.save_report(report)
    
    # 生成可视化（如果可能）
    try:
        generate_visualization(report)
    except ImportError:
        print("⚠️  无法生成可视化图表，请安装matplotlib和networkx")
    
    print("\n✅ 依赖分析完成")


def generate_visualization(report: Dict):
    """生成可视化图表"""
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
        
        print("\n📈 生成依赖关系图...")
        
        # 创建有向图
        G = nx.DiGraph()
        
        # 添加节点和边
        for module, info in report["module_info"].items():
            G.add_node(module, size=info.get("lines_of_code", 1))
            
            for dep in info.get("imports", []):
                if dep in report["module_info"]:  # 只显示内部依赖
                    G.add_edge(module, dep)
        
        # 设置节点颜色基于不稳定性
        node_colors = []
        for node in G.nodes():
            instability = report["coupling_metrics"]["instability"].get(node, 0.5)
            # 红色表示高不稳定性，绿色表示稳定
            node_colors.append((instability, 0.3, 1-instability, 0.8))
        
        # 绘制图形
        plt.figure(figsize=(12, 10))
        
        # 使用spring布局
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # 绘制节点
        nx.draw_networkx_nodes(G, pos, 
                              node_color=node_colors,
                              node_size=[G.nodes[node].get('size', 100) / 10 for node in G.nodes()],
                              alpha=0.8)
        
        # 绘制边
        nx.draw_networkx_edges(G, pos, 
                              edge_color='gray',
                              arrows=True,
                              arrowsize=10,
                              alpha=0.5)
        
        # 绘制标签
        nx.draw_networkx_labels(G, pos, 
                               font_size=8,
                               font_weight='bold')
        
        plt.title("PythonCode项目依赖关系图", fontsize=16)
        plt.axis('off')
        plt.tight_layout()
        
        # 保存图像
        plt.savefig("dependency_graph.png", dpi=300, bbox_inches='tight')
        print("📊 依赖关系图已保存到: dependency_graph.png")
        
        # 显示图例
        plt.figure(figsize=(8, 2))
        plt.text(0.1, 0.7, "节点颜色说明:", fontsize=12, fontweight='bold')
        plt.text(0.1, 0.4, "• 红色: 高不稳定性 (I > 0.7)", color='red', fontsize=10)
        plt.text(0.1, 0.1, "• 绿色: 低不稳定性 (I < 0.3)", color='green', fontsize=10)
        plt.text(0.5, 0.4, "• 节点大小: 代码行数", fontsize=10)
        plt.text(0.5, 0.1, "• 箭头: 依赖方向", fontsize=10)
        plt.axis('off')
        plt.savefig("dependency_legend.png", dpi=150, bbox_inches='tight')
        
    except ImportError as e:
        print(f"⚠️  无法生成可视化: {e}")
    except Exception as e:
        print(f"⚠️  生成可视化时出错: {e}")


if __name__ == "__main__":
    main()