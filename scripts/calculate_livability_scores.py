from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]

CITY_BASIC_PATH = BASE_DIR / "data" / "raw" / "city_basic.csv"
INDICATOR_PATH = BASE_DIR / "data" / "raw" / "city_indicators_2024_mvp.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "livability_scores_2024.csv"


def read_csv_safely(path):
    encodings = ["utf-8-sig", "utf-8", "gbk", "gb18030"]

    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue

    raise ValueError(f"Cannot decode file: {path}")


def min_max_score(series, positive=True):
    """
    Convert a numeric indicator into a 0-100 score.

    positive=True  means higher is better.
    positive=False means lower is better.
    """
    series = pd.to_numeric(series, errors="coerce")

    min_value = series.min(skipna=True)
    max_value = series.max(skipna=True)

    if pd.isna(min_value) or pd.isna(max_value):
        return pd.Series([pd.NA] * len(series), index=series.index)

    if max_value == min_value:
        return pd.Series([50] * len(series), index=series.index)

    if positive:
        score = (series - min_value) / (max_value - min_value) * 100
    else:
        score = (max_value - series) / (max_value - min_value) * 100

    return score.round(1)


def average_available_scores(df, columns):
    """
    Calculate row-wise average using available indicator scores.
    Missing values are ignored.
    """
    existing_columns = [col for col in columns if col in df.columns]

    if not existing_columns:
        return pd.Series([pd.NA] * len(df), index=df.index)

    temp = df[existing_columns].copy()

    # 强制把所有列转成数值型，无法转换的变成 NaN
    for col in existing_columns:
        temp[col] = pd.to_numeric(temp[col], errors="coerce")

    return temp.mean(axis=1, skipna=True).round(1)


def main():
    city_basic = read_csv_safely(CITY_BASIC_PATH)
    indicators = read_csv_safely(INDICATOR_PATH)

    # Merge city names
    df = indicators.merge(
        city_basic[["city_id", "city_name"]],
        on="city_id",
        how="left"
    )

    # Positive indicators
    positive_indicators = [
        "gdp_per_capita",
        "avg_salary_non_private",
        "avg_salary_private",
        "tertiary_industry_ratio",
        "hospital_count",
        "university_count",
        "metro_station_count",
        "good_air_days_ratio",
        "park_count",
    ]

    # Negative indicators
    negative_indicators = [
        "house_price",
        "avg_rent",
        "house_price_income_ratio_non_private",
        "house_price_income_ratio_private",
        "pm25",
    ]

    # Create normalized score columns
    for col in positive_indicators:
        if col in df.columns:
            df[col + "_score"] = min_max_score(df[col], positive=True)

    for col in negative_indicators:
        if col in df.columns:
            df[col + "_score"] = min_max_score(df[col], positive=False)

    # Dimension score definitions
    economy_score_columns = [
        "gdp_per_capita_score",
        "avg_salary_non_private_score",
        "avg_salary_private_score",
        "tertiary_industry_ratio_score",
    ]

    cost_score_columns = [
        "house_price_score",
        "avg_rent_score",
        "house_price_income_ratio_non_private_score",
        "house_price_income_ratio_private_score",
    ]

    service_score_columns = [
        "hospital_count_score",
        "university_count_score",
        "metro_station_count_score",
    ]

    environment_score_columns = [
        "pm25_score",
        "good_air_days_ratio_score",
        "park_count_score",
    ]

    # Calculate dimension scores
    df["economy_score"] = average_available_scores(df, economy_score_columns)
    df["cost_score"] = average_available_scores(df, cost_score_columns)
    df["service_score"] = average_available_scores(df, service_score_columns)
    df["environment_score"] = average_available_scores(df, environment_score_columns)

    # MVP weights
    weights = {
        "economy_score": 0.35,
        "cost_score": 0.30,
        "service_score": 0.20,
        "environment_score": 0.15,
    }

    # Calculate total score
    df["total_score"] = (
        df["economy_score"] * weights["economy_score"]
        + df["cost_score"] * weights["cost_score"]
        + df["service_score"] * weights["service_score"]
        + df["environment_score"] * weights["environment_score"]
    ).round(1)

    # Ranking
    df["rank"] = df["total_score"].rank(ascending=False, method="min").astype("Int64")

    # Output columns
    output_columns = [
        "city_id",
        "city_name",
        "year",
        "economy_score",
        "cost_score",
        "service_score",
        "environment_score",
        "total_score",
        "rank",
    ]

    result = df[output_columns].sort_values("rank")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Generated: {OUTPUT_PATH}")
    print(result)


if __name__ == "__main__":
    main()