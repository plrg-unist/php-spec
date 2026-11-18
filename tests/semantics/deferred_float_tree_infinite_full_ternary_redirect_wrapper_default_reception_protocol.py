import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_float_tree_infinite_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
F = ('F',)
RAW_TREES = [
    ('ADD', ('ADD', ('UP', ('UM', F)), F), F),
    ('ADD', ('MULTIPLY', ('UM', F), ('ADD', F, F)), ('UM', F)),
    ('SUBTRACT', F, ('MULTIPLY', ('UM', F), F)),
    ('SUBTRACT', ('UM', F), ('MULTIPLY', F, F)),
    ('MULTIPLY', ('MULTIPLY', F, F), F),
    ('MULTIPLY', ('MULTIPLY', ('UM', F), F), F),
    ('DIVIDE', ('DIVIDE', F, F), ('MULTIPLY', F, F)),
    ('DIVIDE', ('DIVIDE', ('UM', F), F), ('MULTIPLY', F, F)),
]
NAMED_RAW = {1: 0, 2: 3, 3: 4}
POSITIVE, NEGATIVE = 9218868437227405312, 18442240474082181120
RAW_BITS = [POSITIVE, NEGATIVE, POSITIVE, NEGATIVE, POSITIVE, NEGATIVE, POSITIVE, NEGATIVE]
RAW_VALUES = ['PINT 0', 'PBOOL true', 'PFLOAT 0', 'PFLOAT 9223372036854775808',
              'PFLOAT n_nan', 'PNULL', 'PBOOL true', 'PINT 1']


def node_path(index, tail):
    fields = ','.join(f'PCFIELD {x}' for x in (0,) + tail)
    return f'pcpath_full_{index} ++ [{fields}]'


def node_bits(index, tail):
    label = '_'.join(map(str, tail)) if tail else 'root'
    return f'n_bits_node_{index}_{label}'


def tree_checks(index, tree, tail=(), expression=None):
    label = f'node_{index}_' + ('_'.join(map(str, tail)) if tail else 'root')
    expression = expression or f'expression_{label}'
    path = node_path(index, tail)
    bits = node_bits(index, tail)
    checks = [f'$origin_node(S.SOURCES,PORIGIN n_unit ({path})) = ({expression})']
    tag = tree[0]
    if tag == 'F':
        checks += [f'{expression} = NScalarFloat (FLOAT text_{label}) metadata_{label}',
                   f'{bits} = $hex_bits(text_{label},0)',
                   f'$lossy_optional_integer_float_literal({expression}) = ({bits})']
    elif tag in ('UP', 'UM'):
        child = f'expression_{label}_0'
        sign = 'Plus' if tag == 'UP' else 'Minus'
        checks += [f'{expression} = NExprUnary{sign} {child} metadata_{label}']
        children, child_bits = tree_checks(index, tree[1], tail + (0,), child)
        checks += children
        checks += [f'{bits} = ' + (child_bits if tag == 'UP' else f'$float_neg({child_bits})'),
                   f'$lossy_optional_integer_float_literal({expression}) = ({bits})']
    else:
        assert tag in ('ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE')
        left, right = f'expression_{label}_0', f'expression_{label}_1'
        checks += [f'$pfshape({expression}) = PFBINARY {tag} {left} {right}']
        left_checks, left_bits = tree_checks(index, tree[1], tail + (0,), left)
        right_checks, right_bits = tree_checks(index, tree[2], tail + (1,), right)
        checks += left_checks + right_checks
        checks += [f'$number_binary({tag},NFLOAT {left_bits},NFLOAT {right_bits}) = NUM (NFLOAT {bits})']
    checks += [f'$pool_value(S.POOLS,PORIGIN n_unit ({path})) = (PFLOAT {bits})',
               f'$code_expression(pcode.EXPRESSIONS,{path}) = eps',
               f'$compiled_read(S,PORIGIN n_unit ({path})) = eps',
               f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path}) = 0']
    checks += [f'$lossy_optional_integer_float_tree_value(S,PORIGIN n_unit ({path})) = ({bits})']
    return checks, bits


