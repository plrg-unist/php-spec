#!/usr/bin/env python3
"""Independent integer negation, MIN promotion and later default errors."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_integer_minus_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

authority = [
    'pdefault_root.ORIGIN = PORIGIN n_unit pcpath_root',
    'porigin_child = PORIGIN n_unit (pcpath_root ++ [PCFIELD 0])',
    '$origin_node(S.SOURCES,pdefault_root.ORIGIN) = (expression_root)',
    'expression_root = NExprUnaryMinus expression_child metadata_root',
    '$origin_node(S.SOURCES,porigin_child) = (expression_child)',
    '$code_at(S.CODE,n_unit) = (pcode)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_root) = ((z_root,false))',
    r'$pool_value(S.POOLS,pdefault_root.ORIGIN) = eps /\ $compiled_read(S,pdefault_root.ORIGIN) = eps',
    '$compiled_redirect(S,pdefault_root.ORIGIN) = eps',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_root.ORIGIN)',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_child)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_child) = (PINT i_child)',
    '$long_range(i_child)',
    '$num_mul(NINT i_child,NINT $(-1)) = pnumber_root',
    'pvalue_root = $number_value(pnumber_root)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_root.ORIGIN) = (pvalue_root)',
]

fences = [
    'S_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_root z_root true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_child) = (PINT i_child)',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    '$pool_at(S.POOLS,n_unit) = (ppool)',
    'S_pool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_root pvalue_root)] ++ ppool.CONSTANTS)]]]',
    '$compiled_read(S_pool,pdefault_root.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S_pool,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    'S_redirect = S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath_root (pcpath_root ++ [PCFIELD 0]) false)] ++ pcode.REDIRECTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,porigin_child) = (PINT i_child)',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    'S.SOURCES = [pcunit]',
    'pcunit_child = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_root (NExprUnaryMinus (NScalarInt (INTEGER 7) eps) metadata_root))] ++ pcunit.OCCURRENCES)]',
    'S_child = S[.SOURCES = [pcunit_child]]',
    '$lossy_optional_integer_deferred_value_at(S_child,pfunction.ENV,porigin_child) = (PINT i_child)',
    '$lossy_optional_integer_deferred_value_at(S_child,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.CODE = eps],pfunction.ENV,pdefault_root.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = eps],pfunction.ENV,pdefault_root.ORIGIN) = eps',
]

raw_tail = [
    '$default_current_cache(S,pdefault_root.ORIGIN) = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    'S.RESULT = KNOWN (PINT i_child)',
    '$unary_apply(S,NEGATIVE,PINT i_child,z) = S[.RESULT = KNOWN pvalue_root]',
    '$runtime_unary_apply(S,NEGATIVE,PINT i_child,z) = S[.RESULT = KNOWN pvalue_root]',
    'S_suppressed = S[.REPORTING = 0]',
    '$runtime_unary_apply(S_suppressed,NEGATIVE,PINT i_child,z) = S_suppressed[.RESULT = KNOWN pvalue_root]',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,pdefault_root.ORIGIN) = (pvalue_root)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_minus',
    'S_minus = S[.TODO = ptask_tail*][.RESULT = KNOWN pvalue_root]',
    'S_done = $drive_steps(S_minus,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.CONSTCONTEXT = eps',
    '$default_at(pfunction.DEFAULTS,0) = (pdefault_zero)',
    '$default_at(pfunction.DEFAULTS,1) = (pdefault_three)',
    '$default_at(pfunction.DEFAULTS,2) = (pdefault_max)',
    '$default_at(pfunction.DEFAULTS,3) = (pdefault_min)',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_zero.ORIGIN) = ({ORIGIN pdefault_zero.ORIGIN,VALUE PINT 0,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_three.ORIGIN) = ({ORIGIN pdefault_three.ORIGIN,VALUE PINT $(-3),CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_max.ORIGIN) = ({ORIGIN pdefault_max.ORIGIN,VALUE PINT $(-9223372036854775807),CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_min.ORIGIN) = ({ORIGIN pdefault_min.ORIGIN,VALUE PFLOAT 4890909195324358656,CLASS PVSCALAR})',
    'S_done.EVENTS = [' + ','.join('OUTPUT $ptascii(' + json.dumps(value) + ')' for value in
                                 (('raw:', '1', ':', '1', ':', '1', ':', '1', ':', '-3', ':', '-9223372036854775807', '|') * 2)) + ']',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]

CASES = {}
for name, index, child, result in [
        ('exact-MAX', 2, '9223372036854775807', 'NINT $(-9223372036854775807)'),
        ('MIN-overflow', 3, '$(-9223372036854775808)', 'NFLOAT 4890909195324358656')]:
    CASES['deferred-integer-minus-actual-' + name] = {
        'source': ROWS['deferred-integer-minus-wrapper-raw-phases']['source'],
        'stage': ('S.TODO = (UNARY NEGATIVE z) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if $function_at(S.FUNCTIONS,pcallcontext.FUNCTION) = (pfunction) '
                  '-- if pfunction.NAME = $ptascii("rawMinus258") '
                  f'-- if $default_at(pfunction.DEFAULTS,{index}) = (pdefault_root) '
                  '-- if S.ORIGIN = (pdefault_root.ORIGIN)'),
        'checks': [f'i_child = {child}', f'pnumber_root = {result}'] + authority + fences + raw_tail,
    }

named = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("MinusIntWrapper258")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base258"),$ptascii("E_WARNING")),($ptascii("One258"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_integer,psparam_last]',
    r'~psparam_first.BYREF /\ psparam_integer.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.HOLES = [1] /\ pcallcontext.ARGC = 3',
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$default_at(pfunction.DEFAULTS,1) = (pdefault_root)',
    'i_child = 3',
    'pnumber_root = NINT $(-3)',
] + authority + [
    '$default_current_cache(S,pdefault_root.ORIGIN) = (pdefaultcache_integer)',
    'pdefaultcache_integer = {ORIGIN pdefault_root.ORIGIN,VALUE PINT $(-3),CLASS PVSCALAR}',
    '$lookup(S.ENV,psparam_integer.NAME) = (n_integer)',
    'S.STORE[n_integer] = DEFINED (PINT $(-3))',
    r'~(n_integer <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_integer) = 1',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 8)',
    '$lossy_optional_integer_deferred(S,pfunction,1)',
    '$lossy_mixed_parameter_source_valid(S,ptask_resume)',
    '$call_task_valid(S,ptask_resume)',
    'S_float = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_integer[.VALUE = PFLOAT 13837309855095848960])]',
    '$default_caches_valid(S_float,S_float.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_float,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S_float,ptask_resume)',
    'S_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_integer[.VALUE = PINT 4])]',
    '$default_caches_valid(S_value,S_value.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_value,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S_value,ptask_resume)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base258"),$ptascii("E_ERROR")),($ptascii("One258"),$ptascii("E_ERROR"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_root.ORIGIN)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    'S_budget = $drive_steps(S,0)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    'PhpStep: S_first ~> S_integer',
    r'S_integer.TODO = [TYPE_RECEIVE porigin 2] /\ S_integer.STORE[n_integer] = DEFINED (PINT $(-3))',
    r'S_integer.DEFAULTCACHE = S.DEFAULTCACHE /\ S_integer.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_integer,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_root.ORIGIN) = (pdefaultcache_integer)',
    r'~((HCELL n_integer) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_integer) = 0',
    '$lookup(S_done.ENV,$ptascii("x258")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]
CASES['deferred-integer-minus-private-named-warning-return'] = {
    'source': ROWS['deferred-integer-minus-wrapper-alias-named-reentry']['source'],
    'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
              '-- if ptask_resume = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z'),
    'checks': named,
}

error_checks = [
    'S.CURRENT = (pcallcontext)',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_later]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ ~psparam_later.BYREF',
    '$ptmasks(psparam_later.TYPE) = ["int"]',
    '$default_at(pfunction.DEFAULTS,1) = (pdefault_root)',
    'i_child = $(-9223372036854775808)',
    'pnumber_root = NFLOAT 4890909195324358656',
] + authority + [
    '$typed_weak(["int"],pvalue_root) = TYPEREJECT',
    '$lossy_optional_integer_deferred(S,pfunction,1)',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lookup(S.ENV,psparam_first.NAME) = (n_first)',
    '$lookup(S.ENV,psparam_later.NAME) = eps',
    '$parameter_default_error_candidate(S,pfunction,1,pvalue_root)',
    'S_budget = $drive_steps(S,0)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_throw',
    'S_throw.COMPLETION = THROWN "TypeError" preqbytes z_error',
    'z_error = $default_parameter_line(S,porigin,1)',
    '$default_cache_at(S_throw.DEFAULTCACHE,pdefault_root.ORIGIN) = ({ORIGIN pdefault_root.ORIGIN,VALUE pvalue_root,CLASS PVSCALAR})',
    '$lookup(S_throw.ENV,psparam_later.NAME) = (n_later)',
    'S_throw.STORE[n_later] = DEFINED pvalue_root',
    '(HCELL n_later) <- S_throw.ALLOCATIONS',
    'S_throw.CONSTCONTEXT = eps',
    'S_done = $drive_steps(S_throw,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_root.ORIGIN) = ({ORIGIN pdefault_root.ORIGIN,VALUE pvalue_root,CLASS PVSCALAR})',
    r'~((HCELL n_later) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_later) = 0',
    '$lookup(S_done.ENV,$ptascii("first258")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4612811918334230528)',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]
for name, task, first, cache in [
        ('cold-bind', 'DEFAULT_BIND', 1, 'eps'),
        ('warm-cache', 'DEFAULT_RECEIVE', 2,
         '({ORIGIN pdefault_root.ORIGIN,VALUE pvalue_root,CLASS PVSCALAR})')]:
    CASES['deferred-integer-minus-later-type-error-' + name] = {
        'source': ROWS['deferred-integer-minus-wrapper-minimum-overflow-type-error']['source'],
        'stage': (f'S.TODO = [{task} porigin 1] '
                  '-- if $function_at(S.FUNCTIONS,porigin) = (pfunction) '
                  '-- if pfunction.NAME = $ptascii("range258") '
                  '-- if $default_at(pfunction.DEFAULTS,1) = (pdefault_root)'
                  + (' -- if $default_current_cache(S,pdefault_root.ORIGIN) = '
                     '({ORIGIN pdefault_root.ORIGIN,VALUE PFLOAT 4890909195324358656,CLASS PVSCALAR})'
                     if task == 'DEFAULT_RECEIVE' else '')),
        'checks': error_checks + [
            f'S.STORE[n_first] = DEFINED (PINT {first})',
            f'$default_current_cache(S,pdefault_root.ORIGIN) = {cache}',
        ],
    }

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
