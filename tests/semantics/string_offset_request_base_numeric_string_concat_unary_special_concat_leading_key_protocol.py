#!/usr/bin/env python3
"""Quiet mixed-CONCAT string children preserve unary and Warning histories."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_numeric_string_concat_unary_special_concat_leading_key_cases as cases
import string_offset_request_base_bool_null_unary_special_concat_leading_key_protocol as prior

runner = prior.runner
arithmetic = prior.arithmetic


def concat(checks, tag, literal, spelling, value, right_text):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    checks += [
        expression + ' = NExprBinaryOpConcat ' + expression + '_l ' + expression + '_r metadata_' + tag,
        '$origin_child((' + origin + '), [PCFIELD 0]) = (' + origin + '_l)',
        '$origin_child((' + origin + '), [PCFIELD 1]) = (' + origin + '_r)',
        '$origin_node(S.SOURCES, ' + origin + '_l) = (' + expression + '_l)',
        expression + '_l = NScalarString (BYTES text_' + tag + '_l) metadata_' + tag + '_l',
        '$base64(text_' + tag + '_l) = $ptascii(' + json.dumps(literal) + ')',
        '$compiled_special_concat_bytes(S, ' + origin + '_l) = ($ptascii(' + json.dumps(literal) + '))',
        '$origin_node(S.SOURCES, ' + origin + '_r) = (' + expression + '_r)',
        expression + '_r = NExprConstFetch name_' + tag + '_r metadata_' + tag + '_r',
        '$ptast(name_' + tag + '_r) = PTNAME PTPLAIN ($ptascii(' + json.dumps(spelling) + '))',
        '$compiled_read(S, ' + origin + '_r) = (' + value + ')',
        '$compiled_special_concat_bytes(S, ' + origin + '_r) = ($ptascii(' + json.dumps(right_text) + '))']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_string_unary)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index < 3:
        operation = 'NEGATIVE' if index == 1 else 'POSITIVE'
        text, number = ('01', 'NINT 1') if index == 0 else (' 1', 'NINT 1') if index == 1 else ('0', 'NINT 0')
        result, result_text = ('PINT 1', '1') if index == 0 else ('PINT $(-1)', '-1') if index == 1 else ('PINT 0', '0')
        child = 'PSTRING ($ptascii(' + json.dumps(text) + '))'
        prior.unary(checks, 'string_unary', operation, child, number, result, result_text, text)
        literal, spelling, value, right_text = ('0', 'true', 'PBOOL true', '1') if index == 0 else (' 1', 'null', 'PNULL', '') if index == 1 else ('0', 'false', 'PBOOL false', '')
        concat(checks, 'string_unary_child', literal, spelling, value, right_text)
        checks += ['$type_bytes(' + child + ') = $ptascii("string")']
    else:
        prior.unary(checks, 'string_unary', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'string_unary_child', 'NExprBinaryOpMul', 'MULTIPLY', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        prior.unary(checks, 'string_unary_child_l', 'POSITIVE', 'PSTRING ($ptascii("2"))', 'NINT 2', 'PINT 2', '2', '2')
        concat(checks, 'string_unary_child_l_child', '2', 'false', 'PBOOL false', '')
        arithmetic.constant(checks, 'string_unary_child_r', 'E_WARNING', '2')
    return checks


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    old = prior.authority(index)
    at = checks.index(old[0])
    assert checks[at:at + len(old)] == old
    checks[at:at + len(old)] = authority(index)
    return checks, derived


if __name__ == '__main__':
    assert cases.OUTPUTS == prior.cases.OUTPUTS
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (prior, arithmetic, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.OUTPUTS = cases.OUTPUTS
    runner.conditions = conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four fresh numeric mixed-CONCAT string unary source-state fixtures authenticate actual literal bytes, bool/null facts, recursive child certificates, own values and matched compiled precision. Explicit COERCEDfalse and exact pure unary results preserve leading-zero/space typing, signed/zero indices, supplied throw, nested arithmetic and fixed negative bounds with existing borrowed-owner/budget laws. Native originals are reused once; previous campaigns retain separate cuts.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
