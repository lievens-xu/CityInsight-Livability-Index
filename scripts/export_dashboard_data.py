"""Export strict JSON plus browser-friendly JS for HTTP and file:// previews."""
import json
import pandas as pd
from model import BASE_DIR, DIMENSIONS, INDICATORS, RAW_INDICATORS, UNITS, read_csv_safely


def records(frame):
    return json.loads(frame.to_json(orient="records", force_ascii=False, double_precision=10))


def main():
    scores = read_csv_safely(BASE_DIR / "data/processed/livability_scores_2024.csv")
    cities = read_csv_safely(BASE_DIR / "data/raw/city_basic.csv")
    sources = read_csv_safely(BASE_DIR / "data/raw/data_source_tracking_2024.csv")
    meta = json.loads((BASE_DIR / "data/processed/livability_scores_2024.metadata.json").read_text())
    payload = {"data_year": 2024, "model_version": "2.1", "cities": records(scores.merge(cities.drop(columns="city_name"), on="city_id", validate="many_to_one")),
               "sources": records(sources[sources.value.notna()]), "dimensions": DIMENSIONS,
               "raw_indicators": RAW_INDICATORS, "units": {**UNITS, **{col: "年" for col in INDICATORS if col.startswith("house_price_income")}}, **meta}
    text = json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False)
    output = BASE_DIR / "dashboard/data"
    output.mkdir(parents=True, exist_ok=True)
    (output / "cities.json").write_text(text + "\n", encoding="utf-8")
    # Prevent HTML-sensitive sequences in generated browser data.
    safe = text.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    (output / "cities.js").write_text("window.CITYINSIGHT_DATA = " + safe + ";\n", encoding="utf-8")
    print(f"Exported {len(scores)} cities to {output}")


if __name__ == "__main__":
    main()
