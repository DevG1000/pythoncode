from check_design_principles import DesignPrincipleChecker
from simple_dependency_analyzer import SimpleDependencyAnalyzer

import os
import sys
import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class ArchitectureQualityAgent:
    def __init__(self, config_path: Optional[str] = None):
        self.agent_id = f"arch_agent_{int(time.time())}"
        self.start_time = datetime.now()
        self.config = self._load_config(config_path)
        self.report_history: List[Dict[str, Any]] = []

        logger.info(f"[ARCH_AGENT] Architecture Quality Agent started: {self.agent_id}")
        logger.info(f"[ARCH_AGENT] Start time: {self.start_time}")

    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        default_config = {
            'enabled': True,
            'log_level': 'INFO',
            'analysis': {
                'solid_principles': {'enabled': True, 'max_methods_per_class': 12, 'max_method_lines': 80, 'max_function_params': 8, 'max_method_params': 6, 'max_function_lines': 100},
                'dependency_analysis': {'enabled': True, 'max_dependencies_per_module': 5, 'detect_circular': True},
                'module_coupling': {'enabled': True, 'high_coupling_threshold': 5},
                'report': {'output_dir': 'reports/architecture', 'save_json': True, 'save_markdown': True}
            },
            'scoring': {'modular_design_max': 20, 'design_principles_max': 20, 'technology_selection_max': 20, 'scalability_max': 20, 'maintainability_max': 20, 'security_design_max': 20}
        }
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                import yaml
                loaded = yaml.safe_load(content)
                if loaded and 'architecture_agent' in loaded:
                    merged = default_config.copy()
                    for k, v in loaded['architecture_agent'].items():
                        if isinstance(v, dict) and k in merged:
                            merged[k].update(v)
                        else:
                            merged[k] = v
                    logger.info(f"[ARCH_AGENT] Configuration loaded from {config_path}")
                    return merged
            except Exception as e:
                logger.warning(f"[ARCH_AGENT] Failed to load config {config_path}: {e}")
        logger.info("[ARCH_AGENT] Using default configuration")
        return default_config

    def analyze_solid_principles(self, project_root: str = ".") -> Dict[str, Any]:
        logger.info("[ARCH_AGENT] Analyzing SOLID principles...")
        checker = DesignPrincipleChecker()

        python_files = list(Path(project_root).rglob('*.py'))
        python_files = [f for f in python_files if 'test' not in str(f) and '__pycache__' not in str(f) and '.venv' not in str(f) and 'venv' not in str(f)]

        logger.info(f"[ARCH_AGENT] Found {len(python_files)} Python files to analyze")
        for filepath in python_files:
            checker.check_file(filepath)
        checker.check_dependencies(Path(project_root))

        total_issues = sum(len(v) for v in checker.issues.values())
        score = max(0, 20 - total_issues)
        if total_issues <= 3:
            score = 18
        elif total_issues <= 6:
            score = 15
        elif total_issues <= 10:
            score = 12
        elif total_issues <= 15:
            score = 8

        return {
            'status': 'completed',
            'stats': checker.stats,
            'issues': {k: v[:10] for k, v in checker.issues.items()},
            'total_issues': total_issues,
            'score': score,
            'max_score': 20
        }

    def analyze_dependencies(self, project_root: str = ".") -> Dict[str, Any]:
        logger.info("[ARCH_AGENT] Analyzing module dependencies...")
        analyzer = SimpleDependencyAnalyzer(project_root)
        analyzer.analyze()
        metrics = analyzer.calculate_coupling_metrics()
        cycles = analyzer.find_circular_dependencies()

        score = 20
        if cycles:
            score -= len(cycles) * 3
        if metrics['high_coupling_modules']:
            score -= len(metrics['high_coupling_modules'])
        score = max(0, min(20, score))

        return {
            'status': 'completed',
            'total_modules': metrics['total_modules'],
            'total_dependencies': metrics['total_dependencies'],
            'avg_dependencies_per_module': metrics['avg_dependencies_per_module'],
            'circular_dependencies': cycles,
            'high_coupling_modules': metrics['high_coupling_modules'],
            'score': score,
            'max_score': 20
        }

    def run_full_assessment(self, project_root: str = ".") -> Dict[str, Any]:
        logger.info("[ARCH_AGENT] Starting full architecture quality assessment...")
        start = time.time()
        project_root = os.path.abspath(project_root)

        solid_result = self.analyze_solid_principles(project_root)
        dep_result = self.analyze_dependencies(project_root)

        total_score = solid_result['score'] + dep_result['score']
        total_max = solid_result['max_score'] + dep_result['max_score']
        percentage = round((total_score / total_max) * 100) if total_max > 0 else 0

        grade = 'A' if percentage >= 90 else 'B' if percentage >= 75 else 'C' if percentage >= 60 else 'D'

        report = {
            'agent_id': self.agent_id,
            'assessment_time': datetime.now().isoformat(),
            'duration_seconds': round(time.time() - start, 2),
            'project_root': project_root,
            'summary': {
                'total_score': total_score,
                'max_score': total_max,
                'percentage': percentage,
                'grade': grade
            },
            'dimensions': {
                'solid_principles': solid_result,
                'dependency_analysis': dep_result
            },
            'recommendations': self._generate_recommendations(solid_result, dep_result)
        }

        self.report_history.append(report)
        self._save_report(report, project_root)
        return report

    def _generate_recommendations(self, solid_result: Dict[str, Any], dep_result: Dict[str, Any]) -> List[Dict[str, str]]:
        recs = []
        if solid_result['total_issues'] > 0:
            for principle, issues in solid_result['issues'].items():
                if issues:
                    if principle == 'SRP':
                        recs.append({'principle': 'SRP', 'priority': 'high', 'suggestion': 'Split large classes with too many methods/responsibilities'})
                    elif principle == 'ISP':
                        recs.append({'principle': 'ISP', 'priority': 'medium', 'suggestion': 'Reduce method parameters, consider using parameter objects'})
                    elif principle == 'DIP':
                        recs.append({'principle': 'DIP', 'priority': 'high', 'suggestion': 'Introduce dependency injection, high-level modules should depend on abstractions'})
        if dep_result.get('circular_dependencies'):
            recs.append({'principle': 'CIRCULAR_DEPS', 'priority': 'high', 'suggestion': f"Fix {len(dep_result['circular_dependencies'])} circular dependencies to improve maintainability"})
        if dep_result.get('high_coupling_modules'):
            recs.append({'principle': 'HIGH_COUPLING', 'priority': 'medium', 'suggestion': f"Refactor {len(dep_result['high_coupling_modules'])} high-coupling modules to reduce dependencies"})
        if not recs:
            recs.append({'principle': 'ALL_GOOD', 'priority': 'low', 'suggestion': 'Architecture quality is satisfactory. Continue maintaining current practices.'})
        return recs

    def _save_report(self, report: Dict[str, Any], project_root: str):
        config = self.config.get('analysis', {}).get('report', {})
        output_dir = config.get('output_dir', 'reports/architecture')
        output_path = Path(project_root) / output_dir
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if config.get('save_json', True):
            json_path = output_path / f'architecture_quality_report_{timestamp}.json'
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"[ARCH_AGENT] JSON report saved: {json_path}")

        if config.get('save_markdown', True):
            self._save_markdown_report(report, output_path, timestamp)

    def _save_markdown_report(self, report: Dict[str, Any], output_path: Path, timestamp: str):
        md_path = output_path / f'architecture_quality_report_{timestamp}.md'
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(f"# Architecture Quality Assessment Report\n\n")
            f.write(f"**Agent ID:** {report['agent_id']}\n")
            f.write(f"**Assessment Time:** {report['assessment_time']}\n")
            f.write(f"**Duration:** {report['duration_seconds']}s\n")
            f.write(f"**Project Root:** {report['project_root']}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- **Total Score:** {report['summary']['total_score']}/{report['summary']['max_score']}\n")
            f.write(f"- **Percentage:** {report['summary']['percentage']}%\n")
            f.write(f"- **Grade:** {report['summary']['grade']}\n\n")

            f.write(f"## Dimensions\n\n")
            solid = report['dimensions']['solid_principles']
            dep = report['dimensions']['dependency_analysis']
            f.write(f"### SOLID Principles\n")
            f.write(f"- Score: {solid['score']}/{solid['max_score']}\n")
            f.write(f"- Files analyzed: {solid['stats']['files_analyzed']}\n")
            f.write(f"- Classes found: {solid['stats']['classes_found']}\n")
            f.write(f"- Total issues: {solid['total_issues']}\n")
            for principle, issues in solid['issues'].items():
                if issues:
                    f.write(f"- {principle} violations: {len(issues)}\n")
                    for issue in issues[:5]:
                        f.write(f"  - {issue}\n")
            f.write(f"\n### Dependency Analysis\n")
            f.write(f"- Score: {dep['score']}/{dep['max_score']}\n")
            f.write(f"- Total modules: {dep['total_modules']}\n")
            f.write(f"- Total dependencies: {dep['total_dependencies']}\n")
            f.write(f"- Circular dependencies: {len(dep.get('circular_dependencies', []))}\n")
            if dep.get('high_coupling_modules'):
                f.write(f"- High coupling modules: {len(dep['high_coupling_modules'])}\n")

            f.write(f"\n## Recommendations\n")
            for rec in report.get('recommendations', []):
                f.write(f"- [{rec['priority'].upper()}] {rec['principle']}: {rec['suggestion']}\n")
        logger.info(f"[ARCH_AGENT] Markdown report saved: {md_path}")

    def get_report_history(self) -> List[Dict[str, Any]]:
        return self.report_history

    def get_agent_stats(self) -> Dict[str, Any]:
        return {
            'agent_id': self.agent_id,
            'start_time': self.start_time.isoformat(),
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'total_assessments': len(self.report_history),
            'last_assessment': self.report_history[-1]['summary'] if self.report_history else None
        }

    def shutdown(self):
        uptime = (datetime.now() - self.start_time).total_seconds()
        logger.info(f"[ARCH_AGENT] Architecture Quality Agent shutting down: {self.agent_id}")
        logger.info(f"[ARCH_AGENT] Uptime: {uptime:.1f}s, Assessments: {len(self.report_history)}")
        return {'status': 'shutdown', 'agent_id': self.agent_id, 'uptime_seconds': uptime, 'total_assessments': len(self.report_history)}


