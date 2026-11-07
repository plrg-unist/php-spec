#!/usr/bin/env python3
"""Two nested COW separations and later genuine scalar-DAG decrements."""
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
SINGLE = (ROOT / 'tests/semantics/gc86_nested_scalar_array_assignment.php').read_text()
REPEATED = (ROOT / 'tests/semantics/gc86_repeated_nested_scalar_cow.php').read_text()
DECLARATIONS = r'''syntax pgc86phase = REPLACE | VIEW
dec $gc86_at(pstate, pgc86phase) : bool
def $gc86_at(S, REPLACE) = true
  -- if S.TODO = (ASSIGN_ARRAY (BASE_DIM (BASE_VALUE (VARIABLE n_name* z_name)) (KNOWN (PINT 1)) z_key) z false) :: ptask_tail*
  -- if n_name* = $ptascii("a") /\ S.RESULT = KNOWN (PINT 29)
def $gc86_at(S, VIEW) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text) metadata)) :: ptask_tail*
  -- if $base64(text) = $ptascii("view")
def $gc86_at(S, pgc86phase) = false -- otherwise
dec $gc86_seek(pstate, pgc86phase, nat) : pstate
def $gc86_seek(S, pgc86phase, n) = S -- if $gc86_at(S, pgc86phase)
def $gc86_seek(S, pgc86phase, n) = $gc86_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc86phase, $nabs($(n - 1)))
  -- if ~$gc86_at(S, pgc86phase) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc86_seek(S, pgc86phase, 0) = S -- if ~$gc86_at(S, pgc86phase)
def $gc86_seek(S, pgc86phase, n) = S
  -- if ~$gc86_at(S, pgc86phase)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $gc86_output(pevent*) : preqbytes
def $gc86_output(eps) = eps
def $gc86_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc86_output(pevent_tail*)
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
    return [f'{after}_pause = $gc86_seek({before}, {phase}, 3000)',
            f'{after} = {after}_pause[.COMPLETION = NORMAL]',
            f'$gc86_at({after}, {phase})']


COMMON = ('S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* '
          '-- if pbase = BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE n_name* z_name)) (KNOWN (PINT 0)) z_outer) (KNOWN (PINT 0)) z_inner '
          '-- if n_name* = $ptascii("a") -- if S.RESULT = KNOWN (PINT 23) '
          '-- if $lookup(S.ENV, $ptascii("a")) = (n_root) '
          '-- if $lookup(S.ENV, $ptascii("view")) = (n_view) '
          '-- if S.STORE[n_root] = DEFINED (PARRAY n_old) '
          '-- if S.STORE[n_view] = DEFINED (PARRAY n_old) '
          '-- if S.NATIVEEXCESS = eps ')
SINGLE_STAGE = (COMMON +
                '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_inner)), ENTRY (KINT 1) (DIRECT (PINT 29))] '
                '-- if S.ARRAYS[n_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17))]')
REPEATED_STAGE = (COMMON +
                  '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_inner)), ENTRY (KINT 1) (DIRECT (PARRAY n_inner))] '
                  '-- if S.ARRAYS[n_inner].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17)), ENTRY (KINT 1) (DIRECT (PARRAY n_leaf))]')


def nested(before, after):
    return [
        *valid('S'), '~$destructor_operational(S)',
        'S.DESTRUCTION.OPERATIONS = eps',
        'n_new_outer = |S.ARRAYS|', 'n_new_inner = $(n_new_outer + 1)',
        '$heap_owners($heap_graph(S), HARRAY n_old) = 2',
        f'$heap_owners($heap_graph(S), HARRAY n_inner) = {before}',
        '~((HARRAY n_old) <- $gc_nodes(S.GC.BUFFER))',
        '~((HARRAY n_inner) <- $gc_nodes(S.GC.BUFFER))',
        '$gc_scalar_array_dag_context(S, n_old, n_root)',
        'PhpStep: S ~> S_raw',
        '|S_raw.ARRAYS| = $(|S.ARRAYS| + 2)',
        'S_raw.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY n_new_outer, HARRAY n_new_inner]',
        'S_raw.STORE = $set_cell(S.STORE, n_root, DEFINED (PARRAY n_new_outer))',
        'S_raw.STORE[n_view] = DEFINED (PARRAY n_old)',
        'S_raw.ARRAYS[n_old] = S.ARRAYS[n_old]',
        'S_raw.ARRAYS[n_inner] = S.ARRAYS[n_inner]',
        '$entry_lookup(S_raw.ARRAYS[n_new_outer].ITEMS, KINT 0) = (DIRECT (PARRAY n_new_inner))',
        '$entry_lookup(S_raw.ARRAYS[n_new_inner].ITEMS, KINT 0) = (DIRECT (PINT 23))',
        '$heap_owners($heap_graph(S_raw), HARRAY n_old) = 1',
        f'$heap_owners($heap_graph(S_raw), HARRAY n_inner) = {after}',
        '$heap_owners($heap_graph(S_raw), HARRAY n_new_outer) = 1',
        '$heap_owners($heap_graph(S_raw), HARRAY n_new_inner) = 1',
        'S_raw.NATIVEEXCESS = eps', 'S_raw.GC = S.GC',
        '$destruction_transition_owners(S, S_raw) = (S_raw, NO_OWNER_ORDER)',
        '$gc_scalar_array_dag_transition(S, S_raw) = eps',
        '$gc_scalar_array_nested_transition(S, S_raw) = (n_old)',
        '$gc_same_location(S, S_raw) = eps',
        '$gc_consumed_handoff(S, S_raw, [HARRAY n_old]) = eps',
        '$gc_consumed_handoff(S, S_raw, [HARRAY n_old, HARRAY n_inner]) = [HARRAY n_inner]',
        'S_next = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
        '$heap_graph(S_next) = $heap_graph(S_raw)',
        'S_next.ARRAYS = S_raw.ARRAYS', 'S_next.STORE = S_raw.STORE',
        'S_next.RESULT = S_raw.RESULT', 'S_next.TODO = S_raw.TODO',
        'S_next.DESTRUCTION.OPERATIONS = eps', 'S_next.EVENTS = S_raw.EVENTS',
        'S_next.GC = S_raw.GC',
        '~((HARRAY n_old) <- $gc_nodes(S_next.GC.BUFFER))',
        '~((HARRAY n_inner) <- $gc_nodes(S_next.GC.BUFFER))',
        *valid('S_raw'), *valid('S_next'), *budget('S'),
    ]


SINGLE_CHECKS = nested(1, 1)
SINGLE_CHECKS += [
    'S_no_origin = S[.ORIGIN = eps]',
    '$gc_scalar_array_nested_transition(S_no_origin, S_raw) = eps',
    '$gc_consumed_handoff(S_no_origin, S_raw, [HARRAY n_old]) = [HARRAY n_old]',
    'S_bad_store = S_raw[.STORE = $set_cell(S_raw.STORE, n_root, DEFINED (PARRAY n_new_inner))]',
    '$gc_scalar_array_nested_transition(S, S_bad_store) = eps',
    'S_bad_inner = S_raw[.ARRAYS = $array_replace(S_raw.ARRAYS, n_new_inner, $array_insert(S_raw.ARRAYS[n_new_inner], KINT 0, DIRECT (PINT 31)))]',
    '$gc_scalar_array_nested_transition(S, S_bad_inner) = eps',
    'S_bad_outer = S_raw[.ARRAYS = $array_replace(S_raw.ARRAYS, n_new_outer, $array_insert(S_raw.ARRAYS[n_new_outer], KINT 0, DIRECT (PARRAY n_inner)))]',
    '$gc_scalar_array_nested_transition(S, S_bad_outer) = eps',
    'S_bad_order = S_raw[.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY n_new_inner, HARRAY n_new_outer]]',
    '$gc_scalar_array_nested_transition(S, S_bad_order) = eps',
    'S_bad_key = S_raw[.KEY = KINT 1]',
    '$gc_scalar_array_nested_transition(S, S_bad_key) = eps',
    'S_no_view = S[.ENV = $unbind(S.ENV, $ptascii("view"))]',
    '$heap_owners($heap_graph(S_no_view), HARRAY n_old) = 2',
    '$gc_scalar_array_nested_transition(S_no_view, S_raw) = eps',
    'S_unit = S[.NATIVEEXCESS = [HARRAY n_old]]',
    '$gc_scalar_array_nested_transition(S_unit, S_raw) = eps',
    'n_missing = |S.STORE|',
    'S_bad_root = S[.ENV = (BIND $ptascii("a") n_missing) :: $unbind(S.ENV, $ptascii("a"))][.ALLOCATIONS = S.ALLOCATIONS ++ [HCELL n_missing]]',
    '~$gc_scalar_array_nested_site(S_bad_root, S_bad_root.ORIGIN, ASSIGN_ARRAY pbase z false, n_missing)',
    '$gc_scalar_array_nested_transition(S_bad_root, S_raw) = eps',
]
REPEATED_CHECKS = nested(2, 3)
REPEATED_CHECKS += [
    '$heap_owners($heap_graph(S), HARRAY n_leaf) = 1',
    '$heap_owners($heap_graph(S_raw), HARRAY n_leaf) = 2',
    'S_raw.ARRAYS[n_leaf] = S.ARRAYS[n_leaf]',
    '$entry_lookup(S_raw.ARRAYS[n_new_inner].ITEMS, KINT 1) = (DIRECT (PARRAY n_leaf))',
    '~((HARRAY n_leaf) <- $gc_nodes(S_next.GC.BUFFER))',
    'S_retag = S[.TODO = (ASSIGN_ARRAY (BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE n_name* z_name)) (KNOWN (PINT 1)) z_outer) (KNOWN (PINT 0)) z_inner) z false) :: ptask_tail*]',
    'PhpStep: S_retag ~> S_retag_raw',
    '$heap_valid($heap_graph(S_retag_raw))',
    '$gc_scalar_array_nested_transition(S_retag, S_retag_raw) = eps',
    '$gc_consumed_handoff(S_retag, S_retag_raw, [HARRAY n_old]) = [HARRAY n_old]',
    *seek('S_next', 'S_replace', 'REPLACE'),
    *valid('S_replace'),
    '$heap_owners($heap_graph(S_replace), HARRAY n_new_outer) = 1',
    '$heap_owners($heap_graph(S_replace), HARRAY n_inner) = 3',
    '$heap_owners($heap_graph(S_replace), HARRAY n_leaf) = 2',
    '~((HARRAY n_inner) <- $gc_nodes(S_replace.GC.BUFFER))',
    '~((HARRAY n_leaf) <- $gc_nodes(S_replace.GC.BUFFER))',
    'PhpStep: S_replace ~> S_replace_raw',
    '|S_replace_raw.ARRAYS| = |S_replace.ARRAYS|',
    'S_replace_raw.GC = S_replace.GC',
    '$heap_owners($heap_graph(S_replace_raw), HARRAY n_inner) = 2',
    '$heap_owners($heap_graph(S_replace_raw), HARRAY n_leaf) = 2',
    '$gc_scalar_array_nested_transition(S_replace, S_replace_raw) = eps',
    '$gc_same_location(S_replace, S_replace_raw) = eps',
    '$gc_consumed_handoff(S_replace, S_replace_raw, [HARRAY n_inner]) = [HARRAY n_inner]',
    'S_replace_next = $drive_steps(S_replace, 1)[.COMPLETION = NORMAL]',
    '$heap_graph(S_replace_next) = $heap_graph(S_replace_raw)',
    'S_replace_next.GC = $gc_buffer_add(S_replace_raw.GC, HARRAY n_inner)',
    '~((HARRAY n_leaf) <- $gc_nodes(S_replace_next.GC.BUFFER))',
    'S_replace_next.DESTRUCTION.OPERATIONS = eps',
    *valid('S_replace_next'), *budget('S_replace'),
    *seek('S_replace_next', 'S_view', 'VIEW'),
    '$heap_owners($heap_graph(S_view), HARRAY n_old) = 1',
    '$heap_owners($heap_graph(S_view), HARRAY n_inner) = 2',
    '$heap_owners($heap_graph(S_view), HARRAY n_leaf) = 1',
    '~((HARRAY n_new_outer) <- S_view.ALLOCATIONS)',
    '~((HARRAY n_new_inner) <- S_view.ALLOCATIONS)',
    '(HARRAY n_leaf) <- $gc_nodes(S_view.GC.BUFFER)',
    *valid('S_view'),
    'S_done = $drive_steps(S_view, 3000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.NATIVEEXCESS = eps', 'S_done.DESTRUCTION.OPERATIONS = eps',
    '~((HARRAY n_old) <- S_done.ALLOCATIONS)',
    '~((HARRAY n_inner) <- S_done.ALLOCATIONS)',
    '~((HARRAY n_new_outer) <- S_done.ALLOCATIONS)',
    '~((HARRAY n_new_inner) <- S_done.ALLOCATIONS)',
    '~((HARRAY n_leaf) <- S_done.ALLOCATIONS)',
    '$gc86_output(S_done.EVENTS) = $ptascii("B|Q|0|W|23|17|17|R|0|U|29|17|K|V|G|0|E|")',
    *valid('S_done'),
]

review.CASES = {
    'nested-scalar-two-copy-assignment': {'source': SINGLE, 'stage': SINGLE_STAGE, 'checks': SINGLE_CHECKS},
    'nested-repeated-scalar-and-real-branch-drop': {'source': REPEATED, 'stage': REPEATED_STAGE, 'checks': REPEATED_CHECKS},
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
