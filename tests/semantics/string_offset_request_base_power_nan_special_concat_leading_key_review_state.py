#!/usr/bin/env python3
"""Independent quiet POWERDONE NaN VALUE and exact-result provenance checks."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import string_offset_request_base_power_nan_special_concat_leading_key_cases as cases
import string_offset_request_base_power_nan_special_concat_leading_key_protocol as source
import string_offset_request_base_arithmetic_nan_special_concat_leading_key_review_state as prior

runner, numeric, NAN = prior.runner, prior.numeric, prior.NAN
PRODUCERS = {'base': ('NAN ** 2', 'POWER'), 'exponent': ('2 ** NAN', 'POWER'),
             'fraction': ('(-E_WARNING) ** 0.5', 'POWER'), 'text': ("NAN ** '2'", 'POWER'),
             'null': ('null ** NAN', 'POWER'), 'bool': ('NAN ** true', 'POWER'),
             'string-base': ("'2' ** NAN", 'POWER'), 'both': ('NAN ** NAN', 'POWER'),
             'nested': ('(NAN ** 2) + (2 ** NAN)', 'ADD')}
ROWS = {operation.lower() + '-' + str(reverse):
        (('base', 'exponent', 'fraction', 'text')[index % 4], operation, 'number', reverse)
        for index, operation in enumerate(numeric.OPERATORS) for reverse in (False, True)}
ROWS |= {operation.lower() + '-' + producer:
         (producer, operation, 'nan', bool((index + (operation == 'NOTIDENTICAL')) % 2))
         for index, producer in enumerate(('base', 'exponent', 'fraction', 'text'))
         for operation in ('IDENTICAL', 'NOTIDENTICAL')}
ROWS |= {'strict-' + producer: (producer, 'NOTIDENTICAL', 'nan', bool(index % 2))
         for index, producer in enumerate(PRODUCERS) if producer not in ('base', 'exponent', 'fraction', 'text')}
ROWS |= {operation.lower() + '-text-' + str(reverse): ('text', operation, 'text', reverse)
         for operation in ('NOTEQUAL', 'SPACESHIP') for reverse in (False, True)}
CONTROLS = {}
for name, (producer, operation, partner, reverse) in ROWS.items():
    operands = (prior.PARTNERS[partner][0], PRODUCERS[producer][0]) if reverse else (PRODUCERS[producer][0], prior.PARTNERS[partner][0])
    CONTROLS[name] = ('<?php $x = ((' + operands[0] + ' ' + prior.OPERATORS[operation] + ' ' + operands[1] + ") . null) . 'x';\n").encode()
for name, expression in {'zero-exponent': 'NAN ** 0', 'unit-base': 'true ** NAN',
                         'deprecated': '0 ** -E_WARNING', 'general': 'E_WARNING ** 0.5',
                         'warning-child': "NAN ** '2x'", 'nonnumeric-child': "NAN ** 'x'",
                         'array-child': 'NAN ** []', 'variable-child': 'NAN ** $missing',
                         'float-not': '!NAN'}.items():
    CONTROLS[name] = ('<?php $x = (((' + expression + ") === NAN) . null) . 'x';\n").encode()


def conditions(program, path, index):
    checks, derived = source.conditions(program, path, index)
    tag = ('power_nan_root_l', 'power_nan_root_child_l', 'power_nan_root_l_l', 'power_nan_root_child_l_l')[index]
    origin, bits = 'porigin_' + tag, source.BITS
    guards = [origin + ' = PORIGIN n_power_nan_review pcpath_power_nan_review']
    for label, replacement in (('drop', 'eps'), ('sign', '(PFLOAT $float_neg(' + bits + '))'),
                               ('invalid', '(PFLOAT 18446744073709551616)'), ('finite', '(PFLOAT 4607182418800017408)'),
                               ('raw', '(PSTRING ($ptascii("NAN")))'),
                               ('carrier', '(PSTRING_CARRIER INTERNED_STRING ($ptascii("NAN")))'),
                               ('array', '(PARRAY 0)'), ('object', '(POBJECT 0)')):
        state = 'S_power_nan_review_' + label
        guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + ', ' + replacement + ')]',
                   '$compiled_comparison_number(' + state + ', ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
    for field, suffix in enumerate(('_l', '_r')):
        child = origin + suffix
        guards += [child + ' = PORIGIN n_power_nan_review pcpath_power_nan_review_' + str(field)]
        for label, replacement in (('drop', 'eps'), ('invalid', '(PFLOAT 18446744073709551616)'),
                                   ('range', '(PINT 9223372036854775808)'), ('raw', '(PSTRING ($ptascii("wrong")))'),
                                   ('carrier', '(PSTRING_CARRIER INTERNED_STRING ($ptascii("2")))'),
                                   ('array', '(PARRAY 0)'), ('object', '(POBJECT 0)')):
            state = 'S_power_nan_review_child_' + str(field) + '_' + label
            guards += [state + ' = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + child + ', ' + replacement + ')]',
                       '$compiled_comparison_number(' + state + ', ' + origin + ') = eps',
                       '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
        state = 'S_power_nan_review_source_' + str(field)
        guards += [state + ' = S_after[.SOURCES = [{ID n_power_nan_review, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_power_nan_review expression_' + tag + '), (PCOCCURRENCE pcpath_power_nan_review_' + str(field) + ' (NExprVariable (BYTES "dW5hdXRo") eps))])}]]',
                   '$compiled_comparison_number(' + state + ', ' + origin + ') = eps']
    for number, node in enumerate((origin, origin + '_l', origin + '_r')):
        state = 'S_power_nan_review_precision_' + str(number)
        guards += [state + ' = S_after[.POOLS = $float_review_precision(S_after.POOLS, ' + node + ', 17)]',
                   '$compiled_precision(' + state + ', (' + node + ')) = (17)',
                   '$compiled_comparison_number(' + state + ', ' + origin + ') = eps',
                   '$compiled_special_concat_bytes(' + state + ', porigin_key) = eps']
    precision = 'S_after.POOLS'
    for node in (origin, origin + '_l', origin + '_r') + ((origin + '_l_child',) if index == 1 else ()):
        precision = '$float_review_precision(' + precision + ', ' + node + ', 17)'
    guards += ['S_power_nan_review_all_precision = S_after[.POOLS = ' + precision + ']',
               '$compiled_comparison_number(S_power_nan_review_all_precision, ' + origin + ') = (NFLOAT ' + bits + ')',
               '$compiled_special_concat_bytes(S_power_nan_review_all_precision, porigin_key) = eps',
               'S_power_nan_review_source = S_after[.SOURCES = [{ID n_power_nan_review, AST (PROGRAM eps), OCCURRENCES ([(PCOCCURRENCE pcpath_power_nan_review (NExprVariable (BYTES "dW5hdXRo") eps))])}]]',
               '$compiled_read(S_power_nan_review_source, ' + origin + ') = (PFLOAT ' + bits + ')',
               '$compiled_comparison_number(S_power_nan_review_source, ' + origin + ') = eps',
               'S_power_nan_review_no_code = S_after[.CODE = eps]',
               '$compiled_comparison_number(S_power_nan_review_no_code, ' + origin + ') = eps',
               'S_power_nan_review_live = S_after[.PRECISIONINI = $ptascii("9")][.PRECISIONMODIFIED = true]',
               '$compiled_comparison_number(S_power_nan_review_live, ' + origin + ') = (NFLOAT ' + bits + ')',
               '$compiled_special_concat_bytes(S_power_nan_review_live, porigin_key) = ($ptascii(' + json.dumps(('1x', '-1x', '0x', '-4x')[index]) + '))']
    if index in (0, 1):
        replacement = 'PBOOL true' if index == 0 else 'PSTRING ($ptascii("0.5"))'
        guards += ['S_power_nan_review_same_result = S_after[.POOLS = $special_review_pools(S_after.POOLS, ' + origin + '_r, (' + replacement + '))]',
                   '$compiled_identity_value(S_power_nan_review_same_result, ' + origin + '_r) = (' + replacement + ')',
                   '$compiled_comparison_number(S_power_nan_review_same_result, ' + origin + ') = (NFLOAT ' + bits + ')',
                   '$compiled_special_concat_bytes(S_power_nan_review_same_result, porigin_key) = ($ptascii(' + json.dumps(('1x', '-1x')[index]) + '))']
    return checks + guards, derived + len(guards)


def compiler_conditions(checked, paths):
    checks, certified = [], set()
    for index, name in enumerate(checked):
        state, origin = 'S_power_nan_control_' + str(index), 'porigin_power_nan_control_' + str(index)
        binary, own = origin + '_binary', origin + '_producer'
        checks += [state + ' = $php_run(' + checked[name]['fixture'] + ', 0, ' + json.dumps(base64.b64encode(bytes(paths[name])).decode()) + ')',
                   state + '.COMPLETION = BUDGET',
                   '$special_review_concat_path(' + state + '.SOURCES[0].OCCURRENCES) = (pcpath_power_nan_control_' + str(index) + ')',
                   origin + ' = PORIGIN 0 pcpath_power_nan_control_' + str(index),
                   '$origin_child((' + origin + '), [PCFIELD 0, PCFIELD 0]) = (' + binary + ')']
        if name not in ROWS:
            checks += ['$origin_child((' + binary + '), [PCFIELD 0]) = (' + own + ')']
            if name in ('zero-exponent', 'unit-base'):
                checks += ['$compiled_read(' + state + ', ' + own + ') = (PFLOAT 4607182418800017408)',
                           '$compiled_comparison_number(' + state + ', ' + own + ') = (NFLOAT 4607182418800017408)',
                           '$compiled_special_concat_bytes(' + state + ', ' + own + ') = ($ptascii("1"))',
                           '$compiled_read(' + state + ', ' + binary + ') = (PBOOL false)',
                           '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(""))',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii("x"))',
                           '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii("x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("x"))']
            else:
                checks += ['$compiled_comparison_number(' + state + ', ' + own + ') = eps',
                           '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = eps',
                           '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = eps']
            if name == 'general':
                checks += ['$power_prepare(NINT 2, NFLOAT 4602678819172646912) = POWERGENERAL n_factor n_base n_exponent n_sign false']
            if name == 'deprecated':
                checks += ['$power_prepare(NINT 0, NINT $(-2)) = POWERDONE (NFLOAT 9218868437227405312) true']
            continue
        producer, operation, partner, reverse = ROWS[name]
        result = 1 if operation == 'SPACESHIP' else operation in ('NOTEQUAL', 'NOTIDENTICAL')
        text, value, bits = numeric.text(result), numeric.value(result), 'n_power_nan_control_' + str(index)
        checks += ['$compiled_read(' + state + ', ' + binary + ') = (' + value + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + binary + ') = ($ptascii(' + json.dumps(text) + '))',
                   '$compiled_special_concat_bytes(' + state + ', ' + origin + ') = ($ptascii(' + json.dumps(text + 'x') + '))',
                   '$compiled_string_value(' + state + ', ' + origin + ', PSTRING ($ptascii(' + json.dumps(text + 'x') + '))) = PSTRING_CARRIER INTERNED_STRING ($ptascii(' + json.dumps(text + 'x') + '))',
                   '$origin_child((' + binary + '), [PCFIELD ' + str(1 if reverse else 0) + ']) = (' + own + ')',
                   '$origin_child((' + binary + '), [PCFIELD ' + str(0 if reverse else 1) + ']) = (' + binary + '_partner)',
                   '$compiled_read(' + state + ', ' + binary + '_partner) = (' + prior.PARTNERS[partner][1] + ')',
                   '$compiled_read(' + state + ', ' + own + ') = (PFLOAT ' + bits + ')',
                   '$fparts_nan($float_decode(' + bits + '))',
                   '$compiled_comparison_number(' + state + ', ' + own + ') = (NFLOAT ' + bits + ')',
                   '$compiled_special_concat_bytes(' + state + ', ' + own + ') = eps']
        if producer in certified:
            continue
        certified.add(producer)
        expression, operation = 'expression_power_nan_' + str(index), PRODUCERS[producer][1]
        checks += ['$origin_node(' + state + '.SOURCES, ' + own + ') = (' + expression + ')',
                   '$pfshape(' + expression + ') = PFBINARY ' + operation + ' ' + expression + '_l ' + expression + '_r',
                   '$compiled_precision(' + state + ', (' + own + ')) = (14)']
        for field, suffix in enumerate(('_l', '_r')):
            child, value, number = own + suffix, 'pvalue_power_nan_' + str(index) + suffix, 'pnumber_power_nan_' + str(index) + suffix
            checks += ['$origin_child((' + own + '), [PCFIELD ' + str(field) + ']) = (' + child + ')',
                       '$origin_node(' + state + '.SOURCES, ' + child + ') = (' + expression + suffix + ')',
                       '$compiled_precision(' + state + ', (' + child + ')) = (14)',
                       '$compiled_read(' + state + ', ' + child + ') = (' + value + ')',
                       '$compiled_identity_value(' + state + ', ' + child + ') = (' + value + ')',
                       '$coerce_number(' + value + ') = COERCED ' + number + ' false']
        if producer == 'nested':
            checks += ['$number_binary(ADD, pnumber_power_nan_' + str(index) + '_l, pnumber_power_nan_' + str(index) + '_r) = NUM (NFLOAT ' + bits + ')']
        else:
            checks += ['$power_prepare(pnumber_power_nan_' + str(index) + '_l, pnumber_power_nan_' + str(index) + '_r) = POWERDONE (NFLOAT ' + bits + ') false']
        checks += ['$binary_apply(' + state + ', ' + operation + ', pvalue_power_nan_' + str(index) + '_l, pvalue_power_nan_' + str(index) + '_r, 0) = ' + state + '[.RESULT = KNOWN (PFLOAT ' + bits + ')]']
        if producer == 'base':
            for label, alternative in (('sign', '$float_neg(' + NAN + ')'), ('payload', '9221120237041090561')):
                changed, result = state + '_' + label, 'n_power_nan_' + label
                checks += [changed + '_pure = $binary_apply(' + state + ', POWER, PFLOAT ' + alternative + ', PINT 2, 0)',
                           changed + '_pure.RESULT = KNOWN (PFLOAT ' + result + ')',
                           changed + '_pure = ' + state + '[.RESULT = KNOWN (PFLOAT ' + result + ')]',
                           result + ' =/= ' + bits,
                           changed + ' = ' + state + '[.POOLS = $special_review_pools(' + state + '.POOLS, ' + own + '_l, (PFLOAT ' + alternative + '))]',
                           '$compiled_comparison_number(' + changed + ', ' + own + ') = eps',
                           changed + '_coherent = ' + changed + '[.POOLS = $special_review_pools(' + changed + '.POOLS, ' + own + ', (PFLOAT ' + result + '))]',
                           '$compiled_comparison_number(' + changed + '_coherent, ' + own + ') = (NFLOAT ' + result + ')',
                           '$compiled_special_concat_bytes(' + changed + '_coherent, ' + own + ') = eps',
                           '$compiled_special_concat_bytes(' + changed + '_coherent, ' + origin + ') = ($ptascii(' + json.dumps(text + 'x') + '))']
    return checks


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    watched = [Path(module.__file__) for module in (source, source.prior, source.prior.prior,
               source.nan, source.strings, source.floats, source.arithmetic, source.unary, prior, numeric, runner)] + [Path(__file__)]
    before = {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.cases, runner.conditions = cases, conditions
    runner.compiler_conditions, runner.CONTROLS = compiler_conditions, CONTROLS
    passed = runner.main(expected_outputs=cases.OUTPUTS)
    assert before == {str(path.resolve()): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    report['scope'] = 'Four authentic POWERDONE NaN fixtures retain actual own/child source/read/precision, genuine scalar VALUE, quiet coercions and exact completed-power result bits. Missing, invalid, range, source/code, precision and array/object/carrier payload controls refuse; pointwise same-result scalar mutations admit at the existing compiler-proof boundary. Compiler-only cases cover NaN base/exponent, negative fractional base, both NaNs, BOOL/NULL/full numeric strings and nested arithmetic, seven weak and two strict comparisons and raw-string partners. Signed/payload mutations require exact recomputed own bits. The separate completed non-NaN FLOAT BYTE slice promotes only zero-exponent/unit-base controls without renewing this earlier campaign. POWERGENERAL, Deprecated, warningful/nonnumeric, array/variable and FLOAT NOT controls refuse. NaN BYTE, wider producers/owners/lifetimes and exact held Source47 remain partial. Native/source observations are reused once; fixture/compiler evidence carries source0 without historical campaign renewal.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
