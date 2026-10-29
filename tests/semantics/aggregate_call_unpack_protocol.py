#!/usr/bin/env python3
"""Source-reached Aggregate getter, chain and raw operand ownership checks."""
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
    'getter-borrows-input-and-retains-selected-call': {
        'source': source('getter_throw'),
        'stage': 'S.TODO = (CALL_ARGS pcalltarget eps 0 eps porigin? z) :: '
                 '(UNPACK_AGGREGATE pcallaggregate "getIterator") :: ptask_tail*',
        'checks': [
            'pcallaggregate.INPUT = KNOWN (POBJECT pcallaggregate.AGGREGATE)',
            'pcallaggregate.OBJECT = pcallaggregate.AGGREGATE',
            'pcallaggregate.ACQUIRED = eps',
            'pcallaggregate.CURRENT = KNOWN PNULL',
            'pcalltarget = AGGREGATE_METHOD_TARGET pcallaggregate.OBJECT porigin_method',
            '$target_function(S, pcalltarget) = (pfunction)',
            'pfunction.ORIGIN = porigin_method',
            '$target_nodes(pcalltarget) = eps',
            '$task_nodes(CALL_ARGS pcalltarget eps 0 eps porigin? z) = eps',
            '$heap_count(HOBJECT pcallaggregate.AGGREGATE, $task_nodes(UNPACK_AGGREGATE pcallaggregate "getIterator")) = 1',
            'pcallaggregate.CALL.FUNCTION = METHOD_TARGET n_receiver porigin_take',
            '$heap_count(HOBJECT n_receiver, $task_nodes(UNPACK_AGGREGATE pcallaggregate "getIterator")) = 1',
            '$call_aggregate_valid(S, pcallaggregate, "getIterator")',
            '$call_aggregate_target(S, pcallaggregate, pcalltarget)',
            '~$call_aggregate_target(S, pcallaggregate, AGGREGATE_METHOD_TARGET n_receiver porigin_method)',
            '~$call_aggregate_valid(S, pcallaggregate[.CALL = pcallaggregate.CALL[.CALLSITE = eps]], "getIterator")',
            '~$call_aggregate_valid(S, pcallaggregate[.CURRENT = KNOWN (PINT 1)], "getIterator")',
            *VALID, *ONE, *POST,
        ],
    },
    'returned-reference-input-and-generator-data-are-distinct': {
        'source': source('reference_closure'),
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "rewind") :: '
                 '(UNPACK_AGGREGATE pcallaggregate "leaf") :: ptask_tail*',
        'checks': [
            'pcallaggregate.INPUT = REFERENCE n_input',
            'pgeneratorunpack.INPUT = REFERENCE n_input',
            '$lookup(S.ENV, $ptascii("aggregate")) = (n_input)',
            'n_input <- S.REFCELLS',
            'S.STORE[n_input] = DEFINED (POBJECT pcallaggregate.AGGREGATE)',
            'pgeneratorunpack.OBJECT = pcallaggregate.OBJECT',
            'pcallaggregate.OBJECT =/= pcallaggregate.AGGREGATE',
            '$task_nodes(UNPACK_AGGREGATE pcallaggregate "leaf") = eps',
            '$heap_count(HCELL n_input, $task_nodes(GENERATOR_UNPACK pgeneratorunpack "rewind")) = 1',
            '$heap_count(HOBJECT pcallaggregate.OBJECT, $task_nodes(GENERATOR_UNPACK pgeneratorunpack "rewind")) = 1',
            '$heap_count(HOBJECT pcallaggregate.AGGREGATE, $task_nodes(GENERATOR_UNPACK pgeneratorunpack "rewind")) = 0',
            '$generator_unpack_valid(S, pgeneratorunpack, "rewind")',
            '$call_aggregate_generator_input(S, pgeneratorunpack)',
            '~$generator_unpack_valid(S, pgeneratorunpack[.INPUT = KNOWN (POBJECT pcallaggregate.OBJECT)], "rewind")',
            '~$generator_unpack_valid(S, pgeneratorunpack[.CALL = pgeneratorunpack.CALL[.LINE = 0]], "rewind")',
            *VALID, *ONE, *POST,
        ],
    },
    'nested-return-layer-retires-before-leaf-rewind': {
        'source': source('nested_generator'),
        'stage': 'S.TODO = (UNPACK_AGGREGATE pcallaggregate "ready") :: ptask_tail*',
        'checks': [
            'pcallaggregate.ACQUIRED = [n_inner]',
            'n_inner =/= pcallaggregate.AGGREGATE',
            'n_inner =/= pcallaggregate.OBJECT',
            '~((HOBJECT n_inner) <- S.ALLOCATIONS)',
            '(HOBJECT pcallaggregate.AGGREGATE) <- S.ALLOCATIONS',
            '(HOBJECT pcallaggregate.OBJECT) <- S.ALLOCATIONS',
            '$call_aggregate_history(S, pcallaggregate)',
            '$call_aggregate_valid(S, pcallaggregate, "ready")',
            '$heap_count(HOBJECT n_inner, $task_nodes(UNPACK_AGGREGATE pcallaggregate "ready")) = 0',
            '$heap_count(HOBJECT pcallaggregate.AGGREGATE, $task_nodes(UNPACK_AGGREGATE pcallaggregate "ready")) = 1',
            '$heap_count(HOBJECT pcallaggregate.OBJECT, $task_nodes(UNPACK_AGGREGATE pcallaggregate "ready")) = 1',
            '~$call_aggregate_history(S, pcallaggregate[.ACQUIRED = [pcallaggregate.OBJECT]])',
            '~$call_aggregate_valid(S, pcallaggregate[.OBJECT = n_inner], "ready")',
            *VALID, *ONE,
            'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack "rewind") :: (UNPACK_AGGREGATE pcallaggregate "leaf") :: ptask_tail*',
            'pgeneratorunpack.OBJECT = pcallaggregate.OBJECT',
            'pgeneratorunpack.INPUT = pcallaggregate.INPUT',
            '$task_nodes(UNPACK_AGGREGATE pcallaggregate "leaf") = eps',
            '$generator_unpack_valid(S_one, pgeneratorunpack, "rewind")',
            *POST,
        ],
    },
    'live-original-cv-controls-first-self-comparison': {
        'source': source('self_rebound'),
        'stage': 'S.TODO = (UNPACK_AGGREGATE pcallaggregate "getIterator") :: ptask_tail* '
                 '-- if pcallaggregate.ACQUIRED = eps '
                 '-- if S.RESULT = KNOWN (POBJECT pcallaggregate.AGGREGATE)',
        'checks': [
            'pcallaggregate.INPUT = VARIABLE ($ptascii("aggregate")) z',
            '$lookup(S.ENV, $ptascii("aggregate")) = (n_input)',
            'S.STORE[n_input] = DEFINED (POBJECT n_other)',
            'n_other =/= pcallaggregate.AGGREGATE',
            '$call_aggregate_self(S, pcallaggregate) = (n_other)',
            '$call_aggregate_self(S[.STORE[n_input] = DEFINED (POBJECT pcallaggregate.AGGREGATE)], pcallaggregate) = (pcallaggregate.AGGREGATE)',
            '$call_aggregate_valid(S, pcallaggregate, "getIterator")',
            '$call_aggregate_acquire(S[.STORE[n_input] = DEFINED (POBJECT pcallaggregate.AGGREGATE)], pcallaggregate, ptask_tail*).COMPLETION = THROWN "Exception" ptbytes z_error',
            *VALID, *ONE,
            'S_one.TODO = (CALL_ARGS (AGGREGATE_METHOD_TARGET pcallaggregate.AGGREGATE porigin_method) eps 0 eps porigin? z_call) :: (UNPACK_AGGREGATE pcallaggregate_next "getIterator") :: ptask_tail*',
            'pcallaggregate_next.ACQUIRED = [pcallaggregate.AGGREGATE]',
            'pcallaggregate_next.OBJECT = pcallaggregate.AGGREGATE',
            '$call_aggregate_acquisition(S_one, pcallaggregate_next)',
            '$heap_count(HOBJECT pcallaggregate.AGGREGATE, $task_nodes(UNPACK_AGGREGATE pcallaggregate_next "getIterator")) = 1',
            *POST,
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
