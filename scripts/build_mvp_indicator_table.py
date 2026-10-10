"""Build all city/year rows; reject invalid observations and ambiguous sources."""
from model import BASE_DIR, build_indicators, read_csv_safely


def main():
    result = build_indicators(
        read_csv_safely(BASE_DIR / "data/raw/city_basic.csv"),
        read_csv_safely(BASE_DIR / "data/raw/data_source_tracking_2024.csv"),
    )
    path = BASE_DIR / "data/raw/city_indicators_2024_mvp.csv"
    result.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"Built {len(result)} city/year rows: {path}")


if __name__ == "__main__":
    main()
