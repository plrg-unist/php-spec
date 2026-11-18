#!/usr/bin/env python3
"""Mixed folded trees preserve raw leaf kinds and every intermediate value tag."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_mixed_number_tree_infinite_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

POSINF, NEGINF = 9218868437227405312, 18442240474082181120
ZERO, NEGZERO = 0, 9223372036854775808
ONE, NEGONE, TWO, THREE = 4607182418800017408, 13830554455654793216, 4611686018427387904, 4613937818241073152
TWO63, NEGTWOPOINTFIVE = 4890909195324358656, 13836183955189006336
MAX, MIN = 9223372036854775807, -9223372036854775808
ROOT = '$lossy_optional_integer_mixed_number_tree_infinite_full_redirect'
NODE = '$lossy_optional_integer_mixed_number_tree_value'
FLOAT_ROOT = '$lossy_optional_integer_float_tree_infinite_full_redirect'


def integer(value):
    return str(value) if value >= 0 else f'$(-{-value})'


def ni(value):
    return f'PINT {integer(value)}', f'NINT {integer(value)}', 'true', 'false'


def nf(bits, has_int=False, has_float=True):
    return f'PFLOAT {bits}', f'NFLOAT {bits}', str(has_int).lower(), str(has_float).lower()


# Values follow tagged integer operations and exact binary64 powers. Overflow
# converts each MAX operand to 2^63; later subtraction retains the FLOAT tag.
NODES = [
    {(): nf(POSINF, True), (0,): ni(2), (0,0): ni(1), (0,1): ni(1),
     (1,): nf(POSINF), (1,0): nf(NEGZERO), (1,0,0): nf(NEGZERO),
     (1,0,0,0): nf(ZERO), (1,1): nf(POSINF)},
    {(): nf(NEGINF, True), (0,): ni(-2), (0,0): ni(-1), (0,0,0): ni(1),
     (0,1): ni(1), (1,): nf(NEGINF), (1,0): nf(POSINF)},
    {(): nf(POSINF, True), (0,): nf(POSINF), (1,): ni(-2),
     (1,0): ni(-1), (1,0,0): ni(1), (1,1): ni(1)},
    {(): nf(NEGINF, True), (0,): nf(NEGINF), (0,0): nf(POSINF),
     (1,): ni(2), (1,0): ni(1), (1,1): ni(1)},
    {(): nf(POSINF, True), (0,): nf(TWO63, True, False),
     (0,0): ni(MAX), (0,1): ni(1), (1,): nf(POSINF)},
    {(): nf(NEGINF, True), (0,): nf(NEGONE, True, False),
     (0,0): nf(ZERO, True, False), (0,0,0): nf(TWO63, True, False),
     (0,0,0,0): ni(MAX), (0,0,0,1): ni(1), (0,0,1): ni(MAX),
     (0,1): ni(1), (1,): nf(POSINF)},
    {(): nf(POSINF, True), (0,): ni(2), (0,0): ni(4), (0,1): ni(2), (1,): nf(1)},
    {(): nf(NEGINF, True), (0,): nf(NEGTWOPOINTFIVE, True, False),
     (0,0): ni(-5), (0,0,0): ni(5), (0,1): ni(2), (1,): nf(1)},
]
OPERATORS = ['ADD', 'ADD', 'SUBTRACT', 'SUBTRACT', 'MULTIPLY', 'MULTIPLY', 'DIVIDE', 'DIVIDE']
VALUES = ['PINT 0', 'PBOOL true', 'PFLOAT 0', 'PFLOAT 9223372036854775808',
          'PFLOAT n_nan', 'PNULL', 'PBOOL true', 'PINT 1']


def path(base, fields):
    return base + ' ++ [' + ','.join('PCFIELD ' + str(field) for field in fields) + ']'


def origin(base, fields):
    return 'PORIGIN n_unit (' + path(base, fields) + ')'


def result(node):
    return f'(({node[1]},{node[2]},{node[3]}))'


base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
raw = base + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
              '$default_cache_owner(S) = (CACHE_SHARED)']
for index, (nodes, operator, value) in enumerate(zip(NODES, OPERATORS, VALUES)):
    default, where = f'pdefault_{index}', f'pcpath_{index}'
    cond, selected = origin(where, (0,)), origin(where, (1,))
    raw += [f'$default_at(pfunction.DEFAULTS,{index}) = ({default})',
        f'{default}.ORIGIN = PORIGIN n_unit {where}',
        f'$origin_node(S.SOURCES,{default}.ORIGIN) = (NExprTernary expression_cond_{index} expression_selected_{index} expression_skip_{index} metadata_{index})',
        f'$pfshape(expression_cond_{index}) = PFBINARY {operator} expression_left_{index} expression_right_{index}',
        f'$code_expression(pcode.EXPRESSIONS,{where}) = ((z_{index},false))',
        rf'$pool_value(S.POOLS,{default}.ORIGIN) = eps /\ $compiled_read(S,{default}.ORIGIN) = eps',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,{cond})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = ' + ('eps' if index == 0 else f'({nodes[()][0]})'),
        f'$float_decode({POSINF if index in (0,2,4,6) else NEGINF}) = INFINITE n_sign_{index}',
        f'$lossy_optional_integer_computed_infinite_float_full_redirect(S,pfunction.ENV,{default}.ORIGIN) = eps',
        f'$lossy_optional_integer_float_integer_infinite_full_redirect(S,pfunction.ENV,{default}.ORIGIN) = eps',
        f'$lossy_optional_integer_integer_float_infinite_full_redirect(S,pfunction.ENV,{default}.ORIGIN) = eps',
        f'{FLOAT_ROOT}(S,pfunction.ENV,{default}.ORIGIN) = eps',
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
    for relative, node in nodes.items():
        fields, at = (0,) + relative, origin(where, (0,) + relative)
        raw += [f'$pool_value(S.POOLS,{at}) = ({node[0]})',
            f'$code_expression(pcode.EXPRESSIONS,{path(where, fields)}) = eps',
            f'$compiled_read(S,{at}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where, fields)}) = 0',
            f'{NODE}(S,{at}) = {result(node)}']
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
for label, fields, value in [
        ('condtag',(0,),'PBOOL true'), ('condsign',(0,),f'PFLOAT {NEGINF}'),
        ('int_leaf_tag',(0,0,0),f'PFLOAT {ONE}'),
        ('float_subtree_tag',(0,1),'PINT 1'), ('plus_zero_sign',(0,1,0),f'PFLOAT {ZERO}'),
        ('minus_zero_sign',(0,1,0,0),f'PFLOAT {ZERO}'),
        ('float_leaf_tag',(0,1,0,0,0),'PINT 0')]:
    mutations[label] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath", fields)}) ({value}))] ++ ppool.CONSTANTS)]]]'
for fields in [(0,) + relative for relative in NODES[0]]:
    label = ''.join(map(str,fields))
    for flag in ['false','true']:
        mutations['code'+label+flag] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path("pcpath", fields)}) z {flag})] ++ pcode.EXPRESSIONS)]]]'
    mutations['redirect'+label] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT ({path("pcpath", fields)}) (pcpath ++ [PCFIELD 1]) false)] ++ pcode.REDIRECTS)]]]'
for label, expression in mutations.items():
    forgeries += [f'S_{label} = {expression}', f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
for fields in [(0,), (1,), (2,), (0,0,0), (0,1,0,0), (0,1,0,0,0)]:
    label = ''.join(map(str,fields))
    forgeries += [f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path("pcpath", fields)}) (NScalarInt (INTEGER 99) eps))] ++ pcunit.OCCURRENCES)]]]',
        f'{ROOT}(S_source_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_source_{label},pfunction,0)']

# Each forged node keeps an actually infinite ancestor. Equal numeric values
# remain different PINT/PFLOAT pool entries; overflow does not recover INT tags.
for label,index,relative,wrong in [
        ('finite_three',0,(0,),'PINT 3'), ('finite_float_two',0,(0,),f'PFLOAT {TWO}'),
        ('overflow_reintegerized',4,(0,),f'PINT {MAX}'),
        ('cancellation_reintegerized',5,(0,0),'PINT 0'),
        ('negative_reintegerized',5,(0,),'PINT $(-1)'),
        ('exact_division_float',6,(0,),f'PFLOAT {TWO}'),
        ('fractional_division_int',7,(0,),'PINT $(-2)')]:
    where, fields = f'pcpath_{label}', (0,) + relative
    forgeries += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{label})',
        f'pdefault_{label}.ORIGIN = PORIGIN n_unit {where}',
        f'{NODE}(S,{origin(where, fields)}) = {result(NODES[index][relative])}',
        f'S_{label} = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path(where, fields)}) ({wrong}))] ++ ppool.CONSTANTS)]]]',
        f'$pool_value(S_{label}.POOLS,{origin(where, (0,))}) = ({NODES[index][()][0]})',
        f'{NODE}(S_{label},{origin(where, fields)}) = eps',
        f'{ROOT}(S_{label},pfunction.ENV,pdefault_{label}.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,{index})']
condition_rows = [f'(PCONSTANT ({path("pcpath",(0,)+relative)}) ({node[0]}))' for relative,node in NODES[0].items()]
missing_rows = [row for relative,row in zip(NODES[0],condition_rows) if relative!=(1,0,0,0)]
forgeries += ['S_cond_only = S[.POOLS = [ppool[.CONSTANTS = [' + ','.join(condition_rows) + ']]]]',
    f'{ROOT}(S_cond_only,pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))',
    'S_missing = S[.POOLS = [ppool[.CONSTANTS = [' + ','.join(missing_rows) + ']]]]',
    f'{NODE}(S_missing,porigin_cond) = eps', f'{ROOT}(S_missing,pfunction.ENV,pdefault.ORIGIN) = eps']

inf = 'NScalarFloat (FLOAT "7ff0000000000000") eps'
neg_inf = 'NScalarFloat (FLOAT "fff0000000000000") eps'
one_float = 'NScalarFloat (FLOAT "3ff0000000000000") eps'
one_int = 'NScalarInt (INTEGER 1) eps'
zero_int = 'NScalarInt (INTEGER 0) eps'
min_int = f'NScalarInt (INTEGER {integer(MIN)}) eps'
max_int = f'NScalarInt (INTEGER {MAX}) eps'

# Seventeen raw MAX leaves produce INF, but never a raw FLOAT leaf. The first
# product promotes to 2^126 and each later product adds exactly 63 to its exponent.
all_int, all_int_nodes = max_int, {(): ni(MAX)}
for count in range(2,18):
    all_int = f'NExprBinaryOpMul ({all_int}) ({max_int}) eps'
    all_int_nodes = {(0,)+relative:node for relative,node in all_int_nodes.items()}
    exponent = count*63
    bits = POSINF if exponent>=1024 else (exponent+1023)*(1<<52)
    all_int_nodes.update({(1,):ni(MAX), ():nf(bits,True,False)})
assert all_int_nodes[()] == nf(POSINF,True,False)

scopes = [
    ('flat_if',f'NExprBinaryOpPlus ({one_int}) ({inf}) eps',
     {():nf(POSINF,True),(0,):ni(1),(1,):nf(POSINF)},nf(POSINF,True)),
    ('flat_fi',f'NExprBinaryOpPlus ({inf}) ({one_int}) eps',
     {():nf(POSINF,True),(0,):nf(POSINF),(1,):ni(1)},nf(POSINF,True)),
    ('pure_float',f'NExprBinaryOpPlus (NExprBinaryOpPlus ({inf}) ({one_float}) eps) ({one_float}) eps',
     {():nf(POSINF),(0,):nf(POSINF),(0,0):nf(POSINF),(0,1):nf(ONE),(1,):nf(ONE)},nf(POSINF)),
    ('all_int_overflow',all_int,all_int_nodes,nf(POSINF,True,False)),
    ('named',f'NExprBinaryOpPlus (NExprBinaryOpPlus (NExprConstFetch (NName (BYTES "RV9FUlJPUg==") eps) eps) ({inf}) eps) ({one_int}) eps',
     {():nf(POSINF,True),(0,):nf(POSINF),(0,0):ni(1),(0,1):nf(POSINF),(1,):ni(1)},None),
    ('string',f'NExprBinaryOpPlus (NExprBinaryOpPlus (NScalarString (BYTES "MA==") eps) ({inf}) eps) ({one_int}) eps',
     {():nf(POSINF,True),(0,):nf(POSINF),(0,0):('PSTRING ([48])','','',''),(0,1):nf(POSINF),(1,):ni(1)},None),
    ('unary_computed',f'NExprBinaryOpPlus (NExprUnaryMinus (NExprBinaryOpPlus ({one_int}) ({one_int}) eps) eps) ({inf}) eps',
     {():nf(POSINF,True),(0,):ni(-2),(0,0):ni(2),(0,0,0):ni(1),(0,0,1):ni(1),(1,):nf(POSINF)},None),
    ('promoted_unary',f'NExprBinaryOpPlus (NExprUnaryMinus ({min_int}) eps) (NExprBinaryOpPlus ({inf}) ({one_float}) eps) eps',
     {():nf(POSINF,True),(0,):nf(TWO63,True,False),(0,0):ni(MIN),(1,):nf(POSINF),(1,0):nf(POSINF),(1,1):nf(ONE)},None),
    ('reversed_promotion',f'NExprBinaryOpPlus (NExprUnaryMinus (NExprUnaryMinus ({min_int}) eps) eps) (NExprBinaryOpPlus ({inf}) ({one_float}) eps) eps',
     {():nf(POSINF,True),(0,):nf(TWO63+(1<<63),True,False),(0,0):nf(TWO63,True,False),(0,0,0):ni(MIN),(1,):nf(POSINF),(1,0):nf(POSINF),(1,1):nf(ONE)},None),
    ('out_of_range',f'NExprBinaryOpPlus (NExprBinaryOpPlus (NScalarInt (INTEGER 9223372036854775808) eps) ({one_int}) eps) ({inf}) eps',
     {():nf(POSINF,True),(0,):nf(TWO63,True,False),(0,0):ni(MAX+1),(0,1):ni(1),(1,):nf(POSINF)},None),
    ('power',f'NExprBinaryOpPlus (NExprBinaryOpPow (NScalarInt (INTEGER 2) eps) ({inf}) eps) ({one_int}) eps',
     {():nf(POSINF,True),(0,):nf(POSINF,True),(0,0):ni(2),(0,1):nf(POSINF),(1,):ni(1)},None),
    ('finite',f'NExprBinaryOpPlus (NExprBinaryOpPlus ({one_int}) ({one_float}) eps) ({one_int}) eps',
     {():nf(THREE,True),(0,):nf(TWO,True),(0,0):ni(1),(0,1):nf(ONE),(1,):ni(1)},nf(THREE,True)),
    ('nan',f'NExprBinaryOpPlus (NExprBinaryOpPlus ({inf}) ({neg_inf}) eps) ({one_int}) eps',
     {():nf(18444492273895866368,True),(0,):nf(18444492273895866368),(0,0):nf(POSINF),(0,1):nf(NEGINF),(1,):ni(1)},nf(18444492273895866368,True)),
    ('division_zero',f'NExprBinaryOpPlus (NExprBinaryOpDiv ({one_int}) ({zero_int}) eps) ({inf}) eps',
     {():nf(POSINF,True),(0,):nf(POSINF,True,False),(0,0):ni(1),(0,1):ni(0),(1,):nf(POSINF)},None),
]
for label,expression,nodes,value in scopes:
    constants=[f'(PCONSTANT ({path("pcpath",(0,)+relative)}) ({node[0]}))' for relative,node in nodes.items()]
    forgeries += [f'expression_{label} = {expression}',
        f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath (NExprTernary expression_{label} expression_selected expression_skip metadata)),(PCOCCURRENCE (pcpath ++ [PCFIELD 0]) expression_{label})] ++ $pcwalk($pcchildren(expression_{label},pcpath ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
        f'S_{label} = S_source_{label}[.POOLS = [ppool[.CONSTANTS = ([' + ','.join(constants) + '] ++ ppool.CONSTANTS)]]]',
        f'{NODE}(S_{label},porigin_cond) = ' + ('eps' if value is None else result(value)),
        f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
for label,earlier in [('flat_if','$lossy_optional_integer_integer_float_infinite_full_redirect'),
                      ('flat_fi','$lossy_optional_integer_float_integer_infinite_full_redirect'),
                      ('pure_float',FLOAT_ROOT)]:
    forgeries += [f'{earlier}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))',
        f'$lossy_optional_integer_deferred_value_at(S_{label},pfunction.ENV,pdefault.ORIGIN) = (PINT 0)']

private = base + ['$default_cache_owner(S) = (CACHE_SHARED)', 'S.CODE = [pcode]']
for index,value in [(1,0),(2,1),(3,0)]:
    private += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED (PINT {value})',
        rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
private += ['pdefault_1.ORIGIN = PORIGIN n_unit pcpath_wrapper',
    'porigin_full = PORIGIN n_unit (pcpath_wrapper ++ [PCFIELD 0])',
    'porigin_cond = PORIGIN n_unit (pcpath_wrapper ++ [PCFIELD 0,PCFIELD 0])',
    f'{NODE}(S,porigin_cond) = {result(nf(POSINF,True))}',
    f'{NODE}(S,{origin("pcpath_wrapper",(0,0,0))}) = {result(ni(2))}',
    f'{NODE}(S,{origin("pcpath_wrapper",(0,0,1))}) = {result(nf(POSINF))}',
    f'$lossy_optional_integer_float_tree_value(S,{origin("pcpath_wrapper",(0,0,1))}) = ({POSINF})',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_cond) = eps',
    f'{ROOT}(S,pfunction.ENV,porigin_full) = ((porigin_cond,{origin("pcpath_wrapper",(0,1))}))',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_full) = (PBOOL false)',
    r'n_private_1 =/= n_private_2 /\ n_private_1 =/= n_private_3 /\ n_private_2 =/= n_private_3',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_1[.VALUE = PBOOL false])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)', '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base310"),$ptascii("E_ERROR")),($ptascii("One310"),$ptascii("E_ERROR")),($ptascii("Skipped310"),$ptascii("Unavailable310") ++ [92] ++ $ptascii("Payload"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_1.ORIGIN)',
    'S_no_names = S[.CODE = [pcode[.NAMES = eps]]]', '~$lossy_optional_integer_deferred(S_no_names,pfunction,1)',
    'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3010)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps /\ S_done.FRAMES = eps']
for index in (1,2,3):
    private += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
private += ['$lookup(S_done.ENV,$ptascii("x310")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']

context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
raw_source=ROWS['deferred-mixed-number-tree-infinite-full-ternary-redirect-wrapper-raw-tagged-results']['source']
named_source=ROWS['deferred-mixed-number-tree-infinite-full-ternary-redirect-wrapper-alias-named-reentry']['source']
raw_stage=context+'-- if pcallcontext.ARGC = 0 -- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)'
CASES = {
    'mixed-number-tree-infinite-full-independent-tags': {'source':raw_source,'stage':raw_stage,'checks':raw},
    'mixed-number-tree-infinite-full-independent-forgeries': {'source':raw_source,'stage':raw_stage,'checks':forgeries},
    'mixed-number-tree-infinite-full-independent-private-lifecycle': {'source':named_source,
        'stage':context+'-- if pcallcontext.ARGC = 1 -- if pfunction.ENV.NAMESPACE = $ptascii("MixedNumberTreeInfiniteRedirect310") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 5 -- if S.TODO = $function_tasks(S,pfunction)','checks':private},
}
if __name__ == '__main__':
    protocol.run(CASES,extra_inputs=(Path(__file__),CATALOGUE),runner_flags=('--sl',))
