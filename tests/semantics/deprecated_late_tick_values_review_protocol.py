#!/usr/bin/env python3
"""Check copied scalar, nested-array and shared-reference tick retirement."""
from pathlib import Path

import fiber_state_review as review


HERE = Path(__file__).parent


def source(name):
    return (HERE / f'deprecated_late_tick_values_review_{name}.php').read_text()


PREFIX = ('S.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, '
          'DESTRUCTOR_OPERATION_EXIT pdestructionoperation, '
          'EXECUTOR_TICK_RELEASE pexecutortick false] '
          '-- if pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true ')
VALID = ['$executor_tick_valid(S, pexecutortick)',
         '$eager_operation_source_valid(S, pdestructionoperation)',
         '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
DONE = ['S_done = $drive_steps(S, 4000)', 'S_done.COMPLETION = NORMAL',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']

review.CASES = {
    'scalar-copies-add-no-owning-node': {
        'source': source('scalar'),
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback), DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.ENTRY = ptickentry',
        'checks': [
            'ptickentry.ENTRY.ARGS = [PNULL, PBOOL false, PBOOL true, PINT 7, PFLOAT 4609434218613702656, PSTRING $ptascii("s")]',
            '$executor_tick_nodes(ptickentry) = [HOBJECT n_callback, HOBJECT n_callback]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            'S.TICKENTRIES = eps', 'pexecutortick.TAIL = eps',
            '$task_nodes(EXECUTOR_TICK_RELEASE pexecutortick false) = eps',
            '~$executor_tick_valid(S, pexecutortick[.ENTRY = ptickentry[.ENTRY = ptickentry.ENTRY[.ARGS = eps]]])',
            '~$executor_tick_valid(S, pexecutortick[.ENTRY = ptickentry[.ENTRY = ptickentry.ENTRY[.CALL = ptickentry.ENTRY.CALL[.KIND = INTRINSIC_ERROR_REPORTING]]]])',
            *VALID,
            'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.TODO = S.TODO', 'S_paused.ALLOCATIONS = S.ALLOCATIONS',
            *DONE,
            '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("C;")]',
        ],
    },
    'shared-array-head-keeps-tail-owner-and-one-child-edge': {
        'source': source('shared_array'),
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_payload), DESTRUCTION_VALUE (HARRAY n_payload), DESTRUCTION_VALUE (HOBJECT n_callback1), DESTRUCTION_VALUE (HOBJECT n_callback1)] -- if pexecutortick.TAIL = [ptickentry_tail]',
        'checks': [
            'pexecutortick.ENTRY = ptickentry', 'S.TICKENTRIES = [ptickentry_tail]',
            'ptickentry.ENTRY.ARGS = [PARRAY n_payload, PARRAY n_payload]',
            'ptickentry_tail.ENTRY.ARGS = [PARRAY n_payload]',
            '$callback_cache_nodes(ptickentry_tail.ENTRY) = [HOBJECT n_callback2, HOBJECT n_callback2]',
            '$executor_tick_nodes(ptickentry) = [HARRAY n_payload, HARRAY n_payload, HOBJECT n_callback1, HOBJECT n_callback1]',
            '$tick_roots(S.TICKENTRIES) = [HOBJECT n_callback2, HOBJECT n_callback2, HARRAY n_payload]',
            '$heap_owners($heap_graph(S), HARRAY n_payload) = 3',
            '$node_children(S, HARRAY n_payload) = [HARRAY n_inner]',
            '$heap_owners($heap_graph(S), HARRAY n_inner) = 1',
            '$node_children(S, HARRAY n_inner) = [HOBJECT n_arg]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID, *DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("C1;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("C2;")]',
            '~((HARRAY n_payload) <- S_done.ALLOCATIONS)',
            '~((HARRAY n_inner) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_arg) <- S_done.ALLOCATIONS)',
        ],
    },
    'shared-array-tail-begins-after-head-fcc-release': {
        'source': source('shared_array'),
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_payload), DESTRUCTION_VALUE (HOBJECT n_callback2), DESTRUCTION_VALUE (HOBJECT n_callback2)] -- if pexecutortick.TAIL = eps',
        'checks': [
            'pexecutortick.ENTRY = ptickentry', 'S.TICKENTRIES = eps',
            'ptickentry.ENTRY.ARGS = [PARRAY n_payload]',
            '$heap_owners($heap_graph(S), HARRAY n_payload) = 1',
            '$node_children(S, HARRAY n_payload) = [HARRAY n_inner]',
            '$heap_owners($heap_graph(S), HARRAY n_inner) = 1',
            '$node_children(S, HARRAY n_inner) = [HOBJECT n_arg]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback2) = 2',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("C1;")]',
            *VALID,
        ],
    },
    'copied-array-keeps-live-mutated-reference-cell': {
        'source': source('array_reference'),
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_payload), DESTRUCTION_VALUE (HARRAY n_payload), DESTRUCTION_VALUE (HOBJECT n_callback), DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.ENTRY = ptickentry',
        'checks': [
            'ptickentry.ENTRY.ARGS = [PARRAY n_payload, PARRAY n_payload]',
            'S.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]',
            'S.STORE[n_cell] = DEFINED (POBJECT n_arg)',
            '$node_children(S, HARRAY n_payload) = [HCELL n_cell]',
            '$node_children(S, HCELL n_cell) = [HOBJECT n_arg]',
            '$heap_owners($heap_graph(S), HARRAY n_payload) = 2',
            '$heap_owners($heap_graph(S), HCELL n_cell) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '$object_name(S, n_arg) = $ptascii("ReferenceArrayTickArg")',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID, *DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("C;")]',
            '~((HARRAY n_payload) <- S_done.ALLOCATIONS)',
            '~((HCELL n_cell) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_arg) <- S_done.ALLOCATIONS)',
        ],
    },
    'retired-array-history-does-not-own-its-reference-or-object': {
        'source': source('array_reference'),
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback), DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.ENTRY = ptickentry -- if ptickentry.ENTRY.ARGS = [PARRAY n_payload, PARRAY n_payload]',
        'checks': [
            'S.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]',
            'S.STORE[n_cell] = DEFINED (POBJECT n_arg)',
            '~((HARRAY n_payload) <- S.ALLOCATIONS)',
            '~((HCELL n_cell) <- S.ALLOCATIONS)',
            '~((HOBJECT n_arg) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HARRAY n_payload) = 0',
            '$heap_owners($heap_graph(S), HCELL n_cell) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '$task_nodes(EXECUTOR_TICK_RELEASE pexecutortick false) = eps',
            '~$tick_entry_valid(S, ptickentry)',
            'n_arg <- S.DESTRUCTION.CALLED',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;")]',
            *VALID,
        ],
    },
    'nested-self-is-an-array-child-owner-before-fcc': {
        'source': source('nested_self'),
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_payload), DESTRUCTION_VALUE (HOBJECT n_callback), DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.ENTRY = ptickentry',
        'checks': [
            'ptickentry.ENTRY.ARGS = [PARRAY n_payload]',
            '$node_children(S, HARRAY n_payload) = [HARRAY n_inner, HOBJECT n_arg]',
            '$node_children(S, HARRAY n_inner) = [HOBJECT n_callback]',
            '$heap_owners($heap_graph(S), HARRAY n_payload) = 1',
            '$heap_owners($heap_graph(S), HARRAY n_inner) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            '$object_name(S, n_callback) = $ptascii("NestedSelfTickCaller")',
            '~(n_callback <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID, *DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("C;")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_callback) = 0',
            'n_callback <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'cow-write-keeps-the-registered-array-snapshot': {
        'source': (HERE / 'deprecated_late_tick_values_cow.php').read_text(),
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_payload), DESTRUCTION_VALUE (HOBJECT n_callback), DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.ENTRY = ptickentry',
        'checks': [
            'ptickentry.ENTRY.ARGS = [PARRAY n_payload]',
            'S.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_arg))]',
            '$heap_owners($heap_graph(S), HARRAY n_payload) = 1',
            '$node_children(S, HARRAY n_payload) = [HOBJECT n_arg]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '$object_name(S, n_arg) = $ptascii("CowTickArg")',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID, *DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("C;")]',
            '~((HARRAY n_payload) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_arg) <- S_done.ALLOCATIONS)',
        ],
    },
}


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=210) else 1)
