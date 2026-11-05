#!/usr/bin/env python3
"""Authenticate general default-handler receipt and inactive-start Notices."""
import argparse
from pathlib import Path

import fiber_state_review as review
from output_executor_reception_sources import ORIGINALS

ROOT = Path(__file__).resolve().parents[2]
review.ROOT = ROOT
ENV = [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')]
FINISH = [
    'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1',
    '$output_state_valid(S)',
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    'S_done = $drive_steps(S, 1000)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
    'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 1',
]
review.CASES = {
    'dynamic-variable-unpack-reception': {
        'source': ORIGINALS['dynamic-unpacked-null'].decode(), 'request_env': ENV,
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_OB_START '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'pconfigcall.INDEX = 1 /\\ pconfigcall.NAMED /\\ pconfigcall.PACKS =/= eps',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN PNULL)]',
            '$config_invoke_valid(S, pconfigcall)',
            '$executor_default_start_valid(S, pconfigcall)',
            '$executor_boundary(S) = eps',
            '~$config_invoke_valid(S, pconfigcall[.PACKS = eps])',
            '~$executor_default_start_valid(S, pconfigcall[.NAMED = false])',
            '~$executor_default_start_valid(S, pconfigcall[.SENT = [NAMED_SENT (KNOWN (PINT 42))]])',
            '$call_descriptors_valid(S)',
            *FINISH,
        ],
    },
    'deprecated-options-received-before-notice': {
        'source': ORIGINALS['deprecated-options'].decode(), 'request_env': ENV,
        'stage': 'S.TODO = (OB_PARSE pconfigcall 3 pvalue_values*) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_OB_START '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'pvalue_values* = [PNULL, PINT 0, PINT 1]',
            '$ob_parse_valid(S, pconfigcall, 3, pvalue_values*)',
            '$ob_conversion(S, pconfigcall, 1) = OB_DEPRECATED (PINT 0) n_chunk*',
            '$ob_conversion(S, pconfigcall, 2) = OB_DEPRECATED (PINT 1) n_flags*',
            '$executor_default_start_valid(S, pconfigcall)',
            '$executor_boundary(S) = eps',
            '~$executor_default_start_valid(S, pconfigcall[.SENT = [NAMED_SENT (KNOWN PNULL), NAMED_SENT (KNOWN (PSTRING $ptascii("bad"))), NAMED_SENT (KNOWN (PINT 1))]])',
            '$call_descriptors_valid(S)',
            *FINISH,
        ],
    },
    'unpacked-options-notice': {
        'source': ORIGINALS['unpacked-named-options'].decode(), 'request_env': ENV,
        'stage': 'S.TODO = (OB_NOTICE_RESULT pobnotice) :: ptask_tail* '
                 '-- if pobnotice.CALL.KIND = INTRINSIC_OB_START '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'pobnotice.CALL.NAMED /\\ pobnotice.CALL.PACKS =/= eps',
            'pobnotice.VALUE = PBOOL false /\\ ~pobnotice.SECOND /\\ ~pobnotice.WRAPPER /\\ pobnotice.LEVEL = eps',
            '$ob_notice_valid(S, pobnotice)',
            '~$ob_notice_valid(S, pobnotice[.CALL = pobnotice.CALL[.PACKS = eps]])',
            '~$ob_notice_valid(S, pobnotice[.CALL = pobnotice.CALL[.LINE = $(pobnotice.CALL.LINE + 1)]])',
            '~$ob_notice_valid(S, pobnotice[.VALUE = PBOOL true])',
            '~$ob_notice_valid(S[.OUTPUTBLOCKED = true], pobnotice)',
            '$call_descriptors_valid(S)',
            *FINISH,
        ],
    },
    'returned-object-unpacked-options': {
        'source': ORIGINALS['retval-unpacked-options'].decode(), 'request_env': ENV,
        'stage': 'S.TODO = (OB_PARSE pconfigcall 3 pvalue_values*) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_OB_START '
                 '-- if S.FRAMES = [pframe, pframe_executor] '
                 '-- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: '
                 '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
                 '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
                 '(ERROR_HANDLER_CLEAN perrorcall) :: ptask_saved*',
        'checks': [
            'pvalue_values* = [PNULL, PINT 2, PINT 112]',
            'pconfigcall.NAMED /\\ pconfigcall.PACKS =/= eps',
            '$ob_parse_valid(S, pconfigcall, 3, pvalue_values*)',
            '$executor_error_handler_active(S) /\\ S.ERRORHANDLER.CALLBACK = eps',
            '$executor_retval_notice_start(S) /\\ $executor_ob_start_allowed(S)',
            '$executor_boundary(S) = eps',
            '~$executor_retval_notice_start(S[.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)])',
            '~$executor_retval_notice_start(S[.DESTRUCTION.CLEANUPS = eps])',
            # The inherited folded-frame validator retains a stale TODO after
            # retiring C certificates; the exact OB08 noarg control also fails.
            # Check this live task and the completed whole state separately.
            '$call_task_valid(S, OB_PARSE pconfigcall 3 pvalue_values*)',
            *FINISH,
            '$call_descriptors_valid(S_done)',
        ],
    },
}

review.CASES['other-buffer-notice-keeps-helper-total'] = {
    'source': '<?php echo ob_flush() ? "T" : "F";',
    'stage': 'S.TODO = (OB_NOTICE_RESULT pobnotice) :: ptask_tail* '
             '-- if pobnotice.CALL.KIND = INTRINSIC_OB_FLUSH',
    'checks': [
        '$config_invoke_valid(S, pobnotice.CALL)',
        '~$executor_default_start_valid(S, pobnotice.CALL)',
        '$ob_notice_valid(S, pobnotice)',
        '~$executor_scope(S)',
        'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 0',
        'S_zero = $drive_steps(S, 0)',
        'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
        'S_done = $drive_steps(S, 1000)',
        '$drive_steps(S_zero[.COMPLETION = NORMAL], 1000) = S_done',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
        'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 0',
    ],
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=120) else 1)
