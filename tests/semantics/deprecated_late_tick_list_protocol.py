#!/usr/bin/env python3
"""Reach ordered post-FINAL tick release for a three-entry list."""
from pathlib import Path

import fiber_state_review as review


SOURCE = Path(__file__).with_name('deprecated_late_tick_list_raw.php').read_text()
PREFIX = ('S.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, '
          'DESTRUCTOR_OPERATION_EXIT pdestructionoperation, '
          'EXECUTOR_TICK_RELEASE pexecutortick false] '
          '-- if pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true ')
VALID = ['$executor_tick_valid(S, pexecutortick)',
         '$eager_operation_source_valid(S, pdestructionoperation)',
         '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
FIRST = ['OUTPUT $ptascii("B;F;")']
SECOND = FIRST + ['OUTPUT $ptascii("A1;"), OUTPUT $ptascii("C1;")']
THIRD = SECOND + ['OUTPUT $ptascii("A2;"), OUTPUT $ptascii("C2;")']
DONE = THIRD + ['OUTPUT $ptascii("A3;"), OUTPUT $ptascii("C3;")']

review.CASES = {
    'first-entry-transfers-only-its-roots': {
        'source': SOURCE,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_arg1), DESTRUCTION_VALUE (HOBJECT n_callback1), DESTRUCTION_VALUE (HOBJECT n_callback1)] -- if pexecutortick.TAIL = [ptickentry_second, ptickentry_third]',
        'checks': [
            'pexecutortick.ENTRY = ptickentry_first',
            'S.TICKENTRIES = [ptickentry_second, ptickentry_third]',
            '$tick_entries_valid(S, [ptickentry_first, ptickentry_second, ptickentry_third], 0)',
            '~$tick_entries_valid(S, [ptickentry_third, ptickentry_second, ptickentry_first], 0)',
            'ptickentry_first.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback1)), NAMED_SENT (KNOWN (POBJECT n_arg1))]',
            'ptickentry_second.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback2)), NAMED_SENT (KNOWN (POBJECT n_arg2))]',
            'ptickentry_third.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback3)), NAMED_SENT (KNOWN (POBJECT n_arg3))]',
            '$object_name(S, n_callback1) = $ptascii("TickCallerOne")',
            '$object_name(S, n_callback2) = $ptascii("TickCallerTwo")',
            '$object_name(S, n_callback3) = $ptascii("TickCallerThree")',
            '$executor_tick_nodes(ptickentry_first) = [HOBJECT n_arg1, HOBJECT n_callback1, HOBJECT n_callback1]',
            '$tick_roots(S.TICKENTRIES) = [HOBJECT n_callback2, HOBJECT n_callback2, HOBJECT n_arg2, HOBJECT n_callback3, HOBJECT n_callback3, HOBJECT n_arg3]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg1) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback1) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_arg2) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback2) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_arg3) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback3) = 2',
            'S.EVENTS = [' + ', '.join(FIRST) + ']',
            *VALID,
        ],
    },
    'first-fcc-object-leaves-one-owner': {
        'source': SOURCE,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback1)] -- if pexecutortick.TAIL = [ptickentry_second, ptickentry_third]',
        'checks': [
            'S.TICKENTRIES = [ptickentry_second, ptickentry_third]',
            'pexecutortick.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback1)), NAMED_SENT (KNOWN (POBJECT n_arg1))]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg1) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_callback1) = 1',
            'n_arg1 <- S.DESTRUCTION.CALLED',
            '~(n_callback1 <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [' + ', '.join(FIRST + ['OUTPUT $ptascii("A1;")']) + ']',
            *VALID,
        ],
    },
    'second-entry-starts-after-first-retirement': {
        'source': SOURCE,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_arg2), DESTRUCTION_VALUE (HOBJECT n_callback2), DESTRUCTION_VALUE (HOBJECT n_callback2)] -- if pexecutortick.TAIL = [ptickentry_third]',
        'checks': [
            'n_callback1 = 0',
            'n_arg1 = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback1) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_arg1) = 0',
            'n_callback1 <- S.DESTRUCTION.CALLED',
            'n_arg1 <- S.DESTRUCTION.CALLED',
            'pexecutortick.ENTRY = ptickentry_second',
            'S.TICKENTRIES = [ptickentry_third]',
            'ptickentry_second.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback2)), NAMED_SENT (KNOWN (POBJECT n_arg2))]',
            'ptickentry_third.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback3)), NAMED_SENT (KNOWN (POBJECT n_arg3))]',
            '$object_name(S, n_callback2) = $ptascii("TickCallerTwo")',
            '$object_name(S, n_callback3) = $ptascii("TickCallerThree")',
            '$executor_tick_nodes(ptickentry_second) = [HOBJECT n_arg2, HOBJECT n_callback2, HOBJECT n_callback2]',
            '$tick_roots(S.TICKENTRIES) = [HOBJECT n_callback3, HOBJECT n_callback3, HOBJECT n_arg3]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg2) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback2) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_arg3) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback3) = 2',
            'S.EVENTS = [' + ', '.join(SECOND) + ']',
            *VALID,
        ],
    },
    'second-fcc-object-leaves-one-owner': {
        'source': SOURCE,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback2)] -- if pexecutortick.TAIL = [ptickentry_third]',
        'checks': [
            'S.TICKENTRIES = [ptickentry_third]',
            'pexecutortick.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback2)), NAMED_SENT (KNOWN (POBJECT n_arg2))]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg2) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_callback2) = 1',
            'n_arg2 <- S.DESTRUCTION.CALLED',
            '~(n_callback2 <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [' + ', '.join(SECOND + ['OUTPUT $ptascii("A2;")']) + ']',
            *VALID,
        ],
    },
    'third-entry-starts-after-second-retirement': {
        'source': SOURCE,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_arg3), DESTRUCTION_VALUE (HOBJECT n_callback3), DESTRUCTION_VALUE (HOBJECT n_callback3)] -- if pexecutortick.TAIL = eps',
        'checks': [
            'n_callback1 = 0',
            'n_arg1 = 1',
            'n_callback2 = 2',
            'n_arg2 = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_callback1) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_arg1) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_callback2) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_arg2) = 0',
            'n_callback1 <- S.DESTRUCTION.CALLED',
            'n_arg1 <- S.DESTRUCTION.CALLED',
            'n_callback2 <- S.DESTRUCTION.CALLED',
            'n_arg2 <- S.DESTRUCTION.CALLED',
            'pexecutortick.ENTRY = ptickentry_third',
            'S.TICKENTRIES = eps',
            'ptickentry_third.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback3)), NAMED_SENT (KNOWN (POBJECT n_arg3))]',
            '$object_name(S, n_callback3) = $ptascii("TickCallerThree")',
            '$executor_tick_nodes(ptickentry_third) = [HOBJECT n_arg3, HOBJECT n_callback3, HOBJECT n_callback3]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg3) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback3) = 2',
            'S.EVENTS = [' + ', '.join(THIRD) + ']',
            *VALID,
        ],
    },
    'third-fcc-object-leaves-one-owner': {
        'source': SOURCE,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback3)] -- if pexecutortick.TAIL = eps',
        'checks': [
            'S.TICKENTRIES = eps',
            'pexecutortick.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback3)), NAMED_SENT (KNOWN (POBJECT n_arg3))]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg3) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_callback3) = 1',
            'n_arg3 <- S.DESTRUCTION.CALLED',
            '~(n_callback3 <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [' + ', '.join(THIRD + ['OUTPUT $ptascii("A3;")']) + ']',
            *VALID,
            'S_done = $drive_steps(S, 4000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = [' + ', '.join(DONE) + ']',
            '$heap_owners($heap_graph(S_done), HOBJECT n_callback3) = 0',
            'n_callback3 <- S_done.DESTRUCTION.CALLED',
            '$call_descriptors_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=240) else 1)
