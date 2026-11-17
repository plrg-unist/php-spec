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
