#!/usr/bin/env python3
"""Independent diagnostic defaults, named holes and warning reentry."""
import hashlib
import json
from pathlib import Path

import immutable_integer_default_reception_review_protocol as previous

CATALOGUE = Path(__file__).with_name('diagnostic_integer_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("DiagnosticAlias234")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Warning234"),$ptascii("E_WARNING")),($ptascii("Notice234"),$ptascii("E_NOTICE")),($ptascii("All234"),$ptascii("E_ALL"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_mask,psparam_sum,psparam_selected,psparam_last]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ ~psparam_mask.BYREF /\ ~psparam_sum.BYREF /\ ~psparam_selected.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
    r'pcallcontext.ARGC = 5 /\ pcallcontext.HOLES = [1,2,3]',
    r'pcallcontext.CACHE = eps /\ pcallcontext.WRAPPER = eps /\ pcallcontext.INSTANCE = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lookup(S.ENV,psparam_first.NAME) = (n_cell)',
    r'~(n_cell <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_cell) = 1',
    'S.STORE[n_cell] = DEFINED (PFLOAT 4609434218613702656)',
    r'n_bits = 4609434218613702656 /\ i = 1',
    'z = $default_parameter_line(S,porigin,0)',
    'ptask_resume = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z',
    '$lossy_mixed_parameter_source_valid(S,ptask_resume)',
    '$lossy_mixed_parameter_ready(S,0,n_cell,n_bits)',
    '$call_task_valid(S,ptask_resume)',
    '$task_nodes(ptask_resume) = eps',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 8)',
    '$default_parameter_origin(S,porigin,4) = PORIGIN n_unit pcpath_last',
    '$default_at(pfunction.DEFAULTS,4) = ({INDEX 4,ORIGIN PORIGIN n_unit (pcpath_last ++ [PCFIELD 6]),KIND PDSTORED})',
    '$compiled_read(S,PORIGIN n_unit (pcpath_last ++ [PCFIELD 6])) = (PINT 7)',
    'S.CODE = [pcode]',
]
for index, label, value, projection in [(1, 'mask', 30719, 'eps'),
                                         (2, 'sum', 11, 'eps'),
                                         (3, 'selected', 8192, '(8192)')]:
    checks.extend([
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
        f'$default_current_cache(S,porigin_{label}) = (pdefaultcache_{label})',
        f'$lookup(S.ENV,psparam_{label}.NAME) = (n_{label})',
        f'S.STORE[n_{label}] = DEFINED (PINT {value})',
        rf'~(n_{label} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_{label}) = 1',
    ])
