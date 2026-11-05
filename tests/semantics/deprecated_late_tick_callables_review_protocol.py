#!/usr/bin/env python3
"""Check zero-root dispatch and certified tick caches after output FINAL."""
from pathlib import Path

import fiber_state_review as review


HERE = Path(__file__).parent


def source(name):
    return (HERE / f'deprecated_late_tick_callables_review_{name}.php').read_text()


PREFIX = ('S.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, '
          'DESTRUCTOR_OPERATION_EXIT pdestructionoperation, '
          'EXECUTOR_TICK_RELEASE pexecutortick false] '
          '-- if pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true ')
VALID = ['$executor_tick_valid(S, pexecutortick)',
         '$eager_operation_source_valid(S, pdestructionoperation)',
         '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
DONE = ['S_done = $drive_steps(S, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.TICKENTRIES = eps', '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))']
ZERO = ['S.TICKENTRIES = eps', 'pexecutortick.TAIL = eps',
        'pexecutortick.RECEIVER = eps',
        '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = eps',
        '$executor_tick_nodes(pexecutortick.ENTRY) = eps',
        '$task_nodes(EXECUTOR_TICK_RELEASE pexecutortick true) = eps',
        '~$executor_module_owners(S)',
        '$call_task_valid(S, EXECUTOR_TICK_RELEASE pexecutortick true)',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
# Each zero-root group has three explicitly reconstructed endpoint conditions.
ENDPOINT = ['S_endpoint = S[.TODO = eps][.TICKENTRIES = [pexecutortick.ENTRY]][.ORIGIN = pexecutortick.ORIGIN]',
            '$executor_free_endpoint(S_endpoint)',
            '$output_executor_finish(S_endpoint) = S']
DERIVED = {'cacheless-scalar-head-selects-tick-before-free-finish': 3,
           'cacheless-empty-head-selects-tick-before-shutdown-queue': 3,
           'mixed-method-tail-keeps-selector-history-nonowning': 1}

review.CASES = {
    'cacheless-scalar-head-selects-tick-before-free-finish': {
        'source': (HERE / 'deprecated_late_tick_named_scalar.php').read_text(),
        'stage': 'S.TODO = [EXECUTOR_TICK_RELEASE pexecutortick true]',
        'checks': [
            'pexecutortick.ENTRY.ENTRY.ARGS = [PNULL, PINT 7, PSTRING_CARRIER INTERNED_STRING $ptascii("s")]',
            'S.SHUTDOWN.ENTRIES = eps', *ZERO, *ENDPOINT,
            'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.TODO = S.TODO', 'S_paused.ALLOCATIONS = S.ALLOCATIONS',
            *DONE,
            '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            'S_done.SHUTDOWN.ENTRIES = eps',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;")]',
        ],
    },
    'cacheless-empty-head-selects-tick-before-shutdown-queue': {
        'source': (HERE / 'deprecated_late_tick_named_empty_shutdown.php').read_text(),
        'stage': 'S.TODO = [EXECUTOR_TICK_RELEASE pexecutortick true]',
        'checks': [
            'pexecutortick.ENTRY.ENTRY.ARGS = eps',
            'S.SHUTDOWN.ENTRIES = [pshutdownentry]',
            'pshutdownentry.ARGS = eps',
            '$executor_queue_nodes(S.SHUTDOWN.ENTRIES) = eps',
            *ZERO, *ENDPOINT, *DONE,
            'S_done.SHUTDOWN.ENTRIES = eps',
            'S_done.EVENTS = [OUTPUT $ptascii("B;S;F;")]',
        ],
    },
    'unbound-closure-keeps-one-fcc-owner-and-captured-child': {
        'source': source('closure'),
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_arg), DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.ENTRY = ptickentry',
        'checks': [
            'ptickentry.ENTRY.ARGS = [POBJECT n_arg]',
            'ptickentry.ENTRY.TARGET = CLOSURE_TARGET n_callback',
            'ptickentry.ENTRY.CACHEOBJECT = eps',
            '$callback_cache_closure(ptickentry.ENTRY) = (n_callback)',
            '$callback_cache_nodes(ptickentry.ENTRY) = [HOBJECT n_callback]',
            '$executor_tick_nodes(ptickentry) = [HOBJECT n_arg, HOBJECT n_callback]',
            'pexecutortick.RECEIVER = eps',
            '$node_children(S, HOBJECT n_callback) = [HOBJECT n_capture]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_capture) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            '$object_name(S, n_capture) = $ptascii("ClosureTick17Capture")',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID, *DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("K;")]',
            '~((HOBJECT n_callback) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
        ],
    },
    'bound-closure-holds-distinct-fcc-slots-and-receiver-edge': {
        'source': source('bound'),
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_arg), DESTRUCTION_VALUE (HOBJECT n_receiver), DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.ENTRY = ptickentry',
        'checks': [
            'ptickentry.ENTRY.TARGET = CLOSURE_TARGET n_callback',
            'ptickentry.ENTRY.ARGS = [POBJECT n_arg]',
            'ptickentry.ENTRY.CACHEOBJECT = (n_receiver)',
            '$callback_cache_closure(ptickentry.ENTRY) = (n_callback)',
            '$callback_cache_nodes(ptickentry.ENTRY) = [HOBJECT n_receiver, HOBJECT n_callback]',
            'n_callback =/= n_receiver', 'pexecutortick.RECEIVER = (n_receiver)',
            '$node_children(S, HOBJECT n_callback) = [HOBJECT n_receiver]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID,
        ],
    },
    'bound-fcc-object-drops-before-closure-releases-receiver': {
        'source': source('bound'),
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.ENTRY = ptickentry -- if ptickentry.ENTRY.TARGET = CLOSURE_TARGET n_callback -- if pexecutortick.RECEIVER = (n_receiver)',
        'checks': [
            '$callback_cache_nodes(ptickentry.ENTRY) = [HOBJECT n_receiver, HOBJECT n_callback]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1',
            '~(n_receiver <- S.DESTRUCTION.CALLED)',
            '$node_children(S, HOBJECT n_callback) = [HOBJECT n_receiver]',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;")]',
            *VALID, *DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("R;")]',
            '~((HOBJECT n_callback) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        ],
    },
    'mixed-cacheless-head-retains-method-tail-and-shared-array': {
        'source': source('mixed'),
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_payload)] -- if pexecutortick.ENTRY = ptickentry -- if pexecutortick.TAIL = [ptickentry_tail]',
        'checks': [
            'ptickentry.ENTRY.ARGS = [PARRAY n_payload]',
            '$callback_cache_nodes(ptickentry.ENTRY) = eps',
            '$executor_tick_nodes(ptickentry) = [HARRAY n_payload]',
            'pexecutortick.RECEIVER = eps',
            'S.TICKENTRIES = [ptickentry_tail]',
            'ptickentry_tail.ENTRY.ARGS = [PARRAY n_payload]',
            '$callback_cache_nodes(ptickentry_tail.ENTRY) = [HOBJECT n_method]',
            '$tick_roots(S.TICKENTRIES) = [HOBJECT n_method, HARRAY n_payload]',
            '$node_children(S, HARRAY n_payload) = [HOBJECT n_arg, HOBJECT n_method]',
            '$heap_owners($heap_graph(S), HARRAY n_payload) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_method) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID,
        ],
    },
    'mixed-method-tail-keeps-selector-history-nonowning': {
        'source': source('mixed'),
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_payload), DESTRUCTION_VALUE (HOBJECT n_method)] -- if pexecutortick.ENTRY = ptickentry -- if pexecutortick.TAIL = eps',
        'checks': [
            'ptickentry.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (PARRAY n_selector)), NAMED_SENT (KNOWN (PARRAY n_payload))]',
            'ptickentry.ENTRY.ARGS = [PARRAY n_payload]',
            'ptickentry.ENTRY.CACHEOBJECT = (n_method)',
            '$callback_cache_closure(ptickentry.ENTRY) = eps',
            '$callback_cache_nodes(ptickentry.ENTRY) = [HOBJECT n_method]',
            'pexecutortick.RECEIVER = (n_method)',
            '~((HARRAY n_selector) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HARRAY n_selector) = 0',
            '$heap_owners($heap_graph(S), HARRAY n_payload) = 1',
            '$node_children(S, HARRAY n_payload) = [HOBJECT n_arg, HOBJECT n_method]',
            '$heap_owners($heap_graph(S), HOBJECT n_method) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            '~$executor_tick_valid(S, pexecutortick[.ENTRY = ptickentry[.ENTRY = ptickentry.ENTRY[.CALL = ptickentry.ENTRY.CALL[.KIND = INTRINSIC_ERROR_REPORTING]]]])',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID, *DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("M;")]',
            '~((HOBJECT n_method) <- S_done.ALLOCATIONS)',
        ],
    },
}


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=240) else 1)
