#!/usr/bin/env python3
"""Independent exit return, local cleanup and caller-VM output guards."""
import hashlib
import json
import subprocess

import enum_is_callable_output_unique_protocol as unique

base = unique.base
ROOT, OUT, MODULES = base.ROOT, base.OUT, base.MODULES
WATCHED = [ROOT / 'spec/semantics/modules.json',
           ROOT / 'tests/semantics/enum_is_callable_cases.json',
           ROOT / 'tests/semantics/enum_is_callable_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_output_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_output_unique_protocol.py',
           ROOT / 'tests/semantics/enum_is_callable_output_exit_protocol.py',
           ROOT / 'tests/semantics/profile.json',
           ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *MODULES]
PREFIX = r'''
dec $eix_resume(pstate) : pstate
def $eix_resume(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $eix_resume(S) = S -- otherwise
dec $eix_front(pstate, penumqueryoutput, bool) : bool
def $eix_front(S, penumqueryoutput, true) = true
  -- if S.TODO = (ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput z) :: ptask_tail*
def $eix_front(S, penumqueryoutput, false) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = ENUM_IS_CALLABLE_CLEAR penumqueryoutput
  -- if pdestructionoperation.COMPLETION = EXITED z
def $eix_front(S, penumqueryoutput, b_restore) = false -- otherwise
dec $eix_seek(pstate, penumqueryoutput, bool, nat) : pstate
def $eix_seek(S, penumqueryoutput, b_restore, 0) = S
def $eix_seek(S, penumqueryoutput, b_restore, n) = S
  -- if $(n > 0) /\ $eix_front(S, penumqueryoutput, b_restore)
def $eix_seek(S, penumqueryoutput, b_restore, n) = $eix_seek($drive_steps($eix_resume(S), 1), penumqueryoutput, b_restore, $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$eix_front(S, penumqueryoutput, b_restore)
dec $eix_local(pstate, penumqueryoutput) : bool
def $eix_local(S, penumqueryoutput) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = ENUM_IS_CALLABLE_EXIT_FRAME penumqueryoutput z
def $eix_local(S, penumqueryoutput) = false -- otherwise
dec $eix_seek_local(pstate, penumqueryoutput, nat) : pstate
def $eix_seek_local(S, penumqueryoutput, 0) = S
def $eix_seek_local(S, penumqueryoutput, n) = S
  -- if $(n > 0) /\ $eix_local(S, penumqueryoutput)
def $eix_seek_local(S, penumqueryoutput, n) = $eix_seek_local($drive_steps($eix_resume(S), 1), penumqueryoutput, $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$eix_local(S, penumqueryoutput)
dec $eix_exit_call(pstate, bool) : bool
def $eix_exit_call(S, b_fiber) = true
  -- if S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail*
  -- if b_fiber = (S.ACTIVEFIBER =/= eps)
def $eix_exit_call(S, b_fiber) = false -- otherwise
dec $eix_seek_exit(pstate, bool, nat) : pstate
def $eix_seek_exit(S, b_fiber, 0) = S
def $eix_seek_exit(S, b_fiber, n) = S
  -- if $(n > 0) /\ $eix_exit_call(S, b_fiber)
def $eix_seek_exit(S, b_fiber, n) = $eix_seek_exit($drive_steps($eix_resume(S), 1), b_fiber, $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$eix_exit_call(S, b_fiber)
dec $eix_drop_restore(ptask*, penumqueryoutput, int) : ptask*
def $eix_drop_restore(eps, penumqueryoutput, z) = eps
def $eix_drop_restore((ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput z) :: ptask_tail*, penumqueryoutput, z) = $eix_drop_restore(ptask_tail*, penumqueryoutput, z)
def $eix_drop_restore(ptask :: ptask_tail*, penumqueryoutput, z) = ptask :: $eix_drop_restore(ptask_tail*, penumqueryoutput, z)
  -- if ptask =/= ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput z
'''


def source(label, suffix):
    row = base.CASES['enum-is-callable-third-output-' + suffix]
    return row, [f'S_{label}_initial = ' + unique.checked(row, label),
                 f'S_{label}_initial.COMPLETION = BUDGET']


