#!/usr/bin/env python3
"""Emitted canonical FLOAT casts retain exact consumer-only NaN identities."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_float_cast_nan_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_power_nan_instanceof_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
NANS = tuple(('NAN', 'CASTFLOAT', child) for child in (
    ('NAN', 'CONSTANT'), prior.prior.prior.NANS[1], prior.prior.NANS[2], prior.NANS[1],
))
TREES = (
    ('CAST', 'CASTINT', ('IDENTICAL', ('INSTANCEOF', NANS[0], 'stdClass', 'PTPLAIN', 'stdClass'), prior.prior.prior.FALSE, True), 'PINT 1'),
    ('BITNOT', ('CAST', 'CASTINT', ('INSTANCEOF', NANS[1], 'stdClass', 'PTFULL', 'stdClass'), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('INSTANCEOF', NANS[2], 'MissingStringRead\\Target', 'PTRELATIVE', 'MissingStringRead\\Target'), 'PINT 0'),
    ('BITNOT', ('ADD', ('CAST', 'CASTINT', ('INSTANCEOF', NANS[3], 'StringReadAlias', 'PTPLAIN', 'stdClass'), 'PINT 0'), ('COMPILED', 'PINT 3', ('ADD', 1, 2)), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[:2] != ('NAN', 'CASTFLOAT'):
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    checks += ['S.COMPLETION = NORMAL',
               '$pfshape(' + expression + ') = PFCAST CASTFLOAT expression_' + tag + '_0',
               '$pplist_meta_kind($pcmetadata(' + expression + ')) = 2',
               '$origin_child((' + origin + '), [PCFIELD 0]) = (porigin_' + tag + '_0)',
               '$origin_node(S.SOURCES, porigin_' + tag + '_0) = (expression_' + tag + '_0)',
               '$compiled_precision(S, (porigin_' + tag + '_0)) = (14)']
    child = value(checks, tag + '_0', tree[2])[0]
    result = 'PFLOAT n_compiled_nan_' + tag
    checks += ['$string_read_runtime_instanceof_operand(S, porigin_' + tag + '_0) = (' + child + ')',
               '$pfcast_nan(' + child + ')', result.removeprefix('PFLOAT ') + ' = ' + child.removeprefix('PFLOAT '),
               '$cast_apply(S, CASTFLOAT, ' + child + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
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
    report['scope'] = 'Four current histories authenticate emitted canonical FLOAT casts of compiled, arithmetic, unary and completed-POWER NaNs through explicit NORMAL, exact false CODE/read-eps, positive line, root/child source and equal captured precision. Canonical kind2, proper recursive consumer operand certificates, genuine child NaN and unchanged full cast_apply preserve exact child bits only for instanceof. General VALUE/BYTE and warningful truth remain refused. Existing named-target authority, CONSTCONTEXTeps, resolve_at/class_instanceof and integer parents retain keys1/-1/0/-4, Warning, supplied throw, bounds, cleanup and budgets. Wider casts/producers/owners/lifetimes and every exact held boundary remain outside. Native originals reused once; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
