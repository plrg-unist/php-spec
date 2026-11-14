#!/usr/bin/env python3
"""Numeric integer powers retain exact caches and fresh BYREF default locals."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('numeric_power_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

VALUES = [('unit', 1), ('bottom', -9223372036854775808),
          ('minIdentity', -9223372036854775808), ('maxIdentity', 9223372036854775807),
          ('odd', -1), ('nested', 16), ('zero', 0)]
checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.NAME = $ptascii("powerDefaults237")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,' + ','.join('psparam_' + label for label, value in VALUES) + ']',
    r'psparam_first.REQUIRED /\ psparam_first.BYREF /\ psparam_bottom.BYREF',
    r' /\ '.join('~psparam_' + label + '.BYREF' for label, value in VALUES if label != 'bottom'),
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
for index, (label, value) in enumerate(VALUES, 1):
    number = str(value) if value >= 0 else f'$({value})'
    checks.extend([
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{label},KIND PDDEFERRED}})',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        rf'$pool_value(S.POOLS,porigin_{label}) = eps /\ $compiled_read(S,porigin_{label}) = eps',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = eps',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = (NINT {number})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = (PINT {number})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_{label})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE PINT {number},CLASS PVSCALAR}}',
    ])
checks.extend([
    'expression_bottom = NExprBinaryOpPow expression_bottom_base expression_bottom_exponent metadata_bottom',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_bottom_base) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_bottom_base) = (NINT $(-2))',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_bottom_exponent) = (NINT 63)',
    '$power_prepare(NINT $(-2),NINT 63) = POWERDONE (NINT $(-9223372036854775808)) false',
    'expression_unit = NExprBinaryOpPow expression_unit_base expression_unit_exponent metadata_unit',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_unit_base) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_unit_exponent) = (NINT 0)',
    '$power_prepare(NINT 0,NINT 0) = POWERDONE (NINT 1) false',
    'expression_odd = NExprBinaryOpPow expression_odd_base expression_odd_exponent metadata_odd',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_odd_base) = (NINT $(-1))',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_odd_exponent) = (NINT 9223372036854775807)',
    'expression_nested = NExprBinaryOpPow expression_nested_base expression_nested_exponent metadata_nested',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_nested_base) = (NINT 2)',
    'expression_nested_exponent = NExprBinaryOpPow expression_nested_left expression_nested_right metadata_nested_exponent',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_nested_exponent) = (NINT 4)',
    'expression_zero = NExprBinaryOpCoalesce expression_zero_left expression_zero_right metadata_zero',
    'expression_zero_left = NExprBinaryOpPow expression_zero_base expression_zero_exponent metadata_zero_left',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_base) = (NINT 0)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_left) = (NINT 0)',
    '$lossy_optional_integer_special(pfunction.ENV,expression_zero_left) = eps',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_zero) = (expression_zero_left)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_zero) = (false)',
    '$power_prepare(NINT 2,NINT 63) = POWERDONE (NFLOAT 4890909195324358656) false',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpPow expression_unit_base expression_bottom_exponent metadata_unit) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpPow expression_unit_base (NScalarInt (INTEGER $(-1)) metadata_unit) metadata_unit) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpPow (NScalarFloat (FLOAT "4000000000000000") metadata_unit) expression_unit_exponent metadata_unit) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpPow expression_unit_base (NScalarFloat (FLOAT "0000000000000000") metadata_unit) metadata_unit) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpPow (NScalarString (BYTES "Mg==") metadata_unit) expression_unit_exponent metadata_unit) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpPow (NExprConstFetch (NName (BYTES "RV9TVFJJQ1Q=") metadata_unit) metadata_unit) expression_unit_exponent metadata_unit) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpPow (NScalarInt (INTEGER 9223372036854775808) metadata_unit) expression_unit_exponent metadata_unit) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpPow expression_unit_base (NScalarInt (INTEGER 9223372036854775808) metadata_unit) metadata_unit) = eps',
    'expression_literal = NExprBinaryOpPow (NScalarInt (INTEGER 2) metadata_unit) (NScalarInt (INTEGER 3) metadata_unit) metadata_unit',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_literal) = (8)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_literal) = (NINT 8)',
    '~$lossy_optional_integer_quiet_shape(NExprBinaryOpCoalesce expression_unit (NExprArrayDimFetch expression_unit (NScalarInt (INTEGER 0) eps) eps) eps)',
    'S.CODE = [pcode]',
    '$call_name_count(pcode.NAMES,pcpath_bottom ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0]) = 1',
    '~$lossy_optional_integer_deferred_bindings(S[.CODE = ([pcode[.NAMES = eps]])],pfunction.ENV,porigin_bottom)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("E_WARNING"),$ptascii("E_NOTICE"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_bottom)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],2)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,2)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,2)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])],pfunction,2)',
    '$default_current_cache(S,porigin_unit) = (pdefaultcache_unit)',
    '$lookup(S.ENV,psparam_unit.NAME) = (n_unit_local)',
    r'S.STORE[n_unit_local] = DEFINED (PINT 1) /\ ~(n_unit_local <- S.REFCELLS)',
    'S.RESULT = KNOWN (PINT $(-9223372036854775808))',
    '$default_current_cache(S,porigin_bottom) = eps',
    '$lookup(S.ENV,psparam_bottom.NAME) = eps',
    'S_good = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_bottom)]',
    '$lossy_optional_integer_deferred(S_good,pfunction,2)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_bottom[.VALUE = PINT 0])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,2)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_bottom[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,2)',
    'S_duplicate = S_good[.DEFAULTCACHE = (S_good.DEFAULTCACHE ++ [pdefaultcache_bottom])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,2)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_bound',
    'S_bound.TODO = [TYPE_RECEIVE porigin 3]',
    '$lookup(S_bound.ENV,psparam_bottom.NAME) = (n_local)',
    'S_bound.STORE[n_local] = DEFINED (PINT $(-9223372036854775808))',
    r'~(n_local <- S_bound.REFCELLS) /\ $heap_owners($heap_graph(S_bound),HCELL n_local) = 1',
    '$default_current_cache(S_bound,porigin_bottom) = (pdefaultcache_bottom)',
    'S_bound.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_bound,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
])
for label, value in VALUES:
    checks.append(f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})')
checks.extend([
    '~((HCELL n_local) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_local) = 0',
    '$lookup(S_done.ENV,$ptascii("xPower237")) = (n_first)',
    'S_done.STORE[n_first] = DEFINED (PINT 2)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

CASES = {
    'numeric-power-bottom-cold-bind': {
        'source': ROWS['numeric-power-default-cold-warm']['source'],
        'stage': 'S.TODO = [DEFAULT_BIND porigin 2]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
