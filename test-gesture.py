from pathlib import Path
import subprocess
import os
root=Path(__file__).parent
source=(root/'excel-wheel-scroll-sheets.wh.cpp').read_text(encoding='utf-8')
start=source.index('struct HorizontalGesture {')
end=source.index('thread_local HorizontalGesture',start)
test=r'''
#include <cstdint>
#include <cstdlib>
#include <cassert>
#include <cstdio>
using HWND=void*;
using DWORD=uint32_t;
constexpr int WHEEL_DELTA=120;
'''+source[start:end]+r'''
int main() {
 HWND a=reinterpret_cast<HWND>(1),b=reinterpret_cast<HWND>(2);
 HorizontalGesture g;
 assert(g.Accept(a,1000,120,450));
 assert(!g.Accept(a,1200,120,450)); // Previous throttle let a second sheet through.
 assert(!g.Accept(a,1500,120,450)); // Repeat updates the quiet-period clock.
 assert(!g.Accept(a,1900,120,450));
 assert(g.Accept(a,2350,120,450)); // Quiet period rearms.
 assert(g.Accept(a,2360,-120,450)); // Reverse gesture is immediate.
 assert(!g.Accept(a,2560,-120,450));
 assert(g.Accept(b,2561,-120,450)); // Another workbook window is independent.
 g.Reset();
 assert(!g.Accept(a,3000,40,450));
 assert(!g.Accept(a,3010,40,450));
 assert(g.Accept(a,3020,40,450)); // High-resolution deltas accumulate once.
 assert(!g.Accept(a,3220,240,450)); // A large repeat still cannot activate twice.
 g.Reset();
 assert(g.Accept(a,0xfffffff0,120,450));
 assert(!g.Accept(a,20,120,450)); // DWORD clock wrap is safe.
 assert(g.Accept(a,500,120,450));
 g.Reset();
 assert(g.Accept(a,10000,120,200));
 assert(!g.Accept(a,10199,120,200));
 assert(!g.Accept(a,10398,120,200)); // Repeats extend the 200 ms quiet period.
 assert(g.Accept(a,10598,120,200)); // Exactly 200 ms rearms.
 assert(g.Accept(a,10599,-120,200));
 assert(!g.Accept(a,10600,-240,200));
 std::puts("PASS: repeat suppression, quiet rearm, reverse, window, partial delta, clock wrap");
}
'''
file=root/'gesture-test.cpp'
file.write_text(test,encoding='utf-8')
exe=root/'gesture-test.exe'
compiler=Path(os.environ.get('WINDHAWK_DIR', r'C:\Program Files\Windhawk'))/'Compiler'/'bin'/'clang++.exe'
r=subprocess.run([str(compiler),'-std=c++23','-static',str(file),'-o',str(exe)],capture_output=True,text=True)
print(r.stdout+r.stderr)
if r.returncode: raise SystemExit(r.returncode)
r=subprocess.run([str(exe)],capture_output=True,text=True)
print(r.stdout+r.stderr)
(root/'gesture-test-result.txt').write_text(r.stdout+r.stderr,encoding='utf-8')
raise SystemExit(r.returncode)