BASE = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
        'S.CODE = [pcode]', 'n_unit = pcode.UNIT', 'S.POOLS = [ppool]',
        '$default_cache_owner(S) = (CACHE_SHARED)']


def facts(entries, wrapped, cached=False):
    checks = list(BASE)
    for index, raw_index, result in entries:
        expected = RAW_BITS[raw_index]
        received = ('PINT 1' if index == 2 else 'PINT 0') if wrapped else result
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_default_{index}',
            f'pcpath_full_{index} = pcpath_default_{index}' + (' ++ [PCFIELD 0]' if wrapped else ''),
            f'porigin_full_{index} = PORIGIN n_unit pcpath_full_{index}',
            f'$origin_node(S.SOURCES,porigin_full_{index}) = (NExprTernary expression_cond_{index} expression_selected_{index} expression_skipped_{index} metadata_{index})',
            f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])) = (expression_selected_{index})',
            f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])) = (expression_skipped_{index})',
            f'expression_skipped_{index} = NExprConstFetch name_skipped_{index} metadata_skipped_{index}']
        nodes, root_bits = tree_checks(index, RAW_TREES[raw_index], expression=f'expression_cond_{index}')
        checks += nodes + [f'{root_bits} = {expected}',
            f'$lossy_optional_integer_numeric(pfunction.ENV,expression_cond_{index}) = (NFLOAT {expected})',
            f'$float_decode({expected}) = INFINITE n_sign_{index}',
            f'$lossy_optional_integer_condition(pfunction.ENV,expression_cond_{index}) = (true)',
            f'$lossy_optional_integer_quiet_shape(NExprTernary expression_cond_{index} expression_selected_{index} expression_skipped_{index} metadata_{index})',
            f'$code_expression(pcode.EXPRESSIONS,pcpath_full_{index}) = ((z_{index},false))',
            f'$pool_value(S.POOLS,porigin_full_{index}) = eps',
            f'$compiled_read(S,porigin_full_{index}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_full_{index}) = 1',
            f'$compiled_redirect(S,porigin_full_{index}) = ((PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1]),expression_selected_{index},false,z_{index}))',
            f'$code_expression(pcode.EXPRESSIONS,pcpath_full_{index} ++ [PCFIELD 2]) = eps',
            f'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])) = eps',
            f'$compiled_read(S,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])) = eps',
            f'$code_name(pcode.NAMES,pcpath_full_{index} ++ [PCFIELD 2]) = eps',
            f'$call_name_count(pcode.NAMES,pcpath_full_{index} ++ [PCFIELD 2]) = 0',
            f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2]))',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0]))',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1]))',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])) = ({result})']
        if raw_index == 0:
            checks += [f'{node_bits(index,(0,0))} = 9223372036854775808',
                       f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0]))',
                       f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = eps']
        else:
            checks += [f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = (PFLOAT {expected})']
        if raw_index == 1:
            checks += [f'{node_bits(index,(0,1,0))} = 4607182418800017408',
                       f'{node_bits(index,(0,1,1))} = 4607182418800017408',
                       f'{node_bits(index,(0,1))} = 4611686018427387904']
        checks += [f'$lossy_optional_integer_float_tree_infinite_full_redirect(S,pfunction.ENV,porigin_full_{index}) = ((PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0]),PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])))']
        for helper in ('infinite_float', 'computed_infinite_float', 'float_integer_infinite',
                       'integer_float_infinite', 'finite_nonzero_float', 'nonzero_integer'):
            checks += [f'$lossy_optional_integer_{helper}_full_redirect(S,pfunction.ENV,porigin_full_{index}) = eps']
        checks += [f'$lossy_optional_integer_truthy_literal_string_full_redirect(S,porigin_full_{index}) = eps',
            f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_full_{index}) = ((PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0]),PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])))',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_full_{index})',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_full_{index})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_full_{index}) = ({result})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({received})',
            f'$lossy_optional_integer_deferred(S,pfunction,{index})',
            f'$default_current_cache(S,pdefault_{index}.ORIGIN) = eps']

        if raw_index == 4:
            checks += [f'{node_bits(index,(0,0))} = 6910736104866537457',
                       f'{node_bits(index,(0,1))} = 6910736104866537457',
                       f'{node_bits(index,(0,))} = 9214871658872686752']
        if raw_index == 5:
            checks += [f'{node_bits(index,(0,0,0))} = 6910736104866537457',
                       f'{node_bits(index,(0,0))} = 16134108141721313265',
                       f'{node_bits(index,(0,1))} = 6910736104866537457',
                       f'{node_bits(index,(0,))} = 18438243695727462560']
        if cached:
            checks.remove(f'$default_current_cache(S,pdefault_{index}.ORIGIN) = eps')
            checks += [f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {received},CLASS PVSCALAR}}',
                       f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
                       f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
                       f'S.STORE[n_cell_{index}] = DEFINED ({received})',
                       f'~(n_cell_{index} <- S.REFCELLS)',
                       f'$heap_owners($heap_graph(S),HCELL n_cell_{index}) = 1']
    return checks


