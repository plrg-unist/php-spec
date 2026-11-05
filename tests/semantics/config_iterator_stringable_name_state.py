#!/usr/bin/env python3
"""Reach copied names, nonowning receive history and live value formatting."""
import argparse
import json
import struct
from functools import partial
from pathlib import Path

import generator_call_unpack_state as base

CATALOG = Path(__file__).with_name('config_iterator_stringable_name_cases.json')
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOG.read_bytes())}
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
DONE = ['S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
        '$drive(S, 4000) = S_done', 'S_done.TODO = eps', 'S_done.FRAMES = eps',
        'S_done.CURRENT = eps', 'S_done.HELD = eps', 'S_done.ITERATORS = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        'S_done.PRECISIONINI = $ptascii("14")',
        'S_done.FILEINCLUDEPATH = eps']

CASES = {
    'current-selected-name-survives-global-rebinding-before-send': {
        'source': SOURCES['retained-iterator-copies-name-before-global-rebinding'],
        'stage': 'S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask_tail* '
                 '-- if pconfigiterator.ITEMS = eps',
        'checks': [
            'n_data = pconfigiterator.OBJECT',
            'pconfigiterator.CURRENT = KNOWN (POBJECT n_name)',
            'pconfigiterator.KEY = KNOWN (PINT 0)',
            '$lookup(S.ENV, $ptascii("name")) = (n_global)',
            'S.STORE[n_global] = DEFINED (POBJECT n_new)', 'n_new =/= n_name',
            '$stringable_instance(S, n_name)',
            '~$config_iterator_argument(S, POBJECT n_name)',
            '$config_iterator_send_argument(S, POBJECT n_name)',
            '$config_iterator_current_value(S, pconfigiterator, pconfigiterator.CURRENT) = (POBJECT n_name)',
            '$heap_owners($heap_graph(S), HOBJECT n_name) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_new) = 1',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            'S.PRECISIONINI = $ptascii("14")', *VALID, *ZERO, *ONE,
            'S_one.TODO = (CONFIG_ITERATOR pconfigiterator_next "next-start") :: ptask_tail*',
            'pconfigiterator_next.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_name))]',
            'pconfigiterator_next.CURRENT = KNOWN PNULL',
            'pconfigiterator_next.KEY = KNOWN PNULL',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.STORE = S.STORE',
            'S_one.EVENTS = S.EVENTS', 'S_one.PRECISIONINI = S.PRECISIONINI',
            '$heap_owners($heap_graph(S_one), HOBJECT n_name) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_new) = 1',
            '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_one_budget',
            *DONE,
            '$heap_owners($heap_graph(S_done), HOBJECT n_name) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_new) = 0',
            '$heap_owners($heap_graph(S_done), HOBJECT n_data) = 0',
        ],
    },
}


def receipt(source, option, precision, old, checks, after, owner=False):
    return {
        'source': SOURCES[source],
        'stage': 'S.TODO = (CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_name pvalue_name) :: ptask_tail*',
        'checks': [
            'S.ORIGIN = (pconfigcall.SITE)',
            '$string_bytes(pvalue_name) = ($ptascii("' + option + '"))',
            '$config_iterator_string_receive_valid(S, pconfigcall, n_name, pvalue_name)',
            '~((HOBJECT n_name) <- S.ALLOCATIONS)',
            '$heap_owners($heap_graph(S), HOBJECT n_name) = 0',
            *checks,
            '$task_nodes(CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_name pvalue_name) = '
            + ('[HOBJECT n_owner]' if owner else 'eps'),
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_name)), NAMED_SENT (KNOWN pvalue_value)]',
            '~$config_iterator_copied_call(S, pconfigcall)',
            'S.PRECISIONINI = $ptascii("' + precision + '")',
            'S.FILEINCLUDEPATH = eps',
            *VALID, *ZERO, *ONE,
            *([] if owner else [
                'S_one.TODO = ptask_tail*',
                'S_one.RESULT = KNOWN pvalue_old',
                '$string_bytes(pvalue_old) = ($ptascii("' + old + '"))',
                'S_one.EVENTS = S.EVENTS',
                'S_one.OBJECTS = S.OBJECTS', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
                '$heap_owners($heap_graph(S_one), HOBJECT n_name) = 0',
                *after]),
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_one_budget',
            *DONE, '$heap_owners($heap_graph(S_done), HOBJECT n_name) = 0',
        ],
    }


