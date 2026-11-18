#!/usr/bin/env python3
"""Raw FLOAT presence and signed-zero phase proofs survive one outer sign."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_unary_float_number_tree_infinite_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

POSINF, NEGINF = 9218868437227405312, 18442240474082181120
NEGZERO, ONE, TWO, NAN = 9223372036854775808, 4607182418800017408, 4611686018427387904, 18444492273895866368
MAX = 9223372036854775807
ROOT = '$lossy_optional_integer_unary_float_number_tree_infinite_full_redirect'
OLD = '$lossy_optional_integer_unary_integer_tree_infinite_full_redirect'
NODE = '$lossy_optional_integer_mixed_number_tree_value'
OPS = {'ADD':'Plus', 'SUBTRACT':'Minus', 'MULTIPLY':'Mul', 'DIVIDE':'Div'}


def I(value): return ('I', f'NINT {value}')
def F(bits): return ('F', f'NFLOAT {bits}')
def U(tag, bits, child): return (tag, f'NFLOAT {bits}', child)
def B(tag, number, left, right): return (tag, number, left, right)


def int_product(size):
    if size == 1: return I(MAX)
    child = int_product(size // 2)
    return B('MULTIPLY', f'NFLOAT {(63 * size + 1023) * (1 << 52)}', child, child)


ALL_INT = B('MULTIPLY', f'NFLOAT {POSINF}', int_product(16), I(MAX))
ZERO_SIGN = U('UP', NEGZERO, U('UM', NEGZERO, F(0)))
FLOAT_PART = B('ADD', f'NFLOAT {POSINF}', F(POSINF), ZERO_SIGN)
PURE = B('ADD', f'NFLOAT {POSINF}', FLOAT_PART, F(ONE))
MIXED = B('ADD', f'NFLOAT {POSINF}', B('DIVIDE', 'NINT 2', I(2), I(1)), FLOAT_PART)
NEGATIVE = {'pure':B('SUBTRACT', f'NFLOAT {NEGINF}', F(0), PURE),
            'mixed':B('SUBTRACT', f'NFLOAT {NEGINF}', I(0), MIXED)}
TREES = {'pure':PURE, 'mixed':MIXED}
ZERO_PATH = {'pure':(0,1), 'mixed':(1,1)}


def kinds(tree):
    if tree[0] == 'I': return True, False
    if tree[0] == 'F': return False, True
    flags = [kinds(child) for child in tree[2:]]
    return any(x[0] for x in flags), any(x[1] for x in flags)


def walk(tree, tail=()):
    result = {tail:tree}
    for index, child in enumerate(tree[2:]):
        result.update(walk(child, tail + (index,)))
    return result


def ast(tree):
    tag, number = tree[:2]
    if tag == 'I': return f'NScalarInt (INTEGER {number[5:]}) eps'
    if tag == 'F': return f'NScalarFloat (FLOAT "{int(number[7:]):016x}") eps'
    if tag in ['UP','UM']:
        return f'NExprUnary{"Plus" if tag == "UP" else "Minus"} ({ast(tree[2])}) eps'
    return f'NExprBinaryOp{OPS[tag]} ({ast(tree[2])}) ({ast(tree[3])}) eps'


def value(tree): return ('PINT ' + tree[1][5:]) if tree[1].startswith('NINT ') else ('PFLOAT ' + tree[1][7:])
def flags(tree): return ','.join(str(x).lower() for x in kinds(tree))
def path(base, fields): return base + ' ++ [' + ','.join('PCFIELD ' + str(x) for x in fields) + ']'
def origin(base, fields): return 'PORIGIN n_unit (' + path(base, fields) + ')'
def expression(index, tail): return 'expression_node_' + str(index) + '_' + (''.join(map(str, tail)) or 'root')


BASE = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
CONTEXT = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
RAW_STAGE = CONTEXT + '-- if pcallcontext.ARGC = 0 -- if |pfunction.SIGNATURE.PARAMETERS| = 2 -- if S.TODO = $function_tasks(S,pfunction)'


def raw_checks(group):
    tree = TREES[group]
    checks = BASE + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]', '$default_cache_owner(S) = (CACHE_SHARED)']
    for index, unary, bits, selected_value in [(0,'POSITIVE',POSINF,'PINT 0'), (1,'NEGATIVE',NEGINF,'PNULL')]:
        where = f'pcpath_{index}'
        cond, child, selected = origin(where,(0,)), origin(where,(0,0)), origin(where,(1,))
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'pdefault_{index}.ORIGIN = PORIGIN n_unit {where}',
            f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (NExprTernary expression_cond_{index} expression_selected_{index} expression_skip_{index} metadata_{index})',
            f'$pfshape(expression_cond_{index}) = PFUNARY {unary} {expression(index,())}',
            f'$code_expression(pcode.EXPRESSIONS,{where}) = ((z_{index},false))',
            rf'$pool_value(S.POOLS,pdefault_{index}.ORIGIN) = eps /\ $compiled_read(S,pdefault_{index}.ORIGIN) = eps',
            f'$pool_value(S.POOLS,{cond}) = (PFLOAT {bits})',
            f'$code_expression(pcode.EXPRESSIONS,{path(where,(0,))}) = eps',
            f'$compiled_read(S,{cond}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where,(0,))}) = 0',
            f'{NODE}(S,{child}) = (({tree[1]},{flags(tree)}))', f'{NODE}(S,{cond}) = eps',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,{child})',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,{cond})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = eps',
            f'{OLD}(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
            f'{ROOT}(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (({cond},{selected}))',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({selected_value})',
            f'$lossy_optional_integer_deferred(S,pfunction,{index})',
            f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,{origin(where,(2,))})',
            f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {selected_value},CLASS PVSCALAR}}',
            f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
            f'S.STORE[n_private_{index}] = DEFINED ({selected_value})',
            rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
        for tail, node in walk(tree).items():
            at, fields, expr = origin(where,(0,0)+tail), (0,0)+tail, expression(index,tail)
            checks += [f'$origin_node(S.SOURCES,{at}) = ({expr})']
            if node[0] == 'I': checks += [f'{expr} = NScalarInt (INTEGER {node[1][5:]}) metadata_{index}_{len(checks)}']
            elif node[0] == 'F': checks += [f'{expr} = NScalarFloat (FLOAT "{int(node[1][7:]):016x}") metadata_{index}_{len(checks)}']
            elif node[0] in ['UP','UM']:
                checks += [f'$pfshape({expr}) = PFUNARY {"POSITIVE" if node[0] == "UP" else "NEGATIVE"} {expression(index,tail+(0,))}']
            else:
                checks += [f'$pfshape({expr}) = PFBINARY {node[0]} {expression(index,tail+(0,))} {expression(index,tail+(1,))}']
            checks += [f'$pool_value(S.POOLS,{at}) = ({value(node)})',
                f'$code_expression(pcode.EXPRESSIONS,{path(where,fields)}) = eps', f'$compiled_read(S,{at}) = eps',
                f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where,fields)}) = 0',
                f'{NODE}(S,{at}) = (({node[1]},{flags(node)}))']
            if not kinds(node)[0]: checks += [f'$lossy_optional_integer_float_tree_value(S,{at}) = ({node[1][7:]})']
    checks += ['n_private_0 =/= n_private_1', 'S_done = $drive_steps(S,3010)',
        r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps /\ S_done.FRAMES = eps']
    for index in (0,1):
        checks += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
    return checks + ['$heap_valid($heap_graph(S_done))']


def forgeries(group):
    tree = TREES[group]
    checks = BASE + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)', 'pdefault.ORIGIN = PORIGIN n_unit pcpath',
        'porigin_cond = ' + origin('pcpath',(0,)), 'porigin_child = ' + origin('pcpath',(0,0)),
        'porigin_selected = ' + origin('pcpath',(1,)),
        '$origin_node(S.SOURCES,pdefault.ORIGIN) = (NExprTernary expression_cond expression_selected expression_skip metadata)',
        'expression_cond = NExprUnaryPlus expression_child metadata_unary',
        '$code_expression(pcode.EXPRESSIONS,pcpath) = ((z,false))',
        f'{NODE}(S,porigin_child) = (({tree[1]},{flags(tree)}))',
        f'{ROOT}(S,pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))']
    mutations = {'no_redirect':'S[.CODE = [pcode[.REDIRECTS = eps]]]',
        'duplicate':'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
        'copy':'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 1]) true)]]]]',
        'target':'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 2]) false)]]]]',
        'ownpool':'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath (PINT 0))] ++ ppool.CONSTANTS)]]]',
        'owncode':'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath z true)] ++ pcode.EXPRESSIONS)]]]',
    }
    pools = [('condtag',(0,),'PINT 0'), ('condsign',(0,),f'PFLOAT {NEGINF}'),
             ('zero_sign',(0,0)+ZERO_PATH[group],'PFLOAT 0'),
             ('zero_tag',(0,0)+ZERO_PATH[group]+(0,0),'PINT 0')]
    if group == 'mixed': pools += [('division_tag',(0,0,0),f'PFLOAT {TWO}')]
    for label, fields, val in pools:
        mutations[label] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath",fields)}) ({val}))] ++ ppool.CONSTANTS)]]]'
    for fields in [(0,), (0,0), (0,0)+ZERO_PATH[group]]:
        label = ''.join(map(str,fields))
        for flag in ['false','true']:
            mutations['code'+label+flag] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path("pcpath",fields)}) z {flag})] ++ pcode.EXPRESSIONS)]]]'
        mutations['redirect'+label] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT ({path("pcpath",fields)}) (pcpath ++ [PCFIELD 1]) false)] ++ pcode.REDIRECTS)]]]'
    for label, update in mutations.items():
        checks += [f'S_{label} = {update}', f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
            f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
    for label in ['condtag','condsign','code0false','code0true','redirect0']:
        checks += [f'{NODE}(S_{label},porigin_child) = (({tree[1]},{flags(tree)}))']
    for label in ['zero_sign','zero_tag'] + (['division_tag'] if group == 'mixed' else []):
        checks += [f'$pool_value(S_{label}.POOLS,porigin_cond) = (PFLOAT {POSINF})',
            f'$pool_value(S_{label}.POOLS,porigin_child) = (PFLOAT {POSINF})', f'{NODE}(S_{label},porigin_child) = eps']
    for fields in [(0,), (0,0), (1,), (2,), (0,0)+ZERO_PATH[group]+(0,0)]:
        label = ''.join(map(str,fields))
        checks += [f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path("pcpath",fields)}) (NScalarInt (INTEGER 99) eps))] ++ pcunit.OCCURRENCES)]]]',
            f'{ROOT}(S_source_{label},pfunction.ENV,pdefault.ORIGIN) = eps', f'~$lossy_optional_integer_deferred(S_source_{label},pfunction,0)']
    controls = [('finite',U('UP',TWO,B('ADD',f'NFLOAT {TWO}',B('ADD',f'NFLOAT {ONE}',F(ONE),F(0)),F(ONE))),False),
        ('flat_child',U('UP',POSINF,B('ADD',f'NFLOAT {POSINF}',F(POSINF),F(ONE))),False),
        ('all_int',U('UP',POSINF,ALL_INT),False),
        ('nan',U('UP',NAN,B('SUBTRACT',f'NFLOAT {NAN}',tree,tree)),False),
        ('divzero',U('UP',POSINF,B('DIVIDE',f'NFLOAT {POSINF}',tree,F(0))),True),
        ('second_wrapper',U('UP',POSINF,U('UP',POSINF,tree)),True),
        ('old_binary_unary_child',B('ADD',f'NFLOAT {POSINF}',U('UP',POSINF,tree),F(ONE)),True)]
    for label, condition, node_refuses in controls:
        constants = [f'(PCONSTANT ({path("pcpath",(0,)+tail)}) ({value(node)}))' for tail,node in walk(condition).items()]
        query = () if label == 'old_binary_unary_child' else (0,)
        child = condition if not query else condition[2]
        expected = 'eps' if node_refuses else f'(({child[1]},{flags(child)}))'
        checks += [f'expression_{label} = {ast(condition)}',
            f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath (NExprTernary expression_{label} expression_selected expression_skip metadata)),(PCOCCURRENCE (pcpath ++ [PCFIELD 0]) expression_{label})] ++ $pcwalk($pcchildren(expression_{label},pcpath ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
            f'S_{label} = S_source_{label}[.POOLS = [ppool[.CONSTANTS = ([' + ','.join(constants) + '] ++ ppool.CONSTANTS)]]]',
            f'{NODE}(S_{label},{origin("pcpath",(0,)+query)}) = {expected}',
            f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ' + ('((porigin_cond,porigin_selected))' if label == 'flat_child' else 'eps'),
            f'{OLD}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ' + ('((porigin_cond,porigin_selected))' if label == 'all_int' else 'eps'),
            f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
        if label == 'all_int':
            checks += [f'$lossy_optional_integer_deferred_value_at(S_{label},pfunction.ENV,pdefault.ORIGIN) = (PINT 0)']
    return checks


def private_checks(group):
    tree = NEGATIVE[group]
    checks = BASE + ['S.CODE = [pcode]', '$default_cache_owner(S) = (CACHE_SHARED)']
    for index, unary, bits, val in [(1,'POSITIVE',NEGINF,'PBOOL false'), (2,'NEGATIVE',POSINF,f'PFLOAT {NEGZERO}')]:
        where = f'pcpath_wrapper_{index}'
        full, cond, child = origin(where,(0,)), origin(where,(0,0)), origin(where,(0,0,0))
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})', f'pdefault_{index}.ORIGIN = PORIGIN n_unit {where}',
            f'$origin_node(S.SOURCES,{cond}) = (expression_cond_{index})', f'$pfshape(expression_cond_{index}) = PFUNARY {unary} expression_child_{index}',
            f'{NODE}(S,{child}) = (({tree[1]},{flags(tree)}))', f'{NODE}(S,{cond}) = eps', f'{OLD}(S,pfunction.ENV,{full}) = eps',
            f'$pool_value(S.POOLS,{cond}) = (PFLOAT {bits})', f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,{cond})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = eps',
            f'{ROOT}(S,pfunction.ENV,{full}) = (({cond},{origin(where,(0,1))}))',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{full}) = ({val})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT 0)', f'$lossy_optional_integer_deferred(S,pfunction,{index})',
            f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT 0,CLASS PVSCALAR}}', f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})', f'S.STORE[n_private_{index}] = DEFINED (PINT 0)',
            rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
        for tail,node in walk(tree).items(): checks += [f'$pool_value(S.POOLS,{origin(where,(0,0,0)+tail)}) = ({value(node)})']
    checks += ['n_private_1 =/= n_private_2', 'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_1[.VALUE = PBOOL false])]',
        '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)', '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
        'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base313"),$ptascii("E_ERROR")),($ptascii("One313"),$ptascii("E_ERROR")),($ptascii("Skipped313"),$ptascii("Unavailable313") ++ [92] ++ $ptascii("Payload"))]]',
        '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_1.ORIGIN)',
        'S_no_names = S[.CODE = [pcode[.NAMES = eps]]]', '~$lossy_optional_integer_deferred(S_no_names,pfunction,1)',
        'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]', '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        'S_done = $drive_steps(S,3010)', r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps /\ S_done.FRAMES = eps']
    for index in (1,2): checks += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
    return checks + ['$lookup(S_done.ENV,$ptascii("x313")) = (n_global)', 'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
        r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']


CASES = {}
for group in ['pure','mixed']:
    prefix = 'deferred-unary-float-number-tree-infinite-full-ternary-redirect-wrapper-' + group
    raw_source = ROWS[prefix + '-raw-tagged-results']['source']
    CASES[group + '-unary-float-tree-independent-tags'] = {'source':raw_source, 'stage':RAW_STAGE, 'checks':raw_checks(group)}
    CASES[group + '-unary-float-tree-independent-forgeries'] = {'source':raw_source, 'stage':RAW_STAGE, 'checks':forgeries(group)}
    CASES[group + '-unary-float-tree-independent-private-lifecycle'] = {'source':ROWS[prefix + '-alias-named-reentry']['source'],
        'stage':CONTEXT + '-- if pcallcontext.ARGC = 1 -- if pfunction.ENV.NAMESPACE = $ptascii("UnaryFloatNumber' + group.capitalize() + 'TreeInfiniteRedirect313") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)', 'checks':private_checks(group)}
if __name__ == '__main__':
    protocol.run(CASES,extra_inputs=(Path(__file__),CATALOGUE),runner_flags=('--sl',))