raw = facts([(index,index,value) for index,value in enumerate(RAW_VALUES)],False,True)
raw += ['$pfcast_nan(PFLOAT n_nan)',
    'S_wrong_mid = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_full_1 ++ [PCFIELD 0,PCFIELD 0,PCFIELD 1]) (PFLOAT 4613937818241073152))] ++ ppool.CONSTANTS)]]]',
    '$pool_value(S_wrong_mid.POOLS,PORIGIN n_unit (pcpath_full_1 ++ [PCFIELD 0])) = (PFLOAT 18442240474082181120)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_cond_1) = (NFLOAT 18442240474082181120)',
    '$lossy_optional_integer_float_tree_value(S_wrong_mid,PORIGIN n_unit (pcpath_full_1 ++ [PCFIELD 0])) = eps',
    '$lossy_optional_integer_float_tree_infinite_full_redirect(S_wrong_mid,pfunction.ENV,porigin_full_1) = eps',
    '~$lossy_optional_integer_deferred(S_wrong_mid,pfunction,1)',
    'S_wrong_bits = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_3[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_bits,S_wrong_bits.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_bits,pfunction,3)',
    'S_done = $drive_steps(S,3010)',
    'S_done.COMPLETION = NORMAL', 'S_done.CURRENT = eps',
    'S_done.FRAMES = eps', 'S_done.TODO = eps',
    '$heap_valid($heap_graph(S_done))',
    '$default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in range(8):
    raw += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            f'~((HCELL n_cell_{index}) <- S_done.ALLOCATIONS)',
            f'$heap_owners($heap_graph(S_done),HCELL n_cell_{index}) = 0']

certificate = facts([(1,0,'PBOOL false'),(2,3,'PINT 1'),
                     (3,4,'PFLOAT 9223372036854775808')],True)
certificate += ['pcallcontext.HOLES = [1,2,3]', 'S.SOURCES = [pcunit]',
    'pcpath_full = pcpath_full_1', 'porigin_full = porigin_full_1',
    'pcpath_cond = pcpath_full ++ [PCFIELD 0]',
    'pcpath_selected = pcpath_full ++ [PCFIELD 1]',
    'pcpath_skipped = pcpath_full ++ [PCFIELD 2]']
mutations = {
    'duplicate': 'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ [(CODEREDIRECT pcpath_full pcpath_selected false)])]]]',
    'copy': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_full pcpath_selected true)]]]]',
    'target': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_full pcpath_skipped false)]]]]',
    'owncode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_full z_1 true)] ++ pcode.EXPRESSIONS)]]]',
    'ownpool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_full (PBOOL false))] ++ ppool.CONSTANTS)]]]',
    'condcode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_cond z_1 false)] ++ pcode.EXPRESSIONS)]]]',
    'condpool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_cond (PBOOL false))] ++ ppool.CONSTANTS)]]]',
    'condsign': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_cond (PFLOAT 18442240474082181120))] ++ ppool.CONSTANTS)]]]',
    'condredirect': 'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT pcpath_cond pcpath_selected false)] ++ pcode.REDIRECTS)]]]',
}


