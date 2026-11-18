#!/usr/bin/env python3
"""One sign over flat division preserves source, numeric kinds and recipients."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import deferred_unary_float_number_tree_infinite_full_ternary_redirect_wrapper_default_reception_review_protocol as previous
from deferred_unary_float_number_tree_infinite_full_ternary_redirect_wrapper_default_reception_review_protocol import (
    I, F, U, B, ast, walk, kinds, flags, value, path, origin, expression,
    POSINF, NEGINF, NEGZERO, ONE, NAN, ROOT, OLD, NODE, ALL_INT, BASE, CONTEXT, RAW_STAGE,
)

CATALOGUE = Path(__file__).with_name('deferred_unary_flat_float_number_tree_infinite_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
TREES = {'pure': B('DIVIDE', f'NFLOAT {POSINF}', F(ONE), F(1)),
         'mixed': B('DIVIDE', f'NFLOAT {POSINF}', I(1), F(1))}
NEGATIVE = {'pure': B('DIVIDE', f'NFLOAT {NEGINF}', U('UM', 13830554455654793216, F(ONE)), F(1)),
            'mixed': B('DIVIDE', f'NFLOAT {NEGINF}', ('UM', 'NINT $(-1)', I(1)), F(1))}


def nodes(tree, where, tail, label):
    checks = []
    for fields, node in walk(tree).items():
        at, expr = origin(where, tail + fields), expression(label, fields)
        checks += [f'$origin_node(S.SOURCES,{at}) = ({expr})']
        if node[0] == 'I':
            checks += [f'{expr} = NScalarInt (INTEGER {node[1][5:]}) metadata_{label}_{len(checks)}']
        elif node[0] == 'F':
            checks += [f'{expr} = NScalarFloat (FLOAT "{int(node[1][7:]):016x}") metadata_{label}_{len(checks)}']
        elif node[0] in ['UP', 'UM']:
            checks += [f'$pfshape({expr}) = PFUNARY {"POSITIVE" if node[0] == "UP" else "NEGATIVE"} {expression(label,fields+(0,))}']
        else:
            checks += [f'$pfshape({expr}) = PFBINARY {node[0]} {expression(label,fields+(0,))} {expression(label,fields+(1,))}']
        checks += [f'$pool_value(S.POOLS,{at}) = ({value(node)})',
            f'$code_expression(pcode.EXPRESSIONS,{path(where,tail+fields)}) = eps',
            f'$compiled_read(S,{at}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where,tail+fields)}) = 0',
            f'{NODE}(S,{at}) = (({node[1]},{flags(node)}))']
        if not kinds(node)[0]:
            checks += [f'$lossy_optional_integer_float_tree_value(S,{at}) = ({node[1][7:]})']
    return checks


def raw_checks(group):
    tree = TREES[group]
    checks = BASE + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]', '$default_cache_owner(S) = (CACHE_SHARED)',
        f'$float_decode(1) = FINITE 0 1 {1 << 1074}', '~$num_zero(NFLOAT 1)',
        f'$number_binary(DIVIDE,{tree[2][1]},NFLOAT 1) = NUM (NFLOAT {POSINF})']
    for index, unary, bits, selected_value in [(0, 'POSITIVE', POSINF, 'PINT 0'), (1, 'NEGATIVE', NEGINF, 'PNULL')]:
        where = f'pcpath_{index}'
        cond, child, selected = origin(where,(0,)), origin(where,(0,0)), origin(where,(1,))
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'pdefault_{index}.ORIGIN = PORIGIN n_unit {where}',
            f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (NExprTernary expression_cond_{index} expression_selected_{index} expression_skip_{index} metadata_{index})',
            f'$pfshape(expression_cond_{index}) = PFUNARY {unary} {expression(index,())}',
            f'$code_expression(pcode.EXPRESSIONS,{where}) = ((z_{index},false))',
            rf'$pool_value(S.POOLS,pdefault_{index}.ORIGIN) = eps /\ $compiled_read(S,pdefault_{index}.ORIGIN) = eps',
            f'$pool_value(S.POOLS,{cond}) = (PFLOAT {bits})',
            f'$code_expression(pcode.EXPRESSIONS,{path(where,(0,))}) = eps', f'$compiled_read(S,{cond}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where,(0,))}) = 0',
            f'{NODE}(S,{cond}) = eps', f'$lossy_optional_integer_phase_safe(S,pfunction.ENV,{child})',
            f'$lossy_optional_integer_phase_safe(S,pfunction.ENV,{cond})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = (PFLOAT {bits})',
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
        checks += nodes(tree, where, (0,0), index)
        for fields in [(0,), (1,)]:
            checks += [f'~$lossy_optional_integer_mixed_number_tree_binary({expression(index,fields)})']
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
    mutations = {'no_redirect': 'S[.CODE = [pcode[.REDIRECTS = eps]]]',
        'duplicate': 'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
        'copy': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 1]) true)]]]]',
        'target': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 2]) false)]]]]',
        'ownpool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath (PINT 0))] ++ ppool.CONSTANTS)]]]',
        'owncode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath z true)] ++ pcode.EXPRESSIONS)]]]',
    }
    pools = [('condtag',(0,),'PINT 0'), ('condsign',(0,),f'PFLOAT {NEGINF}'),
        ('childsign',(0,0),f'PFLOAT {NEGINF}'), ('childtag',(0,0),'PINT 1'),
        ('tiny_zero',(0,0,1),'PFLOAT 0'), ('tiny_other',(0,0,1),'PFLOAT 2'),
        ('tiny_tag',(0,0,1),'PINT 0'), ('left_tag',(0,0,0),'PINT 1' if group == 'pure' else f'PFLOAT {ONE}')]
    for label, fields, val in pools:
        mutations[label] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath",fields)}) ({val}))] ++ ppool.CONSTANTS)]]]'
    for fields in [(0,), (0,0), (0,0,0), (0,0,1)]:
        label = ''.join(map(str,fields))
        for flag in ['false','true']:
            mutations['code'+label+flag] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path("pcpath",fields)}) z {flag})] ++ pcode.EXPRESSIONS)]]]'
        mutations['redirect'+label] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT ({path("pcpath",fields)}) (pcpath ++ [PCFIELD 1]) false)] ++ pcode.REDIRECTS)]]]'
    for label, update in mutations.items():
        checks += [f'S_{label} = {update}', f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
            f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
    for label in ['condtag','condsign','code0false','code0true','redirect0']:
        checks += [f'{NODE}(S_{label},porigin_child) = (({tree[1]},{flags(tree)}))']
    for label in ['tiny_zero','tiny_other','tiny_tag','left_tag']:
        checks += [f'$pool_value(S_{label}.POOLS,porigin_cond) = (PFLOAT {POSINF})',
            f'$pool_value(S_{label}.POOLS,porigin_child) = (PFLOAT {POSINF})', f'{NODE}(S_{label},porigin_child) = eps']
    for fields in [(0,), (0,0), (0,0,0), (0,0,1), (1,), (2,)]:
        label = ''.join(map(str,fields))
        checks += [f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path("pcpath",fields)}) (NScalarInt (INTEGER 99) eps))] ++ pcunit.OCCURRENCES)]]]',
            f'{ROOT}(S_source_{label},pfunction.ENV,pdefault.ORIGIN) = eps', f'~$lossy_optional_integer_deferred(S_source_{label},pfunction,0)']
    controls = [('finite', U('UP',ONE,B('DIVIDE',f'NFLOAT {ONE}',F(ONE),F(ONE))), False),
        ('literal', U('UP',POSINF,F(POSINF)), False), ('all_int', U('UP',POSINF,ALL_INT), False),
        ('nan', U('UP',NAN,B('SUBTRACT',f'NFLOAT {NAN}',F(POSINF),F(POSINF))), False),
        ('divzero', U('UP',POSINF,B('DIVIDE',f'NFLOAT {POSINF}',tree[2],F(0))), True),
        ('second_wrapper', U('UP',POSINF,U('UP',POSINF,tree)), True),
        ('old_binary_unary_child', B('ADD',f'NFLOAT {POSINF}',U('UP',POSINF,tree),F(ONE)), True)]
    for label, condition, node_refuses in controls:
        constants = [f'(PCONSTANT ({path("pcpath",(0,)+tail)}) ({value(node)}))' for tail,node in walk(condition).items()]
        query = () if label == 'old_binary_unary_child' else (0,)
        child = condition if not query else condition[2]
        expected = 'eps' if node_refuses else f'(({child[1]},{flags(child)}))'
        checks += [f'expression_{label} = {ast(condition)}',
            f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath (NExprTernary expression_{label} expression_selected expression_skip metadata)),(PCOCCURRENCE (pcpath ++ [PCFIELD 0]) expression_{label})] ++ $pcwalk($pcchildren(expression_{label},pcpath ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
            f'S_{label} = S_source_{label}[.POOLS = [ppool[.CONSTANTS = ([' + ','.join(constants) + '] ++ ppool.CONSTANTS)]]]',
            f'{NODE}(S_{label},{origin("pcpath",(0,)+query)}) = {expected}',
            f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
            f'{OLD}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ' + ('((porigin_cond,porigin_selected))' if label == 'all_int' else 'eps'),
            f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
    return checks


def private_checks(group):
    tree = NEGATIVE[group]
    checks = BASE + ['S.CODE = [pcode]', '$default_cache_owner(S) = (CACHE_SHARED)',
        f'$number_binary(DIVIDE,{tree[2][1]},NFLOAT 1) = NUM (NFLOAT {NEGINF})']
    for index, unary, bits, selected_value in [(1,'POSITIVE',NEGINF,'PBOOL false'), (2,'NEGATIVE',POSINF,f'PFLOAT {NEGZERO}')]:
        where = f'pcpath_wrapper_{index}'
        full, cond, child = origin(where,(0,)), origin(where,(0,0)), origin(where,(0,0,0))
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})', f'pdefault_{index}.ORIGIN = PORIGIN n_unit {where}',
            f'$origin_node(S.SOURCES,{cond}) = (expression_cond_{index})', f'$pfshape(expression_cond_{index}) = PFUNARY {unary} expression_child_{index}',
            f'{NODE}(S,{child}) = (({tree[1]},{flags(tree)}))', f'{NODE}(S,{cond}) = eps', f'{OLD}(S,pfunction.ENV,{full}) = eps',
            f'$pool_value(S.POOLS,{cond}) = (PFLOAT {bits})', f'$lossy_optional_integer_phase_safe(S,pfunction.ENV,{cond})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = (PFLOAT {bits})',
            f'{ROOT}(S,pfunction.ENV,{full}) = (({cond},{origin(where,(0,1))}))',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{full}) = ({selected_value})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT 0)', f'$lossy_optional_integer_deferred(S,pfunction,{index})',
            f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT 0,CLASS PVSCALAR}}', f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})', f'S.STORE[n_private_{index}] = DEFINED (PINT 0)',
            rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
        checks += nodes(tree, where, (0,0,0), f'private{index}')
        for fields in [(0,), (1,)]:
            checks += [f'~$lossy_optional_integer_mixed_number_tree_binary({expression(f"private{index}",fields)})']
    checks += ['n_private_1 =/= n_private_2', 'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_1[.VALUE = PBOOL false])]',
        '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)', '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
        'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base314"),$ptascii("E_ERROR")),($ptascii("One314"),$ptascii("E_ERROR")),($ptascii("Skipped314"),$ptascii("Unavailable314") ++ [92] ++ $ptascii("Payload"))]]',
        '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_1.ORIGIN)',
        'S_no_names = S[.CODE = [pcode[.NAMES = eps]]]', '~$lossy_optional_integer_deferred(S_no_names,pfunction,1)',
        'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]', '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        'S_done = $drive_steps(S,3010)', r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps /\ S_done.FRAMES = eps']
    for index in (1,2):
        checks += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
    return checks + ['$lookup(S_done.ENV,$ptascii("x314")) = (n_global)', 'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
        r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']


CASES = {}
for group in ['pure','mixed']:
    prefix = 'deferred-unary-flat-float-number-tree-infinite-full-ternary-redirect-wrapper-' + group
    raw_source = ROWS[prefix + '-raw-tagged-results']['source']
    CASES[group + '-unary-flat-float-independent-tags'] = {'source':raw_source, 'stage':RAW_STAGE, 'checks':raw_checks(group)}
    CASES[group + '-unary-flat-float-independent-forgeries'] = {'source':raw_source, 'stage':RAW_STAGE, 'checks':forgeries(group)}
    CASES[group + '-unary-flat-float-independent-private-lifecycle'] = {'source':ROWS[prefix + '-alias-named-reentry']['source'],
        'stage':CONTEXT + '-- if pcallcontext.ARGC = 1 -- if pfunction.ENV.NAMESPACE = $ptascii("UnaryFlatFloatNumber' + group.capitalize() + 'TreeInfiniteRedirect314") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)', 'checks':private_checks(group)}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE, Path(previous.__file__), previous.CATALOGUE), runner_flags=('--sl',))
