#!/usr/bin/env python3
"""A folded false ternary authenticates only its actual condition and child."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('folded_boolean_ternary_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.NAME = $ptascii("foldedDefaults228")',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps /\ pcallcontext.CACHE = eps',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_later]',
    r'psparam_first.REQUIRED /\ psparam_first.BYREF /\ psparam_later.BYREF',
    'psparam_later.DEFAULT = PSDEFAULT expression_default "deferred"',
    '$default_parameter_origin(S,porigin,1) = PORIGIN n_unit pcpath_parameter',
    'pcpath_default = pcpath_parameter ++ [PCFIELD 6]',
    'porigin_default = PORIGIN n_unit pcpath_default',
    '$default_at(pfunction.DEFAULTS,1) = ({INDEX 1,ORIGIN porigin_default,KIND PDDEFERRED})',
    '$origin_node(S.SOURCES,porigin_default) = (expression_default)',
    'expression_default = NExprTernary expression_cond expression_skipped expression_selected metadata_default',
    'porigin_cond = PORIGIN n_unit (pcpath_default ++ [PCFIELD 0])',
    'porigin_skipped = PORIGIN n_unit (pcpath_default ++ [PCFIELD 1])',
    'porigin_selected = PORIGIN n_unit (pcpath_default ++ [PCFIELD 2])',
    '$origin_node(S.SOURCES,porigin_cond) = (expression_cond)',
    '$origin_node(S.SOURCES,porigin_skipped) = (expression_skipped)',
    '$origin_node(S.SOURCES,porigin_selected) = (expression_selected)',
    '$lossy_optional_integer_special(pfunction.ENV,expression_cond) = (PBOOL false)',
    '$pool_value(S.POOLS,porigin_cond) = (PBOOL false)',
    r'$pool_value(S.POOLS,porigin_default) = eps /\ $compiled_read(S,porigin_default) = eps',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_default) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_default) = (NINT 9223372036854775807)',
    '$lossy_optional_integer_deferred_value(pfunction.ENV,expression_default) = (PINT 9223372036854775807)',
    '$lossy_optional_integer_quiet_shape(expression_default)',
    'S.CODE = [pcode]',
    'pcoderedirect_good = CODEREDIRECT pcpath_default (pcpath_default ++ [PCFIELD 2]) false',
    '$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_default) = 1',
    '$code_redirect(pcode.REDIRECTS,pcpath_default) = ((pcpath_default ++ [PCFIELD 2],false))',
    '$compiled_redirect(S,porigin_default) = ((porigin_selected,expression_selected,false,z_root))',
    '$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_default) = ((porigin_cond,porigin_selected))',
    '$call_name_count(pcode.NAMES,pcpath_default ++ [PCFIELD 1]) = 0',
    '$call_name_count(pcode.NAMES,pcpath_default ++ [PCFIELD 2]) = 1',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_cond)',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_selected)',
    '~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_skipped)',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_default)',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$default_current_cache(S,porigin_default) = eps',
    '$lossy_optional_integer_deferred(S,pfunction,1)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'S.RESULT = KNOWN (PINT 9223372036854775807)',
    '$lookup(S.ENV,psparam_later.NAME) = eps',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    r'S.STORE[n_first] = DEFINED (PINT 1) /\ n_first <- S.REFCELLS',
    '$heap_owners($heap_graph(S),HCELL n_first) = 2',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
]

for label, redirects in [
    ('missing', 'eps'),
    ('wrong_target', '[CODEREDIRECT pcpath_default (pcpath_default ++ [PCFIELD 1]) false]'),
    ('wrong_flag', '[CODEREDIRECT pcpath_default (pcpath_default ++ [PCFIELD 2]) true]'),
    ('duplicate', 'pcode.REDIRECTS ++ [pcoderedirect_good]'),
]:
    checks.extend([
        f'S_{label} = S[.CODE = ([pcode[.REDIRECTS = ({redirects})]])]',
        f'$lossy_optional_integer_pruned_ternary(S_{label},pfunction.ENV,porigin_default) = eps',
        f'~$lossy_optional_integer_deferred_bindings(S_{label},pfunction.ENV,porigin_default)',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,1)',
    ])

checks.extend([
    'S_wrong_pool = S[.POOLS = [{UNIT n_unit,CONSTANTS ([(PCONSTANT (pcpath_default ++ [PCFIELD 0]) (PBOOL true))])}]]',
    '$lossy_optional_integer_pruned_ternary(S_wrong_pool,pfunction.ENV,porigin_default) = eps',
    '~$lossy_optional_integer_deferred_bindings(S_wrong_pool,pfunction.ENV,porigin_default)',
    'S_no_pool = S[.POOLS = eps]',
    '$lossy_optional_integer_pruned_ternary(S_no_pool,pfunction.ENV,porigin_default) = eps',
    '~$lossy_optional_integer_deferred_bindings(S_no_pool,pfunction.ENV,porigin_default)',
    'S_no_selected_name = S[.CODE = ([pcode[.NAMES = eps]])]',
    '$lossy_optional_integer_pruned_ternary(S_no_selected_name,pfunction.ENV,porigin_default) = ((porigin_cond,porigin_selected))',
    '~$lossy_optional_integer_deferred_bindings(S_no_selected_name,pfunction.ENV,porigin_default)',
    'S_no_line = S[.CODE = ([pcode[.EXPRESSIONS = eps]])]',
    '$lossy_optional_integer_pruned_ternary(S_no_line,pfunction.ENV,porigin_default) = eps',
    '~$lossy_optional_integer_deferred_bindings(S_no_line,pfunction.ENV,porigin_default)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("PHP_INT_MAX"),$ptascii("PHP_INT_MIN"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_selected)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_default)',
    'pdefaultcache_good = {ORIGIN porigin_default,VALUE PINT 9223372036854775807,CLASS PVSCALAR}',
    'S_wrong_cache = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.VALUE = PINT 1])]',
    '~$lossy_optional_integer_deferred(S_wrong_cache,pfunction,1)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_bound',
    'S_bound.TODO = $call_receive_body(S,pfunction)',
    '$lookup(S_bound.ENV,psparam_later.NAME) = (n_later)',
    'S_bound.STORE[n_later] = DEFINED (PINT 9223372036854775807)',
    r'~(n_later <- S_bound.REFCELLS) /\ $heap_owners($heap_graph(S_bound),HCELL n_later) = 1',
    '$default_current_cache(S_bound,porigin_default) = (pdefaultcache_good)',
    'S_bound.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_bound,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_default) = (pdefaultcache_good)',
    r'~((HCELL n_later) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_later) = 0',
    '$lookup(S_done.ENV,$ptascii("xFolded228")) = (n_first)',
    'S_done.STORE[n_first] = DEFINED (PINT 2)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

CASES = {
    'folded-boolean-ternary-cold-bind': {
        'source': ROWS['folded-boolean-ternary-default-cold-warm']['source'],
        'stage': 'S.TODO = [DEFAULT_BIND porigin 1]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
