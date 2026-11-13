#!/usr/bin/env python3
"""Independent selected integer leaves, receipts and named-hole cache checks."""
import base64
import hashlib
import json
from pathlib import Path


def node(tag, *children):
    return tag + ''.join(f' ({child})' for child in children) + ' eps'


def constant(name, qualified=False):
    encoded = base64.b64encode(name.encode()).decode()
    return node('NExprConstFetch', node('NNameFullyQualified' if qualified else 'NName', f'BYTES "{encoded}"'))


def integer(value):
    return node('NScalarInt', f'INTEGER {value}')


checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("SelectedAlias227")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Bound227"),$ptascii("PHP_INT_MAX"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_bound,psparam_size,psparam_last]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ $ptmasks(psparam_first.TYPE) = ["int"]',
    r'~psparam_bound.BYREF /\ ~psparam_size.BYREF /\ ~psparam_last.BYREF',
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
    '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_bound ++ [PCFIELD 6,PCFIELD 0,PCFIELD 2])) = (NExprConstFetch name_bound metadata_bound)',
    '$pnresolve(pfunction.ENV,PLCONSTANT,name_bound) = PNRESOLVED pnreference_bound',
    r'pnreference_bound.RESOLVED = $ptascii("PHP_INT_MAX") /\ pnreference_bound.FALLBACK = eps',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xAlias227")) = (n_global)',
    r'n_global =/= n_cell /\ S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
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
    '$call_name_count(pcode.NAMES,pcpath_bound ++ [PCFIELD 6,PCFIELD 0,PCFIELD 1]) = 1',
    '$call_name_count(pcode.NAMES,pcpath_size ++ [PCFIELD 6,PCFIELD 0,PCFIELD 2]) = 1',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("Bound227"),$ptascii("PHP_INT_MIN"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_bound)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_bound ++ [PCFIELD 6,PCFIELD 0])) = (expression_selected_bound)',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_selected_bound) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_selected_bound) = (NINT 9223372036854775807)',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_selected_bound) = (expression_leaf_bound)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_leaf_bound) = (NINT 9223372036854775807)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    'S_first.STORE[n_global] = S.STORE[n_global]',
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
    '$lookup(S_done.ENV,$ptascii("xAlias227")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'~((HCELL n_bound) <- S_done.ALLOCATIONS) /\ ~((HCELL n_size) <- S_done.ALLOCATIONS)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

root = '$plempty(false)'
unknown = constant('MISSING_SELECTED_PEER227')
maximum = constant('PHP_INT_MAX')
minimum = constant('PHP_INT_MIN')
size = constant('PHP_INT_SIZE')
selected_values = [
    (node('NExprTernary',constant('true'),maximum,unknown),'9223372036854775807'),
    (node('NExprTernary',constant('false'),unknown,minimum),'$(-9223372036854775808)'),
    (node('NExprTernary',maximum,'ABSENT',integer(0)),'9223372036854775807'),
    (node('NExprBinaryOpCoalesce',constant('null'),size),'8'),
]
for expression, value in selected_values:
    checks.extend([
        f'$lossy_optional_integer_default_in({root},{expression}) = eps',
        f'$lossy_optional_integer_numeric({root},{expression}) = (NINT {value})',
        f'$lossy_optional_integer_deferred_value({root},{expression}) = (PINT {value})',
    ])
zero = node('NExprBinaryOpMinus',size,integer(8))
for expression in [node('NExprBinaryOpCoalesce',zero,size),
                   node('NExprBinaryOpCoalesce',constant('false'),size),
                   node('NExprBinaryOpCoalesce',node('NScalarString','BYTES "MA=="'),size),
                   node('NExprBinaryOpCoalesce',unknown,size),
                   node('NExprTernary',constant('true'),unknown,size)]:
    checks.extend([
        f'$lossy_optional_integer_numeric({root},{expression}) = eps',
        f'$lossy_optional_integer_deferred_value({root},{expression}) = eps',
    ])
selected_nan = node('NExprTernary',constant('true'),constant('NAN'),unknown)
checks.extend([
    f'$lossy_optional_integer_numeric({root},{selected_nan}) = (NFLOAT 9221120237041090560)',
    f'$lossy_optional_integer_default_in({root},{node("NExprCastInt",selected_nan)}) = eps',
    f'$lossy_optional_integer_numeric({root},{node("NExprTernary",constant("true"),integer("9223372036854775808"),unknown)}) = eps',
])
dimension = node('NExprArrayDimFetch',node('NScalarString','BYTES "MTI="'),integer(0))
skipped_dimension = node('NExprTernary',size,maximum,dimension)
checks.extend([
    f'$lossy_optional_integer_numeric({root},{skipped_dimension}) = (NINT 9223372036854775807)',
    f'~$lossy_optional_integer_quiet_shape({skipped_dimension})',
])

checks.extend([
    'metadata_a = eps',
    'plenv_source = $plempty(false)[.CONSTANTS = ([($ptascii("YesReceive219"),$ptascii("true")), ($ptascii("NoReceive219"),$ptascii("false")), ($ptascii("NilReceive219"),$ptascii("null")), ($ptascii("YesReceive216"),$ptascii("true")), ($ptascii("NoReceive216"),$ptascii("false")), ($ptascii("NilReceive216"),$ptascii("null"))])]',
    '$lossy_optional_integer_numeric(plenv_source, NExprBinaryOpCoalesce (NExprTernary (NExprConstFetch (NName (BYTES "WWVzUmVjZWl2ZTIxOQ==") metadata_a) metadata_a) (NExprConstFetch (NName (BYTES "TmlsUmVjZWl2ZTIxOQ==") metadata_a) metadata_a) (NExprConstFetch (NName (BYTES "VW5zZWxlY3RlZFJlY2VpdmUyMTk=") metadata_a) metadata_a) metadata_a) (NScalarInt (INTEGER 1) metadata_a) metadata_a) = (NINT 1)',
    '$lossy_optional_integer_numeric(plenv_source,NExprBinaryOpCoalesce (NExprTernary (NExprConstFetch (NName (BYTES "WWVzUmVjZWl2ZTIxOQ==") metadata_a) metadata_a) (NExprConstFetch (NName (BYTES "TmlsUmVjZWl2ZTIxOQ==") metadata_a) metadata_a) (NExprConstFetch (NName (BYTES "VW5zZWxlY3RlZFJlY2VpdmUyMTk=") metadata_a) metadata_a) metadata_a) (NScalarInt (INTEGER 1) metadata_a) metadata_a) = (NINT 1)',
    '$lossy_optional_integer_numeric(plenv_source, NExprBinaryOpCoalesce (NExprTernary (NExprConstFetch (NName (BYTES "WWVzUmVjZWl2ZTIxNg==") metadata_a) metadata_a) (NExprConstFetch (NName (BYTES "TmlsUmVjZWl2ZTIxNg==") metadata_a) metadata_a) (NExprConstFetch (NName (BYTES "VW5zZWxlY3RlZFJlY2VpdmUyMTY=") metadata_a) metadata_a) metadata_a) (NScalarInt (INTEGER 1) metadata_a) metadata_a) = (NINT 1)',
])

CATALOGUE = Path(__file__).with_name('selected_integer_default_reception_cases.json')
rows = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in rows.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
CASES = {
    'selected-integer-unfolded-named-hole': {
        'source': rows['selected-integer-default-unfolded-alias-arithmetic-named']['source'],
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
