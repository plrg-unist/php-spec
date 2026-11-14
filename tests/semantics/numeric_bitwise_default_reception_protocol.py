#!/usr/bin/env python3
"""Numeric bitwise defaults retain exact signed64 caches and fresh BYREF locals."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('numeric_bitwise_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

VALUES = [('and', 0), ('or', 8194), ('xor', 0),
          ('notMax', -9223372036854775808), ('notMin', 9223372036854775807),
          ('signed', -9223372036854775806), ('zero', 0)]
checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.NAME = $ptascii("bitwiseDefaults235")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,' + ','.join('psparam_' + label for label, value in VALUES) + ']',
    r'psparam_first.REQUIRED /\ psparam_first.BYREF /\ psparam_or.BYREF',
    r' /\ '.join('~psparam_' + label + '.BYREF' for label, value in VALUES if label != 'or'),
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
    'expression_or = NExprBinaryOpBitwiseOr expression_or_left expression_or_right metadata_or',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_or_left) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_or_right) = (NINT 8192)',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_or_left) = eps',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_or_right) = eps',
    'expression_and = NExprBinaryOpBitwiseAnd expression_and_left expression_and_right metadata_and',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_and_left) = (NINT $(-9223372036854775808))',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_and_right) = (NINT 9223372036854775807)',
    'expression_notMax = NExprBitwiseNot expression_notMax_child metadata_notMax',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_notMax_child) = (NINT 9223372036854775807)',
    'expression_notMin = NExprBitwiseNot expression_notMin_child metadata_notMin',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_notMin_child) = (NINT $(-9223372036854775808))',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpBitwiseOr (NScalarFloat (FLOAT "4000000000000000") metadata_or) expression_or_right metadata_or) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpBitwiseOr (NScalarString (BYTES "Mg==") metadata_or) expression_or_right metadata_or) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpBitwiseOr (NExprConstFetch (NName (BYTES "RV9TVFJJQ1Q=") metadata_or) metadata_or) expression_or_right metadata_or) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpBitwiseOr (NScalarInt (INTEGER 9223372036854775808) metadata_or) expression_or_right metadata_or) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBitwiseNot (NScalarFloat (FLOAT "4000000000000000") metadata_or) metadata_or) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBitwiseNot (NScalarInt (INTEGER 9223372036854775808) metadata_or) metadata_or) = eps',
    'expression_literal = NExprBinaryOpBitwiseOr (NScalarInt (INTEGER 1) metadata_or) (NScalarInt (INTEGER 2) metadata_or) metadata_or',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_literal) = (3)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_literal) = (NINT 3)',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBitwiseNot (NScalarInt (INTEGER 1) metadata_or) metadata_or) = (NINT $(-2))',
    'expression_zero = NExprBinaryOpCoalesce expression_zero_left expression_zero_right metadata_zero',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_left) = (NINT 0)',
    '$lossy_optional_integer_special(pfunction.ENV,expression_zero_left) = eps',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_zero) = (expression_zero_left)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_zero) = (false)',
    'S.CODE = [pcode]',
    '$call_name_count(pcode.NAMES,pcpath_or ++ [PCFIELD 6,PCFIELD 1]) = 1',
    '~$lossy_optional_integer_deferred_bindings(S[.CODE = ([pcode[.NAMES = eps]])],pfunction.ENV,porigin_or)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("E_WARNING"),$ptascii("E_NOTICE"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_or)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],2)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,2)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,2)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])],pfunction,2)',
    '$default_current_cache(S,porigin_and) = (pdefaultcache_and)',
    '$lookup(S.ENV,psparam_and.NAME) = (n_and)',
    r'S.STORE[n_and] = DEFINED (PINT 0) /\ ~(n_and <- S.REFCELLS)',
    'S.RESULT = KNOWN (PINT 8194)',
    '$default_current_cache(S,porigin_or) = eps',
    '$lookup(S.ENV,psparam_or.NAME) = eps',
    'S_good = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_or)]',
    '$lossy_optional_integer_deferred(S_good,pfunction,2)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_or[.VALUE = PINT 8195])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,2)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_or[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,2)',
    'S_duplicate = S_good[.DEFAULTCACHE = (S_good.DEFAULTCACHE ++ [pdefaultcache_or])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,2)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_bound',
    'S_bound.TODO = [TYPE_RECEIVE porigin 3]',
    '$lookup(S_bound.ENV,psparam_or.NAME) = (n_local)',
    'S_bound.STORE[n_local] = DEFINED (PINT 8194)',
    r'~(n_local <- S_bound.REFCELLS) /\ $heap_owners($heap_graph(S_bound),HCELL n_local) = 1',
    '$default_current_cache(S_bound,porigin_or) = (pdefaultcache_or)',
    'S_bound.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_bound,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
])
for label, value in VALUES:
    checks.append(f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})')
checks.extend([
    '~((HCELL n_local) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_local) = 0',
    '$lookup(S_done.ENV,$ptascii("xBitwise235")) = (n_first)',
    'S_done.STORE[n_first] = DEFINED (PINT 2)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

CASES = {
    'numeric-bitwise-or-cold-bind': {
        'source': ROWS['numeric-bitwise-default-cold-warm']['source'],
        'stage': 'S.TODO = [DEFAULT_BIND porigin 2]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
