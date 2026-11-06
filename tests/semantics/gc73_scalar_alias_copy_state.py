#!/usr/bin/env python3
"""Genuine shared/singleton scalar-reference COW, receipts and physical edges."""
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SHARED_SOURCE = (ROOT / 'tests/semantics/gc73_peer_shared_alias_cow.php').read_text()
SINGLE_SOURCE = (ROOT / 'tests/semantics/gc73_singleton_alias_cow.php').read_text()
SHARED_STAGE = (
    'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
    '(ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_after_output* '
    '-- if pdestructionoperation.SOURCE = ENUM_IS_CALLABLE_CLEAR penumqueryoutput '
    '-- if S.STORE[penumqueryoutput.CELL] = DEFINED (PARRAY n_old) '
    '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (ALIAS n_alias), '
    'ENTRY (KINT 1) (DIRECT (PINT 17)), ENTRY (KINT 2) (ALIAS n_alias), '
    'ENTRY (KINT 3) (DIRECT (POBJECT n_child))] '
    '-- if $object_name(S, n_child) = $ptascii("GC73ChildPeer")')
SINGLE_STAGE = (
    'S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* '
    '-- if S.RESULT = KNOWN (PINT 23) '
    '-- if S.NATIVEEXCESS = [HARRAY n_old] '
    '-- if $lookup(S.ENV, $ptascii("kept")) = (n_kept) '
    '-- if S.STORE[n_kept] = DEFINED (PARRAY n_old) '
    '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (ALIAS n_alias), '
    'ENTRY (KINT 1) (DIRECT (POBJECT n_child))] '
    '-- if $object_name(S, n_child) = $ptascii("SingletonAliasChild73")')

