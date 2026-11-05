#!/usr/bin/env python3
"""Frozen invalid selection and root-only argument cleanup from real sources."""
from pathlib import Path

import fiber_state_review as review
from output_executor_invalid_review_sources import ORIGINALS

ROOT = Path(__file__).resolve().parents[2]
review.ROOT = ROOT
ENV = [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')]
DONE = [
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    'S_zero.ALLOCATIONS = S.ALLOCATIONS /\\ S_zero.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S, 1000)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
    'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 1',
    'n_callback <- S_done.DESTRUCTION.CALLED',
    '~((HOBJECT n_callback) <- S_done.ALLOCATIONS)',
    '$call_descriptors_valid(S_done) /\\ $output_state_valid(S_done)',
]


def operation_negative(name, expression):
    return [
        f'pdestructionoperation_{name} = {expression}',
        f'S_{name} = S[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_{name}) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_{name} :: pdestructionoperation_tail*]',
        f'$gc_temporary_release($gc_temporary_pairs(S_{name}), pdestructionoperation_{name}) = (pdestructionrelease)',
        f'~$gc_temporary_metadata_valid(S_{name}, pdestructionoperation_{name})',
    ]


def released_negative(name, cleanup, operation):
    return [
        f'pdestructioncleanup_{name} = {cleanup}',
        f'pdestructionoperation_{name} = {operation}',
        f'S_{name} = S[.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_{name}) :: (OB_START_INVALID_NOTICE pobcreation) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_{name} :: pdestructionoperation_tail*][.DESTRUCTION.CLEANUPS = pdestructioncleanup_{name} :: pdestructioncleanup_tail*]',
        f'~$ob_failure_tasks(S_{name}, pobcreation)',
    ]


def discard_negative(name, expression):
    return [
        f'pdestructionoperation_{name} = {expression}',
        f'S_{name} = S_release[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_{name}) :: ptask_after*][.DESTRUCTION.OPERATIONS = pdestructionoperation_{name} :: pdestructionoperation_tail*]',
        f'$gc_temporary_release($gc_temporary_pairs(S_{name}), pdestructionoperation_{name}) = (pdestructionrelease)',
        f'~$gc_temporary_metadata_valid(S_{name}, pdestructionoperation_{name})',
    ]


review.CASES = {
    'abrupt-failed-warning-consumes-only-argument-root-nogc': {
        'source': ORIGINALS['invalid-direct-cycle-warning-throw'].decode(),
        'request_env': ENV,
        'stage': 'S.TODO = (THROW_SEARCH n_pending) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail* '
                 '-- if perrorcall.RESUME = OB_START_INVALID_NOTICE pobcreation',
        'checks': [
            '$throwable_live(S, n_pending)',
            'pobcreation.VALUE = POBJECT n_callback',
            '$ob_failure_valid(S, pobcreation)',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 3',
            '~((HOBJECT n_callback) <- $gc_nodes(S.GC.BUFFER))',
            'S_projected = S[.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*]',
            '$call_task_valid(S_projected, ERROR_HANDLER_RESULT perrorcall)',
            '$ob_failure_discarded(S, n_pending) = (pobcreation)',
            'perrorcall_level_bad = perrorcall[.LEVEL = 8][.EVENT = DIAGNOSTIC "Notice" perrorcall.MESSAGE perrorcall.LINE]',
            'S_level_bad = S[.TODO = (THROW_SEARCH n_pending) :: (ERROR_HANDLER_RESULT perrorcall_level_bad) :: ptask_tail*]',
            '$ob_failure_discarded(S_level_bad, n_pending) = eps',
            'ptbytes_forged = $ptascii("forged")',
            'perrorcall_message_bad = perrorcall[.MESSAGE = ptbytes_forged][.EVENT = DIAGNOSTIC "Warning" ptbytes_forged perrorcall.LINE]',
            'S_message_bad = S[.TODO = (THROW_SEARCH n_pending) :: (ERROR_HANDLER_RESULT perrorcall_message_bad) :: ptask_tail*]',
            '$ob_failure_discarded(S_message_bad, n_pending) = eps',
            'PhpStep: S ~> S_raw',
            'S_release = $literal_reference_debt_step(S, S_raw)',
            'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_after*',
            'S_release.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            'pdestructionoperation.SOURCE = OB_START_INVALID_DISCARD pobcreation n_pending',
            'pdestructionoperation.CLEANUP = eps',
            'pdestructionoperation.PENDING = (n_pending) /\\ pdestructionoperation.COMPLETION = NORMAL',
            'pdestructionoperation.VALUE = KNOWN PNULL',
            'pdestructionoperation.NOGC = eps',
            'pdestructionoperation.NOGCEXTRA = [pgctemporary]',
            'pgctemporary.OPERAND = KNOWN (POBJECT n_callback)',
            'pgctemporary.PENDING',
            '(DESTRUCTION_TEMP (HOBJECT n_callback)) <- pdestructionrelease.JOBS',
            '~((DESTRUCTION_VALUE (HOBJECT n_callback)) <- pdestructionrelease.JOBS)',
            '$task_nodes(OB_START_INVALID_DISCARD pobcreation n_pending) = eps',
            '~$call_task_valid(S_release, OB_START_INVALID_DISCARD pobcreation n_pending)',
            '$ob_failure_discard_valid(S_release, pdestructionoperation)',
            '$eager_operation_source_valid(S_release, pdestructionoperation)',
            '$call_task_valid(S_release, DESTRUCTOR_OPERATION_EXIT pdestructionoperation)',
            '$gc_temporary_metadata_valid(S_release, pdestructionoperation)',
            '$gc_release_metadata_valid(S_release, pdestructionrelease)',
            *discard_negative('prefix_bad', 'pdestructionoperation[.SOURCE = OB_START_INVALID_DISCARD (pobcreation[.PREFIX = eps]) n_pending]'),
            *discard_negative('source_bad', 'pdestructionoperation[.SOURCE = THROW_SEARCH n_pending]'),
            *discard_negative('source_pending_bad', 'pdestructionoperation[.SOURCE = OB_START_INVALID_DISCARD pobcreation (|S_release.OBJECTS|)]'),
            *discard_negative('pending_bad', 'pdestructionoperation[.PENDING = eps]'),
            *discard_negative('value_bad', 'pdestructionoperation[.VALUE = KNOWN (PBOOL false)]'),
            *discard_negative('operand_bad', 'pdestructionoperation[.NOGCEXTRA = [pgctemporary[.OPERAND = KNOWN PNULL]]]'),
            *discard_negative('progress_bad', 'pdestructionoperation[.NOGCEXTRA = [pgctemporary[.PENDING = false]]]'),
            'S_after = $drive_steps(S_release, 4)',
            '~((HOBJECT n_callback) <- $gc_nodes(S_after.GC.BUFFER))',
            '$heap_owners($heap_graph(S_after), HOBJECT n_callback) = 2',
            '$heap_count(HOBJECT n_callback, $node_children(S_after, HOBJECT n_callback)) = 1',
            '$throwable_field(S_after, n_pending, "trace") = PARRAY n_trace',
            '$heap_count(HARRAY n_trace, $node_children(S_after, HOBJECT n_pending)) = 1',
            'H_after = $heap_graph(S_after)',
            '(HOBJECT n_callback) <- $heap_reach([HARRAY n_trace], eps, H_after.EDGES)',
            'S_zero = $drive_steps(S_release, 0)',
            'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S_release.TODO',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 4) = S_after',
            'S_done = $drive_steps(S_after[.COMPLETION = NORMAL], 1000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
            'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 1',
            'n_callback <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_callback) <- S_done.ALLOCATIONS)',
            '$call_descriptors_valid(S_done) /\\ $output_state_valid(S_done)',
        ],
    },
    'released-warning-handler-retires-before-notice': {
        'source': ORIGINALS['warning-handler-created-late'].decode(),
        'request_env': ENV,
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: '
                 '(OB_START_INVALID_NOTICE pobcreation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = ERROR_HANDLER_CLEAN perrorcall '
                 '-- if pdestructionoperation.CLEANUP = (pdestructioncleanup) '
                 '-- if pdestructioncleanup.RELEASED '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'perrorcall.RESUME = OB_START_INVALID_NOTICE pobcreation',
            'pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall',
            'perrorcall.CALLBACK = POBJECT n_callback',
            '~((HOBJECT n_callback) <- S.ALLOCATIONS)',
            'n_callback <- S.DESTRUCTION.CALLED',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 0',
            '$heap_count(HOBJECT n_callback, $task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation)) = 0',
            '$task_nodes(OB_START_INVALID_NOTICE pobcreation) = eps',
            'S.ERRORHANDLER.CALLBACK = (POBJECT n_replacement)',
            'n_replacement =/= n_callback',
            '$error_handler_eligible(S, 8)',
            'pdestructionoperation.NOGC = eps /\\ pdestructionoperation.NOGCEXTRA = eps',
            'pdestructionoperation.PENDING = eps /\\ pdestructionoperation.COMPLETION = NORMAL',
            'S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            'S.DESTRUCTION.CLEANUPS = pdestructioncleanup :: pdestructioncleanup_tail*',
            '$ob_failure_valid(S, pobcreation)',
            '$ob_failure_tasks(S, pobcreation)',
            '$ob_failure_task_valid(S, pobcreation)',
            '$error_call_valid(S, perrorcall)',
            '$call_task_valid(S, DESTRUCTOR_OPERATION_EXIT pdestructionoperation)',
            '~$ob_failure_tasks(S[.DESTRUCTION.OPERATIONS = pdestructionoperation_tail*], pobcreation)',
            '~$ob_failure_tasks(S[.DESTRUCTION.CLEANUPS = pdestructioncleanup_tail*], pobcreation)',
            *released_negative('released_bad', 'pdestructioncleanup[.RELEASED = false]',
                               'pdestructionoperation[.CLEANUP = (pdestructioncleanup_released_bad)]'),
            *released_negative('source_bad', 'pdestructioncleanup',
                               'pdestructionoperation[.SOURCE = ERROR_HANDLER_RESULT perrorcall]'),
            *released_negative('context_bad', 'pdestructioncleanup[.ORIGIN = eps]',
                               'pdestructionoperation[.CLEANUP = (pdestructioncleanup_context_bad)]'),
            'perrorcall_resume_bad = perrorcall[.RESUME = OB_START_INVALID_NOTICE (pobcreation[.FLAGS = 0])]',
            *released_negative('resume_bad', 'pdestructioncleanup[.SOURCE = ERROR_HANDLER_RESULT perrorcall_resume_bad]',
                               'pdestructionoperation[.SOURCE = ERROR_HANDLER_CLEAN perrorcall_resume_bad][.CLEANUP = (pdestructioncleanup_resume_bad)]'),
            '$heap_valid($heap_graph(S))',
            *DONE,
        ],
    },
    'failure-survives-selector-repair-without-zoh': {
        'source': ORIGINALS['invalid-selector-becomes-valid'].decode(),
        'request_env': ENV,
        'stage': 'S.TODO = (OB_START_INVALID_NOTICE pobcreation) :: ptask_tail* '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'pobcreation.VALUE = PARRAY n_argument',
            'pobcreation.PREFIX = (n_prefix)',
            'pobcreation.PRODUCER = eps /\\ pobcreation.CAPTURE = eps',
            'pobcreation.RAW = (parray)',
            '$entry_lookup(parray.ITEMS, KINT 0) = (DIRECT (POBJECT n_callback))',
            '$entry_lookup(parray.ITEMS, KINT 1) = (DIRECT pvalue_old)',
            '$string_bytes(pvalue_old) = ($ptascii("missing"))',
            'pobcreation.RESOLUTION = HANDLERINVALID ptbytes_reason',
            '$error_handler_resolution(S, pobcreation.VALUE) = HANDLERRESOLVED pcalltarget_now',
            'S_history = $ob_failure_history(S, pobcreation)',
            '$error_handler_resolution(S_history, pobcreation.VALUE) = pobcreation.RESOLUTION',
            'S_history.STORE = S.STORE /\\ S_history.REFCELLS = S.REFCELLS',
            '$ob_failure_valid(S, pobcreation)',
            '$ob_start_receipt_valid(S, pobcreation)',
            '$call_task_valid(S, OB_START_INVALID_NOTICE pobcreation)',
            '~$ob_creation_valid(S, pobcreation)',
            'S_created = S[.TODO = (OB_START_CREATED pobcreation) :: ptask_tail*]',
            '~$call_task_valid(S_created, OB_START_CREATED pobcreation)',
            'S_failed = S[.TODO = (OB_START_FAILED pobcreation) :: ptask_tail*]',
            '~$call_task_valid(S_failed, OB_START_FAILED pobcreation)',
            '$heap_count(HARRAY n_argument, $task_nodes(OB_START_INVALID_NOTICE pobcreation)) = 1',
            '$heap_count(HOBJECT n_callback, $task_nodes(OB_START_INVALID_NOTICE pobcreation)) = 0',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            '$shutdown_snapshot(S, pobcreation.VALUE) = (parray_now)',
            '~$ob_failure_valid(S, pobcreation[.RAW = (parray_now)])',
            '$entry_lookup(S.ARRAYS[n_argument].ITEMS, KINT 1) = (ALIAS n_method)',
            'parray_aliased = S.ARRAYS[n_argument]',
            'S_unrepaired = S[.STORE[n_method] = DEFINED pvalue_old]',
            '$error_handler_resolution(S_unrepaired, pobcreation.VALUE) = pobcreation.RESOLUTION',
            'pobcreation_aliased = pobcreation[.RAW = (parray_aliased)]',
            'S_history_aliased = $ob_failure_history(S_unrepaired, pobcreation_aliased)',
            '$error_handler_resolution(S_history_aliased, pobcreation.VALUE) = pobcreation.RESOLUTION',
            '~$ob_failure_valid(S_unrepaired, pobcreation_aliased)',
            '~$ob_failure_valid(S, pobcreation[.PREFIX = eps])',
            'n_future = $(|S.DECLARATIONS| + 1)',
            '~$ob_failure_valid(S, pobcreation[.PREFIX = (n_future)])',
            '~$ob_failure_valid(S, pobcreation[.RESOLUTION = HANDLERINVALID $ptascii("forged")])',
            '~$ob_failure_valid(S, pobcreation[.CALL = pobcreation.CALL[.LINE = $(pobcreation.CALL.LINE + 1)]])',
            '~$ob_failure_task_valid(S[.OUTPUTBLOCKED = true], pobcreation)',
            '$output_guard(S) = S',
            '$heap_valid($heap_graph(S))',
            *DONE,
            '~((HARRAY n_argument) <- S_done.ALLOCATIONS)',
        ],
    },
    'invalid-direct-cycle-consumes-root-without-buffering': {
        'source': ORIGINALS['invalid-direct-cycle'].decode(),
        'request_env': ENV,
        'stage': 'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
                 '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail* '
                 '-- if pdestructionoperation.SOURCE = OB_NOTICE_RESULT pobnotice '
                 '-- if pobnotice.CREATION = (pobcreation) '
                 '-- if pdestructionoperation.NOGCEXTRA = [pgctemporary] '
                 '-- if ~pgctemporary.PENDING',
        'checks': [
            'pobcreation.VALUE = POBJECT n_callback',
            'pobcreation.RESOLUTION = HANDLERINVALID ptbytes_reason',
            'pobcreation.PREFIX = (n_prefix)',
            'pobcreation.PRODUCER = eps /\\ pobcreation.CAPTURE = eps',
            'pgctemporary.OPERAND = KNOWN (POBJECT n_callback)',
            'pdestructionoperation.VALUE = KNOWN (PBOOL false)',
            '$ob_failure_valid(S, pobcreation)',
            '~$ob_creation_valid(S, pobcreation)',
            '$ob_start_receipt_valid(S, pobcreation)',
            '$gc_temporary_release($gc_temporary_pairs(S), pdestructionoperation) = (pdestructionrelease)',
            '$gc_temporary_nodes(pdestructionrelease.JOBS) = eps',
            '$gc_temporary_metadata_valid(S, pdestructionoperation)',
            '$gc_release_metadata_valid(S, pdestructionrelease)',
            '(HOBJECT n_callback) <- S.ALLOCATIONS',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            '$heap_count(HOBJECT n_callback, $node_children(S, HOBJECT n_callback)) = 1',
            '$heap_count(HOBJECT n_callback, $task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation)) = 0',
            '~((HOBJECT n_callback) <- $gc_nodes(S.GC.BUFFER))',
            '~(n_callback <- S.DESTRUCTION.CALLED)',
            *operation_negative('prefix_bad', 'pdestructionoperation[.SOURCE = OB_NOTICE_RESULT (pobnotice[.CREATION = (pobcreation[.PREFIX = eps])])]'),
            *operation_negative('source_bad', 'pdestructionoperation[.SOURCE = OB_NOTICE_RESULT (pobnotice[.CREATION = eps])]'),
            *operation_negative('value_bad', 'pdestructionoperation[.VALUE = KNOWN PNULL]'),
            *operation_negative('operand_bad', 'pdestructionoperation[.NOGCEXTRA = [pgctemporary[.OPERAND = KNOWN PNULL]]]'),
            '$heap_valid($heap_graph(S))',
            *DONE,
        ],
    },
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
