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
     b'function nm(){global $c;$c="B";echo "N";return "x";} $c="a"; echo $c::${nm()};', [
        'poperand = KNOWN (PSTRING n_class*)',
        '$ptlc(n_class*) = $ptascii("a")',
    ], '(KNOWN (PSTRING $ptascii("B")))', [
        '$lookup(S_head.ENV,$ptascii("c")) = (n_class_cell)',
        'S_head.STORE[n_class_cell] = DEFINED (PSTRING $ptascii("B"))',
    ]),
    ('object', b'<?php class A { public static $x=1; } class B { public static $x=2; } '
     b'function nm(){global $a,$b;$a=$b;echo "N";return "x";} $a=new A; $b=new B; echo $a::${nm()};', [
        '$lookup(S.ENV,$ptascii("a")) = (n_a_cell)',
        '$lookup(S.ENV,$ptascii("b")) = (n_b_cell)',
        'S.STORE[n_a_cell] = DEFINED (POBJECT n_a)',
        'S.STORE[n_b_cell] = DEFINED (POBJECT n_b)',
        'poperand = KNOWN (PSTRING $ptascii("A"))',
        '$heap_owners($heap_graph(S),HOBJECT n_a) = 1',
    ], '(KNOWN (PSTRING $ptascii("B")))', [
        'S_head.STORE[n_a_cell] = DEFINED (POBJECT n_b)',
        '$task_nodes(STATIC_PROP_NAME phpType19 poperand z) = eps',
        '$task_nodes(STATIC_PROP_CAPTURE porigin poperand z) = eps',
        '~((HOBJECT n_a) <- S_head.ALLOCATIONS)',
        'S_raw = S_head[.TODO = (STATIC_PROP_NAME phpType19 (KNOWN (POBJECT n_b)) z) :: (STATIC_PROP_CAPTURE porigin (KNOWN (POBJECT n_b)) z) :: ptask_tail*]',
        '~$call_descriptors_valid(S_raw)',
    ]),
    ('nested', b'<?php class A { public static $x=1; } class B { public static $x=2; } '
     b'function nm(){global $c;$n="x";echo B::${$n};$c="B";return "x";} '
     b'$c="a";echo $c::${nm()};', [
        'poperand = KNOWN (PSTRING n_class*)',
        '$ptlc(n_class*) = $ptascii("a")',
    ], '(KNOWN (PSTRING $ptascii("B")))', [
        '$lookup(S_head.ENV,$ptascii("c")) = (n_class_cell)',
        'S_head.STORE[n_class_cell] = DEFINED (PSTRING $ptascii("B"))',
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
dec $static_name_head(pstate,porigin) : bool
def $static_name_head(S,porigin) = true
  -- if S.ORIGIN = (porigin)
  -- if S.TODO = (STATIC_PROP_NAME phpType19 poperand z) :: ptask_tail*
def $static_name_head(S,porigin) = false -- otherwise
dec $static_name_head_seek(pstate,porigin,nat) : pstate
def $static_name_head_seek(S,porigin,n) = S -- if $static_name_head(S,porigin)
def $static_name_head_seek(S,porigin,n) = $static_name_head_seek($drive_steps(S[.COMPLETION = NORMAL],1),porigin,$nabs($(n - 1)))
  -- if ~$static_name_head(S,porigin)
  -- if $(n > 0)
dec $static_name_without_capture(ptask*,porigin) : ptask*
def $static_name_without_capture(eps,porigin) = eps
def $static_name_without_capture((STATIC_PROP_CAPTURE porigin poperand z) :: ptask_tail*,porigin) = ptask_tail*
def $static_name_without_capture(ptask :: ptask_tail*,porigin) = ptask :: $static_name_without_capture(ptask_tail*,porigin)
  -- if $class_static_capture_origin(ptask) =/= (porigin)
dec $static_name_saved(pstate,porigin,phpType19,poperand,int) : bool
def $static_name_saved(S,porigin,phpType19,poperand,z) = $class_static_name_pair_present(pframe.TODO,porigin,phpType19,poperand,z)
  -- if S.FRAMES = pframe :: pframe_tail*
def $static_name_saved(S,porigin,phpType19,poperand,z) = false -- otherwise
dec $static_name_callback_seek(pstate,porigin,phpType19,poperand,int,nat) : pstate
def $static_name_callback_seek(S,porigin,phpType19,poperand,z,n) = S -- if $static_name_saved(S,porigin,phpType19,poperand,z)
def $static_name_callback_seek(S,porigin,phpType19,poperand,z,n) = $static_name_callback_seek($drive_steps(S[.COMPLETION = NORMAL],1),porigin,phpType19,poperand,z,$nabs($(n - 1)))
  -- if ~$static_name_saved(S,porigin,phpType19,poperand,z)
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
        for name, source_bytes, extra, forged_operand, after in CASES:
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
                'S.ORIGIN = (porigin)',
                'S.RESULT = poperand',
                '$call_task_valid(S, STATIC_PROP_NAME phpType19 poperand z)',
                '$call_task_valid(S, STATIC_PROP_CAPTURE porigin poperand z)',
                '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $heap_valid($heap_graph(S))',
                *extra,
                '~$call_task_valid(S, STATIC_PROP_NAME phpType19 ' + forged_operand + ' z)',
                'S_callback = $static_name_callback_seek(S[.COMPLETION = NORMAL],porigin,phpType19,poperand,z,128)',
                'S_callback.FRAMES = pframe :: pframe_tail*',
                '$call_descriptors_valid(S_callback)',
                '~$call_frames_valid(S_callback,[pframe[.TODO = $static_name_without_capture(pframe.TODO,porigin)]] ++ pframe_tail*)',
                'S_head = $static_name_head_seek(S_callback[.COMPLETION = NORMAL], porigin, 256)',
                'S_head.TODO = (STATIC_PROP_NAME phpType19 poperand z) :: (STATIC_PROP_CAPTURE porigin poperand z) :: ptask_tail*',
                'S_head.RESULT = KNOWN (PSTRING ([120]))',
                '$call_task_valid(S_head, STATIC_PROP_NAME phpType19 poperand z)',
                '$call_task_valid(S_head, STATIC_PROP_CAPTURE porigin poperand z)',
                '$call_descriptors_valid(S_head) /\\ $class_state_valid(S_head) /\\ $heap_valid($heap_graph(S_head))',
                *after,
                'S_forged = S_head[.TODO = (STATIC_PROP_NAME phpType19 ' + forged_operand + ' z) :: (STATIC_PROP_CAPTURE porigin poperand z) :: ptask_tail*]',
                '~$call_task_valid(S_forged, STATIC_PROP_NAME phpType19 ' + forged_operand + ' z)',
                '~$call_descriptors_valid(S_forged)',
                'S_deleted = S_head[.TODO = (STATIC_PROP_NAME phpType19 poperand z) :: ptask_tail*]',
                '~$call_task_valid(S_deleted, STATIC_PROP_NAME phpType19 poperand z)',
                '~$call_descriptors_valid(S_deleted)',
                'S_orphan = S_head[.TODO = (STATIC_PROP_CAPTURE porigin poperand z) :: ptask_tail*]',
                '~$call_task_valid(S_orphan, STATIC_PROP_CAPTURE porigin poperand z)',
                '~$call_descriptors_valid(S_orphan)',
                'S_duplicate_capture = S_head[.TODO = (STATIC_PROP_NAME phpType19 poperand z) :: (STATIC_PROP_CAPTURE porigin poperand z) :: (STATIC_PROP_CAPTURE porigin poperand z) :: ptask_tail*]',
                '~$call_descriptors_valid(S_duplicate_capture)',
                'S_duplicate_name = S_head[.TODO = (STATIC_PROP_NAME phpType19 poperand z) :: (STATIC_PROP_NAME phpType19 poperand z) :: (STATIC_PROP_CAPTURE porigin poperand z) :: ptask_tail*]',
                '~$call_descriptors_valid(S_duplicate_name)',
                'S_wrapped_capture = S_head[.TODO = S_head.TODO ++ [AT porigin (STATIC_PROP_CAPTURE porigin poperand z)]]',
                '~$call_descriptors_valid(S_wrapped_capture)',
                'S_wrapped_name = S_head[.TODO = S_head.TODO ++ [AT porigin (STATIC_PROP_NAME phpType19 poperand z)]]',
                '~$call_descriptors_valid(S_wrapped_name)',
                'S_wrong_origin = S_head[.TODO = (STATIC_PROP_NAME phpType19 poperand z) :: (STATIC_PROP_CAPTURE (PORIGIN 0 eps) poperand z) :: ptask_tail*]',
                '~$call_descriptors_valid(S_wrong_origin)',
                '~$call_task_valid(S_head, STATIC_PROP_NAME phpType19 poperand $(z + 1))',
                '~$call_task_valid(S_head, STATIC_PROP_CAPTURE porigin poperand $(z + 1))',
                '~$call_task_valid(S_head[.CODE = eps], STATIC_PROP_NAME phpType19 poperand z)',
                '~$call_task_valid(S_head[.ORIGIN = (PORIGIN 0 eps)], STATIC_PROP_NAME phpType19 poperand z)',
                'S_done = $drive(S_head[.COMPLETION = NORMAL], 2048)',
                'S_done.COMPLETION = NORMAL',
                'S_done.TODO = eps',
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
