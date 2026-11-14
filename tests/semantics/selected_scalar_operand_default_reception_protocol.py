#!/usr/bin/env python3
"""Selected scalar defaults retain raw caches through reference and throw reception."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import computed_boolean_operand_default_reception_protocol as prior

CATALOGUE = Path(__file__).with_name('selected_scalar_operand_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

cold = prior.authority('selectionDefaults243', 'psparam_first,psparam_sum,psparam_falseLeft,psparam_nullLeft,psparam_power,psparam_later', 5)
cold.extend([
    r'~psparam_first.BYREF /\ ~psparam_sum.BYREF /\ ~psparam_falseLeft.BYREF /\ ~psparam_nullLeft.BYREF /\ ~psparam_power.BYREF /\ psparam_later.BYREF',
    '$call_task_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 5 n_cell n_bits i z)',
    'expression_later = NExprBinaryOpPlus expression_selected expression_zero metadata_later',
    'expression_selected = NExprTernary expression_condition expression_string expression_false metadata_selection',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_selected) = eps',
    '$lossy_optional_integer_selection_shape(expression_selected)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_condition) = (true)',
    '$lossy_optional_integer_special(pfunction.ENV,expression_false) = (PBOOL false)',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_selected) = (expression_string)',
    'expression_string =/= expression_selected',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_string) = ([50,46,53])',
    '$lossy_optional_integer_quiet_operand(pfunction.ENV,expression_selected) = (NFLOAT 4612811918334230528)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero) = (NINT 0)',
    '$number_binary(ADD,NFLOAT 4612811918334230528,NINT 0) = NUM (NFLOAT 4612811918334230528)',
])
VALUES = [(1, 'sum', 'NINT 3', 'PINT 3', 3),
          (2, 'falseLeft', 'NINT 2', 'PINT 2', 2),
          (3, 'nullLeft', 'NFLOAT 4616189618054758400', 'PFLOAT 4616189618054758400', 4),
          (4, 'power', 'NINT 2', 'PINT 2', 2)]
for index, label, number, raw, integer in VALUES:
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
        f'S.STORE[n_local_{label}] = DEFINED (PINT {integer})',
    ])
cold.extend([
    'S.CODE = [pcode]',
    '~$lossy_default_parameter_source_valid(S[.CODE = ([pcode[.NAMES = eps]])],LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 5 n_cell n_bits i z)',
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
    '$lookup(S_done.ENV,$ptascii("xSelection243")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])
for index, label, number, raw, integer in VALUES:
    cold.append(f'$default_cache_at(S_done.DEFAULTCACHE,porigin_{label}) = (pdefaultcache_{label})')

throwing = prior.authority('selectionThrow243', 'psparam_first,psparam_later', 1)
throwing.extend([
    r'~psparam_first.BYREF /\ ~psparam_later.BYREF',
    'expression_later = NExprBinaryOpDiv expression_selected expression_base metadata_later',
    'expression_selected = NExprTernary expression_condition expression_string expression_false metadata_selection',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_selected) = eps',
    '$lossy_optional_integer_cast_leaf(pfunction.ENV,expression_selected) = (expression_string)',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_string) = ([53])',
    '$lossy_optional_integer_quiet_operand(pfunction.ENV,expression_selected) = (NINT 5)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_base) = (NINT 2)',
    '$number_binary(DIVIDE,NINT 5,NINT 2) = NUM (NFLOAT 4612811918334230528)',
    'perrorcall.SITE = $default_parameter_origin(S,porigin,1)',
    r'perrorcall.LEVEL = 8192 /\ perrorcall.LINE = z /\ perrorcall.MESSAGE = ptbytes',
    'perrorcall.EVENT = DIAGNOSTIC "Deprecated" ptbytes z',
    '$error_call_valid(S,perrorcall)',
    '$call_task_valid(S,ERROR_HANDLER_INVOKE perrorcall)',
    '~$error_call_valid(S,perrorcall[.LEVEL = 2])',
    '~$error_call_valid(S,perrorcall[.MESSAGE = $ptascii("forged")])',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("countThrow243")) = (n_count)',
    'S.STORE[n_count] = DEFINED (PINT 1)',
    '$lookup(psymboltable_global.ENV,$ptascii("xThrow243")) = (n_global)',
    'S.STORE[n_global] = DEFINED (PFLOAT 4616752568008179712)',
    '$lookup(psymboltable_global.ENV,$ptascii("result243")) = (n_result)',
    'S.STORE[n_result] = DEFINED (PINT 99)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_later) = (pdefaultcache_later)',
    '$lookup(S_done.ENV,$ptascii("countThrow243")) = (n_count)',
    'S_done.STORE[n_count] = DEFINED (PINT 4)',
    '$lookup(S_done.ENV,$ptascii("result243")) = (n_result)',
    'S_done.STORE[n_result] = DEFINED (PINT 2)',
    '$lookup(S_done.ENV,$ptascii("xThrow243")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4616752568008179712)',
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_first) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_cell) = 0',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

CASES = {
    'selected-scalar-operand-fractional-reference-resume': {
        'source': ROWS['selected-scalar-operand-default-cold-warm']['source'],
        'stage': 'S.TODO = [LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 5 n_cell n_bits i z]',
        'checks': cold,
    },
    'selected-scalar-operand-fractional-throw-retry': {
        'source': ROWS['selected-scalar-operand-default-fractional-handler-throw-retry']['source'],
        'stage': 'S.TODO = [ERROR_HANDLER_INVOKE perrorcall] -- if perrorcall.RESUME = LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 1 n_cell n_bits i z',
        'checks': throwing,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE, Path(prior.__file__), prior.CATALOGUE), runner_flags=('--sl',))
