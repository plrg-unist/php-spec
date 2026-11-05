#!/usr/bin/env python3
"""Authenticate a source-reached positional-null failed start after deactivation."""
from pathlib import Path

import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
review.ROOT = ROOT
SOURCE = (HERE / 'output_executor_post_deactivate_explicit.php').read_text()
review.CASES = {
    'explicit-null-invoke': {
        'source': SOURCE,
        'request_env': [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')],
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_OB_START '
                 '-- if pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL)] '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'pconfigcall.INDEX = 1 /\\ ~pconfigcall.NAMED /\\ pconfigcall.PACKS = eps /\\ pconfigcall.LINE = 5',
            'S.COMPLETION = NORMAL /\\ ~S.OUTPUTBLOCKED',
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1',
            '$config_invoke_valid(S, pconfigcall)',
            '$executor_default_start_sent(pconfigcall)',
            '$executor_ob_start_allowed(S)',
            '$executor_boundary(S) = eps',
            '~$executor_default_start_sent(pconfigcall[.NAMED = true])',
            '~$executor_default_start_sent(pconfigcall[.SENT = [NAMED_SENT (KNOWN (PINT 42))]])',
            'pconfigpack_bad = {INDEX 0, SITE pconfigcall.SITE, LINE pconfigcall.LINE, ARRAY 0, ITEMS eps}',
            'pconfigcall_pack_bad = pconfigcall[.PACKS = [pconfigpack_bad]]',
            '~$executor_default_start_sent(pconfigcall_pack_bad)',
            'S_done = $drive_steps(S, 1000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
            'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 1',
        ],
    },
    'explicit-null-notice': {
        'source': SOURCE,
        'request_env': [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')],
        'stage': 'S.TODO = (OB_NOTICE_RESULT pobnotice) :: ptask_tail* '
                 '-- if pobnotice.CALL.KIND = INTRINSIC_OB_START '
                 '-- if pobnotice.CALL.SENT = [NAMED_SENT (KNOWN PNULL)] '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'pobnotice.CALL.LINE = 5 /\\ ~pobnotice.CALL.NAMED /\\ pobnotice.CALL.PACKS = eps',
            'pobnotice.VALUE = PBOOL false /\\ ~pobnotice.SECOND /\\ ~pobnotice.WRAPPER',
            'pobnotice.LEVEL = eps',
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1',
            '$ob_notice_valid(S, pobnotice)',
            '~$ob_notice_valid(S, pobnotice[.CALL = pobnotice.CALL[.NAMED = true]])',
            '~$ob_notice_valid(S, pobnotice[.VALUE = PBOOL true])',
            'pconfigpack_bad = {INDEX 0, SITE pobnotice.CALL.SITE, LINE pobnotice.CALL.LINE, ARRAY 0, ITEMS eps}',
            '~$ob_notice_valid(S, pobnotice[.CALL = pobnotice.CALL[.PACKS = [pconfigpack_bad]]])',
            'S_zero = $drive_steps(S, 0)',
            'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
            'S_done = $drive_steps(S, 1000)',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 1000) = S_done',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
            'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 1',
        ],
    },
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=120) else 1)
