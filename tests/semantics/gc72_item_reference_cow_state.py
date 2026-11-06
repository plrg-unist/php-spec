#!/usr/bin/env python3
"""Source-reached reference COW: borrowed CELL, TEMP receipt and real edges."""
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc72_peer_repeated_reference_cow.php').read_text()
STAGE = (
    'S.TODO = (ACQUIRE_ARRAY z) :: ptask_tail* '
    '-- if S.NATIVEEXCESS = [HARRAY n_old] '
    '-- if S.BASE = BASE_DIM (BASE_VALUE (VARIABLE n_name* z_name)) (KNOWN (PINT 0)) z_key '
    '-- if n_name* = $ptascii("kept") '
    '-- if $lookup(S.ENV, n_name*) = (n_kept) '
    '-- if S.STORE[n_kept] = DEFINED (PARRAY n_old) '
    '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child)), '
    'ENTRY (KINT 1) (DIRECT (PINT 17)), ENTRY (KINT 2) (DIRECT (POBJECT n_child))] '
    '-- if $object_name(S, n_child) = $ptascii("GC72ChildPeer")')

DECLARATIONS = r'''syntax pgc72stage = BIND | WRITE29 | WRITE31 | UNSETREF | TRACE | CHILD
dec $gc72_at(pstate, pgc72stage, nat, nat) : bool
def $gc72_at(S, BIND, n_ref, n_child) = true
  -- if S.TODO = (REF_NAME n_name*) :: ptask_tail*
  -- if n_name* = $ptascii("ref") /\ S.CELL = n_ref
def $gc72_at(S, WRITE29, n_ref, n_child) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask_tail*
  -- if n_name* = $ptascii("ref") /\ S.RESULT = KNOWN (PINT 29)
def $gc72_at(S, WRITE31, n_ref, n_child) = true
  -- if S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail*
  -- if S.RESULT = KNOWN (PINT 31)
def $gc72_at(S, UNSETREF, n_ref, n_child) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text) metadata)) :: ptask_tail*
  -- if $base64(text) = $ptascii("ref")
def $gc72_at(S, TRACE, n_ref, n_child) = true
  -- if S.TODO = (GC_TRACE pgccall) :: ptask_tail*
def $gc72_at(S, CHILD, n_ref, n_child) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.STORE /\ pdestructorcall.OBJECT = n_child
def $gc72_at(S, pgc72stage, n_ref, n_child) = false -- otherwise
dec $gc72_seek(pstate, pgc72stage, nat, nat, nat) : pstate
def $gc72_seek(S, pgc72stage, n_ref, n_child, n) = S
  -- if $gc72_at(S, pgc72stage, n_ref, n_child)
def $gc72_seek(S, pgc72stage, n_ref, n_child, n) = $gc72_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc72stage, n_ref, n_child, $nabs($(n - 1)))
  -- if ~$gc72_at(S, pgc72stage, n_ref, n_child) -- if $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc72_seek(S, pgc72stage, n_ref, n_child, 0) = S
  -- if ~$gc72_at(S, pgc72stage, n_ref, n_child)
def $gc72_seek(S, pgc72stage, n_ref, n_child, n) = S
  -- if ~$gc72_at(S, pgc72stage, n_ref, n_child)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $gc72_op_view(pstate, pdestructionoperation) : pstate
def $gc72_op_view(S, pdestructionoperation_new) = S[.TODO = $destructor_operation_tasks(S.TODO, pdestructionoperation_old, pdestructionoperation_new)][.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]]
  -- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation_old]
dec $gc72_output(pevent*) : preqbytes
def $gc72_output(eps) = eps
def $gc72_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc72_output(pevent_tail*)
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture


def seek(before, after, stage):
    return [f'{after}_paused = $gc72_seek({before}, {stage}, n_ref, n_child, 4000)',
            f'{after}_paused.COMPLETION = NORMAL \\/ {after}_paused.COMPLETION = BUDGET',
            f'{after} = {after}_paused[.COMPLETION = NORMAL]',
            f'$gc72_at({after}, {stage}, n_ref, n_child)']


def valid(state):
    return [f'$heap_valid($heap_graph({state}))',
            f'$native_excess_valid({state})',
            f'$destruction_state_valid({state})',
            f'$call_descriptors_valid({state})']


def counts(state, physical, native, child):
    return [f'$heap_owners($heap_graph({state}), HARRAY n_old) = {physical}',
            f'$native_rc({state}, HARRAY n_old) = {native}',
            f'$heap_owners($heap_graph({state}), HOBJECT n_child) = {child}',
            f'$native_rc({state}, HOBJECT n_child) = {child}',
            f'$heap_count(HOBJECT n_child, {state}.NATIVEEXCESS) = 0']


def budget(state):
    return [f'$drive_steps({state}, 0) = {state}[.COMPLETION = BUDGET]',
            f'$drive_steps({state}, 2) = $drive_steps($drive_steps({state}, 1)[.COMPLETION = NORMAL], 1)']


def reject_op(name, patch):
    operation = f'pdestructionoperation_{name}'
    state = f'S_{name}'
    return [f'{operation} = pdestructionoperation_drop{patch}',
            f'{state} = $gc72_op_view(S_drop, {operation})',
            f'$heap_graph({state}) = $heap_graph(S_drop)',
            f'~$gc_operation_metadata_valid({state}, {operation})']


CHECKS = [
    'pentry_old* = S.ARRAYS[n_old].ITEMS',
    'n_new = |S.ARRAYS|', 'n_ref = |S.STORE|',
    '$lookup(S.ENV, $ptascii("watch")) = (n_watch_cell)',
    'S.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
    '$gc_array_reference_site(S, S.ORIGIN, ACQUIRE_ARRAY z) = ((S.BASE, n_kept))',
    'S.RESULT = KNOWN PNULL', *counts('S', 1, 2, 2), *valid('S'),
    'PhpStep: S ~> S_raw',
    'S_raw.ARRAYS = S.ARRAYS ++ [$array_insert(S.ARRAYS[n_old], KINT 0, ALIAS n_ref)]',
    'S_raw.STORE = $set_cell(S.STORE, n_kept, DEFINED (PARRAY n_new)) ++ [DEFINED (POBJECT n_child)]',
    'S_raw.REFCELLS = n_ref :: S.REFCELLS',
    'S_raw.NATIVEEXCESS = [HARRAY n_old]',
    'S_raw.RESULT = KNOWN PNULL', 'S_raw.BASE = BASE_VALUE (KNOWN PNULL)',
    'S_raw.CELL = n_ref', 'S_raw.KEY = KINT 0', 'S_raw.LOCATION = ELEMENT n_new (KINT 0)',
    '$heap_owners($heap_graph(S_raw), HARRAY n_new) = 1',
    '$heap_owners($heap_graph(S_raw), HCELL n_ref) = 1',
    '$heap_count(HARRAY n_new, S_raw.NATIVEEXCESS) = 0',
    '$heap_count(HCELL n_ref, S_raw.NATIVEEXCESS) = 0',
    '$node_children(S_raw, HCELL n_ref) = [HOBJECT n_child]',
    *counts('S_raw', 0, 1, 4),
    '$gc_array_reference_image(S_raw, n_old, n_new, n_kept, n_ref, KINT 0)',
    '$gc_operation_temporary_extra(S, S_raw, ACQUIRE_ARRAY z, [HARRAY n_old]) = [{OPERAND KNOWN (PARRAY n_old), PENDING true}]',
    '$gc_operation_temporary_extra(S, S_raw, ACQUIRE_ARRAY z, [HOBJECT n_child]) = eps',
    '$gc_operation_temporary_extra(S, S_raw, ACQUIRE_ARRAY z, [HARRAY n_old, HOBJECT n_child]) = eps',
    '$gc_operation_temporary_extra(S, S_raw, DISCARD, [HARRAY n_old]) = eps',
    '$gc_operation_temporary_extra(S[.BASE = BASE_VALUE (KNOWN PNULL)], S_raw, ACQUIRE_ARRAY z, [HARRAY n_old]) = eps',
    '$gc_operation_temporary_extra(S[.RESULT = KNOWN (PARRAY n_old)], S_raw, ACQUIRE_ARRAY z, [HARRAY n_old]) = eps',
    '$gc_operation_temporary_extra(S, S_raw[.RESULT = REFERENCE n_ref], ACQUIRE_ARRAY z, [HARRAY n_old]) = eps',
    '$gc_operation_temporary_extra(S, S_raw[.REFCELLS = S.REFCELLS], ACQUIRE_ARRAY z, [HARRAY n_old]) = eps',
    '$gc_operation_temporary_extra(S[.NATIVEEXCESS = eps], S_raw[.NATIVEEXCESS = eps], ACQUIRE_ARRAY z, [HARRAY n_old]) = eps',
    # Name each actual validator before any two-step budget evaluates TEMP pop.
    'S_drop = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_drop.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_drop) :: ptask_drop_tail*',
    'pdestructionrelease_drop.JOBS = [DESTRUCTION_TEMP (HARRAY n_old)]',
    'S_drop.DESTRUCTION.OPERATIONS = [pdestructionoperation_drop]',
    'pdestructionoperation_drop.SOURCE = ACQUIRE_ARRAY z',
    'pdestructionoperation_drop.ORIGIN = S.ORIGIN',
    'pdestructionoperation_drop.VALUE = KNOWN PNULL',
    'pdestructionoperation_drop.CELL = n_ref',
    'pdestructionoperation_drop.KEY = KINT 0',
    'pdestructionoperation_drop.LOCATION = ELEMENT n_new (KINT 0)',
    'pdestructionoperation_drop.NOGC = eps',
    'pdestructionoperation_drop.NOGCEXTRA = [pgctemporary_drop]',
    'pgctemporary_drop.OPERAND = KNOWN (PARRAY n_old)', 'pgctemporary_drop.PENDING',
    '$gc_operation_metadata_valid(S_drop, pdestructionoperation_drop)',
    '$gc_release_metadata_valid(S_drop, pdestructionrelease_drop)',
    *valid('S_drop'), *counts('S_drop', 1, 2, 4),
    '$heap_owners($heap_graph(S_drop), HCELL n_ref) = 1',
    '$gc_operation_jobs(pdestructionoperation_drop, [HARRAY n_old, HOBJECT n_child]) = [DESTRUCTION_TEMP (HARRAY n_old), DESTRUCTION_VALUE (HOBJECT n_child)]',
    *reject_op('bad_source', '[.SOURCE = DISCARD]'),
    *reject_op('bad_line', '[.SOURCE = ACQUIRE_ARRAY $(z + 1)]'),
    *reject_op('bad_origin', '[.ORIGIN = eps]'),
    *reject_op('bad_root_cell', '[.CELL = n_kept]'),
    *reject_op('bad_cell_bound', '[.CELL = |S_drop.STORE|]'),
    *reject_op('bad_key', '[.KEY = KINT 2]'),
    *reject_op('bad_location', '[.LOCATION = ELEMENT n_old (KINT 0)]'),
    *reject_op('wrong_header', '[.NOGCEXTRA = [pgctemporary_drop[.OPERAND = KNOWN (PARRAY n_new)]]]'),
    *reject_op('early_consumed', '[.NOGCEXTRA = [pgctemporary_drop[.PENDING = false]]]'),
    *reject_op('duplicate_receipt', '[.NOGCEXTRA = [pgctemporary_drop, pgctemporary_drop]]'),
    'pdestructionoperation_reference = pdestructionoperation_drop[.VALUE = REFERENCE n_ref]',
    'S_reference = $gc72_op_view(S_drop, pdestructionoperation_reference)',
    '$heap_owners($heap_graph(S_reference), HCELL n_ref) = 2',
    '$heap_owners($heap_graph(S_reference), HOBJECT n_child) = 4',
    '~$gc_operation_metadata_valid(S_reference, pdestructionoperation_reference)',
    'S_no_unit = S_drop[.NATIVEEXCESS = eps]',
    '~$gc_operation_metadata_valid(S_no_unit, pdestructionoperation_drop)',
    'S_new_unit = S_drop[.NATIVEEXCESS = [HARRAY n_old, HARRAY n_new]]',
    '~$gc_operation_metadata_valid(S_new_unit, pdestructionoperation_drop)',
    'S_cell_unit = S_drop[.NATIVEEXCESS = [HARRAY n_old, HCELL n_ref]]',
    '~$gc_operation_metadata_valid(S_cell_unit, pdestructionoperation_drop)',
    'S_wrong_payload = S_drop[.STORE = $set_cell(S_drop.STORE, n_ref, DEFINED (PINT 17))]',
    '~$gc_operation_metadata_valid(S_wrong_payload, pdestructionoperation_drop)',
    'S_wrong_cv = S_drop[.STORE = $set_cell(S_drop.STORE, n_kept, DEFINED (PARRAY n_old))]',
    '~$gc_operation_metadata_valid(S_wrong_cv, pdestructionoperation_drop)',
    'S_wrong_row = S_drop[.ARRAYS = $array_replace(S_drop.ARRAYS, n_new, $array_insert(S_drop.ARRAYS[n_new], KINT 0, DIRECT (POBJECT n_child)))]',
    '~$gc_operation_metadata_valid(S_wrong_row, pdestructionoperation_drop)',
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
    *counts('S_popped', 0, 1, 4),
    'S_popped.GC.BUFFER = S_drop.GC.BUFFER',
    'S_drop_next = $drive_steps(S_drop, 1)[.COMPLETION = NORMAL]',
    'S_drop_next.DESTRUCTION.OPERATIONS = [pdestructionoperation_consumed]',
    'S_drop_next.GC.BUFFER = S_drop.GC.BUFFER',
    *valid('S_drop_next'), *counts('S_drop_next', 0, 1, 4),
    # An existing buffer member must not conceal a forbidden fresh visit.
    'S_clear = S_drop[.GC = $gc_buffer_remove(S_drop.GC, HARRAY n_old)]',
    '$heap_graph(S_clear) = $heap_graph(S_drop)', '$gc_state_valid(S_clear)',
    '~((HARRAY n_old) <- $gc_nodes(S_clear.GC.BUFFER))',
    'S_clear_next = $drive_steps(S_clear, 1)[.COMPLETION = NORMAL]',
    'S_clear_next.GC.BUFFER = S_clear.GC.BUFFER',
    *budget('S'), *budget('S_drop'),
    *seek('S_drop_next', 'S_bind', 'BIND'),
    'S_bind.RESULT = KNOWN PNULL', 'S_bind.CELL = n_ref',
    '$heap_owners($heap_graph(S_bind), HCELL n_ref) = 1',
    'PhpStep: S_bind ~> S_bound_raw',
    'S_bound_raw.RESULT = REFERENCE n_ref',
    '$lookup(S_bound_raw.ENV, $ptascii("ref")) = (n_ref)',
    '$heap_owners($heap_graph(S_bound_raw), HCELL n_ref) = 3',
    '$node_children(S_bound_raw, HCELL n_ref) = [HOBJECT n_child]',
    '$heap_owners($heap_graph(S_bound_raw), HOBJECT n_child) = 4',
    'S_bound_next = $drive_steps(S_bind, 1)[.COMPLETION = NORMAL]',
    'S_bound_next.RESULT = REFERENCE n_ref',
    '$heap_owners($heap_graph(S_bound_next), HCELL n_ref) = 3',
    *seek('S_bound_next', 'S_write29', 'WRITE29'),
    '$heap_owners($heap_graph(S_write29), HCELL n_ref) = 2',
    '$node_children(S_write29, HCELL n_ref) = [HOBJECT n_child]',
    *counts('S_write29', 0, 1, 4),
    'PhpStep: S_write29 ~> S_written29',
    'S_written29.STORE[n_ref] = DEFINED (PINT 29)',
    'S_written29.ARRAYS[n_new] = S_write29.ARRAYS[n_new]',
    'S_written29.ARRAYS[n_old].ITEMS = pentry_old*',
    '$heap_owners($heap_graph(S_written29), HCELL n_ref) = 2',
    *counts('S_written29', 0, 1, 3),
    'S_write29_next = $drive_steps(S_write29, 1)[.COMPLETION = NORMAL]',
    'S_write29_next.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_child) :: ptask_child_drop_tail*',
    'pdestructionrelease_child.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child)]',
    '$heap_count(HOBJECT n_child, $eager_slots(S_write29, S_written29)) = 1',
    *seek('S_write29_next', 'S_write31', 'WRITE31'),
    *counts('S_write31', 0, 1, 3),
    'PhpStep: S_write31 ~> S_written31',
    'S_written31.ARRAYS[n_old].ITEMS = pentry_old*',
    'S_written31.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (ALIAS n_ref), ENTRY (KINT 1) (DIRECT (PINT 17)), ENTRY (KINT 2) (DIRECT (PINT 31))]',
    *counts('S_written31', 0, 1, 2),
    'S_write31_next = $drive_steps(S_write31, 1)[.COMPLETION = NORMAL]',
    'S_write31_next.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_direct) :: ptask_direct_tail*',
    'pdestructionrelease_direct.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child)]',
    *seek('S_write31_next', 'S_unset', 'UNSETREF'),
    '$heap_owners($heap_graph(S_unset), HCELL n_ref) = 2',
    'PhpStep: S_unset ~> S_unset_raw',
    '$heap_owners($heap_graph(S_unset_raw), HCELL n_ref) = 1',
    '(HCELL n_ref) <- S_unset_raw.ALLOCATIONS',
    'S_unset_next = $drive_steps(S_unset, 1)[.COMPLETION = NORMAL]',
    *seek('S_unset_next', 'S_trace', 'TRACE'),
    'S_trace.TODO = (GC_TRACE pgccall) :: ptask_trace_tail*',
    'S_trace.NATIVEEXCESS = [HARRAY n_old]',
    'S_trace.ARRAYS[n_old].ITEMS = pentry_old*',
    '~((HARRAY n_new) <- S_trace.ALLOCATIONS)',
    '~((HCELL n_ref) <- S_trace.ALLOCATIONS)',
    *counts('S_trace', 0, 1, 2), *valid('S_trace'),
    'H_trace = $gc_graph(S_trace)',
    '$heap_count(HARRAY n_old, H_trace.ROOTS) = 0',
    '$heap_count(HOBJECT n_child, H_trace.ROOTS) = 0',
    '$gc_native_white(H_trace, S_trace.NATIVEEXCESS, $gc_eligible_nodes(S_trace.GC.BUFFER)) = eps',
    'pgcplan = $gc_plan(S_trace, pgccall)',
    'pgcplan.DTORS = eps', 'pgcplan.FREESET = eps',
    'PhpStep: S_trace ~> S_plan',
    'S_plan.TODO = (GC_DTORS pgcplan) :: ptask_trace_tail*',
    '$gc_plan_valid(S_plan, pgcplan)',
    *seek('S_plan', 'S_child', 'CHILD'),
    'S_child.ARRAYS[n_old].ITEMS = pentry_old*',
    'S_child.NATIVEEXCESS = [HARRAY n_old]',
    '$weakref_get(S_child, n_watch) = POBJECT n_child',
    *counts('S_child', 0, 1, 4), *valid('S_child'),
    'S_done = $drive_steps(S_child, 4000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    'S_done.NATIVEEXCESS = [HARRAY n_old]',
    'S_done.ARRAYS[n_old].ITEMS = pentry_old*',
    '(HARRAY n_old) <- S_done.ALLOCATIONS', '(HOBJECT n_child) <- S_done.ALLOCATIONS',
    *counts('S_done', 0, 1, 2), *valid('S_done'),
    '$gc72_output(S_done.EVENTS) = $ptascii("O|B|1|gc72TargetPeer|1|A|1|1|R|29|1|W|31|1|C|29|1|U|1|G|0|1|E|S|1|D|")',
]

review.CASES = {'item-reference-cow-and-borrowed-cell': {
    'source': SOURCE, 'stage': STAGE, 'checks': CHECKS,
}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
