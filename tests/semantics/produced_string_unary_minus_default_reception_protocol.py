#!/usr/bin/env python3
"""Produced strings retain raw negation caches and genuine fractional receive authority."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import computed_boolean_operand_default_reception_protocol as prior

CATALOGUE = Path(__file__).with_name('produced_string_unary_minus_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def produced_minus():
    return [
        'expression_later = NExprUnaryMinus expression_string metadata_later',
        '~$lossy_optional_integer_selection_shape(expression_string)',
        '~$lossy_optional_integer_boolean_shape(expression_string)',
        '$lossy_optional_integer_numeric(pfunction.ENV,expression_string) = eps',
        'expression_string = NExprBinaryOpConcat expression_prefix expression_suffix metadata_string',
        '$lossy_optional_integer_string_in(pfunction.ENV,expression_prefix) = ([45,50,46])',
        '$lossy_optional_integer_string_in(pfunction.ENV,expression_suffix) = ([53])',
        '$lossy_optional_integer_string_in(pfunction.ENV,expression_string) = ([45,50,46,53])',
        '$coerce_number(PSTRING ([45,50,46,53])) = COERCED (NFLOAT 13836183955189006336) false',
        '$num_mul(NFLOAT 13836183955189006336,NINT $(-1)) = NFLOAT 4612811918334230528',
        '$typed_conversion([(PTBRANCH ([PTBUILTIN "int"]))],PFLOAT 4612811918334230528,true) = TYPEREJECT',
        '~$typed_caller_strict(S)',
    ]

cold = prior.authority('stringDefaults246', 'psparam_first,psparam_integer,psparam_zero,psparam_floating,psparam_later', 4)
cold.extend(produced_minus())
cold.extend([
    r'~psparam_first.BYREF /\ ~psparam_integer.BYREF /\ ~psparam_zero.BYREF /\ ~psparam_floating.BYREF /\ psparam_later.BYREF',
    '$call_task_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 4 n_cell n_bits i z)',
])
VALUES = [(1, 'integer', 'NINT $(-22)', 'PINT $(-22)', -22),
          (2, 'zero', 'NFLOAT 0', 'PFLOAT 0', 0),
          (3, 'floating', 'NFLOAT 9223372036854775808', 'PFLOAT 9223372036854775808', 0)]
for index, label, number, raw, integer in VALUES:
    encoded = f'$({integer})' if integer < 0 else str(integer)
    cold.extend([
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "deferred"',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = ({number})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_{label}) = ({raw})',
        f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE {raw},CLASS PVSCALAR}}',
        f'$default_current_cache(S,porigin_{label}) = (pdefaultcache_{label})',
        f'$lookup(S.ENV,psparam_{label}.NAME) = (n_local_{label})',
        f'S.STORE[n_local_{label}] = DEFINED (PINT {encoded})',
    ])
cold.extend([
    'S.CODE = [pcode]',
    '~$lossy_default_parameter_source_valid(S[.CODE = ([pcode[.NAMES = eps]])],LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 4 n_cell n_bits i z)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("E_WARNING"),$ptascii("E_ERROR"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_later)',
    'PhpStep: S ~> S_bound',
    'S_bound.TODO = $function_tasks(S,pfunction)',
    'S_bound.STORE[n_cell] = DEFINED (PINT 2)',
    r'S_bound.DEFAULTCACHE = S.DEFAULTCACHE /\ S_bound.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_bound,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_later) = (pdefaultcache_later)',
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_first) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_cell) = 0',
    '$lookup(S_done.ENV,$ptascii("xStringUnary246")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])
for index, label, number, raw, integer in VALUES:
    cold.append(f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})')

throwing = prior.authority('stringThrow246', 'psparam_first,psparam_later', 1)
throwing.extend(produced_minus())
throwing.extend([
    r'~psparam_first.BYREF /\ ~psparam_later.BYREF',
    'perrorcall.SITE = $default_parameter_origin(S,porigin,1)',
    r'perrorcall.LEVEL = 8192 /\ perrorcall.LINE = z /\ perrorcall.MESSAGE = ptbytes',
    'perrorcall.EVENT = DIAGNOSTIC "Deprecated" ptbytes z',
    '$error_call_valid(S,perrorcall)',
    '$call_task_valid(S,ERROR_HANDLER_INVOKE perrorcall)',
    '~$error_call_valid(S,perrorcall[.LEVEL = 2])',
    '~$error_call_valid(S,perrorcall[.MESSAGE = $ptascii("forged")])',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("countThrow246")) = (n_count)',
    'S.STORE[n_count] = DEFINED (PINT 1)',
    '$lookup(psymboltable_global.ENV,$ptascii("xThrow246")) = (n_global)',
    'S.STORE[n_global] = DEFINED (PFLOAT 4616752568008179712)',
    '$lookup(psymboltable_global.ENV,$ptascii("result246")) = (n_result)',
    'S.STORE[n_result] = DEFINED (PINT 99)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_later) = (pdefaultcache_later)',
    '$lookup(S_done.ENV,$ptascii("countThrow246")) = (n_count)',
    'S_done.STORE[n_count] = DEFINED (PINT 4)',
    '$lookup(S_done.ENV,$ptascii("result246")) = (n_result)',
    'S_done.STORE[n_result] = DEFINED (PINT 2)',
    '$lookup(S_done.ENV,$ptascii("xThrow246")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4616752568008179712)',
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_first) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_cell) = 0',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

CASES = {
    'produced-string-unary-minus-fractional-reference-resume': {
        'source': ROWS['produced-string-unary-minus-cold-warm']['source'],
        'stage': 'S.TODO = [LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 4 n_cell n_bits i z]',
        'checks': cold,
    },
    'produced-string-unary-minus-fractional-throw-retry': {
        'source': ROWS['produced-string-unary-minus-fractional-handler-throw-retry']['source'],
        'stage': 'S.TODO = [ERROR_HANDLER_INVOKE perrorcall] -- if perrorcall.RESUME = LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 1 n_cell n_bits i z',
        'checks': throwing,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE, Path(prior.__file__), prior.CATALOGUE), runner_flags=('--sl',))
