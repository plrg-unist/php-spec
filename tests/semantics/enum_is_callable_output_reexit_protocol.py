#!/usr/bin/env python3
"""Independent nested cleanup C returns, borrowed anchors and latest status."""
import argparse
import hashlib
import json
import subprocess

import enum_is_callable_output_cleanup_protocol as cleanup

exitcase = cleanup.exitcase
base = cleanup.base
ROOT, OUT, MODULES = base.ROOT, base.OUT, base.MODULES
WATCHED = [*cleanup.WATCHED,
           ROOT / 'tests/semantics/enum_is_callable_output_reexit_protocol.py']
PREFIX = r'''
dec $eir_front(pstate, penumqueryoutput, nat) : bool
def $eir_front(S, penumqueryoutput, 0) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = ENUM_IS_CALLABLE_CLEANUP_FRAME penumqueryoutput z pdestructorcall_anchor
def $eir_front(S, penumqueryoutput, 1) = true
  -- if S.TODO = (ENUM_IS_CALLABLE_CLEANUP_RESTORE penumqueryoutput z pdestructorcall) :: ptask_tail*
def $eir_front(S, penumqueryoutput, 2) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ENUM_IS_CALLABLE_CLEANUP_RESTORE penumqueryoutput z pdestructorcall) :: ptask_tail*
def $eir_front(S, penumqueryoutput, 3) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = ENUM_IS_CALLABLE_CLEAR penumqueryoutput
def $eir_front(S, penumqueryoutput, 4) = true
  -- if $enum_is_callable_cleanup_capture(S) = ((penumqueryoutput, z, pdestructorcall))
def $eir_front(S, penumqueryoutput, n_kind) = false -- otherwise
dec $eir_seek(pstate, penumqueryoutput, nat, nat) : pstate
def $eir_seek(S, penumqueryoutput, n_kind, 0) = S
def $eir_seek(S, penumqueryoutput, n_kind, n) = S
  -- if $(n > 0) /\ $eir_front(S, penumqueryoutput, n_kind)
def $eir_seek(S, penumqueryoutput, n_kind, n) = S
  -- if $(n > 0) /\ ~$eir_front(S, penumqueryoutput, n_kind)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $eir_seek(S, penumqueryoutput, n_kind, n) = $eir_seek($drive_steps($eix_resume(S), 1), penumqueryoutput, n_kind, $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$eir_front(S, penumqueryoutput, n_kind)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $eir_drop(ptask*, penumqueryoutput, int, pdestructorcall) : ptask*
def $eir_drop(eps, penumqueryoutput, z, pdestructorcall) = eps
def $eir_drop((ENUM_IS_CALLABLE_CLEANUP_RESTORE penumqueryoutput z pdestructorcall) :: ptask_tail*, penumqueryoutput, z, pdestructorcall) = $eir_drop(ptask_tail*, penumqueryoutput, z, pdestructorcall)
def $eir_drop(ptask :: ptask_tail*, penumqueryoutput, z, pdestructorcall) = ptask :: $eir_drop(ptask_tail*, penumqueryoutput, z, pdestructorcall)
  -- if ptask =/= ENUM_IS_CALLABLE_CLEANUP_RESTORE penumqueryoutput z pdestructorcall
dec $eir_drop_root_frames(pframe*, penumqueryoutput, int) : pframe*
def $eir_drop_root_frames(eps, penumqueryoutput, z) = eps
def $eir_drop_root_frames(pframe :: pframe_tail*, penumqueryoutput, z) = pframe[.TODO = $eix_drop_restore(pframe.TODO, penumqueryoutput, z)] :: $eir_drop_root_frames(pframe_tail*, penumqueryoutput, z)
'''


def begin(label, suffix):
    row, checks = exitcase.source(label, suffix)
    return row, checks + exitcase.capture(label, f'S_{label}_initial', 'FirstCheck::from')


