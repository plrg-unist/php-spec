#!/usr/bin/env python3
"""Raw FLOAT Warning keys keep exact bits through the source-only continuation."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_null_warning_protocol as null
import string_offset_nested_unset_float_warning_cases as cases

INDEX = 2


def base(value):
    return 'BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE ($ptascii("base")) 5)) (KNOWN ' + value + ') 5) (KNOWN (PINT 7)) 5'


def conditions(program, path):
    null.INDEX = INDEX % 2
    checks, derived = null.conditions(program, path)
    bits = cases.KEY_BITS[tuple(cases.CASES)[INDEX]]
    old = 'S.BASE = ' + base('PNULL')
    assert checks.count(old) == 1
    checks[checks.index(old)] = 'S.BASE = ' + base('(PFLOAT ' + str(bits) + ')')
    at = checks.index('$string_unset_warning_plan(S) = ((porigin_site, 5))') + 1
    wrong = bits + 1 if bits < 9218868437227405312 else bits - 1
    checks[at:at] = [
        '$origin_child((porigin_site), [PCFIELD 0, PCFIELD 1]) = (porigin_key)',
        '$origin_node(S.SOURCES, porigin_key) = (NScalarFloat (FLOAT text_float) metadata_float)',
        '$hex_bits(text_float, 0) = ' + str(bits),
        '$compiled_read(S, porigin_key) = (PFLOAT ' + str(bits) + ')',
        '$compiled_identity_value(S, porigin_key) = (PFLOAT ' + str(bits) + ')',
        *('$string_unset_warning_plan(S[.BASE = ' + base(value) + ']) = eps'
          for value in ('(PFLOAT ' + str(wrong) + ')', 'PNULL', '(PBOOL true)', '(PINT 0)', '(PINT 1)')),
    ]
    controls = []
    for raw, value in (
        ('0000000000000000', 0), ('8000000000000000', 9223372036854775808),
        ('0000000000000001', 1), ('8000000000000001', 9223372036854775809),
    ):
        controls.append('$string_unset_warning_literal(NScalarFloat (FLOAT "' + raw + '") eps, PFLOAT ' + str(value) + ')')
    for raw, value in (
        ('7ff8000000000000', 9221120237041090560),
        ('7ff0000000000001', 9218868437227405313),
        ('10000000000000000', 18446744073709551616),
        ('3ff8000000000000', 4609434218613702657),
    ):
        controls.append('~$string_unset_warning_literal(NScalarFloat (FLOAT "' + raw + '") eps, PFLOAT ' + str(value) + ')')
    for value in ('PNULL', '(PBOOL true)', '(PINT 1)'):
        controls.append('~$string_unset_warning_literal(NScalarFloat (FLOAT "3ff0000000000000") eps, ' + value + ')')
    controls.append('~$string_unset_warning_literal(NExprUnaryMinus (NScalarFloat (FLOAT "0000000000000000") eps) eps, PFLOAT 9223372036854775808)')
    if INDEX == 2:
        assert program.count('"3ff8000000000000"') == 1
        zero = program.replace('"3ff8000000000000"', '"0000000000000000"')
        encoded = json.dumps(base64.b64encode(bytes(path)).decode())
        controls += [
            'S_zero_I = $php_run(' + zero + ', 0, ' + encoded + ')',
            'S_zero_found = $null_unset_seek(S_zero_I, 0, 2000)',
            '$null_unset_front(S_zero_found, 0)',
            'S_zero_E = S_zero_found[.COMPLETION = NORMAL]',
            'S_zero_E.BASE = ' + base('(PFLOAT 0)'),
            '$string_unset_warning_plan(S_zero_E) = ((porigin_zero, 5))',
            '$origin_child((porigin_zero), [PCFIELD 0, PCFIELD 1]) = (porigin_zero_key)',
            '$compiled_read(S_zero_E, porigin_zero_key) = (PFLOAT 0)',
            '$compiled_identity_value(S_zero_E, porigin_zero_key) = (PFLOAT 0)',
            '$string_unset_warning_plan(S_zero_E[.BASE = ' + base('(PFLOAT 1)') + ']) = eps',
        ]
    return checks + controls, derived + 5 + len(controls)


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(null.__file__), Path(null.cases.__file__), Path(cases.__file__)]
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    at = sys.argv.index('--index')
    INDEX = int(sys.argv[at + 1])
    del sys.argv[at:at + 2]
    assert INDEX in (2, 5)
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
    report['derived_zero_full_authentication'] = INDEX == 2
    report['scope'] = ('Raw nonNaN FLOAT source/compiled-read/identity and captured key retain exact bits, '
        'Warning handler return/throw and source-only resume. Derived ±zero/subnormal leaf positives, '
        'NaN/range/wrong-tag refusals and the fractional-return-only zero-AST full source/captured-key '
        'check are source0/native0, without zero/subnormal source agreement. Whole/split, handler restoration and no-owner bounds '
        'reuse only the fresh selected original; accepted NULL/BOOL cuts are not renewed.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
