#!/usr/bin/env python3
"""Emitted arithmetic NaNs carry exact consumer-only source and state receipts."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_arithmetic_nan_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_compiled_nan_instanceof_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
FALSE, TRUTH = prior.FALSE, prior.prior.TRUTH
ZERO = ('CAST', 'CASTFLOAT', FALSE, 'PFLOAT 0')
ONE = ('CAST', 'CASTFLOAT', TRUTH, 'PFLOAT 4607182418800017408')
NANS = (
    ('NAN', 'EMITTED', 'MULTIPLY', ZERO, ('FLOAT', 9218868437227405312)),
    ('NAN', 'EMITTED', 'SUBTRACT', ZERO, ('NAN', 'CONSTANT')),
    ('NAN', 'EMITTED', 'DIVIDE', ONE, ('NAN', 'CONSTANT')),
    ('NAN', 'EMITTED', 'ADD', ZERO, ('NAN', 'CONSTANT')),
)
TREES = (
    ('CAST', 'CASTINT', ('IDENTICAL', ('INSTANCEOF', NANS[0], 'stdClass', 'PTPLAIN', 'stdClass'), FALSE, True), 'PINT 1'),
    ('BITNOT', ('CAST', 'CASTINT', ('INSTANCEOF', NANS[1], 'stdClass', 'PTFULL', 'stdClass'), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('INSTANCEOF', NANS[2], 'MissingStringRead\\Target', 'PTRELATIVE', 'MissingStringRead\\Target'), 'PINT 0'),
    ('BITNOT', ('ADD', ('CAST', 'CASTINT', ('INSTANCEOF', NANS[3], 'StringReadAlias', 'PTPLAIN', 'stdClass'), 'PINT 0'), ('COMPILED', 'PINT 3', ('ADD', 1, 2)), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[:2] != ('NAN', 'EMITTED'):
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    operation, left, right = tree[2:]
    result = 'PFLOAT n_compiled_nan_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    checks += ['S.COMPLETION = NORMAL',
               '$pfshape(' + expression + ') = PFBINARY ' + operation + ' expression_' + tag + '_0 expression_' + tag + '_1']
    for field in (0, 1):
        child = origin + '_' + str(field)
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                   '$origin_node(S.SOURCES, ' + child + ') = (expression_' + tag + '_' + str(field) + ')',
                   '$compiled_precision(S, (' + child + ')) = (14)']
    left_value = value(checks, tag + '_0', left)[0]
    right_value = value(checks, tag + '_1', right)[0]
    left_number, right_number = 'pnumber_nan_left_' + tag, 'pnumber_nan_right_' + tag
    checks += ['$string_read_runtime_instanceof_operand(S, ' + origin + '_0) = (' + left_value + ')',
               '$string_read_runtime_instanceof_operand(S, ' + origin + '_1) = (' + right_value + ')',
               '$coerce_number(' + left_value + ') = COERCED ' + left_number + ' false',
               '$coerce_number(' + right_value + ') = COERCED ' + right_number + ' false',
               '$number_binary(' + operation + ', ' + left_number + ', ' + right_number + ') = NUM (NFLOAT n_compiled_nan_' + tag + ')',
               '$pfcast_nan(' + result + ')',
               '$binary_apply(S, ' + operation + ', ' + left_value + ', ' + right_value + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
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
    report['scope'] = 'Four current histories authenticate emitted ADD/SUBTRACT/MULTIPLY/DIVIDE NaN operands through exact false CODE/read-eps, root/both-child source and equal captured precision. Proper recursive consumer operand certificates, quiet typed coercions, exact NUM NaN bits and full unchanged binary_apply under explicit NORMAL supply only the instanceof operand. General VALUE, BYTE and quiet truth remain absent for the NaN result. Named-target authority, CONSTCONTEXTeps, whole resolve_at/class_instanceof and existing integer parents retain keys1/-1/0/-4, Warning, supplied throw, bounds, cleanup and budget histories. Last key uses false0+compiled3 before BITNOT. Leading/nonquiet strings, zero division, late namespace fallback without child certificates, wider ownership/lifetimes and all exact held boundaries remain outside. Native originals reused once; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
