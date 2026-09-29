#!/usr/bin/env python3
"""A pending computed static name cannot swap its literal class selector."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (b'<?php class A { public static $x=1; } class B { public static $x=2; } '
          b'$n="x"; echo A::${$n};')


def main():
    out = Path(tempfile.mkdtemp(prefix='class-static-selector-', dir=ROOT / '.tools'))
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
dec $static_name_one(ptask) : (phpType19,poperand,int)?
def $static_name_one(STATIC_PROP_NAME phpType19 poperand z) = ((phpType19,poperand,z))
def $static_name_one(ptask) = eps -- otherwise
dec $static_name_pending(ptask*) : (phpType19,poperand,int)?
def $static_name_pending(eps) = eps
def $static_name_pending(ptask :: ptask_tail*) = (phpType19,poperand,z)
  -- if $static_name_one(ptask) = ((phpType19,poperand,z))
def $static_name_pending(ptask :: ptask_tail*) = $static_name_pending(ptask_tail*)
  -- if $static_name_one(ptask) = eps
dec $static_name_seek(pstate,nat) : pstate
def $static_name_seek(S,n) = S -- if $static_name_pending(S.TODO) =/= eps
def $static_name_seek(S,n) = $static_name_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $static_name_pending(S.TODO) = eps
  -- if $(n > 0)
'''
    checks = [
        'S_initial = ' + initial,
        'S = $static_name_seek(S_initial[.COMPLETION = NORMAL], 128)',
        '$static_name_pending(S.TODO) = ((phpType19,poperand,z))',
        'poperand = KNOWN (PSTRING $ptascii("A"))',
        '$call_descriptors_valid(S)',
        '$class_state_valid(S)',
        '$heap_valid($heap_graph(S))',
        '$call_task_valid(S, STATIC_PROP_NAME phpType19 poperand z)',
        '~$call_task_valid(S, STATIC_PROP_NAME phpType19 (KNOWN (PSTRING $ptascii("B"))) z)',
        'S_done = $drive(S[.COMPLETION = NORMAL], 2048)',
        'S_done.COMPLETION = NORMAL',
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
    print('PASS class static selector protocol', len(checks), out)


if __name__ == '__main__':
    main()
