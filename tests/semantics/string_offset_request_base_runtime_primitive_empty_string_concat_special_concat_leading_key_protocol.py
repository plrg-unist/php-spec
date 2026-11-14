#!/usr/bin/env python3
"""Quiet primitive CONCAT preserves original values and sequential conversion."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_primitive_empty_string_concat_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_empty_string_concat_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
FALSE, TRUE = prior.prior.prior.FALSE, prior.prior.TRUTH
THREE = ('ADD', ('POSITIVE', TRUE, 1), ('COMPILED', 'PINT 2', ('ADD', 1, 1)), 3)
NULL = ('NULL_TERNARY',)
TREES = (
    ('CAST', 'CASTINT', ('IDENTICAL', ('MIXED_CONCAT', FALSE, TRUE, ([], [49]), [49]), ('STRING', '1', None), True), 'PINT 1'),
    ('BITNOT', ('CAST', 'CASTINT', ('MIXED_CONCAT', ('STRING', '0', None), NULL, ([48], []), [48]), 'PINT 0'), -1),
    ('CAST', 'CASTINT', ('MIXED_CONCAT', FALSE, NULL, ([], []), []), 'PINT 0'),
    ('BITNOT', ('CAST', 'CASTINT', ('MIXED_CONCAT', ('MIXED_CONCAT', FALSE, THREE, ([], [51]), [51]), FALSE, ([51], []), [51]), 'PINT 3'), -4),
)
base_value = prior.value


def value(checks, tag, tree):
    if tree[0] != 'MIXED_CONCAT':
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    integers.emitted(checks, tag)
    checks += ['$pfshape(' + expression + ') = PFBINARY CONCAT ' + expression + '_0 ' + expression + '_1',
               'S.COMPLETION = NORMAL', 'S.CONSTCONTEXT = eps']
    values, flags, state = [], [], 'S'
    for index, child in enumerate(tree[1:3]):
        child_tag = tag + '_' + str(index)
        child_origin, flag = 'porigin_' + child_tag, 'b_concat_' + child_tag
        prepared, converted = 'pvalue_concat_prepared_' + child_tag, 'S_concat_string_' + child_tag
        checks += ['$origin_child((' + origin + '), [PCFIELD ' + str(index) + ']) = (' + child_origin + ')']
        child_value = value(checks, child_tag, child)[0]
        string = 'PSTRING_CARRIER INTERNED_STRING (' + str(tree[3][index]) + ')'
        checks += ['$string_read_runtime_cast_quiet(CASTSTRING, ' + child_value + ')',
                   flag + ' = $concat_constant(S, (' + child_origin + '))',
                   '(' + state + ', KNOWN ' + prepared + ') = $concat_operand(' + state + ', KNOWN (' + child_value + '), ' + flag + ', 5)',
                   converted + ' = $stringify(' + state + ', ' + prepared + ', 5)',
                   converted + ' = S[.RESULT = KNOWN (' + string + ')]']
        values.append(string)
        flags.append(flag)
        state = converted
    payload = str(tree[-1])
    result = 'PSTRING_CARRIER INTERNED_STRING (' + payload + ')'
    checks += ['$string_concat(' + state + ', ' + ', '.join([*values, *flags]) + ') = S[.RESULT = KNOWN (' + result + ')]',
               '$startup_bytes(' + payload + ')', '$c_string(' + payload + ') = ' + payload,
               '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
               '$string_read_runtime_bytes(S, ' + origin + ') = (' + payload + ')']
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
    report['scope'] = 'Four emitted CONCAT trees retain original certified NULL/BOOL/digit-PINT0..9/nonNUL INTERNED VALUE under existing CASTSTRING-quiet whitelist, NORMAL/CONSTCONTEXTeps, exact source/CODE/read/line/precision, actual const facts and left-then-right concat_operand/stringify whole-state checks. Converted operands and final string_concat result keep canonical INTERNED headers with no STRINGDATA allocation. False/true, string0/selected NULL, both-empty false/NULL and nested computed3 retain typed-parent keys1/-1/0/-4 and existing Warning/Throwable/bounds/cleanup/budget histories. Both-STRING compatibility is pointwise; known extra slowpath const-empty reuse, wider integers/FLOAT/raw/REQUEST/undefined/owning/lifetimes and held forms gain no authority. No30/35/59/compiler/formatter/owner changes; native originals reused once and fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
