#!/usr/bin/env python3
"""Independent selected ternary values, skipped source and private receives."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_boolean_ternary_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

raw = ['$code_at(S.CODE,n_unit) = (pcode)', 'S.SOURCES = [pcunit]',
       'S.RESULT = KNOWN (PBOOL false)', '$default_cache_owner(S) = (CACHE_SHARED)']
values = ['PBOOL true','PBOOL false','PBOOL true','PINT 2','PFLOAT 4611686018427387904','PINT 2']
for index, condition, shorthand, selected, skipped in [
    (0,'false',False,2,1), (1,'true',False,1,2), (2,'true',True,0,2),
    (3,'false',True,2,None), (4,'true',False,1,2), (5,'false',False,2,1),
]:
    true_arm = 'ABSENT' if shorthand else f'expression_true_{index}'
    raw += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (NExprTernary expression_cond_{index} {true_arm} expression_false_{index} metadata_{index})',
        f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = (expression_cond_{index})',
        f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2])) = (expression_false_{index})',
        (f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])) = eps' if shorthand else
         f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])) = (expression_true_{index})'),
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index}) = ((z_{index},false))',
        rf'$pool_value(S.POOLS,pdefault_{index}.ORIGIN) = eps /\ $compiled_read(S,pdefault_{index}.ORIGIN) = eps',
        f'$compiled_redirect(S,pdefault_{index}.ORIGIN) = eps',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = (PBOOL {condition})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {selected}])) = ({values[index]})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({values[index]})',
        f'S_cond_code_{index} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_{index} ++ [PCFIELD 0]) z_{index} true)] ++ pcode.EXPRESSIONS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_cond_code_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'S_cond_source_{index} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_{index} ++ [PCFIELD 0]) (NExprBooleanNot expression_cond_{index} eps))] ++ pcunit.OCCURRENCES)]]]',
        f'~$lossy_optional_integer_phase_safe(S_cond_source_{index},pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S_cond_source_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
    ]
    if index == 3:
        raw += [
            'S_literal_cond = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_3 ++ [PCFIELD 0]) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
            '$lossy_optional_integer_phase_safe(S_literal_cond,pfunction.ENV,pdefault_3.ORIGIN)',
            '$lossy_optional_integer_deferred_value_at(S_literal_cond,pfunction.ENV,pdefault_3.ORIGIN) = (PINT 2)',
        ]
    if selected != 0:
        raw += [
            f'S_selected_source_{index} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_{index} ++ [PCFIELD {selected}]) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
            f'$lossy_optional_integer_deferred_value_at(S_selected_source_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        ]
    if skipped is not None:
        raw += [
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {skipped}])) = eps',
            f'S_skip_code_{index} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_{index} ++ [PCFIELD {skipped}]) z_{index} true)] ++ pcode.EXPRESSIONS)]]]',
            f'$lossy_optional_integer_deferred_value_at(S_skip_code_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = ({values[index]})',
            f'S_skip_source_{index} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_{index} ++ [PCFIELD {skipped}]) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
            f'$lossy_optional_integer_deferred_value_at(S_skip_source_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        ]
    raw += [
        f'S_choice_{index} = S[.ORIGIN = (pdefault_{index}.ORIGIN)][.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL {condition})][.BASE = BASE_VALUE (KNOWN (PINT 42))]',
    ]
    if shorthand and selected == 0:
        delta = '[.BASE = BASE_VALUE (KNOWN PNULL)]'
    else:
        chosen = f'expression_true_{index}' if selected == 1 else f'expression_false_{index}'
        line = 'z_true' if selected == 1 else 'z_false'
        delta = (f'[.TODO = [$at_task($origin_child(S_choice_{index}.ORIGIN,[PCFIELD {selected}]),EVAL {chosen}),'
                 f'VALUE_COPY {line}] ++ ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]')
    raw += [f'$select_value(S_choice_{index},{true_arm},expression_false_{index},z_cond,z_true,z_false) = S_choice_{index}' + delta]
raw += [
    'S.ORIGIN = (pdefault_0.ORIGIN)',
    '$default_current_cache(S,pdefault_0.ORIGIN) = eps',
    'S_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_0 z_0 true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_code,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    '$pool_at(S.POOLS,n_unit) = (ppool)',
    'S_pool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_0 (PBOOL true))] ++ ppool.CONSTANTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_pool,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    'S_redirect = S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath_0 (pcpath_0 ++ [PCFIELD 2]) false)] ++ pcode.REDIRECTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_redirect,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.SOURCES = eps],pfunction.ENV,pdefault_0.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S[.CODE = eps],pfunction.ENV,pdefault_0.ORIGIN) = eps',
    'S_budget = $drive_steps(S,0)',
    '$lossy_optional_integer_deferred_value_at(S_budget,pfunction.ENV,pdefault_0.ORIGIN) = (PBOOL true)',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_after',
    'S_after = S_choice_0[.TODO = [$at_task($origin_child(S.ORIGIN,[PCFIELD 2]),EVAL expression_false_0),VALUE_COPY z_false] ++ ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    'S_done = $drive_steps(S_after,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.CONSTCONTEXT = eps',
]
for index, value in enumerate(values):
    raw += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = ({{ORIGIN pdefault_{index}.ORIGIN,VALUE {value},CLASS PVSCALAR}})']
raw += [
    'S_done.EVENTS = [' + ','.join('OUTPUT $ptascii(' + json.dumps(token) + ')' for token in
                                 ((['raw:', '1'] + [':', '1'] * 5 + ['|']) * 2)) + ']',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]
CASES = {'deferred-boolean-ternary-actual-select-value': {
    'source': ROWS['deferred-boolean-ternary-wrapper-raw-phases']['source'],
    'stage': ('S.TODO = (SELECT_VALUE expression_true expression_false z_cond z_true z_false) :: ptask_tail* '
              '-- if S.CURRENT = (pcallcontext) '
              '-- if $function_at(S.FUNCTIONS,pcallcontext.FUNCTION) = (pfunction) '
              '-- if pfunction.NAME = $ptascii("rawBooleanTernary267") '
              '-- if $default_at(pfunction.DEFAULTS,0) = (pdefault_root) '
              '-- if S.ORIGIN = (pdefault_root.ORIGIN) '
              '-- if pdefault_root.ORIGIN = PORIGIN n_unit pcpath_root'),
    'checks': raw,
}}

named = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("BooleanTernary267")',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_identity,psparam_negated,psparam_last]',
    r'~psparam_first.BYREF /\ psparam_identity.BYREF /\ psparam_negated.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.HOLES = [1,2] /\ pcallcontext.ARGC = 4',
    r'n_bits = 4609434218613702656 /\ i = 1',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    'S.CODE = [pcode]',
]
for label, index, selected, skipped, boolean, value, wrong in [
    ('identity',1,1,2,'true','1','0'), ('negated',2,2,1,'false','0','1'),
]:
    named += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{label})',
        f'porigin_{label} = pdefault_{label}.ORIGIN',
        f'porigin_{label} = PORIGIN n_unit pcpath_{label}',
        f'$origin_node(S.SOURCES,porigin_{label}) = (NExprCastInt expression_{label} metadata_{label})',
        f'$plstyle(metadata_{label}) = 1',
        f'pcpath_{label}_ternary = pcpath_{label} ++ [PCFIELD 0]',
        f'pcpath_{label}_skipped = pcpath_{label}_ternary ++ [PCFIELD {skipped}]',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{label}_ternary ++ [PCFIELD 0])) = (PBOOL {boolean})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{label}_ternary ++ [PCFIELD {selected}])) = (PBOOL {boolean})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit pcpath_{label}_skipped) = eps',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit pcpath_{label}_ternary) = (PBOOL {boolean})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_{label}) = (PINT {value})',
        f'$origin_node(S.SOURCES,PORIGIN n_unit pcpath_{label}_skipped) = (NExprConstFetch name_{label}_skipped metadata_{label}_skipped)',
        f'$pnresolve(pfunction.ENV,PLCONSTANT,name_{label}_skipped) = PNRESOLVED pnreference_{label}_skipped',
        f'$call_name_count(pcode.NAMES,pcpath_{label}_skipped) = 1',
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
        f'S_name_{label} = S[.CODE = [pcode[.NAMES = ([(CODENAME pcpath_{label}_skipped pnreference_{label}_skipped.RESOLVED pnreference_{label}_skipped.FALLBACK)] ++ pcode.NAMES)]]]',
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
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base267"),$ptascii("E_ERROR")),($ptascii("One267"),$ptascii("E_ERROR"))]]',
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
    '$lookup(S_done.ENV,$ptascii("x267")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
]
CASES['deferred-boolean-ternary-private-two-holes-warning-return'] = {
    'source': ROWS['deferred-boolean-ternary-wrapper-alias-named-reentry']['source'],
    'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
              '-- if ptask_resume = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z'),
    'checks': named,
}
CASES['deferred-boolean-ternary-ordinary-float-condition-control'] = {
    'source': ROWS['deferred-boolean-ternary-wrapper-float-condition-control']['source'],
    'stage': ('S.TODO = [TYPE_RECEIVE porigin 0] '
              '-- if $function_at(S.FUNCTIONS,porigin) = (pfunction) '
              '-- if pfunction.NAME = $ptascii("ordinaryFloatTernary267")'),
    'checks': [
        '$default_at(pfunction.DEFAULTS,0) = (pdefault_root)',
        'pdefault_root.ORIGIN = PORIGIN n_unit pcpath_root',
        '$origin_node(S.SOURCES,pdefault_root.ORIGIN) = (NExprCastInt expression_ternary metadata_root)',
        '$plstyle(metadata_root) = 1',
        'porigin_ternary = PORIGIN n_unit (pcpath_root ++ [PCFIELD 0])',
        '$origin_node(S.SOURCES,porigin_ternary) = (expression_ternary)',
        'expression_ternary = NExprTernary expression_cond ABSENT expression_false metadata_ternary',
        '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_root ++ [PCFIELD 0,PCFIELD 0])) = (PFLOAT 0)',
        '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_ternary) = eps',
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
        'S_done.EVENTS = [OUTPUT $ptascii("ordinary:"),OUTPUT $ptascii("7"),OUTPUT $ptascii("|")]',
        '$default_cache_at(S_done.DEFAULTCACHE,pdefault_root.ORIGIN) = ({ORIGIN pdefault_root.ORIGIN,VALUE PINT 7,CLASS PVSCALAR})',
        r'$call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE) /\ $heap_valid($heap_graph(S_done))',
    ],
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__),CATALOGUE), runner_flags=('--sl',))
