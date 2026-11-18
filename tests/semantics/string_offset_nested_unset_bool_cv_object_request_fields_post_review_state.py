#!/usr/bin/env python3
"""Independent reached REQUEST fields, immutable registry and object retirement."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_object_scalar_fields_post_review_state as prior
import string_offset_nested_unset_bool_cv_object_request_fields_post_cases as cases

INDEX = 0
PRELAW = False
FRONT = prior.front
PREFIX = prior.PREFIX


def slots(count, value):
    return '[' + prior.slot('$ptascii("count")', 'PINT ' + str(count)) + ', ' + prior.slot('$ptascii("tag")', value) + ']'


def carrier(identity, text):
    return 'PSTRING_CARRIER (REQUEST_STRING ' + identity + ') ($ptascii("' + text + '"))'


INITIAL = slots(7, carrier('n_tag', 'field-old'))
CHANGED = slots(9, carrier('n_tag_changed', 'field-changed'))
REBOUND = slots(11, carrier('n_tag_after', 'field-new'))


def front(program, path):
    prior.INDEX, prior.cases = INDEX, cases
    checks = FRONT(program, path)
    original = prior.fields(7, 'true', 'old', 4609434218613702656)
    assert sum(check.count(original) for check in checks) == 2
    checks = [check.replace(original, INITIAL) for check in checks]
    checks += ['pvalue_request = ' + carrier('n_tag', 'field-old'),
        '$(n_tag < |S_R.STRINGDATA|)',
        'S_R.STRINGDATA[n_tag] = $ptascii("field-old")',
        '$string_carrier_valid(S_R, pvalue_request)',
        '$string_getter_value(pvalue_request) = (pvalue_request)',
        '$value_nodes(pvalue_request) = eps',
        '~$string_unset_bool_cv_post_value(pvalue_request)']
    return checks


def conditions(program, path):
    prior.INDEX, prior.PRELAW, prior.cases, prior.front = INDEX, PRELAW, cases, front
    try:
        checks, derived = prior.conditions(program, path)
    finally:
        prior.front = FRONT
    changed = prior.fields(9, 'true', 'changed', 4609434218613702656)
    rebound = prior.fields(11, 'false', 'new', 4612811918334230528)
    assert sum(check.count(changed) for check in checks) == 1
    assert sum(check.count(rebound) for check in checks) == 2
    checks = [check.replace(changed, CHANGED).replace(rebound, REBOUND).replace(
        'PSTRING_CARRIER (REQUEST_STRING 0) ([65])', carrier('n_tag', 'forged')) for check in checks]
    at = checks.index('$objectprops_at(S_B.OBJECTPROPS, n_after) = (' + REBOUND + ')') + 1
    registry = ['$(n_tag < |S_B.STRINGDATA|)',
        '$(n_tag_changed < |S_B.STRINGDATA|)', '$(n_tag_after < |S_B.STRINGDATA|)',
        'S_B.STRINGDATA[n_tag] = $ptascii("field-old")',
        'S_B.STRINGDATA[n_tag_changed] = $ptascii("field-changed")',
        'S_B.STRINGDATA[n_tag_after] = $ptascii("field-new")',
        'n_tag_changed =/= n_tag', 'n_tag_after =/= n_tag',
        'n_tag_after =/= n_tag_changed']
    checks[at:at] = registry
    at = checks.index('S_RET.COMPLETION = NORMAL') + 1
    checks[at:at] = ['S_RET.STRINGDATA = S_B.STRINGDATA']
    at = checks.index('S_DONE = $drive_steps(S_RET, 4000)') + 1
    checks[at:at] = ['S_DONE.STRINGDATA = S_B.STRINGDATA']
    if PRELAW:
        return checks, derived + len(registry) + 2
    at = checks.index('S_next.OBJECTPROPS = S_R.OBJECTPROPS') + 1
    checks[at:at] = ['S_next.STRINGDATA = S_R.STRINGDATA']
    reached = len(checks)
    checks += ['S_legacy = S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, ' +
        prior.fields(7, 'true', 'old', 4609434218613702656) + ')]',
        '$heap_graph(S_legacy) = H_saved',
        '$string_unset_bool_cv_post_object_fields(S_legacy, ' + prior.fields(7, 'true', 'old', 4609434218613702656) + ')',
        '$string_unset_bool_cv_post_object(S_legacy, n_object)',
        '$string_unset_bool_cv_post_object_cell(S_legacy, n_alias)',
        '$string_unset_bool_cv_post_nonempty_array(S_legacy, n_key)',
        'S_extra = $objectprops_mark(S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, [' +
            prior.slot('$ptascii("extra")', 'PINT 1') + '])], n_object)',
        '$heap_graph(S_extra) = H_saved',
        '$string_unset_bool_cv_post_object_cell(S_extra, n_alias)',
        '$string_unset_bool_cv_post_nonempty_array(S_extra, n_key)',
        'S_key_carrier = S_R[.STORE[n_key] = DEFINED pvalue_request]',
        '~$string_unset_bool_cv_post_cell(S_key_carrier, n_key_name*, z_key, n_key)',
        '~$string_unset_bool_cv_post_discard_cell(S_key_carrier, n_key_name*, z_key, n_key)']
    for tag, state in (
        ('missing', 'S_R[.STRINGDATA = eps]'),
        ('registry', 'S_R[.STRINGDATA[n_tag] = $ptascii("forged")]'),
        ('index', 'S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, ' + slots(7, carrier('(|S_R.STRINGDATA|)', 'field-old')) + ')]'),
        ('raw', 'S_R[.OBJECTPROPS = $objectprops_set(S_R.OBJECTPROPS, n_object, ' + slots(7, 'PSTRING ($ptascii("field-old"))') + ')]'),
    ):
        name = 'S_bad_' + tag
        checks += [name + ' = ' + state,
            '$heap_graph(' + name + ') = H_saved',
            '~$string_unset_bool_cv_post_object(' + name + ', n_object)',
            '~$string_unset_bool_cv_post_object_cell(' + name + ', n_alias)',
            '~$string_unset_bool_cv_post_nonempty_array(' + name + ', n_key)']
    for tag, payload, authenticated in (
        ('nul', '([65, 0, 66])', True),
        ('bytes', '([256, 65])', False),
    ):
        seed, value, state = 'S_seed_' + tag, 'pvalue_' + tag, 'S_bad_' + tag
        checks += [seed + ' = $string_request(S_R, ' + payload + ')',
            seed + '.RESULT = KNOWN ' + value,
            ('' if authenticated else '~') + '$string_carrier_valid(' + seed + ', ' + value + ')',
            state + ' = ' + seed + '[.OBJECTPROPS = $objectprops_set(' + seed + '.OBJECTPROPS, n_object, ' + slots(7, value) + ')]',
            '$heap_graph(' + state + ') = H_saved',
            '~$string_unset_bool_cv_post_object(' + state + ', n_object)',
            '~$string_unset_bool_cv_post_object_cell(' + state + ', n_alias)',
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
    watched = [Path(__file__), Path(prior.__file__), Path(prior.base.__file__),
        Path(prior.base.prior.__file__), Path(prior.base.prior.seek.__file__),
        Path(prior.base.prior.sl.__file__), Path(cases.prior.__file__),
        *[prior.base.prior.runner.ROOT / path for path in cases.WATCHED]]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner = prior.base.prior.runner
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = PREFIX, prior.base.prior.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    output = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(output.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Independent reached two-slot REQUEST registry/owner/source facts precede old Unsupported; '
        'derived B/R/final registry and weak retirement remain source0/native0.' if PRELAW else
        'Independent real REQUEST fields preserve Error/Throwable, registry, public whole/split and object retirement; '
        'fresh registry/index/forgery/NUL/invalid-byte/root-key and exact legacy scalar controls remain source0/native0.')
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
