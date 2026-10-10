"""One command for the validated, offline pipeline. Stop on the first failure."""
from pathlib import Path
import subprocess
import sys


def main():
    scripts = Path(__file__).resolve().parent
    for name in ("build_mvp_indicator_table.py", "check_mvp_data.py", "calculate_livability_scores.py", "analyze_scenarios.py", "create_basic_charts.py", "export_dashboard_data.py", "create_analysis_report.py"):
        subprocess.run([sys.executable, str(scripts / name)], check=True)


if __name__ == "__main__":
    main()
