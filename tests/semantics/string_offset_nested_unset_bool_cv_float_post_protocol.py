#!/usr/bin/env python3
"""Genuine finite post-handler FLOAT values retain the saved ordinary BOOL CV."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_quiet_post_protocol as prior
import string_offset_nested_unset_bool_cv_float_post_cases as cases

INDEX = 0


def finite_checks():
    return ['S_P.STORE[n_key] = DEFINED (PFLOAT n_post)',
        '$(n_post < 18446744073709551616)',
        '$float_decode(n_post) = FINITE n_sign n_numerator n_denominator']


def front_checks(program, path):
    assert INDEX in (0, 3)
    prior.INDEX, prior.cases = INDEX, cases
    return prior.front_checks(program, path) + finite_checks()


def conditions(program, path):
    assert INDEX in (0, 3)
    prior.INDEX, prior.cases = INDEX, cases
    checks, derived = prior.conditions(program, path)
    if INDEX == 3:
        old = '$error_read_discard(S_P, perrorcall_entered.RESUME) = S_P'
        assert checks.count(old) == 1
        checks[checks.index(old)] = '$error_read_discard(S_P, perrorcall_entered.RESUME).COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"'
        controls = [
            '~$string_unset_bool_cv_post_normal_cell(S_P, n_key_name*, z_key, n_key)',
            '$string_unset_bool_cv_post_discard_cell(S_next, n_key_name*, z_key, n_key)',
            '$error_read_discard(S_next, perrorcall_entered.RESUME) = S_next',
        ]
        for mask in (0, 512):
            state = 'S_mask_' + str(mask)
            controls += [state + ' = S_P[.ERRORHANDLER.LEVELS = ' + str(mask) + ']',
                'PhpStep: ' + state + ' ~> ' + state + '_next',
                state + '_next.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"',
                state + '_next.ERRORHANDLER.CALLBACK = (pvalue_callback)',
                state + '_next.ERRORHANDLER.LEVELS = ' + str(mask),
                state + '_next.STORE = ' + state + '.STORE',
                state + '_next.EVENTS = ' + state + '.EVENTS',
                state + '_next.OBJECTS[n_throwable] = S_P.OBJECTS[n_throwable]']
        checks += controls
        derived += len(controls)
    else:
        controls = []
        for tag, bits in (('maximum_fit', 4890909195324358655),
                          ('minimum_fit', 14114281232179134464)):
            controls += ['$string_unset_bool_cv_post_normal_value(PFLOAT ' + str(bits) + ')']
        for tag, bits in (('positive_boundary', 4890909195324358656),
                          ('below_minimum', 14114281232179134465)):
            state = 'S_oob_' + tag
            controls += [state + ' = S_P[.STORE[n_key] = DEFINED (PFLOAT ' + str(bits) + ')]',
                '$string_unset_bool_cv_post_cell(' + state + ', n_key_name*, z_key, n_key)',
                '~$string_unset_bool_cv_post_normal_cell(' + state + ', n_key_name*, z_key, n_key)',
                'PhpStep: ' + state + ' ~> ' + state + '_next',
                state + '_next.COMPLETION = UNSUPPORTED "post-warning Boolean CV conversion"',
                state + '_next.EVENTS = ' + state + '.EVENTS']
        checks += controls
        derived += len(controls)
    return checks + finite_checks(), derived


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(prior.__file__), Path(prior.seek.__file__), Path(prior.sl.__file__),
               Path(cases.prior.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (0, 3)
    runner = prior.runner
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions = cases, conditions
    runner.PREFIX, runner.recorded = prior.seek.PREFIX, prior.sl.recorded
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Actual finite PFLOAT post-handler bits retain the saved ordinary BOOL-CV slot, '
        'no reference/released marker and whole-state quiet read. Normal Error or same pending Exception '
        'and callback restoration retain whole/split; fixture source0/native0 reuses only fresh FLOAT originals.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
