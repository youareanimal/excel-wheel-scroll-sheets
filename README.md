# Excel Wheel Sheet Navigation

This mod brings WPS-style mouse wheel navigation to Excel, making it easier and faster to browse sheet tabs and switch between worksheets in workbooks with many sheets.

## Features

1. **Tilt the wheel to switch worksheets**

   With a mouse that supports left/right wheel tilt, such as the Logitech G502, tilt the wheel over the worksheet area to switch to the previous or next worksheet.

   Horizontal scrolling from a thumb wheel or a touchpad's two-finger swipe also switches worksheets. To restore Excel's horizontal grid scrolling, turn off **Switch sheets with the horizontal wheel**.

2. **Scroll the wheel to browse sheet tabs**

   Hover over the sheet tab bar at the bottom of Excel and scroll the wheel up or down to reveal tabs that are out of view. This scrolls the tab bar without changing the active worksheet—especially useful for workbooks with many sheets.

## Compatibility and behavior

For 64-bit desktop Excel on Windows:

- The tab strip uses Excel's native navigation arrows and animation. If the arrows cannot be used, it falls back to `ScrollWorkbookTabs`.
- Repeated same-direction horizontal wheel messages are grouped with a 50 ms quiet period by default; the first switch is immediate.
- Hidden sheets are skipped. Modified wheel input and ordinary vertical worksheet scrolling keep Excel's behavior.

Horizontal input over non-tab points in the bottom strip of the sheet area (about 64 pixels at 100% scaling) retains Excel's behavior, including a narrow strip of cells above the tab row.
The horizontal quiet period accepts 50–2000 ms. Reversal switches immediately.
The **Vertical sheet switching interval** setting defaults to 150 ms; reverse direction and wraparound are off by default.

Settings allow direct sheet activation instead of tab scrolling, reversing direction, disabling horizontal switching, and optional wraparound.
No macros are required. Activating a sheet can trigger existing workbook activation events, just like clicking a tab.
Tested on one installation of 64-bit Microsoft 365 Excel; other Office versions and 32-bit Excel have not been tested.


## Install

Install this mod from the [Windhawk catalog](https://windhawk.net/mods/excel-wheel-scroll-sheets). For local development, create a mod in Windhawk and paste `excel-wheel-scroll-sheets.wh.cpp` into its source editor. Existing saved settings are preserved.

## Development and contributions

The source in this repository matches the Windhawk catalog version 0.5.5. The catalog copy is [here](https://github.com/ramensoftware/windhawk-mods/blob/main/mods/excel-wheel-scroll-sheets.wh.cpp). Please base contributions on this repository's main branch.

Shift + vertical-wheel navigation is not implemented yet. Issue #1 proposes an optional setting; contributions are welcome. Modified wheel input currently retains Excel's behavior.

Build on Windows with Windhawk installed:

```powershell
python build.py
```

Run the source-extracted regression tests:

```powershell
python test-gesture.py
python test-arrow-cache.py
python test-host-scope.py
python tests/test-horizontal-fallback.py --source excel-wheel-scroll-sheets.wh.cpp
```

Tests use Windhawk's compiler on Windows. On Linux, install a C++23 compiler (`g++` by default), or set `CXX` to its path. They mock Win32/COM behavior and do not replace live Excel testing. See [TESTING.md](TESTING.md) for historical test evidence.

Older release ZIPs contain historical binaries; do not treat them as a build of the current source. The installation script is for first installs only.

## License

GPL-3.0-or-later; see [LICENSE](LICENSE).
