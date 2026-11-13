#!/usr/bin/env python3
"""Independent scalar-coerced integer power bytes and compiler-proof boundaries."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_coercive_integer_power_special_concat_leading_key_cases as cases
import string_offset_request_base_coercive_integer_power_special_concat_leading_key_protocol as source
import string_offset_request_base_power_float_special_concat_leading_key_review_state as prior

runner = prior.runner
MINIMUM, MAXIMUM = -9223372036854775808, 9223372036854775807
ROWS = {
    'boolean-base': ('true ** 2', 1, 2, 1), 'false-base': ('false ** 2', 0, 2, 0),
    'boolean-zero': ('false ** false', 0, 0, 1), 'null-positive': ('null ** 2', 0, 2, 0),
    'null-zero': ('null ** false', 0, 0, 1), 'string-base': ("'2' ** 2", 2, 2, 4),
    'string-exponent': ("2 ** '0'", 2, 0, 1), 'both-string': ("'2' ** '3'", 2, 3, 8),
    'negative-string': ("'-2' ** 3", -2, 3, -8), 'space-string': ("' 2 ' ** 2", 2, 2, 4),
    'string-maximum': ("'9223372036854775807' ** true", MAXIMUM, 1, MAXIMUM),
    'string-minimum': ("'-9223372036854775808' ** true", MINIMUM, 1, MINIMUM),
    'huge-exponent': ('true ** 9223372036854775807', 1, MAXIMUM, 1),
}
REFUSALS = {
    'general': 'E_WARNING ** 0.5', 'general-coerced-float': "'2.0' ** 2",
    'deprecated': "0 ** '-2'", 'nan-byte': 'NAN ** true',
    'warning-left': "'2x' ** 2", 'warning-right': "2 ** '2x'",
    'nonnumeric-left': "'x' ** 2", 'empty-string': "'' ** 2",
    'array-left': '[] ** 2', 'array-right': '2 ** []',
    'variable-left': '$missing ** 2', 'float-not': '!NAN',
}
CONTROLS = {name: ('<?php $x = (((' + expression + ") . null) . 'x');\n").encode()
            for name, expression in ({name: row[0] for name, row in ROWS.items()} | REFUSALS).items()}


def term(number):
    return str(number) if number >= 0 else '$(' + str(number) + ')'


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = 'coercive_power_root' + ('_child' if index in (1, 3) else '')
    origin, result = 'porigin_' + tag, (1, 1, 0, 4)[index]
    key = json.dumps(('1x', '-1x', '0x', '-4x')[index])
    guards = [origin + ' = PORIGIN n_coercive_power_review pcpath_coercive_power_review']
    for label, replacement in (('drop', 'eps'), ('wrong', '(PINT 99)'),
                               ('range', '(PINT 9223372036854775808)'), ('float', '(PFLOAT 0)'),
                               ('raw', '(PSTRING ($ptascii("1")))'),
                               ('carrier', '(PSTRING_CARRIER INTERNED_STRING ($ptascii("1")))'),
                               ('array', '(PARRAY 0)'), ('object', '(POBJECT 0)')):
        state = 'S_coercive_power_review_' + label
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + replacement + ')]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
    for field, child in enumerate((origin + '_l', origin + '_r')):
        guards += [child + ' = PORIGIN n_coercive_power_review pcpath_coercive_power_review_' + str(field)]
        for label, replacement in (('drop', 'eps'), ('invalid', '(PFLOAT 18446744073709551616)'),
                                   ('float', '(PFLOAT 0)'), ('range', '(PINT 9223372036854775808)'),
                                   ('raw', '(PSTRING ($ptascii("bad")))'),
                                   ('carrier', '(PSTRING_CARRIER INTERNED_STRING ($ptascii("2")))'),
                                   ('array', '(PARRAY 0)'), ('object', '(POBJECT 0)')):
            state = 'S_coercive_power_review_child_' + str(field) + '_' + label
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + replacement + ')]',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
        state = 'S_coercive_power_review_source_' + str(field)
        guards += [state + ' = S_after[.SOURCES = [{ID n_coercive_power_review, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_coercive_power_review expression_' + tag + '), (PCOCCURRENCE pcpath_coercive_power_review_' + str(field) + ' (NExprVariable (BYTES "dW5hdXRo") eps))])}]]',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
    for number, node in enumerate((origin, origin + '_l', origin + '_r')):
        state = 'S_coercive_power_review_precision_' + str(number)
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + node + ', 17)]',
                   '$compiled_precision(' + state + ', (' + node + ')) = (17)',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
    precision = 'S_after.POOLS'
    for node in (origin, origin + '_l', origin + '_r'):
        precision = '$float_review_precision(' + precision + ', ' + node + ', 17)'
    guards += ['S_coercive_power_review_all_precision = S_after[.POOLS = ' + precision + ']',
               '$compiled_special_concat_bytes(S_coercive_power_review_all_precision, ' + origin + ') = ($decimal_integer(' + str(result) + '))',
               '$compiled_special_concat_bytes(S_coercive_power_review_all_precision, porigin_key) = ' + ('($ptascii(' + key + '))' if index in (0, 2) else 'eps'),
               'S_coercive_power_review_source = S_after[.SOURCES = [{ID n_coercive_power_review, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_coercive_power_review (NExprVariable (BYTES "dW5hdXRo") eps))])}]]',
               '$compiled_read(S_coercive_power_review_source, ' + origin + ') = (PINT ' + str(result) + ')',
               '$compiled_special_concat_bytes(S_coercive_power_review_source, ' + origin + ') = eps',
               'S_coercive_power_review_no_code = S_after[.CODE = eps]',
               '$compiled_special_concat_bytes(S_coercive_power_review_no_code, ' + origin + ') = eps',
               'S_coercive_power_review_live = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]',
               '$compiled_special_concat_bytes(S_coercive_power_review_live, porigin_key) = ($ptascii(' + key + '))']
    mutations = ((('_r', 'PINT 0'), ('_r', 'PNULL'), ('_l', 'PINT 1')),
                 (('_l', 'PINT 3'), ('_l', 'PBOOL true'), ('_r', 'PINT 0')),
                 (('_l', 'PBOOL false'), ('_l', 'PINT 0'), ('_r', 'PINT 3')),
                 (('_l', 'PINT 2'),))[index]
    for number, (suffix, replacement) in enumerate(mutations):
        state, child = 'S_coercive_power_review_same_' + str(number), origin + suffix
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', (' + replacement + '))]',
                   '$compiled_identity_value(' + state + ', ' + child + ') = (' + replacement + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($decimal_integer(' + str(result) + '))',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = ($ptascii(' + key + '))']
    if index in (1, 3):
        child, payload, number = (origin + '_r', '00', 0) if index == 1 else (origin + '_l', '02', 2)
        guards += ['S_coercive_power_review_bytes = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', (PSTRING ($ptascii("' + payload + '"))))]',
                   '$coerce_number(PSTRING ($ptascii("' + payload + '"))) = COERCED (NINT ' + str(number) + ') false',
                   '$compiled_identity_value(S_coercive_power_review_bytes, ' + child + ') = eps',
                   '$compiled_special_concat_bytes(S_coercive_power_review_bytes, ' + origin + ') = eps']
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks = []
    for index, name in enumerate(checked):
        state, origin = 'S_coercive_power_control_' + str(index), 'porigin_coercive_power_control_' + str(index)
        own = origin + '_power'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_coercive_power_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_coercive_power_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + own + ')']
        if name not in ROWS:
            checks += ['$compiled_special_concat_bytes(' + state + ', ' + own + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            continue
        _, left, right, result = ROWS[name]
        checks += ['$compiled_read(' + state + ', ' + own + ') = (PINT ' + term(result) + ')',
                   '$compiled_comparison_number(' + state + ', ' + own + ') = (NINT ' + term(result) + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + own + ') = ($decimal_integer(' + term(result) + '))',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(str(result) + 'x') + '))',
                   '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(str(result) + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(str(result) + 'x') + '))',
                   '$origin_node(' + state + '.SOURCES, ' + own + ') = (expression_coercive_power_' + str(index) + ')',
                   '$pfshape(expression_coercive_power_' + str(index) + ') = PFBINARY POWER expression_coercive_power_' + str(index) + '_l expression_coercive_power_' + str(index) + '_r',
                   '$compiled_precision(' + state + ', (' + own + ')) = (14)']
        for field, number in ((0, left), (1, right)):
            child, value = own + '_' + str(field), 'pvalue_coercive_power_' + str(index) + '_' + str(field)
            checks += ['$origin_child((' + own + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                       '$origin_node(' + state + '.SOURCES, ' + child + ') = (expression_coercive_power_' + str(index) + ('_l' if field == 0 else '_r') + ')',
                       '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                       '$compiled_read(' + state + ', ' + child + ') = (' + value + ')',
                       '$compiled_identity_value(' + state + ', ' + child + ') = (' + value + ')',
                       '$coerce_number(' + value + ') = COERCED (NINT ' + term(number) + ') false']
        checks += ['$type_bytes(pvalue_coercive_power_' + str(index) + r'_0) =/= $ptascii("int") \/ $type_bytes(pvalue_coercive_power_' + str(index) + '_1) =/= $ptascii("int")',
                   '$long_range(' + term(result) + ')',
                   '$power_prepare(NINT ' + term(left) + ', NINT ' + term(right) + ') = POWERDONE (NINT ' + term(result) + ') false',
                   '$binary_apply(' + state + ', POWER, pvalue_coercive_power_' + str(index) + '_0, pvalue_coercive_power_' + str(index) + '_1, 0) = ' + state + '[.RESULT = KNOWN (PINT ' + term(result) + ')]']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.prior.prior,
               source.strings, source.arithmetic, source.unary, prior, prior.prior, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.conditions = cases, conditions
    runner.compiler_conditions, runner.CONTROLS = compiler_conditions, CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic-source scalar-coerced PINT power fixtures add own-result/type/range, missing or malformed children, actual own/child source/code, quiet NINT and three precision guards. Matching producer precisions17 retain direct BYTE1/0; unary parents retain14 and refuse mismatched child precision. Live precision9 leaves captured keys unchanged. At the compiler-proof boundary, pointwise same-result scalar mutations admit, including transitions back to the old strict-PINT arm; different raw bytes refuse identity even with the same quiet integer coercion. Compiler-only programs cover BOOL/NULL, full numeric raw strings, signed parity, LONG endpoints and a huge exponent on1, with both actual source/child facts and exact quiet completed NINT state. GENERAL, Deprecated, NaN BYTE, warningful/nonnumeric/empty strings, arrays/variables and FLOAT NOT refuse. Existing FLOAT and negative-exponent results keep their separate scope. Native/source originals are reused once; fixture/compiler conditions carry source0, and providers/owners/held lanes remain unchanged.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
