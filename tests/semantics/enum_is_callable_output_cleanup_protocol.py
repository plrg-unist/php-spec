#!/usr/bin/env python3
"""Independent C-return pending transfer, cleanup order and exit-status checks."""
import argparse
import hashlib
import json
import subprocess

import enum_is_callable_output_exit_protocol as exitcase

base = exitcase.base
ROOT, OUT, MODULES = base.ROOT, base.OUT, base.MODULES
WATCHED = [*exitcase.WATCHED,
           ROOT / 'tests/semantics/enum_is_callable_output_cleanup_protocol.py']
PREFIX = r'''
dec $eit_front(pstate, penumqueryoutput, bool) : bool
def $eit_front(S, penumqueryoutput, true) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput z) :: (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = ENUM_IS_CALLABLE_CLEAR penumqueryoutput
def $eit_front(S, penumqueryoutput, false) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = ENUM_IS_CALLABLE_CLEAR penumqueryoutput
  -- if pdestructionoperation.PENDING =/= eps
def $eit_front(S, penumqueryoutput, b_throw) = false -- otherwise
dec $eit_seek(pstate, penumqueryoutput, bool, nat) : pstate
def $eit_seek(S, penumqueryoutput, b_throw, 0) = S
def $eit_seek(S, penumqueryoutput, b_throw, n) = S
  -- if $(n > 0) /\ $eit_front(S, penumqueryoutput, b_throw)
def $eit_seek(S, penumqueryoutput, b_throw, n) = $eit_seek($drive_steps($eix_resume(S), 1), penumqueryoutput, b_throw, $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$eit_front(S, penumqueryoutput, b_throw)
dec $eit_frame_seek(pstate, nat) : pstate
def $eit_frame_seek(S, 0) = S
def $eit_frame_seek(S, n) = S
  -- if $(n > 0) /\ $enum_is_callable_exit_frame_capture(S) =/= eps
def $eit_frame_seek(S, n) = $eit_frame_seek($drive_steps($eix_resume(S), 1), $nabs($(n - 1)))
  -- if $(n > 0) /\ $enum_is_callable_exit_frame_capture(S) = eps
dec $eit_second_exit(pstate) : bool
def $eit_second_exit(S) = true
  -- if S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail*
  -- if $enum_is_callable_exit_restore_pending(S)
def $eit_second_exit(S) = false -- otherwise
dec $eit_exit_seek(pstate, nat) : pstate
def $eit_exit_seek(S, 0) = S
def $eit_exit_seek(S, n) = S -- if $(n > 0) /\ $eit_second_exit(S)
def $eit_exit_seek(S, n) = $eit_exit_seek($drive_steps($eix_resume(S), 1), $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$eit_second_exit(S)
'''


