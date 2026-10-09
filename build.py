from pathlib import Path
import subprocess
import json
import struct
import hashlib
import datetime
import sys

root = Path(__file__).resolve().parent
import os
import re
windhawk = Path(os.environ.get('WINDHAWK_DIR', r'C:\Program Files\Windhawk'))
compiler = windhawk / 'Compiler'
engine_override = os.environ.get('WINDHAWK_ENGINE_LIB')
def version_key(path):
    return tuple(int(part) for part in re.findall(r'\d+', path.parent.parent.name))
engines = sorted((windhawk / 'Engine').glob('*/64/windhawk.lib'), key=version_key)
if engine_override:
    engine = Path(engine_override)
elif engines:
    engine = engines[-1]
else:
    raise SystemExit('Windhawk x64 engine library not found; set WINDHAWK_ENGINE_LIB.')
source = root / 'excel-wheel-scroll-sheets.wh.cpp'
output = root / 'excel-wheel-scroll-sheets_0.5.1.dll'
args = [
    str(compiler / 'bin' / 'clang++.exe'), '-std=c++23', '-O2', '-shared',
    '-DUNICODE', '-D_UNICODE', '-DWINVER=0x0A00', '-D_WIN32_WINNT=0x0A00',
    '-D_WIN32_IE=0x0A00', '-DNTDDI_VERSION=0x0A000008', '-D__USE_MINGW_ANSI_STDIO=0',
    '-DWH_MOD', '-DWH_MOD_ID=L"excel-wheel-scroll-sheets"', '-DWH_MOD_VERSION=L"0.5.1"',
    str(engine), '-x', 'c++', '-', '-include', 'windhawk_api.h',
    '-target', 'x86_64-w64-mingw32', '-Wl,--export-all-symbols', '-o', str(output),
    '-loleacc', '-lole32', '-loleaut32', '-luuid',
]
start = datetime.datetime.now(datetime.timezone.utc)
verify_only = '--verify-only' in sys.argv
if not verify_only:
    result = subprocess.run(args, input=source.read_bytes(), cwd=compiler, capture_output=True)
    (root / 'build.log').write_bytes(result.stdout + result.stderr)
    print(result.stdout.decode('utf-8', errors='replace'))
    print(result.stderr.decode('utf-8', errors='replace'))
    if result.returncode:
        raise SystemExit(result.returncode)

# Check the resulting PE architecture, DLL flag, and Windhawk entry points without loading it.
data = output.read_bytes()
assert data[:2] == b'MZ'
pe = struct.unpack_from('<I', data, 0x3c)[0]
assert data[pe:pe+4] == b'PE\0\0'
machine, section_count = struct.unpack_from('<HH', data, pe+4)
optional_size, characteristics = struct.unpack_from('<HH', data, pe+20)
optional = pe+24
assert machine == 0x8664 and characteristics & 0x2000
assert struct.unpack_from('<H', data, optional)[0] == 0x20b
sections = []
for i in range(section_count):
    at = optional+optional_size+i*40
    virtual_size, virtual_address, raw_size, raw_address = struct.unpack_from('<IIII', data, at+8)
    sections.append((virtual_address, max(virtual_size, raw_size), raw_address))
def offset(rva):
    for address, size, raw in sections:
        if address <= rva < address+size:
            return raw + rva-address
    raise ValueError(f'Unmapped RVA: {rva}')
def zstring(at):
    return data[at:data.index(b'\0', at)].decode('ascii')
exports_rva = struct.unpack_from('<I', data, optional+112)[0]
exports_at = offset(exports_rva)
name_count = struct.unpack_from('<I', data, exports_at+24)[0]
names_at = offset(struct.unpack_from('<I', data, exports_at+32)[0])
exports = [zstring(offset(struct.unpack_from('<I', data, names_at+i*4)[0])) for i in range(name_count)]
entrypoints = [name for name in exports if 'Wh_Mod' in name]
assert '_Z10Wh_ModInitv' in entrypoints
assert '_Z12Wh_ModUninitv' in entrypoints
assert '_Z15Wh_ModAfterInitv' in entrypoints
assert '_Z21Wh_ModSettingsChangedv' in entrypoints
imports = []
imports_rva = struct.unpack_from('<I', data, optional+120)[0]
imports_at = offset(imports_rva)
while any(data[imports_at:imports_at+20]):
    name_rva = struct.unpack_from('<I', data, imports_at+12)[0]
    imports.append(zstring(offset(name_rva)))
    imports_at += 20
report = {
    'exit_code': 0,
    'compiler': str(compiler / 'bin' / 'clang++.exe'),
    'engine': str(engine), 'architecture': 'x86-64',
    'dll': str(output), 'size_bytes': len(data),
    'sha256': hashlib.sha256(data).hexdigest(),
    'windhawk_exports': entrypoints, 'imports': imports,
    'duration_seconds': None if verify_only else (datetime.datetime.now(datetime.timezone.utc)-start).total_seconds(),
    'arguments': args,
}
(root / 'build-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k != 'arguments'}, ensure_ascii=False, indent=2))
