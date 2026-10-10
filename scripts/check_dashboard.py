"""Browser smoke checks using a temporary loopback server or a supplied URL."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright
from model import BASE_DIR, DIMENSIONS, calculate_scores, read_csv_safely


def check_weight_parity(page):
    from itertools import product
    cities = read_csv_safely(BASE_DIR / 'data/raw/city_basic.csv')
    indicators = read_csv_safely(BASE_DIR / 'data/raw/city_indicators_2024_mvp.csv')
    count = 0
    for a, b, c in product(range(11), repeat=3):
        d = 10 - a - b - c
        if d < 0:
            continue
        weights = [a, b, c, d]
        expected, _ = calculate_scores(cities, indicators, dict(zip(DIMENSIONS, [w / 10 for w in weights])))
        expected = expected.sort_values('city_id')
        actual = page.evaluate('(w)=>{currentWeights=w;return currentCities().sort((a,b)=>a.city_id-b.city_id).map(c=>[c.custom_score,c.custom_rank]);}', weights)
        wanted = [[float(r.total_score), int(r.rank)] for r in expected.itertuples()]
        assert actual == wanted, (weights, actual, wanted)
        count += 1
    assert count == 286
    page.evaluate("setPreset('balanced')")


def check(page, url):
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(url, wait_until='networkidle')
    city_count = page.evaluate('window.CITYINSIGHT_DATA.cities.length')
    assert page.locator('.city-row').count() == city_count
    assert city_count == 10
    assert page.evaluate('data.cities.every(c=>c.coverage===1) && data.sources.length===120 && data.sources.every(s=>s.verification_status==="verified")')
    default = page.locator('.city-row .score').all_text_contents()
    page.get_by_role('button', name='成本优先', exact=True).click()
    assert page.locator('.city-row .score').all_text_contents() != default
    page.get_by_role('button', name='恢复默认权重').click()
    assert page.locator('.city-row .score').all_text_contents() == default
    # Browser and Python totals must agree, including rank and exported precision.
    assert page.evaluate('currentCities().every(c=>c.status!=="provisional" || (c.total_score===c.custom_score && c.rank===c.custom_rank))')
    check_weight_parity(page)
    page.locator('#city-search').fill('杭州')
    assert page.locator('.city-row').count() == 1
    page.locator('#city-search').fill('不存在')
    assert '没有匹配' in page.locator('#ranking-list').inner_text()
    page.locator('#city-search').fill('')
    page.select_option('#city-a', '9')
    page.select_option('#city-b', '10')
    assert '广州' in page.locator('#compare-content').inner_text()
    assert '深圳' in page.locator('#compare-content').inner_text()
    assert page.locator('#compare-content .radar').count() == 1
    for city in ('4', '9', '10'):
        page.select_option('#source-city', city)
        assert page.locator('#sources-body tr').count() == 12
    with page.expect_download() as download:
        page.locator('#download').click()
    path = download.value.path()
    import csv
    with open(path, encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.reader(stream))
    assert len(rows) == city_count + 1
    assert len(rows[0]) == 14
    for dim in ('economy', 'cost', 'service', 'environment'):
        page.locator('#weight-' + dim).evaluate('(e)=>{e.value=0;e.dispatchEvent(new Event("input",{bubbles:true}));}')
    assert '至少' in page.locator('#weight-status').inner_text()
    page.get_by_role('button', name='恢复默认权重').click()
    page.set_viewport_size({'width': 390, 'height': 844})
    assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
    assert not errors, errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url')
    parser.add_argument('--browser-path', default=os.environ.get('CHROME_PATH'))
    args = parser.parse_args()
    server = None
    if not args.url:
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(BASE_DIR / 'dashboard')))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        args.url = f'http://127.0.0.1:{server.server_port}/'
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(**({'executable_path': args.browser_path} if args.browser_path else {}))
            try:
                check(browser.new_page(viewport={'width': 1440, 'height': 1100}), args.url)
                offline = browser.new_page()
                offline.goto((BASE_DIR / 'dashboard/index.html').as_uri(), wait_until='load')
                assert offline.locator('.city-row').count() == len(__import__('json').loads((BASE_DIR / 'dashboard/data/cities.json').read_text())['cities'])
            finally:
                browser.close()
    finally:
        if server:
            server.shutdown()
            server.server_close()
    print('Dashboard checks passed: complete ten-city data, 286-weight Python/JS parity, search, comparison, sources, CSV, mobile and file://')


if __name__ == '__main__':
    main()
