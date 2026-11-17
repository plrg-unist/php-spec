#!/usr/bin/env python3
"""Computed FLOAT predicates retain selected tags, exact receipts and private cells."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_computed_infinite_float_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
values = ['PINT 0', 'PBOOL true', 'PFLOAT 0', 'PFLOAT 9223372036854775808',
          'PFLOAT n_nan', 'PNULL', 'PBOOL true', 'PINT 1']
conditions = [9218868437227405312, 18442240474082181120, 9218868437227405312, 18442240474082181120,
              9218868437227405312, 18442240474082181120, 9218868437227405312, 18442240474082181120]
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
        f'$lossy_optional_integer_float_literal(expression_cond_{index}) = eps',
        f'$float_decode({condition}) = INFINITE n_sign_{index}',
        f'$pfshape(expression_cond_{index}) = PFBINARY pbin_{index} expression_left_{index} expression_right_{index}',
        f'pbin_{index} = ' + ['ADD','ADD','SUBTRACT','SUBTRACT','MULTIPLY','MULTIPLY','DIVIDE','DIVIDE'][index],
        f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD 0])) = (expression_left_{index})',
        f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD 1])) = (expression_right_{index})',
        f'$lossy_optional_integer_float_literal(expression_left_{index}) = (n_left_{index})',
        f'$lossy_optional_integer_float_literal(expression_right_{index}) = (n_right_{index})',
        f'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD 0])) = (PFLOAT n_left_{index})',
        f'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD 1])) = (PFLOAT n_right_{index})',
        f'$number_binary(pbin_{index},NFLOAT n_left_{index},NFLOAT n_right_{index}) = NUM (NFLOAT {condition})',
        f'$lossy_optional_integer_infinite_float_full_redirect(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'$lossy_optional_integer_computed_infinite_float_full_redirect(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ((porigin_cond_{index},porigin_selected_{index}))',
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
    '$lossy_optional_integer_computed_infinite_float_full_redirect(S,pfunction.ENV,pdefault_0.ORIGIN) = ((porigin_cond_0,porigin_selected_0))']
forgeries += ['expression_cond_0 = NExprBinaryOpPlus expression_left_0 expression_right_0 metadata_cond_0',
    '$lossy_optional_integer_float_literal(expression_left_0) = (n_left_0)',
    '$lossy_optional_integer_float_literal(expression_right_0) = (n_right_0)']
variants = [
    ('zero', 'NScalarFloat (FLOAT "0000000000000000") eps', 'PFLOAT 0', 'eps'),
    ('negative_zero', 'NScalarFloat (FLOAT "8000000000000000") eps', 'PFLOAT 9223372036854775808', 'eps'),
    ('nan', 'NScalarFloat (FLOAT "7ff8000000000000") eps', 'PFLOAT 9221120237041090560', 'eps'),
    ('positive_infinity', 'NScalarFloat (FLOAT "7ff0000000000000") eps', 'PFLOAT 9218868437227405312', '(PINT 0)'),
    ('negative_infinity', 'NScalarFloat (FLOAT "fff0000000000000") eps', 'PFLOAT 18442240474082181120', '(PINT 0)'),
    ('integer', 'NScalarInt (INTEGER 1) eps', 'PINT 1', '(PINT 0)'),
    ('boolean', 'NExprConstFetch (NName (BYTES "dHJ1ZQ==") eps) eps', 'PBOOL true', '(PINT 0)'),
]
for name, expression, value, expected in variants:
    forgeries += [f'expression_{name} = {expression}',
        f'S_source_{name} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_0 (NExprTernary expression_{name} expression_selected_0 expression_skip_0 metadata_0)), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_{name})] ++ $pcwalk($pcchildren(expression_{name},pcpath_0 ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
        f'S_{name} = S_source_{name}[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) ({value}))] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,porigin_cond_0) = ({value})',
        f'$lossy_optional_integer_computed_infinite_float_full_redirect(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = eps',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = {expected}',
        f'~$lossy_optional_integer_deferred(S_{name},pfunction,0)']
for name, bits in [('maximum', 9218868437227405311), ('negative_maximum', 18442240474082181119)]:
    spelling = f'{bits:016x}'
    forgeries += [f'expression_{name} = NScalarFloat (FLOAT "{spelling}") eps',
        f'S_source_{name} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_0 (NExprTernary expression_{name} expression_selected_0 expression_skip_0 metadata_0)), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_{name})] ++ pcunit.OCCURRENCES)]]]',
        f'S_{name} = S_source_{name}[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) (PFLOAT {bits}))] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,porigin_cond_0) = (PFLOAT {bits})',
        f'$lossy_optional_integer_computed_infinite_float_full_redirect(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = eps',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = (PINT 0)',
        f'~$lossy_optional_integer_deferred(S_{name},pfunction,0)']
forgeries += ['expression_high = NScalarFloat (FLOAT "10000000000000000") eps',
    'S_source_high = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_0 (NExprTernary expression_high expression_selected_0 expression_skip_0 metadata_0)), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_high)] ++ pcunit.OCCURRENCES)]]]',
    'S_high = S_source_high[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) (PFLOAT 18446744073709551616))] ++ ppool.CONSTANTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_high,pfunction.ENV,porigin_cond_0) = eps',
    '$lossy_optional_integer_computed_infinite_float_full_redirect(S_high,pfunction.ENV,pdefault_0.ORIGIN) = eps',
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
        f'$lossy_optional_integer_computed_infinite_float_full_redirect(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = eps',
        (f'~$lossy_optional_integer_deferred_bindings(S_{name},pfunction.ENV,pdefault_0.ORIGIN)' if name == 'wrong_target' else f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = eps'),
        f'~$lossy_optional_integer_deferred(S_{name},pfunction,0)']
for field in range(3):
    forgeries += [f'S_source_arm_{field} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_0 ++ [PCFIELD {field}]) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
        f'$lossy_optional_integer_computed_infinite_float_full_redirect(S_source_arm_{field},pfunction.ENV,pdefault_0.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_source_arm_{field},pfunction,0)']
forgeries += ['pcoccurrence_kept* = [(PCOCCURRENCE pcpath_0 (NExprTernary expression_cond_0 expression_selected_0 expression_skip_0 metadata_0)), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_cond_0)] ++ $pcwalk($pcchildren(expression_cond_0,pcpath_0 ++ [PCFIELD 0])) ++ [(PCOCCURRENCE (pcpath_0 ++ [PCFIELD 1]) expression_selected_0)] ++ $pcwalk($pcchildren(expression_selected_0,pcpath_0 ++ [PCFIELD 1]))',
    'S_missing = S[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_kept*]]]',
    '$origin_node(S_missing.SOURCES,porigin_skip_0) = eps',
    '$lossy_optional_integer_computed_infinite_float_full_redirect(S_missing,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    '~$lossy_optional_integer_deferred(S_missing,pfunction,0)']

named = base + ['|pfunction.SIGNATURE.PARAMETERS| = 6', '$default_cache_owner(S) = (CACHE_SHARED)']
for index, condition, value in [(1, 9218868437227405312, 0), (2, 18442240474082181120, 1),
        (3, 9218868437227405312, 0), (4, 18442240474082181120, 0)]:
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
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base306"),$ptascii("E_ERROR")),($ptascii("One306"),$ptascii("E_ERROR")),($ptascii("Skipped306"),$ptascii("Unavailable306") ++ [92] ++ $ptascii("Payload"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_1.ORIGIN)',
    'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)']
# A computed FLOAT pair is admitted; a bare named condition remains outside.
for name, expression in [
    ('computed', 'NExprBinaryOpPlus (NScalarFloat (FLOAT "7ff0000000000000") eps) (NScalarFloat (FLOAT "0000000000000000") eps) eps'),
    ('named', 'NExprConstFetch (NName (BYTES "SU5G") eps) eps'),
]:
    forgeries += [f'expression_{name} = {expression}',
        f'S_source_{name} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_0 (NExprTernary expression_{name} expression_selected_0 expression_skip_0 metadata_0)), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_{name})] ++ $pcwalk($pcchildren(expression_{name},pcpath_0 ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
        f'S_{name} = S_source_{name}[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) (PFLOAT 9218868437227405312)), (PCONSTANT (pcpath_0 ++ [PCFIELD 0,PCFIELD 0]) (PFLOAT 9218868437227405312)), (PCONSTANT (pcpath_0 ++ [PCFIELD 0,PCFIELD 1]) (PFLOAT 0))] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_float_literal(expression_{name}) = eps',
        f'$lossy_optional_integer_computed_infinite_float_full_redirect(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = ' + ('((porigin_cond_0,porigin_selected_0))' if name == 'computed' else 'eps'),
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = ' + ('(PINT 0)' if name == 'computed' else 'eps'),
        f'~$lossy_optional_integer_deferred(S_{name},pfunction,0)']
forgeries += ['$lossy_optional_integer_deferred_value_at(S_computed,pfunction.ENV,porigin_cond_0) = (PFLOAT 9218868437227405312)']
named += ['S_wrong_bool = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_1[.VALUE = PBOOL false])]',
    '$default_caches_valid(S_wrong_bool,S_wrong_bool.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_bool,pfunction,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps']
for index in (1,2,3,4):
    named += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
named += ['$lookup(S_done.ENV,$ptascii("x306")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
# Operand type, operator result and exact child receipts remain independent.
for name, expression, entries, value, selected in [
    ('integer_child', 'NExprBinaryOpPlus (NScalarFloat (FLOAT "7ff0000000000000") eps) (NScalarInt (INTEGER 0) eps) eps', [('0','PFLOAT 9218868437227405312'),('1','PINT 0')], 'PFLOAT 9218868437227405312', '(PINT 0)'),
    ('string_child', 'NExprBinaryOpPlus (NScalarFloat (FLOAT "7ff0000000000000") eps) (NScalarString (BYTES "MA==") eps) eps', [('0','PFLOAT 9218868437227405312'),('1','PSTRING ([48])')], 'PFLOAT 9218868437227405312', 'eps'),
    ('nested_child', 'NExprBinaryOpPlus (NExprBinaryOpPlus (NScalarFloat (FLOAT "7ff0000000000000") eps) (NScalarFloat (FLOAT "0000000000000000") eps) eps) (NScalarFloat (FLOAT "0000000000000000") eps) eps', [('0','PFLOAT 9218868437227405312'),('1','PFLOAT 0'),('0,PCFIELD 0','PFLOAT 9218868437227405312'),('0,PCFIELD 1','PFLOAT 0')], 'PFLOAT 9218868437227405312', 'eps'),
    ('finite', 'NExprBinaryOpPlus (NScalarFloat (FLOAT "3ff0000000000000") eps) (NScalarFloat (FLOAT "3ff0000000000000") eps) eps', [('0','PFLOAT 4607182418800017408'),('1','PFLOAT 4607182418800017408')], 'PFLOAT 4611686018427387904', '(PINT 0)'),
]:
    constants = [f'(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) ({value}))'] + [f'(PCONSTANT (pcpath_0 ++ [PCFIELD 0,PCFIELD {path}]) ({operand}))' for path,operand in entries]
    forgeries += [f'expression_{name} = {expression}',
        f'S_source_{name} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_0 (NExprTernary expression_{name} expression_selected_0 expression_skip_0 metadata_0)), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_{name})] ++ $pcwalk($pcchildren(expression_{name},pcpath_0 ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
        f'S_{name} = S_source_{name}[.POOLS = [ppool[.CONSTANTS = ([' + ','.join(constants) + '] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,porigin_cond_0) = ({value})',
        f'$lossy_optional_integer_computed_infinite_float_full_redirect(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = eps',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = {selected}',
        f'~$lossy_optional_integer_deferred(S_{name},pfunction,0)']
for name, expression in {
    'left_pool_sign': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0,PCFIELD 0]) (PFLOAT $float_neg(n_left_0)))] ++ ppool.CONSTANTS)]]]',
    'right_pool_type': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0,PCFIELD 1]) (PINT 1))] ++ ppool.CONSTANTS)]]]',
    'left_code': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_0 ++ [PCFIELD 0,PCFIELD 0]) z_0 false)] ++ pcode.EXPRESSIONS)]]]',
    'right_code': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_0 ++ [PCFIELD 0,PCFIELD 1]) z_0 false)] ++ pcode.EXPRESSIONS)]]]',
    'left_redirect': 'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT (pcpath_0 ++ [PCFIELD 0,PCFIELD 0]) (pcpath_0 ++ [PCFIELD 1]) false)] ++ pcode.REDIRECTS)]]]',
    'right_redirect': 'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT (pcpath_0 ++ [PCFIELD 0,PCFIELD 1]) (pcpath_0 ++ [PCFIELD 1]) false)] ++ pcode.REDIRECTS)]]]',
}.items():
    forgeries += [f'S_{name} = {expression}',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,porigin_cond_0) = (PFLOAT 9218868437227405312)',
        f'$lossy_optional_integer_computed_infinite_float_full_redirect(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_{name},pfunction,0)']
forgeries += [
    'expression_unary_left = NExprUnaryPlus expression_left_0 eps',
    'expression_unary = NExprBinaryOpPlus expression_unary_left expression_right_0 metadata_cond_0',
    'S_unary_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_0 (NExprTernary expression_unary expression_selected_0 expression_skip_0 metadata_0)), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_unary)] ++ $pcwalk($pcchildren(expression_unary,pcpath_0 ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
    'S_unary = S_unary_source[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0,PCFIELD 0,PCFIELD 0]) (PFLOAT n_left_0))] ++ ppool.CONSTANTS)]]]',
    '$lossy_optional_integer_computed_infinite_float_full_redirect(S_unary,pfunction.ENV,pdefault_0.ORIGIN) = ((porigin_cond_0,porigin_selected_0))',
    'S_deep = S_unary[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0,PCFIELD 0,PCFIELD 0]) (NScalarFloat (FLOAT "0000000000000000") eps))] ++ $pcwalk($pcchildren(expression_unary,pcpath_0 ++ [PCFIELD 0])) ++ [(PCOCCURRENCE pcpath_0 (NExprTernary expression_unary expression_selected_0 expression_skip_0 metadata_0)),(PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_unary)] ++ pcunit.OCCURRENCES)]]]',
    '~$lossy_optional_integer_deferred_bindings(S_deep,pfunction.ENV,porigin_cond_0)',
    '$lossy_optional_integer_computed_infinite_float_full_redirect(S_deep,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    '~$lossy_optional_integer_deferred(S_deep,pfunction,0)']
forgeries += [
    '$number_binary(SUBTRACT,NFLOAT 9218868437227405312,NFLOAT 9218868437227405312) = NUM (NFLOAT n_condition_nan)',
    '$pfcast_nan(PFLOAT n_condition_nan)']
for name, expression, right, result, condition in [
    ('nan_result', 'NExprBinaryOpMinus (NScalarFloat (FLOAT "7ff0000000000000") eps) (NScalarFloat (FLOAT "7ff0000000000000") eps) eps', 'PFLOAT 9218868437227405312', 'PFLOAT n_condition_nan', '(PFLOAT n_condition_nan)'),
    ('zero_divisor', 'NExprBinaryOpDiv (NScalarFloat (FLOAT "7ff0000000000000") eps) (NScalarFloat (FLOAT "0000000000000000") eps) eps', 'PFLOAT 0', 'PFLOAT 9218868437227405312', 'eps'),
]:
    forgeries += [f'expression_{name} = {expression}',
        f'S_source_{name} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_0 (NExprTernary expression_{name} expression_selected_0 expression_skip_0 metadata_0)), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_{name})] ++ $pcwalk($pcchildren(expression_{name},pcpath_0 ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
        f'S_{name} = S_source_{name}[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) ({result})), (PCONSTANT (pcpath_0 ++ [PCFIELD 0,PCFIELD 0]) (PFLOAT 9218868437227405312)), (PCONSTANT (pcpath_0 ++ [PCFIELD 0,PCFIELD 1]) ({right}))] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,porigin_cond_0) = {condition}',
        f'$lossy_optional_integer_computed_infinite_float_full_redirect(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = eps',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_{name},pfunction,0)']
context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
raw_source = ROWS['deferred-computed-infinite-float-full-ternary-redirect-wrapper-raw-tagged-results']['source']
named_source = ROWS['deferred-computed-infinite-float-full-ternary-redirect-wrapper-alias-named-reentry']['source']
CASES = {
    'computed-infinite-float-full-independent-raw-tags': {'source': raw_source,
        'stage': context + '-- if pcallcontext.ARGC = 0 -- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': raw},
    'computed-infinite-float-full-independent-forgeries': {'source': raw_source,
        'stage': context + '-- if pcallcontext.ARGC = 0 -- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': forgeries},
    'computed-infinite-float-full-independent-private-lifecycle': {'source': named_source,
        'stage': context + '-- if pcallcontext.ARGC = 1 -- if pfunction.ENV.NAMESPACE = $ptascii("ComputedInfiniteFloatRedirect306") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': named},
}
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
