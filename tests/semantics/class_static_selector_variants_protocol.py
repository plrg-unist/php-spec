#!/usr/bin/env python3
"""Authenticate captured dynamic static class selectors at a pending name fetch."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('casefold', b'<?php class A { public static $x=1; } class B { public static $x=2; } '
     b'$c="a"; $n="x"; echo $c::${$n};', [
        'poperand = KNOWN (PSTRING ([97]))',
        '~$call_task_valid(S, STATIC_PROP_NAME phpType19 (KNOWN (PSTRING $ptascii("B"))) z)',
    ]),
    ('object', b'<?php class A { public static $x=1; } class B { public static $x=2; } '
     b'$a=new A; $b=new B; $n="x"; echo $a::${$n};', [
        '$lookup(S.ENV,$ptascii("a")) = (n_a_cell)',
        '$lookup(S.ENV,$ptascii("b")) = (n_b_cell)',
        'S.STORE[n_a_cell] = DEFINED (POBJECT n_a)',
        'S.STORE[n_b_cell] = DEFINED (POBJECT n_b)',
        'poperand = KNOWN (POBJECT n_a)',
        '~$call_task_valid(S, STATIC_PROP_NAME phpType19 (KNOWN (POBJECT n_b)) z)',
    ]),
]
HELPERS = '''
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


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(tempfile.mkdtemp(prefix='class-static-selector-variants-', dir=ROOT / '.tools'))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = modules + [Path(__file__), ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
                         ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so']
    before = {str(p.relative_to(ROOT)): sha(p) for p in watched}
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    reports = []
    try:
        for name, source_bytes, extra in CASES:
            directory = out / name
            directory.mkdir()
            source = directory / 'source.php'
            source.write_bytes(source_bytes)
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source_bytes).decode()})
            assert parsed['accepted'], parsed
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], checked
            initial = ('$php_run(' + checked['fixture'] + ', 0, '
                       + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')')
            checks = [
                'S_initial = ' + initial,
                'S = $static_name_seek(S_initial[.COMPLETION = NORMAL], 128)',
                '$static_name_pending(S.TODO) = ((phpType19,poperand,z))',
                'S.RESULT = poperand',
                '$call_task_valid(S, STATIC_PROP_NAME phpType19 poperand z)',
                '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $heap_valid($heap_graph(S))',
                *extra,
                'S_done = $drive(S[.COMPLETION = NORMAL], 2048)',
                'S_done.COMPLETION = NORMAL',
            ]
            fixture = directory / 'protocol.watsup'
            fixture.write_text(HELPERS + 'dec $main() : bool\ndef $main() = true\n'
                               + ''.join('  -- if ' + check + '\n' for check in checks))
            result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                     *map(str, modules), str(fixture)], capture_output=True, text=True, timeout=120)
            (directory / 'stdout').write_text(result.stdout)
            (directory / 'stderr').write_text(result.stderr)
            assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, result.stderr[-3500:]
            reports.append({'name': name, 'source_sha256': hashlib.sha256(source_bytes).hexdigest(),
                            'assertions': len(checks)})
            print(name, len(checks), flush=True)
    finally:
        frontend.close()
        adapter.close()
    assert before == {str(p.relative_to(ROOT)): sha(p) for p in watched}
    (out / 'report.json').write_text(json.dumps({'result': 'pass', 'inputs': before,
                                                  'stages': reports}, indent=2) + '\n')
    print('PASS class static selector variants', out)


if __name__ == '__main__':
    main()
