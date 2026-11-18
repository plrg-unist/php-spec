#!/usr/bin/env python3
"""Proper folded FLOAT trees retain every intermediate and private default value."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_float_tree_infinite_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

POSINF, NEGINF = 9218868437227405312, 18442240474082181120
ZERO, NEGZERO, ONE, NEGONE = 0, 9223372036854775808, 4607182418800017408, 13830554455654793216
TWO, NEGTWO, THREE = 4611686018427387904, 13835058055282163712, 4613937818241073152
F154, N154 = 6910736104866537457, 16134108141721313265
F308, N308 = 9214871658872686752, 18438243695727462560
# Integer/rational binary64 RNE gives F154*F154 exactly F308 after rounding.
NODES = [
    {(): POSINF, (0,): POSINF, (0,0): NEGZERO, (0,0,0): NEGZERO, (0,0,0,0): ZERO, (0,1): POSINF, (1,): ONE},
    {(): NEGINF, (0,): NEGINF, (0,0): N308, (0,0,0): F308, (0,1): TWO, (0,1,0): ONE, (0,1,1): ONE, (1,): NEGONE, (1,0): ONE},
    {(): POSINF, (0,): POSINF, (1,): NEGINF, (1,0): N308, (1,0,0): F308, (1,1): TWO},
    {(): NEGINF, (0,): NEGINF, (0,0): POSINF, (1,): POSINF, (1,0): F308, (1,1): TWO},
    {(): POSINF, (0,): F308, (0,0): F154, (0,1): F154, (1,): TWO},
    {(): NEGINF, (0,): N308, (0,0): N154, (0,0,0): F154, (0,1): F154, (1,): TWO},
    {(): POSINF, (0,): TWO, (0,0): TWO, (0,1): ONE, (1,): 1, (1,0): 1, (1,1): ONE},
    {(): NEGINF, (0,): NEGTWO, (0,0): NEGTWO, (0,0,0): TWO, (0,1): ONE, (1,): 1, (1,0): 1, (1,1): ONE},
]
OPERATORS = ['ADD', 'ADD', 'SUBTRACT', 'SUBTRACT', 'MULTIPLY', 'MULTIPLY', 'DIVIDE', 'DIVIDE']
VALUES = ['PINT 0', 'PBOOL true', 'PFLOAT 0', 'PFLOAT 9223372036854775808',
          'PFLOAT n_nan', 'PNULL', 'PBOOL true', 'PINT 1']
ROOT = '$lossy_optional_integer_float_tree_infinite_full_redirect'
NODE = '$lossy_optional_integer_float_tree_value'


def path(base, fields):
    return base + ' ++ [' + ','.join('PCFIELD ' + str(field) for field in fields) + ']'


def origin(base, fields):
    return 'PORIGIN n_unit (' + path(base, fields) + ')'


base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
raw = base + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
              '$default_cache_owner(S) = (CACHE_SHARED)']
for index, (nodes, operator, value) in enumerate(zip(NODES, OPERATORS, VALUES)):
    default = f'pdefault_{index}'
    where = f'pcpath_{index}'
    cond, selected = origin(where, (0,)), origin(where, (1,))
    raw += [f'$default_at(pfunction.DEFAULTS,{index}) = ({default})',
        f'{default}.ORIGIN = PORIGIN n_unit {where}',
        f'$origin_node(S.SOURCES,{default}.ORIGIN) = (NExprTernary expression_cond_{index} expression_selected_{index} expression_skip_{index} metadata_{index})',
        f'$pfshape(expression_cond_{index}) = PFBINARY {operator} expression_left_{index} expression_right_{index}',
        f'$code_expression(pcode.EXPRESSIONS,{where}) = ((z_{index},false))',
        f'$pool_value(S.POOLS,{default}.ORIGIN) = eps /\\ $compiled_read(S,{default}.ORIGIN) = eps',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,{cond})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = ' + ('eps' if index == 0 else f'(PFLOAT {nodes[()]})'),
        f'$float_decode({nodes[()]}) = INFINITE n_sign_{index}',
        f'$lossy_optional_integer_computed_infinite_float_full_redirect(S,pfunction.ENV,{default}.ORIGIN) = eps',
        f'$lossy_optional_integer_float_integer_infinite_full_redirect(S,pfunction.ENV,{default}.ORIGIN) = eps',
        f'$lossy_optional_integer_integer_float_infinite_full_redirect(S,pfunction.ENV,{default}.ORIGIN) = eps',
        f'{ROOT}(S,pfunction.ENV,{default}.ORIGIN) = (({cond},{selected}))',
        f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,{default}.ORIGIN) = (({cond},{selected}))',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{selected}) = ({value})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{default}.ORIGIN) = ({value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,{origin(where, (2,))})',
        f'pdefaultcache_{index} = {{ORIGIN {default}.ORIGIN,VALUE {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,{default}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED ({value})',
        rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
    for relative, bits in nodes.items():
        fields = (0,) + relative
        at = origin(where, fields)
        raw += [f'$pool_value(S.POOLS,{at}) = (PFLOAT {bits})',
            f'$code_expression(pcode.EXPRESSIONS,{path(where, fields)}) = eps',
            f'$compiled_read(S,{at}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where, fields)}) = 0']
    raw += [f'{NODE}(S,{cond}) = ({nodes[()]})']
raw += ['$pfcast_nan(PFLOAT n_nan)',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,' + origin('pcpath_0', (0,)) + ')',
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
    '$default_at(pfunction.DEFAULTS,0) = (pdefault)', 'pdefault.ORIGIN = PORIGIN n_unit pcpath',
    'porigin_cond = ' + origin('pcpath', (0,)), 'porigin_selected = ' + origin('pcpath', (1,)),
    '$origin_node(S.SOURCES,pdefault.ORIGIN) = (NExprTernary expression_cond expression_selected expression_skip metadata)',
    '$code_expression(pcode.EXPRESSIONS,pcpath) = ((z,false))',
    f'{ROOT}(S,pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))']
mutations = {
    'no_redirect': 'S[.CODE = [pcode[.REDIRECTS = eps]]]',
    'duplicate': 'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
    'copy': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 1]) true)]]]]',
    'target': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 2]) false)]]]]',
    'ownpool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath (PINT 0))] ++ ppool.CONSTANTS)]]]',
    'owncode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath z true)] ++ pcode.EXPRESSIONS)]]]',
}
for label, fields, value in [('condtag',(0,),'PBOOL true'),('condsign',(0,),f'PFLOAT {NEGINF}'),
        ('intermediate',(0,0),f'PFLOAT {ONE}'),('signed_leaf',(0,0,0),f'PFLOAT {ZERO}'),
        ('deep_sign',(0,0,0,0),f'PFLOAT {ZERO}'),('deep_scalar',(0,0,0,0,0),f'PFLOAT {ONE}'),('integer_leaf',(0,1),'PINT 1')]:
    mutations[label] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath", fields)}) ({value}))] ++ ppool.CONSTANTS)]]]'
for fields in [(0,), (0,0), (0,0,0), (0,0,0,0), (0,0,0,0,0), (0,1)]:
    label = ''.join(map(str,fields))
    for flag in ['false','true']:
        mutations['code'+label+flag] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path("pcpath", fields)}) z {flag})] ++ pcode.EXPRESSIONS)]]]'
    mutations['redirect'+label] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT ({path("pcpath", fields)}) (pcpath ++ [PCFIELD 1]) false)] ++ pcode.REDIRECTS)]]]'
for label, expression in mutations.items():
    forgeries += [f'S_{label} = {expression}', f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
for fields in [(0,), (1,), (2,), (0,0), (0,0,0,0), (0,1)]:
    label = ''.join(map(str,fields))
    forgeries += [f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path("pcpath", fields)}) (NScalarInt (INTEGER 99) eps))] ++ pcunit.OCCURRENCES)]]]',
        f'{ROOT}(S_source_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_source_{label},pfunction,0)']

# A changed finite child can leave both infinite ancestors unchanged.
finite = origin('pcpath_finite', (0,0,1))
forgeries += ['$default_at(pfunction.DEFAULTS,1) = (pdefault_finite)',
    'pdefault_finite.ORIGIN = PORIGIN n_unit pcpath_finite',
    f'$pool_value(S.POOLS,{finite}) = (PFLOAT {TWO})', f'{NODE}(S,{finite}) = ({TWO})',
    f'S_three = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath_finite", (0,0,1))}) (PFLOAT {THREE}))] ++ ppool.CONSTANTS)]]]',
    f'$pool_value(S_three.POOLS,{origin("pcpath_finite", (0,))}) = (PFLOAT {NEGINF})',
    f'{NODE}(S_three,{finite}) = eps', f'{ROOT}(S_three,pfunction.ENV,pdefault_finite.ORIGIN) = eps',
    '~$lossy_optional_integer_deferred(S_three,pfunction,1)']
forgeries += [
    f'S_finite_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path("pcpath_finite", (0,0,1,0))}) (NScalarFloat (FLOAT "4000000000000000") eps))] ++ pcunit.OCCURRENCES)]]]',
    f'S_finite_coherent = S_finite_source[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath_finite", (0,0,1,0))}) (PFLOAT {TWO})),(PCONSTANT ({path("pcpath_finite", (0,0,1))}) (PFLOAT {THREE}))] ++ ppool.CONSTANTS)]]]',
    f'$pool_value(S_finite_coherent.POOLS,{origin("pcpath_finite", (0,))}) = (PFLOAT {NEGINF})',
    f'~$lossy_optional_integer_deferred_bindings(S_finite_coherent,pfunction.ENV,{origin("pcpath_finite", (0,))})',
    f'{ROOT}(S_finite_coherent,pfunction.ENV,pdefault_finite.ORIGIN) = eps',
    '~$lossy_optional_integer_deferred(S_finite_coherent,pfunction,1)']
condition_rows = [f'(PCONSTANT ({path("pcpath_finite", (0,)+relative)}) (PFLOAT {bits}))' for relative,bits in NODES[1].items()]
missing_rows = [f'(PCONSTANT ({path("pcpath_finite", (0,)+relative)}) (PFLOAT {bits}))' for relative,bits in NODES[1].items() if relative!=(0,1)]
forgeries += ['S_cond_only = S[.POOLS = [ppool[.CONSTANTS = [' + ','.join(condition_rows) + ']]]]',
    f'{ROOT}(S_cond_only,pfunction.ENV,pdefault_finite.ORIGIN) = (({origin("pcpath_finite", (0,))},{origin("pcpath_finite", (1,))}))',
    'S_missing = S[.POOLS = [ppool[.CONSTANTS = [' + ','.join(missing_rows) + ']]]]',
    f'$pool_value(S_missing.POOLS,{finite}) = eps', f'{NODE}(S_missing,{finite}) = eps',
    f'{ROOT}(S_missing,pfunction.ENV,pdefault_finite.ORIGIN) = eps']

# Fresh well-indexed trees with excluded leaves or operation/phase shapes.
inf = 'NScalarFloat (FLOAT "7ff0000000000000") eps'
neg_inf = 'NScalarFloat (FLOAT "fff0000000000000") eps'
one = 'NScalarFloat (FLOAT "3ff0000000000000") eps'
zero = 'NScalarFloat (FLOAT "0000000000000000") eps'
for label, expression, pools in [
    ('flat',f'NExprBinaryOpPlus ({inf}) ({one}) eps',{():POSINF,(0,):POSINF,(1,):ONE}),
    ('integer',f'NExprBinaryOpPlus (NExprBinaryOpPlus (NScalarInt (INTEGER 0) eps) ({inf}) eps) ({one}) eps',{():POSINF,(0,):POSINF,(0,0):'PINT 0',(0,1):POSINF,(1,):ONE}),
    ('named',f'NExprBinaryOpPlus (NExprBinaryOpPlus (NExprConstFetch (NName (BYTES "SU5G") eps) eps) ({one}) eps) ({one}) eps',{():POSINF,(0,):POSINF,(0,0):POSINF,(0,1):ONE,(1,):ONE}),
    ('string',f'NExprBinaryOpPlus (NExprBinaryOpPlus (NScalarString (BYTES "MA==") eps) ({inf}) eps) ({one}) eps',{():POSINF,(0,):POSINF,(0,0):'PSTRING ([48])',(0,1):POSINF,(1,):ONE}),
    ('unary_computed',f'NExprBinaryOpPlus (NExprUnaryMinus (NExprBinaryOpPlus ({neg_inf}) ({one}) eps) eps) ({one}) eps',{():POSINF,(0,):POSINF,(0,0):NEGINF,(0,0,0):NEGINF,(0,0,1):ONE,(1,):ONE}),
    ('power',f'NExprBinaryOpPlus (NExprBinaryOpPow ({one}) ({inf}) eps) ({inf}) eps',{():POSINF,(0,):ONE,(0,0):ONE,(0,1):POSINF,(1,):POSINF}),
    ('finite',f'NExprBinaryOpPlus (NExprBinaryOpPlus ({one}) ({one}) eps) ({one}) eps',{():THREE,(0,):TWO,(0,0):ONE,(0,1):ONE,(1,):ONE}),
    ('nan',f'NExprBinaryOpPlus (NExprBinaryOpPlus ({inf}) ({neg_inf}) eps) ({one}) eps',{():9221120237041090560,(0,):9221120237041090560,(0,0):POSINF,(0,1):NEGINF,(1,):ONE}),
    ('division_zero',f'NExprBinaryOpPlus (NExprBinaryOpDiv ({one}) ({zero}) eps) ({inf}) eps',{():POSINF,(0,):POSINF,(0,0):ONE,(0,1):ZERO,(1,):POSINF}),
]:
    constants=[f'(PCONSTANT ({path("pcpath",(0,)+relative)}) ('+(value if isinstance(value,str) else f'PFLOAT {value}')+'))' for relative,value in pools.items()]
    forgeries += [f'expression_{label} = {expression}',
        f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath (NExprTernary expression_{label} expression_selected expression_skip metadata)),(PCOCCURRENCE (pcpath ++ [PCFIELD 0]) expression_{label})] ++ $pcwalk($pcchildren(expression_{label},pcpath ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
        f'S_{label} = S_source_{label}[.POOLS = [ppool[.CONSTANTS = ([' + ','.join(constants) + '] ++ ppool.CONSTANTS)]]]',
        f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
forgeries += ['$lossy_optional_integer_computed_infinite_float_full_redirect(S_flat,pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))',
    '$lossy_optional_integer_deferred_value_at(S_flat,pfunction.ENV,pdefault.ORIGIN) = (PINT 0)']

private = base + ['$default_cache_owner(S) = (CACHE_SHARED)', 'S.CODE = [pcode]']
for index,value in [(1,0),(2,1),(3,0)]:
    private += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED (PINT {value})',
        rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
private += [r'n_private_1 =/= n_private_2 /\ n_private_1 =/= n_private_3 /\ n_private_2 =/= n_private_3',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_1[.VALUE = PBOOL false])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)', '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base309"),$ptascii("E_ERROR")),($ptascii("One309"),$ptascii("E_ERROR")),($ptascii("Skipped309"),$ptascii("Unavailable309") ++ [92] ++ $ptascii("Payload"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_1.ORIGIN)',
    'S_no_names = S[.CODE = [pcode[.NAMES = eps]]]', '~$lossy_optional_integer_deferred(S_no_names,pfunction,1)',
    'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3010)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps /\ S_done.FRAMES = eps']
for index in (1,2,3):
    private += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
private += ['$lookup(S_done.ENV,$ptascii("x309")) = (n_global)', 'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']

context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
raw_source=ROWS['deferred-float-tree-infinite-full-ternary-redirect-wrapper-raw-tagged-results']['source']
named_source=ROWS['deferred-float-tree-infinite-full-ternary-redirect-wrapper-alias-named-reentry']['source']
raw_stage=context+'-- if pcallcontext.ARGC = 0 -- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)'
CASES = {
    'float-tree-infinite-full-independent-tags': {'source':raw_source,'stage':raw_stage,'checks':raw},
    'float-tree-infinite-full-independent-forgeries': {'source':raw_source,'stage':raw_stage,'checks':forgeries},
    'float-tree-infinite-full-independent-private-lifecycle': {'source':named_source,
        'stage':context+'-- if pcallcontext.ARGC = 1 -- if pfunction.ENV.NAMESPACE = $ptascii("FloatTreeInfiniteRedirect309") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 5 -- if S.TODO = $function_tasks(S,pfunction)','checks':private},
}
if __name__ == '__main__':
    protocol.run(CASES,extra_inputs=(Path(__file__),CATALOGUE),runner_flags=('--sl',))
