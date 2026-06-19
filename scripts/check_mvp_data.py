from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]

CITY_BASIC_PATH = BASE_DIR / "data" / "raw" / "city_basic.csv"
INDICATOR_PATH = BASE_DIR / "data" / "raw" / "city_indicators_2024_mvp.csv"
SOURCE_TRACKING_PATH = BASE_DIR / "data" / "raw" / "data_source_tracking_2024.csv"


def read_csv_safely(path):
    encodings = ["utf-8-sig", "utf-8", "gbk", "gb18030"]

    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue

    raise ValueError(f"Cannot decode file: {path}")


def main():
    city_basic = read_csv_safely(CITY_BASIC_PATH)
    indicators = read_csv_safely(INDICATOR_PATH)
    source = read_csv_safely(SOURCE_TRACKING_PATH)

    print("=" * 60)
    print("1. Basic shape")
    print("=" * 60)
    print("city_basic:", city_basic.shape)
    print("city_indicators:", indicators.shape)
    print("source_tracking:", source.shape)

    print("\n" + "=" * 60)
    print("2. City ID check")
    print("=" * 60)

    expected_city_ids = set(city_basic["city_id"])
    actual_city_ids = set(indicators["city_id"])

    print("Expected city_ids:", sorted(expected_city_ids))
    print("Actual city_ids:", sorted(actual_city_ids))
    print("Missing city_ids:", expected_city_ids - actual_city_ids)
    print("Extra city_ids:", actual_city_ids - expected_city_ids)

    print("\n" + "=" * 60)
    print("3. Missing values")
    print("=" * 60)
    print(indicators.isna().sum())

    print("\n" + "=" * 60)
    print("4. Duplicate check")
    print("=" * 60)

    duplicated = indicators.duplicated(subset=["city_id", "year"])
    print("Duplicated rows:", duplicated.sum())

    if duplicated.sum() > 0:
        print(indicators[duplicated])

    print("\n" + "=" * 60)
    print("5. Data type check")
    print("=" * 60)
    print(indicators.dtypes)

    print("\n" + "=" * 60)
    print("6. Simple range check")
    print("=" * 60)

    range_rules = {
        "gdp_per_capita": (50000, 300000),
        "house_price": (5000, 100000),
        "pm25": (0, 100),
        "good_air_days_ratio": (0, 100),
    }

    for col, (lower, upper) in range_rules.items():
        if col in indicators.columns:
            abnormal = indicators[
                indicators[col].notna()
                & ((indicators[col] < lower) | (indicators[col] > upper))
            ]

            if abnormal.empty:
                print(f"{col}: OK")
            else:
                print(f"{col}: abnormal values found")
                print(abnormal[["city_id", "year", col]])

    print("\n" + "=" * 60)
    print("7. Preview")
    print("=" * 60)
    print(indicators)


if __name__ == "__main__":
    main()