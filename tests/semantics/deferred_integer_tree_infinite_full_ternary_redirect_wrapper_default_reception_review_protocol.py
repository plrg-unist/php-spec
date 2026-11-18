#!/usr/bin/env python3
"""All-INT trees retain promoted FLOAT pools without acquiring raw FLOAT leaves."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_integer_tree_infinite_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

MAX = 9223372036854775807
POSINF, NEGINF = 9218868437227405312, 18442240474082181120
NEGZERO, ONE, TWO = 9223372036854775808, 4607182418800017408, 4611686018427387904
NAN = 18444492273895866368
ROOT = '$lossy_optional_integer_integer_tree_infinite_full_redirect'
NODE = '$lossy_optional_integer_mixed_number_tree_value'
MIXED_ROOT = '$lossy_optional_integer_mixed_number_tree_infinite_full_redirect'
FLOAT_ROOT = '$lossy_optional_integer_float_tree_infinite_full_redirect'


def ni(value):
    text = str(value) if value >= 0 else f'$(-{-value})'
    return f'PINT {text}', f'NINT {text}'


def nf(bits):
    return f'PFLOAT {bits}', f'NFLOAT {bits}'


def product(size):
    """MAX rounds to 2^63 only after a binary integer operation overflows."""
    if size == 1:
        return {(): ni(MAX)}, f'NScalarInt (INTEGER {MAX}) eps'
    assert size % 2 == 0
    child, expression = product(size // 2)
    bits = (63 * size + 1023) * (1 << 52)
    nodes = {(): nf(bits)}
    for field in (0, 1):
        nodes.update({(field,) + tail: value for tail, value in child.items()})
    return nodes, f'NExprBinaryOpMul ({expression}) ({expression}) eps'


P16, EXPR16 = product(16)
P17 = {(): nf(POSINF), **{(0,) + tail: value for tail, value in P16.items()}, (1,): ni(MAX)}
EXPR17 = f'NExprBinaryOpMul ({EXPR16}) (NScalarInt (INTEGER {MAX}) eps) eps'
RAW_NODES = [
    {(): nf(POSINF), **{(0,) + tail: value for tail, value in P17.items()},
     (1,): ni(2), (1,0): ni(1), (1,1): ni(1)},
    {(): nf(NEGINF), (0,): ni(1), **{(1,) + tail: value for tail, value in P17.items()}},
]
NAMED_NODES = [P17,
    {(): nf(NEGINF), **{(0,) + tail: value for tail, value in P17.items()},
     (1,): ni(-1), (1,0): ni(1)}]
assert [len(nodes) for nodes in RAW_NODES] == [37, 35]
assert [len(nodes) for nodes in NAMED_NODES] == [33, 36]


def path(base, fields):
    return base + ' ++ [' + ','.join('PCFIELD ' + str(field) for field in fields) + ']'


def origin(base, fields):
    return 'PORIGIN n_unit (' + path(base, fields) + ')'


def result(node, kinds='true,false'):
    return f'(({node[1]},{kinds}))'


base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
raw = base + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
              '$default_cache_owner(S) = (CACHE_SHARED)']
for index, (nodes, operator, value) in enumerate(zip(RAW_NODES, ['ADD','SUBTRACT'], ['PINT 0','PNULL'])):
    default, where = f'pdefault_{index}', f'pcpath_{index}'
    cond, selected = origin(where, (0,)), origin(where, (1,))
    raw += [f'$default_at(pfunction.DEFAULTS,{index}) = ({default})',
        f'{default}.ORIGIN = PORIGIN n_unit {where}',
        f'$origin_node(S.SOURCES,{default}.ORIGIN) = (NExprTernary expression_cond_{index} expression_selected_{index} expression_skip_{index} metadata_{index})',
        f'$pfshape(expression_cond_{index}) = PFBINARY {operator} expression_left_{index} expression_right_{index}',
        f'$code_expression(pcode.EXPRESSIONS,{where}) = ((z_{index},false))',
        rf'$pool_value(S.POOLS,{default}.ORIGIN) = eps /\ $compiled_read(S,{default}.ORIGIN) = eps',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = ({nodes[()][0]})',
        f'{FLOAT_ROOT}(S,pfunction.ENV,{default}.ORIGIN) = eps',
        f'{MIXED_ROOT}(S,pfunction.ENV,{default}.ORIGIN) = eps',
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
    for tail,node in nodes.items():
        fields, at = (0,) + tail, origin(where, (0,) + tail)
        raw += [f'$pool_value(S.POOLS,{at}) = ({node[0]})',
            f'$code_expression(pcode.EXPRESSIONS,{path(where, fields)}) = eps',
            f'$compiled_read(S,{at}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where, fields)}) = 0',
            f'{NODE}(S,{at}) = {result(node)}']
raw += ['n_private_0 =/= n_private_1', 'S_done = $drive_steps(S,3010)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps /\ S_done.FRAMES = eps']
for index in (0,1):
    raw += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
raw += ['$heap_valid($heap_graph(S_done))']

forgeries = base + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
    '$default_at(pfunction.DEFAULTS,0) = (pdefault)', 'pdefault.ORIGIN = PORIGIN n_unit pcpath',
    'porigin_cond = ' + origin('pcpath',(0,)), 'porigin_selected = ' + origin('pcpath',(1,)),
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
finite = (0,0)
deep_leaf = (0,0,0,0,0,0)
for label,tail,value in [
        ('condtag',(),'PBOOL true'), ('condsign',(),f'PFLOAT {NEGINF}'),
        ('finite_power',finite,f'PFLOAT {(1007+1023)*(1<<52)}'),
        ('integer_two_tag',(1,),f'PFLOAT {TWO}'),
        ('max_neighbor',deep_leaf,f'PINT {MAX-1}'),
        ('max_float_tag',deep_leaf,'PFLOAT 4890909195324358656')]:
    fields = (0,) + tail
    mutations[label] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath",fields)}) ({value}))] ++ ppool.CONSTANTS)]]]'
for tail in [(),finite,deep_leaf,(1,)]:
    fields = (0,) + tail
    label = ''.join(map(str,fields))
    for flag in ['false','true']:
        mutations['code'+label+flag] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path("pcpath",fields)}) z {flag})] ++ pcode.EXPRESSIONS)]]]'
    mutations['redirect'+label] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT ({path("pcpath",fields)}) (pcpath ++ [PCFIELD 1]) false)] ++ pcode.REDIRECTS)]]]'
for label,expression in mutations.items():
    forgeries += [f'S_{label} = {expression}', f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
for label,tail in [('finite_power',finite),('integer_two_tag',(1,)),('max_neighbor',deep_leaf),('max_float_tag',deep_leaf)]:
    forgeries += [f'$pool_value(S_{label}.POOLS,porigin_cond) = (PFLOAT {POSINF})',
        f'{NODE}(S_{label},{origin("pcpath",(0,)+tail)}) = eps']
for fields in [(0,), (1,), (2,), (0,)+deep_leaf]:
    label = ''.join(map(str,fields))
    forgeries += [f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path("pcpath",fields)}) (NScalarInt (INTEGER 99) eps))] ++ pcunit.OCCURRENCES)]]]',
        f'{ROOT}(S_source_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_source_{label},pfunction,0)']

inf = 'NScalarFloat (FLOAT "7ff0000000000000") eps'
one_float = 'NScalarFloat (FLOAT "3ff0000000000000") eps'
one_int = 'NScalarInt (INTEGER 1) eps'
scopes = [
    ('pure_float',f'NExprBinaryOpPlus (NExprBinaryOpPlus ({inf}) ({one_float}) eps) ({one_float}) eps',
     {():nf(POSINF),(0,):nf(POSINF),(0,0):nf(POSINF),(0,1):nf(ONE),(1,):nf(ONE)},nf(POSINF),'false,true'),
    ('mixed',f'NExprBinaryOpPlus (NExprBinaryOpPlus ({one_int}) ({one_int}) eps) ({inf}) eps',
     {():nf(POSINF),(0,):ni(2),(0,0):ni(1),(0,1):ni(1),(1,):nf(POSINF)},nf(POSINF),'true,true'),
    ('finite_int',f'NExprBinaryOpPlus (NExprBinaryOpPlus ({one_int}) ({one_int}) eps) ({one_int}) eps',
     {():ni(3),(0,):ni(2),(0,0):ni(1),(0,1):ni(1),(1,):ni(1)},ni(3),'true,false'),
    ('finite_float',EXPR16,P16,nf((1008+1023)*(1<<52)),'true,false'),
    ('nan',f'NExprBinaryOpMinus ({EXPR17}) ({EXPR17}) eps',
     {():nf(NAN),**{(0,)+tail:value for tail,value in P17.items()},**{(1,)+tail:value for tail,value in P17.items()}},nf(NAN),'true,false'),
    ('division_zero',f'NExprBinaryOpDiv ({EXPR17}) (NScalarInt (INTEGER 0) eps) eps',
     {():nf(POSINF),**{(0,)+tail:value for tail,value in P17.items()},(1,):ni(0)},None,'true,false'),
]
for label,expression,nodes,value,kinds in scopes:
    constants=[f'(PCONSTANT ({path("pcpath",(0,)+tail)}) ({node[0]}))' for tail,node in nodes.items()]
    forgeries += [f'expression_{label} = {expression}',
        f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath (NExprTernary expression_{label} expression_selected expression_skip metadata)),(PCOCCURRENCE (pcpath ++ [PCFIELD 0]) expression_{label})] ++ $pcwalk($pcchildren(expression_{label},pcpath ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
        f'S_{label} = S_source_{label}[.POOLS = [ppool[.CONSTANTS = ([' + ','.join(constants) + '] ++ ppool.CONSTANTS)]]]',
        f'{NODE}(S_{label},porigin_cond) = ' + ('eps' if value is None else result(value,kinds)),
        f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
for label,earlier in [('pure_float',FLOAT_ROOT),('mixed',MIXED_ROOT)]:
    forgeries += [f'{earlier}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))',
        f'$lossy_optional_integer_deferred_value_at(S_{label},pfunction.ENV,pdefault.ORIGIN) = (PINT 0)']

private = base + ['$default_cache_owner(S) = (CACHE_SHARED)', 'S.CODE = [pcode]']
for index,(nodes,operator,selected_value) in enumerate(zip(NAMED_NODES,['MULTIPLY','DIVIDE'],['PBOOL false',f'PFLOAT {NEGZERO}']),1):
    where = f'pcpath_wrapper_{index}'
    full,cond = origin(where,(0,)),origin(where,(0,0))
    private += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit {where}',
        f'$origin_node(S.SOURCES,{cond}) = (expression_cond_{index})',
        f'$pfshape(expression_cond_{index}) = PFBINARY {operator} expression_left_{index} expression_right_{index}',
        f'{NODE}(S,{cond}) = {result(nodes[()])}',
        f'{MIXED_ROOT}(S,pfunction.ENV,{full}) = eps',
        f'{ROOT}(S,pfunction.ENV,{full}) = (({cond},{origin(where,(0,1))}))',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = ({nodes[()][0]})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{full}) = ({selected_value})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT 0)',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT 0,CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED (PINT 0)',
        rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
    for tail,node in nodes.items():
        private += [f'$pool_value(S.POOLS,{origin(where,(0,0)+tail)}) = ({node[0]})']
private += [f'{NODE}(S,{origin("pcpath_wrapper_2",(0,0,1))}) = {result(ni(-1))}',
    f'{NODE}(S,{origin("pcpath_wrapper_2",(0,0,1,0))}) = {result(ni(1))}',
    'n_private_1 =/= n_private_2',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_1[.VALUE = PBOOL false])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)', '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base311"),$ptascii("E_ERROR")),($ptascii("One311"),$ptascii("E_ERROR")),($ptascii("Skipped311"),$ptascii("Unavailable311") ++ [92] ++ $ptascii("Payload"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_1.ORIGIN)',
    'S_no_names = S[.CODE = [pcode[.NAMES = eps]]]', '~$lossy_optional_integer_deferred(S_no_names,pfunction,1)',
    'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3010)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps /\ S_done.FRAMES = eps']
for index in (1,2):
    private += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
private += ['$lookup(S_done.ENV,$ptascii("x311")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']

context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
raw_source=ROWS['deferred-integer-tree-infinite-full-ternary-redirect-wrapper-raw-tagged-results']['source']
named_source=ROWS['deferred-integer-tree-infinite-full-ternary-redirect-wrapper-alias-named-reentry']['source']
raw_stage=context+'-- if pcallcontext.ARGC = 0 -- if |pfunction.SIGNATURE.PARAMETERS| = 2 -- if S.TODO = $function_tasks(S,pfunction)'
CASES = {
    'integer-tree-infinite-full-independent-tags': {'source':raw_source,'stage':raw_stage,'checks':raw},
    'integer-tree-infinite-full-independent-forgeries': {'source':raw_source,'stage':raw_stage,'checks':forgeries},
    'integer-tree-infinite-full-independent-private-lifecycle': {'source':named_source,
        'stage':context+'-- if pcallcontext.ARGC = 1 -- if pfunction.ENV.NAMESPACE = $ptascii("IntegerTreeInfiniteRedirect311") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)','checks':private},
}
if __name__ == '__main__':
    protocol.run(CASES,extra_inputs=(Path(__file__),CATALOGUE),runner_flags=('--sl',))
