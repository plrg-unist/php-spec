#!/usr/bin/env python3
"""Independent strict NaN identity and per-occurrence value provenance."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_nan_identity_special_concat_leading_key_cases as cases
import string_offset_request_base_nan_identity_special_concat_leading_key_protocol as source
import string_offset_request_base_numeric_comparison_special_concat_leading_key_review_state as numeric
import string_offset_request_base_string_comparison_special_concat_leading_key_review_state as strings

runner, raw, NAN = numeric.runner, source.strings.bytes_term, source.nan.NAN
VALUES = {name: (numeric.NUMBERS[name][0], numeric.NUMBERS[name][1], None)
          for name in ('i0', 'imax', 'imin', 'f0', 'fn0', 'f15', 'finf')}
VALUES |= {'nan': ('NAN', 'PFLOAT ' + NAN, None), 'true': ('true', 'PBOOL true', None),
           'false': ('false', 'PBOOL false', None), 'null': ('null', 'PNULL', None)}
for name, data in (('text', b'NAN'), ('numeric', b'1.5'), ('empty', b''), ('nul', b'\0'), ('high', b'\xff')):
    VALUES[name] = strings.literal(data), 'PSTRING ' + raw(data), data
OPERATORS = {'IDENTICAL': '===', 'NOTIDENTICAL': '!=='}
ROWS = {operation.lower() + '-' + name + '-' + str(reverse): (operation, name, reverse)
        for operation in OPERATORS for name in VALUES for reverse in ((False,) if name == 'nan' else (False, True))}
CONTROLS = {}
for name, (operation, partner, reverse) in ROWS.items():
    operands = (VALUES[partner][0], 'NAN') if reverse else ('NAN', VALUES[partner][0])
    CONTROLS[name] = ("<?php $x = ((" + operands[0] + ' ' + OPERATORS[operation] + ' ' + operands[1] + ") . null) . 'x';\n").encode()
CONTROLS |= {
    'arithmetic-nan': b"<?php $x = (((1e309-1e309) === NAN) . null) . 'x';\n",
    'array': b"<?php $x = ((NAN !== []) . null) . 'x';\n",
    'object': b"<?php $x = ((NAN !== new stdClass()) . null) . 'x';\n",
    'variable': b"<?php $x = ((NAN !== $missing) . null) . 'x';\n",
    'const-string': b"<?php $x = ((NAN !== PHP_OS) . null) . 'x';\n",
    'const-float': b"<?php $x = ((NAN !== INF) . null) . 'x';\n",
    'not-nan': b"<?php $x = ((!NAN) . null) . 'x';\n"}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('nan_identity_root', 'nan_identity_root_child', 'nan_identity_root_l', 'nan_identity_root_child_l')[index]
    origin, expression = 'porigin_' + tag, 'expression_' + tag
    values = ((VALUES['nan'][1], VALUES['nan'][1]), (VALUES['nan'][1], VALUES['f15'][1]),
              (VALUES['nan'][1], VALUES['nan'][1]), (VALUES['text'][1], VALUES['nan'][1]))[index]
    text = '' if index == 2 else '1'
    nan_fields = (0, 1) if index in (0, 2) else (0,) if index == 1 else (1,)
    guards = [origin + ' = PORIGIN n_nan_identity pcpath_nan_identity',
              origin + '_l = PORIGIN n_nan_identity pcpath_nan_identity_l',
              origin + '_r = PORIGIN n_nan_identity pcpath_nan_identity_r']
    for label, replacement in (('drop', 'eps'), ('wrong', '(PBOOL ' + ('true' if index == 2 else 'false') + ')'),
                               ('type', '(PSTRING ($ptascii("")))' if index == 2 else '(PINT 1)')):
        state = 'S_nan_identity_' + label
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + replacement + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$string_read_request_base_saved(' + state + ', pstringread) = eps']
    for field, suffix in enumerate(('_l', '_r')):
        child = origin + suffix
        guards += ['$compiled_identity_value(S_after, ' + child + ') = (' + values[field] + ')']
        state = 'S_nan_identity_drop' + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', eps)]',
                   '$compiled_identity_value(' + state + ', ' + child + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        state = 'S_nan_identity_precision' + suffix
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + child + ', 17)]',
                   '$compiled_precision(' + state + ', (' + origin + ')) = (14)',
                   '$compiled_precision(' + state + ', (' + child + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        for label, value in (('carrier', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("NAN"))'), ('array', 'PARRAY 0'), ('object', 'POBJECT 0')):
            state = 'S_nan_identity_' + label + suffix
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', (' + value + '))]',
                       '$compiled_identity_value(' + state + ', ' + child + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        if field in nan_fields:
            for bits in (9221120237041090561, 18444492273895866368):
                state = 'S_nan_identity_payload' + suffix + '_' + str(bits)
                guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', (PFLOAT ' + str(bits) + '))]',
                           '$compiled_identity_value(' + state + ', ' + child + ') = (PFLOAT ' + str(bits) + ')',
                           '$compiled_special_concat_bytes(' + state + ', ' + child + ') = eps',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
            state = 'S_nan_identity_invalid' + suffix
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', (PFLOAT 27667864310750642176))]',
                       '$compiled_identity_value(' + state + ', ' + child + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    guards += ['S_nan_identity_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
               '$compiled_precision(S_nan_identity_precision, (' + origin + ')) = (17)',
               '$compiled_precision(S_nan_identity_precision, (' + origin + '_l)) = (14)',
               '$compiled_precision(S_nan_identity_precision, (' + origin + '_r)) = (14)',
               '$compiled_special_concat_bytes(S_nan_identity_precision, ' + origin + ') = eps']
    field = 1 if index in (2, 3) else 0
    nan_origin = origin + ('_l' if field == 0 else '_r')
    left, right = ('expression_nan_identity_float', expression + '_r') if field == 0 else (expression + '_l', 'expression_nan_identity_float')
    shape = 'Identical' if index == 2 else 'NotIdentical'
    guards += ['expression_nan_identity_float = NScalarFloat (FLOAT "3ff8000000000000") metadata_' + tag + ('_l' if field == 0 else '_r'),
               'expression_nan_identity_finite_source = NExprBinaryOp' + shape + ' ' + left + ' ' + right + ' metadata_' + tag,
               'S_nan_identity_kind = S_after[.SOURCES = [{ID n_nan_identity, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_nan_identity expression_nan_identity_finite_source), (PCOCCURRENCE pcpath_nan_identity_l ' + left + '), (PCOCCURRENCE pcpath_nan_identity_r ' + right + ')])}]]',
               '$compiled_read(S_nan_identity_kind, ' + nan_origin + ') = (PFLOAT ' + NAN + ')',
               '$compiled_special_concat_bytes(S_nan_identity_kind, ' + nan_origin + ') = ($ptascii("1.5"))',
               '$compiled_identity_value(S_nan_identity_kind, ' + nan_origin + ') = eps']
    if index in (0, 2):
        guards += ['$compiled_special_concat_bytes(S_nan_identity_kind, ' + origin + ') = eps']
    guards += ['expression_nan_identity_variable = NExprVariable (BYTES "dW5hdXRo") metadata_' + tag,
               'S_nan_identity_source = S_after[.SOURCES = [{ID n_nan_identity, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_nan_identity expression_nan_identity_variable)])}]]',
               '$compiled_special_concat_bytes(S_nan_identity_source, ' + origin + ') = eps',
               'S_nan_identity_live = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]',
               '$compiled_special_concat_bytes(S_nan_identity_live, porigin_key) = ($ptascii("' + ('1x', '-1x', '0x', '-4x')[index] + '"))']
    if index == 1:
        for label, value in (('range', 'PINT 9223372036854775808'), ('bits', 'PFLOAT 18446744073709551616')):
            state = 'S_nan_identity_numeric_' + label
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + '_r, (' + value + '))]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + '_r) = ($ptascii("1.5"))',
                       '$compiled_identity_value(' + state + ', ' + origin + '_r) = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        guards += ['S_nan_identity_numeric_valid = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + '_r, (PINT 4))]',
                   '$compiled_special_concat_bytes(S_nan_identity_numeric_valid, ' + origin + '_r) = ($ptascii("1.5"))',
                   '$compiled_identity_value(S_nan_identity_numeric_valid, ' + origin + '_r) = (PINT 4)',
                   '$compiled_special_concat_bytes(S_nan_identity_numeric_valid, ' + origin + ') = ($ptascii("1"))']
    if index == 3:
        guards += ['S_nan_identity_bytes = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + '_l, (PSTRING ($ptascii("other"))))]',
                   '$compiled_special_concat_bytes(S_nan_identity_bytes, ' + origin + '_l) = ($ptascii("NAN"))',
                   '$compiled_identity_value(S_nan_identity_bytes, ' + origin + '_l) = eps',
                   '$compiled_special_concat_bytes(S_nan_identity_bytes, ' + origin + ') = eps']
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, name in enumerate(CONTROLS):
        state, origin = 'S_nan_identity_control_' + str(index), 'porigin_nan_identity_control_' + str(index)
        binary = origin + '_binary'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_nan_identity_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_nan_identity_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name not in ROWS:
            checks += ['$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            continue
        operation, partner, reverse = ROWS[name]
        rendered, value = ('1', 'PBOOL true') if operation == 'NOTIDENTICAL' else ('', 'PBOOL false')
        checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + value + ')',
                   '$compiled_precision(' + state + ', (' + binary + ')) = (14)',
                   '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(rendered) + '))',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(rendered + 'x') + '))',
                   '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(rendered + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(rendered + 'x') + '))']
        for field in (0, 1):
            label = 'nan' if reverse != (field == 0) else partner
            child, child_value, data = binary + '_' + str(field), VALUES[label][1], VALUES[label][2]
            checks += ['$origin_child((' + binary + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                       '$compiled_read(' + state + ', ' + child + ') = (' + child_value + ')',
                       '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                       '$compiled_identity_value(' + state + ', ' + child + ') = (' + child_value + ')',
                       '$compiled_special_concat_bytes(' + state + ', ' + child + ') ' + ('= eps' if label == 'nan' else '= (' + raw(data) + ')' if data is not None else '=/= eps')]
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
    report['scope'] = 'Four authentic-source-seeded strict NaN fixtures add exact typed projection values, own-result/equal-rendering type, missing reads, both child precisions, carriers/arrays/objects, valid signed/payload NaNs with BYTE absent and invalid64 rejection. Numeric partner type/range and raw-string exact payload are checked directly; valid numeric values need not equal literal BYTE text. A coherent finite source with a retained NaN read/literal BYTE fails the new projection; global BYTE rejection is asserted only in both-NaN contexts where the other genuine NaN still lacks BYTE, preserving the old strict BYTE arm. Independent compiler tables cover IDENTICAL/NOTIDENTICAL, both orientations, equal NaN bits, all quiet scalar types, signed zeros/infinity/signed endpoints, formatted-same NAN text, numeric strings and binary bytes. Direct projections preserve exact types, with no numeric/string coercion. Arithmetic NaN, arrays/objects, variables, unsupported startup-string/FLOAT BYTE providers and direct NaN NOT remain separate. No outcome-insensitive changed-NaN-value refusal, universal malformed-state module33 refusal, old full/source/native/author replay or source-credit sum is claimed; exact author prefixes/native4-once and fixture/compiler source0 remain.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
