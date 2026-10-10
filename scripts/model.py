"""Shared, validated data and scoring rules. No network access at runtime."""
from pathlib import Path
from urllib.parse import urlparse
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DIMENSIONS = {
    "economy": ["gdp_per_capita", "avg_salary_non_private", "avg_salary_private", "tertiary_industry_ratio"],
    "cost": ["house_price", "avg_rent", "house_price_income_ratio_non_private", "house_price_income_ratio_private"],
    "service": ["hospital_count", "university_count", "metro_station_count"],
    "environment": ["pm25", "good_air_days_ratio", "park_count"],
}
WEIGHTS = {"economy": 0.35, "cost": 0.30, "service": 0.20, "environment": 0.15}
INDICATORS = [col for columns in DIMENSIONS.values() for col in columns]
DERIVED = ["house_price_income_ratio_non_private", "house_price_income_ratio_private"]
RAW_INDICATORS = [col for col in INDICATORS if col not in DERIVED]
NEGATIVE = set(DIMENSIONS["cost"] + ["pm25"])
MIN_AVAILABLE = {"economy": 2, "cost": 1, "service": 1, "environment": 1}
UNITS = dict(zip(RAW_INDICATORS, ["元/人", "元/年", "元/年", "%", "元/平方米", "元/月", "个", "所", "个", "μg/m³", "%", "个"]))


def read_csv_safely(path):
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Cannot decode file: {path}")


def require_columns(frame, columns, name):
    missing = set(columns) - set(frame.columns)
    if missing:
        raise ValueError(f"{name}: missing columns {sorted(missing)}")


def validate_cities(cities):
    require_columns(cities, ["city_id", "city_name"], "cities")
    if cities.empty or cities[["city_id", "city_name"]].isna().any().any():
        raise ValueError("cities: empty table or missing identifiers")
    if cities.city_id.duplicated().any() or cities.city_name.duplicated().any():
        raise ValueError("cities: duplicate ID or name")
    validate_integer(cities.city_id, "city_id", 1)


def validate_integer(series, name, lower=1900, upper=None):
    values = pd.to_numeric(series, errors="coerce")
    bad = ~np.isfinite(values) | (values % 1 != 0) | (values < lower)
    if upper is not None:
        bad |= values > upper
    if bad.any():
        raise ValueError(f"{name}: invalid integer identifier/year")


def validate_values(frame):
    for col in RAW_INDICATORS:
        if col not in frame:
            continue
        raw = frame[col]
        values = pd.to_numeric(raw, errors="coerce")
        invalid = raw.notna() & (~np.isfinite(values) | (values < 0))
        if col in ("gdp_per_capita", "avg_salary_non_private", "avg_salary_private", "house_price", "avg_rent"):
            invalid |= values.notna() & (values <= 0)
        if col in ("tertiary_industry_ratio", "good_air_days_ratio"):
            invalid |= values > 100
        if col.endswith("_count"):
            invalid |= values.notna() & (values % 1 != 0)
        if invalid.any():
            raise ValueError(f"{col}: invalid numeric/range values at rows {frame.index[invalid].tolist()}")


def build_indicators(cities, source):
    validate_cities(cities)
    require_columns(source, ["city", "year", "indicator", "value", "unit", "source_name", "source_url"], "sources")
    source = source.copy()
    for col in ("city", "indicator", "unit", "source_name", "source_url"):
        source[col] = source[col].fillna("").astype(str).str.strip()
    source["value"] = source.value.replace(r"^\s*$", np.nan, regex=True)
    validate_integer(source.year, "year", 1900, 2100)
    if source.empty:
        raise ValueError("sources: empty table")
    if not set(source.city).issubset(set(cities.city_name)):
        raise ValueError("sources: unknown city")
    if not set(source.indicator).issubset(set(RAW_INDICATORS)):
        raise ValueError("sources: unknown indicator")
    if source.duplicated(["city", "year", "indicator"]).any():
        raise ValueError("sources: duplicate city/year/indicator; resolve conflicts explicitly")
    populated = source[source.value.notna()].copy()
    for row in populated.itertuples():
        if row.unit != UNITS[row.indicator]:
            raise ValueError(f"sources: unexpected unit for {row.city}/{row.indicator}: {row.unit}")
        url = urlparse(row.source_url)
        if not row.source_name or url.scheme not in ("https", "http") or not url.netloc:
            raise ValueError(f"sources: missing source name/URL for {row.city}/{row.indicator}")
    populated["value"] = pd.to_numeric(populated.value, errors="raise")
    grid = pd.MultiIndex.from_product([cities.city_name, sorted(source.year.unique())], names=["city", "year"])
    wide = populated.pivot(index=["city", "year"], columns="indicator", values="value")
    wide = wide.reindex(index=grid, columns=RAW_INDICATORS).reset_index()
    validate_values(wide)
    result = wide.merge(cities[["city_id", "city_name"]], left_on="city", right_on="city_name", validate="many_to_one")
    for sector in ("non_private", "private"):
        result[f"house_price_income_ratio_{sector}"] = (result.house_price * 90 / result[f"avg_salary_{sector}"]).round(1)
    return result[["city_id", "year"] + INDICATORS].sort_values(["year", "city_id"]).reset_index(drop=True)


