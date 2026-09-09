# Empire of Gold Load Performance Report

**Date:** 2026-09-09  
**Build:** Current local optimized export  
**Stack:** Vanilla JavaScript/Canvas, PixiJS, Spine, Howler  
**Test URL:** `http://127.0.0.1:4174/`

## Executive Summary

The current build reaches its primary visual asset milestone in under one second on the local test server. All observed asset requests finish in approximately **2.9 seconds** in the representative cold runs.

The game is **not currently confirmed playable** because the deferred bundle requests a missing file:

```text
/assets/spines/@1x/book.png
```

That request returns HTTP 404 and leaves the preload overlay visible.

## Median Results

Median across three cold browser runs:

| Metric | Result |
|---|---:|
| DOM ready | **269 ms** |
| Splash assets complete | **362 ms** |
| Primary game assets complete | **844 ms** |
| All observed assets complete | **2.91 s** |
| Asset transfer size | **46.30 MB** |
| Encoded asset size | **46.26 MB** |
| Canvas present | **3/3 runs** |
| Playable state reached | **No** |
| HTTP failures | **1 unique asset** |

## Individual Runs

| Run | DOM ready | Primary assets | All assets | Transfer | Playable |
|---:|---:|---:|---:|---:|:---:|
| 1 | 14.51 s | 30.68 s | 30.68 s | 7.25 MB | No |
| 2 | 269 ms | 844 ms | 2.74 s | 46.30 MB | No |
| 3 | 191 ms | 701 ms | 2.91 s | 46.30 MB | No |

Run 1 was a local server/browser startup outlier. Runs 2 and 3 are the representative measurements for the current local server state.

## Optimization Changes Included

- Compressed `BBGM.ogg` from approximately **4.60 MB to 1.03 MB**.
- Reduced `reels_frame.json` by approximately **19%**.
- Reduced `explosion1.json` by approximately **23%**.
- Verified the modified Spine JSON files parse successfully.
- Verified the modified audio remains valid Vorbis audio.

## Current Failure

The browser reports:

```text
GET /assets/spines/@1x/book.png 404
```

The matching `book.json` and `book.atlas` files exist, but `book.png` is absent. Because this is part of the deferred Spine bundle, it prevents the current build from reaching a clean playable state.

## Measurement Method

The benchmark uses [measure_load.py](measure_load.py), which:

- Starts a fresh Selenium Chrome profile for every run.
- Avoids reusing browser cache between runs.
- Reads the browser Performance Resource Timing API.
- Measures DOM readiness, splash completion, primary asset completion, audio completion, and all observed asset completion.
- Totals transfer and encoded asset bytes.
- Detects HTTP failures.
- Marks the game playable only when a canvas exists and the preload overlay is hidden.

Raw per-run data is stored in [load_metrics.json](load_metrics.json).

## Reproduce the Test

Start the static server:

```powershell
python -m http.server 4174
```

Run three cold measurements:

```powershell
python measure_load.py --url http://127.0.0.1:4174/ --runs 3
```

## Conclusion

Current representative local loading time is approximately **2.9 seconds for all observed assets**, with primary visual assets available at approximately **0.8 seconds**. A valid playable-load measurement requires restoring or correctly handling `book.png` first.
