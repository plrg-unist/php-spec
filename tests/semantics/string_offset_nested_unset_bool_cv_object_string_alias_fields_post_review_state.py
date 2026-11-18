#!/usr/bin/env python3
"""Independent STRING field cells, exact registry and duplicate-edge retirement."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_object_primitive_alias_fields_post_review_state as prior
import string_offset_nested_unset_bool_cv_object_string_alias_fields_post_cases as cases

INDEX = 0
PRELAW = False
FRONT = prior.front
PREFIX = prior.PREFIX


def front(program, path):
    checks = FRONT(program, path)
    for old, new in (
        ('S_R.STORE[n_field] = DEFINED (PINT 7)', 'S_R.STORE[n_field] = DEFINED pvalue_field'),
        ('$literal_reference_plain_cell(S_R, n_field)', '~$literal_reference_plain_cell(S_R, n_field)'),
        ('~$string_read_array_string_cell(S_R, n_field)', '$string_read_array_string_cell(S_R, n_field)'),
    ):
        assert checks.count(old) == 1
        checks[checks.index(old)] = new
    if INDEX:
        checks += ['pvalue_field = PSTRING_CARRIER (REQUEST_STRING n_initial) ($ptascii("old"))',
            '$(n_initial < |S_R.STRINGDATA|)', 'S_R.STRINGDATA[n_initial] = $ptascii("old")']
    else:
        checks += ['pvalue_field = PSTRING_CARRIER INTERNED_STRING ($ptascii("old"))']
    checks += ['$string_carrier_valid(S_R, pvalue_field)',
        '$string_getter_value(pvalue_field) = (pvalue_field)', '$value_nodes(pvalue_field) = eps']
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
    later = ['S_B.STORE[n_field] = DEFINED pvalue_later',
        'pvalue_later = PSTRING_CARRIER (REQUEST_STRING n_later) ($ptascii("later"))',
        '$(n_later < |S_B.STRINGDATA|)', 'S_B.STRINGDATA[n_later] = $ptascii("later")',
        '$string_carrier_valid(S_B, pvalue_later)',
        '$string_getter_value(pvalue_later) = (pvalue_later)',
        '~$literal_reference_plain_cell(S_B, n_field)',
        '$string_carrier_valid(S_B, pvalue_field)', '$(n_later >= |S_R.STRINGDATA|)']
    if INDEX:
        later += ['n_later =/= n_initial']
    checks[at:at + 1] = later
    added = len(later) - 1
    for state in ('S_RET', 'S_DONE'):
        extra = [state + '.STRINGDATA = S_B.STRINGDATA',
            '$string_carrier_valid(' + state + ', pvalue_later)',
            '$string_getter_value(pvalue_later) = (pvalue_later)',
            '$string_carrier_valid(' + state + ', pvalue_field)',
            '~$string_read_array_string_cell(' + state + ', n_field)',
            state + '.STRINGDATA[n_later] = $ptascii("later")']
        if INDEX:
            extra += [state + '.STRINGDATA[n_initial] = $ptascii("old")']
        checks += extra
        added += len(extra)
    if PRELAW:
        return checks, derived + added
    reached = len(checks)
    for payload in ('eps', '($ptascii("0"))', '([128, 255])'):
        state = 'S_R[.STORE[n_field] = DEFINED (PSTRING_CARRIER INTERNED_STRING ' + payload + ')]'
        checks += ['$heap_graph(' + state + ') = H_saved',
            '~$literal_reference_plain_cell(' + state + ', n_field)',
            '$string_read_array_string_cell(' + state + ', n_field)',
            '$string_unset_bool_cv_post_object(' + state + ', n_object)',
            '$string_unset_bool_cv_post_object_cell(' + state + ', n_alias)',
            '$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    checks += ['S_cert_seed = $string_request(S_R, $ptascii("certified"))',
        'S_cert_seed.RESULT = KNOWN pvalue_certified',
        'pvalue_certified = PSTRING_CARRIER (REQUEST_STRING n_certified) ($ptascii("certified"))',
        'S_cert = S_cert_seed[.STORE[n_field] = DEFINED pvalue_certified]',
        '$heap_graph(S_cert) = H_saved', '~$literal_reference_plain_cell(S_cert, n_field)',
        '$string_read_array_string_cell(S_cert, n_field)',
        '$string_unset_bool_cv_post_object(S_cert, n_object)',
        '$string_unset_bool_cv_post_object_cell(S_cert, n_alias)',
        '$string_unset_bool_cv_post_nonempty_array(S_cert, n_key)']
    for state in (
        'S_R[.STORE[n_field] = DEFINED (PSTRING ($ptascii("raw")))]',
        'S_R[.STORE[n_field] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([0, 65]))]',
        'S_R[.STORE[n_field] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([256]))]',
        'S_R[.STORE[n_field] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S_R.STRINGDATA|)) ($ptascii("out")))]',
        'S_cert[.STRINGDATA = eps]',
        'S_cert[.STRINGDATA[n_certified] = $ptascii("forged")]',
        'S_cert[.STORE[n_field] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_certified) ($ptascii("forged")))]',
    ):
        checks += ['~$string_read_array_string_cell(' + state + ', n_field)',
            '~$string_unset_bool_cv_post_object(' + state + ', n_object)',
            '~$string_unset_bool_cv_post_object_cell(' + state + ', n_alias)',
            '~$string_unset_bool_cv_post_nonempty_array(' + state + ', n_key)']
    checks += ['S_nul_seed = $string_request(S_R, [65, 0, 66])',
        'S_nul_seed.RESULT = KNOWN pvalue_nul', '$string_carrier_valid(S_nul_seed, pvalue_nul)',
        'S_nul = S_nul_seed[.STORE[n_field] = DEFINED pvalue_nul]',
        '$heap_graph(S_nul) = H_saved', '~$string_read_array_string_cell(S_nul, n_field)',
        '~$string_unset_bool_cv_post_object(S_nul, n_object)',
        '~$string_unset_bool_cv_post_object_cell(S_nul, n_alias)',
        '~$string_unset_bool_cv_post_nonempty_array(S_nul, n_key)']
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
        Path(prior.prior.base.__file__), Path(prior.prior.base.prior.__file__),
        Path(prior.prior.base.prior.seek.__file__), Path(prior.prior.base.prior.sl.__file__),
        Path(cases.__file__), Path(cases.prior.__file__),
        *[prior.prior.base.prior.runner.ROOT / path for path in cases.WATCHED]]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = prior.prior.base.prior.runner
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = PREFIX, prior.prior.base.prior.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    output = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(output.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Independent reached INTERNED/REQUEST field cells and duplicate owners precede old Unsupported; '
        'derived later REQUEST identity, full immutable registry and cell/object retirement remain source0/native0.' if PRELAW else
        'Independent STRING field sharing preserves Error/Throwable, distinct REQUEST headers and immutable registry after retirement; '
        'full-state/public/budget replay and exact promoted/byte/registry/wrapper/owning controls remain source0/native0.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
