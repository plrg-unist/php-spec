#!/usr/bin/env python3
"""Consumed Closure arguments retain borrowed checking facts during propagation."""
from pathlib import Path

import fiber_state_review as review
from output_executor_notice_discard_sources import ORIGINALS

review.ROOT = Path(__file__).resolve().parents[2]


def producer_negative(name, expression):
    return [
        f'pobcreation_{name} = pobcreation[.PRODUCER = ({expression})]',
        f'pdestructionoperation_{name} = pdestructionoperation[.SOURCE = OB_START_ARGUMENT_DISCARD pobcreation_{name} n_pending]',
        f'S_{name} = S[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_{name}) :: ptask_tail*][.DESTRUCTION.OPERATIONS = pdestructionoperation_{name} :: pdestructionoperation_tail*]',
        f'$gc_temporary_release($gc_temporary_pairs(S_{name}), pdestructionoperation_{name}) = (pdestructionrelease)',
        f'~$gc_temporary_metadata_valid(S_{name}, pdestructionoperation_{name})',
    ]


review.CASES = {
    'consumed-notice-throw-closure-capture-is-borrowed': {
        'source': ORIGINALS['factory-byref-closure'].decode(),
        'request_env': [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one')],
        'stage': 'S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
                 '(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail* '
                 '-- if pdestructionoperation.SOURCE = OB_START_ARGUMENT_DISCARD pobcreation n_pending '
                 '-- if pobcreation.VALUE = POBJECT n_callback '
                 '-- if pobcreation.PRODUCER = (pshutdownproducer) '
                 '-- if ~((HOBJECT n_callback) <- S.ALLOCATIONS) '
                 '-- if $node_children(S, HOBJECT n_callback) = [HCELL n_capture] '
                 '-- if ~((HCELL n_capture) <- S.ALLOCATIONS) '
                 '-- if S.STORE[n_capture] = DEFINED (POBJECT n_child) '
                 '-- if n_child <- S.DESTRUCTION.CALLED '
                 '-- if ~((HOBJECT n_child) <- S.ALLOCATIONS)',
        'checks': [
            'pdestructionoperation.PENDING = (n_pending)',
            '$throwable_live(S, n_pending)',
            'pdestructionoperation.COMPLETION = NORMAL',
            'pdestructionoperation.NOGC = eps',
            'pdestructionoperation.NOGCEXTRA = [pgctemporary]',
            'pgctemporary.OPERAND = KNOWN (POBJECT n_callback)',
            '~pgctemporary.PENDING',
            '$gc_temporary_release($gc_temporary_pairs(S), pdestructionoperation) = (pdestructionrelease)',
            'pshutdownproducer.SCOPE = eps /\\ pshutdownproducer.BINDING = eps',
            'n_capture <- S.REFCELLS',
            'S.STORE[n_capture] = DEFINED (POBJECT n_child)',
            'n_child <- S.DESTRUCTION.CALLED',
            '~((HOBJECT n_child) <- S.ALLOCATIONS)',
            '~$ob_creation_valid(S, pobcreation)',
            'S_borrowed = $ob_creation_consumed_history(S, pobcreation)',
            'S_borrowed[.ALLOCATIONS = S.ALLOCATIONS][.CLOSURESCOPES = S.CLOSURESCOPES][.CLOSUREBINDINGS = S.CLOSUREBINDINGS] = S',
            '(HCELL n_capture) <- S_borrowed.ALLOCATIONS',
            '$closure_callable(S_borrowed, n_callback)',
            '$ob_start_receipt_valid(S_borrowed, pobcreation)',
            '$ob_start_discard_valid(S, pdestructionoperation)',
            '$gc_temporary_metadata_valid(S, pdestructionoperation)',
            '$gc_release_metadata_valid(S, pdestructionrelease)',
            'H = $heap_graph(S)',
            '$heap_owners(H, HOBJECT n_callback) = 0',
            '$heap_owners(H, HCELL n_capture) = 0',
            '$heap_owners(H, HOBJECT n_child) = 0',
            '$task_nodes(OB_START_ARGUMENT_DISCARD pobcreation n_pending) = eps',
            '~$call_task_valid(S, OB_START_ARGUMENT_DISCARD pobcreation n_pending)',
            '$heap_count(HOBJECT n_callback, $task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation)) = 0',
            '$heap_count(HOBJECT n_pending, $task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation)) = 1',
            *producer_negative('target_bad', 'pshutdownproducer[.TARGET = CLOSURE_TARGET (|S.OBJECTS|)]'),
            *producer_negative('site_bad', 'pshutdownproducer[.SITE = (pobcreation.CALL.SITE)]'),
            *producer_negative('internal_bad', 'pshutdownproducer[.INTERNAL = false]'),
            'S_zero = $drive_steps(S, 0)',
            'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
            'S_zero.EVENTS = S.EVENTS /\\ S_zero.ALLOCATIONS = S.ALLOCATIONS',
            'S_done = $drive_steps(S, 1000)',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 1000) = S_done',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
            'S_done.OUTPUTBUFFERS = eps /\\ S_done.OUTPUTSEQ = 1',
            '~((HOBJECT n_callback) <- S_done.ALLOCATIONS)',
            '~((HCELL n_capture) <- S_done.ALLOCATIONS)',
            '$call_descriptors_valid(S_done) /\\ $output_state_valid(S_done)',
        ],
    },
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=180) else 1)