def all_nodes(tree, tail=()):
    result = [tail]
    for field,child in enumerate(tree[1:]):
        result += all_nodes(child,tail + (field,))
    return result


for serial,tail in enumerate(all_nodes(RAW_TREES[0])):
    path = node_path(1,tail)
    mutations[f'nodepool{serial}'] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path}) (PINT 0))] ++ ppool.CONSTANTS)]]]'
    mutations[f'nodecode{serial}'] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path}) z_1 false)] ++ pcode.EXPRESSIONS)]]]'
    mutations[f'noderead{serial}'] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path}) z_1 true)] ++ pcode.EXPRESSIONS)]]]'
    mutations[f'noderedirect{serial}'] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT ({path}) pcpath_selected false)] ++ pcode.REDIRECTS)]]]'
    mutations[f'nodesource{serial}'] = f'S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path}) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]'
for label,expression in mutations.items():
    certificate += [f'S_{label} = {expression}',
        f'$lossy_optional_integer_float_tree_infinite_full_redirect(S_{label},pfunction.ENV,porigin_full) = eps',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,1)']
certificate += ['S_no_names = S[.CODE = [pcode[.NAMES = eps]]]',
    '~$lossy_optional_integer_deferred_bindings(S_no_names,pfunction.ENV,pdefault_1.ORIGIN)',
    '~$lossy_optional_integer_deferred(S_no_names,pfunction,1)']

recipient = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("FloatTreeInfiniteRedirect309")',
    '$default_cache_owner(S) = (CACHE_SHARED)']
for index,value in [(1,0),(2,1),(3,0)]:
    recipient += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED (PINT {value})',
        f'~(n_private_{index} <- S.REFCELLS)',
        f'$heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
recipient += ['pdefault_3.ORIGIN = PORIGIN n_unit pcpath_negative',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_negative ++ [PCFIELD 0])) = (PFLOAT 9223372036854775808)',
    'n_private_1 =/= n_private_2', 'n_private_1 =/= n_private_3', 'n_private_2 =/= n_private_3',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_1[.VALUE = PBOOL false])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    '$heap_valid($heap_graph(S))', '$call_descriptors_valid(S)',
    '$default_caches_valid(S,S.DEFAULTCACHE)',
    'S_done = $drive_steps(S,3010)', 'S_done.COMPLETION = NORMAL',
    'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.TODO = eps']
for index in (1,2,3):
    recipient += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS)',
        f'$heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
recipient += ['$lookup(S_done.ENV,$ptascii("x309")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
    '$default_caches_valid(S_done,S_done.DEFAULTCACHE)']
context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
           '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
           '-- if pfunction.ENV.NAMESPACE = $ptascii("FloatTreeInfiniteRedirect309") '
           '-- if |pfunction.SIGNATURE.PARAMETERS| = 5 ')
named_source = ROWS['deferred-float-tree-infinite-full-ternary-redirect-wrapper-alias-named-reentry']['source']
CASES = {
    'float-tree-infinite-full-raw-tags': {
        'source': ROWS['deferred-float-tree-infinite-full-ternary-redirect-wrapper-raw-tagged-results']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 '
            '-- if pcallcontext.FUNCTION = porigin_function -- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)'),
        'checks': raw},
    'float-tree-infinite-full-certificate-forgeries': {
        'source': named_source,
        'stage': context + '-- if pcallcontext.ARGC = 5 -- if S.TODO = [NAMED_PREFLIGHT porigin_function 0]',
        'checks': certificate},
    'float-tree-infinite-full-private-recipients': {
        'source': named_source,
        'stage': context + '-- if pcallcontext.ARGC = 1 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks': recipient},
}
if __name__ == '__main__':
    protocol.run(CASES,extra_inputs=(Path(__file__),CATALOGUE),runner_flags=('--sl',))
