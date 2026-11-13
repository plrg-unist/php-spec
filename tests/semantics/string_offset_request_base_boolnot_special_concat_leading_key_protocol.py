#!/usr/bin/env python3
"""Non-float Boolean-not certificates retain actual Warning histories."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_boolnot_special_concat_leading_key_cases as cases
import string_offset_request_base_bool_null_unary_special_concat_leading_key_protocol as prior
import string_offset_request_base_numeric_string_concat_unary_special_concat_leading_key_protocol as strings

runner = prior.runner
arithmetic = prior.arithmetic


def boolnot(checks, tag, child, truth, literal=False):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    result, text = ('PBOOL false', '') if truth else ('PBOOL true', '1')
    checks += [
        '$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
        expression + ' = NExprBooleanNot ' + expression + '_child metadata_' + tag,
        '$origin_child((' + origin + '), [PCFIELD 0]) = (' + origin + '_child)',
        '$origin_node(S.SOURCES, ' + origin + '_child) = (' + expression + '_child)',
        '$compiled_precision(S, (' + origin + ')) = (14)',
        '$compiled_read(S, ' + origin + ') = (' + result + ')',
        '$parser_literal_at(' + expression + ', 14) = eps',
        '$truth(S, ' + child + ') = ' + str(truth).lower(),
        '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
    if literal:
        checks += ['$parser_literal_at(' + expression + '_child, 14) = (' + child + ')']
    else:
        checks += ['$parser_literal_at(' + expression + '_child, 14) = eps',
                   '$compiled_read(S, ' + origin + '_child) = (' + child + ')',
                   '$compiled_precision(S, (' + origin + '_child)) = (14)']


def authority(index):
    checks = ['$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_boolnot_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index == 0:
        boolnot(checks, 'boolnot_root', 'PSTRING ($ptascii("0"))', False, True)
        arithmetic.scalar(checks, 'boolnot_root_child', 'NScalarString (BYTES text_boolnot_zero)', 'PSTRING ($ptascii("0"))', '0')
    elif index == 1:
        prior.unary(checks, 'boolnot_root', 'NEGATIVE', 'PBOOL true', 'NINT 1', 'PINT $(-1)', '-1', '1')
        boolnot(checks, 'boolnot_root_child', 'PNULL', False)
        arithmetic.constant(checks, 'boolnot_root_child_child', 'null', '')
    elif index == 2:
        arithmetic.binary(checks, 'boolnot_root', 'NExprBinaryOpPlus', 'ADD', 'PBOOL false', 'PBOOL false', 'PINT 0', 'NINT 0', 'NINT 0', 'NINT 0')
        boolnot(checks, 'boolnot_root_l', 'PSTRING ($ptascii("1tail"))', True)
        strings.concat(checks, 'boolnot_root_l_child', '1tail', 'false', 'PBOOL false', '')
        arithmetic.constant(checks, 'boolnot_root_r', 'false', '')
        checks += ['$coerce_number(PSTRING ($ptascii("1tail"))) = COERCED (NINT 1) true']
    else:
        prior.unary(checks, 'boolnot_root', 'NEGATIVE', 'PINT 4', 'NINT 4', 'PINT $(-4)', '-4', '4')
        arithmetic.binary(checks, 'boolnot_root_child', 'NExprBinaryOpMul', 'MULTIPLY', 'PBOOL true', 'PINT 4', 'PINT 4', 'NINT 1', 'NINT 4', 'NINT 4')
        boolnot(checks, 'boolnot_root_child_l', 'PSTRING ($ptascii("0"))', False)
        strings.concat(checks, 'boolnot_root_child_l_child', '0', 'false', 'PBOOL false', '')
        arithmetic.binary(checks, 'boolnot_root_child_r', 'NExprBinaryOpPlus', 'ADD', 'PINT 2', 'PINT 2', 'PINT 4', 'NINT 2', 'NINT 2', 'NINT 4')
        arithmetic.constant(checks, 'boolnot_root_child_r_l', 'E_WARNING', '2')
        arithmetic.constant(checks, 'boolnot_root_child_r_r', 'E_WARNING', '2')
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
    watched = [Path(module.__file__) for module in (prior, strings, arithmetic, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.OUTPUTS = cases.OUTPUTS
    runner.conditions = conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four fresh Boolean-not source-state fixtures authenticate actual scalar truth and own PBOOL results. Literal zero-string truth differs from truthy nonnumeric text without numeric conversion. Certified null and mixed CONCAT children compose with unary/arithmetic ancestors while saved index, supplied throw, negative bounds and borrowed owners retain their existing laws. Float, array and object Boolean-not children remain outside the source certificate.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
