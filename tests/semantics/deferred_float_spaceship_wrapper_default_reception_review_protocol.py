#!/usr/bin/env python3
"""Independent FLOAT order, demanded operands and nonNaN boundaries."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_float_spaceship_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

raw = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    '|pfunction.SIGNATURE.PARAMETERS| = 5',
    'pcallcontext.ARGC = 0 /\\ pcallcontext.HOLES = eps',
    'S.CODE = [pcode]',
    'S.SOURCES = [pcunit]',
    'S.POOLS = [ppool]',
    '$default_cache_owner(S) = (CACHE_SHARED)',
]
for index, (left, right, value) in enumerate([
    ('13830554455654793216', '0', '$(-1)'),
    ('0', '9223372036854775808', '0'),
    ('0', '13830554455654793216', '1'),
    ('18442240474082181120', '0', '$(-1)'),
    ('9218868437227405312', '0', '1'),
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
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_left_{index}) = (PFLOAT {left})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_right_{index}) = (PFLOAT {right})',
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
for side, field in [('left', 0), ('right', 1)]:
    raw += [
        f'S_{side}_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_0 ++ [PCFIELD {field}]) z_0 true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_{side}_code,pfunction.ENV,pdefault_0.ORIGIN) = eps',
        f'S_{side}_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_0 ++ [PCFIELD {field}]) (NExprBooleanNot expression_{side}_0 metadata_0))] ++ pcunit.OCCURRENCES)]]]',
        f'~$lossy_optional_integer_phase_safe(S_{side}_source,pfunction.ENV,pdefault_0.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S_{side}_source,pfunction.ENV,pdefault_0.ORIGIN) = eps',
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
for index in range(5):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
refused_pairs = [
    (f'((bool)({chain}))', f'({chain})', 'PBOOL false', 'PFLOAT 0'),
    (f'({chain})', f'((bool)({chain}))', 'PFLOAT 0', 'PBOOL false'),
    ('NAN', f'({chain})', None, 'PFLOAT 0'),
    (f'({chain})', 'NAN', 'PFLOAT 0', None),
]
refused = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    '|pfunction.SIGNATURE.PARAMETERS| = 4',
]
for index, (_, _, left, right) in enumerate(refused_pairs):
    refused += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (NExprBinaryOpSpaceship expression_left_{index} expression_right_{index} metadata_{index})',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
    ]
    for side, field, value in [('left', 0, left), ('right', 1, right)]:
        result = value if value is not None else f'PFLOAT n_nan_{index}'
        refused.append(f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {field}])) = ({result})')
        if value is None:
            refused.append(f'$pfcast_nan(PFLOAT n_nan_{index})')
    refused += [
        (f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT 1)'
         if index >= 2 else
         f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps'),
        (f'$lossy_optional_integer_deferred(S,pfunction,{index})' if index >= 2 else
         f'~$lossy_optional_integer_deferred(S,pfunction,{index})'),
    ]

CASES = {
    'deferred-float-spaceship-wrapper-raw-orders': {
        'source': ROWS['deferred-float-spaceship-wrapper-raw-orderings']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 5 '
                  '-- if S.TODO = $function_tasks(S,pfunction)'),
        'checks': raw,
    },
    'deferred-float-spaceship-wrapper-typed-nan-refusals': {
        'source': '<?php function refused270(' + ', '.join(
            f'$p{index} = ({left} <=> {right})'
            for index, (left, right, _, _) in enumerate(refused_pairs)
        ) + ') {} refused270();',
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 4'),
        'checks': refused,
    },
    'deferred-float-spaceship-wrapper-runtime-result-control': {
        'source': '<?php $left270 = -1.0; echo $left270 <=> 0.0;',
        'stage': ('S.TODO = (BINARY_RIGHT SPACESHIP poperand_left z) :: ptask_tail* '
                  '-- if S.RESULT = KNOWN (PFLOAT 0)'),
        'checks': [
            '$lookup(S.ENV,$ptascii("left270")) = (n_left)',
            'S.STORE[n_left] = DEFINED (PFLOAT 13830554455654793216)',
            'S_read = $resolve_at(S,poperand_left,z)',
            'S_read.RESULT = KNOWN (PFLOAT 13830554455654793216)',
            'S_after = $drive_steps(S,1)[.COMPLETION = NORMAL]',
            'S_after.RESULT = KNOWN (PINT $(-1))',
            'S_after.TODO = ptask_tail*',
            'S_done = $drive_steps(S_after,1000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'deferred-float-spaceship-wrapper-ordinary-receive-control': {
        'source': ROWS['deferred-float-spaceship-wrapper-ordinary-control']['source'],
        'stage': 'S.TODO = [TYPE_RECEIVE porigin_function 0]',
        'checks': [
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.FUNCTION = porigin_function',
            '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
            '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
            '$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault.ORIGIN)',
            '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault.ORIGIN) = (PINT $(-1))',
            'S_done = $drive_steps(S,3000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
