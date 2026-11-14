#!/usr/bin/env python3
"""Selected literal strings supply bytes through exact typed selector authority."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_literal_string_bytes_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_literal_string_cast_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
ZERO = prior.prior.ZERO
TREES = (
    ('SHORTHAND', ('TERNARY', prior.TRUTH, ('STRING', '1', '1'), True), None, True),
    ('TERNARY', ZERO, ('STRING', '-1', '$(-1)'), False),
    ('COALESCE', ('TERNARY', prior.TRUTH, ('STRING', '0', '0'), True), None),
    ('SHORTHAND', ('COALESCE', ('NULL_TERNARY',), ('STRING', '0', '0')), ('STRING', '-4', '$(-4)'), False),
)
integers.TREES = TREES
value, conditions = prior.value, prior.conditions


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
    report['scope'] = 'Four emitted full/shorthand ternary and ordinary coalesce trees preserve certified nonNUL literal-INTERNED STRING bytes. Exact compiled-read absence, typed VALUE carrier and canonical nonNUL bytes retain selector NORMAL/source/CODE/read/line/captured-precision and quiet truth/nullness authority; compiled-leaf BYTE remains disjoint. Truthy shorthand, false full selection, nonnull falsey zero-string coalesce and NULL-to-zero-string-to-falsey-shorthand fallback preserve real REQUEST keys1/-1/0/-4 through unchanged CONCAT, returning Warning, supplied Throwable, bounds, cleanup and budget rejoining. Emitted FLOAT BYTE, REQUEST/NUL/wider STRING producers, formatter/compiler/owner bodies and every exact hold gain no authority. Saved native originals reused once; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