def capture(label, initial, name):
    return [
        f'S_{label}_invoke = $eic_seek({initial}, 0, 5000)',
        f'$eic_front(S_{label}_invoke)',
        f'S_{label}_invoke.TODO = (CONFIG_INVOKE pconfigcall_{label}) :: ptask_{label}_tail*',
        f'$enum_is_callable_output_capture(S_{label}_invoke, pconfigcall_{label}) = (penumqueryoutput_{label})',
        f'penumqueryoutput_{label}.NAME = $ptascii(' + json.dumps(name) + ')',
        f'S_{label}_clear = $drive_steps(S_{label}_invoke[.COMPLETION = NORMAL], 1)',
        f'S_{label}_clear.STORE[penumqueryoutput_{label}.CELL] = DEFINED PNULL',
    ]


def restore(label, start, status):
    return [
        f'S_{label}_restore = $eix_seek({start}, penumqueryoutput_{label}, true, 7000)',
        f'$eix_front(S_{label}_restore, penumqueryoutput_{label}, true)',
        f'S_{label}_restore.TODO = (ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput_{label} {status}) :: (DESTRUCTOR_RESULT pdestructorcall_{label}) :: ptask_{label}_restore_tail*',
        f'$enum_is_callable_exit_restore_valid(S_{label}_restore, penumqueryoutput_{label}, {status})',
        f'$enum_is_callable_exit_return(S_{label}_restore[.TODO = (DESTRUCTOR_RESULT pdestructorcall_{label}) :: ptask_{label}_restore_tail*]) = ((penumqueryoutput_{label}, pdestructorcall_{label}, pdestructionoperation_{label}_old))',
        f'$task_nodes(ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput_{label} {status}) = eps',
        f'$eager_explicit_task(ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput_{label} {status})',
        f'$throwable_marker(ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput_{label} {status})',
        f'~$call_task_valid(S_{label}_restore, ENUM_IS_CALLABLE_EXIT_FRAME penumqueryoutput_{label} {status})',
        f'pdestructionoperation_{label}_old.COMPLETION = NORMAL',
        f'S_{label}_rebased = $drive_steps(S_{label}_restore[.COMPLETION = NORMAL], 1)',
        f'S_{label}_commit = $eix_seek(S_{label}_rebased, penumqueryoutput_{label}, false, 4000)',
        f'$eix_front(S_{label}_commit, penumqueryoutput_{label}, false)',
        f'S_{label}_commit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_{label}) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput_{label}) :: ptask_{label}_tail*',
        f'pdestructionoperation_{label}.COMPLETION = EXITED {status}',
        f'pdestructionoperation_{label}.PENDING = eps',
        f'pdestructionoperation_{label}.VALUE = KNOWN (PBOOL true)',
        f'$eager_operation_source_guard(S_{label}_commit, pdestructionoperation_{label})',
        f'S_{label}_atomic = $destructor_operation_finish(S_{label}_commit[.COMPLETION = NORMAL], pdestructionoperation_{label})',
        f'S_{label}_atomic.COMPLETION = EXITED {status}',
        f'S_{label}_atomic.STORE[penumqueryoutput_{label}.CELL] = DEFINED (PSTRING penumqueryoutput_{label}.NAME)',
        f'S_{label}_atomic.TODO = ptask_{label}_tail*',
    ]


def finish(label, row, status):
    return [
        f'S_{label}_done = $drive($eix_resume(S_{label}_commit), 10000)',
        f'S_{label}_done.COMPLETION = EXITED {status}',
        f'$eic_output(S_{label}_done.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
        f'S_{label}_zero = $drive_steps(S_{label}_commit[.COMPLETION = NORMAL], 0)',
        f'S_{label}_zero.COMPLETION = BUDGET',
        f'$drive($eix_resume(S_{label}_zero), 10000) = S_{label}_done',
    ]


