#!/usr/bin/env python3
"""Strict NaN identity retains typed results and the legacy admission boundary."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_nan_identity_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_null_left_nan_coalesce_instanceof_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
NANS, FALSE = prior.NANS, prior.FALSE
TREES = (
    ('POSITIVE', ('IDENTICAL', ('IDENTICAL', NANS[0], ('NAN', 'CONSTANT'), False), FALSE, True), 1),
    ('BITNOT', ('CAST', 'CASTINT', ('IDENTICAL', ('FLOAT', 4607182418800017408), NANS[1], False), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('IDENTICAL', NANS[2], ('LITERAL_INT', 0), False), 'PINT 0'),
    ('BITNOT', ('ADD', ('CAST', 'CASTINT', ('IDENTICAL', ('NOTIDENTICAL', NANS[3], ('NAN', 'CONSTANT'), True), FALSE, False), 'PINT 0'),
               ('COMPILED', 'PINT 3', ('ADD', 1, 2)), 3), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] not in ('IDENTICAL', 'NOTIDENTICAL'):
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    checks += ['$pfshape(' + expression + ') = PFBINARY ' + tree[0] + ' ' + expression + '_0 ' + expression + '_1']
    children = []
    for index, child in enumerate(tree[1:3]):
        child_origin = 'porigin_' + tag + '_' + str(index)
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (' + child_origin + ')',
                   '$origin_node(S.SOURCES, ' + child_origin + ') = (' + expression + '_' + str(index) + ')',
                   '$compiled_precision(S, (' + child_origin + ')) = (14)']
        children.append(value(checks, tag + '_' + str(index), child)[0])
    if any(child[0] == 'NAN' for child in tree[1:3]):
        checks += ['S.COMPLETION = NORMAL',
                   '$string_read_runtime_instanceof_operand(S, porigin_' + tag + '_0) = (' + children[0] + ')',
                   '$string_read_runtime_instanceof_operand(S, porigin_' + tag + '_1) = (' + children[1] + ')',
                   '$pfcast_nan(' + children[0] + r') \/ $pfcast_nan(' + children[1] + ')']
    identical = tree[-1] if tree[0] == 'IDENTICAL' else not tree[-1]
    result = 'PBOOL ' + str(tree[-1]).lower()
    checks += ['$strict_identical(' + children[0] + ', ' + children[1] + ') = ' + str(identical).lower(),
               '$strict_check(S, ' + children[0] + ', ' + children[1] + ', eps) = COMPARED ' + str(identical).lower(),
               '$binary_apply(S, ' + tree[0] + ', ' + children[0] + ', ' + children[1] + ', 5) = S[.RESULT = KNOWN (' + result + ')]',
               '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    return result, '1' if tree[-1] else '0'


module = prior
while module is not integers:
    module.value = value
    module = module.prior
integers.value, integers.TREES = value, TREES


def conditions(program, path, index):
    if index == 3:
        # Source comparison covers this original's bounds history. This fixture
        # targets only the genuine compiled key at its checked source origin.
        checks = ['S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
                  'S_initial.COMPLETION = BUDGET',
                  'S = S_initial[.COMPLETION = NORMAL]',
                  'S_after = S',
                  'porigin_key = PORIGIN 0 ([PCINDEX 8, PCFIELD 0, PCFIELD 1, PCFIELD 1])',
                  '$origin_node(S.SOURCES, porigin_key) = (NExprBinaryOpConcat expression_1 expression_2 metadata_key)',
                  '$string_read_literal_bytes(NExprBinaryOpConcat expression_1 expression_2 metadata_key) = eps',
                  '$parser_literal_at(NExprBinaryOpConcat expression_1 expression_2 metadata_key, 14) = eps']
        authority = integers.authority(index)
        precision = r'S.PRECISIONINI = $ptascii("17") /\ $precision_value(S) = 17'
        assert authority.count(precision) == 1
        authority[authority.index(precision)] = precision.replace('17', '14')
        checks += authority
        roots = {
            '$string_read_runtime_value(S, porigin_operator_0_0_0_0) = (PBOOL true)',
            '$string_read_runtime_value(S, porigin_operator) = (PINT $(-4))',
        }
        checks = [check for check in checks
                  if not check.startswith(('$string_read_runtime_value(S, porigin_operator',
                                           '$string_read_runtime_bytes(S, porigin_operator'))
                  or check.endswith(' = eps') or check in roots]
        return list(dict.fromkeys(checks)), 0
    checks, derived = prior.conditions(program, path, index)
    if index == 0:
        expected = '$compiled_read(S, porigin_runtime_right) = (PNULL)'
        assert checks.count(expected) == 1
        checks[checks.index(expected)] = '$compiled_read(S, porigin_runtime_right) = (PBOOL false)'
    return checks, derived


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
    report['scope'] = 'Three source-reached histories and one targeted compiled-state root fixture admit strict NaN identity only through a disjoint NORMAL/at-least-one-NaN certificate with exact own/both-child source, CODEfalse/read-eps/line and captured precision, genuine quiet operand certificates, pure strict-identical Boolean and unchanged whole binary_apply. Both NaNs compare nonidentical; NaN versus finite FLOAT or PINT retains typed false; !== supplies true before existing Boolean/integer parents preserve keys1/-1/0/-4. Fourth uses checked original Program/php_run0, initial live/captured14 and its actual key origin; S_after aliases that NORMAL compiled state. It proves inner NOTIDENTICAL=true, outer PINT-4 and root BYTE-4x with recursive NaN VALUE/BYTEeps and pure coalesce/resolve, without claiming fourth ownership, callback, bounds or resumption histories. Those remain in the accepted original source comparison, while first three full-state histories retain live17/captured14. Legacy identity/BUDGET admission, general NaN VALUE/BYTE/truth, compiler/numerics, owners/lifetimes and holds remain literal. Saved native originals reused once; fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
