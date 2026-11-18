#!/usr/bin/env python3
"""Reached REQUEST fields, immutable registry facts and split object retirement."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_object_scalar_fields_post_protocol as prior
import string_offset_nested_unset_bool_cv_object_request_fields_post_cases as cases

INDEX = 0
PRELAW = False
BASE_FRONT = prior.front
LEGACY = prior.INITIAL


def fields(count, identity, data):
    return ('[{DECL eps, NAME $ptascii("count"), STATE PROP_VALUE (DIRECT (PINT ' + str(count) + '))}, '
            '{DECL eps, NAME $ptascii("tag"), STATE PROP_VALUE (DIRECT (PSTRING_CARRIER '
            '(REQUEST_STRING ' + identity + ') ' + data + '))}]')


INITIAL = fields(7, 'n_tag_before', 'n_tag_before_bytes*')
CHANGED = fields(9, 'n_tag_changed', 'n_tag_changed_bytes*')
REBOUND = fields(11, 'n_tag_after', 'n_tag_after_bytes*')


def carrier(identity, data):
    return 'PSTRING_CARRIER (REQUEST_STRING ' + identity + ') ' + data


def front(program, path):
    checks = BASE_FRONT(program, path)
    at = checks.index('$objectprops_at(S_R.OBJECTPROPS, n_object) = (' + INITIAL + ')') + 1
    checks[at:at] = ['n_tag_before_bytes* = $ptascii("field-old")',
        '$(n_tag_before < |S_R.STRINGDATA|)',
        'S_R.STRINGDATA[n_tag_before] = n_tag_before_bytes*',
        '$string_carrier_valid(S_R, ' + carrier('n_tag_before', 'n_tag_before_bytes*') + ')',
        '$value_nodes(' + carrier('n_tag_before', 'n_tag_before_bytes*') + ') = eps',
        '$property_release_nodes(' + INITIAL + ') = eps']
    return checks


def conditions(program, path):
    prior.INDEX, prior.PRELAW, prior.cases = INDEX, PRELAW, cases
    prior.INITIAL, prior.CHANGED, prior.REBOUND = INITIAL, CHANGED, REBOUND
    prior.front = front
    try:
        checks, derived = prior.conditions(program, path)
    finally:
        prior.front = BASE_FRONT
    at = checks.index('$objectprops_at(S_B.OBJECTPROPS, n_after) = (' + REBOUND + ')') + 1
    checks[at:at] = ['n_tag_changed_bytes* = $ptascii("field-changed")',
        'n_tag_after_bytes* = $ptascii("field-new")',
        r'n_tag_before =/= n_tag_changed /\ n_tag_before =/= n_tag_after /\ n_tag_changed =/= n_tag_after',
        'S_B.STRINGDATA[n_tag_before] = n_tag_before_bytes*',
        '$string_carrier_valid(S_B, ' + carrier('n_tag_changed', 'n_tag_changed_bytes*') + ')',
        '$string_carrier_valid(S_B, ' + carrier('n_tag_after', 'n_tag_after_bytes*') + ')']
    derived += 6
    at = checks.index('$objectprops_at(S_RET.OBJECTPROPS, n_after) = (' + REBOUND + ')') + 1
    checks[at:at] = ['S_RET.STRINGDATA = S_B.STRINGDATA',
        '$string_carrier_valid(S_RET, ' + carrier('n_tag_after', 'n_tag_after_bytes*') + ')']
    derived += 2
    checks += ['S_DONE.STRINGDATA = S_RET.STRINGDATA']
    derived += 1
    if PRELAW:
        return checks, derived
    reached = len(checks)
    fields_call = '$string_unset_bool_cv_post_object_fields'
    checks += [fields_call + '(S_R, ' + INITIAL + ')',
        '~$string_unset_bool_cv_post_value(' + carrier('n_tag_before', 'n_tag_before_bytes*') + ')',
        '~$string_unset_bool_cv_post_normal_value(' + carrier('n_tag_before', 'n_tag_before_bytes*') + ')',
        '~$string_unset_bool_cv_post_cell(S_R[.STORE[n_key] = DEFINED (' + carrier('n_tag_before', 'n_tag_before_bytes*') + ')], n_key_name*, z_key, n_key)',
        fields_call + '(S_R, ' + LEGACY + ')',
        'S_legacy = S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, ' + LEGACY + ')]',
        '$heap_graph(S_legacy) = $heap_graph(S_R)',
        '$string_unset_bool_cv_post_object_cell(S_legacy, n_owner)',
        '$string_unset_bool_cv_post_nonempty_array(S_legacy, n_key)']
    for bad_carrier in (
        carrier('(|S_R.STRINGDATA|)', 'n_tag_before_bytes*'),
        carrier('n_tag_before', '($ptascii("forged"))'),
        'PSTRING n_tag_before_bytes*',
        'PSTRING_CARRIER INTERNED_STRING ([0, 65])',
    ):
        bad_fields = '[{DECL eps, NAME $ptascii("tag"), STATE PROP_VALUE (DIRECT (' + bad_carrier + '))}]'
        changed = 'S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, ' + bad_fields + ')]'
        checks += ['~' + fields_call + '(S_R, ' + bad_fields + ')',
            '~$string_unset_bool_cv_post_object(' + changed + ', n_object)',
            '~$string_unset_bool_cv_post_nonempty_array(' + changed + ', n_key)']
    for changed in ('S_R[.STRINGDATA = eps]',
                    'S_R[.STRINGDATA[n_tag_before] = $ptascii("forged")]'):
        checks += ['~' + fields_call + '(' + changed + ', ' + INITIAL + ')',
            '~$string_unset_bool_cv_post_object_cell(' + changed + ', n_owner)',
            '~$string_unset_bool_cv_post_nonempty_array(' + changed + ', n_key)']
    nul_fields = fields(7, '(|S_R.STRINGDATA|)', '([0, 65])')
    checks += ['S_nul = $string_request(S_R, [0, 65])',
        '$string_carrier_valid(S_nul, ' + carrier('(|S_R.STRINGDATA|)', '([0, 65])') + ')',
        '~' + fields_call + '(S_nul, ' + nul_fields + ')',
        '~$string_unset_bool_cv_post_object(S_nul[.OBJECTPROPS = $objectprops_set(S_nul.OBJECTPROPS, n_object, ' + nul_fields + ')], n_object)']
    checks += ['S_wide = $string_request(S_R, [256])',
        '~$string_carrier_valid(S_wide, ' + carrier('(|S_R.STRINGDATA|)', '([256])') + ')',
        '~' + fields_call + '(S_wide, ' + fields(7, '(|S_R.STRINGDATA|)', '([256])') + ')']
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
               Path(prior.prior.prior.__file__), Path(cases.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = prior.prior.raw.runner
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = prior.PREFIX, prior.prior.raw.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Reached REQUEST-field ownership before old Unsupported; tail states are derived/source0/native0.'
        if PRELAW else 'Reached authenticated non-NUL REQUEST fields, DIRECT/ALIAS owners, Error/same-Throwable and staged retirement. Registry, NUL, legacy scalar and owner/source controls are derived/source0/native0.')
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
