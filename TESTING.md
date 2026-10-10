# Verification for 0.5.4

- Built with Windhawk 1.7.3's x64 engine and compiler. PE architecture, DLL flag, imports, and the four Windhawk callbacks were checked without loading the build into the test process.
- `test-gesture.py` extracts the actual horizontal gesture state machine and checks duplicate suppression, quiet-period boundaries, reversal, window changes, partial wheel deltas, and timer wraparound.
- `test-arrow-cache.py` extracts the actual discovery and cache structures. A simulated native row takes 7 probes on first discovery. Tests cover first arrows before overflow buttons, far-right tabs, a foreign-window hard boundary, missing arrows, out-of-row bounds, cache identity/layout changes, failure expiry, and timer wraparound.
- `test-host-scope.py` extracts the native workbook ownership check. It rejects task panes, foreign child windows, a foreign window named EXCEL7, and wrong frame roots.
- Installed 0.5.4 in a running 64-bit Microsoft 365 Excel process. A narrowed tab strip scrolled in both directions without changing the active sheet, selected cell, or worksheet position. A read-only MSAA diagnostic confirmed the arrows and sheet tabs belong to the native EXCEL7 window at its bottom row. No action is performed by that diagnostic.
- With the Navigation pane docked left, the user tested both wheel directions and confirmed that the animation and response were normal.
- The installed settings and registry value types were preserved; neither Excel nor Windhawk was restarted.

Screenshots verify final tab positions. The user's animation and response feedback is subjective; no frame timing or measured input latency is claimed. Other Office installations have not been tested.

The installed source and DLL hashes match the published 0.5.4 build. Settings keys, defaults, and option values match 0.5.3; only display strings and their localizations changed. The source contains no Wh_SetIntValue calls.
