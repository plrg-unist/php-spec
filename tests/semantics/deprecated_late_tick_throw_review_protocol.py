#!/usr/bin/env python3
"""Check module-local tick fatal owners, cause retirement and later cleanup."""
from pathlib import Path

import fiber_state_review as review


HERE = Path(__file__).parent


def source(name):
    return (HERE / f'deprecated_late_tick_throw_review_{name}.php').read_text()


ABANDONED = [
    'S.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
    'pdestructioncleanup.SOURCE = DESTRUCTOR_RESULT pdestructorcall',
    'pdestructorcall.OPERATION = (pdestructionoperation)',
    'pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true',
    'pdestructorcall.OBJECT = n_arg', '~pdestructioncleanup.RELEASED',
    '~pdestructorcall.USER', 'pdestructorcall.CALLER = eps',
    'pexecutortick.COMPLETION = NORMAL',
    'S.SHUTDOWN.COMPLETION = NORMAL', 'S.DESTRUCTION.COMPLETION = NORMAL',
]
VALID = ['$executor_tick_abandoned(S, pdestructioncleanup) = (pexecutortick)',
         '$eager_cleanup_valid(S, pdestructioncleanup)',
         '$eager_operation_source_valid(S, pdestructionoperation)',
         '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
FATAL = ['pexecutortickfatal.TICK = pexecutortick',
         'n_cause = pexecutortickfatal.OBJECT',
         '$executor_tick_fatal_valid(S, pexecutortickfatal)',
         'S.EXITSTATUS = 255', 'S.COMPLETION = NORMAL',
         'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), STDERR ptbytes_fatal]']
DONE = ['S_done = $drive_steps(S, 4000)', 'S_done.TODO = eps',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']
DERIVED = {'reported-throwable-does-not-own-unconsumed-module-slots': 7,
           'retired-cause-keeps-no-root-and-tail-never-restarts': 4}

review.CASES = {
    'reported-throwable-does-not-own-unconsumed-module-slots': {
        'source': source('tail'),
        'stage': 'S.TODO = [EXECUTOR_TICK_FATAL pexecutortickfatal true] -- if pexecutortickfatal.TICK.TAIL = [ptickentry_tail]',
        'checks': [
            *ABANDONED, *FATAL,
            'pexecutortick.ENTRY.ENTRY.ARGS = [POBJECT n_arg, POBJECT n_later]',
            '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_callback, HOBJECT n_callback]',
            'S.TICKENTRIES = [ptickentry_tail]',
            'ptickentry_tail.ENTRY.ARGS = [POBJECT n_tail_arg]',
            '$callback_cache_nodes(ptickentry_tail.ENTRY) = [HOBJECT n_tail, HOBJECT n_tail]',
            '$eager_abandoned_owner(pdestructioncleanup.SOURCE) = [HOBJECT n_arg, HOBJECT n_arg, HOBJECT n_later, HOBJECT n_callback, HOBJECT n_callback]',
            '$tick_roots(S.TICKENTRIES) = [HOBJECT n_tail, HOBJECT n_tail, HOBJECT n_tail_arg]',
            '$task_nodes(EXECUTOR_TICK_FATAL pexecutortickfatal true) = [HOBJECT n_cause]',
            '$heap_owners($heap_graph(S), HOBJECT n_cause) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_later) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_tail) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_tail_arg) = 1',
            '$throwable_live(S, n_cause)',
            '$executor_report_cause(S, pexecutortickfatal.COMPLETION, n_cause)',
            '$call_task_valid(S, EXECUTOR_TICK_FATAL pexecutortickfatal true)',
            '~$executor_tick_fatal_valid(S[.EXITSTATUS = 0], pexecutortickfatal)',
            '~$call_task_valid(S[.TODO = [EXECUTOR_TICK_FATAL pexecutortickfatal[.OBJECT = n_callback] true]], EXECUTOR_TICK_FATAL pexecutortickfatal[.OBJECT = n_callback] true)',
            '~$call_task_valid(S[.TODO = [EXECUTOR_TICK_FATAL pexecutortickfatal[.OBJECT = |S.OBJECTS|] true]], EXECUTOR_TICK_FATAL pexecutortickfatal[.OBJECT = |S.OBJECTS|] true)',
            '~$executor_tick_fatal_valid(S[.DESTRUCTION.ABANDONED = eps], pexecutortickfatal)',
            '~$executor_tick_fatal_valid(S[.TICKENTRIES = eps], pexecutortickfatal)',
            '~$executor_tick_fatal_valid(S[.DESTRUCTION.ABANDONED = [pdestructioncleanup[.RELEASED = true]]], pexecutortickfatal)',
            '~$call_task_valid(S[.TODO = [EXECUTOR_TICK_FATAL pexecutortickfatal[.COMPLETION = REQUESTFATAL $ptascii("Exception") $ptascii("forged") 3] true]], EXECUTOR_TICK_FATAL pexecutortickfatal[.COMPLETION = REQUESTFATAL $ptascii("Exception") $ptascii("forged") 3] true)',
            *VALID,
            'PhpStep: S ~> S_pending',
            '$output_final_destructors(S_pending)',
            '$destructor_operational(S_pending)',
            '$call_descriptors_valid(S_pending)',
            '$heap_valid($heap_graph(S_pending))',
        ],
    },
    'retired-cause-keeps-no-root-and-tail-never-restarts': {
        'source': source('tail'),
        'stage': 'S.TODO = [EXECUTOR_TICK_FATAL pexecutortickfatal false] -- if pexecutortickfatal.TICK.TAIL = [ptickentry_tail]',
        'checks': [
            *ABANDONED, *FATAL,
            'pexecutortick.ENTRY.ENTRY.ARGS = [POBJECT n_arg, POBJECT n_later]',
            '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_callback, HOBJECT n_callback]',
            'ptickentry_tail.ENTRY.ARGS = [POBJECT n_tail_arg]',
            '$callback_cache_nodes(ptickentry_tail.ENTRY) = [HOBJECT n_tail, HOBJECT n_tail]',
            'S.TICKENTRIES = [ptickentry_tail]',
            '~((HOBJECT n_cause) <- S.ALLOCATIONS)', '~$throwable_live(S, n_cause)',
            '$objectprops_at(S.OBJECTPROPS, n_cause) = eps',
            '$heap_owners($heap_graph(S), HOBJECT n_cause) = 0',
            '$task_nodes(EXECUTOR_TICK_FATAL pexecutortickfatal false) = eps',
            '~$executor_tick_fatal_valid(S, pexecutortickfatal[.COMPLETION = NORMAL])',
            '~$executor_tick_fatal_valid(S, pexecutortickfatal[.OBJECT = |S.OBJECTS|])',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_later) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_tail) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_tail_arg) = 1',
            'pexecutorqueue_readonly = {COMPLETION pexecutortickfatal.COMPLETION, VALUE KNOWN PNULL, BASE BASE_VALUE (KNOWN PNULL), ORIGIN eps, ENTRIES eps, TARGETS eps, RECEIVERS eps}',
            '~$executor_pending_cause(S, pexecutorqueue_readonly, n_cause)',
            *VALID,
            'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused.TODO = S.TODO', 'S_paused.ALLOCATIONS = S.ALLOCATIONS',
            *DONE,
            'S_done.COMPLETION = pexecutortickfatal.COMPLETION', 'S_done.EXITSTATUS = 255',
            'S_done.TICKENTRIES = [ptickentry_tail]', 'S_done.EVENTS = S.EVENTS',
            '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
        ],
    },
    'scalar-capture-closure-keeps-one-abandoned-fcc-owner': {
        'source': source('closure'),
        'stage': 'S.TODO = [EXECUTOR_TICK_FATAL pexecutortickfatal false]',
        'checks': [
            *ABANDONED, *FATAL,
            '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_callback]',
            'pexecutortick.ENTRY.ENTRY.TARGET = CLOSURE_TARGET n_callback',
            '$node_children(S, HOBJECT n_callback) = eps',
            '$eager_abandoned_owner(pdestructioncleanup.SOURCE) = [HOBJECT n_arg, HOBJECT n_arg, HOBJECT n_callback]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_cause) = 0',
            'S.TICKENTRIES = eps', *VALID, *DONE,
            'S_done.COMPLETION = pexecutortickfatal.COMPLETION', 'S_done.EXITSTATUS = 255',
            'S_done.EVENTS = S.EVENTS',
        ],
    },
    'later-shutdown-queue-runs-with-tick-owners-abandoned': {
        'source': source('shutdown'),
        'stage': 'S.TODO = [EXECUTOR_RELEASE pexecutorqueue EXECUTOR_QUEUE] -- if pexecutorqueue.ENTRIES = [pshutdownentry]',
        'checks': [
            *ABANDONED,
            'pexecutorqueue.COMPLETION = REQUESTFATAL $ptascii("Exception") $ptascii("shutdown-arg-failure") 3',
            'pshutdownentry.ARGS = [POBJECT n_queue_arg]',
            '$callback_cache_nodes(pshutdownentry) = eps',
            '$executor_queue_nodes(pexecutorqueue.ENTRIES) = [HOBJECT n_queue_arg]',
            'S.SHUTDOWN.ENTRIES = eps', 'S.TICKENTRIES = eps',
            '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_callback, HOBJECT n_callback]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_queue_arg) = 1',
            '$executor_scope(S)', '~$executor_tick_scope(S)',
            '$executor_queue_valid(S, pexecutorqueue)',
            'S.EXITSTATUS = 255', 'S.COMPLETION = NORMAL',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), STDERR ptbytes_fatal]',
            *VALID, *DONE,
            'S_done.COMPLETION = pexecutorqueue.COMPLETION', 'S_done.EXITSTATUS = 255',
            'S_done.SHUTDOWN.ENTRIES = eps',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("Q;")]',
        ],
    },
    'owning-closure-capture-reaches-existing-inactive-child-fatal': {
        'source': (HERE / 'deprecated_late_tick_throw_owning_capture.php').read_text(),
        'stage': 'S.TODO = [EXECUTOR_TICK_FATAL pexecutortickfatal false]',
        'checks': [
            *ABANDONED, *FATAL,
            '$callback_cache_nodes(pexecutortick.ENTRY.ENTRY) = [HOBJECT n_callback]',
            '$node_children(S, HOBJECT n_callback) = [HOBJECT n_child]',
            '$object_name(S, n_child) = $ptascii("ThrowCapture19Child")',
            '$eager_abandoned_owner(pdestructioncleanup.SOURCE) = [HOBJECT n_arg, HOBJECT n_arg, HOBJECT n_callback]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_child) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_cause) = 0',
            'S.TICKENTRIES = eps', *VALID, *DONE,
            'S_done.COMPLETION = REQUESTFATAL $ptascii("Error") $ptascii("Couldn\'t execute method ThrowCapture19Child::__destruct") 0',
            'S_done.EXITSTATUS = 0',
            'S_done.EVENTS = S.EVENTS ++ [STDERR ptbytes_late]',
            'n_child <- S_done.DESTRUCTION.CALLED',
        ],
    },
}


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=240) else 1)
