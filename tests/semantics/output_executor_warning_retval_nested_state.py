#!/usr/bin/env python3
"""Check the genuine normal Warning-retval nested-start admission."""
from pathlib import Path

import fiber_state_review as review
from output_executor_warning_retval_nested_sources import ORIGINALS

review.ROOT = Path(__file__).resolve().parents[2]
review.CASES = {
    'warning-retval-nested-start': {
        'source': ORIGINALS['warning-return-nested-start'].decode(),
        'request_env': [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')],
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                 '-- if pconfigcall.KIND = INTRINSIC_OB_START '
                 '-- if S.FRAMES = [pframe, pframe_executor] '
                 '-- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: '
                 '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
                 '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
                 '(ERROR_HANDLER_CLEAN perrorcall) :: ptask_saved* '
                 '-- if perrorcall.RESUME = OB_START_INVALID_NOTICE pobcreation',
        'checks': [
            'pconfigcall.SENT = eps /\\ S.ERRORHANDLER.CALLBACK = eps',
            'S.OUTPUTBUFFERS = eps /\\ ~S.OUTPUTBLOCKED',
            'pframe_executor.TODO = (DESTRUCTOR_RESULT pdestructorcall_outer) :: '
                '(DESTRUCTOR_RELEASE pdestructionrelease_outer) :: '
                '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_outer) :: '
                '(EXECUTOR_RELEASE pexecutorqueue pexecutorstage) :: eps',
            'pexecutorqueue.COMPLETION = NORMAL',
            'pdestructorcall.OPERATION = (pdestructionoperation)',
            'pdestructorcall.PENDING = eps /\\ pdestructionoperation.PENDING = eps',
            'pdestructionoperation.COMPLETION = NORMAL',
            'pdestructionoperation.SOURCE = ERROR_HANDLER_RESULT perrorcall',
            'pdestructionoperation.CLEANUP = (pdestructioncleanup)',
            'pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall',
            '~pdestructioncleanup.RELEASED',
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            'pdestructioncleanup <- S.DESTRUCTION.CLEANUPS',
            'perrorcall.LEVEL = 2 /\\ perrorcall.TARGET =/= eps',
            'pobcreation.CALL.KIND = INTRINSIC_OB_START',
            'pobcreation.CALL.SITE = perrorcall.SITE',
            'S_view = S[.TODO = pframe.TODO][.CURRENT = pframe.CONTEXT]'
                '[.ORIGIN = pframe.ORIGIN][.CONSTCONTEXT = pframe.CONSTCONTEXT]'
                '[.FRAMES = [pframe_executor]]',
            '$error_call_valid(S_view, perrorcall)',
            '$executor_retval_start_resume_valid(S_view, perrorcall, ptask_saved*)',
            '$executor_retval_notice_start(S) /\\ $executor_ob_start_allowed(S)',
            '~$executor_retval_start_resume_valid(S_view, perrorcall[.LEVEL = 8], ptask_saved*)',
            '~$executor_retval_start_resume_valid(S_view, perrorcall[.TARGET = eps], ptask_saved*)',
            '~$executor_retval_start_resume_valid(S_view[.ORIGIN = eps], perrorcall, ptask_saved*)',
            '~$executor_retval_start_resume_valid(S_view[.DESTRUCTION.CLEANUPS = eps], perrorcall, ptask_saved*)',
            '~$executor_retval_start_resume_valid(S_view[.OUTPUTBLOCKED = true], perrorcall, ptask_saved*)',
            '~$executor_retval_start_resume_valid(S_view, perrorcall, (ERROR_HANDLER_RESULT perrorcall) :: ptask_saved*)',
            'S_zero = $drive_steps(S, 0)',
            'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
            'S_done = $drive_steps(S, 1000)',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 1000) = S_done',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
            'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 1',
            '$call_descriptors_valid(S_done) /\\ $output_state_valid(S_done)',
        ],
    },
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
