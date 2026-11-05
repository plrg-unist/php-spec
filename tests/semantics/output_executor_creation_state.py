#!/usr/bin/env python3
"""Creation-only internal metadata and a retired borrowed callback receiver."""
import argparse
from pathlib import Path

import fiber_state_review as review
from output_executor_creation_sources import ORIGINALS

ROOT = Path(__file__).resolve().parents[2]
review.ROOT = ROOT
ENV = [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')]
DONE = [
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    'S_zero.EVENTS = S.EVENTS /\\ S_zero.ALLOCATIONS = S.ALLOCATIONS',
    'S_done = $drive_steps(S, 1000)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
    'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 1',
    '$call_descriptors_valid(S_done) /\\ $output_state_valid(S_done)',
]
review.CASES = {
    'known-internal-needs-no-executable-body': {
        'source': ORIGINALS['internal-noargs'].decode(), 'request_env': ENV,
        'stage': 'S.TODO = (OB_START_CREATED pobcreation) :: ptask_tail* '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            '$string_bytes(pobcreation.VALUE) = ($ptascii("ob_get_level"))',
            'pobcreation.RESOLUTION = HANDLERUNKNOWN text',
            '$ob_creation_target(pobcreation.RESOLUTION) = eps',
            '$typed_callable(S, pobcreation.VALUE) = (true)',
            '$ob_creation_ready(S, pobcreation.CALL, [pobcreation.VALUE, PINT pobcreation.CHUNK, PINT pobcreation.FLAGS])',
            '$ob_creation_valid(S, pobcreation)',
            '$call_task_valid(S, OB_START_CREATED pobcreation)',
            '$task_nodes(OB_START_CREATED pobcreation) = eps',
            '~$ob_creation_valid(S, pobcreation[.RESOLUTION = HANDLERINVALID $ptascii("invalid")])',
            '~$ob_creation_valid(S, pobcreation[.RAW = ($array_empty())])',
            '~$ob_creation_valid(S, pobcreation[.FLAGS = 0])',
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1',
            '$call_descriptors_valid(S) /\\ $heap_valid($heap_graph(S))',
            *DONE,
        ],
    },
    'notice-receipt-does-not-retain-retired-receiver': {
        'source': ORIGINALS['receiver-rebound-during-notice'].decode(), 'request_env': ENV,
        'stage': 'S.TODO = (OB_NOTICE_RESULT pobnotice) :: ptask_tail* '
                 '-- if pobnotice.CREATION = (pobcreation) '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'pobcreation.VALUE = PARRAY n_argument',
            'pobcreation.RAW = (parray)',
            '$entry_lookup(parray.ITEMS, KINT 0) = (DIRECT (POBJECT n_callback))',
            '$ob_creation_target(pobcreation.RESOLUTION) = (pcalltarget)',
            '$error_handler_resolution(S, pobcreation.VALUE) = HANDLERINVALID $ptascii("first array member is not a valid class name or object")',
            '~((HOBJECT n_callback) <- S.ALLOCATIONS)',
            'n_callback <- S.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 0',
            '$heap_count(HOBJECT n_callback, $task_nodes(OB_NOTICE_RESULT pobnotice)) = 0',
            'S_history = $ob_creation_history(S, pobcreation)',
            '(HOBJECT n_callback) <- S_history.ALLOCATIONS',
            '$target_receiver(S_history, pcalltarget) = (n_callback)',
            '$ob_creation_valid(S, pobcreation) /\\ $ob_notice_valid(S, pobnotice)',
            '~$ob_notice_valid(S, pobnotice[.CREATION = eps])',
            '~$ob_creation_valid(S, pobcreation[.RAW = eps])',
            '~$ob_creation_valid(S, pobcreation[.FLAGS = 0])',
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1',
            '$call_descriptors_valid(S) /\\ $heap_valid($heap_graph(S))',
            *DONE,
            '~((HOBJECT n_callback) <- S_done.ALLOCATIONS)',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=150) else 1)
