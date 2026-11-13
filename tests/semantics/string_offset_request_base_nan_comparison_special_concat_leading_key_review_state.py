#!/usr/bin/env python3
"""Independent unordered comparisons and source-restricted NaN value proofs."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_nan_comparison_special_concat_leading_key_cases as cases
import string_offset_request_base_nan_comparison_special_concat_leading_key_protocol as source
import string_offset_request_base_numeric_comparison_special_concat_leading_key_review_state as prior

runner = prior.runner
NAN = source.NAN
NUMBERS = prior.NUMBERS | {'nan': ('NAN', 'PFLOAT ' + NAN, 'NFLOAT ' + NAN, None, True),
                           'computed': ('(1 + E_WARNING)', 'PINT 3', 'NINT 3', 3, False)}
ROWS = {operation.lower() + '-' + side: (operation, left, right)
        for operation in prior.OPERATORS
        for side, left, right in (('left', 'nan', 'f15'), ('right', 'f15', 'nan'), ('both', 'nan', 'nan'))}
ROWS.update({
    'less-min': ('LESS', 'nan', 'imin'), 'greater-max': ('GREATER', 'imax', 'nan'),
    'ge-infinity': ('GREATEREQUAL', 'finf', 'nan'), 'greater-ninf': ('GREATER', 'nan', 'fninf'),
    'space-zero': ('SPACESHIP', 'nan', 'fn0'), 'space-zero-reverse': ('SPACESHIP', 'i0', 'nan'),
    'equal-computed': ('EQUAL', 'nan', 'computed'), 'space-computed': ('SPACESHIP', 'computed', 'nan')})
CONTROLS = {name: ("<?php $x = ((" + NUMBERS[left][0] + ' ' + prior.OPERATORS[operation] + ' ' + NUMBERS[right][0] + ") . null) . 'x';\n").encode()
            for name, (operation, left, right) in ROWS.items()} | {
    'arithmetic-nan': prior.CONTROLS['nan-arithmetic'],
    'numeric-string': b"<?php $x = ((NAN < '2') . null) . 'x';\n",
    'strict-identity': b"<?php $x = ((NAN === NAN) . null) . 'x';\n"}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('nan_root_l', 'nan_root_child', 'nan_root_l', 'nan_root_child_l')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    rendered = '1' if index == 1 else ''
    own = 'PINT 1' if index == 1 else 'PBOOL false'
    guards = [origin + ' = PORIGIN n_nan pcpath_nan',
              origin + '_l = PORIGIN n_nan pcpath_nan_l',
              origin + '_r = PORIGIN n_nan pcpath_nan_r']
    for suffix, replacement in (('drop', 'eps'), ('wrong', '(PINT 0)' if index == 1 else '(PBOOL true)'),
                                ('type', '(PBOOL true)' if index == 1 else '(PINT 0)')):
        state = 'S_nan_' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + replacement + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    for suffix in ('_l', '_r'):
        child = origin + suffix
        state = 'S_nan_drop' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', eps)]',
                   '$compiled_read(' + state + ', ' + child + ') = eps',
                   '$compiled_comparison_number(' + state + ', ' + child + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
        state = 'S_nan_precision' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                   '$compiled_comparison_number(' + state + ', ' + child + ') =/= eps',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        left = 'expression_nan_other' if suffix == '_l' else expression + '_l'
        right = 'expression_nan_other' if suffix == '_r' else expression + '_r'
        if suffix == '_l':
            guards += ['expression_nan_other = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag]
        state = 'S_nan_source' + suffix
        guards += [state + ' = S_after[.SOURCES = [{ID n_nan, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_nan ' + expression + '), (PCOCCURRENCE pcpath_nan_l ' + left + '), (PCOCCURRENCE pcpath_nan_r ' + right + ')])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_nan_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_nan_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_nan_precision, (' + origin + '_l)) = (14)',
               '$compiled_precision(S_nan_precision, (' + origin + '_r)) = (14)',
               '$compiled_special_concat_bytes(S_nan_precision, ' + origin + ') = eps']
    nan_sides = ('_l',) if index == 0 else ('_r',) if index == 1 else ('_l', '_r')
    for suffix in nan_sides:
        child = origin + suffix
        guards += ['$compiled_comparison_number(S_after, ' + child + ') = (NFLOAT ' + NAN + ')',
                   '$compiled_special_concat_bytes(S_after, ' + child + ') = eps',
                   '$compiled_order_number(PFLOAT ' + NAN + ') = eps']
        for label, bits in (('sign', '18444492273895866368'), ('payload', '9218868437227405313')):
            state = 'S_nan_' + label + suffix
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', (PFLOAT ' + bits + '))]',
                       '$fparts_nan($float_decode(' + bits + '))',
                       '$compiled_comparison_number(' + state + ', ' + child + ') = (NFLOAT ' + bits + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + child + ') = eps',
                       '$compiled_read(' + state + ', ' + origin + ') = (' + own + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(rendered) + '))']
    guards += prior.prior.unary_guards([], ('1x', '-1x', '0x', '-4x')[index])
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_nan_control_' + str(index), 'porigin_nan_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_nan_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_nan_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name not in ROWS:
            if name == 'numeric-string':
                checks += ['$compiled_read(' + state + ', ' + binary + ') = (PBOOL false)',
                           '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(""))',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii("x"))',
                           '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("x"))']
            else:
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            continue
        operation, left_name, right_name = ROWS[name]
        result = 1 if operation == 'SPACESHIP' else operation == 'NOTEQUAL'
        rendered = prior.text(result)
        checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + prior.value(result) + ')',
                   '$compiled_precision(' + state + ', (' + binary + ')) = (14)',
                   '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(rendered) + '))',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(rendered + 'x') + '))',
                   '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(rendered + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(rendered + 'x') + '))']
        numbers = NUMBERS[left_name], NUMBERS[right_name]
        checks += ['$num_compare(' + numbers[0][2] + ', ' + numbers[1][2] + ') = 1',
                   '$num_compare(' + numbers[1][2] + ', ' + numbers[0][2] + ') = 1']
        for field, number in enumerate(numbers):
            child = binary + '_' + str(field)
            checks += ['$origin_child((' + binary + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                       '$compiled_read(' + state + ', ' + child + ') = (' + number[1] + ')',
                       '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                       '$compiled_comparison_number(' + state + ', ' + child + ') = (' + number[2] + ')']
            if number[3] is None:
                checks += ['$origin_node(' + state + '.SOURCES, ' + child + ') = (NExprConstFetch name_nan_' + str(index) + '_' + str(field) + ' metadata_nan_' + str(index) + '_' + str(field) + ')',
                           '$compiled_special_concat_bytes(' + state + ', ' + child + ') = eps',
                           '$number_text(' + number[2] + ', 14) = ($ptascii("NAN"), true)']
            else:
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + child + ') =/= eps']
        if name == 'greater-left':
            child, changed = binary + '_0', state + '_kind'
            checks += [child + ' = PORIGIN 0 pcpath_nan_kind',
                       changed + ' = ' + state + '[.SOURCES = [{ID 0, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_nan_kind (NScalarFloat (FLOAT "3ff8000000000000") eps))])}]]',
                       '$compiled_read(' + changed + ', ' + child + ') = (PFLOAT ' + NAN + ')',
                       '$compiled_precision(' + changed + ', (' + child + ')) = (14)',
                       '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii("1.5"))',
                       '$compiled_comparison_number(' + changed + ', ' + child + ') = eps']
            for label, replacement in (('invalid', '(PFLOAT 27667864310750642176)'), ('string', '(PSTRING ($ptascii("1.5")))')):
                changed = state + '_' + label
                checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', ' + replacement + ')]',
                           '$compiled_read(' + changed + ', ' + child + ') = ' + replacement,
                           '$compiled_comparison_number(' + changed + ', ' + child + ') = eps']
                checks += ['$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = ' + ('($ptascii(""))' if label == 'string' else 'eps')]
            child, changed = binary + '_1', state + '_coercive'
            checks += [changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + child + ', (PSTRING ($ptascii("1.5"))))]',
                       '$compiled_special_concat_bytes(' + changed + ', ' + child + ') = ($ptascii("1.5"))',
                       '$coerce_number(PSTRING ($ptascii("1.5"))) = COERCED (NFLOAT 4609434218613702656) false',
                       '$compiled_comparison_number(' + changed + ', ' + child + ') = eps',
                       '$compiled_read(' + changed + ', ' + binary + ') = (PBOOL false)',
                       '$compiled_special_concat_bytes(' + changed + ', ' + binary + ') = ($ptascii(""))']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.arithmetic, source.unary, prior, prior.prior, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.conditions = cases, conditions
    runner.compiler_conditions, runner.CONTROLS = compiler_conditions, CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic-source-seeded NaN comparison fixtures add own-result/type, missing child reads, actual child sources and three precision refusals. Signed/payload NaN pool variants keep VALUE admission with BYTE absent. The independent table fixes unordered results for all seven operators with NaN on left/right/both, including reversed greater and integer/zero/infinity/computed partners. A finite-literal source with the same NaN read retains child bytes but fails VALUE provenance; invalid64bit still refuses. String reads retain numeric VALUE refusal, while the exact raw-string selector and partner mutation now check the separate NaN/scalar admission. The exact string replacement on the former NaN side already belongs to the prior mixed STRING/FLOAT domain; its stale predicate is corrected without renewing that earlier cut. Arithmetic NaN and strict identity keep their separate boundaries. Outcome-insensitive NaN comparisons do not establish independent changed-child-value refusals. Source/native4 are reused once, author recipes remain exact prefixes, and owner/throw/fixed-bounds/budget controls remain. The old nan-left selector has its own isolated cut; no unique aggregate or NaN Boolean/string conversion claim. Fixture/compiler conditions carry source0.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
