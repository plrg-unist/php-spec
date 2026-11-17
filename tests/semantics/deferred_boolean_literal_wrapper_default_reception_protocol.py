#!/usr/bin/env python3
"""Literal BOOL certificates retain their tags through real private reception."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_boolean_literal_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

PARAMETERS = [
    ('boolZero', 1, 'NExprBinaryOpEqual', 'false', 'PINT 0', 'PBOOL true', '1'),
    ('nanSpace', 3, 'NExprBinaryOpSpaceship', 'true', 'PFLOAT n_nan', 'PINT 0', '0'),
]
checks = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin',
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("BooleanLiteral285")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base285"),$ptascii("E_WARNING")),($ptascii("One285"),$ptascii("E_ERROR")),($ptascii("Nan285"),$ptascii("NAN"))]',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps',
    r'pcallcontext.CACHE = eps /\ pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'S.CODE = [pcode]',
    'S.SOURCES = [pcunit]',
    'S.POOLS = [ppool]',
]
for name, index, constructor, boolean, sibling, raw, value in PARAMETERS:
    checks += [
        f'psparam_{name} = pfunction.SIGNATURE.PARAMETERS[{index}]',
        f'psparam_{name}.BYREF',
        f'psparam_{name}.DEFAULT = PSDEFAULT expression_{name} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{name}_parameter',
        f'pcpath_{name} = pcpath_{name}_parameter ++ [PCFIELD 6]',
        f'porigin_{name} = PORIGIN n_unit pcpath_{name}',
        f'pcpath_{name}_compare = pcpath_{name} ++ [PCFIELD 0]',
        f'porigin_{name}_compare = PORIGIN n_unit pcpath_{name}_compare',
        f'pcpath_{name}_bare = pcpath_{name}_compare ++ [PCFIELD 0]',
        f'porigin_{name}_bare = PORIGIN n_unit pcpath_{name}_bare',
        f'pcpath_{name}_sibling = pcpath_{name}_compare ++ [PCFIELD 1]',
        f'porigin_{name}_sibling = PORIGIN n_unit pcpath_{name}_sibling',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{name},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{name}) = (expression_{name})',
        f'expression_{name} = NExprCastInt expression_{name}_compare metadata_{name}',
        f'$origin_node(S.SOURCES,porigin_{name}_compare) = (expression_{name}_compare)',
        f'expression_{name}_compare = {constructor} expression_{name}_bare expression_{name}_sibling metadata_{name}_compare',
        f'$origin_node(S.SOURCES,porigin_{name}_bare) = (expression_{name}_bare)',
        f'$origin_node(S.SOURCES,porigin_{name}_sibling) = (expression_{name}_sibling)',
        f'$lossy_optional_integer_special(pfunction.ENV,expression_{name}_bare) = (PBOOL {boolean})',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}) = ((z_{name},false))',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}_compare) = ((z_{name}_compare,false))',
        rf'$pool_value(S.POOLS,porigin_{name}_compare) = eps /\ $compiled_read(S,porigin_{name}_compare) = eps',
        f'$compiled_redirect(S,porigin_{name}_compare) = eps',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_{name}_compare)',
        f'$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_{name}_bare)',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}_bare) = ((z_{name}_bare,true))',
        f'$pool_value(S.POOLS,porigin_{name}_bare) = (PBOOL {boolean})',
        f'$compiled_read(S,porigin_{name}_bare) = (PBOOL {boolean})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{name}_bare) = (PBOOL {boolean})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}_bare) = (PBOOL {boolean})',
        f'$power_warning_number(PBOOL {boolean}) = eps',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}_sibling) = ({sibling})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}_compare) = ({raw})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}) = (PINT {value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{name} = {{ORIGIN porigin_{name},VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,porigin_{name}) = (pdefaultcache_{name})',
        f'$lookup(S.ENV,psparam_{name}.NAME) = (n_{name})',
        f'S.STORE[n_{name}] = DEFINED (PINT {value})',
        rf'~(n_{name} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_{name}) = 1',
        f'S_own_code_{name} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_{name}_compare z_{name}_compare true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_own_code_{name},pfunction.ENV,porigin_{name}) = eps',
        f'S_sibling_code_{name} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_{name}_sibling z_{name}_compare true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_sibling_code_{name},pfunction.ENV,porigin_{name}) = eps',
        f'S_bare_source_{name} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_{name}_bare (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_bare_source_{name},pfunction.ENV,porigin_{name}) = eps',
        f'S_tag_{name} = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{name}[.VALUE = PBOOL false])]',
        f'$default_caches_valid(S_tag_{name},S_tag_{name}.DEFAULTCACHE)',
        f'~$lossy_optional_integer_deferred(S_tag_{name},pfunction,{index})',
    ]
    for tag, forged in [('tag', 'PINT 1'), ('value', f'PBOOL {"true" if boolean == "false" else "false"}')]:
        checks += [
            f'S_bare_{tag}_{name} = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_{name}_bare ({forged}))] ++ ppool.CONSTANTS)]]]',
            f'~$lossy_optional_integer_phase_safe(S_bare_{tag}_{name},pfunction.ENV,porigin_{name}_bare)',
            f'$lossy_optional_integer_deferred_value_at(S_bare_{tag}_{name},pfunction.ENV,porigin_{name}_bare) = eps',
            f'$lossy_optional_integer_deferred_value_at(S_bare_{tag}_{name},pfunction.ENV,porigin_{name}) = eps',
        ]
checks += [
    '$pfcast_nan(PFLOAT n_nan)',
    'n_boolZero =/= n_nanSpace',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base285"),$ptascii("E_ERROR")),($ptascii("One285"),$ptascii("E_ERROR")),($ptascii("Nan285"),$ptascii("NAN"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_boolZero)',
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
    '$lookup(S_done.ENV,$ptascii("x285")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]
CASES = {'deferred-boolean-literal-wrapper-private-certificates': {
    'source': ROWS['deferred-boolean-literal-wrapper-alias-named-reentry']['source'],
    'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin '
              '-- if pcallcontext.ARGC = 1 -- if $function_at(S.FUNCTIONS,porigin) = (pfunction) '
              '-- if pfunction.ENV.NAMESPACE = $ptascii("BooleanLiteral285") '
              '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 '
              '-- if S.TODO = $function_tasks(S,pfunction)'),
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
