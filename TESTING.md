# Verification for 0.5.3

- Built with Windhawk 1.7.3's x64 engine and compiler. PE architecture, DLL flag, imports, and the four Windhawk callbacks were checked without loading the build into the test process.
- `test-gesture.py` extracts the actual horizontal gesture state machine and checks duplicate suppression, quiet-period boundaries, reversal, window changes, partial wheel deltas, and timer wraparound.
- `test-arrow-cache.py` extracts the actual discovery and cache structures. A simulated left-pane layout takes 13 probes on first discovery; the cached path validates two controls. Tests cover far-right tabs, missing arrows, moved buttons, changed window size/position, and changed control identity.
- Installed 0.5.3 in a running 64-bit Microsoft 365 Excel process. Both vertical wheel directions scrolled the bottom tab strip with the left Navigation pane closed and open. The active sheet, selected cell, and worksheet scroll position stayed unchanged.
- The installed settings and registry value types were preserved; neither Excel nor Windhawk was restarted.

Screenshots verified final tab positions. They do not establish animation frame timing or measured input latency. The user confirmed the native animation was restored in 0.5.2; subjective response-speed feedback for 0.5.3 is pending. Other Office installations have not been tested.

The published source changes metadata and documentation from the installed local source. Its runtime C++ and settings block are identical to the installed 0.5.3 version.
