#!/usr/bin/env python3
"""Emitted NULL empty bytes retain source authority and actual key carriers."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_null_bytes_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_null_cast_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
TRUTH, FALSE = prior.prior.prior.TRUTH, prior.FALSE
NULL = prior.NULL
TREES = (
    ('NULL_TERNARY',),
    ('SHORTHAND', FALSE, NULL, False),
    ('COALESCE', ('NULL_TERNARY',), NULL),
    ('TERNARY', TRUTH, NULL, True),
)
base_authority = integers.authority
value = prior.value


def authority(index):
    checks = base_authority(index)
    digits = ('1', '-1', '0', '-4')[index]
    old = '$compiled_read(S, porigin_runtime_right) = (' + ('PNULL' if index == 0 else 'PBOOL false') + ')'
    checks[checks.index(old)] = '$compiled_read(S, porigin_runtime_right) = (PSTRING ($ptascii(' + json.dumps(digits) + ')))'
    old = '$string_read_runtime_bytes(S, porigin_runtime_right) = (eps)'
    checks[checks.index(old)] = '$string_read_runtime_bytes(S, porigin_runtime_right) = ($ptascii(' + json.dumps(digits) + '))'
    checks += ['$compiled_identity_value(S, porigin_runtime_right) = (PSTRING ($ptascii(' + json.dumps(digits) + ')))',
               '$string_read_literal_bytes(expression_runtime_right) = ($ptascii(' + json.dumps(digits) + '))',
               '$compiled_read(S, porigin_operator) = eps',
               '$string_read_runtime_value(S, porigin_operator) = (PNULL)',
               '$string_read_runtime_bytes(S, porigin_operator) = (eps)',
               '$stringify(S, PNULL, 5) = S[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING eps)]']
    return checks


integers.authority, integers.TREES = authority, TREES
conditions = prior.conditions


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
    report['scope'] = 'Four emitted exact NULL full/shorthand/coalesce selections contribute certified empty BYTE (eps) through compiled-read-eps and the existing typed VALUE proof. Both nonempty outer concat operands retain the real authenticated REQUEST carrier, key bytes1x/-1x/0x/-4x and existing owners. Captured14/live17 precision, returning Warning, supplied Throwable, fixed bounds, cleanup and budget rejoining remain. Pure stringify retains its interned empty result and full state; FLOAT BYTE stays eps. Only direct old NULL BYTE expectations are promoted; historical source/state/native campaigns retain their identities. No formatter/compiler/cast/API/owner or held-boundary expansion; saved native originals reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
