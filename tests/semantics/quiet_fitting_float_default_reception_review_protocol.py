#!/usr/bin/env python3
"""Independent raw FLOAT cache and quiet integer-formal conversion checks."""
import hashlib
import json
from pathlib import Path


def base(function_name, zero_bits):
    return [
        '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
        f'pfunction.NAME = $ptascii("{function_name}")',
        'S.CURRENT = (pcallcontext)',
        r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
        r'pcallcontext.WRAPPER = eps /\ pcallcontext.INSTANCE = eps /\ pcallcontext.LEXICAL_CLASS = eps',
        'pfunction.SIGNATURE.PARAMETERS[0] = psparam_first',
        'pfunction.SIGNATURE.PARAMETERS[1] = psparam_zero',
        'pfunction.SIGNATURE.PARAMETERS[2] = psparam_limit',
        r'psparam_first.REQUIRED /\ $ptmasks(psparam_first.TYPE) = ["int"]',
        r'~psparam_zero.REQUIRED /\ $ptmasks(psparam_zero.TYPE) = ["int"]',
        'psparam_zero.DEFAULT = PSDEFAULT expression_zero "deferred"',
        '$default_parameter_origin(S,porigin,1) = PORIGIN n_unit pcpath_zero',
        'porigin_zero = PORIGIN n_unit (pcpath_zero ++ [PCFIELD 6])',
        '$origin_node(S.SOURCES,porigin_zero) = (expression_zero)',
        '$default_at(pfunction.DEFAULTS,1) = ({INDEX 1,ORIGIN porigin_zero,KIND PDDEFERRED})',
        r'$pool_value(S.POOLS,porigin_zero) = eps /\ $compiled_read(S,porigin_zero) = eps',
        '$lossy_optional_integer_default_in(pfunction.ENV,expression_zero) = eps',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_zero) = (NFLOAT {zero_bits})',
        f'$typed_weak(["int"],PFLOAT {zero_bits}) = TYPEINTEGER (PFLOAT {zero_bits})',
        f'$float_long({zero_bits},true) = (0,eps)',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_zero) = (PFLOAT {zero_bits})',
        '$lossy_optional_integer_quiet_shape(expression_zero)',
        '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_zero)',
        '$default_cache_owner(S) = (CACHE_SHARED)',
        '$default_caches_valid(S,S.DEFAULTCACHE)',
        '$lossy_optional_integer_deferred(S,pfunction,1)',
        '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
        '$default_parameter_origin(S,porigin,2) = PORIGIN n_unit pcpath_limit',
        'porigin_limit = PORIGIN n_unit (pcpath_limit ++ [PCFIELD 6])',
        'psparam_limit.DEFAULT = PSDEFAULT expression_limit "deferred"',
        '$origin_node(S.SOURCES,porigin_limit) = (expression_limit)',
        '$default_at(pfunction.DEFAULTS,2) = ({INDEX 2,ORIGIN porigin_limit,KIND PDDEFERRED})',
        '$lossy_optional_integer_deferred(S,pfunction,2)',
        r'$call_descriptors_valid(S) /\ $heap_valid($heap_graph(S))',
    ]