def stage(label, start, status):
    return [
        f'S_{label}_stage = $eir_seek({start}, penumqueryoutput_{label}, 1, 5000)',
        f'$eir_front(S_{label}_stage, penumqueryoutput_{label}, 1)',
        f'S_{label}_stage.TODO = (ENUM_IS_CALLABLE_CLEANUP_RESTORE penumqueryoutput_{label} 23 pdestructorcall_{label}_stage) :: (DESTRUCTOR_RESULT pdestructorcall_{label}_stage) :: ptask_{label}_stage_tail*',
        f'$enum_is_callable_cleanup_restore_valid(S_{label}_stage, penumqueryoutput_{label}, 23, pdestructorcall_{label}_stage)',
        f'$task_nodes(ENUM_IS_CALLABLE_CLEANUP_RESTORE penumqueryoutput_{label} 23 pdestructorcall_{label}_stage) = eps',
        f'$eager_explicit_task(ENUM_IS_CALLABLE_CLEANUP_RESTORE penumqueryoutput_{label} 23 pdestructorcall_{label}_stage)',
        f'$throwable_marker(ENUM_IS_CALLABLE_CLEANUP_RESTORE penumqueryoutput_{label} 23 pdestructorcall_{label}_stage)',
        f'S_{label}_stage.EXITSTATUS = {status}',
        f'$heap_owners($heap_graph(S_{label}_stage), HOBJECT pdestructorcall_{label}_stage.OBJECT) = 1',
        f'$heap_owners($heap_graph(S_{label}_stage), HOBJECT penumqueryoutput_{label}.OLD) = 2',
        f'pdestructorcall_{label}_stage.OPERATION = (pdestructionoperation_{label}_parent)',
        f'pdestructionoperation_{label}_parent.COMPLETION = NORMAL',
        f'pdestructionoperation_{label}_parent.PENDING = eps',
        f'S_{label}_after = $drive_steps(S_{label}_stage[.COMPLETION = NORMAL], 1)',
        f'S_{label}_after.EXITSTATUS = {status}',
        f'pdestructionoperation_{label}_parent <- S_{label}_after.DESTRUCTION.OPERATIONS',
        f'$heap_owners($heap_graph(S_{label}_after), HOBJECT pdestructorcall_{label}_stage.OBJECT) = 1',
        f'S_{label}_after.STORE[penumqueryoutput_{label}.CELL] = DEFINED PNULL',
    ]


def root_finish(label, start, receipt, status):
    return [
        f'S_{label}_root = $eix_seek({start}, penumqueryoutput_{label}, true, 5000)',
        f'S_{label}_root.TODO = (ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput_{label} {receipt}) :: (DESTRUCTOR_RESULT pdestructorcall_{label}_root) :: ptask_{label}_root_tail*',
        f'$enum_is_callable_exit_restore_valid(S_{label}_root, penumqueryoutput_{label}, {receipt})',
        f'S_{label}_root.EXITSTATUS = {status}',
        f'$heap_owners($heap_graph(S_{label}_root), HOBJECT penumqueryoutput_{label}.OLD) = 1',
        f'S_{label}_root_after = $drive_steps(S_{label}_root[.COMPLETION = NORMAL], 1)',
        f'S_{label}_commit = $eir_seek(S_{label}_root_after, penumqueryoutput_{label}, 3, 3000)',
        f'S_{label}_commit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_{label}_query) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput_{label}) :: ptask_{label}_tail*',
        f'pdestructionoperation_{label}_query.COMPLETION = EXITED {status}',
        f'pdestructionoperation_{label}_query.PENDING = eps',
        f'$eager_operation_source_guard(S_{label}_commit, pdestructionoperation_{label}_query)',
        f'~((HOBJECT penumqueryoutput_{label}.OLD) <- S_{label}_commit.ALLOCATIONS)',
        f'S_{label}_atomic = $destructor_operation_finish(S_{label}_commit[.COMPLETION = NORMAL], pdestructionoperation_{label}_query)',
        f'S_{label}_atomic.COMPLETION = EXITED {status}',
        f'S_{label}_atomic.EXITSTATUS = {status}',
        f'S_{label}_atomic.STORE[penumqueryoutput_{label}.CELL] = DEFINED (PSTRING penumqueryoutput_{label}.NAME)',
        f'S_{label}_atomic.TODO = ptask_{label}_tail*',
    ]


