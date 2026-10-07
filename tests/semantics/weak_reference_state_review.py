#!/usr/bin/env python3
"""Independent source-reached WeakReference selection and ownership checks."""
import argparse
import json
from pathlib import Path

import shutdown_state_review as runner

AUTHOR = {row['id']: row['source'] for row in json.loads(
    Path(__file__).with_name('weak_reference_cases.json').read_text())}
INDEPENDENT = {row['id']: row['source'] for row in json.loads(
    Path(__file__).with_name('weak_reference_review_cases.json').read_text())}
VALID = ['$weakref_records_valid(S, S.ALLOCATIONS, eps)',
         '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']


def replay():
    return ['S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused[.COMPLETION = NORMAL] = S',
            'S_done = $drive(S, 2000)', 'S_done.COMPLETION = NORMAL',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
            '$drive(S_paused[.COMPLETION = NORMAL], 2000) = S_done']


CASES = {
    'literal-create-retains-memoized-identity-and-static-owner-shape': {
        'source': AUTHOR['create-memoizes-live-wrapper'],
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_CREATE '
                 '-- if pconfigcall.OWNER = eps '
                 '-- if pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_target))] '
                 '-- if $weakref_find(S, S.ALLOCATIONS, n_target) = (n_wrapper)',
        'checks': [
            'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
            'pconfigcall.KIND = INTRINSIC_WEAKREF_CREATE',
            'pconfigcall.OWNER = eps',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_target))]',
            '$weakref_find(S, S.ALLOCATIONS, n_target) = (n_wrapper)',
            'S.OBJECTS[n_wrapper] = WEAKREFERENCE (n_target)',
            '$node_children(S, HOBJECT n_wrapper) = eps',
            '$weakref_get(S, n_wrapper) = POBJECT n_target',
            '$config_invoke_valid(S, pconfigcall)', *VALID,
            'pconfigcall_bad = pconfigcall[.OWNER = (n_wrapper)]',
            '~$config_selected_valid(S, pconfigcall_bad)',
            '~$config_invoke_valid(S, pconfigcall_bad)',
            '~$call_descriptors_valid(S[.TODO = (CONFIG_INVOKE pconfigcall_bad) :: ptask_tail*])',
            '~$config_invoke_valid(S, pconfigcall[.LINE = $(pconfigcall.LINE + 1)])',
            '~$config_selected_valid(S, pconfigcall[.KIND = INTRINSIC_WEAKREF_GET])',
            'S_forged = S[.OBJECTS = $object_set(S.OBJECTS, n_wrapper, WEAKREFERENCE eps)]',
            '$heap_valid($heap_graph(S_forged))',
            '~$weakref_records_valid(S_forged, S_forged.ALLOCATIONS, eps)',
            '~$call_descriptors_valid(S_forged)',
            *replay(),
        ],
    },
    'instance-static-create-retains-only-borrowed-retired-selector': {
        'source': AUTHOR['static-create-through-instance-borrows-selector'],
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_CREATE '
                 '-- if pconfigcall.OWNER = (n_selector) '
                 '-- if ~((HOBJECT n_selector) <- S.ALLOCATIONS)',
        'checks': [
            'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
            'pconfigcall.KIND = INTRINSIC_WEAKREF_CREATE',
            'pconfigcall.OWNER = (n_selector)',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_target))]',
            'S.OBJECTS[n_selector] = WEAKREFERENCE (n_target)',
            '~((HOBJECT n_selector) <- S.ALLOCATIONS)',
            '~((HOBJECT n_selector) <- $config_nodes(pconfigcall))',
            '$weakref_find(S, S.ALLOCATIONS, n_target) = eps',
            '$weakref_find(S, S.ALLOCATIONS, n_selector) = (n_watch)',
            '$weakref_get(S, n_watch) = PNULL',
            '$config_invoke_valid(S, pconfigcall)', *VALID,
            'pconfigcall_bad = pconfigcall[.OWNER = eps]',
            '~$config_selected_valid(S, pconfigcall_bad)',
            '~$config_invoke_valid(S, pconfigcall_bad)',
            '~$call_descriptors_valid(S[.TODO = (CONFIG_INVOKE pconfigcall_bad) :: ptask_tail*])',
            '~$config_selected_valid(S, pconfigcall[.OWNER = (|S.OBJECTS|)])',
            *replay(),
        ],
    },
    'destructor-get-retains-target-through-once-mark-and-strong-result': {
        'source': INDEPENDENT['review-get-resurrects-until-later-free'],
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
                 '-- if pconfigcall.LINE = 7 '
                 '-- if S.DESTRUCTION.CALLS = pdestructorcall :: pdestructorcall_tail*',
        'checks': [
            'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
            'pconfigcall.KIND = INTRINSIC_WEAKREF_GET',
            'pconfigcall.OWNER = (n_wrapper)',
            'pconfigcall.SENT = eps',
            'S.DESTRUCTION.CALLS = pdestructorcall :: pdestructorcall_tail*',
            'n_target = pdestructorcall.OBJECT',
            'n_target <- S.DESTRUCTION.CALLED',
            '(HOBJECT n_target) <- S.ALLOCATIONS',
            'S.OBJECTS[n_wrapper] = WEAKREFERENCE (n_target)',
            '$node_children(S, HOBJECT n_wrapper) = eps',
            '$weakref_get(S, n_wrapper) = POBJECT n_target',
            '$config_invoke_valid(S, pconfigcall)', *VALID,
            '~$config_selected_valid(S, pconfigcall[.OWNER = eps])',
            '~$config_selected_valid(S, pconfigcall[.OWNER = (n_target)])',
            'S_received = $weakref_receive(S, pconfigcall)',
            'S_received.RESULT = KNOWN (POBJECT n_target)',
            '$heap_valid($heap_graph(S_received))',
            '$heap_owners($heap_graph(S_received), HOBJECT n_target) = $($heap_owners($heap_graph(S), HOBJECT n_target) + 1)',
            'S_received.DESTRUCTION.CALLED = S.DESTRUCTION.CALLED',
            *replay(),
            '~((HOBJECT n_target) <- S_done.ALLOCATIONS)',
            '$weakref_get(S_done, n_wrapper) = PNULL',
            '$destructor_unique(S_done.DESTRUCTION.CALLED)',
        ],
    },
}

runner.CASES = CASES

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if runner.run(args.case) else 1)
