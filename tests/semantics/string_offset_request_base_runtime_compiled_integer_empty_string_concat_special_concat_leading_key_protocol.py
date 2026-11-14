#!/usr/bin/env python3
"""Actual compiled integer operands bypass only dynamic CONCAT conversion."""
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_runtime_compiled_integer_empty_string_concat_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_primitive_empty_string_concat_special_concat_leading_key_protocol as prior

runner, integers = prior.runner, prior.integers
FALSE = prior.FALSE
MAX = 9223372036854775807
MAX_BYTES = list(str(MAX).encode())
TREES = (
    ('CAST', 'CASTINT', ('IDENTICAL', ('CONSTANT_INT_CONCAT', ('COMPILED', 'PINT 10', ('ADD', 5, 5)), FALSE, ([49, 48], []), [49, 48]), ('STRING', '10', None), True), 'PINT 1'),
    ('CAST', 'CASTINT', ('CONSTANT_INT_CONCAT', FALSE, ('COMPILED', 'PINT $(-1)', ('NEGATIVE', 1)), ([], [45, 49]), [45, 49]), 'PINT $(-1)'),
    ('CAST', 'CASTINT', ('IDENTICAL', ('CONSTANT_INT_CONCAT', ('LITERAL_INT', MAX), FALSE, (MAX_BYTES, []), MAX_BYTES), ('STRING', '0', None), False), 'PINT 0'),
    ('CAST', 'CASTINT', ('CONSTANT_INT_CONCAT', FALSE, ('COMPILED', 'PINT $(-4)', ('NEGATIVE', 4)), ([], [45, 52]), [45, 52]), 'PINT $(-4)'),
)
base_value = prior.value


def value(checks, tag, tree):
    kind = tree[0]
    if kind not in ('CONSTANT_INT_CONCAT', 'LITERAL_INT'):
        return base_value(checks, tag, tree)
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    checks += ['$origin_node(S.SOURCES, ' + origin + ') = (' + expression + ')']
    if kind == 'LITERAL_INT':
        number = str(tree[1])
        result = 'PINT ' + number
        checks += [expression + ' = NScalarInt (INTEGER ' + number + ') metadata_' + tag,
                   '$long_range(' + number + ')',
                   '$parser_literal_at(' + expression + ', 14) = (' + result + ')',
                   '$compiled_precision(S, (' + origin + ')) = (14)',
                   '$compiled_read(S, ' + origin + ') = (' + result + ')',
                   '$compiled_identity_value(S, ' + origin + ') = (' + result + ')',
                   '$string_read_runtime_value(S, ' + origin + ') = (' + result + ')',
                   '$string_read_runtime_bytes(S, ' + origin + ') = ($echo_value(' + result + '))']
        return result, number
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
        checks += [flag + ' = $concat_constant(S, (' + child_origin + '))',
                   '$string_read_runtime_cast_quiet(CASTSTRING, ' + child_value + r') \/ (' + flag + r' /\ $type_bytes(' + child_value + ') = $ptascii("int"))',
                   '(' + state + ', KNOWN ' + prepared + ') = $concat_operand(' + state + ', KNOWN (' + child_value + '), ' + flag + ', 5)',
                   converted + ' = $stringify(' + state + ', ' + prepared + ', 5)',
                   converted + ' = S[.RESULT = KNOWN (' + string + ')]']
        if child[0] in ('COMPILED', 'LITERAL_INT'):
            checks += [flag + ' = true', '$string_read_runtime_cast_quiet(CASTSTRING, ' + child_value + ') = false']
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
    report['scope'] = 'Actual compiled signed64 PINT operands outside0..9 retain their source/type/value, actual concat_constant=true and compiler-prepared canonical INTERNED header through the unique quiet CONCAT certificate. Folded10, negative1/4 and rawMAX survive emitted false emptiness under strict identity or explicit INT parents. Existing NORMAL/CONSTCONTEXTeps/source/CODE/read/line/precision and sequential concat_operand/stringify/final string_concat whole-state checks remain exact. Dynamic wider integers, FLOAT/raw/REQUEST/undefined/owning operands and const-empty slowpath reuse remain outside. No shared CASTSTRINGquiet,30/35/59/compiler/formatter/owner or held-boundary changes; native originals reused once, fixture source0/native0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
