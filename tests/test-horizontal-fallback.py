"""Replay the actual hook without driving Excel. Pass the v0.5.5 candidate source."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--source', type=Path, required=True)
parser.add_argument('--output-dir', type=Path, default=Path('.test-output-horizontal-fallback'))
args = parser.parse_args()
source = args.source.read_text(encoding='utf-8')
gesture = source[source.index('struct HorizontalGesture {'):source.index('thread_local HorizontalGesture')]
hook = source[source.index('LRESULT WINAPI DispatchMessageWHook('):source.index('\nvoid LoadSettings()')]
prefix = r'''
#include <algorithm>
#include <atomic>
#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cwchar>
#include <vector>
#undef assert
#define assert(test) do { if(!(test)) { std::fprintf(stderr,"FAIL: %s (line %d)\n",#test,__LINE__); std::exit(1); } } while(false)
#define WINAPI
#define ARRAYSIZE(x) (sizeof(x)/sizeof((x)[0]))
#define Wh_Log(...) ((void)0)
using HWND=void*;
using DWORD=uint32_t;
using UINT=unsigned;
using ULONGLONG=uint64_t;
using WPARAM=uintptr_t;
using LPARAM=intptr_t;
using LRESULT=intptr_t;
struct POINT { int32_t x,y; };
struct RECT { int32_t left,top,right,bottom; };
struct MSG { HWND hwnd; UINT message; WPARAM wParam; LPARAM lParam; DWORD time; POINT pt; };
constexpr UINT WM_MOUSEWHEEL=0x20a, WM_MOUSEHWHEEL=0x20e;
constexpr int WHEEL_DELTA=120, GA_ROOT=2, VK_CONTROL=17, VK_SHIFT=16, VK_MENU=18;
int GET_KEYSTATE_WPARAM(WPARAM x) { return x&0xffff; }
int GET_WHEEL_DELTA_WPARAM(WPARAM x) { return int16_t(x>>16); }
int GET_X_LPARAM(LPARAM x) { return int16_t(x); }
int GET_Y_LPARAM(LPARAM x) { return int16_t(x>>16); }
HWND rootWindow=reinterpret_cast<HWND>(1), worksheetWindow=reinterpret_cast<HWND>(2);
HWND GetAncestor(HWND,int) { return rootWindow; }
int GetClassNameW(HWND,wchar_t* out,int) { std::wcscpy(out,L"XLMAIN"); return 6; }
HWND GetForegroundWindow() { return rootWindow; }
bool IsWindowEnabled(HWND) { return true; }
short GetAsyncKeyState(int) { return 0; }
HWND WindowFromPoint(POINT) { return worksheetWindow; }
HWND GetWorksheetWindow(HWND,HWND) { return worksheetWindow; }
bool IsHorizontalSwitchTarget(HWND,POINT,RECT&) { return true; }
bool IsSheetTab(POINT,HWND,RECT&) { return false; }
ULONGLONG GetTickCount64() { return 10000; }
bool g_insideHook=false;
std::atomic<bool> g_horizontal{true},g_reverse{false},g_scrollTabs{true};
std::atomic<unsigned> g_horizontalGestureMs{50},g_throttle{150};
HWND g_lastRoot=nullptr;
UINT g_lastAxis=0; // Compatibility with the pre-fix handler for the regression check.
ULONGLONG g_lastWheel=0,g_lastSwitch=0;
int g_deltaRemainder=0;
bool actionSucceeds=false, worksheetReady=false;
int forwarded=0,attempted=0,readyChecks=0;
std::vector<MSG> originalMessages,sentMessages;
bool IsWorksheetReady(HWND) { ++readyChecks; return worksheetReady; }
bool ApplyWheelAction(HWND,int,bool,POINT,int,const RECT&) { ++attempted; return actionSucceeds; }
LRESULT OriginalDispatch(const MSG* message) {
 ++forwarded; originalMessages.push_back(*message); return 73;
}
LRESULT (*g_originalDispatchMessageW)(const MSG*)=OriginalDispatch;
'''
tests = r'''
void reset(unsigned gap,bool ready,bool action) {
 g_horizontalGesture.Reset(); g_insideHook=false; g_horizontal=true;
 g_horizontalGestureMs=gap; worksheetReady=ready; actionSucceeds=action;
 rootWindow=reinterpret_cast<HWND>(1);
 forwarded=attempted=readyChecks=0; originalMessages.clear(); sentMessages.clear();
}
void send(int delta,DWORD time) {
 MSG message{worksheetWindow,WM_MOUSEHWHEEL,WPARAM(uint16_t(delta))<<16,
             LPARAM(10)|(LPARAM(20)<<16),time,{10,20}};
 sentMessages.push_back(message);
 DispatchMessageWHook(&message);
}
void assertAllForwarded() {
 assert(originalMessages.size()==sentMessages.size());
 for(unsigned i=0;i<sentMessages.size();++i) {
  const MSG& a=originalMessages[i]; const MSG& b=sentMessages[i];
  assert(a.hwnd==b.hwnd && a.message==b.message && a.wParam==b.wParam);
  assert(a.lParam==b.lParam && a.time==b.time && a.pt.x==b.pt.x && a.pt.y==b.pt.y);
 }
}
int main() {
 for(unsigned gap: {50u,200u}) {
  for(int delta: {1,15,30,40,60,120,-1,-40,-120}) {
   reset(gap,false,false);
   for(int i=0;i<120;++i) send(delta,1000+i);
   assertAllForwarded();
   assert(readyChecks==(std::abs(delta)<120?1:0));
   assert(attempted==(std::abs(delta)<120?0:1));

   reset(gap,true,false);
   for(int i=0;i<120;++i) send(delta,2000+i);
   assertAllForwarded(); assert(attempted==1);

   reset(gap,true,true);
   for(int i=0;i<240;++i) send(delta,3000+i);
   assert(attempted==1 && forwarded==0);
  }
 }
 std::puts("PASS: not-ready and failed-activation bursts forward every original message in order; successful bursts switch once (50/200 ms, small/coarse deltas, both directions).");

 reset(50,true,false);
 send(40,4000); send(40,4010); send(40,4020);
 assertAllForwarded(); assert(attempted==1);
 actionSucceeds=true;
 send(120,4069); assert(attempted==1 && forwarded==4); // 49 ms keeps failure latched.
 send(120,4119); assert(attempted==2 && forwarded==4); // Exactly 50 ms retries.
 send(120,4120); assert(attempted==2 && forwarded==4);

 reset(50,true,false); send(120,5000);
 actionSucceeds=true; send(-120,5001);
 assert(attempted==2 && forwarded==1); // Reversal starts a new gesture immediately.
 reset(50,true,false); send(120,6000);
 actionSucceeds=true; rootWindow=reinterpret_cast<HWND>(3); send(120,6001);
 assert(attempted==2 && forwarded==1); // Another workbook root retries.

 reset(50,true,true); send(40,7000); send(40,7010);
 actionSucceeds=false; send(40,7020);
 assertAllForwarded(); assert(attempted==1); // Failure after buffering restores earlier messages.
 reset(50,true,false);
 send(40,0xfffffff0u); send(40,0xfffffffau); send(40,4);
 assertAllForwarded(); actionSucceeds=true; send(120,54);
 assert(attempted==2 && forwarded==3); // Timestamp wrap and quiet-period boundary.

 reset(50,false,false); g_horizontal=false;
 for(int i=0;i<12;++i) send(40,8000+i);
 assertAllForwarded(); assert(attempted==0 && readyChecks==0);
 reset(50,true,true); send(0,9000);
 assertAllForwarded(); assert(attempted==0 && readyChecks==0);
 std::puts("PASS: failure latch, exact quiet boundary, reversal, window change, buffered replay, timer wrap, disabled switching and zero delta.");
}
'''
args.output_dir.mkdir(parents=True, exist_ok=True)
test_path = args.output_dir / 'horizontal-fallback.cpp'
test_path.write_text(prefix + gesture + '\nthread_local HorizontalGesture g_horizontalGesture;\n' + hook + tests, encoding='utf-8')
exe = args.output_dir / 'horizontal-fallback.exe'
compiler = Path(os.environ.get('WINDHAWK_DIR', r'C:\Program Files\Windhawk')) / 'Compiler' / 'bin' / 'clang++.exe'
build = subprocess.run([str(compiler), '-std=c++23', '-static', str(test_path), '-o', str(exe)], capture_output=True, text=True)
if build.returncode:
    print(build.stdout + build.stderr)
    raise SystemExit(build.returncode)
result = subprocess.run([str(exe.resolve())], capture_output=True, text=True)
print(result.stdout + result.stderr)
(args.output_dir / 'result.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
(args.output_dir / 'evidence.json').write_text(json.dumps({
    'source_sha256': hashlib.sha256(args.source.read_bytes()).hexdigest(),
    'method': 'Actual gesture state and full message hook; mocked Win32 scope/readiness/action outcome; original message identity, order and count checked.',
    'not_claimed': 'Physical touchpad or live Excel validation.',
    'exit_code': result.returncode,
}, indent=2), encoding='utf-8')
raise SystemExit(result.returncode)
