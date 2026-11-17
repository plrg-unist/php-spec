#!/usr/bin/env python3
"""Independent mixed comparison rounding, demand and nonNaN boundaries."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_mixed_spaceship_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

raw = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    '|pfunction.SIGNATURE.PARAMETERS| = 6',
    'pcallcontext.ARGC = 0 /\\ pcallcontext.HOLES = eps',
    'S.CODE = [pcode]',
    'S.SOURCES = [pcunit]',
    'S.POOLS = [ppool]',
    '$default_cache_owner(S) = (CACHE_SHARED)',
]
for index, (left, right, value) in enumerate([
    ('PINT 9223372036854775807', 'PFLOAT 4890909195324358656', '0'),
    ('PFLOAT 4890909195324358656', 'PINT 9223372036854775807', '0'),
    ('PINT 1', 'PFLOAT 9223372036854775808', '1'),
    ('PFLOAT 9223372036854775808', 'PINT 1', '$(-1)'),
    ('PFLOAT 9218868437227405312', 'PINT 0', '1'),
    ('PINT 1', 'PFLOAT 18442240474082181120', '1'),
]):
    raw += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.KIND = PDDEFERRED',
        f'$default_parameter_origin(S,porigin_function,{index}) = PORIGIN n_unit pcpath_parameter_{index}',
        f'pcpath_{index} = pcpath_parameter_{index} ++ [PCFIELD 6]',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (expression_{index})',
        f'expression_{index} = NExprBinaryOpSpaceship expression_left_{index} expression_right_{index} metadata_{index}',
        f'porigin_left_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
        f'porigin_right_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])',
        f'$origin_node(S.SOURCES,porigin_left_{index}) = (expression_left_{index})',
        f'$origin_node(S.SOURCES,porigin_right_{index}) = (expression_right_{index})',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index}) = ((z_{index},false))',
        f'$pool_value(S.POOLS,pdefault_{index}.ORIGIN) = eps /\\ $compiled_read(S,pdefault_{index}.ORIGIN) = eps',
        f'$compiled_redirect(S,pdefault_{index}.ORIGIN) = eps',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_left_{index}) = ({left})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_right_{index}) = ({right})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT {value})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'S_own_code_{index} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_{index} z_{index} true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_own_code_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'S_own_pool_{index} = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_{index} (PFLOAT 0))] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_own_pool_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
    ]
for index, side, field in [(0, 'left', 0), (0, 'right', 1), (1, 'left', 0), (1, 'right', 1)]:
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
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_0[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,0)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,pdefault_3.ORIGIN) = (PINT $(-1))',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,pdefault_4.ORIGIN) = (PINT 1)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
    '$heap_valid($heap_graph(S_done)) /\\ $call_descriptors_valid(S_done) /\\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]
for index in range(6):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
refused_pairs = [
    ('NAN', f'((int)(!({chain})))', None, 'PINT 1'),
    (f'((int)(!({chain})))', 'NAN', 'PINT 1', None),
]
refused = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    '|pfunction.SIGNATURE.PARAMETERS| = 2',
]
for index, (_, _, left, right) in enumerate(refused_pairs):
    refused += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (NExprBinaryOpSpaceship expression_left_{index} expression_right_{index} metadata_{index})',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
    ]
    for field, value in [(0, left), (1, right)]:
        result = value if value is not None else f'PFLOAT n_nan_{index}'
        refused.append(f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {field}])) = ({result})')
        if value is None:
            refused.append(f'$pfcast_nan(PFLOAT n_nan_{index})')
    refused += [
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT 1)',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
    ]

CASES = {
    'deferred-mixed-spaceship-wrapper-raw-orders': {
        'source': ROWS['deferred-mixed-spaceship-wrapper-raw-orderings']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 '
                  '-- if S.TODO = $function_tasks(S,pfunction)'),
        'checks': raw,
    },
    'deferred-mixed-spaceship-wrapper-typed-nan-refusals': {
        'source': '<?php function refused271(' + ', '.join(
            f'$p{index} = ({left} <=> {right})'
            for index, (left, right, _, _) in enumerate(refused_pairs)
        ) + ') {} refused271();',
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 2'),
        'checks': refused,
    },
    'deferred-mixed-spaceship-wrapper-runtime-result-control': {
        'source': '<?php $left271 = PHP_INT_MAX; echo $left271 <=> (float)PHP_INT_MAX;',
        'stage': ('S.TODO = (BINARY_RIGHT SPACESHIP poperand_left z) :: ptask_tail* '
                  '-- if S.RESULT = KNOWN (PFLOAT 4890909195324358656)'),
        'checks': [
            '$lookup(S.ENV,$ptascii("left271")) = (n_left)',
            'S.STORE[n_left] = DEFINED (PINT 9223372036854775807)',
            'S_read = $resolve_at(S,poperand_left,z)',
            'S_read.RESULT = KNOWN (PINT 9223372036854775807)',
            'S_after = $drive_steps(S,1)[.COMPLETION = NORMAL]',
            'S_after.RESULT = KNOWN (PINT 0)',
            'S_after.TODO = ptask_tail*',
            'S_done = $drive_steps(S_after,1000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'deferred-mixed-spaceship-wrapper-ordinary-receive-control': {
        'source': ROWS['deferred-mixed-spaceship-wrapper-ordinary-control']['source'],
        'stage': 'S.TODO = [TYPE_RECEIVE porigin_function 0]',
        'checks': [
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.FUNCTION = porigin_function',
            '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
            '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
            '$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault.ORIGIN)',
            '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault.ORIGIN) = (PINT 0)',
            'S_done = $drive_steps(S,3000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
