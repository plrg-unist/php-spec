#!/usr/bin/env python3
"""Nonnull NaN coalesce retains its exact consumer-only left value."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_nonnull_nan_coalesce_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_float_cast_nan_instanceof_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
NANS = tuple(('NAN', 'COALESCE', child) for child in (
    ('NAN', 'CONSTANT'), prior.NANS[1][2], prior.NANS[2][2], prior.NANS[3],
))
TREES = (
    ('CAST', 'CASTINT', ('IDENTICAL', ('INSTANCEOF', NANS[0], 'stdClass', 'PTPLAIN', 'stdClass'), prior.prior.prior.prior.FALSE, True), 'PINT 1'),
    ('BITNOT', ('CAST', 'CASTINT', ('INSTANCEOF', NANS[1], 'stdClass', 'PTFULL', 'stdClass'), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('INSTANCEOF', NANS[2], 'MissingStringRead\\Target', 'PTRELATIVE', 'MissingStringRead\\Target'), 'PINT 0'),
    ('BITNOT', ('ADD', ('CAST', 'CASTINT', ('INSTANCEOF', NANS[3], 'StringReadAlias', 'PTPLAIN', 'stdClass'), 'PINT 0'), ('COMPILED', 'PINT 3', ('ADD', 1, 2)), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[:2] != ('NAN', 'COALESCE'):
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    checks += ['S.COMPLETION = NORMAL',
               '$pfshape(' + expression + ') = PFCOALESCE expression_' + tag + '_0 expression_' + tag + '_1',
               '~$coalesce_quiet_operand(expression_' + tag + '_0)']
    for index in range(2):
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + tag + '_' + str(index) + ')',
                   '$origin_node(S.SOURCES, porigin_' + tag + '_' + str(index) + ') = (expression_' + tag + '_' + str(index) + ')']
    checks += ['$compiled_precision(S, (porigin_' + tag + '_0)) = (14)']
    child = value(checks, tag + '_0', tree[2])[0]
    result = 'PFLOAT n_compiled_nan_' + tag
    checks += ['$string_read_runtime_instanceof_operand(S, porigin_' + tag + '_0) = (' + child + ')',
               result.removeprefix('PFLOAT ') + ' = ' + child.removeprefix('PFLOAT '),
               '$pfcast_nan(' + result + ')',
               '$coalesce_result(S[.RESULT = KNOWN (' + child + ')], expression_' + tag + '_1, 5, 5) = S[.RESULT = KNOWN (' + result + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
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
    report['scope'] = 'Four histories authenticate ordinary emitted coalesce with a certified nonnull NaN left operand through exact NORMAL/source/CODE/read/positive-line and root/left captured precision. Both actual source children, proper recursive typed left certificates, genuine NaN bits and full coalesce_result preserve the left value/TODO and canonical BASE without demanding skipped RHS division, coercion or truth. General VALUE/BYTE and warningful truth remain unchanged. Existing named-target authority, CONSTCONTEXTeps, resolve_at/class_instanceof and integer parents retain keys1/-1/0/-4, Warning, supplied throw, bounds, cleanup and budgets. Null-left selection, quiet variable/location coalesce, wider producers/lifetimes and every exact hold remain partial. Native originals reused once; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
