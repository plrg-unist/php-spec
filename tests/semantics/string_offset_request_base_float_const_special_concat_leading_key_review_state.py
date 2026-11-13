#!/usr/bin/env python3
"""Independent FLOAT ConstFetch source, bits and captured-precision checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_float_const_special_concat_leading_key_cases as cases
import string_offset_request_base_float_const_special_concat_leading_key_protocol as source
import string_offset_request_base_numeric_comparison_special_concat_leading_key_review_state as numeric

runner, INF = numeric.runner, source.INF
NAN = '9221120237041090560'
LEAVES = (('float_const_root_l',),
          ('float_const_root_l_child', 'float_const_root_r'),
          ('float_const_root_l_l', 'float_const_root_l_r'),
          ('float_const_root_child_l_l', 'float_const_root_child_l_r_child'))
COMPILER = {
    'imported-inf': ('namespace Local; use const INF as Leaf;', 'Leaf', 'PFLOAT ' + INF, 'INF'),
    'qualified-inf': ('namespace Local;', r'\INF', 'PFLOAT ' + INF, 'INF'),
    'positive-inf': ('', '+INF', 'PFLOAT ' + INF, 'INF'),
    'negative-inf': ('', '-INF', 'PFLOAT ' + source.NINF, '-INF'),
    'same-inf-identity': ('', 'INF === INF', 'PBOOL true', '1'),
    'literal-inf-identity': ('', 'INF === 1e309', 'PBOOL true', '1'),
    'literal-inf-notidentity': ('', 'INF !== 1e309', 'PBOOL false', ''),
    'inf-nan-identity': ('', 'INF === NAN', 'PBOOL false', ''),
    'inf-nan-notidentity': ('', 'INF !== NAN', 'PBOOL true', '1'),
    'nan-inf-identity': ('', 'NAN === INF', 'PBOOL false', ''),
    'infinities-space': ('', 'INF <=> -INF', 'PINT 1', '1'),
    'infinities-reverse': ('', '-INF > INF', 'PBOOL false', ''),
    'same-inf-less': ('', 'INF < INF', 'PBOOL false', ''),
    'sum-inf': ('', 'INF + INF', 'PFLOAT ' + INF, 'INF'),
    'namespace-fallback': ('namespace Local;', 'INF', 'eps', None),
    'namespace-relative': ('namespace Local;', r'namespace\INF', 'eps', None),
    'missing-import': (r'use const Missing\INF as Leaf;', 'Leaf', 'eps', None),
    'startup-os': ('', 'PHP_OS', 'eps', None),
    'startup-sapi': ('', 'PHP_SAPI', 'eps', None),
    'startup-float-max': ('', 'PHP_FLOAT_MAX', 'eps', None),
    'startup-float-min': ('', 'PHP_FLOAT_MIN', 'eps', None),
    'nan-byte': ('', 'NAN', 'PFLOAT ' + NAN, None),
    'arithmetic-nan': ('', '(INF - INF) === NAN', 'PBOOL false', ''),
    'float-not': ('', '!INF', 'eps', None),
    'variable': ('', '$missing', 'eps', None),
    'array': ('', '[]', None, None),
    'object': ('', 'new stdClass()', None, None)}
CONTROLS = {name: ('<?php ' + prefix + ' $x = ((' + expression + ") . null) . 'x';\n").encode()
            for name, (prefix, expression, _, _) in COMPILER.items()}


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    guards = []
    for number, tag in enumerate(LEAVES[index]):
        origin, state = 'porigin_' + tag, 'S_float_const_' + str(number)
        guards += ['$compiled_read(S_after, ' + origin + ') = (PFLOAT ' + INF + ')',
                   '$compiled_precision(S_after, (' + origin + ')) = (14)',
                   '$compiled_special_concat_bytes(S_after, ' + origin + ') = ($ptascii("INF"))']
        for label, replacement in (('drop', 'eps'), ('nan', '(PFLOAT ' + NAN + ')'),
                                   ('payload', '(PFLOAT 9221120237041090561)'),
                                   ('signed_nan', '(PFLOAT 18444492273895866368)'),
                                   ('invalid', '(PFLOAT 18446744073709551616)'),
                                   ('raw', '(PSTRING ($ptascii("INF")))'),
                                   ('carrier', '(PSTRING_CARRIER INTERNED_STRING ($ptascii("INF")))'),
                                   ('array', '(PARRAY 0)'), ('object', '(POBJECT 0)')):
            changed = state + '_' + label
            guards += [changed + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + replacement + ')]',
                       '$compiled_special_concat_bytes(' + changed + ', ' + origin + ') = eps']
        for label, bits, text in (('one', '4607182418800017408', '1'),
                                  ('zero', '0', '0'), ('negative_zero', '9223372036854775808', '-0'),
                                  ('negative_inf', source.NINF, '-INF')):
            changed = state + '_' + label
            guards += [changed + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', (PFLOAT ' + bits + '))]',
                       '$compiled_read(' + changed + ', ' + origin + ') = (PFLOAT ' + bits + ')',
                       '$compiled_order_number(PFLOAT ' + bits + ') = (NFLOAT ' + bits + ')',
                       '$compiled_special_concat_bytes(' + changed + ', ' + origin + ') = ($ptascii(' + json.dumps(text) + '))']
        guards += [state + '_no_code = S_after[.CODE = eps]',
                   '$compiled_read(' + state + '_no_code, ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + '_no_code, ' + origin + ') = eps',
                   state + '_precision = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + origin + ', 17)]',
                   '$compiled_precision(' + state + '_precision, (' + origin + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + '_precision, ' + origin + ') = ($ptascii("INF"))',
                   '$compiled_special_concat_bytes(' + state + '_precision, porigin_key) = eps',
                   '$string_read_request_base_saved(' + state + '_precision, pstringread) = eps',
                   origin + ' = PORIGIN n_float_const_' + str(number) + ' pcpath_float_const_' + str(number),
                   state + '_source = S_after[.SOURCES = [{ID n_float_const_' + str(number) + ', AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_float_const_' + str(number) + ' (NExprVariable (BYTES "dW5hdXRo") eps))])}]]',
                   '$compiled_read(' + state + '_source, ' + origin + ') = (PFLOAT ' + INF + ')',
                   '$compiled_special_concat_bytes(' + state + '_source, ' + origin + ') = eps',
                   state + '_finite = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', (PFLOAT 4607182418800017409))]',
                   '$compiled_special_concat_bytes(' + state + '_finite, ' + origin + ') = ($ptascii("1"))',
                   state + '_finite_precision = ' + state + '_finite[.POOLS = $float_review_precision(' + state + '_finite.POOLS, ' + origin + ', 17)]',
                   '$compiled_special_concat_bytes(' + state + '_finite_precision, ' + origin + ') = ($ptascii("1.0000000000000002"))']
    guards += ['S_float_const_live = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]',
               '$precision_value(S_float_const_live) = 9',
               '$compiled_special_concat_bytes(S_float_const_live, porigin_key) = ($ptascii(' + json.dumps(('1x', '-1x', '0x', '-4x')[index]) + '))']
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, name in enumerate(checked):
        state, origin = 'S_float_const_control_' + str(index), 'porigin_float_const_control_' + str(index)
        child, (_, _, read, text) = origin + '_child', COMPILER[name]
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_float_const_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_float_const_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + child + ')']
        if read is not None:
            checks += ['$compiled_read(' + state + ', ' + child + ') = ' + ('eps' if read == 'eps' else '(' + read + ')')]
        if text is None:
            checks += ['$compiled_special_concat_bytes(' + state + ', ' + child + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
        else:
            checks += ['$compiled_precision(' + state + ', (' + child + ')) = (14)',
                       '$compiled_special_concat_bytes(' + state + ', ' + child + ') = ($ptascii(' + json.dumps(text) + '))',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(text + 'x') + '))',
                       '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(text + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text + 'x') + '))']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.identity, source.arithmetic, source.unary, numeric, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.conditions = cases, conditions
    runner.compiler_conditions, runner.CONTROLS = compiler_conditions, CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic infinity-source fixtures add independent checks at every admitted ConstFetch leaf: actual reads, captured precision, missing reads/code/source, nonNaN valid64 bits, signed zero/infinity, raw/carrier/owning refusal and NaN BYTE refusal. Adjacent finite bits format at the changed captured precision; live precision changes preserve the compiled key. Derived value substitutions use existing internal compiler-proved pool authority and do not validate arbitrary forged pools or require every changed value to invalidate its ancestors. Compiler controls cover imported/qualified and signed infinity, identity/comparison/arithmetic composition, namespace fallback/missing imports, unsupported startup providers, direct NaN/FLOAT NOT and the separately reviewed exact quiet arithmetic-NaN producer VALUE. Fixture/compiler source0 reuses native4 once; no old source/native/full campaign is renewed.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
