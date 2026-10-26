#!/usr/bin/env python3
"""Reached array-callable Iterator unpack target, warning and cleanup states."""
import argparse
from pathlib import Path
import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']


def source(name):
    return (HERE / ('array_callable_iterator_' + name + '.php')).read_text()


CASES = {
    'selected-object-before-iterator': {
        'source': source('object_selection'),
        'stage': 'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail* '
                 '-- if punpackcall.FUNCTION = '
                 'ARRAY_METHOD_TARGET (METHOD_TARGET n_old porigin_method) parrayselection',
        'checks': [
            'punpackcall.CALLSITE = (parrayselection.SITE)',
            '$unpack_class(S, punpackcall) = (UNPACK_CV)',
            '$call_selected_valid(S, punpackcall.FUNCTION, punpackcall.CALLSITE)',
            '$iterator_unpack_plain(S, punpackcall)',
            '$target_nodes(punpackcall.FUNCTION) = [HOBJECT n_old]',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 3',
            *VALID, *ONE,
            'S_one.TODO = (ITERATOR_UNPACK piteratorunpack "rewind-start") :: ptask_tail*',
            'piteratorunpack.CALL = punpackcall',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'selected-object-after-key-rebind': {
        'source': source('object_selection'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "key") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = '
                 'ARRAY_METHOD_TARGET (METHOD_TARGET n_old porigin_method) parrayselection',
        'checks': [
            '$lookup(S.ENV, $ptascii("cb")) = (n_cb)',
            'S.STORE[n_cb] = DEFINED (PARRAY n_callback_new)',
            '$lookup(S.ENV, $ptascii("owner")) = (n_owner)',
            'S.STORE[n_owner] = DEFINED PNULL',
            '$target_nodes(piteratorunpack.CALL.FUNCTION) = [HOBJECT n_old]',
            '$heap_owners($heap_graph(S), HOBJECT n_old) = 1',
            '$iterator_unpack_result_valid(S, piteratorunpack, "key")',
            *VALID, *ONE,
            'S_one.TODO = (ITERATOR_UNPACK piteratorunpack_send "send") :: ptask_tail*',
            'piteratorunpack_send.CALL.FUNCTION = piteratorunpack.CALL.FUNCTION',
            'piteratorunpack_send.KEY = KNOWN (PINT 0)',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'selected-static-before-iterator': {
        'source': source('static_named'),
        'stage': 'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail* '
                 '-- if punpackcall.FUNCTION = '
                 'ARRAY_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) parrayselection',
        'checks': [
            'punpackcall.CALLSITE = (parrayselection.SITE)',
            '$unpack_class(S, punpackcall) = (UNPACK_CV)',
            '$call_selected_valid(S, punpackcall.FUNCTION, punpackcall.CALLSITE)',
            '$iterator_unpack_plain(S, punpackcall)',
            '$target_nodes(punpackcall.FUNCTION) = eps',
            *VALID, *ONE,
            'S_one.TODO = (ITERATOR_UNPACK piteratorunpack "rewind-start") :: ptask_tail*',
            'piteratorunpack.CALL = punpackcall',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'static-warning-declaring-owner': {
        'source': source('static_reference'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = '
                 'ARRAY_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) parrayselection',
        'checks': [
            '$iterator_unpack_warning_target(S, piteratorunpack.CALL.FUNCTION) = '
            '$ptascii("ReferenceBase119::take")',
            '$iterator_unpack_warning_message(S, piteratorunpack) = '
            '$ptascii("Cannot pass by-reference argument 1 of ReferenceBase119::take() '
            'by unpacking a Traversable, passing by-value instead")',
            *VALID, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_warned "byref"',
            'perrorcall.LINE = 20',
            '$call_task_valid(S_one, ERROR_HANDLER_INVOKE perrorcall)',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'invalid-key-before-discard': {
        'source': source('invalid_key'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = '
                 'ARRAY_METHOD_TARGET (METHOD_TARGET n_old porigin_method) parrayselection',
        'checks': [
            'piteratorunpack.KEY = KNOWN (PBOOL false)',
            'piteratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
            '$iterator_unpack_result_valid(S, piteratorunpack, "send")',
            *VALID,
            'S_error = $iterator_unpack_send(S, piteratorunpack, ptask_tail*)',
            'S_error.COMPLETION = THROWN "Error" '
            '($ptascii("Keys must be of type int|string during argument unpacking")) '
            '$unpack_line(S, piteratorunpack.CALL)',
            'S_error.TODO = (ITERATOR_UNPACK piteratorunpack "error") :: ptask_tail*',
            '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
        ],
    },
    'throwing-key-receiver-cleanup': {
        'source': source('key_throw'),
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "key" '
                 '-- if piteratorunpack.CALL.FUNCTION = '
                 'ARRAY_METHOD_TARGET (METHOD_TARGET n_old porigin_method) parrayselection',
        'checks': [
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            '~((HOBJECT n_old) <- S.ALLOCATIONS)',
            'S.OBJECTS[n_old] = INSTANCE parrayselection.REQUESTED',
            'S_scope = S[.CURRENT = pdestructionoperation.CALLER]'
            '[.ORIGIN = pdestructionoperation.ORIGIN]'
            '[.CONSTCONTEXT = pdestructionoperation.CONSTCONTEXT]',
            '~$iterator_unpack_plain(S_scope, piteratorunpack.CALL)',
            '$array_site_valid(S_scope, parrayselection, false)',
            '$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL)',
            '~$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL[.FUNCTION = '
            'ARRAY_METHOD_TARGET (METHOD_TARGET n_old porigin_method) '
            'parrayselection[.LINE = 0]])',
            '~$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL[.CALLSITE = eps])',
            '~$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL[.FUNCTION = '
            'ARRAY_METHOD_TARGET (METHOD_TARGET n_old porigin_method) '
            'parrayselection[.REQUESTED = porigin_method]])',
            '~$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL[.FUNCTION = '
            'ARRAY_METHOD_TARGET (METHOD_TARGET n_old porigin_method) '
            'parrayselection[.NAME = $ptascii("missing")]])',
            '~$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL[.FUNCTION = '
            'METHOD_TARGET n_old porigin_method])',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            *VALID,
        ],
    },
    'invalid-key-receiver-cleanup': {
        'source': source('invalid_key'),
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "error" '
                 '-- if piteratorunpack.CALL.FUNCTION = '
                 'ARRAY_METHOD_TARGET (METHOD_TARGET n_old porigin_method) parrayselection',
        'checks': [
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            '$iterator_unpack_abort_plain(S[.CURRENT = pdestructionoperation.CALLER]'
            '[.ORIGIN = pdestructionoperation.ORIGIN]'
            '[.CONSTCONTEXT = pdestructionoperation.CONSTCONTEXT], piteratorunpack.CALL)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            *VALID,
        ],
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    assert not args.case or set(args.case) <= CASES.keys()
    review.ROOT = ROOT
    review.CASES = CASES
    for name in args.case or list(CASES):
        assert review.run([name])
