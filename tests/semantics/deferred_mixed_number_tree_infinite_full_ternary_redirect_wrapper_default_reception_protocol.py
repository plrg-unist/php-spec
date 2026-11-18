import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_mixed_number_tree_infinite_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
POSITIVE, NEGATIVE = 9218868437227405312, 18442240474082181120
MAX = 9223372036854775807
TWO63 = 4890909195324358656
MINUS_ONE_FLOAT = 13830554455654793216
MINUS_TWO_POINT_FIVE = 13836183955189006336
# Every node records its exact compiler tag; values are independent literals.
def I(value): return ('I', f'NINT {value}')
def F(bits): return ('F', f'NFLOAT {bits}')
def U(sign, value, child): return (sign, value, child)
def B(op, value, left, right): return (op, value, left, right)
RAW_TREES = [
    B('ADD',f'NFLOAT {POSITIVE}',B('ADD','NINT 2',I(1),I(1)),B('ADD',f'NFLOAT {POSITIVE}',U('UP','NFLOAT 9223372036854775808',U('UM','NFLOAT 9223372036854775808',F(0))),F(POSITIVE))),
    B('ADD',f'NFLOAT {NEGATIVE}',B('SUBTRACT','NINT $(-2)',U('UM','NINT $(-1)',I(1)),I(1)),U('UM',f'NFLOAT {NEGATIVE}',F(POSITIVE))),
    B('SUBTRACT',f'NFLOAT {POSITIVE}',F(POSITIVE),B('SUBTRACT','NINT $(-2)',U('UM','NINT $(-1)',I(1)),I(1))),
    B('SUBTRACT',f'NFLOAT {NEGATIVE}',U('UM',f'NFLOAT {NEGATIVE}',F(POSITIVE)),B('ADD','NINT 2',I(1),I(1))),
    B('MULTIPLY',f'NFLOAT {POSITIVE}',B('ADD',f'NFLOAT {TWO63}',I(MAX),I(1)),F(POSITIVE)),
    B('MULTIPLY',f'NFLOAT {NEGATIVE}',B('SUBTRACT',f'NFLOAT {MINUS_ONE_FLOAT}',B('SUBTRACT','NFLOAT 0',B('ADD',f'NFLOAT {TWO63}',I(MAX),I(1)),I(MAX)),I(1)),F(POSITIVE)),
    B('DIVIDE',f'NFLOAT {POSITIVE}',B('DIVIDE','NINT 2',I(4),I(2)),F(1)),
    B('DIVIDE',f'NFLOAT {NEGATIVE}',B('DIVIDE',f'NFLOAT {MINUS_TWO_POINT_FIVE}',U('UM','NINT $(-5)',I(5)),I(2)),F(1)),
]
RAW_BITS = [POSITIVE,NEGATIVE,POSITIVE,NEGATIVE,POSITIVE,NEGATIVE,POSITIVE,NEGATIVE]
NAMED_RAW = {1:0,2:3,3:4}
RAW_VALUES = ['PINT 0','PBOOL true','PFLOAT 0','PFLOAT 9223372036854775808',
              'PFLOAT n_nan','PNULL','PBOOL true','PINT 1']

def node_path(index,tail):
    fields=','.join(f'PCFIELD {x}' for x in (0,)+tail)
    return f'pcpath_full_{index} ++ [{fields}]'

def node_number(index,tail):
    return f'pnumber_node_{index}_'+('_'.join(map(str,tail)) if tail else 'root')

def kinds(tree):
    if tree[0]=='I': return True,False
    if tree[0]=='F': return False,True
    children=[kinds(x) for x in tree[2:]]
    return any(x[0] for x in children),any(x[1] for x in children)

