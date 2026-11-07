#!/usr/bin/env python3
"""Fresh versus reused quiet reference cells during ordinary array COW."""
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
SINGLE = (ROOT / 'tests/semantics/gc82_ordinary_singleton_alias_reference.php').read_text()
SHARED = (ROOT / 'tests/semantics/gc82_ordinary_shared_alias_reference.php').read_text()
DECLARATIONS = r'''syntax pgc82phase = WRITE | REF | VIEW | ARRAY | CELL | SLOT
dec $gc82_at(pstate, pgc82phase, nat, nat) : bool
def $gc82_at(S, WRITE, n_old, n_ref) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask_tail*
  -- if n_name* = $ptascii("ref") /\ S.RESULT = KNOWN (PINT 23)
def $gc82_at(S, REF, n_old, n_ref) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text) metadata)) :: ptask_tail*
  -- if $base64(text) = $ptascii("ref")
def $gc82_at(S, VIEW, n_old, n_ref) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text) metadata)) :: ptask_tail*
  -- if $base64(text) = $ptascii("view")
def $gc82_at(S, SLOT, n_old, n_ref) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text) metadata)) :: ptask_tail*
  -- if $base64(text) = $ptascii("slot")
def $gc82_at(S, ARRAY, n_old, n_ref) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*
  -- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_old)]
def $gc82_at(S, CELL, n_old, n_ref) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HCELL n_ref)) :: pdestructionjob_tail*
def $gc82_at(S, pgc82phase, n_old, n_ref) = false -- otherwise
dec $gc82_seek(pstate, pgc82phase, nat, nat, nat) : pstate
def $gc82_seek(S, pgc82phase, n_old, n_ref, n) = S
  -- if $gc82_at(S, pgc82phase, n_old, n_ref)
def $gc82_seek(S, pgc82phase, n_old, n_ref, n) = $gc82_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc82phase, n_old, n_ref, $nabs($(n - 1)))
  -- if ~$gc82_at(S, pgc82phase, n_old, n_ref) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc82_seek(S, pgc82phase, n_old, n_ref, 0) = S
  -- if ~$gc82_at(S, pgc82phase, n_old, n_ref)
def $gc82_seek(S, pgc82phase, n_old, n_ref, n) = S
  -- if ~$gc82_at(S, pgc82phase, n_old, n_ref)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $gc82_op(pstate, pdestructionoperation) : pstate
def $gc82_op(S, pdestructionoperation_new) = S[.TODO = $destructor_operation_tasks(S.TODO, pdestructionoperation_old, pdestructionoperation_new)][.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]]
  -- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation_old]
dec $gc82_output(pevent*) : preqbytes
def $gc82_output(eps) = eps
def $gc82_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc82_output(pevent_tail*)
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


def seek(before, after, phase, cell='n_acquired'):
    return [f'{after}_pause = $gc82_seek({before}, {phase}, n_old, {cell}, 3000)',
            f'{after} = {after}_pause[.COMPLETION = NORMAL]',
            f'$gc82_at({after}, {phase}, n_old, {cell})']


COMMON = ('S.TODO = (ACQUIRE_ARRAY z) :: ptask_tail* '
          '-- if S.BASE = BASE_DIM (BASE_VALUE (VARIABLE n_name* z_name)) (KNOWN (PINT 0)) z_key '
          '-- if n_name* = $ptascii("a") '
          '-- if $lookup(S.ENV, $ptascii("a")) = (n_root) '
          '-- if $lookup(S.ENV, $ptascii("view")) = (n_view) '
          '-- if S.STORE[n_root] = DEFINED (PARRAY n_old) '
          '-- if S.STORE[n_view] = DEFINED (PARRAY n_old) '
          '-- if S.NATIVEEXCESS = eps ')
SINGLE_ROW = '[ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) (DIRECT (POBJECT n_child))]'
SHARED_ROW = ('[ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) (DIRECT (PINT 17)), '
              'ENTRY (KINT 2) (ALIAS n_leaf), ENTRY (KINT 3) (DIRECT (POBJECT n_child))]')


def acquire(shared):
    return [
        *valid('S'), 'n_new = |S.ARRAYS|',
        'n_acquired = n_leaf' if shared else 'n_acquired = |S.STORE|',
        'S.STORE[n_leaf] = DEFINED (PINT 17)',
        'n_leaf <- S.REFCELLS',
        '$heap_owners($heap_graph(S), HARRAY n_old) = 2',
        '$native_rc(S, HARRAY n_old) = 2',
        f'$heap_owners($heap_graph(S), HCELL n_leaf) = {3 if shared else 1}',
        '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
        '~((HARRAY n_old) <- $gc_nodes(S.GC.BUFFER))',
        '~((HOBJECT n_child) <- $gc_nodes(S.GC.BUFFER))',
        'parray_copy = $gc_array_alias_copy(S, n_old)',
        '$entry_lookup(parray_copy.ITEMS, KINT 0) = (ALIAS n_leaf)' if shared else
        '$entry_lookup(parray_copy.ITEMS, KINT 0) = (DIRECT (PINT 17))',
        '$gc_array_header_domain(S, n_old, n_new, n_root)',
        'PhpStep: S ~> S_raw',
        'S_raw.ARRAYS = S.ARRAYS ++ [$array_insert(parray_copy, KINT 0, ALIAS n_acquired)]',
        'S_raw.STORE = $set_cell(S.STORE, n_root, DEFINED (PARRAY n_new))' if shared else
        'S_raw.STORE = $set_cell(S.STORE, n_root, DEFINED (PARRAY n_new)) ++ [DEFINED (PINT 17)]',
        'S_raw.REFCELLS = S.REFCELLS' if shared else 'S_raw.REFCELLS = n_acquired :: S.REFCELLS',
        'S_raw.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY n_new]' if shared else
        'S_raw.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY n_new, HCELL n_acquired]',
        'S_raw.RESULT = KNOWN PNULL', 'S_raw.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_raw.CELL = n_acquired',
        'S_raw.LOCATION = ELEMENT n_new (KINT 0)', 'S_raw.KEY = KINT 0',
        'S_raw.STORE[n_acquired] = DEFINED (PINT 17)',
        '$heap_owners($heap_graph(S_raw), HARRAY n_old) = 1',
        f'$heap_owners($heap_graph(S_raw), HCELL n_acquired) = {5 if shared else 1}',
        '$heap_owners($heap_graph(S_raw), HOBJECT n_child) = 2',
        '$gc_array_alias_reference_image(S_raw, n_old, n_new, n_root, n_acquired, KINT 0)',
        '~$gc_array_reference_image(S_raw, n_old, n_new, n_root, n_acquired, KINT 0)',
        'pgctemporary_live = {OPERAND KNOWN (PARRAY n_old), PENDING true}',
        'pgctemporary_done = pgctemporary_live[.PENDING = false]',
        '$gc_operation_temporary_extra(S, S_raw, ACQUIRE_ARRAY z, [HARRAY n_old]) = [pgctemporary_live]',
        'S_live = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
        'S_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_live) :: ptask_live_tail*',
        'pdestructionrelease_live.JOBS = [DESTRUCTION_TEMP (HARRAY n_old)]',
        'S_live.DESTRUCTION.OPERATIONS = [pdestructionoperation_live]',
        'pdestructionoperation_live.VALUE = KNOWN PNULL',
        'pdestructionoperation_live.CELL = n_acquired',
        'pdestructionoperation_live.NOGCEXTRA = [pgctemporary_live]',
        '$gc_operation_metadata_valid(S_live, pdestructionoperation_live)',
        '$gc_release_metadata_valid(S_live, pdestructionrelease_live)',
        *valid('S_live'),
        '$native_rc(S_live, HARRAY n_old) = 2',
        f'$heap_owners($heap_graph(S_live), HCELL n_acquired) = {5 if shared else 1}',
        'S_live.DESTRUCTION.CALLS = eps',
        '~((HARRAY n_old) <- $gc_nodes(S_live.GC.BUFFER))',
        '~((HOBJECT n_child) <- $gc_nodes(S_live.GC.BUFFER))',
        'S_after = $drive_steps(S_live, 1)[.COMPLETION = NORMAL]',
        'pdestructionoperation_done = pdestructionoperation_live[.NOGCEXTRA = [pgctemporary_done]]',
        'S_after.DESTRUCTION.OPERATIONS = [pdestructionoperation_done]',
        '$gc_operation_metadata_valid(S_after, pdestructionoperation_done)',
        '$native_rc(S_after, HARRAY n_old) = 1',
        '~((HARRAY n_old) <- $gc_nodes(S_after.GC.BUFFER))',
        *valid('S_after'), *budget('S'), *budget('S_live'),
        *seek('S_after', 'S_write', 'WRITE'),
        '$lookup(S_write.ENV, $ptascii("ref")) = (n_acquired)',
        f'$heap_owners($heap_graph(S_write), HCELL n_acquired) = {6 if shared else 2}',
        'S_write.STORE[n_acquired] = DEFINED (PINT 17)',
        *valid('S_write'),
        'PhpStep: S_write ~> S_written',
        'S_written.STORE[n_acquired] = DEFINED (PINT 23)',
        'S_written.DESTRUCTION.CALLS = eps',
    ]


SINGLE_CHECKS = acquire(False) + [
    'n_acquired =/= n_leaf',
    'S_written.STORE[n_leaf] = DEFINED (PINT 17)',
    '$heap_owners($heap_graph(S_written), HCELL n_leaf) = 1',
    # A false merge would change singleton copying into a shared two-edge cell.
    'S_merged = S_raw[.ARRAYS = $array_replace(S_raw.ARRAYS, n_new, $array_insert(S_raw.ARRAYS[n_new], KINT 0, ALIAS n_leaf))]',
    '$heap_owners($heap_graph(S_merged), HCELL n_leaf) = 2',
    '~$gc_array_alias_reference_image(S_merged, n_old, n_new, n_root, n_leaf, KINT 0)',
    *seek('S_write', 'S_ref', 'REF'),
    '~((HARRAY n_new) <- S_ref.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_ref), HCELL n_acquired) = 1',
    *seek('S_ref', 'S_last', 'CELL'),
    'S_last_next = $drive_steps(S_last, 1)[.COMPLETION = NORMAL]',
    '~((HCELL n_acquired) <- S_last_next.ALLOCATIONS)',
    *seek('S_last_next', 'S_view', 'VIEW'),
    'S_view.STORE[n_leaf] = DEFINED (PINT 17)',
    '$heap_owners($heap_graph(S_view), HCELL n_leaf) = 1',
    '$heap_owners($heap_graph(S_view), HOBJECT n_child) = 1',
    *seek('S_view', 'S_array', 'ARRAY'),
    'S_array_next = $drive_steps(S_array, 1)[.COMPLETION = NORMAL]',
    '~((HARRAY n_old) <- S_array_next.ALLOCATIONS)',
    *seek('S_array_next', 'S_leaf', 'CELL', 'n_leaf'),
    'S_leaf_next = $drive_steps(S_leaf, 1)[.COMPLETION = NORMAL]',
    '~((HCELL n_leaf) <- S_leaf_next.ALLOCATIONS)',
    *valid('S_leaf_next'),
]

SHARED_CHECKS = acquire(True) + [
    '$lookup(S.ENV, $ptascii("slot")) = (n_leaf)',
    'S_written.STORE[n_leaf] = DEFINED (PINT 23)',
    '$entry_lookup(S_written.ARRAYS[n_old].ITEMS, KINT 0) = (ALIAS n_leaf)',
    '$entry_lookup(S_written.ARRAYS[n_new].ITEMS, KINT 2) = (ALIAS n_leaf)',
    'S_no_view = S[.ENV = $unbind(S.ENV, $ptascii("view"))]',
    '~$gc_array_header_domain(S_no_view, n_old, n_new, n_root)',
    'S_owning = S[.STORE = $set_cell(S.STORE, n_leaf, DEFINED (POBJECT n_child))]',
    'PhpStep: S_owning ~> S_owning_raw',
    '~$gc_array_alias_reference_image(S_owning_raw, n_old, n_new, n_root, n_acquired, KINT 0)',
    '$gc_operation_temporary_extra(S_owning, S_owning_raw, ACQUIRE_ARRAY z, [HARRAY n_old]) = eps',
    'S_unit = S_raw[.NATIVEEXCESS = [HCELL n_leaf]]',
    '~$gc_array_alias_reference_image(S_unit, n_old, n_new, n_root, n_acquired, KINT 0)',
]
for name, patch in {
    'source': '[.SOURCE = DISCARD]',
    'reference': '[.CELL = n_root]',
    'location': '[.LOCATION = ELEMENT n_old (KINT 0)]',
    'key': '[.KEY = KINT 1]',
    'value': '[.VALUE = REFERENCE n_leaf]',
    'progress': '[.NOGCEXTRA = [pgctemporary_done]]',
}.items():
    SHARED_CHECKS += [f'pdestructionoperation_bad_{name} = pdestructionoperation_live{patch}',
                      f'S_bad_{name} = $gc82_op(S_live, pdestructionoperation_bad_{name})',
                      f'~$gc_operation_metadata_valid(S_bad_{name}, pdestructionoperation_bad_{name})']
SHARED_CHECKS += [
    'S_no_view_live = S_live[.ENV = $unbind(S_live.ENV, $ptascii("view"))]',
    '~$gc_operation_metadata_valid(S_no_view_live, pdestructionoperation_live)',
    *seek('S_write', 'S_ref', 'REF'),
    '$heap_owners($heap_graph(S_ref), HCELL n_acquired) = 6',
    *seek('S_ref', 'S_value', 'CELL'),
    'S_value.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_value) :: ptask_value_tail*',
    'pdestructionrelease_value.JOBS = [DESTRUCTION_VALUE (HCELL n_acquired)]',
    'S_value_next = $drive_steps(S_value, 1)[.COMPLETION = NORMAL]',
    '$heap_owners($heap_graph(S_value_next), HCELL n_acquired) = 5',
    'S_value_next.DESTRUCTION.CALLS = eps',
    *valid('S_value_next'),
    *seek('S_value_next', 'S_slot', 'SLOT'),
    '~((HARRAY n_old) <- S_slot.ALLOCATIONS)',
    '~((HARRAY n_new) <- S_slot.ALLOCATIONS)',
    '~((HOBJECT n_child) <- S_slot.ALLOCATIONS)',
    'n_child <- S_slot.DESTRUCTION.CALLED',
    '$heap_owners($heap_graph(S_slot), HCELL n_acquired) = 1',
    *seek('S_slot', 'S_last', 'CELL'),
    'S_last_next = $drive_steps(S_last, 1)[.COMPLETION = NORMAL]',
    '~((HCELL n_acquired) <- S_last_next.ALLOCATIONS)',
    'S_done = $drive_steps(S_last_next, 3000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    'S_done.NATIVEEXCESS = eps',
    '$gc82_output(S_done.EVENTS) = $ptascii("B|Q|0|A|W|23|23|23|23|23|R|K|D|V|23|F|G|0|E|S|")',
    *valid('S_done'),
]

review.CASES = {
    'ordinary-singleton-alias-acquire-fresh-cell': {'source': SINGLE, 'stage': COMMON + '-- if S.ARRAYS[n_old].ITEMS = ' + SINGLE_ROW, 'checks': SINGLE_CHECKS},
    'ordinary-shared-alias-acquire-reused-cell': {'source': SHARED, 'stage': COMMON + '-- if S.ARRAYS[n_old].ITEMS = ' + SHARED_ROW, 'checks': SHARED_CHECKS},
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
