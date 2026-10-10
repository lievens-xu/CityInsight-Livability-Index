"""Fail on errors, report missing coverage without turning it into zero."""
import json
from model import BASE_DIR, RAW_INDICATORS, build_indicators, read_csv_safely, validate_indicators
import pandas as pd


def main():
    cities = read_csv_safely(BASE_DIR / "data/raw/city_basic.csv")
    source = read_csv_safely(BASE_DIR / "data/raw/data_source_tracking_2024.csv")
    indicators = read_csv_safely(BASE_DIR / "data/raw/city_indicators_2024_mvp.csv")
    expected = build_indicators(cities, source)
    validate_indicators(cities, indicators)
    pd.testing.assert_frame_equal(
        indicators.sort_values(["year", "city_id"]).reset_index(drop=True), expected,
        check_dtype=False, check_exact=False, rtol=1e-12, atol=1e-12,
    )
    report = {
        "valid": True, "city_year_rows": len(indicators),
        "missing_by_indicator": {col: int(indicators[col].isna().sum()) for col in RAW_INDICATORS},
        "coverage": [{"city_id": int(row.city_id), "year": int(row.year),
                      "available": int(indicators.loc[index, RAW_INDICATORS].notna().sum()),
                      "expected": len(RAW_INDICATORS)} for index, row in indicators.iterrows()],
    }
    path = BASE_DIR / "data/processed/data_quality_2024.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
