#!/usr/bin/env python3
"""Numeric integer casts and nonnull zero preserve exact caches and fresh locals."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('numeric_integer_cast_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

common = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.NAME = $ptascii("castDefaults232")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_size,psparam_zero,psparam_bound,psparam_value]',
    r'psparam_first.REQUIRED /\ psparam_first.BYREF /\ psparam_zero.BYREF',
    r'~psparam_size.BYREF /\ ~psparam_bound.BYREF /\ ~psparam_value.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps /\ pcallcontext.CACHE = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    r'S.STORE[n_first] = DEFINED (PINT 1) /\ n_first <- S.REFCELLS',
    '$heap_owners($heap_graph(S),HCELL n_first) = 2',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
]
for index, label, value, projection in [
    (1, 'size', '8', '(8)'),
    (2, 'zero', '0', 'eps'),
    (3, 'bound', '9223372036854775807', '(9223372036854775807)'),
    (4, 'value', '9223372036854775807', 'eps'),
]:
    common.extend([
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{label},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        rf'$pool_value(S.POOLS,porigin_{label}) = eps /\ $compiled_read(S,porigin_{label}) = eps',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = {projection}',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = (NINT {value})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = (PINT {value})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_{label})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE PINT {value},CLASS PVSCALAR}}',
    ])
common.extend([
    'expression_size = NExprCastInt expression_size_leaf metadata_size',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_size_leaf) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_size_leaf) = (NINT 8)',
    'expression_bound = NExprCastInt expression_bound_leaf metadata_bound',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_bound_leaf) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_bound_leaf) = (NINT 9223372036854775807)',
    'expression_zero = NExprBinaryOpCoalesce expression_zero_left expression_zero_right metadata_zero',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_zero_left) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_left) = (NINT 0)',
    '$lossy_optional_integer_special(pfunction.ENV,expression_zero_left) = eps',
    '$lossy_optional_integer_default_in(pfunction.ENV,NExprCastInt expression_zero_left metadata_zero) = (0)',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_zero) = (expression_zero_left)',
    '$lossy_optional_integer_leaf_truth(pfunction.ENV,expression_zero) = ((expression_zero_left,false))',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_zero) = (false)',
    'expression_value = NExprBinaryOpCoalesce expression_value_left expression_value_right metadata_value',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_value_left) = (NINT 9223372036854775807)',
    '$lossy_optional_integer_default_in(pfunction.ENV,NExprCastInt expression_value_left metadata_value) = (9223372036854775807)',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_value) = (expression_value_left)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_value) = (true)',
    'S.CODE = [pcode]',
    '$call_name_count(pcode.NAMES,pcpath_zero ++ [PCFIELD 6,PCFIELD 1]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_value ++ [PCFIELD 6,PCFIELD 1]) = 1',
    '$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_zero) = eps',
    '$lossy_optional_integer_pruned_short(S,pfunction.ENV,porigin_zero) = eps',
    '~$lossy_optional_integer_deferred_bindings(S[.CODE = ([pcode[.NAMES = eps]])],pfunction.ENV,porigin_zero)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("PHP_INT_SIZE"),$ptascii("PHP_INT_MAX"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_size)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_zero)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])],pfunction,1)',
])

CASES = {}
for index, label, value, float_bits in [(1, 'size', 8, 4620693217682128896),
                                        (2, 'zero', 0, 0)]:
    checks = common + [
        f'S.RESULT = KNOWN (PINT {value})',
        f'$default_current_cache(S,porigin_{label}) = eps',
        f'$lookup(S.ENV,psparam_{label}.NAME) = eps',
        f'S_good = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{label})]',
        f'$lossy_optional_integer_deferred(S_good,pfunction,{index})',
        f'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{label}[.VALUE = PINT {value + 1}])]',
        f'~$lossy_optional_integer_deferred(S_wrong_value,pfunction,{index})',
        f'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{label}[.VALUE = PFLOAT {float_bits}])]',
        '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
        f'~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,{index})',
        f'S_duplicate = S_good[.DEFAULTCACHE = (S_good.DEFAULTCACHE ++ [pdefaultcache_{label}])]',
        f'~$lossy_optional_integer_deferred(S_duplicate,pfunction,{index})',
        'S_budget = $drive_steps(S,0)',
        'S_budget = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        'PhpStep: S ~> S_bound',
        f'S_bound.TODO = [TYPE_RECEIVE porigin {index + 1}]',
        f'$lookup(S_bound.ENV,psparam_{label}.NAME) = (n_local)',
        f'S_bound.STORE[n_local] = DEFINED (PINT {value})',
        r'~(n_local <- S_bound.REFCELLS) /\ $heap_owners($heap_graph(S_bound),HCELL n_local) = 1',
        f'$default_current_cache(S_bound,porigin_{label}) = (pdefaultcache_{label})',
        'S_bound.EVENTS = S.EVENTS',
        'S_done = $drive_steps(S_bound,3000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
        '$default_cache_at(S_done.DEFAULTCACHE,porigin_size) = (pdefaultcache_size)',
        '$default_cache_at(S_done.DEFAULTCACHE,porigin_zero) = (pdefaultcache_zero)',
        '$default_cache_at(S_done.DEFAULTCACHE,porigin_bound) = (pdefaultcache_bound)',
        '$default_cache_at(S_done.DEFAULTCACHE,porigin_value) = (pdefaultcache_value)',
        '~((HCELL n_local) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_done),HCELL n_local) = 0',
        '$lookup(S_done.ENV,$ptascii("xCast232")) = (n_first)',
        'S_done.STORE[n_first] = DEFINED (PINT 2)',
        r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
    ]
    if index == 2:
        checks.extend([
            '$default_current_cache(S,porigin_size) = (pdefaultcache_size)',
            '$lookup(S.ENV,psparam_size.NAME) = (n_size)',
            r'S.STORE[n_size] = DEFINED (PINT 8) /\ ~(n_size <- S.REFCELLS)',
        ])
    CASES[f'numeric-integer-{label}-cold-bind'] = {
        'source': ROWS['numeric-integer-cast-default-cold-warm']['source'],
        'stage': f'S.TODO = [DEFAULT_BIND porigin {index}]',
        'checks': checks,
    }

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
