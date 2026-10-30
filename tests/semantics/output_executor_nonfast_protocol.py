#!/usr/bin/env python3
"""Source-reached storage shields and caught post-output queue release."""
import argparse
from pathlib import Path

import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SLOW_ENV = [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one'),
            (b'USE_ZEND_ALLOC', b'0')]
VALID = ['$call_descriptors_valid(S)', '$destruction_state_valid(S)',
         '$output_state_valid(S)', '$heap_valid($heap_graph(S))']
PAUSE = ['S_zero = $drive_steps(S, 0)',
         'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
         'S_zero.ALLOCATIONS = S.ALLOCATIONS /\\ S_zero.EVENTS = S.EVENTS',
         'S_done = $drive_steps(S, 1000)',
         '$drive_steps(S_zero[.COMPLETION = NORMAL], 1000) = S_done']
DONE = ['$call_descriptors_valid(S_done)', '$destruction_state_valid(S_done)',
        '$output_state_valid(S_done)', '$gc_state_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        'S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps']
STORE = [
    'S.REQUEST = (Q)', '$request_valid(Q) /\\ ~$executor_allocator_fast((Q))',
    'S.COMPLETION = NORMAL /\\ S.OUTPUTBUFFERS = eps',
    'S.EVENTS = [OUTPUT $ptascii("B|T|")]',
    'S_endpoint = S[.TODO = eps][.COMPLETION = pobdrain.COMPLETION][.RESULT = pobdrain.VALUE][.BASE = pobdrain.BASE][.ORIGIN = pobdrain.ORIGIN]',
    '$executor_free_endpoint(S_endpoint)',
    'pexecutorfree_start = {HEAP $heap_graph(S_endpoint), MARKED eps, FAILED eps, UNKNOWN false}',
    'pexecutorfree_tables = $executor_free_tables(S_endpoint, pexecutorfree_start)',
    'pexecutorfree_tables.FAILED = eps /\\ ~pexecutorfree_tables.UNKNOWN',
    '$heap_owners(pexecutorfree_tables.HEAP, HOBJECT n_child) = 1',
    '$heap_owners(pexecutorfree_tables.HEAP, HOBJECT n_holder) = 1',
    '$node_children(S, HOBJECT n_holder) = [HOBJECT n_holder, HOBJECT n_child]',
    '~(n_child <- S.DESTRUCTION.CALLED) /\\ ~(n_holder <- S.DESTRUCTION.CALLED)',
    *VALID,
]


def source(name):
    return (HERE / ('output_executor_nonfast_' + name + '.php')).read_text()


review.ROOT = ROOT
review.CASES = {
    'unswept-child-reaches-inactive-callback-before-shield': {
        'source': source('child_first'), 'request_env': SLOW_ENV,
        'stage': 'S.TODO = [OUTPUT_DRAIN pobdrain] -- if S.OUTPUTBUFFERS = eps',
        'checks': [
            'n_child = 1', 'n_holder = 2', *STORE,
            '$object_name(S, n_child) = $ptascii("BornChildOB05")',
            '$object_name(S, n_holder) = $ptascii("CycleHolderOB05")',
            'pexecutorfree_holder = $executor_free_force(S_endpoint, pexecutorfree_tables, n_holder)',
            'pexecutorfree_holder.FAILED = (n_child)',
            '~pexecutorfree_holder.UNKNOWN',
            '$heap_owners(pexecutorfree_holder.HEAP, HOBJECT n_child) = 0',
            '$heap_owners(pexecutorfree_holder.HEAP, HOBJECT n_holder) = 1',
            'pexecutorfree_borrowed = pexecutorfree_tables[.HEAP.ROOTS = pexecutorfree_tables.HEAP.ROOTS ++ [HOBJECT n_child]]',
            'pexecutorfree_protected = $executor_free_walk(S_endpoint, pexecutorfree_borrowed, S.DESTRUCTION.NEXT)',
            'pexecutorfree_protected.FAILED = eps /\\ ~pexecutorfree_protected.UNKNOWN',
            *PAUSE,
            'ptbytes_message = $ptascii("Couldn\'t execute method BornChildOB05::__destruct")',
            'S_done.COMPLETION = REQUESTFATAL ($ptascii("Error")) ptbytes_message 0',
            'S_done.EXITSTATUS = 0',
            'S_done.DESTRUCTION.CALLED = $destructor_all(0, |S_done.OBJECTS|)',
            'preqbytes_late = $ptascii("Fatal error: ") ++ ptbytes_message ++ $ptascii(" in Unknown on line 0") ++ [10] ++ $ptascii("Stack trace:") ++ [10] ++ $ptascii("#0 {main}") ++ [10]',
            'S_done.EVENTS = [OUTPUT $ptascii("B|T|"), STDERR preqbytes_late]',
            '$output_executor_finish(S_done) = S_done',
            '$output_executor_finish(S_endpoint[.COMPLETION = BUDGET]) = S_endpoint[.COMPLETION = BUDGET]',
            *DONE,
        ],
    },
    'already-swept-standard-child-keeps-its-protective-count': {
        'source': source('holder_first'), 'request_env': SLOW_ENV,
        'stage': 'S.TODO = [OUTPUT_DRAIN pobdrain] -- if S.OUTPUTBUFFERS = eps',
        'checks': [
            'n_holder = 1', 'n_child = 2', *STORE,
            'pexecutorfree_child = $executor_free_force(S_endpoint, pexecutorfree_tables, n_child)',
            'pexecutorfree_child.FAILED = eps /\\ ~pexecutorfree_child.UNKNOWN',
            'pexecutorfree_child.MARKED = [HOBJECT n_child]',
            '$heap_owners(pexecutorfree_child.HEAP, HOBJECT n_child) = 2',
            '$executor_free_force(S_endpoint, pexecutorfree_child, n_child) = pexecutorfree_child',
            'pexecutorfree_holder = $executor_free_force(S_endpoint, pexecutorfree_child, n_holder)',
            'pexecutorfree_holder.FAILED = eps /\\ ~pexecutorfree_holder.UNKNOWN',
            '$heap_owners(pexecutorfree_holder.HEAP, HOBJECT n_child) = 1',
            '$heap_owners(pexecutorfree_holder.HEAP, HOBJECT n_holder) = 1',
            '$heap_children(HOBJECT n_holder, pexecutorfree_holder.HEAP.EDGES) = eps',
            *PAUSE,
            'S_done.COMPLETION = NORMAL /\\ S_done.EXITSTATUS = 0',
            'S_done.EVENTS = [OUTPUT $ptascii("B|T|")]',
            '~(n_child <- S_done.DESTRUCTION.CALLED)',
            '$output_executor_finish(S_done) = S_done',
            *DONE,
        ],
    },
    'caught-argument-throw-retains-real-unfinished-fcc-owner': {
        'source': source('shutdown_throw'), 'request_env': SLOW_ENV,
        'stage': 'S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_tail* '
                 '-- if pdestructorcall.OPERATION = (pdestructionoperation) '
                 '-- if pdestructionoperation.SOURCE = EXECUTOR_RELEASE pexecutorqueue EXECUTOR_QUEUE',
        'checks': [
            'n_argument = pdestructorcall.OBJECT', 'n_argument = 3',
            'n_capture = 1', 'n_closure = 2',
            '$object_name(S, n_argument) = $ptascii("LateArgumentOB05")',
            '$object_name(S, n_capture) = $ptascii("LateFccCaptureOB05")',
            '~pdestructorcall.USER /\\ pdestructorcall.CALLER = eps',
            'pdestructorcall.SITE = eps /\\ pdestructorcall.LINE = 0',
            'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ORIGIN = eps',
            'S.OUTPUTBUFFERS = eps /\\ S.SHUTDOWN.ENTRIES = eps /\\ S.SHUTDOWN.INDEX = 0',
            'S.EVENTS = [OUTPUT $ptascii("B|T|")]',
            'pdestructorcall.RELEASE = (pdestructionrelease)',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_argument), DESTRUCTION_VALUE (HOBJECT n_closure)]',
            '$heap_owners($heap_graph(S), HOBJECT n_argument) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_closure) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_capture) = 1',
            '(n_argument <- S.DESTRUCTION.CALLED) /\\ ~(n_capture <- S.DESTRUCTION.CALLED)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            *VALID, *PAUSE,
            'ptbytes_message = $ptascii("Couldn\'t execute method LateFccCaptureOB05::__destruct")',
            'S_done.COMPLETION = REQUESTFATAL ($ptascii("Error")) ptbytes_message 0',
            'S_done.EXITSTATUS = 0',
            'S_done.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
            'pdestructioncleanup.SOURCE = DESTRUCTOR_RESULT pdestructorcall',
            '~pdestructioncleanup.RELEASED',
            '$eager_cleanup_valid(S_done, pdestructioncleanup)',
            '$eager_abandoned_owner(pdestructioncleanup.SOURCE) = [HOBJECT n_argument, HOBJECT n_argument, HOBJECT n_closure]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_argument) = 2',
            '$heap_owners($heap_graph(S_done), HOBJECT n_closure) = 1',
            '$heap_owners($heap_graph(S_done), HOBJECT n_capture) = 1',
            'preqbytes_file = $call_sourcefile(S.FILES, PORIGIN 0 eps)',
            'preqbytes_first = $ptascii("Fatal error: Uncaught Exception: late-queue-secondary in ") ++ preqbytes_file ++ $ptascii(":8") ++ [10] ++ $ptascii("Stack trace:") ++ [10] ++ $ptascii("#0 [internal function]: LateArgumentOB05->__destruct()") ++ [10] ++ $ptascii("#1 {main}") ++ [10] ++ $ptascii("  thrown in ") ++ preqbytes_file ++ $ptascii(" on line 8") ++ [10]',
            'preqbytes_late = $ptascii("Fatal error: ") ++ ptbytes_message ++ $ptascii(" in Unknown on line 0") ++ [10] ++ $ptascii("Stack trace:") ++ [10] ++ $ptascii("#0 {main}") ++ [10]',
            'S_done.EVENTS = [OUTPUT $ptascii("B|T|"), OUTPUT $ptascii("Q|"), STDERR preqbytes_first, STDERR preqbytes_late]',
            'S_done.DESTRUCTION.CALLED = $destructor_all(0, |S_done.OBJECTS|)',
            'S_missing = S_done[.DESTRUCTION.ABANDONED = eps]',
            '~$eager_operation_source_valid(S_missing[.DESTRUCTION.PHASE = DESTRUCTION_STORE], pdestructionoperation)',
            '$output_executor_finish(S_done) = S_done',
            *DONE,
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case) else 1)
