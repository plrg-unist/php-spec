#!/usr/bin/env python3
"""Reached dynamic __invoke Iterator unpack selection, warning and cleanup checks."""
import argparse
from pathlib import Path
import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']


def source(name):
    return (HERE / ('invokable_iterator_unpack_' + name + '.php')).read_text()


CASES = {
    'selected-before-iterator': {
        'source': source('selected'),
        'stage': 'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail* '
                 '-- if punpackcall.FUNCTION = METHOD_TARGET n_old porigin_method',
        'checks': [
            'punpackcall.CALLSITE = (porigin_site)',
            '$dynamic_site(S, (porigin_site))',
            '$dynamic_fixed_name(S, porigin_site) = eps',
            '$dynamic_cv_name(S, porigin_site) = (ptbytes)',
            '$unpack_class(S, punpackcall) = (UNPACK_CV)',
            '$object_invoke_method(S, n_old) = (pmethoddesc)',
            'pmethoddesc.FUNCTION.ORIGIN = porigin_method',
            'pmethoddesc.NAME = $ptascii("__invoke")',
            'pmethoddesc.VISIBILITY = PROPERTY_PUBLIC',
            '~pmethoddesc.STATIC',
            'S.OBJECTS[n_old] = INSTANCE porigin_class',
            '$effective_method(S, porigin_class, $ptascii("__destruct"), '
            '|S.CLASSES|) = (pmethoddesc_destructor)',
            'pmethoddesc_destructor.FUNCTION.ORIGIN = porigin_destruct',
            'porigin_destruct =/= porigin_method',
            '$call_selected_valid(S, punpackcall.FUNCTION, punpackcall.CALLSITE)',
            '$iterator_unpack_plain(S, punpackcall)',
            '$target_nodes(punpackcall.FUNCTION) = [HOBJECT n_old]',
            '~$iterator_unpack_plain(S, punpackcall[.CALLSITE = eps])',
            '~$iterator_unpack_plain(S, punpackcall[.FUNCTION = '
            'METHOD_TARGET n_old porigin_destruct])',
            *VALID, *ONE,
            'S_one.TODO = (ITERATOR_UNPACK piteratorunpack "rewind-start") :: ptask_tail*',
            'piteratorunpack.CALL = punpackcall',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'selected-after-key-rebind': {
        'source': source('selected'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "key") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = METHOD_TARGET n_old porigin_method',
        'checks': [
            '$lookup(S.ENV, $ptascii("callback")) = (n_callback)',
            'S.STORE[n_callback] = DEFINED (POBJECT n_new)',
            'n_new =/= n_old',
            '$lookup(S.ENV, $ptascii("owner")) = (n_owner)',
            'S.STORE[n_owner] = DEFINED PNULL',
            '$target_nodes(piteratorunpack.CALL.FUNCTION) = [HOBJECT n_old]',
            '$iterator_unpack_result_valid(S, piteratorunpack, "key")',
            *VALID, *ONE,
            'S_one.TODO = (ITERATOR_UNPACK piteratorunpack_send "send") :: ptask_tail*',
            'piteratorunpack_send.CALL.FUNCTION = piteratorunpack.CALL.FUNCTION',
            'piteratorunpack_send.KEY = KNOWN (PINT 0)',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'inherited-named-key': {
        'source': source('named'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = METHOD_TARGET n porigin_method',
        'checks': [
            '$class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc)',
            'pmethoddesc.NAME = $ptascii("__invoke")',
            'piteratorunpack.KEY = KNOWN pvalue_key',
            '$fiber_traversal_key(pvalue_key) = (KSTRING ($ptascii("right")))',
            '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_POSITION 1',
            '$iterator_unpack_result_valid(S, piteratorunpack, "send")',
            *VALID, *ONE,
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'inherited-reference-warning': {
        'source': source('reference'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = METHOD_TARGET n porigin_method',
        'checks': [
            '$iterator_unpack_warning_target(S, piteratorunpack.CALL.FUNCTION) = '
            '$ptascii("InvokableReferenceBase121::__invoke")',
            '$iterator_unpack_warning_message(S, piteratorunpack) = '
            '$ptascii("Cannot pass by-reference argument 1 of '
            'InvokableReferenceBase121::__invoke() by unpacking a Traversable, '
            'passing by-value instead")',
            '$iterator_unpack_result_valid(S, piteratorunpack, "send")',
            *VALID, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_warned "byref"',
            'perrorcall.LINE = $unpack_line(S, piteratorunpack.CALL)',
            '$call_task_valid(S_one, ERROR_HANDLER_INVOKE perrorcall)',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'invalid-key-before-discard': {
        'source': source('invalid_key'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = METHOD_TARGET n_old porigin_method',
        'checks': [
            'piteratorunpack.KEY = KNOWN (PBOOL false)',
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
    'invalid-key-retired-receiver': {
        'source': source('invalid_key'),
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "error" '
                 '-- if piteratorunpack.CALL.FUNCTION = METHOD_TARGET n_old porigin_method',
        'checks': [
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            '~((HOBJECT n_old) <- S.ALLOCATIONS)',
            'S.OBJECTS[n_old] = INSTANCE porigin_class',
            '$effective_method(S, porigin_class, $ptascii("__destruct"), '
            '|S.CLASSES|) = (pmethoddesc_destructor)',
            'pmethoddesc_destructor.FUNCTION.ORIGIN = porigin_destruct',
            'porigin_destruct =/= porigin_method',
            'S_scope = S[.CURRENT = pdestructionoperation.CALLER]'
            '[.ORIGIN = pdestructionoperation.ORIGIN]'
            '[.CONSTCONTEXT = pdestructionoperation.CONSTCONTEXT]',
            '~$iterator_unpack_plain(S_scope, piteratorunpack.CALL)',
            '$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL)',
            '~$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL[.CALLSITE = eps])',
            '~$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL[.FUNCTION = '
            'METHOD_TARGET n_old porigin_destruct])',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            *VALID,
        ],
    },
    'throwing-key-retired-receiver': {
        'source': source('throwing_key'),
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "key" '
                 '-- if piteratorunpack.CALL.FUNCTION = METHOD_TARGET n_old porigin_method',
        'checks': [
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            '~((HOBJECT n_old) <- S.ALLOCATIONS)',
            'S.OBJECTS[n_old] = INSTANCE porigin_class',
            '$effective_method(S, porigin_class, $ptascii("__destruct"), '
            '|S.CLASSES|) = (pmethoddesc_destructor)',
            'pmethoddesc_destructor.FUNCTION.ORIGIN = porigin_destruct',
            'porigin_destruct =/= porigin_method',
            'S_scope = S[.CURRENT = pdestructionoperation.CALLER]'
            '[.ORIGIN = pdestructionoperation.ORIGIN]'
            '[.CONSTCONTEXT = pdestructionoperation.CONSTCONTEXT]',
            '~$iterator_unpack_plain(S_scope, piteratorunpack.CALL)',
            '$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL)',
            '~$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL[.CALLSITE = eps])',
            '~$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL[.FUNCTION = '
            'METHOD_TARGET n_old porigin_destruct])',
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
