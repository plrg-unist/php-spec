#!/usr/bin/env python3
"""Source-reached computed callee acquisition, selection and retired receipts."""
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
    return (HERE / ('computed_callee_unpack_' + name + '.php')).read_text()


CASES = {
    'owned-callee-transfers-at-init': {
        'source': source('direct'),
        'stage': 'S.TODO = (CALL_DYNAMIC porigin_site z_init z_call) :: ptask_tail* '
                 '-- if S.RESULT = KNOWN (POBJECT n_receiver)',
        'checks': [
            '$dynamic_site(S, (porigin_site))',
            '$dynamic_fixed_name(S, porigin_site) = eps',
            '$dynamic_cv_name(S, porigin_site) = eps',
            '~$dynamic_this_site(S, porigin_site)',
            '$dynamic_operand_valid(S, porigin_site)',
            '$dynamic_result_valid(S)',
            '~$dynamic_operand_valid(S[.RESULT = VARIABLE ($ptascii("wrong")) 1], porigin_site)',
            '$object_invoke_method(S, n_receiver) = (pmethoddesc)',
            'pmethoddesc.NAME = $ptascii("__invoke")',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1',
            *VALID, *ONE,
            'S_one.RESULT = KNOWN PNULL',
            'S_one.TODO = (UNPACK_ARGS punpackcall) :: ptask_tail*',
            'punpackcall.FUNCTION = METHOD_TARGET n_receiver pmethoddesc.FUNCTION.ORIGIN',
            'punpackcall.CALLSITE = (porigin_site)',
            'punpackcall.LINE = z_call',
            'punpackcall.SENT = {SLOTS eps, NAMED eps}',
            '$target_nodes(punpackcall.FUNCTION) = [HOBJECT n_receiver]',
            '$heap_owners($heap_graph(S_one), HOBJECT n_receiver) = 1',
            '$iterator_unpack_plain(S_one, punpackcall)',
            '$call_task_valid(S_one, UNPACK_ARGS punpackcall)',
            *POST,
        ],
    },
    'returned-callee-inherited-named-warning': {
        'source': source('named'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = METHOD_TARGET n_receiver porigin_method',
        'checks': [
            'piteratorunpack.CALL.CALLSITE = (porigin_site)',
            '$dynamic_cv_name(S, porigin_site) = eps',
            '$unpack_class(S, piteratorunpack.CALL) = (UNPACK_CV)',
            'piteratorunpack.INPUT = VARIABLE ($ptascii("iterator")) 25',
            '$unpack_line(S, piteratorunpack.CALL) = 25',
            '$dynamic_init_line(S, porigin_site) =/= 25',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_called',
            '$class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc)',
            'pmethoddesc.OWNER =/= porigin_called',
            '$target_called_class(S, piteratorunpack.CALL.FUNCTION) = (porigin_called)',
            '$target_lexical_class(S, piteratorunpack.CALL.FUNCTION) = (pmethoddesc.OWNER)',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1',
            'piteratorunpack.KEY = KNOWN pvalue_key',
            '$fiber_traversal_key(pvalue_key) = (KSTRING ($ptascii("right")))',
            '$iterator_unpack_named_target(S, piteratorunpack) = NAMED_POSITION 1',
            '$iterator_unpack_warning_message(S, piteratorunpack) = '
            '$ptascii("Cannot pass by-reference argument 2 of ComputedNamedBase123::__invoke() '
            'by unpacking a Traversable, passing by-value instead")',
            '$iterator_unpack_result_valid(S, piteratorunpack, "send")',
            *VALID, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.LINE = 25',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_warned "byref"',
            'piteratorunpack_warned.CALL.FUNCTION = piteratorunpack.CALL.FUNCTION',
            *POST,
        ],
    },
    'conditional-callee-survives-source-clear': {
        'source': source('conditional'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "key") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = METHOD_TARGET n_receiver porigin_method',
        'checks': [
            'piteratorunpack.CALL.CALLSITE = (porigin_site)',
            '$dynamic_cv_name(S, porigin_site) = eps',
            '$lookup(S.ENV, $ptascii("old")) = (n_source)',
            'S.STORE[n_source] = DEFINED PNULL',
            'n_data = piteratorunpack.OBJECT',
            'n_data =/= n_receiver',
            'piteratorunpack.INPUT = KNOWN (POBJECT n_data)',
            '$iterator_unpack_nodes(piteratorunpack) = [HOBJECT n_data, HOBJECT n_data]',
            '$task_nodes(ITERATOR_UNPACK piteratorunpack "key") = '
            '[HOBJECT n_data, HOBJECT n_data, HOBJECT n_receiver]',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1',
            '$iterator_unpack_result_valid(S, piteratorunpack, "key")',
            '~$iterator_unpack_plain(S, piteratorunpack.CALL[.CALLSITE = eps])',
            *VALID, *ONE,
            'S_one.TODO = (ITERATOR_UNPACK piteratorunpack_send "send") :: ptask_tail*',
            'piteratorunpack_send.CALL.FUNCTION = piteratorunpack.CALL.FUNCTION',
            'piteratorunpack_send.KEY = KNOWN (PINT 0)',
            *POST,
        ],
    },
    'computed-callee-retired-abrupt-receipt': {
        'source': source('invalid'),
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "error" '
                 '-- if piteratorunpack.CALL.FUNCTION = METHOD_TARGET n_receiver porigin_method '
                 '-- if ~((HOBJECT n_receiver) <- S.ALLOCATIONS)',
        'checks': [
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            'piteratorunpack.CALL.CALLSITE = (porigin_site)',
            '$dynamic_cv_name(S, porigin_site) = eps',
            'piteratorunpack.INPUT = KNOWN (POBJECT piteratorunpack.OBJECT)',
            '~((HOBJECT piteratorunpack.OBJECT) <- S.ALLOCATIONS)',
            'piteratorunpack.CURRENT = KNOWN (POBJECT n_current)',
            '~((HOBJECT n_current) <- S.ALLOCATIONS)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
            '$effective_method(S, porigin_class, $ptascii("__destruct"), '
            '|S.CLASSES|) = (pmethoddesc_destructor)',
            'pmethoddesc_destructor.FUNCTION.ORIGIN = porigin_destruct',
            'porigin_destruct =/= porigin_method',
            'S_scope = S[.CURRENT = pdestructionoperation.CALLER]'
            '[.ORIGIN = pdestructionoperation.ORIGIN]'
            '[.CONSTCONTEXT = pdestructionoperation.CONSTCONTEXT]',
            '~$iterator_unpack_plain(S_scope, piteratorunpack.CALL)',
            '$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL)',
            '$iterator_unpack_abort_input(S_scope, piteratorunpack)',
            '~$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL[.CALLSITE = eps])',
            '~$iterator_unpack_abort_plain(S_scope, piteratorunpack.CALL[.FUNCTION = '
            'METHOD_TARGET n_receiver porigin_destruct])',
            '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 0',
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
