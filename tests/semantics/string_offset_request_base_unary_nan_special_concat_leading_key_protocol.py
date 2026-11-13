#!/usr/bin/env python3
"""Quiet unary NaN VALUE retains source and exact pure result bits."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_unary_nan_special_concat_leading_key_cases as cases
import string_offset_request_base_arithmetic_nan_special_concat_leading_key_protocol as prior

runner, arithmetic, unary, floats = prior.runner, prior.arithmetic, prior.unary, prior.floats
BITS = 'n_unary_nan_bits'
VALUE = ('PFLOAT ' + BITS, 'NFLOAT ' + BITS, None)


def producer(checks, tag, operation, child):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
               expression + ' = ' + ('NExprUnaryPlus' if operation == 'POSITIVE' else 'NExprUnaryMinus') + ' ' + expression + '_child metadata_' + tag,
               '$pfshape(' + expression + ') = PFUNARY ' + operation + ' ' + expression + '_child',
               '$origin_child((' + origin + '), [PCFIELD 0]) = (' + origin + '_child)',
               '$origin_node(S.SOURCES, ' + origin + '_child) = (' + expression + '_child)',
               '$compiled_read(S, ' + origin + ') = (' + VALUE[0] + ')',
               '$compiled_precision(S, (' + origin + ')) = (14)',
               '$compiled_read(S, ' + origin + '_child) = (' + child[0] + ')',
               '$compiled_precision(S, (' + origin + '_child)) = (14)',
               '$compiled_comparison_number(S, ' + origin + '_child) = (' + child[1] + ')',
               '$(' + child[0][7:] + ' < 18446744073709551616)',
               '$fparts_nan($float_decode(' + child[0][7:] + '))',
               '$compiled_special_concat_bytes(S, ' + origin + '_child) = eps',
               '$coerce_number(' + child[0] + ') = COERCED (' + child[1] + ') false',
               '$unary_apply(S, ' + operation + ', ' + child[0] + ', 0) = S[.RESULT = KNOWN (' + VALUE[0] + ')]',
               '$(' + BITS + ' < 18446744073709551616)',
               '$fparts_nan($float_decode(' + BITS + '))',
               '$compiled_comparison_number(S, ' + origin + ') = (' + VALUE[1] + ')',
               '$compiled_special_concat_bytes(S, ' + origin + ') = eps',
               '$parser_literal_text_at(' + VALUE[0] + ', 14) = eps',
               '$number_text(' + VALUE[1] + ', 14) = ($ptascii("NAN"), true)']


def authority(index):
    operation = 'POSITIVE' if index in (0, 3) else 'NEGATIVE'
    child = prior.CONSTANT if index < 2 else prior.VALUE
    checks = []
    if index >= 2:
        checks += ['$number_binary(SUBTRACT, ' + floats.POSITIVE[1] + ', ' + floats.POSITIVE[1] + ') = NUM (' + prior.VALUE[1] + ')']
    checks += ['S_unary_nan_pure = $unary_apply(S, ' + operation + ', ' + child[0] + ', 0)',
               'S_unary_nan_pure.RESULT = KNOWN (' + VALUE[0] + ')',
               'S_unary_nan_pure = S[.RESULT = KNOWN (' + VALUE[0] + ')]',
               '$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_unary_nan_root)',
               r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        prior.comparison(checks, 'unary_nan_root', 'NOTIDENTICAL', VALUE, prior.CONSTANT, 'PBOOL true', '1')
        tag = 'unary_nan_root_l'
        prior.nan.nan(checks, 'unary_nan_root_r')
    elif index == 1:
        unary.unary(checks, 'unary_nan_root', 'NEGATIVE', 'PINT 1', 'NINT 1', 'PINT $(-1)', '-1', '1')
        prior.comparison(checks, 'unary_nan_root_child', 'SPACESHIP', VALUE,
                         ('PFLOAT 4609434218613702656', 'NFLOAT 4609434218613702656', '1.5'), 'PINT 1', '1')
        tag = 'unary_nan_root_child_l'
        prior.prior.scalar(checks, 'unary_nan_root_child_r', '4609434218613702656', '1.5')
    elif index == 2:
        arithmetic.binary(checks, 'unary_nan_root', 'NExprBinaryOpPlus', 'ADD',
                          'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        prior.comparison(checks, 'unary_nan_root_l', 'IDENTICAL', VALUE, prior.CONSTANT, 'PBOOL false', '')
        tag = 'unary_nan_root_l_l'
        prior.nan.nan(checks, 'unary_nan_root_l_r')
        arithmetic.constant(checks, 'unary_nan_root_r', 'false', '')
    else:
        unary.unary(checks, 'unary_nan_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'unary_nan_root_child', 'NExprBinaryOpMul', 'MULTIPLY',
                          'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        prior.comparison(checks, 'unary_nan_root_child_l', 'NOTEQUAL', VALUE,
                         ('PSTRING ($ptascii("NAN"))', '', 'NAN'), 'PBOOL true', '1')
        tag = 'unary_nan_root_child_l_l'
        prior.strings.string(checks, 'unary_nan_root_child_l_r', b'NAN')
        arithmetic.binary(checks, 'unary_nan_root_child_r', 'NExprBinaryOpPlus', 'ADD',
                          'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'unary_nan_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'unary_nan_root_child_r_r', 'E_WARNING', '2')
    producer(checks, tag, operation, child)
    if index < 2:
        prior.nan.nan(checks, tag + '_child')
    else:
        prior.producer(checks, tag + '_child', 'SUBTRACT', floats.POSITIVE, floats.POSITIVE)
        floats.constant(checks, tag + '_child_l')
        floats.constant(checks, tag + '_child_r')
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
    watched = [Path(module.__file__) for module in (prior, prior.prior, prior.nan, prior.strings, floats, arithmetic, unary, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, cases.OUTPUTS, conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic-source unary NaN fixtures retain actual +/- source, own and child reads, matching compile14 precision despite live17 and genuine valid NaN child VALUE. Exact quiet unary result bits bind before dependent comparison premises without a canonical payload assumption. Direct NaN ConstFetch and admitted arithmetic NaN children keep BYTE absent; strict/unordered comparisons feed quiet Boolean/integer ancestors. REQUEST owners, supplied throw, fixed bounds and budgets retain their laws. NaN BYTE, FLOAT NOT, binary arithmetic with NaN children, wider producers/ownership and held Source47 stay separate.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
