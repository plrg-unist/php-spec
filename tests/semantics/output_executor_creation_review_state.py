#!/usr/bin/env python3
"""Independent source-reached create/free owners and borrowed selection checks."""
from pathlib import Path

import fiber_state_review as review
from output_executor_creation_review_sources import ORIGINALS

ROOT = Path(__file__).resolve().parents[2]
review.ROOT = ROOT
ENV = [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')]
DONE = [
    'S_zero = $drive_steps(S, 0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    'S_zero.EVENTS = S.EVENTS /\\ S_zero.ALLOCATIONS = S.ALLOCATIONS',
    'S_done = $drive_steps(S, 1000)',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1000) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
    'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 1',
    'n_callback <- S_done.DESTRUCTION.CALLED',
    '~((HOBJECT n_callback) <- S_done.ALLOCATIONS)',
    '$call_descriptors_valid(S_done) /\\ $output_state_valid(S_done)',
]

review.CASES = {
    'created-zoh-is-one-extra-owner': {
        'source': ORIGINALS['required-invokable'].decode(), 'request_env': ENV,
        'stage': 'S.TODO = (OB_START_CREATED pobcreation) :: ptask_tail* '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'pobcreation.VALUE = POBJECT n_callback',
            'pobcreation.RAW = eps',
            'pobcreation.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_callback))]',
            'pobcreation.CHUNK = 0 /\\ pobcreation.FLAGS = 112',
            '$ob_creation_target(pobcreation.RESOLUTION) = (pcalltarget)',
            '$target_function(S, pcalltarget) = (pfunction)',
            '|pfunction.SIGNATURE.PARAMETERS| = 4',
            '$ob_creation_valid(S, pobcreation)',
            '$call_task_valid(S, OB_START_CREATED pobcreation)',
            '$executor_boundary(S) = eps',
            '$heap_count(HOBJECT n_callback, $task_nodes(OB_START_CREATED pobcreation)) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '~(n_callback <- S.DESTRUCTION.CALLED)',
            '~$ob_creation_valid(S, pobcreation[.VALUE = PNULL])',
            '~$ob_creation_valid(S, pobcreation[.FLAGS = 0])',
            '~$ob_creation_valid(S, pobcreation[.CALL = pobcreation.CALL[.LINE = $(pobcreation.CALL.LINE + 1)]])',
            '~$ob_creation_valid(S, pobcreation[.RESOLUTION = HANDLERINVALID $ptascii("invalid")])',
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1',
            '$call_descriptors_valid(S) /\\ $heap_valid($heap_graph(S))',
            *DONE,
        ],
    },
    'failed-start-retains-only-argument-owner': {
        'source': ORIGINALS['required-invokable'].decode(), 'request_env': ENV,
        'stage': 'S.TODO = (OB_START_FAILED pobcreation) :: ptask_tail* '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'pobcreation.VALUE = POBJECT n_callback',
            'pobcreation.RAW = eps',
            '$ob_creation_valid(S, pobcreation)',
            '$call_task_valid(S, OB_START_FAILED pobcreation)',
            '$heap_count(HOBJECT n_callback, $task_nodes(OB_START_FAILED pobcreation)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            '~(n_callback <- S.DESTRUCTION.CALLED)',
            '(HOBJECT n_callback) <- $gc_nodes(S.GC.BUFFER)',
            '$executor_boundary(S) = eps',
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1',
            '$call_descriptors_valid(S) /\\ $heap_valid($heap_graph(S))',
            *DONE,
        ],
    },
    'notice-keeps-selection-after-reference-rebind': {
        'source': ORIGINALS['referenced-selector-rebound'].decode(), 'request_env': ENV,
        'stage': 'S.TODO = (OB_NOTICE_RESULT pobnotice) :: ptask_tail* '
                 '-- if pobnotice.CREATION = (pobcreation) '
                 '-- if $executor_normal_scope(S)',
        'checks': [
            'pobcreation.VALUE = PARRAY n_argument',
            'pobcreation.RAW = (parray)',
            '$entry_lookup(parray.ITEMS, KINT 1) = (DIRECT pvalue_method)',
            '$string_bytes(pvalue_method) = ($ptascii("run"))',
            '$error_handler_resolution(S, pobcreation.VALUE) = HANDLERINVALID $ptascii("second array member is not a valid method")',
            '$ob_creation_target(pobcreation.RESOLUTION) = (pcalltarget)',
            'S_history = $ob_creation_history(S, pobcreation)',
            '$target_receiver(S_history, pcalltarget) = (n_callback)',
            '$ob_creation_valid(S, pobcreation)',
            '$ob_notice_valid(S, pobnotice)',
            'pobnotice.CALL = pobcreation.CALL /\\ pobnotice.VALUE = PBOOL false',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 1',
            '$heap_count(HOBJECT n_callback, $task_nodes(OB_NOTICE_RESULT pobnotice)) = 0',
            '~$ob_creation_valid(S, pobcreation[.RESOLUTION = HANDLERINVALID $ptascii("invalid")])',
            'pentry_bad* = [ENTRY (KINT 0) (DIRECT (POBJECT n_callback)), ENTRY (KINT 1) (DIRECT (PINT 42))]',
            'parray_bad = parray[.ITEMS = pentry_bad*]',
            '~$ob_creation_valid(S, pobcreation[.RAW = (parray_bad)])',
            '~$ob_notice_valid(S, pobnotice[.CREATION = eps])',
            'PhpStep: S ~> S_returned',
            '$gc_operation_temporary_extra(S, S_returned, OB_NOTICE_RESULT pobnotice, [HARRAY n_argument]) = [pgctemporary]',
            'pgctemporary.OPERAND = KNOWN (PARRAY n_argument) /\\ pgctemporary.PENDING',
            '$gc_operation_temporary_extra(S, S_returned, OB_NOTICE_RESULT pobnotice, [HOBJECT n_callback]) = eps',
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1',
            '$call_descriptors_valid(S) /\\ $heap_valid($heap_graph(S))',
            *DONE,
        ],
    },
    'pending-argument-nogc-matches-source-and-job': {
        'source': ORIGINALS['required-invokable'].decode(), 'request_env': ENV,
        'stage': 'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
                 '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = OB_NOTICE_RESULT pobnotice '
                 '-- if pobnotice.CREATION = (pobcreation) '
                 '-- if pdestructionoperation.NOGCEXTRA = [pgctemporary] '
                 '-- if pdestructionrelease.JOBS = (DESTRUCTION_TEMP pnode) :: pdestructionjob_tail*',
        'checks': [
            'pobcreation.VALUE = POBJECT n_callback',
            'pnode = HOBJECT n_callback',
            'pgctemporary.OPERAND = KNOWN (POBJECT n_callback)',
            'pgctemporary.PENDING',
            'pdestructionoperation.NOGC = eps /\\ pdestructionoperation.CLEANUP = eps',
            'pdestructionoperation.VALUE = KNOWN (PBOOL false)',
            'S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            '$gc_temporary_metadata_valid(S, pdestructionoperation)',
            '$gc_release_metadata_valid(S, pdestructionrelease)',
            '$gc_temporary_release($gc_temporary_pairs(S), pdestructionoperation) = (pdestructionrelease)',
            'pdestructionoperation_origin_bad = pdestructionoperation[.ORIGIN = eps]',
            'S_origin_bad = S[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_origin_bad) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_origin_bad :: pdestructionoperation_tail*]',
            '~$gc_temporary_metadata_valid(S_origin_bad, pdestructionoperation_origin_bad)',
            'pdestructionoperation_value_bad = pdestructionoperation[.VALUE = KNOWN PNULL]',
            'S_value_bad = S[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_value_bad) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_value_bad :: pdestructionoperation_tail*]',
            '~$gc_temporary_metadata_valid(S_value_bad, pdestructionoperation_value_bad)',
            'pdestructionoperation_source_bad = pdestructionoperation[.SOURCE = OB_NOTICE_RESULT (pobnotice[.CREATION = eps])]',
            'S_source_bad = S[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_source_bad) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_source_bad :: pdestructionoperation_tail*]',
            '~$gc_temporary_metadata_valid(S_source_bad, pdestructionoperation_source_bad)',
            'pdestructionoperation_operand_bad = pdestructionoperation[.NOGCEXTRA = [pgctemporary[.OPERAND = KNOWN PNULL]]]',
            'S_operand_bad = S[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_operand_bad) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_operand_bad :: pdestructionoperation_tail*]',
            '~$gc_temporary_metadata_valid(S_operand_bad, pdestructionoperation_operand_bad)',
            'pdestructionoperation_pending_bad = pdestructionoperation[.NOGCEXTRA = [pgctemporary[.PENDING = false]]]',
            'S_pending_bad = S[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_pending_bad) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_pending_bad :: pdestructionoperation_tail*]',
            '~$gc_temporary_metadata_valid(S_pending_bad, pdestructionoperation_pending_bad)',
            'S.OUTPUTBUFFERS = eps /\\ S.OUTPUTSEQ = 1',
            '$heap_valid($heap_graph(S))',
            *DONE,
        ],
    },
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=150) else 1)
