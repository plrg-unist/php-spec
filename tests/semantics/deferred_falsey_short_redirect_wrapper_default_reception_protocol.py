#!/usr/bin/env python3
"""Folded falsey predicates preserve exact pool types, result tags and private cells."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_falsey_short_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
raw = base + ['|pfunction.SIGNATURE.PARAMETERS| = 8',
              'S.CODE = [pcode]', 'S.POOLS = [ppool]', '$default_cache_owner(S) = (CACHE_SHARED)']
values = ['PINT 0', 'PBOOL true', 'PFLOAT 0', 'PFLOAT 9223372036854775808',
          'PFLOAT n_nan', 'PNULL', 'PBOOL true', 'PINT 1']
condition_values = ['PBOOL false', 'PINT 0', 'PNULL', 'PFLOAT 0',
                    'PFLOAT 9223372036854775808', 'PNULL', 'PFLOAT 0', 'PFLOAT 9223372036854775808']
for index, (condition_value, value) in enumerate(zip(condition_values, values)):
    raw += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (NExprTernary expression_left_{index} ABSENT expression_right_{index} metadata_{index})',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index}) = ((z_{index},false))',
        rf'$pool_value(S.POOLS,pdefault_{index}.ORIGIN) = eps /\ $compiled_read(S,pdefault_{index}.ORIGIN) = eps',
        f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_{index}) = 1',
        f'$compiled_redirect(S,pdefault_{index}.ORIGIN) = ((PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2]),expression_right_{index},false,z_{index}))',
        f'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = ({condition_value})',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index} ++ [PCFIELD 0]) = eps',
        f'$compiled_read(S,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = eps',
        f'$lossy_optional_integer_phase_safe(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0]))',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = ({condition_value})',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2])) = ({value})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
        f'S.STORE[n_cell_{index}] = DEFINED ({value})',
        rf'~(n_cell_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_cell_{index}) = 1',
    ]
raw += ['$pfcast_nan(PFLOAT n_nan)', '$default_caches_valid(S,S.DEFAULTCACHE)',
    'S_bool_no_redirect = S[.CODE = [pcode[.REDIRECTS = eps]]]',
    '$lossy_optional_integer_deferred_value_at(S_bool_no_redirect,pfunction.ENV,pdefault_0.ORIGIN) = (PINT 0)',
    '$lossy_optional_integer_deferred(S_bool_no_redirect,pfunction,0)',
    'S_wrong_cond_bits = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_4 ++ [PCFIELD 0]) (PFLOAT 0))] ++ ppool.CONSTANTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_wrong_cond_bits,pfunction.ENV,PORIGIN n_unit (pcpath_4 ++ [PCFIELD 0])) = (PFLOAT 9223372036854775808)',
    '$pool_value(S_wrong_cond_bits.POOLS,PORIGIN n_unit (pcpath_4 ++ [PCFIELD 0])) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred_value_at(S_wrong_cond_bits,pfunction.ENV,pdefault_4.ORIGIN) = eps',
    '~$lossy_optional_integer_deferred(S_wrong_cond_bits,pfunction,4)']

certificate = base + [
    'pfunction.ENV.NAMESPACE = $ptascii("FalseyRedirect297")',
    'S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
    '$default_at(pfunction.DEFAULTS,1) = (pdefault)',
    'pdefault.ORIGIN = PORIGIN n_unit pcpath_default',
    'pcpath_short = pcpath_default ++ [PCFIELD 0]',
    'pcpath_left = pcpath_short ++ [PCFIELD 0]',
    'pcpath_right = pcpath_short ++ [PCFIELD 2]',
    'porigin_short = PORIGIN n_unit pcpath_short',
    '$origin_node(S.SOURCES,porigin_short) = (NExprTernary expression_left ABSENT expression_right metadata)',
    '$origin_node(S.SOURCES,PORIGIN n_unit pcpath_left) = (expression_left)',
    '$origin_node(S.SOURCES,PORIGIN n_unit pcpath_right) = (expression_right)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit pcpath_left) = (PINT 0)',
    '$pool_value(S.POOLS,PORIGIN n_unit pcpath_left) = (PINT 0)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_left) = eps',
    '$compiled_read(S,PORIGIN n_unit pcpath_left) = eps',
    '$lossy_optional_integer_phase_safe(S,pfunction.ENV,PORIGIN n_unit pcpath_left)',
    '$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_left) = 0',
    '$code_expression(pcode.EXPRESSIONS,pcpath_short) = ((z,false))',
    r'$pool_value(S.POOLS,porigin_short) = eps /\ $compiled_read(S,porigin_short) = eps',
    '$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_short) = 1',
    '$compiled_redirect(S,porigin_short) = ((PORIGIN n_unit pcpath_right,expression_right,false,z))',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_short)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit pcpath_right) = (PBOOL false)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_short) = (PBOOL false)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault.ORIGIN) = (PINT 0)',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault.ORIGIN)',
    '$lossy_optional_integer_deferred(S,pfunction,1)',
    '$default_current_cache(S,pdefault.ORIGIN) = eps',
    'S_no_redirect = S[.CODE = [pcode[.REDIRECTS = eps]]]',
    '$lossy_optional_integer_deferred_value_at(S_no_redirect,pfunction.ENV,porigin_short) = eps',
    '~$lossy_optional_integer_deferred(S_no_redirect,pfunction,1)',
]
mutations = {
    'duplicate': 'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ [(CODEREDIRECT pcpath_short pcpath_right false)])]]]',
    'copy': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_short pcpath_right true)]]]]',
    'target': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_short (pcpath_right ++ [PCFIELD 0]) false)]]]]',
    'owncode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_short z true)] ++ pcode.EXPRESSIONS)]]]',
    'ownpool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_short (PBOOL false))] ++ ppool.CONSTANTS)]]]',
    'leftcode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_left z true)] ++ pcode.EXPRESSIONS)]]]',
    'leftpool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_left (PBOOL false))] ++ ppool.CONSTANTS)]]]',
}
for label, expression in mutations.items():
    certificate += [f'S_{label} = {expression}',
        f'$lossy_optional_integer_deferred_value_at(S_{label},pfunction.ENV,porigin_short) = eps',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,1)']
certificate += [
    'S_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_right (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
    '~$lossy_optional_integer_deferred_bindings(S_source,pfunction.ENV,pdefault.ORIGIN)',
    '~$lossy_optional_integer_deferred(S_source,pfunction,1)',
]
recipient = base + ['pfunction.ENV.NAMESPACE = $ptascii("FalseyRedirect297")',
                    '$default_cache_owner(S) = (CACHE_SHARED)']
for index, value in [(1,0), (2,1), (3,0), (4,0)]:
    recipient += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED (PINT {value})',
        rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
recipient += [
    'pdefault_4.ORIGIN = PORIGIN n_unit pcpath_negative',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_negative ++ [PCFIELD 0])) = (PFLOAT 9223372036854775808)',
    r'n_private_1 =/= n_private_2 /\ n_private_1 =/= n_private_3 /\ n_private_2 =/= n_private_3 /\ n_private_1 =/= n_private_4 /\ n_private_2 =/= n_private_4 /\ n_private_3 =/= n_private_4',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_1[.VALUE = PBOOL false])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
]
for index in (1,2,3,4):
    recipient += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
recipient += ['$lookup(S_done.ENV,$ptascii("x297")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
named_context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
    '-- if pfunction.ENV.NAMESPACE = $ptascii("FalseyRedirect297") '
    '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 ')
named_source = ROWS['deferred-falsey-short-redirect-wrapper-alias-named-reentry']['source']
CASES = {
    'deferred-falsey-short-redirect-raw-tags': {
        'source': ROWS['deferred-falsey-short-redirect-wrapper-raw-tagged-results']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 '
            '-- if pcallcontext.FUNCTION = porigin_function -- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)'), 'checks': raw},
    'deferred-falsey-short-redirect-certificate': {'source': named_source,
        'stage': named_context + '-- if pcallcontext.ARGC = 6 -- if S.TODO = [NAMED_PREFLIGHT porigin_function 0]', 'checks': certificate},
    'deferred-falsey-short-redirect-private-recipients': {'source': named_source,
        'stage': named_context + '-- if pcallcontext.ARGC = 1 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': recipient},
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
