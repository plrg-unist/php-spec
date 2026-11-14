#!/usr/bin/env python3
"""Direct integer NOT retains Boolean truth and separate private integer caches."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_integer_not_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin',
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("IntNot263")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base263"),$ptascii("E_WARNING")),($ptascii("One263"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_zero,psparam_nonzero,psparam_last]',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps',
    r'pcallcontext.CACHE = eps /\ pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ psparam_zero.BYREF /\ psparam_nonzero.BYREF /\ ~psparam_last.BYREF',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'S.CODE = [pcode]',
]
for name, index, operand, truth, value in [('zero', 1, '0', 'true', '1'),
                                         ('nonzero', 2, '$(-3)', 'false', '0')]:
    checks += [
        f'psparam_{name}.DEFAULT = PSDEFAULT expression_{name} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{name}_parameter',
        f'pcpath_{name} = pcpath_{name}_parameter ++ [PCFIELD 6]',
        f'porigin_{name} = PORIGIN n_unit pcpath_{name}',
        f'porigin_{name}_truth = PORIGIN n_unit (pcpath_{name} ++ [PCFIELD 0])',
        f'porigin_{name}_operand = PORIGIN n_unit (pcpath_{name} ++ [PCFIELD 0,PCFIELD 0])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{name},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{name}) = (expression_{name})',
        f'expression_{name} = NExprCastInt expression_{name}_truth metadata_{name}',
        f'$plstyle(metadata_{name}) = 1',
        f'$origin_node(S.SOURCES,porigin_{name}_truth) = (NExprBooleanNot expression_{name}_operand metadata_{name}_truth)',
        f'$origin_node(S.SOURCES,porigin_{name}_operand) = (expression_{name}_operand)',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}) = ((z_{name},false))',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{name} ++ [PCFIELD 0]) = ((z_{name}_truth,false))',
        rf'$pool_value(S.POOLS,porigin_{name}) = eps /\ $compiled_read(S,porigin_{name}) = eps',
        f'$compiled_redirect(S,porigin_{name}) = eps',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_{name})',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_{name}_truth)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}_operand) = (PINT {operand})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}_truth) = (PBOOL {truth})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}) = (PINT {value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{name} = {{ORIGIN porigin_{name},VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,porigin_{name}) = (pdefaultcache_{name})',
        f'$lookup(S.ENV,psparam_{name}.NAME) = (n_{name})',
        f'S.STORE[n_{name}] = DEFINED (PINT {value})',
        rf'~(n_{name} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_{name}) = 1',
    ]

checks += [
    'n_zero =/= n_nonzero',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    'S.STORE[n_first] = DEFINED (PINT 2)',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 7)',
]
for label, operand, result in [('zero', '0', 'true'), ('negative', '$(-3)', 'false'),
                               ('positive', '3', 'false'), ('min', '$(-9223372036854775808)', 'false'),
                               ('max', '9223372036854775807', 'false')]:
    checks += [
        f'S_{label} = S[.RESULT = KNOWN (PINT {operand})][.BASE = BASE_VALUE (KNOWN (PINT 42))]',
        f'$boolean_result(S_{label},true,z_zero_truth) = S_{label}[.RESULT = KNOWN (PBOOL {result})][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
checks += [
    'S_suppressed = S_negative[.REPORTING = 0]',
    '$boolean_result(S_suppressed,true,z_nonzero_truth) = S_suppressed[.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
    'S_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero[.VALUE = PBOOL true])]',
    '$default_caches_valid(S_tag,S_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_tag,pfunction,1)',
    'S_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_nonzero[.VALUE = PINT 1])]',
    '$default_caches_valid(S_value,S_value.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_value,pfunction,2)',
    '$lossy_optional_integer_deferred(S_value,pfunction,1)',
    'S_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_zero ++ [PCFIELD 0]) z_zero_truth true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_zero_operand) = (PINT 0)',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_zero_truth) = eps',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_zero) = eps',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_nonzero) = (PINT 0)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base263"),$ptascii("E_ERROR")),($ptascii("One263"),$ptascii("E_ERROR"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_zero)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,porigin_zero) = (PINT 1)',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,porigin_nonzero) = (PINT 0)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_zero) = (pdefaultcache_zero)',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_nonzero) = (pdefaultcache_nonzero)',
    r'~((HCELL n_zero) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_zero) = 0',
    r'~((HCELL n_nonzero) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_nonzero) = 0',
    r'~((HCELL n_first) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_first) = 0',
    r'~((HCELL n_last) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_last) = 0',
    '$lookup(S_done.ENV,$ptascii("x263")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

CASES = {'deferred-integer-not-wrapper-private-caches': {
    'source': ROWS['deferred-integer-not-wrapper-alias-named-reentry']['source'],
    'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin '
              '-- if pcallcontext.ARGC = 1 -- if $function_at(S.FUNCTIONS,porigin) = (pfunction) '
              '-- if pfunction.ENV.NAMESPACE = $ptascii("IntNot263") '
              '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 '
              '-- if S.TODO = $function_tasks(S,pfunction)'),
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
