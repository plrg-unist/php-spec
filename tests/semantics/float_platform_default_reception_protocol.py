#!/usr/bin/env python3
"""Platform-number defaults retain exact tags, caches, formals and errors."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('float_platform_default_reception_cases.json')
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
        'pfunction.SIGNATURE.PARAMETERS[0] = psparam_first',
        r'psparam_first.REQUIRED /\ psparam_first.BYREF',
        '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
        r'S.STORE[n_first] = DEFINED (PINT 1) /\ n_first <- S.REFCELLS',
        '$heap_owners($heap_graph(S),HCELL n_first) = 2',
        r'$call_descriptors_valid(S) /\ $heap_valid($heap_graph(S)) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    ]


def default(index, label, value, numeric, projection):
    return [
        f'pfunction.SIGNATURE.PARAMETERS[{index}] = psparam_{label}',
        rf'~psparam_{label}.REQUIRED /\ ~psparam_{label}.VARIADIC /\ $ptmasks(psparam_{label}.TYPE) = ["int"]',
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{label},KIND PDDEFERRED}})',
        rf'$pool_value(S.POOLS,porigin_{label}) = eps /\ $compiled_read(S,porigin_{label}) = eps',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = {projection}',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = ({numeric})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = ({value})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_{label})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'$default_current_cache(S,porigin_{label}) = eps',
        f'$lookup(S.ENV,psparam_{label}.NAME) = eps',
    ]


quiet = authority('platformDefaults231')
for index, label, value, projection in [(1, 'digits', '15', 'eps'),
                                        (2, 'epsilon', '1', '(1)'),
                                        (3, 'minimum', '3', '(3)')]:
    quiet += default(index, label, 'PINT ' + value, 'NINT ' + value, projection)
    quiet += [f'$typed_parameter_conversion(S,psparam_{label},PINT {value}) = TYPEVALUE (PINT {value})']
quiet += [
    r'psparam_digits.BYREF /\ ~psparam_epsilon.BYREF /\ ~psparam_minimum.BYREF',
    'expression_digits = NExprConstFetch name_digits metadata_digits',
    '$pnresolve(pfunction.ENV,PLCONSTANT,name_digits) = PNRESOLVED pnreference_digits',
    r'pnreference_digits.RESOLVED = $ptascii("PHP_FLOAT_DIG") /\ pnreference_digits.FALLBACK = eps',
    '$builtin_value_bytes(pnreference_digits.RESOLVED) = (PINT 15)',
    'expression_epsilon = NExprCastInt expression_epsilon_product metadata_epsilon',
    'expression_epsilon_product = NExprBinaryOpMul expression_epsilon_leaf expression_scale metadata_epsilon_product',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_epsilon_leaf) = (NFLOAT 4372995238176751616)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_scale) = (NINT 4503599627370496)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_epsilon_product) = (NFLOAT 4607182418800017408)',
    'expression_minimum = NExprCastInt expression_minimum_product metadata_minimum',
    'expression_minimum_product = NExprBinaryOpMul expression_minimum_leaf expression_maximum_leaf metadata_minimum_product',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_minimum_leaf) = (NFLOAT 4503599627370496)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_maximum_leaf) = (NFLOAT 9218868437227405311)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_minimum_product) = (NFLOAT 4616189618054758399)',
    '$builtin_value_bytes($ptascii("PHP_FLOAT_EPSILON")) = (PFLOAT 4372995238176751616)',
    '$builtin_value_bytes($ptascii("PHP_FLOAT_MIN")) = (PFLOAT 4503599627370496)',
    '$builtin_value_bytes($ptascii("PHP_FLOAT_MAX")) = (PFLOAT 9218868437227405311)',
    'S.RESULT = KNOWN (PINT 15)',
    'pdefaultcache_digits = {ORIGIN porigin_digits,VALUE PINT 15,CLASS PVSCALAR}',
    'S_good = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_digits)]',
    '$lossy_optional_integer_deferred(S_good,pfunction,1)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_digits[.VALUE = PINT 14])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,1)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_digits[.VALUE = PFLOAT 4624633867356078080])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    '~$lossy_optional_integer_deferred(S_good[.DEFAULTCACHE = (S_good.DEFAULTCACHE ++ [pdefaultcache_digits])],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    'S.CODE = [pcode]',
    '$call_name_count(pcode.NAMES,pcpath_digits ++ [PCFIELD 6]) = 1',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("PHP_FLOAT_DIG"),$ptascii("PHP_INT_SIZE"))])]',
    '$lossy_optional_integer_numeric(plenv_wrong,expression_digits) = (NINT 8)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_digits)',
    'plenv_namespace = pfunction.ENV[.NAMESPACE = $ptascii("Unresolved231")]',
    '$lossy_optional_integer_numeric(plenv_namespace,expression_digits) = eps',
    '$lossy_optional_integer_deferred_value(plenv_namespace,expression_digits) = eps',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_digits',
    'S_digits.TODO = [TYPE_RECEIVE porigin 2]',
    '$lookup(S_digits.ENV,psparam_digits.NAME) = (n_digits)',
    'S_digits.STORE[n_digits] = DEFINED (PINT 15)',
    r'~(n_digits <- S_digits.REFCELLS) /\ $heap_owners($heap_graph(S_digits),HCELL n_digits) = 1',
    '$default_current_cache(S_digits,porigin_digits) = (pdefaultcache_digits)',
    'S_digits.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_digits,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_digits) = (pdefaultcache_digits)',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_epsilon) = ({ORIGIN porigin_epsilon,VALUE PINT 1,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_minimum) = ({ORIGIN porigin_minimum,VALUE PINT 3,CLASS PVSCALAR})',
    '~((HCELL n_digits) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_digits) = 0',
    '$lookup(S_done.ENV,$ptascii("xPlatform231")) = (n_first)',
    'S_done.STORE[n_first] = DEFINED (PINT 2)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

maximum = authority('maximumDefaults231') + default(1, 'maximum', 'PFLOAT 9218868437227405311', 'NFLOAT 9218868437227405311', 'eps') + [
    'expression_maximum = NExprConstFetch name_maximum metadata_maximum',
    '$pnresolve(pfunction.ENV,PLCONSTANT,name_maximum) = PNRESOLVED pnreference_maximum',
    r'pnreference_maximum.RESOLVED = $ptascii("PHP_FLOAT_MAX") /\ pnreference_maximum.FALLBACK = eps',
    '~psparam_maximum.BYREF',
    'S.RESULT = KNOWN (PFLOAT 9218868437227405311)',
    '$typed_weak(["int"],PFLOAT 9218868437227405311) = TYPEREJECT',
    '$parameter_default_error_candidate(S,pfunction,1,PFLOAT 9218868437227405311)',
    'PhpStep: S ~> S_throw',
    'S_throw.COMPLETION = THROWN "TypeError" preqbytes z',
    'z = $default_parameter_line(S,porigin,1)',
    'S_throw.CURRENT = $parameter_receive_end(S).CURRENT',
    '$default_cache_at(S_throw.DEFAULTCACHE,porigin_maximum) = ({ORIGIN porigin_maximum,VALUE PFLOAT 9218868437227405311,CLASS PVSCALAR})',
    '$lookup(S_throw.ENV,psparam_maximum.NAME) = (n_maximum)',
    'S_throw.STORE[n_maximum] = DEFINED (PFLOAT 9218868437227405311)',
    '(HCELL n_maximum) <- S_throw.ALLOCATIONS',
    'S_throw.CONSTCONTEXT = eps',
    'S_done = $drive_steps(S_throw,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_maximum) = ({ORIGIN porigin_maximum,VALUE PFLOAT 9218868437227405311,CLASS PVSCALAR})',
    '~((HCELL n_maximum) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_maximum) = 0',
    '$lookup(S_done.ENV,$ptascii("xMaximum231")) = (n_first)',
    'S_done.STORE[n_first] = DEFINED (PINT 1)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

CASES = {
    'float-platform-quiet-cold-bind': {
        'source': ROWS['float-platform-default-quiet-cold-warm']['source'],
        'stage': 'S.TODO = [DEFAULT_BIND porigin 1]',
        'checks': quiet,
    },
    'float-platform-maximum-before-throw': {
        'source': ROWS['float-platform-default-maximum-type-error']['source'],
        'stage': 'S.TODO = [DEFAULT_BIND porigin 1]',
        'checks': maximum,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
