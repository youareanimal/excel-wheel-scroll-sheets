from pathlib import Path
import os
import subprocess

root = Path(__file__).resolve().parent
source = (root / 'excel-wheel-scroll-sheets.wh.cpp').read_text(encoding='utf-8')
host_function = source[source.index('HWND GetWorksheetWindow('):source.index('bool SameRect(')]
test = r'''#include <cassert>
#include <cstdio>
#include <cwchar>
#include <cstdint>
#include <map>
using DWORD=unsigned;using HWND=void*;
HWND h(unsigned value){return reinterpret_cast<HWND>(uintptr_t(value));}
#define ARRAYSIZE(x) (sizeof(x)/sizeof(x[0]))
constexpr int GA_ROOT=2;
struct Window { HWND parent,root;DWORD pid;const wchar_t* cls; };
std::map<HWND,Window> windows={
 {h(1),{h(0),h(1),42,L"XLMAIN"}}, {h(2),{h(1),h(1),42,L"EXCEL7"}},
 {h(3),{h(1),h(1),42,L"TaskPane"}}, {h(4),{h(3),h(1),99,L"EXCEL7"}},
 {h(5),{h(2),h(1),99,L"WebView"}}, {h(6),{h(2),h(1),42,L"ChildControl"}},
 {h(7),{h(0),h(7),43,L"XLMAIN"}}, {h(8),{h(7),h(7),43,L"EXCEL7"}}
};
DWORD GetCurrentProcessId(){return 42;}
DWORD GetWindowThreadProcessId(HWND w,DWORD* pid){*pid=windows[w].pid;return 1;}
HWND GetAncestor(HWND w,int){return windows[w].root;}
HWND GetParent(HWND w){return windows[w].parent;}
int GetClassNameW(HWND w,wchar_t* output,unsigned count){std::wcsncpy(output,windows[w].cls,count-1);return 1;}
''' + host_function + r'''
int main(){
 assert(GetWorksheetWindow(h(2),h(1))==h(2));
 assert(GetWorksheetWindow(h(6),h(1))==h(2));
 assert(GetWorksheetWindow(h(3),h(1))==nullptr);
 assert(GetWorksheetWindow(h(4),h(1))==nullptr);
 assert(GetWorksheetWindow(h(5),h(1))==nullptr);
 assert(GetWorksheetWindow(h(8),h(7))==nullptr);
 assert(GetWorksheetWindow(h(2),h(7))==nullptr);
 std::puts("PASS: native workbook ownership; task panes, foreign child HWNDs, foreign EXCEL7 classes and wrong roots rejected");
}
'''
file = root / 'host-scope-test.cpp'
file.write_text(test, encoding='utf-8')
exe = root / 'host-scope-test.exe'
compiler = Path(os.environ.get('WINDHAWK_DIR', r'C:\Program Files\Windhawk')) / 'Compiler' / 'bin' / 'clang++.exe'
r = subprocess.run([str(compiler), '-std=c++23', '-static', str(file), '-o', str(exe)], capture_output=True, text=True)
if r.returncode:
    print(r.stdout+r.stderr)
    raise SystemExit(r.returncode)
r = subprocess.run([str(exe)], capture_output=True, text=True)
print(r.stdout+r.stderr)
(root / 'host-scope-test-result.txt').write_text(r.stdout+r.stderr, encoding='utf-8')
raise SystemExit(r.returncode)
