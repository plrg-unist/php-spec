#!/usr/bin/env python3
"""Source-reached clone permissions, own callback frames and real input owners."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker
from readonly_clone_sources import CASES, EXPECTED, snapshot

ROOT = Path(__file__).resolve().parents[2]
PREFIX = r'''
dec $clone_review_output(pevent*) : ptbytes
dec $clone_review_is_output(pevent) : bool
def $clone_review_output(eps) = eps
def $clone_review_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $clone_review_output(pevent*)
def $clone_review_output(pevent :: pevent_tail*) = $clone_review_output(pevent_tail*) -- if ~$clone_review_is_output(pevent)
def $clone_review_is_output(OUTPUT ptbytes) = true
def $clone_review_is_output(pevent) = false -- otherwise
dec $clone_review_entering(pstate) : bool
def $clone_review_entering(S) = true
  -- if S.TODO = (CLONE_CALLBACK_ENTER pcloneoperation) :: ptask_tail*
def $clone_review_entering(S) = false -- otherwise
dec $clone_review_operation(pstate) : pcloneoperation?
def $clone_review_operation(S) = (pcloneoperation)
  -- if S.TODO = (CLONE_CALLBACK_ENTER pcloneoperation) :: ptask_tail*
def $clone_review_operation(S) = (pcloneoperation)
  -- if ~$clone_review_entering(S)
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (CLONE_CALLBACK_RESULT pcloneoperation) :: ptask_tail*
  -- if $clone_context_valid(S[.COMPLETION = NORMAL],pcallcontext)
def $clone_review_operation(S) = eps -- otherwise
dec $clone_review_phase(pstate,nat) : bool
def $clone_review_phase(S,0) = $clone_review_entering(S)
def $clone_review_phase(S,1) = ($clone_review_operation(S) =/= eps /\ $clone_review_output(S.EVENTS) = $ptascii("U|"))
def $clone_review_phase(S,2) = ($clone_review_operation(S) =/= eps /\ $clone_review_output(S.EVENTS) = $ptascii("U|Cannot assign array to property Owner::$x of type int|F|"))
def $clone_review_phase(S,3) = ($clone_review_operation(S) =/= eps /\ $clone_review_output(S.EVENTS) = $ptascii("U|Cannot assign array to property Owner::$x of type int|F|W|"))
def $clone_review_phase(S,4) = ($clone_review_operation(S) =/= eps /\ $clone_review_output(S.EVENTS) = $ptascii("C|"))
def $clone_review_phase(S,5) = (S.ACTIVEFIBER = eps /\ S.CLONES =/= eps /\ $clone_review_output(S.EVENTS) = $ptascii("C|pause|"))
def $clone_review_phase(S,6) = (S.ACTIVEFIBER = eps /\ S.CLONES =/= eps /\ $clone_review_output(S.EVENTS) = $ptascii("C|pause|2|"))
def $clone_review_phase(S,7) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin_method
  -- if $clone_method(S,n) = (pmethoddesc)
  -- if porigin_method = pmethoddesc.FUNCTION.ORIGIN
  -- if ~$clone_context_kind(S[.COMPLETION = NORMAL],pcallcontext)
  -- if S.CLONES = eps
def $clone_review_phase(S,n) = false -- otherwise
dec $clone_review_terminal(pstate) : bool
def $clone_review_terminal(S) = (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $clone_review_seek(pstate,nat,nat) : pstate
def $clone_review_seek(S,n_phase,n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $clone_review_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $clone_review_phase(S,n_phase)
def $clone_review_seek(S,n_phase,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$clone_review_phase(S,n_phase)
  -- if n = 0 \/ $clone_review_terminal(S)
def $clone_review_seek(S,n_phase,n) = $clone_review_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_phase,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$clone_review_phase(S,n_phase) /\ ~$clone_review_terminal(S) /\ $(n > 0)
'''

def valid(state):
    return [f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))',
            f'$clone_windows_valid({state})']

def seek(parent, state, phase):
    return [f'{state}_found = $clone_review_seek({parent},{phase},2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$clone_review_phase({state},{phase})', *valid(state)]

def complete(state, expected):
    encoded = '[' + ', '.join(str(c) for c in expected.encode()) + ']'
    return [f'S_done = $drive_steps({state},2048)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
            '$clone_review_output(S_done.EVENTS) = ' + encoded,
            'S_done.CLONES = eps', *valid('S_done')]

def reject(name, changed, predicate='$clone_windows_valid'):
    state = 'S_bad_' + name
    clauses = [f'{state} = {changed}', f'$heap_valid($heap_graph({state}))',
               f'~$call_descriptors_valid({state})']
    if predicate:
        clauses.append(f'~{predicate}({state})')
    return clauses

def window(initial, expected):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
              *seek('S_initial','S_enter',0),
              'S_enter.TODO = (CLONE_CALLBACK_ENTER pcloneoperation) :: ptask_enter_tail*',
              'S_enter.CLONES = [pclonewindow]', 'pclonewindow.OPERATION = pcloneoperation',
              'pclonewindow.AVAILABLE = [$ptascii("x"),$ptascii("y"),$ptascii("z")]',
              'pcloneoperation.INPUT = (VARIABLE $ptascii("original") z_input)',
              'pcloneoperation.CALL = eps', 'pcloneoperation.SCOPE = eps',
              '$clone_operation_valid(S_enter,pcloneoperation)',
              '$lookup(S_enter.ENV,$ptascii("other")) = (n_other_cell)',
              'S_enter.STORE[n_other_cell] = DEFINED (POBJECT n_other)',
              r'$(pcloneoperation.SOURCE < n_other) /\ $(n_other < pcloneoperation.TARGET)',
              *seek('S_enter','S_unset',1),
              'S_unset.CURRENT = (pcallcontext)',
              'S_unset.FRAMES = pframe :: pframe_tail*',
              'pframe.TODO = (CLONE_CALLBACK_RESULT pcloneoperation) :: ptask_callback_tail*',
              'S_unset.CLONES = [pclonewindow_unset]',
              'pclonewindow_unset.OPERATION = pcloneoperation',
              'pclonewindow_unset.AVAILABLE = [$ptascii("x"),$ptascii("z")]',
              '$location_slot(S_unset,PROPERTY pcloneoperation.TARGET $ptascii("x")) = UNDEFINED',
              '$location_slot(S_unset,PROPERTY pcloneoperation.TARGET $ptascii("y")) = UNDEFINED',
              '$location_slot(S_unset,PROPERTY pcloneoperation.TARGET $ptascii("z")) = UNDEFINED',
              '$clone_context_valid(S_unset,pcallcontext)',
              '$clone_reinitable(S_unset,pcloneoperation.TARGET,$ptascii("x"))',
              '~$clone_reinitable(S_unset,pcloneoperation.TARGET,$ptascii("y"))',
              '$clone_reinitable(S_unset,pcloneoperation.TARGET,$ptascii("z"))']
    for name, changed in [
        ('duplicate_window','S_unset[.CLONES = [pclonewindow_unset,pclonewindow_unset]]'),
        ('duplicate_key','S_unset[.CLONES = [pclonewindow_unset[.AVAILABLE = [$ptascii("x"),$ptascii("x"),$ptascii("z")]]]]'),
        ('nonreadonly_key','S_unset[.CLONES = [pclonewindow_unset[.AVAILABLE = [$ptascii("mutable")]]]]'),
        ('missing_key','S_unset[.CLONES = [pclonewindow_unset[.AVAILABLE = [$ptascii("absent")]]]]')]:
        checks += reject(name,changed)
    checks += reject('missing_window','S_unset[.CLONES = eps]',None)
    for name, changed in [
        ('target','pcloneoperation[.TARGET = n_other]'),
        ('line','pcloneoperation[.LINE = $(pcloneoperation.LINE + 1)]'),
        ('input','pcloneoperation[.INPUT = (KNOWN (POBJECT pcloneoperation.SOURCE))]')]:
        op = 'pcloneoperation_bad_' + name
        frame = 'pframe_bad_' + name
        state = 'S_bad_' + name
        checks += [f'{op} = {changed}',
                   f'{frame} = pframe[.TODO = (CLONE_CALLBACK_RESULT {op}) :: ptask_callback_tail*]',
                   f'{state} = S_unset[.FRAMES = {frame} :: pframe_tail*][.CLONES = [pclonewindow_unset[.OPERATION = {op}]]]',
                   f'$clone_operation_body_valid({state},{op})',
                   f'$clone_windows_valid({state})',
                   f'$heap_valid($heap_graph({state}))',
                   f'~$clone_context_frame_valid({state},pcallcontext,{frame},pframe_tail*)',
                   f'~$call_descriptors_valid({state})']
    checks += reject('duplicate_consumer','S_unset[.FRAMES = pframe[.TODO = (CLONE_CALLBACK_RESULT pcloneoperation) :: (CLONE_CALLBACK_RESULT pcloneoperation) :: ptask_callback_tail*] :: pframe_tail*]',None)
    checks += [*seek('S_unset','S_failed',2),
               'S_failed.CLONES = S_unset.CLONES',
               '$location_slot(S_failed,PROPERTY pcloneoperation.TARGET $ptascii("x")) = UNDEFINED',
               *seek('S_failed','S_written',3),
               'S_written.CLONES = [pclonewindow_unset[.AVAILABLE = eps][.REVISIONS = [{KEY $ptascii("x"), COUNT 1},{KEY $ptascii("y"), COUNT 1},{KEY $ptascii("z"), COUNT 1}]]]',
               '$location_slot(S_written,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PINT 2)',
               '$location_slot(S_written,PROPERTY pcloneoperation.TARGET $ptascii("y")) = DEFINED (PINT 3)',
               '$location_slot(S_written,PROPERTY pcloneoperation.TARGET $ptascii("z")) = DEFINED (PINT 4)',
               *seek('S_written','S_manual',7),
               'S_manual.CURRENT = (pcallcontext_manual)',
               'S_manual.CLONES = eps', '~$clone_context_kind(S_manual,pcallcontext_manual)',
               'pcallcontext_manual.CALLSITE = (porigin_manual)',
               '$method_call_selected(S_manual,pcallcontext_manual.TARGET,porigin_manual)']
    checks += reject('manual_window','S_manual[.CLONES = [pclonewindow_unset]]')
    return checks + complete('S_manual',expected)

def ownership(initial, expected, kind):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
              *seek('S_initial','S_body',4),
              '$clone_review_operation(S_body) = (pcloneoperation)',
              'S_body.CURRENT = (pcallcontext)', 'S_body.FRAMES = pframe :: pframe_tail*',
              'pframe.TODO = (CLONE_CALLBACK_RESULT pcloneoperation) :: ptask_callback_tail*',
              '$clone_context_valid(S_body,pcallcontext)',
              '$clone_operation_body_valid(S_body,pcloneoperation)',
              '(HOBJECT pcloneoperation.TARGET) <- S_body.ALLOCATIONS']
    if kind == 'borrowed':
        checks += ['pcloneoperation.CALL = eps',
                   'pcloneoperation.INPUT = (VARIABLE $ptascii("original") z_input)',
                   '~((HOBJECT pcloneoperation.SOURCE) <- S_body.ALLOCATIONS)',
                   '$task_nodes(CLONE_CALLBACK_RESULT pcloneoperation) = [HOBJECT pcloneoperation.TARGET]']
    elif kind == 'temporary':
        checks += ['pcloneoperation.CALL = eps',
                   'pcloneoperation.INPUT = (KNOWN (POBJECT pcloneoperation.SOURCE))',
                   '(HOBJECT pcloneoperation.SOURCE) <- S_body.ALLOCATIONS',
                   '$($heap_owners($heap_prune($heap_graph(S_body)),HOBJECT pcloneoperation.SOURCE) > 0)',
                   '$task_nodes(CLONE_CALLBACK_RESULT pcloneoperation) = [HOBJECT pcloneoperation.TARGET,HOBJECT pcloneoperation.SOURCE]']
        op = 'pcloneoperation[.INPUT = eps]'
        checks += reject('dropped_temporary_input',
            'S_body[.FRAMES = pframe[.TODO = (CLONE_CALLBACK_RESULT '+op+') :: ptask_callback_tail*] :: pframe_tail*][.CLONES = [S_body.CLONES[0][.OPERATION = '+op+']]]',None)
    else:
        checks += ['pcloneoperation.INPUT = eps', 'pcloneoperation.CALL = (pclonecall)',
                   'pclonecall.SENT = [NAMED_SENT (KNOWN (POBJECT pcloneoperation.SOURCE)),NAMED_SENT (KNOWN (PARRAY n_array))]',
                   'S_body.ARRAYS[n_array].ITEMS = eps',
                   '(HOBJECT pcloneoperation.SOURCE) <- S_body.ALLOCATIONS',
                   '$($heap_owners($heap_prune($heap_graph(S_body)),HOBJECT pcloneoperation.SOURCE) > 0)',
                   '$task_nodes(CLONE_CALLBACK_RESULT pcloneoperation) = [HOBJECT pcloneoperation.TARGET] ++ $clone_call_nodes(pclonecall)']
    return checks + complete('S_body',expected)

def fiber(initial, expected):
    checks = ['S_initial = ' + initial, '~S_initial.COMPILESTOP',
              *seek('S_initial','S_parked',5), 'S_parked.CLONES = [pclonewindow]',
              'pcloneoperation = pclonewindow.OPERATION',
              'pclonewindow.AVAILABLE = [$ptascii("x"),$ptascii("y"),$ptascii("z")]',
              '$clone_window_fibers(S_parked,S_parked.ALLOCATIONS,pcloneoperation,CLONE_CALLBACK)',
              '~$clone_window_tasks(S_parked.TODO,pcloneoperation,CLONE_CALLBACK)',
              '~$clone_window_frames(S_parked.FRAMES,pcloneoperation,CLONE_CALLBACK)',
              '$clone_reinitable(S_parked,pcloneoperation.TARGET,$ptascii("x"))',
              *seek('S_parked','S_main_written',6),
              'S_main_written.CLONES = [pclonewindow[.AVAILABLE = [$ptascii("y"),$ptascii("z")]][.REVISIONS = [{KEY $ptascii("x"), COUNT 1},{KEY $ptascii("y"), COUNT 0},{KEY $ptascii("z"), COUNT 0}]]]',
              '$clone_window_fibers(S_main_written,S_main_written.ALLOCATIONS,pcloneoperation,CLONE_CALLBACK)',
              '~$clone_reinitable(S_main_written,pcloneoperation.TARGET,$ptascii("x"))',
              '$clone_reinitable(S_main_written,pcloneoperation.TARGET,$ptascii("y"))',
              '$location_slot(S_main_written,PROPERTY pcloneoperation.TARGET $ptascii("x")) = DEFINED (PINT 2)']
    checks += reject('parked_missing_window','S_main_written[.CLONES = eps]',None)
    checks += reject('parked_duplicate_window','S_main_written[.CLONES = S_main_written.CLONES ++ S_main_written.CLONES]')
    return checks + complete('S_main_written',expected)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', required=True,
                        choices=['window', 'borrowed', 'intrinsic', 'temporary', 'fiber'])
    parser.add_argument('--freeze', type=Path)
    parser.add_argument('--prepare', action='store_true', help='frontend/adapter only; no model credit')
    args = parser.parse_args()
    names = {'window': 'readonly-state-clone-window',
             'borrowed': 'readonly-clone-cv-original-retired',
             'intrinsic': 'readonly-clone-two-argument-intrinsic-original-retired',
             'temporary': 'readonly-clone-factory-temporary-source',
             'fiber': 'readonly-clone-fiber-escaped-window'}
    name = names[args.group]
    source_bytes, expected = CASES[name], EXPECTED[name]
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = snapshot(args.freeze)
    out = Path(tempfile.mkdtemp(prefix='readonly-clone-'+args.group+'-', dir=ROOT/'.tools')).resolve()
    path = out/'source.php'; path.write_bytes(source_bytes)
    report = {'passed': False, 'before': before, 'group': args.group, 'source': str(path),
              'source_sha256': sha(path), 'state_assertions_evaluated': 0,
              'mode': 'prepared; model UNRUN' if args.prepare else 'source-reached',
              'profile': cross.invoke.types.PROFILE, 'runner_mode': 'AL', 'jobs': 1}
    frontend = adapter = None
    print(out, flush=True)
    try:
        frontend = Worker([str(ROOT/'.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
            '-d', 'extension='+str(ROOT/'.tools/php-file.so'), str(ROOT/'frontend/worker.php')], out/'frontend')
        adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)], out/'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source_bytes).decode()})
        assert parsed['accepted'] is True
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] is True
        initial = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(path)).decode())+')'
        if args.group in ['borrowed', 'intrinsic', 'temporary']:
            clauses = ownership(initial, expected, args.group)
        else:
            clauses = globals()[args.group](initial, expected)
        clauses = ['program_source = '+checked['fixture'], *clauses]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
            ''.join('  -- if '+clause+'\n' for clause in clauses)+
            '\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report['prepared_assertions'] = len(clauses)
        if not args.prepare:
            modules = json.loads((ROOT/'spec/semantics/modules.json').read_text())
            result = cross.invoke.process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),
                *[str(ROOT/p) for p in modules], str(fixture)], out/'numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report.update(passed=True, state_assertions_evaluated=len(clauses))
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        if adapter: adapter.close()
        if frontend: frontend.close()
        report['after'] = snapshot(args.freeze)
        report['source_unchanged'] = report['source_sha256'] == sha(path)
        report['passed'] = report['passed'] and report['before'] == report['after'] and report['source_unchanged']
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['mode'] if args.prepare else report['passed'], flush=True)
    assert args.prepare or report['passed']


if __name__ == '__main__':
    main()
