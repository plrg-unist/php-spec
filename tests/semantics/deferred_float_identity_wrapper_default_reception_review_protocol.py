#!/usr/bin/env python3
"""Independent FLOAT identity, signed zeros, Boolean tags and NaN refusals."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_float_identity_wrapper_default_reception_cases.json')
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
    ('NExprBinaryOpIdentical', '0', '9223372036854775808', 'true'),
    ('NExprBinaryOpIdentical', '13830554455654793216', '0', 'false'),
    ('NExprBinaryOpNotIdentical', '0', '9223372036854775808', 'false'),
    ('NExprBinaryOpNotIdentical', '13830554455654793216', '0', 'true'),
    ('NExprBinaryOpIdentical', '9218868437227405312', '9218868437227405312', 'true'),
    ('NExprBinaryOpIdentical', '9218868437227405312', '18442240474082181120', 'false'),
    ('NExprBinaryOpNotIdentical', '9218868437227405312', '9218868437227405312', 'false'),
    ('NExprBinaryOpNotIdentical', '9218868437227405312', '18442240474082181120', 'true'),
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
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_left_{index}) = (PFLOAT {left})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_right_{index}) = (PFLOAT {right})',
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
for index, side, field in [(0, 'left', 0), (0, 'right', 1), (2, 'left', 0), (2, 'right', 1)]:
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
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,pdefault_6.ORIGIN) = (PBOOL false)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]
for index in range(8):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
refused_pairs = [
    ('===', 'NExprBinaryOpIdentical', 'NAN', f'({chain})', None, 'PFLOAT 0'),
    ('===', 'NExprBinaryOpIdentical', f'({chain})', 'NAN', 'PFLOAT 0', None),
    ('!==', 'NExprBinaryOpNotIdentical', 'NAN', f'({chain})', None, 'PFLOAT 0'),
    ('!==', 'NExprBinaryOpNotIdentical', f'({chain})', 'NAN', 'PFLOAT 0', None),
    ('===', 'NExprBinaryOpIdentical', f'((bool)({chain}))', f'({chain})', 'PBOOL false', 'PFLOAT 0'),
    ('!==', 'NExprBinaryOpNotIdentical', f'({chain})', f'((bool)({chain}))', 'PFLOAT 0', 'PBOOL false'),
    ('===', 'NExprBinaryOpIdentical', f'((int)({chain}))', f'({chain})', 'PINT 0', 'PFLOAT 0'),
    ('!==', 'NExprBinaryOpNotIdentical', f'({chain})', f'((int)({chain}))', 'PFLOAT 0', 'PINT 0'),
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
    ]
    for field, value in [(0, left), (1, right)]:
        result = value if value is not None else f'PFLOAT n_nan_{index}'
        refused.append(f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {field}])) = ({result})')
        if value is None:
            refused.append(f'$pfcast_nan(PFLOAT n_nan_{index})')
    refused += [
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S,pfunction,{index})',
    ]

CASES = {
    'deferred-float-identity-wrapper-raw-booleans': {
        'source': ROWS['deferred-float-identity-wrapper-raw-booleans']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 '
                  '-- if S.TODO = $function_tasks(S,pfunction)'),
        'checks': raw,
    },
    'deferred-float-identity-wrapper-nan-kind-refusals': {
        'source': '<?php function refused273(' + ', '.join(
            f'$p{index} = ({left} {operator} {right})'
            for index, (operator, _, left, right, _, _) in enumerate(refused_pairs)
        ) + ') {} refused273();',
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 8'),
        'checks': refused,
    },
    'deferred-float-identity-wrapper-runtime-result-control': {
        'source': '<?php $left273 = -0.0; echo $left273 !== 0.0;',
        'stage': ('S.TODO = (BINARY_RIGHT NOTIDENTICAL poperand_left z) :: ptask_tail* '
                  '-- if S.RESULT = KNOWN (PFLOAT 0)'),
        'checks': [
            '$lookup(S.ENV,$ptascii("left273")) = (n_left)',
            'S.STORE[n_left] = DEFINED (PFLOAT 9223372036854775808)',
            'S_read = $resolve_at(S,poperand_left,z)',
            'S_read.RESULT = KNOWN (PFLOAT 9223372036854775808)',
            'S_after = $drive_steps(S,1)[.COMPLETION = NORMAL]',
            'S_after.RESULT = KNOWN (PBOOL false)',
            'S_after.TODO = ptask_tail*',
            'S_done = $drive_steps(S_after,1000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'deferred-float-identity-wrapper-ordinary-receive-control': {
        'source': ROWS['deferred-float-identity-wrapper-ordinary-control']['source'],
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
