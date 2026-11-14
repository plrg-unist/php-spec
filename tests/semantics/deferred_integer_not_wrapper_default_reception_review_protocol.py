#!/usr/bin/env python3
"""Independent signed-integer NOT values, authority and private receive lifetimes."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_integer_not_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

authority = [
    'porigin_truth = PORIGIN n_unit pcpath_truth',
    'porigin_integer = PORIGIN n_unit (pcpath_truth ++ [PCFIELD 0])',
    '$origin_node(S.SOURCES,porigin_truth) = (NExprBooleanNot expression_integer metadata_truth)',
    '$origin_node(S.SOURCES,porigin_integer) = (expression_integer)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_integer) = (PINT i_operand)',
    '$long_range(i_operand)',
    'b_truth = (i_operand = 0)',
    '$code_at(S.CODE,n_unit) = (pcode)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_truth) = ((z_truth,false))',
    r'$pool_value(S.POOLS,porigin_truth) = eps /\ $compiled_read(S,porigin_truth) = eps',
    '$compiled_redirect(S,porigin_truth) = eps',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_truth)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_truth) = (PBOOL b_truth)',
]
fences = [
    'S_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_truth z_truth true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_integer) = (PINT i_operand)',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_truth) = eps',
    '$pool_at(S.POOLS,n_unit) = (ppool)',
    'S_pool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_truth (PBOOL b_truth))] ++ ppool.CONSTANTS)]]]',
    '$compiled_read(S_pool,porigin_truth) = eps',
    '$lossy_optional_integer_deferred_value_at(S_pool,pfunction.ENV,porigin_truth) = eps',
    'S_intpool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_truth (PINT 0))] ++ ppool.CONSTANTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_intpool,pfunction.ENV,porigin_truth) = eps',
    'S_redirect = S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath_truth (pcpath_truth ++ [PCFIELD 0]) false)] ++ pcode.REDIRECTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,porigin_integer) = (PINT i_operand)',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,porigin_truth) = eps',
    'S.SOURCES = [pcunit]',
    'pcunit_child = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_truth (NExprBooleanNot (NScalarInt (INTEGER 7) eps) metadata_truth))] ++ pcunit.OCCURRENCES)]',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = [pcunit_child]],pfunction.ENV,porigin_truth) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.CODE = eps],pfunction.ENV,porigin_truth) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = eps],pfunction.ENV,porigin_truth) = eps',
]
raw_tail = [
    '$default_current_cache(S,porigin_truth) = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    'S.RESULT = KNOWN (PINT i_operand)',
    '$boolean_result(S,true,z) = S[.RESULT = KNOWN (PBOOL b_truth)][.BASE = BASE_VALUE (KNOWN PNULL)]',
    'S_marker = S[.BASE = BASE_VALUE (KNOWN (PINT 7))]',
    '$boolean_result(S_marker,true,z) = S_marker[.RESULT = KNOWN (PBOOL b_truth)][.BASE = BASE_VALUE (KNOWN PNULL)]',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,porigin_truth) = (PBOOL b_truth)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_truth',
    'S_truth = S[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL b_truth)][.BASE = BASE_VALUE (KNOWN PNULL)]',
    'S_done = $drive_steps(S_truth,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.CONSTCONTEXT = eps',
]
for index, value in enumerate(['true', 'false', 'false']):
    raw_tail.extend([
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = ({{ORIGIN pdefault_{index}.ORIGIN,VALUE PBOOL {value},CLASS PVSCALAR}})',
    ])
raw_tail.extend([
    'S_done.EVENTS = [' + ','.join('OUTPUT $ptascii(' + json.dumps(value) + ')' for value in
                                 (('raw:', '1', ':', '1', ':', '1', '|') * 2)) + ']',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {}
for name, index, operand, truth in [('zero', 0, '0', 'true'), ('negative', 1, '$(-3)', 'false'), ('positive', 2, '3', 'false')]:
    boundaries = []
    if index == 0:
        for label, bound in [('min', '$(-9223372036854775808)'), ('max', '9223372036854775807')]:
            boundaries.extend([
                f'$long_range({bound})',
                f'S_{label} = S[.RESULT = KNOWN (PINT {bound})][.BASE = BASE_VALUE (KNOWN (PINT 7))]',
                f'$boolean_result(S_{label},true,z) = S_{label}[.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
            ])
    CASES['deferred-integer-not-actual-' + name] = {
        'source': ROWS['deferred-integer-not-wrapper-raw-phases']['source'],
        'stage': ('S.TODO = (TRUTH_RESULT true z) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if $function_at(S.FUNCTIONS,pcallcontext.FUNCTION) = (pfunction) '
                  '-- if pfunction.NAME = $ptascii("rawNot263") '
                  f'-- if $default_at(pfunction.DEFAULTS,{index}) = (pdefault_root) '
                  '-- if S.ORIGIN = (pdefault_root.ORIGIN)'),
        'checks': [f'i_operand = {operand}', f'b_truth = {truth}', 'porigin_truth = pdefault_root.ORIGIN']
                  + authority + fences + raw_tail + boundaries,
    }

named = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("IntNot263")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_zero,psparam_nonzero,psparam_last]',
    r'~psparam_first.BYREF /\ psparam_zero.BYREF /\ psparam_nonzero.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.HOLES = [1,2] /\ pcallcontext.ARGC = 4',
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$default_cache_owner(S) = (CACHE_SHARED)',
]
for index, label, operand, boolean, value, wrong_value in [(1, 'zero', '0', 'true', '1', '0'), (2, 'nonzero', '$(-3)', 'false', '0', '1')]:
    named.extend([
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{label})',
        f'porigin_{label} = pdefault_{label}.ORIGIN',
        f'porigin_{label} = PORIGIN n_unit pcpath_{label}',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{label} ++ [PCFIELD 0,PCFIELD 0])) = (PINT {operand})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{label} ++ [PCFIELD 0])) = (PBOOL {boolean})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{label}) = (PINT {value})',
        f'$default_current_cache(S,porigin_{label}) = (pdefaultcache_{label})',
        f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE PINT {value},CLASS PVSCALAR}}',
        f'$lookup(S.ENV,psparam_{label}.NAME) = (n_{label})',
        f'S.STORE[n_{label}] = DEFINED (PINT {value})',
        rf'~(n_{label} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_{label}) = 1',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'S_tag_{label} = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{label}[.VALUE = PBOOL true])]',
        f'$default_caches_valid(S_tag_{label},S_tag_{label}.DEFAULTCACHE)',
        f'~$lossy_optional_integer_deferred(S_tag_{label},pfunction,{index})',
        f'~$lossy_mixed_parameter_source_valid(S_tag_{label},ptask_resume)',
        f'S_value_{label} = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{label}[.VALUE = PINT {wrong_value}])]',
        f'$default_caches_valid(S_value_{label},S_value_{label}.DEFAULTCACHE)',
        f'~$lossy_optional_integer_deferred(S_value_{label},pfunction,{index})',
        f'~$lossy_mixed_parameter_source_valid(S_value_{label},ptask_resume)',
    ])
named.extend([
    'n_zero =/= n_nonzero',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 8)',
    '$lossy_mixed_parameter_source_valid(S,ptask_resume)',
    '$call_task_valid(S,ptask_resume)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base263"),$ptascii("E_ERROR")),($ptascii("One263"),$ptascii("E_ERROR"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_zero)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_nonzero)',
    '~$lossy_optional_integer_header(S,pfunction[.ENV = plenv_wrong],pfunction.SIGNATURE.PARAMETERS,0)',
    'S_budget = $drive_steps(S,0)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    'PhpStep: S_first ~> S_zero',
    r'S_zero.TODO = [TYPE_RECEIVE porigin 2] /\ S_zero.STORE[n_zero] = DEFINED (PINT 1)',
    'PhpStep: S_zero ~> S_nonzero',
    r'S_nonzero.TODO = [TYPE_RECEIVE porigin 3] /\ S_nonzero.STORE[n_nonzero] = DEFINED (PINT 0)',
    r'S_nonzero.DEFAULTCACHE = S.DEFAULTCACHE /\ S_nonzero.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_nonzero,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_zero) = (pdefaultcache_zero)',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_nonzero) = (pdefaultcache_nonzero)',
    r'~((HCELL n_zero) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_zero) = 0',
    r'~((HCELL n_nonzero) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_nonzero) = 0',
    '$lookup(S_done.ENV,$ptascii("x263")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
])
CASES['deferred-integer-not-private-two-holes-warning-return'] = {
    'source': ROWS['deferred-integer-not-wrapper-alias-named-reentry']['source'],
    'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
              '-- if ptask_resume = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z'),
    'checks': named,
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
