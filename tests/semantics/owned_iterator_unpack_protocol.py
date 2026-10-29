#!/usr/bin/env python3
"""Source-reached owned Iterator INPUT, selected targets and cleanup receipts."""
import argparse
from pathlib import Path
import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']


def source(name):
    return (HERE / ('owned_iterator_unpack_' + name + '.php')).read_text()


CASES = {
    'array-input-data-and-selected-receiver': {
        'source': source('array_instance'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "key") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = '
                 'ARRAY_METHOD_TARGET (METHOD_TARGET n_receiver porigin_method) parrayselection',
        'checks': [
            '$unpack_class(S, piteratorunpack.CALL) = (UNPACK_VALUE)',
            'n_data = piteratorunpack.OBJECT',
            'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
            'n_receiver =/= n_data',
            '$lookup(S.ENV, $ptascii("callback")) = (n_callback)',
            'S.STORE[n_callback] = DEFINED PNULL',
            '$lookup(S.ENV, $ptascii("receiver")) = (n_source)',
            'S.STORE[n_source] = DEFINED PNULL',
            '$iterator_unpack_nodes(piteratorunpack) = [HOBJECT n_data, HOBJECT n_data]',
            '$target_nodes(piteratorunpack.CALL.FUNCTION) = [HOBJECT n_receiver]',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1',
            '$iterator_unpack_result_valid(S, piteratorunpack, "key")',
            '~$iterator_unpack_input(S, piteratorunpack.CALL, VARIABLE ($ptascii("iterator")) 1)',
            *VALID, *ONE,
            'S_one.TODO = (ITERATOR_UNPACK piteratorunpack_send "send") :: ptask_tail*',
            'piteratorunpack_send.INPUT = piteratorunpack.INPUT',
            'piteratorunpack_send.CALL.FUNCTION = piteratorunpack.CALL.FUNCTION',
            'piteratorunpack_send.KEY = KNOWN (PINT 0)',
            *POST,
        ],
    },
    'inherited-static-factory-named-send': {
        'source': source('array_static'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = '
                 'ARRAY_METHOD_TARGET (STATIC_METHOD_TARGET porigin_class porigin_method) parrayselection',
        'checks': [
            '$unpack_class(S, piteratorunpack.CALL) = (UNPACK_VAR)',
            'piteratorunpack.INPUT = KNOWN (POBJECT piteratorunpack.OBJECT)',
            '$class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc)',
            'pmethoddesc.OWNER =/= porigin_class',
            '$target_called_class(S, piteratorunpack.CALL.FUNCTION) = (porigin_class)',
            '$target_nodes(piteratorunpack.CALL.FUNCTION) = eps',
            'piteratorunpack.KEY = KNOWN pvalue_key',
            '$fiber_traversal_key(pvalue_key) = (KSTRING ($ptascii("right")))',
            '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_POSITION 1',
            '$iterator_unpack_result_valid(S, piteratorunpack, "send")',
            *VALID, *ONE, *POST,
        ],
    },
    'arrow-value-input-finishes-before-entry': {
        'source': source('arrow_value'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "finish") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = CLOSURE_TARGET n_closure',
        'checks': [
            '$unpack_class(S, piteratorunpack.CALL) = (UNPACK_VALUE)',
            'n_data = piteratorunpack.OBJECT',
            'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
            'piteratorunpack.CURRENT = KNOWN PNULL',
            'piteratorunpack.KEY = KNOWN PNULL',
            'piteratorunpack.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN (PINT 7))]',
            '$iterator_unpack_nodes(piteratorunpack) = [HOBJECT n_data, HOBJECT n_data]',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            '$iterator_unpack_result_valid(S, piteratorunpack, "finish")',
            *VALID, *ONE,
            'S_one.ITERATORS = eps',
            *POST,
        ],
    },
    'direct-method-retired-value-input': {
        'source': source('method_invalid'),
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "error" '
                 '-- if piteratorunpack.CALL.FUNCTION = METHOD_TARGET n_receiver porigin_method '
                 '-- if ~((HOBJECT n_receiver) <- S.ALLOCATIONS)',
        'checks': [
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            '~((HOBJECT n_receiver) <- S.ALLOCATIONS)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
            'piteratorunpack.CALL.CALLSITE = (porigin_site)',
            '$origin_node(S.SOURCES, porigin_site) = '
            '(NExprMethodCall expression phpType20 (SEQUENCE phpType7*) metadata)',
            '$unpack_class(S, piteratorunpack.CALL) = (UNPACK_VALUE)',
            'piteratorunpack.INPUT = KNOWN (POBJECT piteratorunpack.OBJECT)',
            '~((HOBJECT piteratorunpack.OBJECT) <- S.ALLOCATIONS)',
            'S_scope = S[.CURRENT = pdestructionoperation.CALLER]'
            '[.ORIGIN = pdestructionoperation.ORIGIN]'
            '[.CONSTCONTEXT = pdestructionoperation.CONSTCONTEXT]',
            '~$iterator_unpack_plain(S_scope, piteratorunpack.CALL)',
            '$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL)',
            '$iterator_unpack_abort_input(S_scope, piteratorunpack)',
            '~$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL[.CALLSITE = eps])',
            '~$iterator_unpack_abort_input(S_scope, piteratorunpack[.INPUT = KNOWN (POBJECT n_receiver)])',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            *VALID,
        ],
    },
    'real-closure-retired-factory-input': {
        'source': source('closure_invalid'),
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "error" '
                 '-- if piteratorunpack.CALL.FUNCTION = CLOSURE_TARGET n_closure '
                 '-- if ~((HOBJECT n_closure) <- S.ALLOCATIONS)',
        'checks': [
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            '~((HOBJECT n_closure) <- S.ALLOCATIONS)',
            '$unpack_class(S, piteratorunpack.CALL) = (UNPACK_VAR)',
            'piteratorunpack.INPUT = KNOWN (POBJECT piteratorunpack.OBJECT)',
            '~((HOBJECT piteratorunpack.OBJECT) <- S.ALLOCATIONS)',
            'piteratorunpack.CLOSUREORIGIN = (porigin_closure)',
            '$iterator_unpack_closure_raw_origin(S, n_closure) = (porigin_closure)',
            'S_scope = S[.CURRENT = pdestructionoperation.CALLER]'
            '[.ORIGIN = pdestructionoperation.ORIGIN]'
            '[.CONSTCONTEXT = pdestructionoperation.CONSTCONTEXT]',
            '~$iterator_unpack_plain(S_scope, piteratorunpack.CALL)',
            '$iterator_unpack_abort_selected(S_scope, piteratorunpack)',
            '$iterator_unpack_abort_input(S_scope, piteratorunpack)',
            '~$iterator_unpack_abort_selected(S_scope, piteratorunpack[.CLOSUREORIGIN = eps])',
            '~$iterator_unpack_abort_selected(S_scope, piteratorunpack[.CALL.CALLSITE = eps])',
            '~$iterator_unpack_abort_input(S_scope, piteratorunpack[.INPUT = KNOWN (POBJECT n_closure)])',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            *VALID,
        ],
    },
    'invokable-private-cell-after-input-destructor': {
        'source': source('invokable_reference'),
        'stage': 'S.CURRENT = (pcallcontext) '
                 '-- if pcallcontext.TARGET = METHOD_TARGET n_receiver porigin_method '
                 '-- if S.TODO = (EMIT z_emit) :: ptask_tail* '
                 '-- if S.RESULT = KNOWN pvalue_text '
                 '-- if $string_bytes(pvalue_text) = ($ptascii("B|"))',
        'checks': [
            '$class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc)',
            'pmethoddesc.NAME = $ptascii("__invoke")',
            '$lookup(S.ENV, $ptascii("item")) = (n_private)',
            '$lookup(S.ENV, $ptascii("value")) = (n_value)',
            'n_private =/= n_value',
            'S.STORE[n_private] = DEFINED (PINT 9)',
            'S.STORE[n_value] = DEFINED (PINT 11)',
            'n_private <- S.REFCELLS',
            'S.ITERATORS = eps',
            '$lookup($global_table_view(S).ENV, $ptascii("callback")) = (n_callback)',
            'S.STORE[n_callback] = DEFINED PNULL',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS',
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
