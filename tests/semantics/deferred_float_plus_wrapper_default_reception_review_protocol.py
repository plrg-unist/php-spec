#!/usr/bin/env python3
"""Independent mixed-sign default phases and private named-cache checks."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_float_plus_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

raw_checks = [
    'pfunction.SIGNATURE.PARAMETERS = [psparam_double,psparam_mixed,psparam_outer,psparam_folded]',
    '$default_at(pfunction.DEFAULTS,1) = (pdefault_mixed)',
    '$default_at(pfunction.DEFAULTS,2) = (pdefault_outer)',
    '$default_at(pfunction.DEFAULTS,3) = (pdefault_folded)',
    'pdefault_root.ORIGIN = PORIGIN n_unit pcpath_root',
    'porigin_child = PORIGIN n_unit (pcpath_root ++ [PCFIELD 0])',
    'porigin_grandchild = PORIGIN n_unit (pcpath_root ++ [PCFIELD 0,PCFIELD 0])',
    '$origin_node(S.SOURCES,pdefault_root.ORIGIN) = (NExprUnaryPlus expression_child metadata_root)',
    '$origin_node(S.SOURCES,porigin_child) = (NExprUnaryPlus expression_grandchild metadata_child)',
    '$origin_node(S.SOURCES,porigin_grandchild) = (expression_grandchild)',
    'expression_child = NExprUnaryPlus expression_grandchild metadata_child',
    'S.RESULT = KNOWN (PFLOAT 0)',
    '$code_at(S.CODE,n_unit) = (pcode)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_root) = ((z_root,false))',
    '$code_expression(pcode.EXPRESSIONS,pcpath_root ++ [PCFIELD 0]) = ((z_child,false))',
    r'$pool_value(S.POOLS,pdefault_root.ORIGIN) = eps /\ $compiled_read(S,pdefault_root.ORIGIN) = eps',
    '$compiled_redirect(S,pdefault_root.ORIGIN) = eps',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_root.ORIGIN)',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_child)',
    '$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_grandchild)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_grandchild) = (NFLOAT 9223372036854775808)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_grandchild) = (PFLOAT 9223372036854775808)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_child) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_root.ORIGIN) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred_value(pfunction.ENV,NExprUnaryPlus expression_child metadata_root) = (PFLOAT 9223372036854775808)',
    '$runtime_unary_apply(S,POSITIVE,PFLOAT 0,z) = S',
    'S_sparse = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_root z_root false),(CODEEXPR (pcpath_root ++ [PCFIELD 0]) z_child false)])]]]',
    '$lossy_optional_integer_deferred_value_at(S_sparse,pfunction.ENV,pdefault_root.ORIGIN) = (PFLOAT 0)',
    'S_wrong_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_root z_root true),(CODEEXPR (pcpath_root ++ [PCFIELD 0]) z_child false)])]]]',
    '$compiled_read(S_wrong_code,pdefault_root.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S_wrong_code,pfunction.ENV,porigin_child) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred_value_at(S_wrong_code,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    'S_missing_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_root ++ [PCFIELD 0]) z_child false)])]]]',
    '$lossy_optional_integer_deferred_value_at(S_missing_code,pfunction.ENV,porigin_child) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred_value_at(S_missing_code,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    '$pool_at(S.POOLS,n_unit) = (ppool)',
    'S_pooled = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_root (PFLOAT 0))] ++ ppool.CONSTANTS)]]]',
    '$compiled_read(S_pooled,pdefault_root.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S_pooled,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    'S_redirect = S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath_root (pcpath_root ++ [PCFIELD 0]) false)] ++ pcode.REDIRECTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,porigin_child) = (PFLOAT 0)',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,pdefault_root.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = eps],pfunction.ENV,pdefault_root.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_mixed.ORIGIN) = (PFLOAT 9223372036854775808)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_outer.ORIGIN) = (PFLOAT 0)',
    '$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_folded.ORIGIN)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_folded.ORIGIN) = (PFLOAT 9223372036854775808)',
    'pdefault_folded.ORIGIN = PORIGIN n_unit pcpath_folded',
    '$compiled_read(S,PORIGIN n_unit (pcpath_folded ++ [PCFIELD 0])) = (PFLOAT 9223372036854775808)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_plus',
    'S_plus = S[.TODO = ptask_tail*]',
    'S_done = $drive_steps(S_plus,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.CONSTCONTEXT = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_root.ORIGIN) = ({ORIGIN pdefault_root.ORIGIN,VALUE PFLOAT 0,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_mixed.ORIGIN) = ({ORIGIN pdefault_mixed.ORIGIN,VALUE PFLOAT 9223372036854775808,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_outer.ORIGIN) = ({ORIGIN pdefault_outer.ORIGIN,VALUE PFLOAT 0,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_folded.ORIGIN) = ({ORIGIN pdefault_folded.ORIGIN,VALUE PFLOAT 9223372036854775808,CLASS PVSCALAR})',
    'S_done.EVENTS = [' + ','.join('OUTPUT $ptascii(' + json.dumps(value) + ')' for value in
                                 (('raw:', '0', ':', '-0', ':', '0', ':', '-0', '|') * 2
                                  + ('ordinary:', '-0', '|'))) + ']',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]

named_checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("PlusWrapper253")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base253"),$ptascii("E_WARNING")),($ptascii("One253"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_zero,psparam_last]',
    r'~psparam_first.BYREF /\ psparam_zero.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.HOLES = [1] /\ pcallcontext.ARGC = 3',
    '$default_at(pfunction.DEFAULTS,1) = (pdefault_zero)',
    'psparam_zero.DEFAULT = PSDEFAULT expression_zero "deferred"',
    '$origin_node(S.SOURCES,pdefault_zero.ORIGIN) = (expression_zero)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_zero) = (NFLOAT 9223372036854775808)',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_zero.ORIGIN)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_zero.ORIGIN) = (PFLOAT 0)',
    '$default_current_cache(S,pdefault_zero.ORIGIN) = (pdefaultcache_zero)',
    'pdefaultcache_zero = {ORIGIN pdefault_zero.ORIGIN,VALUE PFLOAT 0,CLASS PVSCALAR}',
    '$lookup(S.ENV,psparam_zero.NAME) = (n_zero)',
    'S.STORE[n_zero] = DEFINED (PFLOAT 0)',
    r'~(n_zero <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_zero) = 1',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 8)',
    '$lossy_optional_integer_deferred(S,pfunction,1)',
    '$lossy_mixed_parameter_source_valid(S,ptask_resume)',
    '$call_task_valid(S,ptask_resume)',
    'S_sign = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero[.VALUE = PFLOAT 9223372036854775808])]',
    '$default_caches_valid(S_sign,S_sign.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_sign,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S_sign,ptask_resume)',
    'S_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_zero[.VALUE = PINT 0])]',
    '$default_caches_valid(S_tag,S_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_tag,pfunction,1)',
    '~$lossy_mixed_parameter_source_valid(S_tag,ptask_resume)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base253"),$ptascii("E_ERROR")),($ptascii("One253"),$ptascii("E_ERROR"))]]',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    '~$lossy_optional_integer_deferred(S[.CODE = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    'PhpStep: S_first ~> S_zero',
    r'S_zero.TODO = [TYPE_RECEIVE porigin 2] /\ S_zero.STORE[n_zero] = DEFINED (PINT 0)',
    r'S_zero.DEFAULTCACHE = S.DEFAULTCACHE /\ S_zero.EVENTS = S.EVENTS',
    'S_done = $drive_steps(S_zero,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault_zero.ORIGIN) = (pdefaultcache_zero)',
    r'~((HCELL n_zero) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_zero) = 0',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]

CASES = {
    'deferred-float-plus-raw-chain': {
        'source': ROWS['deferred-float-plus-wrapper-raw-chain']['source'],
        'stage': ('S.TODO = (UNARY POSITIVE z) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if $function_at(S.FUNCTIONS,pcallcontext.FUNCTION) = (pfunction) '
                  '-- if pfunction.NAME = $ptascii("rawPlus253") '
                  '-- if $default_at(pfunction.DEFAULTS,0) = (pdefault_root) '
                  '-- if S.ORIGIN = (pdefault_root.ORIGIN)'),
        'checks': raw_checks,
    },
    'deferred-float-plus-private-named': {
        'source': ROWS['deferred-float-plus-wrapper-alias-named-reentry']['source'],
        'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
                  '-- if ptask_resume = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z'),
        'checks': named_checks,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
