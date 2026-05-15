# Architecture Quality Assessment Agent

## Overview

The Architecture Quality Assessment Agent evaluates Python project architecture by analyzing SOLID principle compliance and module dependency structures. It generates comprehensive quality reports with scores, grades, and actionable recommendations.

## Quick Start

```bash
# Run full architecture quality assessment
python architecture_agent.py assess

# Run with custom project root
python architecture_agent.py assess --project-root /path/to/project

# Run with custom config
python architecture_agent.py assess --config config/architecture_config.yaml
```

## Commands

| Command | Description |
|---------|-------------|
| `assess` | Run full architecture quality assessment (SOLID + dependencies) |
| `solid` | Run SOLID principles check only |
| `deps` | Run dependency analysis only |
| `stats` | Show agent statistics |
| `stop` | Stop the agent |

### Examples

```bash
# SOLID principles check
python architecture_agent.py solid --project-root .

# Dependency analysis
python architecture_agent.py deps --project-root .

# View agent stats
python architecture_agent.py stats
```

## Configuration

Configuration file: `config/architecture_config.yaml`

```yaml
architecture_agent:
  analysis:
    solid_principles:
      enabled: true
      max_methods_per_class: 12      # Max methods before SRP warning
      max_method_lines: 80           # Max lines per method
      max_function_params: 8         # Max params for functions
      max_method_params: 6           # Max params for methods
    dependency_analysis:
      enabled: true
      max_dependencies_per_module: 5  # Coupling threshold
      detect_circular: true          # Detect circular dependencies
    report:
      output_dir: "reports/architecture"
      save_json: true
      save_markdown: true
```

## Assessment Dimensions

| Dimension | Max Score | Description |
|-----------|-----------|-------------|
| SOLID Principles | 20 | Checks SRP (class size), ISP (parameter count), DIP (dependency direction) |
| Dependency Analysis | 20 | Module coupling, circular dependencies, stability |

## Scoring

| Grade | Score % | Meaning |
|-------|---------|---------|
| A | >= 90% | Excellent architecture |
| B | >= 75% | Good architecture, minor improvements |
| C | >= 60% | Satisfactory, needs improvement |
| D | < 60% | Major architectural issues |

## Reports

Reports are saved to `reports/architecture/` as both JSON and Markdown:
- `architecture_quality_report_<timestamp>.json` - Machine-readable
- `architecture_quality_report_<timestamp>.md` - Human-readable

## Programmatic Usage

```python
from architecture_agent import ArchitectureQualityAgent

agent = ArchitectureQualityAgent()
report = agent.run_full_assessment(".")
print(f"Score: {report['summary']['percentage']}%")
print(f"Grade: {report['summary']['grade']}")

for rec in report['recommendations']:
    print(f"[{rec['priority']}] {rec['suggestion']}")
```

## Integration with Opencode Agent System

Registered CLI entry point:
```bash
pythoncode-arch-agent assess
```
