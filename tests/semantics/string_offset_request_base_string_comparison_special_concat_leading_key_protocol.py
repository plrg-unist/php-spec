#!/usr/bin/env python3
"""Raw-string comparison facts preserve normalized and numeric-string order."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_string_comparison_special_concat_leading_key_cases as cases
import string_offset_request_base_numeric_comparison_special_concat_leading_key_protocol as prior
import string_offset_request_base_string_bitwise_special_concat_leading_key_protocol as strings

runner, arithmetic, unary = prior.runner, prior.arithmetic, prior.unary


def comparison(checks, tag, operation, left, right, result, text):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    shape = {'LESS': 'Smaller', 'LESSEQUAL': 'SmallerOrEqual', 'GREATER': 'Greater',
             'GREATEREQUAL': 'GreaterOrEqual', 'EQUAL': 'Equal', 'NOTEQUAL': 'NotEqual',
             'SPACESHIP': 'Spaceship'}[operation]
    ordered = (right, left) if operation in ('GREATER', 'GREATEREQUAL') else (left, right)
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = NExprBinaryOp' + shape + ' ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (' + result + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$comparison_value(' + operation + ', $string_order(' + strings.bytes_term(ordered[0]) + ', ' + strings.bytes_term(ordered[1]) + ')) = ' + result,
        '$echo_value(' + result + ') = $ptascii(' + json.dumps(text) + ')',
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
    for field, suffix, child in ((0, '_l', left), (1, '_r', right)):
        value = strings.bytes_term(child)
        checks += [
            '$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
            '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
            '$compiled_read(S, ' + origin + suffix + ') = (PSTRING ' + value + ')',
            '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
            '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = (' + value + ')']
        strings.string(checks, tag + suffix, child)


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_string_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        left, right = b'9223372036854775808', b'9223372036854775809'
        comparison(checks, 'string_root', 'LESS', left, right, 'PBOOL true', '1')
        number = 'NFLOAT $float_of_int(9223372036854775808)'
        for child in (left, right):
            checks += ['$numeric_string(' + strings.bytes_term(child) + ') = FULLNUM (' + number + ')',
                       '$string_integer_overflow(' + strings.bytes_term(child) + ') = 1']
        checks += ['$num_compare(' + number + ', ' + number + ') = 0',
                   '$string_numeric_fallback(' + strings.bytes_term(left) + ', ' + strings.bytes_term(right) + ', ' + number + ', ' + number + ')',
                   '$string_order(' + strings.bytes_term(left) + ', ' + strings.bytes_term(right) + ') = $(-1)']
    elif index == 1:
        comparison(checks, 'string_root', 'SPACESHIP', b'a', b'z', 'PINT $(-1)', '-1')
        checks += ['$numeric_string($ptascii("a")) = NOTNUMERIC',
                   '$numeric_string($ptascii("z")) = NOTNUMERIC',
                   '$ntbyte_compare($ptascii("a"), $ptascii("z")) = $(-1)']
    elif index == 2:
        arithmetic.binary(checks, 'string_root', 'NExprBinaryOpPlus', 'ADD', 'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        comparison(checks, 'string_root_l', 'NOTEQUAL', b'02', b'2', 'PBOOL false', '')
        arithmetic.constant(checks, 'string_root_r', 'false', '')
        checks += ['$numeric_string($ptascii("02")) = FULLNUM (NINT 2)',
                   '$numeric_string($ptascii("2")) = FULLNUM (NINT 2)',
                   '$ntbyte_compare($ptascii("02"), $ptascii("2")) = $(-1)']
    else:
        unary.unary(checks, 'string_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'string_root_child', 'NExprBinaryOpMul', 'MULTIPLY', 'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        comparison(checks, 'string_root_child_l', 'GREATEREQUAL', b'2tail', b'10tail', 'PBOOL true', '1')
        arithmetic.binary(checks, 'string_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'string_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'string_root_child_r_r', 'E_WARNING', '2')
        checks += ['$numeric_string($ptascii("2tail")) = LEADNUM (NINT 2)',
                   '$numeric_string($ptascii("10tail")) = LEADNUM (NINT 10)',
                   '$string_order($ptascii("2tail"), $ptascii("10tail")) = 1']
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
    report['scope'] = 'Four actual raw-PSTRING comparison fixtures authenticate both child source/read/exactBYTE payloads and three matching compile14 precisions despite live17. Existing52 string_order retains normalized lexical spaceship, full numeric equality, leading-text lexical order and integer-overflow provenance fallback when both floats round equal. Own PBOOL versus PINT results and reversed greater order compose with existing arithmetic/unary ancestors, REQUEST owners, saved throw, fixed bounds and budgets. Runtime carriers, mixed string/number or owning comparisons and other producers remain separate; no copied string-order algorithm, native evaluation fallback or Source47 expansion.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
