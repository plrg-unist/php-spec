#!/usr/bin/env python3
"""Independent imported release defaults, named holes and warning reentry."""
import hashlib
import json
from pathlib import Path

import float_platform_default_reception_review_protocol as previous

CATALOGUE = Path(__file__).with_name('version_integer_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("VersionAlias233")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Major233"),$ptascii("PHP_MAJOR_VERSION")),($ptascii("Minor233"),$ptascii("PHP_MINOR_VERSION")),($ptascii("Patch233"),$ptascii("PHP_RELEASE_VERSION")),($ptascii("Version233"),$ptascii("PHP_VERSION_ID"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_id,psparam_assembled,psparam_selected,psparam_last]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ ~psparam_id.BYREF /\ ~psparam_assembled.BYREF /\ ~psparam_selected.BYREF /\ ~psparam_last.BYREF',
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
for index, label, value, projection in [(1, 'id', 80510, 'eps'),
                                         (2, 'assembled', 80510, 'eps'),
                                         (3, 'selected', 8, '(8)')]:
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
    'expression_id = NExprConstFetch name_id metadata_id',
    '$pnresolve(pfunction.ENV,PLCONSTANT,name_id) = PNRESOLVED pnreference_id',
    r'pnreference_id.RESOLVED = $ptascii("PHP_VERSION_ID") /\ pnreference_id.FALLBACK = eps',
    '$call_name_count(pcode.NAMES,pcpath_id ++ [PCFIELD 6]) = 1',
    'expression_assembled = NExprBinaryOpPlus expression_sum expression_patch metadata_assembled',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_sum) = (NINT 80500)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_patch) = (NINT 10)',
    'expression_selected = NExprTernary expression_condition expression_skipped expression_cast metadata_selected',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_condition) = (NINT 0)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_condition) = (false)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_skipped) = eps',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_selected) = (expression_cast)',
    'expression_cast = NExprCastInt expression_major metadata_cast',
    'expression_major = NExprConstFetch (NNameFullyQualified (BYTES text_major) metadata_major_name) metadata_major',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_major) = (NINT 8)',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_major) = eps',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_cast) = (8)',
    '$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_selected) = eps',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 1]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 2,PCFIELD 0]) = 1',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xAlias233")) = (n_global)',
    r'n_global =/= n_cell /\ S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_id[.VALUE = PINT 8])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,1)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_id[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_id])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    'S_unknown = S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
    r'$default_cache_owner(S_unknown) = eps /\ ~$lossy_optional_integer_deferred(S_unknown,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S[.CURRENT = (pcallcontext[.HOLES = [1,2]])],ptask_resume)',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("Version233"),$ptascii("PHP_RELEASE_VERSION"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_id)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    'S_changed = $write_name(S,psparam_first.NAME,PINT 9)',
    '$lossy_mixed_parameter_source_valid(S_changed,ptask_resume)',
    '~$lossy_mixed_parameter_ready(S_changed,0,n_cell,n_bits)',
    'PhpStep: S_changed ~> S_refused',
    'S_refused = S_changed[.COMPLETION = UNSUPPORTED "lossy mixed parameter receive continuation"]',
    '~$lossy_optional_integer_quiet_shape(NExprBinaryOpCoalesce expression_id (NExprArrayDimFetch expression_id (NScalarInt (INTEGER 0) eps) eps) eps)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    r'S_first.STORE[n_global] = S.STORE[n_global] /\ S_first.DEFAULTCACHE = S.DEFAULTCACHE',
    'PhpStep: S_first ~> S_id',
    r'S_id.TODO = [TYPE_RECEIVE porigin 2] /\ S_id.STORE[n_id] = DEFINED (PINT 80510)',
    r'S_id.DEFAULTCACHE = S.DEFAULTCACHE /\ S_id.EVENTS = S_first.EVENTS',
    'PhpStep: S_id ~> S_assembled',
    r'S_assembled.TODO = [TYPE_RECEIVE porigin 3] /\ S_assembled.STORE[n_assembled] = DEFINED (PINT 80510)',
    r'S_assembled.DEFAULTCACHE = S.DEFAULTCACHE /\ S_assembled.EVENTS = S_id.EVENTS',
    'PhpStep: S_assembled ~> S_selected',
    r'S_selected.TODO = [TYPE_RECEIVE porigin 4] /\ S_selected.STORE[n_selected] = DEFINED (PINT 8)',
    r'S_selected.DEFAULTCACHE = S.DEFAULTCACHE /\ S_selected.EVENTS = S_assembled.EVENTS',
    'S_done = $drive_steps(S_selected,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$lookup(S_done.ENV,$ptascii("xAlias233")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
])
for label in ['id', 'assembled', 'selected']:
    checks.extend([
        f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})',
        rf'~((HCELL n_{label}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_{label}) = 0',
    ])
checks.extend([
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_last) <- S_done.ALLOCATIONS)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])
for name, value in [('PHP_MAJOR_VERSION', 8), ('PHP_MINOR_VERSION', 5),
                    ('PHP_RELEASE_VERSION', 10)]:
    checks.append(f'$lossy_optional_integer_numeric($plempty(false),{previous.constant(name, True)}) = (NINT {value})')
for name in ['php_version_id', 'PHP_VERSION', 'PHP_ZTS', 'UPLOAD_ERR_OK', 'E_STRICT']:
    checks.append(f'$lossy_optional_integer_numeric($plempty(false),{previous.constant(name)}) = eps')
checks.extend([
    'plenv_fallback = $plempty(false)[.NAMESPACE = $ptascii("MissingVersion233")]',
    f'$lossy_optional_integer_numeric(plenv_fallback,{previous.constant("PHP_VERSION_ID")}) = eps',
])
# Execute only the affected old assertion; the old source/stages are not replayed.
affected = [clause for clause in previous.CASES['platform-float-epsilon-named-own-receive']['checks']
            if previous.constant('PHP_VERSION_ID') in clause]
assert affected == [f'$lossy_optional_integer_numeric($plempty(false),{previous.constant("PHP_VERSION_ID")}) = (NINT 80510)']
checks.extend(affected)

CASES = {
    'version-integer-alias-named-reentry': {
        'source': ROWS['version-integer-default-alias-arithmetic-named']['source'],
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE, Path(previous.__file__), previous.CATALOGUE),
                 runner_flags=('--sl',))
