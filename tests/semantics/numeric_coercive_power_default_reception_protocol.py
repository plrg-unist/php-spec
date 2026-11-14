#!/usr/bin/env python3
"""Quiet string power conversion precedes fractional reception and throwing callbacks."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('numeric_coercive_power_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

TASK = 'LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 1 n_cell n_bits i z'


throwing = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.NAME = $ptascii("coerciveThrow240")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_later]',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps /\ pcallcontext.CACHE = eps',
    r'pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
    '$parameter_receive_owner(S.CURRENT) = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    'psparam_later.DEFAULT = PSDEFAULT expression_later "deferred"',
    '$default_parameter_origin(S,porigin,1) = PORIGIN n_unit pcpath_later',
    'porigin_later = PORIGIN n_unit (pcpath_later ++ [PCFIELD 6])',
    '$default_at(pfunction.DEFAULTS,1) = ({INDEX 1,ORIGIN porigin_later,KIND PDDEFERRED})',
    '$origin_node(S.SOURCES,porigin_later) = (expression_later)',
    r'$pool_value(S.POOLS,porigin_later) = eps /\ $compiled_read(S,porigin_later) = eps',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_later) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_later) = (NFLOAT 4602678819172646912)',
    '$lossy_optional_integer_deferred_value(pfunction.ENV,expression_later) = (PFLOAT 4602678819172646912)',
    'expression_later = NExprBinaryOpPow expression_string expression_half metadata_later',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_string) = eps',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_string) = ([48,46,50,53])',
    '$coerce_number(PSTRING ([48,46,50,53])) = COERCED (NFLOAT 4598175219545276416) false',
    '$lossy_optional_integer_power_operand(pfunction.ENV,expression_string) = (NFLOAT 4598175219545276416)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_half) = (NFLOAT 4602678819172646912)',
    '$lossy_optional_integer_power_operand(pfunction.ENV,expression_half) = (NFLOAT 4602678819172646912)',
    '$power_prepare(NFLOAT 4598175219545276416,NFLOAT 4602678819172646912) = POWERGENERAL 4607182418800017408 4598175219545276416 4602678819172646912 0 false',
    '$num_pow(NFLOAT 4598175219545276416,NFLOAT 4602678819172646912) = (NFLOAT 4602678819172646912,false)',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_later)',
    '$lossy_optional_integer_deferred(S,pfunction,1)',
    'pdefaultcache_later = {ORIGIN porigin_later,VALUE PFLOAT 4602678819172646912,CLASS PVSCALAR}',
    '$default_current_cache(S,porigin_later) = (pdefaultcache_later)',
    r'n_bits = 4602678819172646912 /\ i = 0',
    '$lossy_parameter_snapshot(n_bits) = ((i,ptbytes))',
    'z = $default_parameter_line(S,porigin,1)',
    'S.ORIGIN = ($default_parameter_origin(S,porigin,1))',
    '$lookup(S.ENV,psparam_later.NAME) = (n_cell)',
    'S.STORE[n_cell] = DEFINED (PFLOAT n_bits)',
    r'(HCELL n_cell) <- S.ALLOCATIONS /\ ~(n_cell <- S.REFCELLS)',
    '$heap_owners($heap_graph(S),HCELL n_cell) = 1',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    r'S.STORE[n_first] = DEFINED (PINT 1) /\ ~(n_first <- S.REFCELLS)',
    '$lossy_default_parameter_context(S,pfunction,1,n_bits,z)',
    '$lossy_parameter_ready(S,n_cell,n_bits)',
    '$lossy_default_parameter_source_valid(S,' + TASK + ')',
    '$task_nodes(' + TASK + ') = eps',
    '~$lossy_default_parameter_source_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 1 n_cell n_bits 1 z)',
    '~$lossy_default_parameter_source_valid(S,LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 1 n_cell n_bits i $(z + 100))',
    '~$lossy_default_parameter_source_valid(S[.SOURCES = eps],' + TASK + ')',
    '~$lossy_default_parameter_source_valid(S[.FUNCTIONS = eps],' + TASK + ')',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_later[.VALUE = PINT 0])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_default_parameter_source_valid(S_wrong_tag,' + TASK + ')',
    'S_wrong_bits = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_later[.VALUE = PFLOAT 4609434218613702656])]',
    '~$lossy_default_parameter_source_valid(S_wrong_bits,' + TASK + ')',
    '~$lossy_parameter_ready(S[.STORE[n_cell] = DEFINED (PINT 0)],n_cell,n_bits)',
    '~$lossy_parameter_ready(S[.REFCELLS = S.REFCELLS ++ [n_cell]],n_cell,n_bits)',
    r'$call_descriptors_valid(S) /\ $heap_valid($heap_graph(S)) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
]

def constant(name):
    return f'NExprConstFetch (NName (BYTES "{base64.b64encode(name.encode()).decode()}") eps) eps'

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
    '$lookup(psymboltable_global.ENV,$ptascii("countThrow240")) = (n_count)',
    'S.STORE[n_count] = DEFINED (PINT 1)',
    '$lookup(psymboltable_global.ENV,$ptascii("xThrow240")) = (n_global)',
    'S.STORE[n_global] = DEFINED (PFLOAT 4616752568008179712)',
    '$lookup(psymboltable_global.ENV,$ptascii("result240")) = (n_result)',
    'S.STORE[n_result] = DEFINED (PINT 99)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_later) = (pdefaultcache_later)',
    '$lookup(S_done.ENV,$ptascii("countThrow240")) = (n_count)',
    'S_done.STORE[n_count] = DEFINED (PINT 4)',
    '$lookup(S_done.ENV,$ptascii("result240")) = (n_result)',
    'S_done.STORE[n_result] = DEFINED (PINT 0)',
    '$lookup(S_done.ENV,$ptascii("xThrow240")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4616752568008179712)',
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_first) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_cell) = 0',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

one = constant('E_ERROR')
true = constant('true')
null = constant('null')
string_two = 'NScalarString (BYTES "Mg==") eps'
zero = 'NScalarInt (INTEGER 0) eps'
false_zero = f'NExprBinaryOpMinus ({one}) ({one}) eps'
throwing.extend([
    f'$lossy_optional_integer_numeric($plempty(false),{string_two}) = eps',
    f'$lossy_optional_integer_numeric($plempty(false),{true}) = eps',
    f'$lossy_optional_integer_numeric($plempty(false),{null}) = eps',
    f'$lossy_optional_integer_numeric($plempty(false),NExprBinaryOpPlus ({string_two}) ({one}) eps) = eps',
    f'$lossy_optional_integer_power_operand($plempty(false),{string_two}) = (NINT 2)',
    f'$lossy_optional_integer_power_operand($plempty(false),{true}) = (NINT 1)',
    f'$lossy_optional_integer_power_operand($plempty(false),{null}) = (NINT 0)',
    f'$lossy_optional_integer_numeric($plempty(false),NExprBinaryOpPow ({string_two}) ({zero}) eps) = (NINT 1)',
    f'$lossy_optional_integer_numeric($plempty(false),NExprBinaryOpPow ({string_two}) ({false_zero}) eps) = (NINT 1)',
    '$lossy_optional_integer_power_operand($plempty(false),NScalarString (BYTES "MnRhaWw=") eps) = eps',
    '$lossy_optional_integer_power_operand($plempty(false),NScalarString (BYTES "bm9uZQ==") eps) = eps',
    f'$lossy_optional_integer_numeric($plempty(false),NExprBinaryOpPow (NScalarString (BYTES "bm9uZQ==") eps) ({zero}) eps) = eps',
    f'$lossy_optional_integer_numeric($plempty(false),NExprBinaryOpPow ({null}) (NExprUnaryMinus ({one}) eps) eps) = eps',
    '$power_prepare(NINT 0,NINT $(-1)) = POWERDONE (NFLOAT 9218868437227405312) true',
    '$coerce_number(PSTRING ([50,116,97,105,108])) = COERCED (NINT 2) true',
    '$coerce_number(PSTRING ([110,111,110,101])) = BADNUMBER',
])

CASES = {
    'numeric-coercive-power-fractional-throw-retry': {
        'source': ROWS['numeric-coercive-power-default-fractional-handler-throw-retry']['source'],
        'stage': 'S.TODO = [ERROR_HANDLER_INVOKE perrorcall] -- if perrorcall.RESUME = ' + TASK,
        'checks': throwing,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
