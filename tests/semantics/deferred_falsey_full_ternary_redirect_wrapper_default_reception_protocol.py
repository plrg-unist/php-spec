#!/usr/bin/env python3
"""Full falsey redirects skip unresolved bindings and retain scalar reception."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_falsey_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
raw = base + ['|pfunction.SIGNATURE.PARAMETERS| = 8',
              'S.CODE = [pcode]', 'S.POOLS = [ppool]', '$default_cache_owner(S) = (CACHE_SHARED)']
values = ['PINT 0', 'PBOOL true', 'PFLOAT 0', 'PFLOAT 9223372036854775808',
          'PFLOAT n_nan', 'PNULL', 'PBOOL true', 'PINT 1']
condition_values = ['PBOOL false', 'PNULL', 'PINT 0', 'PFLOAT 0',
                    'PFLOAT 9223372036854775808', 'PSTRING eps', 'PSTRING ([48])', 'PSTRING ([48])']
for index, (condition_value, value) in enumerate(zip(condition_values, values)):
    raw += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (NExprTernary expression_left_{index} expression_skipped_{index} expression_right_{index} metadata_{index})',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index}) = ((z_{index},false))',
        rf'$pool_value(S.POOLS,pdefault_{index}.ORIGIN) = eps /\ $compiled_read(S,pdefault_{index}.ORIGIN) = eps',
        f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_{index}) = 1',
        f'$compiled_redirect(S,pdefault_{index}.ORIGIN) = ((PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2]),expression_right_{index},false,z_{index}))',
        f'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = ({condition_value})',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index} ++ [PCFIELD 0]) = eps',
        f'$compiled_read(S,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = eps',
        f'$lossy_optional_integer_phase_safe(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0]))',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = ' + (f'({condition_value})' if index < 5 else 'eps'),
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
raw += ['$pfcast_nan(PFLOAT n_nan)', '$default_caches_valid(S,S.DEFAULTCACHE)']
for index in range(8):
    raw += [f'expression_skipped_{index} = NExprConstFetch name_skipped_{index} metadata_skipped_{index}',
        f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])) = (expression_skipped_{index})',
        f'$code_name(pcode.NAMES,pcpath_{index} ++ [PCFIELD 1]) = eps',
        f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1]))',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_falsey_full_redirect(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ((PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0]), PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2])))',
        f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ((PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0]), PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2])))']
    if index >= 5:
        raw += [f'$compiled_string_value(S,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0]),{condition_values[index]}) = PSTRING_CARRIER INTERNED_STRING ' + ('eps' if index == 5 else '([48])')]
raw += ['S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in range(8):
    raw += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_cell_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_cell_{index}) = 0']

certificate = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
          '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
          'S.CODE = [pcode]', 'n_unit = pcode.UNIT', 'S.POOLS = [ppool]',
          'pcallcontext.HOLES = [1,2,3,4]', '$default_cache_owner(S) = (CACHE_SHARED)']
for index, condition, result in [(1,'PINT 0','PBOOL false'), (2,'PNULL','PINT 1'),
        (3,'PFLOAT 9223372036854775808','PFLOAT 9223372036854775808'), (4,'PSTRING eps','PNULL')]:
    certificate += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_default_{index}',
        f'pcpath_full_{index} = pcpath_default_{index} ++ [PCFIELD 0]',
        f'porigin_full_{index} = PORIGIN n_unit pcpath_full_{index}',
        f'$origin_node(S.SOURCES,porigin_full_{index}) = (NExprTernary expression_cond_{index} expression_skipped_{index} expression_selected_{index} metadata_{index})',
        f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = (expression_cond_{index})',
        f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])) = (expression_skipped_{index})',
        f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])) = (expression_selected_{index})',
        f'expression_skipped_{index} = NExprConstFetch name_skipped_{index} metadata_skipped_{index}',
        f'$lossy_optional_integer_quiet_shape(NExprTernary expression_cond_{index} expression_skipped_{index} expression_selected_{index} metadata_{index})',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_full_{index}) = ((z_{index},false))',
        rf'$pool_value(S.POOLS,porigin_full_{index}) = eps /\ $compiled_read(S,porigin_full_{index}) = eps',
        f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_full_{index}) = 1',
        f'$compiled_redirect(S,porigin_full_{index}) = ((PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2]),expression_selected_{index},false,z_{index}))',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_full_{index} ++ [PCFIELD 0]) = eps',
        f'$compiled_read(S,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = eps',
        f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_full_{index} ++ [PCFIELD 0]) = 0',
        f'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = ({condition})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = ' + ('eps' if index == 4 else f'({condition})'),
        f'$code_expression(pcode.EXPRESSIONS,pcpath_full_{index} ++ [PCFIELD 1]) = eps',
        rf'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])) = eps /\ $compiled_read(S,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])) = eps',
        f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_full_{index} ++ [PCFIELD 1]) = 0',
        f'$code_name(pcode.NAMES,pcpath_full_{index} ++ [PCFIELD 1]) = eps',
        f'$call_name_count(pcode.NAMES,pcpath_full_{index} ++ [PCFIELD 1]) = 0',
        f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1]))',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2]))',
        f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_full_{index}) = ((PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0]), PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])))',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_full_{index})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_full_{index}) = ({result})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])) = ({result})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT ' + ('1' if index == 2 else '0') + ')',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = eps']
certificate += ['$compiled_precision(S,(PORIGIN n_unit (pcpath_full_4 ++ [PCFIELD 0]))) = (14)',
    '$compiled_string_value(S,PORIGIN n_unit (pcpath_full_4 ++ [PCFIELD 0]),PSTRING eps) = PSTRING_CARRIER INTERNED_STRING eps']
certificate += ['S.SOURCES = [pcunit]', 'pcpath_full = pcpath_full_1',
    'pcpath_cond = pcpath_full ++ [PCFIELD 0]', 'pcpath_skipped = pcpath_full ++ [PCFIELD 1]',
    'pcpath_selected = pcpath_full ++ [PCFIELD 2]', 'porigin_full = porigin_full_1']
mutations = {
    'no_redirect': 'S[.CODE = [pcode[.REDIRECTS = eps]]]',
    'duplicate': 'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ [(CODEREDIRECT pcpath_full pcpath_selected false)])]]]',
    'copy': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_full pcpath_selected true)]]]]',
    'target': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_full (pcpath_selected ++ [PCFIELD 0]) false)]]]]',
    'owncode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_full z_1 true)] ++ pcode.EXPRESSIONS)]]]',
    'ownpool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_full (PBOOL false))] ++ ppool.CONSTANTS)]]]',
    'condcode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_cond z_1 false)] ++ pcode.EXPRESSIONS)]]]',
    'condpool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_cond (PBOOL false))] ++ ppool.CONSTANTS)]]]',
    'condredirect': 'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath_cond pcpath_selected false)] ++ pcode.REDIRECTS)]]]',
}
for label, expression in mutations.items():
    certificate += [f'S_{label} = {expression}',
        f'$lossy_optional_integer_falsey_full_redirect(S_{label},pfunction.ENV,porigin_full) = eps',
        f'$lossy_optional_integer_deferred_value_at(S_{label},pfunction.ENV,porigin_full) = eps',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,1)']
for field, path in [(0,'pcpath_cond'), (1,'pcpath_skipped'), (2,'pcpath_selected')]:
    certificate += [f'S_source_{field} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE {path} (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
        f'$lossy_optional_integer_falsey_full_redirect(S_source_{field},pfunction.ENV,porigin_full) = eps',
        f'~$lossy_optional_integer_deferred_bindings(S_source_{field},pfunction.ENV,porigin_full)',
        f'~$lossy_optional_integer_deferred(S_source_{field},pfunction,1)']
certificate += ['S_no_names = S[.CODE = [pcode[.NAMES = eps]]]',
    '~$lossy_optional_integer_deferred_bindings(S_no_names,pfunction.ENV,porigin_full)',
    '~$lossy_optional_integer_deferred(S_no_names,pfunction,1)']


certificate += ['pdefault_4.ORIGIN = PORIGIN n_unit pcpath_nullcast',
    '$origin_node(S.SOURCES,pdefault_4.ORIGIN) = (NExprCastInt expression_nullcast metadata_nullcast)',
    '$plstyle(metadata_nullcast) = 1',
    '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_nullcast ++ [PCFIELD 0])) = (expression_nullcast)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_nullcast ++ [PCFIELD 0])) = (PNULL)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_4.ORIGIN) = (PINT 0)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_nullcast) = ((z_nullcast,false))']
nullcast_mutations = {
    'style': 'S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_nullcast (NExprCastInt expression_nullcast eps))] ++ pcunit.OCCURRENCES)]]]',
    'code': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_nullcast z_nullcast true)] ++ pcode.EXPRESSIONS)]]]',
    'pool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_nullcast (PINT 0))] ++ ppool.CONSTANTS)]]]',
    'redirect': 'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath_nullcast (pcpath_nullcast ++ [PCFIELD 0]) false)] ++ pcode.REDIRECTS)]]]',
    'source': 'S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_nullcast ++ [PCFIELD 0]) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
}
for label, expression in nullcast_mutations.items():
    certificate += [f'S_nullcast_{label} = {expression}',
        f'$lossy_optional_integer_deferred_value_at(S_nullcast_{label},pfunction.ENV,pdefault_4.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_nullcast_{label},pfunction,4)']

recipient = base + ['pfunction.ENV.NAMESPACE = $ptascii("FullRedirect299")',
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
    'pdefault_3.ORIGIN = PORIGIN n_unit pcpath_negative',
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
recipient += ['$lookup(S_done.ENV,$ptascii("x299")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
named_context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
    '-- if pfunction.ENV.NAMESPACE = $ptascii("FullRedirect299") '
    '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 ')
named_source = ROWS['deferred-falsey-full-ternary-redirect-wrapper-alias-named-reentry']['source']
CASES = {
    'falsey-full-ternary-raw-tags': {
        'source': ROWS['deferred-falsey-full-ternary-redirect-wrapper-raw-tagged-results']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 '
            '-- if pcallcontext.FUNCTION = porigin_function -- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)'), 'checks': raw},
    'falsey-full-ternary-binding-certificate': {'source': named_source,
        'stage': named_context + '-- if pcallcontext.ARGC = 6 -- if S.TODO = [NAMED_PREFLIGHT porigin_function 0]', 'checks': certificate},
    'falsey-full-ternary-private-recipients': {'source': named_source,
        'stage': named_context + '-- if pcallcontext.ARGC = 1 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': recipient},
}
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
