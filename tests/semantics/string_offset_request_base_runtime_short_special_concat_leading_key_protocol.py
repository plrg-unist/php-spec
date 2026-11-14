#!/usr/bin/env python3
"""Emitted AND/OR retains selected truth, skipped tasks and Warning state."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_short_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_xor_special_concat_leading_key_protocol as prior

runner = prior.runner
ZERO, INF = prior.prior.ZERO, prior.prior.INF
ONE, INTEGER_ZERO = prior.ONE, prior.INTEGER_ZERO
TREES = (
    ('SHORT', True, ZERO, None, True, True),
    ('NEGATIVE', ('SHORT', False, ONE, ('FLOAT', 9218868437227405312), True, True), -1),
    ('POSITIVE', ('SHORT', False, INF, None, False, False), 0),
    ('BITNOT', ('ADD', ('SHORT', True, INF, ONE, False, True),
               ('ADD', ('SHORT', False, ZERO, ONE, True, True),
                ('SHORT', True, INTEGER_ZERO, ZERO, False, True), 2), 3), -4),
)
base_value = prior.prior.value


def value(checks, tag, tree):
    if tree[0] != 'SHORT':
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    boolean_or, left_truth, result_truth = (str(bit).lower() for bit in (tree[1], *tree[4:]))
    left_result, result = 'PBOOL ' + left_truth, 'PBOOL ' + result_truth
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    prior.prior.emitted(checks, tag)
    checks += ['$pfshape(' + expression + ') = PFSHORT ' + boolean_or + ' ' + expression + '_0 ' + expression + '_1']
    for index in range(2):
        child_tag = tag + '_' + str(index)
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + child_tag + ')',
                   '$origin_node(S.SOURCES, porigin_' + child_tag + ') = (expression_' + child_tag + ')']
    left = value(checks, tag + '_0', tree[2])[0]
    checks += ['S.COMPLETION = NORMAL',
               '$truth(S, ' + left + ') = ' + left_truth,
               '$truth_value(S, ' + left + ', 5) = S[.RESULT = KNOWN (' + left_result + ')]']
    beginning = 'S_short_' + tag
    checks += [beginning + ' = S[.ORIGIN = (' + origin + ')][.RESULT = KNOWN (' + left + ')]']
    if tree[3] is None:
        assert tree[1] == tree[4] == tree[5]
        checks += ['$pfshape(' + expression + '_1) = PFBINARY DIVIDE expression_' + tag + '_numerator expression_' + tag + '_denominator',
                   '$string_read_runtime_value(S, porigin_' + tag + '_1) = eps',
                   '$short_result(' + beginning + ', ' + boolean_or + ', ' + expression + '_1, 5, 5) = ' + beginning + '[.RESULT = KNOWN (' + result + ')][.BASE = BASE_VALUE (KNOWN PNULL)]']
    else:
        assert tree[1] != tree[4]
        right = value(checks, tag + '_1', tree[3])[0]
        checks += ['$truth(S, ' + right + ') = ' + result_truth,
                   '$truth_value(S[.RESULT = KNOWN (' + left_result + ')], ' + right + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
                   '$short_result(' + beginning + ', ' + boolean_or + ', ' + expression + '_1, 5, 5) = ' + beginning + '[.TODO = [$at_task($origin_child(' + beginning + '.ORIGIN, [PCFIELD 1]), EVAL ' + expression + '_1), TRUTH_RESULT false 5] ++ ' + beginning + '.TODO][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]']
    checks += ['$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    return result, '1' if tree[-1] else '0'


prior.prior.value, prior.prior.TREES = value, TREES
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
    report['scope'] = 'Four actual emitted Boolean/Logical AND/OR trees retain recursive quiet PFLOAT/PBOOL/PINT values and exact sequential full-state truth conversions. Decisive left values preserve Boolean results without certifying or evaluating the error-producing right child; demanded right values retain genuine typed source/CODE/read/precision authority. Both actual child SOURCE identities and own NORMAL/CODEfalse/read-eps/precision remain required. Direct existing51 short_result fixture checks distinguish skipped RHS from the exact right EVAL/TRUTH_RESULT tasks and reset BASE, without asserting unchanged whole-state short_result or inventing binary_apply. Existing REQUEST keys1/-1/0/-4, Warning owners, supplied Throwable, fixed bounds, cleanup and guarded-frontier zero/one-step budget rejoining remain. No runtime state normalization, new leaf, NaN truth, runtime FLOAT producer/BYTE, compiler/schema/API/50/51/387/kernel/owner expansion; natives reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
