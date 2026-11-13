#!/usr/bin/env python3
"""Quiet FLOAT ConstFetch bytes retain source, value and compile precision."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_float_const_special_concat_leading_key_cases as cases
import string_offset_request_base_numeric_comparison_special_concat_leading_key_protocol as prior
import string_offset_request_base_identity_special_concat_leading_key_protocol as identity

runner, arithmetic, unary = prior.runner, prior.arithmetic, prior.unary
INF, NINF = '9218868437227405312', '18442240474082181120'
POSITIVE = ('PFLOAT ' + INF, 'NFLOAT ' + INF, 'INF')
NEGATIVE = ('PFLOAT ' + NINF, 'NFLOAT ' + NINF, '-INF')


def constant(checks, tag):
    arithmetic.constant(checks, tag, 'INF', 'INF')
    checks += [
        '$compiled_read(S, porigin_' + tag + ') = (PFLOAT ' + INF + ')',
        '$compiled_precision(S, (porigin_' + tag + ')) = (14)',
        '$compiled_order_number(PFLOAT ' + INF + ') = (NFLOAT ' + INF + ')',
        '$(' + INF + ' < 18446744073709551616)',
        '~$fparts_nan($float_decode(' + INF + '))',
        '$number_text(NFLOAT ' + INF + ', 14) = ($ptascii("INF"), false)',
        '$parser_literal_text_at(PFLOAT ' + INF + ', 14) = ($ptascii("INF"))']


def negative(checks, tag):
    unary.unary(checks, tag, 'NEGATIVE', POSITIVE[0], POSITIVE[1], NEGATIVE[0], '-INF', 'INF')
    constant(checks, tag + '_child')


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_float_const_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        prior.comparison(checks, 'float_const_root', 'GREATER', POSITIVE,
                         ('PFLOAT 4609434218613702656', 'NFLOAT 4609434218613702656', '1.5'),
                         'PBOOL true', '1')
        constant(checks, 'float_const_root_l')
        prior.scalar(checks, 'float_const_root_r', '4609434218613702656', '1.5')
    elif index == 1:
        prior.comparison(checks, 'float_const_root', 'SPACESHIP', NEGATIVE, POSITIVE, 'PINT $(-1)', '-1')
        negative(checks, 'float_const_root_l')
        constant(checks, 'float_const_root_r')
    elif index == 2:
        arithmetic.binary(checks, 'float_const_root', 'NExprBinaryOpPlus', 'ADD',
                          'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        identity.identity(checks, 'float_const_root_l', 'NOTIDENTICAL', POSITIVE[0], POSITIVE[0], False, 'INF', 'INF')
        constant(checks, 'float_const_root_l_l')
        constant(checks, 'float_const_root_l_r')
        arithmetic.constant(checks, 'float_const_root_r', 'false', '')
    else:
        unary.unary(checks, 'float_const_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'float_const_root_child', 'NExprBinaryOpMul', 'MULTIPLY',
                          'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        prior.comparison(checks, 'float_const_root_child_l', 'GREATEREQUAL', POSITIVE, NEGATIVE, 'PBOOL true', '1')
        constant(checks, 'float_const_root_child_l_l')
        negative(checks, 'float_const_root_child_l_r')
        arithmetic.binary(checks, 'float_const_root_child_r', 'NExprBinaryOpPlus', 'ADD',
                          'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'float_const_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'float_const_root_child_r_r', 'E_WARNING', '2')
    return checks


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    old = prior.authority(index)
    at = checks.index(old[0])
    assert checks[at:at + len(old)] == old
    checks[at:at + len(old)] = authority(index)
    return checks, derived


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (prior, identity, prior.prior, arithmetic, unary, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, cases.OUTPUTS, conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four genuine-source infinity ConstFetch fixtures retain actual own FLOAT reads, source names and compile14 precision despite live17. Valid64 nonNaN infinity has a quiet exact formatter. Negative infinity is the existing unary result; typed comparison and strict infinity identity feed quiet Boolean/integer ancestors. Existing REQUEST owners, supplied throw, fixed bounds and budgets remain. NaN BYTE, raw-string constant providers, arithmetic NaN, runtime carriers, ownership and held Source47 stay separate. Compiler-proved pool authority is unchanged; derived pool mutations do not validate arbitrary inputs.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
