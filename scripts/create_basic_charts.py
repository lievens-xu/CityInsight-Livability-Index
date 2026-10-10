"""Headless charts with portable font fallback and honest cohort labels."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
from model import BASE_DIR, read_csv_safely

OUTPUT_DIR = BASE_DIR / 'dashboard/figures'


def main():
    available = {font.name for font in font_manager.fontManager.ttflist}
    chinese = next((name for name in ('Arial Unicode MS', 'PingFang SC', 'Noto Sans CJK SC', 'Microsoft YaHei', 'SimHei') if name in available), None)
    if chinese:
        plt.rcParams['font.sans-serif'] = [chinese]
    plt.rcParams['axes.unicode_minus'] = False
    df = read_csv_safely(BASE_DIR / 'data/processed/livability_scores_2024.csv')
    all_cities = df.copy()
    df = df[df.status == 'provisional'].copy()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Remove only the chart filenames owned by this generator (including stale top-city radar).
    for pattern in ('01_total_score_ranking*.png', '02_dimension_scores*.png', '03_radar_*.png'):
        for path in OUTPUT_DIR.glob(pattern):
            path.unlink()
    english = {1: 'Shanghai', 2: 'Suzhou', 3: 'Nanjing', 4: 'Hangzhou', 5: 'Ningbo', 6: 'Wuxi', 7: 'Hefei', 8: 'Changzhou'}
    labels = ['经济机会', '生活成本', '公共服务', '环境质量'] if chinese else ['Economy', 'Affordability', 'Services', 'Environment']
    for year, rows in df.groupby('year'):
        names = rows.city_name if chinese else rows.city_id.map(english)
        rows = rows.assign(label=names).sort_values('total_score')
        suffix = '' if df.year.nunique() == 1 else f'_{int(year)}'
        fig, ax = plt.subplots(figsize=(9, 5), layout='constrained')
        ax.barh(rows.label, rows.total_score, color='#147d78')
        ax.bar_label(ax.containers[0], fmt='%.1f', padding=4)
        ax.set(xlim=(0, 105), xlabel='Score (0–100)', title=f'{int(year)} · Provisional ranking · {len(rows)} comparable cities')
        ax.spines[['top', 'right']].set_visible(False)
        fig.savefig(OUTPUT_DIR / f'01_total_score_ranking{suffix}.png', dpi=180)
        plt.close(fig)
        fig, ax = plt.subplots(figsize=(10, 5), layout='constrained')
        x = np.arange(len(rows))
        for i, (dim, label) in enumerate(zip(('economy', 'cost', 'service', 'environment'), labels)):
            ax.bar(x + (i - 1.5) * .2, rows[f'{dim}_score'], .2, label=label)
        ax.set(xticks=x, xticklabels=rows.label, ylim=(0, 110), title=f'{int(year)} · Dimension comparison (common indicators)')
        ax.legend(loc='upper center', ncols=4)
        fig.savefig(OUTPUT_DIR / f'02_dimension_scores{suffix}.png', dpi=180)
        plt.close(fig)
        top = rows.sort_values(['rank', 'city_id']).iloc[0]
        angles = np.linspace(0, 2 * np.pi, 4, endpoint=False)
        values = [top[f'{dim}_score'] for dim in ('economy', 'cost', 'service', 'environment')]
        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'polar': True}, layout='constrained')
        ax.plot(np.append(angles, angles[0]), values + values[:1], color='#147d78')
        ax.fill(np.append(angles, angles[0]), values + values[:1], color='#147d78', alpha=.15)
        ax.set(xticks=angles, xticklabels=labels, ylim=(0, 100), title=f'{top.label} · {int(year)} · Provisional profile')
        fig.savefig(OUTPUT_DIR / f'03_radar_{top.city_name}{suffix}.png', dpi=180)
        plt.close(fig)
    for year, rows in all_cities.groupby('year'):
        rows = rows.dropna(subset=['gdp_per_capita', 'pm25'])
        fig, ax = plt.subplots(figsize=(9, 5), layout='constrained')
        ax.scatter(rows.gdp_per_capita / 1000, rows.pm25, s=75, color='#147d78')
        for row in rows.itertuples():
            name = row.city_name if chinese else english.get(row.city_id, str(row.city_id))
            ax.annotate(name, (row.gdp_per_capita / 1000, row.pm25), xytext=(5, 7), textcoords='offset points', fontsize=9)
        ax.set(xlabel='GDP per capita (thousand CNY)', ylabel='Annual PM2.5 (micrograms/m³)',
               title=f'{int(year)} · {len(rows)} cities · Economic output and air quality')
        ax.margins(.12)
        ax.spines[['top', 'right']].set_visible(False)
        suffix = '' if all_cities.year.nunique() == 1 else f'_{int(year)}'
        fig.savefig(OUTPUT_DIR / f'04_gdp_vs_pm25{suffix}.png', dpi=180)
        plt.close(fig)
    print(f'Generated charts for {df.year.nunique()} annual cohort(s): {OUTPUT_DIR}')


if __name__ == '__main__':
    main()
