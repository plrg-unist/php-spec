#!/usr/bin/env python3
"""Completed emitted POWER NaNs carry exact consumer-only receipts."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_power_nan_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_unary_nan_instanceof_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
FLOAT_TWO = ('FLOAT', 4611686018427387904)
NANS = (
    ('NAN', 'POWER', ('FLOAT', 13830554455654793216), ('FLOAT_BINARY', 'DIVIDE', prior.prior.ONE, FLOAT_TWO, 4602678819172646912)),
    ('NAN', 'POWER', ('NAN', 'CONSTANT'), prior.prior.ONE),
    ('NAN', 'POWER', prior.prior.NANS[0], FLOAT_TWO),
    ('NAN', 'POWER', FLOAT_TWO, prior.prior.NANS[1]),
)
TREES = (
    ('CAST', 'CASTINT', ('IDENTICAL', ('INSTANCEOF', NANS[0], 'stdClass', 'PTPLAIN', 'stdClass'), prior.prior.FALSE, True), 'PINT 1'),
    ('BITNOT', ('CAST', 'CASTINT', ('INSTANCEOF', NANS[1], 'stdClass', 'PTFULL', 'stdClass'), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('INSTANCEOF', NANS[2], 'MissingStringRead\\Target', 'PTRELATIVE', 'MissingStringRead\\Target'), 'PINT 0'),
    ('BITNOT', ('ADD', ('CAST', 'CASTINT', ('INSTANCEOF', NANS[3], 'StringReadAlias', 'PTPLAIN', 'stdClass'), 'PINT 0'), ('COMPILED', 'PINT 3', ('ADD', 1, 2)), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[:2] != ('NAN', 'POWER'):
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    result = 'PFLOAT n_compiled_nan_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    checks += ['S.COMPLETION = NORMAL',
               '$pfshape(' + expression + ') = PFBINARY POWER expression_' + tag + '_0 expression_' + tag + '_1']
    children = []
    for index, child in enumerate(tree[2:]):
        child_tag = tag + '_' + str(index)
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + child_tag + ')',
                   '$origin_node(S.SOURCES, porigin_' + child_tag + ') = (expression_' + child_tag + ')',
                   '$compiled_precision(S, (porigin_' + child_tag + ')) = (14)']
        child_value = value(checks, child_tag, child)[0]
        number = 'pnumber_power_' + child_tag
        checks += ['$string_read_runtime_instanceof_operand(S, porigin_' + child_tag + ') = (' + child_value + ')',
                   '$coerce_number(' + child_value + ') = COERCED ' + number + ' false']
        children.append((child_value, number))
    checks += ['$power_prepare(' + children[0][1] + ', ' + children[1][1] + ') = POWERDONE (NFLOAT n_compiled_nan_' + tag + ') false',
               '$pfcast_nan(' + result + ')',
               '$binary_apply(S, POWER, ' + children[0][0] + ', ' + children[1][0] + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
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
    report['scope'] = 'Four current histories authenticate emitted POWER NaN operands through exact false CODE/read-eps, root/both-child source and equal captured precision. Proper recursive consumer operand certificates, quiet original typed coercions, POWERDONE(NFLOAT bits)false, genuine NaN results and unchanged full binary_apply under explicit NORMAL supply only the instanceof operand. Negative fractional powers and NaN in either operand retain general VALUE/BYTE refusal and warningful truth. Existing named-target authority, CONSTCONTEXTeps, whole resolve_at/class_instanceof and integer parents retain keys1/-1/0/-4, Warning, supplied throw, bounds, cleanup and budgets. GENERAL/Deprecated, wider producers/owners/lifetimes and all exact held boundaries remain outside. Native originals reused once; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
