#!/usr/bin/env python3
"""Reached VM argument-warning release and owned producer continuations."""
import argparse
from pathlib import Path

import fiber_state_review as review
from output_reference_warning_sources import CASES

review.ROOT = Path(__file__).resolve().parents[2]
SOURCE = CASES['vm-second-warning-owned-print'][0].decode()
VALID = [*review.VALID, '$output_state_valid(S)']
PAUSE = [
    'S_zero = $drive_steps(S, 0)', 'S_zero.COMPLETION = BUDGET',
    r'S_zero.TODO = S.TODO /\ S_zero.STORE = S.STORE',
    r'S_zero.ALLOCATIONS = S.ALLOCATIONS /\ S_zero.OUTPUTBUFFERS = S.OUTPUTBUFFERS',
    'S_zero.DESTRUCTION = S.DESTRUCTION',
    r'$call_descriptors_valid(S_zero) /\ $heap_valid($heap_graph(S_zero))',
    '$output_state_valid(S_zero)',
]
DONE = [
    'S_done = $drive_steps(S_zero[.COMPLETION = NORMAL], 1000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
    r'S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.OUTPUTBUFFERS = eps',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
    '$output_state_valid(S_done)',
]
review.CASES = {
    'prepared-prefix': {
        'source': SOURCE,
        'stage': 'S.TODO = (OB_USER_REFERENCE_RELEASE pobinvoke 1 n_pending) :: ptask_tail*',
        'checks': [
            'pobinvoke.CALL = OB_WRITE pobwrite', 'ptask_tail* = pobwrite.TAIL',
            'pobwrite.CALLER = OUTPUT_VM porigin (PRINT_EMIT porigin z) z',
            r'pobwrite.FINISH = OUTPUT_VM_DONE /\ pobwrite.INDEX = 0',
            r'S.CURRENT = pobwrite.CONTEXT /\ S.ORIGIN = (porigin)',
            'pobinvoke.SENT = [REFERENCE n_cell]', 'pobinvoke.PHASE = 1',
            '$string_bytes(pobinvoke.INPUT) = ($ptascii("A"))',
            'S.STORE[n_cell] = DEFINED pobinvoke.INPUT',
            '$heap_owners($heap_graph(S), HCELL n_cell) = 1',
            '$ob_reference_prefix(S, pobinvoke, pobinvoke.SENT, 0)',
            '$ob_reference_metadata(S, pobinvoke, 1)',
            r'$throwable_live(S, n_pending) /\ $ob_user_running(S)',
            'S.OUTPUTBUFFERS = [poutputbuffer]',
            r'poutputbuffer.FLAGS = 32881 /\ poutputbuffer.BYTES = $ptascii("AH")',
            'pobwrite.TAIL = (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_native*',
            '$heap_owners($heap_graph(S), HOBJECT pobstringrelease.OBJECT) = 1',
            '~$call_task_valid(S, OB_USER_REFERENCE_RELEASE pobinvoke 0 n_pending)',
            '~$call_task_valid(S, OB_USER_REFERENCE_RELEASE pobinvoke 2 n_pending)',
            '~$call_task_valid(S, OB_USER_REFERENCE_RELEASE pobinvoke 1 999999)',
            '~$call_task_valid(S[.ORIGIN = eps], OB_USER_REFERENCE_RELEASE pobinvoke 1 n_pending)',
            'S_alias = S[.RESULT = REFERENCE n_cell]',
            '$heap_owners($heap_graph(S_alias), HCELL n_cell) = 2',
            '~$call_task_valid(S_alias, OB_USER_REFERENCE_RELEASE pobinvoke 1 n_pending)',
            *VALID, *PAUSE,
            'S_step_found = $drive_steps(S_zero[.COMPLETION = NORMAL], 1)',
            r'S_step_found.COMPLETION = NORMAL \/ S_step_found.COMPLETION = BUDGET',
            'S_step = S_step_found[.COMPLETION = NORMAL]',
            'S_step.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
                '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
                '(OB_USER_FAIL_ARGS pobinvoke_fci n_pending) :: ptask_tail*',
            'pobinvoke_fci = $ob_reference_fci(pobinvoke)',
            '$ob_user_fci_arguments(pobinvoke_fci)',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_cell)]',
            'pdestructionoperation.SOURCE = OB_USER_REFERENCE_RELEASE pobinvoke 1 n_pending',
            r'pdestructionoperation.PENDING = eps /\ pdestructionoperation.COMPLETION = NORMAL',
            '$ob_reference_source_valid(S_step, pdestructionoperation, pobinvoke, 1, n_pending)',
            '$eager_operation_source_guard(S_step, pdestructionoperation)',
            '~$ob_reference_source_valid(S_step, pdestructionoperation, pobinvoke, 0, n_pending)',
            '~$ob_reference_source_valid(S_step, pdestructionoperation, pobinvoke, 1, 999999)',
            r'$call_descriptors_valid(S_step) /\ $heap_valid($heap_graph(S_step))',
            '$output_state_valid(S_step)',
            'S_retired_found = $drive_steps(S_step, 3)',
            r'S_retired_found.COMPLETION = NORMAL \/ S_retired_found.COMPLETION = BUDGET',
            'S_retired = S_retired_found[.COMPLETION = NORMAL]',
            'S_retired.TODO = (OB_USER_FAIL_ARGS pobinvoke_fci n_pending) :: ptask_tail*',
            '~((HCELL n_cell) <- S_retired.ALLOCATIONS)',
            '$heap_owners($heap_graph(S_retired), HCELL n_cell) = 0',
            '$ob_reference_metadata(S_retired, pobinvoke, 1)',
            '~$ob_reference_prefix(S_retired, pobinvoke, pobinvoke.SENT, 0)',
            r'$call_descriptors_valid(S_retired) /\ $heap_valid($heap_graph(S_retired))',
            '$output_state_valid(S_retired)', *DONE,
        ],
    },
    'owned-producer': {
        'source': SOURCE,
        'stage': 'S.TODO = (OUTPUT_FAIL_FINISH pobwrite n_pending) :: ptask_tail* '
                 '-- if pobwrite.TAIL = (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_native*',
        'checks': [
            'ptask_tail* = pobwrite.TAIL',
            'pobwrite.CALLER = OUTPUT_VM porigin (PRINT_EMIT porigin z) z',
            r'pobwrite.INDEX = |pobwrite.IDS| /\ pobwrite.BYTES = $ptascii("AH")',
            'pobstringrelease.CALLER = pobwrite.CALLER',
            'pobstringrelease.CONTEXT = pobwrite.CONTEXT',
            'pobstringrelease.TAIL = ptask_native*',
            '$heap_owners($heap_graph(S), HOBJECT pobstringrelease.OBJECT) = 1',
            r'$throwable_live(S, n_pending) /\ ~$ob_user_running(S)',
            'S.OUTPUTBUFFERS = [poutputbuffer]',
            r'poutputbuffer.FLAGS = 45169 /\ poutputbuffer.SIZE = 0',
            'poutputbuffer.BYTES = eps',
            '$call_task_valid(S, OUTPUT_STRING_RELEASE pobstringrelease)',
            '~$call_task_valid(S, OUTPUT_STRING_RELEASE pobstringrelease[.OBJECT = n_pending])',
            '~$call_task_valid(S, OUTPUT_FAIL_FINISH pobwrite[.TAIL = eps] n_pending)',
            '~$call_task_valid(S, OUTPUT_FAIL_FINISH pobwrite[.IDS = eps] n_pending)',
            *VALID, *PAUSE, *DONE,
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=review.CASES)
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=180) else 1)
