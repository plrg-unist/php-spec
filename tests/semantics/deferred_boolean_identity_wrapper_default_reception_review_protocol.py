#!/usr/bin/env python3
"""Independent Boolean identity truth table, raw tags and kind refusals."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_boolean_identity_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

raw = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    '|pfunction.SIGNATURE.PARAMETERS| = 8',
    r'pcallcontext.ARGC = 0 /\ pcallcontext.HOLES = eps',
    'S.CODE = [pcode]',
    'S.SOURCES = [pcunit]',
    'S.POOLS = [ppool]',
    '$default_cache_owner(S) = (CACHE_SHARED)',
]
for index, (constructor, left, right, truth) in enumerate([
    ('NExprBinaryOpIdentical', 'true', 'true', 'true'),
    ('NExprBinaryOpIdentical', 'true', 'false', 'false'),
    ('NExprBinaryOpIdentical', 'false', 'true', 'false'),
    ('NExprBinaryOpIdentical', 'false', 'false', 'true'),
    ('NExprBinaryOpNotIdentical', 'true', 'true', 'false'),
    ('NExprBinaryOpNotIdentical', 'true', 'false', 'true'),
    ('NExprBinaryOpNotIdentical', 'false', 'true', 'true'),
    ('NExprBinaryOpNotIdentical', 'false', 'false', 'false'),
]):
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
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_left_{index}) = (PBOOL {left})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_right_{index}) = (PBOOL {right})',
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
for index, side, field in [(index, side, field) for index in (0, 1, 4, 5) for side, field in [('left', 0), ('right', 1)]]:
    raw += [
        f'S_{side}_{index}_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_{index} ++ [PCFIELD {field}]) z_{index} true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_{side}_{index}_code,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'S_{side}_{index}_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_{index} ++ [PCFIELD {field}]) (NExprBooleanNot expression_{side}_{index} metadata_{index}))] ++ pcunit.OCCURRENCES)]]]',
        f'~$lossy_optional_integer_phase_safe(S_{side}_{index}_source,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S_{side}_{index}_source,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
    ]
raw += [
    'S_no_code = S[.CODE = eps]',
    '$lossy_optional_integer_deferred_value_at(S_no_code,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_0[.VALUE = PINT 1])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,0)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,pdefault_6.ORIGIN) = (PBOOL true)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]
for index in range(8):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
boolean = f'((bool)({chain}))'
integer = f'((int)({chain}))'
refused_pairs = [
    (operator, constructor, left, right, left_value, right_value)
    for operator, constructor in [('===', 'NExprBinaryOpIdentical'), ('!==', 'NExprBinaryOpNotIdentical')]
    for left, right, left_value, right_value in [
        (boolean, integer, 'PBOOL false', 'PINT 0'),
        (integer, boolean, 'PINT 0', 'PBOOL false'),
        (boolean, f'({chain})', 'PBOOL false', 'PFLOAT 0'),
        (f'({chain})', boolean, 'PFLOAT 0', 'PBOOL false'),
    ]
]
refused = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    '|pfunction.SIGNATURE.PARAMETERS| = 8',
]
for index, (_, constructor, _, _, left, right) in enumerate(refused_pairs):
    refused += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = ({constructor} expression_left_{index} expression_right_{index} metadata_{index})',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = ({left})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])) = ({right})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S,pfunction,{index})',
    ]

CASES = {
    'deferred-boolean-identity-wrapper-raw-booleans': {
        'source': ROWS['deferred-boolean-identity-wrapper-raw-booleans']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 '
                  '-- if S.TODO = $function_tasks(S,pfunction)'),
        'checks': raw,
    },
    'deferred-boolean-identity-wrapper-mixed-kind-refusals': {
        'source': '<?php function refused275(' + ', '.join(
            f'$p{index} = ({left} {operator} {right})'
            for index, (operator, _, left, right, _, _) in enumerate(refused_pairs)
        ) + ') {} refused275();',
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 8'),
        'checks': refused,
    },
    'deferred-boolean-identity-wrapper-runtime-result-control': {
        'source': '<?php $left275 = false; echo $left275 !== true;',
        'stage': ('S.TODO = (BINARY_RIGHT NOTIDENTICAL poperand_left z) :: ptask_tail* '
                  '-- if S.RESULT = KNOWN (PBOOL true)'),
        'checks': [
            '$lookup(S.ENV,$ptascii("left275")) = (n_left)',
            'S.STORE[n_left] = DEFINED (PBOOL false)',
            'S_read = $resolve_at(S,poperand_left,z)',
            'S_read.RESULT = KNOWN (PBOOL false)',
            'S_after = $drive_steps(S,1)[.COMPLETION = NORMAL]',
            'S_after.RESULT = KNOWN (PBOOL true)',
            'S_after.TODO = ptask_tail*',
            'S_done = $drive_steps(S_after,1000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'deferred-boolean-identity-wrapper-ordinary-receive-control': {
        'source': ROWS['deferred-boolean-identity-wrapper-ordinary-control']['source'],
        'stage': 'S.TODO = [TYPE_RECEIVE porigin_function 0]',
        'checks': [
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.FUNCTION = porigin_function',
            '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
            '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
            '$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault.ORIGIN)',
            '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault.ORIGIN) = (PINT 0)',
            'S_done = $drive_steps(S,3000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