def own():
    row, checks = begin('own', 'cleanup-exit-own-local-trace')
    checks += [
        'S_own_entry = $eir_seek(S_own_clear, penumqueryoutput_own, 0, 5000)',
        'S_own_entry.TODO = (DESTRUCTOR_ENTER pdestructorcall_own_child) :: ptask_own_child_tail*',
        'pdestructorcall_own_child.OPERATION = (pdestructionoperation_own_child)',
        'pdestructionoperation_own_child.SOURCE = ENUM_IS_CALLABLE_CLEANUP_FRAME penumqueryoutput_own 23 pdestructorcall_own_anchor',
        '$eager_operation_source_guard(S_own_entry, pdestructionoperation_own_child)',
        '$heap_owners($heap_graph(S_own_entry), HOBJECT pdestructorcall_own_anchor.OBJECT) = 2',
        '$heap_owners($heap_graph(S_own_entry), HOBJECT penumqueryoutput_own.OLD) = 2',
        'S_own_entry.EXITSTATUS = 29',
        'S_missing = S_own_entry[.TODO = $eir_drop(S_own_entry.TODO, penumqueryoutput_own, 23, pdestructorcall_own_anchor)]',
        '$enum_is_callable_cleanup_scope(S_missing, penumqueryoutput_own, 23, pdestructorcall_own_anchor) = eps',
        '~$eager_operation_source_guard(S_missing, pdestructionoperation_own_child)',
        'S_own_body = $drive_steps(S_own_entry[.COMPLETION = NORMAL], 1)',
        'S_own_body.CURRENT = (pcallcontext_own_body)',
        '$enum_is_callable_cleanup_body(S_own_body)',
        'S_missing_root = S_own_body[.TODO = $eix_drop_restore(S_own_body.TODO, penumqueryoutput_own, 23)][.FRAMES = $eir_drop_root_frames(S_own_body.FRAMES, penumqueryoutput_own, 23)]',
        '$enum_is_callable_exit_frame_scope(S_missing_root, penumqueryoutput_own, 23) = eps',
        '~$destructor_context_valid(S_missing_root, pcallcontext_own_body)',
        '~$enum_is_callable_cleanup_body(S_missing_root)',
        '$trace_context(S_own_body, S_own_body.ENV, S_own_body.CURRENT) = [ptraceframe_own_child, ptraceframe_own_api]',
        'ptraceframe_own_child.CLASS = ($ptascii("ChildDrop"))',
        'ptraceframe_own_child.FUNCTION = $ptascii("__destruct")',
        'ptraceframe_own_child.FILE = eps /\\ ptraceframe_own_child.LINE = $(-1)',
        'ptraceframe_own_api.FUNCTION = $ptascii("is_callable")',
        'ptraceframe_own_api.LINE = penumqueryoutput_own.CALL.LINE',
        'ptraceframe_own_api.ARGS = [(KINT 0, pvalue_own_name), (KINT 1, PBOOL false), (KINT 2, PNULL)]',
        '$string_bytes(pvalue_own_name) = ($ptascii("FirstCheck::from"))',
        'S_orphan = S_own_body[.TODO = [ENUM_IS_CALLABLE_CLEANUP_RESTORE penumqueryoutput_own 23 pdestructorcall_own_anchor]]',
        '$enum_is_callable_cleanup_scope(S_orphan, penumqueryoutput_own, 23, pdestructorcall_own_anchor) = eps',
        '~$eager_operation_source_guard(S_orphan, pdestructionoperation_own_child)',
        '~$call_task_valid(S_own_entry, ENUM_IS_CALLABLE_CLEANUP_FRAME penumqueryoutput_own 23 pdestructorcall_own_anchor)',
    ]
    checks += stage('own', 'S_own_entry', 29)
    checks += [
        'pdestructorcall_own_stage = pdestructorcall_own_anchor',
        'S_own_zero = $drive_steps(S_own_stage[.COMPLETION = NORMAL], 0)',
        'S_own_zero.COMPLETION = BUDGET',
        '$drive_steps($eix_resume(S_own_zero), 1) = S_own_after',
        'S_own_tail = $eix_seek_local(S_own_after, penumqueryoutput_own, 5000)',
        'S_own_tail.TODO = (DESTRUCTOR_ENTER pdestructorcall_own_tail) :: ptask_own_tail_entry*',
        '$object_name(S_own_tail, pdestructorcall_own_tail.OBJECT) = $ptascii("TailDrop")',
        '~((HOBJECT pdestructorcall_own_anchor.OBJECT) <- S_own_tail.ALLOCATIONS)',
    ]
    checks += root_finish('own', 'S_own_tail', 23, 29)
    checks += [
        'S_own_root.STORE[penumqueryoutput_own.CELL] = DEFINED pvalue_own_rebound',
        '$string_bytes(pvalue_own_rebound) = ($ptascii("TAIL-REBOUND"))',
        'S_own_done = $drive($eix_resume(S_own_commit), 10000)',
        'S_own_done.COMPLETION = EXITED 29',
        '$eic_output(S_own_done.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
        'S_bad_status = S_own_root[.EXITSTATUS = 4294967296]',
        '~$exit_status_valid(S_bad_status)',
        '$enum_is_callable_exit_restore_valid(S_bad_status, penumqueryoutput_own, 23)',
    ]
    return checks


