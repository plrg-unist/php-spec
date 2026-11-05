#!/usr/bin/env python3
"""Reach strict Iterator option rejection with raw TraceArgs owners."""
import argparse
import json
from functools import partial
from pathlib import Path

import generator_call_unpack_state as base

CATALOG = Path(__file__).with_name('config_iterator_stringable_strict_cases.json')
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOG.read_bytes())}


def case(source, owned):
    checks = [
        'S.ORIGIN = (pconfigiterator.CALL.SITE)',
        '$config_iterator_valid(S, pconfigiterator, "ready")',
        'pconfigiterator.CALL.KIND = INTRINSIC_INI_SET',
        'pconfigiterator.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_name)), '
        'ENTRY (KINT 1) (DIRECT (PARRAY n_array))]',
        '$config_pack_prefix(pconfigiterator.CALL, pconfigiterator.ITEMS, false) = (pconfigcall)',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_name)), '
        'NAMED_SENT (KNOWN (PARRAY n_array))]',
        '$config_iterator_copied_call(S, pconfigcall[.INDEX = 1])',
        '$config_strict(S, pconfigcall)',
        'S.ITERATORS = eps', 'S.PRECISIONINI = $ptascii("14")',
        '(HOBJECT n_name) <- S.ALLOCATIONS', '(HARRAY n_array) <- S.ALLOCATIONS',
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 3)), '
        'ENTRY (KINT 1) (ALIAS n_leaf)]',
        '$lookup(S.ENV, $ptascii("leaf")) = (n_leaf)',
        'S.STORE[n_leaf] = DEFINED (PINT 17)',
        '$lookup(S.ENV, $ptascii("row")) = (n_row_cell)',
        'S.STORE[n_row_cell] = DEFINED (PARRAY n_source)',
        'n_source =/= n_array',
        'S.ARRAYS[n_source].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 31)), '
        'ENTRY (KINT 1) (ALIAS n_leaf)]',
        '$($heap_owners($heap_graph(S), HOBJECT n_name) > 0)',
        '$($heap_owners($heap_graph(S), HARRAY n_array) > 0)',
    ]
    if owned:
        checks += [
            'pconfigcall.OWNER = (n_owner)',
            'S.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET',
            '$lookup(S.ENV, $ptascii("keep")) = (n_keep_cell)',
            'S.STORE[n_keep_cell] = DEFINED (POBJECT n_owner)',
            '$lookup(S.ENV, $ptascii("call")) = (n_call_cell)',
            'S.STORE[n_call_cell] = DEFINED (POBJECT n_getter)',
            'n_getter =/= n_owner',
            'S.OBJECTS[n_getter] = INTRINSICCLOSURE INTRINSIC_INI_GET',
        ]
    else:
        checks += ['pconfigcall.OWNER = eps']
    checks += [
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S',
        'PhpStep: S ~> S_invoke',
        'S_invoke.TODO = (CONFIG_INVOKE pconfigcall[.INDEX = 1]) :: ptask_tail*',
        'S_invoke.COMPLETION = NORMAL',
        '$config_iterator_copied_call(S_invoke, pconfigcall[.INDEX = 1])',
        'PhpStep: S_invoke ~> S_error',
        'S_error.COMPLETION = THROWING n_error',
        '$throwable_field(S_error, n_error, "trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error, n_frame, $ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_name)), '
        'ENTRY (KINT 1) (DIRECT (PARRAY n_array))]',
        '$($heap_owners($heap_graph(S_error), HOBJECT n_name) > 0)',
        '$($heap_owners($heap_graph(S_error), HARRAY n_array) > 0)',
        'S_done = $drive(S, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps', 'S_done.ITERATORS = eps',
        'S_done.PRECISIONINI = $ptascii("14")',
        '$heap_owners($heap_graph(S_done), HOBJECT n_name) = 0',
        '$heap_owners($heap_graph(S_done), HARRAY n_array) = 0',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return {'source': SOURCES[source],
            'stage': 'S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask_tail*',
            'checks': checks}


CASES = {
    'strict-direct-raw-option-and-array-trace': case(
        'strict-direct-option-rejects-after-iterator-cleanup', False),
    'strict-selected-owner-survives-cv-rebinding': case(
        'strict-selected-setter-survives-rebinding-before-option-error', True),
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    base.CASES = CASES
    base.INPUTS = [Path(__file__), CATALOG, Path(base.__file__)]
    base.review.run = partial(base.review.run, process_seconds=300)
    raise SystemExit(0 if base.run(parser.parse_args().case) else 1)
