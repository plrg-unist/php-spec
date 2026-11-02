#!/usr/bin/env python3
"""Reach duplicate raw-object FCC owners at post-output queue retirement."""
from pathlib import Path

import fiber_state_review as review


source = Path(__file__).with_name('callback_cache_executor_raw.php').read_text()
review.CASES = {
    'shutdown-raw-invokable-cache-release': {
        'source': source,
        'stage': 'S.TODO = [EXECUTOR_RELEASE pexecutorqueue EXECUTOR_QUEUE]',
        'checks': [
            'pexecutorqueue.ENTRIES = [pshutdownentry, pshutdownentry_probe]',
            'pshutdownentry.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n))]',
            'pshutdownentry.CACHEOBJECT = (n)',
            '$object_name(S, n) = $ptascii("ShutdownRawInvoker")',
            '$callback_cache_closure(pshutdownentry) = (n)',
            '$callback_cache_nodes(pshutdownentry) = [HOBJECT n, HOBJECT n]',
            '$callback_cache_nodes(pshutdownentry_probe) = eps',
            '$executor_queue_nodes(pexecutorqueue.ENTRIES) = [HOBJECT n, HOBJECT n]',
            '$task_nodes(EXECUTOR_RELEASE pexecutorqueue EXECUTOR_QUEUE) = [HOBJECT n, HOBJECT n]',
            '$heap_owners($heap_graph(S), HOBJECT n) = 2',
            '$executor_queue_valid(S, pexecutorqueue)',
            '$call_task_valid(S, EXECUTOR_RELEASE pexecutorqueue EXECUTOR_QUEUE)',
            '$call_descriptors_valid(S)',
            '$heap_valid($heap_graph(S))',
            'S_paused = $drive_steps(S, 0)',
            r'S_paused.COMPLETION = BUDGET /\ S_paused.TODO = S.TODO',
            'S_done = $drive_steps(S, 4000)',
            '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            'S_done.COMPLETION = NORMAL',
            r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
            '$heap_owners($heap_graph(S_done), HOBJECT n) = 0',
            'n <- S_done.DESTRUCTION.CALLED',
            '$call_descriptors_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=150) else 1)
