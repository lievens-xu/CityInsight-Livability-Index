"""Browser smoke checks using a temporary loopback server or a supplied URL."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright
from model import BASE_DIR


def check(page, url):
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto(url, wait_until='networkidle')
    city_count = page.evaluate('window.CITYINSIGHT_DATA.cities.length')
    assert page.locator('.city-row').count() == city_count
    default = page.locator('.city-row .score').all_text_contents()
    page.get_by_role('button', name='成本优先', exact=True).click()
    assert page.locator('.city-row .score').all_text_contents() != default
    page.get_by_role('button', name='恢复默认权重').click()
    assert page.locator('.city-row .score').all_text_contents() == default
    # Browser and Python totals must agree, including rank and exported precision.
    assert page.evaluate('currentCities().every(c=>c.status!=="provisional" || (c.total_score===c.custom_score && c.rank===c.custom_rank))')
    page.locator('#city-search').fill('杭州')
    assert page.locator('.city-row').count() == 1
    page.locator('#city-search').fill('不存在')
    assert '没有匹配' in page.locator('#ranking-list').inner_text()
    page.locator('#city-search').fill('')
    page.select_option('#city-b', '4')
    assert '数据不足' in page.locator('#compare-content').inner_text()
    page.select_option('#source-city', '4')
    assert page.locator('#sources-body tr').count() > 0
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
                assert offline.locator('.city-row').count() == 8
            finally:
                browser.close()
    finally:
        if server:
            server.shutdown()
            server.server_close()
    print('Dashboard checks passed: weights, score parity, search, comparison, sources, CSV, mobile and file://')


if __name__ == '__main__':
    main()
