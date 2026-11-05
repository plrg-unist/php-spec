#!/usr/bin/env python3
"""Reach callback-as-argument owner decrements after output FINAL."""
from pathlib import Path

import fiber_state_review as review


HERE = Path(__file__).parent
SELF = (HERE / 'deprecated_late_tick_self_arg_raw.php').read_text()
MIXED = (HERE / 'deprecated_late_tick_self_other_raw.php').read_text()
PREFIX = ('S.TODO = [DESTRUCTOR_RELEASE pdestructionrelease, '
          'DESTRUCTOR_OPERATION_EXIT pdestructionoperation, '
          'EXECUTOR_TICK_RELEASE pexecutortick false] '
          '-- if pdestructionoperation.SOURCE = EXECUTOR_TICK_RELEASE pexecutortick true ')
VALID = ['$executor_tick_valid(S, pexecutortick)',
         '$eager_operation_source_valid(S, pdestructionoperation)',
         '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']

review.CASES = {
    'self-arg-starts-with-three-owners': {
        'source': SELF,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback), DESTRUCTION_VALUE (HOBJECT n_callback), DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.TAIL = eps',
        'checks': [
            'pexecutortick.ENTRY = ptickentry',
            'S.TICKENTRIES = eps',
            'ptickentry.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback)), NAMED_SENT (KNOWN (POBJECT n_callback))]',
            'ptickentry.ENTRY.ARGS = [POBJECT n_callback]',
            '$executor_tick_nodes(ptickentry) = [HOBJECT n_callback, HOBJECT n_callback, HOBJECT n_callback]',
            '$object_name(S, n_callback) = $ptascii("SelfTickCaller")',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 3',
            '~(n_callback <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID,
        ],
    },
    'self-arg-retires-before-fcc-slots': {
        'source': SELF,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback), DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.TAIL = eps',
        'checks': [
            'pexecutortick.ENTRY = ptickentry',
            'S.TICKENTRIES = eps',
            'ptickentry.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback)), NAMED_SENT (KNOWN (POBJECT n_callback))]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '~(n_callback <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID,
        ],
    },
    'self-final-fcc-slot-retires-callback': {
        'source': SELF,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.TAIL = eps',
        'checks': [
            'pexecutortick.ENTRY = ptickentry',
            'ptickentry.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback)), NAMED_SENT (KNOWN (POBJECT n_callback))]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            '~(n_callback <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID,
            'S_done = $drive_steps(S, 4000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("C;")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_callback) = 0',
            'n_callback <- S_done.DESTRUCTION.CALLED',
        ],
    },
    'mixed-self-and-other-start-with-three-callback-owners': {
        'source': MIXED,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback), DESTRUCTION_VALUE (HOBJECT n_arg), DESTRUCTION_VALUE (HOBJECT n_callback), DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.TAIL = eps',
        'checks': [
            'pexecutortick.ENTRY = ptickentry',
            'ptickentry.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback)), NAMED_SENT (KNOWN (POBJECT n_callback)), NAMED_SENT (KNOWN (POBJECT n_arg))]',
            'ptickentry.ENTRY.ARGS = [POBJECT n_callback, POBJECT n_arg]',
            '$executor_tick_nodes(ptickentry) = [HOBJECT n_callback, HOBJECT n_arg, HOBJECT n_callback, HOBJECT n_callback]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID,
        ],
    },
    'mixed-self-argument-leaves-two-callback-owners': {
        'source': MIXED,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_arg), DESTRUCTION_VALUE (HOBJECT n_callback), DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.TAIL = eps',
        'checks': [
            'pexecutortick.ENTRY = ptickentry',
            'ptickentry.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback)), NAMED_SENT (KNOWN (POBJECT n_callback)), NAMED_SENT (KNOWN (POBJECT n_arg))]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 1',
            '~(n_callback <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;")]',
            *VALID,
        ],
    },
    'mixed-other-argument-retires-before-fcc': {
        'source': MIXED,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback), DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.TAIL = eps',
        'checks': [
            'pexecutortick.ENTRY = ptickentry',
            'ptickentry.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback)), NAMED_SENT (KNOWN (POBJECT n_callback)), NAMED_SENT (KNOWN (POBJECT n_arg))]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 0',
            'n_arg <- S.DESTRUCTION.CALLED',
            '~(n_callback <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;")]',
            *VALID,
        ],
    },
    'mixed-final-fcc-slot-retires-callback': {
        'source': MIXED,
        'stage': PREFIX + '-- if pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_callback)] -- if pexecutortick.TAIL = eps',
        'checks': [
            'pexecutortick.ENTRY = ptickentry',
            'ptickentry.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback)), NAMED_SENT (KNOWN (POBJECT n_callback)), NAMED_SENT (KNOWN (POBJECT n_arg))]',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_arg) = 0',
            'n_arg <- S.DESTRUCTION.CALLED',
            '~(n_callback <- S.DESTRUCTION.CALLED)',
            'S.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;")]',
            *VALID,
            'S_done = $drive_steps(S, 4000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.EVENTS = [OUTPUT $ptascii("B;F;"), OUTPUT $ptascii("A;"), OUTPUT $ptascii("C;")]',
            '$heap_owners($heap_graph(S_done), HOBJECT n_callback) = 0',
            'n_callback <- S_done.DESTRUCTION.CALLED',
        ],
    },
}


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=150) else 1)
