#!/usr/bin/env python3
"""Exception search discards the selected class and its marker together."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (b'<?php class A { public int $p=1; public static $x=1; } '
          b'function nm(){global $a;$a=null;throw new Exception("boom");} '
          b'$a=new A;$r=&$a->p;try{echo $a::${nm()};}catch(Exception $e){echo "C";} '
          b'finally{echo "F";}echo "|",A::$x;')
HELPERS = '''
dec $static_name_capture_head(pstate) : bool
def $static_name_capture_head(S) = true
  -- if S.TODO = (AT porigin_name (EVAL expression_name)) :: (STATIC_PROP_NAME phpType19 poperand z) :: (STATIC_PROP_CAPTURE porigin poperand z) :: ptask_tail*
def $static_name_capture_head(S) = false -- otherwise
dec $static_name_capture_seek(pstate,nat) : pstate
def $static_name_capture_seek(S,n) = S -- if $static_name_capture_head(S)
def $static_name_capture_seek(S,n) = $static_name_capture_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if ~$static_name_capture_head(S)
  -- if $(n > 0)
dec $static_name_throw_head(pstate) : bool
def $static_name_throw_head(S) = true
  -- if S.TODO = (THROW_SEARCH n) :: (STATIC_PROP_NAME phpType19 poperand z) :: (STATIC_PROP_CAPTURE porigin poperand z) :: ptask_tail*
def $static_name_throw_head(S) = false -- otherwise
dec $static_name_throw_seek(pstate,nat) : pstate
def $static_name_throw_seek(S,n) = S -- if $static_name_throw_head(S)
def $static_name_throw_seek(S,n) = $static_name_throw_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if ~$static_name_throw_head(S)
  -- if $(n > 0)
'''


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(tempfile.mkdtemp(prefix='class-static-selector-unwind-', dir=ROOT / '.tools'))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = modules + [Path(__file__), ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
                         ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php-file.so']
    before = {str(p.relative_to(ROOT)): digest(p) for p in watched}
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
    checks = [
        'S_initial = ' + initial,
        'S_capture = $static_name_capture_seek(S_initial[.COMPLETION = NORMAL],256)',
        'S_capture.TODO = (AT porigin_name (EVAL expression_name)) :: (STATIC_PROP_NAME phpType19 poperand z) :: (STATIC_PROP_CAPTURE porigin poperand z) :: ptask_tail*',
        'poperand = KNOWN (PSTRING $ptascii("A"))',
        '$lookup(S_capture.ENV,$ptascii("a")) = (n_cell)',
        'S_capture.STORE[n_cell] = DEFINED (POBJECT n_selector)',
        '$lookup(S_capture.ENV,$ptascii("r")) = (n_refcell)',
        '$propref_at(S_capture.PROPREFS,n_refcell) = (ppropref)',
        '$heap_owners($heap_graph(S_capture),HOBJECT n_selector) = 1',
        '$task_nodes(STATIC_PROP_NAME phpType19 poperand z) = eps /\\ $task_nodes(STATIC_PROP_CAPTURE porigin poperand z) = eps',
        '$call_descriptors_valid(S_capture) /\\ $class_state_valid(S_capture) /\\ $heap_valid($heap_graph(S_capture))',
        'S = $static_name_throw_seek(S_capture[.COMPLETION = NORMAL],256)',
        'S.TODO = (THROW_SEARCH n_exception) :: (STATIC_PROP_NAME phpType19 poperand z) :: (STATIC_PROP_CAPTURE porigin poperand z) :: ptask_tail*',
        'S.ORIGIN = (porigin)',
        'poperand = KNOWN (PSTRING $ptascii("A"))',
        'S.OBJECTS[n_selector] = INSTANCE porigin_class',
        'S.STORE[n_cell] = DEFINED PNULL',
        '~((HOBJECT n_selector) <- S.ALLOCATIONS)',
        '$propref_at(S.PROPREFS,n_refcell) = eps /\\ S.STORE[n_refcell] = DEFINED (PINT 1)',
        '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $heap_valid($heap_graph(S))',
        'S_after = $drive_steps(S[.COMPLETION = NORMAL],1)',
        'S_after.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        '~((HOBJECT n_selector) <- $machine_roots(S_after))',
        'S_after.CLASSSTATICS = S.CLASSSTATICS',
        '$call_descriptors_valid(S_after) /\\ $class_state_valid(S_after) /\\ $heap_valid($heap_graph(S_after))',
        'S_done = $drive(S_after[.COMPLETION = NORMAL],2048)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
    ]
    fixture = out / 'protocol.watsup'
    fixture.write_text(HELPERS + 'dec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + check + '\n' for check in checks))
    result = subprocess.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                             *map(str, modules), str(fixture)], capture_output=True, text=True, timeout=120)
    (out / 'stdout').write_text(result.stdout)
    (out / 'stderr').write_text(result.stderr)
    assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr, result.stderr[-3500:]
    assert before == {str(p.relative_to(ROOT)): digest(p) for p in watched}
    (out / 'report.json').write_text(json.dumps({'result': 'pass', 'inputs': before,
        'source_sha256': hashlib.sha256(SOURCE).hexdigest(), 'assertions': len(checks)}, indent=2) + '\n')
    print('PASS class static selector unwind', len(checks), out)


if __name__ == '__main__':
    main()
