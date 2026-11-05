#!/usr/bin/env python3
"""Real Notice consumption distinguishes root TEMP from ordinary child release."""
from pathlib import Path

import fiber_state_review as review
from output_executor_notice_discard_review_sources import ORIGINALS

ROOT = Path(__file__).resolve().parents[2]
review.ROOT = ROOT
ENV = [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')]


def issuer_negative(name, expression):
    return [
        f'perrorcall_{name} = {expression}',
        f'S_{name} = S[.TODO = (THROW_SEARCH n_pending) :: (ERROR_HANDLER_RESULT perrorcall_{name}) :: ptask_tail*]',
        f'$ob_start_discarded(S_{name}, n_pending) = eps',
    ]


def operation_negative(name, expression):
    return [
        f'pdestructionoperation_{name} = {expression}',
        f'S_{name} = S_release[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_{name}) :: ptask_after*][.DESTRUCTION.OPERATIONS = pdestructionoperation_{name} :: pdestructionoperation_tail*]',
        f'$gc_temporary_release($gc_temporary_pairs(S_{name}), pdestructionoperation_{name}) = (pdestructionrelease)',
        f'~$gc_temporary_metadata_valid(S_{name}, pdestructionoperation_{name})',
    ]


def completed(state, callback):
    return [
        f'S_done = $drive_steps({state}[.COMPLETION = NORMAL], 1000)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
        'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 1',
        f'{callback} <- S_done.DESTRUCTION.CALLED',
        f'~((HOBJECT {callback}) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done) /\\ $output_state_valid(S_done)',
    ]


def direct_checks(successful):
    receipt = ([
        'pobcreation.PREFIX = eps',
        '$ob_creation_valid(S, pobcreation)',
        '~$ob_failure_valid(S, pobcreation)',
    ] if successful else [
        'pobcreation.PREFIX = (n_prefix)',
        '$ob_failure_valid(S, pobcreation)',
        '~$ob_creation_valid(S, pobcreation)',
    ])
    bad_prefix = '(0)' if successful else 'eps'
    return [
        '$throwable_live(S, n_pending)',
        'pobcreation.VALUE = POBJECT n_callback',
        'pobnotice.CALL = pobcreation.CALL /\\ pobnotice.VALUE = PBOOL false',
        *receipt,
        '$ob_start_receipt_valid(S, pobcreation)',
        '$heap_owners($heap_graph(S), HOBJECT n_callback) = 2',
        '$heap_count(HOBJECT n_callback, $node_children(S, HOBJECT n_callback)) = 1',
        '~((HOBJECT n_callback) <- $gc_nodes(S.GC.BUFFER))',
        '$throwable_field(S, n_pending, "trace") = PARRAY n_trace',
        'H_before = $heap_graph(S)',
        '~((HOBJECT n_callback) <- $heap_reach([HARRAY n_trace], eps, H_before.EDGES))',
        'S_projected = S[.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*]',
        '$call_task_valid(S_projected, ERROR_HANDLER_RESULT perrorcall)',
        '$ob_start_continuation(ERROR_HANDLER_RESULT perrorcall) = (OB_NOTICE_RESULT pobnotice)',
        '$ob_start_discard_phase(ERROR_HANDLER_RESULT perrorcall) = (pobcreation)',
        '$ob_start_discarded(S, n_pending) = (pobcreation)',
        *issuer_negative('level_bad', 'perrorcall[.LEVEL = 2][.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE perrorcall.LINE]'),
        'ptbytes_forged = $ptascii("forged")',
        *issuer_negative('message_bad', 'perrorcall[.MESSAGE = ptbytes_forged][.EVENT = DIAGNOSTIC "Notice" ptbytes_forged perrorcall.LINE]'),
        'pobnotice_creation_bad = pobnotice[.CREATION = eps]',
        *issuer_negative('creation_bad', 'perrorcall[.RESUME = OB_NOTICE_RESULT pobnotice_creation_bad]'),
        'PhpStep: S ~> S_raw',
        'S_release = $literal_reference_debt_step(S, S_raw)',
        'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_after*',
        'S_release.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
        'pdestructionoperation.SOURCE = OB_START_ARGUMENT_DISCARD pobcreation n_pending',
        'pdestructionoperation.CLEANUP = eps',
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
        '$call_task_valid(S_release, DESTRUCTOR_OPERATION_EXIT pdestructionoperation)',
        '$gc_temporary_metadata_valid(S_release, pdestructionoperation)',
        '$gc_release_metadata_valid(S_release, pdestructionrelease)',
        *operation_negative('prefix_bad', f'pdestructionoperation[.SOURCE = OB_START_ARGUMENT_DISCARD (pobcreation[.PREFIX = {bad_prefix}]) n_pending]'),
        *operation_negative('source_bad', 'pdestructionoperation[.SOURCE = THROW_SEARCH n_pending]'),
        *operation_negative('pending_bad', 'pdestructionoperation[.PENDING = eps]'),
        *operation_negative('progress_bad', 'pdestructionoperation[.NOGCEXTRA = [pgctemporary[.PENDING = false]]]'),
        'S_after = $drive_steps(S_release, 4)',
        '~((HOBJECT n_callback) <- $gc_nodes(S_after.GC.BUFFER))',
        '$heap_owners($heap_graph(S_after), HOBJECT n_callback) = 1',
        '$heap_count(HOBJECT n_callback, $node_children(S_after, HOBJECT n_callback)) = 1',
        '~(n_callback <- S_after.DESTRUCTION.CALLED)',
        'S_zero = $drive_steps(S_release, 0)',
        'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S_release.TODO',
        '$drive_steps(S_zero[.COMPLETION = NORMAL], 4) = S_after',
        *completed('S_after', 'n_callback'),
    ]


review.CASES = {}
for successful in (True, False):
    name = 'successful-direct' if successful else 'failed-direct'
    review.CASES[name + '-notice-argument-root'] = {
        'source': ORIGINALS[name].decode(),
        'request_env': ENV,
        'stage': 'S.TODO = (THROW_SEARCH n_pending) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail* '
                 '-- if perrorcall.RESUME = OB_NOTICE_RESULT pobnotice '
                 '-- if pobnotice.CREATION = (pobcreation)',
        'checks': direct_checks(successful),
    }

review.CASES['array-child-remains-an-ordinary-decrement'] = {
    'source': ORIGINALS['successful-array-child'].decode(),
    'request_env': ENV,
    'stage': 'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
             '-- if pdestructionoperation.SOURCE = OB_START_ARGUMENT_DISCARD pobcreation n_pending '
             '-- if pobcreation.VALUE = PARRAY n_argument '
             '-- if pobcreation.RAW = (parray) '
             '-- if $entry_lookup(parray.ITEMS, KINT 0) = (DIRECT (POBJECT n_child)) '
             '-- if pdestructionoperation.NOGCEXTRA = [pgctemporary] '
             '-- if ~pgctemporary.PENDING '
             '-- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_child)) :: pdestructionjob_tail*',
    'checks': [
        '$throwable_live(S, n_pending)',
        'pobcreation.PREFIX = eps',
        'pgctemporary.OPERAND = KNOWN (PARRAY n_argument)',
        'pdestructionoperation.PENDING = (n_pending)',
        'pdestructionoperation.VALUE = KNOWN PNULL',
        'pdestructionoperation.NOGC = eps',
        '~((HARRAY n_argument) <- S.ALLOCATIONS)',
        '(HOBJECT n_child) <- S.ALLOCATIONS',
        '$heap_owners($heap_graph(S), HOBJECT n_child) = 2',
        '$heap_count(HOBJECT n_child, $node_children(S, HOBJECT n_child)) = 1',
        '~((HOBJECT n_child) <- $gc_nodes(S.GC.BUFFER))',
        '$gc_temporary_nodes(pdestructionrelease.JOBS) = eps',
        '$ob_start_discard_valid(S, pdestructionoperation)',
        '$gc_temporary_release($gc_temporary_pairs(S), pdestructionoperation) = (pdestructionrelease)',
        '$gc_temporary_metadata_valid(S, pdestructionoperation)',
        '$gc_release_metadata_valid(S, pdestructionrelease)',
        'S_after = $drive_steps(S, 1)',
        '(HOBJECT n_child) <- $gc_nodes(S_after.GC.BUFFER)',
        '$heap_owners($heap_graph(S_after), HOBJECT n_child) = 1',
        '$heap_count(HOBJECT n_child, $node_children(S_after, HOBJECT n_child)) = 1',
        '~(n_child <- S_after.DESTRUCTION.CALLED)',
        'S_zero = $drive_steps(S, 0)',
        'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
        '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_after',
        *completed('S_after', 'n_child'),
    ],
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=360) else 1)
