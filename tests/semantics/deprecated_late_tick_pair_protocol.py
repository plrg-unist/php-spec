#!/usr/bin/env python3
"""Reach both ordered post-FINAL tick FCC retirement boundaries."""
from pathlib import Path

import fiber_state_review as review


SOURCE = Path(__file__).with_name('deprecated_late_tick_pair_raw.php').read_text()
PREFIX = ('S.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, '
          'DESTRUCTOR_OPERATION_EXIT pdestructionoperation, '
          'EXECUTOR_TICK_RELEASE pexecutortick false] '
          '-- if pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true ')
VALID = ['$executor_tick_valid(S, pexecutortick)',
         '$eager_operation_source_valid(S, pdestructionoperation)',
         '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
DONE = ['S_done.COMPLETION = NORMAL',
        'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A1;"), '
        'OUTPUT $ptascii("C1;"), OUTPUT $ptascii("A2;"), OUTPUT $ptascii("C2;")]',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']

review.CASES = {
    'first-tick-owns-only-its-argument-and-two-fcc-slots': {
        'source': SOURCE,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_arg1), DESTRUCTION_VALUE (HOBJECT n_callback1), DESTRUCTION_VALUE (HOBJECT n_callback1)]',
        'checks': [
            'pexecutortick.ENTRY = ptickentry_first',
            'pexecutortick.TAIL = [ptickentry_second]',
            'ptickentry_first.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback1)), NAMED_SENT (KNOWN (POBJECT n_arg1))]',
            'ptickentry_second.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback2)), NAMED_SENT (KNOWN (POBJECT n_arg2))]',
            '$object_name(S, n_arg1) = $ptascii("TickArgOne")',
            '$object_name(S, n_callback1) = $ptascii("TickCallerOne")',
            '$object_name(S, n_arg2) = $ptascii("TickArgTwo")',
            '$object_name(S, n_callback2) = $ptascii("TickCallerTwo")',
            'S.TICKENTRIES = [ptickentry_second]',
            '$tick_entries_valid(S, [ptickentry_first, ptickentry_second], 0)',
            '~$tick_entries_valid(S, [ptickentry_second, ptickentry_first], 0)',
            '$executor_tick_nodes(ptickentry_first) = [HOBJECT n_arg1, HOBJECT n_callback1, HOBJECT n_callback1]',
            '$task_nodes(EXECUTOR_TICK_RELEASE pexecutortick true) = $executor_tick_nodes(ptickentry_first)',
            '$task_nodes(EXECUTOR_TICK_RELEASE pexecutortick false) = eps',
            '$tick_roots(S.TICKENTRIES) = [HOBJECT n_callback2, HOBJECT n_callback2, HOBJECT n_arg2]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg1) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback1) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_arg2) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback2) = 2',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID,
            'S_paused = $drive_steps(S, 0)',
            r'S_paused.COMPLETION = BUDGET /\ S_paused.TODO = S.TODO',
            'S_done = $drive_steps(S, 4000)',
            '$drive_steps(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            *DONE,
            '$heap_owners($heap_graph(S_done), HOBJECT n_callback1) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_callback2) = 0',
        ],
    },
    'first-fcc-object-decrement-leaves-closure-owner': {
        'source': SOURCE,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback1)] -- if pexecutortick.TAIL = [ptickentry_second]',
        'checks': [
            'pexecutortick.ENTRY = ptickentry_first',
            'ptickentry_first.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback1)), NAMED_SENT (KNOWN (POBJECT n_arg1))]',
            'ptickentry_second.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback2)), NAMED_SENT (KNOWN (POBJECT n_arg2))]',
            'S.TICKENTRIES = [ptickentry_second]',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A1;")]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg1) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_callback1) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_arg2) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback2) = 2',
            'n_arg1 <- S.DESTRUCTION.CALLED',
            '~(n_callback1 <- S.DESTRUCTION.CALLED)',
            *VALID,
            'S_done = $drive_steps(S, 4000)',
            *DONE,
        ],
    },
    'second-tick-starts-after-first-fcc-retirement': {
        'source': SOURCE,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_arg2), DESTRUCTION_VALUE (HOBJECT n_callback2), DESTRUCTION_VALUE (HOBJECT n_callback2)] -- if pexecutortick.TAIL = eps',
        'checks': [
            'n_callback1 = 0',
            'n_arg1 = 1',
            '$object_name(S, n_callback1) = $ptascii("TickCallerOne")',
            '$object_name(S, n_arg1) = $ptascii("TickArgOne")',
            '$heap_owners($heap_graph(S), HOBJECT n_callback1) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_arg1) = 0',
            'n_callback1 <- S.DESTRUCTION.CALLED',
            'n_arg1 <- S.DESTRUCTION.CALLED',
            'pexecutortick.ENTRY = ptickentry_second',
            'pexecutortick.TAIL = eps',
            'ptickentry_second.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback2)), NAMED_SENT (KNOWN (POBJECT n_arg2))]',
            '$object_name(S, n_arg2) = $ptascii("TickArgTwo")',
            '$object_name(S, n_callback2) = $ptascii("TickCallerTwo")',
            'S.TICKENTRIES = eps',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A1;"), OUTPUT $ptascii("C1;")]',
            '$executor_tick_nodes(ptickentry_second) = [HOBJECT n_arg2, HOBJECT n_callback2, HOBJECT n_callback2]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg2) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback2) = 2',
            *VALID,
            'S_done = $drive_steps(S, 4000)',
            *DONE,
            '$heap_owners($heap_graph(S_done), HOBJECT n_callback2) = 0',
        ],
    },
    'second-fcc-object-decrement-leaves-closure-owner': {
        'source': SOURCE,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback2)] -- if pexecutortick.TAIL = eps',
        'checks': [
            'pexecutortick.ENTRY = ptickentry_second',
            'ptickentry_second.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback2)), NAMED_SENT (KNOWN (POBJECT n_arg2))]',
            'S.TICKENTRIES = eps',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A1;"), OUTPUT $ptascii("C1;"), OUTPUT $ptascii("A2;")]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg2) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_callback2) = 1',
            'n_arg2 <- S.DESTRUCTION.CALLED',
            '~(n_callback2 <- S.DESTRUCTION.CALLED)',
            *VALID,
            'S_done = $drive_steps(S, 4000)',
            *DONE,
            '$heap_owners($heap_graph(S_done), HOBJECT n_callback2) = 0',
        ],
    },
}


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=180) else 1)