def nested():
    _, checks = begin('nested', 'cleanup-exit-third-integer')
    checks += [
        'S_nested_entry = $eir_seek(S_nested_clear, penumqueryoutput_nested, 0, 5000)',
        'S_nested_entry.TODO = (DESTRUCTOR_ENTER pdestructorcall_nested_child) :: ptask_nested_child_tail*',
        'pdestructorcall_nested_child.OPERATION = (pdestructionoperation_nested_child)',
        'pdestructionoperation_nested_child.SOURCE = ENUM_IS_CALLABLE_CLEANUP_FRAME penumqueryoutput_nested 23 pdestructorcall_nested_parent',
    ]
    checks += stage('nested', 'S_nested_entry', 31)
    checks += [
        'pdestructorcall_nested_stage = pdestructorcall_nested_child',
        'pdestructorcall_nested_stage =/= pdestructorcall_nested_parent',
        '$enum_is_callable_cleanup_restore_valid(S_nested_stage, penumqueryoutput_nested, 23, pdestructorcall_nested_parent)',
        'S_graft = S_nested_stage[.TODO = (ENUM_IS_CALLABLE_CLEANUP_RESTORE penumqueryoutput_nested 23 pdestructorcall_nested_parent) :: (DESTRUCTOR_RESULT pdestructorcall_nested_child) :: ptask_nested_stage_tail*]',
        '~$enum_is_callable_cleanup_restore_valid(S_graft, penumqueryoutput_nested, 23, pdestructorcall_nested_parent)',
        '$enum_is_callable_cleanup_scope(S_graft, penumqueryoutput_nested, 23, pdestructorcall_nested_parent) = eps',
        '~$enum_is_callable_cleanup_tail(S_nested_stage, [DESTRUCTOR_OPERATION_EXIT pdestructionoperation_nested_child, ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput_nested 23], pdestructionoperation_nested_child, penumqueryoutput_nested, 23)',
        'S_nested_parent = $eir_seek(S_nested_after, penumqueryoutput_nested, 1, 5000)',
        'S_nested_parent.TODO = (ENUM_IS_CALLABLE_CLEANUP_RESTORE penumqueryoutput_nested 23 pdestructorcall_nested_parent) :: (DESTRUCTOR_RESULT pdestructorcall_nested_parent) :: ptask_nested_parent_tail*',
        '$enum_is_callable_cleanup_restore_valid(S_nested_parent, penumqueryoutput_nested, 23, pdestructorcall_nested_parent)',
        '~((HOBJECT pdestructorcall_nested_child.OBJECT) <- S_nested_parent.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_nested_parent), HOBJECT pdestructorcall_nested_parent.OBJECT) = 1',
        'S_nested_parent.EXITSTATUS = 31',
        'S_nested_parent_after = $drive_steps(S_nested_parent[.COMPLETION = NORMAL], 1)',
    ]
    return checks + root_finish('nested', 'S_nested_parent_after', 23, 31)


