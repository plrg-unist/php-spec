#!/usr/bin/env python3
"""Selected full-ternary NaNs retain exact tasks and consumer-only values."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_arithmetic_nan_instanceof_special_concat_leading_key_protocol as arithmetic
import string_offset_request_base_runtime_unary_nan_instanceof_special_concat_leading_key_protocol as unary
import string_offset_request_base_runtime_full_ternary_nan_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_nonnull_nan_coalesce_instanceof_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
fixture_recorded = runner.recorded
runner.recorded = lambda command, stem, cap: fixture_recorded(command, stem, 360)
TRUTH, FALSE = ('NOT', ('FLOAT', 0), True), arithmetic.FALSE
ONE, ZERO = ('POSITIVE', TRUTH, 1), ('POSITIVE', FALSE, 0)
NANS = (
    ('NAN', 'TERNARY', TRUTH, ('NAN', 'CONSTANT'), True),
    ('NAN', 'TERNARY', ZERO, arithmetic.NANS[1], False),
    ('NAN', 'TERNARY', ('FLOAT_BINARY', 'ADD', ('FLOAT', 0), ONE, 4607182418800017408), unary.NANS[2], True),
    ('NAN', 'TERNARY', ('FLOAT_BINARY', 'ADD', ('FLOAT', 0), ZERO, 0), prior.NANS[3], False),
)
TREES = (
    ('CAST', 'CASTINT', ('IDENTICAL', ('INSTANCEOF', NANS[0], 'stdClass', 'PTPLAIN', 'stdClass'), FALSE, True), 'PINT 1'),
    ('BITNOT', ('CAST', 'CASTINT', ('INSTANCEOF', NANS[1], 'stdClass', 'PTFULL', 'stdClass'), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('INSTANCEOF', NANS[2], 'MissingStringRead\\Target', 'PTRELATIVE', 'MissingStringRead\\Target'), 'PINT 0'),
    ('BITNOT', ('ADD', ('CAST', 'CASTINT', ('INSTANCEOF', NANS[3], 'StringReadAlias', 'PTPLAIN', 'stdClass'), 'PINT 0'), ('COMPILED', 'PINT 3', ('ADD', 1, 2)), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[:2] != ('NAN', 'TERNARY'):
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    checks += ['S.COMPLETION = NORMAL',
               '$pfshape(' + expression + ') = PFTERNARY ' + expression + '_0 ' + expression + '_1 ' + expression + '_2']
    for index in range(3):
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + tag + '_' + str(index) + ')',
                   '$origin_node(S.SOURCES, porigin_' + tag + '_' + str(index) + ') = (' + expression + '_' + str(index) + ')']
    truth = str(tree[-1]).lower()
    selected = str(1 if tree[-1] else 2)
    checks += ['$compiled_precision(S, (porigin_' + tag + '_0)) = (14)',
               '$compiled_precision(S, (porigin_' + tag + '_' + selected + ')) = (14)']
    condition = value(checks, tag + '_0', tree[2])[0]
    child = value(checks, tag + '_' + selected, tree[3])[0]
    result, select = 'PFLOAT n_compiled_nan_' + tag, 'S_select_nan_' + tag
    checks += ['$string_read_runtime_value(S, porigin_' + tag + '_0) = (' + condition + ')',
               '$truth(S, ' + condition + ') = ' + truth,
               '$truth_value(S, ' + condition + ', 5) = S[.RESULT = KNOWN (PBOOL ' + truth + ')]',
               '$string_read_runtime_instanceof_operand(S, porigin_' + tag + '_' + selected + ') = (' + child + ')',
               result.removeprefix('PFLOAT ') + ' = ' + child.removeprefix('PFLOAT '),
               '$pfcast_nan(' + result + ')',
               '$resolve_at(S, KNOWN (' + result + '), 5) = S[.RESULT = KNOWN (' + result + ')]',
               select + ' = S[.ORIGIN = (' + origin + ')][.RESULT = KNOWN (' + condition + ')]',
               '$select_value(' + select + ', ' + expression + '_1, ' + expression + '_2, 5, 5, 5) = ' + select + '[.TODO = [$at_task((porigin_' + tag + '_' + selected + '), EVAL ' + expression + '_' + selected + '), VALUE_COPY 5] ++ ' + select + '.TODO][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
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
    report['scope'] = 'Four histories authenticate emitted FULL ternaries through exact NORMAL/root CODEfalse/read-eps/positive-line, condition and both arm SOURCE, parent/condition/selected captured precision, quiet full-state condition truth and only the selected recursive consumer NaN certificate. Exact selected bits, full resolve_at and module51 select_value tasks preserve VALUE_COPY, TODO and canonical RESULT/BASE without demanding skipped division, leading conversion or NaN truth. General VALUE/BYTE/NaN truth remain unchanged; named target authority and integer parents preserve keys1/-1/0/-4, Warning owners, supplied throw, bounds, cleanup and budgets. Shorthand/NaN conditions, wider producers/owners/lifetimes and every exact hold remain partial. Native originals reused once; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
