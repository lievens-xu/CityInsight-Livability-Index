import numpy as np
import pandas as pd
import pytest
from model import (BASE_DIR, INDICATORS, RAW_INDICATORS, WEIGHTS, build_indicators,
                   calculate_scores, min_max_score, read_csv_safely, validate_indicators)


@pytest.fixture
def fixture():
    cities = pd.DataFrame({'city_id': [1, 2, 3], 'city_name': ['甲', '乙', '丙']})
    rows = pd.DataFrame({'city_id': [1, 2, 3], 'year': [2024] * 3})
    for col in RAW_INDICATORS:
        rows[col] = [10., 20., 30.]
    for sector in ('private', 'non_private'):
        rows[f'house_price_income_ratio_{sector}'] = 90.
    return cities, rows


def test_constant_indicator_preserves_missing():
    result = min_max_score(pd.Series([4., np.nan, 4.], index=[7, 8, 9]))
    assert result[7] == result[9] == 50
    assert pd.isna(result[8])
    assert min_max_score(pd.Series([np.nan, np.nan])).isna().all()


def test_direction_and_precision():
    assert min_max_score(pd.Series([1., 2., 4.])).iloc[1] == pytest.approx(100 / 3)
    assert min_max_score(pd.Series([1., 4.]), positive=False).tolist() == [100, 0]


def test_missing_city_retained_without_rank(fixture):
    cities, rows = fixture
    rows.loc[2, INDICATORS] = np.nan
    result, meta = calculate_scores(cities, rows)
    absent = result[result.city_id == 3].iloc[0]
    assert pd.isna(absent['rank']) and pd.isna(absent.total_score)
    assert absent.status == 'insufficient_data' and absent.coverage == 0
    assert meta['2024']['city_ids'] == [1, 2]


def test_common_indicators_prevent_unequal_weights(fixture):
    cities, rows = fixture
    rows.loc[1, 'rent_per_sqm'] = np.nan
    result, meta = calculate_scores(cities, rows)
    assert 'rent_per_sqm' not in meta['2024']['indicators']['cost']
    assert result.rent_per_sqm_score.isna().all()
    for row in result.itertuples():
        expected = round(sum(getattr(row, dim + '_score') * weight for dim, weight in WEIGHTS.items()), 1)
        assert row.total_score == pytest.approx(expected)


def test_years_normalize_and_rank_independently(fixture):
    cities, rows = fixture
    later = rows.copy()
    later.year = 2025
    later.gdp_per_capita *= 100
    result, _ = calculate_scores(cities, pd.concat([rows, later], ignore_index=True))
    a, b = [x.sort_values('city_id') for _, x in result.groupby('year')]
    assert a.total_score.tolist() == b.total_score.tolist()
    assert a['rank'].tolist() == b['rank'].tolist()


def test_ties_and_single_city(fixture):
    cities, rows = fixture
    for col in RAW_INDICATORS:
        rows[col] = 10.
    result, _ = calculate_scores(cities, rows)
    assert result.total_score.tolist() == [50.] * 3
    assert result['rank'].tolist() == [1] * 3
    result, _ = calculate_scores(cities.iloc[:1], rows.iloc[:1])
    assert result.total_score.isna().all()


@pytest.mark.parametrize('weights', [dict(WEIGHTS, economy=-.35), dict(WEIGHTS, cost=1), dict(WEIGHTS, environment=float('nan')), {'economy': 1}])
def test_invalid_weights_fail(fixture, weights):
    with pytest.raises(ValueError, match='weights'):
        calculate_scores(*fixture, weights)


@pytest.mark.parametrize('col,value', [('avg_salary_private', 0), ('pm25', float('inf')), ('good_air_days_ratio', 101), ('hospital_count', 1.5), ('rent_per_sqm', 'invalid')])
def test_invalid_observations_fail(fixture, col, value):
    cities, rows = fixture
    rows[col] = rows[col].astype(object)
    rows.loc[0, col] = value
    with pytest.raises(ValueError):
        calculate_scores(cities, rows)


def test_source_integrity_and_complete_grid():
    cities = read_csv_safely(BASE_DIR / 'data/raw/city_basic.csv')
    source = read_csv_safely(BASE_DIR / 'data/raw/data_source_tracking_2024.csv')
    wide = build_indicators(cities, source)
    assert len(wide) == len(cities)
    assert len(cities) == 10 and {'广州', '深圳'} <= set(cities.city_name)
    from check_mvp_data import require_complete
    require_complete(cities, source, wide)
    validate_indicators(cities, wide)
    for bad_source in (pd.concat([source, source.iloc[:1]]), source.assign(city='unknown'),
                       source.assign(unit='wrong'), source.assign(source_url='javascript:bad')):
        with pytest.raises(ValueError):
            build_indicators(cities, bad_source)


def test_release_rejects_missing_and_unverified_data():
    from check_mvp_data import require_complete
    cities = read_csv_safely(BASE_DIR / 'data/raw/city_basic.csv')
    source = read_csv_safely(BASE_DIR / 'data/raw/data_source_tracking_2024.csv')
    missing = source.copy()
    missing.loc[0, 'value'] = np.nan
    with pytest.raises(ValueError, match='incomplete'):
        require_complete(cities, missing, build_indicators(cities, missing))
    pending = source.copy()
    pending.loc[0, 'verification_status'] = 'pending'
    with pytest.raises(ValueError, match='verified'):
        require_complete(cities, pending, build_indicators(cities, pending))


def test_reject_stale_ratios_and_duplicate_rows(fixture):
    cities, rows = fixture
    rows.loc[0, 'house_price_income_ratio_private'] = 1
    with pytest.raises(ValueError, match='derived ratio'):
        validate_indicators(cities, rows)
    with pytest.raises(ValueError, match='duplicate'):
        validate_indicators(cities, pd.concat([rows, rows.iloc[:1]]))


def test_university_counts_match_common_national_reference():
    reference = pd.read_csv(BASE_DIR / 'data/reference/ordinary_universities_2024.csv', dtype={'school_code': str})
    assert len(reference) == 381
    assert reference.school_code.str.fullmatch(r'\d{10}').all()
    assert reference.school_code.is_unique
    source = read_csv_safely(BASE_DIR / 'data/raw/data_source_tracking_2024.csv')
    counts = source[source.indicator == 'university_count'].set_index('city').value.astype(int).to_dict()
    assert counts == reference.groupby('city_name').size().to_dict()
    assert set(source[source.indicator == 'university_count'].source_name) == {'教育部2024全国普通高等学校名单'}


def test_pipeline_source_errors_stop_instead_of_coercing():
    cities = read_csv_safely(BASE_DIR / 'data/raw/city_basic.csv')
    source = read_csv_safely(BASE_DIR / 'data/raw/data_source_tracking_2024.csv')
    source.value = source.value.astype(object)
    source.loc[source.value.notna().idxmax(), 'value'] = 'unparseable'
    with pytest.raises(ValueError):
        build_indicators(cities, source)


def test_disjoint_indicator_support_is_not_rankable(fixture):
    cities, rows = fixture
    # Each city has service data, but no single service indicator covers the cohort.
    rows.loc[:, ['hospital_count', 'university_count', 'rail_station_count']] = np.nan
    for i, col in enumerate(['hospital_count', 'university_count', 'rail_station_count']):
        rows.loc[i, col] = 10
    result, meta = calculate_scores(cities, rows)
    assert result.total_score.isna().all()
    assert result['rank'].isna().all()
    assert meta['2024']['city_ids'] == []
