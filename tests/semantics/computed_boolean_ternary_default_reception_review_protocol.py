#!/usr/bin/env python3
"""Independent computed-condition named-hole and shared-cache authority."""
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_name('computed_boolean_ternary_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("ComputedAlias229")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Word229"),$ptascii("PHP_INT_SIZE"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_size,psparam_minimum,psparam_last]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ $ptmasks(psparam_first.TYPE) = ["int"]',
    r'~psparam_size.BYREF /\ ~psparam_minimum.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
    r'pcallcontext.ARGC = 4 /\ pcallcontext.HOLES = [1,2]',
    r'pcallcontext.CACHE = eps /\ pcallcontext.WRAPPER = eps /\ pcallcontext.INSTANCE = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lookup(S.ENV,psparam_first.NAME) = (n_cell)',
    r'~(n_cell <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_cell) = 1',
    'S.STORE[n_cell] = DEFINED (PFLOAT 4609434218613702656)',
    r'n_bits = 4609434218613702656 /\ i = 1',
    'z = $default_parameter_line(S,porigin,0)',
    '$lossy_mixed_parameter_source_valid(S,LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    '$lossy_mixed_parameter_ready(S,0,n_cell,n_bits)',
    '$call_task_valid(S,LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z) = eps',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 8)',
    '$default_parameter_origin(S,porigin,3) = PORIGIN n_unit pcpath_last',
    'porigin_last = PORIGIN n_unit (pcpath_last ++ [PCFIELD 6])',
    '$default_at(pfunction.DEFAULTS,3) = ({INDEX 3,ORIGIN porigin_last,KIND PDSTORED})',
    '$compiled_read(S,porigin_last) = (PINT 7)',
    '~$lossy_optional_integer_deferred(S,pfunction,3)',
    'S.CODE = [pcode]',
]
for index, label, value, boolean, selected, skipped in [
    (1, 'size', '8', 'true', 1, 2),
    (2, 'minimum', '$(-9223372036854775808)', 'false', 2, 1),
]:
    checks.extend([
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{label}',
        f'pcpath_default_{label} = pcpath_{label} ++ [PCFIELD 6]',
        f'porigin_{label} = PORIGIN n_unit pcpath_default_{label}',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{label},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        rf'$pool_value(S.POOLS,porigin_{label}) = eps /\ $compiled_read(S,porigin_{label}) = eps',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = eps',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = (NINT {value})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = (PINT {value})',
        f'$lossy_optional_integer_quiet_shape(expression_{label})',
        f'porigin_cond_{label} = PORIGIN n_unit (pcpath_default_{label} ++ [PCFIELD 0])',
        f'porigin_selected_{label} = PORIGIN n_unit (pcpath_default_{label} ++ [PCFIELD {selected}])',
        f'porigin_skipped_{label} = PORIGIN n_unit (pcpath_default_{label} ++ [PCFIELD {skipped}])',
        f'$origin_node(S.SOURCES,porigin_cond_{label}) = (expression_cond_{label})',
        f'$origin_node(S.SOURCES,porigin_selected_{label}) = (expression_selected_{label})',
        f'$lossy_optional_integer_special(pfunction.ENV,expression_cond_{label}) = eps',
        f'$lossy_optional_integer_condition(pfunction.ENV,expression_cond_{label}) = ({boolean})',
        f'$pool_value(S.POOLS,porigin_cond_{label}) = (PBOOL {boolean})',
        f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_default_{label}) = 1',
        f'$code_redirect(pcode.REDIRECTS,pcpath_default_{label}) = ((pcpath_default_{label} ++ [PCFIELD {selected}],false))',
        f'$compiled_redirect(S,porigin_{label}) = ((porigin_selected_{label},expression_selected_{label},false,z_root_{label}))',
        f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_{label}) = ((porigin_cond_{label},porigin_selected_{label}))',
        f'$call_name_count(pcode.NAMES,pcpath_default_{label} ++ [PCFIELD {selected}]) = 1',
        f'$call_name_count(pcode.NAMES,pcpath_default_{label} ++ [PCFIELD {skipped}]) = 0',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_cond_{label})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_selected_{label})',
        f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_skipped_{label})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_{label})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,porigin_{label}) = (pdefaultcache_{label})',
        f'$lookup(S.ENV,psparam_{label}.NAME) = (n_{label})',
        f'S.STORE[n_{label}] = DEFINED (PINT {value})',
        rf'~(n_{label} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_{label}) = 1',
    ])
