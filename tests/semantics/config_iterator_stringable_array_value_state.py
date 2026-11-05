#!/usr/bin/env python3
"""Reach copied COW table and live alias at Stringable INI value TypeError."""
import argparse
import json
from functools import partial
from pathlib import Path

import generator_call_unpack_state as base

CATALOG = Path(__file__).with_name('config_iterator_stringable_array_value_cases.json')
SOURCE = json.loads(CATALOG.read_bytes())[0]['source']
CASES = {
    'copied-array-and-live-alias-enter-type-error-trace': {
        'source': SOURCE,
        'stage': 'S.TODO = (CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_name pvalue_name) :: ptask_tail*',
        'checks': [
            'S.ORIGIN = (pconfigcall.SITE)',
            'pconfigcall.KIND = INTRINSIC_INI_SET',
            'pconfigcall.OWNER = eps',
            '$string_bytes(pvalue_name) = ($ptascii("precision"))',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_name)), '
            'NAMED_SENT (KNOWN (PARRAY n_array))]',
            '$config_iterator_string_receive_valid(S, pconfigcall, n_name, pvalue_name)',
            '~((HOBJECT n_name) <- S.ALLOCATIONS)',
            '(HARRAY n_array) <- S.ALLOCATIONS',
            '$config_iterator_data_value(S, PARRAY n_array, eps)',
            '~$config_ini_quiet_value(S, PARRAY n_array)',
            '$config_iterator_string_value(S, PARRAY n_array)',
            '$config_ini_value_conversion(PARRAY n_array) = TYPEREJECT',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 3)), '
            'ENTRY (KINT 1) (ALIAS n_leaf)]',
            '$lookup(S.ENV, $ptascii("leaf")) = (n_leaf)',
            'S.STORE[n_leaf] = DEFINED (PINT 42)',
            '$lookup(S.ENV, $ptascii("row")) = (n_row_cell)',
            'S.STORE[n_row_cell] = DEFINED (PARRAY n_source)',
            'n_source =/= n_array',
            'S.ARRAYS[n_source].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 31)), '
            'ENTRY (KINT 1) (ALIAS n_leaf)]',
            '$heap_owners($heap_graph(S), HOBJECT n_name) = 0',
            '$heap_owners($heap_graph(S), HARRAY n_array) = 1',
            'S.PRECISIONINI = $ptascii("21")',
            'S.FILEINCLUDEPATH = eps', 'S.ITERATORS = eps',
            '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
            'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero[.COMPLETION = NORMAL] = S',
            'S_cycle = S[.ARRAYS[n_array].ITEMS = '
            '[ENTRY (KINT 0) (DIRECT (PARRAY n_array))]]',
            '~$config_iterator_data_value(S_cycle, PARRAY n_array, eps)',
            '~$config_iterator_string_value(S_cycle, PARRAY n_array)',
            '~$config_iterator_string_receive_valid(S_cycle, pconfigcall, n_name, pvalue_name)',
            'PhpStep: S ~> S_error',
            'S_error.COMPLETION = THROWING n_error',
            '$throwable_field(S_error, n_error, "trace") = PARRAY n_trace',
            'S_error.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_frame))',
            '$trace_array_field(S_error, n_frame, $ptascii("args")) = PARRAY n_args',
            'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option), '
            'ENTRY (KINT 1) (DIRECT (PARRAY n_array))]',
            '$string_bytes(pvalue_option) = ($ptascii("precision"))',
            '$($heap_owners($heap_graph(S_error), HARRAY n_array) > 0)',
            'S_done = $drive(S, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.TODO = eps', 'S_done.ITERATORS = eps',
            'S_done.PRECISIONINI = $ptascii("14")',
            '$heap_owners($heap_graph(S_done), HARRAY n_array) = 0',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    base.CASES = CASES
    base.INPUTS = [Path(__file__), CATALOG, Path(base.__file__)]
    base.review.run = partial(base.review.run, process_seconds=300)
    raise SystemExit(0 if base.run(parser.parse_args().case) else 1)
