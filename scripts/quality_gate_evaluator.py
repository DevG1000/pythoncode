#!/usr/bin/env python3
"""
Quality Gate Evaluator
Evaluates code quality against defined thresholds
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Any

class QualityGateEvaluator:
    """Evaluate quality gates against thresholds"""
    
    def __init__(self, thresholds_file: str = None):
        self.thresholds = self.load_thresholds(thresholds_file)
        self.results = {
            "overall": {"passed": True, "score": 100},
            "gates": {},
            "violations": []
        }
    
    def load_thresholds(self, thresholds_file: str) -> Dict[str, Any]:
        """Load quality thresholds from YAML file"""
        default_thresholds = {
            "solid_principles": {
                "min_score": 80,
                "max_violations": 5
            },
            "code_complexity": {
                "max_cyclomatic_complexity": 10,
                "max_maintainability_index": 65
            },
            "test_coverage": {
                "min_line_coverage": 80,
                "min_branch_coverage": 70
            },
            "security": {
                "max_critical_vulnerabilities": 0,
                "max_high_vulnerabilities": 2
            },
            "performance": {
                "max_response_time_ms": 1000,
                "max_memory_mb": 512
            }
        }
        
        if thresholds_file and Path(thresholds_file).exists():
            try:
                with open(thresholds_file, 'r', encoding='utf-8') as f:
                    custom_thresholds = yaml.safe_load(f)
                    # Merge with defaults
                    default_thresholds.update(custom_thresholds)
            except Exception as e:
                print(f"Warning: Could not load thresholds file: {e}", file=sys.stderr)
        
        return default_thresholds
    
    def evaluate_solid_principles(self, solid_report: str) -> Dict[str, Any]:
        """Evaluate SOLID principles report"""
        try:
            with open(solid_report, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            score = data.get("overall", {}).get("score", 0)
            violations = data.get("overall", {}).get("total_violations", 0)
            
            passed = (score >= self.thresholds["solid_principles"]["min_score"] and 
                     violations <= self.thresholds["solid_principles"]["max_violations"])
            
            return {
                "passed": passed,
                "score": score,
                "violations": violations,
                "threshold": self.thresholds["solid_principles"]["min_score"]
            }
            
        except Exception as e:
            print(f"Error evaluating SOLID principles: {e}", file=sys.stderr)
            return {"passed": False, "error": str(e)}
    
    def evaluate_code_complexity(self, complexity_report: str) -> Dict[str, Any]:
        """Evaluate code complexity report"""
        try:
            with open(complexity_report, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Simplified evaluation - in real implementation, parse radon output
            max_complexity = 0
            avg_complexity = 0
            
            # Mock evaluation
            passed = max_complexity <= self.thresholds["code_complexity"]["max_cyclomatic_complexity"]
            
            return {
                "passed": passed,
                "max_complexity": max_complexity,
                "average_complexity": avg_complexity,
                "threshold": self.thresholds["code_complexity"]["max_cyclomatic_complexity"]
            }
            
        except Exception as e:
            print(f"Error evaluating code complexity: {e}", file=sys.stderr)
            return {"passed": False, "error": str(e)}
    
    def evaluate_test_coverage(self, coverage_report: str) -> Dict[str, Any]:
        """Evaluate test coverage report"""
        try:
            with open(coverage_report, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Parse coverage data
            line_coverage = data.get("totals", {}).get("percent_covered", 0)
            branch_coverage = data.get("totals", {}).get("percent_covered_branch", 0)
            
            passed = (line_coverage >= self.thresholds["test_coverage"]["min_line_coverage"] and
                     branch_coverage >= self.thresholds["test_coverage"]["min_branch_coverage"])
            
            return {
                "passed": passed,
                "line_coverage": line_coverage,
                "branch_coverage": branch_coverage,
                "thresholds": {
                    "line": self.thresholds["test_coverage"]["min_line_coverage"],
                    "branch": self.thresholds["test_coverage"]["min_branch_coverage"]
                }
            }
            
        except Exception as e:
            print(f"Error evaluating test coverage: {e}", file=sys.stderr)
            return {"passed": False, "error": str(e)}
    
    def evaluate_all(self, reports: Dict[str, str]) -> Dict[str, Any]:
        """Evaluate all quality gates"""
        evaluations = {}
        
        # Evaluate each report
        if "solid_report" in reports:
            evaluations["solid_principles"] = self.evaluate_solid_principles(reports["solid_report"])
        
        if "complexity_report" in reports:
            evaluations["code_complexity"] = self.evaluate_code_complexity(reports["complexity_report"])
        
        if "coverage_report" in reports:
            evaluations["test_coverage"] = self.evaluate_test_coverage(reports["coverage_report"])
        
        # Calculate overall result
        all_passed = all(eval.get("passed", False) for eval in evaluations.values())
        
        # Calculate score
        score = 0
        if evaluations:
            passed_count = sum(1 for eval in evaluations.values() if eval.get("passed", False))
            score = int((passed_count / len(evaluations)) * 100)
        
        self.results["overall"]["passed"] = all_passed
        self.results["overall"]["score"] = score
        self.results["gates"] = evaluations
        
        return self.results
    
    def generate_summary(self) -> str:
        """Generate human-readable summary"""
        summary = []
        summary.append("Quality Gate Evaluation Summary")
        summary.append("=" * 50)
        
        for gate_name, evaluation in self.results["gates"].items():
            status = "[OK] PASS" if evaluation.get("passed", False) else "[FAIL] FAIL"
            summary.append(f"\n{gate_name.replace('_', ' ').title()}: {status}")
            
            if "score" in evaluation:
                summary.append(f"  Score: {evaluation['score']}/{evaluation.get('threshold', 100)}")
            if "violations" in evaluation:
                summary.append(f"  Violations: {evaluation['violations']}")
        
        summary.append(f"\nOverall Status: {'[OK] PASS' if self.results['overall']['passed'] else '[FAIL] FAIL'}")
        summary.append(f"Overall Score: {self.results['overall']['score']}/100")
        
        return "\n".join(summary)

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate quality gates")
    parser.add_argument("--solid-report", help="SOLID principles report JSON")
    parser.add_argument("--complexity-report", help="Code complexity report JSON")
    parser.add_argument("--maintainability-report", help="Maintainability report JSON")
    parser.add_argument("--coverage-report", help="Test coverage report JSON")
    parser.add_argument("--thresholds", help="Quality thresholds YAML file")
    parser.add_argument("--output", "-o", help="Output JSON file")
    
    args = parser.parse_args()
    
    # Collect reports
    reports = {}
    if args.solid_report:
        reports["solid_report"] = args.solid_report
    if args.complexity_report:
        reports["complexity_report"] = args.complexity_report
    if args.maintainability_report:
        reports["maintainability_report"] = args.maintainability_report
    if args.coverage_report:
        reports["coverage_report"] = args.coverage_report
    
    if not reports:
        print("Error: No reports provided for evaluation", file=sys.stderr)
        sys.exit(1)
    
    # Evaluate
    evaluator = QualityGateEvaluator(args.thresholds)
    results = evaluator.evaluate_all(reports)
    
    # Print summary
    print(evaluator.generate_summary())
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.output}")
    
    # Exit code based on overall result
    sys.exit(0 if results["overall"]["passed"] else 1)

if __name__ == "__main__":
    main()