def validate_indicators(cities, indicators):
    validate_cities(cities)
    require_columns(indicators, ["city_id", "year"] + INDICATORS, "indicators")
    if indicators.empty:
        raise ValueError("indicators: empty table")
    validate_integer(indicators.city_id, "city_id", 1)
    validate_integer(indicators.year, "year", 1900, 2100)
    if indicators.duplicated(["city_id", "year"]).any():
        raise ValueError("indicators: duplicate city/year")
    if not set(indicators.city_id).issubset(set(cities.city_id)):
        raise ValueError("indicators: unknown city ID")
    for year, rows in indicators.groupby("year"):
        if set(rows.city_id) != set(cities.city_id):
            raise ValueError(f"indicators: cities missing from year {year}; retain empty rows")
    validate_values(indicators)
    for sector in ("private", "non_private"):
        actual = pd.to_numeric(indicators[f"house_price_income_ratio_{sector}"], errors="raise")
        expected = (indicators.house_price * 90 / indicators[f"avg_salary_{sector}"]).round(1)
        if not np.isclose(actual, expected, equal_nan=True).all():
            raise ValueError(f"indicators: incorrect derived ratio for {sector}")


def min_max_score(series, positive=True):
    values = pd.to_numeric(series, errors="raise").astype(float)
    if not np.isfinite(values.dropna()).all():
        raise ValueError("normalization: non-finite values")
    lo, hi = values.min(), values.max()
    if pd.isna(lo):
        return values
    if hi == lo:
        return values.where(values.isna(), 50.0)
    return ((values - lo) if positive else (hi - values)) / (hi - lo) * 100


def validate_weights(weights):
    if set(weights) != set(DIMENSIONS):
        raise ValueError("weights: expected exactly four dimensions")
    values = np.array(list(weights.values()), dtype=float)
    if not np.isfinite(values).all() or (values < 0).any() or not np.isclose(values.sum(), 1):
        raise ValueError("weights: finite, nonnegative values must sum to one")


def calculate_scores(cities, indicators, weights=None):
    weights = WEIGHTS if weights is None else weights
    validate_weights(weights)
    validate_indicators(cities, indicators)
    result = indicators.merge(cities[["city_id", "city_name"]], on="city_id", validate="many_to_one")
    result["coverage"] = result[RAW_INDICATORS].notna().mean(axis=1).round(4)
    result["available_indicators"] = result[RAW_INDICATORS].notna().sum(axis=1)
    result["status"] = "insufficient_data"
    for dim, columns in DIMENSIONS.items():
        result[f"{dim}_score"] = np.nan
        result[f"{dim}_available"] = result[columns].notna().sum(axis=1)
    result["total_score"] = np.nan
    result["rank"] = pd.Series(pd.NA, index=result.index, dtype="Int64")
    for col in INDICATORS:
        result[col + "_score"] = np.nan
    cohorts = {}
    for year, rows in result.groupby("year"):
        eligible = pd.Series(True, index=rows.index)
        for dim, minimum in MIN_AVAILABLE.items():
            eligible &= rows[f"{dim}_available"] >= minimum
        subset = rows.loc[eligible]
        common = {dim: [col for col in columns if subset[col].notna().all()] for dim, columns in DIMENSIONS.items()}
        usable = len(subset) >= 2 and all(len(common[dim]) >= MIN_AVAILABLE[dim] for dim in DIMENSIONS)
        cohorts[str(int(year))] = {"city_ids": subset.city_id.astype(int).tolist() if usable else [], "indicators": common if usable else {dim: [] for dim in DIMENSIONS}}
        if not usable:
            continue
        for dim, columns in common.items():
            for col in columns:
                result.loc[subset.index, col + "_score"] = min_max_score(subset[col], col not in NEGATIVE)
            result.loc[subset.index, f"{dim}_score"] = result.loc[subset.index, [col + "_score" for col in columns]].mean(axis=1)
        totals = sum(result.loc[subset.index, f"{dim}_score"] * weight for dim, weight in weights.items()).round(1)
        result.loc[subset.index, "total_score"] = totals
        result.loc[subset.index, "rank"] = totals.rank(ascending=False, method="min").astype("Int64")
        result.loc[subset.index, "status"] = "provisional"
    for dim in DIMENSIONS:
        result[f"{dim}_score"] = result[f"{dim}_score"].round(4)
    return result.sort_values(["year", "rank", "city_id"], na_position="last"), cohorts
