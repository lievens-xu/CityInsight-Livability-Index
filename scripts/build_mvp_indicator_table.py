from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]

CITY_BASIC_PATH = BASE_DIR / "data" / "raw" / "city_basic.csv"
SOURCE_TRACKING_PATH = BASE_DIR / "data" / "raw" / "data_source_tracking_2024.csv"
OUTPUT_PATH = BASE_DIR / "data" / "raw" / "city_indicators_2024_mvp.csv"

MVP_COLUMNS = [
    "gdp_per_capita",
    "avg_salary_non_private",
    "avg_salary_private",
    "tertiary_industry_ratio",
    "house_price",
    "avg_rent",
    "hospital_count",
    "university_count",
    "metro_station_count",
    "pm25",
    "good_air_days_ratio",
    "park_count",
]

def main():
    def read_csv_safely(path):
        encodings = ["utf-8-sig", "utf-8", "gbk", "gb18030"]
    
        for enc in encodings:
            try:
                return pd.read_csv(path, encoding=enc)
            except UnicodeDecodeError:
                continue
    
        raise UnicodeDecodeError(
            "unknown",
            b"",
            0,
            1,
            f"Cannot decode file: {path}"
            )

    city_basic = read_csv_safely(CITY_BASIC_PATH)
    source = read_csv_safely(SOURCE_TRACKING_PATH)

    # 去掉没有 value 的行
    source = source.dropna(subset=["value"])
    source = source[source["value"].astype(str).str.strip() != ""]

    # value 转成数字
    source["value"] = pd.to_numeric(source["value"], errors="coerce")

    # 只保留 MVP 指标
    source = source[source["indicator"].isin(MVP_COLUMNS)]

    # 转成宽表：一行一个城市，一列一个指标
    pivot = source.pivot_table(
        index=["city", "year"],
        columns="indicator",
        values="value",
        aggfunc="first"
    ).reset_index()

    # 加入 city_id
    result = pivot.merge(
        city_basic[["city_id", "city_name"]],
        left_on="city",
        right_on="city_name",
        how="left"
    )

    result = result.drop(columns=["city", "city_name"])

    # 确保所有 MVP 列都存在
    for col in MVP_COLUMNS:
        if col not in result.columns:
            result[col] = pd.NA

    # 计算房价收入比
    # 假设标准住房面积为 90 平方米
    STANDARD_HOME_AREA = 90

    result["house_price_income_ratio_non_private"] = (
        result["house_price"] * STANDARD_HOME_AREA / result["avg_salary_non_private"]
    ).round(1)

    result["house_price_income_ratio_private"] = (
        result["house_price"] * STANDARD_HOME_AREA / result["avg_salary_private"]
    ).round(1)

    # 调整列顺序
    OUTPUT_COLUMNS = [
    "city_id",
    "year",
    "gdp_per_capita",
    "avg_salary_non_private",
    "avg_salary_private",
    "tertiary_industry_ratio",
    "house_price",
    "avg_rent",
    "house_price_income_ratio_non_private",
    "house_price_income_ratio_private",
    "hospital_count",
    "university_count",
    "metro_station_count",
    "pm25",
    "good_air_days_ratio",
    "park_count",
    ]

    result = result[OUTPUT_COLUMNS]

    # 排序
    result = result.sort_values(["city_id", "year"])

    # 保存结果
    result.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Generated: {OUTPUT_PATH}")
    print(result)

    print("\nMissing values:")
    print(result.isna().sum())

if __name__ == "__main__":
    main()