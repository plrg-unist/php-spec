#!/usr/bin/env python3
"""Unused result disposal, real same-reference rebinding and CV decrements."""
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
SECOND = (ROOT / 'tests/semantics/gc83_second_reference_result.php').read_text()
THIRD = (ROOT / 'tests/semantics/gc83_third_reference_result.php').read_text()
DECLARATIONS = r'''syntax pgc83phase = REBIND | RESULTDROP | UNSETREF | WRITE
dec $gc83_target(pstate, preqbytes) : bool
def $gc83_target(S, preqbytes) = true
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NStmtExpression (NExprAssignRef (NExprVariable (BYTES text_target) metadata_target) expression_rhs metadata_assignment) metadata_statement)
  -- if $base64(text_target) = preqbytes
def $gc83_target(S, preqbytes) = false -- otherwise
dec $gc83_at(pstate, pgc83phase, preqbytes, nat) : bool
def $gc83_at(S, REBIND, preqbytes, n_reference) = true
  -- if S.TODO = (REF_NAME n_name*) :: ptask_tail*
  -- if n_name* = preqbytes
  -- if $lookup(S.ENV, preqbytes) = (n_reference)
  -- if S.CELL = n_reference /\ S.RESULT = KNOWN PNULL
def $gc83_at(S, RESULTDROP, preqbytes, n_reference) = true
  -- if S.TODO = DISCARD :: ptask_tail*
  -- if S.RESULT = REFERENCE n_reference
  -- if $gc83_target(S, preqbytes)
def $gc83_at(S, UNSETREF, preqbytes, n_reference) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text) metadata)) :: ptask_tail*
  -- if $base64(text) = preqbytes
def $gc83_at(S, WRITE, preqbytes, n_reference) = true
  -- if S.TODO = (WRITE_NAME n_name* z) :: ptask_tail*
  -- if n_name* = $ptascii("first") /\ S.RESULT = KNOWN (PINT 23)
def $gc83_at(S, pgc83phase, preqbytes, n_reference) = false -- otherwise
dec $gc83_seek(pstate, pgc83phase, preqbytes, nat, nat) : pstate
def $gc83_seek(S, pgc83phase, preqbytes, n_reference, n) = S
  -- if $gc83_at(S, pgc83phase, preqbytes, n_reference)
def $gc83_seek(S, pgc83phase, preqbytes, n_reference, n) = $gc83_seek($drive_steps(S[.COMPLETION = NORMAL], 1), pgc83phase, preqbytes, n_reference, $nabs($(n - 1)))
  -- if ~$gc83_at(S, pgc83phase, preqbytes, n_reference) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc83_seek(S, pgc83phase, preqbytes, n_reference, 0) = S
  -- if ~$gc83_at(S, pgc83phase, preqbytes, n_reference)
def $gc83_seek(S, pgc83phase, preqbytes, n_reference, n) = S
  -- if ~$gc83_at(S, pgc83phase, preqbytes, n_reference)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $gc83_op(pstate, pdestructionoperation) : pstate
def $gc83_op(S, pdestructionoperation_new) = S[.TODO = $destructor_operation_tasks(S.TODO, pdestructionoperation_old, pdestructionoperation_new)][.DESTRUCTION.OPERATIONS = [pdestructionoperation_new]]
  -- if S.DESTRUCTION.OPERATIONS = [pdestructionoperation_old]
dec $gc83_output(pevent*) : preqbytes
def $gc83_output(eps) = eps
def $gc83_output((OUTPUT preqbytes) :: pevent_tail*) = preqbytes ++ $gc83_output(pevent_tail*)
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
    return [f'{after}_pause = $gc83_seek({before}, {phase}, $ptascii("third"), n_reference, 3000)',
            f'{after} = {after}_pause[.COMPLETION = NORMAL]',
            f'$gc83_at({after}, {phase}, $ptascii("third"), n_reference)']


def stage(name):
    return ('S.TODO = DISCARD :: ptask_tail* -- if S.RESULT = REFERENCE n_reference '
            f'-- if $gc83_target(S, $ptascii("{name}")) '
            '-- if $lookup(S.ENV, $ptascii("a")) = (n_root) '
            '-- if S.STORE[n_root] = DEFINED (PARRAY n_array) '
            '-- if $entry_lookup(S.ARRAYS[n_array].ITEMS, KINT 0) = (ALIAS n_reference) '
            '-- if S.STORE[n_reference] = DEFINED (POBJECT n_child) '
            '-- if S.NATIVEEXCESS = eps')


def unused(after):
    return [
        *valid('S'), '$gc_reference_discard_site(S, S.ORIGIN, n_reference)',
        'S.DESTRUCTION.OPERATIONS = eps',
        f'$heap_owners($heap_graph(S), HCELL n_reference) = {after + 1}',
        '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
        '~((HOBJECT n_child) <- $gc_nodes(S.GC.BUFFER))',
        'pgctemporary_live = {OPERAND REFERENCE n_reference, PENDING true}',
        'pgctemporary_done = pgctemporary_live[.PENDING = false]',
        '$gc_temporary_node(REFERENCE n_reference) = eps',
        '~$gc_extra_bounded(S, [pgctemporary_live])',
        'PhpStep: S ~> S_raw',
        'S_raw = S[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        f'$heap_owners($heap_graph(S_raw), HCELL n_reference) = {after}',
        '$heap_owners($heap_graph(S_raw), HOBJECT n_child) = 1',
        '$eager_slots(S, S_raw) = [HCELL n_reference]',
        '$gc_operation_temporary_extra(S, S_raw, DISCARD, [HCELL n_reference]) = [pgctemporary_live]',
        '$gc_operation_temporary_extra(S, S_raw, DISCARD, [HOBJECT n_child]) = eps',
        '$gc_same_location(S, S_raw) = eps',
        'S_live = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
        'S_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_live) :: ptask_live_tail*',
        'pdestructionrelease_live.JOBS = [DESTRUCTION_TEMP (HCELL n_reference)]',
        'S_live.DESTRUCTION.OPERATIONS = [pdestructionoperation_live]',
        'pdestructionoperation_live.SOURCE = DISCARD',
        'pdestructionoperation_live.VALUE = KNOWN PNULL',
        'pdestructionoperation_live.NOGCEXTRA = [pgctemporary_live]',
        '$gc_operation_metadata_valid(S_live, pdestructionoperation_live)',
        '$gc_release_metadata_valid(S_live, pdestructionrelease_live)',
        *valid('S_live'),
        f'$heap_owners($heap_graph(S_live), HCELL n_reference) = {after + 1}',
        'S_live.GC.BUFFER = S.GC.BUFFER',
        'S_after = $drive_steps(S_live, 1)[.COMPLETION = NORMAL]',
        'pdestructionoperation_done = pdestructionoperation_live[.NOGCEXTRA = [pgctemporary_done]]',
        'S_after.DESTRUCTION.OPERATIONS = [pdestructionoperation_done]',
        '$gc_operation_metadata_valid(S_after, pdestructionoperation_done)',
        f'$heap_owners($heap_graph(S_after), HCELL n_reference) = {after}',
        '$heap_owners($heap_graph(S_after), HOBJECT n_child) = 1',
        'S_after.GC.BUFFER = S.GC.BUFFER',
        *valid('S_after'), *budget('S'), *budget('S_live'),
    ]


SECOND_CHECKS = unused(3) + [
    # Restore the old minimal two real owners, then exercise its two former caps.
    'S_legacy = S[.ENV = $unbind(S.ENV, $ptascii("first"))]',
    'S_legacy_raw = S_raw[.ENV = S_legacy.ENV]',
    '$heap_owners($heap_graph(S_legacy), HCELL n_reference) = 3',
    '$gc_operation_temporary_extra(S_legacy, S_legacy_raw, DISCARD, [HCELL n_reference]) = [pgctemporary_live]',
    'S_held = S_legacy[.HELD = S_legacy.HELD ++ [HCELL n_reference]]',
    'S_held_raw = S_legacy_raw[.HELD = S_held.HELD]',
    '$heap_valid($heap_graph(S_held))',
    '$heap_owners($heap_graph(S_held), HCELL n_reference) = 4',
    '$heap_owners($heap_graph(S_held_raw), HCELL n_reference) = 3',
    '$gc_operation_temporary_extra(S_held, S_held_raw, DISCARD, [HCELL n_reference]) = [pgctemporary_live]',
    'S_legacy_live = S_live[.ENV = $unbind(S_live.ENV, $ptascii("first"))]',
    '$gc_operation_metadata_valid(S_legacy_live, pdestructionoperation_live)',
    'S_extra_owner = S_legacy_live[.ARRAYS = $array_replace(S_legacy_live.ARRAYS, n_array, $array_insert(S_legacy_live.ARRAYS[n_array], KINT 1, ALIAS n_reference))]',
    '$heap_valid($heap_graph(S_extra_owner))',
    '$heap_owners($heap_graph(S_extra_owner), HCELL n_reference) = 4',
    '$heap_owners($heap_graph(S_extra_owner), HOBJECT n_child) = 1',
    '$gc_operation_metadata_valid(S_extra_owner, pdestructionoperation_live)',
]

THIRD_CHECKS = unused(4)
for name, patch in {
    'origin': '[.ORIGIN = eps]',
    'cell': '[.CELL = n_root]',
    'key': '[.KEY = KINT 1]',
    'progress': '[.NOGCEXTRA = [pgctemporary_done]]',
    'operand': '[.NOGCEXTRA = [{OPERAND REFERENCE n_root, PENDING true}]]',
    'tail': '[.NOGCEXTRA = [pgctemporary_live, pgctemporary_live]]',
}.items():
    THIRD_CHECKS += [f'pdestructionoperation_bad_{name} = pdestructionoperation_live{patch}',
                     f'S_bad_{name} = $gc83_op(S_live, pdestructionoperation_bad_{name})',
                     f'~$gc_operation_metadata_valid(S_bad_{name}, pdestructionoperation_bad_{name})']
THIRD_CHECKS += [
    'S_no_target = S_live[.ENV = $unbind(S_live.ENV, $ptascii("third"))]',
    '~$gc_operation_metadata_valid(S_no_target, pdestructionoperation_live)',
    'S_unit = S_live[.NATIVEEXCESS = [HCELL n_reference]]',
    '~$gc_operation_metadata_valid(S_unit, pdestructionoperation_live)',
    *seek('S_after', 'S_bind', 'REBIND'),
    '$heap_owners($heap_graph(S_bind), HCELL n_reference) = 4',
    '~((HOBJECT n_child) <- $gc_nodes(S_bind.GC.BUFFER))',
    'S_bind.TODO = (REF_NAME n_bind_target*) :: ptask_bind_tail*',
    'PhpStep: S_bind ~> S_bind_raw',
    'S_bind_raw = $reference_bind_name(S_bind, $ptascii("third"))[.TODO = ptask_bind_tail*]',
    '$heap_owners($heap_graph(S_bind_raw), HCELL n_reference) = 5',
    '$eager_slots(S_bind, S_bind_raw) = eps',
    '$gc_same_location(S_bind, S_bind_raw) = [HCELL n_reference]',
    'S_retag = S_bind[.TODO = (REF_NAME $ptascii("first")) :: ptask_bind_tail*]',
    'S_retag_raw = $reference_bind_name(S_retag, $ptascii("first"))[.TODO = ptask_bind_tail*]',
    '$gc_same_location(S_retag, S_retag_raw) = eps',
    'S_no_origin = S_bind[.ORIGIN = eps]',
    'S_no_origin_raw = S_bind_raw[.ORIGIN = eps]',
    '$gc_same_location(S_no_origin, S_no_origin_raw) = eps',
    'S_changed = S_bind_raw[.STORE = $set_cell(S_bind_raw.STORE, n_reference, DEFINED (PINT 17))]',
    '$gc_same_location(S_bind, S_changed) = eps',
    'S_bound = $drive_steps(S_bind, 1)[.COMPLETION = NORMAL]',
    '(HOBJECT n_child) <- $gc_nodes(S_bound.GC.BUFFER)',
    '$heap_owners($heap_graph(S_bound), HOBJECT n_child) = 1',
    *valid('S_bound'),
    *seek('S_bound', 'S_repeated', 'RESULTDROP'),
    '$heap_owners($heap_graph(S_repeated), HCELL n_reference) = 5',
    'S_clear = S_repeated[.GC = $gc_buffer_remove(S_repeated.GC, HOBJECT n_child)]',
    *valid('S_clear'),
    'S_clear_live = $drive_steps(S_clear, 1)[.COMPLETION = NORMAL]',
    'S_clear_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_clear) :: ptask_clear_tail*',
    'pdestructionrelease_clear.JOBS = [DESTRUCTION_TEMP (HCELL n_reference)]',
    '~((HOBJECT n_child) <- $gc_nodes(S_clear_live.GC.BUFFER))',
    'S_clear_after = $drive_steps(S_clear_live, 1)[.COMPLETION = NORMAL]',
    '~((HOBJECT n_child) <- $gc_nodes(S_clear_after.GC.BUFFER))',
    '$heap_owners($heap_graph(S_clear_after), HCELL n_reference) = 4',
    'S_repeated_after = $drive_steps(S_repeated, 2)[.COMPLETION = NORMAL]',
    'S_repeated_after.GC.BUFFER = S_repeated.GC.BUFFER',
    *seek('S_repeated_after', 'S_unset', 'UNSETREF'),
    '~((HOBJECT n_child) <- $gc_nodes(S_unset.GC.BUFFER))',
    'S_unset.TODO = (UNSET expression_unset) :: ptask_unset_tail*',
    'PhpStep: S_unset ~> S_unset_raw',
    '$gc_operation_temporary_extra(S_unset, S_unset_raw, UNSET expression_unset, [HCELL n_reference]) = eps',
    '$heap_owners($heap_graph(S_unset_raw), HCELL n_reference) = 3',
    'S_value_live = $drive_steps(S_unset, 1)[.COMPLETION = NORMAL]',
    'S_value_live.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_value) :: ptask_value_tail*',
    'pdestructionrelease_value.JOBS = [DESTRUCTION_VALUE (HCELL n_reference)]',
    'S_value_after = $drive_steps(S_value_live, 1)[.COMPLETION = NORMAL]',
    '$heap_owners($heap_graph(S_value_after), HCELL n_reference) = 3',
    '$heap_owners($heap_graph(S_value_after), HOBJECT n_child) = 1',
    '(HOBJECT n_child) <- $gc_nodes(S_value_after.GC.BUFFER)',
    'S_value_after.DESTRUCTION.CALLS = eps',
    *valid('S_value_after'), *budget('S_value_live'),
    *seek('S_value_after', 'S_write', 'WRITE'),
    'PhpStep: S_write ~> S_write_raw',
    'S_write_raw.STORE[n_reference] = DEFINED (PINT 23)',
    '$heap_owners($heap_graph(S_write_raw), HOBJECT n_child) = 0',
    'S_done = $drive_steps(S_write, 3000)',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE',
    '~((HOBJECT n_child) <- S_done.ALLOCATIONS)',
    'n_child <- S_done.DESTRUCTION.CALLED',
    '$gc83_output(S_done.EVENTS) = $ptascii("B|Q|0|R|T|0|A|C|0|U|D|W|23|23|F|E|S|")',
    *valid('S_done'),
]

review.CASES = {
    'unused-second-result-and-superseded-owner-caps': {'source': SECOND, 'stage': stage('second'), 'checks': SECOND_CHECKS},
    'unused-third-result-genuine-rebind-and-real-value': {'source': THIRD, 'stage': stage('third'), 'checks': THIRD_CHECKS},
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
