#!/usr/bin/env python3
"""Reach post-FINAL user tick argument and duplicate FCC retirement."""
from pathlib import Path

import fiber_state_review as review


SOURCE = Path(__file__).with_name('deprecated_late_tick_final_raw.php').read_text()
SHUTDOWN_PEER = Path(__file__).with_name('deprecated_late_tick_final_shutdown_peer.php').read_text()
review.CASES = {
    'post-final-raw-invokable-tick-release': {
        'source': SOURCE,
        'stage': 'S.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, DESTRUCTOR_OPERATION_EXIT pdestructionoperation, EXECUTOR_TICK_RELEASE pexecutortick false] '
                 '-- if pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true '
                 '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_argument), DESTRUCTION_VALUE (HOBJECT n_callback), DESTRUCTION_VALUE (HOBJECT n_callback)]',
        'checks': [
            'pexecutortick.ENTRY = ptickentry',
            'ptickentry.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback)), NAMED_SENT (KNOWN (POBJECT n_argument))]',
            'ptickentry.ENTRY.ARGS = [POBJECT n_argument]',
            'ptickentry.ENTRY.CACHEOBJECT = (n_callback)',
            '$callback_cache_nodes(ptickentry.ENTRY) = [HOBJECT n_callback, HOBJECT n_callback]',
            '$executor_tick_nodes(ptickentry) = [HOBJECT n_argument, HOBJECT n_callback, HOBJECT n_callback]',
            '$task_nodes(EXECUTOR_TICK_RELEASE pexecutortick true) = $executor_tick_nodes(ptickentry)',
            '$task_nodes(EXECUTOR_TICK_RELEASE pexecutortick false) = eps',
            'S.TICKENTRIES = eps',
            'S.ASSERTCALLBACK = eps',
            'S.SHUTDOWN.ENTRIES = eps',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            '$heap_owners($heap_graph(S), HOBJECT n_argument) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '$executor_tick_valid(S, pexecutortick)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '~$executor_tick_valid(S, pexecutortick[.RECEIVER = eps])',
            '~$executor_tick_ready(S[.TICKENTRIES = [ptickentry, ptickentry]])',
            '$call_descriptors_valid(S)',
            '$heap_valid($heap_graph(S))',
            'S_paused = $drive_steps(S, 0)',
            r'S_paused.COMPLETION = BUDGET /\ S_paused.TODO = S.TODO',
            'S_done = $drive_steps(S, 4000)',
            '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            'S_done.COMPLETION = NORMAL',
            r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("C;")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_argument) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_callback) = 0',
            'n_argument <- S_done.DESTRUCTION.CALLED',
            'n_callback <- S_done.DESTRUCTION.CALLED',
            '$call_descriptors_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'post-final-fcc-object-decrement-precedes-closure': {
        'source': SOURCE,
        'stage': 'S.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, DESTRUCTOR_OPERATION_EXIT pdestructionoperation, EXECUTOR_TICK_RELEASE pexecutortick false] '
                 '-- if pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true '
                 '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback)]',
        'checks': [
            'pexecutortick.ENTRY = ptickentry',
            'ptickentry.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback)), NAMED_SENT (KNOWN (POBJECT n_argument))]',
            '$executor_tick_nodes(ptickentry) = [HOBJECT n_argument, HOBJECT n_callback, HOBJECT n_callback]',
            'S.TICKENTRIES = eps',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;")]',
            '$heap_owners($heap_graph(S), HOBJECT n_argument) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            'n_argument <- S.DESTRUCTION.CALLED',
            '~(n_callback <- S.DESTRUCTION.CALLED)',
            '$executor_tick_valid(S, pexecutortick)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$call_descriptors_valid(S)',
            '$heap_valid($heap_graph(S))',
            'S_done = $drive_steps(S, 4000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("C;")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_callback) = 0',
            'n_callback <- S_done.DESTRUCTION.CALLED',
            '$call_descriptors_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'post-final-tick-free-keeps-shutdown-entry-until-queue': {
        'source': SHUTDOWN_PEER,
        'stage': 'S.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, DESTRUCTOR_OPERATION_EXIT pdestructionoperation, EXECUTOR_TICK_RELEASE pexecutortick false] '
                 '-- if pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true '
                 '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_argument), DESTRUCTION_VALUE (HOBJECT n_callback), DESTRUCTION_VALUE (HOBJECT n_callback)]',
        'checks': [
            'pexecutortick.ENTRY = ptickentry',
            '$executor_tick_nodes(ptickentry) = [HOBJECT n_argument, HOBJECT n_callback, HOBJECT n_callback]',
            'S.TICKENTRIES = eps',
            'S.SHUTDOWN.ENTRIES = [pshutdownentry]',
            '$shutdown_roots([pshutdownentry]) = eps',
            'S.EVENTS = [OUTPUT $ptascii("B;S;F;")]',
            '$heap_owners($heap_graph(S), HOBJECT n_argument) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '$executor_tick_valid(S, pexecutortick)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$call_descriptors_valid(S)',
            '$heap_valid($heap_graph(S))',
            'S_done = $drive_steps(S, 4000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.SHUTDOWN.ENTRIES = eps',
            'S_done.EVENTS = [OUTPUT $ptascii("B;S;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("C;")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_argument) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_callback) = 0',
            '$call_descriptors_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=150) else 1)
