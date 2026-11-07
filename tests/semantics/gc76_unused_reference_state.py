#!/usr/bin/env python3
"""Unused reference-result TEMP and genuine reference-CV decrement."""
from pathlib import Path

import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc76_unused_reference_peer.php').read_text()
STAGE = (
    'S.TODO = DISCARD :: ptask_tail* -- if S.RESULT = REFERENCE n_reference '
    '-- if $lookup(S.ENV, $ptascii("ref")) = (n_reference) '
    '-- if $lookup(S.ENV, $ptascii("a")) = (n_root) '
    '-- if S.STORE[n_root] = DEFINED (PARRAY n_array) '
    '-- if S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_reference), ENTRY (KINT 1) (DIRECT (PINT 17))] '
    '-- if S.STORE[n_reference] = DEFINED (POBJECT n_child) '
    '-- if $object_name(S, n_child) = $ptascii("GC76PeerChild")')
DECLARATIONS = r'''syntax pgc76stage = UNSET | WRITE
 dec $gc76_at(pstate, pgc76stage) : bool
 def $gc76_at(S, UNSET) = true
   -- if S.TODO = (UNSET (NExprVariable (BYTES text) metadata)) :: ptask_tail*
   -- if $base64(text) = $ptascii("ref")
 def $gc76_at(S, WRITE) = true
   -- if S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail*
   -- if S.RESULT = KNOWN (PINT 23)
 def $gc76_at(S, pgc76stage) = false -- otherwise
 dec $gc76_seek(pstate, pgc76stage, nat) : pstate
 def $gc76_seek(S, pgc76stage, n) = S
   -- if $gc76_at(S, pgc76stage)
 def $gc76_seek(S, pgc76stage, n) = $gc76_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc76stage, $nabs($(n - 1)))
   -- if ~$gc76_at(S, pgc76stage) /\ $(n > 0)
   -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
 def $gc76_seek(S, pgc76stage, 0) = S
   -- if ~$gc76_at(S, pgc76stage)
 def $gc76_seek(S, pgc76stage, n) = S
   -- if ~$gc76_at(S, pgc76stage)
   -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
 dec $gc76_op(pstate, pdestructionoperation, pdestructionoperation) : pstate
 def $gc76_op(S, pdestructionoperation, pdestructionoperation_new) = S[.TODO = $destructor_operation_tasks(S.TODO, pdestructionoperation, pdestructionoperation_new)][.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]]
 dec $gc76_output(pevent*) : preqbytes
 def $gc76_output(eps) = eps
 def $gc76_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc76_output(pevent_tail*)
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


def seek(before, after, stage):
    return [f'{after}_paused = $gc76_seek({before}, {stage}, 2000)',
            f'{after}_paused.COMPLETION = NORMAL \\/ {after}_paused.COMPLETION = BUDGET',
            f'{after} = {after}_paused[.COMPLETION = NORMAL]',
            f'$gc76_at({after}, {stage})']


CHECKS = [
    *valid('S'), 'S.NATIVEEXCESS = eps',
    '$heap_owners($heap_graph(S), HCELL n_reference) = 3',
    '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
    '~((HOBJECT n_child) <- $gc_nodes(S.GC.BUFFER))',
    '~((HARRAY n_array) <- $gc_nodes(S.GC.BUFFER))',
    '$gc_reference_discard_site(S, S.ORIGIN, n_reference)',
    'pgctemporary_live = {OPERAND REFERENCE n_reference, PENDING true}',
    'pgctemporary_done = pgctemporary_live[.PENDING = false]',
    # Generic DISCARD/BINARY operand maps do not gain reference admission.
    '$gc_temporary_node(REFERENCE n_reference) = eps',
    '~$gc_extra_bounded(S, [pgctemporary_live])',
    '~$gc_extra_source(REFERENCE n_reference, [pgctemporary_live])',
    '$gc_extra_pending_nodes([pgctemporary_live]) = [HCELL n_reference]',
    '$gc_extra_advance([pgctemporary_live], HCELL n_reference) = [pgctemporary_done]',
    '$gc_extra_advance([pgctemporary_done], HCELL n_reference) = [pgctemporary_done]',
    '~$gc_extra_consumed([pgctemporary_live], HCELL n_reference)',
    '$gc_extra_consumed([pgctemporary_done], HCELL n_reference)',
    'PhpStep: S ~> S_raw',
    'S_raw = S[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    '$heap_owners($heap_graph(S_raw), HCELL n_reference) = 2',
    '$heap_owners($heap_graph(S_raw), HOBJECT n_child) = 1',
    '$eager_slots(S, S_raw) = [HCELL n_reference]',
    '$gc_operation_temporary_extra(S, S_raw, DISCARD, [HCELL n_reference]) = [pgctemporary_live]',
    '$gc_operation_temporary_extra(S, S_raw, DISCARD, [HOBJECT n_child]) = eps',
    '$gc_operation_temporary_extra(S, S_raw[.RESULT = KNOWN (PINT 17)], DISCARD, [HCELL n_reference]) = eps',
    '$gc_operation_temporary_extra(S[.ORIGIN = eps], S_raw[.ORIGIN = eps], DISCARD, [HCELL n_reference]) = eps',
    'S_held = S[.HELD = S.HELD ++ [HCELL n_reference]]',
    'S_held_raw = S_raw[.HELD = S_held.HELD]',
    '$heap_valid($heap_graph(S_held))',
    '$heap_owners($heap_graph(S_held), HCELL n_reference) = 4',
    '$gc_operation_temporary_extra(S_held, S_held_raw, DISCARD, [HCELL n_reference]) = [pgctemporary_live]',
    'S_live = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
    'S_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_live) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_live) :: ptask_tail*',
    'pdestructionrelease_live.JOBS = [DESTRUCTION_TEMP (HCELL n_reference)]',
    'S_live.DESTRUCTION.OPERATIONS = [pdestructionoperation_live]',
    'pdestructionoperation_live.SOURCE = DISCARD',
    'pdestructionoperation_live.VALUE = KNOWN PNULL',
    'pdestructionoperation_live.BASE = BASE_VALUE (KNOWN PNULL)',
    'pdestructionoperation_live.CELL = n_reference',
    'pdestructionoperation_live.KEY = KINT 0',
    'pdestructionoperation_live.LOCATION = ELEMENT n_array (KINT 0)',
    'pdestructionoperation_live.NOGC = eps',
    'pdestructionoperation_live.NOGCEXTRA = [pgctemporary_live]',
    '$gc_operation_jobs(pdestructionoperation_live, [HCELL n_reference]) = [DESTRUCTION_TEMP (HCELL n_reference)]',
    '$gc_operation_metadata_valid(S_live, pdestructionoperation_live)',
    '$gc_release_metadata_valid(S_live, pdestructionrelease_live)',
    '$heap_owners($heap_graph(S_live), HCELL n_reference) = 3',
    '$heap_owners($heap_graph(S_live), HOBJECT n_child) = 1',
    'S_live.GC.BUFFER = S.GC.BUFFER',
    *valid('S_live'),
    '$destructor_release_replace(S_live, pdestructionrelease_live) = S_live',
]

for suffix, edit in {
    'origin': '.ORIGIN = eps',
    'cell': '.CELL = n_root',
    'key': '.KEY = KINT 1',
    'location': '.LOCATION = ROOT n_root',
    'progress': '.NOGCEXTRA = [pgctemporary_done]',
    'operand': '.NOGCEXTRA = [{OPERAND REFERENCE n_root, PENDING true}]',
    'tail': '.NOGCEXTRA = [pgctemporary_live, pgctemporary_live]',
    'value': '.VALUE = KNOWN (PINT 17)',
}.items():
    CHECKS += [f'pdestructionoperation_{suffix} = pdestructionoperation_live[{edit}]',
               f'S_forged_{suffix} = $gc76_op(S_live, pdestructionoperation_live, pdestructionoperation_{suffix})',
               f'$heap_graph(S_forged_{suffix}) = $heap_graph(S_live)',
               f'~$gc_operation_metadata_valid(S_forged_{suffix}, pdestructionoperation_{suffix})']

CHECKS += [
    'S_extra_owner = S_live[.ARRAYS = $array_replace(S_live.ARRAYS, n_array, $array_insert(S_live.ARRAYS[n_array], KINT 2, ALIAS n_reference))]',
    '$heap_valid($heap_graph(S_extra_owner))',
    '$heap_owners($heap_graph(S_extra_owner), HCELL n_reference) = 4',
    '$gc_operation_metadata_valid(S_extra_owner, pdestructionoperation_live)',
    'S_no_ref = S_live[.REFCELLS = eps]',
    '~$gc_operation_metadata_valid(S_no_ref, pdestructionoperation_live)',
    'S_unit = S_live[.NATIVEEXCESS = [HCELL n_reference]]',
    '~$gc_operation_metadata_valid(S_unit, pdestructionoperation_live)',
    'S_no_target = S_live[.ENV = $unbind(S_live.ENV, $ptascii("ref"))]',
    '~$gc_operation_metadata_valid(S_no_target, pdestructionoperation_live)',
    'PhpStep: S_live ~> S_popped',
    'pdestructionoperation_done = pdestructionoperation_live[.NOGCEXTRA = [pgctemporary_done]]',
    'S_popped.DESTRUCTION.OPERATIONS = [pdestructionoperation_done]',
    '$heap_owners($heap_graph(S_popped), HCELL n_reference) = 2',
    '$heap_owners($heap_graph(S_popped), HOBJECT n_child) = 1',
    '$gc_operation_metadata_valid(S_popped, pdestructionoperation_done)',
    '$gc_consumed_decrements(S_live, S_popped, [HCELL n_reference]) = eps',
    'S_after = $drive_steps(S_live, 1)[.COMPLETION = NORMAL]',
    'S_after.GC.BUFFER = S.GC.BUFFER',
    '$heap_owners($heap_graph(S_after), HCELL n_reference) = 2',
    '$heap_owners($heap_graph(S_after), HOBJECT n_child) = 1',
    *valid('S_after'), *budget('S'), *budget('S_live'),
    # Removing a real CV reference retains its actual GC_CHECK_POSSIBLE_ROOT.
    *seek('S_after', 'S_unset', 'UNSET'),
    'S_unset.TODO = (UNSET expression_unset) :: ptask_unset_tail*',
    'S_unset.DESTRUCTION.OPERATIONS = eps',
    '$heap_owners($heap_graph(S_unset), HCELL n_reference) = 2',
    '~((HOBJECT n_child) <- $gc_nodes(S_unset.GC.BUFFER))',
    '~$gc_reference_discard_site(S_unset, S_unset.ORIGIN, n_reference)',
    'PhpStep: S_unset ~> S_unbound',
    '$lookup(S_unbound.ENV, $ptascii("ref")) = eps',
    '$heap_owners($heap_graph(S_unbound), HCELL n_reference) = 1',
    '$heap_owners($heap_graph(S_unbound), HOBJECT n_child) = 1',
    '$gc_operation_temporary_extra(S_unset, S_unbound, UNSET expression_unset, [HCELL n_reference]) = eps',
    'S_real = $drive_steps(S_unset, 1)[.COMPLETION = NORMAL]',
    'S_real.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_real) :: ptask_real_tail*',
    'pdestructionrelease_real.JOBS = [DESTRUCTION_VALUE (HCELL n_reference)]',
    'S_real.DESTRUCTION.OPERATIONS = [pdestructionoperation_real]',
    'pdestructionoperation_real.NOGC = eps',
    'pdestructionoperation_real.NOGCEXTRA = eps',
    '$gc_release_metadata_valid(S_real, pdestructionrelease_real)',
    '$heap_owners($heap_graph(S_real), HCELL n_reference) = 2',
    '~((HOBJECT n_child) <- $gc_nodes(S_real.GC.BUFFER))',
    *valid('S_real'),
    'S_real_after = $drive_steps(S_real, 1)[.COMPLETION = NORMAL]',
    '$heap_owners($heap_graph(S_real_after), HCELL n_reference) = 1',
    '$heap_owners($heap_graph(S_real_after), HOBJECT n_child) = 1',
    'pgc_real = $gc_buffer_add(S_real.GC, HOBJECT n_child)',
    'S_real_after.GC.BUFFER = pgc_real.BUFFER',
    '$heap_count(HOBJECT n_child, $gc_nodes(S_real_after.GC.BUFFER)) = 1',
    *valid('S_real_after'), *budget('S_unset'),
    *seek('S_real_after', 'S_write', 'WRITE'),
    'S_write.STORE[n_reference] = DEFINED (POBJECT n_child)',
    'PhpStep: S_write ~> S_written',
    'S_written.STORE[n_reference] = DEFINED (PINT 23)',
    'S_value = $drive_steps(S_write, 1)[.COMPLETION = NORMAL]',
    'S_value.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_child) :: ptask_child_tail*',
    'pdestructionrelease_child.JOBS = [DESTRUCTION_VALUE (HOBJECT n_child)]',
    '$gc_release_metadata_valid(S_value, pdestructionrelease_child)',
    *valid('S_value'),
    'S_done = $drive_steps(S_value, 3000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    'S_done.NATIVEEXCESS = eps',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    '~((HCELL n_reference) <- S_done.ALLOCATIONS)',
    '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
    'n_child <- S_done.DESTRUCTION.CALLED',
    '$gc76_output(S_done.EVENTS) = $ptascii("B|R|U|D|W|23|G|0|E|S|")',
    *valid('S_done'),
]

review.CASES = {'unused-result-temp-and-genuine-reference-removal': {
    'source': SOURCE, 'stage': STAGE, 'checks': CHECKS,
}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
