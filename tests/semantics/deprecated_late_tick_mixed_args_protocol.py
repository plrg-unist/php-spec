#!/usr/bin/env python3
"""Reach empty and copied-object argument retirement after output FINAL."""
from pathlib import Path

import fiber_state_review as review


HERE = Path(__file__).parent
MIXED = (HERE / 'deprecated_late_tick_mixed_args_raw.php').read_text()
SHARED = (HERE / 'deprecated_late_tick_mixed_args_alias.php').read_text()
PREFIX = ('S.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, '
          'DESTRUCTOR_OPERATION_EXIT pdestructionoperation, '
          'EXECUTOR_TICK_RELEASE pexecutortick false] '
          '-- if pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true ')
VALID = ['$executor_tick_valid(S, pexecutortick)',
         '$eager_operation_source_valid(S, pdestructionoperation)',
         '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']

review.CASES = {
    'zero-arg-head-retains-one-arg-tail': {
        'source': MIXED,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback1), DESTRUCTION_VALUE (HOBJECT n_callback1)] -- if pexecutortick.TAIL = [ptickentry_second]',
        'checks': [
            'pexecutortick.ENTRY = ptickentry_first',
            'S.TICKENTRIES = [ptickentry_second]',
            '$tick_entries_valid(S, [ptickentry_first, ptickentry_second], 0)',
            'ptickentry_first.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback1))]',
            'ptickentry_first.ENTRY.ARGS = eps',
            'ptickentry_second.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback2)), NAMED_SENT (KNOWN (POBJECT n_arg2))]',
            '$object_name(S, n_callback1) = $ptascii("TickCallerOne")',
            '$object_name(S, n_callback2) = $ptascii("TickCallerTwo")',
            '$executor_tick_nodes(ptickentry_first) = [HOBJECT n_callback1, HOBJECT n_callback1]',
            '$tick_roots(S.TICKENTRIES) = [HOBJECT n_callback2, HOBJECT n_callback2, HOBJECT n_arg2]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback1) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_callback2) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_arg2) = 1',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID,
        ],
    },
    'one-arg-tail-starts-after-zero-head': {
        'source': MIXED,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_arg2), DESTRUCTION_VALUE (HOBJECT n_callback2), DESTRUCTION_VALUE (HOBJECT n_callback2)] -- if pexecutortick.TAIL = eps',
        'checks': [
            'n_callback1 = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_callback1) = 0',
            'n_callback1 <- S.DESTRUCTION.CALLED',
            'pexecutortick.ENTRY = ptickentry_second',
            'S.TICKENTRIES = eps',
            'ptickentry_second.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback2)), NAMED_SENT (KNOWN (POBJECT n_arg2))]',
            '$object_name(S, n_callback2) = $ptascii("TickCallerTwo")',
            '$executor_tick_nodes(ptickentry_second) = [HOBJECT n_arg2, HOBJECT n_callback2, HOBJECT n_callback2]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg2) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback2) = 2',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("C1;")]',
            *VALID,
        ],
    },
    'shared-zero-head-keeps-four-fcc-owners': {
        'source': SHARED,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback), DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.TAIL = [ptickentry_second]',
        'checks': [
            'pexecutortick.ENTRY = ptickentry_first',
            'S.TICKENTRIES = [ptickentry_second]',
            'ptickentry_first.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback))]',
            'ptickentry_first.ENTRY.ARGS = eps',
            'ptickentry_second.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback)), NAMED_SENT (KNOWN (POBJECT n_arg1)), NAMED_SENT (KNOWN (POBJECT n_arg2))]',
            '$executor_tick_nodes(ptickentry_first) = [HOBJECT n_callback, HOBJECT n_callback]',
            '$tick_roots(S.TICKENTRIES) = [HOBJECT n_callback, HOBJECT n_callback, HOBJECT n_arg1, HOBJECT n_arg2]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 4',
            '$heap_owners($heap_graph(S), HOBJECT n_arg1) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_arg2) = 1',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID,
        ],
    },
    'shared-first-fcc-object-leaves-three-owners': {
        'source': SHARED,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.TAIL = [ptickentry_second]',
        'checks': [
            'pexecutortick.ENTRY = ptickentry_first',
            'S.TICKENTRIES = [ptickentry_second]',
            'ptickentry_first.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback))]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 3',
            '~(n_callback <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID,
        ],
    },
    'shared-two-arg-tail-keeps-two-fcc-owners': {
        'source': SHARED,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_arg1), DESTRUCTION_VALUE (HOBJECT n_arg2), DESTRUCTION_VALUE (HOBJECT n_callback), DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.TAIL = eps',
        'checks': [
            'pexecutortick.ENTRY = ptickentry_second',
            'S.TICKENTRIES = eps',
            'ptickentry_second.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback)), NAMED_SENT (KNOWN (POBJECT n_arg1)), NAMED_SENT (KNOWN (POBJECT n_arg2))]',
            '$executor_tick_nodes(ptickentry_second) = [HOBJECT n_arg1, HOBJECT n_arg2, HOBJECT n_callback, HOBJECT n_callback]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_arg1) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_arg2) = 1',
            '~(n_callback <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID,
        ],
    },
    'shared-last-fcc-owner-retires-after-both-args': {
        'source': SHARED,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.TAIL = eps',
        'checks': [
            'pexecutortick.ENTRY = ptickentry_second',
            'S.TICKENTRIES = eps',
            'ptickentry_second.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback)), NAMED_SENT (KNOWN (POBJECT n_arg1)), NAMED_SENT (KNOWN (POBJECT n_arg2))]',
            '$heap_owners($heap_graph(S), HOBJECT n_arg1) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_arg2) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            'n_arg1 <- S.DESTRUCTION.CALLED',
            'n_arg2 <- S.DESTRUCTION.CALLED',
            '~(n_callback <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A1;"), OUTPUT $ptascii("A2;")]',
            *VALID,
            'S_done = $drive_steps(S, 4000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A1;"), OUTPUT $ptascii("A2;"), OUTPUT $ptascii("C;")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_callback) = 0',
            'n_callback <- S_done.DESTRUCTION.CALLED',
            '$call_descriptors_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=210) else 1)
