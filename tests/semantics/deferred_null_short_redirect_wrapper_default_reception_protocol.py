#!/usr/bin/env python3
"""Actual folded-false NULL redirects retain private default reception."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_null_short_redirect_wrapper_default_reception_cases.json')
ROWS = json.loads(CATALOGUE.read_text())
assert len(ROWS) == 1
SOURCE = ROWS[0]['source']
assert hashlib.sha256(SOURCE.encode()).hexdigest() == ROWS[0]['source_sha256'] == '366d7634930bf78db6bb0c575b03eb94d7ffe92343a38838b16836c2fe2739dc'

base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
        'pfunction.ENV.NAMESPACE = $ptascii("NullTruth292")',
        '$default_cache_owner(S) = (CACHE_SHARED)',
        '$default_at(pfunction.DEFAULTS,3) = (pdefault)',
        'pdefault.ORIGIN = PORIGIN n_unit pcpath_default']
certificate = base + [
    'pfunction.SIGNATURE.PARAMETERS[3].BYREF',
    'pfunction.SIGNATURE.PARAMETERS[3].DEFAULT = PSDEFAULT expression_default "deferred"',
    '$origin_node(S.SOURCES,pdefault.ORIGIN) = (expression_default)',
    'S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
    'pcpath_bool = pcpath_default ++ [PCFIELD 0]',
    'pcpath_short = pcpath_bool ++ [PCFIELD 0]',
    'pcpath_cond = pcpath_short ++ [PCFIELD 0]',
    'pcpath_fallback = pcpath_short ++ [PCFIELD 2]',
    'porigin_short = PORIGIN n_unit pcpath_short',
    'porigin_fallback = PORIGIN n_unit pcpath_fallback',
    '$origin_node(S.SOURCES,porigin_short) = (NExprTernary expression_cond ABSENT expression_fallback metadata)',
    '$origin_node(S.SOURCES,PORIGIN n_unit pcpath_cond) = (expression_cond)',
    '$origin_node(S.SOURCES,porigin_fallback) = (expression_fallback)',
    '$lossy_optional_integer_special(pfunction.ENV,expression_cond) = (PBOOL false)',
    '$pool_value(S.POOLS,PORIGIN n_unit pcpath_cond) = (PBOOL false)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_cond) = eps',
    '$compiled_read(S,PORIGIN n_unit pcpath_cond) = eps',
    '$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_cond) = 0',
    '$code_expression(pcode.EXPRESSIONS,pcpath_short) = ((z,false))',
    '$pool_value(S.POOLS,porigin_short) = eps',
    '$compiled_read(S,porigin_short) = eps',
    '$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_short) = 1',
    '$compiled_redirect(S,porigin_short) = ((porigin_fallback,expression_fallback,false,z))',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_short)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_fallback) = (PNULL)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_short) = (PNULL)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit pcpath_bool) = (PBOOL false)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault.ORIGIN) = (PINT 0)',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault.ORIGIN)',
    '$lossy_optional_integer_deferred(S,pfunction,3)',
    '$default_current_cache(S,pdefault.ORIGIN) = eps',
    'S_no_redirect = S[.CODE = [pcode[.REDIRECTS = eps]]]',
    '$lossy_optional_integer_deferred_value_at(S_no_redirect,pfunction.ENV,porigin_short) = (PNULL)',
    '$lossy_optional_integer_deferred(S_no_redirect,pfunction,3)',
]
for label, redirects in [
        ('duplicate', '(pcode.REDIRECTS ++ pcode.REDIRECTS)'),
        ('copy', '[(CODEREDIRECT pcpath_short pcpath_fallback true)]'),
        ('target', '[(CODEREDIRECT pcpath_short (pcpath_fallback ++ [PCFIELD 0]) false)]')]:
    certificate += [
        f'S_{label} = S[.CODE = [pcode[.REDIRECTS = {redirects}]]]',
        f'$lossy_optional_integer_deferred_value_at(S_{label},pfunction.ENV,porigin_short) = eps',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,3)',
    ]
for label, value in [('bool', 'PBOOL false'), ('int', 'PINT 0')]:
    certificate += [
        f'S_fallback_{label} = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_fallback ({value}))] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_fallback_{label},pfunction.ENV,porigin_short) = eps',
        f'~$lossy_optional_integer_deferred(S_fallback_{label},pfunction,3)',
    ]
certificate += [
    'S_cond_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_cond (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
    '~$lossy_optional_integer_deferred_bindings(S_cond_source,pfunction.ENV,pdefault.ORIGIN)',
    '~$lossy_optional_integer_deferred(S_cond_source,pfunction,3)',
]
recipient = base + [
    r'pcallcontext.HOLES = eps /\ pcallcontext.CACHE = eps /\ pcallcontext.DEFAULTRECEIVE = eps',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault.ORIGIN) = (PINT 0)',
    '$lossy_optional_integer_deferred(S,pfunction,3)',
    'pdefaultcache = {ORIGIN pdefault.ORIGIN,VALUE PINT 0,CLASS PVSCALAR}',
    '$default_current_cache(S,pdefault.ORIGIN) = (pdefaultcache)',
    '$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[3].NAME) = (n_private)',
    'S.STORE[n_private] = DEFINED (PINT 0)',
    r'~(n_private <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private) = 1',
    '$default_at(pfunction.DEFAULTS,4) = (pdefault_selected)',
    'pdefaultcache_selected = {ORIGIN pdefault_selected.ORIGIN,VALUE PINT 1,CLASS PVSCALAR}',
    '$default_current_cache(S,pdefault_selected.ORIGIN) = (pdefaultcache_selected)',
    '$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[4].NAME) = (n_selected)',
    'S.STORE[n_selected] = DEFINED (PINT 1)',
    r'n_selected =/= n_private /\ ~(n_selected <- S.REFCELLS)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache[.VALUE = PBOOL false])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,3)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_selected.ORIGIN) = (pdefaultcache_selected)',
    r'~((HCELL n_private) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private) = 0',
    r'~((HCELL n_selected) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_selected) = 0',
    '$lookup(S_done.ENV,$ptascii("x292")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]
context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
           '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
           '-- if pfunction.ENV.NAMESPACE = $ptascii("NullTruth292") '
           '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 ')
CASES = {
    'deferred-null-short-redirect-certificate': {
        'source': SOURCE, 'stage': context + '-- if pcallcontext.ARGC = 6 -- if S.TODO = [NAMED_PREFLIGHT porigin_function 0]',
        'checks': certificate},
    'deferred-null-short-redirect-private-recipient': {
        'source': SOURCE, 'stage': context + '-- if pcallcontext.ARGC = 1 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks': recipient},
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
