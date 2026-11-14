#!/usr/bin/env python3
"""Exact NULL casts retain typed values and existing source/owner guards."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_null_cast_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_coalesce_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
ONE, NULL, FALSE = prior.ONE, prior.NULL, prior.prior.FALSE
TREES = (
    ('POSITIVE', ('IDENTICAL', ('CAST', 'CASTBOOL', ('NULL_TERNARY',), 'PBOOL false'), FALSE, True), 1),
    ('BITNOT', ('CAST', 'CASTINT', ('SHORTHAND', FALSE, NULL, False), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('CAST', 'CASTFLOAT', ('COALESCE', ('NULL_TERNARY',), NULL), 'PFLOAT 0'), 'PINT 0'),
    ('BITNOT', ('ADD', ('CAST', 'CASTINT', NULL, 'PINT 0'), ('ADD', ONE, ('ADD', ONE, ONE, 2), 3), 3), -4),
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
    report['scope'] = 'Four actual emitted CASTBOOL/CASTINT/CASTFLOAT trees admit exact PNULL operands through the existing demanded source/CODEfalse/read-eps/positive-line/equal captured-precision and full-state cast_apply certificate. Full-ternary, shorthand, coalesce and raw compiled NULL retain typed false/int0/float+0; FLOAT VALUE keeps BYTE eps; exact emitted NULL retains certified empty BYTE. Existing source/owner/history builders are reused without a new evaluator. REQUEST keys1/-1/0/-4 preserve captured14/live17 precision, returning Warning owners, supplied Throwable identity, fixed bounds, cleanup and budget rejoining. Exactly three old scalar-cast helper negatives become NULL positives with unchanged guard count; the accepted old33/1792 campaign is not replayed. No compiler/cast/numeric/formatter/API/owner body or quiet-location expansion; saved natives reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
