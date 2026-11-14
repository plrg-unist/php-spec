#!/usr/bin/env python3
"""Selected full ternary values retain exact tasks and existing key owners."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_full_ternary_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_scalar_cast_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
ONE, ZERO = prior.prior.ONE, prior.prior.INTEGER_ZERO
TREES = (
    ('TERNARY', ('NOT', ('FLOAT', 0), True), ONE, True),
    ('TERNARY', ZERO, ('NEGATIVE', ('NOT', ('FLOAT', 0), True), -1), False),
    ('POSITIVE', ('IDENTICAL', ('TERNARY', ('FLOAT_BINARY', 'ADD', ('FLOAT', 0), ZERO, 0), ('FLOAT_BINARY', 'ADD', ('FLOAT', 4609434218613702656), ZERO, 4609434218613702656), False), ONE, False), 0),
    ('BITNOT', ('ADD', ('IDENTICAL', ('TERNARY', ONE, ('CAST', 'CASTFLOAT', ('NOT', ('FLOAT', 0), True), 'PFLOAT 4607182418800017408'), True), ('FLOAT', 4607182418800017408), True),
               ('ADD', ONE, ONE, 2), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] != 'TERNARY':
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    truth = str(tree[-1]).lower()
    selected, skipped = (1, 2) if tree[-1] else (2, 1)
    checks += ['$pfshape(' + expression + ') = PFTERNARY ' + expression + '_0 ' + expression + '_1 ' + expression + '_2']
    for index in range(3):
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + tag + '_' + str(index) + ')',
                   '$origin_node(S.SOURCES, porigin_' + tag + '_' + str(index) + ') = (' + expression + '_' + str(index) + ')']
    condition = value(checks, tag + '_0', tree[1])[0]
    result, number = value(checks, tag + '_' + str(selected), tree[2])
    checks += ['S.COMPLETION = NORMAL',
               '$truth(S, ' + condition + ') = ' + truth,
               '$truth_value(S, ' + condition + ', 5) = S[.RESULT = KNOWN (PBOOL ' + truth + ')]',
               '$pfshape(' + expression + '_' + str(skipped) + ') = PFBINARY DIVIDE expression_' + tag + '_skipped_left expression_' + tag + '_skipped_right',
               '$number_binary(DIVIDE, NINT 1, NINT 0) = DIVZERO',
               '$string_read_runtime_value(S, porigin_' + tag + '_' + str(skipped) + ') = eps',
               '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')']
    if result == 'PNULL' or result.startswith('PFLOAT '):
        checks += ['$string_read_runtime_bytes(S, ' + origin + ') = eps']
    else:
        checks += ['$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    select = 'S_select_' + tag
    checks += [select + ' = S[.ORIGIN = (' + origin + ')][.RESULT = KNOWN (' + condition + ')]',
               '$select_value(' + select + ', ' + expression + '_1, ' + expression + '_2, 5, 5, 5) = ' + select + '[.TODO = [$at_task((porigin_' + tag + '_' + str(selected) + '), EVAL ' + expression + '_' + str(selected) + '), VALUE_COPY 5] ++ ' + select + '.TODO][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]']
    return result, number


prior.value, prior.prior.value, prior.prior.prior.value, integers.value, integers.TREES = value, value, value, value, TREES
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
    report['scope'] = 'Four actual emitted full ternaries retain NORMAL/parent CODEfalse/read-eps/line, exact condition and both present arm SOURCE identities, equal parent/condition/selected precision, quiet full-state typed truth and only the selected recursive VALUE. Skipped divide-zero arms have no value certificate. Exact module51 select_value transitions preserve AT(selected EVAL), VALUE_COPY and cleared RESULT/BASE rather than pretending selection leaves state unchanged. Boolean/integer/float conditions and selected PINT/PFLOAT values retain types/bits, FLOAT BYTE eps and existing REQUEST keys1/-1/0/-4 with captured14/live17 precision, Warning owners, supplied Throwable, bounds/cleanup and inherited budget rejoining. Shorthand, compiler/static errors, new owner/formatter/API/kernel behavior remain separate; saved natives reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
