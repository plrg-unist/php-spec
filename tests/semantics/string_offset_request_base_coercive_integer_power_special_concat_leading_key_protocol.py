#!/usr/bin/env python3
"""Quiet coerced integer powers retain genuine scalar children and exact BYTE."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_coercive_integer_power_special_concat_leading_key_cases as cases
import string_offset_request_base_power_float_special_concat_leading_key_protocol as prior

runner, arithmetic, unary, strings = prior.runner, prior.arithmetic, prior.unary, prior.prior.strings
TWO = ('PINT 2', 'NINT 2', '2')


def producer(checks, tag, left, right, result):
    expression, origin = 'expression_' + tag, 'porigin_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
               expression + ' = NExprBinaryOpPow ' + expression + '_l ' + expression + '_r metadata_' + tag,
               '$pfshape(' + expression + ') = PFBINARY POWER ' + expression + '_l ' + expression + '_r',
               '$parser_literal_at(' + expression + ', 14) = eps',
               '$compiled_read(S, ' + origin + ') = (PINT ' + str(result) + ')',
               '$long_range(' + str(result) + ')',
               '$compiled_precision(S, (' + origin + ')) = (14)',
               '$power_prepare(' + left[1] + ', ' + right[1] + ') = POWERDONE (NINT ' + str(result) + ') false',
               '$binary_apply(S, POWER, ' + left[0] + ', ' + right[0] + ', 0) = S[.RESULT = KNOWN (PINT ' + str(result) + ')]',
               '$compiled_comparison_number(S, ' + origin + ') = (NINT ' + str(result) + ')',
               '$compiled_special_concat_bytes(S, ' + origin + ') = ($ptascii(' + json.dumps(str(result)) + '))',
               '$type_bytes(' + left[0] + r') =/= $ptascii("int") \/ $type_bytes(' + right[0] + ') =/= $ptascii("int")']
    for field, suffix, (value, number, payload) in ((0, '_l', left), (1, '_r', right)):
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + origin + suffix + ')',
                   '$origin_node(S.SOURCES, ' + origin + suffix + ') = (' + expression + suffix + ')',
                   '$compiled_read(S, ' + origin + suffix + ') = (' + value + ')',
                   '$compiled_precision(S, (' + origin + suffix + ')) = (14)',
                   '$compiled_identity_value(S, ' + origin + suffix + ') = (' + value + ')',
                   '$coerce_number(' + value + ') = COERCED (' + number + ') false',
                   '$compiled_special_concat_bytes(S, ' + origin + suffix + ') = ($ptascii(' + json.dumps(payload) + '))']


def authority(index):
    left = (('PBOOL true', 'NINT 1', '1'), TWO, ('PNULL', 'NINT 0', ''), ('PSTRING ($ptascii("2"))', 'NINT 2', '2'))[index]
    right = ('PSTRING ($ptascii("0"))', 'NINT 0', '0') if index == 1 else TWO
    result = (1, 1, 0, 4)[index]
    checks = ['$power_prepare(' + left[1] + ', ' + right[1] + ') = POWERDONE (NINT ' + str(result) + ') false',
              '$origin_child((porigin_key), [PCFIELD 0, PCFIELD 0]) = (porigin_coercive_power_root)',
              r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17']
    if index in (1, 3):
        unary.unary(checks, 'coercive_power_root', 'NEGATIVE', 'PINT ' + str(result), 'NINT ' + str(result),
                    'PINT $(-' + str(result) + ')', '-' + str(result), str(result))
        tag = 'coercive_power_root_child'
    else:
        tag = 'coercive_power_root'
    producer(checks, tag, left, right, result)
    if index == 3:
        strings.string(checks, tag + '_l', b'2')
    else:
        arithmetic.constant(checks, tag + '_l', ('true', 'E_WARNING', 'null')[index], left[2])
    if index == 1:
        strings.string(checks, tag + '_r', b'0')
    else:
        arithmetic.constant(checks, tag + '_r', 'E_WARNING', '2')
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
    watched = [Path(module.__file__) for module in (prior, prior.prior, prior.prior.prior, strings, strings.prior, arithmetic, unary, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, cases.OUTPUTS, conditions
    passed = runner.main()
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic-source coerced PINT-result POWER fixtures retain actual own/child nodes and reads, three capture14 precisions despite live17, genuine scalar child identity VALUE/BYTE and both quiet NINT conversions. POWERDONE with a false diagnostic flag and the exact full binary state/result precede BYTE. At least one child is not PINT, separating the old strict arm. BOOL, NULL and full numeric raw-string operands retain distinct source facts. Existing REQUEST owners, supplied throw, fixed bounds and budgets keep their laws. FLOAT/overflow/general/Deprecated results, NaN BYTE, warningful/nonnumeric strings, owning/carrier operands and held Source47 remain separate. Fixtures have source0; native originals are reused once.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