def forgeries(zero_bits, other_zero):
    return [
        f'pdefaultcache_zero = {{ORIGIN porigin_zero,VALUE PFLOAT {zero_bits},CLASS PVSCALAR}}',
        'S_good = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero)]',
        '$default_caches_valid(S_good,S_good.DEFAULTCACHE)',
        '$lossy_optional_integer_deferred(S_good,pfunction,1)',
        f'S_wrong_sign = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero[.VALUE = PFLOAT {other_zero}])]',
        '$default_caches_valid(S_wrong_sign,S_wrong_sign.DEFAULTCACHE)',
        '~$lossy_optional_integer_deferred(S_wrong_sign,pfunction,1)',
        'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero[.VALUE = PINT 0])]',
        '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
        '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
        'S_wrong_class = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero[.CLASS = PVSTRING false])]',
        '~$lossy_optional_integer_deferred(S_wrong_class,pfunction,1)',
        'S_duplicate = S_good[.DEFAULTCACHE = (S_good.DEFAULTCACHE ++ [pdefaultcache_zero])]',
        '~$default_caches_valid(S_duplicate,S_duplicate.DEFAULTCACHE)',
        '~$lossy_optional_integer_deferred(S_duplicate,pfunction,1)',
        'S_unknown = S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
        '$default_cache_owner(S_unknown) = eps',
        '~$lossy_optional_integer_deferred(S_unknown,pfunction,1)',
        '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.CACHE = (CACHE_PRIVATE 0)])],pfunction,1)',
        '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
        '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
        'S.CODE = [pcode]',
        '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
        'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("INF"),$ptascii("NAN"))])]',
        '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_zero)',
    ]


