#!/usr/bin/env python3
"""Independent source-reached Generator input, unwind and admission checks."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker
import generator_effects_review as source
import typed_static_invoke_set_protocol as driver

ROOT = source.ROOT
CASES = {name: source.CASES[case] for name, case in [
    ('array-input', 'send-array-reference-copy'),
    ('finally-input', 'throw-finally-suspends'),
    ('initialization-input', 'throw-fresh-initialization-exception'),
]}
PREFIX = r'''
dec $effects_pending_head(ptask) : bool
def $effects_pending_head(FINALLY_RESUME porigin (n)) = true
def $effects_pending_head(ptask) = false -- otherwise
dec $effects_pending(ptask*) : ptask?
def $effects_pending(eps) = eps
def $effects_pending((FINALLY_RESUME porigin (n)) :: ptask*) = (FINALLY_RESUME porigin (n))
def $effects_pending(ptask :: ptask_tail*) = $effects_pending(ptask_tail*)
  -- if ~$effects_pending_head(ptask)
dec $effects_phase(pstate,nat) : bool
def $effects_phase(S,0) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.NAME = "send" /\ pgeneratorop.ADVANCE
  -- if pgeneratorop.ARGUMENTS = [PARRAY n]
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_RUNNING /\ pgenerator.FIRST
def $effects_phase(S,1) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.NAME = "send" /\ pgeneratorop.ADVANCE
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED /\ pgenerator.FIRST
def $effects_phase(S,2) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.NAME = "send" /\ ~pgeneratorop.ADVANCE
  -- if pgeneratorop.ARGUMENTS = [PARRAY n]
  -- if S.RESULT = KNOWN (PARRAY n)
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_RUNNING /\ ~pgenerator.FIRST
def $effects_phase(S,3) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.NAME = "send" /\ ~pgeneratorop.ADVANCE
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
  -- if pgenerator.VALUE = (PARRAY n)
def $effects_phase(S,4) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.NAME = "next"
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $effects_phase(S,10) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask*
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resumer*
  -- if pgeneratorop.NAME = "throw" /\ ~pgeneratorop.ADVANCE
  -- if pgeneratorop.ARGUMENTS = [POBJECT n]
def $effects_phase(S,11) = true
  -- if S.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.NAME = "throw" /\ ~pgeneratorop.ADVANCE
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
  -- if pgenerator.VALUE = (PINT 2)
  -- if pgenerator.FRAME = (pframe)
  -- if $effects_pending(pframe.TODO) =/= eps
def $effects_phase(S,12) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.NAME = "send" /\ ~pgeneratorop.ADVANCE
  -- if S.RESULT = KNOWN (PSTRING $ptascii("S"))
  -- if $effects_pending(S.TODO) =/= eps
def $effects_phase(S,13) = true
  -- if S.TODO = (THROW_SEARCH n) :: (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.NAME = "send" /\ ~pgeneratorop.ADVANCE
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $effects_phase(S,20) = true
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.NAME = "throw" /\ pgeneratorop.ADVANCE
  -- if pgeneratorop.ARGUMENTS = [POBJECT n]
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_RUNNING /\ pgenerator.FIRST
def $effects_phase(S,21) = true
  -- if S.TODO = (THROW_SEARCH n) :: (GENERATOR_RESUME pgeneratorop) :: ptask*
  -- if pgeneratorop.NAME = "throw" /\ pgeneratorop.ADVANCE
  -- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $effects_phase(S,n) = false -- otherwise
dec $effects_seek(pstate,nat,nat) : pstate
def $effects_seek(S,n_phase,n) = S -- if S.COMPILESTOP
def $effects_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $effects_seek(S,n_phase,n) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $effects_phase(S,n_phase)
def $effects_seek(S,n_phase,0) = S
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$effects_phase(S,n_phase)
def $effects_seek(S,n_phase,n) = $effects_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if ~S.COMPILESTOP
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$effects_phase(S,n_phase)
  -- if $(n > 0)
dec $effects_output(pevent) : bool
def $effects_output(OUTPUT ptbytes) = true
def $effects_output(pevent) = false -- otherwise
dec $effects_outputs(pevent*) : ptbytes
def $effects_outputs(eps) = eps
def $effects_outputs((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $effects_outputs(pevent*)
def $effects_outputs(pevent :: pevent_tail*) = $effects_outputs(pevent_tail*)
  -- if ~$effects_output(pevent)
'''


def seek(state, previous, phase):
    return [f'{state}_found = $effects_seek({previous},{phase},4096)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]', f'$effects_phase({state},{phase})']


def valid(state):
    return [f'$call_descriptors_valid({state})', f'$generator_state_valid({state})',
            f'$call_tasks_valid({state},{state}.TODO)', f'$call_frames_valid({state},{state}.FRAMES)',
            f'$call_current_valid({state})', f'$heap_valid($heap_graph({state}))']


def reject(checks, name, expression):
    state = 'S_bad_' + name
    checks += [state + ' = ' + expression, f'$heap_valid($heap_graph({state}))',
               f'~$call_descriptors_valid({state})']


def argument_negatives(checks, state, operation, frame, tail, frames):
    for label, mutation in [('missing', '.ARGUMENTS = eps'),
                            ('count', f'.ARGUMENTS = {operation}.ARGUMENTS ++ {operation}.ARGUMENTS'),
                            ('line', f'.LINE = $({operation}.LINE + 1)'),
                            ('method', '.NAME = "key"'),
                            ('advance', f'.ADVANCE = ~{operation}.ADVANCE')]:
        reject(checks, label, f'{state}[.FRAMES = {frame}[.TODO = (GENERATOR_RESUME {operation}[{mutation}]) :: {tail}] :: {frames}]')
    reject(checks, 'stranded', f'{state}[.FRAMES = {frame}[.TODO = DISCARD :: (GENERATOR_RESUME {operation}) :: {tail}] :: {frames}]')
    reject(checks, 'wrapped', f'{state}[.FRAMES = {frame}[.TODO = (AT {operation}.SITE (GENERATOR_RESUME {operation})) :: {tail}] :: {frames}]')


def assertions(checked, path, directory, name):
    initial = '$php_file_run(' + checked['fixture'] + ',0,' + driver.byte_expr(os.fsencode(path)) + ',' + driver.byte_expr(os.fsencode(directory)) + ')'
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP']
    if name == 'array-input':
        checks += seek('S_captured', 'S_initial', 0) + valid('S_captured')
        checks += r'''
S_captured.FRAMES = pframe_capture :: pframe_capture_tail*
pframe_capture.TODO = (GENERATOR_RESUME pgeneratorop_capture) :: ptask_capture*
pgeneratorop_capture.ARGUMENTS = [PARRAY n_array]
S_captured.OBJECTS[pgeneratorop_capture.OBJECT] = GENERATOR pgenerator_capture
pgenerator_capture.FRAME = eps
pgenerator_capture.VALUE = eps
pgenerator_capture.KEY = eps
pgenerator_capture.FIRST
S_captured.GLOBALTABLE = (psymboltable_global)
$trace_slot(S_captured,psymboltable_global.ENV,$ptascii("a")) = PARRAY n_array
S_captured.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]
S_captured.STORE[n_cell] = DEFINED (PINT 4)
$heap_owners($heap_graph(S_captured),HARRAY n_array) = 2
$generator_operation_trace(S_captured,pgeneratorop_capture) = [ptraceframe_capture]
ptraceframe_capture.FUNCTION = $ptascii("send")
ptraceframe_capture.ARGS = [(KINT 0, PARRAY n_array)]
'''.strip().splitlines()
        argument_negatives(checks, 'S_captured', 'pgeneratorop_capture', 'pframe_capture', 'ptask_capture*', 'pframe_capture_tail*')
        checks += seek('S_first', 'S_captured', 1) + valid('S_first')
        checks += r'''
S_first.TODO = (GENERATOR_RESUME pgeneratorop_first) :: ptask_first*
pgeneratorop_first.ARGUMENTS = [PARRAY n_array]
pgeneratorop_first.ADVANCE
S_first.OBJECTS[pgeneratorop_capture.OBJECT] = GENERATOR pgenerator_first
pgenerator_first.VALUE = (PINT 1)
pgenerator_first.KEY = (PINT 0)
pgenerator_first.FIRST
S_first.STORE[n_cell] = DEFINED (PINT 9)
$heap_owners($heap_graph(S_first),HARRAY n_array) = 2
'''.strip().splitlines()
        reject(checks, 'initial_completion', 'S_first[.TODO = (GENERATOR_RESUME pgeneratorop_first[.ADVANCE = false]) :: ptask_first*]')
        checks += seek('S_delivered', 'S_first', 2) + valid('S_delivered')
        checks += r'''
S_delivered.RESULT = KNOWN (PARRAY n_array)
S_delivered.FRAMES = pframe_delivered :: pframe_delivered_tail*
pframe_delivered.TODO = (GENERATOR_RESUME pgeneratorop_delivered) :: ptask_delivered*
pgeneratorop_delivered.ARGUMENTS = [PARRAY n_array]
~pgeneratorop_delivered.ADVANCE
S_delivered.OBJECTS[pgeneratorop_capture.OBJECT] = GENERATOR pgenerator_delivered
~pgenerator_delivered.FIRST
$heap_owners($heap_graph(S_delivered),HARRAY n_array) = 3
'''.strip().splitlines()
        reject(checks, 'replayed_initialization', '$generator_set(S_delivered,pgeneratorop_capture.OBJECT,pgenerator_delivered[.FIRST = true])')
        checks += seek('S_second', 'S_delivered', 3) + valid('S_second')
        checks += r'''
S_second.OBJECTS[pgeneratorop_capture.OBJECT] = GENERATOR pgenerator_second
pgenerator_second.VALUE = (PARRAY n_array)
pgenerator_second.KEY = (PINT 1)
pgenerator_second.FRAME = (pframe_second)
pframe_second.LOCALS = (psymboltable_second)
$trace_slot(S_second,psymboltable_second.ENV,$ptascii("x")) = PARRAY n_array
$heap_owners($heap_graph(S_second),HARRAY n_array) = 4
'''.strip().splitlines()
        checks += seek('S_closed', 'S_second', 4) + valid('S_closed')
        checks += r'''
S_closed.OBJECTS[pgeneratorop_capture.OBJECT] = GENERATOR pgenerator_closed
pgenerator_closed.FRAME = eps
pgenerator_closed.VALUE = (PARRAY n_array)
pgenerator_closed.RETURN = (PARRAY n_array)
$trace_slot(S_closed,S_closed.ENV,$ptascii("a")) = PARRAY n_separate
n_separate =/= n_array
S_closed.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]
S_closed.ARRAYS[n_separate].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell),ENTRY (KINT 1) (DIRECT (PINT 8))]
S_closed.STORE[n_cell] = DEFINED (PINT 6)
$heap_owners($heap_graph(S_closed),HARRAY n_array) = 3
'''.strip().splitlines()
        previous = 'S_closed'
    elif name == 'finally-input':
        checks += seek('S_injected', 'S_initial', 10) + valid('S_injected')
        checks += r'''
S_injected.TODO = (THROW_SEARCH n_input) :: ptask_injected*
S_injected.FRAMES = pframe_throw :: pframe_throw_tail*
pframe_throw.TODO = (GENERATOR_RESUME pgeneratorop_throw) :: ptask_throw*
pgeneratorop_throw.ARGUMENTS = [POBJECT n_input]
S_injected.OBJECTS[pgeneratorop_throw.OBJECT] = GENERATOR pgenerator_injected
~pgenerator_injected.FIRST
pgenerator_injected.VALUE = (PINT 1)
pgenerator_injected.KEY = (PINT 0)
S_injected.RESULT = KNOWN PNULL
S_injected.BASE = BASE_VALUE (KNOWN PNULL)
$throwable_member(S_injected,n_input)
'''.strip().splitlines()
        argument_negatives(checks, 'S_injected', 'pgeneratorop_throw', 'pframe_throw', 'ptask_throw*', 'pframe_throw_tail*')
        reject(checks, 'throw_type', 'S_injected[.FRAMES = pframe_throw[.TODO = (GENERATOR_RESUME pgeneratorop_throw[.ARGUMENTS = [PINT 1]]) :: ptask_throw*] :: pframe_throw_tail*]')
        checks += seek('S_pending', 'S_injected', 11) + valid('S_pending')
        checks += r'''
S_pending.OBJECTS[pgeneratorop_throw.OBJECT] = GENERATOR pgenerator_pending
pgenerator_pending.VALUE = (PINT 2)
pgenerator_pending.KEY = (PINT 1)
pgenerator_pending.FRAME = (pframe_pending)
$effects_pending(pframe_pending.TODO) = (FINALLY_RESUME porigin_finally (n_input))
$finally_phase_at(pframe_pending.TODO,FINALLY_RESUME porigin_finally (n_input),1)
$task_nodes(FINALLY_RESUME porigin_finally (n_input)) = [HOBJECT n_input]
$heap_owners($heap_graph(S_pending),HOBJECT n_input) = 3
'''.strip().splitlines()
        reject(checks, 'search_paused', 'S_pending[.TODO = (THROW_SEARCH n_input) :: S_pending.TODO]')
        checks += seek('S_sent', 'S_pending', 12) + valid('S_sent')
        checks += r'''
S_sent.RESULT = KNOWN (PSTRING $ptascii("S"))
S_sent.FRAMES = pframe_send :: pframe_send_tail*
pframe_send.TODO = (GENERATOR_RESUME pgeneratorop_send) :: ptask_send*
pgeneratorop_send.ARGUMENTS = [PSTRING $ptascii("S")]
pgeneratorop_send.OBJECT = pgeneratorop_throw.OBJECT
$effects_pending(S_sent.TODO) = (FINALLY_RESUME porigin_finally (n_input))
$throwable_previous_id(S_sent,n_input) = eps
$heap_owners($heap_graph(S_sent),HOBJECT n_input) = 2
'''.strip().splitlines()
        checks += seek('S_crossed', 'S_sent', 13) + valid('S_crossed')
        checks += r'''
S_crossed.TODO = (THROW_SEARCH n_input) :: (GENERATOR_RESUME pgeneratorop_send) :: ptask_crossed*
S_crossed.OBJECTS[pgeneratorop_throw.OBJECT] = GENERATOR pgenerator_closed
pgenerator_closed.FRAME = eps
pgenerator_closed.RETURN = eps
$throwable_previous_id(S_crossed,n_input) = eps
'''.strip().splitlines()
        reject(checks, 'double_search', 'S_crossed[.TODO = (THROW_SEARCH n_input) :: S_crossed.TODO]')
        reject(checks, 'saved_search', 'S_sent[.FRAMES = pframe_send[.TODO = (THROW_SEARCH n_input) :: pframe_send.TODO] :: pframe_send_tail*]')
        previous = 'S_crossed'
    else:
        checks += seek('S_initializing', 'S_initial', 20) + valid('S_initializing')
        checks += r'''
S_initializing.FRAMES = pframe_init :: pframe_init_tail*
pframe_init.TODO = (GENERATOR_RESUME pgeneratorop_init) :: ptask_init*
pgeneratorop_init.ARGUMENTS = [POBJECT n_input]
pgeneratorop_init.ADVANCE
S_initializing.OBJECTS[pgeneratorop_init.OBJECT] = GENERATOR pgenerator_initializing
pgenerator_initializing.FIRST
$throwable_previous_id(S_initializing,n_input) = eps
'''.strip().splitlines()
        argument_negatives(checks, 'S_initializing', 'pgeneratorop_init', 'pframe_init', 'ptask_init*', 'pframe_init_tail*')
        reject(checks, 'init_throw_type', 'S_initializing[.FRAMES = pframe_init[.TODO = (GENERATOR_RESUME pgeneratorop_init[.ARGUMENTS = [PINT 1]]) :: ptask_init*] :: pframe_init_tail*]')
        checks += seek('S_failed', 'S_initializing', 21) + valid('S_failed')
        checks += r'''
S_failed.TODO = (THROW_SEARCH n_initial) :: (GENERATOR_RESUME pgeneratorop_init) :: ptask_failed*
n_initial =/= n_input
S_failed.OBJECTS[pgeneratorop_init.OBJECT] = GENERATOR pgenerator_closed
pgenerator_closed.FRAME = eps
pgenerator_closed.RETURN = eps
pgenerator_closed.VALUE = eps
pgenerator_closed.KEY = eps
pgenerator_closed.FIRST
$throwable_previous_id(S_failed,n_input) = eps
$throwable_marker(GENERATOR_RESUME pgeneratorop_init)
'''.strip().splitlines()
        reject(checks, 'double_search', 'S_failed[.TODO = (THROW_SEARCH n_initial) :: S_failed.TODO]')
        reject(checks, 'wrong_stage', 'S_failed[.TODO = (THROW_SEARCH n_initial) :: (GENERATOR_RESUME pgeneratorop_init[.ADVANCE = false]) :: ptask_failed*]')
        reject(checks, 'search_return', '$generator_set(S_failed,pgeneratorop_init.OBJECT,pgenerator_closed[.RETURN = (PINT 1)])')
        checks += ['S_chained_stop = $drive_steps(S_failed,1)', 'S_chained_stop.COMPLETION = BUDGET',
                   'S_chained = S_chained_stop[.COMPLETION = NORMAL]',
                   'S_chained.TODO = (THROW_SEARCH n_input) :: ptask_failed*',
                   '$throwable_previous_id(S_chained,n_input) = (n_initial)',
                   '$throwable_chain_valid(S_chained,n_input)'] + valid('S_chained')
        previous = 'S_chained'
    checks += [f'S_stopped = $drive_steps({previous},0)', 'S_stopped.COMPLETION = BUDGET',
               f'S_stopped = {previous}[.COMPLETION = BUDGET]',
               'S_resumed = $drive(S_stopped[.COMPLETION = NORMAL],4096)',
               f'S_direct = $drive({previous},4096)', 'S_resumed = S_direct',
               'S_resumed.COMPLETION = NORMAL', 'S_resumed.TODO = eps',
               'S_resumed.FRAMES = eps', 'S_resumed.ITERATORS = eps',
               '$effects_outputs(S_resumed.EVENTS) = ' + driver.byte_expr(CASES[name][1])]
    checks += valid('S_resumed')
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['fixtures', 'prepare', 'check'], default='check')
    parser.add_argument('--select', help='Comma-separated exact case IDs')
    args = parser.parse_args()
    names = args.select.split(',') if args.select else list(CASES)
    assert names and len(names) == len(set(names)) and all(n in CASES for n in names)
    out = Path(tempfile.mkdtemp(prefix='generator-effects-protocol-', dir=ROOT / '.tools'))
    report = {'result': 'fail', 'mode': args.mode, 'records': [], 'assertions': 0,
              'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'profile': driver.types.PROFILE, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}}
    print(out, flush=True)
    try:
        (out / 'candidate.diff').write_bytes(subprocess.check_output(['git', 'diff', 'HEAD'], cwd=ROOT))
        (out / 'case-fixture.py').write_bytes(Path(__file__).read_bytes())
        report['tools'] = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                           for path in [Path(__file__), ROOT / '.tools/php/bin/php', ROOT / '_build/default/adapter/main.exe']}
        if args.mode != 'fixtures':
            runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
            report['tools'][str(runner.relative_to(ROOT))] = hashlib.sha256(runner.read_bytes()).hexdigest()
        identity = source.run([str(driver.types.PHP), '-n', *driver.types.FLAGS, '-r',
                               'echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,get_loaded_extensions(),ini_get_all(null,false)]);'], out / 'runtime', 10)
        assert identity.returncode == 0 and not identity.stderr
        report['runtime'] = json.loads(identity.stdout)
        assert report['runtime'][:4] == ['8.5.10', 'cli', 8, False]
        assert all(report['runtime'][5][key] == value for key, value in driver.types.PROFILE.items())
        for name in names:
            directory = out / name
            directory.mkdir()
            path = directory / 'source.php'
            path.write_bytes(CASES[name][0])
            row = {'id': name, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'evaluated': args.mode == 'check'}
            report['records'].append(row)
            native = source.run([str(driver.types.PHP), '-n', *driver.types.FLAGS, str(path)], directory / 'native', 10)
            row.update(native_exit=native.returncode, native_stdout=driver.b64(native.stdout), native_stderr=driver.b64(native.stderr))
            assert native.returncode == 0 and native.stdout == CASES[name][1] and not native.stderr
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
