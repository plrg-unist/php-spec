#!/usr/bin/env python3
"""Quiet shallow COW observes the selected nested table, not the old header."""
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
ASSIGN = (ROOT / 'tests/semantics/gc85_scalar_array_dag_assignment.php').read_text()
UNSET = (ROOT / 'tests/semantics/gc85_scalar_array_dag_unset.php').read_text()
DECLARATIONS = r'''dec $gc85_second(pstate) : bool
def $gc85_second(S) = true
  -- if S.TODO = UNSET_ARRAY :: ptask_tail*
  -- if S.BASE = BASE_DIM (BASE_VALUE (VARIABLE n_name* z_name)) (KNOWN (PINT 1)) z_key
  -- if n_name* = $ptascii("a")
def $gc85_second(S) = false -- otherwise
dec $gc85_seek(pstate, nat) : pstate
def $gc85_seek(S, n) = S -- if $gc85_second(S)
def $gc85_seek(S, n) = $gc85_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$gc85_second(S) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc85_seek(S, 0) = S -- if ~$gc85_second(S)
def $gc85_seek(S, n) = S
  -- if ~$gc85_second(S)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $gc85_output(pevent*) : preqbytes
def $gc85_output(eps) = eps
def $gc85_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc85_output(pevent_tail*)
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


COMMON = ('-- if $lookup(S.ENV, $ptascii("a")) = (n_root) '
          '-- if $lookup(S.ENV, $ptascii("view")) = (n_view) '
          '-- if S.STORE[n_root] = DEFINED (PARRAY n_old) '
          '-- if S.STORE[n_view] = DEFINED (PARRAY n_old) '
          '-- if S.NATIVEEXCESS = eps ')
ASG_STAGE = ('S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* ' + COMMON +
             '-- if S.RESULT = KNOWN (PINT 23) '
             '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_inner)), ENTRY (KINT 1) (DIRECT (PINT 29))]')
UNSET_STAGE = ('S.TODO = UNSET_ARRAY :: ptask_tail* ' + COMMON +
               '-- if S.BASE = BASE_DIM (BASE_VALUE (VARIABLE n_name* z_name)) (KNOWN (PINT 0)) z_key '
               '-- if n_name* = $ptascii("a") '
               '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_inner)), ENTRY (KINT 1) (DIRECT (PARRAY n_inner))] '
               '-- if S.ARRAYS[n_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf))]')


def copy(before, after):
    return [
        *valid('S'), '~$destructor_operational(S)',
        'S.DESTRUCTION.OPERATIONS = eps', 'n_new = |S.ARRAYS|',
        '$heap_owners($heap_graph(S), HARRAY n_old) = 2',
        f'$heap_owners($heap_graph(S), HARRAY n_inner) = {before}',
        '~((HARRAY n_old) <- $gc_nodes(S.GC.BUFFER))',
        '~((HARRAY n_inner) <- $gc_nodes(S.GC.BUFFER))',
        '$gc_scalar_array_dag_context(S, n_old, n_root)',
        'PhpStep: S ~> S_raw',
        'S_raw.STORE[n_root] = DEFINED (PARRAY n_new)',
        'S_raw.STORE[n_view] = DEFINED (PARRAY n_old)',
        'S_raw.ARRAYS[n_old] = S.ARRAYS[n_old]',
        'S_raw.ARRAYS[n_inner] = S.ARRAYS[n_inner]',
        '$heap_owners($heap_graph(S_raw), HARRAY n_old) = 1',
        f'$heap_owners($heap_graph(S_raw), HARRAY n_inner) = {after}',
        'S_raw.NATIVEEXCESS = eps', 'S_raw.GC = S.GC',
        '$destruction_transition_owners(S, S_raw) = (S_raw, NO_OWNER_ORDER)',
        '$gc_scalar_array_dag_transition(S, S_raw) = ((n_old, KINT 0))',
        '$gc_same_location(S, S_raw) = [HARRAY n_inner]',
        '$gc_consumed_handoff(S, S_raw, [HARRAY n_old]) = eps',
        '$gc_consumed_handoff(S, S_raw, [HARRAY n_old, HARRAY n_inner]) = [HARRAY n_inner]',
        'S_next = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
        '$heap_graph(S_next) = $heap_graph(S_raw)',
        'S_next.ARRAYS = S_raw.ARRAYS', 'S_next.STORE = S_raw.STORE',
        'S_next.RESULT = S_raw.RESULT', 'S_next.TODO = S_raw.TODO',
        'S_next.EVENTS = S_raw.EVENTS', 'S_next.DESTRUCTION.OPERATIONS = eps',
        '~$destructor_operational(S_next)',
        'S_next.GC = $gc_buffer_add(S_raw.GC, HARRAY n_inner)',
        '~((HARRAY n_old) <- $gc_nodes(S_next.GC.BUFFER))',
        '(HARRAY n_inner) <- $gc_nodes(S_next.GC.BUFFER)',
        *valid('S_raw'), *valid('S_next'), *budget('S'),
    ]


ASG_CHECKS = copy(1, 1)
ASG_CHECKS += [
    '$entry_lookup(S_raw.ARRAYS[n_new].ITEMS, KINT 0) = (DIRECT (PINT 23))',
    '~$gc_array_header_domain(S, n_old, n_new, n_root)',
    'S_bad_store = S_raw[.STORE = $set_cell(S_raw.STORE, n_root, DEFINED (PARRAY n_old))]',
    '$gc_scalar_array_dag_transition(S, S_bad_store) = eps',
    '$gc_consumed_handoff(S, S_bad_store, [HARRAY n_old]) = [HARRAY n_old]',
    '$gc_same_location(S, S_bad_store) = eps',
    'S_no_origin = S[.ORIGIN = eps]',
    '$gc_consumed_handoff(S_no_origin, S_raw, [HARRAY n_old]) = [HARRAY n_old]',
    '$gc_same_location(S_no_origin, S_raw) = eps',
    'S_bad_row = S_raw[.ARRAYS = $array_replace(S_raw.ARRAYS, n_new, $array_insert(S_raw.ARRAYS[n_new], KINT 1, DIRECT (PINT 31)))]',
    '$gc_scalar_array_dag_transition(S, S_bad_row) = eps',
    'S_bad_key = S_raw[.KEY = KINT 1]',
    '$gc_scalar_array_dag_transition(S, S_bad_key) = eps',
    'S_bad_alloc = S_raw[.ALLOCATIONS = $native_remove_one(S_raw.ALLOCATIONS, HARRAY n_new)]',
    '$gc_scalar_array_dag_transition(S, S_bad_alloc) = eps',
    'S_no_view = S[.ENV = $unbind(S.ENV, $ptascii("view"))]',
    '$heap_owners($heap_graph(S_no_view), HARRAY n_old) = 2',
    '~$gc_scalar_array_dag_context(S_no_view, n_old, n_root)',
    'S_held = S[.HELD = [HARRAY n_old]]',
    '~$gc_scalar_array_dag_context(S_held, n_old, n_root)',
    'S_cycle = S[.ARRAYS = $array_replace(S.ARRAYS, n_inner, $array_insert(S.ARRAYS[n_inner], KINT 0, DIRECT (PARRAY n_old)))]',
    '~$gc_scalar_array_dag_context(S_cycle, n_old, n_root)',
    'S_alias = S[.ARRAYS = $array_replace(S.ARRAYS, n_inner, $array_insert(S.ARRAYS[n_inner], KINT 0, ALIAS n_root))][.REFCELLS = [n_root]]',
    '~$gc_scalar_array_dag_context(S_alias, n_old, n_root)',
    'S_unit = S[.NATIVEEXCESS = [HARRAY n_inner]]',
    '~$gc_scalar_array_dag_context(S_unit, n_old, n_root)',
    'S_history = S[.LITERALARRAYDEBTS = [n_inner]]',
    '~$gc_scalar_array_dag_context(S_history, n_old, n_root)',
    'S_retired = S[.ALLOCATIONS = $native_remove_one(S.ALLOCATIONS, HARRAY n_inner)]',
    '~$gc_scalar_array_dag_context(S_retired, n_old, n_root)',
]
UNSET_CHECKS = copy(2, 3)
UNSET_CHECKS += [
    '$heap_owners($heap_graph(S), HARRAY n_leaf) = 1',
    '$heap_owners($heap_graph(S_raw), HARRAY n_leaf) = 1',
    'S_raw.ARRAYS[n_leaf] = S.ARRAYS[n_leaf]',
    '~((HARRAY n_leaf) <- $gc_nodes(S_next.GC.BUFFER))',
    '$entry_lookup(S_raw.ARRAYS[n_new].ITEMS, KINT 0) = eps',
    '$entry_lookup(S_raw.ARRAYS[n_new].ITEMS, KINT 1) = (DIRECT (PARRAY n_inner))',
    'S_second_pause = $gc85_seek(S_next, 3000)',
    'S_second = S_second_pause[.COMPLETION = NORMAL]',
    '$gc85_second(S_second)',
    *valid('S_second'),
    'S_second.STORE[n_root] = DEFINED (PARRAY n_new)',
    '$heap_owners($heap_graph(S_second), HARRAY n_new) = 1',
    '$heap_owners($heap_graph(S_second), HARRAY n_inner) = 3',
    '$heap_owners($heap_graph(S_second), HARRAY n_leaf) = 1',
    '~((HARRAY n_new) <- $gc_nodes(S_second.GC.BUFFER))',
    '~((HARRAY n_inner) <- $gc_nodes(S_second.GC.BUFFER))',
    'PhpStep: S_second ~> S_second_raw',
    'S_second_raw.STORE[n_root] = DEFINED (PARRAY n_new)',
    '|S_second_raw.ARRAYS| = |S_second.ARRAYS|',
    '$heap_owners($heap_graph(S_second_raw), HARRAY n_inner) = 2',
    '$gc_scalar_array_dag_transition(S_second, S_second_raw) = eps',
    '$gc_same_location(S_second, S_second_raw) = eps',
    '$gc_consumed_handoff(S_second, S_second_raw, [HARRAY n_inner]) = [HARRAY n_inner]',
    'S_second_next = $drive_steps(S_second, 1)[.COMPLETION = NORMAL]',
    '$heap_owners($heap_graph(S_second_next), HARRAY n_inner) = 2',
    '$heap_owners($heap_graph(S_second_next), HARRAY n_leaf) = 1',
    '(HARRAY n_inner) <- $gc_nodes(S_second_next.GC.BUFFER)',
    '~((HARRAY n_new) <- $gc_nodes(S_second_next.GC.BUFFER))',
    '~((HARRAY n_leaf) <- $gc_nodes(S_second_next.GC.BUFFER))',
    'S_second_next.DESTRUCTION.OPERATIONS = eps',
    *valid('S_second_next'), *budget('S_second'),
    'S_done = $drive_steps(S_second_next, 3000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.NATIVEEXCESS = eps', 'S_done.DESTRUCTION.OPERATIONS = eps',
    '~((HARRAY n_old) <- S_done.ALLOCATIONS)',
    '~((HARRAY n_new) <- S_done.ALLOCATIONS)',
    '~((HARRAY n_inner) <- S_done.ALLOCATIONS)',
    '~((HARRAY n_leaf) <- S_done.ALLOCATIONS)',
    '$gc85_output(S_done.EVENTS) = $ptascii("B|Q|0|W|0|17|17|R|0|U|0|17|K|V|G|0|E|")',
    *valid('S_done'),
]

review.CASES = {
    'scalar-dag-assignment-selected-inner': {'source': ASSIGN, 'stage': ASG_STAGE, 'checks': ASG_CHECKS},
    'scalar-dag-repeated-delete-and-real-release': {'source': UNSET, 'stage': UNSET_STAGE, 'checks': UNSET_CHECKS},
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
