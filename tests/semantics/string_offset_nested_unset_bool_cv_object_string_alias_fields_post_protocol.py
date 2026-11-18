#!/usr/bin/env python3
"""Reached STRING field cells retain exact carriers, real edges and retirement."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_object_primitive_alias_fields_post_protocol as prior
import string_offset_nested_unset_bool_cv_object_string_alias_fields_post_cases as cases

INDEX = 0
PRELAW = False
FRONT = prior.front


def front(program, path):
    checks = FRONT(program, path)
    old = 'S_R.STORE[n_field] = DEFINED (PINT 7)'
    assert checks.count(old) == 1
    checks[checks.index(old)] = 'S_R.STORE[n_field] = DEFINED pvalue_field'
    old = '$literal_reference_plain_cell(S_R, n_field)'
    assert checks.count(old) == 1
    checks[checks.index(old)] = '$string_read_array_string_cell(S_R, n_field)'
    if INDEX:
        checks += ['pvalue_field = PSTRING_CARRIER (REQUEST_STRING n_initial) ($ptascii("old"))',
            '$(n_initial < |S_R.STRINGDATA|)', 'S_R.STRINGDATA[n_initial] = $ptascii("old")']
    else:
        checks += ['pvalue_field = PSTRING_CARRIER INTERNED_STRING ($ptascii("old"))']
    checks += ['$string_carrier_valid(S_R, pvalue_field)', '$value_nodes(pvalue_field) = eps',
        '~$literal_reference_plain_cell(S_R, n_field)']
    return checks


def conditions(program, path):
    prior.INDEX, prior.PRELAW, prior.cases, prior.front = INDEX, PRELAW, cases, front
    try:
        checks, derived = prior.conditions(program, path)
    finally:
        prior.front = FRONT
    old = 'S_B.STORE[n_field] = DEFINED (PINT 13)'
    assert checks.count(old) == 1
    at = checks.index(old)
    checks[at:at + 1] = ['S_B.STORE[n_field] = DEFINED pvalue_later',
        'pvalue_later = PSTRING_CARRIER (REQUEST_STRING n_later) ($ptascii("later"))',
        '$(n_later < |S_B.STRINGDATA|)', 'S_B.STRINGDATA[n_later] = $ptascii("later")',
        '$string_carrier_valid(S_B, pvalue_later)']
    old = '$literal_reference_plain_cell(S_B, n_field)'
    assert checks.count(old) == 1
    checks[checks.index(old)] = '$string_read_array_string_cell(S_B, n_field)'
    derived += 4
    for state in ('S_RET', 'S_DONE'):
        checks += [state + '.STRINGDATA[n_later] = $ptascii("later")',
            '$string_carrier_valid(' + state + ', pvalue_later)',
            '~$string_read_array_string_cell(' + state + ', n_field)']
        derived += 3
        if INDEX:
            checks += [state + '.STRINGDATA[n_initial] = $ptascii("old")',
                '$string_carrier_valid(' + state + ', pvalue_field)']
            derived += 2
    if PRELAW:
        return checks, derived
    reached = len(checks)
    for data in ('eps', '$ptascii("0")', '$ptascii("string-field")'):
        state = 'S_R[.STORE[n_field] = DEFINED (PSTRING_CARRIER INTERNED_STRING (' + data + '))]'
        checks += ['$string_read_array_string_cell(' + state + ', n_field)',
            '$string_unset_bool_cv_post_object(' + state + ', n_object)',
            '$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    checks += ['S_seed_string = $string_request(S_R, $ptascii("registered-field"))',
        'S_seed_string.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING n_registered) n_registered_bytes*)',
        'S_valid_string = S_seed_string[.STORE[n_field] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_registered) n_registered_bytes*)]',
        '$string_read_array_string_cell(S_valid_string, n_field)',
        '$string_unset_bool_cv_post_object(S_valid_string, n_object)',
        '$string_unset_bool_cv_post_nonempty_array(S_valid_string, n_key)']
    for state in (
        'S_R[.STORE[n_field] = DEFINED (PSTRING ($ptascii("raw")))]',
        'S_R[.STORE[n_field] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([0, 65]))]',
        'S_R[.STORE[n_field] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([256]))]',
        'S_R[.STORE[n_field] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S_R.STRINGDATA|)) ($ptascii("out")))]',
        'S_valid_string[.STRINGDATA = eps]',
        'S_valid_string[.STORE[n_field] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_registered) ($ptascii("forged")))]',
    ):
        checks += ['~$string_read_array_string_cell(' + state + ', n_field)',
            '~$string_unset_bool_cv_post_object(' + state + ', n_object)',
            '~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    return checks, derived + len(checks) - reached


if __name__ == '__main__':
    PRELAW = '--prelaw' in sys.argv
    if PRELAW:
        sys.argv.remove('--prelaw')
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (0, 1)
    watched = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__),
        Path(prior.prior.prior.__file__), Path(prior.prior.prior.prior.__file__),
        Path(cases.__file__), Path(cases.prior.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = prior.prior.prior.raw.runner
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = prior.prior.PREFIX, prior.prior.prior.raw.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Reached INTERNED/REQUEST STRING property cells and duplicate edges precede old Unsupported; derived string-cell/object retirement and registry persistence remain source0/native0.'
        if PRELAW else 'Reached STRING property cells preserve Error/Throwable, duplicate owners, cell/object retirement and immutable registry. Carrier/wrapper/legacy controls remain derived/source0/native0.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
