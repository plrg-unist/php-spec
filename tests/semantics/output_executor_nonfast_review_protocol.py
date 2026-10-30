#!/usr/bin/env python3
"""Independent nonfast table order and bound shutdown FCC owner checks."""
import argparse
from pathlib import Path

import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SLOW_ENV = [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one'),
            (b'USE_ZEND_ALLOC', b'0')]
VALID = ['$call_descriptors_valid(S)', '$destruction_state_valid(S)',
         '$output_state_valid(S)', '$heap_valid($heap_graph(S))']
ENDPOINT = [
    'S.REQUEST = (Q)',
    '$request_valid(Q) /\\ ~$executor_allocator_fast((Q))',
    'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ORIGIN = eps',
    'S.COMPLETION = NORMAL /\\ S.EXITSTATUS = 0',
    'S.OUTPUTBUFFERS = eps /\\ S.SHUTDOWN.ENTRIES = eps',
    'S.EVENTS = [OUTPUT $ptascii("B|T|A:live|")]',
    'S.DESTRUCTION.CALLS = eps /\\ S.DESTRUCTION.RELEASES = eps',
    'S.DESTRUCTION.FRAMES = eps /\\ S.DESTRUCTION.OPERATIONS = eps',
    'S_endpoint = S[.TODO = eps][.COMPLETION = pobdrain.COMPLETION][.RESULT = pobdrain.VALUE][.BASE = pobdrain.BASE][.ORIGIN = pobdrain.ORIGIN]',
    '$executor_free_endpoint(S_endpoint)',
    'pexecutorfree_start = {HEAP $heap_graph(S_endpoint), MARKED eps, FAILED eps, UNKNOWN false}',
    'pexecutorfree_tables = $executor_free_tables(S_endpoint, pexecutorfree_start)',
    '~pexecutorfree_tables.UNKNOWN',
    *VALID,
]


def source(name):
    return (HERE / ('output_executor_nonfast_' + name + '.php')).read_text()


def finish(owner):
    return [
        'S_zero = $drive_steps(S, 0)',
        'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
        'S_zero.ALLOCATIONS = S.ALLOCATIONS /\\ S_zero.EVENTS = S.EVENTS',
        'S_done = $drive_steps(S, 600)',
        '$drive_steps(S_zero[.COMPLETION = NORMAL], 600) = S_done',
        'ptbytes_late_message = $ptascii("Couldn\'t execute method ' + owner + '::__destruct")',
        'S_done.COMPLETION = REQUESTFATAL ($ptascii("Error")) ptbytes_late_message 0',
        'S_done.EXITSTATUS = 0 /\\ S_done.TODO = eps /\\ S_done.OUTPUTBUFFERS = eps',
        'preqbytes_late = $ptascii("Fatal error: ") ++ ptbytes_late_message ++ $ptascii(" in Unknown on line 0") ++ [10] ++ $ptascii("Stack trace:") ++ [10] ++ $ptascii("#0 {main}") ++ [10]',
        'S_done.EVENTS = [OUTPUT $ptascii("B|T|A:live|"), STDERR preqbytes_late]',
        'S_done.DESTRUCTION.CALLED = $destructor_all(0, |S_done.OBJECTS|)',
        '$call_descriptors_valid(S_done)',
        '$destruction_state_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
    ]


