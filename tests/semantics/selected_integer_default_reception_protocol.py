#!/usr/bin/env python3
"""Selected integer defaults preserve proper leaf values and formal ownership."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('selected_integer_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def authority(function):
    return [
        '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
        f'pfunction.NAME = $ptascii("{function}")',
        'S.CURRENT = (pcallcontext)',
        r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
        r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps',
        r'pcallcontext.CACHE = eps /\ pcallcontext.WRAPPER = eps /\ pcallcontext.INSTANCE = eps',
        r'pcallcontext.RECEIVER = eps /\ pcallcontext.LEXICAL_CLASS = eps /\ pcallcontext.CALLED_CLASS = eps',
        '$default_cache_owner(S) = (CACHE_SHARED)',
        '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
        r'$call_descriptors_valid(S) /\ $heap_valid($heap_graph(S)) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    ]


def default(index, label, value, numeric):
    return [
        f'pfunction.SIGNATURE.PARAMETERS[{index}] = psparam_{label}',
        fr'~psparam_{label}.REQUIRED /\ ~psparam_{label}.VARIADIC /\ $ptmasks(psparam_{label}.TYPE) = ["int"]',
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{label},KIND PDDEFERRED}})',
        fr'$pool_value(S.POOLS,porigin_{label}) = eps /\ $compiled_read(S,porigin_{label}) = eps',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = eps',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = ({numeric})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = ({value})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_{label})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'$default_current_cache(S,porigin_{label}) = eps',
        f'$lookup(S.ENV,psparam_{label}.NAME) = eps',
    ]


cold = authority('selectedDefaults227')
for index, label, value in [(1, 'max', '9223372036854775807'), (2, 'min', '$(-9223372036854775808)'), (3, 'size', '8')]:
    cold += default(index, label, 'PINT ' + value, 'NINT ' + value)
    cold += [
        f'$lossy_optional_integer_selection_shape(expression_{label})',
        f'$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_{label}) = (expression_selected_{label})',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_selected_{label}) = (NINT {value})',
        f'$typed_parameter_conversion(S,psparam_{label},PINT {value}) = TYPEVALUE (PINT {value})',
    ]
cold += [
    'expression_max = NExprTernary expression_selected_max ABSENT expression_max_no metadata_max',
    'expression_min = NExprTernary expression_min_condition expression_min_yes expression_selected_min metadata_min',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_min_condition) = (NINT 0)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_min_condition) = (false)',
    'expression_size = NExprBinaryOpCoalesce expression_size_left expression_selected_size metadata_size',
    '$lossy_optional_integer_special(pfunction.ENV,expression_size_left) = (PNULL)',
    r'psparam_max.BYREF /\ ~psparam_min.BYREF /\ ~psparam_size.BYREF',
    'S.RESULT = KNOWN (PINT 9223372036854775807)',
    'pfunction.SIGNATURE.PARAMETERS[0] = psparam_first',
    'psparam_first.BYREF',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    r'S.STORE[n_first] = DEFINED (PINT 1) /\ n_first <- S.REFCELLS',
    '$heap_owners($heap_graph(S),HCELL n_first) = 2',
    'pdefaultcache_good = {ORIGIN porigin_max,VALUE PINT 9223372036854775807,CLASS PVSCALAR}',
    'S_good = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good)]',
    '$lossy_optional_integer_deferred(S_good,pfunction,1)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.VALUE = PINT 9223372036854775806])]',
    '$default_caches_valid(S_wrong_value,S_wrong_value.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,1)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.VALUE = PFLOAT 4890909195324358656])]',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    '~$lossy_optional_integer_deferred(S_good[.DEFAULTCACHE = (S_good.DEFAULTCACHE ++ [pdefaultcache_good])],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    'S.CODE = [pcode]',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("PHP_INT_MAX"),$ptascii("PHP_INT_MIN"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_max)',
    'plenv_namespace = pfunction.ENV[.NAMESPACE = $ptascii("Unresolved225")]',
    '$lossy_optional_integer_numeric(plenv_namespace,expression_max) = eps',
    '$lossy_optional_integer_deferred_value(plenv_namespace,expression_max) = eps',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_max',
    'S_max.COMPLETION = NORMAL',
    'S_max.CURRENT = $parameter_receive_end(S).CURRENT',
    'S_max.TODO = [TYPE_RECEIVE porigin 2]',
    '$lookup(S_max.ENV,psparam_max.NAME) = (n_max)',
    'S_max.STORE[n_max] = DEFINED (PINT 9223372036854775807)',
    r'~(n_max <- S_max.REFCELLS) /\ $heap_owners($heap_graph(S_max),HCELL n_max) = 1',
    '$default_current_cache(S_max,porigin_max) = (pdefaultcache_good)',
    'S_max.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_max,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_max) = (pdefaultcache_good)',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_min) = ({ORIGIN porigin_min,VALUE PINT $(-9223372036854775808),CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_size) = ({ORIGIN porigin_size,VALUE PINT 8,CLASS PVSCALAR})',
    '~((HCELL n_max) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_max) = 0',
    '$lookup(S_done.ENV,$ptascii("xSelected227")) = (n_first)',
    'S_done.STORE[n_first] = DEFINED (PINT 2)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

overflow = authority('maximumOverflow227') + default(1, 'later', 'PFLOAT 4890909195324358656', 'NFLOAT 4890909195324358656') + [
    'S.RESULT = KNOWN (PFLOAT 4890909195324358656)',
    '$typed_weak(["int"],PFLOAT 4890909195324358656) = TYPEREJECT',
    '$parameter_default_error_candidate(S,pfunction,1,PFLOAT 4890909195324358656)',
    'PhpStep: S ~> S_throw',
    'S_throw.COMPLETION = THROWN "TypeError" preqbytes z',
    'z = $default_parameter_line(S,porigin,1)',
    'S_throw.CURRENT = $parameter_receive_end(S).CURRENT',
    '$default_cache_at(S_throw.DEFAULTCACHE,porigin_later) = ({ORIGIN porigin_later,VALUE PFLOAT 4890909195324358656,CLASS PVSCALAR})',
    '$lookup(S_throw.ENV,psparam_later.NAME) = (n_later)',
    'S_throw.STORE[n_later] = DEFINED (PFLOAT 4890909195324358656)',
    '(HCELL n_later) <- S_throw.ALLOCATIONS',
    'S_done = $drive_steps(S_throw,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_later) = ({ORIGIN porigin_later,VALUE PFLOAT 4890909195324358656,CLASS PVSCALAR})',
    '~((HCELL n_later) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_later) = 0',
    '$lookup(S_done.ENV,$ptascii("xOverflow227")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PINT 1)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

CASES = {
    'selected-integer-default-cold-bind': {
        'source': ROWS['selected-integer-default-cold-warm']['source'],
        'stage': 'S.TODO = [DEFAULT_BIND porigin 1]',
        'checks': cold,
    },
    'selected-integer-default-overflow-bind': {
        'source': ROWS['selected-integer-default-overflow-type-errors']['source'],
        'stage': 'S.TODO = [DEFAULT_BIND porigin 1] -- if $function_at(S.FUNCTIONS,porigin) = (pfunction) -- if pfunction.NAME = $ptascii("maximumOverflow227")',
        'checks': overflow,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
