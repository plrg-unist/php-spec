#!/usr/bin/env python3
"""Independent reached ordinary/magic Aggregate leaf and final-tail checks."""
import argparse
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
ONE = ['S_zero = $drive_steps(S, 0)', 'S_zero.COMPLETION = BUDGET',
       'S_zero.TODO = S.TODO', 'S_budget = $drive_steps(S, 1)',
       'S_budget.COMPLETION = BUDGET',
       '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_budget',
       'S_one = S_budget[.COMPLETION = NORMAL]']
POST = ['$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))']


def source(name):
    return (HERE / ('aggregate_call_unpack_' + name + '.php')).read_text()


CASES = {
    'ordinary-leaf-keeps-rebound-receiver-and-nonowning-receipt': {
        'source': source('review_ordinary'),
        'stage': 'S.TODO = (ITERATOR_UNPACK piteratorunpack "send") :: '
                 '(UNPACK_AGGREGATE pcallaggregate "leaf") :: ptask_tail* '
                 '-- if piteratorunpack.CALL.FUNCTION = METHOD_TARGET n_receiver porigin_take '
                 '-- if piteratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
        'checks': [
            'pcallaggregate.INPUT = VARIABLE ($ptascii("aggregate")) z',
            'piteratorunpack.INPUT = pcallaggregate.INPUT',
            'piteratorunpack.OBJECT = pcallaggregate.OBJECT',
            'pcallaggregate.ACQUIRED = eps',
            'pcallaggregate.OBJECT =/= pcallaggregate.AGGREGATE',
            '$lookup(S.ENV, $ptascii("aggregate")) = (n_aggregate_cv)',
            'S.STORE[n_aggregate_cv] = DEFINED PNULL',
            '$lookup(S.ENV, $ptascii("receiver")) = (n_receiver_cv)',
            'S.STORE[n_receiver_cv] = DEFINED PNULL',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS',
            '$call_aggregate_history(S, pcallaggregate)',
            '$call_aggregate_receipt(S, piteratorunpack.CALL, piteratorunpack.INPUT, piteratorunpack.OBJECT, S.TODO)',
            '$call_aggregate_iterator_input(S, piteratorunpack)',
            '$iterator_unpack_valid(S, piteratorunpack, "send")',
            '$call_task_valid(S, UNPACK_AGGREGATE pcallaggregate "leaf")',
            '$task_nodes(UNPACK_AGGREGATE pcallaggregate "leaf") = eps',
            '~$call_aggregate_receipt(S, piteratorunpack.CALL, piteratorunpack.INPUT, |S.OBJECTS|, S.TODO)',
            '~$call_task_valid(S, UNPACK_AGGREGATE pcallaggregate[.CALL = pcallaggregate.CALL[.CALLSITE = eps]] "leaf")',
            *VALID, *ONE,
            'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: '
            '(ITERATOR_UNPACK piteratorunpack_next "next-start") :: '
            '(UNPACK_AGGREGATE pcallaggregate "leaf") :: ptask_tail*',
            'pdestructionrelease <- S_one.DESTRUCTION.RELEASES',
            'piteratorunpack_next.CALL.SENT.SLOTS = [NAMED_SENT (KNOWN pvalue_left)]',
            'piteratorunpack_next.CALL.SENT.NAMED = eps',
            '$call_aggregate_iterator_input(S_one, piteratorunpack_next)',
            '$iterator_unpack_valid(S_one, piteratorunpack_next, "next-start")',
            *POST,
        ],
    },
    'magic-generator-leaf-keeps-invalid-key-and-saved-target': {
        'source': source('review_magic'),
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "ready") :: '
                 '(UNPACK_AGGREGATE pcallaggregate "leaf") :: ptask_tail* '
                 '-- if pgeneratorunpack.CALL.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall '
                 '-- if pgeneratorunpack.COUNT = 2',
        'checks': [
            'pgeneratorunpack.NAMED',
            'pcallaggregate.INPUT = KNOWN (POBJECT pcallaggregate.AGGREGATE)',
            'pgeneratorunpack.INPUT = pcallaggregate.INPUT',
            'pgeneratorunpack.OBJECT = pcallaggregate.OBJECT',
            'pcallaggregate.OBJECT =/= pcallaggregate.AGGREGATE',
            '$generator_object(S, pgeneratorunpack.OBJECT)',
            '$fiber_traversal_key($generator_cached_value(S, pgeneratorunpack.OBJECT, true)) = eps',
            '$target_function(S, pgeneratorunpack.CALL.FUNCTION) = eps',
            '$call_aggregate_history(S, pcallaggregate)',
            '$call_aggregate_generator_input(S, pgeneratorunpack)',
            '$generator_unpack_valid(S, pgeneratorunpack, "ready")',
            '$call_aggregate_magic_suffix(GENERATOR_UNPACK pgeneratorunpack "ready", '
            '(UNPACK_AGGREGATE pcallaggregate "leaf") :: ptask_tail*, pgeneratorunpack.CALL.FUNCTION)',
            '$magic_unpack_raw_valid(S, pgeneratorunpack.CALL.FUNCTION)',
            '$call_task_valid(S, UNPACK_AGGREGATE pcallaggregate "leaf")',
            '$task_nodes(UNPACK_AGGREGATE pcallaggregate "leaf") = eps',
            '~$call_aggregate_generator_input(S, pgeneratorunpack[.OBJECT = |S.OBJECTS|])',
            '~$call_aggregate_magic_suffix(GENERATOR_UNPACK pgeneratorunpack "ready", '
            '(UNPACK_AGGREGATE pcallaggregate[.CALL = pcallaggregate.CALL[.CALLSITE = eps]] "leaf") :: ptask_tail*, '
            'pgeneratorunpack.CALL.FUNCTION)',
            *VALID,
        ],
    },
    'both-empty-leaves-consumed-before-magic-handler-entry': {
        'source': source('empty'),
        'stage': 'S.TODO = (UNPACK_ARGS punpackcall) :: ptask_tail* '
                 '-- if punpackcall.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall '
                 '-- if punpackcall.INDEX = 2 -- if punpackcall.ARGUMENTS = eps',
        'checks': [
            'punpackcall.SENT = {SLOTS eps, NAMED eps}',
            'ptask_tail* = METHOD_RESULT :: $magic_unpack_tail(punpackcall.FUNCTION)',
            '~$call_aggregate_marker(punpackcall, S.TODO)',
            '$magic_unpack_raw_valid(S, punpackcall.FUNCTION)',
            '$unpack_before_valid(S, punpackcall, 0)',
            *VALID, *ONE,
            'S_one.TODO = (CALL_ARGS pcalltarget_final eps 2 poperand_pair* porigin_site? z) :: '
            '(MAGIC_UNPACK_RESULT pcalltarget_final) :: ptask_tail*',
            'pcalltarget_final = MAGIC_UNPACK_TARGET punpackcall.FUNCTION n_arguments eps punpackcall.SENT',
            '$magic_unpack_pending(S_one, pcalltarget_final)',
            *POST,
        ],
    },
    'magic-invalid-key-retired-source-keeps-aggregate-history': {
        'source': source('review_magic'),
        'stage': 'S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail* '
                 '-- if pdestructionoperation.SOURCE = UNPACK_AGGREGATE_SOURCE pcallaggregate '
                 '(GENERATOR_UNPACK pgeneratorunpack "ready") '
                 '-- if pgeneratorunpack.CALL.FUNCTION = MAGIC_METHOD_SEND_TARGET pmagicmethodcall',
        'checks': [
            'pdestructionoperation <- S.DESTRUCTION.OPERATIONS',
            'pdestructionoperation.PENDING = (n_error)',
            '$throwable_live(S, n_error)',
            'pcallaggregate.INPUT = KNOWN (POBJECT pcallaggregate.AGGREGATE)',
            'pgeneratorunpack.INPUT = pcallaggregate.INPUT',
            'pgeneratorunpack.OBJECT = pcallaggregate.OBJECT',
            '$call_aggregate_history(S, pcallaggregate)',
            '~((HOBJECT pcallaggregate.AGGREGATE) <- S.ALLOCATIONS)',
            '~((HOBJECT pgeneratorunpack.OBJECT) <- S.ALLOCATIONS)',
            '~((HOBJECT pmagicmethodcall.OBJECT) <- S.ALLOCATIONS)',
            '$call_aggregate_source_task(GENERATOR_UNPACK pgeneratorunpack "ready", pcallaggregate)',
            '$call_aggregate_leaf_saved(pcallaggregate, S.DESTRUCTION.OPERATIONS)',
            '$eager_operation_source_valid(S, pdestructionoperation)',
            '~$eager_operation_source_valid(S, pdestructionoperation[.SOURCE = '
            'UNPACK_AGGREGATE_SOURCE pcallaggregate[.CALL = pcallaggregate.CALL[.LINE = 0]] '
            '(GENERATOR_UNPACK pgeneratorunpack "ready")])',
            *VALID, *ONE, *POST,
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
