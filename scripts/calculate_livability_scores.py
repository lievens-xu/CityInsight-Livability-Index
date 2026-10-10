"""Calculate explainable provisional scores within comparable annual cohorts."""
import argparse
import json
from model import BASE_DIR, WEIGHTS, calculate_scores, min_max_score, read_csv_safely


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", help='JSON object with economy, cost, service, environment weights')
    parser.add_argument("--output", type=str, default=str(BASE_DIR / "data/processed/livability_scores_2024.csv"))
    args = parser.parse_args()
    weights = json.loads(args.weights) if args.weights else WEIGHTS
    result, cohorts = calculate_scores(
        read_csv_safely(BASE_DIR / "data/raw/city_basic.csv"),
        read_csv_safely(BASE_DIR / "data/raw/city_indicators_2024_mvp.csv"), weights,
    )
    from pathlib import Path
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(path, index=False, encoding="utf-8-sig")
    path.with_suffix(".metadata.json").write_text(json.dumps({
        "weights": weights, "normalization": "within_year_common_indicators",
        "score_status": "provisional", "cohorts": cohorts,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(result[["city_name", "year", "coverage", "status", "total_score", "rank"]].to_string(index=False))


if __name__ == "__main__":
    main()