cold = base('exactFloatDefaults223', 9223372036854775808) + [
    'pcallcontext.ARGC = 1',
    'pcallcontext.HOLES = eps',
    r'~psparam_first.BYREF /\ psparam_zero.BYREF /\ ~psparam_limit.BYREF',
    'S.RESULT = KNOWN (PFLOAT 9223372036854775808)',
    '$default_current_cache(S,porigin_zero) = eps',
    '$default_current_cache(S,porigin_limit) = eps',
    '$lookup(S.ENV,psparam_zero.NAME) = eps',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    'S.STORE[n_first] = DEFINED (PINT 1)',
    '$lossy_optional_integer_deferred_value(pfunction.ENV,expression_limit) = (PFLOAT 4890909195324358655)',
    '$float_long(4890909195324358655,true) = (9223372036854774784,eps)',
] + forgeries(9223372036854775808, 0) + [
    'PhpStep: S ~> S_zero',
    'S_zero.COMPLETION = NORMAL',
    r'S_zero.CURRENT = $parameter_receive_end(S).CURRENT /\ S_zero.FRAMES = S.FRAMES',
    'S_zero.PARAMETERRECEIVES = $parameter_receive_end(S).PARAMETERRECEIVES',
    'S_zero.CONSTCONTEXT = eps',
    'S_zero.TODO = [TYPE_RECEIVE porigin 2]',
    '$lookup(S_zero.ENV,psparam_zero.NAME) = (n_zero)',
    'S_zero.STORE[n_zero] = DEFINED (PINT 0)',
    r'~(n_zero <- S_zero.REFCELLS) /\ $heap_owners($heap_graph(S_zero),HCELL n_zero) = 1',
    '$default_current_cache(S_zero,porigin_zero) = ({ORIGIN porigin_zero,VALUE PFLOAT 9223372036854775808,CLASS PVSCALAR})',
    'S_zero.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_zero,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_zero) = ({ORIGIN porigin_zero,VALUE PFLOAT 9223372036854775808,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_limit) = ({ORIGIN porigin_limit,VALUE PFLOAT 4890909195324358655,CLASS PVSCALAR})',
    '~((HCELL n_zero) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_zero) = 0',
    '$lookup(S_done.ENV,$ptascii("rExact223")) = (n_result)',
    'S_done.STORE[n_result] = DEFINED (PINT 9223372036854774784)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

named = base('namedFloatDefaults223', 0) + [
    'pcallcontext.ARGC = 4',
    'pcallcontext.HOLES = [1,2]',
    r'psparam_first.BYREF /\ ~psparam_zero.BYREF /\ ~psparam_limit.BYREF',
    '$lookup(S.ENV,psparam_first.NAME) = (n_cell)',
    r'n_cell <- S.REFCELLS /\ $heap_owners($heap_graph(S),HCELL n_cell) = 2',
    'S.STORE[n_cell] = DEFINED (PFLOAT 4615063718147915776)',
    'n_bits = 4609434218613702656',
    'i = 1',
    'z = $default_parameter_line(S,porigin,0)',
    '$lossy_mixed_parameter_source_valid(S,LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    '$lossy_mixed_parameter_ready(S,0,n_cell,n_bits)',
    '$call_task_valid(S,LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z) = eps',
    '$lookup(S.ENV,psparam_zero.NAME) = (n_zero)',
    'S.STORE[n_zero] = DEFINED (PFLOAT 0)',
    '$lookup(S.ENV,psparam_limit.NAME) = (n_min)',
    'S.STORE[n_min] = DEFINED (PFLOAT 14114281232179134464)',
    '$default_current_cache(S,porigin_zero) = ({ORIGIN porigin_zero,VALUE PFLOAT 0,CLASS PVSCALAR})',
    '$default_current_cache(S,porigin_limit) = ({ORIGIN porigin_limit,VALUE PFLOAT 14114281232179134464,CLASS PVSCALAR})',
    '$lossy_optional_integer_deferred_value(pfunction.ENV,expression_limit) = (PFLOAT 14114281232179134464)',
    '$float_long(14114281232179134464,true) = ($(-9223372036854775808),eps)',
] + forgeries(0, 9223372036854775808) + [
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    'S_first.DEFAULTCACHE = S.DEFAULTCACHE',
    'PhpStep: S_first ~> S_zero',
    r'S_zero.TODO = [TYPE_RECEIVE porigin 2] /\ S_zero.STORE[n_zero] = DEFINED (PINT 0)',
    'S_zero.DEFAULTCACHE = S.DEFAULTCACHE',
    'S_zero.EVENTS = S_first.EVENTS',
    'PhpStep: S_zero ~> S_min',
    r'S_min.TODO = [TYPE_RECEIVE porigin 3] /\ S_min.STORE[n_min] = DEFINED (PINT $(-9223372036854775808))',
    'S_min.DEFAULTCACHE = S.DEFAULTCACHE',
    'S_min.EVENTS = S_zero.EVENTS',
    'S_done = $drive_steps(S_min,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_zero) = ({ORIGIN porigin_zero,VALUE PFLOAT 0,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_limit) = ({ORIGIN porigin_limit,VALUE PFLOAT 14114281232179134464,CLASS PVSCALAR})',
    '$lookup(S_done.ENV,$ptascii("xNamed223")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PINT 1)',
    '$lookup(S_done.ENV,$ptascii("zeroNamed223")) = (n_supplied)',
    'S_done.STORE[n_supplied] = DEFINED (PINT 3)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

for bits, expected in [
    ('0000000000000000', '(PFLOAT 0)'),
    ('8000000000000000', '(PFLOAT 9223372036854775808)'),
    ('43dfffffffffffff', '(PFLOAT 4890909195324358655)'),
    ('c3e0000000000000', '(PFLOAT 14114281232179134464)'),
    ('3ff0000000000000', '(PFLOAT 4607182418800017408)'),
    ('3ff8000000000000', '(PFLOAT 4609434218613702656)'),
    ('8000000000000001', '(PFLOAT 9223372036854775809)'),
    ('10000000000000000', 'eps'),
]:
    cold.append(f'$lossy_optional_integer_deferred_value($plempty(false),NScalarFloat (FLOAT "{bits}") eps) = {expected}')
cold.extend([
    '$typed_weak(["int"],PFLOAT 4609434218613702656) = TYPEINTEGER (PFLOAT 4609434218613702656)',
    '$float_long(4609434218613702656,false) = (1,eps)',
    '$float_long(4609434218613702656,true) =/= (1,eps)',
])

CATALOGUE = Path(__file__).with_name('quiet_fitting_float_default_reception_cases.json')
rows = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in rows.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
CASES = {
    'quiet-float-cold-bind': {
        'source': rows['quiet-fitting-float-default-cold-warm']['source'],
        'stage': 'S.TODO = [DEFAULT_BIND porigin 1]',
        'checks': cold,
    },
    'quiet-float-named-hole': {
        'source': rows['quiet-fitting-float-default-named-supplied']['source'],
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': named,
    },
}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