def reached(label, suffix, message, completion, status, two_locals=False, shared_reference=False):
    row, checks = exitcase.source(label, suffix)
    checks += exitcase.capture(label, f'S_{label}_initial', 'FirstCheck::from')
    start = f'S_{label}_clear'
    if shared_reference:
        checks += [
            f'S_{label}_frame = $eit_frame_seek({start}, 7000)',
            f'$enum_is_callable_exit_frame_capture(S_{label}_frame) = (penumqueryoutput_{label})',
            f'S_{label}_frame.TODO = [EXIT_UNWIND 23]',
            f'$lookup(S_{label}_frame.ENV, $ptascii("first")) = (n_{label}_shared)',
            f'$lookup(S_{label}_frame.ENV, $ptascii("alias")) = (n_{label}_shared)',
            f'$lookup(S_{label}_frame.ENV, $ptascii("second")) = (n_{label}_other)',
            f'n_{label}_shared =/= n_{label}_other',
            f'S_{label}_frame.STORE[n_{label}_shared] = DEFINED (POBJECT n_{label}_held)',
            f'pnode_{label}_cells* = $destructor_local_cells(S_{label}_frame.ENV, S_{label}_frame.SYMBOLS)',
            f'$heap_count(HCELL n_{label}_shared, pnode_{label}_cells*) = 2',
            f'$heap_count(HCELL n_{label}_other, pnode_{label}_cells*) = 1',
            f'$heap_owners($heap_graph(S_{label}_frame), HCELL n_{label}_shared) = 2',
            f'pnode_{label}_order* = $eager_owner_order(S_{label}_frame)',
            f'n_{label}_cell_count = |pnode_{label}_cells*|',
            f'pnode_{label}_order*[0:n_{label}_cell_count] = pnode_{label}_cells*',
            f'$heap_count(HCELL n_{label}_shared, pnode_{label}_order*) = 2',
            f'$heap_count(HCELL n_{label}_other, pnode_{label}_order*) = 1',
        ]
        start = f'S_{label}_frame'
    if two_locals or shared_reference:
        first_class, second_class = ('LocalSecond', 'LocalFirst') if shared_reference else ('LocalFirst', 'LocalSecond')
        first_message = 'second' if shared_reference else 'first'
        first_output = 'D-null|SECOND-null|' if shared_reference else 'D-null|FIRST-null|'
        checks += [
            f'S_{label}_first = $eix_seek_local({start}, penumqueryoutput_{label}, 7000)',
            f'$eix_local(S_{label}_first, penumqueryoutput_{label})',
            f'S_{label}_first.TODO = (DESTRUCTOR_ENTER pdestructorcall_{label}_first) :: ptask_{label}_first_tail*',
            f'$object_name(S_{label}_first, pdestructorcall_{label}_first.OBJECT) = $ptascii(' + json.dumps(first_class) + ')',
            f'pdestructorcall_{label}_first.PENDING = eps',
            f'S_{label}_first_body = $drive_steps(S_{label}_first[.COMPLETION = NORMAL], 1)',
            f'S_{label}_second = $eix_seek_local(S_{label}_first_body, penumqueryoutput_{label}, 7000)',
            f'$eix_local(S_{label}_second, penumqueryoutput_{label})',
            f'S_{label}_second.TODO = (DESTRUCTOR_ENTER pdestructorcall_{label}_second) :: ptask_{label}_second_tail*',
            f'$object_name(S_{label}_second, pdestructorcall_{label}_second.OBJECT) = $ptascii(' + json.dumps(second_class) + ')',
            f'pdestructorcall_{label}_second.PENDING = (n_{label}_first)',
            f'$string_bytes($throwable_field(S_{label}_second, n_{label}_first, "message")) = ($ptascii(' + json.dumps(first_message) + '))',
            f'~((HOBJECT pdestructorcall_{label}_first.OBJECT) <- S_{label}_second.ALLOCATIONS)',
            f'S_{label}_second.STORE[penumqueryoutput_{label}.CELL] = DEFINED PNULL',
            f'$heap_owners($heap_graph(S_{label}_second), HOBJECT penumqueryoutput_{label}.OLD) = 2',
            f'ptask_{label}_second_tail* = (DESTRUCTOR_RELEASE pdestructionrelease_{label}_context) :: ptask_{label}_context_tail*',
            f'$destructor_release_live(S_{label}_second, pdestructionrelease_{label}_context)',
            f'$heap_count(HOBJECT penumqueryoutput_{label}.OLD, $task_nodes(DESTRUCTOR_RELEASE pdestructionrelease_{label}_context)) = 1',
            f'$enum_is_callable_exit_frame_scope(S_{label}_second, penumqueryoutput_{label}, 23) = (S_{label}_c_scope)',
            f'$enum_is_callable_exit_restore_tail(S_{label}_c_scope.TODO, penumqueryoutput_{label}, 23) = (DESTRUCTOR_RESULT pdestructorcall_{label}_c) :: ptask_{label}_c_tail*',
            f'$task_nodes(DESTRUCTOR_RESULT pdestructorcall_{label}_c) = [HOBJECT penumqueryoutput_{label}.OLD]',
            f'$eic_output(S_{label}_second.EVENTS) = $ptascii(' + json.dumps(first_output) + ')',
        ]
        if shared_reference:
            checks += [
                f'$heap_owners($heap_graph(S_{label}_first), HCELL n_{label}_shared) = 1',
                f'$heap_owners($heap_graph(S_{label}_first), HOBJECT n_{label}_held) = 1',
                f'~(n_{label}_held <- S_{label}_first.DESTRUCTION.CALLED)',
                f'pdestructorcall_{label}_second.OBJECT = n_{label}_held',
            ]
        start = f'S_{label}_second'
    checks += [
        f'S_{label}_throw = $eit_seek({start}, penumqueryoutput_{label}, true, 8000)',
        f'$eit_front(S_{label}_throw, penumqueryoutput_{label}, true)',
        f'S_{label}_throw.TODO = (THROW_SEARCH n_{label}) :: (ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput_{label} 23) :: (DESTRUCTOR_RESULT pdestructorcall_{label}) :: ptask_{label}_restore_tail*',
        f'$enum_is_callable_exit_restore_valid(S_{label}_throw, penumqueryoutput_{label}, 23)',
        f'S_{label}_throw.DESTRUCTION.CALLS = pdestructorcall_{label} :: pdestructorcall_{label}_tail*',
        f'pdestructorcall_{label}.OPERATION = (pdestructionoperation_{label}_old)',
        f'pdestructorcall_{label}.PENDING = eps',
        f'S_{label}_throw.DESTRUCTION.OPERATIONS = pdestructionoperation_{label}_old :: pdestructionoperation_{label}_tail*',
        f'pdestructionoperation_{label}_old.PENDING = eps',
        f'pdestructionoperation_{label}_old.COMPLETION = NORMAL',
        f'S_{label}_throw.EXITSTATUS = 23',
        f'S_{label}_throw.STORE[penumqueryoutput_{label}.CELL] = DEFINED PNULL',
        f'$heap_owners($heap_graph(S_{label}_throw), HOBJECT penumqueryoutput_{label}.OLD) = 1',
        f'$heap_owners($heap_graph(S_{label}_throw), HOBJECT n_{label}) = 1',
        f'$task_nodes(THROW_SEARCH n_{label}) = [HOBJECT n_{label}]',
        f'$task_nodes(ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput_{label} 23) = eps',
        f'$string_bytes($throwable_field(S_{label}_throw, n_{label}, "message")) = ($ptascii(' + json.dumps(message) + '))',
        f'S_{label}_rebased = $drive_steps(S_{label}_throw[.COMPLETION = NORMAL], 1)',
        f'pdestructionoperation_{label}_new = pdestructionoperation_{label}_old[.PENDING = (n_{label})][.COMPLETION = NORMAL]',
        f'S_{label}_rebased.DESTRUCTION.OPERATIONS = pdestructionoperation_{label}_new :: pdestructionoperation_{label}_tail*',
        f'S_{label}_rebased.DESTRUCTION.CALLS = pdestructorcall_{label}_tail*',
        f'S_{label}_rebased.EXITSTATUS = 23',
        f'S_{label}_rebased.STORE[penumqueryoutput_{label}.CELL] = DEFINED PNULL',
        f'$heap_owners($heap_graph(S_{label}_rebased), HOBJECT penumqueryoutput_{label}.OLD) = 1',
        f'$heap_owners($heap_graph(S_{label}_rebased), HOBJECT n_{label}) = 1',
        f'S_{label}_rebased.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_{label}) :: ptask_{label}_rebased_tail*',
        f'$task_nodes(DESTRUCTOR_RELEASE pdestructionrelease_{label}) = [HOBJECT penumqueryoutput_{label}.OLD]',
        f'$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_{label}_new) = [HOBJECT n_{label}]',
        f'S_{label}_commit = $eit_seek(S_{label}_rebased, penumqueryoutput_{label}, false, 4000)',
        f'$eit_front(S_{label}_commit, penumqueryoutput_{label}, false)',
        f'S_{label}_commit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_{label}_new) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput_{label}) :: ptask_{label}_tail*',
        f'~((HOBJECT penumqueryoutput_{label}.OLD) <- S_{label}_commit.ALLOCATIONS)',
        f'$heap_owners($heap_graph(S_{label}_commit), HOBJECT n_{label}) = 1',
        f'S_{label}_commit.STORE[penumqueryoutput_{label}.CELL] = DEFINED PNULL',
        f'$eager_operation_source_guard(S_{label}_commit, pdestructionoperation_{label}_new)',
        f'S_{label}_atomic = $destructor_operation_finish(S_{label}_commit[.COMPLETION = NORMAL], pdestructionoperation_{label}_new)',
        f'S_{label}_atomic.TODO = (THROW_SEARCH n_{label}) :: ptask_{label}_tail*',
        f'S_{label}_atomic.COMPLETION = NORMAL',
        f'S_{label}_atomic.EXITSTATUS = 23',
        f'S_{label}_atomic.RESULT = KNOWN PNULL',
        f'S_{label}_atomic.STORE[penumqueryoutput_{label}.CELL] = DEFINED (PSTRING penumqueryoutput_{label}.NAME)',
        f'$heap_owners($heap_graph(S_{label}_atomic), HOBJECT n_{label}) = 1',
        f'$lookup(S_{label}_atomic.ENV, $ptascii("ok")) = (n_{label}_ok)',
        f'S_{label}_atomic.STORE[n_{label}_ok] = DEFINED pvalue_{label}_ok',
        f'$string_bytes(pvalue_{label}_ok) = ($ptascii("UNCHANGED"))',
        f'S_{label}_done = $drive($eix_resume(S_{label}_commit), 10000)',
        f'S_{label}_done.COMPLETION = {completion}',
        f'S_{label}_done.EXITSTATUS = {status}',
        f'$eic_output(S_{label}_done.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
        f'S_{label}_zero = $drive_steps(S_{label}_throw[.COMPLETION = NORMAL], 0)',
        f'S_{label}_zero.COMPLETION = BUDGET',
        f'$drive($eix_resume(S_{label}_zero), 10000) = S_{label}_done',
    ]
    if two_locals or shared_reference:
        checks += [
            f'$throwable_field(S_{label}_throw, n_{label}, "previous") = POBJECT n_{label}_first',
            f'$heap_owners($heap_graph(S_{label}_throw), HOBJECT n_{label}_first) = 1',
            f'$heap_owners($heap_graph(S_{label}_rebased), HOBJECT n_{label}_first) = 1',
            f'$throwable_field(S_{label}_atomic, n_{label}, "previous") = POBJECT n_{label}_first',
        ]
    return checks


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--control-only', action='store_true')
    args = parser.parse_args()
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    checks = []
    if not args.control_only:
        checks += reached('string', 'integer-exit-cleanup-throw-later-string', 'local', 'EXITED 23', 23)
        checks += reached('ordered', 'two-locals-both-throw', 'second', 'NORMAL', 23, two_locals=True)
        checks += reached('alias', 'two-locals-shared-reference', 'first', 'NORMAL', 23, shared_reference=True)
    row_exit, cleanup_exit = exitcase.source('exit', 'two-locals-throw-then-exit')
    checks += cleanup_exit + exitcase.capture('exit', 'S_exit_initial', 'FirstCheck::from')
    checks += [
        'S_exit_pending = $eit_exit_seek(S_exit_clear, 9000)',
        '$eit_second_exit(S_exit_pending)',
        'S_exit_pending.ACTIVEFIBER = eps /\\ S_exit_pending.FIBERCALLERS = eps',
        'S_exit_pending.DESTRUCTION.CALLS = pdestructorcall_exit_local :: pdestructorcall_exit_tail*',
        'pdestructorcall_exit_local.PENDING = (n_exit_exception)',
        '$string_bytes($throwable_field(S_exit_pending, n_exit_exception, "message")) = ($ptascii("first"))',
        'S_exit_pending.STORE[penumqueryoutput_exit.CELL] = DEFINED PNULL',
        '$heap_owners($heap_graph(S_exit_pending), HOBJECT penumqueryoutput_exit.OLD) = 2',
        'S_exit_pending.DESTRUCTION.RELEASES = pdestructionrelease_exit_context :: pdestructionrelease_exit_tail*',
        '$destructor_release_live(S_exit_pending, pdestructionrelease_exit_context)',
        '$heap_count(HOBJECT penumqueryoutput_exit.OLD, $task_nodes(DESTRUCTOR_RELEASE pdestructionrelease_exit_context)) = 1',
        '$enum_is_callable_exit_frame_scope(S_exit_pending, penumqueryoutput_exit, 23) = (S_exit_c_scope)',
        '$enum_is_callable_exit_restore_tail(S_exit_c_scope.TODO, penumqueryoutput_exit, 23) = (DESTRUCTOR_RESULT pdestructorcall_exit_c) :: ptask_exit_c_tail*',
        '$task_nodes(DESTRUCTOR_RESULT pdestructorcall_exit_c) = [HOBJECT penumqueryoutput_exit.OLD]',
        'S_exit_early = $exit_ready(S_exit_pending, 23)',
        'S_exit_early.COMPLETION = UNSUPPORTED "is_callable output exit local cleanup exit"',
        'S_exit_early.TODO = S_exit_pending.TODO',
        'S_exit_early.DESTRUCTION = S_exit_pending.DESTRUCTION',
        'S_exit_early.STORE = S_exit_pending.STORE',
        'S_exit_early.ALLOCATIONS = S_exit_pending.ALLOCATIONS',
        'S_exit_step = S_exit_pending[.COMPLETION = NORMAL]',
        'PhpStep: S_exit_step ~> S_exit_refused',
        'S_exit_refused.COMPLETION = UNSUPPORTED "is_callable output exit local cleanup exit"',
        'S_exit_refused.STORE[penumqueryoutput_exit.CELL] = DEFINED PNULL',
        'S_exit_refused.DESTRUCTION = S_exit_pending.DESTRUCTION',
        '$enum_is_callable_exit_restore_pending(S_exit_refused)',
        '$heap_owners($heap_graph(S_exit_refused), HOBJECT penumqueryoutput_exit.OLD) = 2',
        '$heap_owners($heap_graph(S_exit_refused), HOBJECT n_exit_exception) = 1',
        '$eic_output(S_exit_refused.EVENTS) = $ptascii("D-null|FIRST-null|SECOND-null|SECOND-STOP|")',
    ]
    checks += [
        'S_marker = S_exit_c_scope[.TODO = (ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput_exit 23) :: (DESTRUCTOR_RESULT pdestructorcall_exit_c) :: ptask_exit_c_tail*]',
        '$enum_is_callable_exit_restore_valid(S_marker, penumqueryoutput_exit, 23)',
        'S_missing = S_marker[.TODO = (DESTRUCTOR_RESULT pdestructorcall_exit_c) :: ptask_exit_c_tail*]',
        '~$enum_is_callable_exit_restore_valid(S_missing, penumqueryoutput_exit, 23)',
        'S_bad_status = S_marker[.TODO = (ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput_exit 4294967296) :: (DESTRUCTOR_RESULT pdestructorcall_exit_c) :: ptask_exit_c_tail*]',
        '~$enum_is_callable_exit_restore_valid(S_bad_status, penumqueryoutput_exit, 4294967296)',
        'penumqueryoutput_depth = penumqueryoutput_exit[.DEPTH = $(penumqueryoutput_exit.DEPTH + 1)]',
        '~$enum_is_callable_exit_restore_valid(S_marker, penumqueryoutput_depth, 23)',
        '~$throwable_live(S_marker, |S_marker.OBJECTS|)',
    ]
    fixture = OUT / 'output-cleanup.watsup'
    fixture.write_text(base.PREFIX + exitcase.PREFIX + PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + check + '\n' for check in checks))
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
               *map(str, MODULES), str(fixture)]
    result = subprocess.run(command, capture_output=True, timeout=240)
    (OUT / 'command.json').write_text(json.dumps(command) + '\n')
    (OUT / 'stdout').write_bytes(result.stdout)
    (OUT / 'stderr').write_bytes(result.stderr)
    record = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'control_only': args.control_only,
              'checks': len(checks), 'exit': result.returncode,
              'stdout': result.stdout.decode(errors='replace'),
              'stderr': result.stderr.decode(errors='replace'),
              'stable': before == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in WATCHED}, 'direct_inputs': before}
    (OUT / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['revision', 'checks', 'exit', 'stdout', 'stderr', 'stable']}), OUT, flush=True)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr and record['stable'], OUT
