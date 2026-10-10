from pathlib import Path
import subprocess
import os

root = Path(__file__).resolve().parent
source = (root / 'excel-wheel-scroll-sheets.wh.cpp').read_text(encoding='utf-8')
geometry = source[source.index('bool SameRect('):source.index('bool GetAccessibleRect(')]
start = source.index('struct NativeArrowCandidates {')
end = source.index('thread_local NativeArrowCache', start)
test = r'''#include <algorithm>
#include <cassert>
#include <cstdio>
#include <cstdint>
#include <type_traits>
using LONG=int32_t;using DWORD=uint32_t;using HWND=void*;
struct RECT { LONG left,top,right,bottom; };
struct POINT { LONG x,y; };
constexpr LONG ROLE_SYSTEM_PAGETAB=37,ROLE_SYSTEM_PAGETABLIST=60,ROLE_SYSTEM_PUSHBUTTON=43;
''' + geometry + source[start:end] + r'''
int main() {
 HWND a=reinterpret_cast<HWND>(1),b=reinterpret_cast<HWND>(2);
 RECT host{280,253,1091,1010},row{280,982,1091,1010};
 RECT left{293,984,319,1008},right{327,984,353,1008},overflow{360,984,380,1008};
 unsigned calls=0,overflowCalls=0;
 auto probe=[&](POINT p,LONG& role,RECT& box,bool& bounds) {
  ++calls;bounds=false;
  assert(ContainsPoint(row,p));
  if(p.x>=293 && p.x<319){role=43;box=left;bounds=true;}
  else if(p.x>=327 && p.x<353){role=43;box=right;bounds=true;}
  else if(p.x>=360 && p.x<380){++overflowCalls;role=43;box=overflow;bounds=true;}
  else if(p.x>=385){role=37;}
  else role=0;
  return true;
 };
 NativeArrowCandidates found;
 assert(FindNativeArrowPair(row,POINT{420,994},probe,found));
 assert(SameRect(found.boxes[0],left) && SameRect(found.boxes[1],right));
 assert(calls<20 && overflowCalls==0);
 unsigned firstCalls=calls;
 calls=0;NativeArrowCandidates far;
 assert(FindNativeArrowPair(row,POINT{1000,994},probe,far));
 assert(calls==firstCalls && overflowCalls==0);
 unsigned beyond=0;NativeArrowCandidates foreign;
 auto boundary=[&](POINT p,LONG& role,RECT& box,bool& bounds) {
  if(p.x>=320){++beyond;return false;}
  return probe(p,role,box,bounds);
 };
 assert(!FindNativeArrowPair(row,POINT{420,994},boundary,foreign));
 assert(beyond==1 && foreign.count==1);
 unsigned missingCalls=0;NativeArrowCandidates missing;
 auto noArrows=[&](POINT p,LONG& role,RECT&,bool& bounds) {
  ++missingCalls;bounds=false;role=p.x>=385?ROLE_SYSTEM_PAGETAB:0;
  assert(p.x<390);return true;
 };
 assert(!FindNativeArrowPair(row,POINT{1000,994},noArrows,missing));
 assert(missingCalls<30);
 NativeArrowCandidates outside;
 auto wrongBounds=[&](POINT,LONG& role,RECT& box,bool& bounds) {
  role=43;bounds=true;box={281,700,310,1008};return true;
 };
 assert(!FindNativeArrowPair(row,POINT{420,994},wrongBounds,outside));
 NativeArrowCandidates badPoint;
 assert(!FindNativeArrowPair(row,POINT{420,700},probe,badPoint));
 NativeArrowCache cache;
 assert(!cache.Matches(a,host,row));
 cache.worksheet=a;cache.hostRect=host;cache.row=row;
 cache.boxes[0]=left;cache.boxes[1]=right;cache.names[0]=11;cache.names[1]=22;
 cache.valid=true;
 assert(cache.Matches(a,host,row));
 assert(cache.IdentityMatches(0,left,11));
 assert(!cache.IdentityMatches(0,left,99));
 assert(!cache.IdentityMatches(0,RECT{12,984,38,1008},11));
 assert(!cache.Matches(b,host,row));
 assert(!cache.Matches(a,RECT{0,253,1091,1010},row));
 assert(!cache.Matches(a,host,RECT{280,950,1091,978}));
 cache.valid=false;cache.failed=true;cache.failedAt=1000;
 assert(cache.FailedRecently(1499));assert(!cache.FailedRecently(1500));
 cache.failedAt=0xfffffff0;assert(cache.FailedRecently(20));
 cache.Reset();assert(!cache.Matches(a,host,row) && !cache.FailedRecently(20));
 static_assert(std::is_trivially_copyable_v<NativeArrowCache>);
 std::printf("PASS: %u probes; bounded native row, first arrows before overflow, foreign boundary, missing arrows, cache identity/layout and failure expiry\n",firstCalls);
}
'''
file = root / 'arrow-cache-test.cpp'
file.write_text(test, encoding='utf-8')
exe = root / 'arrow-cache-test.exe'
compiler = Path(os.environ.get('WINDHAWK_DIR', r'C:\Program Files\Windhawk')) / 'Compiler' / 'bin' / 'clang++.exe'
r = subprocess.run([str(compiler), '-std=c++23', '-static', str(file), '-o', str(exe)], capture_output=True, text=True)
if r.returncode:
    print(r.stdout+r.stderr)
    raise SystemExit(r.returncode)
r = subprocess.run([str(exe)], capture_output=True, text=True)
(root / 'arrow-cache-test-result.txt').write_text(r.stdout+r.stderr, encoding='utf-8')
print(r.stdout+r.stderr)
raise SystemExit(r.returncode)
