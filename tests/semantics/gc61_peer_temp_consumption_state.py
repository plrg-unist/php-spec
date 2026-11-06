#!/usr/bin/env python3
"""Genuine Some/Extra TEMP pops advance once; storage replacement consumes none."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'tests/semantics/gc61_peer_cast_temp_identity.php').read_text()
STAGE = (
    'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_single) :: '
    '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_single) :: ptask_single_tail* '
    '-- if pdestructionrelease_single.JOBS = [DESTRUCTION_TEMP (HARRAY n_single)] '
    '-- if pdestructionoperation_single.SOURCE = DISCARD '
    '-- if pdestructionoperation_single.NOGC = (pgctemporary_single)')
DECLARATIONS = r'''dec $gc61_extra_stage(pstate) : bool
def $gc61_extra_stage(S) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if pdestructionrelease.JOBS = [DESTRUCTION_TEMP (HARRAY n_first), DESTRUCTION_TEMP (HARRAY n_second)]
  -- if pdestructionoperation.SOURCE = BINARY_RIGHT NOTIDENTICAL (KNOWN (PARRAY n_first)) z
def $gc61_extra_stage(S) = false -- otherwise
dec $gc61_seek_extra(pstate, nat) : pstate
def $gc61_seek_extra(S, n) = S -- if $gc61_extra_stage(S)
def $gc61_seek_extra(S, n) = $gc61_seek_extra($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$gc61_extra_stage(S) -- if $(n > 0) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $gc61_seek_extra(S, 0) = S -- if ~$gc61_extra_stage(S)
def $gc61_seek_extra(S, n) = S -- if ~$gc61_extra_stage(S) -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''
recorded = review.recorded


def recorded_fixture(command, directory, stem, environment, seconds):
    fixture = Path(command[-1])
    fixture.write_text(DECLARATIONS + fixture.read_text())
    return recorded(command, directory, stem, environment, seconds)


review.recorded = recorded_fixture
CHECKS = [
    r'S.CURRENT = eps /\ S.FRAMES = eps /\ S.ITERATORS = eps',
    r'S.GC.ACTIVE = eps /\ S.GC.PLAN = eps /\ S.GC.WORKER = eps',
    '$lookup(S.ENV, $ptascii("sentinel61Peer")) = (n_sentinel_cell)',
    'S.STORE[n_sentinel_cell] = DEFINED (POBJECT n_sentinel)',
    '$lookup(S.ENV, $ptascii("object61Peer")) = (n_receiver_cell)',
    'S.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
    'n_receiver =/= n_sentinel',
    '$heap_owners($heap_graph(S), HOBJECT n_sentinel) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1',
    'S.DESTRUCTION.CALLED = eps',
    'pdestructionoperation_single.NOGCEXTRA = eps',
    'pgctemporary_single = {OPERAND KNOWN (PARRAY n_single), PENDING true}',
    'pdestructionoperation_single.VALUE = KNOWN PNULL',
    '$destructor_release_valid(S, pdestructionrelease_single)',
    '$gc_operation_metadata_valid(S, pdestructionoperation_single)',
    '$heap_owners($heap_graph(S), HARRAY n_single) = 1',
    '$node_children(S, HARRAY n_single) = eps',
    '$destructor_release_replace(S, pdestructionrelease_single) = S',
    'pdestructionrelease_single_empty = pdestructionrelease_single[.JOBS = eps]',
    'S_single_pop = $destructor_release_replace(S, pdestructionrelease_single_empty)',
    'pdestructionoperation_single_done = pdestructionoperation_single[.NOGC = (pgctemporary_single[.PENDING = false])]',
    'S_single_pop.DESTRUCTION.OPERATIONS = [pdestructionoperation_single_done]',
    'S_single_pop.DESTRUCTION.RELEASES = [pdestructionrelease_single_empty]',
    'S_single_pop.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_single_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_single_done) :: ptask_single_tail*',
    'S_single_pop.ALLOCATIONS = S.ALLOCATIONS',
    '$heap_owners($heap_graph(S_single_pop), HARRAY n_single) = 0',
    '$gc_operation_metadata_valid(S_single_pop, pdestructionoperation_single_done)',
    '$destructor_release_replace(S_single_pop, pdestructionrelease_single_empty) = S_single_pop',
    'PhpStep: S ~> S_single_raw',
    'S_single_raw = $destruction_storage_free(S_single_pop, HARRAY n_single, pdestructionrelease_single_empty)',
    '~((HARRAY n_single) <- S_single_raw.ALLOCATIONS)',
    'S_single_raw.DESTRUCTION.OPERATIONS = [pdestructionoperation_single_done]',
    'S_single_raw.DESTRUCTION.RELEASES = [pdestructionrelease_single_empty]',
    '$heap_owners($heap_graph(S_single_raw), HOBJECT n_sentinel) = 1',
    '$heap_owners($heap_graph(S_single_raw), HOBJECT n_receiver) = 1',
    '$gc_operation_metadata_valid(S_single_raw, pdestructionoperation_single_done)',
    '$gc_consumed_decrements(S, S_single_raw, [HARRAY n_single]) = eps',
    '$gc_consumed_decrements(S, S_single_raw, [HARRAY n_single, HOBJECT n_sentinel]) = [HOBJECT n_sentinel]',
    'S_zero = $drive_steps(S, 0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_single_paused = $drive_steps(S, 1)',
    'S_single_paused.COMPLETION = BUDGET',
    'S_single_one = S_single_paused[.COMPLETION = NORMAL]',
    '~((HARRAY n_single) <- S_single_one.ALLOCATIONS)',
    'S_single_one.DESTRUCTION.OPERATIONS = [pdestructionoperation_single_done]',
    'S_extra_reached = $gc61_seek_extra(S_single_one, 4000)',
    'S_extra_reached.COMPLETION = BUDGET',
    'S_extra = S_extra_reached[.COMPLETION = NORMAL]',
    'S_extra.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_extra) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_extra) :: ptask_extra_tail*',
    'pdestructionrelease_extra.JOBS = [DESTRUCTION_TEMP (HARRAY n_cast), DESTRUCTION_TEMP (HARRAY n_literal)]',
    'pdestructionoperation_extra.SOURCE = BINARY_RIGHT NOTIDENTICAL (KNOWN (PARRAY n_cast)) z',
    'pdestructionoperation_extra.NOGC = eps',
    'pdestructionoperation_extra.NOGCEXTRA = [pgctemporary_cast, pgctemporary_literal]',
    'pgctemporary_cast = {OPERAND KNOWN (PARRAY n_cast), PENDING true}',
    'pgctemporary_literal = {OPERAND KNOWN (PARRAY n_literal), PENDING true}',
    'pdestructionoperation_extra.VALUE = KNOWN (PBOOL true)',
    'S_extra.EVENTS = [OUTPUT $ptascii("B|")]',
    'n_cast =/= n_literal',
    'S_extra.ARRAYS[n_cast].ITEMS = eps',
    'S_extra.ARRAYS[n_literal].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 17))]',
    '$node_children(S_extra, HARRAY n_cast) = eps',
    '$node_children(S_extra, HARRAY n_literal) = eps',
    '$heap_owners($heap_graph(S_extra), HARRAY n_cast) = 1',
    'n_literal_owners = $heap_owners($heap_graph(S_extra), HARRAY n_literal)',
    '$(n_literal_owners > 0)',
    '$destructor_release_valid(S_extra, pdestructionrelease_extra)',
    '$gc_operation_metadata_valid(S_extra, pdestructionoperation_extra)',
    '$destructor_release_replace(S_extra, pdestructionrelease_extra) = S_extra',
    'pdestructionrelease_tail = pdestructionrelease_extra[.JOBS = [DESTRUCTION_TEMP (HARRAY n_literal)]]',
    'S_extra_pop = $destructor_release_replace(S_extra, pdestructionrelease_tail)',
    'pdestructionoperation_cast_done = pdestructionoperation_extra[.NOGCEXTRA = [pgctemporary_cast[.PENDING = false], pgctemporary_literal]]',
    'S_extra_pop.DESTRUCTION.OPERATIONS = [pdestructionoperation_cast_done]',
    'S_extra_pop.DESTRUCTION.RELEASES = [pdestructionrelease_tail]',
    'S_extra_pop.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_tail) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cast_done) :: ptask_extra_tail*',
    'S_extra_pop.ALLOCATIONS = S_extra.ALLOCATIONS',
    '$heap_owners($heap_graph(S_extra_pop), HARRAY n_cast) = 0',
    '$heap_owners($heap_graph(S_extra_pop), HARRAY n_literal) = n_literal_owners',
    '$gc_operation_metadata_valid(S_extra_pop, pdestructionoperation_cast_done)',
    '$destructor_release_replace(S_extra_pop, pdestructionrelease_tail) = S_extra_pop',
    # A helper-only storage expansion prefixes one ordinary owning job, not a pop.
    'pdestructionrelease_expanded = pdestructionrelease_tail[.JOBS = (DESTRUCTION_VALUE (HOBJECT n_sentinel)) :: pdestructionrelease_tail.JOBS]',
    'S_expanded = $destructor_release_replace(S_extra_pop, pdestructionrelease_expanded)',
    'S_expanded.DESTRUCTION.OPERATIONS = [pdestructionoperation_cast_done]',
    'S_expanded.DESTRUCTION.RELEASES = [pdestructionrelease_expanded]',
    '$gc_operation_metadata_valid(S_expanded, pdestructionoperation_cast_done)',
    '$heap_owners($heap_graph(S_expanded), HOBJECT n_sentinel) = 2',
    'PhpStep: S_extra ~> S_cast_raw',
    'S_cast_raw = $destruction_storage_free(S_extra_pop, HARRAY n_cast, pdestructionrelease_tail)',
    '~((HARRAY n_cast) <- S_cast_raw.ALLOCATIONS)',
    '(HARRAY n_literal) <- S_cast_raw.ALLOCATIONS',
    'S_cast_raw.DESTRUCTION.OPERATIONS = [pdestructionoperation_cast_done]',
    'S_cast_raw.DESTRUCTION.RELEASES = [pdestructionrelease_tail]',
    'S_cast_raw.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_tail) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cast_done) :: ptask_extra_tail*',
    '$heap_owners($heap_graph(S_cast_raw), HARRAY n_literal) = n_literal_owners',
    '$heap_owners($heap_graph(S_cast_raw), HOBJECT n_sentinel) = 1',
    '$heap_owners($heap_graph(S_cast_raw), HOBJECT n_receiver) = 1',
    'S_cast_raw.DESTRUCTION.CALLED = eps',
    '$gc_operation_metadata_valid(S_cast_raw, pdestructionoperation_cast_done)',
    '$gc_release_metadata_valid(S_cast_raw, pdestructionrelease_tail)',
    '$gc_consumed_decrements(S_extra, S_cast_raw, [HARRAY n_cast]) = eps',
    '$gc_consumed_decrements(S_extra, S_cast_raw, [HARRAY n_cast, HOBJECT n_sentinel]) = [HOBJECT n_sentinel]',
    # Reconstruct the old bad progress; the real remaining owner/job is unchanged.
    'pdestructionoperation_bad = pdestructionoperation_cast_done[.NOGCEXTRA = [pgctemporary_cast[.PENDING = false], pgctemporary_literal[.PENDING = false]]]',
    'S_bad = S_cast_raw[.DESTRUCTION.OPERATIONS = [pdestructionoperation_bad]][.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_tail) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: ptask_extra_tail*]',
    '$heap_graph(S_bad) = $heap_graph(S_cast_raw)',
    '~$gc_release_metadata_valid(S_bad, pdestructionrelease_tail)',
    '$gc_consumed_decrements(S_extra, S_bad, [HARRAY n_cast]) = [HARRAY n_cast]',
    'S_cast_paused = $drive_steps(S_extra, 1)',
    'S_cast_paused.COMPLETION = BUDGET',
    'S_remaining = S_cast_paused[.COMPLETION = NORMAL]',
    'S_remaining.DESTRUCTION.OPERATIONS = [pdestructionoperation_cast_done]',
    'S_remaining.DESTRUCTION.RELEASES = [pdestructionrelease_tail]',
    'PhpStep: S_remaining ~> S_literal_raw',
    'pdestructionoperation_both_done = pdestructionoperation_extra[.NOGCEXTRA = [pgctemporary_cast[.PENDING = false], pgctemporary_literal[.PENDING = false]]]',
    'S_literal_raw.DESTRUCTION.OPERATIONS = [pdestructionoperation_both_done]',
    'S_literal_raw.DESTRUCTION.RELEASES = [pdestructionrelease_extra[.JOBS = eps]]',
    '$gc_operation_metadata_valid(S_literal_raw, pdestructionoperation_both_done)',
    '$gc_consumed_decrements(S_remaining, S_literal_raw, [HARRAY n_literal]) = eps',
    'S_literal_paused = $drive_steps(S_remaining, 1)',
    'S_literal_paused.COMPLETION = BUDGET',
    'S_literal_done = S_literal_paused[.COMPLETION = NORMAL]',
    'S_literal_done.DESTRUCTION.OPERATIONS = [pdestructionoperation_both_done]',
    'S_done = $drive_steps(S_literal_done, 4000)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 4000) = S_done',
    '$drive_steps(S_single_paused[.COMPLETION = NORMAL], 4000) = S_done',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps',
    'S_done.CURRENT = eps',
    r'S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
    'S_done.DESTRUCTION.CALLS = eps',
    'S_done.EVENTS = [OUTPUT $ptascii("B|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("D|"), OUTPUT $ptascii("Z|")]',
    '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
    '~((HOBJECT n_sentinel) <- S_done.ALLOCATIONS)',
    '~((HARRAY n_cast) <- S_done.ALLOCATIONS)',
    '$heap_valid($heap_graph(S_done))',
]
review.CASES = {'single-and-extra-temp-consumption': {
    'source': SOURCE, 'stage': STAGE, 'checks': CHECKS}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=240) else 1)
