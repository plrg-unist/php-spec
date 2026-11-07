#!/usr/bin/env python3
"""Zero-unit DIRECT COW, persistent CV witnesses and real last-view cleanup."""
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
ASSIGN = (ROOT / 'tests/semantics/gc80_ordinary_assignment_cow.php').read_text()
REFERENCE = (ROOT / 'tests/semantics/gc80_ordinary_reference_cow.php').read_text()
UNSET = ASSIGN.replace('$a[0] = 23;', 'unset($a[0]);').replace(
    "echo 'W|', $a[0], '|', $view[1], '|';",
    "echo 'W|', (int) isset($a[0]), '|', $view[1], '|';")
DECLARATIONS = r'''syntax pgc80phase = VIEW | ARRAY | CHILD
dec $gc80_at(pstate, pgc80phase, nat, nat) : bool
def $gc80_at(S, VIEW, n_old, n_child) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text) metadata)) :: ptask_tail*
  -- if $base64(text) = $ptascii("view")
def $gc80_at(S, ARRAY, n_old, n_child) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*
  -- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_old)]
def $gc80_at(S, CHILD, n_old, n_child) = true
  -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
  -- if pdestructorcall.OBJECT = n_child
def $gc80_at(S, pgc80phase, n_old, n_child) = false -- otherwise
dec $gc80_seek(pstate, pgc80phase, nat, nat, nat) : pstate
def $gc80_seek(S, pgc80phase, n_old, n_child, n) = S
  -- if $gc80_at(S, pgc80phase, n_old, n_child)
def $gc80_seek(S, pgc80phase, n_old, n_child, n) = $gc80_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc80phase, n_old, n_child, $nabs($(n - 1)))
  -- if ~$gc80_at(S, pgc80phase, n_old, n_child) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc80_seek(S, pgc80phase, n_old, n_child, 0) = S
  -- if ~$gc80_at(S, pgc80phase, n_old, n_child)
def $gc80_seek(S, pgc80phase, n_old, n_child, n) = S
  -- if ~$gc80_at(S, pgc80phase, n_old, n_child)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $gc80_op(pstate, pdestructionoperation) : pstate
def $gc80_op(S, pdestructionoperation_new) = S[.TODO = $destructor_operation_tasks(S.TODO, pdestructionoperation_old, pdestructionoperation_new)][.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]]
  -- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation_old]
dec $gc80_output(pevent*) : preqbytes
def $gc80_output(eps) = eps
def $gc80_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc80_output(pevent_tail*)
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture


def valid(state):
    return [f'$heap_valid($heap_graph({state}))', f'$native_excess_valid({state})',
            f'$gc_state_valid({state})', f'$destruction_state_valid({state})',
            f'$call_descriptors_valid({state})']


def budget(state):
    return [f'$drive_steps({state}, 0) = {state}[.COMPLETION = BUDGET]',
            f'$drive_steps({state}, 2) = $drive_steps($drive_steps({state}, 1)[.COMPLETION = NORMAL], 1)']


def seek(before, after, phase):
    return [f'{after}_pause = $gc80_seek({before}, {phase}, n_old, n_child, 3000)',
            f'{after} = {after}_pause[.COMPLETION = NORMAL]',
            f'$gc80_at({after}, {phase}, n_old, n_child)']


COMMON = ('-- if $lookup(S.ENV, $ptascii("a")) = (n_root) '
          '-- if $lookup(S.ENV, $ptascii("view")) = (n_view) '
          '-- if S.STORE[n_root] = DEFINED (PARRAY n_old) '
          '-- if S.STORE[n_view] = DEFINED (PARRAY n_old) '
          '-- if S.NATIVEEXCESS = eps ')
ASG_STAGE = ('S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* ' + COMMON +
             '-- if S.RESULT = KNOWN (PINT 23) '
             '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child)), ENTRY (KINT 1) (DIRECT (PINT 17))]')
REF_STAGE = ('S.TODO = (ACQUIRE_ARRAY z) :: ptask_tail* ' + COMMON +
             '-- if S.BASE = BASE_DIM (BASE_VALUE (VARIABLE n_name* z_name)) (KNOWN (PINT 0)) z_key '
             '-- if n_name* = $ptascii("a") '
             '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17)), ENTRY (KINT 1) (DIRECT (POBJECT n_child))]')
UNSET_STAGE = ('S.TODO = UNSET_ARRAY :: ptask_tail* ' + COMMON +
              '-- if S.BASE = BASE_DIM (BASE_VALUE (VARIABLE n_name* z_name)) (KNOWN (PINT 0)) z_key '
              '-- if n_name* = $ptascii("a") '
              '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child)), ENTRY (KINT 1) (DIRECT (PINT 17))]')


def cow(kind, child_after, selected):
    task = {'assign': 'ASSIGN_ARRAY pbase z false', 'reference': 'ACQUIRE_ARRAY z', 'unset': 'UNSET_ARRAY'}[kind]
    checks = [
        *valid('S'), 'n_new = |S.ARRAYS|', 'n_ref = |S.STORE|',
        '$heap_owners($heap_graph(S), HARRAY n_old) = 2',
        '$native_rc(S, HARRAY n_old) = 2',
        '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
        '~((HARRAY n_old) <- $gc_nodes(S.GC.BUFFER))',
        '~((HOBJECT n_child) <- $gc_nodes(S.GC.BUFFER))',
        '$gc_array_ordinary_view(S, n_old, n_root, S.CVS)',
        '$gc_array_header_domain(S, n_old, n_new, n_root)',
        'PhpStep: S ~> S_raw',
        'S_raw.STORE[n_root] = DEFINED (PARRAY n_new)',
        'S_raw.STORE[n_view] = DEFINED (PARRAY n_old)',
        'S_raw.ARRAYS[n_old] = S.ARRAYS[n_old]',
        'S_raw.NATIVEEXCESS = eps',
        '$heap_owners($heap_graph(S_raw), HARRAY n_old) = 1',
        '$native_rc(S_raw, HARRAY n_old) = 1',
        f'$heap_owners($heap_graph(S_raw), HOBJECT n_child) = {child_after}',
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
        f'$heap_owners($heap_graph(S_live), HOBJECT n_child) = {child_after}',
        'S_live.DESTRUCTION.CALLS = eps',
        '~((HARRAY n_old) <- $gc_nodes(S_live.GC.BUFFER))',
        'S_after = $drive_steps(S_live, 1)[.COMPLETION = NORMAL]',
        'pdestructionoperation_done = pdestructionoperation_live[.NOGCEXTRA = [pgctemporary_done]]',
        'S_after.DESTRUCTION.OPERATIONS = [pdestructionoperation_done]',
        '$gc_operation_metadata_valid(S_after, pdestructionoperation_done)',
        '$native_rc(S_after, HARRAY n_old) = 1',
        '(HARRAY n_old) <- S_after.ALLOCATIONS',
        'S_after.DESTRUCTION.CALLS = eps',
        '~(n_child <- S_after.DESTRUCTION.CALLED)',
        '~((HARRAY n_old) <- $gc_nodes(S_after.GC.BUFFER))',
        *valid('S_after'), *budget('S'), *budget('S_live'),
    ]
    if selected:
        checks += ['$gc_same_location(S, S_raw) = [HOBJECT n_child]',
                   '$gc_same_location(S, S_live) = [HOBJECT n_child]',
                   '(HOBJECT n_child) <- $gc_nodes(S_live.GC.BUFFER)']
    else:
        checks += ['S_raw.STORE[n_ref] = DEFINED (PINT 17)',
                   '$heap_owners($heap_graph(S_raw), HCELL n_ref) = 1',
                   'S_raw.RESULT = KNOWN PNULL',
                   '$entry_lookup(S_raw.ARRAYS[n_new].ITEMS, KINT 0) = (ALIAS n_ref)',
                   '~((HOBJECT n_child) <- $gc_nodes(S_live.GC.BUFFER))']
    return checks


ASG_CHECKS = cow('assign', 1, True)
UNSET_CHECKS = cow('unset', 1, True)
REF_CHECKS = cow('reference', 2, False)
ASG_CHECKS += [
    'S_no_view = S[.ENV = $unbind(S.ENV, $ptascii("view"))][.HELD = [HARRAY n_old]]',
    '$($native_rc(S_no_view, HARRAY n_old) > 1)',
    '~$gc_array_ordinary_view(S_no_view, n_old, n_root, S_no_view.CVS)',
    '~$gc_array_header_domain(S_no_view, n_old, n_new, n_root)',
    'S_held = S[.HELD = [HARRAY n_old]]',
    '~$gc_array_header_domain(S_held, n_old, n_new, n_root)',
    'S_debt = S[.LITERALARRAYDEBTS = [n_old]]',
    '~$gc_array_header_domain(S_debt, n_old, n_new, n_root)',
    'S_view_debt = S[.LITERALREFDEBTS = [n_view]]',
    '~$gc_array_header_domain(S_view_debt, n_old, n_new, n_root)',
    'S_retired = S[.ALLOCATIONS = $native_remove_one(S.ALLOCATIONS, HARRAY n_old)]',
    '~$gc_array_header_domain(S_retired, n_old, n_new, n_root)',
    'S_nested = S[.ARRAYS = $array_replace(S.ARRAYS, n_old, $array_insert(S.ARRAYS[n_old], KINT 1, DIRECT (PARRAY n_old)))]',
    '~$gc_array_header_domain(S_nested, n_old, n_new, n_root)',
    'S_child_unit = S[.NATIVEEXCESS = [HOBJECT n_child]]',
    '~$gc_array_header_domain(S_child_unit, n_old, n_new, n_root)',
]
for name, patch in {
    'source': '[.SOURCE = DISCARD]',
    'root': '[.CELL = n_view]',
    'key': '[.KEY = KINT 1]',
    'early_done': '[.NOGCEXTRA = [pgctemporary_done]]',
    'operand': '[.NOGCEXTRA = [pgctemporary_live[.OPERAND = KNOWN (PARRAY n_new)]]]',
}.items():
    REF_CHECKS += [f'pdestructionoperation_bad_{name} = pdestructionoperation_live{patch}',
                   f'S_bad_{name} = $gc80_op(S_live, pdestructionoperation_bad_{name})',
                   f'$heap_graph(S_bad_{name}) = $heap_graph(S_live)',
                   f'~$gc_operation_metadata_valid(S_bad_{name}, pdestructionoperation_bad_{name})']
REF_CHECKS += [
    'S_no_view_live = S_live[.ENV = $unbind(S_live.ENV, $ptascii("view"))]',
    '~$gc_operation_metadata_valid(S_no_view_live, pdestructionoperation_live)',
    *seek('S_after', 'S_view', 'VIEW'),
    'S_view.NATIVEEXCESS = eps',
    '$native_rc(S_view, HARRAY n_old) = 1',
    '$heap_owners($heap_graph(S_view), HOBJECT n_child) = 1',
    '~((HARRAY n_new) <- S_view.ALLOCATIONS)',
    *seek('S_view', 'S_array', 'ARRAY'),
    'S_array.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_array) :: ptask_array_tail*',
    'pdestructionrelease_array.JOBS = [DESTRUCTION_VALUE (HARRAY n_old)]',
    '$native_rc(S_array, HARRAY n_old) = 1',
    'S_array_next = $drive_steps(S_array, 1)[.COMPLETION = NORMAL]',
    '~((HARRAY n_old) <- S_array_next.ALLOCATIONS)',
    'S_array_next.NATIVEEXCESS = eps',
    '~$gc_array_header_domain(S_array_next, n_old, n_new, n_root)',
    '~$gc_array_header_progress(S_array_next, pgctemporary_done)',
    *valid('S_array_next'),
    *seek('S_array_next', 'S_child', 'CHILD'),
    '$heap_owners($heap_graph(S_child), HOBJECT n_child) = 2',
    'S_done = $drive_steps(S_child, 3000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    'S_done.NATIVEEXCESS = eps',
    '~((HARRAY n_old) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    'n_child <- S_done.DESTRUCTION.CALLED',
    '$gc80_output(S_done.EVENTS) = $ptascii("B|Q|0|W|17|23|K|D|V|G|0|E|S|")',
    *valid('S_done'),
]

review.CASES = {
    'ordinary-assignment-cow-and-view-authority': {'source': ASSIGN, 'stage': ASG_STAGE, 'checks': ASG_CHECKS},
    'ordinary-reference-cow-and-last-view-retirement': {'source': REFERENCE, 'stage': REF_STAGE, 'checks': REF_CHECKS},
    'ordinary-direct-unset-count-slice': {'source': UNSET, 'stage': UNSET_STAGE, 'checks': UNSET_CHECKS},
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
