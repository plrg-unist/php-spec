#!/usr/bin/env python3
"""Independent actual Boolean signs, raw integer caches and two-hole lifetimes."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_boolean_sign_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

authority = [
    'porigin_sign = PORIGIN n_unit pcpath_sign',
    'porigin_bool = PORIGIN n_unit (pcpath_sign ++ [PCFIELD 0])',
    '$origin_node(S.SOURCES,porigin_sign) = (expression_sign)',
    '$pfshape(expression_sign) = PFUNARY punary expression_bool',
    '$origin_node(S.SOURCES,porigin_bool) = (expression_bool)',
    'expression_bool = NExprCastBool expression_child metadata_bool',
    '$plstyle(metadata_bool) = 1',
    '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_sign ++ [PCFIELD 0,PCFIELD 0])) = (expression_child)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_sign ++ [PCFIELD 0,PCFIELD 0])) = (PINT i_child)',
    '$code_at(S.CODE,n_unit) = (pcode)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_sign) = ((z_sign,false))',
    r'$pool_value(S.POOLS,porigin_sign) = eps /\ $compiled_read(S,porigin_sign) = eps',
    '$compiled_redirect(S,porigin_sign) = eps',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_sign)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_bool) = (PBOOL b_truth)',
    '$coerce_number(PBOOL b_truth) = COERCED (NINT i_bool) false',
    '$long_range(i_bool)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_sign) = (PINT i_sign)',
]

fences = [
    'S_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_sign z_sign true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_bool) = (PBOOL b_truth)',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_sign) = eps',
    '$pool_at(S.POOLS,n_unit) = (ppool)',
    'S_pool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_sign (PINT i_sign))] ++ ppool.CONSTANTS)]]]',
    '$compiled_read(S_pool,porigin_sign) = eps',
    '$lossy_optional_integer_deferred_value_at(S_pool,pfunction.ENV,porigin_sign) = eps',
    'S_boolpool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_sign (PBOOL b_truth))] ++ ppool.CONSTANTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_boolpool,pfunction.ENV,porigin_sign) = eps',
    'S_redirect = S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath_sign (pcpath_sign ++ [PCFIELD 0]) false)] ++ pcode.REDIRECTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,porigin_bool) = (PBOOL b_truth)',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,porigin_sign) = eps',
    'S.SOURCES = [pcunit]',
    'pcunit_child = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_sign (NExprUnaryPlus (NScalarInt (INTEGER 7) eps) eps))] ++ pcunit.OCCURRENCES)]',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = [pcunit_child]],pfunction.ENV,porigin_sign) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.CODE = eps],pfunction.ENV,porigin_sign) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = eps],pfunction.ENV,porigin_sign) = eps',
]

raw_tail = [
    '$default_current_cache(S,porigin_sign) = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    'S.RESULT = KNOWN (PBOOL b_truth)',
    '$unary_apply(S,punary,PBOOL b_truth,z) = S[.RESULT = KNOWN (PINT i_sign)]',
    'S_suppressed = S[.REPORTING = 0]',
    '$unary_apply(S_suppressed,punary,PBOOL b_truth,z) = S_suppressed[.RESULT = KNOWN (PINT i_sign)]',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,porigin_sign) = (PINT i_sign)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_sign',
    'S_sign = S[.TODO = ptask_tail*][.RESULT = KNOWN (PINT i_sign)]',
    'S_done = $drive_steps(S_sign,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.CONSTCONTEXT = eps',
]
for index, value in enumerate(['0', '1', '0', '$(-1)']):
    raw_tail.extend([
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = ({{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}})',
    ])
raw_tail.extend([
    'S_done.EVENTS = [' + ','.join('OUTPUT $ptascii(' + json.dumps(value) + ')' for value in
                                 (('raw:', '1', ':', '1', ':', '1', ':', '1', '|') * 2)) + ']',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
])

CASES = {}
for name, index, unary, truth, boolean, child, signed in [
    ('plus-false', 0, 'POSITIVE', 'false', '0', '0', '0'),
    ('plus-true-negative', 1, 'POSITIVE', 'true', '1', '$(-3)', '1'),
    ('minus-false', 2, 'NEGATIVE', 'false', '0', '0', '0'),
    ('minus-true-negative', 3, 'NEGATIVE', 'true', '1', '$(-3)', '$(-1)'),
]:
    CASES['deferred-boolean-sign-actual-' + name] = {
        'source': ROWS['deferred-boolean-sign-wrapper-raw-phases']['source'],
        'stage': (f'S.TODO = (UNARY {unary} z) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if $function_at(S.FUNCTIONS,pcallcontext.FUNCTION) = (pfunction) '
                  '-- if pfunction.NAME = $ptascii("rawSign261") '
                  f'-- if $default_at(pfunction.DEFAULTS,{index}) = (pdefault_root) '
                  '-- if S.ORIGIN = (pdefault_root.ORIGIN)'),
        'checks': [f'punary = {unary}', f'b_truth = {truth}', f'i_bool = {boolean}',
                   f'i_child = {child}', f'i_sign = {signed}', 'porigin_sign = pdefault_root.ORIGIN']
                  + authority + fences + raw_tail,
    }

named = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("BoolSigns261")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_positive,psparam_negative,psparam_last]',
    r'~psparam_first.BYREF /\ psparam_positive.BYREF /\ psparam_negative.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.HOLES = [1,2] /\ pcallcontext.ARGC = 4',
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$default_cache_owner(S) = (CACHE_SHARED)',
]
for index, label, value in [(1, 'positive', '1'), (2, 'negative', '$(-1)')]:
    named.extend([
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{label})',
        f'porigin_{label} = pdefault_{label}.ORIGIN',
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
        f'S_value_{label} = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{label}[.VALUE = PINT 0])]',
        f'$default_caches_valid(S_value_{label},S_value_{label}.DEFAULTCACHE)',
        f'~$lossy_optional_integer_deferred(S_value_{label},pfunction,{index})',
        f'~$lossy_mixed_parameter_source_valid(S_value_{label},ptask_resume)',
    ])
named.extend([
    'n_positive =/= n_negative',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 8)',
    '$lossy_mixed_parameter_source_valid(S,ptask_resume)',
    '$call_task_valid(S,ptask_resume)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base261"),$ptascii("E_ERROR")),($ptascii("One261"),$ptascii("E_ERROR"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_positive)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_negative)',
    '~$lossy_optional_integer_header(S,pfunction[.ENV = plenv_wrong],pfunction.SIGNATURE.PARAMETERS,0)',
    'S_budget = $drive_steps(S,0)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    'PhpStep: S_first ~> S_positive',
    r'S_positive.TODO = [TYPE_RECEIVE porigin 2] /\ S_positive.STORE[n_positive] = DEFINED (PINT 1)',
    'PhpStep: S_positive ~> S_negative',
    r'S_negative.TODO = [TYPE_RECEIVE porigin 3] /\ S_negative.STORE[n_negative] = DEFINED (PINT $(-1))',
    r'S_negative.DEFAULTCACHE = S.DEFAULTCACHE /\ S_negative.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_negative,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_positive) = (pdefaultcache_positive)',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_negative) = (pdefaultcache_negative)',
    r'~((HCELL n_positive) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_positive) = 0',
    r'~((HCELL n_negative) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_negative) = 0',
    '$lookup(S_done.ENV,$ptascii("x261")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
])
CASES['deferred-boolean-sign-private-two-holes-warning-return'] = {
    'source': ROWS['deferred-boolean-sign-wrapper-alias-named-reentry']['source'],
    'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
              '-- if ptask_resume = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z'),
    'checks': named,
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
