#!/usr/bin/env python3
"""Completed FLOAT powers keep raw caches before integer reception or rejection."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('numeric_float_power_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

VALUES = [('unit', 4607182418800017408, 1), ('negativeZero', 9223372036854775808, 0),
          ('zero', 0, 0), ('nested', 4607182418800017408, 1), ('positiveZero', 0, 0)]
checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.NAME = $ptascii("floatPowerDefaults238")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,' + ','.join('psparam_' + label for label, bits, integer in VALUES) + ']',
    r'psparam_first.REQUIRED /\ psparam_first.BYREF /\ psparam_negativeZero.BYREF',
    r' /\ '.join('~psparam_' + label + '.BYREF' for label, bits, integer in VALUES if label != 'negativeZero'),
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
for index, (label, bits, integer) in enumerate(VALUES, 1):
    checks.extend([
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{label},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        rf'$pool_value(S.POOLS,porigin_{label}) = eps /\ $compiled_read(S,porigin_{label}) = eps',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = eps',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = (NFLOAT {bits})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = (PFLOAT {bits})',
        f'$typed_weak(["int"],PFLOAT {bits}) = TYPEINTEGER (PFLOAT {bits})',
        f'$float_long({bits},true) = ({integer},eps)',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_{label})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE PFLOAT {bits},CLASS PVSCALAR}}',
    ])
checks.extend([
    'expression_negativeZero = NExprBinaryOpPow expression_negativeZero_base expression_one metadata_negativeZero',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_negativeZero_base) = (NFLOAT 9223372036854775808)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_one) = (NINT 1)',
    '$power_prepare(NFLOAT 9223372036854775808,NINT 1) = POWERDONE (NFLOAT 9223372036854775808) false',
    'expression_unit = NExprBinaryOpPow expression_nan expression_unit_exponent metadata_unit',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_nan) = (NFLOAT 9221120237041090560)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_unit_exponent) = (NINT 0)',
    'expression_nested = NExprBinaryOpPow expression_nested_base expression_nested_exponent metadata_nested',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_nested_base) = (NFLOAT 4607182418800017408)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_nested_exponent) = (NINT 0)',
    'expression_zero = NExprBinaryOpPow expression_infinity expression_negative_one metadata_zero',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_infinity) = (NFLOAT 9218868437227405312)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_negative_one) = (NINT $(-1))',
    '$power_warning_number($number_value(NINT 9223372036854775807)) = (NINT 9223372036854775807)',
    '$power_warning_number($number_value(NFLOAT 18446744073709551615)) = (NFLOAT 18446744073709551615)',
    '$power_warning_number($number_value(NFLOAT 18446744073709551616)) = eps',
    '$power_warning_number($number_value(NINT 9223372036854775808)) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpPow (NScalarFloat (FLOAT "10000000000000000") metadata_unit) expression_unit_exponent metadata_unit) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpPow expression_one (NScalarFloat (FLOAT "10000000000000000") metadata_unit) metadata_unit) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpPow expression_one expression_negative_one metadata_unit) = (NFLOAT 4607182418800017408)',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpPow (NScalarFloat (FLOAT "0000000000000000") metadata_unit) expression_negative_one metadata_unit) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpPow (NScalarString (BYTES "Mg==") metadata_unit) expression_unit_exponent metadata_unit) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpPow (NExprConstFetch (NName (BYTES "RV9TVFJJQ1Q=") metadata_unit) metadata_unit) expression_unit_exponent metadata_unit) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpPow (NScalarInt (INTEGER 9223372036854775808) metadata_unit) expression_unit_exponent metadata_unit) = eps',
    '~$lossy_optional_integer_quiet_shape(NExprBinaryOpCoalesce expression_unit (NExprArrayDimFetch expression_unit (NScalarInt (INTEGER 0) eps) eps) eps)',
    'S.CODE = [pcode]',
    '$call_name_count(pcode.NAMES,pcpath_negativeZero ++ [PCFIELD 6,PCFIELD 1]) = 1',
    '~$lossy_optional_integer_deferred_bindings(S[.CODE = ([pcode[.NAMES = eps]])],pfunction.ENV,porigin_negativeZero)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("E_ERROR"),$ptascii("E_WARNING"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_negativeZero)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],2)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,2)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,2)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])],pfunction,2)',
    '$default_current_cache(S,porigin_unit) = (pdefaultcache_unit)',
    '$lookup(S.ENV,psparam_unit.NAME) = (n_unit_local)',
    r'S.STORE[n_unit_local] = DEFINED (PINT 1) /\ ~(n_unit_local <- S.REFCELLS)',
    'S.RESULT = KNOWN (PFLOAT 9223372036854775808)',
    '$default_current_cache(S,porigin_negativeZero) = eps',
    '$lookup(S.ENV,psparam_negativeZero.NAME) = eps',
    'S_good = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_negativeZero)]',
    '$lossy_optional_integer_deferred(S_good,pfunction,2)',
    'S_wrong_sign = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_negativeZero[.VALUE = PFLOAT 0])]',
    '~$lossy_optional_integer_deferred(S_wrong_sign,pfunction,2)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_negativeZero[.VALUE = PINT 0])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,2)',
    'S_duplicate = S_good[.DEFAULTCACHE = (S_good.DEFAULTCACHE ++ [pdefaultcache_negativeZero])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,2)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_bound',
    'S_bound.TODO = [TYPE_RECEIVE porigin 3]',
    '$lookup(S_bound.ENV,psparam_negativeZero.NAME) = (n_local)',
    'S_bound.STORE[n_local] = DEFINED (PINT 0)',
    r'~(n_local <- S_bound.REFCELLS) /\ $heap_owners($heap_graph(S_bound),HCELL n_local) = 1',
    '$default_current_cache(S_bound,porigin_negativeZero) = (pdefaultcache_negativeZero)',
    'S_bound.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_bound,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
])
for label, bits, integer in VALUES:
    checks.append(f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})')
checks.extend([
    '~((HCELL n_local) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_local) = 0',
    '$lookup(S_done.ENV,$ptascii("xFloatPower238")) = (n_first)',
    'S_done.STORE[n_first] = DEFINED (PINT 2)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

# These three previously EPS helpers change under the new NFLOAT completion arm.
def constant(name):
    import base64
    return f'NExprConstFetch (NName (BYTES "{base64.b64encode(name.encode()).decode()}") eps) eps'


base = constant('E_WARNING')
for left, right, bits in [
        (base, 'NScalarInt (INTEGER 63) eps', 4890909195324358656),
        ('NScalarFloat (FLOAT "4000000000000000") eps', 'NScalarInt (INTEGER 0) eps', 4607182418800017408),
        (base, 'NScalarFloat (FLOAT "0000000000000000") eps', 4607182418800017408)]:
    checks.append(f'$lossy_optional_integer_numeric($plempty(false),NExprBinaryOpPow ({left}) ({right}) eps) = (NFLOAT {bits})')

nan_checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.NAME = $ptascii("defaults238")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_later]',
    'psparam_later.DEFAULT = PSDEFAULT expression_later "deferred"',
    '$default_parameter_origin(S,porigin,1) = PORIGIN n_unit pcpath_later',
    'porigin_later = PORIGIN n_unit (pcpath_later ++ [PCFIELD 6])',
    '$origin_node(S.SOURCES,porigin_later) = (expression_later)',
    '$default_at(pfunction.DEFAULTS,1) = ({INDEX 1,ORIGIN porigin_later,KIND PDDEFERRED})',
    r'$pool_value(S.POOLS,porigin_later) = eps /\ $compiled_read(S,porigin_later) = eps',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_later) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_later) = (NFLOAT 18444492273895866368)',
    '$lossy_optional_integer_deferred_value(pfunction.ENV,expression_later) = (PFLOAT 18444492273895866368)',
    '$typed_weak(["int"],PFLOAT 18444492273895866368) = TYPEREJECT',
    '$lossy_optional_integer_deferred(S,pfunction,1)',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$default_current_cache(S,porigin_later) = eps',
    '$lookup(S.ENV,psparam_later.NAME) = eps',
    'S.RESULT = KNOWN (PFLOAT 18444492273895866368)',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps /\ pcallcontext.CACHE = eps',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    r'S.STORE[n_first] = DEFINED (PINT 1) /\ ~(n_first <- S.REFCELLS)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'pdefaultcache_later = {ORIGIN porigin_later,VALUE PFLOAT 18444492273895866368,CLASS PVSCALAR}',
    'S_good = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_later)]',
    '$lossy_optional_integer_deferred(S_good,pfunction,1)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_later[.VALUE = PINT 0])]',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_error',
    'S_error.COMPLETION = THROWN "TypeError" preqbytes_error z_error',
    'z_error = $default_parameter_line(S,porigin,1)',
    '$lookup(S_error.ENV,psparam_later.NAME) = (n_later)',
    'S_error.STORE[n_later] = DEFINED (PFLOAT 18444492273895866368)',
    '$default_current_cache(S_error,porigin_later) = (pdefaultcache_later)',
    'S_error.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_error,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_later) = (pdefaultcache_later)',
    '~((HCELL n_first) <- S_done.ALLOCATIONS)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

CASES = {
    'numeric-float-power-negative-zero-cold-bind': {
        'source': ROWS['numeric-float-power-default-cold-warm']['source'],
        'stage': 'S.TODO = [DEFAULT_BIND porigin 2]',
        'checks': checks,
    },
    'numeric-float-power-nan-type-error-bind': {
        'source': ROWS['numeric-float-power-default-nan-type-error']['source'],
        'stage': 'S.TODO = [DEFAULT_BIND porigin 1]',
        'checks': nan_checks,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
