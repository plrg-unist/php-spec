#!/usr/bin/env python3
"""Independent selected tags and pooled name-pruning receipt authority."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_boolean_selection_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

operands = [
    ('NExprBinaryOpEqual', 0, 'PBOOL false', 'PINT 0', 'PBOOL true'),
    ('NExprBinaryOpNotEqual', 1, 'PBOOL false', 'PFLOAT 0', 'PBOOL false'),
    ('NExprBinaryOpEqual', 0, 'PBOOL true', 'PFLOAT n_nan_2', 'PBOOL true'),
    ('NExprBinaryOpNotEqual', 1, 'PBOOL true', 'PFLOAT n_nan_3', 'PBOOL false'),
    ('NExprBinaryOpSmaller', 0, 'PBOOL false', 'PFLOAT n_nan_4', 'PBOOL true'),
    ('NExprBinaryOpSmallerOrEqual', 1, 'PBOOL true', 'PFLOAT n_nan_5', 'PBOOL true'),
    ('NExprBinaryOpGreater', 0, 'PBOOL true', 'PFLOAT 9218868437227405312', 'PBOOL false'),
    ('NExprBinaryOpGreaterOrEqual', 1, 'PBOOL false', 'PFLOAT 18442240474082181120', 'PBOOL true'),
    ('NExprBinaryOpSpaceship', 0, 'PBOOL false', 'PBOOL true', 'PINT $(-1)'),
    ('NExprBinaryOpSpaceship', 1, 'PBOOL true', 'PBOOL false', 'PINT $(-1)'),
    ('NExprBinaryOpSpaceship', 0, 'PBOOL true', 'PFLOAT n_nan_10', 'PINT 0'),
    ('NExprBinaryOpSpaceship', 1, 'PBOOL false', 'PFLOAT n_nan_11', 'PINT 1'),
    ('NExprBinaryOpIdentical', 0, 'PBOOL false', 'PBOOL false', 'PBOOL true'),
    ('NExprBinaryOpIdentical', 0, 'PINT 1', 'PINT 1', 'PBOOL true'),
    ('NExprBinaryOpIdentical', 0, 'PBOOL true', 'PINT 1', 'PBOOL false'),
    ('NExprBinaryOpNotIdentical', 1, 'PBOOL false', 'PINT 0', 'PBOOL true'),
]
base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
raw = base + ['|pfunction.SIGNATURE.PARAMETERS| = 16', 'S.CODE = [pcode]',
              'S.SOURCES = [pcunit]', 'S.POOLS = [ppool]']
for index, (constructor, field, selected, sibling, result) in enumerate(operands):
    raw += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = ({constructor} expression_left_{index} expression_right_{index} metadata_{index})',
        f'porigin_selection_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {field}])',
        f'$origin_node(S.SOURCES,porigin_selection_{index}) = (expression_selection_{index})',
        f'$lossy_optional_integer_selection_shape(expression_selection_{index})',
        f'$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_selection_{index})',
        f'$lossy_optional_integer_deferred_value(pfunction.ENV,expression_selection_{index}) = ({selected})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_selection_{index}) = ({selected})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {1-field}])) = ({sibling})',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index}) = ((z_{index},false))',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({result})',
        f'{"~" if index == 13 else ""}$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {result},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
        f'S.STORE[n_cell_{index}] = DEFINED ({result})',
    ]
    if 'n_nan_' in sibling:
        raw.append(f'$pfcast_nan({sibling})')
raw += [
    '$origin_node(S.SOURCES,porigin_selection_0) = (NExprTernary expression_true expression_false expression_unused metadata_selector)',
    '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_2 ++ [PCFIELD 1])) = (NExprBinaryOpPlus expression_nan_leaf expression_zero metadata_nan)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_nan_leaf) = (NFLOAT 9221120237041090560)',
    '$lossy_optional_integer_deferred_value(pfunction.ENV,NExprTernary expression_nan_leaf expression_true expression_false eps) = eps',
    '$lossy_optional_integer_deferred_value(pfunction.ENV,NExprTernary expression_nan_leaf ABSENT expression_false eps) = eps',
    r'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_selection_13) = eps /\ ~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_selection_13)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_8[.VALUE = PBOOL true])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,8)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]
for index in range(16):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

named = base + ['pfunction.ENV.NAMESPACE = $ptascii("BooleanSelection287")',
    'S.CODE = [pcode]', 'S.SOURCES = [pcunit]', 'S.POOLS = [ppool]',
    '$default_cache_owner(S) = (CACHE_SHARED)']
# index, selection side, chosen field, skipped field, condition, result, cache
receipts = [(1, 0, 1, 2, 'true', 'false', '1'),
            (2, 1, 2, 1, 'false', 'true', '1'),
            (3, 0, 0, 2, 'true', 'true', '0'),
            (4, 1, 0, 1, 'false', 'false', '1')]
for index, side, chosen, skipped, condition, result, value in receipts:
    named += [
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_default_{index}',
        f'pcpath_selection_{index} = pcpath_default_{index} ++ [PCFIELD 0,PCFIELD {side}]',
        f'porigin_selection_{index} = PORIGIN n_unit pcpath_selection_{index}',
        f'porigin_condition_{index} = PORIGIN n_unit (pcpath_selection_{index} ++ [PCFIELD 0])',
        f'porigin_chosen_{index} = PORIGIN n_unit (pcpath_selection_{index} ++ [PCFIELD {chosen}])',
        f'pcpath_unused_{index} = pcpath_selection_{index} ++ [PCFIELD {skipped}]',
        f'porigin_unused_{index} = PORIGIN n_unit pcpath_unused_{index}',
        f'$origin_node(S.SOURCES,porigin_unused_{index}) = (expression_unused_{index})',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_selection_{index}) = ((z_selection_{index},true))',
        f'$compiled_read(S,porigin_selection_{index}) = (PBOOL {result})',
        f'$pool_value(S.POOLS,porigin_condition_{index}) = (PBOOL {condition})',
        f'$pool_value(S.POOLS,porigin_chosen_{index}) = (PBOOL {result})',
        f'$pool_value(S.POOLS,porigin_unused_{index}) = eps',
        f'$call_name_count(pcode.NAMES,pcpath_unused_{index}) = 0',
        f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_unused_{index})',
        f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_selection_{index}) = 0',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_selection_{index}) = (PBOOL {result})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED (PINT {value})',
        rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1',
        f'S_code_{index} = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_selection_{index} z_selection_{index} false)] ++ pcode.EXPRESSIONS)]]]',
        f'~$lossy_optional_integer_deferred_bindings(S_code_{index},pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'S_redirect_{index} = S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath_selection_{index} (pcpath_selection_{index} ++ [PCFIELD 0]) false)] ++ pcode.REDIRECTS)]]]',
        f'~$lossy_optional_integer_deferred_bindings(S_redirect_{index},pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'S_cond_pool_{index} = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_selection_{index} ++ [PCFIELD 0]) (PBOOL {"false" if condition == "true" else "true"}))] ++ ppool.CONSTANTS)]]]',
        f'~$lossy_optional_integer_deferred_bindings(S_cond_pool_{index},pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'S_unused_{index} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_unused_{index} (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_unused_{index},pfunction.ENV,porigin_selection_{index}) = (PBOOL {result})',
        f'~$lossy_optional_integer_deferred_children(S_unused_{index},pfunction.ENV,n_unit,[(PCOCCURRENCE pcpath_unused_{index} expression_unused_{index})])',
        f'~$lossy_optional_integer_deferred_bindings(S_unused_{index},pfunction.ENV,pdefault_{index}.ORIGIN)',
    ]
    if index == 4:
        named.append(f'$lossy_optional_integer_pruned_short(S,pfunction.ENV,porigin_selection_{index}) = (porigin_chosen_{index})')
    else:
        named.append(f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_selection_{index}) = ((porigin_condition_{index},porigin_chosen_{index}))')
named += [
    'plenv_skip = pfunction.ENV[.CONSTANTS = [($ptascii("Base287"),$ptascii("E_WARNING")),($ptascii("One287"),$ptascii("E_ERROR")),($ptascii("Nan287"),$ptascii("Other287"))]]',
    '$lossy_optional_integer_deferred_bindings(S,plenv_skip,porigin_selection_1)',
    '$lossy_optional_integer_deferred_bindings(S,plenv_skip,porigin_selection_4)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_skip,pdefault_2.ORIGIN)',
    'S_absent = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_selection_3 ++ [PCFIELD 1]) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
    '$lossy_optional_integer_pruned_ternary(S_absent,pfunction.ENV,porigin_selection_3) = eps',
    '~$lossy_optional_integer_deferred_bindings(S_absent,pfunction.ENV,pdefault_3.ORIGIN)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]
for index, *_ in receipts:
    named += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
              rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']

chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
truth = f'(!((bool)({chain})))'
float_source = (f'<?php function floats287($p0 = ((true ? 1.0 : false) === ((int)({truth}))), '
                f'$p1 = ({truth} ? 1.0 : 2.0), $p2 = ((NULL ?? 1.0) >= {truth})) {{}} floats287();')
floats = base + ['|pfunction.SIGNATURE.PARAMETERS| = 3']
for index, result in enumerate(['PBOOL false', 'PFLOAT 4607182418800017408', 'PBOOL true']):
    floats += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
               f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({result})',
               f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_float_{index})',
               f'S.STORE[n_float_{index}] = DEFINED ({result})']
for index in (0, 2):
    floats += [f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
               f'porigin_float_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
               f'$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_float_{index})',
               f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_float_{index}) = (PFLOAT 4607182418800017408)']
floats += ['~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_1.ORIGIN)']

refused = base + ['|pfunction.SIGNATURE.PARAMETERS| = 2']
for index in range(2):
    refused += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
                f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
                f'~$lossy_optional_integer_deferred(S,pfunction,{index})']
stage = ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 '
         '-- if pcallcontext.FUNCTION = porigin_function '
         '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
CASES = {
    'deferred-boolean-selection-wrapper-raw-tagged-results': {
        'source': ROWS['deferred-boolean-selection-wrapper-raw-tagged-results']['source'],
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 16 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks': raw,
    },
    'deferred-boolean-selection-wrapper-named-receipt-authority': {
        'source': ROWS['deferred-boolean-selection-wrapper-alias-named-reentry']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 1 '
                  '-- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if pfunction.ENV.NAMESPACE = $ptascii("BooleanSelection287") '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 -- if S.TODO = $function_tasks(S,pfunction)'),
        'checks': named,
    },
    'deferred-boolean-selection-wrapper-derived-float-tags': {
        'source': float_source,
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 3 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks': floats,
    },
    'deferred-boolean-selection-wrapper-current-unprojected-tags': {
        'source': f'<?php function refused287($p0 = ((true ? NULL : false) == ((int)({chain}))), $p1 = (("0" ?? false) != ((int)({chain})))) {{}} refused287();',
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 2',
        'checks': refused,
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
