#!/usr/bin/env python3
"""Explicit casts consume exact literal string carriers without arithmetic notices."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_literal_string_cast_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_literal_string_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
TRUTH = ('NOT', ('FLOAT', 0), True)
TREES = (
    ('CAST', 'CASTINT', ('TERNARY', TRUTH, ('STRING', '1tail', None), True), 'PINT 1'),
    ('BITNOT', ('CAST', 'CASTINT', ('TERNARY', TRUTH, ('STRING', 'junk', None), True), 'PINT 0'), -1),
    ('POSITIVE', ('CAST', 'CASTBOOL', ('TERNARY', TRUTH, ('STRING', '0', None), True), 'PBOOL false'), 0),
    ('BITNOT', ('CAST', 'CASTINT', ('CAST', 'CASTFLOAT', ('TERNARY', TRUTH, ('STRING', '3.0tail', None), True), 'PFLOAT 4613937818241073152'), 'PINT 3'), -4),
)
value = prior.value
module = prior
while module is not integers:
    module.value = value
    module = module.prior
integers.value, integers.TREES = value, TREES


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    at = checks.index('$string_read_plan(S_found) = $string_read_plan(S_found[.COMPLETION = NORMAL])')
    checks[at] = '$string_read_plan(S_found) = eps'
    return checks, derived


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values())
               if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent}
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four emitted CASTINT/CASTBOOL/CASTFLOAT trees consume certified nonNUL literal-INTERNED string values selected by genuine full ternaries. Exact NORMAL/source/CODEfalse/read-eps/equal captured precision and original typed full-state cast_apply retain quiet explicit numeric-prefix/nonnumeric casts, exact Boolean zero-string truth and fitting nested FLOAT-to-INT conversion. Emitted FLOAT BYTE remains eps. BUDGET plans refuse before fixture-only guarded discovery; unchanged key Warning, supplied Throwable, bounds, ownership, cleanup and budget rejoining preserve REQUEST keys1/-1/0/-4. Arithmetic leading-string Warnings, integer/string-bitwise consumers, REQUEST/raw PSTRING inputs, other casts, compiler/formatter/owner bodies and every exact hold gain no authority. Saved native originals reused once; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
