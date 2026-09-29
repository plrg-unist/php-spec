#!/usr/bin/env python3
"""A rejected typed static rebind preserves both cells and type sources."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (b'<?php class A { public static int $x=1; public static string $y="1"; } '
          b'$r=&A::$x; try { A::$y =& $r; } catch(TypeError $e) {}')


def main():
    out = Path(tempfile.mkdtemp(prefix='class-static-reference-conflict-', dir=ROOT / '.tools'))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = modules + [Path(__file__), ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
                         ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so']
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    source = out / 'source.php'
    source.write_bytes(SOURCE)
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE).decode()})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'], checked
    finally:
        frontend.close()
        adapter.close()
    initial = ('$php_run(' + checked['fixture'] + ', 0, '
               + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')')
    helpers = '''
dec $static_bind_one(ptask) : (porigin,ptbytes,nat*,int)?
def $static_bind_one(PROPERTY_REF_BIND_CV (BASE_CLASS_STATIC porigin ptbytes) n_name* z) = ((porigin,ptbytes,n_name*,z))
def $static_bind_one(ptask) = eps -- otherwise
dec $static_bind_pending(ptask*) : (porigin,ptbytes,nat*,int)?
def $static_bind_pending(eps) = eps
def $static_bind_pending(ptask :: ptask_tail*) = (porigin,ptbytes,n_name*,z)
  -- if $static_bind_one(ptask) = ((porigin,ptbytes,n_name*,z))
def $static_bind_pending(ptask :: ptask_tail*) = $static_bind_pending(ptask_tail*)
  -- if $static_bind_one(ptask) = eps
dec $static_bind_seek(pstate,nat) : pstate
def $static_bind_seek(S,n) = S -- if $static_bind_pending(S.TODO) =/= eps
def $static_bind_seek(S,n) = $static_bind_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $static_bind_pending(S.TODO) = eps
  -- if $(n > 0)
'''
    checks = [
        'S_initial = ' + initial,
        'S = $static_bind_seek(S_initial[.COMPLETION = NORMAL], 256)',
        '$static_bind_pending(S.TODO) = ((porigin_actual,ptbytes_name,n_name*,z))',
        'ptbytes_name = [121]',
        'S.CLASSES = [pclassdesc_a]',
        'pclassdesc_a.PROPERTIES = [ppropertydesc_x,ppropertydesc_y]',
        'S.CLASSSTATICS = [pclassstatic_x,pclassstatic_y]',
        'pclassstatic_x.STATE = PROP_VALUE (ALIAS n_x)',
        'pclassstatic_y.STATE = PROP_VALUE (DIRECT (PSTRING ([49])))',
        'S.PROPREFS = [ppropref_x]',
        'ppropref_x.CELL = n_x',
        'ppropref_x.SOURCES = [CLASS_PROP_SOURCE ppropertydesc_x.ORIGIN]',
        'S.STORE[n_x] = DEFINED (PINT 1)',
        '$class_state_valid(S) /\\ $proprefs_valid(S) /\\ $heap_valid($heap_graph(S))',
        'S_done = $drive(S[.COMPLETION = NORMAL], 2048)',
        'S_done.COMPLETION = NORMAL',
        'S_done.CLASSSTATICS = S.CLASSSTATICS',
        'S_done.PROPREFS = S.PROPREFS',
        'S_done.STORE[n_x] = S.STORE[n_x]',
        '$class_state_valid(S_done) /\\ $proprefs_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        '~$proprefs_valid(S_done[.PROPREFS = [ppropref_x[.SOURCES = [CLASS_PROP_SOURCE ppropertydesc_x.ORIGIN,CLASS_PROP_SOURCE ppropertydesc_y.ORIGIN]]]])',
    ]
    fixture = out / 'protocol.watsup'
    fixture.write_text(helpers + 'dec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + x + '\n' for x in checks))
    result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                             *map(str, modules), str(fixture)], capture_output=True, text=True, timeout=120)
    (out / 'stdout').write_text(result.stdout)
    (out / 'stderr').write_text(result.stderr)
    assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, result.stderr[-3500:]
    assert before == {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    (out / 'report.json').write_text(json.dumps({'result': 'pass', 'inputs': before,
        'source_sha256': hashlib.sha256(SOURCE).hexdigest(), 'assertions': len(checks)}, indent=2) + '\n')
    print('PASS class static reference conflict protocol', len(checks), out)


if __name__ == '__main__':
    main()