def create_parser():
    parser = argparse.ArgumentParser(description='Architecture Quality Assessment Agent')
    subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)

    assess_parser = subparsers.add_parser('assess', help='Run full architecture quality assessment')
    assess_parser.add_argument('--project-root', default='.', help='Project root directory')
    assess_parser.add_argument('--config', help='Path to configuration file')
    assess_parser.add_argument('--output', help='Output report path (overrides config)')

    solid_parser = subparsers.add_parser('solid', help='Run SOLID principles check only')
    solid_parser.add_argument('--project-root', default='.', help='Project root directory')

    dep_parser = subparsers.add_parser('deps', help='Run dependency analysis only')
    dep_parser.add_argument('--project-root', default='.', help='Project root directory')

    subparsers.add_parser('stats', help='Show agent statistics')
    subparsers.add_parser('stop', help='Stop the agent')

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    agent = ArchitectureQualityAgent(config_path=getattr(args, 'config', None))

    try:
        if args.command == 'assess':
            report = agent.run_full_assessment(args.project_root)
            s = report['summary']
            print(f"\n{'='*60}")
            print(f"ARCHITECTURE QUALITY ASSESSMENT COMPLETE")
            print(f"{'='*60}")
            print(f"Score: {s['total_score']}/{s['max_score']} ({s['percentage']}%)")
            print(f"Grade: {s['grade']}")
            print(f"Duration: {report['duration_seconds']}s")
            print(f"\nRecommendations:")
            for rec in report['recommendations']:
                print(f"  [{rec['priority'].upper()}] {rec['suggestion']}")
            print(f"{'='*60}")

        elif args.command == 'solid':
            result = agent.analyze_solid_principles(args.project_root)
            print(f"\nSOLID Principles Analysis:")
            print(f"  Score: {result['score']}/{result['max_score']}")
            print(f"  Files analyzed: {result['stats']['files_analyzed']}")
            print(f"  Total issues: {result['total_issues']}")
            for principle, issues in result['issues'].items():
                if issues:
                    print(f"\n  {principle} ({len(issues)} issues):")
                    for issue in issues[:5]:
                        print(f"    - {issue}")
                    if len(issues) > 5:
                        print(f"    ... and {len(issues)-5} more")

        elif args.command == 'deps':
            result = agent.analyze_dependencies(args.project_root)
            print(f"\nDependency Analysis:")
            print(f"  Score: {result['score']}/{result['max_score']}")
            print(f"  Modules: {result['total_modules']}")
            print(f"  Dependencies: {result['total_dependencies']}")
            print(f"  Avg deps/module: {result['avg_dependencies_per_module']:.2f}")
            if result.get('circular_dependencies'):
                print(f"\n  Circular Dependencies ({len(result['circular_dependencies'])}):")
                for cycle in result['circular_dependencies']:
                    print(f"    {' -> '.join(cycle)}")
            if result.get('high_coupling_modules'):
                print(f"\n  High Coupling Modules:")
                for mod, score in result['high_coupling_modules']:
                    print(f"    {mod}: {score} deps")

        elif args.command == 'stats':
            stats = agent.get_agent_stats()
            print(f"\nAgent Statistics:")
            for k, v in stats.items():
                if isinstance(v, float):
                    print(f"  {k}: {v:.1f}")
                else:
                    print(f"  {k}: {v}")

        elif args.command == 'stop':
            result = agent.shutdown()
            print(f"Agent stopped. Uptime: {result['uptime_seconds']:.1f}s, Assessments: {result['total_assessments']}")

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        agent.shutdown()
    except Exception as e:
        logger.exception(f"Error: {e}")
        print(f"Error: {e}")
        agent.shutdown()


if __name__ == '__main__':
    main()
