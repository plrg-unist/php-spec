#!/usr/bin/env python3
"""Coalesce retains original nonnull values and exact fallback tasks."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_coalesce_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_compiled_primitive_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
ONE, ZERO = prior.prior.ONE, prior.prior.ZERO
NULL = ('COMPILED', 'PNULL', 'null')
NEGATIVE_ZERO = ('FLOAT_UNARY', 'NEGATIVE', ('FLOAT_BINARY', 'ADD', ('FLOAT', 0), ZERO, 0), 9223372036854775808)
TREES = (
    ('POSITIVE', ('IDENTICAL', ('COALESCE', prior.FALSE, None), prior.FALSE, True), 1),
    ('BITNOT', ('COALESCE', ZERO, None), -1),
    ('CAST', 'CASTINT', ('COALESCE', NEGATIVE_ZERO, None), 'PINT 0'),
    ('BITNOT', ('COALESCE', ('NULL_TERNARY',), ('ADD', ONE, ('ADD', ONE, ONE, 2), 3)), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] not in ('COALESCE', 'NULL_TERNARY'):
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    indexes = (0, 1) if tree[0] == 'COALESCE' else (0, 1, 2)
    checks += ['$pfshape(' + expression + ') = ' + ('PFCOALESCE' if tree[0] == 'COALESCE' else 'PFTERNARY') +
               ' ' + ' '.join(expression + '_' + str(index) for index in indexes)]
    for index in indexes:
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (porigin_' + tag + '_' + str(index) + ')',
                   '$origin_node(S.SOURCES, porigin_' + tag + '_' + str(index) + ') = (' + expression + '_' + str(index) + ')']
    checks += ['S.COMPLETION = NORMAL']
    select = 'S_select_' + tag
    if tree[0] == 'NULL_TERNARY':
        condition = value(checks, tag + '_0', prior.FALSE)[0]
        result, number = value(checks, tag + '_2', NULL)
        checks += [expression + '_1 = NExprConstFetch name_' + tag + '_1 metadata_' + tag + '_1',
                   '$ptast(name_' + tag + '_1) = PTNAME PTPLAIN ($ptascii("true"))',
                   '$truth_value(S, ' + condition + ', 5) = S[.RESULT = KNOWN (PBOOL false)]',
                   select + ' = S[.ORIGIN = (' + origin + ')][.RESULT = KNOWN (' + condition + ')]',
                   '$select_value(' + select + ', ' + expression + '_1, ' + expression + '_2, 5, 5, 5) = ' + select +
                   '[.TODO = [$at_task((porigin_' + tag + '_2), EVAL ' + expression + '_2), VALUE_COPY 5] ++ ' + select + '.TODO][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]']
    else:
        left, number = value(checks, tag + '_0', tree[1])
        checks += ['~$coalesce_quiet_operand(' + expression + '_0)',
                   select + ' = S[.ORIGIN = (' + origin + ')][.RESULT = KNOWN (' + left + ')]']
        if left == 'PNULL':
            result, number = value(checks, tag + '_1', tree[2])
            checks += ['$coalesce_result(' + select + ', ' + expression + '_1, 5, 5) = ' + select +
                       '[.TODO = [$at_task((porigin_' + tag + '_1), EVAL ' + expression + '_1), VALUE_COPY 5] ++ ' + select + '.TODO][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]']
        else:
            assert tree[2] is None
            result = left
            checks += ['$pfshape(' + expression + '_1) = PFBINARY DIVIDE expression_' + tag + '_skipped_left expression_' + tag + '_skipped_right',
                       '$number_binary(DIVIDE, NINT 1, NINT 0) = DIVZERO',
                       '$string_read_runtime_value(S, porigin_' + tag + '_1) = eps',
                       '$coalesce_result(' + select + ', ' + expression + '_1, 5, 5) = ' + select + '[.BASE = BASE_VALUE (KNOWN PNULL)]']
    checks += ['$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = ' +
               ('eps' if result == 'PNULL' or result.startswith('PFLOAT ') else '($echo_value(' + result + '))')]
    return result, number


prior.value, prior.prior.value, prior.prior.prior.value, prior.prior.prior.prior.value, prior.prior.prior.prior.prior.value, prior.prior.prior.prior.prior.prior.value, integers.value, integers.TREES = value, value, value, value, value, value, value, TREES
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
    report['scope'] = 'Four emitted coalesce trees retain NORMAL/parent CODEfalse/read-eps/positive line, exact left and fallback SOURCE identities, ordinary rather than quiet-location left operands and equal captured precision only for demanded values. Nonnull PBOOL false/PINT0/FLOAT-0 retain their original values without truth or fallback demand; selected PNULL requires the typed fallback. Actual module66 coalesce_result keeps the original nonnull result and resets BASE, or schedules exact fallback AT(EVAL)/VALUE_COPY while clearing RESULT/BASE. Full-ternary-selected NULL retains its actual skipped raw true source and module51 selection. FLOAT VALUE and emitted NULL keep BYTE eps. REQUEST keys1/-1/0/-4 retain captured14/live17 precision, Warning owners, supplied Throwable identity, fixed bounds, cleanup and budget rejoining. No compiler/schema/numeric/formatter/API/owner or quiet-location expansion; saved natives reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
