#!/usr/bin/env python3
"""One computed unary sign preserves a certified all-INT tree and its own bits."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_unary_integer_tree_infinite_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

MAX = 9223372036854775807
POSINF, NEGINF = 9218868437227405312, 18442240474082181120
ONE, NEGZERO, NAN = 4607182418800017408, 9223372036854775808, 18444492273895866368
ROOT = '$lossy_optional_integer_unary_integer_tree_infinite_full_redirect'
OLD = '$lossy_optional_integer_integer_tree_infinite_full_redirect'
NODE = '$lossy_optional_integer_mixed_number_tree_value'


def ni(value):
    text = str(value) if value >= 0 else f'$(-{-value})'
    return f'PINT {text}', f'NINT {text}'


def nf(bits):
    return f'PFLOAT {bits}', f'NFLOAT {bits}'


def product(size):
    if size == 1:
        return {(): ni(MAX)}, f'NScalarInt (INTEGER {MAX}) eps'
    assert size % 2 == 0
    child, expression = product(size // 2)
    nodes = {(): nf((63 * size + 1023) * (1 << 52))}
    for field in (0, 1):
        nodes.update({(field,) + tail: value for tail, value in child.items()})
    return nodes, f'NExprBinaryOpMul ({expression}) ({expression}) eps'


P16, EXPR16 = product(16)
P17 = {(): nf(POSINF), **{(0,) + tail: value for tail, value in P16.items()}, (1,): ni(MAX)}
EXPR17 = f'NExprBinaryOpMul ({EXPR16}) (NScalarInt (INTEGER {MAX}) eps) eps'
NEGATIVE = {(): nf(NEGINF), (0,): ni(1), **{(1,) + tail: value for tail, value in P17.items()}}
EXPR_NEGATIVE = f'NExprBinaryOpMinus (NScalarInt (INTEGER 1) eps) ({EXPR17}) eps'
assert len(P17) == 33 and len(NEGATIVE) == 35


def path(base, fields):
    return base + ' ++ [' + ','.join('PCFIELD ' + str(field) for field in fields) + ']'


def origin(base, fields):
    return 'PORIGIN n_unit (' + path(base, fields) + ')'


base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
raw = base + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
              '$default_cache_owner(S) = (CACHE_SHARED)']
for index, unary, sign, bits, value in [(0, 'POSITIVE', '1', POSINF, 'PINT 0'),
                                       (1, 'NEGATIVE', '$(-1)', NEGINF, 'PNULL')]:
    where = f'pcpath_{index}'
    cond, child, selected = origin(where, (0,)), origin(where, (0, 0)), origin(where, (1,))
    raw += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit {where}',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (NExprTernary expression_cond_{index} expression_selected_{index} expression_skip_{index} metadata_{index})',
        f'$pfshape(expression_cond_{index}) = PFUNARY {unary} expression_child_{index}',
        f'$origin_node(S.SOURCES,{child}) = (expression_child_{index})',
        f'$pfshape(expression_child_{index}) = PFBINARY MULTIPLY expression_left_{index} expression_right_{index}',
        f'$num_mul(NFLOAT {POSINF},NINT {sign}) = NFLOAT {bits}',
        f'$code_expression(pcode.EXPRESSIONS,{where}) = ((z_{index},false))',
        rf'$pool_value(S.POOLS,pdefault_{index}.ORIGIN) = eps /\ $compiled_read(S,pdefault_{index}.ORIGIN) = eps',
        f'$pool_value(S.POOLS,{cond}) = (PFLOAT {bits})',
        f'$code_expression(pcode.EXPRESSIONS,{path(where,(0,))}) = eps',
        f'$compiled_read(S,{cond}) = eps',
        f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where,(0,))}) = 0',
        f'{NODE}(S,{cond}) = eps',
        f'{OLD}(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'{ROOT}(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (({cond},{selected}))',
        f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (({cond},{selected}))',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = (PFLOAT {bits})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{selected}) = ({value})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,{origin(where,(2,))})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED ({value})',
        rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
    for tail, node in P17.items():
        fields, at = (0, 0) + tail, origin(where, (0, 0) + tail)
        label = str(index) + '_' + (''.join(map(str, tail)) or 'root')
        expression = 'expression_node_' + label
        raw += [f'$origin_node(S.SOURCES,{at}) = ({expression})']
        if node[0].startswith('PINT '):
            raw += [f'{expression} = NScalarInt (INTEGER {node[0][5:]}) metadata_node_{label}']
        else:
            raw += [f'$pfshape({expression}) = PFBINARY MULTIPLY expression_left_{label} expression_right_{label}']
        raw += [f'$pool_value(S.POOLS,{at}) = ({node[0]})',
            f'$code_expression(pcode.EXPRESSIONS,{path(where,fields)}) = eps',
            f'$compiled_read(S,{at}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where,fields)}) = 0',
            f'{NODE}(S,{at}) = (({node[1]},true,false))']
raw += ['n_private_0 =/= n_private_1', 'S_done = $drive_steps(S,3010)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps /\ S_done.FRAMES = eps']
for index in (0, 1):
    raw += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
raw += ['$heap_valid($heap_graph(S_done))']

forgeries = base + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
    '$default_at(pfunction.DEFAULTS,0) = (pdefault)', 'pdefault.ORIGIN = PORIGIN n_unit pcpath',
    'porigin_cond = ' + origin('pcpath', (0,)), 'porigin_child = ' + origin('pcpath', (0, 0)),
    'porigin_selected = ' + origin('pcpath', (1,)),
    '$origin_node(S.SOURCES,pdefault.ORIGIN) = (NExprTernary expression_cond expression_selected expression_skip metadata)',
    'expression_cond = NExprUnaryPlus expression_child metadata_unary',
    '$code_expression(pcode.EXPRESSIONS,pcpath) = ((z,false))',
    f'{NODE}(S,porigin_child) = ((NFLOAT {POSINF},true,false))',
    f'{ROOT}(S,pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))']
mutations = {
    'no_redirect': 'S[.CODE = [pcode[.REDIRECTS = eps]]]',
    'duplicate': 'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
    'copy': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 1]) true)]]]]',
    'target': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 2]) false)]]]]',
    'ownpool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath (PINT 0))] ++ ppool.CONSTANTS)]]]',
    'owncode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath z true)] ++ pcode.EXPRESSIONS)]]]',
}
for label, value in [('condtag', 'PINT 0'), ('condsign', f'PFLOAT {NEGINF}')]:
    mutations[label] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath",(0,))}) ({value}))] ++ ppool.CONSTANTS)]]]'
deep = (0, 0, 0, 0, 0)
for label, tail, value in [('finite_power', (0,), f'PFLOAT {(1007+1023)*(1<<52)}'),
                         ('max_neighbor', deep, f'PINT {MAX-1}'),
                         ('max_float_tag', deep, 'PFLOAT 4890909195324358656')]:
    mutations[label] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath",(0,0)+tail)}) ({value}))] ++ ppool.CONSTANTS)]]]'
for fields in [(0,), (0, 0), (0, 0) + deep]:
    label = ''.join(map(str, fields))
    for flag in ['false', 'true']:
        mutations['code' + label + flag] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path("pcpath",fields)}) z {flag})] ++ pcode.EXPRESSIONS)]]]'
    mutations['redirect' + label] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT ({path("pcpath",fields)}) (pcpath ++ [PCFIELD 1]) false)] ++ pcode.REDIRECTS)]]]'
for label, expression in mutations.items():
    forgeries += [f'S_{label} = {expression}', f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
for label in ['condtag', 'condsign', 'code0false', 'code0true', 'redirect0']:
    forgeries += [f'{NODE}(S_{label},porigin_child) = ((NFLOAT {POSINF},true,false))']
for label in ['finite_power', 'max_neighbor', 'max_float_tag']:
    forgeries += [f'$pool_value(S_{label}.POOLS,porigin_cond) = (PFLOAT {POSINF})',
        f'$pool_value(S_{label}.POOLS,porigin_child) = (PFLOAT {POSINF})',
        f'{NODE}(S_{label},porigin_child) = eps']
for fields in [(0,), (0, 0), (1,), (2,), (0, 0) + deep]:
    label = ''.join(map(str, fields))
    forgeries += [f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path("pcpath",fields)}) (NScalarInt (INTEGER 99) eps))] ++ pcunit.OCCURRENCES)]]]',
        f'{ROOT}(S_source_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_source_{label},pfunction,0)']

inf = 'NScalarFloat (FLOAT "7ff0000000000000") eps'
one_float, one_int = 'NScalarFloat (FLOAT "3ff0000000000000") eps', 'NScalarInt (INTEGER 1) eps'
scopes = [
    ('finite', f'NExprUnaryPlus ({EXPR16}) eps', {():nf((1008+1023)*(1<<52)), **{(0,)+tail:node for tail,node in P16.items()}}, (0,), f'((NFLOAT {(1008+1023)*(1<<52)},true,false))'),
    ('nan', f'NExprUnaryPlus (NExprBinaryOpMinus ({EXPR17}) ({EXPR17}) eps) eps',
     {():nf(NAN),(0,):nf(NAN),**{(0,0)+tail:node for tail,node in P17.items()},**{(0,1)+tail:node for tail,node in P17.items()}}, (0,), f'((NFLOAT {NAN},true,false))'),
    ('division_zero', f'NExprUnaryPlus (NExprBinaryOpDiv ({EXPR17}) (NScalarInt (INTEGER 0) eps) eps) eps',
     {():nf(POSINF),(0,):nf(POSINF),**{(0,0)+tail:node for tail,node in P17.items()},(0,1):ni(0)}, (0,), 'eps'),
    ('pure_float', f'NExprUnaryPlus (NExprBinaryOpPlus (NExprBinaryOpPlus ({inf}) ({one_float}) eps) ({one_float}) eps) eps',
     {():nf(POSINF),(0,):nf(POSINF),(0,0):nf(POSINF),(0,0,0):nf(POSINF),(0,0,1):nf(ONE),(0,1):nf(ONE)}, (0,), f'((NFLOAT {POSINF},false,true))'),
    ('mixed', f'NExprUnaryPlus (NExprBinaryOpPlus (NExprBinaryOpPlus ({one_int}) ({one_int}) eps) ({inf}) eps) eps',
     {():nf(POSINF),(0,):nf(POSINF),(0,0):ni(2),(0,0,0):ni(1),(0,0,1):ni(1),(0,1):nf(POSINF)}, (0,), f'((NFLOAT {POSINF},true,true))'),
    ('second_wrapper', f'NExprUnaryPlus (NExprUnaryPlus ({EXPR17}) eps) eps',
     {():nf(POSINF),(0,):nf(POSINF),**{(0,0)+tail:node for tail,node in P17.items()}}, (0,), 'eps'),
    ('flat_child', f'NExprUnaryPlus (NExprBinaryOpMul (NScalarInt (INTEGER {MAX}) eps) (NScalarInt (INTEGER {MAX}) eps) eps) eps',
     {():nf((126+1023)*(1<<52)),(0,):nf((126+1023)*(1<<52)),(0,0):ni(MAX),(0,1):ni(MAX)}, (0,), f'((NFLOAT {(126+1023)*(1<<52)},true,false))'),
    ('old_binary_unary_child', f'NExprBinaryOpPlus (NExprUnaryPlus ({EXPR17}) eps) ({one_int}) eps',
     {():nf(POSINF),(0,):nf(POSINF),**{(0,0)+tail:node for tail,node in P17.items()},(1,):ni(1)}, (), 'eps'),
]
for label, expression, nodes, query, expected in scopes:
    constants = [f'(PCONSTANT ({path("pcpath",(0,)+tail)}) ({node[0]}))' for tail,node in nodes.items()]
    forgeries += [f'expression_{label} = {expression}',
        f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath (NExprTernary expression_{label} expression_selected expression_skip metadata)),(PCOCCURRENCE (pcpath ++ [PCFIELD 0]) expression_{label})] ++ $pcwalk($pcchildren(expression_{label},pcpath ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
        f'S_{label} = S_source_{label}[.POOLS = [ppool[.CONSTANTS = ([' + ','.join(constants) + '] ++ ppool.CONSTANTS)]]]',
        f'{NODE}(S_{label},{origin("pcpath",(0,)+query)}) = {expected}',
        f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
        f'{OLD}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
forgeries += ['expression_changed = NExprUnaryMinus expression_child metadata_unary',
    'expression_default_changed = NExprTernary expression_changed expression_selected expression_skip metadata',
    'S_descriptor_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath expression_default_changed),(PCOCCURRENCE (pcpath ++ [PCFIELD 0]) expression_changed)] ++ pcunit.OCCURRENCES)]]]',
    f'S_descriptor = S_descriptor_source[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath ++ [PCFIELD 0]) (PFLOAT {NEGINF}))] ++ ppool.CONSTANTS)]]]',
    f'{ROOT}(S_descriptor,pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))',
    '$lossy_optional_integer_deferred_value_at(S_descriptor,pfunction.ENV,pdefault.ORIGIN) = (PINT 0)',
    'pfunction.SIGNATURE.PARAMETERS[0].DEFAULT = PSDEFAULT expression_default "deferred"',
    'expression_default =/= expression_default_changed', '~$lossy_optional_integer_deferred(S_descriptor,pfunction,0)']

private = base + ['S.CODE = [pcode]', '$default_cache_owner(S) = (CACHE_SHARED)']
for index, unary, bits, selected_value in [(1, 'POSITIVE', NEGINF, 'PBOOL false'),
                                          (2, 'NEGATIVE', POSINF, f'PFLOAT {NEGZERO}')]:
    where = f'pcpath_wrapper_{index}'
    full, cond, child = origin(where,(0,)), origin(where,(0,0)), origin(where,(0,0,0))
    private += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit {where}',
        f'$origin_node(S.SOURCES,{cond}) = (expression_cond_{index})',
        f'$pfshape(expression_cond_{index}) = PFUNARY {unary} expression_child_{index}',
        f'$origin_node(S.SOURCES,{child}) = (expression_child_{index})',
        f'$pfshape(expression_child_{index}) = PFBINARY SUBTRACT expression_left_{index} expression_right_{index}',
        f'{NODE}(S,{child}) = ((NFLOAT {NEGINF},true,false))',
        f'{NODE}(S,{cond}) = eps', f'{OLD}(S,pfunction.ENV,{full}) = eps',
        f'{ROOT}(S,pfunction.ENV,{full}) = (({cond},{origin(where,(0,1))}))',
        f'$pool_value(S.POOLS,{cond}) = (PFLOAT {bits})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{full}) = ({selected_value})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT 0)',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT 0,CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED (PINT 0)',
        rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
    for tail,node in NEGATIVE.items():
        private += [f'$pool_value(S.POOLS,{origin(where,(0,0,0)+tail)}) = ({node[0]})']
private += ['n_private_1 =/= n_private_2',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_1[.VALUE = PBOOL false])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)', '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base312"),$ptascii("E_ERROR")),($ptascii("One312"),$ptascii("E_ERROR")),($ptascii("Skipped312"),$ptascii("Unavailable312") ++ [92] ++ $ptascii("Payload"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_1.ORIGIN)',
    'S_no_names = S[.CODE = [pcode[.NAMES = eps]]]', '~$lossy_optional_integer_deferred(S_no_names,pfunction,1)',
    'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3010)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps /\ S_done.FRAMES = eps']
for index in (1,2):
    private += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
private += ['$lookup(S_done.ENV,$ptascii("x312")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']

context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
raw_stage = context + '-- if pcallcontext.ARGC = 0 -- if |pfunction.SIGNATURE.PARAMETERS| = 2 -- if S.TODO = $function_tasks(S,pfunction)'
raw_source = ROWS['deferred-unary-integer-tree-infinite-full-ternary-redirect-wrapper-raw-tagged-results']['source']
named_source = ROWS['deferred-unary-integer-tree-infinite-full-ternary-redirect-wrapper-alias-named-reentry']['source']
CASES = {
    'unary-integer-tree-infinite-full-independent-tags': {'source':raw_source,'stage':raw_stage,'checks':raw},
    'unary-integer-tree-infinite-full-independent-forgeries': {'source':raw_source,'stage':raw_stage,'checks':forgeries},
    'unary-integer-tree-infinite-full-independent-private-lifecycle': {'source':named_source,
        'stage':context + '-- if pcallcontext.ARGC = 1 -- if pfunction.ENV.NAMESPACE = $ptascii("UnaryIntegerTreeInfiniteRedirect312") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)','checks':private},
}
if __name__ == '__main__':
    protocol.run(CASES,extra_inputs=(Path(__file__),CATALOGUE),runner_flags=('--sl',))
