#!/usr/bin/env python3
"""A real Warning publication changes live lookup without repairing the attempt."""
from pathlib import Path

import fiber_state_review as review
from output_executor_invalid_sources import ORIGINALS

ROOT = Path(__file__).resolve().parents[2]
review.ROOT = ROOT
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


def publication_controls(state):
    # Late handler publication has an inherited declaration-history validator
    # frontier, also reproduced with a default NULL start. Check output controls
    # and real ownership without claiming that unrelated global certificate.
    return [
        f'$call_registry_valid({state}.FUNCTIONS, {state}.CALLABLES)',
        f'$call_tasks_valid({state}, {state}.TODO)',
        f'$call_frames_valid({state}, {state}.FRAMES)',
        f'$call_current_valid({state})',
        f'$destruction_state_valid({state})',
        f'$output_state_valid({state})',
        f'$heap_valid($heap_graph({state}))',
    ]


review.CASES = {
    'pending-warning-result-throw-keeps-builtin-argument-trace': {
        'source': ORIGINALS['warning-return-destructor-throw'].decode(),
        'request_env': [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')],
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
                 '(ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = ERROR_HANDLER_RESULT perrorcall '
                 '-- if perrorcall.RESUME = OB_START_INVALID_NOTICE pobcreation '
                 '-- if pdestructionoperation.PENDING = (n_pending)',
        'checks': [
            'pdestructionoperation.COMPLETION = NORMAL',
            '$throwable_live(S, n_pending)',
            '$destructor_pending_valid(S, pdestructionoperation.PENDING)',
            '$ob_failure_valid(S, pobcreation)',
            '$ob_failure_tasks(S, pobcreation)',
            '$error_call_valid(S, perrorcall)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            'pobcreation.VALUE = POBJECT n_argument',
            '(HOBJECT n_argument) <- S.ALLOCATIONS',
            '~(n_argument <- S.DESTRUCTION.CALLED)',
            '$heap_count(HOBJECT n_argument, $task_nodes(OB_START_INVALID_NOTICE pobcreation)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_argument) = 2',
            '$throwable_field(S, n_pending, "trace") = PARRAY n_trace',
            '$heap_count(HARRAY n_trace, $node_children(S, HOBJECT n_pending)) = 1',
            'H = $heap_graph(S)',
            '(HOBJECT n_argument) <- $heap_reach([HARRAY n_trace], eps, H.EDGES)',
            'S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            'pdestructionoperation_pending_bad = pdestructionoperation[.PENDING = (|S.OBJECTS|)]',
            'S_pending_bad = S[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending_bad) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_pending_bad :: pdestructionoperation_tail*]',
            '~$ob_failure_tasks(S_pending_bad, pobcreation)',
            'pdestructionoperation_done_bad = pdestructionoperation[.COMPLETION = EXITED 1]',
            'S_done_bad = S[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_done_bad) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_done_bad :: pdestructionoperation_tail*]',
            '~$ob_failure_tasks(S_done_bad, pobcreation)',
            'pdestructionoperation_source_bad = pdestructionoperation[.SOURCE = ERROR_HANDLER_INVOKE perrorcall]',
            'S_source_bad = S[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_source_bad) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_source_bad :: pdestructionoperation_tail*]',
            '~$ob_failure_tasks(S_source_bad, pobcreation)',
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1',
            'S_zero = $drive_steps(S, 0)',
            'S_zero.COMPLETION = BUDGET',
            'S_done = $drive_steps(S, 1000)',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 1000) = S_done',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
            'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 1',
            'n_argument <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_argument) <- S_done.ALLOCATIONS)',
            '$call_descriptors_valid(S_done) /\\ $output_state_valid(S_done)',
        ],
    },
    'warning-return-destructor-keeps-authenticated-caller': {
        'source': ORIGINALS['warning-return-object'].decode(),
        'request_env': [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')],
        'stage': 'S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: '
                 '(DESTRUCTOR_RELEASE pdestructionrelease) :: '
                 '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
                 '(ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = ERROR_HANDLER_RESULT perrorcall '
                 '-- if perrorcall.RESUME = OB_START_INVALID_NOTICE pobcreation',
        'checks': [
            '$ob_failure_valid(S, pobcreation)',
            '$ob_failure_tasks(S, pobcreation)',
            '$error_call_valid(S, perrorcall)',
            'pobcreation.VALUE = POBJECT n_argument',
            '$heap_count(HOBJECT n_argument, $task_nodes(OB_START_INVALID_NOTICE pobcreation)) = 1',
            'pdestructorcall.OPERATION = (pdestructionoperation)',
            'pdestructorcall.RELEASE = (pdestructionrelease_saved)',
            'pdestructionrelease_saved.JOBS = [DESTRUCTION_VALUE (HOBJECT pdestructorcall.OBJECT)]',
            'pdestructionrelease.JOBS = eps',
            'S.DESTRUCTION.CALLS = pdestructorcall :: pdestructorcall_tail*',
            'S.DESTRUCTION.RELEASES = pdestructionrelease :: pdestructionrelease_tail*',
            'pdestructorcall_op_bad = pdestructorcall[.OPERATION = eps]',
            'S_op_bad = S[.TODO = (DESTRUCTOR_ENTER pdestructorcall_op_bad) :: (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*][.DESTRUCTION.CALLS = pdestructorcall_op_bad :: pdestructorcall_tail*]',
            '~$ob_failure_tasks(S_op_bad, pobcreation)',
            'pdestructorcall_release_bad = pdestructorcall[.RELEASE = (pdestructionrelease_saved[.JOBS = eps])]',
            'S_release_bad = S[.TODO = (DESTRUCTOR_ENTER pdestructorcall_release_bad) :: (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*][.DESTRUCTION.CALLS = pdestructorcall_release_bad :: pdestructorcall_tail*]',
            '~$ob_failure_tasks(S_release_bad, pobcreation)',
            '~$ob_failure_tasks(S[.DESTRUCTION.RELEASES = pdestructionrelease_tail*], pobcreation)',
            '~$ob_failure_tasks(S[.DESTRUCTION.CALLED = eps], pobcreation)',
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1',
            'S_done = $drive_steps(S, 1000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
            'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 1',
            '$call_descriptors_valid(S_done) /\\ $output_state_valid(S_done)',
        ],
    },
    'warning-cleanup-authenticates-original-attempt': {
        'source': ORIGINALS['published-after-warning'].decode(),
        'request_env': [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')],
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
                 '(ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = ERROR_HANDLER_RESULT perrorcall '
                 '-- if perrorcall.RESUME = OB_START_INVALID_NOTICE pobcreation',
        'checks': [
            '$ob_failure_valid(S, pobcreation)',
            '$ob_failure_tasks(S, pobcreation)',
            '$ob_failure_task_valid(S, pobcreation)',
            '$error_call_valid(S, perrorcall)',
            'pdestructionoperation.CLEANUP = (pdestructioncleanup)',
            'pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall',
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            'pdestructioncleanup <- S.DESTRUCTION.CLEANUPS',
            'S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            'S.DESTRUCTION.CLEANUPS = pdestructioncleanup :: pdestructioncleanup_tail*',
            '~$ob_failure_tasks(S[.DESTRUCTION.OPERATIONS = pdestructionoperation_tail*], pobcreation)',
            '~$ob_failure_tasks(S[.DESTRUCTION.CLEANUPS = pdestructioncleanup_tail*], pobcreation)',
            'pdestructionoperation_source_bad = pdestructionoperation[.SOURCE = ERROR_HANDLER_INVOKE perrorcall]',
            'S_source_bad = S[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_source_bad) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_source_bad :: pdestructionoperation_tail*]',
            '~$ob_failure_tasks(S_source_bad, pobcreation)',
            'pdestructioncleanup_source_bad = pdestructioncleanup[.SOURCE = ERROR_HANDLER_INVOKE perrorcall]',
            'pdestructionoperation_cleanup_bad = pdestructionoperation[.CLEANUP = (pdestructioncleanup_source_bad)]',
            'S_cleanup_bad = S[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_cleanup_bad) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_cleanup_bad :: pdestructionoperation_tail*][.DESTRUCTION.CLEANUPS = pdestructioncleanup_source_bad :: pdestructioncleanup_tail*]',
            '~$ob_failure_tasks(S_cleanup_bad, pobcreation)',
            'pdestructioncleanup_origin_bad = pdestructioncleanup[.ORIGIN = eps]',
            'pdestructionoperation_origin_bad = pdestructionoperation[.CLEANUP = (pdestructioncleanup_origin_bad)]',
            'S_cleanup_origin_bad = S[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_origin_bad) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_origin_bad :: pdestructionoperation_tail*][.DESTRUCTION.CLEANUPS = pdestructioncleanup_origin_bad :: pdestructioncleanup_tail*]',
            '~$ob_failure_tasks(S_cleanup_origin_bad, pobcreation)',
            'perrorcall_resume_bad = perrorcall[.RESUME = OB_START_INVALID_NOTICE (pobcreation[.FLAGS = 0])]',
            'pdestructioncleanup_resume_bad = pdestructioncleanup[.SOURCE = ERROR_HANDLER_RESULT perrorcall_resume_bad]',
            'pdestructionoperation_resume_bad = pdestructionoperation[.SOURCE = ERROR_HANDLER_RESULT perrorcall_resume_bad][.CLEANUP = (pdestructioncleanup_resume_bad)]',
            'S_resume_bad = S[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_resume_bad) :: (ERROR_HANDLER_CLEAN perrorcall_resume_bad) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_resume_bad :: pdestructionoperation_tail*][.DESTRUCTION.CLEANUPS = pdestructioncleanup_resume_bad :: pdestructioncleanup_tail*]',
            '~$ob_failure_tasks(S_resume_bad, pobcreation)',
            'pdestructionoperation_bad = pdestructionoperation[.PENDING = (|S.OBJECTS|)]',
            'S_pending_bad = S[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_bad) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_bad :: pdestructionoperation_tail*]',
            '~$ob_failure_tasks(S_pending_bad, pobcreation)',
            'pdestructionoperation_done_bad = pdestructionoperation[.COMPLETION = EXITED 1]',
            'S_done_bad = S[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_done_bad) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_done_bad :: pdestructionoperation_tail*]',
            '~$ob_failure_tasks(S_done_bad, pobcreation)',
            '~$ob_failure_tasks(S[.ORIGIN = eps], pobcreation)',
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1',
            'S_done = $drive_steps(S, 1000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
            'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 1',
            *publication_controls('S_done'),
        ],
    },
    'warning-publication-keeps-original-failed-function-lookup': {
        'source': ORIGINALS['published-after-warning'].decode(),
        'request_env': [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')],
        'stage': 'S.TODO = (OB_START_INVALID_NOTICE pobcreation) :: ptask_tail* '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'pobcreation.PREFIX = (n_prefix)',
            '$(n_prefix < |S.DECLARATIONS|)',
            '$string_bytes(pobcreation.VALUE) = ($ptascii("appearedAfterWarningOB11"))',
            'pobcreation.RESOLUTION = HANDLERINVALID ptbytes',
            '$error_handler_resolution(S, pobcreation.VALUE) = HANDLERRESOLVED pcalltarget',
            '$target_function(S, pcalltarget) = (pfunction)',
            '$ptlc(pfunction.NAME) = $ptascii("appearedafterwarningob11")',
            'S_history = $ob_failure_history(S, pobcreation)',
            '$error_handler_resolution(S_history, pobcreation.VALUE) = pobcreation.RESOLUTION',
            'S_history.CALLABLES = $constant_callable_functions(S, S.DECLARATIONS[0:n_prefix])',
            'pobcreation.RAW = eps /\\ pobcreation.PRODUCER = eps /\\ pobcreation.CAPTURE = eps',
            '$ob_failure_valid(S, pobcreation)',
            '~$ob_creation_valid(S, pobcreation)',
            '$ob_creation_ready(S, pobcreation.CALL, [pobcreation.VALUE, PINT pobcreation.CHUNK, PINT pobcreation.FLAGS])',
            '$call_task_valid(S, OB_START_INVALID_NOTICE pobcreation)',
            '$task_nodes(OB_START_INVALID_NOTICE pobcreation) = eps',
            '~$call_task_valid(S[.TODO = (OB_START_CREATED pobcreation) :: ptask_tail*], OB_START_CREATED pobcreation)',
            '~$call_task_valid(S[.TODO = (OB_START_FAILED pobcreation) :: ptask_tail*], OB_START_FAILED pobcreation)',
            '~$ob_failure_valid(S, pobcreation[.PREFIX = (|S.DECLARATIONS|)])',
            '~$ob_failure_valid(S, pobcreation[.PREFIX = ($(|S.DECLARATIONS| + 1))])',
            '~$ob_failure_valid(S, pobcreation[.PREFIX = eps])',
            '~$ob_failure_valid(S, pobcreation[.RESOLUTION = HANDLERINVALID $ptascii("forged")])',
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1',
            *publication_controls('S'),
            *DONE[:-1],
            *publication_controls('S_done'),
        ],
    },
    'warning-retires-borrowed-array-receiver-before-notice': {
        'source': ORIGINALS['warning-retires-array-receiver'].decode(),
        'request_env': [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')],
        'stage': 'S.TODO = (OB_START_INVALID_NOTICE pobcreation) :: ptask_tail* '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'pobcreation.VALUE = PARRAY n_argument',
            'pobcreation.RAW = (parray)',
            '$entry_lookup(parray.ITEMS, KINT 0) = (DIRECT (POBJECT n_callback))',
            '$entry_lookup(S.ARRAYS[n_argument].ITEMS, KINT 0) = (ALIAS n_receiver)',
            'S.STORE[n_receiver] = DEFINED PNULL',
            '~((HOBJECT n_callback) <- S.ALLOCATIONS)',
            'n_callback <- S.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 0',
            '$heap_count(HOBJECT n_callback, $task_nodes(OB_START_INVALID_NOTICE pobcreation)) = 0',
            'pobcreation.PRODUCER = eps /\\ pobcreation.CAPTURE = eps',
            '$error_handler_resolution(S, pobcreation.VALUE) =/= pobcreation.RESOLUTION',
            'S_history = $ob_failure_history(S, pobcreation)',
            '(HOBJECT n_callback) <- S_history.ALLOCATIONS',
            '$error_handler_resolution(S_history, pobcreation.VALUE) = pobcreation.RESOLUTION',
            'S_history[.ALLOCATIONS = S.ALLOCATIONS][.ARRAYS = S.ARRAYS][.CALLABLES = S.CALLABLES][.ORIGIN = S.ORIGIN] = S',
            '$ob_failure_valid(S, pobcreation)',
            '$call_task_valid(S, OB_START_INVALID_NOTICE pobcreation)',
            '~$ob_failure_valid(S, pobcreation[.RAW = (S.ARRAYS[n_argument])])',
            '~$ob_failure_valid(S, pobcreation[.RAW = eps])',
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1',
            '$call_descriptors_valid(S) /\\ $heap_valid($heap_graph(S))',
            *DONE,
            '~((HOBJECT n_callback) <- S_done.ALLOCATIONS)',
        ],
    },
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=180) else 1)
