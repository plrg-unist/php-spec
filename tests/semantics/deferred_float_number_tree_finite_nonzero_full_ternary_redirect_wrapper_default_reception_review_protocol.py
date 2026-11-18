#!/usr/bin/env python3
"""Direct finite folded predicates retain typed sources, phase bounds and recipients."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import deferred_unary_flat_float_number_tree_finite_nonzero_full_ternary_redirect_wrapper_default_reception_review_protocol as prior
from deferred_unary_flat_float_number_tree_finite_nonzero_full_ternary_redirect_wrapper_default_reception_review_protocol import (
    I, F, U, B, ast, walk, flags, value, path, origin, expression, nodes,
    POSINF, NEGZERO, ONE, TWO, NAN, ZERO_SIGN, BASE, CONTEXT, RAW_STAGE, NODE,
)

CATALOGUE = Path(__file__).with_name('deferred_float_number_tree_finite_nonzero_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
ROOT = '$lossy_optional_integer_float_number_tree_finite_nonzero_full_redirect'
FINITE, UNARY = prior.FINITE, prior.ROOT
TREES, NEGATIVE = prior.TREES, prior.NEGATIVE
BITS, NEGATIVE_BITS = prior.POSITIVE, prior.NEGATIVE_BITS


def receipts(group, entries, wrapped):
    checks = BASE + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]', '$default_cache_owner(S) = (CACHE_SHARED)']
    for index, negative, selected_value in entries:
        tree = NEGATIVE[group] if negative else TREES[group]
        bits = NEGATIVE_BITS[group] if negative else BITS[group]
        where = f'pcpath_{index}'
        tail = (0,) if wrapped else ()
        full, cond, selected, skipped = [origin(where, tail + fields) for fields in [(), (0,), (1,), (2,)]]
        received = 'PINT 0' if wrapped else selected_value
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})', f'pdefault_{index}.ORIGIN = PORIGIN n_unit {where}',
            f'$origin_node(S.SOURCES,{full}) = (NExprTernary {expression(index,())} expression_selected_{index} expression_skip_{index} metadata_{index})',
            f'$code_expression(pcode.EXPRESSIONS,{path(where,tail)}) = ((z_{index},false))',
            rf'$pool_value(S.POOLS,{full}) = eps /\ $compiled_read(S,{full}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where,tail)}) = 1',
            f'$compiled_redirect(S,{full}) = (({selected},expression_selected_{index},false,z_{index}))',
            f'$float_decode({bits}) = FINITE {int(negative)} n_numerator_{index} n_denominator_{index}', f'n_numerator_{index} =/= 0',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,{cond})',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,{origin(where,tail+(0,1))})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = eps',
            f'{FINITE}(S,pfunction.ENV,{full}) = eps', f'{UNARY}(S,pfunction.ENV,{full}) = eps',
            f'{ROOT}(S,pfunction.ENV,{full}) = (({cond},{selected}))',
            f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,{full}) = (({cond},{selected}))',
            f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,{skipped})',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,{full})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{full}) = ({selected_value})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({received})',
            f'$lossy_optional_integer_deferred(S,pfunction,{index})',
            f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {received},CLASS PVSCALAR}}',
            f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
            f'S.STORE[n_private_{index}] = DEFINED ({received})',
            rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
        checks += nodes(tree, where, tail+(0,), index)
    return checks


def finish(entries, named):
    checks = []
    indexes = [index for index, _, _ in entries]
    for index in indexes:
        checks += [f'S_cache_{index} = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{index}[.VALUE = PBOOL false])]',
            f'$default_caches_valid(S_cache_{index},S_cache_{index}.DEFAULTCACHE)', f'~$lossy_optional_integer_deferred(S_cache_{index},pfunction,{index})']
    first = indexes[0]
    checks += [f'n_private_{indexes[0]} =/= n_private_{indexes[1]}',
        f'S_target = S[.CURRENT = (pcallcontext[.TARGET = pdefault_{first}.ORIGIN])]',
        f'~$lossy_optional_integer_deferred(S_target,pfunction,{first})',
        'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]', '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        'S_done = $drive_steps(S,3010)', r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps /\ S_done.FRAMES = eps']
    for index in indexes:
        checks += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
    if named:
        checks += ['S_no_names = S[.CODE = [pcode[.NAMES = eps]]]', f'~$lossy_optional_integer_deferred(S_no_names,pfunction,{first})',
            '$lookup(S_done.ENV,$ptascii("x317")) = (n_global)', 'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)']
    return checks + ['$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)', '$default_caches_valid(S_done,S_done.DEFAULTCACHE)']


def certificates(group):
    bits, tree = BITS[group], TREES[group]
    checks = receipts(group, [(0,False,'PINT 0')], False) + ['pcpath = pcpath_0', 'pdefault = pdefault_0',
        'porigin_cond = ' + origin('pcpath',(0,)), 'porigin_selected = ' + origin('pcpath',(1,)),
        '$origin_node(S.SOURCES,pdefault.ORIGIN) = (NExprTernary expression_cond expression_selected expression_skip metadata)']
    mutations = {'missing':'S[.CODE = [pcode[.REDIRECTS = eps]]]',
        'duplicate':'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
        'copy':'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 1]) true)]]]]',
        'target':'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 2]) false)]]]]',
        'owncode':'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath z_0 true)] ++ pcode.EXPRESSIONS)]]]',
        'ownpool':'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath (PINT 0))] ++ ppool.CONSTANTS)]]]',
        'condsign':f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath ++ [PCFIELD 0]) (PFLOAT {NEGATIVE_BITS[group]}))] ++ ppool.CONSTANTS)]]]',
        'lefttag':f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath ++ [PCFIELD 0,PCFIELD 0]) ({"PFLOAT " + str(TWO) if group == "mixed" else "PINT 1"}))] ++ ppool.CONSTANTS)]]]',
        'zerosign':f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath ++ [PCFIELD 0,PCFIELD 1]) (PFLOAT 0))] ++ ppool.CONSTANTS)]]]',
        'zerotag':'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath ++ [PCFIELD 0,PCFIELD 1,PCFIELD 0,PCFIELD 0]) (PINT 0))] ++ ppool.CONSTANTS)]]]'}
    for fields in [(0,), (0,0), (0,1), (0,1,0), (0,1,0,0)]:
        label = ''.join(map(str,fields))
        for flag in ['false','true']:
            mutations['code'+label+flag] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path("pcpath",fields)}) z_0 {flag})] ++ pcode.EXPRESSIONS)]]]'
        mutations['redirect'+label] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT ({path("pcpath",fields)}) (pcpath ++ [PCFIELD 1]) false)] ++ pcode.REDIRECTS)]]]'
    for label, update in mutations.items():
        checks += [f'S_{label} = {update}', f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps']
        if label in ['code0true','code01true']:
            checks += [f'$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,porigin_cond)',
                f'$lossy_optional_integer_deferred_value_at(S_{label},pfunction.ENV,porigin_cond) = (PFLOAT {bits})',
                f'{FINITE}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ' + ('eps' if label=='code0true' else '((porigin_cond,porigin_selected))')]
        if label=='code01true':
            checks += [f'$lossy_optional_integer_deferred(S_{label},pfunction,0)']
        else:
            checks += [f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
        if label=='code0true':
            checks += [f'$lossy_optional_integer_pruned_ternary(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
                f'~$lossy_optional_integer_deferred_bindings(S_{label},pfunction.ENV,pdefault.ORIGIN)']
    for fields in [(0,), (0,0), (0,1), (1,), (2,)]:
        label = ''.join(map(str,fields))
        checks += [f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path("pcpath",fields)}) (NScalarInt (INTEGER 99) eps))] ++ pcunit.OCCURRENCES)]]]',
            f'{ROOT}(S_source_{label},pfunction.ENV,pdefault.ORIGIN) = eps', f'~$lossy_optional_integer_deferred(S_source_{label},pfunction,0)']
    proper = B('ADD',f'NFLOAT {TWO}',TREES['pure'],F(ONE))
    controls = [('safe',B('ADD',f'NFLOAT {ONE}',F(ONE),F(0)),True,False,False),
        ('literal',F(ONE),True,False,False), ('flat',B('SUBTRACT',f'NFLOAT {ONE}',F(ONE),ZERO_SIGN),False,True,False),
        ('proper',proper,False,True,False), ('infinite',B('ADD',f'NFLOAT {POSINF}',F(POSINF),ZERO_SIGN),False,False,False),
        ('zero',B('MULTIPLY',f'NFLOAT {NEGZERO}',F(ONE),ZERO_SIGN),False,False,False),
        ('nan',B('ADD',f'NFLOAT {NAN}',F(NAN),ZERO_SIGN),False,False,False),
        ('divzero',B('DIVIDE',f'NFLOAT {bits}',F(ONE),ZERO_SIGN),False,False,True),
        ('unary',U('UP',bits,tree),False,False,True),
        ('nested_unary',B('ADD',f'NFLOAT {TWO if group=="pure" else prior.THREE}',U('UP',bits,tree),F(ONE)),False,False,True)]
    for label, condition, safe, accepted, refuses in controls:
        constants = [f'(PCONSTANT ({path("pcpath",(0,)+tail)}) ({value(node)}))' for tail,node in walk(condition).items()]
        checks += [f'expression_{label} = {ast(condition)}',
            f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath (NExprTernary expression_{label} expression_selected expression_skip metadata)),(PCOCCURRENCE (pcpath ++ [PCFIELD 0]) expression_{label})] ++ $pcwalk($pcchildren(expression_{label},pcpath ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
            f'S_{label} = S_source_{label}[.POOLS = [ppool[.CONSTANTS = ([' + ','.join(constants) + '] ++ ppool.CONSTANTS)]]]',
            f'{NODE}(S_{label},porigin_cond) = ' + ('eps' if refuses else f'(({condition[1]},{flags(condition)}))'),
            f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ' + ('((porigin_cond,porigin_selected))' if accepted else 'eps'),
            f'{FINITE}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ' + ('((porigin_cond,porigin_selected))' if safe else 'eps'),
            f'{UNARY}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ' + ('((porigin_cond,porigin_selected))' if label=='unary' else 'eps'),
            f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
        if safe:
            checks += [f'$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,porigin_cond)']
    return checks


CASES = {}
for group in ['pure','mixed']:
    prefix = 'deferred-float-number-tree-finite-nonzero-full-ternary-redirect-wrapper-' + group
    raw = ROWS[prefix+'-raw-tagged-results']['source']
    raw_entries = [(0,False,'PINT 0'),(1,True,'PNULL')]
    named_entries = [(1,True,'PBOOL false'),(2,False,f'PFLOAT {NEGZERO}')]
    CASES[group+'-direct-finite-independent-tags'] = {'source':raw, 'stage':RAW_STAGE, 'checks':receipts(group,raw_entries,False)+finish(raw_entries,False)}
    CASES[group+'-direct-finite-independent-certificates'] = {'source':raw, 'stage':RAW_STAGE, 'checks':certificates(group)}
    CASES[group+'-direct-finite-independent-private'] = {'source':ROWS[prefix+'-alias-named-reentry']['source'],
        'stage':CONTEXT+'-- if pcallcontext.ARGC = 1 -- if pfunction.ENV.NAMESPACE = $ptascii("FloatNumber'+group.title()+'TreeFiniteRedirect317") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks':receipts(group,named_entries,True)+finish(named_entries,True)}
for group in ['pure','mixed']:
    old_checks = prior.forgeries(group)
    prefix_end = next(i for i,c in enumerate(old_checks) if c.startswith('S_no_redirect = '))
    start = next(i for i,c in enumerate(old_checks) if c.startswith('expression_old_binary_unary_child = '))
    CASES[group+'-affected316-computed-unary'] = {
        'source':prior.ROWS['deferred-unary-flat-float-number-tree-finite-nonzero-full-ternary-redirect-wrapper-'+group+'-raw-tagged-results']['source'],
        'stage':RAW_STAGE, 'checks':old_checks[:prefix_end]+old_checks[start:]+[
            ROOT+'(S_old_binary_unary_child,pfunction.ENV,pdefault.ORIGIN) = eps']}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE, Path(prior.__file__), prior.CATALOGUE,
        Path(prior.affected.__file__), prior.affected.CATALOGUE, Path(prior.previous.__file__), prior.previous.CATALOGUE,
        Path(prior.previous.previous.__file__), prior.previous.previous.CATALOGUE), runner_flags=('--sl',))