DECLARATIONS = r'''syntax pgc73stage = COW | TRACE | CHILD
dec $gc73_at(pstate, pgc73stage, nat) : bool
def $gc73_at(S, COW, n_child) = true
  -- if S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail*
  -- if S.RESULT = KNOWN (PINT 23)
def $gc73_at(S, TRACE, n_child) = true
  -- if S.TODO = (GC_TRACE pgccall) :: ptask_tail*
def $gc73_at(S, CHILD, n_child) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.STORE /\ pdestructorcall.OBJECT = n_child
def $gc73_at(S, pgc73stage, n_child) = false -- otherwise
dec $gc73_seek(pstate, pgc73stage, nat, nat) : pstate
def $gc73_seek(S, pgc73stage, n_child, n) = S
  -- if $gc73_at(S, pgc73stage, n_child)
def $gc73_seek(S, pgc73stage, n_child, n) = $gc73_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc73stage, n_child, $nabs($(n - 1)))
  -- if ~$gc73_at(S, pgc73stage, n_child) -- if $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc73_seek(S, pgc73stage, n_child, 0) = S
  -- if ~$gc73_at(S, pgc73stage, n_child)
def $gc73_seek(S, pgc73stage, n_child, n) = S
  -- if ~$gc73_at(S, pgc73stage, n_child)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $gc73_op_view(pstate, pdestructionoperation) : pstate
def $gc73_op_view(S, pdestructionoperation_new) = S[.TODO = $destructor_operation_tasks(S.TODO, pdestructionoperation_old, pdestructionoperation_new)][.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]]
  -- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation_old]
dec $gc73_output(pevent*) : preqbytes
def $gc73_output(eps) = eps
def $gc73_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc73_output(pevent_tail*)
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture


def seek(before, after, stage):
    return [f'{after}_paused = $gc73_seek({before}, {stage}, n_child, 4000)',
            f'{after}_paused.COMPLETION = NORMAL \\/ {after}_paused.COMPLETION = BUDGET',
            f'{after} = {after}_paused[.COMPLETION = NORMAL]',
            f'$gc73_at({after}, {stage}, n_child)']


def valid(state):
    return [f'$heap_valid($heap_graph({state}))',
            f'$native_excess_valid({state})',
            f'$destruction_state_valid({state})',
            f'$call_descriptors_valid({state})']


def counts(state, physical, native, alias, child):
    return [f'$heap_owners($heap_graph({state}), HARRAY n_old) = {physical}',
            f'$native_rc({state}, HARRAY n_old) = {native}',
            f'$heap_owners($heap_graph({state}), HCELL n_alias) = {alias}',
            f'$native_rc({state}, HCELL n_alias) = {alias}',
            f'$heap_owners($heap_graph({state}), HOBJECT n_child) = {child}',
            f'$native_rc({state}, HOBJECT n_child) = {child}']


def budget(state):
    return [f'$drive_steps({state}, 0) = {state}[.COMPLETION = BUDGET]',
            f'$drive_steps({state}, 2) = $drive_steps($drive_steps({state}, 1)[.COMPLETION = NORMAL], 1)']


def reject_op(name, patch):
    operation = f'pdestructionoperation_{name}'
    state = f'S_{name}'
    return [f'{operation} = pdestructionoperation_drop{patch}',
            f'{state} = $gc73_op_view(S_drop, {operation})',
            f'$heap_graph({state}) = $heap_graph(S_drop)',
            f'~$gc_operation_metadata_valid({state}, {operation})']


SHARED = [
    '$lookup(S.ENV, $ptascii("kept")) = (n_kept)',
    '$lookup(S.ENV, $ptascii("slot")) = (n_alias)',
    '$lookup(S.ENV, $ptascii("watch")) = (n_watch_cell)',
    'S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
    'S.STORE[n_alias] = DEFINED (PINT 17)', 'n_alias =/= n_kept',
    'pentry_old* = S.ARRAYS[n_old].ITEMS',
    'S.NATIVEEXCESS = eps', *counts('S', 2, 2, 3, 1), *valid('S'),
    # The actual completed clear authenticates the new raw-NAME data fold.
    'PhpStep: S ~> S_raw',
    'S_raw.NATIVEEXCESS = [HARRAY n_old]',
    'S_raw.ARRAYS = S.ARRAYS', 'S_raw.STORE[n_alias] = DEFINED (PINT 17)',
    'S_raw.TODO = ptask_after_output*',
    *counts('S_raw', 1, 2, 3, 1),
    'S_emit = S_raw[.STORE = S.STORE][.NATIVEEXCESS = eps][.TODO = (ENUM_IS_CALLABLE_OUTPUT penumqueryoutput) :: ptask_after_output*]',
    '$enum_is_callable_array_excess_ready(S_emit, penumqueryoutput)',
    '$gc_array_alias_row(S_emit, pentry_old*)',
    '$enum_is_callable_output_commit(S_emit, penumqueryoutput) = S_raw',
    '$enum_is_callable_member_snapshot(S_emit, ALIAS n_alias, PNULL)',
    '~$gc_array_alias_row(S_emit, [ENTRY (KINT 0) (DIRECT (PINT 17))])',
    'S_leaf_unit = S_emit[.NATIVEEXCESS = [HCELL n_alias]]',
    '~$enum_is_callable_array_excess_ready(S_leaf_unit, penumqueryoutput)',
    'S_owning_leaf = S_emit[.STORE = $set_cell(S_emit.STORE, n_alias, DEFINED (POBJECT n_child))]',
    '~$enum_is_callable_array_excess_ready(S_owning_leaf, penumqueryoutput)',
    'n_bad_cell = |S_emit.STORE|',
    '~$gc_array_alias_row(S_emit, [ENTRY (KINT 0) (ALIAS n_bad_cell)])',
    'S_after = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    *seek('S_after', 'S_cow', 'COW'),
    'S_cow.TODO = (ASSIGN_ARRAY pbase_cow z_cow false) :: ptask_cow_tail*',
    'S_cow.STORE[n_kept] = DEFINED (PARRAY n_old)',
    'S_cow.STORE[n_alias] = DEFINED (PINT 17)',
    *counts('S_cow', 1, 2, 3, 1), *valid('S_cow'),
    '$duplicate_item(S_cow, n_old, ALIAS n_alias) = ALIAS n_alias',
    '$duplicate_entries(S_cow, n_old, pentry_old*) = pentry_old*',
    'n_new = |S_cow.ARRAYS|',
    'PhpStep: S_cow ~> S_copied',
    'S_copied.ARRAYS = S_cow.ARRAYS ++ [S_cow.ARRAYS[n_old]]',
    'S_copied.STORE = $set_cell($set_cell(S_cow.STORE, n_kept, DEFINED (PARRAY n_new)), n_alias, DEFINED (PINT 23))',
    'S_copied.NATIVEEXCESS = [HARRAY n_old]',
    'S_copied.REFCELLS = S_cow.REFCELLS',
    '$node_children(S_copied, HCELL n_alias) = eps',
    '$node_children(S_copied, HARRAY n_old) = [HCELL n_alias, HCELL n_alias, HOBJECT n_child]',
    '$node_children(S_copied, HARRAY n_new) = [HCELL n_alias, HCELL n_alias, HOBJECT n_child]',
    '$heap_owners($heap_graph(S_copied), HARRAY n_new) = 1',
    *counts('S_copied', 0, 1, 5, 2),
    '$gc_operation_temporary_extra(S_cow, S_copied, ASSIGN_ARRAY pbase_cow z_cow false, [HARRAY n_old]) = [{OPERAND KNOWN (PARRAY n_old), PENDING true}]',
    '$gc_operation_temporary_extra(S_cow, S_copied, ASSIGN_ARRAY pbase_cow z_cow false, [HARRAY n_old, HCELL n_alias]) = eps',
    'S_no_store_write = S_copied[.STORE = $set_cell(S_copied.STORE, n_alias, DEFINED (PINT 17))]',
    '$gc_operation_temporary_extra(S_cow, S_no_store_write, ASSIGN_ARRAY pbase_cow z_cow false, [HARRAY n_old]) = eps',
    # Explicit actual validators precede any two-step budget or TEMP pop.
    'S_drop = $drive_steps(S_cow, 1)[.COMPLETION = NORMAL]',
    'S_drop.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_drop) :: ptask_drop_tail*',
    'pdestructionrelease_drop.JOBS = [DESTRUCTION_TEMP (HARRAY n_old)]',
    'S_drop.DESTRUCTION.OPERATIONS = [pdestructionoperation_drop]',
    'pdestructionoperation_drop.SOURCE = ASSIGN_ARRAY pbase_cow z_cow false',
    'pdestructionoperation_drop.VALUE = KNOWN (PINT 23)',
    'pdestructionoperation_drop.CELL = n_kept',
    'pdestructionoperation_drop.KEY = KINT 0',
    'pdestructionoperation_drop.LOCATION = ELEMENT n_new (KINT 0)',
    'pdestructionoperation_drop.NOGC = eps',
    'pdestructionoperation_drop.NOGCEXTRA = [pgctemporary_drop]',
    'pgctemporary_drop.OPERAND = KNOWN (PARRAY n_old)', 'pgctemporary_drop.PENDING',
    '$gc_operation_metadata_valid(S_drop, pdestructionoperation_drop)',
    '$gc_release_metadata_valid(S_drop, pdestructionrelease_drop)',
    *valid('S_drop'), *counts('S_drop', 1, 2, 5, 2),
    *reject_op('bad_source', '[.SOURCE = DISCARD]'),
    *reject_op('bad_origin', '[.ORIGIN = eps]'),
    *reject_op('bad_cell', '[.CELL = n_alias]'),
    *reject_op('bad_key', '[.KEY = KINT 2]'),
    *reject_op('bad_location', '[.LOCATION = ELEMENT n_old (KINT 0)]'),
    *reject_op('bad_payload', '[.VALUE = KNOWN (PINT 29)]'),
    *reject_op('wrong_header', '[.NOGCEXTRA = [pgctemporary_drop[.OPERAND = KNOWN (PARRAY n_new)]]]'),
    *reject_op('early_consumed', '[.NOGCEXTRA = [pgctemporary_drop[.PENDING = false]]]'),
    *reject_op('duplicate_receipt', '[.NOGCEXTRA = [pgctemporary_drop, pgctemporary_drop]]'),
    'S_old_payload = S_drop[.STORE = $set_cell(S_drop.STORE, n_alias, DEFINED (PINT 17))]',
    '$heap_graph(S_old_payload) = $heap_graph(S_drop)',
    '~$gc_operation_metadata_valid(S_old_payload, pdestructionoperation_drop)',
    'S_new_direct = S_drop[.ARRAYS = $array_replace(S_drop.ARRAYS, n_new, $array_insert(S_drop.ARRAYS[n_new], KINT 0, DIRECT (PINT 23)))]',
    '~$gc_operation_metadata_valid(S_new_direct, pdestructionoperation_drop)',
    'S_no_unit = S_drop[.NATIVEEXCESS = eps]',
    '~$gc_operation_metadata_valid(S_no_unit, pdestructionoperation_drop)',
    'S_new_unit = S_drop[.NATIVEEXCESS = [HARRAY n_old, HARRAY n_new]]',
    '~$gc_operation_metadata_valid(S_new_unit, pdestructionoperation_drop)',
    'S_alias_unit = S_drop[.NATIVEEXCESS = [HARRAY n_old, HCELL n_alias]]',
    '~$gc_operation_metadata_valid(S_alias_unit, pdestructionoperation_drop)',
    'pdestructionrelease_value = pdestructionrelease_drop[.JOBS = [DESTRUCTION_VALUE (HARRAY n_old)]]',
    'S_value = S_drop[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_value) :: ptask_drop_tail*][.DESTRUCTION.RELEASES = [pdestructionrelease_value]]',
    '$heap_graph(S_value) = $heap_graph(S_drop)',
    '~$gc_operation_metadata_valid(S_value, pdestructionoperation_drop)',
    '~$gc_release_metadata_valid(S_value, pdestructionrelease_value)',
    'PhpStep: S_drop ~> S_popped',
    'S_popped.ARRAYS = S_drop.ARRAYS', 'S_popped.STORE = S_drop.STORE',
    'S_popped.DESTRUCTION.OPERATIONS = [pdestructionoperation_consumed]',
    'pdestructionoperation_consumed = pdestructionoperation_drop[.NOGCEXTRA = [pgctemporary_drop[.PENDING = false]]]',
    '$gc_operation_metadata_valid(S_popped, pdestructionoperation_consumed)',
    *counts('S_popped', 0, 1, 5, 2),
    'S_drop_next = $drive_steps(S_drop, 1)[.COMPLETION = NORMAL]',
    'S_drop_next.GC.BUFFER = S_drop.GC.BUFFER',
    *valid('S_drop_next'),
    'S_clear = S_drop[.GC = $gc_buffer_remove(S_drop.GC, HARRAY n_old)]',
    '$gc_state_valid(S_clear)',
    'S_clear_next = $drive_steps(S_clear, 1)[.COMPLETION = NORMAL]',
    'S_clear_next.GC.BUFFER = S_clear.GC.BUFFER',
    *budget('S_cow'), *budget('S_drop'),
    *seek('S_drop_next', 'S_trace', 'TRACE'),
    'S_trace.TODO = (GC_TRACE pgccall) :: ptask_trace_tail*',
    'S_trace.ARRAYS[n_old].ITEMS = pentry_old*',
    'S_trace.STORE[n_alias] = DEFINED (PINT 23)',
    '~((HARRAY n_new) <- S_trace.ALLOCATIONS)',
    '(HCELL n_alias) <- S_trace.ALLOCATIONS',
    'S_trace.NATIVEEXCESS = [HARRAY n_old]',
    *counts('S_trace', 0, 1, 2, 1), *valid('S_trace'),
    'H_trace = $gc_graph(S_trace)',
    '$heap_count(HARRAY n_old, H_trace.ROOTS) = 0',
    '$heap_count(HCELL n_alias, H_trace.ROOTS) = 0',
    '$gc_native_white(H_trace, S_trace.NATIVEEXCESS, $gc_eligible_nodes(S_trace.GC.BUFFER)) = eps',
    'pgcplan = $gc_plan(S_trace, pgccall)',
    'pgcplan.DTORS = eps', 'pgcplan.FREESET = eps',
    'PhpStep: S_trace ~> S_plan',
    '$gc_plan_valid(S_plan, pgcplan)',
    *seek('S_plan', 'S_child', 'CHILD'),
    'S_child.STORE[n_alias] = DEFINED (PINT 23)',
    '$weakref_get(S_child, n_watch) = POBJECT n_child',
    *counts('S_child', 0, 1, 2, 3), *valid('S_child'),
    'S_done = $drive_steps(S_child, 4000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    'S_done.NATIVEEXCESS = [HARRAY n_old]',
    'S_done.ARRAYS[n_old].ITEMS = pentry_old*',
    'S_done.STORE[n_alias] = DEFINED (PINT 23)',
    '(HARRAY n_old) <- S_done.ALLOCATIONS', '(HCELL n_alias) <- S_done.ALLOCATIONS',
    *counts('S_done', 0, 1, 2, 1), *valid('S_done'),
    '$gc73_output(S_done.EVENTS) = $ptascii("O|B|1|gc73TargetPeer|17|1|W|23|23|23|1|U|1|G|0|1|E|S|1|D|")',
]

SINGLETON = [
    'pentry_old* = S.ARRAYS[n_old].ITEMS',
    'S.STORE[n_alias] = DEFINED (PINT 17)',
    '$lookup(S.ENV, $ptascii("slot")) = eps',
    '$gc_array_alias_row(S, pentry_old*)',
    *counts('S', 1, 2, 1, 1), *valid('S'),
    '$duplicate_item(S, n_old, ALIAS n_alias) = DIRECT (PINT 17)',
    'pentry_copy* = [ENTRY (KINT 0) (DIRECT (PINT 17)), ENTRY (KINT 1) (DIRECT (POBJECT n_child))]',
    '$duplicate_entries(S, n_old, pentry_old*) = pentry_copy*',
    'n_new = |S.ARRAYS|',
    'PhpStep: S ~> S_raw',
    'S_raw.ARRAYS[n_old] = S.ARRAYS[n_old]',
    'S_raw.ARRAYS[n_new] = $array_insert(S.ARRAYS[n_old][.ITEMS = pentry_copy*], KINT 0, DIRECT (PINT 23))',
    'S_raw.STORE = $set_cell(S.STORE, n_kept, DEFINED (PARRAY n_new))',
    'S_raw.STORE[n_alias] = DEFINED (PINT 17)',
    'S_raw.REFCELLS = S.REFCELLS', 'S_raw.NATIVEEXCESS = [HARRAY n_old]',
    *counts('S_raw', 0, 1, 1, 2),
    '$gc_operation_temporary_extra(S, S_raw, ASSIGN_ARRAY pbase z false, [HARRAY n_old]) = [{OPERAND KNOWN (PARRAY n_old), PENDING true}]',
    'S_drop = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_drop.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_drop) :: ptask_drop_tail*',
    'pdestructionrelease_drop.JOBS = [DESTRUCTION_TEMP (HARRAY n_old)]',
    'S_drop.DESTRUCTION.OPERATIONS = [pdestructionoperation_drop]',
    '$gc_operation_metadata_valid(S_drop, pdestructionoperation_drop)',
    '$gc_release_metadata_valid(S_drop, pdestructionrelease_drop)',
    *valid('S_drop'),
    'S_clear = S_drop[.GC = $gc_buffer_remove(S_drop.GC, HARRAY n_old)]',
    '$gc_state_valid(S_clear)',
    'S_next = $drive_steps(S_clear, 1)[.COMPLETION = NORMAL]',
    'S_next.GC.BUFFER = S_clear.GC.BUFFER',
    'S_next.STORE[n_alias] = DEFINED (PINT 17)',
    'S_next.ARRAYS[n_old] = S.ARRAYS[n_old]',
    *counts('S_next', 0, 1, 1, 2), *valid('S_next'),
    *budget('S'), *budget('S_drop'),
    # The original supplies the normal singleton full ending; this facet stops
    # at the actual clone/receipt boundary rather than driving it a second time.
]

review.CASES = {
    'shared-scalar-cell-copy-write-and-lifetime': {
        'source': SHARED_SOURCE, 'stage': SHARED_STAGE, 'checks': SHARED,
    },
    'singleton-scalar-cell-copy-and-receipt': {
        'source': SINGLE_SOURCE, 'stage': SINGLE_STAGE, 'checks': SINGLETON,
    },
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
