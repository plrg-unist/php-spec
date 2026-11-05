#!/usr/bin/env python3
"""Reach float assertion INI writes after option disposal changes precision."""
import argparse
import json
from functools import partial
from pathlib import Path

import generator_call_unpack_state as base

CATALOG = Path(__file__).with_name('config_iterator_assertions_float_cases.json')
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOG.read_bytes())}


def case(source, bits, text, quantity, owner):
    raw = '$ptascii(' + json.dumps(text) + ')'
    checks = [
        'S.ORIGIN = (pconfigcall.SITE)',
        'pconfigcall.KIND = INTRINSIC_INI_SET',
        'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_name)), NAMED_SENT (KNOWN (PFLOAT n_float))]',
        f'n_float = {bits}',
        'S.PRECISIONINIT = $ptascii("14")',
        'S.PRECISIONINI = $ptascii("1")',
        'S.PRECISIONMODIFIED',
        f'$number_text(NFLOAT n_float, 1) = ({raw}, false)',
        '$config_iterator_assertion_float(PFLOAT n_float)',
        '$config_iterator_assertion_float_at(1, PFLOAT n_float)',
        '~$config_iterator_assertion_float_at(14, PFLOAT n_float)',
        '~$config_iterator_assertion_float(PFLOAT 9221120237041090560)',
        '~$config_iterator_assertion_float(PFLOAT 9218868437227405312)',
        '~$config_iterator_assertion_float_at(1, PFLOAT 13830554455654793216)',
        '$string_bytes(pvalue_name) = ($ptascii("zend.assertions"))',
        '$config_iterator_string_receive_valid(S, pconfigcall, n_name, pvalue_name)',
        '~((HOBJECT n_name) <- S.ALLOCATIONS)',
        '$heap_owners($heap_graph(S), HOBJECT n_name) = 0',
        'S.ITERATORS = eps', 'S.ASSERTIONS = 1',
        'S.ASSERTIONSINI = $ptascii("1")', '~S.ASSERTIONSMODIFIED',
        'S.ASSERTIONINI = eps',
        'S_high = $precision_memory(S, 14)',
        '$config_iterator_string_receive_valid(S_high, pconfigcall, n_name, pvalue_name)',
        'PhpStep: S_high ~> S_unsupported',
        'S_unsupported.COMPLETION = UNSUPPORTED "CONFIG Iterator assertion float outside warning-free nonnegative quantity"',
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
        '[NAMED_SENT (KNOWN pvalue_name), NAMED_SENT (KNOWN (PFLOAT n_float))]]',
        'passertini.PHASE = ASSERTION_PARSE',
        'passertini.PRECISION = 1',
        f'passertini.VALUE = {quantity}',
        'passertini.WARNING = eps',
        f'$string_bytes(passertini.INPUT) = ({raw})',
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
        'S_reprec = S_pending[.PRECISIONINI = $ptascii("14")]',
        '$assertion_ini_conversion_valid(S_reprec, (passertiniconversion), passertini.CALL, passertini.PRECISION)',
        '$assertion_ini_valid(S_reprec, passertini)',
        'passertini_bad = passertini[.PRECISION = 14]',
        'S_bad = S_pending[.ASSERTIONINI = [passertini_bad]]'
        '[.TODO = (ASSERTION_INI_RESULT passertini_bad) :: ptask_tail*]',
        '~$assertion_ini_conversion_valid(S_bad, (passertiniconversion), passertini_bad.CALL, passertini_bad.PRECISION)',
        '~$assertion_ini_valid(S_bad, passertini_bad)',
        'S_pending.ASSERTIONINI = [passertini]',
        'passertini_bare = passertini[.CONVERSION = eps]',
        'S_bare = S_pending[.ASSERTIONINI = [passertini_bare]]'
        '[.TODO = (ASSERTION_INI_RESULT passertini_bare) :: ptask_tail*]',
        '~$assertion_ini_call_valid(S_bare, passertini_bare)',
        '~$assertion_ini_valid(S_bare, passertini_bare)',
        '$call_descriptors_valid(S_pending)', '$heap_valid($heap_graph(S_pending))',
        'PhpStep: S_pending ~> S_written',
        f'S_written.ASSERTIONS = {quantity}',
        f'S_written.ASSERTIONSINI = {raw}',
        'S_written.PRECISIONINI = $ptascii("1")',
        'S_written.ASSERTIONSMODIFIED',
        'S_written.ASSERTIONSRAW =/= PNULL',
        f'$string_bytes(S_written.ASSERTIONSRAW) = ({raw})',
        'S_written.ASSERTIONINI = eps',
        'S_written.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = ($ptascii("1"))',
        'S_done = $drive(S, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps', 'S_done.ITERATORS = eps',
        'S_done.ASSERTIONS = 1', 'S_done.ASSERTIONSINI = $ptascii("1")',
        'S_done.PRECISIONINI = $ptascii("14")',
        '~S_done.ASSERTIONSMODIFIED', 'S_done.ASSERTIONINI = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return {'source': SOURCES[source],
            'stage': 'S.TODO = (CONFIG_ITERATOR_STRING_RECEIVE pconfigcall n_name pvalue_name) :: ptask_tail*',
            'checks': checks}


CASES = {
    'temporary-float-freezes-post-retirement-precision': case(
        'temporary-float-after-option-precision-change', 4608983858650965606, '1', 1, False),
    'selected-float-freezes-owner-and-precision': case(
        'selected-float-after-option-precision-change', 4609884578576439706, '2', 2, True),
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    base.CASES = CASES
    base.INPUTS = [Path(__file__), CATALOG, Path(base.__file__)]
    base.review.run = partial(base.review.run, process_seconds=300)
    raise SystemExit(0 if base.run(parser.parse_args().case) else 1)
