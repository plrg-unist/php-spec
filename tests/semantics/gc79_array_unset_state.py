#!/usr/bin/env python3
"""Copied item deletion: header TEMP, reference redirect and real VALUE loss."""
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
SINGLETON = (ROOT / 'tests/semantics/gc79_singleton_alias_unset.php').read_text()
SHARED = (ROOT / 'tests/semantics/gc79_shared_alias_unset.php').read_text()
DECLARATIONS = r'''syntax pgc79phase = SECOND | WRITE
dec $gc79_at(pstate, pgc79phase) : bool
def $gc79_at(S, SECOND) = true
  -- if S.TODO = UNSET_ARRAY :: ptask_tail*
  -- if S.BASE = BASE_DIM (BASE_VALUE (VARIABLE n_name* z_name)) (KNOWN (PINT 2)) z_key
  -- if n_name* = $ptascii("kept")
def $gc79_at(S, WRITE) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask_tail*
  -- if n_name* = $ptascii("slot") /\ S.RESULT = KNOWN (PINT 23)
def $gc79_at(S, pgc79phase) = false -- otherwise
dec $gc79_seek(pstate, pgc79phase, nat) : pstate
def $gc79_seek(S, pgc79phase, n) = S -- if $gc79_at(S, pgc79phase)
def $gc79_seek(S, pgc79phase, n) = $gc79_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc79phase, $nabs($(n - 1)))
  -- if ~$gc79_at(S, pgc79phase) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc79_seek(S, pgc79phase, 0) = S -- if ~$gc79_at(S, pgc79phase)
def $gc79_seek(S, pgc79phase, n) = S
  -- if ~$gc79_at(S, pgc79phase)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $gc79_op(pstate, pdestructionoperation) : pstate
def $gc79_op(S, pdestructionoperation_new) = S[.TODO = $destructor_operation_tasks(S.TODO, pdestructionoperation_old, pdestructionoperation_new)][.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]]
  -- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation_old]
dec $gc79_output(pevent*) : preqbytes
def $gc79_output(eps) = eps
def $gc79_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc79_output(pevent_tail*)
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture


def valid(state):
    return [f'$heap_valid($heap_graph({state}))',
            f'$native_excess_valid({state})', f'$gc_state_valid({state})',
            f'$destruction_state_valid({state})', f'$call_descriptors_valid({state})']


def header(state, physical, native):
    return [f'$heap_owners($heap_graph({state}), HARRAY n_old) = {physical}',
            f'$native_rc({state}, HARRAY n_old) = {native}']


def budget(state):
    return [f'$drive_steps({state}, 0) = {state}[.COMPLETION = BUDGET]',
            f'$drive_steps({state}, 2) = $drive_steps($drive_steps({state}, 1)[.COMPLETION = NORMAL], 1)']


def seek(before, after, phase):
    return [f'{after}_pause = $gc79_seek({before}, {phase}, 3000)',
            f'{after} = {after}_pause[.COMPLETION = NORMAL]',
            f'$gc79_at({after}, {phase})']


COMMON_STAGE = (
    'S.TODO = UNSET_ARRAY :: ptask_tail* '
    '-- if S.BASE = BASE_DIM (BASE_VALUE (VARIABLE n_name* z_name)) (KNOWN (PINT 0)) z_key '
    '-- if n_name* = $ptascii("kept") '
    '-- if $lookup(S.ENV, n_name*) = (n_root) '
    '-- if $lookup(S.ENV, $ptascii("view")) = (n_view) '
    '-- if S.STORE[n_root] = DEFINED (PARRAY n_old) '
    '-- if S.STORE[n_view] = DEFINED (PARRAY n_old) '
    '-- if S.NATIVEEXCESS = [HARRAY n_old] ')
SINGLE_STAGE = COMMON_STAGE + (
    '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) (DIRECT (PINT 17))] '
    '-- if S.STORE[n_leaf] = DEFINED (POBJECT n_child)')
SHARED_STAGE = COMMON_STAGE + (
    '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) (DIRECT (PINT 17)), ENTRY (KINT 2) (ALIAS n_leaf)] '
    '-- if S.STORE[n_leaf] = DEFINED (POBJECT n_child)')


def cow_checks(item, cell_before, cell_after):
    return [
        *valid('S'), *header('S', 2, 3),
        '~((HARRAY n_old) <- $gc_nodes(S.GC.BUFFER))',
        '~((HOBJECT n_child) <- $gc_nodes(S.GC.BUFFER))',
        f'$heap_owners($heap_graph(S), HCELL n_leaf) = {cell_before}',
        '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
        'n_new = |S.ARRAYS|', 'n_scratch = S.CELL', 'n_scratch =/= n_root',
        '$gc_array_unset_site(S, S.ORIGIN) = ((S.BASE, n_root))',
        'parray_copy = $gc_array_alias_copy(S, n_old)',
        f'$entry_lookup(parray_copy.ITEMS, KINT 0) = ({item})',
        'parray_written = parray_copy[.ITEMS = $entry_delete(parray_copy.ITEMS, KINT 0)][.POSITIONS = $position_delete(parray_copy.POSITIONS, KINT 0)]',
        'PhpStep: S ~> S_raw',
        'S_raw.ARRAYS = S.ARRAYS ++ [parray_written]',
        'S_raw.STORE = $set_cell(S.STORE, n_root, DEFINED (PARRAY n_new))',
        'S_raw.CELL = n_scratch', 'S_raw.LOCATION = ROOT n_root', 'S_raw.KEY = KINT 0',
        'S_raw.RESULT = KNOWN PNULL', 'S_raw.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_raw.NATIVEEXCESS = S.NATIVEEXCESS', 'S_raw.REFCELLS = S.REFCELLS',
        '$entry_lookup(S_raw.ARRAYS[n_new].ITEMS, KINT 0) = eps',
        'S_raw.ARRAYS[n_old] = S.ARRAYS[n_old]',
        '$gc_array_unset_transition(S, S_raw) = ((n_old, n_new, n_root, KINT 0, parray_copy))',
        '$gc_array_unset_image(S_raw, n_old, n_new, n_root, KINT 0)',
        *header('S_raw', 1, 2),
        f'$heap_owners($heap_graph(S_raw), HCELL n_leaf) = {cell_after}',
        '$heap_owners($heap_graph(S_raw), HOBJECT n_child) = 1',
        f'$gc_array_unset_decrements(S, S_raw) = $item_nodes({item})',
        'pgctemporary_live = {OPERAND KNOWN (PARRAY n_old), PENDING true}',
        'pgctemporary_done = pgctemporary_live[.PENDING = false]',
        '$gc_operation_temporary_extra(S, S_raw, UNSET_ARRAY, [HARRAY n_old]) = [pgctemporary_live]',
        '$gc_operation_temporary_extra(S, S_raw, DISCARD, [HARRAY n_old]) = eps',
        '$gc_operation_temporary_extra(S, S_raw[.CELL = n_root], UNSET_ARRAY, [HARRAY n_old]) = eps',
        '$gc_array_unset_transition(S, S_raw[.LOCATION = ROOT n_view]) = eps',
        '$gc_array_unset_transition(S, S_raw[.KEY = KINT 1]) = eps',
        '$gc_array_unset_transition(S, S_raw[.OBJECTS = eps]) = eps',
        'S_live = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
        'S_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_live) :: ptask_live_tail*',
        'pdestructionrelease_live.JOBS = [DESTRUCTION_TEMP (HARRAY n_old)]',
        'S_live.DESTRUCTION.OPERATIONS = [pdestructionoperation_live]',
        'pdestructionoperation_live.SOURCE = UNSET_ARRAY',
        'pdestructionoperation_live.CELL = n_scratch',
        'pdestructionoperation_live.LOCATION = ROOT n_root',
        'pdestructionoperation_live.NOGCEXTRA = [pgctemporary_live]',
        '$gc_operation_metadata_valid(S_live, pdestructionoperation_live)',
        '$gc_release_metadata_valid(S_live, pdestructionrelease_live)',
        *valid('S_live'), *header('S_live', 2, 3),
        f'$gc_same_location(S, S_live) = $item_nodes({item})',
        '(HOBJECT n_child) <- $gc_nodes(S_live.GC.BUFFER)',
        '~((HARRAY n_old) <- $gc_nodes(S_live.GC.BUFFER))',
        f'$heap_owners($heap_graph(S_live), HCELL n_leaf) = {cell_after}',
        '$heap_owners($heap_graph(S_live), HOBJECT n_child) = 1',
        'S_after = $drive_steps(S_live, 1)[.COMPLETION = NORMAL]',
        'pdestructionoperation_done = pdestructionoperation_live[.NOGCEXTRA = [pgctemporary_done]]',
        'S_after.DESTRUCTION.OPERATIONS = [pdestructionoperation_done]',
        '$gc_operation_metadata_valid(S_after, pdestructionoperation_done)',
        *header('S_after', 1, 2), *valid('S_after'),
        '~((HARRAY n_old) <- $gc_nodes(S_after.GC.BUFFER))',
        '$heap_owners($heap_graph(S_after), HOBJECT n_child) = 1',
        'S_after.DESTRUCTION.CALLS = eps',
        *budget('S'), *budget('S_live'),
    ]


SINGLE_CHECKS = cow_checks('DIRECT (POBJECT n_child)', 1, 1)
SHARED_CHECKS = cow_checks('ALIAS n_leaf', 3, 4)
for name, patch in {
    'scratch': '[.CELL = n_root]',
    'location': '[.LOCATION = ROOT n_view]',
    'key': '[.KEY = KINT 2]',
    'source': '[.SOURCE = DISCARD]',
    'early_done': '[.NOGCEXTRA = [pgctemporary_done]]',
    'operand': '[.NOGCEXTRA = [pgctemporary_live[.OPERAND = KNOWN (PARRAY n_new)]]]',
}.items():
    SHARED_CHECKS += [f'pdestructionoperation_bad_{name} = pdestructionoperation_live{patch}',
                      f'S_bad_{name} = $gc79_op(S_live, pdestructionoperation_bad_{name})',
                      f'$heap_graph(S_bad_{name}) = $heap_graph(S_live)',
                      f'~$gc_operation_metadata_valid(S_bad_{name}, pdestructionoperation_bad_{name})']
SHARED_CHECKS += [
    'S.ORIGIN = (PORIGIN n_unit pcpath_site)',
    'PCINDEX n_index = pcpath_site[0]',
    'porigin_other = PORIGIN n_unit ([PCINDEX $(n_index + 1), PCFIELD 0, PCINDEX 1, PCFIELD 0, PCFIELD 0, PCINDEX 0])',
    '$origin_node(S.SOURCES, porigin_other) = (NExprArrayDimFetch expression_base_other phpType5_other metadata_other)',
    'expression_other = NExprArrayDimFetch expression_base_other phpType5_other metadata_other',
    'z_other = $runtime_line(S[.ORIGIN = (porigin_other)], eps, expression_other)',
    'S_other_source = S[.ORIGIN = (porigin_other)]',
    '$gc_array_reference_site(S_other_source, (porigin_other), ACQUIRE_ARRAY z_other) = ((pbase_other, n_root))',
    '$gc_array_unset_site(S_other_source, (porigin_other)) = eps',
    'pdestructionoperation_other = pdestructionoperation_live[.ORIGIN = (porigin_other)]',
    'S_other_op = $gc79_op(S_live, pdestructionoperation_other)[.ORIGIN = (porigin_other)]',
    '~$gc_operation_metadata_valid(S_other_op, pdestructionoperation_other)',
    # Missing-key deletion still separates, but has no copied item decrement.
    'S_missing = S[.ARRAYS = $array_replace(S.ARRAYS, n_old, S.ARRAYS[n_old][.ITEMS = $entry_delete(S.ARRAYS[n_old].ITEMS, KINT 0)][.POSITIONS = $position_delete(S.ARRAYS[n_old].POSITIONS, KINT 0)])]',
    *valid('S_missing'),
    'PhpStep: S_missing ~> S_missing_raw',
    '$gc_array_unset_decrements(S_missing, S_missing_raw) = eps',
    '$gc_operation_temporary_extra(S_missing, S_missing_raw, UNSET_ARRAY, [HARRAY n_old]) = [pgctemporary_live]',
    'S_missing_live = $drive_steps(S_missing, 1)[.COMPLETION = NORMAL]',
    '~((HOBJECT n_child) <- $gc_nodes(S_missing_live.GC.BUFFER))',
    '~((HARRAY n_old) <- $gc_nodes(S_missing_live.GC.BUFFER))',
    *seek('S_after', 'S_second', 'SECOND'),
    '$heap_owners($heap_graph(S_second), HCELL n_leaf) = 4',
    'PhpStep: S_second ~> S_second_raw',
    'S_second_raw.ARRAYS[n_old] = S.ARRAYS[n_old]',
    '$heap_owners($heap_graph(S_second_raw), HCELL n_leaf) = 3',
    '$gc_array_unset_transition(S_second, S_second_raw) = eps',
    '$gc_array_unset_decrements(S_second, S_second_raw) = eps',
    '~((HARRAY n_new) <- $gc_nodes(S_second_raw.GC.BUFFER))',
    'S_second_cache = S_second[.CELL = n_scratch]',
    '$heap_graph(S_second_cache) = $heap_graph(S_second)',
    *valid('S_second_cache'),
    'PhpStep: S_second_cache ~> S_second_cache_raw',
    '~((HARRAY n_new) <- $gc_nodes(S_second_cache_raw.GC.BUFFER))',
    # Remove only an already-buffered target to observe this real decrement.
    'S_second_clear = S_second[.GC = $gc_buffer_remove(S_second.GC, HOBJECT n_child)]',
    *valid('S_second_clear'),
    'S_value_live = $drive_steps(S_second_clear, 1)[.COMPLETION = NORMAL]',
    'S_value_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_cell) :: ptask_value_tail*',
    'pdestructionrelease_cell.JOBS = [DESTRUCTION_VALUE (HCELL n_leaf)]',
    '$heap_owners($heap_graph(S_value_live), HCELL n_leaf) = 4',
    'S_value_after = $drive_steps(S_value_live, 1)[.COMPLETION = NORMAL]',
    '$heap_owners($heap_graph(S_value_after), HCELL n_leaf) = 3',
    '$heap_owners($heap_graph(S_value_after), HOBJECT n_child) = 1',
    '(HOBJECT n_child) <- $gc_nodes(S_value_after.GC.BUFFER)',
    '~((HARRAY n_new) <- $gc_nodes(S_value_after.GC.BUFFER))',
    *valid('S_value_after'), *budget('S_value_live'),
    *seek('S_value_after', 'S_write', 'WRITE'),
    'PhpStep: S_write ~> S_write_raw',
    'S_write_raw.STORE[n_leaf] = DEFINED (PINT 23)',
    '$heap_owners($heap_graph(S_write_raw), HOBJECT n_child) = 0',
    'S_child_live = $drive_steps(S_write, 1)[.COMPLETION = NORMAL]',
    'S_child_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_child) :: ptask_child_tail*',
    'pdestructionrelease_child.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child)]',
    'S_done = $drive_steps(S_child_live, 4000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    'n_child <- S_done.DESTRUCTION.CALLED',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    'S_done.NATIVEEXCESS = [HARRAY n_old]',
    '$gc79_output(S_done.EVENTS) = $ptascii("B|O|N|1|gc79AvailablePeer|Q|0|C|0|1|17|R|0|1|D|W|23|23|23|U|G|0|E|S|")',
    *valid('S_done'),
]

review.CASES = {
    'singleton-unwrap-copied-child-delete': {'source': SINGLETON, 'stage': SINGLE_STAGE, 'checks': SINGLE_CHECKS},
    'shared-cell-copy-delete-and-real-value': {'source': SHARED, 'stage': SHARED_STAGE, 'checks': SHARED_CHECKS},
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
