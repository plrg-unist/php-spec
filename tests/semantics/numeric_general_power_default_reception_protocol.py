#!/usr/bin/env python3
"""General power caches precede fractional reception and throwing callbacks."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('numeric_general_power_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

TASK = 'LOSSY_DEFAULT_PARAMETER_RECEIVE porigin 1 n_cell n_bits i z'


def authority(function, parameters):
    return [
        '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
        f'pfunction.NAME = $ptascii("{function}")',
        f'pfunction.SIGNATURE.PARAMETERS = [{parameters}]',
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
        'expression_later = NExprBinaryOpPow expression_base expression_negative_one metadata_later',
        '$lossy_optional_integer_numeric(pfunction.ENV,expression_base) = (NINT 2)',
        '$lossy_optional_integer_numeric(pfunction.ENV,expression_negative_one) = (NINT $(-1))',
        '$power_prepare(NINT 2,NINT $(-1)) = POWERGENERAL 4607182418800017408 4611686018427387904 13830554455654793216 0 false',
        '$num_pow(NINT 2,NINT $(-1)) = (NFLOAT 4602678819172646912,false)',
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


reference = authority('generalPowerDefaults239', 'psparam_first,psparam_later,psparam_root') + [
    r'~psparam_first.BYREF /\ psparam_later.BYREF /\ ~psparam_root.BYREF',
    '$call_task_valid(S,' + TASK + ')',
    'psparam_root.DEFAULT = PSDEFAULT expression_root "deferred"',
    '$default_parameter_origin(S,porigin,2) = PORIGIN n_unit pcpath_root',
    'porigin_root = PORIGIN n_unit (pcpath_root ++ [PCFIELD 6])',
    '$origin_node(S.SOURCES,porigin_root) = (expression_root)',
    '$default_at(pfunction.DEFAULTS,2) = ({INDEX 2,ORIGIN porigin_root,KIND PDDEFERRED})',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_root) = eps',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_root) = (NFLOAT 4611686018427387904)',
    '$power_prepare(NINT 4,NFLOAT 4602678819172646912) = POWERGENERAL 4607182418800017408 4616189618054758400 4602678819172646912 0 false',
    '$default_current_cache(S,porigin_root) = eps',
    '$lookup(S.ENV,psparam_root.NAME) = eps',
    'S.CODE = [pcode]',
    '~$lossy_default_parameter_source_valid(S[.CODE = ([pcode[.NAMES = eps]])],' + TASK + ')',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("E_WARNING"),$ptascii("E_ERROR"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_later)',
    '~$lossy_default_parameter_source_valid(S[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])],' + TASK + ')',
    'PhpStep: S ~> S_bound',
    'S_bound.TODO = [TYPE_RECEIVE porigin 2]',
    'S_bound.STORE[n_cell] = DEFINED (PINT 0)',
    'S_bound.STORE[n_first] = S.STORE[n_first]',
    r'S_bound.DEFAULTCACHE = S.DEFAULTCACHE /\ S_bound.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_bound,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_later) = (pdefaultcache_later)',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_root) = ({ORIGIN porigin_root,VALUE PFLOAT 4611686018427387904,CLASS PVSCALAR})',
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_first) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_cell) = 0',
    '$lookup(S_done.ENV,$ptascii("xGeneralPower239")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]


def constant(name):
    return f'NExprConstFetch (NName (BYTES "{base64.b64encode(name.encode()).decode()}") eps) eps'


# Only the two author-owned old EPS expectations are promoted here.
base = constant('E_WARNING')
one = constant('E_ERROR')
reference.extend([
    f'$lossy_optional_integer_numeric($plempty(false),NExprBinaryOpPow ({base}) (NScalarInt (INTEGER $(-1)) eps) eps) = (NFLOAT 4602678819172646912)',
    f'$lossy_optional_integer_numeric($plempty(false),NExprBinaryOpPow ({one}) (NExprUnaryMinus ({one}) eps) eps) = (NFLOAT 4607182418800017408)',
])

throwing = authority('generalThrow239', 'psparam_first,psparam_later') + [
    r'~psparam_first.BYREF /\ ~psparam_later.BYREF',
    'perrorcall.SITE = $default_parameter_origin(S,porigin,1)',
    r'perrorcall.LEVEL = 8192 /\ perrorcall.LINE = z /\ perrorcall.MESSAGE = ptbytes',
    'perrorcall.EVENT = DIAGNOSTIC "Deprecated" ptbytes z',
    '$error_call_valid(S,perrorcall)',
    '$call_task_valid(S,ERROR_HANDLER_INVOKE perrorcall)',
    '~$error_call_valid(S,perrorcall[.LEVEL = 2])',
    '~$error_call_valid(S,perrorcall[.MESSAGE = $ptascii("forged")])',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("countThrow239")) = (n_count)',
    'S.STORE[n_count] = DEFINED (PINT 1)',
    '$lookup(psymboltable_global.ENV,$ptascii("xThrow239")) = (n_global)',
    'S.STORE[n_global] = DEFINED (PFLOAT 4616752568008179712)',
    '$lookup(psymboltable_global.ENV,$ptascii("result239")) = (n_result)',
    'S.STORE[n_result] = DEFINED (PINT 99)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_later) = (pdefaultcache_later)',
    '$lookup(S_done.ENV,$ptascii("countThrow239")) = (n_count)',
    'S_done.STORE[n_count] = DEFINED (PINT 4)',
    '$lookup(S_done.ENV,$ptascii("result239")) = (n_result)',
    'S_done.STORE[n_result] = DEFINED (PINT 0)',
    '$lookup(S_done.ENV,$ptascii("xThrow239")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4616752568008179712)',
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_first) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HCELL n_cell) = 0',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

CASES = {
    'numeric-general-power-fractional-reference-resume': {
        'source': ROWS['numeric-general-power-default-fractional-cold-warm']['source'],
        'stage': 'S.TODO = [' + TASK + ']',
        'checks': reference,
    },
    'numeric-general-power-fractional-throw-retry': {
        'source': ROWS['numeric-general-power-default-fractional-handler-throw-retry']['source'],
        'stage': 'S.TODO = [ERROR_HANDLER_INVOKE perrorcall] -- if perrorcall.RESUME = ' + TASK,
        'checks': throwing,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
