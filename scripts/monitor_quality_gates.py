#!/usr/bin/env python3
"""
Quality Gate Monitoring Script
Monitors the performance and effectiveness of quality gates over time.
"""

import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import yaml


class QualityGateMonitor:
    """Monitor quality gate performance and effectiveness"""

    def __init__(self, data_dir=".github/quality-metrics"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load thresholds
        self.quality_thresholds = self._load_thresholds("quality-gates-thresholds.yaml")
        self.performance_thresholds = self._load_thresholds("performance-thresholds.yaml")
        self.security_thresholds = self._load_thresholds("security-thresholds.yaml")

    def _load_thresholds(self, filename):
        """Load thresholds from YAML file"""
        filepath = Path(filename)
        if not filepath.exists():
            print(f"[WARNING] {filename} not found, using defaults")
            return {}

        try:
            with open(filepath, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"[ERROR] Error loading {filename}: {e}")
            return {}

    def record_quality_run(self, run_data):
        """Record quality gate run data"""
        timestamp = datetime.now().isoformat()
        run_id = run_data.get("run_id", f"run_{timestamp}")

        # Create run record
        run_record = {
            "timestamp": timestamp,
            "run_id": run_id,
            "data": run_data,
            "metadata": {
                "branch": run_data.get("branch", "unknown"),
                "commit": run_data.get("commit", "unknown"),
                "trigger": run_data.get("trigger", "unknown"),
            },
        }

        # Save to file
        run_file = self.data_dir / f"run_{run_id}.json"
        with open(run_file, "w") as f:
            json.dump(run_record, f, indent=2)

        print(f"[INFO] Recorded quality run: {run_id}")
        return run_id

    def analyze_trends(self, days=30):
        """Analyze quality gate trends over time"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        runs = self._load_runs_in_range(start_date, end_date)

        if not runs:
            print(f"[WARNING] No quality gate runs found in the last {days} days")
            return {}

        print(f"\n[TRENDS] Quality Gate Trends Analysis ({len(runs)} runs)")
        print("=" * 60)

        trends = {
            "total_runs": len(runs),
            "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
            "summary": self._calculate_summary(runs),
            "by_category": self._analyze_by_category(runs),
            "failures": self._analyze_failures(runs),
            "improvements": self._identify_improvements(runs),
        }

        # Print summary
        self._print_summary(trends["summary"])

        # Save trends report
        trends_file = self.data_dir / f"trends_{end_date.strftime('%Y%m%d')}.json"
        with open(trends_file, "w") as f:
            json.dump(trends, f, indent=2)

        print(f"\n[INFO] Trends report saved to: {trends_file}")
        return trends

    def _load_runs_in_range(self, start_date, end_date):
        """Load runs within date range"""
        runs = []

        for run_file in self.data_dir.glob("run_*.json"):
            try:
                with open(run_file, "r") as f:
                    run_data = json.load(f)

                run_time = datetime.fromisoformat(run_data["timestamp"])
                if start_date <= run_time <= end_date:
                    runs.append(run_data)
            except Exception as e:
                print(f"[WARNING] Error loading {run_file}: {e}")

        # Sort by timestamp
        runs.sort(key=lambda x: x["timestamp"])
        return runs

    def _calculate_summary(self, runs):
        """Calculate summary statistics"""
        total_runs = len(runs)
        passed_runs = sum(1 for r in runs if r["data"].get("overall_passed", False))
        failed_runs = total_runs - passed_runs

        # Calculate average scores
        scores = []
        for run in runs:
            if "scores" in run["data"]:
                scores.append(run["data"]["scores"].get("total", 0))

        avg_score = sum(scores) / len(scores) if scores else 0

        return {
            "total_runs": total_runs,
            "passed_runs": passed_runs,
            "failed_runs": failed_runs,
            "pass_rate": (passed_runs / total_runs * 100) if total_runs > 0 else 0,
            "average_score": avg_score,
            "success_rate_trend": self._calculate_trend(runs, "overall_passed"),
        }

    def _analyze_by_category(self, runs):
        """Analyze performance by quality category"""
        categories = {
            "code_quality": {"total": 0, "passed": 0, "failed": 0},
            "security": {"total": 0, "passed": 0, "failed": 0},
            "testing": {"total": 0, "passed": 0, "failed": 0},
            "performance": {"total": 0, "passed": 0, "failed": 0},
            "architecture": {"total": 0, "passed": 0, "failed": 0},
        }

        for run in runs:
            data = run["data"]

            # Check each category
            for category in categories.keys():
                categories[category]["total"] += 1

                # Check if category passed (simplified logic)
                if category in data.get("passed_categories", []):
                    categories[category]["passed"] += 1
                else:
                    categories[category]["failed"] += 1

        # Calculate pass rates
        for category in categories:
            total = categories[category]["total"]
            passed = categories[category]["passed"]
            categories[category]["pass_rate"] = (passed / total * 100) if total > 0 else 0

        return categories

    def _analyze_failures(self, runs):
        """Analyze failure patterns"""
        failures = defaultdict(int)

        for run in runs:
            if not run["data"].get("overall_passed", False):
                # Record failure reasons
                failure_reasons = run["data"].get("failure_reasons", ["unknown"])
                for reason in failure_reasons:
                    failures[reason] += 1

        return dict(failures)

    def _identify_improvements(self, runs):
        """Identify areas for improvement"""
        improvements = []

        # Check code quality trends
        code_scores = []
        for run in runs:
            if "scores" in run["data"]:
                code_scores.append(run["data"]["scores"].get("code_quality", 0))

        if code_scores:
            avg_code_score = sum(code_scores) / len(code_scores)
            if avg_code_score < self.quality_thresholds.get("code_quality", {}).get("pylint_score", 7.0):
                improvements.append(
                    {
                        "area": "code_quality",
                        "issue": f"Average code quality score ({avg_code_score:.1f}) below threshold",
                        "recommendation": "Improve code structure and reduce complexity",
                    }
                )

        # Check security trends
        security_issues = []
        for run in runs:
            if "security_issues" in run["data"]:
                security_issues.extend(run["data"]["security_issues"])

        if security_issues:
            improvements.append(
                {
                    "area": "security",
                    "issue": f"{len(security_issues)} security issues detected",
                    "recommendation": "Address security vulnerabilities and update dependencies",
                }
            )

        return improvements

    def _calculate_trend(self, runs, metric_key):
        """Calculate trend for a metric"""
        if len(runs) < 2:
            return "insufficient_data"

        # Get metric values over time
        values = []
        for run in runs:
            if metric_key in run["data"]:
                values.append(1 if run["data"][metric_key] else 0)

        if len(values) < 2:
            return "insufficient_data"

        # Simple trend calculation
        first_half = values[: len(values) // 2]
        second_half = values[len(values) // 2 :]

        avg_first = sum(first_half) / len(first_half) if first_half else 0
        avg_second = sum(second_half) / len(second_half) if second_half else 0

        if avg_second > avg_first + 0.1:
            return "improving"
        elif avg_second < avg_first - 0.1:
            return "declining"
        else:
            return "stable"

    def _print_summary(self, summary):
        """Print summary statistics"""
        print(f"\n[STATS] Summary Statistics:")
        print(f"  Total Runs: {summary['total_runs']}")
        print(f"  Passed Runs: {summary['passed_runs']}")
        print(f"  Failed Runs: {summary['failed_runs']}")
        print(f"  Pass Rate: {summary['pass_rate']:.1f}%")
        print(f"  Average Score: {summary['average_score']:.1f}")

        trend = summary.get("success_rate_trend", "unknown")
        trend_symbol = "[UP]" if trend == "improving" else "[DOWN]" if trend == "declining" else "[SAME]"
        print(f"  Success Rate Trend: {trend_symbol} {trend}")

    def generate_report(self, days=30):
        """Generate comprehensive monitoring report"""
        trends = self.analyze_trends(days)

        if not trends:
            return

        print(f"\n[ANALYSIS] Detailed Analysis:")
        print("=" * 60)

        # Category performance
        print(f"\n[CATEGORY] Category Performance:")
        for category, stats in trends["by_category"].items():
            pass_rate = stats.get("pass_rate", 0)
            status = "[PASS]" if pass_rate >= 90 else "[WARN]" if pass_rate >= 70 else "[FAIL]"
            print(f"  {status} {category.replace('_', ' ').title()}: {pass_rate:.1f}%")

        # Failure analysis
        if trends["failures"]:
            print(f"\n[FAILURE] Failure Analysis:")
            for reason, count in trends["failures"].items():
                percentage = (count / trends["summary"]["failed_runs"] * 100) if trends["summary"]["failed_runs"] > 0 else 0
                print(f"  • {reason}: {count} times ({percentage:.1f}% of failures)")

        # Improvement recommendations
        if trends["improvements"]:
            print(f"\n[RECOMMEND] Improvement Recommendations:")
            for improvement in trends["improvements"]:
                print(f"  • {improvement['area'].replace('_', ' ').title()}:")
                print(f"    Issue: {improvement['issue']}")
                print(f"    Recommendation: {improvement['recommendation']}")

        # Generate HTML report
        self._generate_html_report(trends, days)

    def _generate_html_report(self, trends, days):
        """Generate HTML report for visualization"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Quality Gate Monitoring Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .metric {{ background: #fff; border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .success {{ color: green; }}
                .warning {{ color: orange; }}
                .error {{ color: red; }}
                .category {{ display: inline-block; width: 200px; margin: 5px; padding: 10px; background: #f9f9f9; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Quality Gate Monitoring Report</h1>
                <p>Period: Last {days} days | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="metric">
                <h2>Summary Statistics</h2>
                <p>Total Runs: {trends['summary']['total_runs']}</p>
                <p>Pass Rate: <span class="{ 'success' if trends['summary']['pass_rate'] >= 90 else 'warning' if trends['summary']['pass_rate'] >= 70 else 'error' }">
                    {trends['summary']['pass_rate']:.1f}%
                </span></p>
                <p>Average Score: {trends['summary']['average_score']:.1f}</p>
            </div>
            
            <div class="metric">
                <h2>Category Performance</h2>
        """

        for category, stats in trends["by_category"].items():
            pass_rate = stats.get("pass_rate", 0)
            html_content += f"""
                <div class="category">
                    <h3>{category.replace('_', ' ').title()}</h3>
                    <p>Pass Rate: {pass_rate:.1f}%</p>
                </div>
            """

        html_content += """
            </div>
            
            <div class="metric">
                <h2>Improvement Recommendations</h2>
        """

        if trends["improvements"]:
            for improvement in trends["improvements"]:
                html_content += f"""
                    <div style="margin: 10px 0; padding: 10px; background: #fff8e1;">
                        <h3>{improvement['area'].replace('_', ' ').title()}</h3>
                        <p><strong>Issue:</strong> {improvement['issue']}</p>
                        <p><strong>Recommendation:</strong> {improvement['recommendation']}</p>
                    </div>
                """
        else:
            html_content += "<p>No specific improvement recommendations at this time.</p>"

        html_content += """
            </div>
        </body>
        </html>
        """

        # Save HTML report
        report_file = self.data_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(report_file, "w") as f:
            f.write(html_content)

        print(f"\n[REPORT] HTML report generated: {report_file}")


def main():
    """Main function"""
    monitor = QualityGateMonitor()

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "analyze":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            monitor.generate_report(days)

        elif command == "record":
            # Simulate recording a run (in real usage, this would come from CI/CD)
            run_data = {
                "run_id": f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "branch": "main",
                "commit": "abc123",
                "trigger": "manual",
                "overall_passed": True,
                "passed_categories": ["code_quality", "security", "testing", "architecture"],
                "scores": {"code_quality": 8.5, "security": 95, "testing": 88, "architecture": 75, "total": 86.5},
                "failure_reasons": [],
            }
            monitor.record_quality_run(run_data)
            print("[SUCCESS] Recorded sample quality run")

        else:
            print(f"Unknown command: {command}")
            print("Usage: python monitor_quality_gates.py [analyze|record]")
    else:
        # Default: analyze last 30 days
        monitor.generate_report(30)


if __name__ == "__main__":
    main()
