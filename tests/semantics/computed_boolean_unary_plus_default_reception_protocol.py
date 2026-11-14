#!/usr/bin/env python3
"""Direct Boolean unary plus keeps raw integer caches and private formal ownership."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('computed_boolean_unary_plus_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    'S.CURRENT = (pcallcontext)',
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pcallcontext.FUNCTION = porigin',
    'pfunction.NAME = $ptascii("booleanUnaryDefaults250")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_comparison,psparam_equal,psparam_cast,psparam_negation,psparam_exclusive]',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps /\ pcallcontext.CACHE = eps',
    r'pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ psparam_comparison.BYREF',
    r'~psparam_equal.BYREF /\ ~psparam_cast.BYREF /\ ~psparam_negation.BYREF /\ ~psparam_exclusive.BYREF',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    'S.STORE[n_first] = DEFINED (PINT 1)',
    r'~(n_first <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_first) = 1',
    'S.CODE = [pcode]',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xBooleanUnary250")) = (n_global)',
    'S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
]
VALUES = [(1,'comparison','true',1,'1'),(2,'equal','false',0,'0'),
          (3,'cast','true',1,'1'),(4,'negation','false',0,'0'),
          (5,'exclusive','true',1,'1')]
for index,label,truth,operand,integer in VALUES:
    checks.extend([
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{label},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        rf'$pool_value(S.POOLS,porigin_{label}) = eps /\ $compiled_read(S,porigin_{label}) = eps',
        f'expression_{label} = NExprUnaryPlus expression_{label}_boolean metadata_{label}',
        f'$lossy_optional_integer_boolean_shape(expression_{label}_boolean)',
        f'~$lossy_optional_integer_selection_shape(expression_{label}_boolean)',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}_boolean) = eps',
        f'$lossy_optional_integer_condition(pfunction.ENV,expression_{label}_boolean) = ({truth})',
        f'$lossy_optional_integer_quiet_operand(pfunction.ENV,expression_{label}_boolean) = (NINT {operand})',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = eps',
        f'$lossy_optional_integer_float_literal(expression_{label}) = eps',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = (NINT {integer})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = (PINT {integer})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_{label})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE PINT {integer},CLASS PVSCALAR}}',
        f'$default_current_cache(S,porigin_{label}) = (pdefaultcache_{label})',
        f'$lookup(S.ENV,psparam_{label}.NAME) = (n_local_{label})',
        f'S.STORE[n_local_{label}] = DEFINED (PINT {integer})',
        rf'~(n_local_{label} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_local_{label}) = 1',
        f'S_wrong_{label} = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{label}[.VALUE = PBOOL {truth}])]',
        f'$default_caches_valid(S_wrong_{label},S_wrong_{label}.DEFAULTCACHE)',
        f'~$lossy_optional_integer_deferred(S_wrong_{label},pfunction,{index})',
    ])
checks.extend([
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("E_WARNING"),$ptascii("E_ERROR"))]]',
    '$lossy_optional_integer_numeric(plenv_wrong,expression_comparison) = (NINT 0)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_comparison)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_comparison])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,1)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$lookup(S_done.ENV,$ptascii("xBooleanUnary250")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'~((HCELL n_first) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_first) = 0',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])
for index,label,truth,operand,integer in VALUES:
    checks.extend([
        f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})',
        rf'~((HCELL n_local_{label}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_local_{label}) = 0',
    ])

CASES = {'computed-boolean-unary-plus-body-cache-retirement': {
    'source': ROWS['computed-boolean-unary-plus-cold-warm']['source'],
    'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin '
              '-- if $function_at(S.FUNCTIONS,porigin) = (pfunction) '
              '-- if pfunction.NAME = $ptascii("booleanUnaryDefaults250") '
              '-- if S.TODO = $function_tasks(S,pfunction)'),
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
