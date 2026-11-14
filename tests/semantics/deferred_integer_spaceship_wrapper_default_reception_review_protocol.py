#!/usr/bin/env python3
"""Independent integer orderings, emitted guards and typed refusals."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_integer_spaceship_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

raw = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_less,psparam_equal,psparam_greater]',
    'pcallcontext.ARGC = 0 /\\ pcallcontext.HOLES = eps',
    'S.CODE = [pcode]',
    'S.SOURCES = [pcunit]',
    'S.POOLS = [ppool]',
    '$default_cache_owner(S) = (CACHE_SHARED)',
]
for index, (name, left, right, value) in enumerate([
    ('less', '0', '1', '$(-1)'), ('equal', '1', '1', '0'), ('greater', '1', '0', '1'),
]):
    raw += [
        f'psparam_{name}.DEFAULT = PSDEFAULT expression_{index} "deferred"',
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
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_left_{index}) = (PINT {left})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_right_{index}) = (PINT {right})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT {value})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,psparam_{name}.NAME) = (n_cell_{index})',
        f'S.STORE[n_cell_{index}] = DEFINED (PINT {value})',
        f'S_code_{index} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_{index} z_{index} true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_code_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'S_pool_{index} = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_{index} (PINT {value}))] ++ ppool.CONSTANTS)]]]',
        f'$compiled_read(S_pool_{index},pdefault_{index}.ORIGIN) = eps',
        f'$lossy_optional_integer_deferred_value_at(S_pool_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
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
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_0[.VALUE = PBOOL false])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,0)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,pdefault_0.ORIGIN) = (PINT $(-1))',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_0.ORIGIN) = (pdefaultcache_0)',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_1.ORIGIN) = (pdefaultcache_1)',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_2.ORIGIN) = (pdefaultcache_2)',
    '$heap_valid($heap_graph(S_done)) /\\ $call_descriptors_valid(S_done) /\\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
bool_value = f'((bool)({chain}))'
float_value = f'({chain})'
int_value = f'((int)(!({chain})))'
refused_pairs = [
    (bool_value, int_value, 'PBOOL false', 'PINT 1'),
    (float_value, int_value, 'PFLOAT 0', 'PINT 1'),
    (int_value, bool_value, 'PINT 1', 'PBOOL false'),
    (int_value, float_value, 'PINT 1', 'PFLOAT 0'),
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
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = ({left})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])) = ({right})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S,pfunction,{index})',
    ]

CASES = {
    'deferred-integer-spaceship-wrapper-raw-orders': {
        'source': ROWS['deferred-integer-spaceship-wrapper-raw-orderings']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 3 '
                  '-- if S.TODO = $function_tasks(S,pfunction)'),
        'checks': raw,
    },
    'deferred-integer-spaceship-wrapper-noninteger-refusals': {
        'source': '<?php function refused269(' + ', '.join(
            f'$p{index} = ({left} <=> {right})'
            for index, (left, right, _, _) in enumerate(refused_pairs)
        ) + ') {} refused269();',
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 4'),
        'checks': refused,
    },
    'deferred-integer-spaceship-wrapper-runtime-result-control': {
        'source': '<?php $left269 = 0; echo $left269 <=> 1;',
        'stage': ('S.TODO = (BINARY_RIGHT SPACESHIP poperand_left z) :: ptask_tail* '
                  '-- if S.RESULT = KNOWN (PINT 1)'),
        'checks': [
            '$lookup(S.ENV,$ptascii("left269")) = (n_left)',
            'S.STORE[n_left] = DEFINED (PINT 0)',
            'S_read = $resolve_at(S,poperand_left,z)',
            'S_read.RESULT = KNOWN (PINT 0)',
            'S_after = $drive_steps(S,1)[.COMPLETION = NORMAL]',
            'S_after.RESULT = KNOWN (PINT $(-1))',
            'S_after.TODO = ptask_tail*',
            'S_done = $drive_steps(S_after,1000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'deferred-integer-spaceship-wrapper-ordinary-receive-control': {
        'source': ROWS['deferred-integer-spaceship-wrapper-ordinary-control']['source'],
        'stage': 'S.TODO = [TYPE_RECEIVE porigin_function 0]',
        'checks': [
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.FUNCTION = porigin_function',
            '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
            '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
            '$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault.ORIGIN)',
            '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault.ORIGIN) = (PINT 1)',
            'S_done = $drive_steps(S,3000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
