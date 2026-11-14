#!/usr/bin/env python3
"""Independent Boolean tags, canonical cast authority and integer consumers."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_integer_bool_cast_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

authority = [
    'porigin_bool = PORIGIN n_unit pcpath_bool',
    'porigin_child = PORIGIN n_unit (pcpath_bool ++ [PCFIELD 0])',
    '$origin_node(S.SOURCES,porigin_bool) = (expression_bool)',
    'expression_bool = NExprCastBool expression_child metadata_bool',
    '$plstyle(metadata_bool) = 1',
    '$origin_node(S.SOURCES,porigin_child) = (expression_child)',
    '$code_at(S.CODE,n_unit) = (pcode)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_bool) = ((z_bool,false))',
    r'$pool_value(S.POOLS,porigin_bool) = eps /\ $compiled_read(S,porigin_bool) = eps',
    '$compiled_redirect(S,porigin_bool) = eps',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_bool)',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_child)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_child) = (PINT i_child)',
    '$long_range(i_child)',
    'b_truth = (i_child =/= 0)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_bool) = (PBOOL b_truth)',
]

fences = [
    'S_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_bool z_bool true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_child) = (PINT i_child)',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_bool) = eps',
    '$pool_at(S.POOLS,n_unit) = (ppool)',
    'S_pool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_bool (PBOOL b_truth))] ++ ppool.CONSTANTS)]]]',
    '$compiled_read(S_pool,porigin_bool) = eps',
    '$lossy_optional_integer_deferred_value_at(S_pool,pfunction.ENV,porigin_bool) = eps',
    'S_redirect = S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath_bool (pcpath_bool ++ [PCFIELD 0]) false)] ++ pcode.REDIRECTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,porigin_child) = (PINT i_child)',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,porigin_bool) = eps',
    'S.SOURCES = [pcunit]',
    'pcunit_alias = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_bool (NExprCastBool expression_child ((Mkind 2) :: metadata_bool)))] ++ pcunit.OCCURRENCES)]',
    'S_alias = S[.SOURCES = [pcunit_alias]]',
    '$lossy_optional_integer_deferred_value_at(S_alias,pfunction.ENV,porigin_child) = (PINT i_child)',
    '$lossy_optional_integer_deferred_value_at(S_alias,pfunction.ENV,porigin_bool) = eps',
    'pcunit_missing = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_bool (NExprCastBool expression_child eps))] ++ pcunit.OCCURRENCES)]',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = [pcunit_missing]],pfunction.ENV,porigin_bool) = eps',
    'pcunit_child = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_bool (NExprCastBool (NScalarInt (INTEGER 7) eps) metadata_bool))] ++ pcunit.OCCURRENCES)]',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = [pcunit_child]],pfunction.ENV,porigin_bool) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.CODE = eps],pfunction.ENV,porigin_bool) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = eps],pfunction.ENV,porigin_bool) = eps',
]

raw_tail = [
    '$default_current_cache(S,porigin_bool) = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    'S.RESULT = KNOWN (PINT i_child)',
    '$cast_apply(S,CASTBOOL,PINT i_child,z) = S[.RESULT = KNOWN (PBOOL b_truth)]',
    'S_suppressed = S[.REPORTING = 0]',
    '$cast_apply(S_suppressed,CASTBOOL,PINT i_child,z) = S_suppressed[.RESULT = KNOWN (PBOOL b_truth)]',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,porigin_bool) = (PBOOL b_truth)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_cast',
    'S_cast = S[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL b_truth)]',
    'S_done = $drive_steps(S_cast,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.CONSTCONTEXT = eps',
    '$default_at(pfunction.DEFAULTS,0) = (pdefault_zero)',
    '$default_at(pfunction.DEFAULTS,1) = (pdefault_positive)',
    '$default_at(pfunction.DEFAULTS,2) = (pdefault_negative)',
    '$default_at(pfunction.DEFAULTS,3) = (pdefault_large)',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_zero.ORIGIN) = ({ORIGIN pdefault_zero.ORIGIN,VALUE PBOOL false,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_positive.ORIGIN) = ({ORIGIN pdefault_positive.ORIGIN,VALUE PBOOL true,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_negative.ORIGIN) = ({ORIGIN pdefault_negative.ORIGIN,VALUE PBOOL true,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_large.ORIGIN) = ({ORIGIN pdefault_large.ORIGIN,VALUE PBOOL true,CLASS PVSCALAR})',
    'S_done.EVENTS = [' + ','.join('OUTPUT $ptascii(' + json.dumps(value) + ')' for value in
                                 (('raw:', '1', ':', '1', ':', '1', ':', '1', '|') * 2)) + ']',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]

CASES = {}
for name, index, child, truth in [('false-zero', 0, '0', 'false'), ('true-negative', 2, '$(-3)', 'true')]:
    CASES['deferred-integer-bool-cast-actual-' + name] = {
        'source': ROWS['deferred-integer-bool-cast-wrapper-raw-phases']['source'],
        'stage': ('S.TODO = (CAST_RESULT CASTBOOL z) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if $function_at(S.FUNCTIONS,pcallcontext.FUNCTION) = (pfunction) '
                  '-- if pfunction.NAME = $ptascii("rawBool259") '
                  f'-- if $default_at(pfunction.DEFAULTS,{index}) = (pdefault_root) '
                  '-- if S.ORIGIN = (pdefault_root.ORIGIN)'),
        'checks': [f'i_child = {child}', f'b_truth = {truth}', 'porigin_bool = pdefault_root.ORIGIN']
                  + authority + fences + raw_tail,
    }

named = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("BoolIntWrapper259")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base259"),$ptascii("E_WARNING")),($ptascii("One259"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_integer,psparam_last]',
    r'~psparam_first.BYREF /\ psparam_integer.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.HOLES = [1] /\ pcallcontext.ARGC = 3',
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$default_at(pfunction.DEFAULTS,1) = (pdefault_root)',
    'pdefault_root.ORIGIN = PORIGIN n_unit pcpath_root',
    'pcpath_bool = pcpath_root ++ [PCFIELD 1]',
    'i_child = 3',
    'b_truth = true',
] + authority + [
    '$origin_node(S.SOURCES,pdefault_root.ORIGIN) = (NExprBinaryOpPlus expression_left expression_bool metadata_root)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_root ++ [PCFIELD 0])) = (PINT 0)',
    '$coerce_number(PBOOL true) = COERCED (NINT 1) false',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_root.ORIGIN) = (PINT 1)',
    '$default_current_cache(S,pdefault_root.ORIGIN) = (pdefaultcache_integer)',
    'pdefaultcache_integer = {ORIGIN pdefault_root.ORIGIN,VALUE PINT 1,CLASS PVSCALAR}',
    '$lookup(S.ENV,psparam_integer.NAME) = (n_integer)',
    'S.STORE[n_integer] = DEFINED (PINT 1)',
    r'~(n_integer <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_integer) = 1',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 8)',
    '$lossy_optional_integer_deferred(S,pfunction,1)',
    '$lossy_mixed_parameter_source_valid(S,ptask_resume)',
    '$call_task_valid(S,ptask_resume)',
    'S_booltag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_integer[.VALUE = PBOOL true])]',
    '$default_caches_valid(S_booltag,S_booltag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_booltag,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S_booltag,ptask_resume)',
    'S_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_integer[.VALUE = PINT 0])]',
    '$default_caches_valid(S_value,S_value.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_value,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S_value,ptask_resume)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base259"),$ptascii("E_ERROR")),($ptascii("One259"),$ptascii("E_ERROR"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_root.ORIGIN)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    'S_budget = $drive_steps(S,0)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    'PhpStep: S_first ~> S_integer',
    r'S_integer.TODO = [TYPE_RECEIVE porigin 2] /\ S_integer.STORE[n_integer] = DEFINED (PINT 1)',
    r'S_integer.DEFAULTCACHE = S.DEFAULTCACHE /\ S_integer.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_integer,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_root.ORIGIN) = (pdefaultcache_integer)',
    r'~((HCELL n_integer) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_integer) = 0',
    '$lookup(S_done.ENV,$ptascii("x259")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]
CASES['deferred-integer-bool-cast-private-named-warning-return'] = {
    'source': ROWS['deferred-integer-bool-cast-wrapper-alias-named-reentry']['source'],
    'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
              '-- if ptask_resume = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z'),
    'checks': named,
}

CASES['deferred-integer-bool-cast-real-int-parent-refusal'] = {
    'source': ROWS['deferred-integer-bool-cast-wrapper-int-parent-control']['source'],
    'stage': ('S.TODO = [TYPE_RECEIVE porigin 0] '
              '-- if $function_at(S.FUNCTIONS,porigin) = (pfunction) '
              '-- if pfunction.NAME = $ptascii("defaults259")'),
    'checks': [
        '$default_at(pfunction.DEFAULTS,1) = (pdefault_root)',
        'pdefault_root.ORIGIN = PORIGIN n_unit pcpath_root',
        '$origin_node(S.SOURCES,pdefault_root.ORIGIN) = (NExprCastInt expression_bool metadata_root)',
        '$plstyle(metadata_root) = 1',
        'pcpath_bool = pcpath_root ++ [PCFIELD 0]',
        'i_child = $(-3)',
        'b_truth = true',
    ] + authority + [
        '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_root.ORIGIN) = (PINT 1)',
        '$lossy_optional_integer_deferred(S,pfunction,1)',
        '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
        '$lossy_mixed_parameter_capture(S) = (LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell 4609434218613702656 1 z)',
        'S_short = $drive_steps(S,100)',
        'S_short.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_short[.COMPLETION = NORMAL],3000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$default_cache_at(S_done.DEFAULTCACHE,pdefault_root.ORIGIN) = ({ORIGIN pdefault_root.ORIGIN,VALUE PINT 1,CLASS PVSCALAR})',
        r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
    ],
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