def alias():
    _, checks = begin('alias', 'cleanup-exit-own-local-alias')
    checks += [
        'S_alias_frame = $eir_seek(S_alias_clear, penumqueryoutput_alias, 4, 5000)',
        '$enum_is_callable_cleanup_capture(S_alias_frame) = ((penumqueryoutput_alias, 23, pdestructorcall_alias_anchor))',
        'S_alias_frame.TODO = [EXIT_UNWIND 29]',
        '$lookup(S_alias_frame.ENV, $ptascii("first")) = (n_alias_shared)',
        '$lookup(S_alias_frame.ENV, $ptascii("alias")) = (n_alias_shared)',
        '$lookup(S_alias_frame.ENV, $ptascii("second")) = (n_alias_other)',
        'S_alias_frame.STORE[n_alias_shared] = DEFINED (POBJECT n_alias_held)',
        '$heap_owners($heap_graph(S_alias_frame), HCELL n_alias_shared) = 2',
        'pnode_alias_cells* = $destructor_local_cells(S_alias_frame.ENV, S_alias_frame.SYMBOLS)',
        'pnode_alias_order* = $eager_owner_order(S_alias_frame)',
        'n_alias_count = |pnode_alias_cells*|',
        'pnode_alias_order*[0:n_alias_count] = pnode_alias_cells*',
        '$heap_count(HCELL n_alias_shared, pnode_alias_order*) = 2',
        '$heap_count(HCELL n_alias_other, pnode_alias_order*) = 1',
        'S_alias_second = $eir_seek(S_alias_frame, penumqueryoutput_alias, 0, 5000)',
        'S_alias_second.TODO = (DESTRUCTOR_ENTER pdestructorcall_alias_second) :: ptask_alias_second_tail*',
        '$object_name(S_alias_second, pdestructorcall_alias_second.OBJECT) = $ptascii("ChildSecond")',
        '$heap_owners($heap_graph(S_alias_second), HCELL n_alias_shared) = 1',
        '$heap_owners($heap_graph(S_alias_second), HOBJECT n_alias_held) = 1',
        '~(n_alias_held <- S_alias_second.DESTRUCTION.CALLED)',
        'S_alias_second_body = $drive_steps(S_alias_second[.COMPLETION = NORMAL], 1)',
        'S_alias_first = $eir_seek(S_alias_second_body, penumqueryoutput_alias, 0, 5000)',
        'S_alias_first.TODO = (DESTRUCTOR_ENTER pdestructorcall_alias_first) :: ptask_alias_first_tail*',
        'pdestructorcall_alias_first.OBJECT = n_alias_held',
        '~((HOBJECT pdestructorcall_alias_second.OBJECT) <- S_alias_first.ALLOCATIONS)',
        'S_alias_first.STORE[penumqueryoutput_alias.CELL] = DEFINED PNULL',
    ]
    return checks


