import argparse
import json
import tempfile
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


METRIC_SCRIPT = """
const resources = performance.getEntriesByType('resource')
  .filter((entry) => entry.name.includes('/assets/'));
const sum = (key) => resources.reduce((total, entry) => total + (entry[key] || 0), 0);
const end = (pattern) => {
  const matching = resources.filter((entry) => pattern.test(entry.name));
  return matching.length ? Math.max(...matching.map((entry) => entry.responseEnd)) : 0;
};
return {
  navigation: performance.getEntriesByType('navigation')[0]?.toJSON(),
  domContentLoadedMs: performance.getEntriesByType('navigation')[0]?.domContentLoadedEventEnd || 0,
  canvasCount: document.querySelectorAll('canvas').length,
  preloadDisplay: getComputedStyle(document.querySelector('#preload')).display,
  splashAssetsEndMs: end(/splashBG|splashAssets/),
  primaryAssetsEndMs: end(/BG_king|king_character|reels_frame|symbols|gameElements|explosion1/),
  audioEndMs: end(/BBGM|genericButtonSound/),
  allAssetsEndMs: end(/assets/),
  resourceCount: resources.length,
  transferBytes: sum('transferSize'),
  encodedBytes: sum('encodedBodySize'),
  failed: resources
    .filter((entry) => entry.responseStatus >= 400)
    .map((entry) => ({name: entry.name, status: entry.responseStatus}))
};
"""


def run_once(url):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1280,720')

    with tempfile.TemporaryDirectory(prefix='empire-load-') as profile:
        options.add_argument(f'--user-data-dir={profile}')
        driver = webdriver.Chrome(options=options)
        try:
            started = time.perf_counter()
            driver.get(url)
            dom_ready_wall_ms = (time.perf_counter() - started) * 1000
            time.sleep(10)
            metrics = driver.execute_script(METRIC_SCRIPT)
            metrics['browserGetWallMs'] = dom_ready_wall_ms
            metrics['wallClockMs'] = (time.perf_counter() - started) * 1000
            metrics['playable'] = (
                metrics['canvasCount'] > 0 and metrics['preloadDisplay'] == 'none'
            )
            return metrics
        finally:
            driver.quit()


def format_bytes(value):
    return f'{value / 1024 / 1024:.2f} MB'


def main():
    parser = argparse.ArgumentParser(description='Measure a cold Empire of Gold browser load.')
    parser.add_argument('--url', default='http://127.0.0.1:4174/', help='Game URL')
    parser.add_argument('--runs', type=int, default=3, help='Cold browser runs')
    args = parser.parse_args()

    results = []
    for run in range(1, args.runs + 1):
        print(f'Run {run}/{args.runs}...', flush=True)
        results.append(run_once(args.url))

    def median(key):
        values = [result[key] for result in results if result.get(key) is not None]
        values.sort()
        return values[len(values) // 2] if values else 0

    print('\nCold-load results')
    print(f'URL: {args.url}')
    print(f'Runs: {args.runs}')
    print('Median values across runs:')
    print(f'DOM ready:          {median("domContentLoadedMs"):.0f} ms')
    print(f'Canvas present:     {sum(result["canvasCount"] > 0 for result in results)}/{args.runs} runs')
    print(f'Splash assets end:  {median("splashAssetsEndMs"):.0f} ms')
    print(f'Primary assets end: {median("primaryAssetsEndMs"):.0f} ms')
    print(f'Audio end:          {median("audioEndMs"):.0f} ms')
    print(f'All assets end:     {median("allAssetsEndMs"):.0f} ms')
    print(f'Asset transfer:     {format_bytes(median("transferBytes"))}')
    print(f'Asset encoded size: {format_bytes(median("encodedBytes"))}')
    print(f'Playable:           {all(result["playable"] for result in results)}')

    print('\nPer-run browser timings:')
    for index, result in enumerate(results, 1):
        print(
            f'  {index}: DOM {result["domContentLoadedMs"]:.0f} ms, '
            f'primary {result["primaryAssetsEndMs"]:.0f} ms, '
            f'all assets {result["allAssetsEndMs"]:.0f} ms, '
            f'{format_bytes(result["transferBytes"])}, '
            f'playable={result["playable"]}'
        )

    failures = sorted({failure['name'] for result in results for failure in result['failed']})
    print(f'HTTP failures:      {len(failures)}')
    for failure in failures:
        print(f'  {failure}')

    output = Path(__file__).with_name('load_metrics.json')
    output.write_text(json.dumps(results, indent=2), encoding='utf-8')
    print(f'\nDetailed metrics: {output}')


if __name__ == '__main__':
    main()