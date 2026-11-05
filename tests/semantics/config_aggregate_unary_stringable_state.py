#!/usr/bin/env python3
"""Reach Aggregate promotion and unary copied-option reception."""
import argparse
import json
from functools import partial
from pathlib import Path

import generator_call_unpack_state as base

CATALOG = Path(__file__).with_name('config_aggregate_unary_stringable_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOG.read_bytes())}

GET = 'aggregate-get-reads-after-fresh-iterator-disposal'
RESTORE = 'aggregate-selected-restore-keeps-original-owner'

CASES = {
    'aggregate-get-promotes-fresh-unary-data': {
        'source': ROWS[GET]['source'],
        'stage': 'S.TODO = (CONFIG_AGGREGATE pconfigaggregate) :: ptask_tail* '
                 '-- if S.RESULT = KNOWN (POBJECT n_data)',
        'checks': [
            'pconfigaggregate.CALL.KIND = INTRINSIC_INI_GET',
            'pconfigaggregate.CALL.INDEX = 0',
            'pconfigaggregate.CALL.SENT = eps',
            'pconfigaggregate.INPUT = VARIABLE $ptascii("aggregate") z_input',
            'pconfigaggregate.OBJECT = n_aggregate',
            '$config_aggregate_source(S, pconfigaggregate)',
            '$config_aggregate_valid(S, pconfigaggregate)',
            '$config_aggregate_method(S, n_aggregate) = (pmethoddesc)',
            '$config_aggregate_owners(S, pconfigaggregate, 1)',
            'S.OBJECTS[n_data] = INSTANCE porigin_class',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 1',
            '$config_iterator_finalizer(S, n_data)',
            '$config_aggregate_return_allowed(S, pconfigaggregate)',
            'S.PRECISIONINI = $ptascii("7")',
            'S.ITERATORS = eps',
            '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
            'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero[.COMPLETION = NORMAL] = S',
            'PhpStep: S ~> S_data',
            'S_data.TODO = (CONFIG_ITERATOR pconfigiterator "rewind-start") :: ptask_tail*',
            'pconfigiterator.CALL = pconfigaggregate.CALL',
            'pconfigiterator.OBJECT = n_data',
            'pconfigiterator.PRODUCER = (n_aggregate)',
            'pconfigiterator.INPUT = pconfigaggregate.INPUT',
            'pconfigiterator.ITEMS = eps',
            '$config_iterator_producer_valid(S_data, pconfigiterator)',
            '$config_iterator_valid(S_data, pconfigiterator, "rewind-start")',
            'S_data.EVENTS = S.EVENTS',
            'S_data.PRECISIONINI = S.PRECISIONINI',
            '$call_descriptors_valid(S_data)', '$heap_valid($heap_graph(S_data))',
            'S_done = $drive(S_data, 4000)',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
            'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
            'S_done.ITERATORS = eps',
            'S_done.PRECISIONINI = $ptascii("14")',
            '$test_outputs(S_done.EVENTS) = $ptascii("' + ROWS[GET]['native_stdout'] + '")',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
    'aggregate-selected-restore-receipt-keeps-owner': {
        'source': ROWS[RESTORE]['source'],
        'stage': 'S.TODO = (CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_name pvalue_name) :: ptask_tail*',
        'checks': [
            'S.ORIGIN = (pconfigcall.SITE)',
            'pconfigcall.KIND = INTRINSIC_INI_RESTORE',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_name))]',
            '$string_bytes(pvalue_name) = ($ptascii("precision"))',
            '$config_iterator_string_receive_valid(S, pconfigcall, n_name, pvalue_name)',
            '$config_iterator_copied_header(S, pconfigcall[.SENT = [NAMED_SENT (KNOWN pvalue_name)]])',
            '~$config_iterator_copied_call(S, pconfigcall)',
            'pconfigcall.OWNER = (n_owner)',
            'S.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_RESTORE',
            'pconfigcall.SELECTION = eps',
            '$lookup(S.ENV, $ptascii("keep")) = (n_keep_cell)',
            'S.STORE[n_keep_cell] = DEFINED (POBJECT n_owner)',
            '$lookup(S.ENV, $ptascii("call")) = (n_call_cell)',
            'S.STORE[n_call_cell] = DEFINED (POBJECT n_getter)',
            'n_getter =/= n_owner',
            'S.OBJECTS[n_getter] = INTRINSICCLOSURE INTRINSIC_INI_GET',
            '$task_nodes(CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_name pvalue_name) = [HOBJECT n_owner]',
            '~((HOBJECT n_name) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_name) = 0',
            'S.PRECISIONINI = $ptascii("1")',
            'S.ITERATORS = eps',
            '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
            'PhpStep: S ~> S_restore',
            'S_restore.RESULT = KNOWN PNULL',
            'S_restore.PRECISIONINI = $ptascii("14")',
            '~S_restore.PRECISIONMODIFIED',
            'S_restore.EVENTS = S.EVENTS',
            '$call_descriptors_valid(S_restore)', '$heap_valid($heap_graph(S_restore))',
            'S_done = $drive(S, 4000)',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
            'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
            'S_done.ITERATORS = eps',
            'S_done.PRECISIONINI = $ptascii("14")',
            '$test_outputs(S_done.EVENTS) = $ptascii("' + ROWS[RESTORE]['native_stdout'] + '")',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        ],
    },
    'aggregate-held-and-named-get-refuse-unvalidated-option': {
        'source': ROWS[GET]['source'],
        'stage': 'S.TODO = (CONFIG_STRING_RESULT pconfigcall n_name porigin_child z_child z_call) :: ptask_tail* '
                 '-- if S.RESULT = KNOWN pvalue_name',
        'checks': [
            'pconfigcall.KIND = INTRINSIC_INI_GET',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_name))]',
            '$string_bytes(pvalue_name) = ($ptascii("precision"))',
            '$config_iterator_copied_call(S[.ORIGIN = (pconfigcall.SITE)], pconfigcall)',
            '$config_iterator_string_receive_valid(S[.ORIGIN = (pconfigcall.SITE)], pconfigcall, n_name, pvalue_name)',
            'pconfigcall_named = pconfigcall[.NAMED = true]',
            '~$config_iterator_copied_header(S[.ORIGIN = (pconfigcall.SITE)], pconfigcall_named)',
            '~$config_iterator_unary_option(S, pconfigcall_named)',
            'pvalue_other = PSTRING $ptascii("display_errors")',
            '~$config_iterator_string_receive_valid(S[.ORIGIN = (pconfigcall.SITE)], pconfigcall, n_name, pvalue_other)',
            '$heap_owners($heap_graph(S), HOBJECT n_name) = 2',
            'S.PRECISIONINI = $ptascii("7")',
            'S_held = S[.HELD = S.HELD ++ [HOBJECT n_name]]',
            '$heap_owners($heap_graph(S_held), HOBJECT n_name) = 3',
            '$heap_valid($heap_graph(S_held))',
            'PhpStep: S_held ~> S_stop',
            'S_stop.COMPLETION = UNSUPPORTED '
            '"CONFIG Iterator getter Stringable option outside precision"',
            'PhpStep: S ~> S_receive',
            'S_receive.TODO = (CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_name pvalue_name) :: ptask_tail*',
            '$heap_owners($heap_graph(S_receive), HOBJECT n_name) = 0',
            '$call_descriptors_valid(S_receive)', '$heap_valid($heap_graph(S_receive))',
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
