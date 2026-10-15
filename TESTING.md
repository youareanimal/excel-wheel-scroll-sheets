# Verification

## v0.5.5 candidate

The candidate is submitted in [Windhawk PR #6237](https://github.com/ramensoftware/windhawk-mods/pull/6237). These checks are separate from the published 0.5.4 build below.

- Built locally against Windhawk 1.7.3 x64. PE architecture, DLL imports, `Wh_ModInit` and `Wh_ModSettingsChanged` exports passed verification. The empty optional callbacks were removed.
- `tests/test-horizontal-fallback.py` extracts the candidate's actual `HorizontalGesture` and complete `DispatchMessageWHook`. It mocks window-scope checks, the readiness probe and activation outcome, then checks the count, order and fields of messages sent to the original dispatch function.
- At both 50 ms and 200 ms, not-ready bursts pass through immediately. Failed activation after partial-delta accumulation restores every buffered message and passes the remainder through. Tests cover small/coarse deltas in both directions, the 119-message accumulation boundary, successful once-per-burst activation, failure latching, the exact quiet-period boundary, reversal, window changes, timestamp wraparound, disabled switching and zero delta.
- The same behavioral regression fails against the pre-fix handler and passes against the repaired candidate. Native-arrow cache and workbook-window ownership tests also pass against the candidate source.
- The submitter reports normal mouse behavior at 50 ms. This is user-reported feedback, not an independently repeated live test of the repaired candidate.
- No laptop/touchpad or 32-bit Excel was available. Physical touchpad behavior and 32-bit Excel remain untested. The repaired candidate has not been installed or traced live in Excel.

Run the regression against the candidate source downloaded or checked out from that PR:

```powershell
python tests/test-horizontal-fallback.py --source path\to\excel-wheel-scroll-sheets.wh.cpp
```

Generated test files are kept in `.test-output-horizontal-fallback/`. This test does not launch or control Excel.

## Published 0.5.4

- Built with Windhawk 1.7.3's x64 engine and compiler. PE architecture, DLL flag, imports, and the four Windhawk callbacks were checked without loading the build into the test process.
- `test-gesture.py` extracts the actual horizontal gesture state machine and checks duplicate suppression, quiet-period boundaries, reversal, window changes, partial wheel deltas, and timer wraparound.
- `test-arrow-cache.py` extracts the actual discovery and cache structures. A simulated native row takes 7 probes on first discovery. Tests cover first arrows before overflow buttons, far-right tabs, a foreign-window hard boundary, missing arrows, out-of-row bounds, cache identity/layout changes, failure expiry, and timer wraparound.
- `test-host-scope.py` extracts the native workbook ownership check. It rejects task panes, foreign child windows, a foreign window named EXCEL7, and wrong frame roots.
- Installed 0.5.4 in a running 64-bit Microsoft 365 Excel process. A narrowed tab strip scrolled in both directions without changing the active sheet, selected cell, or worksheet position. A read-only MSAA diagnostic confirmed the arrows and sheet tabs belong to the native EXCEL7 window at its bottom row. No action is performed by that diagnostic.
- With the Navigation pane docked left, the user tested both wheel directions and confirmed that the animation and response were normal.
- The installed settings and registry value types were preserved; neither Excel nor Windhawk was restarted.

Screenshots verify final tab positions. The user's animation and response feedback is subjective; no frame timing or measured input latency is claimed. Other Office installations have not been tested.

The installed source and DLL hashes match the published 0.5.4 build. Settings keys, defaults, and option values match 0.5.3; only display strings and their localizations changed. The source contains no Wh_SetIntValue calls.
