#!/usr/bin/env python3
"""Independent immutable-int name authority and named-hole cache checks."""
import base64
import hashlib
import json
from pathlib import Path


def node(tag, *children):
    return tag + ''.join(f' ({child})' for child in children) + ' eps'


def constant(name, qualified=False):
    encoded = base64.b64encode(name.encode()).decode()
    return node('NExprConstFetch', node('NNameFullyQualified' if qualified else 'NName', f'BYTES "{encoded}"'))


checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("ImmutableAlias225")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Bound225"),$ptascii("PHP_INT_MAX"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_bound,psparam_size,psparam_last]',
    r'psparam_first.REQUIRED /\ psparam_first.BYREF /\ $ptmasks(psparam_first.TYPE) = ["int"]',
    r'~psparam_bound.BYREF /\ ~psparam_size.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
    r'pcallcontext.ARGC = 4 /\ pcallcontext.HOLES = [1,2]',
    r'pcallcontext.CACHE = eps /\ pcallcontext.WRAPPER = eps /\ pcallcontext.INSTANCE = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lookup(S.ENV,psparam_first.NAME) = (n_cell)',
    r'n_cell <- S.REFCELLS /\ $heap_owners($heap_graph(S),HCELL n_cell) = 2',
    'S.STORE[n_cell] = DEFINED (PFLOAT 4615063718147915776)',
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
]
for index, label, value in [(1, 'bound', 9223372036854775805), (2, 'size', 9)]:
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
        f'$default_current_cache(S,porigin_{label}) = (pdefaultcache_{label})',
        f'$lookup(S.ENV,psparam_{label}.NAME) = (n_{label})',
        f'S.STORE[n_{label}] = DEFINED (PINT {value})',
        rf'~(n_{label} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_{label}) = 1',
    ])
checks.extend([
    '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_bound ++ [PCFIELD 6,PCFIELD 0])) = (NExprConstFetch name_bound metadata_bound)',
    '$pnresolve(pfunction.ENV,PLCONSTANT,name_bound) = PNRESOLVED pnreference_bound',
    r'pnreference_bound.RESOLVED = $ptascii("PHP_INT_MAX") /\ pnreference_bound.FALLBACK = eps',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xAlias225")) = (n_cell)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_cold = S[.DEFAULTCACHE = eps]',
    r'$lossy_optional_integer_deferred(S_cold,pfunction,1) /\ $lossy_optional_integer_deferred(S_cold,pfunction,2)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_bound[.VALUE = PINT 9])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,1)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_bound[.VALUE = PFLOAT 4890909195324358656])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'S_wrong_class = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_bound[.CLASS = PVSTRING false])]',
    '~$lossy_optional_integer_deferred(S_wrong_class,pfunction,1)',
    'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_bound])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,1)',
    'S_unknown = S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
    '$default_cache_owner(S_unknown) = eps',
    '~$lossy_optional_integer_deferred(S_unknown,pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    'S.CODE = [pcode]',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("Bound225"),$ptascii("PHP_INT_MIN"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_bound)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    r'S_first.DEFAULTCACHE = S.DEFAULTCACHE /\ S_first.STORE[n_bound] = S.STORE[n_bound] /\ S_first.STORE[n_size] = S.STORE[n_size]',
    'PhpStep: S_first ~> S_bound',
    r'S_bound.TODO = [TYPE_RECEIVE porigin 2] /\ S_bound.STORE[n_bound] = DEFINED (PINT 9223372036854775805)',
    r'S_bound.DEFAULTCACHE = S.DEFAULTCACHE /\ S_bound.EVENTS = S_first.EVENTS',
    'PhpStep: S_bound ~> S_size',
    r'S_size.TODO = [TYPE_RECEIVE porigin 3] /\ S_size.STORE[n_size] = DEFINED (PINT 9)',
    r'S_size.DEFAULTCACHE = S.DEFAULTCACHE /\ S_size.EVENTS = S_bound.EVENTS',
    'S_done = $drive_steps(S_size,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_bound) = (pdefaultcache_bound)',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_size) = (pdefaultcache_size)',
    '$lookup(S_done.ENV,$ptascii("xAlias225")) = (n_cell)',
    'S_done.STORE[n_cell] = DEFINED (PINT 1)',
    r'~((HCELL n_bound) <- S_done.ALLOCATIONS) /\ ~((HCELL n_size) <- S_done.ALLOCATIONS)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

checks.append('plenv_root = $plempty(false)')
for name, value in [('PHP_INT_MAX', '9223372036854775807'), ('PHP_INT_MIN', '$(-9223372036854775808)'), ('PHP_INT_SIZE', '8')]:
    expression = constant(name)
    checks.extend([
        f'$lossy_optional_integer_default_in($plempty(false),{expression}) = eps',
        f'$lossy_optional_integer_numeric(plenv_root,{expression}) = (NINT {value})',
        f'$lossy_optional_integer_deferred_value($plempty(false),{expression}) = (PINT {value})',
    ])
for environment, name, qualified, expected in [
    ('$plempty(false)', 'php_int_max', False, 'eps'),
    ('$plempty(false)', 'MISSING_INTEGER225', False, 'eps'),
    ('$plempty(false)', 'E_WARNING', False, 'eps'),
    ('$plempty(false)', 'PHP_OUTPUT_HANDLER_START', False, 'eps'),
    ('pfunction.ENV', 'PHP_INT_MAX', False, 'eps'),
    ('pfunction.ENV', 'Bound225', False, '(NINT 9223372036854775807)'),
    ('pfunction.ENV', 'bound225', False, 'eps'),
    ('pfunction.ENV', 'PHP_INT_MAX', True, '(NINT 9223372036854775807)'),
]:
    checks.append(f'$lossy_optional_integer_numeric({environment},{constant(name,qualified)}) = {expected}')
for expression in [
    node('NExprBinaryOpPlus', constant('PHP_INT_MAX'), node('NScalarInt', 'INTEGER 1')),
    node('NExprBinaryOpDiv', constant('PHP_INT_MIN'), node('NExprUnaryMinus', node('NScalarInt', 'INTEGER 1'))),
]:
    checks.extend([
        f'$lossy_optional_integer_numeric($plempty(false),{expression}) = (NFLOAT 4890909195324358656)',
        f'$lossy_optional_integer_deferred_value($plempty(false),{expression}) = (PFLOAT 4890909195324358656)',
    ])
checks.append('$typed_weak(["int"],PFLOAT 4890909195324358656) = TYPEREJECT')

CATALOGUE = Path(__file__).with_name('immutable_integer_default_reception_cases.json')
rows = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in rows.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
CASES = {
    'immutable-integer-named-hole': {
        'source': rows['immutable-integer-default-alias-named-hole']['source'],
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
