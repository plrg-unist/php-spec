#!/usr/bin/env python3
"""Independent selected Boolean defaults, authority and private receive checks."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_boolean_short_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def certificate(suffix, index, constructor, disjunction, left, result, right=None):
    checks = [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault{suffix})',
        f'pdefault{suffix}.ORIGIN = PORIGIN n_unit pcpath{suffix}',
        f'porigin{suffix} = pdefault{suffix}.ORIGIN',
        f'porigin_left{suffix} = PORIGIN n_unit (pcpath{suffix} ++ [PCFIELD 0])',
        f'porigin_right{suffix} = PORIGIN n_unit (pcpath{suffix} ++ [PCFIELD 1])',
        f'$origin_node(S.SOURCES,porigin{suffix}) = ({constructor} expression_left{suffix} expression_right{suffix} metadata{suffix})',
        f'$pfshape({constructor} expression_left{suffix} expression_right{suffix} metadata{suffix}) = PFSHORT {disjunction} expression_left{suffix} expression_right{suffix}',
        f'$origin_node(S.SOURCES,porigin_left{suffix}) = (expression_left{suffix})',
        f'$origin_node(S.SOURCES,porigin_right{suffix}) = (expression_right{suffix})',
        f'$code_expression(pcode.EXPRESSIONS,pcpath{suffix}) = ((z{suffix},false))',
        rf'$pool_value(S.POOLS,porigin{suffix}) = eps /\ $compiled_read(S,porigin{suffix}) = eps',
        f'$compiled_redirect(S,porigin{suffix}) = eps',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin{suffix})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_left{suffix}) = (PBOOL {left})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin{suffix}) = (PBOOL {result})',
    ]
    checks.append(f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_right{suffix}) = '
                  + ('eps' if right is None else f'(PBOOL {right})'))
    return checks


CASES = {}
for name, index, constructor, disjunction, left, result, right, alternate in [
    ('decisive-and', 0, 'NExprBinaryOpBooleanAnd', 'false', 'false', 'false', None,
     (2, 'NExprBinaryOpBooleanAnd', 'false', 'true', 'false', 'false')),
    ('decisive-or', 1, 'NExprBinaryOpBooleanOr', 'true', 'true', 'true', None,
     (3, 'NExprBinaryOpBooleanOr', 'true', 'false', 'true', 'true')),
    ('demanded-and', 6, 'NExprBinaryOpLogicalAnd', 'false', 'true', 'true', 'true',
     (4, 'NExprBinaryOpLogicalAnd', 'false', 'false', 'false', None)),
    ('demanded-or', 7, 'NExprBinaryOpLogicalOr', 'true', 'false', 'false', 'false',
     (5, 'NExprBinaryOpLogicalOr', 'true', 'true', 'true', None)),
]:
    checks = [
        '$code_at(S.CODE,n_unit) = (pcode)',
        'S.ORIGIN = (porigin)',
        f'S.RESULT = KNOWN (PBOOL {left})',
    ] + certificate('', index, constructor, disjunction, left, result, right)
    checks += certificate('_alternate', *alternate)
    checks += [
        '$default_cache_owner(S) = (CACHE_SHARED)',
        '$default_current_cache(S,porigin) = eps',
        'S.SOURCES = [pcunit]',
        'S_badleft = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath ++ [PCFIELD 0]) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
        '$lossy_optional_integer_deferred_value_at(S_badleft,pfunction.ENV,porigin) = eps',
        'S_badright = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath ++ [PCFIELD 1]) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
        '$lossy_optional_integer_deferred_value_at(S_badright,pfunction.ENV,porigin) = eps',
        'S_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath z true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin_left) = (PBOOL {left})',
        '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,porigin) = eps',
        '$pool_at(S.POOLS,n_unit) = (ppool)',
        f'S_pool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath (PBOOL {result}))] ++ ppool.CONSTANTS)]]]',
        '$lossy_optional_integer_deferred_value_at(S_pool,pfunction.ENV,porigin) = eps',
        'S_redirect = S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 0]) false)] ++ pcode.REDIRECTS)]]]',
        '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,porigin) = eps',
        '$lossy_optional_integer_deferred_value_at(S[.SOURCES = eps],pfunction.ENV,porigin) = eps',
        '$lossy_optional_integer_deferred_value_at(S[.CODE = eps],pfunction.ENV,porigin) = eps',
        'S_budget = $drive_steps(S,0)',
        'S_budget = S[.COMPLETION = BUDGET]',
        f'$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,porigin) = (PBOOL {result})',
        '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        'S_tail = S[.TODO = ptask_tail*]',
        'S_marker = S_tail[.BASE = BASE_VALUE (KNOWN (PINT 42))]',
    ]
    if right is None:
        delta = '[.BASE = BASE_VALUE (KNOWN PNULL)]'
        checks += [
            'S_skipcode = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath ++ [PCFIELD 1]) z_right true)] ++ pcode.EXPRESSIONS)]]]',
            f'$lossy_optional_integer_deferred_value_at(S_skipcode,pfunction.ENV,porigin) = (PBOOL {result})',
        ]
    else:
        delta = ('[.TODO = [$at_task($origin_child(S.ORIGIN,[PCFIELD 1]),EVAL expression_right),'
                 'TRUTH_RESULT false z_right] ++ ptask_tail*]'
                 '[.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]')
        checks += [
            'S_rightcode = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath ++ [PCFIELD 1]) z_right true)] ++ pcode.EXPRESSIONS)]]]',
            '$lossy_optional_integer_deferred_value_at(S_rightcode,pfunction.ENV,porigin) = eps',
        ]
    checks += [
        f'$short_result(S_tail,{disjunction},expression_right,z_left,z_right) = S_tail' + delta,
        f'$short_result(S_marker,{disjunction},expression_right,z_left,z_right) = S_marker' + delta,
        'PhpStep: S ~> S_after',
        'S_after = S_tail' + delta,
        'S_done = $drive_steps(S_after,3000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.CONSTCONTEXT = eps',
    ]
    for slot, boolean in enumerate(['false', 'true', 'false', 'true', 'false', 'true', 'true', 'false']):
        checks += [
            f'$default_at(pfunction.DEFAULTS,{slot}) = (pdefault_done_{slot})',
            f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_done_{slot}.ORIGIN) = ({{ORIGIN pdefault_done_{slot}.ORIGIN,VALUE PBOOL {boolean},CLASS PVSCALAR}})',
        ]
    tokens = (['raw:', '1'] + [':', '1'] * 7 + ['|']) * 2
    checks += [
        'S_done.EVENTS = [' + ','.join('OUTPUT $ptascii(' + json.dumps(token) + ')' for token in tokens) + ']',
        r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
    ]
    CASES['deferred-boolean-short-actual-' + name] = {
        'source': ROWS['deferred-boolean-short-wrapper-raw-phases']['source'],
        'stage': (f'S.TODO = (SHORT_RESULT {disjunction} expression_right z_left z_right) :: ptask_tail* '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if $function_at(S.FUNCTIONS,pcallcontext.FUNCTION) = (pfunction) '
                  '-- if pfunction.NAME = $ptascii("rawBooleanShort265") '
                  f'-- if $default_at(pfunction.DEFAULTS,{index}) = (pdefault_root) '
                  '-- if S.ORIGIN = (pdefault_root.ORIGIN) '
                  '-- if pdefault_root.ORIGIN = PORIGIN n_unit pcpath_root'),
        'checks': checks,
    }

named = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("BooleanShort265")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_identity,psparam_negated,psparam_last]',
    r'~psparam_first.BYREF /\ psparam_identity.BYREF /\ psparam_negated.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.HOLES = [1,2] /\ pcallcontext.ARGC = 4',
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    'S.CODE = [pcode]',
]
for label, index, constructor, boolean, value, wrong in [
    ('identity', 1, 'NExprBinaryOpBooleanOr', 'true', '1', '0'),
    ('negated', 2, 'NExprBinaryOpLogicalAnd', 'false', '0', '1'),
]:
    named += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{label})',
        f'porigin_{label} = pdefault_{label}.ORIGIN',
        f'porigin_{label} = PORIGIN n_unit pcpath_{label}',
        f'pcpath_{label}_short = pcpath_{label} ++ [PCFIELD 0]',
        f'porigin_{label}_short = PORIGIN n_unit pcpath_{label}_short',
        f'pcpath_{label}_right = pcpath_{label}_short ++ [PCFIELD 1]',
        f'$origin_node(S.SOURCES,porigin_{label}) = (NExprCastInt expression_{label} metadata_{label})',
        f'$plstyle(metadata_{label}) = 1',
        f'$origin_node(S.SOURCES,porigin_{label}_short) = (expression_{label})',
        f'expression_{label} = {constructor} expression_{label}_left expression_{label}_right metadata_{label}_short',
        f'$origin_node(S.SOURCES,PORIGIN n_unit pcpath_{label}_right) = (expression_{label}_right)',
        f'expression_{label}_right = NExprConstFetch name_{label}_right metadata_{label}_right',
        f'$pnresolve(pfunction.ENV,PLCONSTANT,name_{label}_right) = PNRESOLVED pnreference_{label}_right',
        f'$call_name_count(pcode.NAMES,pcpath_{label}_right) = 1',
        f'$code_name(pcode.NAMES,pcpath_{label}_right) = ((pnreference_{label}_right.RESOLVED,pnreference_{label}_right.FALLBACK))',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit pcpath_{label}_right) = eps',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{label}_short) = (PBOOL {boolean})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{label}) = (PINT {value})',
        f'pdefaultcache_{label} = {{ORIGIN porigin_{label},VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,porigin_{label}) = (pdefaultcache_{label})',
        f'$lookup(S.ENV,psparam_{label}.NAME) = (n_{label})',
        f'S.STORE[n_{label}] = DEFINED (PINT {value})',
        rf'~(n_{label} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_{label}) = 1',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'S_tag_{label} = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{label}[.VALUE = PBOOL {boolean}])]',
        f'$default_caches_valid(S_tag_{label},S_tag_{label}.DEFAULTCACHE)',
        f'~$lossy_optional_integer_deferred(S_tag_{label},pfunction,{index})',
        f'~$lossy_mixed_parameter_source_valid(S_tag_{label},ptask_resume)',
        f'S_value_{label} = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{label}[.VALUE = PINT {wrong}])]',
        f'$default_caches_valid(S_value_{label},S_value_{label}.DEFAULTCACHE)',
        f'~$lossy_optional_integer_deferred(S_value_{label},pfunction,{index})',
        f'~$lossy_mixed_parameter_source_valid(S_value_{label},ptask_resume)',
        f'S_name_{label} = S[.CODE = [pcode[.NAMES = ([(CODENAME pcpath_{label}_right pnreference_{label}_right.RESOLVED pnreference_{label}_right.FALLBACK)] ++ pcode.NAMES)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_name_{label},pfunction.ENV,porigin_{label}) = (PINT {value})',
        f'~$lossy_optional_integer_deferred_bindings(S_name_{label},pfunction.ENV,porigin_{label})',
        f'~$lossy_optional_integer_deferred(S_name_{label},pfunction,{index})',
        f'~$lossy_mixed_parameter_source_valid(S_name_{label},ptask_resume)',
    ]
named += [
    'n_identity =/= n_negated',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 8)',
    '$lossy_mixed_parameter_source_valid(S,ptask_resume)',
    '$call_task_valid(S,ptask_resume)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base265"),$ptascii("E_ERROR")),($ptascii("One265"),$ptascii("E_ERROR"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_identity)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_negated)',
    '~$lossy_optional_integer_header(S,pfunction[.ENV = plenv_wrong],pfunction.SIGNATURE.PARAMETERS,0)',
    '~$lossy_optional_integer_deferred(S[.CURRENT = (pcallcontext[.RECEIVER = (999)])],pfunction,1)',
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
    '$lookup(S_done.ENV,$ptascii("x265")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]
CASES['deferred-boolean-short-private-two-holes-warning-return'] = {
    'source': ROWS['deferred-boolean-short-wrapper-alias-named-reentry']['source'],
    'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
              '-- if ptask_resume = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z'),
    'checks': named,
}

CASES['deferred-boolean-short-ordinary-integer-receive-control'] = {
    'source': ROWS['deferred-boolean-short-wrapper-demanded-integer-control']['source'],
    'stage': ('S.TODO = [TYPE_RECEIVE porigin 0] '
              '-- if $function_at(S.FUNCTIONS,porigin) = (pfunction) '
              '-- if pfunction.NAME = $ptascii("demandedIntegerShort265")'),
    'checks': [
        '$default_at(pfunction.DEFAULTS,0) = (pdefault_root)',
        'pdefault_root.ORIGIN = PORIGIN n_unit pcpath_root',
        '$origin_node(S.SOURCES,pdefault_root.ORIGIN) = (NExprCastInt expression_short metadata_root)',
        '$plstyle(metadata_root) = 1',
        'porigin_short = PORIGIN n_unit (pcpath_root ++ [PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_short) = (expression_short)',
        'expression_short = NExprBinaryOpBooleanOr expression_left expression_right metadata_short',
        '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_root ++ [PCFIELD 0,PCFIELD 1])) = (expression_right)',
        'expression_right = NScalarInt (INTEGER 7) metadata_right',
        '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_root ++ [PCFIELD 0,PCFIELD 0])) = (PBOOL false)',
        '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_root ++ [PCFIELD 0,PCFIELD 1])) = (PINT 7)',
        '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_short) = eps',
        '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_root.ORIGIN) = eps',
        '~$lossy_optional_integer_deferred(S,pfunction,0)',
        '~$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
        '$call_task_valid(S,TYPE_RECEIVE porigin 0)',
        'pfunction.SIGNATURE.PARAMETERS = [psparam_value]',
        'psparam_value.BYREF',
        '$lookup(S.ENV,psparam_value.NAME) = eps',
        '$default_current_cache(S,pdefault_root.ORIGIN) = eps',
        'S_done = $drive_steps(S,3000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        'S_done.EVENTS = [OUTPUT $ptascii("wider:"),OUTPUT $ptascii("1"),OUTPUT $ptascii("|")]',
        '$default_cache_at(S_done.DEFAULTCACHE,pdefault_root.ORIGIN) = ({ORIGIN pdefault_root.ORIGIN,VALUE PINT 1,CLASS PVSCALAR})',
        r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
    ],
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
