#!/usr/bin/env python3
"""Independent integer-cast nonnull-zero named reception and compatibility checks."""
import base64
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_name('numeric_integer_cast_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("CastAlias232")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Word232"),$ptascii("PHP_INT_SIZE"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_zero,psparam_selected,psparam_last]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ ~psparam_zero.BYREF /\ ~psparam_selected.BYREF /\ ~psparam_last.BYREF',
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
    '$compiled_read(S,PORIGIN n_unit (pcpath_last ++ [PCFIELD 6])) = (PINT 7)',
    'S.CODE = [pcode]',
]
for index, label, value, projection in [(1, 'zero', 0, 'eps'), (2, 'selected', 8, '(8)')]:
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
    'expression_zero = NExprBinaryOpCoalesce expression_zero_left expression_zero_right metadata_zero',
    '$lossy_optional_integer_special(pfunction.ENV,expression_zero_left) = eps',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_zero_left) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_left) = (NINT 0)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_zero) = (false)',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_zero) = (expression_zero_left)',
    '$lossy_optional_integer_default_in(pfunction.ENV,NExprCastInt expression_zero_left metadata_zero) = (0)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_right) = eps',
    '$call_name_count(pcode.NAMES,pcpath_zero ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_zero ++ [PCFIELD 6,PCFIELD 1]) = 1',
    '$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_zero) = eps',
    '$lossy_optional_integer_pruned_short(S,pfunction.ENV,porigin_zero) = eps',
    'expression_selected = NExprTernary expression_condition expression_skipped expression_cast metadata_selected',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_condition) = (false)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_condition) = (NINT 0)',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_selected) = (expression_cast)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_skipped) = eps',
    'expression_cast = NExprCastInt expression_word metadata_cast',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_word) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_word) = (NINT 8)',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_cast) = (8)',
    '$pool_value(S.POOLS,PORIGIN n_unit (pcpath_selected ++ [PCFIELD 6,PCFIELD 0])) = eps',
    '$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_selected) = eps',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0,PCFIELD 0]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 0,PCFIELD 1]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 1]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_selected ++ [PCFIELD 6,PCFIELD 2,PCFIELD 0]) = 1',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xAlias232")) = (n_global)',
    r'n_global =/= n_cell /\ S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero[.VALUE = PINT 8])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,1)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'S_wrong_class = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero[.CLASS = PVSTRING false])]',
    '~$lossy_optional_integer_deferred(S_wrong_class,pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_zero])],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    'S_unknown = S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
    '$default_cache_owner(S_unknown) = eps',
    '~$lossy_optional_integer_deferred(S_unknown,pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("Word232"),$ptascii("PHP_INT_MIN"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_zero)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    r'S_first.STORE[n_global] = S.STORE[n_global] /\ S_first.DEFAULTCACHE = S.DEFAULTCACHE',
    'PhpStep: S_first ~> S_zero',
    r'S_zero.TODO = [TYPE_RECEIVE porigin 2] /\ S_zero.STORE[n_zero] = DEFINED (PINT 0)',
    r'S_zero.DEFAULTCACHE = S.DEFAULTCACHE /\ S_zero.EVENTS = S_first.EVENTS',
    'PhpStep: S_zero ~> S_selected',
    r'S_selected.TODO = [TYPE_RECEIVE porigin 3] /\ S_selected.STORE[n_selected] = DEFINED (PINT 8)',
    r'S_selected.DEFAULTCACHE = S.DEFAULTCACHE /\ S_selected.EVENTS = S_zero.EVENTS',
    'S_done = $drive_steps(S_selected,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_zero) = (pdefaultcache_zero)',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_selected) = (pdefaultcache_selected)',
    '$lookup(S_done.ENV,$ptascii("xAlias232")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_zero) <- S_done.ALLOCATIONS) /\ ~((HCELL n_selected) <- S_done.ALLOCATIONS)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])


def node(tag, *children):
    return tag + ''.join(f' ({child})' for child in children) + ' eps'


def constant(name):
    return node('NExprConstFetch', node('NName', 'BYTES "' + base64.b64encode(name.encode()).decode() + '"'))


root = '$plempty(false)'
for name, value in [('PHP_INT_SIZE', '8'), ('PHP_INT_MAX', '9223372036854775807'),
                    ('PHP_INT_MIN', '$(-9223372036854775808)'), ('PHP_FLOAT_DIG', '15')]:
    checks.append(f'$lossy_optional_integer_default_in({root},{node("NExprCastInt",constant(name))}) = ({value})')

checks.extend(['$lossy_optional_integer_numeric($plempty(false),NExprBinaryOpCoalesce (NExprBinaryOpMinus (NExprConstFetch (NName (BYTES "UEhQX0lOVF9TSVpF") eps) eps) (NScalarInt (INTEGER 8) eps) eps) (NExprConstFetch (NName (BYTES "UEhQX0lOVF9TSVpF") eps) eps) eps) = (NINT 0)', '$lossy_optional_integer_deferred_value($plempty(false),NExprBinaryOpCoalesce (NExprBinaryOpMinus (NExprConstFetch (NName (BYTES "UEhQX0lOVF9TSVpF") eps) eps) (NScalarInt (INTEGER 8) eps) eps) (NExprConstFetch (NName (BYTES "UEhQX0lOVF9TSVpF") eps) eps) eps) = (PINT 0)'])

CASES = {
    'numeric-integer-cast-alias-named-reentry': {
        'source': ROWS['numeric-integer-cast-default-alias-named-reentry']['source'],
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
