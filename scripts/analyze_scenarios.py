"""Deterministic preference scenarios, not statistical confidence intervals."""
import json
from itertools import product
from model import BASE_DIR, DIMENSIONS, read_csv_safely

PRESETS = {'balanced': [35, 30, 20, 15], 'career': [55, 20, 15, 10],
           'budget': [20, 55, 15, 10], 'green': [20, 20, 20, 40]}


def main():
    scores = read_csv_safely(BASE_DIR / 'data/processed/livability_scores_2024.csv')
    dims = list(DIMENSIONS)
    scenario_rows, sensitivity_rows = [], []
    for year, group in scores[scores.status == 'provisional'].groupby('year'):
        for name, weights in PRESETS.items():
            totals = sum(group[dim + '_score'] * weight / 100 for dim, weight in zip(dims, weights)).round(1)
            ranks = totals.rank(ascending=False, method='min').astype(int)
            for index, row in group.iterrows():
                scenario_rows.append({'year': int(year), 'scenario': name, 'city_id': int(row.city_id), 'city_name': row.city_name,
                                      'total_score': float(totals.loc[index]), 'rank': int(ranks.loc[index])})
        rank_samples = {index: [] for index in group.index}
        for a, b, c in product(range(11), repeat=3):
            d = 10 - a - b - c
            if d < 0:
                continue
            totals = sum(group[dim + '_score'] * weight / 10 for dim, weight in zip(dims, [a, b, c, d])).round(1)
            ranks = totals.rank(ascending=False, method='min').astype(int)
            for index in group.index:
                rank_samples[index].append(int(ranks.loc[index]))
        for index, row in group.iterrows():
            samples = rank_samples[index]
            sensitivity_rows.append({'year': int(year), 'city_id': int(row.city_id), 'city_name': row.city_name,
                                     'best_rank': min(samples), 'worst_rank': max(samples),
                                     'top_rank_weight_combinations': samples.count(1), 'weight_combinations': len(samples)})
    import pandas as pd
    scenario_path = BASE_DIR / 'data/processed/preference_scenarios_2024.csv'
    pd.DataFrame(scenario_rows, columns=['year', 'scenario', 'city_id', 'city_name', 'total_score', 'rank']).to_csv(scenario_path, index=False, encoding='utf-8-sig')
    (BASE_DIR / 'data/processed/weight_sensitivity_2024.json').write_text(json.dumps({
        'method': 'all four-dimensional weight combinations on a 10-percentage-point grid, summing to 100%',
        'interpretation': 'exploratory weight sensitivity, not probabilities or confidence intervals',
        'cities': sensitivity_rows,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Generated {len(scenario_rows)} preference scenario rows')


if __name__ == '__main__':
    main()
