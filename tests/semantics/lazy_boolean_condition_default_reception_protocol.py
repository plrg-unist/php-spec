#!/usr/bin/env python3
"""Decisive logical conditions retain own/left pools and proper-left bindings."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('lazy_boolean_condition_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.NAME = $ptascii("lazyDefaults230")',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps /\ pcallcontext.CACHE = eps',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_later,psparam_maximum]',
    r'psparam_first.REQUIRED /\ psparam_first.BYREF /\ psparam_later.BYREF',
    'psparam_later.DEFAULT = PSDEFAULT expression_default "deferred"',
    '$default_parameter_origin(S,porigin,1) = PORIGIN n_unit pcpath_parameter',
    'pcpath_default = pcpath_parameter ++ [PCFIELD 6]',
    'porigin_default = PORIGIN n_unit pcpath_default',
    '$default_at(pfunction.DEFAULTS,1) = ({INDEX 1,ORIGIN porigin_default,KIND PDDEFERRED})',
    '$origin_node(S.SOURCES,porigin_default) = (expression_default)',
    'expression_default = NExprTernary expression_cond expression_selected expression_skipped metadata_default',
    'porigin_cond = PORIGIN n_unit (pcpath_default ++ [PCFIELD 0])',
    'porigin_skipped = PORIGIN n_unit (pcpath_default ++ [PCFIELD 2])',
    'porigin_selected = PORIGIN n_unit (pcpath_default ++ [PCFIELD 1])',
    '$origin_node(S.SOURCES,porigin_cond) = (expression_cond)',
    '$origin_node(S.SOURCES,porigin_skipped) = (expression_skipped)',
    '$origin_node(S.SOURCES,porigin_selected) = (expression_selected)',
    '$lossy_optional_integer_special(pfunction.ENV,expression_cond) = eps',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_cond) = (true)',
    '$pfshape(expression_cond) = PFSHORT true expression_cond_child expression_cond_right',
    'porigin_cond_child = PORIGIN n_unit (pcpath_default ++ [PCFIELD 0,PCFIELD 0])',
    '$origin_node(S.SOURCES,porigin_cond_child) = (expression_cond_child)',
    '$lossy_optional_integer_special(pfunction.ENV,expression_cond_child) = (PBOOL true)',
    '$pool_value(S.POOLS,porigin_cond_child) = (PBOOL true)',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_cond_child)',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_cond)',
    '$pool_value(S.POOLS,porigin_cond) = (PBOOL true)',
    r'$pool_value(S.POOLS,porigin_default) = eps /\ $compiled_read(S,porigin_default) = eps',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_default) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_default) = (NINT 8)',
    '$lossy_optional_integer_deferred_value(pfunction.ENV,expression_default) = (PINT 8)',
    '$lossy_optional_integer_quiet_shape(expression_default)',
    'S.CODE = [pcode]',
    'pcoderedirect_good = CODEREDIRECT pcpath_default (pcpath_default ++ [PCFIELD 1]) false',
    '$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_default) = 1',
    '$code_redirect(pcode.REDIRECTS,pcpath_default) = ((pcpath_default ++ [PCFIELD 1],false))',
    '$compiled_redirect(S,porigin_default) = ((porigin_selected,expression_selected,false,z_root))',
    '$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_default) = ((porigin_cond,porigin_selected))',
    '$call_name_count(pcode.NAMES,pcpath_default ++ [PCFIELD 2]) = 0',
    '$call_name_count(pcode.NAMES,pcpath_default ++ [PCFIELD 1]) = 1',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_cond)',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_selected)',
    '~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_skipped)',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_default)',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$default_current_cache(S,porigin_default) = eps',
    '$lossy_optional_integer_deferred(S,pfunction,1)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'S.RESULT = KNOWN (PINT 8)',
    '$lookup(S.ENV,psparam_later.NAME) = eps',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    r'S.STORE[n_first] = DEFINED (PINT 1) /\ n_first <- S.REFCELLS',
    '$heap_owners($heap_graph(S),HCELL n_first) = 2',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
]

for label, redirects in [
    ('missing', 'eps'),
    ('wrong_target', '[CODEREDIRECT pcpath_default (pcpath_default ++ [PCFIELD 2]) false]'),
    ('wrong_flag', '[CODEREDIRECT pcpath_default (pcpath_default ++ [PCFIELD 1]) true]'),
    ('duplicate', 'pcode.REDIRECTS ++ [pcoderedirect_good]'),
]:
    checks.extend([
        f'S_{label} = S[.CODE = ([pcode[.REDIRECTS = ({redirects})]])]',
        f'$lossy_optional_integer_pruned_ternary(S_{label},pfunction.ENV,porigin_default) = eps',
        f'~$lossy_optional_integer_deferred_bindings(S_{label},pfunction.ENV,porigin_default)',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,1)',
    ])

checks.extend([
    'S_wrong_pool = S[.POOLS = [{UNIT n_unit,CONSTANTS ([(PCONSTANT (pcpath_default ++ [PCFIELD 0]) (PBOOL false))])}]]',
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
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("PHP_INT_SIZE"),$ptascii("PHP_INT_MIN"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_selected)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_default)',
    'pdefaultcache_good = {ORIGIN porigin_default,VALUE PINT 8,CLASS PVSCALAR}',
    'S_wrong_cache = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.VALUE = PINT 1])]',
    '~$lossy_optional_integer_deferred(S_wrong_cache,pfunction,1)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_bound',
    'S_bound.TODO = [TYPE_RECEIVE porigin 2]',
    '$lookup(S_bound.ENV,psparam_later.NAME) = (n_later)',
    'S_bound.STORE[n_later] = DEFINED (PINT 8)',
    r'~(n_later <- S_bound.REFCELLS) /\ $heap_owners($heap_graph(S_bound),HCELL n_later) = 1',
    '$default_current_cache(S_bound,porigin_default) = (pdefaultcache_good)',
    'S_bound.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_bound,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_default) = (pdefaultcache_good)',
    r'~((HCELL n_later) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_later) = 0',
    '$lookup(S_done.ENV,$ptascii("xLazy230")) = (n_first)',
    'S_done.STORE[n_first] = DEFINED (PINT 2)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])


checks.extend([
    'S_integer_pool = S[.POOLS = [{UNIT n_unit,CONSTANTS ([(PCONSTANT (pcpath_default ++ [PCFIELD 0]) (PINT 1))])}]]',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_cond) = (true)',
    '$lossy_optional_integer_pruned_ternary(S_integer_pool,pfunction.ENV,porigin_default) = eps',
    '~$lossy_optional_integer_deferred_bindings(S_integer_pool,pfunction.ENV,porigin_default)',
    'S_bad_child = S[.POOLS = [{UNIT n_unit,CONSTANTS ([(PCONSTANT (pcpath_default ++ [PCFIELD 0]) (PBOOL true)),(PCONSTANT (pcpath_default ++ [PCFIELD 0,PCFIELD 0]) (PBOOL false))])}]]',
    '$lossy_optional_integer_pruned_ternary(S_bad_child,pfunction.ENV,porigin_default) = ((porigin_cond,porigin_selected))',
    '~$lossy_optional_integer_deferred_bindings(S_bad_child,pfunction.ENV,porigin_cond_child)',
    '~$lossy_optional_integer_deferred_bindings(S_bad_child,pfunction.ENV,porigin_cond)',
    '~$lossy_optional_integer_deferred_bindings(S_bad_child,pfunction.ENV,porigin_default)',
    '~$lossy_optional_integer_deferred(S_bad_child,pfunction,1)',
    '~psparam_maximum.BYREF',
    'psparam_maximum.DEFAULT = PSDEFAULT expression_maximum "deferred"',
    '$default_parameter_origin(S,porigin,2) = PORIGIN n_unit pcpath_maximum_param',
    'pcpath_maximum = pcpath_maximum_param ++ [PCFIELD 6]',
    'porigin_maximum = PORIGIN n_unit pcpath_maximum',
    '$origin_node(S.SOURCES,porigin_maximum) = (expression_maximum)',
    'expression_maximum = NExprTernary expression_maximum_cond expression_maximum_skipped expression_maximum_selected metadata_maximum',
    '$pfshape(expression_maximum_cond) = PFSHORT false expression_maximum_child expression_maximum_right',
    '$lossy_optional_integer_special(pfunction.ENV,expression_maximum_cond) = eps',
    '$lossy_optional_integer_special(pfunction.ENV,expression_maximum_child) = (PBOOL false)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_maximum_cond) = (false)',
    'porigin_maximum_cond = PORIGIN n_unit (pcpath_maximum ++ [PCFIELD 0])',
    'porigin_maximum_selected = PORIGIN n_unit (pcpath_maximum ++ [PCFIELD 2])',
    '$pool_value(S.POOLS,porigin_maximum_cond) = (PBOOL false)',
    '$pool_value(S.POOLS,PORIGIN n_unit (pcpath_maximum ++ [PCFIELD 0,PCFIELD 0])) = (PBOOL false)',
    '$pool_value(S.POOLS,porigin_maximum) = eps',
    '$compiled_read(S,porigin_maximum) = eps',
    '$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_maximum) = 1',
    '$code_redirect(pcode.REDIRECTS,pcpath_maximum) = ((pcpath_maximum ++ [PCFIELD 2],false))',
    '$compiled_redirect(S,porigin_maximum) = ((porigin_maximum_selected,expression_maximum_selected,false,z_maximum))',
    '$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_maximum) = ((porigin_maximum_cond,porigin_maximum_selected))',
    '$call_name_count(pcode.NAMES,pcpath_maximum ++ [PCFIELD 1]) = 0',
    '$call_name_count(pcode.NAMES,pcpath_maximum ++ [PCFIELD 2]) = 1',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_maximum)',
    '$lossy_optional_integer_deferred_value(pfunction.ENV,expression_maximum) = (PINT 9223372036854775807)',
    '$lossy_optional_integer_deferred(S,pfunction,2)',
    'pdefaultcache_maximum = {ORIGIN porigin_maximum,VALUE PINT 9223372036854775807,CLASS PVSCALAR}',
    '$default_current_cache(S,porigin_maximum) = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_maximum) = (pdefaultcache_maximum)',
])


checks.extend([
    'porigin_cond_right = PORIGIN n_unit (pcpath_default ++ [PCFIELD 0,PCFIELD 1])',
    '$origin_node(S.SOURCES,porigin_cond_right) = (expression_cond_right)',
    '$call_name_count(pcode.NAMES,pcpath_default ++ [PCFIELD 0,PCFIELD 1]) = 0',
    '~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_cond_right)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_default ++ [PCFIELD 0]) = eps',
    '$compiled_read(S,porigin_cond) = eps',
    '$lossy_optional_integer_pruned_short(S,pfunction.ENV,porigin_cond) = (porigin_cond_child)',
    '$lossy_optional_integer_pruned_short(S,pfunction.ENV,porigin_default) = eps',
    '$lossy_optional_integer_pruned_short(S_bad_child,pfunction.ENV,porigin_cond) = eps',
    '$lossy_optional_integer_pruned_short(S_integer_pool,pfunction.ENV,porigin_cond) = eps',
    'porigin_maximum_child = PORIGIN n_unit (pcpath_maximum ++ [PCFIELD 0,PCFIELD 0])',
    'porigin_maximum_right = PORIGIN n_unit (pcpath_maximum ++ [PCFIELD 0,PCFIELD 1])',
    '$origin_node(S.SOURCES,porigin_maximum_child) = (expression_maximum_child)',
    '$origin_node(S.SOURCES,porigin_maximum_right) = (expression_maximum_right)',
    '$call_name_count(pcode.NAMES,pcpath_maximum ++ [PCFIELD 0,PCFIELD 1]) = 0',
    '~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_maximum_right)',
    '$compiled_read(S,porigin_maximum_cond) = eps',
    '$lossy_optional_integer_pruned_short(S,pfunction.ENV,porigin_maximum_cond) = (porigin_maximum_child)',
    'plenv_bad_left = pfunction.ENV[.CONSTANTS = ([($ptascii("true"),$ptascii("false"))])]',
    '$lossy_optional_integer_condition(plenv_bad_left,expression_cond_child) = (false)',
    '$lossy_optional_integer_pruned_short(S,plenv_bad_left,porigin_cond) = eps',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_bad_left,porigin_cond_child)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_bad_left,porigin_default)',
])
for label, own, left in [
    ('own_integer', 'PINT 1', 'PBOOL true'),
    ('left_integer', 'PBOOL true', 'PINT 1'),
    ('wrong_own', 'PBOOL false', 'PBOOL true'),
    ('wrong_left', 'PBOOL true', 'PBOOL false'),
]:
    checks.extend([
        f'S_{label} = S[.POOLS = [{{UNIT n_unit,CONSTANTS ([(PCONSTANT (pcpath_default ++ [PCFIELD 0]) ({own})),(PCONSTANT (pcpath_default ++ [PCFIELD 0,PCFIELD 0]) ({left}))])}}]]',
        f'$lossy_optional_integer_pruned_short(S_{label},pfunction.ENV,porigin_cond) = eps',
        f'~$lossy_optional_integer_deferred_bindings(S_{label},pfunction.ENV,porigin_cond)',
    ])
for label, retained in [('no_own', '0,PCFIELD 0'), ('no_left', '0')]:
    checks.extend([
        f'S_{label} = S[.POOLS = [{{UNIT n_unit,CONSTANTS ([(PCONSTANT (pcpath_default ++ [PCFIELD {retained}]) (PBOOL true))])}}]]',
        f'$lossy_optional_integer_pruned_short(S_{label},pfunction.ENV,porigin_cond) = eps',
        f'~$lossy_optional_integer_deferred_bindings(S_{label},pfunction.ENV,porigin_cond)',
    ])

CASES = {
    'lazy-boolean-condition-cold-bind': {
        'source': ROWS['lazy-boolean-condition-default-cold-warm']['source'],
        'stage': 'S.TODO = [DEFAULT_BIND porigin 1]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
