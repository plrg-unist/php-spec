#!/usr/bin/env python3
"""Independent completed-power FLOAT bytes, exact bits and captured precision."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_power_float_special_concat_leading_key_cases as cases
import string_offset_request_base_power_float_special_concat_leading_key_protocol as source
import string_offset_request_base_power_nan_special_concat_leading_key_review_state as prior

runner, NAN, INF = prior.runner, prior.NAN, source.floats.INF
ROWS = {
    'nan-zero': ('NAN ** 0', 4607182418800017408, '1'),
    'nan-null': ('NAN ** null', 4607182418800017408, '1'),
    'nan-text-zero': ("NAN ** '0'", 4607182418800017408, '1'),
    'unit-nan': ('E_ERROR ** NAN', 4607182418800017408, '1'),
    'bool-unit-nan': ('true ** NAN', 4607182418800017408, '1'),
    'inf-negative': ('INF ** -E_WARNING', 0, '0'),
    'negative-inf-negative-odd': ('(-INF) ** -E_ERROR', 9223372036854775808, '-0'),
    'negative-inf-positive-odd': ('(-INF) ** E_ERROR', 18442240474082181120, '-INF'),
    'inf-bool': ('INF ** true', 9218868437227405312, 'INF'),
    'bool-inf': ('false ** INF', 0, '0'),
    'overflow': ('2 ** 63', 4890909195324358656, '9.2233720368548E+18'),
    'text-overflow': ("'2' ** 63", 4890909195324358656, '9.2233720368548E+18'),
    'final-overflow': ('(E_ERROR + 3000000) ** 3', 4897500998791157728, '2.7000027000009E+19'),
}
REFUSALS = {
    'general': 'E_WARNING ** 0.5', 'general-integral-float': '2.0 ** 2',
    'deprecated': '0 ** -E_WARNING', 'nan-byte': 'NAN ** true',
    'int-text': "'2' ** 2", 'int-bool': 'true ** 2', 'int-null': 'null ** 2',
    'warning-child': "NAN ** '0x'", 'nonnumeric-child': "NAN ** 'x'",
    'array-child': 'INF ** []', 'variable-child': 'INF ** $missing', 'float-not': '!NAN',
}
CONTROLS = {name: ('<?php $x = (((' + expression + ") . null) . 'x');\n").encode()
            for name, expression in ({name: row[0] for name, row in ROWS.items()} | REFUSALS).items()}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('power_float_root', 'power_float_root_l', 'power_float_root', 'power_float_root_child_l_l')[index]
    origin, bits = 'porigin_' + tag, source.BITS
    guards = [origin + ' = PORIGIN n_power_float_review pcpath_power_float_review',
              '$compiled_read(S_after, ' + origin + ') = (PFLOAT ' + bits + ')',
              '$compiled_special_concat_bytes(S_after, ' + origin + ') = (n_power_float_text*)']
    for label, replacement in (('drop', 'eps'), ('sign', '(PFLOAT $float_neg(' + bits + '))'),
                               ('invalid', '(PFLOAT 18446744073709551616)'), ('nan', '(PFLOAT ' + NAN + ')'),
                               ('type', '(PINT 1)'), ('raw', '(PSTRING ($ptascii("1")))'),
                               ('carrier', '(PSTRING_CARRIER INTERNED_STRING ($ptascii("1")))'),
                               ('array', '(PARRAY 0)'), ('object', '(POBJECT 0)')):
        state = 'S_power_float_review_' + label
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + replacement + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
    for field, child in enumerate((origin + '_l', origin + '_r')):
        guards += [child + ' = PORIGIN n_power_float_review pcpath_power_float_review_' + str(field)]
        for label, replacement in (('drop', 'eps'), ('invalid', '(PFLOAT 18446744073709551616)'),
                                   ('range', '(PINT 9223372036854775808)'), ('raw', '(PSTRING ($ptascii("bad")))'),
                                   ('carrier', '(PSTRING_CARRIER INTERNED_STRING ($ptascii("2")))'),
                                   ('array', '(PARRAY 0)'), ('object', '(POBJECT 0)')):
            state = 'S_power_float_review_child_' + str(field) + '_' + label
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + replacement + ')]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
        state = 'S_power_float_review_source_' + str(field)
        guards += [state + ' = S_after[.SOURCES = [{ID n_power_float_review, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_power_float_review expression_' + tag + '), (PCOCCURRENCE pcpath_power_float_review_' + str(field) + ' (NExprVariable (BYTES "dW5hdXRo") eps))])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    for number, node in enumerate((origin, origin + '_l', origin + '_r')):
        state = 'S_power_float_review_precision_' + str(number)
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + node + ', 17)]',
                   '$compiled_precision(' + state + ', (' + node + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
    nodes = (origin, origin + '_l', origin + '_r')
    nodes += (origin + '_l_l', origin + '_l_r') if index == 1 else (origin + '_r_child',) if index == 2 else ()
    precision = 'S_after.POOLS'
    for node in nodes:
        precision = '$float_review_precision(' + precision + ', ' + node + ', 17)'
    key = json.dumps(('1x', '-1x', '0x', '-4x')[index])
    guards += ['S_power_float_review_all_precision = S_after[.POOLS = ' + precision + ']',
               '$compiled_special_concat_bytes(S_power_float_review_all_precision, ' + origin + ') = (n_power_float_review_text*)',
               '$parser_literal_text_at(PFLOAT ' + bits + ', 17) = (n_power_float_review_text*)',
               '$compiled_special_concat_bytes(S_power_float_review_all_precision, porigin_key) = ' + ('($ptascii(' + key + '))' if index in (0, 2) else 'eps'),
               'S_power_float_review_source = S_after[.SOURCES = [{ID n_power_float_review, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_power_float_review (NExprVariable (BYTES "dW5hdXRo") eps))])}]]',
               '$compiled_read(S_power_float_review_source, ' + origin + ') = (PFLOAT ' + bits + ')',
               '$compiled_special_concat_bytes(S_power_float_review_source, ' + origin + ') = eps',
               'S_power_float_review_no_code = S_after[.CODE = eps]',
               '$compiled_special_concat_bytes(S_power_float_review_no_code, ' + origin + ') = eps',
               'S_power_float_review_live = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]',
               '$compiled_special_concat_bytes(S_power_float_review_live, ' + origin + ') = (n_power_float_text*)',
               '$compiled_special_concat_bytes(S_power_float_review_live, porigin_key) = ($ptascii(' + key + '))']
    if index == 1:
        guards += ['n_power_float_review_text* =/= n_power_float_text*']
    mutations = ((('_l', 'PFLOAT $float_neg(' + NAN + ')'), ('_l', 'PFLOAT 9221120237041090561'),
                  ('_r', 'PNULL'), ('_r', 'PINT 0')) if index == 0 else
                 (('_r', 'PSTRING ($ptascii("3"))'),) if index == 1 else
                 (('_l', 'PFLOAT $float_neg(' + INF + ')'),) if index == 2 else (('_r', 'PBOOL true'),))
    for number, (suffix, replacement) in enumerate(mutations):
        state, child = 'S_power_float_review_same_' + str(number), origin + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', (' + replacement + '))]',
                   '$compiled_identity_value(' + state + ', ' + child + ') = (' + replacement + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = (n_power_float_text*)',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = ($ptascii(' + key + '))']
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, name in enumerate(checked):
        state, origin = 'S_power_float_control_' + str(index), 'porigin_power_float_control_' + str(index)
        own = origin + '_power'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_power_float_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_power_float_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + own + ')']
        if name not in ROWS:
            checks += ['$compiled_special_concat_bytes(' + state + ', ' + own + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            if name == 'nan-byte':
                checks += ['$compiled_comparison_number(' + state + ', ' + own + ') = (NFLOAT n_power_float_control_nan)',
                           '$fparts_nan($float_decode(n_power_float_control_nan))']
            if name == 'deprecated':
                checks += ['$power_prepare(NINT 0, NINT $(-2)) = POWERDONE (NFLOAT ' + INF + ') true']
            if name == 'general-integral-float':
                checks += ['$power_prepare(NFLOAT 4611686018427387904, NINT 2) = POWERGENERAL n_factor n_base n_exponent n_sign false']
            continue
        _, bits, text = ROWS[name]
        checks += ['$compiled_read(' + state + ', ' + own + ') = (PFLOAT ' + str(bits) + ')',
                   '$compiled_comparison_number(' + state + ', ' + own + ') = (NFLOAT ' + str(bits) + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + own + ') = ($ptascii(' + json.dumps(text) + '))',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(text + 'x') + '))',
                   '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(text + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text + 'x') + '))',
                   '$origin_node(' + state + '.SOURCES, ' + own + ') = (expression_power_float_' + str(index) + ')',
                   '$pfshape(expression_power_float_' + str(index) + ') = PFBINARY POWER expression_power_float_' + str(index) + '_l expression_power_float_' + str(index) + '_r',
                   '$compiled_precision(' + state + ', (' + own + ')) = (14)']
        for field in (0, 1):
            child, value, number = own + '_' + str(field), 'pvalue_power_float_' + str(index) + '_' + str(field), 'pnumber_power_float_' + str(index) + '_' + str(field)
            checks += ['$origin_child((' + own + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                       '$origin_node(' + state + '.SOURCES, ' + child + ') = (expression_power_float_' + str(index) + ('_l' if field == 0 else '_r') + ')',
                       '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                       '$compiled_read(' + state + ', ' + child + ') = (' + value + ')',
                       '$compiled_identity_value(' + state + ', ' + child + ') = (' + value + ')',
                       '$coerce_number(' + value + ') = COERCED ' + number + ' false']
        checks += ['$power_prepare(pnumber_power_float_' + str(index) + '_0, pnumber_power_float_' + str(index) + '_1) = POWERDONE (NFLOAT ' + str(bits) + ') false',
                   '$binary_apply(' + state + ', POWER, pvalue_power_float_' + str(index) + '_0, pvalue_power_float_' + str(index) + '_1, 0) = ' + state + '[.RESULT = KNOWN (PFLOAT ' + str(bits) + ')]']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.prior.prior,
               source.nan, source.floats, source.arithmetic, source.unary, prior, prior.prior, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.conditions = cases, conditions
    runner.compiler_conditions, runner.CONTROLS = compiler_conditions, CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic-source completed POWER non-NaN FLOAT fixtures add exact own bits and signed-result refusals, missing/type/range/own-child source/code and three precision controls. Matching producer precisions17 retain BYTE1/0 in direct CONCATs; comparison parents retain capture14, while final integer overflow also distinguishes formatter14/17. Live precision9 leaves captured bytes unchanged. At the existing compiler-proof boundary, pointwise same-result NaN sign/payload, NULL/int-zero, raw numeric exponent, negative-INF/even exponent and BOOL exponent mutations retain genuine child VALUE and quiet completed-power results. Independent compiler controls cover finite final-multiply overflow, integer-overflow/string coercion, quiet NaN zero/unit cases and signed zero/infinities. GENERAL, Deprecated, NaN BYTE, PINT-result coercive powers, warningful/nonnumeric/array/variable children and FLOAT NOT refuse. Native/source observations are reused once; fixture/compiler evidence is source0 and held boundaries remain separate.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
