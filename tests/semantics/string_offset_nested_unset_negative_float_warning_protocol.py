#!/usr/bin/env python3
"""Unary-minus FLOAT keys authenticate child bits and the folded captured key."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_nested_unset_null_warning_protocol as null
import string_offset_nested_unset_negative_float_warning_cases as cases

INDEX = 2


def base(value):
    return 'BASE_DIM (BASE_DIM (BASE_VALUE (VARIABLE ($ptascii("base")) 5)) (KNOWN ' + value + ') 5) (KNOWN (PINT 7)) 5'


def literal(raw, value):
    return '$string_unset_warning_literal(NExprUnaryMinus (NScalarFloat (FLOAT "' + raw + '") eps) eps, ' + value + ')'


def conditions(program, path):
    null.INDEX = INDEX % 2
    checks, derived = null.conditions(program, path)
    name = tuple(cases.CASES)[INDEX]
    bits, child = cases.KEY_BITS[name], cases.CHILD_BITS[name]
    old = 'S.BASE = ' + base('PNULL')
    assert checks.count(old) == 1
    checks[checks.index(old)] = 'S.BASE = ' + base('(PFLOAT ' + str(bits) + ')')
    at = checks.index('$string_unset_warning_plan(S) = ((porigin_site, 5))') + 1
    checks[at:at] = [
        '$origin_child((porigin_site), [PCFIELD 0, PCFIELD 1]) = (porigin_key)',
        '$origin_node(S.SOURCES, porigin_key) = (NExprUnaryMinus (NScalarFloat (FLOAT text_float) metadata_float) metadata_minus)',
        '$origin_child((porigin_key), [PCFIELD 0]) = (porigin_child)',
        '$origin_node(S.SOURCES, porigin_child) = (NScalarFloat (FLOAT text_float) metadata_float)',
        '$hex_bits(text_float, 0) = ' + str(child),
        '$compiled_read(S, porigin_key) = (PFLOAT ' + str(bits) + ')',
        '$compiled_identity_value(S, porigin_key) = (PFLOAT ' + str(bits) + ')',
    ]
    controls = [
        *('$string_unset_warning_plan(S[.BASE = ' + base(value) + ']) = eps'
          for value in ('(PFLOAT ' + str(child) + ')', '(PFLOAT ' + str(bits - 1) + ')',
                        'PNULL', '(PBOOL true)', '(PINT 0)', '(PINT 1)')),
        '~' + literal(format(child, '016x'), '(PFLOAT ' + str(child) + ')'),
        '~' + literal(format(child + 1, '016x'), '(PFLOAT ' + str(bits) + ')'),
    ]
    if INDEX == 2:
        for raw in (0, 1, 0x8000000000000000, 0x8000000000000001,
                    0x000fffffffffffff, 0x7fefffffffffffff, 0xfff0000000000000):
            controls.append(literal(format(raw, '016x'), '(PFLOAT ' + str(raw ^ (1 << 63)) + ')'))
        for raw in (0x7ff8000000000000, 0x7ff0000000000001,
                    0xfff8000000000000, 0xfff0000000000001, 1 << 64):
            controls.append('~' + literal(format(raw, '016x'), '(PFLOAT ' + str((raw + (1 << 63)) % (1 << 64)) + ')'))
        for value in ('PNULL', '(PBOOL true)', '(PINT (-1))', '(PFLOAT 18446744073709551616)'):
            controls.append('~' + literal('3ff0000000000000', value))
        controls += [
            '~$string_unset_warning_literal(NExprUnaryPlus (NScalarFloat (FLOAT "3ff0000000000000") eps) eps, PFLOAT 4607182418800017408)',
            '~$string_unset_warning_literal(NExprUnaryMinus (NExprUnaryMinus (NScalarFloat (FLOAT "3ff0000000000000") eps) eps) eps, PFLOAT 4607182418800017408)',
            '~$string_unset_warning_literal(NExprUnaryMinus (NScalarInt (INTEGER 1) eps) eps, PINT (-1))',
        ]
        assert program.count('"3ff8000000000000"') == 1
        zero = program.replace('"3ff8000000000000"', '"0000000000000000"')
        encoded = json.dumps(base64.b64encode(bytes(path)).decode())
        controls += [
            'S_zero_I = $php_run(' + zero + ', 0, ' + encoded + ')',
            'S_zero_found = $null_unset_seek(S_zero_I, 0, 2000)',
            '$null_unset_front(S_zero_found, 0)',
            'S_zero_E = S_zero_found[.COMPLETION = NORMAL]',
            'S_zero_E.BASE = ' + base('(PFLOAT 9223372036854775808)'),
            '$string_unset_warning_plan(S_zero_E) = ((porigin_zero, 5))',
            '$origin_child((porigin_zero), [PCFIELD 0, PCFIELD 1]) = (porigin_zero_key)',
            '$compiled_read(S_zero_E, porigin_zero_key) = (PFLOAT 9223372036854775808)',
            '$compiled_identity_value(S_zero_E, porigin_zero_key) = (PFLOAT 9223372036854775808)',
            '$string_unset_warning_plan(S_zero_E[.BASE = ' + base('(PFLOAT 0)') + ']) = eps',
        ]
    return checks + controls, derived + len(controls)


if __name__ == '__main__':
    own = Path(__file__).resolve()
    watched = [own, Path(null.__file__), Path(null.cases.__file__), Path(cases.__file__), Path(cases.raw.__file__)]
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
    report['derived_negative_zero_full_authentication'] = INDEX == 2
    report['scope'] = ('Unary-minus raw nonNaN FLOAT child/source, folded read/identity and captured-key equality; '
        'actual named Warning handler return/throw, value-free resume, exact producer tail and whole/split budgets. '
        'Derived leaf boundaries, wrong sign/child/tag, NaN/range refusals and return-only negative-zero AST '
        'authentication are source0/native0; accepted raw FLOAT/NULL/BOOL evidence is not renewed.')
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
