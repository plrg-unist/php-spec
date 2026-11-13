#!/usr/bin/env python3
"""Number/string comparisons retain captured precision and exact raw bytes."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_number_string_comparison_special_concat_leading_key_cases as cases
import string_offset_request_base_numeric_comparison_special_concat_leading_key_protocol as prior
import string_offset_request_base_string_bitwise_special_concat_leading_key_protocol as strings

runner, arithmetic, unary = prior.runner, prior.arithmetic, prior.unary


def comparison(checks, tag, operation, number, raw, string_first, result, text):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    shape = {'LESS': 'Smaller', 'LESSEQUAL': 'SmallerOrEqual', 'GREATER': 'Greater',
             'GREATEREQUAL': 'GreaterOrEqual', 'EQUAL': 'Equal', 'NOTEQUAL': 'NotEqual',
             'SPACESHIP': 'Spaceship'}[operation]
    order = '$number_string_precision_order(' + number[1] + ', ' + strings.bytes_term(raw) + ', 14)'
    if string_first != (operation in ('GREATER', 'GREATEREQUAL')):
        order = '$(-' + order + ')'
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = NExprBinaryOp' + shape + ' ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (' + result + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$comparison_value(' + operation + ', ' + order + ') = ' + result,
        '$echo_value(' + result + ') = $ptascii(' + json.dumps(text) + ')',
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
    for field, suffix in ((0, '_l'), (1, '_r')):
        is_string = string_first == (field == 0)
        value = 'PSTRING ' + strings.bytes_term(raw) if is_string else number[0]
        payload = strings.bytes_term(raw) if is_string else '$ptascii(' + json.dumps(number[2]) + ')'
        checks += [
            '$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
            '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
            '$compiled_read(S, ' + origin + suffix + ') = (' + value + ')',
            '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
            '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = (' + payload + ')']
        if is_string:
            strings.string(checks, tag + suffix, raw)
        else:
            checks += ['$compiled_order_number(' + value + ') = (' + number[1] + ')',
                       '$number_text(' + number[1] + ', 14) = (' + payload + ', false)']


def integer(checks, tag):
    arithmetic.scalar(checks, tag, 'NScalarInt (INTEGER 10)', 'PINT 10', '10')


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_mixed_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    ten = ('PINT 10', 'NINT 10', '10')
    if index == 0:
        maximum = ('PINT 9223372036854775807', 'NINT 9223372036854775807', '9223372036854775807')
        comparison(checks, 'mixed_root', 'EQUAL', maximum, b'9223372036854775808', False, 'PBOOL true', '1')
        arithmetic.constant(checks, 'mixed_root_l', 'PHP_INT_MAX', '9223372036854775807')
        checks += ['$numeric_string($ptascii("9223372036854775808")) = FULLNUM (NFLOAT $float_of_int(9223372036854775808))',
                   '$num_compare(NINT 9223372036854775807, NFLOAT $float_of_int(9223372036854775808)) = 0',
                   '$string_order($ptascii("9223372036854775807"), $ptascii("9223372036854775808")) = $(-1)']
    elif index == 1:
        comparison(checks, 'mixed_root', 'SPACESHIP', ten, b'2tail', False, 'PINT $(-1)', '-1')
        integer(checks, 'mixed_root_l')
        checks += ['$numeric_string($ptascii("2tail")) = LEADNUM (NINT 2)',
                   '$number_string_precision_order(NINT 10, $ptascii("2tail"), 14) = $(-1)']
    elif index == 2:
        arithmetic.binary(checks, 'mixed_root', 'NExprBinaryOpPlus', 'ADD', 'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        number = ('PFLOAT 4607182418800017409', 'NFLOAT 4607182418800017409', '1')
        raw = b'1.0000000000000001x'
        comparison(checks, 'mixed_root_l', 'GREATER', number, raw, False, 'PBOOL false', '')
        prior.scalar(checks, 'mixed_root_l_l', '4607182418800017409', '1')
        arithmetic.constant(checks, 'mixed_root_r', 'false', '')
        checks += ['$numeric_string($ptascii("1.0000000000000001x")) = LEADNUM (NFLOAT $float_of_int(1))',
                   '$number_string_precision_order(NFLOAT 4607182418800017409, $ptascii("1.0000000000000001x"), 14) = $(-1)',
                   '$number_string_precision_order(NFLOAT 4607182418800017409, $ptascii("1.0000000000000001x"), 17) = 1',
                   '$number_text(NFLOAT 4607182418800017409, 17) = ($ptascii("1.0000000000000002"), false)']
    else:
        unary.unary(checks, 'mixed_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'mixed_root_child', 'NExprBinaryOpMul', 'MULTIPLY', 'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        comparison(checks, 'mixed_root_child_l', 'GREATEREQUAL', ten, b'2tail', True, 'PBOOL true', '1')
        integer(checks, 'mixed_root_child_l_r')
        arithmetic.binary(checks, 'mixed_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'mixed_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'mixed_root_child_r_r', 'E_WARNING', '2')
        checks += ['$numeric_string($ptascii("2tail")) = LEADNUM (NINT 2)',
                   '$number_string_precision_order(NINT 10, $ptascii("2tail"), 14) = $(-1)']
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
    report['scope'] = 'Four actual ordered-number/raw-PSTRING comparison fixtures retain own/child source/read facts, exact string BYTE payloads, quiet signed64 or valid64 nonNaN numbers and three matching compile14 precisions despite live17. Existing52 number_string_precision_order distinguishes numeric integer-overflow equality from both-string provenance and uses normalized lexical order for leading text. A FLOAT greater case changes at live17, proving captured compile14; reversed string/number greater-equal composes with arithmetic/unary ancestors. REQUEST owners, saved throw, fixed bounds and budgets retain prior laws. NaN, Boolean/null or owning coercions, runtime carriers and held Source47 remain outside this certificate.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
