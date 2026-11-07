#!/usr/bin/env python3
"""Ordinary quiet-reference copies, captured views and real CELL retirement."""
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
SINGLE = (ROOT / 'tests/semantics/gc81_ordinary_singleton_alias.php').read_text()
SHARED = (ROOT / 'tests/semantics/gc81_ordinary_shared_alias.php').read_text()
UNSET = SHARED.replace('$a[0] = 23;', 'unset($a[0]);').replace(
    "echo 'W|', $slot, '|', $a[0], '|', $a[2], '|', $view[0], '|', $view[2], '|';",
    "echo 'W|', (int) isset($a[0]), '|', $a[2], '|', $view[0], '|';\nunset($a[2]);")

DECLARATIONS = r'''syntax pgc81phase = VIEW | ARRAY | CELL | SLOT | SECOND
dec $gc81_at(pstate, pgc81phase, nat, nat) : bool
def $gc81_at(S, VIEW, n_old, n_leaf) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text) metadata)) :: ptask_tail*
  -- if $base64(text) = $ptascii("view")
def $gc81_at(S, SLOT, n_old, n_leaf) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text) metadata)) :: ptask_tail*
  -- if $base64(text) = $ptascii("slot")
def $gc81_at(S, ARRAY, n_old, n_leaf) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*
  -- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_old)]
def $gc81_at(S, CELL, n_old, n_leaf) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HCELL n_leaf)) :: pdestructionjob_tail*
def $gc81_at(S, SECOND, n_old, n_leaf) = true
  -- if S.TODO = UNSET_ARRAY :: ptask_tail*
  -- if S.BASE = BASE_DIM (BASE_VALUE (VARIABLE n_name* z_name)) (KNOWN (PINT 2)) z_key
def $gc81_at(S, pgc81phase, n_old, n_leaf) = false -- otherwise
dec $gc81_seek(pstate, pgc81phase, nat, nat, nat) : pstate
def $gc81_seek(S, pgc81phase, n_old, n_leaf, n) = S
  -- if $gc81_at(S, pgc81phase, n_old, n_leaf)
def $gc81_seek(S, pgc81phase, n_old, n_leaf, n) = $gc81_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc81phase, n_old, n_leaf, $nabs($(n - 1)))
  -- if ~$gc81_at(S, pgc81phase, n_old, n_leaf) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc81_seek(S, pgc81phase, n_old, n_leaf, 0) = S
  -- if ~$gc81_at(S, pgc81phase, n_old, n_leaf)
def $gc81_seek(S, pgc81phase, n_old, n_leaf, n) = S
  -- if ~$gc81_at(S, pgc81phase, n_old, n_leaf)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $gc81_op(pstate, pdestructionoperation) : pstate
def $gc81_op(S, pdestructionoperation_new) = S[.TODO = $destructor_operation_tasks(S.TODO, pdestructionoperation_old, pdestructionoperation_new)][.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]]
  -- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation_old]
dec $gc81_output(pevent*) : preqbytes
def $gc81_output(eps) = eps
def $gc81_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc81_output(pevent_tail*)
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture


def valid(s):
    return [f'$heap_valid($heap_graph({s}))', f'$native_excess_valid({s})',
            f'$gc_state_valid({s})', f'$destruction_state_valid({s})',
            f'$call_descriptors_valid({s})']


def budget(s):
    return [f'$drive_steps({s}, 0) = {s}[.COMPLETION = BUDGET]',
            f'$drive_steps({s}, 2) = $drive_steps($drive_steps({s}, 1)[.COMPLETION = NORMAL], 1)']


def seek(before, after, phase):
    return [f'{after}_pause = $gc81_seek({before}, {phase}, n_old, n_leaf, 3000)',
            f'{after} = {after}_pause[.COMPLETION = NORMAL]',
            f'$gc81_at({after}, {phase}, n_old, n_leaf)']


COMMON = ('-- if $lookup(S.ENV, $ptascii("a")) = (n_root) '
          '-- if $lookup(S.ENV, $ptascii("view")) = (n_view) '
          '-- if S.STORE[n_root] = DEFINED (PARRAY n_old) '
          '-- if S.STORE[n_view] = DEFINED (PARRAY n_old) '
          '-- if S.NATIVEEXCESS = eps ')
SINGLE_ROW = '[ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) (DIRECT (POBJECT n_child))]'
SHARED_ROW = ('[ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) (DIRECT (PINT 17)), '
              'ENTRY (KINT 2) (ALIAS n_leaf), ENTRY (KINT 3) (DIRECT (POBJECT n_child))]')


def stage(row, unset=False):
    head = ('S.TODO = UNSET_ARRAY :: ptask_tail* '
            '-- if S.BASE = BASE_DIM (BASE_VALUE (VARIABLE n_name* z_name)) (KNOWN (PINT 0)) z_key '
            '-- if n_name* = $ptascii("a") ' if unset else
            'S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* '
            '-- if S.RESULT = KNOWN (PINT 23) ')
    return head + COMMON + f'-- if S.ARRAYS[n_old].ITEMS = {row}'


def cow(shared, unset=False):
    leaf_before = 3 if shared else 1
    leaf_after = 4 if unset else 5 if shared else 1
    task = 'UNSET_ARRAY' if unset else 'ASSIGN_ARRAY pbase z false'
    return [
        *valid('S'), 'n_new = |S.ARRAYS|',
        'S.STORE[n_leaf] = DEFINED (PINT 17)',
        '$heap_owners($heap_graph(S), HARRAY n_old) = 2',
        '$native_rc(S, HARRAY n_old) = 2',
        f'$heap_owners($heap_graph(S), HCELL n_leaf) = {leaf_before}',
        '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
        '~((HARRAY n_old) <- $gc_nodes(S.GC.BUFFER))',
        '~((HOBJECT n_child) <- $gc_nodes(S.GC.BUFFER))',
        '$gc_array_quiet_alias_entries(S, S.ARRAYS[n_old].ITEMS)',
        '$gc_array_header_domain(S, n_old, n_new, n_root)',
        'parray_copy = $gc_array_alias_copy(S, n_old)',
        f'$entry_lookup(parray_copy.ITEMS, KINT 0) = (ALIAS n_leaf)' if shared else
        '$entry_lookup(parray_copy.ITEMS, KINT 0) = (DIRECT (PINT 17))',
        'PhpStep: S ~> S_raw',
        'S_raw.STORE[n_root] = DEFINED (PARRAY n_new)',
        'S_raw.STORE[n_view] = DEFINED (PARRAY n_old)',
        'S_raw.ARRAYS[n_old] = S.ARRAYS[n_old]',
        'S_raw.NATIVEEXCESS = eps',
        '$heap_owners($heap_graph(S_raw), HARRAY n_old) = 1',
        f'$heap_owners($heap_graph(S_raw), HCELL n_leaf) = {leaf_after}',
        '$heap_owners($heap_graph(S_raw), HOBJECT n_child) = 2',
        'pgctemporary_live = {OPERAND KNOWN (PARRAY n_old), PENDING true}',
        'pgctemporary_done = pgctemporary_live[.PENDING = false]',
        f'$gc_operation_temporary_extra(S, S_raw, {task}, [HARRAY n_old]) = [pgctemporary_live]',
        'S_live = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
        'S_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_live) :: ptask_live_tail*',
        'pdestructionrelease_live.JOBS = [DESTRUCTION_TEMP (HARRAY n_old)]',
        'S_live.DESTRUCTION.OPERATIONS = [pdestructionoperation_live]',
        'pdestructionoperation_live.NOGCEXTRA = [pgctemporary_live]',
        '$gc_operation_metadata_valid(S_live, pdestructionoperation_live)',
        '$gc_release_metadata_valid(S_live, pdestructionrelease_live)',
        *valid('S_live'),
        '$native_rc(S_live, HARRAY n_old) = 2',
        'S_live.DESTRUCTION.CALLS = eps',
        '~((HARRAY n_old) <- $gc_nodes(S_live.GC.BUFFER))',
        '~((HOBJECT n_child) <- $gc_nodes(S_live.GC.BUFFER))',
        'S_after = $drive_steps(S_live, 1)[.COMPLETION = NORMAL]',
        'pdestructionoperation_done = pdestructionoperation_live[.NOGCEXTRA = [pgctemporary_done]]',
        'S_after.DESTRUCTION.OPERATIONS = [pdestructionoperation_done]',
        '$gc_operation_metadata_valid(S_after, pdestructionoperation_done)',
        '$native_rc(S_after, HARRAY n_old) = 1',
        f'$heap_owners($heap_graph(S_after), HCELL n_leaf) = {leaf_after}',
        '$heap_owners($heap_graph(S_after), HOBJECT n_child) = 2',
        '~((HARRAY n_old) <- $gc_nodes(S_after.GC.BUFFER))',
        'S_after.DESTRUCTION.CALLS = eps',
        *valid('S_after'), *budget('S'), *budget('S_live'),
    ]


SINGLE_CHECKS = cow(False) + [
    '$lookup(S.ENV, $ptascii("slot")) = eps',
    'S_raw.STORE[n_leaf] = DEFINED (PINT 17)',
    '$entry_lookup(S_raw.ARRAYS[n_new].ITEMS, KINT 0) = (DIRECT (PINT 23))',
    '$gc_array_ordinary_alias_image(S_raw, n_old, n_new, n_root, KINT 0, PINT 23)',
    '~$gc_array_alias_image(S_raw, n_old, n_new, n_root, KINT 0, PINT 23)',
    '$gc_same_location(S, S_raw) = eps',
    '$gc_same_location(S, S_live) = eps',
    *seek('S_after', 'S_view', 'VIEW'),
    '$heap_owners($heap_graph(S_view), HCELL n_leaf) = 1',
    '$heap_owners($heap_graph(S_view), HOBJECT n_child) = 1',
    '~((HARRAY n_new) <- S_view.ALLOCATIONS)',
    *seek('S_view', 'S_array', 'ARRAY'),
    'S_array_next = $drive_steps(S_array, 1)[.COMPLETION = NORMAL]',
    '~((HARRAY n_old) <- S_array_next.ALLOCATIONS)',
    *seek('S_array_next', 'S_cell', 'CELL'),
    '$heap_owners($heap_graph(S_cell), HCELL n_leaf) = 1',
    'S_cell_next = $drive_steps(S_cell, 1)[.COMPLETION = NORMAL]',
    '~((HCELL n_leaf) <- S_cell_next.ALLOCATIONS)',
    '~$gc_array_header_progress(S_cell_next, pgctemporary_done)',
    *valid('S_cell_next'),
]

SHARED_CHECKS = cow(True) + [
    '$lookup(S.ENV, $ptascii("slot")) = (n_leaf)',
    'S_raw.STORE[n_leaf] = DEFINED (PINT 23)',
    'S_raw.ARRAYS[n_new] = S.ARRAYS[n_old]',
    '$gc_array_ordinary_alias_image(S_raw, n_old, n_new, n_root, KINT 0, PINT 23)',
    '~$gc_array_alias_image(S_raw, n_old, n_new, n_root, KINT 0, PINT 23)',
    '$gc_same_location(S, S_raw) = eps',
    '$gc_same_location(S, S_live) = eps',
    'n_bad = |S.STORE|',
    '~$gc_array_quiet_alias_item(S, ALIAS n_bad)',
    'S_owning = S[.STORE = $set_cell(S.STORE, n_leaf, DEFINED (POBJECT n_child))]',
    '~$gc_array_quiet_alias_entries(S_owning, S_owning.ARRAYS[n_old].ITEMS)',
    '~$gc_array_header_domain(S_owning, n_old, n_new, n_root)',
    'S_owning_drop = S_owning[.ARRAYS = $array_replace(S_owning.ARRAYS, n_old, $array_insert(S_owning.ARRAYS[n_old], KINT 3, DIRECT (PINT 17)))]',
    *valid('S_owning_drop'),
    'PhpStep: S_owning_drop ~> S_owning_raw',
    '$heap_owners($heap_graph(S_owning_drop), HOBJECT n_child) = 1',
    '$heap_owners($heap_graph(S_owning_raw), HOBJECT n_child) = 0',
    '$gc_array_ordinary_alias_image(S_owning_raw, n_old, n_new, n_root, KINT 0, PINT 23)',
    '~$gc_array_alias_image(S_owning_raw, n_old, n_new, n_root, KINT 0, PINT 23)',
    '$gc_operation_temporary_extra(S_owning_drop, S_owning_raw, ASSIGN_ARRAY pbase z false, [HARRAY n_old]) = eps',
    '$gc_operation_temporary_extra(S_owning_drop, S_owning_raw, ASSIGN_ARRAY pbase z false, [HARRAY n_old, HOBJECT n_child]) = eps',
    'S_leaf_unit = S[.NATIVEEXCESS = [HCELL n_leaf]]',
    '~$gc_array_header_domain(S_leaf_unit, n_old, n_new, n_root)',
    'S_no_view = S[.ENV = $unbind(S.ENV, $ptascii("view"))]',
    '~$gc_array_header_domain(S_no_view, n_old, n_new, n_root)',
    'S_held = S[.HELD = [HARRAY n_old]]',
    '~$gc_array_header_domain(S_held, n_old, n_new, n_root)',
    'S_retained = S[.LITERALREFRETAINED = [n_leaf]]',
    '~$gc_array_header_domain(S_retained, n_old, n_new, n_root)',
    # Same owner graph, but the selected copied DIRECT Child is overwritten.
    # The quiet ALIA siblings stay shared and do not acquire payload owners.
    'parray_direct = $array_insert($array_insert(S.ARRAYS[n_old], KINT 0, DIRECT (POBJECT n_child)), KINT 3, ALIAS n_leaf)',
    'S_direct = S[.ARRAYS = $array_replace(S.ARRAYS, n_old, parray_direct)]',
    *valid('S_direct'),
    'PhpStep: S_direct ~> S_direct_raw',
    '$heap_owners($heap_graph(S_direct_raw), HOBJECT n_child) = 1',
    '$gc_array_ordinary_alias_image(S_direct_raw, n_old, n_new, n_root, KINT 0, PINT 23)',
    '$gc_same_location(S_direct, S_direct_raw) = [HOBJECT n_child]',
    'S_direct_live = $drive_steps(S_direct, 1)[.COMPLETION = NORMAL]',
    '$gc_same_location(S_direct, S_direct_live) = [HOBJECT n_child]',
    '(HOBJECT n_child) <- $gc_nodes(S_direct_live.GC.BUFFER)',
    '~((HARRAY n_old) <- $gc_nodes(S_direct_live.GC.BUFFER))',
    *valid('S_direct_live'),
]
for name, patch in {
    'source': '[.SOURCE = DISCARD]',
    'root': '[.CELL = n_view]',
    'key': '[.KEY = KINT 1]',
    'progress': '[.NOGCEXTRA = [pgctemporary_done]]',
    'operand': '[.NOGCEXTRA = [pgctemporary_live[.OPERAND = KNOWN (PARRAY n_new)]]]',
}.items():
    SHARED_CHECKS += [f'pdestructionoperation_bad_{name} = pdestructionoperation_live{patch}',
                      f'S_bad_{name} = $gc81_op(S_live, pdestructionoperation_bad_{name})',
                      f'$heap_graph(S_bad_{name}) = $heap_graph(S_live)',
                      f'~$gc_operation_metadata_valid(S_bad_{name}, pdestructionoperation_bad_{name})']
SHARED_CHECKS += [
    'S_view_missing = S_live[.ENV = $unbind(S_live.ENV, $ptascii("view"))]',
    '~$gc_operation_metadata_valid(S_view_missing, pdestructionoperation_live)',
    *seek('S_after', 'S_slot', 'SLOT'),
    '~((HARRAY n_old) <- S_slot.ALLOCATIONS)',
    '~((HARRAY n_new) <- S_slot.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_slot.ALLOCATIONS)',
    'n_child <- S_slot.DESTRUCTION.CALLED',
    'S_slot.STORE[n_leaf] = DEFINED (PINT 23)',
    '$heap_owners($heap_graph(S_slot), HCELL n_leaf) = 1',
    *seek('S_slot', 'S_last', 'CELL'),
    'S_last_next = $drive_steps(S_last, 1)[.COMPLETION = NORMAL]',
    '~((HCELL n_leaf) <- S_last_next.ALLOCATIONS)',
    *valid('S_last_next'),
    'S_done = $drive_steps(S_last_next, 3000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    'S_done.NATIVEEXCESS = eps',
    '$gc81_output(S_done.EVENTS) = $ptascii("B|Q|0|W|23|23|23|23|23|K|D|V|23|F|G|0|E|S|")',
    *valid('S_done'),
]

UNSET_CHECKS = cow(True, True) + [
    'S_raw.STORE[n_leaf] = DEFINED (PINT 17)',
    '$entry_lookup(S_raw.ARRAYS[n_new].ITEMS, KINT 0) = eps',
    '$gc_array_unset_decrements(S, S_raw) = [HCELL n_leaf]',
    '$gc_array_unset_decrements(S, S_live) = [HCELL n_leaf]',
    '~((HCELL n_leaf) <- $gc_nodes(S_live.GC.BUFFER))',
    *seek('S_after', 'S_second', 'SECOND'),
    '$heap_owners($heap_graph(S_second), HCELL n_leaf) = 4',
    'PhpStep: S_second ~> S_second_raw',
    '$heap_owners($heap_graph(S_second_raw), HCELL n_leaf) = 3',
    '$gc_array_unset_transition(S_second, S_second_raw) = eps',
    'S_second_live = $drive_steps(S_second, 1)[.COMPLETION = NORMAL]',
    'S_second_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_second) :: ptask_second_tail*',
    'pdestructionrelease_second.JOBS = [DESTRUCTION_VALUE (HCELL n_leaf)]',
    'S_second_next = $drive_steps(S_second_live, 1)[.COMPLETION = NORMAL]',
    '$heap_owners($heap_graph(S_second_next), HCELL n_leaf) = 3',
    'S_second_next.STORE[n_leaf] = DEFINED (PINT 17)',
    '(HCELL n_leaf) <- S_second_next.ALLOCATIONS',
    'S_second_next.DESTRUCTION.CALLS = eps',
    '~((HCELL n_leaf) <- $gc_nodes(S_second_next.GC.BUFFER))',
    '~((HOBJECT n_child) <- $gc_nodes(S_second_next.GC.BUFFER))',
    *valid('S_second_next'), *budget('S_second_live'),
]

review.CASES = {
    'ordinary-singleton-scalar-unwrap-and-cell-retirement': {'source': SINGLE, 'stage': stage(SINGLE_ROW), 'checks': SINGLE_CHECKS},
    'ordinary-shared-scalar-copy-write-and-retirement': {'source': SHARED, 'stage': stage(SHARED_ROW), 'checks': SHARED_CHECKS},
    'ordinary-quiet-alias-unset-count-slice': {'source': UNSET, 'stage': stage(SHARED_ROW, True), 'checks': UNSET_CHECKS},
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
