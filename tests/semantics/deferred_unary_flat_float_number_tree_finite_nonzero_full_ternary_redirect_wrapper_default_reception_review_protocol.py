#!/usr/bin/env python3
"""Flat typed children retain finite sign bits, phase refusals and private defaults."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import deferred_unary_float_number_tree_finite_nonzero_full_ternary_redirect_wrapper_default_reception_review_protocol as affected
import deferred_unary_flat_float_number_tree_infinite_full_ternary_redirect_wrapper_default_reception_review_protocol as previous
from deferred_unary_flat_float_number_tree_infinite_full_ternary_redirect_wrapper_default_reception_review_protocol import nodes
from deferred_unary_float_number_tree_infinite_full_ternary_redirect_wrapper_default_reception_review_protocol import (
    I, F, U, B, ast, walk, flags, value, path, origin, expression,
    POSINF, NEGZERO, ONE, TWO, NAN, ZERO_SIGN, BASE, CONTEXT, RAW_STAGE, NODE,
)

CATALOGUE = Path(__file__).with_name('deferred_unary_flat_float_number_tree_finite_nonzero_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
ROOT = '$lossy_optional_integer_unary_float_number_tree_finite_nonzero_full_redirect'
FINITE = '$lossy_optional_integer_finite_nonzero_float_full_redirect'
INFINITE = previous.ROOT
THREE = 4613937818241073152
POSITIVE = {'pure': ONE, 'mixed': TWO}
NEGATIVE_BITS = {group: bits + (1 << 63) for group,bits in POSITIVE.items()}
FLOAT_PART = B('ADD', f'NFLOAT {ONE}', F(ONE), ZERO_SIGN)
TREES = {'pure': FLOAT_PART, 'mixed': B('ADD', f'NFLOAT {TWO}', I(2), ZERO_SIGN)}
NEGATIVE = {'pure': B('ADD', f'NFLOAT {NEGATIVE_BITS["pure"]}', U('UM', NEGATIVE_BITS['pure'], F(ONE)), ZERO_SIGN),
            'mixed': B('ADD', f'NFLOAT {NEGATIVE_BITS["mixed"]}', ('UM', 'NINT $(-2)', I(2)), ZERO_SIGN)}
ZERO_PATH = {'pure': (1,), 'mixed': (1,)}


def raw_checks(group):
    tree = TREES[group]
    checks = BASE + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]', '$default_cache_owner(S) = (CACHE_SHARED)']
    for index, unary, bits, selected_value in [(0,'POSITIVE',POSITIVE[group],'PINT 0'), (1,'NEGATIVE',NEGATIVE_BITS[group],'PNULL')]:
        where = f'pcpath_{index}'
        cond, child, selected = origin(where,(0,)), origin(where,(0,0)), origin(where,(1,))
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})', f'pdefault_{index}.ORIGIN = PORIGIN n_unit {where}',
            f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (NExprTernary expression_cond_{index} expression_selected_{index} expression_skip_{index} metadata_{index})',
            f'$pfshape(expression_cond_{index}) = PFUNARY {unary} {expression(index,())}',
            f'$code_expression(pcode.EXPRESSIONS,{where}) = ((z_{index},false))',
            rf'$pool_value(S.POOLS,pdefault_{index}.ORIGIN) = eps /\ $compiled_read(S,pdefault_{index}.ORIGIN) = eps',
            f'$pool_value(S.POOLS,{cond}) = (PFLOAT {bits})',
            f'$code_expression(pcode.EXPRESSIONS,{path(where,(0,))}) = eps', f'$compiled_read(S,{cond}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where,(0,))}) = 0',
            f'$float_decode({bits}) = FINITE {index} n_numerator_{index} n_denominator_{index}', f'n_numerator_{index} =/= 0',
            f'{NODE}(S,{cond}) = eps', f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,{child})',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,{cond})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = eps',
            f'{FINITE}(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps', f'{INFINITE}(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
            f'{ROOT}(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (({cond},{selected}))',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({selected_value})',
            f'$lossy_optional_integer_deferred(S,pfunction,{index})', f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,{origin(where,(2,))})',
            f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {selected_value},CLASS PVSCALAR}}',
            f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})', f'S.STORE[n_private_{index}] = DEFINED ({selected_value})',
            rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
        checks += nodes(tree, where, (0,0), index)
        checks += [f'~($lossy_optional_integer_mixed_number_tree_binary({expression(index,(0,))}) \\/ $lossy_optional_integer_mixed_number_tree_binary({expression(index,(1,))}))',
            f'$float_decode({POSITIVE[group]}) = FINITE 0 n_child_numerator_{index} n_child_denominator_{index}', f'n_child_numerator_{index} =/= 0']
    checks += ['n_private_0 =/= n_private_1', 'S_done = $drive_steps(S,3010)',
        r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps /\ S_done.FRAMES = eps']
    for index in (0,1):
        checks += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
    return checks + ['$heap_valid($heap_graph(S_done))']


def forgeries(group):
    tree, bits = TREES[group], POSITIVE[group]
    checks = BASE + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)', 'pdefault.ORIGIN = PORIGIN n_unit pcpath',
        'porigin_cond = ' + origin('pcpath',(0,)), 'porigin_child = ' + origin('pcpath',(0,0)), 'porigin_selected = ' + origin('pcpath',(1,)),
        '$origin_node(S.SOURCES,pdefault.ORIGIN) = (NExprTernary expression_cond expression_selected expression_skip metadata)',
        'expression_cond = NExprUnaryPlus expression_child metadata_unary', '$code_expression(pcode.EXPRESSIONS,pcpath) = ((z,false))',
        f'{NODE}(S,porigin_child) = (({tree[1]},{flags(tree)}))', f'{ROOT}(S,pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))']
    mutations = {'no_redirect': 'S[.CODE = [pcode[.REDIRECTS = eps]]]',
        'duplicate': 'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
        'copy': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 1]) true)]]]]',
        'target': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 2]) false)]]]]',
        'ownpool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath (PINT 0))] ++ ppool.CONSTANTS)]]]',
        'owncode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath z true)] ++ pcode.EXPRESSIONS)]]]',
    }
    pools = [('condtag',(0,),'PINT 0'), ('condsign',(0,),f'PFLOAT {NEGATIVE_BITS[group]}'),
        ('childsign',(0,0),f'PFLOAT {NEGATIVE_BITS[group]}'), ('childtag',(0,0),'PINT ' + ('1' if group == 'pure' else '2')),
        ('zerosign',(0,0)+ZERO_PATH[group],'PFLOAT 0'), ('zerotag',(0,0)+ZERO_PATH[group]+(0,0),'PINT 0')]
    if group == 'mixed': pools += [('lefttag',(0,0,0),f'PFLOAT {TWO}')]
    for label, fields, val in pools:
        mutations[label] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath",fields)}) ({val}))] ++ ppool.CONSTANTS)]]]'
    safe_reads = set()
    for fields in [(0,), (0,0), (0,0)+ZERO_PATH[group][:-1], (0,0)+ZERO_PATH[group], (0,0)+ZERO_PATH[group]+(0,0)]:
        label = ''.join(map(str,fields))
        for flag in ['false','true']:
            key = 'code'+label+flag
            mutations[key] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path("pcpath",fields)}) z {flag})] ++ pcode.EXPRESSIONS)]]]'
            if flag == 'true' and fields in [(0,0), (0,0)+ZERO_PATH[group][:-1], (0,0)+ZERO_PATH[group]]:
                safe_reads.add(key)
        mutations['redirect'+label] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT ({path("pcpath",fields)}) (pcpath ++ [PCFIELD 1]) false)] ++ pcode.REDIRECTS)]]]'
    for label, update in mutations.items():
        checks += [f'S_{label} = {update}', f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps']
        if label in safe_reads:
            checks += [f'$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,porigin_cond)',
                f'$lossy_optional_integer_deferred_value_at(S_{label},pfunction.ENV,porigin_cond) = (PFLOAT {bits})',
                f'{FINITE}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))',
                f'$lossy_optional_integer_deferred(S_{label},pfunction,0)']
        else:
            checks += [f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
    for label in ['condtag','condsign','code0false','code0true','redirect0']:
        checks += [f'{NODE}(S_{label},porigin_child) = (({tree[1]},{flags(tree)}))']
    for label in ['zerosign','zerotag'] + (['lefttag'] if group == 'mixed' else []):
        checks += [f'$pool_value(S_{label}.POOLS,porigin_cond) = (PFLOAT {bits})',
            f'$pool_value(S_{label}.POOLS,porigin_child) = (PFLOAT {bits})', f'{NODE}(S_{label},porigin_child) = eps']
    for fields in [(0,), (0,0), (1,), (2,), (0,0)+ZERO_PATH[group]+(0,0)]:
        label = ''.join(map(str,fields))
        checks += [f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path("pcpath",fields)}) (NScalarInt (INTEGER 99) eps))] ++ pcunit.OCCURRENCES)]]]',
            f'{ROOT}(S_source_{label},pfunction.ENV,pdefault.ORIGIN) = eps', f'~$lossy_optional_integer_deferred(S_source_{label},pfunction,0)']
    safe = U('UP',ONE,B('ADD',f'NFLOAT {ONE}',F(ONE),F(0)))
    zero = B('MULTIPLY',f'NFLOAT {NEGZERO}',F(ONE),ZERO_SIGN)
    nan = B('ADD',f'NFLOAT {NAN}',F(NAN),ZERO_SIGN)
    controls = [('finite_safe',safe,False), ('literal',U('UP',ONE,F(ONE)),False),
        ('infinite',U('UP',POSINF,B('ADD',f'NFLOAT {POSINF}',F(POSINF),ZERO_SIGN)),False),
        ('flat_unsafe',U('UP',ONE,B('SUBTRACT',f'NFLOAT {ONE}',F(ONE),ZERO_SIGN)),False),
        ('zero',U('UP',NEGZERO,zero),False), ('nan',U('UP',NAN,nan),False),
        ('divzero',U('UP',bits,B('DIVIDE',f'NFLOAT {bits}',F(ONE),ZERO_SIGN)),True),
        ('second_wrapper',U('UP',bits,U('UP',bits,tree)),True),
        ('old_binary_unary_child',B('ADD',f'NFLOAT {TWO if group == "pure" else THREE}',U('UP',bits,tree),F(ONE)),True)]
    for label, condition, node_refuses in controls:
        constants = [f'(PCONSTANT ({path("pcpath",(0,)+tail)}) ({value(node)}))' for tail,node in walk(condition).items()]
        query = () if label == 'old_binary_unary_child' else (0,)
        child = condition if not query else condition[2]
        expected = 'eps' if node_refuses else f'(({child[1]},{flags(child)}))'
        checks += [f'expression_{label} = {ast(condition)}',
            f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath (NExprTernary expression_{label} expression_selected expression_skip metadata)),(PCOCCURRENCE (pcpath ++ [PCFIELD 0]) expression_{label})] ++ $pcwalk($pcchildren(expression_{label},pcpath ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
            f'S_{label} = S_source_{label}[.POOLS = [ppool[.CONSTANTS = ([' + ','.join(constants) + '] ++ ppool.CONSTANTS)]]]',
            f'{NODE}(S_{label},{origin("pcpath",(0,)+query)}) = {expected}',
            f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ' + ('((porigin_cond,porigin_selected))' if label == 'flat_unsafe' else 'eps'),
            f'{FINITE}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ' + ('((porigin_cond,porigin_selected))' if label in ['finite_safe','literal'] else 'eps'),
            f'{INFINITE}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ' + ('((porigin_cond,porigin_selected))' if label == 'infinite' else 'eps'),
            f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
        if label in ['finite_safe','literal']:
            checks += [f'$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,porigin_cond)']
        elif label in ['infinite','flat_unsafe','zero','nan']:
            checks += [f'~$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,porigin_cond)',
                f'$lossy_optional_integer_deferred_value_at(S_{label},pfunction.ENV,porigin_cond) = eps']
    return checks


def private_checks(group):
    tree = NEGATIVE[group]
    checks = BASE + ['S.CODE = [pcode]', '$default_cache_owner(S) = (CACHE_SHARED)']
    for index, unary, bits, selected_value in [(1,'POSITIVE',NEGATIVE_BITS[group],'PBOOL false'), (2,'NEGATIVE',POSITIVE[group],f'PFLOAT {NEGZERO}')]:
        where = f'pcpath_wrapper_{index}'
        full, cond, child = origin(where,(0,)), origin(where,(0,0)), origin(where,(0,0,0))
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})', f'pdefault_{index}.ORIGIN = PORIGIN n_unit {where}',
            f'$origin_node(S.SOURCES,{cond}) = (expression_cond_{index})', f'$pfshape(expression_cond_{index}) = PFUNARY {unary} expression_child_{index}',
            f'{NODE}(S,{child}) = (({tree[1]},{flags(tree)}))', f'{NODE}(S,{cond}) = eps',
            f'$pool_value(S.POOLS,{cond}) = (PFLOAT {bits})', f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,{cond})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = eps',
            f'{FINITE}(S,pfunction.ENV,{full}) = eps', f'{INFINITE}(S,pfunction.ENV,{full}) = eps',
            f'{ROOT}(S,pfunction.ENV,{full}) = (({cond},{origin(where,(0,1))}))',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{full}) = ({selected_value})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT 0)', f'$lossy_optional_integer_deferred(S,pfunction,{index})',
            f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT 0,CLASS PVSCALAR}}', f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})', f'S.STORE[n_private_{index}] = DEFINED (PINT 0)',
            rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
        checks += nodes(tree, where, (0,0,0), f'private{index}')
    checks += ['n_private_1 =/= n_private_2', 'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_1[.VALUE = PBOOL false])]',
        '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)', '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
        'S_wrong_target = S[.CURRENT = (pcallcontext[.TARGET = pdefault_1.ORIGIN])]',
        f'{ROOT}(S_wrong_target,pfunction.ENV,{origin("pcpath_wrapper_1",(0,))}) = (({origin("pcpath_wrapper_1",(0,0))},{origin("pcpath_wrapper_1",(0,1))}))',
        '~$lossy_optional_integer_deferred(S_wrong_target,pfunction,1)',
        'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base316"),$ptascii("E_ERROR")),($ptascii("One316"),$ptascii("E_ERROR")),($ptascii("Skipped316"),$ptascii("Unavailable316") ++ [92] ++ $ptascii("Payload"))]]',
        '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_1.ORIGIN)',
        'S_no_names = S[.CODE = [pcode[.NAMES = eps]]]', '~$lossy_optional_integer_deferred(S_no_names,pfunction,1)',
        'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]', '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        'S_done = $drive_steps(S,3010)', r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps /\ S_done.FRAMES = eps']
    for index in (1,2):
        checks += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
    return checks + ['$lookup(S_done.ENV,$ptascii("x316")) = (n_global)', 'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
        r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']


CASES = {}
for group in ['pure','mixed']:
    prefix = 'deferred-unary-flat-float-number-tree-finite-nonzero-full-ternary-redirect-wrapper-' + group
    raw_source = ROWS[prefix + '-raw-tagged-results']['source']
    CASES[group + '-unary-flat-finite-independent-tags'] = {'source':raw_source, 'stage':RAW_STAGE, 'checks':raw_checks(group)}
    CASES[group + '-unary-flat-finite-independent-certificates'] = {'source':raw_source, 'stage':RAW_STAGE, 'checks':forgeries(group)}
    CASES[group + '-unary-flat-finite-independent-private-lifecycle'] = {'source':ROWS[prefix + '-alias-named-reentry']['source'],
        'stage':CONTEXT + '-- if pcallcontext.ARGC = 1 -- if pfunction.ENV.NAMESPACE = $ptascii("UnaryFlatFloatNumber' + group.capitalize() + 'TreeFiniteRedirect316") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)', 'checks':private_checks(group)}
    old_checks = affected.forgeries(group)
    prefix_end = next(i for i, check in enumerate(old_checks) if check.startswith('S_no_redirect = '))
    start = next(i for i, check in enumerate(old_checks) if check.startswith('expression_flat_unsafe = '))
    end = next(i for i, check in enumerate(old_checks) if check.startswith('expression_zero = '))
    CASES[group + '-accepted315-flat-unsafe-query'] = {
        'source': affected.ROWS['deferred-unary-float-number-tree-finite-nonzero-full-ternary-redirect-wrapper-' + group + '-raw-tagged-results']['source'],
        'stage': RAW_STAGE, 'checks': old_checks[:prefix_end] + old_checks[start:end]}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE, Path(affected.__file__), affected.CATALOGUE, Path(previous.__file__), previous.CATALOGUE,
        Path(previous.previous.__file__), previous.previous.CATALOGUE), runner_flags=('--sl',))
