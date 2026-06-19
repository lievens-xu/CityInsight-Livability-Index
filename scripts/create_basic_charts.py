from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]

SCORE_PATH = BASE_DIR / "data" / "processed" / "livability_scores_2024.csv"
OUTPUT_DIR = BASE_DIR / "dashboard" / "figures"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def read_csv_safely(path):
    encodings = ["utf-8-sig", "utf-8", "gbk", "gb18030"]

    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue

    raise ValueError(f"Cannot decode file: {path}")


def setup_chinese_font():
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False


def plot_total_score_ranking(df):
    data = df.sort_values("total_score", ascending=True)

    plt.figure(figsize=(10, 6))
    plt.barh(data["city_name"], data["total_score"])
    plt.xlabel("宜居总分")
    plt.ylabel("城市")
    plt.title("2024年长三角城市宜居指数排名")
    plt.tight_layout()

    output_path = OUTPUT_DIR / "01_total_score_ranking.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved: {output_path}")


def plot_dimension_scores(df):
    columns = [
        "economy_score",
        "cost_score",
        "service_score",
        "environment_score",
    ]

    data = df[["city_name"] + columns].copy()
    data = data.sort_values("city_name")

    x = np.arange(len(data["city_name"]))
    width = 0.2

    plt.figure(figsize=(12, 6))

    for i, col in enumerate(columns):
        plt.bar(x + i * width, data[col], width, label=col)

    plt.xticks(x + width * 1.5, data["city_name"])
    plt.ylabel("得分")
    plt.title("各城市分项得分对比")
    plt.legend()
    plt.tight_layout()

    output_path = OUTPUT_DIR / "02_dimension_scores.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved: {output_path}")


def plot_city_radar(df, city_name):
    row = df[df["city_name"] == city_name]

    if row.empty:
        print(f"City not found: {city_name}")
        return

    labels = ["经济机会", "生活成本", "公共服务", "环境质量"]
    score_columns = [
        "economy_score",
        "cost_score",
        "service_score",
        "environment_score",
    ]

    values = row.iloc[0][score_columns].astype(float).tolist()

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()

    values += values[:1]
    angles += angles[:1]

    plt.figure(figsize=(6, 6))
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.2)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 100)
    ax.set_title(f"{city_name} 宜居维度雷达图")

    output_path = OUTPUT_DIR / f"03_radar_{city_name}.png"
    plt.savefig(output_path, dpi=300)
    plt.close()

    print(f"Saved: {output_path}")


def main():
    setup_chinese_font()

    df = read_csv_safely(SCORE_PATH)

    numeric_columns = [
        "economy_score",
        "cost_score",
        "service_score",
        "environment_score",
        "total_score",
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    print("Data preview:")
    print(df)

    plot_total_score_ranking(df)
    plot_dimension_scores(df)

    # 给排名第一的城市画雷达图
    top_city = df.sort_values("total_score", ascending=False).iloc[0]["city_name"]
    plot_city_radar(df, top_city)


if __name__ == "__main__":
    main()