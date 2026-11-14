#!/usr/bin/env python3
"""Emitted unary NaNs carry exact consumer-only source and state receipts."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_unary_nan_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_arithmetic_nan_instanceof_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
NANS = tuple(('NAN', 'UNARY', operation, child)
             for operation, child in zip(('POSITIVE', 'NEGATIVE', 'POSITIVE', 'NEGATIVE'), prior.NANS))
TREES = (
    ('CAST', 'CASTINT', ('IDENTICAL', ('INSTANCEOF', NANS[0], 'stdClass', 'PTPLAIN', 'stdClass'), prior.FALSE, True), 'PINT 1'),
    ('BITNOT', ('CAST', 'CASTINT', ('INSTANCEOF', NANS[1], 'stdClass', 'PTFULL', 'stdClass'), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('INSTANCEOF', NANS[2], 'MissingStringRead\\Target', 'PTRELATIVE', 'MissingStringRead\\Target'), 'PINT 0'),
    ('BITNOT', ('ADD', ('CAST', 'CASTINT', ('INSTANCEOF', NANS[3], 'StringReadAlias', 'PTPLAIN', 'stdClass'), 'PINT 0'), ('COMPILED', 'PINT 3', ('ADD', 1, 2)), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[:2] != ('NAN', 'UNARY'):
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    operation, child = tree[2:]
    result, state = 'PFLOAT n_compiled_nan_' + tag, 'S_unary_nan_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    checks += ['S.COMPLETION = NORMAL',
               '$pfshape(' + expression + ') = PFUNARY ' + operation + ' expression_' + tag + '_0',
               '$origin_child((' + origin + '), [PCFIELD 0]) = (porigin_' + tag + '_0)',
               '$origin_node(S.SOURCES, porigin_' + tag + '_0) = (expression_' + tag + '_0)',
               '$compiled_precision(S, (porigin_' + tag + '_0)) = (14)']
    child_value = value(checks, tag + '_0', child)[0]
    checks += ['$string_read_runtime_instanceof_operand(S, porigin_' + tag + '_0) = (' + child_value + ')',
               '$pfcast_nan(' + child_value + ')',
               '$coerce_number(' + child_value + ') = COERCED (NFLOAT n_compiled_nan_' + tag + '_0) false',
               state + ' = $unary_apply(S, ' + operation + ', ' + child_value + ', 5)',
               state + '.RESULT = KNOWN (' + result + ')',
               '$pfcast_nan(' + result + ')',
               state + ' = S[.RESULT = KNOWN (' + result + ')]',
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
    report['scope'] = 'Four current histories authenticate emitted POSITIVE/NEGATIVE NaN operands through exact false CODE/read-eps, root/child source and equal captured precision. A proper recursive consumer-only child certificate, intrinsically quiet FLOAT coercion, genuine NaN child/result and unchanged full unary_apply under explicit NORMAL supply only the instanceof operand. General VALUE, BYTE and warningful truth remain absent for the unary NaN result. Existing named-target authority, CONSTCONTEXTeps, whole resolve_at/class_instanceof and integer parents retain keys1/-1/0/-4, Warning, supplied throw, bounds, cleanup and budgets. No numeric, compiler, formatter, ownership, lifecycle or exact held-boundary changes. Native originals reused once; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
