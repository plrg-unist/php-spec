#!/usr/bin/env python3
"""Genuine finite post-handler FLOAT values retain the saved ordinary BOOL CV."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_bool_cv_quiet_post_protocol as prior
import string_offset_nested_unset_bool_cv_float_post_cases as cases

INDEX = 0
RANGE_ONLY = False
PENDING_ONLY = False


def finite_checks():
    return ['S_P.STORE[n_key] = DEFINED (PFLOAT n_post)',
        '$(n_post < 18446744073709551616)',
        '$float_decode(n_post) = FINITE n_sign n_numerator n_denominator']


def front_checks(program, path):
    assert INDEX in (0, 3)
    prior.INDEX, prior.cases = INDEX, cases
    return prior.front_checks(program, path) + finite_checks()


def normal_range_checks():
    checks = []
    for tag, bits in (('positive_boundary', 4890909195324358656),
                      ('below_minimum', 14114281232179134465)):
        state = 'S_oob_' + tag
        call = 'perrorcall_' + tag
        checks += [state + ' = S_P[.STORE[n_key] = DEFINED (PFLOAT ' + str(bits) + ')]',
            '$string_unset_bool_cv_post_cell(' + state + ', n_key_name*, z_key, n_key)',
            '~$string_unset_bool_cv_post_normal_cell(' + state + ', n_key_name*, z_key, n_key)',
            '$string_unset_cv_range_plan(' + state + ') = ((porigin_site, z, n_key, ' + str(bits) + '))',
            'PhpStep: ' + state + ' ~> ' + state + '_next',
            state + '_next.COMPLETION = NORMAL',
            state + '_next.TODO = (ERROR_HANDLER_INVOKE ' + call + ') :: ptask_after*',
            call + '.RESUME = STRING_UNSET_CV_RANGE_WARNING_RESULT porigin_site z n_key ' + str(bits),
            '$error_call_valid(' + state + '_next, ' + call + ')',
            state + '_next.EVENTS = ' + state + '.EVENTS']
    return checks


def pending_mask_checks():
    checks = ['$integer_float_notices([RANGEWARNING], n_post) = [(2, n_message*)]',
        'pevent_range = DIAGNOSTIC "Warning" n_message* z']
    for mask in (0, 512):
        state = 'S_mask_' + str(mask)
        checks += [state + ' = S_P[.ERRORHANDLER.LEVELS = ' + str(mask) + ']',
            'PhpStep: ' + state + ' ~> ' + state + '_next',
            state + '_next = S_next[.ERRORHANDLER.LEVELS = ' + str(mask) + '][.EVENTS = S_P.EVENTS ++ [pevent_range]]',
            state + '_next.TODO = (THROW_SEARCH n_throwable) :: ptask_after*',
            state + '_next.OBJECTS[n_throwable] = S_P.OBJECTS[n_throwable]']
    return checks


def conditions(program, path):
    assert INDEX in (0, 3)
    prior.INDEX, prior.cases = INDEX, cases
    if PENDING_ONLY:
        checks = front_checks(program, path) + [
            'S_P.TODO = (THROW_SEARCH n_throwable) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_after*',
            'perrorcall_entered.RESUME = STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key',
            'S_P.OBJECTS[n_throwable] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception"',
            'S_P.ERRORHANDLER.CALLBACK = eps',
            'PhpStep: S_P ~> S_next',
            'S_next.TODO = (THROW_SEARCH n_throwable) :: ptask_after*',
            'S_next.ERRORHANDLER.CALLBACK = (pvalue_callback)',
            'S_next.EVENTS = S_P.EVENTS',
        ]
        changed = pending_mask_checks()
        return checks + changed, len(changed)
    if RANGE_ONLY:
        checks = front_checks(program, path) + [
            'S_P.TODO = (STRING_UNSET_BOOL_CV_WARNING_RESULT porigin_site z n_key) :: ptask_after*']
        changed = normal_range_checks()
        return checks + changed, len(changed)
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
        controls += pending_mask_checks()
        checks += controls
        derived += len(controls)
    else:
        controls = []
        for tag, bits in (('maximum_fit', 4890909195324358655),
                          ('minimum_fit', 14114281232179134464)):
            controls += ['$string_unset_bool_cv_post_normal_value(PFLOAT ' + str(bits) + ')']
        controls += normal_range_checks()
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
    RANGE_ONLY = '--range-only' in sys.argv
    if RANGE_ONLY:
        sys.argv.remove('--range-only')
        assert INDEX == 0
    PENDING_ONLY = '--pending-only' in sys.argv
    if PENDING_ONLY:
        sys.argv.remove('--pending-only')
        assert INDEX == 3 and not RANGE_ONLY
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
    report['scope'] = ('Only the two formerly refused pending mask0/512 controls now report the default Warning '
        'before retaining the identical Throwable and caller tail. Source0/native0; no closed whole run.' if PENDING_ONLY else
        'Only the two formerly refused eligible normal finite-OOB controls now dispatch a '
        'secondary Warning with their copied bits and complete caller tail. Old fitting/discard campaigns '
        'are not renewed; source0/native0, saved native reused.' if RANGE_ONLY else
        'Actual finite PFLOAT post-handler bits retain the saved ordinary BOOL-CV slot, '
        'no reference/released marker and whole-state quiet read. Normal Error or same pending Exception '
        'and callback restoration retain whole/split; fixture source0/native0 reuses only fresh FLOAT originals.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
