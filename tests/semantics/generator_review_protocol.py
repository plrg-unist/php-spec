#!/usr/bin/env python3
"""Independent source-reached Generator frame, owner and resume checks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker
import generator_review as source
import typed_static_invoke_set_protocol as driver

ROOT = source.ROOT
CASES = {
    "carrier": (b'<?php\n$cell=7;function seq(&$r){$a=[&$r];yield $a;return $a;}$g=seq($cell);$g->current();$cell=9;$g->next();echo $g->getReturn()[0];unset($g);echo "Z";', b'9Z'),
    "closure": (b'<?php\n$cell=7;$f=function(&$r){$a=[&$r];yield $a;return $a;};$g=$f($cell);unset($f);$g->current();$cell=9;$g->next();echo $g->getReturn()[0];unset($g);echo "Z";', b'9Z'),
    "nested": (b'<?php\nfunction inner(){yield [1];yield [2];}function outer(){foreach(inner() as $v){yield $v;}}foreach(outer() as $v){echo $v[0];}echo "Z";', b'12Z'),
    "abrupt": (b'<?php\nfunction seq(){try{yield [7];throw new Exception("x");}finally{echo "F";}}$g=seq();echo $g->current()[0];try{$g->next();}catch(Exception $e){echo "E";}echo $g->valid()?"T":"N";unset($g);echo "Z";', b'7FENZ'),
}
PREFIX = r'''
dec $generator_review_phase(pstate,nat) : bool
def $generator_review_phase(S,0) = true
  -- if S.TODO = (GENERATOR_ARGS pgeneratorop eps eps) :: ptask*
  -- if pgeneratorop.NAME = "current"
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_FRESH
def $generator_review_phase(S,1) = true
  -- if $generator_active(S)
def $generator_review_phase(S,2) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
def $generator_review_phase(S,3) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $generator_review_phase(S,4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe_inner :: pframe_outer :: pframe*
  -- if pframe_inner.TODO = (GENERATOR_RESUME pgeneratorop_inner) :: ptask_inner*
  -- if pframe_outer.TODO = (GENERATOR_RESUME pgeneratorop_outer) :: ptask_outer*
  -- if pgeneratorop_inner.OBJECT =/= pgeneratorop_outer.OBJECT
  -- if S.OBJECTS[pgeneratorop_inner.OBJECT] = GENERATOR pgenerator_inner
  -- if S.OBJECTS[pgeneratorop_outer.OBJECT] = GENERATOR pgenerator_outer
  -- if pgenerator_inner.PHASE = GENERATOR_RUNNING
  -- if pgenerator_outer.PHASE = GENERATOR_RUNNING
def $generator_review_phase(S,n) = false -- otherwise
dec $generator_review_seek(pstate,nat,nat) : pstate
def $generator_review_seek(S,n_phase,n) = S -- if S.COMPILESTOP
def $generator_review_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $generator_review_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $generator_review_phase(S,n_phase)
def $generator_review_seek(S,n_phase,0) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$generator_review_phase(S,n_phase)
def $generator_review_seek(S,n_phase,n) = $generator_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$generator_review_phase(S,n_phase)
  -- if $(n > 0)
dec $generator_review_output(pevent) : bool
def $generator_review_output(OUTPUT ptbytes) = true
def $generator_review_output(pevent) = false -- otherwise
dec $generator_review_outputs(pevent*) : ptbytes
def $generator_review_outputs(eps) = eps
def $generator_review_outputs((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $generator_review_outputs(pevent*)
def $generator_review_outputs(pevent :: pevent*) = $generator_review_outputs(pevent*)
  -- if ~$generator_review_output(pevent)
'''


def seek(state, previous, phase):
    return [f'{state}_found = $generator_review_seek({previous},{phase},4096)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$generator_review_phase({state},{phase})']


def valid(state, full=False):
    checks = [f'$generator_state_valid({state})',
              f'$call_tasks_valid({state},{state}.TODO)',
              f'$call_frames_valid({state},{state}.FRAMES)',
              f'$call_current_valid({state})', f'$heap_valid($heap_graph({state}))']
    return ([f'$call_descriptors_valid({state})'] if full else []) + checks


def rejected(checks, name, expression):
    state = 'S_bad_' + name
    checks += [state + ' = ' + expression, f'$heap_valid($heap_graph({state}))',
               f'~$generator_state_valid({state})']


def assertions(checked, path, directory, name):
    initial = '$php_file_run(' + checked['fixture'] + ',0,' + driver.byte_expr(os.fsencode(path)) + ',' + driver.byte_expr(os.fsencode(directory)) + ')'
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    if name in ('carrier', 'closure'):
        checks += seek('S_fresh', 'S_initial', 0) + valid('S_fresh', True)
        checks += r'''
S_fresh.TODO = (GENERATOR_ARGS pgeneratorop eps eps) :: ptask_fresh*
S_fresh.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_fresh
pgenerator_fresh.FRAME = (pframe_fresh)
pframe_fresh.CONTEXT = (pcallcontext_fresh)
pframe_fresh.LOCALS = (psymboltable_fresh)
pgenerator_fresh.VALUE = eps
pgenerator_fresh.KEY = eps
pgenerator_fresh.RETURN = eps
pcallcontext_fresh.FUNCTION = pgenerator_fresh.FUNCTION
$trace_slot(S_fresh,S_fresh.ENV,$ptascii("g")) = POBJECT pgeneratorop.OBJECT
'''.strip().splitlines()
        if name == 'closure':
            checks += ['pgenerator_fresh.CLOSURE = (n_closure)',
                       'pcallcontext_fresh.INSTANCE = (n_closure)',
                       'n_closure =/= pgeneratorop.OBJECT',
                       '(HOBJECT n_closure) <- S_fresh.ALLOCATIONS']
        rejected(checks, 'fresh_no_frame', '$generator_set(S_fresh,pgeneratorop.OBJECT,pgenerator_fresh[.FRAME = eps])')
        rejected(checks, 'fresh_cached_value', '$generator_set(S_fresh,pgeneratorop.OBJECT,pgenerator_fresh[.VALUE = (PINT 1)])')
        rejected(checks, 'fresh_cv', '$generator_set(S_fresh,pgeneratorop.OBJECT,pgenerator_fresh[.FRAME = (pframe_fresh[.LOCALS = (psymboltable_fresh[.CVS = eps])])])')
        checks += seek('S_running', 'S_fresh', 1) + valid('S_running')
        checks += r'''
S_running.CURRENT = (pcallcontext_running)
S_running.FRAMES = pframe_resumer :: pframe_resumer_tail*
pframe_resumer.TODO = (GENERATOR_RESUME pgeneratorop_running) :: ptask_resumer*
pgeneratorop_running.OBJECT = pgeneratorop.OBJECT
S_running.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_running
pgenerator_running.PHASE = GENERATOR_RUNNING
pgenerator_running.FRAME = eps
pcallcontext_running = pcallcontext_fresh
$heap_owners($heap_graph(S_running),HOBJECT pgeneratorop.OBJECT) = 2
'''.strip().splitlines()
        rejected(checks, 'detached_owner', 'S_running[.FRAMES = pframe_resumer[.TODO = ptask_resumer*] :: pframe_resumer_tail*]')
        rejected(checks, 'duplicate_owner', 'S_running[.FRAMES = pframe_resumer[.TODO = (GENERATOR_RESUME pgeneratorop_running) :: (GENERATOR_RESUME pgeneratorop_running) :: ptask_resumer*] :: pframe_resumer_tail*]')
        rejected(checks, 'wrapped_owner', 'S_running[.FRAMES = pframe_resumer[.TODO = (AT pgeneratorop_running.SITE (GENERATOR_RESUME pgeneratorop_running)) :: ptask_resumer*] :: pframe_resumer_tail*]')
        rejected(checks, 'stranded_owner', 'S_running[.FRAMES = pframe_resumer[.TODO = DISCARD :: (GENERATOR_RESUME pgeneratorop_running) :: ptask_resumer*] :: pframe_resumer_tail*]')
        rejected(checks, 'top_owner', 'S_running[.TODO = (GENERATOR_RESUME pgeneratorop_running) :: S_running.TODO][.FRAMES = pframe_resumer[.TODO = ptask_resumer*] :: pframe_resumer_tail*]')
        rejected(checks, 'owner_line', 'S_running[.FRAMES = pframe_resumer[.TODO = (GENERATOR_RESUME pgeneratorop_running[.LINE = $(pgeneratorop_running.LINE + 1)]) :: ptask_resumer*] :: pframe_resumer_tail*]')
        rejected(checks, 'owner_method', 'S_running[.FRAMES = pframe_resumer[.TODO = (GENERATOR_RESUME pgeneratorop_running[.NAME = "key"]) :: ptask_resumer*] :: pframe_resumer_tail*]')
        rejected(checks, 'owner_advance', 'S_running[.FRAMES = pframe_resumer[.TODO = (GENERATOR_RESUME pgeneratorop_running[.ADVANCE = true]) :: ptask_resumer*] :: pframe_resumer_tail*]')
        rejected(checks, 'running_return', '$generator_set(S_running,pgeneratorop.OBJECT,pgenerator_running[.RETURN = (PINT 1)])')
        checks += seek('S_paused', 'S_running', 2) + valid('S_paused')
        checks += r'''
S_paused.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_paused
pgenerator_paused.FRAME = (pframe_paused)
pgenerator_paused.VALUE = (PARRAY n_array)
pgenerator_paused.KEY = (PINT 0)
pgenerator_paused.FIRST
$heap_owners($heap_graph(S_paused),HARRAY n_array) = 2
S_paused.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]
(HCELL n_cell) <- S_paused.ALLOCATIONS
pframe_paused.TODO = ptask_paused :: ptask_paused_tail*
'''.strip().splitlines()
        rejected(checks, 'paused_no_frame', '$generator_set(S_paused,pgeneratorop.OBJECT,pgenerator_paused[.FRAME = eps])')
        rejected(checks, 'paused_return', '$generator_set(S_paused,pgeneratorop.OBJECT,pgenerator_paused[.RETURN = (PINT 1)])')
        rejected(checks, 'paused_wrapped_owner', '$generator_set(S_paused,pgeneratorop.OBJECT,pgenerator_paused[.FRAME = (pframe_paused[.TODO = (AT pgeneratorop_running.SITE (GENERATOR_RESUME pgeneratorop_running)) :: pframe_paused.TODO])])')
        checks += seek('S_closed', 'S_paused', 3) + valid('S_closed')
        checks += r'''
S_closed.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_closed
pgenerator_closed.FRAME = eps
pgenerator_closed.VALUE = (PARRAY n_array)
pgenerator_closed.RETURN = (PARRAY n_array)
$heap_owners($heap_graph(S_closed),HARRAY n_array) = 2
S_closed.STORE[n_cell] = DEFINED (PINT 9)
'''.strip().splitlines()
        rejected(checks, 'closed_cache_pair', '$generator_set(S_closed,pgeneratorop.OBJECT,pgenerator_closed[.KEY = eps])')
        if name == 'closure':
            checks += ['pgenerator_closed.CLOSURE = (n_closure)',
                       '$heap_owners($heap_graph(S_closed),HOBJECT n_closure) = 1']
            rejected(checks, 'closed_closure_target', '$generator_set(S_closed,pgeneratorop.OBJECT,pgenerator_closed[.CLOSURE = (pgeneratorop.OBJECT)])')
        previous = 'S_closed'
    elif name == 'nested':
        checks += seek('S_nested', 'S_initial', 4) + valid('S_nested', True)
        checks += r'''
S_nested.FRAMES = pframe_inner :: pframe_outer :: pframe_tail*
pframe_inner.TODO = (GENERATOR_RESUME pgeneratorop_inner) :: ptask_inner*
pframe_outer.TODO = (GENERATOR_RESUME pgeneratorop_outer) :: ptask_outer*
n_inner = pgeneratorop_inner.OBJECT
n_outer = pgeneratorop_outer.OBJECT
n_inner =/= n_outer
S_nested.OBJECTS[n_inner] = GENERATOR pgenerator_inner
S_nested.OBJECTS[n_outer] = GENERATOR pgenerator_outer
pgenerator_inner.FRAME = eps
pgenerator_outer.FRAME = eps
'''.strip().splitlines()
        rejected(checks, 'nested_alias', 'S_nested[.FRAMES = pframe_inner[.TODO = (GENERATOR_RESUME pgeneratorop_inner[.OBJECT = n_outer]) :: ptask_inner*] :: pframe_outer :: pframe_tail*]')
        rejected(checks, 'nested_detached', 'S_nested[.FRAMES = pframe_inner :: pframe_outer[.TODO = ptask_outer*] :: pframe_tail*]')
        previous = 'S_nested'
    else:
        checks += seek('S_paused', 'S_initial', 2) + valid('S_paused', True)
        checks += r'''
S_paused.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
S_paused.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator_paused
pgenerator_paused.VALUE = (PARRAY n_array)
pgenerator_paused.FRAME = (pframe_paused)
$generator_finalizer_tasks(S_paused,pframe_paused.TODO)
'''.strip().splitlines()
        previous = 'S_paused'
    checks += [f'S_stopped = $drive_steps({previous},0)', 'S_stopped.COMPLETION = BUDGET',
               f'S_stopped = {previous}[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
               f'S_direct = $drive({previous},4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = NORMAL', 'S_resumed.TODO = eps',
               'S_resumed.FRAMES = eps', 'S_resumed.ITERATORS = eps',
               '$generator_review_outputs(S_resumed.EVENTS) = ' + driver.byte_expr(CASES[name][1])]
    checks += valid('S_resumed')
    if name in ('carrier', 'closure'):
        checks += ['~((HOBJECT pgeneratorop.OBJECT) <- S_resumed.ALLOCATIONS)',
                   '~((HARRAY n_array) <- S_resumed.ALLOCATIONS)',
                   '(HCELL n_cell) <- S_resumed.ALLOCATIONS']
        if name == 'closure':
            checks += ['~((HOBJECT n_closure) <- S_resumed.ALLOCATIONS)']
    if name == 'abrupt':
        checks += ['~((HOBJECT pgeneratorop.OBJECT) <- S_resumed.ALLOCATIONS)',
                   '~((HARRAY n_array) <- S_resumed.ALLOCATIONS)']
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['native', 'fixtures', 'prepare', 'check'], default='check')
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    args = parser.parse_args()
    names = args.select.split(',') if args.select else list(CASES)
    assert names and len(names) == len(set(names)) and all(n in CASES for n in names)
    out = Path(tempfile.mkdtemp(prefix='generator-review-protocol-', dir=ROOT / '.tools'))
    report = {'result': 'fail', 'mode': args.mode, 'records': [], 'assertions': 0,
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'profile': driver.types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}}
    print(out, flush=True)
    try:
        (out / 'candidate.diff').write_bytes(subprocess.check_output(['git', 'diff', 'HEAD'], cwd=ROOT))
        candidate = ROOT / 'spec/semantics/280-generators.watsup'
        if candidate.exists():
            (out / 'candidate-generator.watsup').write_bytes(candidate.read_bytes())
        report['tools'] = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                           for path in [Path(__file__), ROOT / '.tools/php/bin/php']}
        if args.mode != 'native':
            for path in [ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / '_build/default/adapter/main.exe']:
                report['tools'][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        identity = source.run([str(driver.types.PHP), '-n', *driver.types.FLAGS, '-r',
                               'echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get_all(null,false)]);'], out / 'runtime', 10)
        assert identity.returncode == 0 and not identity.stderr
        report['runtime'] = json.loads(identity.stdout)
        assert report['runtime'][:4] == ['8.5.10', 'cli', 8, False]
        assert all(report['runtime'][4][key] == value for key, value in driver.types.PROFILE.items())
        for name in names:
            directory = out / name
            directory.mkdir()
            path = directory / 'source.php'
            path.write_bytes(CASES[name][0])
            row = {'id': name, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'evaluated': args.mode == 'check'}
            report['records'].append(row)
            native = source.run([str(driver.types.PHP), '-n', *driver.types.FLAGS, str(path)], directory / 'native', 10)
            row['native_exit'] = native.returncode
            assert native.returncode == 0 and native.stdout == CASES[name][1] and not native.stderr
            if args.mode != 'native':
                frontend = Worker([str(driver.types.PHP), '-n', *driver.types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
                try:
                    parsed = frontend.request({'op': 'parse', 'source': driver.b64(path.read_bytes())})
                    assert parsed['accepted']
                    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
                    try:
                        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                    finally:
                        adapter.close()
                finally:
                    frontend.close()
                checks = assertions(checked, path, directory, name)
                (directory / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
                fixture = directory / 'protocol.watsup'
                fixture.write_text(PREFIX + '\ndec $body() : bool\ndef $body() = true\n' +
                                   ''.join('  -- if ' + check + '\n' for check in checks) +
                                   '\ndec $main() : bool\ndef $main() = ' + ('true' if args.mode == 'prepare' else '$body()') + '\n')
                row['assertions'] = len(checks)
                if args.mode != 'fixtures':
                    driver.numeric(fixture, directory)
                report['assertions'] += len(checks) if args.mode == 'check' else 0
            row['passed'] = True
            print(name, args.mode, 'pass', flush=True)
        report['result'] = 'pass'
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['result'], flush=True)


if __name__ == '__main__':
    main()
