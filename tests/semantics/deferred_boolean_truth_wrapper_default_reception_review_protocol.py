#!/usr/bin/env python3
"""Independent Boolean identity/NOT authority, state effects and two-hole calls."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_boolean_truth_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

head = [
    'porigin_truth = PORIGIN n_unit pcpath_truth',
    'porigin_bool = PORIGIN n_unit (pcpath_truth ++ [PCFIELD 0])',
    '$origin_node(S.SOURCES,porigin_truth) = (expression_truth)',
]
authority = [
    '$origin_node(S.SOURCES,porigin_bool) = (expression_bool)',
    'expression_bool = NExprCastBool expression_child metadata_bool',
    '$plstyle(metadata_bool) = 1',
    '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_truth ++ [PCFIELD 0,PCFIELD 0])) = (expression_child)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_truth ++ [PCFIELD 0,PCFIELD 0])) = (PINT i_child)',
    '$code_at(S.CODE,n_unit) = (pcode)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_truth) = ((z_truth,false))',
    r'$pool_value(S.POOLS,porigin_truth) = eps /\ $compiled_read(S,porigin_truth) = eps',
    '$compiled_redirect(S,porigin_truth) = eps',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_truth)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_bool) = (PBOOL b_input)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_truth) = (PBOOL b_output)',
]
fences = [
    'S_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_truth z_truth true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_bool) = (PBOOL b_input)',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_truth) = eps',
    '$pool_at(S.POOLS,n_unit) = (ppool)',
    'S_pool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_truth (PBOOL b_output))] ++ ppool.CONSTANTS)]]]',
    '$compiled_read(S_pool,porigin_truth) = eps',
    '$lossy_optional_integer_deferred_value_at(S_pool,pfunction.ENV,porigin_truth) = eps',
    'S_intpool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_truth (PINT 0))] ++ ppool.CONSTANTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_intpool,pfunction.ENV,porigin_truth) = eps',
    'S_redirect = S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath_truth (pcpath_truth ++ [PCFIELD 0]) false)] ++ pcode.REDIRECTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,porigin_bool) = (PBOOL b_input)',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,porigin_truth) = eps',
    'S.SOURCES = [pcunit]',
    'pcunit_child = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_truth (NExprCastBool (NScalarInt (INTEGER 7) eps) metadata_bool))] ++ pcunit.OCCURRENCES)]',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = [pcunit_child]],pfunction.ENV,porigin_truth) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.CODE = eps],pfunction.ENV,porigin_truth) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = eps],pfunction.ENV,porigin_truth) = eps',
]
raw_tail = [
    '$default_current_cache(S,porigin_truth) = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    'S.RESULT = KNOWN (PBOOL b_input)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,porigin_truth) = (PBOOL b_output)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
]
finish = [
    'S_done = $drive_steps(S_truth,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.CONSTCONTEXT = eps',
]
for index, value in enumerate(['false', 'true', 'true', 'false']):
    finish.extend([
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = ({{ORIGIN pdefault_{index}.ORIGIN,VALUE PBOOL {value},CLASS PVSCALAR}})',
    ])
finish.extend([
    'S_done.EVENTS = [' + ','.join('OUTPUT $ptascii(' + json.dumps(value) + ')' for value in
                                 (('raw:', '1', ':', '1', ':', '1', ':', '1', '|') * 2)) + ']',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {}
for name, index, constructor, child, input_value, output_value, task in [
    ('identity-false', 0, 'NExprCastBool', '0', 'false', 'false', 'CAST_RESULT CASTBOOL z'),
    ('identity-true-negative', 1, 'NExprCastBool', '$(-3)', 'true', 'true', 'CAST_RESULT CASTBOOL z'),
    ('not-false', 2, 'NExprBooleanNot', '0', 'false', 'true', 'TRUTH_RESULT true z'),
    ('not-true-negative', 3, 'NExprBooleanNot', '$(-3)', 'true', 'false', 'TRUTH_RESULT true z'),
]:
    identity = constructor == 'NExprCastBool'
    style = ['$plstyle(metadata_truth) = 1'] if identity else []
    style_fences = [
        'pcunit_alias = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_truth (NExprCastBool expression_bool ((Mkind 2) :: metadata_truth)))] ++ pcunit.OCCURRENCES)]',
        '$lossy_optional_integer_deferred_value_at(S[.SOURCES = [pcunit_alias]],pfunction.ENV,porigin_truth) = eps',
        'pcunit_missing = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_truth (NExprCastBool expression_bool eps))] ++ pcunit.OCCURRENCES)]',
        '$lossy_optional_integer_deferred_value_at(S[.SOURCES = [pcunit_missing]],pfunction.ENV,porigin_truth) = eps',
    ] if identity else []
    state_delta = '[.RESULT = KNOWN (PBOOL b_output)]' + ('' if identity else '[.BASE = BASE_VALUE (KNOWN PNULL)]')
    operation = '$cast_apply(S,CASTBOOL,PBOOL b_input,z)' if identity else '$boolean_result(S,true,z)'
    marker_operation = '$cast_apply(S_marker,CASTBOOL,PBOOL b_input,z)' if identity else '$boolean_result(S_marker,true,z)'
    runtime = [
        operation + ' = S' + state_delta,
        'S_marker = S[.BASE = BASE_VALUE (KNOWN (PINT 7))]',
        marker_operation + ' = S_marker' + state_delta,
        'PhpStep: S ~> S_truth',
        'S_truth = S[.TODO = ptask_tail*]' + state_delta,
    ]
    CASES['deferred-boolean-truth-actual-' + name] = {
        'source': ROWS['deferred-boolean-truth-wrapper-raw-phases']['source'],
        'stage': (f'S.TODO = ({task}) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if $function_at(S.FUNCTIONS,pcallcontext.FUNCTION) = (pfunction) '
                  '-- if pfunction.NAME = $ptascii("rawTruth262") '
                  f'-- if $default_at(pfunction.DEFAULTS,{index}) = (pdefault_root) '
                  '-- if S.ORIGIN = (pdefault_root.ORIGIN)'),
        'checks': [f'i_child = {child}', f'b_input = {input_value}', f'b_output = {output_value}',
                   'porigin_truth = pdefault_root.ORIGIN'] + head
                  + [f'expression_truth = {constructor} expression_bool metadata_truth'] + style
                  + authority + fences + style_fences + raw_tail + runtime + finish,
    }

named = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("BoolTruth262")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_identity,psparam_negated,psparam_last]',
    r'~psparam_first.BYREF /\ psparam_identity.BYREF /\ psparam_negated.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.HOLES = [1,2] /\ pcallcontext.ARGC = 4',
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$default_cache_owner(S) = (CACHE_SHARED)',
]
for index, label, boolean, value, wrong_value in [(1, 'identity', 'true', '1', '0'), (2, 'negated', 'false', '0', '1')]:
    named.extend([
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{label})',
        f'porigin_{label} = pdefault_{label}.ORIGIN',
        f'porigin_{label} = PORIGIN n_unit pcpath_{label}',
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
    'n_identity =/= n_negated',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 8)',
    '$lossy_mixed_parameter_source_valid(S,ptask_resume)',
    '$call_task_valid(S,ptask_resume)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base262"),$ptascii("E_ERROR")),($ptascii("One262"),$ptascii("E_ERROR"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_identity)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_negated)',
    '~$lossy_optional_integer_header(S,pfunction[.ENV = plenv_wrong],pfunction.SIGNATURE.PARAMETERS,0)',
    'S_budget = $drive_steps(S,0)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    'PhpStep: S_first ~> S_identity',
    r'S_identity.TODO = [TYPE_RECEIVE porigin 2] /\ S_identity.STORE[n_identity] = DEFINED (PINT 1)',
    'PhpStep: S_identity ~> S_negated',
    r'S_negated.TODO = [TYPE_RECEIVE porigin 3] /\ S_negated.STORE[n_negated] = DEFINED (PINT 0)',
    r'S_negated.DEFAULTCACHE = S.DEFAULTCACHE /\ S_negated.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_negated,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_identity) = (pdefaultcache_identity)',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_negated) = (pdefaultcache_negated)',
    r'~((HCELL n_identity) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_identity) = 0',
    r'~((HCELL n_negated) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_negated) = 0',
    '$lookup(S_done.ENV,$ptascii("x262")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
])
CASES['deferred-boolean-truth-private-two-holes-warning-return'] = {
    'source': ROWS['deferred-boolean-truth-wrapper-alias-named-reentry']['source'],
    'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
              '-- if ptask_resume = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z'),
    'checks': named,
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