checks.extend([
    'expression_mask = NExprConstFetch name_mask metadata_mask',
    '$pnresolve(pfunction.ENV,PLCONSTANT,name_mask) = PNRESOLVED pnreference_mask',
    r'pnreference_mask.RESOLVED = $ptascii("E_ALL") /\ pnreference_mask.FALLBACK = eps',
    '$call_name_count(pcode.NAMES,pcpath_mask ++ [PCFIELD 6]) = 1',
    'expression_sum = NExprBinaryOpPlus expression_pair expression_notice metadata_sum',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_pair) = (NINT 3)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_notice) = (NINT 8)',
    'expression_selected = NExprTernary expression_condition expression_skipped expression_cast metadata_selected',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_condition) = (NINT 0)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_condition) = (false)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_skipped) = eps',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_selected) = (expression_cast)',
    'expression_cast = NExprCastInt expression_deprecated metadata_cast',
    'expression_deprecated = NExprConstFetch (NNameFullyQualified (BYTES text_deprecated) metadata_deprecated_name) metadata_deprecated',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_deprecated) = (NINT 8192)',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_deprecated) = eps',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_cast) = (8192)',
    '$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_selected) = eps',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 1]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 2,PCFIELD 0]) = 1',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xAlias234")) = (n_global)',
    r'n_global =/= n_cell /\ S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_mask[.VALUE = PINT 2])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,1)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_mask[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_mask])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    'S_unknown = S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
    r'$default_cache_owner(S_unknown) = eps /\ ~$lossy_optional_integer_deferred(S_unknown,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S[.CURRENT = (pcallcontext[.HOLES = [1,2]])],ptask_resume)',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("All234"),$ptascii("E_ERROR"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_mask)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    'S_changed = $write_name(S,psparam_first.NAME,PINT 9)',
    '$lossy_mixed_parameter_source_valid(S_changed,ptask_resume)',
    '~$lossy_mixed_parameter_ready(S_changed,0,n_cell,n_bits)',
    'PhpStep: S_changed ~> S_refused',
    'S_refused = S_changed[.COMPLETION = UNSUPPORTED "lossy mixed parameter receive continuation"]',
    '~$lossy_optional_integer_quiet_shape(NExprBinaryOpCoalesce expression_mask (NExprArrayDimFetch expression_mask (NScalarInt (INTEGER 0) eps) eps) eps)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    r'S_first.STORE[n_global] = S.STORE[n_global] /\ S_first.DEFAULTCACHE = S.DEFAULTCACHE',
    'PhpStep: S_first ~> S_mask',
    r'S_mask.TODO = [TYPE_RECEIVE porigin 2] /\ S_mask.STORE[n_mask] = DEFINED (PINT 30719)',
    r'S_mask.DEFAULTCACHE = S.DEFAULTCACHE /\ S_mask.EVENTS = S_first.EVENTS',
    'PhpStep: S_mask ~> S_sum',
    r'S_sum.TODO = [TYPE_RECEIVE porigin 3] /\ S_sum.STORE[n_sum] = DEFINED (PINT 11)',
    r'S_sum.DEFAULTCACHE = S.DEFAULTCACHE /\ S_sum.EVENTS = S_mask.EVENTS',
    'PhpStep: S_sum ~> S_selected',
    r'S_selected.TODO = [TYPE_RECEIVE porigin 4] /\ S_selected.STORE[n_selected] = DEFINED (PINT 8192)',
    r'S_selected.DEFAULTCACHE = S.DEFAULTCACHE /\ S_selected.EVENTS = S_sum.EVENTS',
    'S_done = $drive_steps(S_selected,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$lookup(S_done.ENV,$ptascii("xAlias234")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
])
for label in ['mask', 'sum', 'selected']:
    checks.extend([
        f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})',
        rf'~((HCELL n_{label}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_{label}) = 0',
    ])
checks.extend([
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_last) <- S_done.ALLOCATIONS)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])
for name, value in [('E_ERROR', 1), ('E_NOTICE', 8), ('E_DEPRECATED', 8192)]:
    checks.append(f'$lossy_optional_integer_numeric($plempty(false),{previous.constant(name, True)}) = (NINT {value})')
for name in ['e_all', 'PHP_VERSION', 'PHP_ZTS', 'E_STRICT', 'E_DONT_BAIL', 'E_CORE']:
    checks.append(f'$lossy_optional_integer_numeric($plempty(false),{previous.constant(name)}) = eps')
checks.extend([
    'plenv_fallback = $plempty(false)[.NAMESPACE = $ptascii("MissingDiagnostic234")]',
    f'$lossy_optional_integer_numeric(plenv_fallback,{previous.constant("E_ALL")}) = eps',
])
# Execute only the affected old assertion; the old source/stage is not replayed.
affected = [clause for clause in previous.CASES['immutable-integer-named-hole']['checks']
            if previous.constant('E_WARNING') in clause]
assert affected == [f'$lossy_optional_integer_numeric($plempty(false),{previous.constant("E_WARNING")}) = (NINT 2)']
checks.extend(affected)

CASES = {
    'diagnostic-integer-alias-named-reentry': {
        'source': ROWS['diagnostic-integer-default-alias-arithmetic-named']['source'],
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE, Path(previous.__file__), previous.CATALOGUE),
                 runner_flags=('--sl',))
