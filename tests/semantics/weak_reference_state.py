#!/usr/bin/env python3
"""Reached WeakReference NEW candidate, parked owner and retirement checks."""
import argparse
import json
from pathlib import Path

import shutdown_state_review as runner

SOURCES = {row['id']: row['source'] for row in json.loads(
    Path(__file__).with_name('weak_reference_cases.json').read_text())}
VALID = ['$weakref_records_valid(S, S.ALLOCATIONS, eps)',
         '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']


def replay():
    return ['S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused[.COMPLETION = NORMAL] = S',
            'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
            '$drive(S_paused[.COMPLETION = NORMAL], 2000) = S_done',
            '~((HOBJECT n_candidate) <- S_done.ALLOCATIONS)']


CASES = {
    'abandoned-fiber-stops-before-pending-stack-retirement': {
        'source': SOURCES['abandon-fiber-with-pending-weak-constructor'],
        'stage': 'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail* '
                 '-- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_carrier)) :: pdestructionjob_tail* '
                 '-- if S.OBJECTS[n_carrier] = FIBER pfiber '
                 '-- if pfiber.STATUS = FIBER_SUSPENDED '
                 '-- if $heap_owners($heap_graph(S), HOBJECT n_carrier) = 1',
        'checks': [
            'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*',
            'pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_carrier)) :: pdestructionjob_tail*',
            'S.OBJECTS[n_carrier] = FIBER pfiber',
            'pfiber.STATUS = FIBER_SUSPENDED',
            'n_candidate = $nabs($(|S.OBJECTS| - 1))',
            'S.OBJECTS[n_candidate] = WEAKREFERENCE eps',
            '$weakref_init_carrier(S, n_candidate, HOBJECT n_carrier)',
            '$destructor_release_valid(S, pdestructionrelease)', *VALID,
            '$heap_owners($heap_graph(S), HOBJECT n_carrier) = 1',
            '$weakref_pending_carrier(S, HOBJECT n_carrier)',
            'S_unallocated = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_carrier)]',
            '~$weakref_pending_carrier(S_unallocated, HOBJECT n_carrier)',
            'S_no_candidate = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_candidate)]',
            '~$weakref_pending_carrier(S_no_candidate, HOBJECT n_carrier)',
            'n_unrelated = |S.OBJECTS|',
            'S_unrelated = S_no_candidate[.OBJECTS = S.OBJECTS ++ [WEAKREFERENCE eps]][.ALLOCATIONS = S_no_candidate.ALLOCATIONS ++ [HOBJECT n_unrelated]]',
            '~$weakref_pending_carrier(S_unrelated, HOBJECT n_carrier)',
            'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused[.COMPLETION = NORMAL] = S',
            'PhpStep: S ~> S_one',
            'S_one.COMPLETION = UNSUPPORTED "abandoning WeakReference constructor argument stack"',
            'S_one[.COMPLETION = NORMAL] = S',
            'S_one.ALLOCATIONS = S.ALLOCATIONS',
            'S_one.OBJECTS = S.OBJECTS',
            'S_one.DESTRUCTION.CALLED = S.DESTRUCTION.CALLED',
            'S_one.TODO = S.TODO',
            'S_one.DESTRUCTION.RELEASES = S.DESTRUCTION.RELEASES',
            '$node_children(S_one, HOBJECT n_carrier) = $node_children(S, HOBJECT n_carrier)',
            '$weakref_init_pending(S_one, n_candidate)',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            'S_resumed = S_paused[.COMPLETION = NORMAL]',
            'PhpStep: S_resumed ~> S_replayed', 'S_replayed = S_one',
        ],
    },
    'abandoned-generator-stops-before-pending-stack-retirement': {
        'source': SOURCES['abandon-generator-with-pending-weak-constructor'],
        'stage': 'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail* '
                 '-- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_carrier)) :: pdestructionjob_tail* '
                 '-- if S.OBJECTS[n_carrier] = GENERATOR pgenerator '
                 '-- if pgenerator.PHASE = GENERATOR_PAUSED '
                 '-- if $heap_owners($heap_graph(S), HOBJECT n_carrier) = 1',
        'checks': [
            'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*',
            'pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_carrier)) :: pdestructionjob_tail*',
            'S.OBJECTS[n_carrier] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_PAUSED',
            'n_candidate = $nabs($(|S.OBJECTS| - 1))',
            'S.OBJECTS[n_candidate] = WEAKREFERENCE eps',
            '$weakref_init_carrier(S, n_candidate, HOBJECT n_carrier)',
            '$destructor_release_valid(S, pdestructionrelease)', *VALID,
            '$heap_owners($heap_graph(S), HOBJECT n_carrier) = 1',
            '$weakref_pending_carrier(S, HOBJECT n_carrier)',
            'S_unallocated = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_carrier)]',
            '~$weakref_pending_carrier(S_unallocated, HOBJECT n_carrier)',
            'S_no_candidate = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_candidate)]',
            '~$weakref_pending_carrier(S_no_candidate, HOBJECT n_carrier)',
            'n_unrelated = |S.OBJECTS|',
            'S_unrelated = S_no_candidate[.OBJECTS = S.OBJECTS ++ [WEAKREFERENCE eps]][.ALLOCATIONS = S_no_candidate.ALLOCATIONS ++ [HOBJECT n_unrelated]]',
            '~$weakref_pending_carrier(S_unrelated, HOBJECT n_carrier)',
            'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused[.COMPLETION = NORMAL] = S',
            'PhpStep: S ~> S_one',
            'S_one.COMPLETION = UNSUPPORTED "abandoning WeakReference constructor argument stack"',
            'S_one[.COMPLETION = NORMAL] = S',
            'S_one.ALLOCATIONS = S.ALLOCATIONS',
            'S_one.OBJECTS = S.OBJECTS',
            'S_one.DESTRUCTION.CALLED = S.DESTRUCTION.CALLED',
            'S_one.TODO = S.TODO',
            'S_one.DESTRUCTION.RELEASES = S.DESTRUCTION.RELEASES',
            '$node_children(S_one, HOBJECT n_carrier) = $node_children(S, HOBJECT n_carrier)',
            '$weakref_init_pending(S_one, n_candidate)',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            'S_resumed = S_paused[.COMPLETION = NORMAL]',
            'PhpStep: S_resumed ~> S_replayed', 'S_replayed = S_one',
        ],
    },
    'nested-new-pairs-with-the-exact-preargument-candidate': {
        'source': SOURCES['nested-forbidden-constructors-retain-distinct-candidates'],
        'stage': 'S.TODO = (CONFIG_ARGS pconfigcall) :: (CTOR_RESULT 1) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_CONSTRUCT '
                 '-- if pconfigcall.OWNER = (1)',
        'checks': [
            'n_candidate = 1',
            'S.TODO = (CONFIG_ARGS pconfigcall) :: (CTOR_RESULT n_candidate) :: ptask_tail*',
            'pconfigcall.KIND = INTRINSIC_WEAKREF_CONSTRUCT',
            'pconfigcall.OWNER = (n_candidate)',
            'pconfigcall.SENT = eps', 'pconfigcall.INDEX = 0',
            'S.OBJECTS = [WEAKREFERENCE eps, WEAKREFERENCE eps]',
            '(HOBJECT 0) <- S.ALLOCATIONS', '(HOBJECT n_candidate) <- S.ALLOCATIONS',
            '$weakref_init_pending(S, 0)', '$weakref_init_pending(S, n_candidate)',
            '$node_children(S, HOBJECT n_candidate) = eps',
            '$heap_owners($heap_graph(S), HOBJECT 0) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_candidate) = 2',
            '$config_call_valid(S, pconfigcall)',
            '$ctor_pair_valid(S, CONFIG_ARGS pconfigcall, CTOR_RESULT n_candidate)',
            '~$ctor_pair_valid(S, CONFIG_ARGS pconfigcall, CTOR_RESULT 0)',
            '$ctor_pairs_valid(S, S.TODO)', *VALID,
            'S_swapped = S[.TODO = (CONFIG_ARGS pconfigcall) :: (CTOR_RESULT 0) :: ptask_tail*]',
            '$heap_valid($heap_graph(S_swapped))',
            '~$ctor_pairs_valid(S_swapped, S_swapped.TODO)',
            '~$call_descriptors_valid(S_swapped)',
            '~$config_call_valid(S, pconfigcall[.LINE = $(pconfigcall.LINE + 1)])',
            'S_one = $drive_steps(S, 1)[.COMPLETION = NORMAL]',
            'S_one.TODO = (CONFIG_INVOKE pconfigcall) :: (CTOR_RESULT n_candidate) :: ptask_tail*',
            '$call_descriptors_valid(S_one)',
            'S_error = $drive_steps(S_one, 1)', 'S_error.COMPLETION = BUDGET',
            '$weakref_init_pending(S_error[.COMPLETION = NORMAL], n_candidate)',
            '$call_descriptors_valid(S_error[.COMPLETION = NORMAL])',
            '$heap_valid($heap_graph(S_error))',
            *replay(), '~((HOBJECT 0) <- S_done.ALLOCATIONS)',
        ],
    },
    'fiber-saved-constructor-argument-retains-the-empty-candidate': {
        'source': SOURCES['forbidden-constructor-candidate-parks-in-fiber'],
        'stage': '$fiber_at(S, 0) = (pfiber) -- if pfiber.STATUS = FIBER_SUSPENDED '
                 '-- if pfiber.VM = (pfibervm) '
                 '-- if n_candidate = $nabs($(|S.OBJECTS| - 1)) '
                 '-- if S.OBJECTS[n_candidate] = WEAKREFERENCE eps',
        'checks': [
            '$fiber_at(S, 0) = (pfiber)', 'pfiber.STATUS = FIBER_SUSPENDED',
            'pfiber.VM = (pfibervm)', 'n_candidate = $nabs($(|S.OBJECTS| - 1))',
            'S.OBJECTS[n_candidate] = WEAKREFERENCE eps',
            '(HOBJECT n_candidate) <- S.ALLOCATIONS',
            '$node_children(S, HOBJECT n_candidate) = eps',
            '$fiber_record_valid(S, 0, pfiber)',
            '~$weakref_init_tasks(S, n_candidate, S.TODO)',
            '~$weakref_init_frames(S, n_candidate, S.FRAMES)',
            '$weakref_init_vm(S, n_candidate, pfibervm)',
            '$weakref_init_carrier(S, n_candidate, HOBJECT 0)',
            '$weakref_init_pending(S, n_candidate)',
            '$heap_owners($heap_graph(S), HOBJECT n_candidate) = 2', *VALID,
            'S_no_vm = S[.OBJECTS = $object_set(S.OBJECTS, 0, FIBER pfiber[.VM = eps])]',
            '~$weakref_init_pending(S_no_vm, n_candidate)',
            '~$weakref_records_valid(S_no_vm, S_no_vm.ALLOCATIONS, eps)',
            'S_unallocated = S[.ALLOCATIONS = [HOBJECT 1, HOBJECT n_candidate]]',
            '~$weakref_init_pending(S_unallocated, n_candidate)',
            '~$weakref_records_valid(S_unallocated, S_unallocated.ALLOCATIONS, eps)',
            *replay(),
        ],
    },
    'generator-saved-constructor-argument-retains-the-empty-candidate': {
        'source': SOURCES['forbidden-constructor-candidate-parks-in-generator'],
        'stage': 'S.OBJECTS[0] = GENERATOR pgenerator '
                 '-- if pgenerator.PHASE = GENERATOR_PAUSED '
                 '-- if pgenerator.FRAME = (pframe) '
                 '-- if n_candidate = $nabs($(|S.OBJECTS| - 1)) '
                 '-- if S.OBJECTS[n_candidate] = WEAKREFERENCE eps',
        'checks': [
            'S.OBJECTS[0] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_PAUSED', 'pgenerator.FRAME = (pframe)',
            'n_candidate = $nabs($(|S.OBJECTS| - 1))',
            'S.OBJECTS[n_candidate] = WEAKREFERENCE eps',
            '(HOBJECT n_candidate) <- S.ALLOCATIONS',
            '$node_children(S, HOBJECT n_candidate) = eps',
            '$generator_record_valid(S, pgenerator)',
            '~$weakref_init_tasks(S, n_candidate, S.TODO)',
            '~$weakref_init_frames(S, n_candidate, S.FRAMES)',
            '$weakref_init_frames(S, n_candidate, [pframe])',
            '$weakref_init_carrier(S, n_candidate, HOBJECT 0)',
            '$weakref_init_pending(S, n_candidate)',
            '$heap_owners($heap_graph(S), HOBJECT n_candidate) = 2', *VALID,
            'S_no_frame = S[.OBJECTS = $object_set(S.OBJECTS, 0, GENERATOR pgenerator[.FRAME = eps])]',
            '~$weakref_init_pending(S_no_frame, n_candidate)',
            '~$weakref_records_valid(S_no_frame, S_no_frame.ALLOCATIONS, eps)',
            'S_unallocated = S[.ALLOCATIONS = [HOBJECT n_candidate]]',
            '~$weakref_init_pending(S_unallocated, n_candidate)',
            '~$weakref_records_valid(S_unallocated, S_unallocated.ALLOCATIONS, eps)',
            *replay(),
        ],
    },
    'failed-constructor-retains-only-authentic-ordered-release': {
        'source': SOURCES['forbidden-constructor-candidate-retires-through-ordered-release'],
        'stage': 'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail* '
                 '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_candidate)] '
                 '-- if S.OBJECTS[n_candidate] = WEAKREFERENCE eps '
                 '-- if n_candidate <- S.DESTRUCTION.CALLED',
        'checks': [
            'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_candidate)]',
            'S.OBJECTS[n_candidate] = WEAKREFERENCE eps',
            'n_candidate <- S.DESTRUCTION.CALLED',
            '(HOBJECT n_candidate) <- S.ALLOCATIONS',
            '$node_children(S, HOBJECT n_candidate) = eps',
            '$destructor_release_valid(S, pdestructionrelease)',
            '$weakref_init_pending(S, n_candidate)', *VALID,
            '$heap_owners($heap_graph(S), HOBJECT n_candidate) = 1',
            'ptask_tail* = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_after*',
            'pdestructionoperation.SOURCE = THROW_SEARCH n_error',
            'pdestructionoperation.PENDING = (n_error)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            'S_no_consumer = S[.DESTRUCTION.OPERATIONS = eps]',
            '$heap_valid($heap_graph(S_no_consumer))',
            '~$weakref_init_pending(S_no_consumer, n_candidate)',
            '~$weakref_records_valid(S_no_consumer, S_no_consumer.ALLOCATIONS, eps)',
            '~$call_descriptors_valid(S_no_consumer)',
            'S_no_failed_mark = S[.DESTRUCTION.CALLED = eps]',
            '~$weakref_init_pending(S_no_failed_mark, n_candidate)',
            'pdestructionoperation_bad = pdestructionoperation[.SOURCE = DISCARD]',
            'S_bad_source = S[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: ptask_after*][.DESTRUCTION.OPERATIONS = [pdestructionoperation_bad]]',
            '$heap_valid($heap_graph(S_bad_source))',
            '~$weakref_init_pending(S_bad_source, n_candidate)',
            '~$call_descriptors_valid(S_bad_source)',
            'pdestructionoperation_bad_pending = pdestructionoperation[.PENDING = eps]',
            'S_bad_pending = S[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad_pending) :: ptask_after*][.DESTRUCTION.OPERATIONS = [pdestructionoperation_bad_pending]]',
            '~$weakref_init_pending(S_bad_pending, n_candidate)',
            'S_without_release = S[.TODO = ptask_tail*][.DESTRUCTION.RELEASES = eps]',
            '~$weakref_init_pending(S_without_release, n_candidate)',
            '~$weakref_records_valid(S_without_release, S_without_release.ALLOCATIONS, eps)',
            *replay(),
        ],
    },
}

runner.CASES = CASES

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if runner.run(args.case) else 1)