def thrown():
    row, checks = begin('thrown', 'cleanup-exit-own-local-throw')
    checks += [
        'S_thrown_front = $eir_seek(S_thrown_clear, penumqueryoutput_thrown, 2, 7000)',
        'S_thrown_front.TODO = (THROW_SEARCH n_thrown) :: (ENUM_IS_CALLABLE_CLEANUP_RESTORE penumqueryoutput_thrown 23 pdestructorcall_thrown_local) :: (DESTRUCTOR_RESULT pdestructorcall_thrown_local) :: ptask_thrown_local_tail*',
        '$enum_is_callable_cleanup_restore_valid(S_thrown_front, penumqueryoutput_thrown, 23, pdestructorcall_thrown_local)',
        '$heap_owners($heap_graph(S_thrown_front), HOBJECT pdestructorcall_thrown_local.OBJECT) = 1',
        '$heap_owners($heap_graph(S_thrown_front), HOBJECT n_thrown) = 1',
        'S_thrown_step = S_thrown_front[.COMPLETION = NORMAL]',
        'PhpStep: S_thrown_step ~> S_thrown_peeled',
        'S_thrown_peeled.TODO = (THROW_SEARCH n_thrown) :: (DESTRUCTOR_RESULT pdestructorcall_thrown_local) :: ptask_thrown_local_tail*',
        'S_thrown_peeled.DESTRUCTION = S_thrown_step.DESTRUCTION',
        '$heap_owners($heap_graph(S_thrown_peeled), HOBJECT pdestructorcall_thrown_local.OBJECT) = 1',
        'S_thrown_tail = $eix_seek_local(S_thrown_peeled, penumqueryoutput_thrown, 5000)',
        'S_thrown_tail.TODO = (DESTRUCTOR_ENTER pdestructorcall_thrown_tail) :: ptask_thrown_tail_entry*',
        '$object_name(S_thrown_tail, pdestructorcall_thrown_tail.OBJECT) = $ptascii("TailDrop")',
        'pdestructorcall_thrown_tail.PENDING = (n_thrown)',
        '~((HOBJECT pdestructorcall_thrown_local.OBJECT) <- S_thrown_tail.ALLOCATIONS)',
        'S_thrown_tail_body = $drive_steps(S_thrown_tail[.COMPLETION = NORMAL], 1)',
        '~$enum_is_callable_cleanup_body(S_thrown_tail_body)',
        'S_pending_exit = $exit_ready(S_thrown_tail_body, 29)',
        'S_pending_exit.COMPLETION = UNSUPPORTED "is_callable output exit local cleanup exit"',
        'S_thrown_root = $eit_seek(S_thrown_tail, penumqueryoutput_thrown, true, 5000)',
        'S_thrown_root.TODO = (THROW_SEARCH n_thrown) :: (ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput_thrown 23) :: (DESTRUCTOR_RESULT pdestructorcall_thrown_root) :: ptask_thrown_root_tail*',
        'S_thrown_transfer = $enum_is_callable_exit_finish(S_thrown_root[.TODO = (ENUM_IS_CALLABLE_EXIT_RESTORE penumqueryoutput_thrown 23) :: (DESTRUCTOR_RESULT pdestructorcall_thrown_root) :: ptask_thrown_root_tail*][.COMPLETION = NORMAL], penumqueryoutput_thrown, NORMAL, (n_thrown))',
        'S_thrown_commit = $eir_seek(S_thrown_transfer, penumqueryoutput_thrown, 3, 3000)',
        'S_thrown_commit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_thrown_query) :: (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput_thrown) :: ptask_thrown_tail*',
        'pdestructionoperation_thrown_query.PENDING = (n_thrown)',
        'S_thrown_atomic = $destructor_operation_finish(S_thrown_commit[.COMPLETION = NORMAL], pdestructionoperation_thrown_query)',
        'S_thrown_atomic.COMPLETION = NORMAL',
        'S_thrown_atomic.EXITSTATUS = 29',
        'S_thrown_atomic.STORE[penumqueryoutput_thrown.CELL] = DEFINED (PSTRING penumqueryoutput_thrown.NAME)',
        'S_thrown_atomic.TODO = (THROW_SEARCH n_thrown) :: ptask_thrown_tail*',
        '$heap_owners($heap_graph(S_thrown_atomic), HOBJECT n_thrown) = 1',
        'S_thrown_done = $drive($eix_resume(S_thrown_commit), 10000)',
        'S_thrown_done.COMPLETION = NORMAL /\\ S_thrown_done.EXITSTATUS = 29',
        '$eic_output(S_thrown_done.EVENTS) = $ptascii(' + json.dumps(row['expected_normal_stdout']) + ')',
    ]
    return checks


