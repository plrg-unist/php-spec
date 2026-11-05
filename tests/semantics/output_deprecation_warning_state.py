#!/usr/bin/env python3
"""Reached defined-return, pending Throwable and deprecation cleanup owners."""
import argparse
from pathlib import Path

import fiber_state_review as review
from output_deprecation_warning_sources import CASES

review.ROOT = Path(__file__).resolve().parents[2]
VALID = [*review.VALID, '$output_state_valid(S)']
PAUSE = [
    'S_zero = $drive_steps(S, 0)', 'S_zero.COMPLETION = BUDGET',
    r'S_zero.TODO = S.TODO /\ S_zero.STORE = S.STORE',
    r'S_zero.OUTPUTBUFFERS = S.OUTPUTBUFFERS /\ S_zero.ALLOCATIONS = S.ALLOCATIONS',
    'S_zero.DESTRUCTION = S.DESTRUCTION',
    r'$call_descriptors_valid(S_zero) /\ $heap_valid($heap_graph(S_zero))',
    '$output_state_valid(S_zero)',
]
DONE = [
    'S_done = $drive_steps(S_zero[.COMPLETION = NORMAL], 1500)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
    r'S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.OUTPUTBUFFERS = eps',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
    '$output_state_valid(S_done)',
]
PENDING = [
    'S.TODO = (OB_USER_DEPRECATED_PENDING pobinvoke pvalue n_pending) :: ptask_tail*',
    r'S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)',
    '$ob_user_fci_arguments(pobinvoke)',
    '$string_bytes(pobinvoke.INPUT) = ($ptascii("A"))',
    'S.OUTPUTBUFFERS = [poutputbuffer]',
    r'poutputbuffer.FLAGS = 8305 /\ poutputbuffer.BYTES = $ptascii("AH")',
    '$ob_user_running(S)', '$ob_user_temporary(S, poutputbuffer.ID)',
    '$heap_count(HOBJECT n_pending, $task_nodes(OB_USER_DEPRECATED_PENDING pobinvoke pvalue n_pending)) = 1',
    '$heap_owners($heap_graph(S), HOBJECT n_pending) = 2',
    '$throwable_live(S, n_pending)',
    '~$call_task_valid(S, OB_USER_DEPRECATED_PENDING pobinvoke pvalue 999999)',
    '~$call_task_valid(S, OB_USER_DEPRECATED_PENDING pobinvoke (POBJECT n_pending) n_pending)',
    '~$call_task_valid(S[.ORIGIN = eps], OB_USER_DEPRECATED_PENDING pobinvoke pvalue n_pending)',
    'S_enabled = S[.OUTPUTBUFFERS = [poutputbuffer[.FLAGS = 113]]]',
    '~$call_task_valid(S_enabled, OB_USER_DEPRECATED_PENDING pobinvoke pvalue n_pending)',
    'S_produced = S[.OUTPUTBUFFERS = [poutputbuffer[.FLAGS = 41073]]]',
    '~$call_task_valid(S_produced, OB_USER_DEPRECATED_PENDING pobinvoke pvalue n_pending)',
    *VALID, *PAUSE,
]
review.CASES = {
    'api-frozen-getter': {
        'source': CASES['api-get-flush'][0].decode(),
        'stage': 'S.TODO = (OB_USER_DEPRECATED_PENDING pobinvoke pvalue n_pending) :: ptask_tail*',
        'checks': [
            *PENDING,
            'pobinvoke.CALL = OB_API_FAILED pconfigcall pcallcontext? ptask_tail*',
            'pconfigcall.KIND = INTRINSIC_OB_GET_FLUSH',
            'S.CURRENT = pcallcontext?', 'pobinvoke.PHASE = 9',
            '$string_bytes(pvalue) = ($ptascii("XA"))',
            '$string_bytes(pobinvoke.VALUE) = ($ptascii("A"))',
            'pobinvoke.VALUE =/= pobinvoke.INPUT',
            'pobinvoke_bad = pobinvoke[.CALL = OB_API_FAILED pconfigcall pcallcontext? eps]',
            'S_bad = S[.TODO = (OB_USER_DEPRECATED_PENDING pobinvoke_bad pvalue n_pending) :: ptask_tail*]',
            '~$call_task_valid(S_bad, OB_USER_DEPRECATED_PENDING pobinvoke_bad pvalue n_pending)',
            '~$call_task_valid(S, OB_USER_DEPRECATED_PENDING pobinvoke[.CALL = OB_API pconfigcall] pvalue n_pending)',
            'S_step_found = $drive_steps(S_zero[.COMPLETION = NORMAL], 1)',
            r'S_step_found.COMPLETION = NORMAL \/ S_step_found.COMPLETION = BUDGET',
            'S_step = S_step_found[.COMPLETION = NORMAL]',
            'S_step.OUTPUTBUFFERS = eps',
            'S_step.TODO = (OUTPUT_FAIL_WRITE pobwrite n_pending) :: ptask_tail*',
            'pobwrite.BYTES = $ptascii("XA")',
            'pobwrite.FINISH = OUTPUT_USER_DONE pobinvoke_done poutputbuffer_done poboutput false',
            'pobinvoke_done = $ob_api_original(pobinvoke)[.SENT = eps]',
            r'poutputbuffer_done.FLAGS = 113 /\ poutputbuffer_done.BYTES = $ptascii("AH")',
            r'poboutput.VALUE = pvalue /\ ~poboutput.FAILED',
            r'$call_descriptors_valid(S_step) /\ $heap_valid($heap_graph(S_step))',
            '$output_state_valid(S_step)', *DONE,
        ],
    },
    'vm-false-live-buffer': {
        'source': CASES['vm-false'][0].decode(),
        'stage': 'S.TODO = (OB_USER_DEPRECATED_PENDING pobinvoke pvalue n_pending) :: ptask_tail*',
        'checks': [
            *PENDING, 'pvalue = PBOOL false',
            'pobinvoke.CALL = OB_WRITE pobwrite', 'ptask_tail* = pobwrite.TAIL',
            'pobwrite.CALLER = OUTPUT_VM porigin (PRINT_EMIT porigin z) z',
            'pobwrite.FINISH = OUTPUT_VM_DONE', 'pobinvoke.PHASE = 1',
            '~$call_task_valid(S, OB_USER_DEPRECATED_PENDING pobinvoke[.CALL = OB_WRITE pobwrite[.TAIL = eps]] pvalue n_pending)',
            'S_step_found = $drive_steps(S_zero[.COMPLETION = NORMAL], 1)',
            r'S_step_found.COMPLETION = NORMAL \/ S_step_found.COMPLETION = BUDGET',
            'S_step = S_step_found[.COMPLETION = NORMAL]',
            'S_step.TODO = (OUTPUT_FAIL_WRITE pobwrite_next n_pending) :: ptask_tail*',
            r'pobwrite_next.INDEX = 1 /\ pobwrite_next.BYTES = $ptascii("AH")',
            'S_step.OUTPUTBUFFERS = [poutputbuffer_next]',
            r'poutputbuffer_next.FLAGS = 12401 /\ poutputbuffer_next.SIZE = 0 /\ poutputbuffer_next.BYTES = eps',
            '~$ob_user_running(S_step)',
            r'$call_descriptors_valid(S_step) /\ $heap_valid($heap_graph(S_step))',
            '$output_state_valid(S_step)', *DONE,
        ],
    },
    'warning-return-destructor': {
        'source': CASES['vm-warning-return-destructor'][0].decode(),
        'stage': 'S.CURRENT = (pcallcontext) '
                 '-- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall) '
                 '-- if pdestructorcall.OPERATION = (pdestructionoperation) '
                 '-- if pdestructionoperation.SOURCE = ERROR_HANDLER_RESULT perrorcall '
                 '-- if perrorcall.RESUME = OB_USER_DEPRECATED pobinvoke pvalue',
        'checks': [
            'S.ERRORHANDLER.CALLBACK = eps',
            '$string_bytes(pvalue) = ($ptascii("XA"))',
            'S.OUTPUTBUFFERS = [poutputbuffer]',
            r'poutputbuffer.FLAGS = 8305 /\ poutputbuffer.BYTES = $ptascii("AH")',
            'pobinvoke.CALL = OB_WRITE pobwrite',
            'pobwrite.CALLER = OUTPUT_VM porigin ptask z',
            r'pdestructorcall.SITE = (porigin) /\ pdestructorcall.LINE = z /\ z = 1',
            r'pdestructionoperation.PENDING = eps /\ pdestructorcall.PENDING = eps',
            'pdestructionoperation.CLEANUP = (pdestructioncleanup)',
            r'pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall /\ ~pdestructioncleanup.RELEASED',
            'pdestructioncleanup <- S.DESTRUCTION.CLEANUPS',
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            '$ob_user_running(S)', '$ob_user_temporary(S, poutputbuffer.ID)',
            'n_return = pdestructorcall.OBJECT',
            '(HOBJECT n_return) <- S.ALLOCATIONS',
            '$(0 < $heap_owners($heap_graph(S), HOBJECT n_return))',
            *VALID, *PAUSE, *DONE,
            '~((HOBJECT n_return) <- S_done.ALLOCATIONS)',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=review.CASES)
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=180) else 1)
