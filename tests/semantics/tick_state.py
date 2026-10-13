#!/usr/bin/env python3
"""Source-reached tick counters, live registry, captures and abrupt cleanup."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker
import tick_sources as sources

ROOT = sources.ROOT
CASES = {
    'counter': sources.CASES['frequency2'],
    'live-append': sources.CASES['append-during-dispatch'],
    'captured-array': (b'<?php function make($v){return [$v];}function t($v){echo $v[0];}$x=make(1);register_tick_function("t",$x);$x[0]=2;declare(ticks=1){echo "A";}unregister_tick_function("t");echo "Z";', b'A1Z'),
    'throw-cleanup': (b'<?php $e=new Exception("E");function a(){global $e;echo "A";throw $e;}function b(){echo "B";}register_tick_function("a");register_tick_function("b");try{declare(ticks=1){echo "X";}}catch(Exception $c){echo $c===$e?"C":"bad";}unregister_tick_function("a");unregister_tick_function("b");echo "Z";', b'XACZ'),
    'returned-object': (b'<?php class C{function __destruct(){try{unregister_tick_function("t");echo "U";}catch(Error $e){echo "H";}}}function t(){return new C;}register_tick_function("t");declare(ticks=1){echo "A";}', b'AH'),
    'unregister-pending': (b'<?php $e=new Exception("E");class C{function __destruct(){global $e;echo "D";throw $e;}}function t($x){echo "A";try{unregister_tick_function("t");}catch(Throwable $c){global $e;echo $c===$e?"same":"bad";echo $c->getPrevious() instanceof Error?"P":"N";}}register_tick_function("t","A");register_tick_function("t",new C);declare(ticks=1){echo "X";}echo "Z";', b'XADsamePZ'),
    'unregister-target': (b'<?php class A{function m($v){}function __destruct(){echo "A";}}class B{function __destruct(){global $r;echo "1";$r=null;echo "2";}}$x=new A;$r=&$x;$cb=[&$r,"m"];register_tick_function($cb,new B);unset($x);unregister_tick_function($cb);echo "Z";', b'12AZ'),
}
PREFIX = r'''
dec $tick_test_output(pevent*) : preqbytes
def $tick_test_output(eps) = eps
def $tick_test_output((OUTPUT n*) :: pevent*) = n* ++ $tick_test_output(pevent*)
dec $tick_test_is_output(pevent) : bool
def $tick_test_is_output(OUTPUT n*) = true
def $tick_test_is_output(pevent) = false -- otherwise
def $tick_test_output(pevent :: pevent_tail*) = $tick_test_output(pevent_tail*) -- if ~$tick_test_is_output(pevent)
dec $tick_test_only_output(pevent*) : bool
def $tick_test_only_output(eps) = true
def $tick_test_only_output(pevent :: pevent_tail*) = ($tick_test_is_output(pevent) /\ $tick_test_only_output(pevent_tail*))
dec $tick_test_hold_tasks(ptask*) : (pshutdownentry, ptickentry)?
dec $tick_test_hold_task(ptask) : bool
def $tick_test_hold_task(TICK_UNREGISTER_RELEASE pshutdownentry ptickentry) = true
def $tick_test_hold_task(ptask) = false -- otherwise
def $tick_test_hold_tasks(eps) = eps
def $tick_test_hold_tasks((TICK_UNREGISTER_RELEASE pshutdownentry ptickentry) :: ptask_tail*) = ((pshutdownentry, ptickentry))
def $tick_test_hold_tasks(ptask :: ptask_tail*) = $tick_test_hold_tasks(ptask_tail*) -- if ~$tick_test_hold_task(ptask)
dec $tick_test_hold_frames(pframe*) : (pshutdownentry, ptickentry)?
def $tick_test_hold_frames(pframe :: pframe_tail*) = ((pshutdownentry, ptickentry))
  -- if $tick_test_hold_tasks(pframe.TODO) = ((pshutdownentry, ptickentry))
def $tick_test_hold_frames(pframe :: pframe_tail*) = $tick_test_hold_frames(pframe_tail*)
  -- if $tick_test_hold_tasks(pframe.TODO) = eps
def $tick_test_hold_frames(eps) = eps
dec $tick_test_phase(pstate, nat) : bool
def $tick_test_phase(S, 0) = true
  -- if S.TODO = (TICK porigin ptickmarker) :: ptask_tail*
  -- if ptickmarker.FREQUENCY = 2 /\ S.TICKCOUNT = 1
  -- if $tick_test_output(S.EVENTS) = ([65])
def $tick_test_phase(S, 1) = true
  -- if S.TODO = (TICK_RESULT ptickdispatch) :: ptask_tail*
  -- if ptickdispatch.ENTRY = (0) /\ S.TICKSEQ = 2
  -- if $tick_test_output(S.EVENTS) = ([88,65])
def $tick_test_phase(S, 2) = true
  -- if S.TODO = (TICK_NEXT ptickdispatch) :: ptask_tail*
  -- if S.TICKSEQ = 1 /\ ptickdispatch.ENTRY = eps
  -- if $tick_test_output(S.EVENTS) = ([65])
def $tick_test_phase(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: ptask_tail*
  -- if $tick_is_calling(S, 0)
  -- if $tick_test_output(S.EVENTS) = ([88,65])
def $tick_test_phase(S, 4) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = TICK_RESULT ptickdispatch
  -- if $tick_test_output(S.EVENTS) = ([65])
def $tick_test_phase(S, 5) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = CONFIG_INVOKE pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_UNREGISTER_TICK /\ pdestructionoperation.PENDING =/= eps
  -- if $tick_test_output(S.EVENTS) = ([88,65])
def $tick_test_phase(S, 6) = true
  -- if S.TODO = (TICK_RESULT ptickdispatch) :: ptask_tail*
  -- if $tick_test_output(S.EVENTS) = ([88,65,68,115,97,109,101,80])
def $tick_test_phase(S, 7) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (TICK_UNREGISTER_RELEASE pshutdownentry ptickentry) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = CONFIG_INVOKE pshutdownentry.CALL
  -- if S.TICKENTRIES = eps /\ $tick_test_output(S.EVENTS) = eps
def $tick_test_phase(S, 8) = true
  -- if S.TODO = (AT porigin (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES "Mg==") metadata_string])) metadata_echo))) :: ptask_tail*
  -- if $tick_test_hold_frames(S.FRAMES) = ((pshutdownentry, ptickentry))
  -- if S.GLOBALTABLE = (psymboltable)
  -- if $lookup(psymboltable.ENV, [114]) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED PNULL
  -- if S.TICKENTRIES = eps /\ $tick_test_output(S.EVENTS) = ([49])
def $tick_test_phase(S, n) = false -- otherwise
dec $tick_test_seek(pstate, nat, nat) : pstate
def $tick_test_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $tick_test_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $tick_test_phase(S, n_phase)
def $tick_test_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$tick_test_phase(S, n_phase)
def $tick_test_seek(S, n_phase, n) = $tick_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$tick_test_phase(S, n_phase) /\ $(n > 0)
'''


def bytes_expr(value):
    return '$base64(' + json.dumps(sources.base64.b64encode(value).decode()) + ')'


def valid(state):
    return ['$call_descriptors_valid(' + state + ')',
            '$heap_valid($heap_graph(' + state + '))', '$tick_state_valid(' + state + ')']


def assertions(name, fixture, directory, path):
    phase = 7 if name == 'unregister-target' else list(CASES).index(name)
    initial = '$php_file_run(' + fixture + ', 0, ' + bytes_expr(os.fsencode(path)) + ', ' + bytes_expr(os.fsencode(directory)) + ')'
    checks = ['S_initial = ' + initial, 'S_initial.COMPLETION = BUDGET',
              'S_initial.TICKCOUNT = 0 /\\ S_initial.TICKSEQ = 0 /\\ S_initial.TICKENTRIES = eps',
              *valid('S_initial'),
              'S_found = $tick_test_seek(S_initial, ' + str(phase) + ', 1024)',
              'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
              'S = S_found[.COMPLETION = NORMAL]', '$tick_test_phase(S, ' + str(phase) + ')', *valid('S'),
              'S_budget = $drive_steps(S, 0)', 'S_budget.COMPLETION = BUDGET',
              'S_budget.TODO = S.TODO /\\ S_budget.TICKCOUNT = S.TICKCOUNT',
              'S_budget.TICKENTRIES = S.TICKENTRIES /\\ S_budget.EVENTS = S.EVENTS', *valid('S_budget')]
    if name == 'counter':
        checks += ['S.TODO = (TICK porigin ptickmarker) :: ptask_tail*',
                   '~$call_task_valid(S, TICK porigin ptickmarker[.FREQUENCY = 3])',
                   '~$call_task_valid(S, TICK porigin ptickmarker[.LINE = $(ptickmarker.LINE + 1)])',
                   '~$call_task_valid(S, TICK (PORIGIN 999 eps) ptickmarker)',
                   '~$call_task_valid(S, TICK porigin ptickmarker[.PATH = ptickmarker.PATH ++ [PCINDEX 999]])',
                   '~$tick_state_valid(S[.TICKCOUNT = 4294967296])',
                   '~$call_descriptors_valid(S[.TODO = [TICK porigin ptickmarker, TICK porigin ptickmarker] ++ ptask_tail*])',
                   'S_dispatched = $drive_steps(S, 1)',
                   'S_dispatched.TICKCOUNT = 0',
                   'S_dispatched.TODO = (TICK_NEXT ptickdispatch) :: ptask_tail*',
                   'ptickdispatch.SITE = porigin /\\ ptickdispatch.MARKER = ptickmarker',
                   'ptickdispatch.CURSOR = 0 /\\ ptickdispatch.ENTRY = eps /\\ ptickdispatch.SENT = eps', *valid('S_dispatched'),
                   'S_wrapped = $drive_steps(S[.TICKCOUNT = 4294967295], 1)',
                   'S_wrapped.TICKCOUNT = 0 /\\ S_wrapped.TODO = ptask_tail*', *valid('S_wrapped')]
    elif name == 'live-append':
        checks += ['S.TODO = (TICK_RESULT ptickdispatch) :: ptask_tail*',
                   'S.TICKENTRIES = [ptickentry_first, ptickentry_second]',
                   'ptickentry_first.ID = 0 /\\ ptickentry_second.ID = 1',
                   '$tick_is_calling(S, 0) /\\ ~$tick_is_calling(S, 1) /\\ $tick_running(S)',
                   '~$tick_entries_valid(S, [ptickentry_second, ptickentry_first], 0)',
                   '~$tick_entry_valid(S, ptickentry_second[.ID = S.TICKSEQ])',
                   'S_next = $drive_steps(S, 1)',
                   'S_next.TODO = (TICK_NEXT ptickdispatch_next) :: ptask_tail*',
                   'ptickdispatch_next.CURSOR = 1 /\\ ptickdispatch_next.ENTRY = eps',
                   '~$tick_running(S_next)', *valid('S_next'),
                   'S_selected = $drive_steps(S_next[.COMPLETION = NORMAL], 1)',
                   'S_selected.TODO = (TICK_SEND ptickdispatch_selected 0) :: ptask_tail*',
                   'ptickdispatch_selected.CURSOR = 1 /\\ ptickdispatch_selected.ENTRY = (1)',
                   '~$tick_dispatch_valid(S_selected, ptickdispatch_selected[.CURSOR = 0])',
                   '~$tick_dispatch_valid(S_selected, ptickdispatch_selected[.ENTRY = (99)])',
                   '~$tick_dispatch_valid(S_selected, ptickdispatch_selected[.SENT = [KNOWN (PINT 7)]])', *valid('S_selected')]
    elif name == 'captured-array':
        checks += ['S.TICKENTRIES = [ptickentry]', 'ptickentry.ENTRY.ARGS = [PARRAY n_saved]',
                   '$lookup(S.ENV, [120]) = (n_cell)', 'S.STORE[n_cell] = DEFINED (PARRAY n_live)',
                   'n_saved =/= n_live',
                   '$entry_lookup(S.ARRAYS[n_saved].ITEMS, KINT 0) = (DIRECT (PINT 1))',
                   '$entry_lookup(S.ARRAYS[n_live].ITEMS, KINT 0) = (DIRECT (PINT 2))',
                   '(HARRAY n_saved) <- $tick_roots(S.TICKENTRIES)',
                   '$heap_owners($heap_graph(S), HARRAY n_saved) = 1',
                   '$heap_owners($heap_graph(S[.TICKENTRIES = eps]), HARRAY n_saved) = 0',
                   '~$tick_entry_valid(S, ptickentry[.ENTRY = ptickentry.ENTRY[.ARGS = [PINT 1]]])']
    elif name == 'throw-cleanup':
        checks += ['S.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
                   '$lookup(S.ENV, [101]) = (n_cell)', 'S.STORE[n_cell] = DEFINED (POBJECT n_exception)',
                   '$throwable_live(S, n_exception)', '$tick_running(S) /\\ $tick_is_calling(S, 0)',
                   'S_done = $drive_steps(S, 2048)',
                   '$lookup(S_done.ENV, [99]) = (n_catch)',
                   'S_done.STORE[n_catch] = DEFINED (POBJECT n_exception)',
                   'S_done.TICKENTRIES = eps']
    elif name == 'returned-object':
        checks += ['S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
                   'S.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
                   'pdestructionoperation.SOURCE = TICK_RESULT ptickdispatch',
                   'S.CURRENT = eps /\\ S.FRAMES = eps',
                   '~$tick_running_tasks(S.TODO) /\\ ~$tick_running_frames(S.FRAMES)',
                   '$tick_running(S) /\\ $tick_is_calling(S, 0) /\\ $fiber_blocked(S)',
                   'S_budget.DESTRUCTION.OPERATIONS = S.DESTRUCTION.OPERATIONS /\\ $tick_running(S_budget)',
                   '$destructor_operation_live(S, pdestructionoperation)',
                   '~$eager_operation_source_guard(S, pdestructionoperation[.SOURCE = TICK_RESULT ptickdispatch[.ENTRY = eps]])',
                   '~$eager_operation_source_guard(S, pdestructionoperation[.ORIGIN = (PORIGIN 999 eps)])',
                   '~$eager_operation_source_guard(S, pdestructionoperation[.VALUE = KNOWN (PINT 7)])']
    elif name == 'unregister-pending':
        checks += ['S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
                   'pdestructionoperation.PENDING = (n_pending)',
                   'pdestructionoperation.SOURCE = CONFIG_INVOKE pconfigcall',
                   '$class_instanceof(S, POBJECT n_pending, $ptascii("Error"))',
                   'S.TICKENTRIES = [ptickentry]',
                   'ptickentry.ID = 0 /\\ S.TICKSEQ = 2',
                   '$tick_is_calling(S, 0) /\\ $tick_running(S)',
                   '$destructor_operation_live(S, pdestructionoperation)',
                   'S_budget.DESTRUCTION.OPERATIONS = S.DESTRUCTION.OPERATIONS',
                   'S.GLOBALTABLE = (psymboltable)',
                   '$lookup(psymboltable.ENV, [101]) = (n_cell)',
                   'S.STORE[n_cell] = DEFINED (POBJECT n_shared)',
                   '$throwable_previous_id(S, n_shared) = eps',
                   'S_return_found = $tick_test_seek(S, 6, 1024)',
                   'S_return_found.COMPLETION = NORMAL \\/ S_return_found.COMPLETION = BUDGET',
                   'S_return = S_return_found[.COMPLETION = NORMAL]',
                   '$tick_test_phase(S_return, 6)',
                   'S_return.TICKENTRIES = S.TICKENTRIES',
                   '$throwable_previous_id(S_return, n_shared) = (n_pending)',
                   'S_return.DESTRUCTION.OPERATIONS = eps', *valid('S_return')]
    elif name == 'unregister-target':
        checks += ['S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (TICK_UNREGISTER_RELEASE pshutdownentry_key ptickentry_removed) :: ptask_tail*',
                   'S.TICKENTRIES = eps /\\ S.TICKSEQ = 1',
                   'pdestructionoperation.SOURCE = CONFIG_INVOKE pshutdownentry_key.CALL',
                   'pdestructionoperation.PENDING = eps',
                   '$target_receiver(S, ptickentry_removed.ENTRY.TARGET) = (n_receiver)',
                   '(HOBJECT n_receiver) <- $task_nodes(TICK_UNREGISTER_RELEASE pshutdownentry_key ptickentry_removed)',
                   '$call_task_valid(S, TICK_UNREGISTER_RELEASE pshutdownentry_key ptickentry_removed)',
                   '~$call_task_valid(S[.ORIGIN = (PORIGIN 999 eps)], TICK_UNREGISTER_RELEASE pshutdownentry_key ptickentry_removed)',
                   '~$call_task_valid(S, TICK_UNREGISTER_RELEASE pshutdownentry_key[.CALL = pshutdownentry_key.CALL[.KIND = INTRINSIC_REGISTER_TICK]] ptickentry_removed)',
                   '~$call_task_valid(S, TICK_UNREGISTER_RELEASE pshutdownentry_key[.CALL = pshutdownentry_key.CALL[.SITE = PORIGIN 999 eps]] ptickentry_removed)',
                   '~$call_task_valid(S, TICK_UNREGISTER_RELEASE pshutdownentry_key[.CALL = pshutdownentry_key.CALL[.LINE = $(pshutdownentry_key.CALL.LINE + 1)]] ptickentry_removed)',
                   '~$call_task_valid(S, TICK_UNREGISTER_RELEASE pshutdownentry_key ptickentry_removed[.ID = S.TICKSEQ])',
                   '~$call_task_valid(S, TICK_UNREGISTER_RELEASE pshutdownentry_key ptickentry_removed[.ENTRY = ptickentry_removed.ENTRY[.CALL = ptickentry_removed.ENTRY.CALL[.KIND = INTRINSIC_UNREGISTER_TICK]]])',
                   '~$call_task_valid(S, TICK_UNREGISTER_RELEASE pshutdownentry_key[.TARGET = PORIGIN 999 eps] ptickentry_removed)',
                   '~$call_task_valid(S, TICK_UNREGISTER_RELEASE pshutdownentry_key ptickentry_removed[.ENTRY = ptickentry_removed.ENTRY[.TARGET = PORIGIN 999 eps]])',
                   '~$call_task_valid(S, TICK_UNREGISTER_RELEASE pshutdownentry_key ptickentry_removed[.ENTRY = ptickentry_removed.ENTRY[.ARGS = [PINT 7]]])',
                   '~$call_task_valid(S[.TICKENTRIES = [ptickentry_removed]], TICK_UNREGISTER_RELEASE pshutdownentry_key ptickentry_removed)',
                   '~$call_task_valid(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_receiver)], TICK_UNREGISTER_RELEASE pshutdownentry_key ptickentry_removed)',
                   'S_alias_found = $tick_test_seek(S, 8, 1024)',
                   'S_alias_found.COMPLETION = NORMAL \\/ S_alias_found.COMPLETION = BUDGET',
                   'S_alias = S_alias_found[.COMPLETION = NORMAL]',
                   '$tick_test_phase(S_alias, 8)',
                   '$tick_test_hold_frames(S_alias.FRAMES) = ((pshutdownentry_key, ptickentry_removed))',
                   '$heap_owners($heap_graph(S_alias), HOBJECT n_receiver) = 1',
                   'S_alias.FRAMES = pframe :: pframe_tail*',
                   'pframe.ORIGIN = (pshutdownentry_key.CALL.SITE)',
                   '$call_task_valid(S_alias[.ORIGIN = pframe.ORIGIN][.CURRENT = pframe.CONTEXT], TICK_UNREGISTER_RELEASE pshutdownentry_key ptickentry_removed)',
                   'S_alias_budget = $drive_steps(S_alias, 0)',
                   'S_alias_budget.COMPLETION = BUDGET /\\ S_alias_budget.TODO = S_alias.TODO /\\ S_alias_budget.FRAMES = S_alias.FRAMES',
                   'S_alias_budget.TICKENTRIES = eps /\\ $heap_owners($heap_graph(S_alias_budget), HOBJECT n_receiver) = 1',
                   *valid('S_alias'), *valid('S_alias_budget')]
    if name != 'throw-cleanup':
        checks += ['S_done = $drive_steps(S, 2048)']
    checks += ['S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
               '~$tick_running(S_done) /\\ ~$fiber_blocked(S_done)',
               'S_done.DESTRUCTION.OPERATIONS = eps',
               '$tick_test_only_output(S_done.EVENTS)',
               '$tick_test_output(S_done.EVENTS) = ' + bytes_expr(CASES[name][1]), *valid('S_done')]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact group IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='tick-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    before = sources.fingerprint(); before['tests/semantics/tick_state.py'] = sources.sha(Path(__file__))
    report = {'revision': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': before, 'groups': [], 'passed': False, 'completed': False}
    print(out, flush=True)
    try:
        for name in selected:
            directory = out / name; directory.mkdir()
            source, expected = CASES[name]; path = directory / 'source.php'; path.write_bytes(source)
            native = sources.run([str(ROOT / '.tools/php/bin/php'), '-n', *sources.FLAGS, str(path)], directory, 'native', 10)
            assert native.returncode == 0 and native.stdout == expected and not native.stderr, (name, native.stdout, expected, native.stderr)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                               'extension=' + str(ROOT / '.tools/php-file.so'),
                               str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                parsed = frontend.request({'op': 'parse', 'source': sources.base64.b64encode(source).decode()})
            finally:
                frontend.close()
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            try:
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            finally:
                adapter.close()
            checks = assertions(name, checked['fixture'], directory, path)
            fixture = directory / 'state.watsup'
            fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                               ''.join('  -- if ' + check + '\n' for check in checks))
            modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
            result = sources.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                  *[str(ROOT / name) for name in modules], str(fixture)], directory, 'state', 120)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, (name, result.returncode, result.stdout, result.stderr)
            report['groups'].append({'id': name, 'premises': len(checks), 'source_sha256': sources.sha(path),
                                     'fixture_sha256': sources.sha(fixture)})
            print(name, len(checks), flush=True)
        report.update(passed=True, completed=True)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = sources.fingerprint(); report['after']['tests/semantics/tick_state.py'] = sources.sha(Path(__file__))
        report['passed'] = report['passed'] and report['before'] == report['after']
        report['runner_sha256'] = sources.sha(ROOT / 'tests/semantics/_build/default/numeric_runner.exe')
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()
