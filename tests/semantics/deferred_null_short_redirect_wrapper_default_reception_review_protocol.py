#!/usr/bin/env python3
"""Independent folded-false NULL redirect authority and recipient lifetime."""
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
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
certificate = base + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
    '$default_at(pfunction.DEFAULTS,3) = (pdefault)',
    'pdefault.ORIGIN = PORIGIN n_unit pcpath_default',
    'pcpath_short = pcpath_default ++ [PCFIELD 0,PCFIELD 0]',
    'pcpath_cond = pcpath_short ++ [PCFIELD 0]',
    'pcpath_selected = pcpath_short ++ [PCFIELD 2]',
    'porigin_short = PORIGIN n_unit pcpath_short',
    'porigin_selected = PORIGIN n_unit pcpath_selected',
    '$origin_node(S.SOURCES,porigin_short) = (NExprTernary expression_cond ABSENT expression_selected metadata)',
    '$origin_node(S.SOURCES,PORIGIN n_unit pcpath_cond) = (expression_cond)',
    '$origin_node(S.SOURCES,porigin_selected) = (expression_selected)',
    '$lossy_optional_integer_special(pfunction.ENV,expression_cond) = (PBOOL false)',
    '$pool_value(S.POOLS,PORIGIN n_unit pcpath_cond) = (PBOOL false)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_cond) = eps',
    '$compiled_read(S,PORIGIN n_unit pcpath_cond) = eps',
    '$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_cond) = 0',
    '$code_expression(pcode.EXPRESSIONS,pcpath_short) = ((z,false))',
    '$pool_value(S.POOLS,porigin_short) = eps', '$compiled_read(S,porigin_short) = eps',
    'pcode.REDIRECTS = [(CODEREDIRECT pcpath_short pcpath_selected false)]',
    '$compiled_redirect(S,porigin_short) = ((porigin_selected,expression_selected,false,z))',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_short)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_selected) = (PNULL)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_short) = (PNULL)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_default ++ [PCFIELD 0])) = (PBOOL false)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault.ORIGIN) = (PINT 0)',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault.ORIGIN)',
    '$lossy_optional_integer_deferred(S,pfunction,3)',
    '$default_current_cache(S,pdefault.ORIGIN) = eps']
mutations = {
    'duplicate': 'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
    'copyflag': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_short pcpath_selected true)]]]]',
    'owncode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_short z true)] ++ pcode.EXPRESSIONS)]]]',
    'ownpool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_short PNULL)] ++ ppool.CONSTANTS)]]]',
    'condpool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_cond (PBOOL true))] ++ ppool.CONSTANTS)]]]',
    'condcode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_cond z true)] ++ pcode.EXPRESSIONS)]]]',
    'condredirect': 'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath_cond pcpath_selected false)] ++ pcode.REDIRECTS)]]]',
    'target': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_short (pcpath_selected ++ [PCFIELD 0]) false)]]]]',
}
certificate += ['~$lossy_optional_integer_phase_safe(S,pfunction.ENV,PORIGIN n_unit (pcpath_selected ++ [PCFIELD 0]))']
for name, expression in mutations.items():
    certificate += [f'S_{name} = {expression}',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,porigin_short) = eps',
        f'~$lossy_optional_integer_deferred(S_{name},pfunction,3)']
certificate += ['S_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_selected (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
    '~$lossy_optional_integer_deferred_bindings(S_source,pfunction.ENV,pdefault.ORIGIN)',
    '~$lossy_optional_integer_deferred(S_source,pfunction,3)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base292"),$ptascii("E_ERROR")),($ptascii("One292"),$ptascii("E_ERROR"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault.ORIGIN)']
recipient = base + ['$default_at(pfunction.DEFAULTS,3) = (pdefault)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault.ORIGIN) = (PINT 0)',
    '$lossy_optional_integer_deferred(S,pfunction,3)', '$default_cache_owner(S) = (CACHE_SHARED)',
    'pdefaultcache = {ORIGIN pdefault.ORIGIN,VALUE PINT 0,CLASS PVSCALAR}',
    '$default_current_cache(S,pdefault.ORIGIN) = (pdefaultcache)',
    '$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[3].NAME) = (n_private)',
    'S.STORE[n_private] = DEFINED (PINT 0)',
    r'~(n_private <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private) = 1',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache[.VALUE = PBOOL false])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,3)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
    r'~((HCELL n_private) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private) = 0',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
false = f'((bool)({chain}))'
truth = f'(!{false})'
selected = f'({truth} ? NULL : false)'
expressions = [f'false ?: {truth}', f'0 ?: {selected}', f'NULL ?? {selected}', 'false ?: NULL']
boundary = base + ['|pfunction.SIGNATURE.PARAMETERS| = 4']
for index in range(4):
    boundary += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ' + ('(PNULL)' if index in (2,3) else 'eps'),
        ('' if index == 2 else '~') + f'$lossy_optional_integer_deferred(S,pfunction,{index})']
context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
           '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
           '-- if pfunction.ENV.NAMESPACE = $ptascii("NullTruth292") '
           '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 ')
CASES = {
    'deferred-null-short-redirect-independent-certificate': {'source': SOURCE,
        'stage': context + '-- if pcallcontext.ARGC = 6 -- if S.TODO = [NAMED_PREFLIGHT porigin_function 0]', 'checks': certificate},
    'deferred-null-short-redirect-independent-recipient': {'source': SOURCE,
        'stage': context + '-- if pcallcontext.ARGC = 1 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': recipient},
    'deferred-null-short-redirect-independent-current-boundaries': {
        'source': '<?php function refused294(' + ', '.join(f'$p{i}=({expression})' for i, expression in enumerate(expressions)) + ') {} refused294();',
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)'), 'checks': boundary},
}
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
