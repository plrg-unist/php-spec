#!/usr/bin/env python3
"""Independent numeric equality, raw tags and exact certificate boundaries."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_numeric_equality_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

raw = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    '|pfunction.SIGNATURE.PARAMETERS| = 10',
    r'pcallcontext.ARGC = 0 /\ pcallcontext.HOLES = eps',
    'S.CODE = [pcode]',
    'S.SOURCES = [pcunit]',
    'S.POOLS = [ppool]',
    '$default_cache_owner(S) = (CACHE_SHARED)',
]
operands = [
    ('NExprBinaryOpEqual', 'PINT 0', 'PINT 0', 'true'),
    ('NExprBinaryOpNotEqual', 'PINT 0', 'PINT 1', 'true'),
    ('NExprBinaryOpEqual', 'PFLOAT 0', 'PFLOAT 9223372036854775808', 'true'),
    ('NExprBinaryOpNotEqual', 'PFLOAT 0', 'PFLOAT 4607182418800017408', 'true'),
    ('NExprBinaryOpEqual', 'PINT 9223372036854775807', 'PFLOAT 4890909195324358656', 'true'),
    ('NExprBinaryOpNotEqual', 'PFLOAT 4890909195324358656', 'PINT 9223372036854775807', 'false'),
    ('NExprBinaryOpEqual', 'PFLOAT n_bits_6_left', 'PFLOAT n_bits_6_right', 'false'),
    ('NExprBinaryOpNotEqual', 'PFLOAT n_bits_7_left', 'PFLOAT 0', 'true'),
    ('NExprBinaryOpEqual', 'PFLOAT 0', 'PFLOAT n_bits_8_right', 'false'),
    ('NExprBinaryOpNotEqual', 'PFLOAT 9218868437227405312', 'PFLOAT 9218868437227405312', 'false'),
]
for index, (constructor, left, right, truth) in enumerate(operands):
    raw += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.KIND = PDDEFERRED',
        f'$default_parameter_origin(S,porigin_function,{index}) = PORIGIN n_unit pcpath_parameter_{index}',
        f'pcpath_{index} = pcpath_parameter_{index} ++ [PCFIELD 6]',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (expression_{index})',
        f'expression_{index} = {constructor} expression_left_{index} expression_right_{index} metadata_{index}',
        f'porigin_left_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
        f'porigin_right_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])',
        f'$origin_node(S.SOURCES,porigin_left_{index}) = (expression_left_{index})',
        f'$origin_node(S.SOURCES,porigin_right_{index}) = (expression_right_{index})',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index}) = ((z_{index},false))',
        rf'$pool_value(S.POOLS,pdefault_{index}.ORIGIN) = eps /\ $compiled_read(S,pdefault_{index}.ORIGIN) = eps',
        f'$compiled_redirect(S,pdefault_{index}.ORIGIN) = eps',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_left_{index}) = ({left})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_right_{index}) = ({right})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PBOOL {truth})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PBOOL {truth},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'psparam_{index} = pfunction.SIGNATURE.PARAMETERS[{index}]',
        f'$lookup(S.ENV,psparam_{index}.NAME) = (n_cell_{index})',
        f'S.STORE[n_cell_{index}] = DEFINED (PBOOL {truth})',
        f'S_own_code_{index} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_{index} z_{index} true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_own_code_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'S_own_pool_{index} = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_{index} (PBOOL {truth}))] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_own_pool_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
    ]
for index, (_, left, right, _) in enumerate(operands):
    for field, value in enumerate([left, right]):
        nan = 'n_bits_' in value
        if not nan and index != 9:
            continue
        side = 'left' if field == 0 else 'right'
        raw += [
            f'{"" if nan else "~"}$pfcast_nan({value})',
            f'$origin_node(S.SOURCES,porigin_{side}_{index}) = (NExprBinaryOpPlus expression_special_{index}_{side} expression_zero_{index}_{side} metadata_special_{index}_{side})',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_{side}_{index})',
            f'$code_expression(pcode.EXPRESSIONS,pcpath_{index} ++ [PCFIELD {field}]) = ((z_special_{index}_{side},false))',
            rf'$pool_value(S.POOLS,porigin_{side}_{index}) = eps /\ $compiled_read(S,porigin_{side}_{index}) = eps',
            f'$compiled_redirect(S,porigin_{side}_{index}) = eps',
        ]
for index, side, field in [(index, side, field) for index in (0, 1, 3, 6, 7, 8, 9) for side, field in [('left', 0), ('right', 1)]] + [(4, 'left', 0), (5, 'right', 1), (2, 'left', 0)]:
    raw += [
        f'S_{side}_{index}_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_{index} ++ [PCFIELD {field}]) z_{index} true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_{side}_{index}_code,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
    ]
    forged = f'NExprBooleanNot expression_{side}_{index} metadata_{index}'
    if (index, side) in [(4, 'left'), (5, 'right'), (2, 'left')]:
        constructor = 'NExprUnaryPlus' if index == 2 else 'NExprBinaryOpPlus'
        children = f'expression_first_{index}' if index == 2 else f'expression_first_{index} expression_second_{index}'
        raw += [
            f'expression_{side}_{index} = {constructor} {children} metadata_child_{index}',
            f'metadata_child_{index} =/= eps',
        ]
        forged = f'{constructor} {children} eps'
    raw += [
        f'S_{side}_{index}_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_{index} ++ [PCFIELD {field}]) ({forged}))] ++ pcunit.OCCURRENCES)]]]',
        f'~$lossy_optional_integer_phase_safe(S_{side}_{index}_source,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S_{side}_{index}_source,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
    ]
raw += [
    '$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_right_4)',
    '$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_left_5)',
    'S_rounded_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_4 ++ [PCFIELD 1]) z_4 true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_rounded_code,pfunction.ENV,pdefault_4.ORIGIN) = (PBOOL true)',
    'S_bad_read = S_rounded_code[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_4 ++ [PCFIELD 1]) (PINT 0))] ++ ppool.CONSTANTS)]]]',
    '$compiled_read(S_bad_read,porigin_right_4) = (PINT 0)',
    '~$lossy_optional_integer_phase_safe(S_bad_read,pfunction.ENV,porigin_right_4)',
    '$lossy_optional_integer_deferred_value_at(S_bad_read,pfunction.ENV,pdefault_4.ORIGIN) = eps',
]
raw += [
    'S_no_code = S[.CODE = eps]',
    '$lossy_optional_integer_deferred_value_at(S_no_code,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_0[.VALUE = PINT 0])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,0)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,pdefault_7.ORIGIN) = (PBOOL true)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]
for index in range(10):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')


chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
integer = f'((int)({chain}))'
boolean = f'((bool)({chain}))'
unsupported_pairs = [
    ('==', 'NExprBinaryOpEqual', boolean, f'({chain})', 'PBOOL false', 'PFLOAT 0'),
    ('!=', 'NExprBinaryOpNotEqual', f'({chain})', boolean, 'PFLOAT 0', 'PBOOL false'),
    ('==', 'NExprBinaryOpEqual', integer, '"0"', 'PINT 0', None),
    ('!=', 'NExprBinaryOpNotEqual', '"0"', integer, None, 'PINT 0'),
    ('==', 'NExprBinaryOpEqual', 'NULL', integer, 'PNULL', 'PINT 0'),
    ('!=', 'NExprBinaryOpNotEqual', integer, 'NULL', 'PINT 0', 'PNULL'),
    ('<', 'NExprBinaryOpSmaller', integer, f'((int)(!({chain})))', 'PINT 0', 'PINT 1'),
]
unsupported = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    '|pfunction.SIGNATURE.PARAMETERS| = 7',
    '$power_warning_number(PBOOL false) = eps',
    '$power_warning_number(PNULL) = eps',
    '$power_warning_number(PSTRING $ptascii("0")) = eps',
    '$power_warning_number(PINT 9223372036854775808) = eps',
    '$power_warning_number(PFLOAT 18446744073709551616) = eps',
]
for index, (_, constructor, _, _, left, right) in enumerate(unsupported_pairs):
    unsupported += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = ({constructor} expression_left_{index} expression_right_{index} metadata_{index})',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
    ]
    for field, value in enumerate([left, right]):
        expected = 'eps' if value is None else f'({value})'
        unsupported.append(f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {field}])) = {expected}')
    admitted = {0: 'true', 1: 'false', 4: 'true', 5: 'false', 6: 'true'}.get(index)
    unsupported += [
        (f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PBOOL {admitted})'
         if admitted is not None else
         f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps'),
        (f'$lossy_optional_integer_deferred(S,pfunction,{index})' if admitted is not None else
         f'~$lossy_optional_integer_deferred(S,pfunction,{index})'),
    ]

CASES = {
    'deferred-numeric-equality-wrapper-raw-booleans': {
        'source': ROWS['deferred-numeric-equality-wrapper-raw-booleans']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 10 '
                  '-- if S.TODO = $function_tasks(S,pfunction)'),
        'checks': raw,
    },
    'deferred-numeric-equality-wrapper-unsupported-kinds-operators': {
        'source': '<?php function refused280(' + ', '.join(
            f'$p{index} = ({left} {operator} {right})'
            for index, (operator, _, left, right, _, _) in enumerate(unsupported_pairs)
        ) + ') {} refused280();',
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 7'),
        'checks': unsupported,
    },
    'deferred-numeric-equality-wrapper-runtime-result-control': {
        'source': '<?php $left280 = PHP_INT_MAX; echo $left280 == (float)PHP_INT_MAX;',
        'stage': ('S.TODO = (BINARY_RIGHT EQUAL poperand_left z) :: ptask_tail* '
                  '-- if S.RESULT = KNOWN (PFLOAT 4890909195324358656)'),
        'checks': [
            '$lookup(S.ENV,$ptascii("left280")) = (n_left)',
            'S.STORE[n_left] = DEFINED (PINT 9223372036854775807)',
            'S_read = $resolve_at(S,poperand_left,z)',
            'S_read.RESULT = KNOWN (PINT 9223372036854775807)',
            'S_after = $drive_steps(S,1)[.COMPLETION = NORMAL]',
            'S_after.RESULT = KNOWN (PBOOL true)',
            'S_after.TODO = ptask_tail*',
            'S_done = $drive_steps(S_after,1000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
