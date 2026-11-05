#!/usr/bin/env python3
"""Reach Boolean assertion INI writes after copied option disposal."""
import argparse
import json
from functools import partial
from pathlib import Path

import generator_call_unpack_state as base

CATALOG = Path(__file__).with_name('config_iterator_assertions_bool_cases.json')
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOG.read_bytes())}


def case(source, value, owner):
    boolean = 'true' if value else 'false'
    quantity = 1 if value else 0
    text = '1' if value else ''
    checks = [
        'S.ORIGIN = (pconfigcall.SITE)',
        'pconfigcall.KIND = INTRINSIC_INI_SET',
        f'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_name)), NAMED_SENT (KNOWN (PBOOL {boolean}))]',
        '$string_bytes(pvalue_name) = ($ptascii("zend.assertions"))',
        '$config_iterator_string_receive_valid(S, pconfigcall, n_name, pvalue_name)',
        '~((HOBJECT n_name) <- S.ALLOCATIONS)',
        '$heap_owners($heap_graph(S), HOBJECT n_name) = 0',
        'S.ITERATORS = eps', 'S.ASSERTIONS = 1',
        'S.ASSERTIONSINI = $ptascii("1")', '~S.ASSERTIONSMODIFIED',
        'S.ASSERTIONINI = eps',
        'pconfigcall_negative = pconfigcall[.SENT = '
        '[NAMED_SENT (KNOWN (POBJECT n_name)), NAMED_SENT (KNOWN (PINT $(-1)))]]',
        '~$config_iterator_string_receive_valid(S, pconfigcall_negative, n_name, pvalue_name)',
        'pconfigcall_null = pconfigcall[.SENT = '
        '[NAMED_SENT (KNOWN (POBJECT n_name)), NAMED_SENT (KNOWN PNULL)]]',
        '$config_iterator_string_receive_valid(S, pconfigcall_null, n_name, pvalue_name)',
    ]
    if owner:
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
        'PhpStep: S ~> S_pending',
        'S_pending.TODO = (ASSERTION_INI_RESULT passertini) :: ptask_tail*',
        'passertini.CALL.KIND = INTRINSIC_INI_SET',
        'passertini.CALL.OWNER = pconfigcall.OWNER',
        'passertini.CONVERSION = (passertiniconversion)',
        'passertiniconversion.SOURCE = '
        'CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_name pvalue_name',
        'passertiniconversion.VALUE = pvalue_name',
        'passertini.CALL = pconfigcall[.SENT = '
        f'[NAMED_SENT (KNOWN pvalue_name), NAMED_SENT (KNOWN (PBOOL {boolean}))]]',
        'passertini.PHASE = ASSERTION_PARSE',
        f'passertini.VALUE = {quantity}',
        f'$string_bytes(passertini.INPUT) = ($ptascii("{text}"))',
        '$string_bytes(passertini.OLDRETURN) = ($ptascii("1"))',
        'S_pending.ASSERTIONS = 1', 'S_pending.ASSERTIONSMODIFIED',
        '$string_bytes(S_pending.ASSERTIONSRAW) = ($ptascii("1"))',
        '$string_bytes(S_pending.ASSERTIONSORIGINAL) = ($ptascii("1"))',
        '$assertion_state_valid(S_pending)',
        '$assertion_ini_record(S_pending.ASSERTIONINI, passertini.ID) = (passertini)',
        '$assertion_ini_record_shape(S_pending, passertini)',
        '$assertion_ini_input_valid(S_pending, passertini)',
        '$assertion_ini_conversion_valid(S_pending, (passertiniconversion), passertini.CALL, passertini.PRECISION)',
        '$assertion_ini_call_valid(S_pending, passertini)',
        '$assertion_ini_valid(S_pending, passertini)',
        'S_pending.ASSERTIONINI = [passertini]',
        'passertini_bare = passertini[.CONVERSION = eps]',
        'S_bare = S_pending[.ASSERTIONINI = [passertini_bare]]'
        '[.TODO = (ASSERTION_INI_RESULT passertini_bare) :: ptask_tail*]',
        '~$assertion_ini_call_valid(S_bare, passertini_bare)',
        '~$assertion_ini_valid(S_bare, passertini_bare)',
        '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
        'PhpStep: S_pending ~> S_written',
        f'S_written.ASSERTIONS = {quantity}',
        f'S_written.ASSERTIONSINI = $ptascii("{text}")',
        'S_written.ASSERTIONSMODIFIED',
        'S_written.ASSERTIONSRAW =/= PNULL',
        f'$string_bytes(S_written.ASSERTIONSRAW) = ($ptascii("{text}"))',
        'S_written.ASSERTIONINI = eps',
        'S_written.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = ($ptascii("1"))',
        'S_done = $drive(S, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps', 'S_done.ITERATORS = eps',
        'S_done.ASSERTIONS = 1', 'S_done.ASSERTIONSINI = $ptascii("1")',
        '~S_done.ASSERTIONSMODIFIED', 'S_done.ASSERTIONINI = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return {'source': SOURCES[source],
            'stage': 'S.TODO = (CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_name pvalue_name) :: ptask_tail*',
            'checks': checks}


CASES = {
    'temporary-false-keeps-empty-raw-distinct-from-zero': case(
        'temporary-false-installs-empty-raw-and-quantity-zero', False, False),
    'selected-true-keeps-owner-after-cv-rebinding': case(
        'selected-true-preserves-original-owner-after-rebinding', True, True),
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    base.CASES = CASES
    base.INPUTS = [Path(__file__), CATALOG, Path(base.__file__)]
    base.review.run = partial(base.review.run, process_seconds=300)
    raise SystemExit(0 if base.run(parser.parse_args().case) else 1)
