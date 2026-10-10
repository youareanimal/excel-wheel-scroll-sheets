from pathlib import Path
import subprocess
import os
root=Path(__file__).resolve().parent
source=(root/'excel-wheel-scroll-sheets.wh.cpp').read_text(encoding='utf-8')
start=source.index('struct NativeArrowCandidates {')
end=source.index('thread_local NativeArrowCache',start)
test=r'''#include <algorithm>
#include <cassert>
#include <cstdio>
#include <type_traits>
using LONG=long;
using HWND=void*;
struct RECT { LONG left,top,right,bottom; };
struct POINT { LONG x,y; };
constexpr LONG ROLE_SYSTEM_PAGETAB=37,ROLE_SYSTEM_PUSHBUTTON=43;
'''+source[start:end]+r'''
int main() {
 HWND a=reinterpret_cast<HWND>(1),b=reinterpret_cast<HWND>(2);
 RECT root{0,0,1091,984},left{293,929,319,955},right{327,929,353,955};
 unsigned calls=0,closeCalls=0;
 auto probe=[&](POINT p,LONG& role,RECT& box,bool& bounds) {
  ++calls; bounds=true;
  if(p.x>=385 && p.x<445) {role=37;box={385,929,445,955};}
  else if(p.x>=445 && p.x<700) {role=37;box={445,929,700,955};}
  else if(p.x>=700 && p.x<970) {role=37;box={700,929,970,955};}
  else if(p.x>=327 && p.x<353) {role=43;box=right;}
  else if(p.x>=293 && p.x<319) {role=43;box=left;}
  else if(p.x>=212 && p.x<254) {++closeCalls;role=43;box={212,925,254,951};}
  else {role=0;bounds=false;}
  return true;
 };
 NativeArrowCandidates found;
 assert(FindNativeArrowPair(root,POINT{420,944},probe,found));
 assert(found.Select(-1)->left==293 && found.Select(1)->left==327);
 assert(calls<20 && closeCalls==0);
 unsigned firstCalls=calls;
 NativeArrowCandidates distant;calls=0;
 assert(FindNativeArrowPair(root,POINT{920,944},probe,distant));
 assert(calls<25 && distant.Select(1)->left==327 && closeCalls==0);
 NativeArrowCandidates missing;
 auto empty=[](POINT,LONG& role,RECT&,bool& bounds){role=0;bounds=false;return true;};
 assert(!FindNativeArrowPair(root,POINT{420,944},empty,missing));
 NativeArrowCache cache;
 assert(!cache.Matches(a,root,POINT{420,944}));
 cache.root=a;cache.rootRect=root;cache.boxes[0]=left;cache.boxes[1]=right;
 cache.targets[0]=a;cache.targets[1]=b;cache.names[0]=11;cache.names[1]=22;
 assert(cache.Matches(a,root,POINT{420,944}));
 assert(cache.IdentityMatches(0,left,a,11));
 assert(cache.IdentityMatches(1,right,b,22));
 assert(!cache.IdentityMatches(0,RECT{12,929,38,955},a,11)); // Pane closes.
 assert(!cache.IdentityMatches(0,left,b,11)); // Same rectangle, another HWND.
 assert(!cache.IdentityMatches(0,left,a,99)); // Same position, another control.
 assert(!cache.Matches(b,root,POINT{420,944}));
 assert(!cache.Matches(a,RECT{0,0,900,984},POINT{420,944}));
 assert(!cache.Matches(a,RECT{-700,0,391,984},POINT{-280,944}));
 assert(!cache.Matches(a,root,POINT{420,900}));
 cache.Reset();assert(!cache.Matches(a,root,POINT{420,944}));
 static_assert(std::is_trivially_copyable_v<NativeArrowCache>);
 std::printf("PASS: %u probes on first discovery; cached path validates two controls; pane/window/identity invalidation and missing arrows\n",firstCalls);
}
'''
file=root/'arrow-cache-test.cpp'
file.write_text(test,encoding='utf-8')
exe=root/'arrow-cache-test.exe'
compiler=Path(os.environ.get('WINDHAWK_DIR', r'C:\Program Files\Windhawk'))/'Compiler'/'bin'/'clang++.exe'
r=subprocess.run([str(compiler),'-std=c++23','-static',str(file),'-o',str(exe)],capture_output=True,text=True)
if r.returncode:print(r.stdout+r.stderr);raise SystemExit(r.returncode)
r=subprocess.run([str(exe)],capture_output=True,text=True)
(root/'arrow-cache-test-result.txt').write_text(r.stdout+r.stderr,encoding='utf-8')
print(r.stdout+r.stderr)
raise SystemExit(r.returncode)