checks.extend([
    '$pfshape(expression_cond_size) = PFBINARY LESS expression_left_size expression_right_size',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_left_size) = (NINT 1)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_right_size) = (NINT 2)',
    '$pfshape(expression_cond_minimum) = PFBINARY IDENTICAL expression_left_minimum expression_right_minimum',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_left_minimum) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_right_minimum) = (NFLOAT 4611686018427387904)',
    '~$num_identical(NINT 2,NFLOAT 4611686018427387904)',
    '$origin_node(S.SOURCES,porigin_selected_size) = (NExprConstFetch name_word metadata_word)',
    '$pnresolve(pfunction.ENV,PLCONSTANT,name_word) = PNRESOLVED pnreference_word',
    r'pnreference_word.RESOLVED = $ptascii("PHP_INT_SIZE") /\ pnreference_word.FALLBACK = eps',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xAlias229")) = (n_global)',
    r'n_global =/= n_cell /\ S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_cold = S[.DEFAULTCACHE = eps]',
    r'$lossy_optional_integer_deferred(S_cold,pfunction,1) /\ $lossy_optional_integer_deferred(S_cold,pfunction,2)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_size[.VALUE = PINT 9])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,1)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_size[.VALUE = PFLOAT 4620693217682128896])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'S_wrong_class = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_size[.CLASS = PVSTRING false])]',
    '~$lossy_optional_integer_deferred(S_wrong_class,pfunction,1)',
    'S_duplicate_cache = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_size])]',
    '~$lossy_optional_integer_deferred(S_duplicate_cache,pfunction,1)',
    'S_unknown = S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
    '$default_cache_owner(S_unknown) = eps',
    '~$lossy_optional_integer_deferred(S_unknown,pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("Word229"),$ptascii("PHP_INT_MIN"))])]',
    '$lossy_optional_integer_pruned_ternary(S,plenv_wrong,porigin_size) = ((porigin_cond_size,porigin_selected_size))',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_size)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    'plenv_unused = pfunction.ENV[.CONSTANTS = (pfunction.ENV.CONSTANTS ++ [($ptascii("MISSING_LESS229"),$ptascii("NAN"))])]',
    '$lossy_optional_integer_deferred_bindings(S,plenv_unused,porigin_size)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_unused],1)',
    'S_no_names = S[.CODE = ([pcode[.NAMES = eps]])]',
    '$lossy_optional_integer_pruned_ternary(S_no_names,pfunction.ENV,porigin_size) = ((porigin_cond_size,porigin_selected_size))',
    '~$lossy_optional_integer_deferred_bindings(S_no_names,pfunction.ENV,porigin_size)',
    'pcodename_duplicate = CODENAME (pcpath_default_size ++ [PCFIELD 1]) ($ptascii("PHP_INT_SIZE")) eps',
    'S_duplicate_name = S[.CODE = ([pcode[.NAMES = (pcode.NAMES ++ [pcodename_duplicate])]])]',
    '~$lossy_optional_integer_deferred_bindings(S_duplicate_name,pfunction.ENV,porigin_size)',
])
for label, pool in [('wrong_bool', 'PBOOL false'), ('wrong_tag', 'PINT 1')]:
    checks.extend([
        f'S_{label}_pool = S[.POOLS = ([{{UNIT n_unit,CONSTANTS ([(PCONSTANT (pcpath_default_size ++ [PCFIELD 0]) ({pool}))])}}])]',
        f'$lossy_optional_integer_pruned_ternary(S_{label}_pool,pfunction.ENV,porigin_size) = eps',
        f'~$lossy_optional_integer_deferred_bindings(S_{label}_pool,pfunction.ENV,porigin_size)',
    ])
for label, redirects in [
    ('wrong_child', '[CODEREDIRECT pcpath_default_size (pcpath_default_size ++ [PCFIELD 2]) false]'),
    ('wrong_flag', '[CODEREDIRECT pcpath_default_size (pcpath_default_size ++ [PCFIELD 1]) true]'),
    ('duplicate', 'pcode.REDIRECTS ++ [CODEREDIRECT pcpath_default_size (pcpath_default_size ++ [PCFIELD 1]) false]'),
]:
    checks.extend([
        f'S_{label}_redirect = S[.CODE = ([pcode[.REDIRECTS = ({redirects})]])]',
        f'$lossy_optional_integer_pruned_ternary(S_{label}_redirect,pfunction.ENV,porigin_size) = eps',
        f'~$lossy_optional_integer_deferred_bindings(S_{label}_redirect,pfunction.ENV,porigin_size)',
    ])
checks.extend([
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    'S_first.STORE[n_global] = S.STORE[n_global]',
    r'S_first.DEFAULTCACHE = S.DEFAULTCACHE /\ S_first.STORE[n_size] = S.STORE[n_size] /\ S_first.STORE[n_minimum] = S.STORE[n_minimum]',
    'PhpStep: S_first ~> S_size',
    r'S_size.TODO = [TYPE_RECEIVE porigin 2] /\ S_size.STORE[n_size] = DEFINED (PINT 8)',
    r'S_size.DEFAULTCACHE = S.DEFAULTCACHE /\ S_size.EVENTS = S_first.EVENTS /\ S_size.PARAMETERRECEIVES = S.PARAMETERRECEIVES',
    'PhpStep: S_size ~> S_minimum',
    r'S_minimum.TODO = [TYPE_RECEIVE porigin 3] /\ S_minimum.STORE[n_minimum] = DEFINED (PINT $(-9223372036854775808))',
    r'S_minimum.DEFAULTCACHE = S.DEFAULTCACHE /\ S_minimum.EVENTS = S_size.EVENTS',
    'S_done = $drive_steps(S_minimum,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_size) = (pdefaultcache_size)',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_minimum) = (pdefaultcache_minimum)',
    '$lookup(S_done.ENV,$ptascii("xAlias229")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_size) <- S_done.ALLOCATIONS) /\ ~((HCELL n_minimum) <- S_done.ALLOCATIONS)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

CASES = {
    'computed-boolean-ternary-comparison-named-reentry': {
        'source': ROWS['computed-boolean-ternary-default-comparison-alias-reentry']['source'],
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
