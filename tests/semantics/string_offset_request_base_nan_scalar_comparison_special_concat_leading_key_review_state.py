#!/usr/bin/env python3
"""Independent unordered string/NaN and quiet Boolean/null compatibility."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_nan_scalar_comparison_special_concat_leading_key_cases as cases
import string_offset_request_base_nan_scalar_comparison_special_concat_leading_key_protocol as source
import string_offset_request_base_numeric_comparison_special_concat_leading_key_review_state as numeric
import string_offset_request_base_string_comparison_special_concat_leading_key_review_state as strings

runner, raw, NAN = numeric.runner, source.strings.bytes_term, source.nan.NAN
PARTNERS = {'string': (strings.literal(b'x'), 'PSTRING ' + raw(b'x'), b'x', 1, 1),
            'true': ('true', 'PBOOL true', None, 0, 0),
            'false': ('false', 'PBOOL false', None, 1, -1),
            'null': ('null', 'PNULL', None, 1, -1)}
ROWS = {operation.lower() + '-' + name + '-' + str(reverse): (operation, name, reverse)
        for operation in numeric.OPERATORS for name in PARTNERS for reverse in (False, True)}
for name, data in (('empty', b''), ('zero', b'0'), ('nul', b'\0'), ('high', b'\xff')):
    PARTNERS[name] = strings.literal(data), 'PSTRING ' + raw(data), data, 1, 1
    for reverse in (False, True):
        ROWS[name + '-' + str(reverse)] = 'SPACESHIP', name, reverse
PARTNERS['nested'] = '(NAN == NAN)', 'PBOOL false', None, 1, -1
for reverse in (False, True):
    ROWS['nested-' + str(reverse)] = 'SPACESHIP', 'nested', reverse
CONTROLS = {}
for name, (operation, partner, reverse) in ROWS.items():
    operands = (PARTNERS[partner][0], 'NAN') if reverse else ('NAN', PARTNERS[partner][0])
    CONTROLS[name] = ("<?php $x = ((" + operands[0] + ' ' + numeric.OPERATORS[operation] + ' ' + operands[1] + ") . null) . 'x';\n").encode()
CONTROLS |= {
    'arithmetic-nan': b"<?php $x = (((1e309-1e309) < 'x') . null) . 'x';\n",
    'strict-identity': b"<?php $x = ((NAN === NAN) . null) . 'x';\n",
    'unsupported-bool-child': b"<?php $x = ((NAN == (NAN === NAN)) . null) . 'x';\n",
    'array': b"<?php $x = ((NAN == []) . null) . 'x';\n",
    'object': b"<?php $x = ((NAN == new stdClass()) . null) . 'x';\n",
    'variable': b"<?php $x = ((NAN < $missing) . null) . 'x';\n",
    'not-nan': b"<?php $x = ((!NAN) . null) . 'x';\n"}


def result(operation, order, reverse_order):
    return {'LESS': order < 0, 'LESSEQUAL': order <= 0, 'GREATER': reverse_order < 0,
            'GREATEREQUAL': reverse_order <= 0, 'EQUAL': order == 0,
            'NOTEQUAL': order != 0, 'SPACESHIP': order}[operation]


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('nan_scalar_root_child', 'nan_scalar_root_child', 'nan_scalar_root_l', 'nan_scalar_root_child_l')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    nan_suffix, partner_suffix = ('_r', '_l') if index == 3 else ('_l', '_r')
    nan_origin, partner = origin + nan_suffix, origin + partner_suffix
    text = ('', '1', '0', '1')[index]
    guards = [origin + ' = PORIGIN n_nan_scalar pcpath_nan_scalar',
              origin + '_l = PORIGIN n_nan_scalar pcpath_nan_scalar_l',
              origin + '_r = PORIGIN n_nan_scalar pcpath_nan_scalar_r']
    wrong, wrong_type = (('PBOOL true', 'PSTRING ($ptascii(""))'), ('PINT 0', 'PBOOL true'),
                         ('PINT 1', 'PFLOAT 0'), ('PBOOL false', 'PINT 1'))[index]
    for label, replacement in (('drop', 'eps'), ('wrong', '(' + wrong + ')'), ('type', '(' + wrong_type + ')')):
        state = 'S_nan_scalar_' + label
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + replacement + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    for suffix in ('_l', '_r'):
        child = origin + suffix
        state = 'S_nan_scalar_drop' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', eps)]',
                   '$compiled_read(' + state + ', ' + child + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        state = 'S_nan_scalar_precision' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        payload = b'NAN' if suffix == nan_suffix else (b'x', b'', b'1', b'x')[index]
        state = 'S_nan_scalar_carrier' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', (PSTRING_CARRIER INTERNED_STRING ' + raw(payload) + '))]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_nan_scalar_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_nan_scalar_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_nan_scalar_precision, (' + origin + '_l)) = (14)',
               '$compiled_precision(S_nan_scalar_precision, (' + origin + '_r)) = (14)',
               '$compiled_special_concat_bytes(S_nan_scalar_precision, ' + origin + ') = eps']
    for number in (9221120237041090561, 18444492273895866368):
        state = 'S_nan_scalar_payload_' + str(number)
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + nan_origin + ', (PFLOAT ' + str(number) + '))]',
                   '$compiled_comparison_number(' + state + ', ' + nan_origin + ') = (NFLOAT ' + str(number) + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + nan_origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
    guards += ['S_nan_scalar_invalid = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + nan_origin + ', (PFLOAT 27667864310750642176))]',
               '$compiled_comparison_number(S_nan_scalar_invalid, ' + nan_origin + ') = eps',
               '$compiled_special_concat_bytes(S_nan_scalar_invalid, ' + origin + ') = eps']
    shape = ('Greater', 'Spaceship', 'Spaceship', 'NotEqual')[index]
    left, right = ('expression_nan_scalar_float', expression + '_r') if nan_suffix == '_l' else (expression + '_l', 'expression_nan_scalar_float')
    guards += ['expression_nan_scalar_float = NScalarFloat (FLOAT "3ff8000000000000") metadata_' + tag + nan_suffix,
               'expression_nan_scalar_finite_source = NExprBinaryOp' + shape + ' ' + left + ' ' + right + ' metadata_' + tag,
               'S_nan_scalar_kind = S_after[.SOURCES = [{ID n_nan_scalar, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_nan_scalar expression_nan_scalar_finite_source), (PCOCCURRENCE pcpath_nan_scalar_l ' + left + '), (PCOCCURRENCE pcpath_nan_scalar_r ' + right + ')])}]]',
               '$origin_node(S_nan_scalar_kind.SOURCES, ' + origin + ') = (expression_nan_scalar_finite_source)',
               '$compiled_read(S_nan_scalar_kind, ' + nan_origin + ') = (PFLOAT ' + NAN + ')',
               '$compiled_special_concat_bytes(S_nan_scalar_kind, ' + nan_origin + ') = ($ptascii("1.5"))',
               '$compiled_comparison_number(S_nan_scalar_kind, ' + nan_origin + ') = eps',
               '$compiled_special_concat_bytes(S_nan_scalar_kind, ' + origin + ') = eps',
               'expression_nan_scalar_variable = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag,
               'S_nan_scalar_root_source = S_after[.SOURCES = [{ID n_nan_scalar, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_nan_scalar expression_nan_scalar_variable)])}]]',
               '$compiled_special_concat_bytes(S_nan_scalar_root_source, ' + origin + ') = eps']
    left, right = ('expression_nan_scalar_variable', expression + '_r') if partner_suffix == '_l' else (expression + '_l', 'expression_nan_scalar_variable')
    guards += ['S_nan_scalar_partner_source = S_after[.SOURCES = [{ID n_nan_scalar, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_nan_scalar ' + expression + '), (PCOCCURRENCE pcpath_nan_scalar_l ' + left + '), (PCOCCURRENCE pcpath_nan_scalar_r ' + right + ')])}]]',
               '$compiled_special_concat_bytes(S_nan_scalar_partner_source, ' + origin + ') = eps',
               'S_nan_scalar_live = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]',
               '$precision_value(S_nan_scalar_live) = 9',
               '$compiled_special_concat_bytes(S_nan_scalar_live, porigin_key) = ($ptascii("' + ('1x', '-1x', '0x', '-4x')[index] + '"))']
    if index in (0, 3):
        guards += ['S_nan_scalar_bytes = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + partner + ', (PSTRING ($ptascii("y"))))]',
                   '$compiled_special_concat_bytes(S_nan_scalar_bytes, ' + partner + ') = ($ptascii("x"))',
                   '$scalar_plain_order(S_nan_scalar_bytes, PFLOAT ' + NAN + ', PSTRING ($ptascii("y"))) = 1',
                   '$scalar_plain_order(S_nan_scalar_bytes, PSTRING ($ptascii("y")), PFLOAT ' + NAN + ') = 1',
                   '$compiled_special_concat_bytes(S_nan_scalar_bytes, ' + origin + ') = eps']
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_nan_scalar_control_' + str(index), 'porigin_nan_scalar_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_nan_scalar_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_nan_scalar_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name not in ROWS:
            if name in ('strict-identity', 'unsupported-bool-child'):
                checks += ['$compiled_read(' + state + ', ' + binary + ') = (PBOOL false)',
                           '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(""))',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii("x"))',
                           '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("x"))']
            else:
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            continue
        operation, partner, reverse = ROWS[name]
        p = PARTNERS[partner]
        order, reverse_order = (p[4], p[3]) if reverse else (p[3], p[4])
        answer = result(operation, order, reverse_order)
        rendered, value = numeric.text(answer), numeric.value(answer)
        checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + value + ')',
                   '$compiled_precision(' + state + ', (' + binary + ')) = (14)',
                   '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(rendered) + '))',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(rendered + 'x') + '))',
                   '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(rendered + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(rendered + 'x') + '))']
        for field in (0, 1):
            child, is_nan = binary + '_' + str(field), reverse != (field == 0)
            child_value = 'PFLOAT ' + NAN if is_nan else p[1]
            checks += ['$origin_child((' + binary + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                       '$compiled_read(' + state + ', ' + child + ') = (' + child_value + ')',
                       '$compiled_precision(' + state + ', (' + child + ')) = (14)']
            if is_nan:
                checks += ['$compiled_comparison_number(' + state + ', ' + child + ') = (NFLOAT ' + NAN + ')',
                           '$compiled_special_concat_bytes(' + state + ', ' + child + ') = eps']
            else:
                checks += ['$compiled_special_concat_bytes(' + state + ', ' + child + ') ' + ('= (' + raw(p[2]) + ')' if p[2] is not None else '=/= eps')]
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.nan, source.strings, source.arithmetic, source.unary, numeric, strings, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.conditions = cases, conditions
    runner.compiler_conditions, runner.CONTROLS = compiler_conditions, CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic-source-seeded NaN/scalar fixtures add own-result/type, missing reads, both precision directions, carriers, same-order string payload mismatches, valid signed/payload NaN admission with BYTE absent and invalid64 refusal. A finite literal replaces the NaN child in both the parent AST and actual occurrence while retaining its NaN read and quiet literal BYTE; VALUE provenance still refuses. Root/partner source omissions also refuse. Independent fixed-order tables distinguish true reverse order for all seven operations, both orientations and STRING/TRUE/FALSE/NULL partners; empty/NUL/high bytes and certified nested Boolean results retain the same rules. Arithmetic NaN, owning values, variables and direct NaN NOT stay outside. Genuine NaN strict identity and the dependent Boolean child now check their separately reviewed strict VALUE admission; wider uncertified children still refuse. Changed NaN values are not claimed to independently isolate result-insensitive reads. Exact author prefixes/native4-once remain; original failed pre-v1 and corrected pre-v2, affected selectors and joined cuts stay separate with fixture/compiler source0, no old full/source/native/author replay or NaN string/Boolean cast/ownership widening.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
