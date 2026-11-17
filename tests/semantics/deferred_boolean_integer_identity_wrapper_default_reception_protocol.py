#!/usr/bin/env python3
"""Actual Boolean/integer identity feeds existing INT parents and private caches."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_boolean_integer_identity_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

PARAMETERS = [
    ('boolSame', 1, 'NExprBinaryOpIdentical', 'PBOOL false', 'PINT 0', 'false', '0'),
    ('intSame', 2, 'NExprBinaryOpIdentical', 'PINT 1', 'PBOOL true', 'false', '0'),
    ('boolDifferent', 3, 'NExprBinaryOpNotIdentical', 'PBOOL false', 'PINT 0', 'true', '1'),
    ('intDifferent', 4, 'NExprBinaryOpNotIdentical', 'PINT 1', 'PBOOL true', 'true', '1'),
]
checks = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin',
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("BooleanIntegerIdentity276")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base276"),$ptascii("E_WARNING")),($ptascii("One276"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_boolSame,psparam_intSame,psparam_boolDifferent,psparam_intDifferent,psparam_last]',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps',
    r'pcallcontext.CACHE = eps /\ pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ psparam_boolSame.BYREF /\ psparam_intSame.BYREF /\ psparam_boolDifferent.BYREF /\ psparam_intDifferent.BYREF /\ ~psparam_last.BYREF',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'S.CODE = [pcode]',
    'S.SOURCES = [pcunit]',
]
for name, index, constructor, left, right, truth, value in PARAMETERS:
    checks += [
        f'psparam_{name}.DEFAULT = PSDEFAULT expression_{name} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{name}_parameter',
        f'pcpath_{name} = pcpath_{name}_parameter ++ [PCFIELD 6]',
        f'porigin_{name} = PORIGIN n_unit pcpath_{name}',
        f'pcpath_{name}_compare = pcpath_{name} ++ [PCFIELD 0]',
        f'porigin_{name}_compare = PORIGIN n_unit pcpath_{name}_compare',
        f'pcpath_{name}_left = pcpath_{name}_compare ++ [PCFIELD 0]',
        f'porigin_{name}_left = PORIGIN n_unit pcpath_{name}_left',
        f'pcpath_{name}_right = pcpath_{name}_compare ++ [PCFIELD 1]',
        f'porigin_{name}_right = PORIGIN n_unit pcpath_{name}_right',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{name},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{name}) = (expression_{name})',
        f'expression_{name} = NExprCastInt expression_{name}_compare metadata_{name}',
        f'$plstyle(metadata_{name}) = 1',
        f'$origin_node(S.SOURCES,porigin_{name}_compare) = (expression_{name}_compare)',
        f'expression_{name}_compare = {constructor} expression_{name}_left expression_{name}_right metadata_{name}_compare',
        f'$origin_node(S.SOURCES,porigin_{name}_left) = (expression_{name}_left)',
        f'$origin_node(S.SOURCES,porigin_{name}_right) = (expression_{name}_right)',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}) = ((z_{name},false))',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}_compare) = ((z_{name}_compare,false))',
        rf'$pool_value(S.POOLS,porigin_{name}_compare) = eps /\ $compiled_read(S,porigin_{name}_compare) = eps',
        f'$compiled_redirect(S,porigin_{name}_compare) = eps',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_{name}_compare)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}_left) = ({left})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}_right) = ({right})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}_compare) = (PBOOL {truth})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}) = (PINT {value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{name} = {{ORIGIN porigin_{name},VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,porigin_{name}) = (pdefaultcache_{name})',
        f'$lookup(S.ENV,psparam_{name}.NAME) = (n_{name})',
        f'S.STORE[n_{name}] = DEFINED (PINT {value})',
        rf'~(n_{name} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_{name}) = 1',
        f'S_own_code_{name} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_{name}_compare z_{name}_compare true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_own_code_{name},pfunction.ENV,porigin_{name}) = eps',
        f'S_left_code_{name} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_{name}_left z_{name}_compare true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_left_code_{name},pfunction.ENV,porigin_{name}) = eps',
        f'S_right_code_{name} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_{name}_right z_{name}_compare true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_right_code_{name},pfunction.ENV,porigin_{name}) = eps',
        f'S_right_source_{name} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_{name}_right (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_right_source_{name},pfunction.ENV,porigin_{name}) = eps',
        f'S_tag_{name} = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{name}[.VALUE = PBOOL {truth}])]',
        f'$default_caches_valid(S_tag_{name},S_tag_{name}.DEFAULTCACHE)',
        f'~$lossy_optional_integer_deferred(S_tag_{name},pfunction,{index})',
    ]

checks += [
    r'n_boolSame =/= n_intSame /\ n_boolSame =/= n_boolDifferent /\ n_boolSame =/= n_intDifferent /\ n_intSame =/= n_boolDifferent /\ n_intSame =/= n_intDifferent /\ n_boolDifferent =/= n_intDifferent',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    'S.STORE[n_first] = DEFINED (PINT 2)',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 7)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base276"),$ptascii("E_ERROR")),($ptascii("One276"),$ptascii("E_ERROR"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_boolSame)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
]
for name, _, _, _, _, _, value in PARAMETERS:
    checks += [
        f'$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,porigin_{name}) = (PINT {value})',
        f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{name}) = (pdefaultcache_{name})',
        rf'~((HCELL n_{name}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_{name}) = 0',
    ]
checks += [
    r'~((HCELL n_first) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_first) = 0',
    r'~((HCELL n_last) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_last) = 0',
    '$lookup(S_done.ENV,$ptascii("x276")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

CASES = {'deferred-boolean-integer-identity-wrapper-private-caches': {
    'source': ROWS['deferred-boolean-integer-identity-wrapper-alias-named-reentry']['source'],
    'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin '
              '-- if pcallcontext.ARGC = 1 -- if $function_at(S.FUNCTIONS,porigin) = (pfunction) '
              '-- if pfunction.ENV.NAMESPACE = $ptascii("BooleanIntegerIdentity276") '
              '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 '
              '-- if S.TODO = $function_tasks(S,pfunction)'),
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
