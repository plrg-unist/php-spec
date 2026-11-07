#!/usr/bin/env python3
"""Singleton unwrapping and shared owning-ALIA payload retirement."""
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
SHARED = (ROOT / 'tests/semantics/gc77_shared_owning_alias.php').read_text()
SINGLETON = (ROOT / 'tests/semantics/gc77_singleton_owning_alias.php').read_text()
DECLARATIONS = r'''syntax pgc77phase = ENTER | ACTIVE | READ | EXIT
 dec $gc77_output(pevent*) : preqbytes
 dec $gc77_at(pstate, pgc77phase, nat) : bool
 def $gc77_at(S, ENTER, n_child) = true
   -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail*
   -- if pdestructorcall.OBJECT = n_child
 def $gc77_at(S, ACTIVE, n_child) = true
   -- if S.CURRENT = (pcallcontext)
   -- if S.DESTRUCTION.CALLS = [pdestructorcall]
   -- if pdestructorcall.OBJECT = n_child /\ pcallcontext.TARGET = pdestructorcall.TARGET
 def $gc77_at(S, READ, n_child) = true
   -- if $gc77_at(S, ACTIVE, n_child)
   -- if $gc77_output(S.EVENTS) = $ptascii("B|O|N|1|gc77SharedTarget|D|")
 def $gc77_at(S, EXIT, n_child) = true
   -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
   -- if pdestructionoperation.SOURCE = ASSIGN_ARRAY pbase z false
   -- if pdestructionoperation.NOGCEXTRA = [{OPERAND KNOWN (PARRAY n_old), PENDING false}]
 def $gc77_at(S, pgc77phase, n_child) = false -- otherwise
 dec $gc77_seek(pstate, pgc77phase, nat, nat) : pstate
 def $gc77_seek(S, pgc77phase, n_child, n) = S
   -- if $gc77_at(S, pgc77phase, n_child)
 def $gc77_seek(S, pgc77phase, n_child, n) = $gc77_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc77phase, n_child, $nabs($(n - 1)))
   -- if ~$gc77_at(S, pgc77phase, n_child) /\ $(n > 0)
   -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
 def $gc77_seek(S, pgc77phase, n_child, 0) = S
   -- if ~$gc77_at(S, pgc77phase, n_child)
 def $gc77_seek(S, pgc77phase, n_child, n) = S
   -- if ~$gc77_at(S, pgc77phase, n_child)
   -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
 dec $gc77_op(pstate, pdestructionoperation, pdestructionoperation) : pstate
 def $gc77_op(S, pdestructionoperation, pdestructionoperation_new) = S[.TODO = $destructor_operation_tasks(S.TODO, pdestructionoperation, pdestructionoperation_new)][.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]]
 dec $gc77_call(pstate, pdestructorcall, pdestructorcall) : pstate
 def $gc77_call(S, pdestructorcall, pdestructorcall_new) = S[.DESTRUCTION.CALLS = [pdestructorcall_new]][.FRAMES = [pframe[.TODO = (DESTRUCTOR_RESULT pdestructorcall_new) :: ptask_tail*]]]
   -- if S.FRAMES = [pframe]
   -- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_tail*
 def $gc77_output(eps) = eps
 def $gc77_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc77_output(pevent_tail*)
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


def budget(state):
    return [f'$drive_steps({state}, 0) = {state}[.COMPLETION = BUDGET]',
            f'$drive_steps({state}, 2) = $drive_steps($drive_steps({state}, 1)[.COMPLETION = NORMAL], 1)']


def seek(before, after, phase):
    return [f'{after}_pause = $gc77_seek({before}, {phase}, n_child, 2000)',
            f'{after}_pause.COMPLETION = NORMAL \\/ {after}_pause.COMPLETION = BUDGET',
            f'{after} = {after}_pause[.COMPLETION = NORMAL]',
            f'$gc77_at({after}, {phase}, n_child)']


COMMON_STAGE = (
    'S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail* '
    '-- if S.RESULT = KNOWN (PINT 23) '
    '-- if $lookup(S.ENV, $ptascii("kept")) = (n_root) '
    '-- if S.STORE[n_root] = DEFINED (PARRAY n_old) '
    '-- if S.NATIVEEXCESS = [HARRAY n_old] ')
SHARED_STAGE = COMMON_STAGE + (
    '-- if $lookup(S.ENV, $ptascii("slot")) = (n_leaf) '
    '-- if S.STORE[n_leaf] = DEFINED (POBJECT n_child) '
    '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) (DIRECT (PINT 17)), ENTRY (KINT 2) (ALIAS n_leaf)]')
SHARED_CHECKS = [
    *valid('S'), 'n_new = |S.ARRAYS|',
    '$heap_owners($heap_graph(S), HARRAY n_old) = 1',
    '$native_rc(S, HARRAY n_old) = 2',
    '$heap_owners($heap_graph(S), HCELL n_leaf) = 3',
    '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
    '$enum_is_callable_array_excess_entries(S, S.ARRAYS[n_old].ITEMS)',
    '$gc_array_alias_row(S, S.ARRAYS[n_old].ITEMS)',
    '$gc_array_alias_copy(S, n_old) = S.ARRAYS[n_old]',
    'S_leaf_unit = S[.NATIVEEXCESS = [HARRAY n_old, HCELL n_leaf]]',
    '~$enum_is_callable_array_excess_entries(S_leaf_unit, S_leaf_unit.ARRAYS[n_old].ITEMS)',
    'S_child_unit = S[.NATIVEEXCESS = [HARRAY n_old, HOBJECT n_child]]',
    '~$enum_is_callable_array_excess_entries(S_child_unit, S_child_unit.ARRAYS[n_old].ITEMS)',
    'S_called = S[.DESTRUCTION.CALLED = S.DESTRUCTION.CALLED ++ [n_child]]',
    '~$enum_is_callable_array_excess_entries(S_called, S_called.ARRAYS[n_old].ITEMS)',
    'S_array_payload = S[.STORE = $set_cell(S.STORE, n_leaf, DEFINED (PARRAY n_old))]',
    '~$enum_is_callable_array_excess_entries(S_array_payload, S_array_payload.ARRAYS[n_old].ITEMS)',
    'PhpStep: S ~> S_raw',
    'S_raw.ARRAYS = S.ARRAYS ++ [S.ARRAYS[n_old]]',
    'S_raw.STORE = $set_cell($set_cell(S.STORE, n_root, DEFINED (PARRAY n_new)), n_leaf, DEFINED (PINT 23))',
    'S_raw.NATIVEEXCESS = [HARRAY n_old]',
    '$heap_owners($heap_graph(S_raw), HCELL n_leaf) = 5',
    '$heap_owners($heap_graph(S_raw), HOBJECT n_child) = 0',
    '$eager_slots(S, S_raw) = [HARRAY n_old, HOBJECT n_child]',
    '$gc_array_copy_decrements(S, S_raw) = eps',
    'pgctemporary_live = {OPERAND KNOWN (PARRAY n_old), PENDING true}',
    'pgctemporary_done = pgctemporary_live[.PENDING = false]',
    '$gc_operation_temporary_extra(S, S_raw, ASSIGN_ARRAY pbase z false, [HARRAY n_old, HOBJECT n_child]) = [pgctemporary_live]',
    '$gc_operation_temporary_extra(S[.ORIGIN = eps], S_raw[.ORIGIN = eps], ASSIGN_ARRAY pbase z false, [HARRAY n_old, HOBJECT n_child]) = eps',
    '$gc_operation_temporary_extra(S, S_raw[.KEY = KINT 2], ASSIGN_ARRAY pbase z false, [HARRAY n_old, HOBJECT n_child]) = eps',
    'S_live = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_live) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_live) :: ptask_tail*',
    'pdestructionrelease_live.JOBS = [DESTRUCTION_TEMP (HARRAY n_old), DESTRUCTION_VALUE (HOBJECT n_child)]',
    'S_live.DESTRUCTION.OPERATIONS = [pdestructionoperation_live]',
    'pdestructionoperation_live.NOGC = eps',
    'pdestructionoperation_live.NOGCEXTRA = [pgctemporary_live]',
    '$gc_operation_metadata_valid(S_live, pdestructionoperation_live)',
    '$gc_release_metadata_valid(S_live, pdestructionrelease_live)',
    '$heap_owners($heap_graph(S_live), HARRAY n_old) = 1',
    '$heap_owners($heap_graph(S_live), HCELL n_leaf) = 5',
    '$heap_owners($heap_graph(S_live), HOBJECT n_child) = 1',
    *valid('S_live'),
]
for suffix, edit in {
    'origin': '.ORIGIN = eps',
    'cell': '.CELL = n_leaf',
    'key': '.KEY = KINT 1',
    'location': '.LOCATION = ELEMENT n_old (KINT 0)',
    'operand': '.NOGCEXTRA = [{OPERAND KNOWN (PARRAY n_new), PENDING true}]',
    'progress': '.NOGCEXTRA = [pgctemporary_done]',
    'tail': '.NOGCEXTRA = [pgctemporary_live, pgctemporary_live]',
}.items():
    SHARED_CHECKS += [f'pdestructionoperation_bad_{suffix} = pdestructionoperation_live[{edit}]',
                      f'S_bad_{suffix} = $gc77_op(S_live, pdestructionoperation_live, pdestructionoperation_bad_{suffix})',
                      f'$heap_graph(S_bad_{suffix}) = $heap_graph(S_live)',
                      f'~$gc_operation_metadata_valid(S_bad_{suffix}, pdestructionoperation_bad_{suffix})']
SHARED_CHECKS += [
    'S_unit_bad = S_live[.NATIVEEXCESS = eps]',
    '~$gc_operation_metadata_valid(S_unit_bad, pdestructionoperation_live)',
    # The actual old-header GC root may preexist. Remove only that canonical
    # buffer entry to discriminate the new mixed TEMP's no-visit behavior.
    'S_unbuffered = S[.GC = $gc_buffer_remove(S.GC, HARRAY n_old)]',
    *valid('S_unbuffered'),
    'S_u_live = $drive_steps(S_unbuffered, 1)[.COMPLETION = NORMAL]',
    'S_u_after = $drive_steps(S_u_live, 1)[.COMPLETION = NORMAL]',
    '~((HARRAY n_old) <- $gc_nodes(S_u_after.GC.BUFFER))',
    '$heap_owners($heap_graph(S_u_after), HARRAY n_old) = 0',
    '$native_rc(S_u_after, HARRAY n_old) = 1',
    'S_after = $drive_steps(S_live, 1)[.COMPLETION = NORMAL]',
    'pdestructionoperation_done = pdestructionoperation_live[.NOGCEXTRA = [pgctemporary_done]]',
    'S_after.DESTRUCTION.OPERATIONS = [pdestructionoperation_done]',
    '$gc_operation_metadata_valid(S_after, pdestructionoperation_done)',
    '$heap_owners($heap_graph(S_after), HARRAY n_old) = 0',
    '$heap_owners($heap_graph(S_after), HOBJECT n_child) = 1',
    *valid('S_after'), *budget('S'), *budget('S_live'),
    *seek('S_after', 'S_enter', 'ENTER'),
    'S_enter.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_enter_tail*',
    'pdestructorcall.OBJECT = n_child',
    'pdestructorcall.OPERATION = (pdestructionoperation_done)',
    'pdestructorcall.RELEASE = (pdestructionrelease_child)',
    'pdestructionrelease_child.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child)]',
    '$heap_owners($heap_graph(S_enter), HOBJECT n_child) = 2',
    *valid('S_enter'),
    *seek('S_enter', 'S_active', 'ACTIVE'),
    'S_active.FRAMES = [pframe]',
    'pframe.LOCALS = eps', 'pframe.CONTEXT = eps',
    'pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_done) :: ptask_tail*',
    'pdestructionrelease_empty = pdestructionrelease_child[.JOBS = eps]',
    '$gc_array_alias_callback_site(S_active, pdestructionoperation_done)',
    '$gc_operation_metadata_valid(S_active, pdestructionoperation_done)',
    '$heap_owners($heap_graph(S_active), HARRAY n_old) = 0',
    '$heap_owners($heap_graph(S_active), HOBJECT n_child) = 2',
    '$heap_owners($heap_graph(S_active), HCELL n_leaf) = 5',
    *valid('S_active'),
    'pdestructorcall_bad_origin = pdestructorcall[.ORIGIN = eps]',
    'S_call_origin = $gc77_call(S_active, pdestructorcall, pdestructorcall_bad_origin)',
    '$heap_graph(S_call_origin) = $heap_graph(S_active)',
    '~$gc_array_alias_callback_site(S_call_origin, pdestructionoperation_done)',
    '~$gc_operation_metadata_valid(S_call_origin, pdestructionoperation_done)',
    'pdestructorcall_bad_op = pdestructorcall[.OPERATION = eps]',
    'S_call_op = $gc77_call(S_active, pdestructorcall, pdestructorcall_bad_op)',
    '$heap_graph(S_call_op) = $heap_graph(S_active)',
    '~$gc_operation_metadata_valid(S_call_op, pdestructionoperation_done)',
    'S_active.CURRENT = (pcallcontext)',
    'S_no_receiver = S_active[.CURRENT = (pcallcontext[.RECEIVER = eps])]',
    '~$gc_array_alias_callback_site(S_no_receiver, pdestructionoperation_done)',
    *seek('S_active', 'S_read', 'READ'),
    '$lookup(S_read.ENV, $ptascii("kept")) = (n_root)',
    '$lookup(S_read.ENV, $ptascii("slot")) = (n_leaf)',
    'S_read.STORE[n_leaf] = DEFINED (PINT 23)',
    'S_read.ARRAYS[n_old] = S.ARRAYS[n_old]',
    'S_read.ARRAYS[n_new] = S.ARRAYS[n_old]',
    '~$enum_is_callable_output_excess_child(S_read, n_child)',
    '$gc_array_alias_callback_site(S_read, pdestructionoperation_done)',
    '$gc_operation_metadata_valid(S_read, pdestructionoperation_done)',
    *valid('S_read'), *budget('S_read'),
    *seek('S_read', 'S_exit', 'EXIT'),
    'S_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_done) :: ptask_tail*',
    'S_exit.CURRENT = eps', 'S_exit.FRAMES = eps',
    '~((HOBJECT n_child) <- S_exit.ALLOCATIONS)',
    'n_child <- S_exit.DESTRUCTION.CALLED',
    '$gc_operation_metadata_valid(S_exit, pdestructionoperation_done)',
    *valid('S_exit'), *budget('S_exit'),
    'S_done = $drive_steps(S_exit, 3000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    'S_done.NATIVEEXCESS = [HARRAY n_old]',
    '(HARRAY n_old) <- S_done.ALLOCATIONS',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    'S_done.STORE[n_leaf] = DEFINED (PINT 23)',
    '$heap_owners($heap_graph(S_done), HCELL n_leaf) = 2',
    '$gc77_output(S_done.EVENTS) = $ptascii("B|O|N|1|gc77SharedTarget|D|23|23|23|W|23|23|23|U|G|0|E|S|")',
    *valid('S_done'),
]

SINGLETON_STAGE = COMMON_STAGE + (
    '-- if S.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) (DIRECT (PINT 17))] '
    '-- if S.STORE[n_leaf] = DEFINED (POBJECT n_child) '
    '-- if $object_name(S, n_child) = $ptascii("GC77ChildAuthor")')
SINGLETON_CHECKS = [
    *valid('S'), 'n_new = |S.ARRAYS|',
    '$heap_owners($heap_graph(S), HCELL n_leaf) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
    '$native_rc(S, HARRAY n_old) = 2',
    '$gc_array_alias_row(S, S.ARRAYS[n_old].ITEMS)',
    'parray_copy = $gc_array_alias_copy(S, n_old)',
    'parray_copy.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_child)), ENTRY (KINT 1) (DIRECT (PINT 17))]',
    'PhpStep: S ~> S_raw',
    'S_raw.ARRAYS[n_old] = S.ARRAYS[n_old]',
    'S_raw.STORE[n_leaf] = DEFINED (POBJECT n_child)',
    'S_raw.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 23)), ENTRY (KINT 1) (DIRECT (PINT 17))]',
    '$heap_owners($heap_graph(S_raw), HCELL n_leaf) = 1',
    '$heap_owners($heap_graph(S_raw), HOBJECT n_child) = 1',
    '$eager_slots(S, S_raw) = [HARRAY n_old]',
    '$gc_array_copy_decrements(S, S_raw) = [HOBJECT n_child]',
    '$gc_same_location(S, S_raw) = [HOBJECT n_child]',
    'pgctemporary_live = {OPERAND KNOWN (PARRAY n_old), PENDING true}',
    '$gc_operation_temporary_extra(S, S_raw, ASSIGN_ARRAY pbase z false, [HARRAY n_old]) = [pgctemporary_live]',
    'S_live = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_live) :: ptask_live_tail*',
    'pdestructionrelease_live.JOBS = [DESTRUCTION_TEMP (HARRAY n_old)]',
    'S_live.DESTRUCTION.OPERATIONS = [pdestructionoperation_live]',
    '$gc_operation_metadata_valid(S_live, pdestructionoperation_live)',
    '$gc_release_metadata_valid(S_live, pdestructionrelease_live)',
    *valid('S_live'),
    # The genuine local reference unset may already buffer Child. This valid
    # canonical counterimage isolates the newly admitted copied-ALIA target.
    'S_unbuffered = S[.GC = $gc_buffer_remove(S.GC, HOBJECT n_child)]',
    *valid('S_unbuffered'),
    'S_u_live = $drive_steps(S_unbuffered, 1)[.COMPLETION = NORMAL]',
    'pgc_copy = $gc_buffer_add(S_unbuffered.GC, HOBJECT n_child)',
    'S_u_live.GC.BUFFER = pgc_copy.BUFFER',
    '$heap_count(HOBJECT n_child, $gc_nodes(S_u_live.GC.BUFFER)) = 1',
    'S_after = $drive_steps(S_live, 1)[.COMPLETION = NORMAL]',
    '$heap_owners($heap_graph(S_after), HARRAY n_old) = 0',
    '$native_rc(S_after, HARRAY n_old) = 1',
    '$heap_owners($heap_graph(S_after), HCELL n_leaf) = 1',
    '$heap_owners($heap_graph(S_after), HOBJECT n_child) = 1',
    '~(n_child <- S_after.DESTRUCTION.CALLED)',
    'S_after.DESTRUCTION.CALLS = eps',
    '$gc_operation_metadata_valid(S_after, S_after.DESTRUCTION.OPERATIONS[0])',
    *valid('S_after'), *budget('S'), *budget('S_live'),
]

# These constructed physical counterstates add real existing graph owners or
# entries; they provide no additional PHP-source agreement credit.
EXTENSION_CHECKS = [
    *valid('S'), 'n_new = |S.ARRAYS|',
    'S_clean = S[.GC = $gc_buffer_remove_nodes(S.GC, [HARRAY n_old, HOBJECT n_child])]',
    *valid('S_clean'),
    'PhpStep: S_clean ~> S_clean_raw',
    'pgctemporary_live = {OPERAND KNOWN (PARRAY n_old), PENDING true}',
    '$gc_operation_temporary_extra(S_clean, S_clean_raw, ASSIGN_ARRAY pbase z false, [HARRAY n_old, HOBJECT n_child]) = [pgctemporary_live]',
    '$gc_operation_temporary_extra(S_clean, S_clean_raw, ASSIGN_ARRAY pbase z false, [HOBJECT n_child, HARRAY n_old]) = [pgctemporary_live]',
    'S_begin_forward = $eager_operation_begin(S_clean_raw, S_clean, ASSIGN_ARRAY pbase z false, [HARRAY n_old, HOBJECT n_child])',
    'S_begin_reverse = $eager_operation_begin(S_clean_raw, S_clean, ASSIGN_ARRAY pbase z false, [HOBJECT n_child, HARRAY n_old])',
    'S_begin_reverse = S_begin_forward',
    'S_begin_forward.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
    '$gc_operation_jobs(pdestructionoperation, [HARRAY n_old, HOBJECT n_child]) = [DESTRUCTION_TEMP (HARRAY n_old), DESTRUCTION_VALUE (HOBJECT n_child)]',
    '$gc_operation_jobs(pdestructionoperation, [HOBJECT n_child, HARRAY n_old]) = [DESTRUCTION_TEMP (HARRAY n_old), DESTRUCTION_VALUE (HOBJECT n_child)]',
    # Other EXTRA producers retain their own input order.
    'pdestructionoperation_binary = pdestructionoperation[.SOURCE = BINARY_RIGHT IDENTICAL (KNOWN (POBJECT n_child)) 0]',
    '$gc_operation_jobs(pdestructionoperation_binary, [HOBJECT n_child, HARRAY n_old]) = [DESTRUCTION_VALUE (HOBJECT n_child), DESTRUCTION_TEMP (HARRAY n_old)]',
    *valid('S_begin_reverse'),
    # One additional physical strong owner makes the payload loss nonlast.
    'S_nonlast = S_clean[.HELD = S_clean.HELD ++ [HOBJECT n_child]]',
    *valid('S_nonlast'),
    '$heap_owners($heap_graph(S_nonlast), HOBJECT n_child) = 2',
    'PhpStep: S_nonlast ~> S_nonlast_raw',
    '$heap_owners($heap_graph(S_nonlast_raw), HOBJECT n_child) = 1',
    '$eager_slots(S_nonlast, S_nonlast_raw) = [HARRAY n_old, HOBJECT n_child]',
    '$gc_operation_temporary_extra(S_nonlast, S_nonlast_raw, ASSIGN_ARRAY pbase z false, [HARRAY n_old, HOBJECT n_child]) = [pgctemporary_live]',
    '$gc_array_copy_decrements(S_nonlast, S_nonlast_raw) = eps',
    'S_nonlast_live = $drive_steps(S_nonlast, 1)[.COMPLETION = NORMAL]',
    'S_nonlast_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_nonlast) :: ptask_nonlast_tail*',
    'pdestructionrelease_nonlast.JOBS = [DESTRUCTION_TEMP (HARRAY n_old), DESTRUCTION_VALUE (HOBJECT n_child)]',
    '$heap_owners($heap_graph(S_nonlast_live), HOBJECT n_child) = 2',
    '$gc_array_copy_decrements(S_nonlast, S_nonlast_live) = eps',
    '~((HOBJECT n_child) <- $gc_nodes(S_nonlast_live.GC.BUFFER))',
    *valid('S_nonlast_live'),
    'S_nonlast_header = $drive_steps(S_nonlast_live, 1)[.COMPLETION = NORMAL]',
    'S_nonlast_header.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_payload) :: ptask_payload_tail*',
    'pdestructionrelease_payload.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child)]',
    '$heap_owners($heap_graph(S_nonlast_header), HARRAY n_old) = 0',
    '$heap_owners($heap_graph(S_nonlast_header), HOBJECT n_child) = 2',
    '~((HARRAY n_old) <- $gc_nodes(S_nonlast_header.GC.BUFFER))',
    '~((HOBJECT n_child) <- $gc_nodes(S_nonlast_header.GC.BUFFER))',
    *valid('S_nonlast_header'),
    'S_nonlast_after = $drive_steps(S_nonlast_header, 1)[.COMPLETION = NORMAL]',
    '$heap_owners($heap_graph(S_nonlast_after), HOBJECT n_child) = 1',
    'pgc_payload = $gc_buffer_add(S_nonlast_header.GC, HOBJECT n_child)',
    'S_nonlast_after.GC.BUFFER = pgc_payload.BUFFER',
    '$heap_count(HOBJECT n_child, $gc_nodes(S_nonlast_after.GC.BUFFER)) = 1',
    '~((HARRAY n_old) <- $gc_nodes(S_nonlast_after.GC.BUFFER))',
    'S_nonlast_after.DESTRUCTION.CALLS = eps',
    '~(n_child <- S_nonlast_after.DESTRUCTION.CALLED)',
    *valid('S_nonlast_after'), *budget('S_nonlast_live'),
    # A copied DIRECT sibling adds the very Child edge lost by store-through.
    'S_sibling = S_clean[.ARRAYS = $array_replace(S_clean.ARRAYS, n_old, $array_insert(S_clean.ARRAYS[n_old], KINT 3, DIRECT (POBJECT n_child)))]',
    *valid('S_sibling'),
    '$gc_array_alias_row(S_sibling, S_sibling.ARRAYS[n_old].ITEMS)',
    '$heap_owners($heap_graph(S_sibling), HOBJECT n_child) = 2',
    'parray_copy = $gc_array_alias_copy(S_sibling, n_old)',
    '$entry_lookup(parray_copy.ITEMS, KINT 0) = (ALIAS n_leaf)',
    '$heap_count(HOBJECT n_child, $entries_nodes(parray_copy.ITEMS)) = 1',
    'PhpStep: S_sibling ~> S_sibling_raw',
    '$heap_owners($heap_graph(S_sibling_raw), HOBJECT n_child) = 2',
    '$eager_slots(S_sibling, S_sibling_raw) = [HARRAY n_old]',
    '$gc_array_copy_decrements(S_sibling, S_sibling_raw) = [HOBJECT n_child]',
    'S_sibling_live = $drive_steps(S_sibling, 1)[.COMPLETION = NORMAL]',
    'S_sibling_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_sibling) :: ptask_sibling_tail*',
    'pdestructionrelease_sibling.JOBS = [DESTRUCTION_TEMP (HARRAY n_old)]',
    '$gc_array_copy_decrements(S_sibling, S_sibling_live) = [HOBJECT n_child]',
    'pgc_sibling = $gc_buffer_add(S_sibling.GC, HOBJECT n_child)',
    'S_sibling_live.GC.BUFFER = pgc_sibling.BUFFER',
    '$heap_count(HOBJECT n_child, $gc_nodes(S_sibling_live.GC.BUFFER)) = 1',
    '$heap_owners($heap_graph(S_sibling_live), HOBJECT n_child) = 2',
    '~(n_child <- S_sibling_live.DESTRUCTION.CALLED)',
    *valid('S_sibling_live'),
    'S_sibling_after = $drive_steps(S_sibling_live, 1)[.COMPLETION = NORMAL]',
    'S_sibling_after.GC.BUFFER = S_sibling_live.GC.BUFFER',
    '$heap_owners($heap_graph(S_sibling_after), HARRAY n_old) = 0',
    '$heap_owners($heap_graph(S_sibling_after), HOBJECT n_child) = 2',
    'S_sibling_after.DESTRUCTION.CALLS = eps',
    *valid('S_sibling_after'), *budget('S_sibling_live'),
]

review.CASES = {
    'shared-alias-real-payload-callback-and-header-temp': {
        'source': SHARED, 'stage': SHARED_STAGE, 'checks': SHARED_CHECKS},
    'singleton-alias-unwrapping-and-copied-target': {
        'source': SINGLETON, 'stage': SINGLETON_STAGE, 'checks': SINGLETON_CHECKS},
    'shared-alias-additional-count-and-native-order': {
        'source': SHARED, 'stage': SHARED_STAGE, 'checks': EXTENSION_CHECKS},
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
