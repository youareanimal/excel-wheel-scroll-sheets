# Excel 滚轮切换工作表

本模组为 Excel 带来类似 WPS 的滚轮工作表导航体验，通过鼠标滚轮即可浏览工作表标签、切换工作表，让包含多个工作表的工作簿操作起来更方便、更快捷。

## 功能简介

1. **左右拨动，快速切换工作表**

   使用支持滚轮左右拨动的鼠标（如罗技 G502），在表格区域左右拨动滚轮，即可切换到上一张或下一张工作表。

2. **上下滚动，轻松浏览工作表标签**

   将鼠标悬停在底部工作表标签栏上，上下滚动滚轮，即可滚动标签栏，查看两侧未显示的标签。此操作不会切换当前工作表，尤其适合工作表数量较多的工作簿。

## 操作

| 鼠标位置 | 操作 | 结果 |
| --- | --- | --- |
| 底部工作表标签 | 上下滚轮 | 滚动标签栏，当前工作表不变 |
| 单元格或工作表标签 | 向右拨动横向滚轮 | 下一张可见工作表 |
| 单元格或工作表标签 | 向左拨动横向滚轮 | 上一张可见工作表 |
| 单元格区域 | 上下滚轮 | 保留 Excel 原有的内容滚动 |

标签栏滚动调用 Excel 左下角左右箭头的原生操作，动画由 Excel 绘制。
横向拨动产生的同方向连续信号会合并，默认停顿 **200ms** 后才能再次切换；反向拨动立即生效。
这是防重复间隔，首次切换立即执行。

隐藏工作表会跳过。按住 Ctrl、Shift、Alt 或鼠标按键时保留原操作。
Excel 未就绪、编辑单元格或对话框占用焦点时不切换。
不需要启用宏；切换会触发工作簿已有的工作表激活事件，与点击标签相同。

## 安装

需要 [Windhawk](https://windhawk.net/) 和 Windows 桌面版 **64 位 Excel**。

推荐从本仓库下载 `excel-wheel-scroll-sheets.wh.cpp`，在 Windhawk 中点击“新建 Mod”，
用该文件内容替换编辑器里的源码，然后点击“编译 Mod”。保存并启用后重新打开 Excel。
此方式由你自己的 Windhawk 编译，适合不同的 Windhawk 引擎版本。
更新旧安装时，在该 Mod 的“源代码”页替换源码并编译，保留已有设置。

[Releases](https://github.com/youareanimal/excel-wheel-scroll-sheets/releases) 同时提供源码、预编译 DLL 和首次安装脚本的 ZIP 包。
预编译包使用 Windhawk 1.7.3 的 x64 引擎库构建。首次安装可解压后以管理员身份运行 `install.ps1`；
如果系统的脚本策略阻止运行，可使用上面的 Windhawk 编辑器安装方法。
脚本检测到同名插件或文件时会停止，以保留已有配置；不会覆盖旧安装或重启 Windhawk 服务。

## 设置

Windhawk → 已安装的 Mod → **Excel 滚轮切换工作表** → **设置**。

- **标签栏上下滚轮行为**：默认只滚动标签栏，也可选择直接切换工作表。
- **使用 Excel 原生标签滚动**：默认开启，使用原生箭头及其动画；关闭后按标签直接滚动。
- **左右拨动防重复（毫秒）**：默认 200。若鼠标一次拨动仍切换多张，可增加该数值。
- **左右滚轮切换工作表**：默认开启，关闭后恢复 Excel 的原有横向滚动。
- **反转滚轮方向**：同时反转上下和左右方向。
- **切换间隔（毫秒）**：默认 150，仅用于标签栏上下滚轮直接切换模式。
- **到达首尾时循环切换**：默认关闭，用于直接切换工作表。

横向滚轮需发送标准 `WM_MOUSEHWHEEL` 事件。普通上下滚轮不等同于左右滚轮，鼠标驱动映射会影响行为。
图标功能区、水平滚动条和状态栏保留原有行为。

## 构建与验证

安装 Windhawk 和 Python 3，在项目目录执行：

```powershell
python build.py
python test-gesture.py
python test-arrow-cache.py
python test-host-scope.py
```

非默认安装目录可设置 `WINDHAWK_DIR`；特定引擎库可设置 `WINDHAWK_ENGINE_LIB`。
构建脚本检查 DLL 的 x64 架构及 Windhawk 入口，手势测试直接提取源码中的状态机，
验证重复信号、200ms 边界、反方向、不同窗口、高精度滚轮增量和计时器回绕。

原生箭头调用、标签栏滚动和用户实际鼠标操作已在一台电脑的 64 位 Excel 中验证。
其他 Office 版本尚未测试。原生箭头不可用时回退到 Excel 的 `ScrollWorkbookTabs`。
0.5.4 将滚轮处理限制在同一 Excel 进程的原生工作簿窗口，箭头搜索限制在底部标签行，
从工作簿左边界选择前两个按钮，排除侧栏和后面的“…”按钮。调试信息仅写入 Windhawk 日志。
设置默认英文，中文界面保留中文标签；设置键、默认值和选项值保持不变。
提取源码的测试覆盖搜索边界、窗口所属进程、缓存失效与手势处理。
0.5.3 已在有、无左侧导航窗格时验证双向滚动；0.5.4 的现场操作验证情况见 [TESTING.md](TESTING.md)。

## 实现与许可

挂钩 Excel 的 `DispatchMessageW`，识别滚轮事件与鼠标区域；通过 MSAA 调用原生导航箭头，
通过 Excel COM 激活相邻可见工作表。不使用截图覆盖或自行绘制的过渡动画。

源码采用 **GPL-3.0-or-later**，许可证正文见 [LICENSE](LICENSE)。
本项目依赖 Windhawk 和 Excel，未宣称滚轮切换标签的思路为首创。

---

## English

This mod brings WPS-style mouse wheel navigation to Excel, making it easier and faster to browse sheet tabs and switch between worksheets in workbooks with many sheets.

### Features

1. **Tilt the wheel to switch worksheets**

   With a mouse that supports left/right wheel tilt, such as the Logitech G502, tilt the wheel over the worksheet area to switch to the previous or next worksheet.

2. **Scroll the wheel to browse sheet tabs**

   Hover over the sheet tab bar at the bottom of Excel and scroll the wheel up or down to reveal tabs that are out of view. This scrolls the tab bar without changing the active worksheet—especially useful for workbooks with many sheets.

A Windhawk mod for 64-bit desktop Excel on Windows. Tab-strip scrolling uses Excel's native arrows.
Repeated same-direction input is grouped with a configurable quiet period (200ms by default).
Build from the source using Windhawk's local mod editor.
