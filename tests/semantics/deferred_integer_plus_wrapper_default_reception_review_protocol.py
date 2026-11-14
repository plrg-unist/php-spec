#!/usr/bin/env python3
"""Independent emitted integer-plus stages, exact MAX and named private cells."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_integer_plus_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

authority_checks = [
    'pdefault_root.ORIGIN = PORIGIN n_unit pcpath_root',
    'porigin_child = PORIGIN n_unit (pcpath_root ++ [PCFIELD 0])',
    '$origin_node(S.SOURCES,pdefault_root.ORIGIN) = (expression_root)',
    'expression_root = NExprUnaryPlus expression_child metadata_root',
    '$origin_node(S.SOURCES,porigin_child) = (expression_child)',
    '$code_at(S.CODE,n_unit) = (pcode)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_root) = ((z_root,false))',
    r'$pool_value(S.POOLS,pdefault_root.ORIGIN) = eps /\ $compiled_read(S,pdefault_root.ORIGIN) = eps',
    '$compiled_redirect(S,pdefault_root.ORIGIN) = eps',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_root.ORIGIN)',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_child)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_child) = (PINT i_root)',
    '$long_range(i_root)',
    '$num_add(NINT 0,NINT i_root) = NINT i_root',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_root.ORIGIN) = (PINT i_root)',
]

fence_checks = [
    'S_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_root z_root true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_child) = (PINT i_root)',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    '$pool_at(S.POOLS,n_unit) = (ppool)',
    'S_pool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_root (PINT i_root))] ++ ppool.CONSTANTS)]]]',
    '$compiled_read(S_pool,pdefault_root.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S_pool,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    'S_redirect = S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath_root (pcpath_root ++ [PCFIELD 0]) false)] ++ pcode.REDIRECTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,porigin_child) = (PINT i_root)',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    'S.SOURCES = [pcunit]',
    'pcunit_child = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_root (NExprUnaryPlus (NScalarInt (INTEGER 7) eps) metadata_root))] ++ pcunit.OCCURRENCES)]',
    'S_child = S[.SOURCES = [pcunit_child]]',
    '$lossy_optional_integer_deferred_value_at(S_child,pfunction.ENV,porigin_child) = (PINT i_root)',
    '$lossy_optional_integer_deferred_value_at(S_child,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.CODE = eps],pfunction.ENV,pdefault_root.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = eps],pfunction.ENV,pdefault_root.ORIGIN) = eps',
]

raw_tail = [
    '$default_current_cache(S,pdefault_root.ORIGIN) = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    'S.RESULT = KNOWN (PINT i_root)',
    '$unary_apply(S,POSITIVE,PINT i_root,z) = S',
    '$runtime_unary_apply(S,POSITIVE,PINT i_root,z) = S',
    'S_suppressed = S[.REPORTING = 0]',
    '$runtime_unary_apply(S_suppressed,POSITIVE,PINT i_root,z) = S_suppressed',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_plus',
    'S_plus = S[.TODO = ptask_tail*]',
    'S_done = $drive_steps(S_plus,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.CONSTCONTEXT = eps',
    '$default_at(pfunction.DEFAULTS,0) = (pdefault_zero)',
    '$default_at(pfunction.DEFAULTS,1) = (pdefault_three)',
    '$default_at(pfunction.DEFAULTS,2) = (pdefault_max)',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_zero.ORIGIN) = ({ORIGIN pdefault_zero.ORIGIN,VALUE PINT 0,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_three.ORIGIN) = ({ORIGIN pdefault_three.ORIGIN,VALUE PINT 3,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_max.ORIGIN) = ({ORIGIN pdefault_max.ORIGIN,VALUE PINT 9223372036854775807,CLASS PVSCALAR})',
    'S_done.EVENTS = [' + ','.join('OUTPUT $ptascii(' + json.dumps(value) + ')' for value in
                                 (('raw:', '1', ':', '1', ':', '1', ':', '3', ':', '9223372036854775807', '|') * 2)) + ']',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]

CASES = {}
for name, index, value in [('zero', 0, 0), ('three', 1, 3), ('exact-MAX', 2, 9223372036854775807)]:
    checks = [f'i_root = {value}'] + authority_checks
    if index == 2:
        checks += [
            '$float_of_int(i_root) = 4890909195324358656',
            '$float_long(4890909195324358656,false) = ($(-9223372036854775808),RANGEWARNING)',
            '~$long_range($(i_root + 1))',
        ]
    CASES['deferred-integer-plus-actual-' + name] = {
        'source': ROWS['deferred-integer-plus-wrapper-raw-phases']['source'],
        'stage': ('S.TODO = (UNARY POSITIVE z) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if $function_at(S.FUNCTIONS,pcallcontext.FUNCTION) = (pfunction) '
                  '-- if pfunction.NAME = $ptascii("rawPlus257") '
                  f'-- if $default_at(pfunction.DEFAULTS,{index}) = (pdefault_root) '
                  '-- if S.ORIGIN = (pdefault_root.ORIGIN)'),
        'checks': checks + fence_checks + raw_tail,
    }

named_checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("PlusIntWrapper257")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base257"),$ptascii("E_WARNING")),($ptascii("One257"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_integer,psparam_last]',
    r'~psparam_first.BYREF /\ psparam_integer.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.HOLES = [1] /\ pcallcontext.ARGC = 3',
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$default_at(pfunction.DEFAULTS,1) = (pdefault_root)',
    'i_root = 3',
] + authority_checks + [
    '$default_current_cache(S,pdefault_root.ORIGIN) = (pdefaultcache_integer)',
    'pdefaultcache_integer = {ORIGIN pdefault_root.ORIGIN,VALUE PINT 3,CLASS PVSCALAR}',
    '$lookup(S.ENV,psparam_integer.NAME) = (n_integer)',
    'S.STORE[n_integer] = DEFINED (PINT 3)',
    r'~(n_integer <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_integer) = 1',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 8)',
    '$lossy_optional_integer_deferred(S,pfunction,1)',
    '$lossy_mixed_parameter_source_valid(S,ptask_resume)',
    '$call_task_valid(S,ptask_resume)',
    'S_float = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_integer[.VALUE = PFLOAT 4613937818241073152])]',
    '$default_caches_valid(S_float,S_float.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_float,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S_float,ptask_resume)',
    'S_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_integer[.VALUE = PINT 4])]',
    '$default_caches_valid(S_value,S_value.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_value,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S_value,ptask_resume)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base257"),$ptascii("E_ERROR")),($ptascii("One257"),$ptascii("E_ERROR"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_root.ORIGIN)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    '~$lossy_optional_integer_deferred(S[.CODE = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    'S_budget = $drive_steps(S,0)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    'PhpStep: S_first ~> S_integer',
    r'S_integer.TODO = [TYPE_RECEIVE porigin 2] /\ S_integer.STORE[n_integer] = DEFINED (PINT 3)',
    r'S_integer.DEFAULTCACHE = S.DEFAULTCACHE /\ S_integer.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_integer,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_root.ORIGIN) = (pdefaultcache_integer)',
    r'~((HCELL n_integer) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_integer) = 0',
    '$lookup(S_done.ENV,$ptascii("x257")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]
CASES['deferred-integer-plus-private-named-warning-return'] = {
    'source': ROWS['deferred-integer-plus-wrapper-alias-named-reentry']['source'],
    'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
              '-- if ptask_resume = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z'),
    'checks': named_checks,
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
