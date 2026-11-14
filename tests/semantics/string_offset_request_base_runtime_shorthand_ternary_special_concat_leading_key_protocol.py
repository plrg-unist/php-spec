#!/usr/bin/env python3
"""Shorthand selection retains original typed values and exact fallback tasks."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_shorthand_ternary_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_full_ternary_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
ONE, ZERO = prior.ONE, prior.ZERO
FRACTION = ('FLOAT_BINARY', 'ADD', ('FLOAT', 4609434218613702656), ZERO, 4609434218613702656)
NEGATIVE_ZERO = ('FLOAT_UNARY', 'NEGATIVE', ('FLOAT_BINARY', 'ADD', ('FLOAT', 0), ZERO, 0), 9223372036854775808)
TREES = (
    ('SHORTHAND', ('NOT', ('FLOAT', 0), True), None, True),
    ('SHORTHAND', ZERO, ('NEGATIVE', ('NOT', ('FLOAT', 0), True), -1), False),
    ('POSITIVE', ('IDENTICAL', ('SHORTHAND', FRACTION, None, True), ONE, False), 0),
    ('BITNOT', ('ADD', ('IDENTICAL', ('SHORTHAND', NEGATIVE_ZERO, ('CAST', 'CASTFLOAT', ('NOT', ('FLOAT', 0), True), 'PFLOAT 4607182418800017408'), False),
                                   ('FLOAT', 4607182418800017408), True),
               ('ADD', ONE, ONE, 2), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] != 'SHORTHAND':
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    truth = str(tree[-1]).lower()
    checks += ['$pfshape(' + expression + ') = PFTERNARY ' + expression + '_0 ABSENT ' + expression + '_2']
    for index in (0, 2):
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + tag + '_' + str(index) + ')',
                   '$origin_node(S.SOURCES, porigin_' + tag + '_' + str(index) + ') = (' + expression + '_' + str(index) + ')']
    condition, condition_number = value(checks, tag + '_0', tree[1])
    checks += ['S.COMPLETION = NORMAL',
               '$truth(S, ' + condition + ') = ' + truth,
               '$truth_value(S, ' + condition + ', 5) = S[.RESULT = KNOWN (PBOOL ' + truth + ')]']
    select = 'S_select_' + tag
    checks += [select + ' = S[.ORIGIN = (' + origin + ')][.RESULT = KNOWN (' + condition + ')]',
               '$true_arm_line(' + select + ', ABSENT) = 0']
    if tree[-1]:
        assert tree[2] is None
        result, number = condition, condition_number
        checks += ['$pfshape(' + expression + '_2) = PFBINARY DIVIDE expression_' + tag + '_skipped_left expression_' + tag + '_skipped_right',
                   '$number_binary(DIVIDE, NINT 1, NINT 0) = DIVZERO',
                   '$string_read_runtime_value(S, porigin_' + tag + '_2) = eps',
                   '$select_value(' + select + ', ABSENT, ' + expression + '_2, 5, 0, 5) = ' + select + '[.RESULT = KNOWN (' + result + ')][.BASE = BASE_VALUE (KNOWN PNULL)]']
    else:
        result, number = value(checks, tag + '_2', tree[2])
        checks += ['$select_value(' + select + ', ABSENT, ' + expression + '_2, 5, 0, 5) = ' + select + '[.TODO = [$at_task((porigin_' + tag + '_2), EVAL ' + expression + '_2), VALUE_COPY 5] ++ ' + select + '.TODO][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]']
    checks += ['$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = ' +
               ('eps' if result.startswith('PFLOAT ') else '($echo_value(' + result + '))')]
    return result, number


prior.value, prior.prior.value, prior.prior.prior.value, prior.prior.prior.prior.value, integers.value, integers.TREES = value, value, value, value, value, TREES
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
    report['scope'] = 'Four emitted shorthand ternaries retain exact ABSENT true arms, NORMAL/parent CODEfalse/read-eps/line, condition and fallback SOURCE identities, equal captured precision only for demanded values, and quiet full-state typed truth. Truthy BOOL/FLOAT retain the original value with no task growth; falsey PINT0/FLOAT-0 schedule the exact fallback AT(EVAL)/VALUE_COPY and clear RESULT/BASE. FLOAT VALUE keeps BYTE eps. Real REQUEST keys1/-1/0/-4 preserve captured14/live17 precision, Warning owners, supplied Throwable identity, fixed bounds/cleanup and inherited budget rejoining. No compiler/schema/formatter/API/kernel/owner expansion; saved natives reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
