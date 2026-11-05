#!/usr/bin/env python3
"""A genuine Notice CLEAN continuation authenticates the consumed argument."""
from pathlib import Path

import fiber_state_review as review
from output_executor_notice_retval_throw_review_sources import ORIGINALS

ROOT = Path(__file__).resolve().parents[2]
review.ROOT = ROOT
ENV = [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')]


def issuer_negative(name, expression):
    return [
        f'perrorcall_{name} = {expression}',
        f'pdestructioncleanup_{name} = pdestructioncleanup[.SOURCE = ERROR_HANDLER_RESULT perrorcall_{name}]',
        f'S_{name} = S[.TODO = (THROW_SEARCH n_pending) :: (ERROR_HANDLER_CLEAN perrorcall_{name}) :: ptask_tail*][.DESTRUCTION.CLEANUPS = pdestructioncleanup_{name} :: pdestructioncleanup_tail*]',
        f'$ob_start_discarded(S_{name}, n_pending) = eps',
    ]


def cleanup_negative(name, expression):
    return [
        f'pdestructioncleanup_{name} = {expression}',
        f'S_{name} = S[.DESTRUCTION.CLEANUPS = pdestructioncleanup_{name} :: pdestructioncleanup_tail*]',
        f'$ob_start_discarded(S_{name}, n_pending) = eps',
    ]


review.CASES = {
    'notice-retval-clean-consumes-only-argument-root': {
        'source': ORIGINALS['retval-precreated-successful-direct'].decode(),
        'request_env': ENV,
        'stage': 'S.TODO = (THROW_SEARCH n_pending) :: (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
                 '-- if perrorcall.RESUME = OB_NOTICE_RESULT pobnotice '
                 '-- if pobnotice.CREATION = (pobcreation) '
                 '-- if pobcreation.VALUE = POBJECT n_callback '
                 '-- if S.DESTRUCTION.CLEANUPS = pdestructioncleanup :: pdestructioncleanup_tail* '
                 '-- if pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall '
                 '-- if ~pdestructioncleanup.RELEASED',
        'checks': [
            '$throwable_live(S, n_pending)',
            'pobcreation.PREFIX = eps',
            '$ob_creation_valid(S, pobcreation)',
            'pobnotice.CALL = pobcreation.CALL /\\ pobnotice.VALUE = PBOOL false',
            '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
            '$heap_count(HOBJECT n_callback, $node_children(S, HOBJECT n_callback)) = 1',
            '~((HOBJECT n_callback) <- $gc_nodes(S.GC.BUFFER))',
            '$throwable_field(S, n_pending, "trace") = PARRAY n_trace',
            'H_before = $heap_graph(S)',
            '~((HOBJECT n_callback) <- $heap_reach([HARRAY n_trace], eps, H_before.EDGES))',
            'S_projected = S[.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail*]',
            '$call_task_valid(S_projected, ERROR_HANDLER_CLEAN perrorcall)',
            '$ob_notice_valid(S_projected, pobnotice)',
            '$ob_start_continuation(ERROR_HANDLER_CLEAN perrorcall) = (OB_NOTICE_RESULT pobnotice)',
            '$ob_start_discarded(S, n_pending) = (pobcreation)',
            *issuer_negative('level_bad', 'perrorcall[.LEVEL = 2][.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE perrorcall.LINE]'),
            'ptbytes_forged = $ptascii("forged")',
            *issuer_negative('message_bad', 'perrorcall[.MESSAGE = ptbytes_forged][.EVENT = DIAGNOSTIC "Notice" ptbytes_forged perrorcall.LINE]'),
            *cleanup_negative('released_bad', 'pdestructioncleanup[.RELEASED = true]'),
            *cleanup_negative('source_bad', 'pdestructioncleanup[.SOURCE = ERROR_HANDLER_CLEAN perrorcall]'),
            *cleanup_negative('origin_bad', 'pdestructioncleanup[.ORIGIN = eps]'),
            'S_missing = S[.DESTRUCTION.CLEANUPS = pdestructioncleanup_tail*]',
            '$ob_start_discarded(S_missing, n_pending) = eps',
            'PhpStep: S ~> S_raw',
            'S_release = $literal_reference_debt_step(S, S_raw)',
            'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_after*',
            'S_release.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            'pdestructionoperation.SOURCE = OB_START_ARGUMENT_DISCARD pobcreation n_pending',
            'pdestructionoperation.PENDING = (n_pending) /\\ pdestructionoperation.COMPLETION = NORMAL',
            'pdestructionoperation.VALUE = KNOWN PNULL',
            'pdestructionoperation.NOGC = eps',
            'pdestructionoperation.NOGCEXTRA = [pgctemporary]',
            'pgctemporary.OPERAND = KNOWN (POBJECT n_callback)',
            'pgctemporary.PENDING',
            '(DESTRUCTION_TEMP (HOBJECT n_callback)) <- pdestructionrelease.JOBS',
            '~((DESTRUCTION_VALUE (HOBJECT n_callback)) <- pdestructionrelease.JOBS)',
            '$task_nodes(OB_START_ARGUMENT_DISCARD pobcreation n_pending) = eps',
            '~$call_task_valid(S_release, OB_START_ARGUMENT_DISCARD pobcreation n_pending)',
            '$ob_start_discard_valid(S_release, pdestructionoperation)',
            '$gc_temporary_metadata_valid(S_release, pdestructionoperation)',
            '$gc_release_metadata_valid(S_release, pdestructionrelease)',
            'S_after = $drive_steps(S_release, 4)',
            '~((HOBJECT n_callback) <- $gc_nodes(S_after.GC.BUFFER))',
            '$heap_owners($heap_graph(S_after), HOBJECT n_callback) = 1',
            '$heap_count(HOBJECT n_callback, $node_children(S_after, HOBJECT n_callback)) = 1',
            '~(n_callback <- S_after.DESTRUCTION.CALLED)',
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
}


if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
