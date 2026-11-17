#!/usr/bin/env python3
"""Quiet false shorthand selection retains exact fallback tasks and NaN bits."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_arithmetic_nan_instanceof_special_concat_leading_key_protocol as arithmetic
import string_offset_request_base_runtime_unary_nan_instanceof_special_concat_leading_key_protocol as unary
import string_offset_request_base_runtime_false_shorthand_nan_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_full_ternary_nan_instanceof_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
FALSE, ZERO = arithmetic.FALSE, prior.ZERO
FLOAT_ZERO = ('FLOAT_BINARY', 'ADD', ('FLOAT', 0), ZERO, 0)
NANS = (
    ('NAN', 'SHORTHAND', FALSE, ('NAN', 'CONSTANT')),
    ('NAN', 'SHORTHAND', ZERO, arithmetic.NANS[1]),
    ('NAN', 'SHORTHAND', ('FLOAT_UNARY', 'NEGATIVE', FLOAT_ZERO, 9223372036854775808), unary.NANS[2]),
    ('NAN', 'SHORTHAND', FLOAT_ZERO, ('NAN', 'CASTFLOAT', ('NAN', 'CONSTANT'))),
)
TREES = (
    ('CAST', 'CASTINT', ('IDENTICAL', ('INSTANCEOF', NANS[0], 'stdClass', 'PTPLAIN', 'stdClass'), FALSE, True), 'PINT 1'),
    ('BITNOT', ('CAST', 'CASTINT', ('INSTANCEOF', NANS[1], 'stdClass', 'PTFULL', 'stdClass'), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('INSTANCEOF', NANS[2], 'MissingStringRead\\Target', 'PTRELATIVE', 'MissingStringRead\\Target'), 'PINT 0'),
    ('BITNOT', ('ADD', ('CAST', 'CASTINT', ('INSTANCEOF', NANS[3], 'StringReadAlias', 'PTPLAIN', 'stdClass'), 'PINT 0'), ('COMPILED', 'PINT 3', ('ADD', 1, 2)), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[:2] != ('NAN', 'SHORTHAND'):
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    checks += ['S.COMPLETION = NORMAL',
               '$pfshape(' + expression + ') = PFTERNARY ' + expression + '_0 ABSENT ' + expression + '_2']
    for index in (0, 2):
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + tag + '_' + str(index) + ')',
                   '$origin_node(S.SOURCES, porigin_' + tag + '_' + str(index) + ') = (' + expression + '_' + str(index) + ')',
                   '$compiled_precision(S, (porigin_' + tag + '_' + str(index) + ')) = (14)']
    condition = value(checks, tag + '_0', tree[2])[0]
    child = value(checks, tag + '_2', tree[3])[0]
    result, select = 'PFLOAT n_compiled_nan_' + tag, 'S_select_nan_' + tag
    checks += ['$string_read_runtime_value(S, porigin_' + tag + '_0) = (' + condition + ')',
               '~$truth(S, ' + condition + ')',
               '$truth_value(S, ' + condition + ', 5) = S[.RESULT = KNOWN (PBOOL false)]',
               '$string_read_runtime_instanceof_operand(S, porigin_' + tag + '_2) = (' + child + ')',
               result.removeprefix('PFLOAT ') + ' = ' + child.removeprefix('PFLOAT '),
               '$pfcast_nan(' + result + ')',
               '$resolve_at(S, KNOWN (' + result + '), 5) = S[.RESULT = KNOWN (' + result + ')]',
               select + ' = S[.ORIGIN = (' + origin + ')][.RESULT = KNOWN (' + condition + ')]',
               '$true_arm_line(' + select + ', ABSENT) = 0',
               '$select_value(' + select + ', ABSENT, ' + expression + '_2, 5, 0, 5) = ' + select + '[.TODO = [$at_task((porigin_' + tag + '_2), EVAL ' + expression + '_2), VALUE_COPY 5] ++ ' + select + '.TODO][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
               '$string_read_runtime_instanceof_operand(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_value(S, ' + origin + ') = eps',
               '$string_read_runtime_bytes(S, ' + origin + ') = eps']
    return result, None


module = prior
while module is not integers:
    module.value = value
    module = module.prior
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
    report['scope'] = 'Four histories authenticate emitted shorthand ternaries with an exact ABSENT true arm, NORMAL/root CODEfalse/read-eps/line, actual condition/fallback SOURCE and matching captured precision. Existing general VALUE certifies a quiet false Boolean/integer/signed-zero float condition; only the genuine selected recursive NaN supplies bits through whole resolve_at. Exact module51 select_value(ABSENT) has true-arm line0 and schedules only fallback AT(EVAL)/VALUE_COPY with original TODO and canonical RESULT/BASE. General VALUE/BYTE/NaN truth, owner/lifetime and all exact held boundaries remain unchanged. Saved natives reused once; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
