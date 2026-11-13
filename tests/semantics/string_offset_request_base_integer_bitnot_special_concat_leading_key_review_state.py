#!/usr/bin/env python3
"""Independent integer complement, type, range and source certificate checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_integer_bitnot_special_concat_leading_key_cases as cases
import string_offset_request_base_integer_bitnot_special_concat_leading_key_protocol as source
import string_offset_request_base_bool_null_unary_special_concat_leading_key_review_state as prior

runner = prior.runner
INTEGERS = {'zero': ('0', 0, -1), 'positive': ('3', 3, -4), 'minus-one': ('0 - 1', -1, 0),
            'maximum': ('9223372036854775807', 9223372036854775807, -9223372036854775808),
            'minimum': ('(0 - 9223372036854775807) - 1', -9223372036854775808, 9223372036854775807),
            'twice': ('~0', -1, 0)}
CONTROLS = {name: ("<?php $x = ((~(" + expression + ")) . null) . 'x';\n").encode()
            for name, (expression, child, result) in INTEGERS.items()} | {
    'float-exact': b"<?php $x = ((~3.0) . null) . 'x';\n",
    'float-fractional': b"<?php $x = ((~3.5) . null) . 'x';\n",
    'string-child': b"<?php $x = ((~'3') . null) . 'x';\n",
    'boolean-child': b"<?php $x = ((~true) . null) . 'x';\n",
    'null-child': b"<?php $x = ((~null) . null) . 'x';\n",
    'nan-child': b"<?php $x = ((~NAN) . null) . 'x';\n",
    'array-child': b"<?php $x = ((~[]) . null) . 'x';\n"}


def term(value):
    return str(value) if value >= 0 else '$(' + str(value) + ')'


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('bitnot_root_l', 'bitnot_root', 'bitnot_root_l', 'bitnot_root')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    child = origin + '_child'
    guards = [origin + ' = PORIGIN n_bitnot pcpath_bitnot',
              child + ' = PORIGIN n_bitnot pcpath_bitnot_child']
    for suffix, value in (('drop', 'eps'), ('wrong', '(PINT 99)'), ('type', '(PFLOAT 0)')):
        state = 'S_bitnot_' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + value + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    for suffix, value in (('drop', 'eps'), ('wrong', '(PINT ' + ('0' if index == 2 else '2') + ')')):
        state = 'S_bitnot_child_' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + value + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    for suffix, changed, root_precision, child_precision in (('child', child, 14, 17), ('root', origin, 17, 14)):
        state = 'S_bitnot_precision_' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + changed + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (' + str(root_precision) + ')',
                   '$compiled_precision(' + state + ', (' + child + ')) = (' + str(child_precision) + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['expression_bitnot_other = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag,
               'S_bitnot_source = S_after[.SOURCES = [{ID n_bitnot, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_bitnot expression_bitnot_other)])}]]',
               '$compiled_special_concat_bytes(S_bitnot_source, ' + origin + ') = eps',
               'S_bitnot_child_source = S_after[.SOURCES = [{ID n_bitnot, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_bitnot ' + expression + '), (PCOCCURRENCE pcpath_bitnot_child expression_bitnot_other)])}]]',
               '$compiled_special_concat_bytes(S_bitnot_child_source, ' + origin + ') = eps']
    if index == 3:
        for suffix, value in (('float', 'PFLOAT 4613937818241073152'), ('string', 'PSTRING ($ptascii("3"))')):
            state = 'S_bitnot_scalar_' + suffix
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', (' + value + '))]',
                       '$compiled_read(' + state + ', ' + child + ') = (' + value + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ($ptascii("3"))',
                       '$compiled_read(' + state + ', ' + origin + ') = (PINT $(-4))',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        guards += ['$bitnot_apply(S_bitnot_scalar_float, PFLOAT 4613937818241073152, 0) = S_bitnot_scalar_float[.RESULT = KNOWN (PINT $(-4))]',
                   '$coerce_number(PSTRING ($ptascii("3"))) = COERCED (NINT 3) false',
                   '$string_not($ptascii("3")) = [204]']
        for suffix, number in (('below', -9223372036854775809), ('above', 9223372036854775808)):
            state, result = 'S_bitnot_range_' + suffix, -number - 1
            guards += [state + ' = S_after[.POOLS = $special_review_pools($special_review_pools(S_after.POOLS, ' + child + ', (PINT ' + term(number) + ')), ' + origin + ', (PINT ' + term(result) + '))]',
                       '$compiled_read(' + state + ', ' + child + ') = (PINT ' + term(number) + ')',
                       '$compiled_read(' + state + ', ' + origin + ') = (PINT ' + term(result) + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ($ptascii("3"))',
                       '$long_not(' + term(number) + ') = ' + term(result),
                       '~$long_range(' + term(number) + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += prior.unary_guards([], ('1x', '-1x', '0x', '-4x')[index])
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_bitnot_control_' + str(index), 'porigin_bitnot_control_' + str(index)
        unary, child = origin + '_unary', origin + '_child'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_bitnot_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_bitnot_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + unary + ')',
                   '$origin_child((' + unary + '), [PCFIELD 0]) = (' + child + ')']
        if name in INTEGERS:
            expression, number, result = INTEGERS[name]
            text, key = str(result), str(result) + 'x'
            checks += ['$compiled_read(' + state + ', ' + child + ') = (PINT ' + term(number) + ')',
                       '$compiled_read(' + state + ', ' + unary + ') = (PINT ' + term(result) + ')',
                       '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                       '$compiled_precision(' + state + ', (' + unary + ')) = (14)',
                       '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ($ptascii(' + json.dumps(str(number)) + '))',
                       '$long_not(' + term(number) + ') = ' + term(result),
                       '$compiled_special_concat_bytes(' + state + ', ' + unary + ') = ($ptascii(' + json.dumps(text) + '))',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(key) + '))',
                       '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(key) + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(key) + '))']
        else:
            checks += ['$compiled_special_concat_bytes(' + state + ', ' + unary + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            if name == 'float-exact':
                checks += ['$compiled_read(' + state + ', ' + child + ') = (PFLOAT 4613937818241073152)',
                           '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ($ptascii("3"))',
                           '$compiled_read(' + state + ', ' + unary + ') = (PINT $(-4))']
            elif name == 'string-child':
                checks += ['$compiled_read(' + state + ', ' + unary + ') = (pvalue_bitnot_string)',
                           '$string_plain(pvalue_bitnot_string) = PSTRING ([204])']
            else:
                checks += ['$compiled_read(' + state + ', ' + unary + ') = eps']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.prior.prior, source.arithmetic, prior, prior.source, prior.prior, prior.strings, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases = cases
    runner.conditions = conditions
    runner.compiler_conditions = compiler_conditions
    runner.CONTROLS = CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic-source-seeded integer bitwise-NOT fixtures add own-result/type, child read/source and both precision refusals. A same-result quiet float pool and numerically convertible string preserve literal byte authority while remaining excluded; matching forged complements beyond both signed64 limits isolate range admission. Compiler controls cover endpoints, zero/minus-one, positive and nested complement, while exact/fractional floats, string-byte NOT, bool/null/NaN/array children remain refused. Original native4 are reused once; owners, supplied throw, fixed bounds and budgets retain their laws. Derived/compiler conditions carry zero source credit.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
