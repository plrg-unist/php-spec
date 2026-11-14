#!/usr/bin/env python3
"""Stored Boolean/null negation retains raw pools and private receive ownership."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('literal_special_unary_minus_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

checks = [
    'S.CURRENT = (pcallcontext)',
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pcallcontext.FUNCTION = porigin',
    'pfunction.NAME = $ptascii("storedSpecialDefaults248")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_truth,psparam_falsity,psparam_nullish,psparam_nested,psparam_wrapped]',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps /\ pcallcontext.CACHE = eps',
    r'pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ psparam_truth.BYREF',
    r'~psparam_falsity.BYREF /\ ~psparam_nullish.BYREF /\ ~psparam_nested.BYREF /\ ~psparam_wrapped.BYREF',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    'S.STORE[n_first] = DEFINED (PINT 1)',
    r'~(n_first <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_first) = 1',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xStored248")) = (n_global)',
    'S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    'S.SOURCES = [pcunit_source]',
]
VALUES = [(1,'truth','$(-1)'),(2,'falsity','0'),(3,'nullish','0'),
          (4,'nested','1'),(5,'wrapped','0')]
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
for label,value,integer in [('truth','PBOOL true','1'),('falsity','PBOOL false','0'),('nullish','PNULL','0')]:
    checks.extend([
        f'expression_{label} = NExprUnaryMinus expression_{label}_child metadata_{label}',
        f'$lossy_optional_integer_special(pfunction.ENV,expression_{label}_child) = ({value})',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}_child) = eps',
        f'$coerce_number({value}) = COERCED (NINT {integer}) false',
    ])
checks.extend([
    '~$lossy_optional_integer_header(S[.SOURCES = eps],pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '~$lossy_optional_integer_header(S[.CODE = eps][.POOLS = eps],pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'S_wrong_source = S[.SOURCES = [pcunit_source[.OCCURRENCES = (PCOCCURRENCE (pcpath_truth ++ [PCFIELD 6]) expression_falsity) :: pcunit_source.OCCURRENCES]]]',
    '~$lossy_optional_integer_tail(S_wrong_source,pfunction,[psparam_truth],1)',
])
for label,value in [('boolean','PBOOL true'),('float','PFLOAT $float_of_int($(-1))'),('null','PNULL'),('integer','PINT 0')]:
    checks.extend([
        f'S_wrong_{label} = S[.POOLS = [{{UNIT n_unit,CONSTANTS ([(PCONSTANT (pcpath_truth ++ [PCFIELD 6]) ({value}))])}}]]',
        f'$compiled_read(S_wrong_{label},porigin_truth) = ({value})',
        f'~$lossy_optional_integer_tail(S_wrong_{label},pfunction,[psparam_truth],1)',
    ])
checks.extend([
    r'$heap_valid($heap_graph(S)) /\ $call_descriptors_valid(S) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$lookup(S_done.ENV,$ptascii("xStored248")) = (n_global)',
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

CASES = {'literal-special-unary-minus-stored-body-retirement': {
    'source': ROWS['literal-special-unary-minus-stored-cold-warm']['source'],
    'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin '
              '-- if $function_at(S.FUNCTIONS,porigin) = (pfunction) '
              '-- if pfunction.NAME = $ptascii("storedSpecialDefaults248") '
              '-- if S.TODO = $function_tasks(S,pfunction)'),
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
