#!/usr/bin/env python3
"""Reciprocal integer/float infinity predicates preserve exact typed source authority."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_integer_float_infinite_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
raw = base + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
              '$default_cache_owner(S) = (CACHE_SHARED)']
operands = [
    ('ADD', '9223372036854775807', 9218868437227405312, 9218868437227405312),
    ('ADD', '$(-9223372036854775807)', 18442240474082181120, 18442240474082181120),
    ('SUBTRACT', '2', 18442240474082181120, 9218868437227405312),
    ('SUBTRACT', '$(-2)', 9218868437227405312, 18442240474082181120),
    ('MULTIPLY', '2', 9214871658872686752, 9218868437227405312),
    ('MULTIPLY', '$(-2)', 9214871658872686752, 18442240474082181120),
    ('DIVIDE', '2', 1, 9218868437227405312),
    ('DIVIDE', '$(-2)', 1, 18442240474082181120),
]
values = ['PINT 0', 'PBOOL true', 'PFLOAT 0', 'PFLOAT 9223372036854775808',
          'PFLOAT n_nan', 'PNULL', 'PBOOL true', 'PINT 1']
for index, ((operator, left, right, result), value) in enumerate(zip(operands, values)):
    raw += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'porigin_cond_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
        f'porigin_selected_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (NExprTernary expression_cond_{index} expression_selected_{index} expression_skip_{index} metadata_{index})',
        f'$pfshape(expression_cond_{index}) = PFBINARY {operator} expression_left_{index} expression_right_{index}',
        f'i_left_{index} = {left}',
        f'$lossy_optional_integer_integer_literal(expression_left_{index}) = (i_left_{index})',
        f'$lossy_optional_integer_float_literal(expression_right_{index}) = ({right})',
        f'$lossy_optional_integer_float_literal(expression_left_{index}) = eps',
        f'$number_binary({operator},NINT i_left_{index},NFLOAT {right}) = NUM (NFLOAT {result})',
        f'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD 0])) = (PINT i_left_{index})',
        f'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD 1])) = (PFLOAT {right})',
        f'$pool_value(S.POOLS,porigin_cond_{index}) = (PFLOAT {result})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_cond_{index}) = (PFLOAT {result})',
        f'$lossy_optional_integer_computed_infinite_float_full_redirect(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'$lossy_optional_integer_float_integer_infinite_full_redirect(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'$lossy_optional_integer_integer_float_infinite_full_redirect(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ((porigin_cond_{index},porigin_selected_{index}))',
        f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ((porigin_cond_{index},porigin_selected_{index}))',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_selected_{index}) = ({value})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2]))',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED ({value})',
        rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
raw += ['$pfcast_nan(PFLOAT n_nan)',
    'S_wrong_zero = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_3[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_zero,S_wrong_zero.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_zero,pfunction,3)',
    'S_done = $drive_steps(S,3010)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps /\ S_done.FRAMES = eps']
for index in range(8):
    raw += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
raw += ['$heap_valid($heap_graph(S_done))']

forgeries = base + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
    '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
    'pdefault.ORIGIN = PORIGIN n_unit pcpath',
    'porigin_cond = PORIGIN n_unit (pcpath ++ [PCFIELD 0])',
    'porigin_selected = PORIGIN n_unit (pcpath ++ [PCFIELD 1])',
    '$origin_node(S.SOURCES,pdefault.ORIGIN) = (NExprTernary expression_cond expression_selected expression_skip metadata)',
    '$code_expression(pcode.EXPRESSIONS,pcpath) = ((z,false))',
    '$lossy_optional_integer_integer_float_infinite_full_redirect(S,pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))']
mutations = {
    'no_redirect': 'S[.CODE = [pcode[.REDIRECTS = eps]]]',
    'duplicate': 'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
    'copy': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 1]) true)]]]]',
    'target': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 2]) false)]]]]',
    'ownpool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath (PINT 0))] ++ ppool.CONSTANTS)]]]',
    'owncode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath z true)] ++ pcode.EXPRESSIONS)]]]',
    'condtag': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath ++ [PCFIELD 0]) (PBOOL true))] ++ ppool.CONSTANTS)]]]',
    'condsign': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath ++ [PCFIELD 0]) (PFLOAT 18442240474082181120))] ++ ppool.CONSTANTS)]]]',
}
for suffix in ('[PCFIELD 0]', '[PCFIELD 0,PCFIELD 0]', '[PCFIELD 0,PCFIELD 1]'):
    label = suffix.replace('[', '').replace(']', '').replace('PCFIELD ', '').replace(',', '')
    mutations['code' + label] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath ++ {suffix}) z false)] ++ pcode.EXPRESSIONS)]]]'
    mutations['redirect' + label] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT (pcpath ++ {suffix}) (pcpath ++ [PCFIELD 1]) false)] ++ pcode.REDIRECTS)]]]'
for field, value in [(0, 'PFLOAT 4890909195324358656'), (1, 'PINT 9223372036854775807'), (0, 'PINT 1')]:
    label = ('left_float' if field == 0 and value.startswith('PFLOAT') else 'right_int' if field == 1 else 'left_other_int')
    mutations[label] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath ++ [PCFIELD 0,PCFIELD {field}]) ({value}))] ++ ppool.CONSTANTS)]]]'
for label, expression in mutations.items():
    forgeries += [f'S_{label} = {expression}',
        f'$lossy_optional_integer_integer_float_infinite_full_redirect(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
for suffix in ('[PCFIELD 0]', '[PCFIELD 1]', '[PCFIELD 2]', '[PCFIELD 0,PCFIELD 0]', '[PCFIELD 0,PCFIELD 1]'):
    label = suffix.replace('[', '').replace(']', '').replace('PCFIELD ', '').replace(',', '')
    forgeries += [f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath ++ {suffix}) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
        f'$lossy_optional_integer_integer_float_infinite_full_redirect(S_source_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_source_{label},pfunction,0)']

infinity = 'NScalarFloat (FLOAT "7ff0000000000000") eps'
integer = lambda number: f'NScalarInt (INTEGER {number}) eps'
for label, expression, left, right, result in [
    ('float_left', f'NExprBinaryOpPlus ({infinity}) ({integer("1")}) eps', 'PFLOAT 9218868437227405312', 'PINT 1', 'PFLOAT 9218868437227405312'),
    ('named_left', f'NExprBinaryOpPlus (NExprConstFetch (NName (BYTES "RV9FUlJPUg==") eps) eps) ({infinity}) eps', 'PINT 1', 'PFLOAT 9218868437227405312', 'PFLOAT 9218868437227405312'),
    ('string_left', f'NExprBinaryOpPlus (NScalarString (BYTES "MQ==") eps) ({infinity}) eps', 'PSTRING ([49])', 'PFLOAT 9218868437227405312', 'PFLOAT 9218868437227405312'),
    ('nested_left', f'NExprBinaryOpPlus (NExprBinaryOpPlus ({integer("1")}) ({integer("1")}) eps) ({infinity}) eps', 'PINT 2', 'PFLOAT 9218868437227405312', 'PFLOAT 9218868437227405312'),
    ('named_right', f'NExprBinaryOpPlus ({integer("1")}) (NExprConstFetch (NName (BYTES "SU5G") eps) eps) eps', 'PINT 1', 'PFLOAT 9218868437227405312', 'PFLOAT 9218868437227405312'),
    ('string_right', f'NExprBinaryOpPlus ({integer("1")}) (NScalarString (BYTES "MS4wZTMwOQ==") eps) eps', 'PINT 1', 'PSTRING ([49,46,48,101,51,48,57])', 'PFLOAT 9218868437227405312'),
    ('nested_right', f'NExprBinaryOpPlus ({integer("1")}) (NExprBinaryOpPlus ({infinity}) (NScalarFloat (FLOAT "0000000000000000") eps) eps) eps', 'PINT 1', 'PFLOAT 9218868437227405312', 'PFLOAT 9218868437227405312'),
    ('promoted', f'NExprBinaryOpPlus (NExprUnaryMinus ({integer("$(-9223372036854775808)")}) eps) ({infinity}) eps', 'PINT 9223372036854775807', 'PFLOAT 9218868437227405312', 'PFLOAT 9218868437227405312'),
    ('reversed_promotion', f'NExprBinaryOpPlus (NExprUnaryMinus (NExprUnaryMinus ({integer("$(-9223372036854775808)")}) eps) eps) ({infinity}) eps', 'PINT $(-9223372036854775808)', 'PFLOAT 9218868437227405312', 'PFLOAT 9218868437227405312'),
    ('out_of_range', f'NExprBinaryOpPlus ({integer("9223372036854775808")}) ({infinity}) eps', 'PINT 9223372036854775808', 'PFLOAT 9218868437227405312', 'PFLOAT 9218868437227405312'),
    ('divide_zero', f'NExprBinaryOpDiv ({integer("2")}) (NScalarFloat (FLOAT "0000000000000000") eps) eps', 'PINT 2', 'PFLOAT 0', 'PFLOAT 9218868437227405312'),
    ('divide_negative_zero', f'NExprBinaryOpDiv ({integer("2")}) (NScalarFloat (FLOAT "8000000000000000") eps) eps', 'PINT 2', 'PFLOAT 9223372036854775808', 'PFLOAT 18442240474082181120'),
    ('divide_infinite', f'NExprBinaryOpDiv ({integer("2")}) ({infinity}) eps', 'PINT 2', 'PFLOAT 9218868437227405312', 'PFLOAT 0'),
    ('divide_negative_infinite', f'NExprBinaryOpDiv ({integer("2")}) (NScalarFloat (FLOAT "fff0000000000000") eps) eps', 'PINT 2', 'PFLOAT 18442240474082181120', 'PFLOAT 9223372036854775808'),
    ('multiply_zero_infinite', f'NExprBinaryOpMul ({integer("0")}) ({infinity}) eps', 'PINT 0', 'PFLOAT 9218868437227405312', 'PFLOAT 9221120237041090560'),
    ('finite', f'NExprBinaryOpPlus ({integer("1")}) (NScalarFloat (FLOAT "3ff0000000000000") eps) eps', 'PINT 1', 'PFLOAT 4607182418800017408', 'PFLOAT 4611686018427387904'),
    ('nan', f'NExprBinaryOpPlus ({integer("1")}) (NScalarFloat (FLOAT "7ff8000000000000") eps) eps', 'PINT 1', 'PFLOAT 9221120237041090560', 'PFLOAT 9221120237041090560'),
    ('power', f'NExprBinaryOpPow ({integer("2")}) ({infinity}) eps', 'PINT 2', 'PFLOAT 9218868437227405312', 'PFLOAT 9218868437227405312'),
]:
    forgeries += [f'expression_{label} = {expression}',
        f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath (NExprTernary expression_{label} expression_selected expression_skip metadata)),(PCOCCURRENCE (pcpath ++ [PCFIELD 0]) expression_{label})] ++ $pcwalk($pcchildren(expression_{label},pcpath ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
        f'S_{label} = S_source_{label}[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath ++ [PCFIELD 0]) ({result})),(PCONSTANT (pcpath ++ [PCFIELD 0,PCFIELD 0]) ({left})),(PCONSTANT (pcpath ++ [PCFIELD 0,PCFIELD 1]) ({right}))] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_integer_float_infinite_full_redirect(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
forgeries += [
    '$lossy_optional_integer_integer_literal(NScalarInt (INTEGER $(-9223372036854775808)) eps) = ($(-9223372036854775808))',
    '$lossy_optional_integer_integer_literal(NScalarInt (INTEGER 9223372036854775807) eps) = (9223372036854775807)',
    '$lossy_optional_integer_integer_literal(NScalarInt (INTEGER $(-9223372036854775809)) eps) = eps',
    '$lossy_optional_integer_integer_literal(NScalarInt (INTEGER 9223372036854775808) eps) = eps',
    '$lossy_optional_integer_integer_literal(NExprUnaryPlus (NExprUnaryMinus (NScalarInt (INTEGER $(-9223372036854775808)) eps) eps) eps) = eps',
    '$lossy_optional_integer_integer_literal(NExprUnaryMinus (NExprUnaryMinus (NScalarInt (INTEGER $(-9223372036854775808)) eps) eps) eps) = eps',
    'expression_unary_left = NExprUnaryMinus (NScalarInt (INTEGER 2) eps) eps',
    f'expression_unary = NExprBinaryOpPlus expression_unary_left ({infinity}) eps',
    'S_unary_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath (NExprTernary expression_unary expression_selected expression_skip metadata)),(PCOCCURRENCE (pcpath ++ [PCFIELD 0]) expression_unary)] ++ $pcwalk($pcchildren(expression_unary,pcpath ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
    'S_unary = S_unary_source[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath ++ [PCFIELD 0,PCFIELD 0]) (PINT $(-2)))] ++ ppool.CONSTANTS)]]]',
    '$lossy_optional_integer_integer_float_infinite_full_redirect(S_unary,pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))',
    '$lossy_optional_integer_deferred_value_at(S_unary,pfunction.ENV,pdefault.ORIGIN) = (PINT 0)',
    '~$lossy_optional_integer_deferred(S_unary,pfunction,0)',
    'S_deep = S_unary[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath ++ [PCFIELD 0,PCFIELD 0,PCFIELD 0]) (NScalarInt (INTEGER 99) eps))] ++ $pcwalk($pcchildren(expression_unary,pcpath ++ [PCFIELD 0])) ++ [(PCOCCURRENCE pcpath (NExprTernary expression_unary expression_selected expression_skip metadata)),(PCOCCURRENCE (pcpath ++ [PCFIELD 0]) expression_unary)] ++ pcunit.OCCURRENCES)]]]',
    '~$lossy_optional_integer_deferred_bindings(S_deep,pfunction.ENV,porigin_cond)',
    '$lossy_optional_integer_integer_float_infinite_full_redirect(S_deep,pfunction.ENV,pdefault.ORIGIN) = eps',
    '~$lossy_optional_integer_deferred(S_deep,pfunction,0)',
    '$default_at(pfunction.DEFAULTS,6) = (pdefault_signed_float)',
    'pdefault_signed_float.ORIGIN = PORIGIN n_unit pcpath_signed_float',
    '$lossy_optional_integer_integer_float_infinite_full_redirect(S,pfunction.ENV,pdefault_signed_float.ORIGIN) = ((PORIGIN n_unit (pcpath_signed_float ++ [PCFIELD 0]),PORIGIN n_unit (pcpath_signed_float ++ [PCFIELD 1])))',
    'S_right_deep = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_signed_float ++ [PCFIELD 0,PCFIELD 1,PCFIELD 0]) (NScalarInt (INTEGER 99) eps))] ++ pcunit.OCCURRENCES)]]]',
    '~$lossy_optional_integer_deferred_bindings(S_right_deep,pfunction.ENV,PORIGIN n_unit (pcpath_signed_float ++ [PCFIELD 0]))',
    '$lossy_optional_integer_integer_float_infinite_full_redirect(S_right_deep,pfunction.ENV,pdefault_signed_float.ORIGIN) = eps',
    '~$lossy_optional_integer_deferred(S_right_deep,pfunction,6)',
]

# Zero is an admitted signed64 leaf; only the infinite result earns this receipt.
forgeries += [
    f'expression_zero_left = NExprBinaryOpPlus ({integer("0")}) ({infinity}) eps',
    'S_zero_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath (NExprTernary expression_zero_left expression_selected expression_skip metadata)),(PCOCCURRENCE (pcpath ++ [PCFIELD 0]) expression_zero_left)] ++ $pcwalk($pcchildren(expression_zero_left,pcpath ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
    'S_zero_left = S_zero_source[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath ++ [PCFIELD 0,PCFIELD 0]) (PINT 0))] ++ ppool.CONSTANTS)]]]',
    '$lossy_optional_integer_integer_float_infinite_full_redirect(S_zero_left,pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))',
    '$lossy_optional_integer_deferred_value_at(S_zero_left,pfunction.ENV,pdefault.ORIGIN) = (PINT 0)',
    '~$lossy_optional_integer_deferred(S_zero_left,pfunction,0)',
]

private = base + ['$default_cache_owner(S) = (CACHE_SHARED)', 'S.CODE = [pcode]']
for index, value in [(1, 0), (2, 1), (3, 0), (4, 0)]:
    private += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED (PINT {value})',
        rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
private += [
    r'n_private_1 =/= n_private_2 /\ n_private_1 =/= n_private_3 /\ n_private_1 =/= n_private_4 /\ n_private_2 =/= n_private_3 /\ n_private_2 =/= n_private_4 /\ n_private_3 =/= n_private_4',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_1[.VALUE = PBOOL false])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base308"),$ptascii("E_ERROR")),($ptascii("One308"),$ptascii("E_ERROR")),($ptascii("Skipped308"),$ptascii("Unavailable308") ++ [92] ++ $ptascii("Payload"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_1.ORIGIN)',
    'S_no_names = S[.CODE = [pcode[.NAMES = eps]]]',
    '~$lossy_optional_integer_deferred(S_no_names,pfunction,1)',
    'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3010)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps /\ S_done.FRAMES = eps']
for index in (1, 2, 3, 4):
    private += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
private += ['$lookup(S_done.ENV,$ptascii("x308")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']

context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
raw_source = ROWS['deferred-integer-float-infinite-full-ternary-redirect-wrapper-raw-tagged-results']['source']
named_source = ROWS['deferred-integer-float-infinite-full-ternary-redirect-wrapper-alias-named-reentry']['source']
raw_stage = context + '-- if pcallcontext.ARGC = 0 -- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)'
CASES = {
    'integer-float-infinite-full-independent-tags': {'source': raw_source, 'stage': raw_stage, 'checks': raw},
    'integer-float-infinite-full-independent-forgeries': {'source': raw_source, 'stage': raw_stage, 'checks': forgeries},
    'integer-float-infinite-full-independent-private-lifecycle': {'source': named_source,
        'stage': context + '-- if pcallcontext.ARGC = 1 -- if pfunction.ENV.NAMESPACE = $ptascii("IntegerFloatInfiniteRedirect308") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': private},
}
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
