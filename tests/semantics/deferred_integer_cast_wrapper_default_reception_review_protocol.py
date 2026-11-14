#!/usr/bin/env python3
"""Independent quiet INT casts, exact large integers and named private caches."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_integer_cast_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

authority_checks = [
    'pdefault_root.ORIGIN = PORIGIN n_unit pcpath_root',
    'porigin_child = PORIGIN n_unit (pcpath_root ++ [PCFIELD 0])',
    '$origin_node(S.SOURCES,pdefault_root.ORIGIN) = (expression_root)',
    'expression_root = NExprCastInt expression_child metadata_root',
    '$plstyle(metadata_root) = 1',
    '$origin_node(S.SOURCES,porigin_child) = (expression_child)',
    '$code_at(S.CODE,n_unit) = (pcode)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_root) = ((z_root,false))',
    r'$pool_value(S.POOLS,pdefault_root.ORIGIN) = eps /\ $compiled_read(S,pdefault_root.ORIGIN) = eps',
    '$compiled_redirect(S,pdefault_root.ORIGIN) = eps',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_root.ORIGIN)',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_child)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_child) = (pvalue_child)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_root.ORIGIN) = (PINT i_root)',
    '$cast_apply(S,CASTINT,pvalue_child,z) = S[.RESULT = KNOWN (PINT i_root)]',
]

kind_checks = [
    'S.SOURCES = [pcunit]',
    'pcunit_alias = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_root (NExprCastInt expression_child ((Mkind 2) :: metadata_root)))] ++ pcunit.OCCURRENCES)]',
    'S_alias = S[.SOURCES = [pcunit_alias]]',
    '$lossy_optional_integer_deferred_value_at(S_alias,pfunction.ENV,porigin_child) = (pvalue_child)',
    '$lossy_optional_integer_deferred_value_at(S_alias,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    'pcunit_missing = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_root (NExprCastInt expression_child eps))] ++ pcunit.OCCURRENCES)]',
    'S_missing = S[.SOURCES = [pcunit_missing]]',
    '$lossy_optional_integer_deferred_value_at(S_missing,pfunction.ENV,porigin_child) = (pvalue_child)',
    '$lossy_optional_integer_deferred_value_at(S_missing,pfunction.ENV,pdefault_root.ORIGIN) = eps',
]

raw_checks = [
    'pfunction.SIGNATURE.PARAMETERS = [psparam_zero,psparam_fraction,psparam_large]',
    '$default_at(pfunction.DEFAULTS,1) = (pdefault_fraction)',
    '$default_at(pfunction.DEFAULTS,2) = (pdefault_large)',
    'pvalue_child = PFLOAT 0',
    'i_root = 0',
    'S.RESULT = KNOWN pvalue_child',
    '$default_current_cache(S,pdefault_root.ORIGIN) = eps',
] + authority_checks + kind_checks + [
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_root) = (NINT 0)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_child) = (NFLOAT 9223372036854775808)',
    '$float_long(0,false) = (0,eps)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_fraction.ORIGIN) = (PINT 3)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_large.ORIGIN) = (PINT 9223372036854775807)',
    'S_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_root z_root true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_child) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    '$pool_at(S.POOLS,n_unit) = (ppool)',
    'S_pool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_root (PINT 0))] ++ ppool.CONSTANTS)]]]',
    '$compiled_read(S_pool,pdefault_root.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S_pool,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    'S_redirect = S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath_root (pcpath_root ++ [PCFIELD 0]) false)] ++ pcode.REDIRECTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,porigin_child) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    'pcunit_child = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_root (NExprCastInt (NScalarInt (INTEGER 7) eps) metadata_root))] ++ pcunit.OCCURRENCES)]',
    'S_child = S[.SOURCES = [pcunit_child]]',
    '$lossy_optional_integer_deferred_value_at(S_child,pfunction.ENV,porigin_child) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred_value_at(S_child,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.CODE = eps],pfunction.ENV,pdefault_root.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = eps],pfunction.ENV,pdefault_root.ORIGIN) = eps',
]

# These derived source/state probes establish refusal of intrinsic notices, not
# PHP error agreement. Suppressed diagnostics cannot make a noisy cast quiet.
for index, (spelling, bits) in enumerate([
        ('43e0000000000000', 4890909195324358656),
        ('7ff0000000000000', 9218868437227405312),
        ('7ff8000000000000', 9221120237041090560)]):
    probe_checks = [
        'expression_probe_zero = NExprUnaryPlus (NScalarFloat (FLOAT "8000000000000000") eps) eps',
        f'expression_probe_right = NScalarFloat (FLOAT "{spelling}") eps',
        'expression_probe_child = NExprBinaryOpPlus expression_probe_zero expression_probe_right eps',
        'expression_probe_root = NExprCastInt expression_probe_child ((Mkind 1) :: eps)',
        'pcunit_probe = pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_root expression_probe_root),'
        '(PCOCCURRENCE (pcpath_root ++ [PCFIELD 0]) expression_probe_child),'
        '(PCOCCURRENCE (pcpath_root ++ [PCFIELD 0,PCFIELD 0]) expression_probe_zero),'
        '(PCOCCURRENCE (pcpath_root ++ [PCFIELD 0,PCFIELD 0,PCFIELD 0]) (NScalarFloat (FLOAT "8000000000000000") eps)),'
        '(PCOCCURRENCE (pcpath_root ++ [PCFIELD 0,PCFIELD 1]) expression_probe_right)] ++ pcunit.OCCURRENCES)]',
        'S_probe = S[.SOURCES = [pcunit_probe]][.POOLS = eps][.CODE = [pcode[.EXPRESSIONS = '
        '[(CODEEXPR pcpath_root z_root false),(CODEEXPR (pcpath_root ++ [PCFIELD 0]) z_root false),'
        '(CODEEXPR (pcpath_root ++ [PCFIELD 0,PCFIELD 0]) z_root false)]]]]',
        f'n_probe = $float_add(0,{bits})',
        '~$lossy_optional_integer_phase_safe(S_probe,pfunction.ENV,pdefault_root.ORIGIN)',
        '$lossy_optional_integer_deferred_value_at(S_probe,pfunction.ENV,porigin_child) = (PFLOAT n_probe)',
        '$float_long(n_probe,false) = (i_probe,RANGEWARNING)',
        '$lossy_optional_integer_deferred_value_at(S_probe,pfunction.ENV,pdefault_root.ORIGIN) = eps',
        'S_quiet = S_probe[.REPORTING = 0]',
        '$cast_apply(S_quiet,CASTINT,PFLOAT n_probe,z) = S_quiet[.RESULT = KNOWN (PINT i_probe)]',
        '$lossy_optional_integer_deferred_value_at(S_quiet,pfunction.ENV,porigin_child) = (PFLOAT n_probe)',
        '$lossy_optional_integer_deferred_value_at(S_quiet,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    ]
    raw_checks += [clause.replace('_probe', f'_probe{index}').replace('S_quiet', f'S_quiet{index}')
                   for clause in probe_checks]

raw_checks += [
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_cast',
    'S_cast = S[.TODO = ptask_tail*][.RESULT = KNOWN (PINT 0)]',
    'S_done = $drive_steps(S_cast,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.CONSTCONTEXT = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_root.ORIGIN) = ({ORIGIN pdefault_root.ORIGIN,VALUE PINT 0,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_fraction.ORIGIN) = ({ORIGIN pdefault_fraction.ORIGIN,VALUE PINT 3,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_large.ORIGIN) = ({ORIGIN pdefault_large.ORIGIN,VALUE PINT 9223372036854775807,CLASS PVSCALAR})',
    'S_done.EVENTS = [' + ','.join('OUTPUT $ptascii(' + json.dumps(value) + ')' for value in
                                 (('raw:', '1', ':', '1', ':', '1', ':', '3', ':', '9223372036854775807', '|') * 2)) + ']',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]

large_checks = [
    'pvalue_child = PINT 9223372036854775807',
    'i_root = 9223372036854775807',
    'S.RESULT = KNOWN pvalue_child',
    '$default_current_cache(S,pdefault_root.ORIGIN) = eps',
] + authority_checks + kind_checks + [
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_child) = (NINT 9223372036854775807)',
    '$float_of_int(9223372036854775807) = 4890909195324358656',
    '$float_long(4890909195324358656,false) = ($(-9223372036854775808),RANGEWARNING)',
    '$cast_apply(S,CASTINT,PINT 9223372036854775807,z) = S',
    'S_budget = $drive_steps(S,0)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_cast',
    'S_cast = S[.TODO = ptask_tail*]',
    'S_done = $drive_steps(S_cast,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_root.ORIGIN) = ({ORIGIN pdefault_root.ORIGIN,VALUE PINT 9223372036854775807,CLASS PVSCALAR})',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]

named_checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("IntCastWrapper256")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base256"),$ptascii("E_WARNING")),($ptascii("One256"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_integer,psparam_last]',
    r'~psparam_first.BYREF /\ psparam_integer.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.HOLES = [1] /\ pcallcontext.ARGC = 3',
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$default_at(pfunction.DEFAULTS,1) = (pdefault_root)',
    'pvalue_child = PFLOAT 4615063718147915776',
    'i_root = 3',
] + authority_checks + [
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_root) = (NINT 3)',
    '$float_long(4615063718147915776,false) = (3,eps)',
    '$float_long(4615063718147915776,true) = (3,PRECISIONLOSS)',
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
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base256"),$ptascii("E_ERROR")),($ptascii("One256"),$ptascii("E_ERROR"))]]',
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
    '$lookup(S_done.ENV,$ptascii("x256")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]

CASES = {}
for name, index, checks in [('actual-float-child', 0, raw_checks),
                             ('exact-large-integer-child', 2, large_checks)]:
    CASES['deferred-integer-cast-' + name] = {
        'source': ROWS['deferred-integer-cast-wrapper-raw-phases']['source'],
        'stage': ('S.TODO = (CAST_RESULT CASTINT z) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if $function_at(S.FUNCTIONS,pcallcontext.FUNCTION) = (pfunction) '
                  '-- if pfunction.NAME = $ptascii("rawInt256") '
                  f'-- if $default_at(pfunction.DEFAULTS,{index}) = (pdefault_root) '
                  '-- if S.ORIGIN = (pdefault_root.ORIGIN)'),
        'checks': checks,
    }
CASES['deferred-integer-cast-private-named-warning-return'] = {
    'source': ROWS['deferred-integer-cast-wrapper-alias-named-reentry']['source'],
    'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
              '-- if ptask_resume = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z'),
    'checks': named_checks,
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