if __name__ == '__main__':
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    row_status, checks = source('status', 'exit-status')
    checks += capture('status', 'S_status_initial', 'FirstCheck::from')
    checks += restore('status', 'S_status_clear', 23) + finish('status', row_status, 23)
    checks += [
        'S_bad_status = S_status_restore[.TODO = (ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput_status 4294967296) :: (DESTRUCTOR_RESULT pdestructorcall_status) :: ptask_status_restore_tail*]',
        '~$enum_is_callable_exit_restore_valid(S_bad_status, penumqueryoutput_status, 4294967296)',
        'penumqueryoutput_wrong = penumqueryoutput_status[.DEPTH = $(penumqueryoutput_status.DEPTH + 1)]',
        '~$enum_is_callable_exit_restore_valid(S_status_restore, penumqueryoutput_wrong, 23)',
        'S_missing = S_status_restore[.TODO = (DESTRUCTOR_RESULT pdestructorcall_status) :: ptask_status_restore_tail*]',
        '~$enum_is_callable_exit_restore_valid(S_missing, penumqueryoutput_status, 23)',
    ]
    row_result, result = source('result', 'exit-result-unassigned')
    checks += result + capture('result', 'S_result_initial', 'FirstCheck::from')
    checks += restore('result', 'S_result_clear', 23)
    checks += [
        '$lookup(S_result_atomic.ENV, $ptascii("ok")) = (n_ok)',
        'S_result_atomic.STORE[n_ok] = DEFINED pvalue_ok',
        '$string_bytes(pvalue_ok) = ($ptascii("UNCHANGED"))',
    ]
    checks += finish('result', row_result, 23)
    row_local, local = source('local', 'exit-local-null-rebound')
    checks += local + capture('local', 'S_local_initial', 'FirstCheck::from')
    checks += [
        'S_local_entry = $eix_seek_local(S_local_clear, penumqueryoutput_local, 7000)',
        '$eix_local(S_local_entry, penumqueryoutput_local)',
        'S_local_entry.TODO = (DESTRUCTOR_ENTER pdestructorcall_local_child) :: ptask_local_child_tail*',
        'pdestructorcall_local_child.OBJECT =/= penumqueryoutput_local.OLD',
        'pdestructorcall_local_child.SITE = eps',
        'pdestructorcall_local_child.OPERATION = (pdestructionoperation_frame)',
        'pdestructionoperation_frame.SOURCE = ENUM_IS_CALLABLE_EXIT_FRAME penumqueryoutput_local 0',
        '$eager_operation_source_guard(S_local_entry, pdestructionoperation_frame)',
        'S_local_entry.STORE[penumqueryoutput_local.CELL] = DEFINED PNULL',
        '(HOBJECT penumqueryoutput_local.OLD) <- S_local_entry.ALLOCATIONS',
        'S_no_restore = S_local_entry[.TODO = $eix_drop_restore(S_local_entry.TODO, penumqueryoutput_local, 0)]',
        '$enum_is_callable_exit_frame_scope(S_no_restore, penumqueryoutput_local, 0) = eps',
        '~$eager_operation_source_guard(S_no_restore, pdestructionoperation_frame)',
        'S_local_body = $drive_steps(S_local_entry[.COMPLETION = NORMAL], 1)',
        '$trace_context(S_local_body, S_local_body.ENV, S_local_body.CURRENT) = [ptraceframe_local, ptraceframe_api]',
        'ptraceframe_local.FILE = eps /\\ ptraceframe_local.LINE = $(-1)',
        'ptraceframe_local.FUNCTION = $ptascii("__destruct")',
        'ptraceframe_local.CLASS = ($ptascii("LocalDrop"))',
        'ptraceframe_api.FUNCTION = $ptascii("is_callable")',
        'ptraceframe_api.LINE = penumqueryoutput_local.CALL.LINE',
        'ptraceframe_api.ARGS = [(KINT 0, pvalue_trace_name), (KINT 1, PBOOL false), (KINT 2, PNULL)]',
        '$string_bytes(pvalue_trace_name) = ($ptascii("FirstCheck::from"))',
    ]
    checks += restore('local', 'S_local_entry', 0)
    checks += [
        'S_local_restore.STORE[penumqueryoutput_local.CELL] = DEFINED pvalue_local_rebound',
        '$string_bytes(pvalue_local_rebound) = ($ptascii("LOCAL-REBOUND"))',
        '$eic_output(S_local_restore.EVENTS) = $ptascii("D-null|STOP|LOCAL-null|")',
    ]
    checks += finish('local', row_local, 0)
    row_nested, nested = source('nested', 'nested-live-output-exit')
    checks += nested + capture('outer', 'S_nested_initial', 'FirstCheck::from')
    checks += capture('inner', 'S_outer_clear', 'OtherCheck::from')
    checks += [
        'penumqueryoutput_inner.DEPTH = $(penumqueryoutput_outer.DEPTH + 1)',
    ]
    checks += restore('inner', 'S_inner_clear', 23)
    checks += [
        'S_inner_atomic.STORE[penumqueryoutput_outer.CELL] = DEFINED PNULL',
    ]
    checks += restore('outer', 'S_inner_atomic', 23)
    checks += [
        'S_outer_atomic.STORE[penumqueryoutput_inner.CELL] = DEFINED (PSTRING $ptascii("OtherCheck::from"))',
        '$lookup(S_outer_atomic.ENV, $ptascii("ok")) = (n_outer_ok)',
        '$lookup(S_outer_atomic.ENV, $ptascii("inner_ok")) = (n_inner_ok)',
        'S_outer_atomic.STORE[n_outer_ok] = DEFINED pvalue_outer_ok',
        'S_outer_atomic.STORE[n_inner_ok] = DEFINED pvalue_inner_ok',
        '$string_bytes(pvalue_outer_ok) = ($ptascii("UNCHANGED"))',
        '$string_bytes(pvalue_inner_ok) = ($ptascii("UNCHANGED"))',
    ]
    checks += finish('outer', row_nested, 23)
    row_fiber, fiber = source('fiber', 'fiber-start-exit')
    checks += fiber + [
        'S_fiber_exit = $eix_seek_exit(S_fiber_initial, true, 10000)',
        '$eix_exit_call(S_fiber_exit, true)',
        '~$enum_is_callable_output_tasks_pending(S_fiber_exit.TODO)',
        '~$enum_is_callable_output_frames_pending(S_fiber_exit.FRAMES)',
        '$enum_is_callable_exit_callers_pending(S_fiber_exit.FIBERCALLERS)',
        '$enum_is_callable_output_exit_pending(S_fiber_exit)',
        '~$enum_is_callable_output_exit_unwind(S_fiber_exit)',
        'S_fiber_refused = $exit_start_unwind(S_fiber_exit, 0)',
        'S_fiber_refused.COMPLETION = UNSUPPORTED "is_callable output destructor exit continuation"',
        'S_fiber_late = S_fiber_exit[.FRAMES = eps]',
        'S_fiber_late_refused = $exit_ready(S_fiber_late, 0)',
        'S_fiber_late_refused.COMPLETION = UNSUPPORTED "is_callable output switched-VM exit continuation"',
    ]
    row_parked, parked = source('parked', 'parked-query-main-exit')
    checks += parked + [
        'S_parked_exit = $eix_seek_exit(S_parked_initial, false, 10000)',
        '$eix_exit_call(S_parked_exit, false)',
        'S_parked_exit.FIBERCALLERS = eps',
        '~$enum_is_callable_output_tasks_pending(S_parked_exit.TODO)',
        '~$enum_is_callable_output_frames_pending(S_parked_exit.FRAMES)',
        '~$enum_is_callable_output_exit_pending(S_parked_exit)',
        '$lookup(S_parked_exit.ENV, $ptascii("fiber")) = (n_parked_cell)',
        'S_parked_exit.STORE[n_parked_cell] = DEFINED (POBJECT n_parked)',
        'S_parked_exit.OBJECTS[n_parked] = FIBER pfiber_parked',
        'pfiber_parked.VM = (pfibervm_parked)',
        r'$enum_is_callable_output_tasks_pending(pfibervm_parked.TODO) \/ $enum_is_callable_output_frames_pending(pfibervm_parked.FRAMES)',
    ]
    fixture = OUT / 'output-exit.watsup'
    fixture.write_text(base.PREFIX + PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + check + '\n' for check in checks))
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
               *map(str, MODULES), str(fixture)]
    result = subprocess.run(command, capture_output=True, timeout=240)
    (OUT / 'command.json').write_text(json.dumps(command) + '\n')
    (OUT / 'stdout').write_bytes(result.stdout)
    (OUT / 'stderr').write_bytes(result.stderr)
    record = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'checks': len(checks), 'exit': result.returncode,
              'stdout': result.stdout.decode(errors='replace'),
              'stderr': result.stderr.decode(errors='replace'),
              'stable': before == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in WATCHED}, 'direct_inputs': before}
    (OUT / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['revision', 'checks', 'exit', 'stdout', 'stderr', 'stable']}), OUT, flush=True)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr and record['stable'], OUT
