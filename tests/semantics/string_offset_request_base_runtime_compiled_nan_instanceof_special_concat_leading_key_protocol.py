#!/usr/bin/env python3
"""Named instanceof consumes exact compiled NaNs through its own certificate."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_compiled_nan_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_scalar_resolved_instanceof_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
FALSE = prior.FALSE
TREES = (
    ('CAST', 'CASTINT', ('IDENTICAL', ('INSTANCEOF', ('NAN', 'CONSTANT'), 'stdClass', 'PTPLAIN', 'stdClass'), FALSE, True), 'PINT 1'),
    ('BITNOT', ('CAST', 'CASTINT', ('INSTANCEOF', ('NAN', 'POSITIVE'), 'stdClass', 'PTFULL', 'stdClass'), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('INSTANCEOF', ('NAN', 'SUBTRACT'), 'MissingStringRead\\Target', 'PTRELATIVE', 'MissingStringRead\\Target'), 'PINT 0'),
    ('BITNOT', ('ADD', ('CAST', 'CASTINT', ('IDENTICAL', ('INSTANCEOF', ('NAN', 'POWER'), 'StringReadAlias', 'PTPLAIN', 'stdClass'), FALSE, True), 'PINT 1'), ('COMPILED', 'PINT 2', ('ADD', 1, 1)), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] == 'NAN':
        origin, expression = 'porigin_' + tag, 'expression_' + tag
        bits = 'n_compiled_nan_' + tag
        result = 'PFLOAT ' + bits
        checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
                   '$compiled_precision(S, (' + origin + ')) = (14)',
                   '$compiled_read(S, ' + origin + ') = (' + result + ')',
                   '$compiled_identity_value(S, ' + origin + ') = (' + result + ')',
                   '$(' + bits + ' < 18446744073709551616)',
                   '$fparts_nan($float_decode(' + bits + '))',
                   '$compiled_special_concat_bytes(S, ' + origin + ') = eps',
                   '$string_read_runtime_value(S, ' + origin + ') = eps',
                   '$string_read_runtime_instanceof_operand(S, ' + origin + ') = (' + result + ')']
        if tree[1] == 'CONSTANT':
            checks += [expression + ' = NExprConstFetch name_' + tag + ' metadata_' + tag,
                       '$ptast(name_' + tag + ') = PTNAME PTPLAIN ($ptascii("NAN"))']
        elif tree[1] == 'POSITIVE':
            checks += ['$pfshape(' + expression + ') = PFUNARY POSITIVE expression_' + tag + '_child']
        else:
            checks += ['$pfshape(' + expression + ') = PFBINARY ' + tree[1] + ' expression_' + tag + '_l expression_' + tag + '_r']
        return result, None
    result = base_value(checks, tag, tree)
    if tree[0] == 'INSTANCEOF':
        assert tree[1][0] == 'NAN'
        # Only this consumer replaces the prior nonNaN operand assertion.
        checks.remove('~$pfcast_nan(PFLOAT n_compiled_nan_' + tag + '_0)')
    return result


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
    report['scope'] = 'Four current histories authenticate raw ConstFetch, unary, arithmetic and quiet POWER compiled NaN operands through exact compiled read/identity certificates, valid64 bits and captured precision. A consumer-specific instanceof operand certificate admits them while general runtime VALUE and operand BYTE remain absent. Exact emitted instanceof root, both source children, CODE.NAMES target, lexical authority, NORMAL/CONSTCONTEXTeps and full resolve_at/class_instanceof state retain keys1/-1/0/-4, returning Warning, supplied throw, bounds, cleanup and budgets. Existing compiler-output trust for authenticated ConstFetch facts remains; no spelling-only or invented-pool rejection claim. Emitted read-eps NaN, general VALUE/truth/formatter bodies, broader ownership/lifetimes and exact held boundaries remain unchanged. Native originals reused once; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
