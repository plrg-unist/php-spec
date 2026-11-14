#!/usr/bin/env python3
"""Numeric modulo and shift defaults retain exact caches and fresh BYREF locals."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('numeric_integer_operator_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

VALUES = [('mod', 7), ('left', -2), ('right', -1), ('wideLeft', 0),
          ('wideRight', -1), ('boundary', 0), ('small', -2), ('zero', 0)]
checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.NAME = $ptascii("integerOperators236")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,' + ','.join('psparam_' + label for label, value in VALUES) + ']',
    r'psparam_first.REQUIRED /\ psparam_first.BYREF /\ psparam_left.BYREF',
    r' /\ '.join('~psparam_' + label + '.BYREF' for label, value in VALUES if label != 'left'),
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
    'expression_mod = NExprBinaryOpMod expression_mod_left expression_mod_right metadata_mod',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_mod_left) = (NINT 30719)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_mod_right) = (NINT 8)',
    'expression_left = NExprBinaryOpShiftLeft expression_left_value expression_left_count metadata_left',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_left_value) = (NINT 9223372036854775807)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_left_count) = (NINT 1)',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_left_value) = eps',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_left_count) = eps',
    'expression_boundary = NExprBinaryOpMod expression_boundary_left expression_boundary_right metadata_boundary',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_boundary_left) = (NINT $(-9223372036854775808))',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_boundary_right) = (NINT $(-1))',
    'expression_small = NExprBinaryOpShiftRight expression_small_left expression_small_right metadata_small',
    'expression_small_left = NExprBitwiseNot expression_small_not metadata_small_not',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_small_not) = (NINT 2)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_small_left) = (NINT $(-3))',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_small_right) = (NINT 1)',
    'expression_zero = NExprBinaryOpCoalesce expression_zero_left expression_zero_right metadata_zero',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero_left) = (NINT 0)',
    '$lossy_optional_integer_special(pfunction.ENV,expression_zero_left) = eps',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_zero) = (expression_zero_left)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_zero) = (false)',
    'S.CODE = [pcode]',
    '$call_name_count(pcode.NAMES,pcpath_left ++ [PCFIELD 6,PCFIELD 1]) = 1',
    '~$lossy_optional_integer_deferred_bindings(S[.CODE = ([pcode[.NAMES = eps]])],pfunction.ENV,porigin_left)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("PHP_INT_MAX"),$ptascii("PHP_INT_MIN"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_left)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],2)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,2)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,2)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])],pfunction,2)',
    '$default_current_cache(S,porigin_mod) = (pdefaultcache_mod)',
    '$lookup(S.ENV,psparam_mod.NAME) = (n_mod)',
    r'S.STORE[n_mod] = DEFINED (PINT 7) /\ ~(n_mod <- S.REFCELLS)',
    'S.RESULT = KNOWN (PINT $(-2))',
    '$default_current_cache(S,porigin_left) = eps',
    '$lookup(S.ENV,psparam_left.NAME) = eps',
    'S_good = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_left)]',
    '$lossy_optional_integer_deferred(S_good,pfunction,2)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_left[.VALUE = PINT $(-1)])]',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,2)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_left[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,2)',
    'S_duplicate = S_good[.DEFAULTCACHE = (S_good.DEFAULTCACHE ++ [pdefaultcache_left])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,2)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_bound',
    'S_bound.TODO = [TYPE_RECEIVE porigin 3]',
    '$lookup(S_bound.ENV,psparam_left.NAME) = (n_local)',
    'S_bound.STORE[n_local] = DEFINED (PINT $(-2))',
    r'~(n_local <- S_bound.REFCELLS) /\ $heap_owners($heap_graph(S_bound),HCELL n_local) = 1',
    '$default_current_cache(S_bound,porigin_left) = (pdefaultcache_left)',
    'S_bound.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_bound,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
])
for label, value in VALUES:
    checks.append(f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})')
checks.extend([
    '~((HCELL n_local) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_local) = 0',
    '$lookup(S_done.ENV,$ptascii("xOperator236")) = (n_first)',
    'S_done.STORE[n_first] = DEFINED (PINT 2)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

for operator, value in [('Mod', 1), ('ShiftLeft', 6), ('ShiftRight', 1)]:
    literal = f'NExprBinaryOp{operator} (NScalarInt (INTEGER 3) metadata_left) (NScalarInt (INTEGER 2) metadata_left) metadata_left'
    if operator != 'Mod':
        literal = literal.replace('INTEGER 2', 'INTEGER 1')
    checks.extend([
        f'$lossy_optional_integer_default_in(pfunction.ENV,{literal}) = ({value})',
        f'$lossy_optional_integer_numeric(pfunction.ENV,{literal}) = (NINT {value})',
    ])
    for child in ['NScalarFloat (FLOAT "4000000000000000") metadata_left',
                  'NScalarString (BYTES "Mg==") metadata_left',
                  'NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_left) metadata_left',
                  'NExprConstFetch (NName (BYTES "bnVsbA==") metadata_left) metadata_left',
                  'NScalarInt (INTEGER 9223372036854775808) metadata_left',
                  'NExprBinaryOpPlus expression_left_value (NScalarInt (INTEGER 1) metadata_left) metadata_left']:
        checks.append(f'$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOp{operator} ({child}) expression_left_count metadata_left) = eps')
    for count in ['NScalarFloat (FLOAT "4000000000000000") metadata_left',
                  'NScalarString (BYTES "Mg==") metadata_left']:
        checks.append(f'$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOp{operator} expression_left_value ({count}) metadata_left) = eps')
checks.extend([
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpMod expression_left_value (NScalarInt (INTEGER 0) metadata_left) metadata_left) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpShiftLeft expression_left_value (NExprUnaryMinus (NScalarInt (INTEGER 1) metadata_left) metadata_left) metadata_left) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,NExprBinaryOpShiftRight expression_left_value (NExprUnaryMinus (NScalarInt (INTEGER 1) metadata_left) metadata_left) metadata_left) = eps',
])

CASES = {
    'numeric-integer-operator-left-cold-bind': {
        'source': ROWS['numeric-integer-operator-default-cold-warm']['source'],
        'stage': 'S.TODO = [DEFAULT_BIND porigin 2]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
