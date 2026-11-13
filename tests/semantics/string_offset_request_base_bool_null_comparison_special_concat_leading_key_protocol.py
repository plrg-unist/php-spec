#!/usr/bin/env python3
"""Boolean/null comparisons retain the null/string exception and quiet truth."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_bool_null_comparison_special_concat_leading_key_cases as cases
import string_offset_request_base_numeric_comparison_special_concat_leading_key_protocol as prior
import string_offset_request_base_string_bitwise_special_concat_leading_key_protocol as strings

runner, arithmetic, unary = prior.runner, prior.arithmetic, prior.unary


def comparison(checks, tag, operation, left, right, result, text):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    shape = {'LESS': 'Smaller', 'LESSEQUAL': 'SmallerOrEqual', 'GREATER': 'Greater',
             'GREATEREQUAL': 'GreaterOrEqual', 'EQUAL': 'Equal', 'NOTEQUAL': 'NotEqual',
             'SPACESHIP': 'Spaceship'}[operation]
    ordered = (right[0], left[0]) if operation in ('GREATER', 'GREATEREQUAL') else (left[0], right[0])
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = NExprBinaryOp' + shape + ' ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (' + result + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$comparison_value(' + operation + ', $scalar_plain_order(S, ' + ordered[0] + ', ' + ordered[1] + ')) = ' + result,
        '$echo_value(' + result + ') = $ptascii(' + json.dumps(text) + ')',
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
    for field, suffix, (value, payload) in ((0, '_l', left), (1, '_r', right)):
        checks += [
            '$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
            '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
            '$compiled_read(S, ' + origin + suffix + ') = (' + value + ')',
            '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
            '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($ptascii(' + json.dumps(payload) + '))']
        if value.startswith(('PINT ', 'PFLOAT ')):
            checks += ['$compiled_order_number(' + value + ') =/= eps']
        elif not value.startswith('PSTRING '):
            checks += [value + ' <- [PNULL, PBOOL false, PBOOL true]']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_bool_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    zero = ('PSTRING ($ptascii("0"))', '0')
    if index == 0:
        comparison(checks, 'bool_root', 'EQUAL', ('PBOOL false', ''), zero, 'PBOOL true', '1')
        arithmetic.constant(checks, 'bool_root_l', 'false', '')
        strings.string(checks, 'bool_root_r', b'0')
        checks += ['$truth(S, PBOOL false) = false', '$truth(S, PSTRING ($ptascii("0"))) = false',
                   '$scalar_plain_order(S, PBOOL false, PSTRING ($ptascii("0"))) = 0']
    elif index == 1:
        comparison(checks, 'bool_root', 'SPACESHIP', ('PNULL', ''), zero, 'PINT $(-1)', '-1')
        arithmetic.constant(checks, 'bool_root_l', 'null', '')
        strings.string(checks, 'bool_root_r', b'0')
        checks += ['$null_string_pair(PNULL, PSTRING ($ptascii("0")))',
                   '$bool_order($truth(S, PNULL), $truth(S, PSTRING ($ptascii("0")))) = 0',
                   '$scalar_plain_order(S, PNULL, PSTRING ($ptascii("0"))) = $(-1)']
    elif index == 2:
        arithmetic.binary(checks, 'bool_root', 'NExprBinaryOpPlus', 'ADD', 'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        comparison(checks, 'bool_root_l', 'NOTEQUAL', ('PBOOL true', '1'), ('PSTRING ($ptascii("text"))', 'text'), 'PBOOL false', '')
        arithmetic.constant(checks, 'bool_root_l_l', 'true', '1')
        strings.string(checks, 'bool_root_l_r', b'text')
        arithmetic.constant(checks, 'bool_root_r', 'false', '')
        checks += ['$truth(S, PSTRING ($ptascii("text"))) = true']
    else:
        unary.unary(checks, 'bool_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'bool_root_child', 'NExprBinaryOpMul', 'MULTIPLY', 'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        comparison(checks, 'bool_root_child_l', 'GREATEREQUAL', ('PFLOAT 0', '0'), ('PNULL', ''), 'PBOOL true', '1')
        prior.scalar(checks, 'bool_root_child_l_l', '0', '0')
        arithmetic.constant(checks, 'bool_root_child_l_r', 'null', '')
        arithmetic.binary(checks, 'bool_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'bool_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'bool_root_child_r_r', 'E_WARNING', '2')
        checks += ['$number_text(NFLOAT 0, 14) = ($ptascii("0"), false)',
                   '$scalar_plain_order(S, PFLOAT 0, PNULL) = 0',
                   '$scalar_plain_order(S, PNULL, PFLOAT 0) = 0']
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
    watched = [Path(module.__file__) for module in (prior, strings, strings.prior, arithmetic, unary, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, cases.OUTPUTS, conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four actual quiet BOOL/NULL-priority comparison fixtures retain own/child source/read facts, exact raw-string BYTE payloads or ordered nonNaN numeric reads, recursive quiet BYTE and three matching compile14 precisions despite live17. Existing52 scalar_plain_order distinguishes false versus string0 truth equality from NULL versus nonempty string0 order, and preserves true/text equality and reversed zero-FLOAT/NULL greater-equal. Under the required BOOL/NULL domain its live-precision number/string formatting branch is unreachable. Typed own Boolean/spaceship integer results compose with existing arithmetic/unary ancestors, REQUEST owners, saved throw, fixed bounds and budgets. NaN operands, runtime carriers, owning values and held Source47 remain separate.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
