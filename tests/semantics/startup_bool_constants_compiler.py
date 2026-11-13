#!/usr/bin/env python3
"""Actual build-Boolean occurrences preserve fold and fallback distinctions."""
import hashlib
import json
from pathlib import Path
import sys

import startup_float_constants_compiler as runner
import startup_bool_constants_cases as cases

original_conditions = runner.conditions


def conditions(program, checked, name, source, baseline):
    checks = original_conditions(program, checked, name, source, baseline)
    if name == 'boundaries' and not baseline:
        # The false left of && prunes its RHS; both source nodes remain authentic.
        parent = [('INDEX', 0), ('FIELD', 0), ('INDEX', 2), ('FIELD', 0)]
        right = runner.occurrences.path_term(parent + [('FIELD', 1)])
        lookup = '$ppconstant_at((pcpath_value, pvalue)*, ' + right + ')'
        expected = lookup + ' = (PBOOL false)'
        assert checks.count(expected) == 1
        checks[checks.index(expected)] = lookup + ' = eps'
        checks.append('$ppconstant_at((pcpath_value, pvalue)*, ' +
                      runner.occurrences.path_term(parent) + ') = (PBOOL false)')
    return checks


if __name__ == '__main__':
    own = Path(__file__).resolve()
    before = hashlib.sha256(own.read_bytes()).hexdigest()
    runner.cases, runner.VALUES = cases, cases.VALUES
    runner.conditions = conditions
    passed = runner.main()
    assert hashlib.sha256(own.read_bytes()).hexdigest() == before
    output = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(output.read_bytes())
    report['inputs'][str(own.relative_to(runner.ROOT))] = before
    report['constants'] = list(cases.VALUES)
    output.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
