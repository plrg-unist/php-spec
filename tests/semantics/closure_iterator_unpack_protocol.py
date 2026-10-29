#!/usr/bin/env python3
"""Reached Closure target, argument, warning, and boundary checks."""
import argparse
from pathlib import Path
import fiber_state_review as review


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']


def source(name):
    return (HERE / ('closure_iterator_unpack_' + name + '.php')).read_text()


CASES = {
    'real-selected-before-iterator': {
        'source': source('real_selected'),
        'stage': 'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail* '
                 '-- if punpackcall.FUNCTION = CLOSURE_TARGET n',
        'checks': [
            'S.OBJECTS[n] = REALCLOSURE porigin pitem* pstaticcell*',
            '$iterator_unpack_closure_origin(S, n) = (porigin)',
            '$unpack_class(S, punpackcall) = (UNPACK_CV)',
            'punpackcall.CALLSITE = (porigin_site)',
            '$dynamic_site(S, (porigin_site))',
            '$dynamic_fixed_name(S, porigin_site) = eps',
            '$call_selected_valid(S, punpackcall.FUNCTION, punpackcall.CALLSITE)',
            '$iterator_unpack_plain(S, punpackcall)',
            '$target_nodes(punpackcall.FUNCTION) = [HOBJECT n]',
            '~$iterator_unpack_plain(S[.OBJECTS = $object_set(S.OBJECTS, n, STDINSTANCE)], punpackcall)',
            '~$iterator_unpack_plain(S, punpackcall[.CALLSITE = eps])',
            *VALID, *ONE,
            'S_one.TODO = (ITERATOR_UNPACK piteratorunpack "rewind-start") :: ptask_tail*',
            'piteratorunpack.CALL = punpackcall',
            'piteratorunpack.CLOSUREORIGIN = (porigin)',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'real-selected-after-key-rebind': {
        'source': source('real_selected'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "key") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = CLOSURE_TARGET n_old',
        'checks': [
            '$lookup(S.ENV, $ptascii("callback")) = (n_callback)',
            'S.STORE[n_callback] = DEFINED (POBJECT n_new)',
            'n_new =/= n_old',
            '$target_nodes(piteratorunpack.CALL.FUNCTION) = [HOBJECT n_old]',
            'piteratorunpack.CLOSUREORIGIN = $iterator_unpack_closure_origin(S, n_old)',
            '$iterator_unpack_result_valid(S, piteratorunpack, "key")',
            *VALID, *ONE,
            'S_one.TODO = (ITERATOR_UNPACK piteratorunpack_send "send") :: ptask_tail*',
            'piteratorunpack_send.CALL.FUNCTION = piteratorunpack.CALL.FUNCTION',
            'piteratorunpack_send.KEY = KNOWN (PINT 0)',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'named-firstclass-target': {
        'source': source('named_firstclass'),
        'stage': 'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail* '
                 '-- if punpackcall.FUNCTION = CLOSURE_TARGET n',
        'checks': [
            'S.OBJECTS[n] = NAMEDCLOSURE porigin',
            '$iterator_unpack_closure_origin(S, n) = (porigin)',
            '$target_function(S, punpackcall.FUNCTION) = (pfunction)',
            'pfunction.ORIGIN = porigin',
            '$iterator_unpack_plain(S, punpackcall)',
            *VALID, *ONE,
            'S_one.TODO = (ITERATOR_UNPACK piteratorunpack "rewind-start") :: ptask_tail*',
            'piteratorunpack.CLOSUREORIGIN = (porigin)',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'arrow-target': {
        'source': source('arrow'),
        'stage': 'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail* '
                 '-- if punpackcall.FUNCTION = CLOSURE_TARGET n',
        'checks': [
            'S.OBJECTS[n] = REALCLOSURE porigin pitem* pstaticcell*',
            '$origin_node(S.SOURCES, porigin) = '
            '(NExprArrowFunction phpType14 phpType4_static phpType4_ref '
            'phpType16 phpType18 expression metadata)',
            '$iterator_unpack_plain(S, punpackcall)',
            *VALID, *ONE,
            'S_one.TODO = (ITERATOR_UNPACK piteratorunpack "rewind-start") :: ptask_tail*',
            'piteratorunpack.CLOSUREORIGIN = (porigin)',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'named-reference-warning': {
        'source': source('named_reference'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = CLOSURE_TARGET n',
        'checks': [
            'S.OBJECTS[n] = NAMEDCLOSURE porigin',
            '$target_lexical_class(S, piteratorunpack.CALL.FUNCTION) = eps',
            '$iterator_unpack_warning_target(S, piteratorunpack.CALL.FUNCTION) = '
            '$ptascii("reference120")',
            '$iterator_unpack_warning_message(S, piteratorunpack) = '
            '$ptascii("Cannot pass by-reference argument 1 of reference120() '
            'by unpacking a Traversable, passing by-value instead")',
            *VALID, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_warned "byref"',
            'perrorcall.LINE = $unpack_line(S, piteratorunpack.CALL)',
            '$call_task_valid(S_one, ERROR_HANDLER_INVOKE perrorcall)',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'scoped-reference-warning': {
        'source': source('scoped_reference'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = CLOSURE_TARGET n',
        'checks': [
            'S.OBJECTS[n] = REALCLOSURE porigin pitem* pstaticcell*',
            '$iterator_unpack_closure_origin(S, n) = (porigin)',
            '$target_lexical_class(S, piteratorunpack.CALL.FUNCTION) = (porigin_class)',
            '$class_at(S.CLASSES, porigin_class) = (pclassdesc)',
            'pclassdesc.NAME = $ptascii("Scoped120")',
            '$iterator_unpack_warning_target(S, piteratorunpack.CALL.FUNCTION) = '
            '$ptascii("Scoped120::{closure:Scoped120::make():5}")',
            '$iterator_unpack_warning_message(S, piteratorunpack) = '
            '$ptascii("Cannot pass by-reference argument 1 of '
            'Scoped120::{closure:Scoped120::make():5}() by unpacking a Traversable, '
            'passing by-value instead")',
            *VALID, *ONE,
            'S_one.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
            'perrorcall.RESUME = ITERATOR_UNPACK piteratorunpack_warned "byref"',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
        ],
    },
    'invalid-key-before-discard': {
        'source': source('invalid_key'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = CLOSURE_TARGET n',
        'checks': [
            'piteratorunpack.KEY = KNOWN (PBOOL false)',
            '$iterator_unpack_result_valid(S, piteratorunpack, "send")',
            *VALID,
            'S_error = $iterator_unpack_send(S, piteratorunpack, ptask_tail*)',
            'S_error.COMPLETION = THROWN "Error" '
            '($ptascii("Keys must be of type int|string during argument unpacking")) '
            '$unpack_line(S, piteratorunpack.CALL)',
            '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
        ],
    },
    'array-wrapper-excluded': {
        'source': source('array_wrapper_boundary'),
        'stage': 'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail* '
                 '-- if punpackcall.FUNCTION = CLOSURE_TARGET n',
        'checks': [
            'S.OBJECTS[n] = ARRAYMETHODCLOSURE pcalltarget parrayselection pmethodcapture?',
            '$iterator_unpack_closure_origin(S, n) = eps',
            '~$iterator_unpack_plain(S, punpackcall)',
            *VALID,
            'S_one = $drive_steps(S, 1)',
            'S_one.COMPLETION = UNSUPPORTED "Iterator unpack target or operand ownership"',
        ],
    },
    'bindto-clone-excluded': {
        'source': source('bound_boundary'),
        'stage': 'S.TODO = (UNPACK_PREP punpackcall) :: ptask_tail* '
                 '-- if punpackcall.FUNCTION = CLOSURE_TARGET n',
        'checks': [
            'S.OBJECTS[n] = INTERNALSCOPECLOSURE pinternalclosurescope '
            '(REALCLOSURE porigin pitem* pstaticcell*)',
            '$internal_closure_row(S, n) = (pinternalclosurescope)',
            'pinternalclosurescope.BOUND',
            '$closure_binding_at(S.CLOSUREBINDINGS, n) = eps',
            '$iterator_unpack_closure_origin(S, n) = eps',
            '~$iterator_unpack_plain(S, punpackcall)',
            *VALID,
            'S_one = $drive_steps(S, 1)',
            'S_one.COMPLETION = UNSUPPORTED "Iterator unpack target or operand ownership"',
        ],
    },
    'retired-closure-cleanup': {
        'source': source('invalid_key'),
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "error" '
                 '-- if piteratorunpack.CALL.FUNCTION = CLOSURE_TARGET n',
        'checks': [
            'piteratorunpack.CALL.FUNCTION = CLOSURE_TARGET n',
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            '~((HOBJECT n) <- S.ALLOCATIONS)',
            'S.OBJECTS[n] = REALCLOSURE porigin pitem* pstaticcell*',
            'piteratorunpack.CLOSUREORIGIN = (porigin)',
            'S_scope = S[.CURRENT = pdestructionoperation.CALLER]'
            '[.ORIGIN = pdestructionoperation.ORIGIN]'
            '[.CONSTCONTEXT = pdestructionoperation.CONSTCONTEXT]',
            '~$iterator_unpack_plain(S_scope, piteratorunpack.CALL)',
            '$iterator_unpack_abort_selected(S_scope, piteratorunpack)',
            '~$iterator_unpack_abort_selected(S_scope, piteratorunpack[.CLOSUREORIGIN = eps])',
            'piteratorunpack.CALL.CALLSITE = (porigin_site)',
            'porigin_site =/= porigin',
            '~$iterator_unpack_abort_selected(S_scope, piteratorunpack[.CLOSUREORIGIN = '
            '(porigin_site)])',
            '~$iterator_unpack_abort_selected(S_scope, piteratorunpack[.CALL = '
            'piteratorunpack.CALL[.CALLSITE = eps]])',
            '~$iterator_unpack_abort_selected(S_scope[.OBJECTS = '
            '$object_set(S_scope.OBJECTS, n, STDINSTANCE)], piteratorunpack)',
            '~$iterator_unpack_abort_selected(S_scope, piteratorunpack[.CALL = '
            'piteratorunpack.CALL[.FUNCTION = CLOSURE_TARGET piteratorunpack.OBJECT]])',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            *VALID,
        ],
    },
    'retired-alias-capture-cleanup': {
        'source': source('reference_capture'),
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack "error" '
                 '-- if piteratorunpack.CALL.FUNCTION = CLOSURE_TARGET n',
        'checks': [
            'S.OBJECTS[n] = REALCLOSURE porigin pitem* pstaticcell*',
            'pitem* = (ALIAS n_cell) :: pitem_tail*',
            '~((HOBJECT n) <- S.ALLOCATIONS)',
            '~((HCELL n_cell) <- S.ALLOCATIONS)',
            'piteratorunpack.CLOSUREORIGIN = (porigin)',
            'S_scope = S[.CURRENT = pdestructionoperation.CALLER]'
            '[.ORIGIN = pdestructionoperation.ORIGIN]'
            '[.CONSTCONTEXT = pdestructionoperation.CONSTCONTEXT]',
            '$iterator_unpack_abort_selected(S_scope, piteratorunpack)',
            '~$call_selected_valid(S_scope[.ALLOCATIONS = '
            '(HOBJECT n) :: S_scope.ALLOCATIONS], '
            'piteratorunpack.CALL.FUNCTION, piteratorunpack.CALL.CALLSITE)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '$destructor_operation_valid(S, pdestructionoperation)',
            *VALID,
        ],
    },
    'invalid-key-discard-probe': {
        'source': source('invalid_key'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = CLOSURE_TARGET n',
        'checks': [
            'S_error = $iterator_unpack_send(S, piteratorunpack, ptask_tail*)',
            'S_error.COMPLETION = THROWN "Error" '
            '($ptascii("Keys must be of type int|string during argument unpacking")) '
            '$unpack_line(S, piteratorunpack.CALL)',
            'S_begin = $throwable_begin(S_error)',
            'S_begin.TODO = (THROW_SEARCH n_error) :: '
            '(ITERATOR_UNPACK piteratorunpack_error "error") :: ptask_tail*',
            'piteratorunpack_error.CLOSUREORIGIN = $iterator_unpack_closure_origin(S_begin, n)',
            'S_unwind = S_begin[.TODO = (THROW_SEARCH n_error) :: ptask_tail*]',
            '$destructor_operational(S_unwind)',
            '$eager_operation_pending(S_unwind) = (n_error)',
            '$iterator_unpack_result_valid(S_unwind[.TODO = (THROW_SEARCH n_error) :: '
            '(ITERATOR_UNPACK piteratorunpack_error "error") :: ptask_tail*], '
            'piteratorunpack_error, "error")',
            'S_discard = $return_discard(S_unwind, '
            'ITERATOR_UNPACK piteratorunpack_error "error")',
            'S_discard.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
            'pdestructionoperation.SOURCE = ITERATOR_UNPACK piteratorunpack_error "error"',
            '(HOBJECT n) <- S_discard.ALLOCATIONS',
            '$closure_binding_at(S_discard.CLOSUREBINDINGS, n) = eps',
            '$eager_operation_source_valid(S_discard, pdestructionoperation)',
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
