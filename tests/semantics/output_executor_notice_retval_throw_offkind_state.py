#!/usr/bin/env python3
"""Check the reached ob_end_clean Notice return throw and its trace frame."""
from pathlib import Path

import fiber_state_review as review
from output_executor_notice_retval_throw_offkind import ORIGINALS

review.ROOT = Path(__file__).resolve().parents[2]
review.CASES = {
    'ob-end-clean-notice-return-trace': {
        'source': ORIGINALS['ob-end-clean-return-throw-trace'].decode(),
        'request_env': [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')],
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
                 '(ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = ERROR_HANDLER_RESULT perrorcall '
                 '-- if pdestructionoperation.PENDING = (n_pending) '
                 '-- if pdestructionoperation.CLEANUP = (pdestructioncleanup) '
                 '-- if pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall '
                 '-- if perrorcall.RESUME = OB_NOTICE_RESULT pobnotice '
                 '-- if pobnotice.CALL.KIND = INTRINSIC_OB_END_CLEAN',
        'checks': [
            'perrorcall.LEVEL = 8 /\\ ~pdestructioncleanup.RELEASED',
            'pobnotice.CREATION = eps /\\ pobnotice.CALL.SENT = eps',
            'pobnotice.VALUE = PBOOL false /\\ pobnotice.TAIL = ptask_tail*',
            'pdestructionoperation.COMPLETION = NORMAL',
            '$throwable_live(S, n_pending)',
            '$ob_notice_tasks(S, pobnotice)',
            '$ob_notice_valid(S, pobnotice)',
            '$error_call_valid(S, perrorcall)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$call_task_valid(S, DESTRUCTOR_OPERATION_EXIT pdestructionoperation)',
            'S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            'S.DESTRUCTION.CLEANUPS = pdestructioncleanup :: pdestructioncleanup_tail*',
            '$throwable_field(S, n_pending, "trace") = PARRAY n_trace',
            '$trace_graph_valid(S, n_trace)',
            'S.ARRAYS[n_trace].ITEMS = (ENTRY (KINT 0) (DIRECT (PARRAY n_frame0))) :: (ENTRY (KINT 1) (DIRECT (PARRAY n_frame1))) :: pentry_tail*',
            '$trace_array_field(S, n_frame0, $ptascii("function")) = PSTRING $ptascii("__destruct")',
            '$trace_array_field(S, n_frame1, $ptascii("function")) = PSTRING $ptascii("ob_end_clean")',
            'S_step = $drive_steps(S, 1)',
            'S_step.TODO = (THROW_SEARCH n_pending) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*',
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
    raise SystemExit(0 if review.run(None, process_seconds=240) else 1)
