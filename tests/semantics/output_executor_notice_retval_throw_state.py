#!/usr/bin/env python3
"""Check the reached pending destructor throw before Notice cleanup resumes."""
from pathlib import Path

import fiber_state_review as review
from output_executor_notice_retval_throw_sources import ORIGINALS

review.ROOT = Path(__file__).resolve().parents[2]
review.CASES = {
    'notice-return-destructor-pending-cleanup': {
        'source': ORIGINALS['noarg'].decode(),
        'request_env': [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')],
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
                 '(ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = ERROR_HANDLER_RESULT perrorcall '
                 '-- if pdestructionoperation.PENDING = (n_pending) '
                 '-- if pdestructionoperation.CLEANUP = (pdestructioncleanup) '
                 '-- if pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall '
                 '-- if perrorcall.RESUME = OB_NOTICE_RESULT pobnotice '
                 '-- if pobnotice.CALL.KIND = INTRINSIC_OB_START',
        'checks': [
            'pobnotice.CREATION = eps /\\ pobnotice.CALL.SENT = eps',
            'pobnotice.VALUE = PBOOL false /\\ pobnotice.TAIL = ptask_tail*',
            'perrorcall.LEVEL = 8 /\\ ~pdestructioncleanup.RELEASED',
            'pdestructionoperation.COMPLETION = NORMAL',
            '$throwable_live(S, n_pending)',
            '$destructor_pending_valid(S, pdestructionoperation.PENDING)',
            '$ob_notice_tasks(S, pobnotice)',
            '$ob_notice_valid(S, pobnotice)',
            '$error_call_valid(S, perrorcall)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$call_task_valid(S, DESTRUCTOR_OPERATION_EXIT pdestructionoperation)',
            '$heap_count(HOBJECT n_pending, $task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation)) = 1',
            'S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            'S.DESTRUCTION.CLEANUPS = pdestructioncleanup :: pdestructioncleanup_tail*',
            'pdestructionoperation_pending_bad = pdestructionoperation[.PENDING = (|S.OBJECTS|)]',
            'S_pending_bad = S[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending_bad) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_pending_bad :: pdestructionoperation_tail*]',
            '~$ob_notice_tasks(S_pending_bad, pobnotice)',
            '~$call_task_valid(S_pending_bad, DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending_bad)',
            'pdestructionoperation_done_bad = pdestructionoperation[.COMPLETION = EXITED 1]',
            'S_done_bad = S[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_done_bad) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_done_bad :: pdestructionoperation_tail*]',
            '~$ob_notice_tasks(S_done_bad, pobnotice)',
            'pdestructionoperation_source_bad = pdestructionoperation[.SOURCE = ERROR_HANDLER_INVOKE perrorcall]',
            'S_source_bad = S[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_source_bad) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_source_bad :: pdestructionoperation_tail*]',
            '~$ob_notice_tasks(S_source_bad, pobnotice)',
            'pdestructioncleanup_released_bad = pdestructioncleanup[.RELEASED = true]',
            'pdestructionoperation_cleanup_bad = pdestructionoperation[.CLEANUP = (pdestructioncleanup_released_bad)]',
            'S_cleanup_bad = S[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cleanup_bad) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_cleanup_bad :: pdestructionoperation_tail*][.DESTRUCTION.CLEANUPS = pdestructioncleanup_released_bad :: pdestructioncleanup_tail*]',
            '~$ob_notice_tasks(S_cleanup_bad, pobnotice)',
            '~$ob_notice_tasks(S[.DESTRUCTION.OPERATIONS = pdestructionoperation_tail*], pobnotice)',
            '~$ob_notice_tasks(S[.DESTRUCTION.CLEANUPS = pdestructioncleanup_tail*], pobnotice)',
            'pdestructionoperation_origin_bad = pdestructionoperation[.ORIGIN = eps]',
            'S_origin_bad = S[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_origin_bad) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_origin_bad :: pdestructionoperation_tail*]',
            '~$ob_notice_tasks(S_origin_bad, pobnotice)',
            'S_tail_bad = S[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ERROR_HANDLER_CLEAN perrorcall) :: (THROW_SEARCH n_pending) :: ptask_tail*]',
            '~$ob_notice_tasks(S_tail_bad, pobnotice)',
            'S_step = $drive_steps(S, 1)',
            'S_step.TODO = (THROW_SEARCH n_pending) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*',
            '$throwable_live(S_step, n_pending)',
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
