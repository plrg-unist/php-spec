#!/usr/bin/env python3
"""Source-reached literal Boolean Warning keys retain exact compiled identity."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_null_warning_protocol as null
import string_offset_nested_unset_bool_warning_cases as cases

INDEX = 0


def base(value):
    return 'BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE ($ptascii("base")) 5)) (KNOWN ' + value + ') 5) (KNOWN (PINT 7)) 5'


def conditions(program, path):
    null.INDEX = INDEX % 2
    checks, derived = null.conditions(program, path)
    literal = 'true' if INDEX < 2 else 'false'
    opposite = 'false' if INDEX < 2 else 'true'
    old = 'S.BASE = ' + base('PNULL')
    assert checks.count(old) == 1
    checks[checks.index(old)] = 'S.BASE = ' + base('(PBOOL ' + literal + ')')
    at = checks.index('$string_unset_warning_plan(S) = ((porigin_site, 5))') + 1
    checks[at:at] = [
        '$origin_child((porigin_site), [PCFIELD 0, PCFIELD 1]) = (porigin_key)',
        '$compiled_read(S, porigin_key) = (PBOOL ' + literal + ')',
        '$compiled_identity_value(S, porigin_key) = (PBOOL ' + literal + ')',
        *('$string_unset_warning_plan(S[.BASE = ' + base(value) + ']) = eps'
          for value in ('(PBOOL ' + opposite + ')', 'PNULL', '(PINT 0)', '(PINT 1)')),
    ]
    return checks, derived + 4


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(null.__file__), Path(null.cases.__file__), Path(cases.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in range(4)
    prior = null.prior
    prior.NAME = tuple(cases.CASES)[INDEX]
    prior.OUTPUT = cases.OUTPUTS[prior.NAME]
    prior.cases, prior.conditions, prior.recorded, prior.PREFIX = cases, conditions, null.recorded, null.PREFIX
    passed = prior.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    report_path = Path(sys.argv[sys.argv.index('--output') + 1]) / 'report.json'
    report = json.loads(report_path.read_bytes())
    report['inputs'].update(before)
    report['mode'], report['raw_unset_steps'] = 'SL', 1
    report['scope'] = ('Literal Boolean key matches its exact source/compiled-read/identity value, refusing '
        'opposite BOOL, NULL and INT0/1 before Warning dispatch. Genuine named USER return/throw, '
        'value-free source-bound Error resume or same-Exception discard, restored callback, no extra '
        'owners and whole/split budgets retain their bounds. Fixture source0/native0; saved originals reused.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
