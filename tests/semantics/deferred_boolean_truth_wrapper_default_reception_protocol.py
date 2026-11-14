#!/usr/bin/env python3
"""Boolean identity and inversion retain distinct integer reception caches."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_boolean_truth_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin',
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("BoolTruth262")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base262"),$ptascii("E_WARNING")),($ptascii("One262"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_identity,psparam_negated,psparam_last]',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps',
    r'pcallcontext.CACHE = eps /\ pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ psparam_identity.BYREF /\ psparam_negated.BYREF /\ ~psparam_last.BYREF',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'S.CODE = [pcode]',
]
for name, index, constructor, truth, value in [('identity', 1, 'NExprCastBool', 'true', '1'),
                                              ('negated', 2, 'NExprBooleanNot', 'false', '0')]:
    checks += [
        f'psparam_{name}.DEFAULT = PSDEFAULT expression_{name} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{name}_parameter',
        f'pcpath_{name} = pcpath_{name}_parameter ++ [PCFIELD 6]',
        f'porigin_{name} = PORIGIN n_unit pcpath_{name}',
        f'porigin_{name}_truth = PORIGIN n_unit (pcpath_{name} ++ [PCFIELD 0])',
        f'porigin_{name}_bool = PORIGIN n_unit (pcpath_{name} ++ [PCFIELD 0,PCFIELD 0])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{name},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{name}) = (expression_{name})',
        f'expression_{name} = NExprCastInt expression_{name}_truth metadata_{name}',
        f'$plstyle(metadata_{name}) = 1',
        f'$origin_node(S.SOURCES,porigin_{name}_truth) = ({constructor} expression_{name}_bool metadata_{name}_truth)',
        f'$origin_node(S.SOURCES,porigin_{name}_bool) = (expression_{name}_bool)',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}) = ((z_{name},false))',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{name} ++ [PCFIELD 0]) = ((z_{name}_truth,false))',
        f'$pool_value(S.POOLS,porigin_{name}) = eps /\\ $compiled_read(S,porigin_{name}) = eps',
        f'$compiled_redirect(S,porigin_{name}) = eps',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_{name})',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_{name}_truth)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}_bool) = (PBOOL true)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}_truth) = (PBOOL {truth})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}) = (PINT {value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{name} = {{ORIGIN porigin_{name},VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,porigin_{name}) = (pdefaultcache_{name})',
        f'$lookup(S.ENV,psparam_{name}.NAME) = (n_{name})',
        f'S.STORE[n_{name}] = DEFINED (PINT {value})',
        f'~(n_{name} <- S.REFCELLS) /\\ $heap_owners($heap_graph(S),HCELL n_{name}) = 1',
    ]

checks += [
    '$plstyle(metadata_identity_truth) = 1',
    'n_identity =/= n_negated',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    'S.STORE[n_first] = DEFINED (PINT 2)',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 7)',
    'S_true = S[.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN (PINT 42))]',
    'S_false = S[.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN (PINT 42))]',
    '$cast_apply(S_true,CASTBOOL,PBOOL true,z_identity_truth) = S_true',
    '$cast_apply(S_false,CASTBOOL,PBOOL false,z_identity_truth) = S_false',
    '$boolean_result(S_true,true,z_negated_truth) = S_true[.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
    '$boolean_result(S_false,true,z_negated_truth) = S_false[.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
    'S_suppressed = S_true[.REPORTING = 0]',
    '$cast_apply(S_suppressed,CASTBOOL,PBOOL true,z_identity_truth) = S_suppressed',
    '$boolean_result(S_suppressed,true,z_negated_truth) = S_suppressed[.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
    'S_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_identity[.VALUE = PBOOL true])]',
    '$default_caches_valid(S_tag,S_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_tag,pfunction,1)',
    'S_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_negated[.VALUE = PINT 1])]',
    '$default_caches_valid(S_value,S_value.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_value,pfunction,2)',
    '$lossy_optional_integer_deferred(S_value,pfunction,1)',
    'S_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_identity ++ [PCFIELD 0]) z_identity_truth true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_identity_bool) = (PBOOL true)',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_identity_truth) = eps',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_identity) = eps',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_negated) = (PINT 0)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base262"),$ptascii("E_ERROR")),($ptascii("One262"),$ptascii("E_ERROR"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_identity)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,porigin_identity) = (PINT 1)',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,porigin_negated) = (PINT 0)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_identity) = (pdefaultcache_identity)',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_negated) = (pdefaultcache_negated)',
    r'~((HCELL n_identity) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_identity) = 0',
    r'~((HCELL n_negated) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_negated) = 0',
    r'~((HCELL n_first) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_first) = 0',
    r'~((HCELL n_last) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_last) = 0',
    '$lookup(S_done.ENV,$ptascii("x262")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

CASES = {'deferred-boolean-truth-wrapper-private-caches': {
    'source': ROWS['deferred-boolean-truth-wrapper-alias-named-reentry']['source'],
    'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin '
              '-- if pcallcontext.ARGC = 1 -- if $function_at(S.FUNCTIONS,porigin) = (pfunction) '
              '-- if pfunction.ENV.NAMESPACE = $ptascii("BoolTruth262") '
              '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 '
              '-- if S.TODO = $function_tasks(S,pfunction)'),
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
