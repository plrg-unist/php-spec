#!/usr/bin/env python3
"""Stored integer-string certificates retain compiled reads and private ownership."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('integer_string_unary_minus_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    'S.CURRENT = (pcallcontext)',
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pcallcontext.FUNCTION = porigin',
    'pfunction.NAME = $ptascii("storedStringDefaults247")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_integer,psparam_zero,psparam_nested,psparam_wrapped]',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps /\ pcallcontext.CACHE = eps',
    r'pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ psparam_integer.BYREF',
    r'~psparam_zero.BYREF /\ ~psparam_nested.BYREF /\ ~psparam_wrapped.BYREF',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    'S.STORE[n_first] = DEFINED (PINT 1)',
    r'~(n_first <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_first) = 1',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xStored247")) = (n_global)',
    'S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    'S.SOURCES = [pcunit_source]',
]
VALUES = [(1,'integer','$(-22)'),(2,'zero','0'),(3,'nested','22'),(4,'wrapped','$(-22)')]
for index,label,integer in VALUES:
    checks.extend([
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "int"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{label},KIND PDSTORED}})',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = ({integer})',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = (NINT {integer})',
        f'$compiled_read(S,porigin_{label}) = (PINT {integer})',
        f'$default_current_cache(S,porigin_{label}) = eps',
        f'$lookup(S.ENV,psparam_{label}.NAME) = (n_local_{label})',
        f'S.STORE[n_local_{label}] = DEFINED (PINT {integer})',
        rf'~(n_local_{label} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_local_{label}) = 1',
    ])
checks.extend([
    'expression_integer = NExprUnaryMinus expression_integer_string metadata_integer',
    '$lossy_optional_integer_quiet_shape(expression_integer_string)',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_integer_string) = ([50,50])',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_integer_string) = eps',
    '$coerce_number(PSTRING ([50,50])) = COERCED (NINT 22) false',
    'expression_zero = NExprUnaryMinus expression_zero_string metadata_zero',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_zero_string) = ([45,48])',
    '$coerce_number(PSTRING ([45,48])) = COERCED (NINT 0) false',
    'expression_nested = NExprUnaryMinus expression_nested_child metadata_nested',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_nested_child) = ($(-22))',
    'expression_wrapped = NExprUnaryPlus expression_wrapped_child metadata_wrapped',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_wrapped_child) = ($(-22))',
    '~$lossy_optional_integer_header(S[.SOURCES = eps],pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '~$lossy_optional_integer_header(S[.CODE = eps][.POOLS = eps],pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'pcpath_default = pcpath_integer ++ [PCFIELD 6]',
    'S_wrong_source = S[.SOURCES = [pcunit_source[.OCCURRENCES = (PCOCCURRENCE pcpath_default expression_zero) :: pcunit_source.OCCURRENCES]]]',
    '~$lossy_optional_integer_header(S_wrong_source,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$lookup(S_done.ENV,$ptascii("xStored247")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'~((HCELL n_first) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_first) = 0',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])
for index,label,integer in VALUES:
    checks.extend([
        f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = eps',
        f'$compiled_read(S_done,porigin_{label}) = (PINT {integer})',
        rf'~((HCELL n_local_{label}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_local_{label}) = 0',
    ])

CASES = {'integer-string-unary-minus-stored-body-retirement': {
    'source': ROWS['integer-string-unary-minus-stored-cold-warm']['source'],
    'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin '
              '-- if $function_at(S.FUNCTIONS,porigin) = (pfunction) '
              '-- if pfunction.NAME = $ptascii("storedStringDefaults247") '
              '-- if S.TODO = $function_tasks(S,pfunction)'),
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
