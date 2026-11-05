#!/usr/bin/env python3
"""Reach zend.assertions value rejection after Iterator option conversion."""
import argparse
import json
from functools import partial
from pathlib import Path

import generator_call_unpack_state as base

CATALOG = Path(__file__).with_name('config_iterator_assertions_reject_cases.json')
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOG.read_bytes())}


def case(source, value, node):
    checks = [
        'S.ORIGIN = (pconfigcall.SITE)',
        'pconfigcall.KIND = INTRINSIC_INI_SET', 'pconfigcall.OWNER = eps',
        '$string_bytes(pvalue_name) = ($ptascii("zend.assertions"))',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_name)), '
        f'NAMED_SENT (KNOWN ({value} n_value))]',
        '$config_iterator_string_receive_valid(S, pconfigcall, n_name, pvalue_name)',
        '~((HOBJECT n_name) <- S.ALLOCATIONS)', f'({node} n_value) <- S.ALLOCATIONS',
        f'$config_iterator_data_value(S, {value} n_value, eps)',
        f'~$config_ini_quiet_value(S, {value} n_value)',
        f'$config_iterator_string_value(S, {value} n_value)',
        f'$config_ini_value_conversion({value} n_value) = TYPEREJECT',
        '$heap_owners($heap_graph(S), HOBJECT n_name) = 0',
        f'$heap_owners($heap_graph(S), {node} n_value) = 1',
        f'$task_nodes(CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_name pvalue_name) = [{node} n_value]',
        'S.PRECISIONINI = $ptascii("21")', 'S.ITERATORS = eps',
    ]
    if value == 'PARRAY':
        checks += [
            'S.ARRAYS[n_value].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 3)), '
            'ENTRY (KINT 1) (ALIAS n_leaf)]',
            '$lookup(S.ENV, $ptascii("leaf")) = (n_leaf)',
            'S.STORE[n_leaf] = DEFINED (PINT 42)',
            '$lookup(S.ENV, $ptascii("row")) = (n_row_cell)',
            'S.STORE[n_row_cell] = DEFINED (PARRAY n_source)',
            'n_source =/= n_value',
            'S.ARRAYS[n_source].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 31)), '
            'ENTRY (KINT 1) (ALIAS n_leaf)]',
            'S_cycle = S[.ARRAYS[n_value].ITEMS = '
            '[ENTRY (KINT 0) (DIRECT (PARRAY n_value))]]',
            '~$config_iterator_data_value(S_cycle, PARRAY n_value, eps)',
            '~$config_iterator_string_receive_valid(S_cycle, pconfigcall, n_name, pvalue_name)',
        ]
    else:
        checks += ['S.OBJECTS[n_value] = INSTANCE porigin_value',
                   '$stringable_instance(S, n_value)']
    checks += [
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S',
        'PhpStep: S ~> S_error', 'S_error.COMPLETION = THROWING n_error',
        '$throwable_field(S_error, n_error, "trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error, n_frame, $ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option), '
        f'ENTRY (KINT 1) (DIRECT ({value} n_value))]',
        '$string_bytes(pvalue_option) = ($ptascii("zend.assertions"))',
        f'$($heap_owners($heap_graph(S_error), {node} n_value) > 0)',
        'S_done = $drive(S, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps', 'S_done.ITERATORS = eps',
        'S_done.PRECISIONINI = $ptascii("14")',
        f'$heap_owners($heap_graph(S_done), {node} n_value) = 0',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return {'source': SOURCES[source],
            'stage': 'S.TODO = (CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_name pvalue_name) :: ptask_tail*',
            'checks': checks}


CASES = {
    'assertions-copied-array-priority-and-cow-trace': case(
        'assertions-option-rejects-copied-array-before-lookup', 'PARRAY', 'HARRAY'),
    'assertions-copied-object-priority-and-raw-trace': case(
        'assertions-option-rejects-copied-object-without-value-cast', 'POBJECT', 'HOBJECT'),
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    base.CASES = CASES
    base.INPUTS = [Path(__file__), CATALOG, Path(base.__file__)]
    base.review.run = partial(base.review.run, process_seconds=300)
    raise SystemExit(0 if base.run(parser.parse_args().case) else 1)
