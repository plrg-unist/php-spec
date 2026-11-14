#!/usr/bin/env python3
"""Certified compiled primitives retain typed emitted-parent and key history."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_compiled_primitive_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_shorthand_ternary_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
TRUTH, FALSE = ('NOT', ('FLOAT', 0), True), ('NOT', ('FLOAT', 9218868437227405312), False)
TREES = (
    ('POSITIVE', ('IDENTICAL', ('TERNARY', TRUTH, ('COMPILED', 'PBOOL true', 'true'), True), TRUTH, True), 1),
    ('SHORTHAND', FALSE, ('COMPILED', 'PINT $(-1)', ('NEGATIVE', 1)), False),
    ('POSITIVE', ('IDENTICAL', ('SHORTHAND', FALSE, ('COMPILED', 'PNULL', 'null'), False), FALSE, False), 0),
    ('BITNOT', ('TERNARY', TRUTH, ('COMPILED', 'PINT 3', ('ADD', 1, 2)), True), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] != 'COMPILED':
        return base_value(checks, tag, tree)
    origin, expression, path = 'porigin_' + tag, 'expression_' + tag, 'pcpath_' + tag
    result, form = tree[1:]
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')',
               origin + ' = PORIGIN n_runtime_unit ' + path,
               '$code_at(S.CODE, n_runtime_unit) = (pcode_runtime)',
               '$code_expression(pcode_runtime.EXPRESSIONS, ' + path + ') = ((5, true))',
               '$compiled_precision(S, (' + origin + ')) = (14)',
               '$compiled_read(S, ' + origin + ') = (' + result + ')',
               '$compiled_identity_value(S, ' + origin + ') = (' + result + ')',
               '$parser_literal_at(' + expression + ', 14) = eps',
               '$compiled_special_concat_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    if isinstance(form, str):
        checks += [expression + ' = NExprConstFetch name_' + tag + ' metadata_' + tag,
                   '$ptast(name_' + tag + ') = PTNAME PTPLAIN ($ptascii(' + json.dumps(form) + '))',
                   '$type_bytes(' + result + ') = $ptascii(' + json.dumps('null' if result == 'PNULL' else 'bool') + ')']
        number = '1' if result == 'PBOOL true' else '0'
    else:
        checks += ['$pfshape(' + expression + ') = ' + ('PFUNARY NEGATIVE ' if form[0] == 'NEGATIVE' else 'PFBINARY ADD ') +
                   ' '.join(expression + '_' + str(index) for index in range(len(form) - 1))]
        for index, integer in enumerate(form[1:]):
            checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + tag + '_' + str(index) + ')',
                       '$origin_node(S.SOURCES, porigin_' + tag + '_' + str(index) + ') = (NScalarInt (INTEGER ' + str(integer) + ') metadata_' + tag + '_' + str(index) + ')']
        number = result.removeprefix('PINT ')
        checks += ['$long_range(' + number + ')']
    checks += ['$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
    return result, number


prior.value, prior.prior.value, prior.prior.prior.value, prior.prior.prior.prior.value, prior.prior.prior.prior.prior.value, integers.value, integers.TREES = value, value, value, value, value, value, TREES
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
    report['scope'] = 'Actual compiled PBOOL/PNULL/signed64 PINT retain captured precision, true CODE, compiled_read and exact compiled_identity_value through emitted full/shorthand/identity/bitnot parents. Raw scalar projections must agree in type/value; nonliteral compiled identities retain the existing compiler-output trust boundary rather than revalidating arbitrary forged child pools. Raw true/null and folded -1/(1+2) remain typed; compiled facts are completion-independent like the unchanged PFLOAT certificate, not execution credit. Emitted parents retain NORMAL/source/CODEfalse/read-eps/demanded precision and full-state truth/selection authority. Compiled NULL keeps its existing empty BYTE while emitted NULL parents retain BYTE eps; only two old fixture-builder branches learn that distinction. Runtime BOOL/INT BYTE requires read-eps, making compiled/emitted routes disjoint without changing formatting. REQUEST keys1/-1/0/-4 preserve captured14/live17 precision, Warning owners, supplied Throwable identity, fixed bounds/cleanup and inherited budgets. No compiler/schema/numeric-body/formatter/API/owner expansion; saved natives reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
