#!/usr/bin/env python3
"""Independent XOR truth, opcode, scalar and precision certificate checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_xor_special_concat_leading_key_cases as cases
import string_offset_request_base_xor_special_concat_leading_key_protocol as source
import string_offset_request_base_bool_null_unary_special_concat_leading_key_review_state as prior

runner = prior.runner
CONTROLS = {
    'xor-false-false': b"<?php $x = ((false xor false) . null) . 'x';\n",
    'xor-one-zero-string': b"<?php $x = ((1 xor '0') . false) . 'x';\n",
    'xor-leading-text-bool': b"<?php $x = (('1tail' xor true) . false) . 'x';\n",
    'xor-finite-left': b"<?php $x = ((0.0 xor 1) . null) . 'x';\n",
    'xor-finite-right': b"<?php $x = ((1 xor 0.0) . null) . 'x';\n",
    'xor-array-left': b"<?php $x = (([] xor false) . null) . 'x';\n",
    'xor-loose-equal': b"<?php $x = ((0 == 0) . null) . 'x';\n",
    'xor-nan-left': b"<?php $x = ((NAN xor false) . null) . 'x';\n"}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('xor_root', 'xor_root_child', 'xor_root_l', 'xor_root_child_l')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    guards = [origin + ' = PORIGIN n_xor pcpath_xor',
              origin + '_l = PORIGIN n_xor pcpath_xor_l',
              origin + '_r = PORIGIN n_xor pcpath_xor_r']
    wrong = 'PBOOL true' if index == 2 else 'PBOOL false'
    for suffix, value in (('drop', 'eps'), ('wrong', '(' + wrong + ')'), ('type', '(PINT 1)')):
        state = 'S_xor_' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + value + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    mutants = (('PINT 1', 'PSTRING ($ptascii("0"))'), ('PBOOL false', 'PBOOL true'),
               ('PINT 0', 'PBOOL false'), ('PSTRING ($ptascii("1"))', 'PBOOL false'))[index]
    for suffix, value in zip(('_l', '_r'), mutants):
        child = origin + suffix
        for operation, replacement in (('drop', 'eps'), ('wrong', '(' + value + ')')):
            state = 'S_xor_child' + suffix + '_' + operation
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + replacement + ')]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_xor_precision' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        left = 'expression_xor_other' if suffix == '_l' else expression + '_l'
        right = 'expression_xor_other' if suffix == '_r' else expression + '_r'
        state = 'S_xor_source' + suffix
        if suffix == '_l':
            guards += ['expression_xor_other = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag]
        guards += [state + ' = S_after[.SOURCES = [{ID n_xor, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_xor ' + expression + '), (PCOCCURRENCE pcpath_xor_l ' + left + '), (PCOCCURRENCE pcpath_xor_r ' + right + ')])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_xor_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_xor_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_xor_precision, (' + origin + '_l)) = (14)',
               '$compiled_precision(S_xor_precision, (' + origin + '_r)) = (14)',
               '$compiled_special_concat_bytes(S_xor_precision, ' + origin + ') = eps']
    if index == 0:
        for suffix, value, truth, text, array in (('_l', 'PFLOAT 0', False, '0', '$array_empty()'),
                                                ('_r', 'PFLOAT 4607182418800017408', True, '1tail', '$array_insert($array_empty(), KINT 0, DIRECT (PINT 1))')):
            child = origin + suffix
            state = 'S_xor_float' + suffix
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', (' + value + '))]',
                       '$truth(' + state + ', ' + value + ') = ' + str(truth).lower(),
                       '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ($ptascii(' + json.dumps(text) + '))',
                       '$compiled_read(' + state + ', ' + origin + ') = (PBOOL true)',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii("1"))']
            state = 'S_xor_array' + suffix
            guards += ['n_xor_array' + suffix + ' = |S_after.ARRAYS|',
                       state + ' = S_after[.ARRAYS = S_after.ARRAYS ++ [' + array + ']][.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', (PARRAY n_xor_array' + suffix + '))]',
                       '$truth(' + state + ', PARRAY n_xor_array' + suffix + ') = ' + str(truth).lower(),
                       '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ($ptascii(' + json.dumps(text) + '))',
                       '$compiled_read(' + state + ', ' + origin + ') = (PBOOL true)',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    if index == 2:
        guards += ['expression_xor_opcode = NExprBinaryOpNotEqual ' + expression + '_l ' + expression + '_r metadata_' + tag,
                   'S_xor_opcode = S_after[.SOURCES = [{ID n_xor, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_xor expression_xor_opcode), (PCOCCURRENCE pcpath_xor_l ' + expression + '_l), (PCOCCURRENCE pcpath_xor_r ' + expression + '_r)])}]]',
                   '$compiled_read(S_xor_opcode, ' + origin + ') = (PBOOL false)',
                   '$compiled_special_concat_bytes(S_xor_opcode, ' + origin + '_l) = ($ptascii("1"))',
                   '$compiled_special_concat_bytes(S_xor_opcode, ' + origin + '_r) = ($ptascii("1"))',
                   '$binary_apply(S_xor_opcode, NOTEQUAL, PINT 1, PBOOL true, 0) = S_xor_opcode[.RESULT = KNOWN (PBOOL false)]',
                   '$compiled_special_concat_bytes(S_xor_opcode, ' + origin + ') = eps']
    guards += prior.unary_guards([], ('1x', '-1x', '0x', '-4x')[index])
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    results = ('false', 'true', 'false', 'true', 'true', 'false', 'true', None)
    values = (('PBOOL false', 'PBOOL false'), ('PINT 1', 'PSTRING ($ptascii("0"))'),
              ('PSTRING ($ptascii("1tail"))', 'PBOOL true'), ('PFLOAT 0', 'PINT 1'), ('PINT 1', 'PFLOAT 0'))
    texts = (('', ''), ('1', '0'), ('1tail', '1'), ('0', '1'), ('1', '0'))
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_xor_control_' + str(index), 'porigin_xor_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_xor_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_xor_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if results[index] is not None:
            checks += ['$compiled_read(' + state + ', ' + binary + ') = (PBOOL ' + results[index] + ')']
        if index < 5:
            for field, value, text in zip((0, 1), values[index], texts[index]):
                child = binary + '_' + str(field)
                checks += ['$origin_child((' + binary + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                           '$compiled_read(' + state + ', ' + child + ') = (' + value + ')',
                           '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                           '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ($ptascii(' + json.dumps(text) + '))']
        if index < 5 or name == 'xor-loose-equal':
            text = '1' if results[index] == 'true' else ''
            key = text + 'x'
            checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(text) + '))',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(key) + '))',
                       '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(key) + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(key) + '))']
        else:
            checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
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
    report['scope'] = 'Four authentic XOR source-state fixtures add independent own-Boolean/type, outcome-changing child read, both child source and three precision refusals. Same-result mixed-type NOTEQUAL source is refused. Per-side finite-float pool values preserve the original truth and byte certificates and now check quiet logical admission; real empty/nonempty arrays remain refused without a new ownership claim. Compiler controls cover false/zero-string/truthy text and both finite-float sides, retaining array/NaN refusals. The former exact-PINT loose-equality refusal retains reviewed integer comparison admission. Original native observations are reused once; borrowed-owner, supplied-throw, fixed bounds and budgets retain their laws. The two finite-float compiler selectors and two pool mutations have separate later cuts; historical reports are not renewed.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