def roots():
    _, checks = exitcase.source('roots', 'nested-output-cleanup-reexit')
    checks += exitcase.capture('outer', 'S_roots_initial', 'FirstCheck::from')
    checks += exitcase.capture('inner', 'S_outer_clear', 'OtherCheck::from')
    checks += stage('inner', 'S_inner_clear', 29)
    checks += [
        'penumqueryoutput_inner.DEPTH = $(penumqueryoutput_outer.DEPTH + 1)',
        'S_inner_stage.STORE[penumqueryoutput_outer.CELL] = DEFINED PNULL',
    ]
    checks += root_finish('inner', 'S_inner_after', 23, 29)
    checks += ['S_inner_atomic.STORE[penumqueryoutput_outer.CELL] = DEFINED PNULL']
    checks += root_finish('outer', 'S_inner_atomic', 29, 29)
    checks += [
        'S_outer_atomic.STORE[penumqueryoutput_inner.CELL] = DEFINED (PSTRING penumqueryoutput_inner.NAME)',
        '$lookup(S_outer_atomic.ENV, $ptascii("ok")) = (n_outer_ok)',
        '$lookup(S_outer_atomic.ENV, $ptascii("inner_ok")) = (n_inner_ok)',
        'S_outer_atomic.STORE[n_outer_ok] = DEFINED pvalue_outer_ok',
        'S_outer_atomic.STORE[n_inner_ok] = DEFINED pvalue_inner_ok',
        '$string_bytes(pvalue_outer_ok) = ($ptascii("UNCHANGED"))',
        '$string_bytes(pvalue_inner_ok) = ($ptascii("UNCHANGED"))',
    ]
    return checks


if __name__ == '__main__':
    groups = {'own': own, 'nested': nested, 'alias': alias, 'thrown': thrown, 'roots': roots}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=['all', *groups], default='all')
    args = parser.parse_args()
    before = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
              for path in WATCHED}
    selected = groups.values() if args.group == 'all' else [groups[args.group]]
    checks = [check for group in selected for check in group()]
    fixture = OUT / 'output-reexit.watsup'
    fixture.write_text(base.PREFIX + exitcase.PREFIX + cleanup.PREFIX + PREFIX
                       + '\ndec $main() : bool\ndef $main() = true\n'
                       + ''.join(('  -- ' if check.startswith('PhpStep:') else '  -- if ')
                                 + check + '\n' for check in checks))
    command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
               *map(str, MODULES), str(fixture)]
    result = subprocess.run(command, capture_output=True, timeout=480)
    (OUT / 'command.json').write_text(json.dumps(command) + '\n')
    (OUT / 'stdout').write_bytes(result.stdout)
    (OUT / 'stderr').write_bytes(result.stderr)
    record = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'group': args.group, 'checks': len(checks), 'exit': result.returncode,
              'stdout': result.stdout.decode(errors='replace'),
              'stderr': result.stderr.decode(errors='replace'),
              'stable': before == {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                  for path in WATCHED}, 'direct_inputs': before}
    (OUT / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k: record[k] for k in ['revision', 'group', 'checks', 'exit', 'stdout', 'stderr', 'stable']}), OUT, flush=True)
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr and record['stable'], OUT