def tree_checks(index,tree,tail=(),expression=None):
    label=f'node_{index}_'+('_'.join(map(str,tail)) if tail else 'root')
    expression=expression or f'expression_{label}'
    path=node_path(index,tail);number=node_number(index,tail)
    checks=[f'$origin_node(S.SOURCES,PORIGIN n_unit ({path})) = ({expression})',f'{number} = {tree[1]}']
    tag=tree[0]
    if tag=='I':
        checks += [f'{expression} = NScalarInt (INTEGER i_{label}) metadata_{label}',
            f'{number} = NINT i_{label}',f'$lossy_optional_integer_integer_literal({expression}) = (i_{label})']
    elif tag=='F':
        checks += [f'{expression} = NScalarFloat (FLOAT text_{label}) metadata_{label}',
            f'{number} = NFLOAT n_bits_{label}',f'n_bits_{label} = $hex_bits(text_{label},0)',
            f'$lossy_optional_integer_float_literal({expression}) = (n_bits_{label})']
    elif tag in ('UP','UM'):
        child=f'expression_{label}_0';sign='Plus' if tag=='UP' else 'Minus'
        checks += [f'{expression} = NExprUnary{sign} {child} metadata_{label}']
        more,child_number=tree_checks(index,tree[2],tail+(0,),child);checks += more
        if kinds(tree)[0]:
            checks += [f'{number} = NINT i_{label}',f'$lossy_optional_integer_integer_literal({expression}) = (i_{label})']
        else:
            checks += [f'{number} = NFLOAT n_bits_{label}',f'$lossy_optional_integer_float_literal({expression}) = (n_bits_{label})']
    else:
        left,right=f'expression_{label}_0',f'expression_{label}_1'
        checks += [f'$pfshape({expression}) = PFBINARY {tag} {left} {right}']
        lc,ln=tree_checks(index,tree[2],tail+(0,),left)
        rc,rn=tree_checks(index,tree[3],tail+(1,),right)
        checks += lc+rc+[f'$number_binary({tag},{ln},{rn}) = NUM {number}']
    checks += [f'$pool_value(S.POOLS,PORIGIN n_unit ({path})) = ($number_value({number}))',
        f'$code_expression(pcode.EXPRESSIONS,{path}) = eps',f'$compiled_read(S,PORIGIN n_unit ({path})) = eps',
        f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path}) = 0']
    if not kinds(tree)[0]:
        checks += [f'{number} = NFLOAT n_float_{label}',f'$lossy_optional_integer_float_tree_value(S,PORIGIN n_unit ({path})) = (n_float_{label})']
    has_int,has_float=kinds(tree)
    checks += [f'$lossy_optional_integer_mixed_number_tree_value(S,PORIGIN n_unit ({path})) = (({number},{str(has_int).lower()},{str(has_float).lower()}))']
    return checks,number

BASE=['S.CURRENT = (pcallcontext)','pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)','S.CODE = [pcode]',
    'n_unit = pcode.UNIT','S.POOLS = [ppool]','$default_cache_owner(S) = (CACHE_SHARED)']

def facts(entries,wrapped,cached=False):
    checks=list(BASE)
    for index,raw_index,result in entries:
        expected=RAW_BITS[raw_index]
        received=('PINT 1' if index==2 else 'PINT 0') if wrapped else result
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_default_{index}',
            f'pcpath_full_{index} = pcpath_default_{index}'+(' ++ [PCFIELD 0]' if wrapped else ''),
            f'porigin_full_{index} = PORIGIN n_unit pcpath_full_{index}',
            f'$origin_node(S.SOURCES,porigin_full_{index}) = (NExprTernary expression_cond_{index} expression_selected_{index} expression_skipped_{index} metadata_{index})',
            f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])) = (expression_selected_{index})',
            f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])) = (expression_skipped_{index})',
            f'expression_skipped_{index} = NExprConstFetch name_skipped_{index} metadata_skipped_{index}']
        nodes,root_number=tree_checks(index,RAW_TREES[raw_index],expression=f'expression_cond_{index}')
        checks += nodes+[f'{root_number} = NFLOAT {expected}',
            f'$lossy_optional_integer_numeric(pfunction.ENV,expression_cond_{index}) = (NFLOAT {expected})',
            f'$float_decode({expected}) = INFINITE n_sign_{index}',
            f'$lossy_optional_integer_condition(pfunction.ENV,expression_cond_{index}) = (true)',
            f'$lossy_optional_integer_quiet_shape(NExprTernary expression_cond_{index} expression_selected_{index} expression_skipped_{index} metadata_{index})',
            f'$code_expression(pcode.EXPRESSIONS,pcpath_full_{index}) = ((z_{index},false))',
            f'$pool_value(S.POOLS,porigin_full_{index}) = eps',f'$compiled_read(S,porigin_full_{index}) = eps',
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
        if raw_index==0:
            checks += [f'{node_number(index,(1,0))} = NFLOAT 9223372036854775808',
                f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0]))',
                f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = eps']
        else:
            checks += [f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = (PFLOAT {expected})']
        for helper in ('infinite_float','computed_infinite_float','float_integer_infinite','integer_float_infinite','float_tree_infinite','finite_nonzero_float','nonzero_integer'):
            checks += [f'$lossy_optional_integer_{helper}_full_redirect(S,pfunction.ENV,porigin_full_{index}) = eps']
        checks += [f'$lossy_optional_integer_mixed_number_tree_infinite_full_redirect(S,pfunction.ENV,porigin_full_{index}) = ((PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0]),PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])))',
            f'$lossy_optional_integer_truthy_literal_string_full_redirect(S,porigin_full_{index}) = eps',
            f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_full_{index}) = ((PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0]),PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])))',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_full_{index})',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_full_{index})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_full_{index}) = ({result})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({received})',
            f'$lossy_optional_integer_deferred(S,pfunction,{index})',f'$default_current_cache(S,pdefault_{index}.ORIGIN) = eps']
        if cached:
            checks.remove(f'$default_current_cache(S,pdefault_{index}.ORIGIN) = eps')
            checks += [f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {received},CLASS PVSCALAR}}',
                f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
                f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
                f'S.STORE[n_cell_{index}] = DEFINED ({received})',f'~(n_cell_{index} <- S.REFCELLS)',
                f'$heap_owners($heap_graph(S),HCELL n_cell_{index}) = 1']
    return checks

