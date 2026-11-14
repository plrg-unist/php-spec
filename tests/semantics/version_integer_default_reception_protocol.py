#!/usr/bin/env python3
"""Pinned release components retain raw caches and fresh BYREF default locals."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('version_integer_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.NAME = $ptascii("versionDefaults233")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_major,psparam_minor,psparam_release,psparam_id,psparam_zero]',
    r'psparam_first.REQUIRED /\ psparam_first.BYREF /\ psparam_minor.BYREF',
    r'~psparam_major.BYREF /\ ~psparam_release.BYREF /\ ~psparam_id.BYREF /\ ~psparam_zero.BYREF',
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
for index, label, value in [(1, 'major', 8), (2, 'minor', 5),
                            (3, 'release', 10), (4, 'id', 80510), (5, 'zero', 0)]:
    checks.extend([
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{label},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        rf'$pool_value(S.POOLS,porigin_{label}) = eps /\ $compiled_read(S,porigin_{label}) = eps',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = eps',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = (NINT {value})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = (PINT {value})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_{label})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE PINT {value},CLASS PVSCALAR}}',
    ])
checks.extend([
    'expression_zero = NExprBinaryOpCoalesce expression_zero_left expression_zero_right metadata_zero',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_left) = (NINT 0)',
    '$lossy_optional_integer_special(pfunction.ENV,expression_zero_left) = eps',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_zero) = (expression_zero_left)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_zero) = (false)',
    'S.CODE = [pcode]',
    '$call_name_count(pcode.NAMES,pcpath_minor ++ [PCFIELD 6]) = 1',
    '~$lossy_optional_integer_deferred_bindings(S[.CODE = ([pcode[.NAMES = eps]])],pfunction.ENV,porigin_minor)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("PHP_MINOR_VERSION"),$ptascii("PHP_RELEASE_VERSION"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_minor)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],2)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,2)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,2)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])],pfunction,2)',
    '$default_current_cache(S,porigin_major) = (pdefaultcache_major)',
    '$lookup(S.ENV,psparam_major.NAME) = (n_major)',
    r'S.STORE[n_major] = DEFINED (PINT 8) /\ ~(n_major <- S.REFCELLS)',
    'S.RESULT = KNOWN (PINT 5)',
    '$default_current_cache(S,porigin_minor) = eps',
    '$lookup(S.ENV,psparam_minor.NAME) = eps',
    'S_good = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_minor)]',
    '$lossy_optional_integer_deferred(S_good,pfunction,2)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_minor[.VALUE = PINT 6])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,2)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_minor[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,2)',
    'S_duplicate = S_good[.DEFAULTCACHE = (S_good.DEFAULTCACHE ++ [pdefaultcache_minor])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,2)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_bound',
    'S_bound.TODO = [TYPE_RECEIVE porigin 3]',
    '$lookup(S_bound.ENV,psparam_minor.NAME) = (n_local)',
    'S_bound.STORE[n_local] = DEFINED (PINT 5)',
    r'~(n_local <- S_bound.REFCELLS) /\ $heap_owners($heap_graph(S_bound),HCELL n_local) = 1',
    '$default_current_cache(S_bound,porigin_minor) = (pdefaultcache_minor)',
    'S_bound.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_bound,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
])
for label in ['major', 'minor', 'release', 'id', 'zero']:
    checks.append(f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})')
checks.extend([
    '~((HCELL n_local) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_local) = 0',
    '$lookup(S_done.ENV,$ptascii("xVersion233")) = (n_first)',
    'S_done.STORE[n_first] = DEFINED (PINT 2)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

CASES = {
    'version-integer-minor-cold-bind': {
        'source': ROWS['version-integer-default-cold-warm']['source'],
        'stage': 'S.TODO = [DEFAULT_BIND porigin 2]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
