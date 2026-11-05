#!/usr/bin/env python3
"""Reach unary copied getter reception after Stringable option disposal."""
import argparse
import json
from functools import partial
from pathlib import Path

import generator_call_unpack_state as base

CATALOG = Path(__file__).with_name('config_iterator_get_stringable_cases.json')
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOG.read_bytes())}


def case(source, selected):
    checks = [
        'S.ORIGIN = (pconfigcall.SITE)',
        'pconfigcall.KIND = INTRINSIC_INI_GET',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_name))]',
        '$string_bytes(pvalue_name) = ($ptascii("precision"))',
        '$config_iterator_string_receive_valid(S, pconfigcall, n_name, pvalue_name)',
        '$config_iterator_copied_header(S, pconfigcall)',
        '~$config_iterator_copied_call(S, pconfigcall)',
        '$task_nodes(CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_name pvalue_name) = '
        + ('[HOBJECT n_owner]' if selected else 'eps'),
        '~((HOBJECT n_name) <- S.ALLOCATIONS)',
        '$heap_owners($heap_graph(S), HOBJECT n_name) = 0',
        'S.PRECISIONINI = $ptascii("1")',
        'S.ITERATORS = eps',
        '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
        'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S',
        'PhpStep: S ~> S_read',
        'S_read.TODO = ptask_tail*',
        'S_read.RESULT = KNOWN pvalue_read',
        '$string_bytes(pvalue_read) = ($ptascii("1"))',
        'S_read.PRECISIONINI = S.PRECISIONINI',
        'S_read.EVENTS = S.EVENTS',
        '$call_descriptors_valid(S_read)', '$heap_valid($heap_graph(S_read))',
        'S_done = $drive(S, 4000)',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
        'S_done.ITERATORS = eps',
        'S_done.PRECISIONINI = $ptascii("14")',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    if selected:
        checks += [
            'pconfigcall.OWNER = (n_owner)',
            'S.OBJECTS[n_owner] = INTRINSICCLOSURE INTRINSIC_INI_GET',
            'pconfigcall.SELECTION = eps',
            '$lookup(S.ENV, $ptascii("keep")) = (n_keep_cell)',
            'S.STORE[n_keep_cell] = DEFINED (POBJECT n_owner)',
            '$lookup(S.ENV, $ptascii("call")) = (n_call_cell)',
            'S.STORE[n_call_cell] = DEFINED (POBJECT n_setter)',
            'n_setter =/= n_owner',
            'S.OBJECTS[n_setter] = INTRINSICCLOSURE INTRINSIC_INI_SET',
            '$heap_owners($heap_graph(S_done), HOBJECT n_owner) = 0',
        ]
    else:
        checks += ['pconfigcall.OWNER = eps']
    return {
        'source': SOURCES[source],
        'stage': 'S.TODO = (CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_name pvalue_name) :: ptask_tail*',
        'checks': checks,
    }


CASES = {
    'temporary-get-reads-after-option-disposal': case(
        'temporary-get-observes-option-disposal', False),
    'selected-get-keeps-original-owner-after-rebinding': case(
        'selected-get-keeps-original-callee', True),
    'held-option-stops-before-unvalidated-getter-read': {
        'source': SOURCES['temporary-get-observes-option-disposal'],
        'stage': 'S.TODO = (CONFIG_STRING_RESULT pconfigcall n_name porigin_child z_child z_call) :: ptask_tail* '
                 '-- if S.RESULT = KNOWN pvalue_name',
        'checks': [
            'pconfigcall.KIND = INTRINSIC_INI_GET',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_name))]',
            '$string_bytes(pvalue_name) = ($ptascii("precision"))',
            '$config_iterator_copied_call(S[.ORIGIN = (pconfigcall.SITE)], pconfigcall)',
            '$config_iterator_string_receive_valid(S[.ORIGIN = (pconfigcall.SITE)], pconfigcall, n_name, pvalue_name)',
            '$heap_owners($heap_graph(S), HOBJECT n_name) = 1',
            'S.PRECISIONINI = $ptascii("14")',
            'S_held = S[.HELD = S.HELD ++ [HOBJECT n_name]]',
            '$heap_owners($heap_graph(S_held), HOBJECT n_name) = 2',
            '$heap_valid($heap_graph(S_held))',
            'PhpStep: S_held ~> S_stop',
            'S_stop.COMPLETION = UNSUPPORTED '
            '"CONFIG Iterator getter Stringable option outside precision"',
            'PhpStep: S ~> S_receive',
            'S_receive.TODO = (CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_name pvalue_name) :: ptask_tail*',
            '$heap_owners($heap_graph(S_receive), HOBJECT n_name) = 1',
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