raw = facts([(index,index,value) for index,value in enumerate(RAW_VALUES)],False,True)
raw += ['$pfcast_nan(PFLOAT n_nan)',
    'S_wrong_tag = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_full_0 ++ [PCFIELD 0,PCFIELD 0]) (PFLOAT 4611686018427387904))] ++ ppool.CONSTANTS)]]]',
    '$pool_value(S_wrong_tag.POOLS,PORIGIN n_unit (pcpath_full_0 ++ [PCFIELD 0])) = (PFLOAT 9218868437227405312)',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_cond_0) = (NFLOAT 9218868437227405312)',
    '$lossy_optional_integer_mixed_number_tree_value(S_wrong_tag,PORIGIN n_unit (pcpath_full_0 ++ [PCFIELD 0])) = eps',
    '$lossy_optional_integer_mixed_number_tree_infinite_full_redirect(S_wrong_tag,pfunction.ENV,porigin_full_0) = eps',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,0)',
    'S_reinteger = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_full_5 ++ [PCFIELD 0,PCFIELD 0,PCFIELD 0]) (PINT 0))] ++ ppool.CONSTANTS)]]]',
    '$pool_value(S_reinteger.POOLS,PORIGIN n_unit (pcpath_full_5 ++ [PCFIELD 0])) = (PFLOAT 18442240474082181120)',
    '$lossy_optional_integer_mixed_number_tree_value(S_reinteger,PORIGIN n_unit (pcpath_full_5 ++ [PCFIELD 0])) = eps',
    '$lossy_optional_integer_mixed_number_tree_infinite_full_redirect(S_reinteger,pfunction.ENV,porigin_full_5) = eps',
    '~$lossy_optional_integer_deferred(S_reinteger,pfunction,5)',
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
    for field,child in enumerate(tree[2:]):
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
        f'$lossy_optional_integer_mixed_number_tree_infinite_full_redirect(S_{label},pfunction.ENV,porigin_full) = eps',
        f'~$lossy_optional_integer_deferred(S_{label},pfunction,1)']
certificate += ['S_no_names = S[.CODE = [pcode[.NAMES = eps]]]',
    '~$lossy_optional_integer_deferred_bindings(S_no_names,pfunction.ENV,pdefault_1.ORIGIN)',
    '~$lossy_optional_integer_deferred(S_no_names,pfunction,1)']

recipient = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
    '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("MixedNumberTreeInfiniteRedirect310")',
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
recipient += ['$lookup(S_done.ENV,$ptascii("x310")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    '$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)',
    '$default_caches_valid(S_done,S_done.DEFAULTCACHE)']
context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
           '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
           '-- if pfunction.ENV.NAMESPACE = $ptascii("MixedNumberTreeInfiniteRedirect310") '
           '-- if |pfunction.SIGNATURE.PARAMETERS| = 5 ')
named_source = ROWS['deferred-mixed-number-tree-infinite-full-ternary-redirect-wrapper-alias-named-reentry']['source']
CASES = {
    'mixed-number-tree-infinite-full-raw-tags': {
        'source': ROWS['deferred-mixed-number-tree-infinite-full-ternary-redirect-wrapper-raw-tagged-results']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 '
            '-- if pcallcontext.FUNCTION = porigin_function -- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)'),
        'checks': raw},
    'mixed-number-tree-infinite-full-certificate-forgeries': {
        'source': named_source,
        'stage': context + '-- if pcallcontext.ARGC = 5 -- if S.TODO = [NAMED_PREFLIGHT porigin_function 0]',
        'checks': certificate},
    'mixed-number-tree-infinite-full-private-recipients': {
        'source': named_source,
        'stage': context + '-- if pcallcontext.ARGC = 1 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks': recipient},
}
if __name__ == '__main__':
    protocol.run(CASES,extra_inputs=(Path(__file__),CATALOGUE),runner_flags=('--sl',))