review.ROOT = ROOT
review.CASES = {
    'reverse-global-symbol-insertion-before-store': {
        'source': source('global_order_peer'),
        'request_env': SLOW_ENV,
        'stage': 'S.TODO = [OUTPUT_DRAIN pobdrain] -- if S.OUTPUTBUFFERS = eps',
        'checks': [
            *ENDPOINT,
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("first_hold_ob05")) = (n_first_cell)',
            '$lookup(S_global.ENV, $ptascii("second_hold_ob05")) = (n_second_cell)',
            'S.STORE[n_first_cell] = DEFINED (POBJECT n_first)',
            'S.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
            '$object_name(S, n_first) = $ptascii("FirstGlobalOwnerOB05")',
            '$object_name(S, n_second) = $ptascii("SecondGlobalOwnerOB05")',
            '$(n_second < n_first)',
            '~(n_first <- S.DESTRUCTION.CALLED) /\\ ~(n_second <- S.DESTRUCTION.CALLED)',
            '$heap_owners($heap_graph(S), HOBJECT n_first) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_second) = 1',
            'pexecutorfree_tables.FAILED = (n_second)',
            '$heap_owners(pexecutorfree_tables.HEAP, HOBJECT n_second) = 0',
            '$heap_owners(pexecutorfree_tables.HEAP, HOBJECT n_first) = 1',
            '$lookup(S_global.ENV, $ptascii("global_stage_ob05")) = (n_stage)',
            'S.STORE[n_stage] = DEFINED pvalue_stage',
            '$string_bytes(pvalue_stage) = $ptascii("live")',
            *finish('SecondGlobalOwnerOB05'),
            'S_done.STORE[n_stage] = DEFINED pvalue_stage',
        ],
    },
    'reverse-function-publication-before-static-cell-birth': {
        'source': source('function_static_peer'),
        'request_env': SLOW_ENV,
        'stage': 'S.TODO = [OUTPUT_DRAIN pobdrain] -- if S.OUTPUTBUFFERS = eps',
        'checks': [
            *ENDPOINT,
            'S.STATICS = [pstaticcell_second, pstaticcell_first]',
            'S.STORE[pstaticcell_first.CELL] = DEFINED (POBJECT n_first)',
            'S.STORE[pstaticcell_second.CELL] = DEFINED (POBJECT n_second)',
            '$object_name(S, n_first) = $ptascii("FirstStaticOwnerOB05")',
            '$object_name(S, n_second) = $ptascii("SecondStaticOwnerOB05")',
            '$(n_second < n_first)',
            '~(n_first <- S.DESTRUCTION.CALLED) /\\ ~(n_second <- S.DESTRUCTION.CALLED)',
            '$heap_owners($heap_graph(S), HOBJECT n_first) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_second) = 1',
            'pexecutorfree_tables.FAILED = (n_second)',
            '$heap_owners(pexecutorfree_tables.HEAP, HOBJECT n_first) = 1',
            '$heap_owners(pexecutorfree_tables.HEAP, HOBJECT n_second) = 0',
            'S_permuted = S_endpoint[.STATICS = [pstaticcell_first, pstaticcell_second]]',
            '$executor_table_nodes(S_permuted) = $executor_table_nodes(S_endpoint)',
            '$executor_free_tables(S_permuted, pexecutorfree_start) = pexecutorfree_tables',
            *finish('SecondStaticOwnerOB05'),
        ],
    },
    'oldest-saved-error-handler-before-reverse-store': {
        'source': source('stack_order_peer'),
        'request_env': SLOW_ENV,
        'stage': 'S.TODO = [OUTPUT_DRAIN pobdrain] -- if S.OUTPUTBUFFERS = eps',
        'checks': [
            *ENDPOINT,
            'S.ERRORHANDLER.CALLBACK = eps /\\ S.EXCEPTIONHANDLER = eps',
            'S.ERRORHANDLERS = [perrorhandler_second, perrorhandler_first, perrorhandler_none]',
            'perrorhandler_none.CALLBACK = eps',
            'perrorhandler_first.CALLBACK = (POBJECT n_first_closure)',
            'perrorhandler_second.CALLBACK = (POBJECT n_second_closure)',
            '$closure_callable(S, n_first_closure) /\\ $closure_callable(S, n_second_closure)',
            '$node_children(S, HOBJECT n_first_closure) = [HOBJECT n_first]',
            '$node_children(S, HOBJECT n_second_closure) = [HOBJECT n_second]',
            '$object_name(S, n_first) = $ptascii("FirstStackCaptureOB05")',
            '$object_name(S, n_second) = $ptascii("SecondStackCaptureOB05")',
            '$(n_first < n_second)',
            '~(n_first <- S.DESTRUCTION.CALLED) /\\ ~(n_second <- S.DESTRUCTION.CALLED)',
            '$heap_owners($heap_graph(S), HOBJECT n_first_closure) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_second_closure) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_first) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_second) = 1',
            'pexecutorfree_tables.FAILED = (n_first)',
            '$heap_owners(pexecutorfree_tables.HEAP, HOBJECT n_first) = 0',
            '$heap_owners(pexecutorfree_tables.HEAP, HOBJECT n_second) = 1',
            *finish('FirstStackCaptureOB05'),
        ],
    },
    'bound-fcc-object-releases-before-closure-this-edge': {
        'source': source('bound_fcc'),
        'request_env': SLOW_ENV,
        'stage': 'S.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, DESTRUCTOR_OPERATION_EXIT pdestructionoperation, EXECUTOR_RELEASE pexecutorqueue EXECUTOR_DONE] '
                 '-- if pdestructionoperation.SOURCE = EXECUTOR_RELEASE pexecutorqueue EXECUTOR_QUEUE '
                 '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_receiver), DESTRUCTION_VALUE (HOBJECT n_closure)]',
        'checks': [
            'S.REQUEST = (Q)',
            '$request_valid(Q) /\\ ~$executor_allocator_fast((Q))',
            'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ORIGIN = eps',
            'S.COMPLETION = NORMAL /\\ S.EXITSTATUS = 0',
            'S.SHUTDOWN.ENTRIES = eps /\\ S.SHUTDOWN.INDEX = 0 /\\ S.OUTPUTBUFFERS = eps',
            'S.EVENTS = [OUTPUT $ptascii("B|T|"), OUTPUT $ptascii("A|")]',
            'pexecutorqueue.COMPLETION = NORMAL',
            'pexecutorqueue.ENTRIES = [pshutdownentry]',
            'pexecutorqueue.TARGETS = [pshutdownproducer]',
            'pshutdownentry.TARGET = CLOSURE_TARGET n_closure',
            'pshutdownentry.ARGS = [POBJECT n_argument]',
            '$object_name(S, n_argument) = $ptascii("BoundFccArgumentOB05")',
            '$object_name(S, n_receiver) = $ptascii("BoundFccReceiverOB05")',
            '$target_receiver(S, CLOSURE_TARGET n_closure) = (n_receiver)',
            '$node_children(S, HOBJECT n_closure) = [HOBJECT n_capture, HOBJECT n_receiver]',
            '$object_name(S, n_capture) = $ptascii("BoundFccCaptureOB05")',
            'pshutdownproducer.SCOPE = (pclosurescope)',
            'pclosurescope.RECEIVER = (n_receiver)',
            '$executor_target_valid(S, pshutdownproducer)',
            'pshutdownproducer_forged = pshutdownproducer[.SCOPE = (pclosurescope[.RECEIVER = (n_capture)])]',
            '~$executor_target_valid(S, pshutdownproducer_forged)',
            '~$executor_targets_valid(S, pexecutorqueue.ENTRIES, [pshutdownproducer_forged])',
            'pexecutorqueue_forged = pexecutorqueue[.TARGETS = [pshutdownproducer_forged]]',
            '~$executor_queue_valid(S, pexecutorqueue_forged)',
            'pshutdownproducer_empty = pshutdownproducer[.SCOPE = eps]',
            '~$executor_target_valid(S, pshutdownproducer_empty)',
            '$executor_queue_nodes(pexecutorqueue.ENTRIES, pexecutorqueue.TARGETS) = [HOBJECT n_argument, HOBJECT n_receiver, HOBJECT n_closure]',
            '$task_nodes(EXECUTOR_RELEASE pexecutorqueue EXECUTOR_DONE) = eps',
            '$heap_count(HOBJECT n_receiver, $task_nodes(DESTRUCTOR_RELEASE pdestructionrelease)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_closure) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_capture) = 1',
            '~(n_receiver <- S.DESTRUCTION.CALLED) /\\ ~(n_capture <- S.DESTRUCTION.CALLED)',
            '(n_argument <- S.DESTRUCTION.CALLED)',
            '~((HOBJECT n_argument) <- S.ALLOCATIONS)',
            '$executor_queue_valid(S, pexecutorqueue)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '~$eager_operation_source_valid(S[.DESTRUCTION.PHASE = DESTRUCTION_STORE], pdestructionoperation)',
            '~$call_task_valid(S[.TODO = [EXECUTOR_RELEASE pexecutorqueue EXECUTOR_QUEUE]], EXECUTOR_RELEASE pexecutorqueue EXECUTOR_QUEUE)',
            '$call_task_valid(S, DESTRUCTOR_RELEASE pdestructionrelease)',
            *VALID,
            'S_one = $drive_steps(S, 1)',
            'S_one.COMPLETION = BUDGET',
            'S_next = S_one[.COMPLETION = NORMAL]',
            'S_next.TODO = [DESTRUCTOR_RELEASE pdestructionrelease_next, DESTRUCTOR_OPERATION_EXIT pdestructionoperation, EXECUTOR_RELEASE pexecutorqueue EXECUTOR_DONE]',
            'pdestructionrelease_next.JOBS = [DESTRUCTION_VALUE (HOBJECT n_closure)]',
            '$heap_owners($heap_graph(S_next), HOBJECT n_receiver) = 1',
            '$heap_count(HOBJECT n_receiver, $task_nodes(DESTRUCTOR_RELEASE pdestructionrelease_next)) = 0',
            '~(n_receiver <- S_next.DESTRUCTION.CALLED)',
            'S_next.EVENTS = S.EVENTS',
            '$call_descriptors_valid(S_next) /\\ $destruction_state_valid(S_next)',
            '$heap_valid($heap_graph(S_next))',
            'S_zero = $drive_steps(S, 0)',
            'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
            'S_done = $drive_steps(S, 600)',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 600) = S_done',
            '$drive_steps(S_next, 600) = S_done',
            'S_done.COMPLETION = NORMAL /\\ S_done.EXITSTATUS = 0',
            'S_done.TODO = eps /\\ S_done.OUTPUTBUFFERS = eps',
            'S_done.EVENTS = [OUTPUT $ptascii("B|T|"), OUTPUT $ptascii("A|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("R|")]',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_closure) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '$call_descriptors_valid(S_done)',
            '$destruction_state_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case) else 1)
