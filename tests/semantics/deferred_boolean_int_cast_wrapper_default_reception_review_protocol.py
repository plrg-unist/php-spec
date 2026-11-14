#!/usr/bin/env python3
"""Independent raw Boolean-to-int casts, authority and named receive lifetimes."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_boolean_int_cast_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

authority = [
    'porigin_integer = PORIGIN n_unit pcpath_integer',
    'porigin_bool = PORIGIN n_unit (pcpath_integer ++ [PCFIELD 0])',
    '$origin_node(S.SOURCES,porigin_integer) = (expression_integer)',
    'expression_integer = NExprCastInt expression_bool metadata_integer',
    '$plstyle(metadata_integer) = 1',
    '$origin_node(S.SOURCES,porigin_bool) = (expression_bool)',
    'expression_bool = NExprCastBool expression_child metadata_bool',
    '$plstyle(metadata_bool) = 1',
    '$code_at(S.CODE,n_unit) = (pcode)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_integer) = ((z_integer,false))',
    r'$pool_value(S.POOLS,porigin_integer) = eps /\ $compiled_read(S,porigin_integer) = eps',
    '$compiled_redirect(S,porigin_integer) = eps',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_integer)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_bool) = (PBOOL b_truth)',
    '$coerce_number(PBOOL b_truth) = COERCED (NINT i_integer) false',
    '$long_range(i_integer)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_integer) = (PINT i_integer)',
]

fences = [
    'S_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_integer z_integer true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_bool) = (PBOOL b_truth)',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_integer) = eps',
    '$pool_at(S.POOLS,n_unit) = (ppool)',
    'S_pool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_integer (PINT i_integer))] ++ ppool.CONSTANTS)]]]',
    '$compiled_read(S_pool,porigin_integer) = eps',
    '$lossy_optional_integer_deferred_value_at(S_pool,pfunction.ENV,porigin_integer) = eps',
    'S_boolpool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_integer (PBOOL b_truth))] ++ ppool.CONSTANTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_boolpool,pfunction.ENV,porigin_integer) = eps',
    'S_redirect = S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath_integer (pcpath_integer ++ [PCFIELD 0]) false)] ++ pcode.REDIRECTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,porigin_bool) = (PBOOL b_truth)',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,porigin_integer) = eps',
    'S.SOURCES = [pcunit]',
    'pcunit_alias = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_integer (NExprCastInt expression_bool ((Mkind 2) :: metadata_integer)))] ++ pcunit.OCCURRENCES)]',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = [pcunit_alias]],pfunction.ENV,porigin_integer) = eps',
    'pcunit_missing = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_integer (NExprCastInt expression_bool eps))] ++ pcunit.OCCURRENCES)]',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = [pcunit_missing]],pfunction.ENV,porigin_integer) = eps',
    'pcunit_child = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_integer (NExprCastInt (NScalarInt (INTEGER 7) eps) metadata_integer))] ++ pcunit.OCCURRENCES)]',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = [pcunit_child]],pfunction.ENV,porigin_integer) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.CODE = eps],pfunction.ENV,porigin_integer) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = eps],pfunction.ENV,porigin_integer) = eps',
]

raw_tail = [
    '$default_current_cache(S,porigin_integer) = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    'S.RESULT = KNOWN (PBOOL b_truth)',
    '$cast_apply(S,CASTINT,PBOOL b_truth,z) = S[.RESULT = KNOWN (PINT i_integer)]',
    'S_suppressed = S[.REPORTING = 0]',
    '$cast_apply(S_suppressed,CASTINT,PBOOL b_truth,z) = S_suppressed[.RESULT = KNOWN (PINT i_integer)]',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,porigin_integer) = (PINT i_integer)',
    '$cast_apply(S_budget,CASTINT,PBOOL b_truth,z) = S_budget',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_integer',
    'S_integer = S[.TODO = ptask_tail*][.RESULT = KNOWN (PINT i_integer)]',
    'S_done = $drive_steps(S_integer,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.CONSTCONTEXT = eps',
    '$default_at(pfunction.DEFAULTS,0) = (pdefault_zero)',
    '$default_at(pfunction.DEFAULTS,1) = (pdefault_negative)',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_zero.ORIGIN) = ({ORIGIN pdefault_zero.ORIGIN,VALUE PINT 0,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_negative.ORIGIN) = ({ORIGIN pdefault_negative.ORIGIN,VALUE PINT 1,CLASS PVSCALAR})',
    'S_done.EVENTS = [' + ','.join('OUTPUT $ptascii(' + json.dumps(value) + ')' for value in
                                 (('raw:', '1', ':', '1', '|') * 2)) + ']',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]

CASES = {}
for name, index, truth, integer in [('false-zero', 0, 'false', '0'), ('true-negative', 1, 'true', '1')]:
    CASES['deferred-boolean-int-cast-actual-' + name] = {
        'source': ROWS['deferred-boolean-int-cast-wrapper-raw-phases']['source'],
        'stage': ('S.TODO = (CAST_RESULT CASTINT z) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if $function_at(S.FUNCTIONS,pcallcontext.FUNCTION) = (pfunction) '
                  '-- if pfunction.NAME = $ptascii("rawInt260") '
                  f'-- if $default_at(pfunction.DEFAULTS,{index}) = (pdefault_root) '
                  '-- if S.ORIGIN = (pdefault_root.ORIGIN)'),
        'checks': [f'b_truth = {truth}', f'i_integer = {integer}', 'porigin_integer = pdefault_root.ORIGIN']
                  + authority + fences + raw_tail,
    }

named = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("BoolIntWrapper260")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_integer,psparam_last]',
    r'~psparam_first.BYREF /\ psparam_integer.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.HOLES = [1] /\ pcallcontext.ARGC = 3',
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$default_at(pfunction.DEFAULTS,1) = (pdefault_root)',
    'porigin_integer = pdefault_root.ORIGIN',
    'b_truth = true',
    'i_integer = 1',
] + authority + [
    '$default_current_cache(S,porigin_integer) = (pdefaultcache_integer)',
    'pdefaultcache_integer = {ORIGIN porigin_integer,VALUE PINT 1,CLASS PVSCALAR}',
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
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base260"),$ptascii("E_ERROR")),($ptascii("One260"),$ptascii("E_ERROR"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_integer)',
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
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_integer) = (pdefaultcache_integer)',
    r'~((HCELL n_integer) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_integer) = 0',
    '$lookup(S_done.ENV,$ptascii("x260")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]
CASES['deferred-boolean-int-cast-private-named-warning-return'] = {
    'source': ROWS['deferred-boolean-int-cast-wrapper-alias-named-reentry']['source'],
    'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
              '-- if ptask_resume = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z'),
    'checks': named,
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
