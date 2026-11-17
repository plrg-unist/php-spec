#!/usr/bin/env python3
"""Finite FLOAT predicates retain selected tags, exact receipts and private cells."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_finite_nonzero_float_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
values = ['PINT 0', 'PBOOL true', 'PFLOAT 0', 'PFLOAT 9223372036854775808',
          'PFLOAT n_nan', 'PNULL', 'PBOOL true', 'PINT 1']
conditions = [4607182418800017408, 13830554455654793216, 1, 9223372036854775809,
              4503599627370496, 9227875636482146304, 4611686018427387904, 4607182418800017408]
raw = base + ['|pfunction.SIGNATURE.PARAMETERS| = 8', 'S.CODE = [pcode]',
              'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]', '$default_cache_owner(S) = (CACHE_SHARED)']
for index, (value, condition) in enumerate(zip(values, conditions)):
    raw += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'porigin_cond_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
        f'porigin_selected_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])',
        f'porigin_skip_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2])',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (NExprTernary expression_cond_{index} expression_selected_{index} expression_skip_{index} metadata_{index})',
        f'$origin_node(S.SOURCES,porigin_cond_{index}) = (expression_cond_{index})',
        f'$origin_node(S.SOURCES,porigin_selected_{index}) = (expression_selected_{index})',
        f'$origin_node(S.SOURCES,porigin_skip_{index}) = (expression_skip_{index})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_cond_{index}) = (PFLOAT {condition})',
        f'$pool_value(S.POOLS,porigin_cond_{index}) = (PFLOAT {condition})',
        f'$float_decode({condition}) = FINITE n_sign_{index} n_numerator_{index} n_denominator_{index}',
        f'n_numerator_{index} =/= 0',
        f'$lossy_optional_integer_finite_nonzero_float_full_redirect(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ((porigin_cond_{index},porigin_selected_{index}))',
        f'$lossy_optional_integer_nonzero_integer_full_redirect(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ((porigin_cond_{index},porigin_selected_{index}))',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_cond_{index})',
        f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_skip_{index})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_selected_{index}) = ({value})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
        f'S.STORE[n_cell_{index}] = DEFINED ({value})',
        rf'~(n_cell_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_cell_{index}) = 1']
raw += ['$pfcast_nan(PFLOAT n_nan)',
    'S_wrong_cache = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_3[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_cache,S_wrong_cache.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_cache,pfunction,3)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in range(8):
    raw += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_cell_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_cell_{index}) = 0']

forgeries = base + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
    '$default_at(pfunction.DEFAULTS,0) = (pdefault_0)',
    'pdefault_0.ORIGIN = PORIGIN n_unit pcpath_0',
    'porigin_cond_0 = PORIGIN n_unit (pcpath_0 ++ [PCFIELD 0])',
    'porigin_selected_0 = PORIGIN n_unit (pcpath_0 ++ [PCFIELD 1])',
    'porigin_skip_0 = PORIGIN n_unit (pcpath_0 ++ [PCFIELD 2])',
    '$origin_node(S.SOURCES,pdefault_0.ORIGIN) = (NExprTernary expression_cond_0 expression_selected_0 expression_skip_0 metadata_0)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_0) = ((z_0,false))',
    '$lossy_optional_integer_finite_nonzero_float_full_redirect(S,pfunction.ENV,pdefault_0.ORIGIN) = ((porigin_cond_0,porigin_selected_0))']
variants = [
    ('zero', 'NScalarFloat (FLOAT "0000000000000000") eps', 'PFLOAT 0', 'eps'),
    ('negative_zero', 'NScalarFloat (FLOAT "8000000000000000") eps', 'PFLOAT 9223372036854775808', 'eps'),
    ('nan', 'NScalarFloat (FLOAT "7ff8000000000000") eps', 'PFLOAT 9221120237041090560', 'eps'),
    ('positive_infinity', 'NScalarFloat (FLOAT "7ff0000000000000") eps', 'PFLOAT 9218868437227405312', 'eps'),
    ('negative_infinity', 'NScalarFloat (FLOAT "fff0000000000000") eps', 'PFLOAT 18442240474082181120', 'eps'),
    ('integer', 'NScalarInt (INTEGER 1) eps', 'PINT 1', '(PINT 0)'),
    ('boolean', 'NExprConstFetch (NName (BYTES "dHJ1ZQ==") eps) eps', 'PBOOL true', '(PINT 0)'),
]
for name, expression, value, expected in variants:
    forgeries += [f'expression_{name} = {expression}',
        f'S_source_{name} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_0 (NExprTernary expression_{name} expression_selected_0 expression_skip_0 metadata_0)), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_{name})] ++ $pcwalk($pcchildren(expression_{name},pcpath_0 ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
        f'S_{name} = S_source_{name}[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) ({value}))] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,porigin_cond_0) = ({value})',
        f'$lossy_optional_integer_finite_nonzero_float_full_redirect(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = eps',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = {expected}',
        f'~$lossy_optional_integer_deferred(S_{name},pfunction,0)']
for name, bits in [('maximum', 9218868437227405311), ('negative_maximum', 18442240474082181119)]:
    spelling = f'{bits:016x}'
    forgeries += [f'expression_{name} = NScalarFloat (FLOAT "{spelling}") eps',
        f'S_source_{name} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_0 (NExprTernary expression_{name} expression_selected_0 expression_skip_0 metadata_0)), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_{name})] ++ pcunit.OCCURRENCES)]]]',
        f'S_{name} = S_source_{name}[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) (PFLOAT {bits}))] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,porigin_cond_0) = (PFLOAT {bits})',
        f'$lossy_optional_integer_finite_nonzero_float_full_redirect(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = ((porigin_cond_0,porigin_selected_0))',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = (PINT 0)',
        f'~$lossy_optional_integer_deferred(S_{name},pfunction,0)']
forgeries += ['expression_high = NScalarFloat (FLOAT "10000000000000000") eps',
    'S_source_high = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_0 (NExprTernary expression_high expression_selected_0 expression_skip_0 metadata_0)), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_high)] ++ pcunit.OCCURRENCES)]]]',
    'S_high = S_source_high[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) (PFLOAT 18446744073709551616))] ++ ppool.CONSTANTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_high,pfunction.ENV,porigin_cond_0) = eps',
    '$lossy_optional_integer_finite_nonzero_float_full_redirect(S_high,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    '$lossy_optional_integer_deferred_value_at(S_high,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    '~$lossy_optional_integer_deferred(S_high,pfunction,0)']
mutations = {
    'no_redirect': 'S[.CODE = [pcode[.REDIRECTS = eps]]]',
    'duplicate': 'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
    'copy': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_0 (pcpath_0 ++ [PCFIELD 1]) true)]]]]',
    'wrong_target': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_0 (pcpath_0 ++ [PCFIELD 2]) false)]]]]',
    'own_pool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_0 (PINT 0))] ++ ppool.CONSTANTS)]]]',
    'own_code': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_0 z_0 true)] ++ pcode.EXPRESSIONS)]]]',
    'condition_pool_type': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) (PBOOL true))] ++ ppool.CONSTANTS)]]]',
    'condition_pool_bits': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) (PFLOAT 13830554455654793216))] ++ ppool.CONSTANTS)]]]',
    'condition_code': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_0 ++ [PCFIELD 0]) z_0 true)] ++ pcode.EXPRESSIONS)]]]',
    'condition_redirect': 'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT (pcpath_0 ++ [PCFIELD 0]) (pcpath_0 ++ [PCFIELD 1]) false)] ++ pcode.REDIRECTS)]]]',
}
for name, expression in mutations.items():
    forgeries += [f'S_{name} = {expression}',
        f'$lossy_optional_integer_finite_nonzero_float_full_redirect(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = eps',
        (f'~$lossy_optional_integer_deferred_bindings(S_{name},pfunction.ENV,pdefault_0.ORIGIN)' if name == 'wrong_target' else f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = eps'),
        f'~$lossy_optional_integer_deferred(S_{name},pfunction,0)']
for field in range(3):
    forgeries += [f'S_source_arm_{field} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_0 ++ [PCFIELD {field}]) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
        f'$lossy_optional_integer_finite_nonzero_float_full_redirect(S_source_arm_{field},pfunction.ENV,pdefault_0.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_source_arm_{field},pfunction,0)']
forgeries += ['pcoccurrence_kept* = [(PCOCCURRENCE pcpath_0 (NExprTernary expression_cond_0 expression_selected_0 expression_skip_0 metadata_0)), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_cond_0)] ++ $pcwalk($pcchildren(expression_cond_0,pcpath_0 ++ [PCFIELD 0])) ++ [(PCOCCURRENCE (pcpath_0 ++ [PCFIELD 1]) expression_selected_0)] ++ $pcwalk($pcchildren(expression_selected_0,pcpath_0 ++ [PCFIELD 1]))',
    'S_missing = S[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_kept*]]]',
    '$origin_node(S_missing.SOURCES,porigin_skip_0) = eps',
    '$lossy_optional_integer_finite_nonzero_float_full_redirect(S_missing,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    '~$lossy_optional_integer_deferred(S_missing,pfunction,0)']

named = base + ['|pfunction.SIGNATURE.PARAMETERS| = 6', '$default_cache_owner(S) = (CACHE_SHARED)']
for index, condition, value in [(1, 1, 0), (2, 9223372036854775809, 1),
        (3, 4607182418800017408, 0), (4, 13830554455654793216, 0)]:
    named += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD 0])) = (PFLOAT {condition})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT {value})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED (PINT {value})',
        rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
named += ['S_wrong_null = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_4[.VALUE = PNULL])]',
    '$default_caches_valid(S_wrong_null,S_wrong_null.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_null,pfunction,4)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base303"),$ptascii("E_ERROR")),($ptascii("One303"),$ptascii("E_ERROR")),($ptascii("Skipped303"),$ptascii("Unavailable303") ++ [92] ++ $ptascii("Payload"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_1.ORIGIN)',
    'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)']
lifecycle = base + ['|pfunction.SIGNATURE.PARAMETERS| = 6', '$default_cache_owner(S) = (CACHE_SHARED)']
for index, value in [(1, 0), (2, 1), (3, 0), (4, 0)]:
    lifecycle += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED (PINT {value})',
        rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
lifecycle += ['S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps']
for index in (1, 2, 3, 4):
    lifecycle += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
lifecycle += ['$lookup(S_done.ENV,$ptascii("x303")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
false = f'((bool)({chain}))'
truth = f'(!{false})'
nan = f'(NAN + ({chain}))'
null = f'({truth} ? NULL : false)'
quiet_defaults = [(f'(1.0 + 1.0) ? {false} : Missing303', 'PBOOL false'),
                  (f'(-5.0e-324) ? ((1.0) ? {nan} : Missing303) : Missing303', 'PFLOAT n_nan'),
                  (f'(int)(0.5 ? (-0.0 ? Missing303 : {null}) : Missing303)', 'PINT 0')]
quiet = base + ['|pfunction.SIGNATURE.PARAMETERS| = 3', 'S.ERRORHANDLER.CALLBACK =/= eps']
for index, (_, value) in enumerate(quiet_defaults):
    quiet += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_quiet_{index})',
        f'S.STORE[n_quiet_{index}] = DEFINED ({value})']
quiet += ['$pfcast_nan(PFLOAT n_nan)', 'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps',
    'S_done.EVENTS = eps', 'S_done.ERRORHANDLER = S.ERRORHANDLER', '$heap_valid($heap_graph(S_done))']
expressions = [f'"1" ? {false} : Missing303', f'INF ? {false} : Missing303',
               f'(-INF) ? {false} : Missing303', f'NAN ? {false} : Missing303',
               f'1.0 ? ((string){false}) : Missing303', '1.0 ? [] : Missing303']
boundary = base + [f'|pfunction.SIGNATURE.PARAMETERS| = {len(expressions)}']
for index in range(len(expressions)):
    boundary += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S,pfunction,{index})']
context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
raw_source = ROWS['deferred-finite-nonzero-float-full-ternary-redirect-wrapper-raw-tagged-results']['source']
named_source = ROWS['deferred-finite-nonzero-float-full-ternary-redirect-wrapper-alias-named-reentry']['source']
CASES = {
    'finite-nonzero-float-full-independent-raw-tags': {'source': raw_source,
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': raw},
    'finite-nonzero-float-full-independent-forgeries': {'source': raw_source,
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': forgeries},
    'finite-nonzero-float-full-independent-private-recipients': {'source': named_source,
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 1 -- if pcallcontext.FUNCTION = porigin_function '
            '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) -- if pfunction.ENV.NAMESPACE = $ptascii("FiniteFloatRedirect303") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 -- if S.TODO = $function_tasks(S,pfunction)'), 'checks': named},
    'finite-nonzero-float-full-independent-nested-quiet': {'source': '<?php function quietHandler303($e,$m,$f,$l) { echo "unexpected-warning|"; } function quietFiniteFloat303(' + ', '.join(f'$p{i}=({e})' for i,(e,_) in enumerate(quiet_defaults)) + ') {} set_error_handler("quietHandler303"); quietFiniteFloat303(); quietFiniteFloat303();',
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 3 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': quiet},
    'finite-nonzero-float-full-independent-current-boundaries': {'source': '<?php function refused303(' + ', '.join(f'$p{i}=({e})' for i,e in enumerate(expressions)) + ') {} refused303(' + ','.join('0' for _ in expressions) + ');',
        'stage': context.replace('pcallcontext.ARGC = 0', f'pcallcontext.ARGC = {len(expressions)}') + f'-- if |pfunction.SIGNATURE.PARAMETERS| = {len(expressions)} -- if S.TODO = $function_tasks(S,pfunction)', 'checks': boundary},
}
CASES['finite-nonzero-float-full-independent-private-lifecycle'] = dict(CASES['finite-nonzero-float-full-independent-private-recipients'], checks=lifecycle)
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
