#!/usr/bin/env python3
"""Check the source-reached failed start before its Notice is delivered."""
import argparse
from pathlib import Path

import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
review.ROOT = ROOT
review.CASES = {
    'failed-start-notice': {
        'source': (HERE / 'output_executor_post_deactivate_plain.php').read_text(),
        'request_env': [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')],
        'stage': 'S.TODO = (OB_NOTICE_RESULT pobnotice) :: ptask_tail* '
                 '-- if pobnotice.CALL.KIND = INTRINSIC_OB_START '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1 /\\ ~S.OUTPUTBLOCKED',
            'pobnotice.CALL.SENT = eps /\\ pobnotice.VALUE = PBOOL false',
            '~pobnotice.SECOND /\\ ~pobnotice.WRAPPER /\\ pobnotice.LEVEL = eps',
            'S.ORIGIN = (pobnotice.CALL.SITE)',
            '$executor_scope(S) /\\ $executor_normal_scope(S)',
            '$config_invoke_valid(S, pobnotice.CALL)',
            '$ob_notice_valid(S, pobnotice)',
            '$call_descriptors_valid(S) /\\ $output_state_valid(S)',
            '$heap_valid($heap_graph(S))',
            '~$ob_notice_valid(S, pobnotice[.CALL = pobnotice.CALL[.SENT = [NAMED_SENT (KNOWN PNULL)]]])',
            '~$ob_notice_valid(S, pobnotice[.VALUE = PBOOL true])',
            '~$ob_notice_valid(S[.OUTPUTBLOCKED = true], pobnotice)',
            'S_zero = $drive_steps(S, 0)',
            'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
            'S_zero.OUTPUTBUFFERS = S.OUTPUTBUFFERS /\\ S_zero.OUTPUTSEQ = S.OUTPUTSEQ',
            'S_zero.EVENTS = S.EVENTS',
            'S_done = $drive_steps(S, 1000)',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 1000) = S_done',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
            'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 1',
            '$call_descriptors_valid(S_done) /\\ $output_state_valid(S_done)',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=120) else 1)
