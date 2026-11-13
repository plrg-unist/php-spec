#!/usr/bin/env python3
"""Typed string-byte certificates retain exact leading-key Warning histories."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_string_bitwise_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_power_special_concat_leading_key_protocol as prior

runner = prior.runner


def bytes_term(data):
    return '([' + ', '.join(map(str, data)) + '])' if data else '$ptascii("")'


def string(checks, tag, data):
    value = bytes_term(data)
    checks += [
        'expression_' + tag + ' = NScalarString (BYTES text_' + tag + ') metadata_' + tag,
        '$base64(text_' + tag + ') = ' + value,
        '$parser_literal_at(expression_' + tag + ', 14) = (PSTRING ' + value + ')',
        '$compiled_special_concat_bytes(S, porigin_' + tag + ') = (' + value + ')']


def binary(checks, tag, operation, left, right, result):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    shape, helper = {'BITAND': ('BitwiseAnd', 'string_and'), 'BITOR': ('BitwiseOr', 'string_or'),
                     'BITXOR': ('BitwiseXor', 'string_xor')}[operation]
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = NExprBinaryOp' + shape + ' ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (PSTRING ' + bytes_term(result) + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$' + helper + '(' + bytes_term(left) + ', ' + bytes_term(right) + ') = ' + bytes_term(result),
        '$compiled_special_concat_bytes(S, ' + origin + ') = (' + bytes_term(result) + ')']
    for field, suffix, child in ((0, '_l', left), (1, '_r', right)):
        checks += [
            '$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
            '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
            '$compiled_read(S, ' + origin + suffix + ') = (PSTRING ' + bytes_term(child) + ')',
            '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
            '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = (' + bytes_term(child) + ')']


def bitnot(checks, tag, child, result):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = NExprBitwiseNot ' + expression + '_child metadata_' + tag,
        '$pfshape(' + expression + ') = PFBITNOT ' + expression + '_child',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$compiled_read(S, ' + origin + ') = (PSTRING ' + bytes_term(result) + ')',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$origin_child((' + origin + '), [PCFIELD 0]) = (' + origin + '_child)',
        '$origin_node(S.SOURCES, ' + origin + '_child) = (' + expression + '_child)',
        '$compiled_read(S, ' + origin + '_child) = (PSTRING ' + bytes_term(child) + ')',
        '$compiled_precision(S, (' + origin + '_child)) = (14)',
        '$compiled_special_concat_bytes(S, ' + origin + '_child) = (' + bytes_term(child) + ')',
        '$string_not(' + bytes_term(child) + ') = ' + bytes_term(result),
        '$compiled_special_concat_bytes(S, ' + origin + ') = (' + bytes_term(result) + ')']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_byte_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index < 3:
        operation, left, right, result = (
            ('BITAND', b'1', b'3', b'1'), ('BITOR', b'-', b'\0' + b'1', b'-1'),
            ('BITXOR', b'1', b'\x01', b'0'))[index]
        binary(checks, 'byte_root', operation, left, right, result)
        string(checks, 'byte_root_l', left)
        string(checks, 'byte_root_r', right)
    else:
        bitnot(checks, 'byte_root', b'\xd2\xcb', b'-4')
        string(checks, 'byte_root_child', b'\xd2\xcb')
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
    watched = [Path(module.__file__) for module in (prior, prior.prior, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.OUTPUTS = cases.OUTPUTS
    runner.conditions = conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four actual exact-PSTRING byte NOT/AND/OR/XOR source-state fixtures retain exact byte results, OR unequal-length tail, NUL/control/high bytes in operands and non-NUL leading keys. Own and actual child PSTRING reads, source occurrences, recursive certificates and matching compiled precisions are explicit. Early05 string helpers supply byte results without numeric conversion or later54 dispatch. Existing REQUEST owners, supplied throw, fixed bounds and budgets retain prior laws; mixed integer/coercive operations and wider histories remain separate core obligations.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
