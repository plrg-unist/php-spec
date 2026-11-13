#!/usr/bin/env python3
"""Independent strict identity type, source, precision and owner checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_identity_special_concat_leading_key_cases as cases
import string_offset_request_base_identity_special_concat_leading_key_protocol as source
import string_offset_request_base_bool_null_unary_special_concat_leading_key_review_state as prior

runner = prior.runner
CONTROLS = {
    'integer-identical': b"<?php $x = ((0 === 0) . null) . 'x';\n",
    'int-float-notidentical': b"<?php $x = ((0 !== 0.0) . null) . 'x';\n",
    'rounded-float-identical': b"<?php $x = ((1.00000000000001 === 1.0) . false) . 'x';\n",
    'text-identical': b"<?php $x = (('1tail' === '1tail') . false) . 'x';\n",
    'loose-equal': b"<?php $x = ((0 == 0) . null) . 'x';\n",
    'array-identical': b"<?php $x = (([] === []) . null) . 'x';\n",
    'nan-identical': b"<?php $x = ((NAN === NAN) . null) . 'x';\n"}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('identity_root_child', 'identity_root_child', 'identity_root_l', 'identity_root_child_l')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    guards = [origin + ' = PORIGIN n_identity pcpath_identity',
              origin + '_l = PORIGIN n_identity pcpath_identity_l',
              origin + '_r = PORIGIN n_identity pcpath_identity_r']
    wrong = 'PBOOL true' if index in (0, 2) else 'PBOOL false'
    for suffix, value in (('drop', 'eps'), ('wrong', '(' + wrong + ')'), ('type', '(PINT 1)')):
        state = 'S_identity_' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + value + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    mutants = (('PINT 0', 'PSTRING ($ptascii("0"))'), ('PBOOL false', 'PINT 0'),
               ('PBOOL true', 'PINT 1'), ('PFLOAT 4607182418800017408', 'PFLOAT 4607182418800017408'))[index]
    for suffix, value in zip(('_l', '_r'), mutants):
        child = origin + suffix
        for operation, replacement in (('drop', 'eps'), ('wrong', '(' + value + ')')):
            state = 'S_identity_child' + suffix + '_' + operation
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + replacement + ')]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                       '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_identity_precision' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        left = 'expression_identity_other' if suffix == '_l' else expression + '_l'
        right = 'expression_identity_other' if suffix == '_r' else expression + '_r'
        state = 'S_identity_source' + suffix
        if suffix == '_l':
            guards += ['expression_identity_other = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag]
        guards += [state + ' = S_after[.SOURCES = [{ID n_identity, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_identity ' + expression + '), (PCOCCURRENCE pcpath_identity_l ' + left + '), (PCOCCURRENCE pcpath_identity_r ' + right + ')])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_identity_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_identity_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_identity_precision, (' + origin + '_l)) = (14)',
               '$compiled_precision(S_identity_precision, (' + origin + '_r)) = (14)',
               '$compiled_special_concat_bytes(S_identity_precision, ' + origin + ') = eps']
    if index == 0:
        for suffix, left, right in (('_l', 'PARRAY 0', 'PINT 0'), ('_r', 'PSTRING ($ptascii("0"))', 'PARRAY 0')):
            state = 'S_identity_array' + suffix
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + suffix + ', (PARRAY 0))]',
                       '$compiled_read(' + state + ', ' + origin + ') = (PBOOL false)',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + '_l) = ($ptascii("0"))',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + '_r) = ($ptascii("0"))',
                       '$strict_identical(' + left + ', ' + right + ') = false',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += prior.unary_guards([], ('1x', '-1x', '0x', '-4x')[index])
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    results = ('true', 'true', 'false', 'true', 'true', 'true', 'false')
    values = (('PINT 0', 'PINT 0'), ('PINT 0', 'PFLOAT 0'),
              ('PFLOAT 4607182418800017453', 'PFLOAT 4607182418800017408'),
              ('PSTRING ($ptascii("1tail"))', 'PSTRING ($ptascii("1tail"))'))
    texts = (('0', '0'), ('0', '0'), ('1', '1'), ('1tail', '1tail'))
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_identity_control_' + str(index), 'porigin_identity_control_' + str(index)
        compare = origin + '_compare'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_identity_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_identity_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + compare + ')',
                   '$compiled_read(' + state + ', ' + compare + ') = (PBOOL ' + results[index] + ')']
        if index < 4:
            text = '1' if results[index] == 'true' else ''
            key = text + 'x'
            checks += ['$compiled_special_concat_bytes(' + state + ', ' + compare + ') = ($ptascii(' + json.dumps(text) + '))',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(key) + '))',
                       '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(key) + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(key) + '))']
            for field, value, child_text in zip((0, 1), values[index], texts[index]):
                child = compare + '_' + str(field)
                checks += ['$origin_child((' + compare + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                           '$compiled_read(' + state + ', ' + child + ') = (' + value + ')',
                           '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                           '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ($ptascii(' + json.dumps(child_text) + '))']
        else:
            if name == 'loose-equal':
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + compare + ') = ($ptascii("1"))',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii("1x"))',
                           '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("1x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))']
            else:
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + compare + ') = eps',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            if index == 4:
                for field in (0, 1):
                    child = compare + '_' + str(field)
                    checks += ['$origin_child((' + compare + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                               '$compiled_read(' + state + ', ' + child + ') = (PINT 0)',
                               '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                               '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ($ptascii("0"))']
                checks += ['$strict_identical(PINT 0, PINT 0) = true']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.arithmetic, prior, prior.source, prior.prior, prior.strings, runner)] + [Path(__file__)]
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
    report['scope'] = 'Four authentic strict scalar identity source-state fixtures add independent own-Boolean/type, outcome-changing child read, both child source and three precision refusals. Malformed one-sided array pool values preserve literal byte certificates and the real false comparison, isolating each scalar fence without claiming array ownership. Fresh compiler controls distinguish strict types, equal formatted text with different float bits, byte-string identity and array/NaN refusals. The former exact-PINT loose-equality refusal now checks the reviewed integer comparison admission. Original source/native observations are reused once; borrowed-owner, supplied-throw, fixed-bounds and budget laws remain separate from these derived controls.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
