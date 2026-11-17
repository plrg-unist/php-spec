#!/usr/bin/env python3
"""Actual NULL BOOL casts and NOT retain private reception authority."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_null_truth_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

PARAMETERS = [
    ('castNull', 1, 'NExprCastBool', 'PBOOL false', '0'),
    ('notNull', 2, 'NExprBooleanNot', 'PBOOL true', '1'),
]
base = [
    'S.CURRENT = (pcallcontext)',
    'pcallcontext.FUNCTION = porigin',
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("NullTruth292")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base292"),$ptascii("E_WARNING")),($ptascii("One292"),$ptascii("E_ERROR"))]',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps',
    r'pcallcontext.CACHE = eps /\ pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'S.CODE = [pcode]',
    'S.SOURCES = [pcunit]',
    'S.POOLS = [ppool]',
]
groups = {}
for name, index, constructor, raw, value in PARAMETERS:
    checks = list(base)
    checks += [
        f'psparam_{name} = pfunction.SIGNATURE.PARAMETERS[{index}]',
        f'psparam_{name}.BYREF',
        f'psparam_{name}.DEFAULT = PSDEFAULT expression_{name} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{name}_parameter',
        f'pcpath_{name} = pcpath_{name}_parameter ++ [PCFIELD 6]',
        f'porigin_{name} = PORIGIN n_unit pcpath_{name}',
        f'pcpath_{name}_op = pcpath_{name} ++ [PCFIELD 0]',
        f'porigin_{name}_op = PORIGIN n_unit pcpath_{name}_op',
        f'pcpath_{name}_child = pcpath_{name}_op ++ [PCFIELD 0]',
        f'porigin_{name}_child = PORIGIN n_unit pcpath_{name}_child',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{name},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{name}) = (expression_{name})',
        f'expression_{name} = NExprCastInt expression_{name}_op metadata_{name}',
        f'$origin_node(S.SOURCES,porigin_{name}_op) = (expression_{name}_op)',
        f'expression_{name}_op = {constructor} expression_{name}_child metadata_{name}_op',
        f'$origin_node(S.SOURCES,porigin_{name}_child) = (expression_{name}_child)',
        f'expression_{name}_child = NExprTernary expression_{name}_cond expression_{name}_true expression_{name}_false metadata_{name}_child',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}) = ((z_{name},false))',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}_op) = ((z_{name}_op,false))',
        rf'$pool_value(S.POOLS,porigin_{name}_op) = eps /\ $compiled_read(S,porigin_{name}_op) = eps',
        f'$compiled_redirect(S,porigin_{name}_op) = eps',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_{name}_op)',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}_child) = ((z_{name}_child,false))',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}_child) = (PNULL)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}_op) = ({raw})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{name}) = (PINT {value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{name} = {{ORIGIN porigin_{name},VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,porigin_{name}) = (pdefaultcache_{name})',
        f'$lookup(S.ENV,psparam_{name}.NAME) = (n_{name})',
        f'S.STORE[n_{name}] = DEFINED (PINT {value})',
        rf'~(n_{name} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_{name}) = 1',
        f'S_own_code_{name} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_{name}_op z_{name}_op true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_own_code_{name},pfunction.ENV,porigin_{name}) = eps',
        f'S_child_code_{name} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_{name}_child z_{name}_child true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_child_code_{name},pfunction.ENV,porigin_{name}) = eps',
        f'S_child_source_{name} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_{name}_child (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
        f'~$lossy_optional_integer_deferred(S_child_source_{name},pfunction,{index})',
        f'S_tag_{name} = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{name}[.VALUE = {raw}])]',
        f'$default_caches_valid(S_tag_{name},S_tag_{name}.DEFAULTCACHE)',
        f'~$lossy_optional_integer_deferred(S_tag_{name},pfunction,{index})',
    ]
    for tag, forged in [('false', 'PBOOL false'), ('zero', 'PINT 0')]:
        checks += [
            f'S_child_{tag}_{name} = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_{name}_child ({forged}))] ++ ppool.CONSTANTS)]]]',
            f'$lossy_optional_integer_deferred_value_at(S_child_{tag}_{name},pfunction.ENV,porigin_{name}_child) = eps',
            f'$lossy_optional_integer_deferred_value_at(S_child_{tag}_{name},pfunction.ENV,porigin_{name}) = eps',
        ]
    groups[name] = checks
groups['castNull'] += [
    '$plstyle(metadata_castNull_op) = 1',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base292"),$ptascii("E_ERROR")),($ptascii("One292"),$ptascii("E_ERROR"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_castNull)',
]
checks = groups['notNull']
checks += [
    '$default_at(pfunction.DEFAULTS,1) = (pdefault_castNull)',
    'porigin_castNull = pdefault_castNull.ORIGIN',
    'pdefaultcache_castNull = {ORIGIN porigin_castNull,VALUE PINT 0,CLASS PVSCALAR}',
    '$default_current_cache(S,porigin_castNull) = (pdefaultcache_castNull)',
    '$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[1].NAME) = (n_castNull)',
    'S.STORE[n_castNull] = DEFINED (PINT 0)',
    'n_castNull =/= n_notNull',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
]
for name, _, _, _, value in PARAMETERS:
    checks += [
        f'$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,porigin_{name}) = (PINT {value})',
        f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{name}) = (pdefaultcache_{name})',
        rf'~((HCELL n_{name}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_{name}) = 0',
    ]
checks += [
    '$lookup(S_done.ENV,$ptascii("x292")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]
stage = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin '
         '-- if $function_at(S.FUNCTIONS,porigin) = (pfunction) '
         '-- if pfunction.ENV.NAMESPACE = $ptascii("NullTruth292") '
         '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 '
         '-- if S.TODO = $function_tasks(S,pfunction)')
CASES = {
    'deferred-null-truth-wrapper-' + name: {
        'source': ROWS['deferred-null-truth-wrapper-alias-named-reentry']['source'],
        'stage': stage,
        'checks': group,
    }
    for name, group in groups.items()
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
