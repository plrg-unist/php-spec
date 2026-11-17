#!/usr/bin/env python3
"""Reached arithmetic NaN CVs use the existing source-only FLOAT continuation."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_float_cv_warning_protocol as floating
import string_offset_nested_unset_nan_cv_warning_cases as cases

INDEX = 3


def conditions(program, path):
    floating.INDEX = INDEX
    checks, derived = floating.conditions(program, path)
    prior_name = tuple(floating.cases.CASES)[INDEX]
    old = 'S.STORE[n_key] = DEFINED (PFLOAT ' + str(floating.cases.KEY_BITS[prior_name]) + ')'
    assert checks.count(old) == 1
    at = checks.index(old)
    checks[at:at + 1] = [
        'S.STORE[n_key] = DEFINED (PFLOAT n_nan)',
        '$(n_nan < 18446744073709551616)',
        '$fparts_nan($float_decode(n_nan))',
    ]
    assert sum(check.count('S.EVENTS = eps') for check in checks) == 1
    checks = [check.replace('S.EVENTS = eps',
        r'$nested_unset_outputs(S.EVENTS) = $ptascii("N:1;") /\ $nested_unset_diagnostics(S.EVENTS) = eps') for check in checks]
    old = '$nested_unset_outputs(S_done.EVENTS) = $ptascii("' + floating.cases.OUTPUTS[prior_name].decode() + '")'
    new = '$nested_unset_outputs(S_done.EVENTS) = $ptascii("' + cases.OUTPUTS[tuple(cases.CASES)[INDEX]].decode() + '")'
    assert checks.count(old) == 1
    checks[checks.index(old)] = new
    return checks, derived


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(floating.__file__), Path(floating.null.__file__),
               Path(floating.null.cases.__file__), Path(cases.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (1, 3)
    runner = floating.null.prior
    runner.NAME = tuple(cases.CASES)[INDEX]
    runner.OUTPUT = cases.OUTPUTS[runner.NAME]
    runner.cases, runner.conditions = cases, conditions
    runner.recorded, runner.PREFIX = floating.null.recorded, floating.PREFIX
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Actual arithmetic NaN FLOAT-CV entry is range-checked and classified without '
        'payload-sign assumptions, with genuine N:1 strict-self observer before Warning. Object-return '
        'and arithmetic-throw preserve source-only resume/discard, no added roots or secondary diagnostic, '
        'same Throwable/restoration and whole/split. Constructed boundaries remain derived source0/native0; '
        'only fresh saved NaN originals are reused, without nonNaN source/state renewal.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
