#!/usr/bin/env python3
"""Independent raw coalesce values, emitted guards and ordinary controls."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_nonnull_coalesce_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

raw = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    'pfunction.ENV.NAMESPACE = eps',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a,psparam_b,psparam_c,psparam_d,psparam_e]',
    'pcallcontext.ARGC = 0 /\\ pcallcontext.HOLES = eps',
    'S.CODE = [pcode]',
    'S.SOURCES = [pcunit]',
    'S.POOLS = [ppool]',
    '$default_cache_owner(S) = (CACHE_SHARED)',
]
for index, (name, value) in enumerate([
    ('a', 'PBOOL false'), ('b', 'PBOOL true'), ('c', 'PFLOAT 0'),
    ('d', 'PFLOAT 9223372036854775808'), ('e', 'PINT 0'),
]):
    raw += [
        f'psparam_{name}.DEFAULT = PSDEFAULT expression_{index} "deferred"',
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.KIND = PDDEFERRED',
        f'$default_parameter_origin(S,porigin_function,{index}) = PORIGIN n_unit pcpath_parameter_{index}',
        f'pcpath_{index} = pcpath_parameter_{index} ++ [PCFIELD 6]',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (expression_{index})',
        f'expression_{index} = NExprBinaryOpCoalesce expression_left_{index} expression_right_{index} metadata_{index}',
        f'porigin_left_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
        f'porigin_right_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])',
        f'$origin_node(S.SOURCES,porigin_left_{index}) = (expression_left_{index})',
        f'$origin_node(S.SOURCES,porigin_right_{index}) = (expression_right_{index})',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index}) = ((z_{index},false))',
        f'$pool_value(S.POOLS,pdefault_{index}.ORIGIN) = eps /\\ $compiled_read(S,pdefault_{index}.ORIGIN) = eps',
        f'$compiled_redirect(S,pdefault_{index}.ORIGIN) = eps',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_left_{index}) = ({value})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_right_{index}) = eps',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,psparam_{name}.NAME) = (n_cell_{index})',
        f'S.STORE[n_cell_{index}] = DEFINED ({value})',
        f'S_code_{index} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_{index} z_{index} true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_code_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'S_pool_{index} = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_{index} ({value}))] ++ ppool.CONSTANTS)]]]',
        f'$compiled_read(S_pool_{index},pdefault_{index}.ORIGIN) = eps',
        f'$lossy_optional_integer_deferred_value_at(S_pool_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'S_marker_{index} = S[.RESULT = KNOWN ({value})][.BASE = BASE_VALUE (KNOWN (PINT 42))]',
        f'$coalesce_result(S_marker_{index},expression_right_{index},1,1) = S_marker_{index}[.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]

raw += [
    'S_right_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_0 ++ [PCFIELD 1]) z_0 true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_right_code,pfunction.ENV,pdefault_0.ORIGIN) = (PBOOL false)',
    'S_right_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_0 ++ [PCFIELD 1]) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
    '~$lossy_optional_integer_phase_safe(S_right_source,pfunction.ENV,pdefault_0.ORIGIN)',
    '$lossy_optional_integer_deferred_value_at(S_right_source,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    'S_left_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) (NExprBooleanNot expression_left_0 metadata_0))] ++ pcunit.OCCURRENCES)]]]',
    '~$lossy_optional_integer_phase_safe(S_left_source,pfunction.ENV,pdefault_0.ORIGIN)',
    '$lossy_optional_integer_deferred_value_at(S_left_source,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    'S_no_code = S[.CODE = eps]',
    '$lossy_optional_integer_deferred_value_at(S_no_code,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    'S_wrong_cache = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_0[.VALUE = PINT 0])]',
    '$default_caches_valid(S_wrong_cache,S_wrong_cache.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_cache,pfunction,0)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,pdefault_3.ORIGIN) = (PFLOAT 9223372036854775808)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_0.ORIGIN) = (pdefaultcache_0)',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_1.ORIGIN) = (pdefaultcache_1)',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_2.ORIGIN) = (pdefaultcache_2)',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_3.ORIGIN) = (pdefaultcache_3)',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_4.ORIGIN) = (pdefaultcache_4)',
    '$heap_valid($heap_graph(S_done)) /\\ $call_descriptors_valid(S_done) /\\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

CASES = {
    'deferred-nonnull-coalesce-wrapper-raw-identity': {
        'source': ROWS['deferred-nonnull-coalesce-wrapper-raw-phases']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 5 '
                  '-- if S.TODO = $function_tasks(S,pfunction)'),
        'checks': raw,
    },
    'deferred-nonnull-coalesce-wrapper-runtime-result-control': {
        'source': '<?php $n268 = true; echo ((!$n268) ?? Missing268) === false;',
        'stage': ('S.TODO = (COALESCE_RESULT expression_right z_left z_right) :: ptask_tail* '
                  '-- if S.RESULT = KNOWN (PBOOL false)'),
        'checks': [
            'S.ORIGIN = (porigin)',
            '$origin_node(S.SOURCES,porigin) = (NExprBinaryOpCoalesce expression_left expression_right metadata)',
            'S_marker = S[.BASE = BASE_VALUE (KNOWN (PINT 42))]',
            'S_after = $drive_steps(S_marker,1)[.COMPLETION = NORMAL]',
            'S_after.RESULT = KNOWN (PBOOL false)',
            'S_after.BASE = BASE_VALUE (KNOWN PNULL)',
            'S_after.TODO = ptask_tail*',
            '$coalesce_result(S_marker[.TODO = ptask_tail*],expression_right,z_left,z_right) = S_after',
            'S_done = $drive_steps(S_after,1000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'deferred-nonnull-coalesce-wrapper-ordinary-receive-control': {
        'source': ROWS['deferred-nonnull-coalesce-wrapper-null-left-control']['source'],
        'stage': 'S.TODO = [TYPE_RECEIVE porigin_function 0]',
        'checks': [
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.FUNCTION = porigin_function',
            '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam]',
            '$default_parameter_origin(S,porigin_function,0) = PORIGIN n_unit pcpath_parameter',
            'pcpath_default = pcpath_parameter ++ [PCFIELD 6]',
            'porigin_default = PORIGIN n_unit pcpath_default',
            '$origin_node(S.SOURCES,porigin_default) = (NExprCastInt expression_coalesce metadata)',
            'porigin_coalesce = PORIGIN n_unit (pcpath_default ++ [PCFIELD 0])',
            '$origin_node(S.SOURCES,porigin_coalesce) = (NExprBinaryOpCoalesce expression_left expression_right metadata_coalesce)',
            '$compiled_redirect(S,porigin_coalesce) = ((porigin_right,expression_right,b,z))',
            'porigin_right = PORIGIN n_unit (pcpath_default ++ [PCFIELD 0,PCFIELD 1])',
            'S_done = $drive_steps(S,3000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
            '$heap_valid($heap_graph(S_done)) /\\ $call_descriptors_valid(S_done) /\\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
