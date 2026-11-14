#!/usr/bin/env python3
"""Quiet FLOAT arithmetic retains exact VALUE bits without a BYTE receipt."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_float_arithmetic_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_short_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.prior.prior
ONE, INTEGER_ZERO = prior.ONE, prior.INTEGER_ZERO
FLOAT_ZERO = ('FLOAT', 0)
FLOAT_ONE = ('FLOAT', 4607182418800017408)
FLOAT_HALF = ('FLOAT', 4602678819172646912)
FLOAT_ONE_HALF = ('FLOAT', 4609434218613702656)
TREES = (
    ('NOT', ('FLOAT_BINARY', 'ADD', INTEGER_ZERO, ('FLOAT', 9223372036854775808), 0), True),
    ('NEGATIVE', ('IDENTICAL', ('FLOAT_BINARY', 'SUBTRACT', ONE, FLOAT_ONE, 0), FLOAT_ZERO, True), -1),
    ('POSITIVE', ('IDENTICAL', ('FLOAT_BINARY', 'MULTIPLY', ONE, FLOAT_ONE_HALF, 4609434218613702656), ONE, False), 0),
    ('BITNOT', ('ADD', ('IDENTICAL', ('FLOAT_BINARY', 'DIVIDE', FLOAT_ONE, ('ADD', ONE, ONE, 2), 4602678819172646912), FLOAT_HALF, True),
               ('ADD', ('IDENTICAL', ('FLOAT_BINARY', 'ADD', prior.ZERO, FLOAT_ZERO, 4607182418800017408), FLOAT_ONE, True),
                ('IDENTICAL', ('FLOAT_BINARY', 'SUBTRACT', FLOAT_ONE, ONE, 0), FLOAT_ZERO, True), 2), 3), -4),
)
base_value = integers.value


def numeric(value):
    if value.startswith('PFLOAT '):
        return 'NFLOAT ' + value.removeprefix('PFLOAT ')
    if value.startswith('PINT '):
        return 'NINT ' + value.removeprefix('PINT ')
    assert value in ('PBOOL false', 'PBOOL true')
    return 'NINT ' + str(int(value == 'PBOOL true'))


def value(checks, tag, tree):
    kind = tree[0]
    if kind not in ('FLOAT', 'NOT', 'FLOAT_BINARY', 'IDENTICAL'):
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    if kind == 'FLOAT':
        result = 'PFLOAT ' + str(tree[1])
        truth = str(tree[1] not in (0, 9223372036854775808)).lower()
        checks += ['$compiled_read(S, ' + origin + ') = (' + result + ')',
                   '$compiled_identity_value(S, ' + origin + ') = (' + result + ')',
                   '$compiled_precision(S, (' + origin + ')) = (14)',
                   '$number_bool(' + numeric(result) + ') = (' + truth + ', false)',
                   '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')']
        return result, None
    integers.emitted(checks, tag)
    children = tree[2:4] if kind == 'FLOAT_BINARY' else tree[1:2] if kind == 'NOT' else tree[1:3]
    operator = tree[1] if kind == 'FLOAT_BINARY' else kind
    shape = 'PFNOT' if kind == 'NOT' else 'PFBINARY ' + operator
    checks += ['$pfshape(' + expression + ') = ' + shape + ' ' + ' '.join(expression + '_' + str(index) for index in range(len(children)))]
    operands = []
    for index, child in enumerate(children):
        child_tag = tag + '_' + str(index)
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + child_tag + ')']
        operands.append(value(checks, child_tag, child)[0])
    if kind == 'FLOAT_BINARY':
        result = 'PFLOAT ' + str(tree[-1])
        truth = str(tree[-1] not in (0, 9223372036854775808)).lower()
        checks += ['S.COMPLETION = NORMAL']
        for operand in operands:
            checks += ['$coerce_number(' + operand + ') = COERCED (' + numeric(operand) + ') false']
        checks += ['$number_binary(' + operator + ', ' + numeric(operands[0]) + ', ' + numeric(operands[1]) + ') = NUM (' + numeric(result) + ')',
                   '$number_bool(' + numeric(result) + ') = (' + truth + ', false)',
                   '$binary_apply(S, ' + operator + ', ' + operands[0] + ', ' + operands[1] + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
                   '$string_read_runtime_bytes(S, ' + origin + ') = eps']
    else:
        result = 'PBOOL ' + str(tree[-1]).lower()
        if kind == 'NOT':
            truth = str(not tree[-1]).lower()
            checks += ['$truth(S, ' + operands[0] + ') = ' + truth,
                       '$truth_value(S, ' + operands[0] + ', 5) = S[.RESULT = KNOWN (PBOOL ' + truth + ')]']
        else:
            checks += ['$strict_identical(' + operands[0] + ', ' + operands[1] + ') = ' + str(tree[-1]).lower(),
                       '$strict_check(S, ' + operands[0] + ', ' + operands[1] + ', eps) = COMPARED ' + str(tree[-1]).lower(),
                       '$binary_apply(S, IDENTICAL, ' + operands[0] + ', ' + operands[1] + ', 5) = S[.RESULT = KNOWN (' + result + ')]']
        checks += ['$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    checks += ['$string_read_runtime_value(S, ' + origin + ') = (' + result + ')']
    return result, None if kind == 'FLOAT_BINARY' else '1' if tree[-1] else '0'


integers.value, integers.TREES = value, TREES
conditions = prior.conditions


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values())
               if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent}
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four actual emitted ADD/SUBTRACT/MULTIPLY/DIVIDE FLOAT-result trees retain actual NORMAL/source/CODEfalse/read-eps/equal captured precision, recursive PFLOAT/PBOOL/PINT operands, quiet numeric coercions, pure exact NUM(NFLOAT bits), valid non-NaN result truth and unchanged full-state binary_apply. Each runtime FLOAT subtree proves VALUE bits and BYTE eps; existing NOT and strict identity consume the typed result and only Boolean/integer ancestors gain bytes. Signed zero, 1.5 versus PINT1 and exact fractional0.5 preserve type and bits. Captured14/live17 precision, real REQUEST keys1/-1/0/-4, Warning owners, same supplied Throwable, fixed bounds, cleanup and inherited guarded-frontier zero/one-step budget rejoining retain existing laws. No runtime state normalization, runtime FLOAT BYTE, NaN truth, primitive/compiler/schema/API/387/kernel/owner expansion; natives reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