CASES['retired-option-history-does-not-delay-normal-ini-write'] = receipt(
    'temporary-iterator-retires-before-name-conversion', 'precision', '14', '14',
    ['pvalue_value = PINT 7', 'S.ITERATORS = eps'],
    ['S_one.PRECISIONINI = $ptascii("7")',
     'S_one.FILEINCLUDEPATH = S.FILEINCLUDEPATH'])
FLOAT = struct.unpack('>Q', struct.pack('>d', 1.2345678901234567))[0]
CASES['self-name-retirement-precedes-raw-float-formatting'] = receipt(
    'self-name-formats-float-into-precision-after-disposal', 'precision', '3', '3',
    [f'pvalue_value = PFLOAT {FLOAT}', '$precision_value(S) = 3', 'S.ITERATORS = eps'],
    ['S_one.PRECISIONINI = $ptascii("1.23")',
     'S_one.FILEINCLUDEPATH = S.FILEINCLUDEPATH'])
CASES['selected-callee-owner-survives-rebinding-and-string-reception'] = receipt(
    'selected-callee-keeps-original-owner-after-rebinding', 'precision', '14', '14',
    ['pvalue_value = PINT 7', 'pconfigcall.OWNER = (n_owner)',
     'S.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_SET',
     'pconfigcall.SELECTION = eps',
     '$($heap_owners($heap_graph(S), HOBJECT n_owner) > 0)'],
    [], owner=True)
CASES['selected-callee-owner-survives-rebinding-and-string-reception']['checks'].append(
    '$heap_owners($heap_graph(S_done), HOBJECT n_owner) = 0')
CASES['copied-stringable-value-rejects-after-unknown-option-conversion'] = {
    'source': SOURCES['unknown-option-rejects-copied-stringable-value-after-option-disposal'],
    'stage': 'S.TODO = (CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_name pvalue_name) :: ptask_tail*',
    'checks': [
        'S.ORIGIN = (pconfigcall.SITE)',
        '$string_bytes(pvalue_name) = ($ptascii("missing_a98_option"))',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_name)), '
        'NAMED_SENT (KNOWN (POBJECT n_value))]',
        '$config_iterator_string_receive_valid(S, pconfigcall, n_name, pvalue_name)',
        '~((HOBJECT n_name) <- S.ALLOCATIONS)',
        '(HOBJECT n_value) <- S.ALLOCATIONS',
        '$config_iterator_data_value(S, POBJECT n_value, eps)',
        '~$config_ini_quiet_value(S, POBJECT n_value)',
        '$config_iterator_string_value(S, POBJECT n_value)',
        '$config_ini_value_conversion(POBJECT n_value) = TYPEREJECT',
        '$heap_owners($heap_graph(S), HOBJECT n_name) = 0',
        '$heap_owners($heap_graph(S), HOBJECT n_value) = 1',
        'S.PRECISIONINI = $ptascii("21")', 'S.ITERATORS = eps',
        *VALID, *ZERO,
        'PhpStep: S ~> S_error',
        'S_error.COMPLETION = THROWING n_error',
        '$throwable_field(S_error, n_error, "trace") = PARRAY n_trace',
        'S_error.ARRAYS[n_trace].ITEMS[0] = ENTRY (KINT 0) (DIRECT (PARRAY n_frame))',
        '$trace_array_field(S_error, n_frame, $ptascii("args")) = PARRAY n_args',
        'S_error.ARRAYS[n_args].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option), '
        'ENTRY (KINT 1) (DIRECT (POBJECT n_value))]',
        '$string_bytes(pvalue_option) = ($ptascii("missing_a98_option"))',
        '$($heap_owners($heap_graph(S_error), HOBJECT n_value) > 0)',
        'S_done = $drive(S, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps', 'S_done.ITERATORS = eps',
        'S_done.PRECISIONINI = $ptascii("14")',
        '$heap_owners($heap_graph(S_done), HOBJECT n_value) = 0',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ],
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    base.CASES = CASES
    base.INPUTS = [Path(__file__), CATALOG, Path(base.__file__)]
    base.review.run = partial(base.review.run, process_seconds=300)
    raise SystemExit(0 if base.run(parser.parse_args().case) else 1)
