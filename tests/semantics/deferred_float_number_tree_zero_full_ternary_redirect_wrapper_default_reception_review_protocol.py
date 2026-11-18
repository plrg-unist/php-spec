#!/usr/bin/env python3
"""Signed-zero FIELD2 receipts preserve phase, typed trees and private defaults."""
import hashlib
import json
from pathlib import Path
import sys

import closure_call_protocol as protocol
import deferred_repeated_unary_float_number_tree_finite_nonzero_full_ternary_redirect_wrapper_default_reception_review_protocol as affected
from deferred_unary_flat_float_number_tree_infinite_full_ternary_redirect_wrapper_default_reception_review_protocol import nodes
from deferred_unary_float_number_tree_infinite_full_ternary_redirect_wrapper_default_reception_review_protocol import (
    I, F, U, B, ast, walk, flags, value, path, origin, expression,
    POSINF, NEGZERO, ONE, TWO, NAN, MAX, ZERO_SIGN, BASE, CONTEXT, RAW_STAGE, NODE,
)

CATALOGUE = Path(__file__).with_name('deferred_float_number_tree_zero_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
ROOT = '$lossy_optional_integer_float_number_tree_zero_full_redirect'
FALSEY = '$lossy_optional_integer_falsey_full_redirect'
NEGONE = 13830554455654793216
NEGATIVE_ONE = {'pure': U('UM', NEGONE, F(ONE)), 'mixed': ('UM', 'NINT $(-1)', I(1))}
TREES = {group: [B('MULTIPLY', f'NFLOAT {NEGZERO}', F(ONE) if group == 'pure' else I(1), ZERO_SIGN),
                B('MULTIPLY', 'NFLOAT 0', NEGATIVE_ONE[group], ZERO_SIGN)] for group in ['pure', 'mixed']}


def receipts(group, entries, wrapped):
    checks = BASE + ['S.CODE = [pcode]', 'n_unit = pcode.UNIT', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
        '$default_cache_owner(S) = (CACHE_SHARED)']
    for index, positive, selected_value in entries:
        tree = TREES[group][positive]
        bits = int(tree[1][7:])
        where, tail = f'pcpath_{index}', (0,) if wrapped else ()
        full, cond, skipped, selected = [origin(where, tail + fields) for fields in [(), (0,), (1,), (2,)]]
        received = 'PINT 0' if wrapped else selected_value
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'pdefault_{index}.ORIGIN = PORIGIN n_unit {where}',
            f'$origin_node(S.SOURCES,{full}) = (NExprTernary {expression(index,())} expression_skip_{index} expression_selected_{index} metadata_{index})',
            f'$origin_node(S.SOURCES,{skipped}) = (expression_skip_{index})',
            f'$origin_node(S.SOURCES,{selected}) = (expression_selected_{index})',
            f'$code_expression(pcode.EXPRESSIONS,{path(where,tail)}) = ((z_{index},false))',
            rf'$pool_value(S.POOLS,{full}) = eps /\ $compiled_read(S,{full}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where,tail)}) = 1',
            f'$compiled_redirect(S,{full}) = (({selected},expression_selected_{index},false,z_{index}))',
            f'$float_decode({bits}) = FINITE {bits >> 63} 0 n_denominator_{index}',
            f'$lossy_optional_integer_condition(pfunction.ENV,{expression(index,())}) = (false)',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,{cond})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = eps',
            f'{FALSEY}(S,pfunction.ENV,{full}) = eps',
            f'{ROOT}(S,pfunction.ENV,{full}) = (({cond},{selected}))',
            f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,{full}) = (({cond},{selected}))',
            f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,{skipped})',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,{selected})',
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
            f'$default_caches_valid(S_cache_{index},S_cache_{index}.DEFAULTCACHE)',
            f'~$lossy_optional_integer_deferred(S_cache_{index},pfunction,{index})']
    first = indexes[0]
    checks += [f'n_private_{indexes[0]} =/= n_private_{indexes[1]}',
        f'S_target = S[.CURRENT = (pcallcontext[.TARGET = pdefault_{first}.ORIGIN])]',
        f'~$lossy_optional_integer_deferred(S_target,pfunction,{first})',
        'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        'S_done = $drive_steps(S,3010)',
        r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps /\ S_done.FRAMES = eps']
    for index in indexes:
        checks += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
    if named:
        checks += ['S_no_names = S[.CODE = [pcode[.NAMES = eps]]]',
            f'~$lossy_optional_integer_deferred(S_no_names,pfunction,{first})',
            'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base319"),$ptascii("E_ERROR")),($ptascii("One319"),$ptascii("E_ERROR"))]]',
            f'~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_{first}.ORIGIN)',
            '$lookup(S_done.ENV,$ptascii("x319")) = (n_global)',
            'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)']
    return checks + ['$heap_valid($heap_graph(S_done))', '$call_descriptors_valid(S_done)', '$default_caches_valid(S_done,S_done.DEFAULTCACHE)']


def install(label, tree):
    constants = [f'(PCONSTANT ({path("pcpath",(0,)+tail)}) ({value(node)}))' for tail,node in walk(tree).items()]
    return [f'expression_{label} = {ast(tree)}',
        f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath (NExprTernary expression_{label} expression_skip expression_selected metadata)),(PCOCCURRENCE (pcpath ++ [PCFIELD 0]) expression_{label})] ++ $pcwalk($pcchildren(expression_{label},pcpath ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
        f'S_{label} = S_source_{label}[.POOLS = [ppool[.CONSTANTS = ([' + ','.join(constants) + '] ++ ppool.CONSTANTS)]]]']


def certificates(group):
    tree = TREES[group][0]
    checks = receipts(group, [(0,0,'PINT 0')], False) + [
        'pcpath = pcpath_0', 'pdefault = pdefault_0', 'porigin_cond = '+origin('pcpath',(0,)),
        'porigin_selected = '+origin('pcpath',(2,)),
        '$origin_node(S.SOURCES,pdefault.ORIGIN) = (NExprTernary expression_cond expression_skip expression_selected metadata)']
    mutations = {'missing':'S[.CODE = [pcode[.REDIRECTS = eps]]]',
        'duplicate':'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
        'copy':'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 2]) true)]]]]',
        'target':'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 1]) false)]]]]',
        'owncode':'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath z_0 true)] ++ pcode.EXPRESSIONS)]]]',
        'ownpool':'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath (PINT 0))] ++ ppool.CONSTANTS)]]]',
        'condsign':'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath ++ [PCFIELD 0]) (PFLOAT 0))] ++ ppool.CONSTANTS)]]]'}
    safe_reads = set()
    for tail,node in walk(tree).items():
        fields = (0,)+tail
        label = ''.join(map(str,fields))
        mutations['pool'+label] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath",fields)}) (PINT 7))] ++ ppool.CONSTANTS)]]]'
        for flag in ['false','true']:
            key = 'code'+label+flag
            mutations[key] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path("pcpath",fields)}) z_0 {flag})] ++ pcode.EXPRESSIONS)]]]'
            if flag == 'true' and tail == (1,): safe_reads.add(key)
        mutations['redirect'+label] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT ({path("pcpath",fields)}) (pcpath ++ [PCFIELD 2]) false)] ++ pcode.REDIRECTS)]]]'
    for label,update in mutations.items():
        checks += [f'S_{label} = {update}', f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps']
        if label in safe_reads or label == 'code0true':
            checks += [f'$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,porigin_cond)',
                f'$lossy_optional_integer_deferred_value_at(S_{label},pfunction.ENV,porigin_cond) = (PFLOAT {NEGZERO})',
                f'{FALSEY}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ' + ('((porigin_cond,porigin_selected))' if label in safe_reads else 'eps')]
        checks += [f'{"" if label in safe_reads else "~"}$lossy_optional_integer_deferred(S_{label},pfunction,0)']
    for fields in [(0,)+tail for tail in walk(tree)] + [(),(1,),(2,)]:
        label = ''.join(map(str,fields)) or 'root'
        checks += [f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path("pcpath",fields)}) (NScalarInt (INTEGER 99) eps))] ++ pcunit.OCCURRENCES)]]]',
            f'{ROOT}(S_source_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
            f'~$lossy_optional_integer_deferred(S_source_{label},pfunction,0)']
    raw_zero, raw_one = (F(0),F(ONE)) if group == 'pure' else (I(0),I(1))
    promoted = B('ADD','NFLOAT 4890909195324358656',I(MAX),I(1))
    controls = [('addzero',B('ADD','NFLOAT 0',ZERO_SIGN,raw_zero),False,True,False),
        ('subzero',B('SUBTRACT',f'NFLOAT {NEGZERO}',ZERO_SIGN,raw_zero),False,True,False),
        ('mulzero',tree,False,True,False),
        ('divzeroresult',B('DIVIDE',f'NFLOAT {NEGZERO}',ZERO_SIGN,raw_one),False,True,False),
        ('divpositivezero',B('DIVIDE','NFLOAT 0',ZERO_SIGN,NEGATIVE_ONE[group]),False,True,False),
        ('safezero',B('MULTIPLY','NFLOAT 0',raw_one,F(0)),True,False,False),
        ('nonzero',B('ADD',f'NFLOAT {ONE}',raw_one,ZERO_SIGN),False,False,False),
        ('infinite',B('ADD',f'NFLOAT {POSINF}',F(POSINF),ZERO_SIGN),False,False,False),
        ('nan',B('ADD',f'NFLOAT {NAN}',F(NAN),ZERO_SIGN),False,False,False),
        ('diverror',B('DIVIDE',f'NFLOAT {ONE}',raw_one,ZERO_SIGN),False,False,True),
        ('outer',U('UP',NEGZERO,tree),False,False,True),
        ('inside',B('ADD','NFLOAT 0',U('UP',NEGZERO,tree),F(0)),False,False,True),
        ('promoted',B('SUBTRACT','NFLOAT 0',promoted,promoted),True,False,False)]
    for label,condition,safe,accepted,refuses in controls:
        checks += install(label,condition) + [f'{NODE}(S_{label},porigin_cond) = ' + ('eps' if refuses else f'(({condition[1]},{flags(condition)}))'),
            f'{"" if safe else "~"}$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,porigin_cond)',
            f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ' + ('((porigin_cond,porigin_selected))' if accepted else 'eps'),
            f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
        if label == 'safezero':
            checks += [f'{FALSEY}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))']
    return checks


def affected318(group):
    checks = BASE + ['S.CODE = [pcode]', 'n_unit = pcode.UNIT', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)', 'pdefault.ORIGIN = PORIGIN n_unit pcpath',
        '$origin_node(S.SOURCES,pdefault.ORIGIN) = (NExprTernary expression_cond expression_selected expression_skip metadata)',
        'porigin_cond = '+origin('pcpath',(0,)), 'porigin_selected = '+origin('pcpath',(1,)),
        f'{ROOT}(S,pfunction.ENV,pdefault.ORIGIN) = eps',
        f'{affected.ROOT}(S,pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))',
        '$lossy_optional_integer_deferred(S,pfunction,0)']
    for label,tree in [('zero',affected.signed('++',TREES[group][0])),
            ('nan',affected.signed('++',B('ADD',f'NFLOAT {NAN}',F(NAN),ZERO_SIGN)))]:
        checks += affected.install(label,tree) + [
            f'{affected.COUNTED}(S_{label},porigin_cond) = eps',
            f'{affected.ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
            f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
            f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
    return checks


CASES = {}
for group in ['pure','mixed']:
    prefix = 'deferred-float-number-tree-zero-full-ternary-redirect-wrapper-'+group
    raw_entries = [(0,0,'PINT 0'),(1,1,'PNULL')]
    named_entries = [(1,1,'PBOOL false'),(2,0,f'PFLOAT {NEGZERO}')]
    raw = ROWS[prefix+'-raw-tagged-results']['source']
    CASES[group+'-zero-independent-tags'] = {'source':raw, 'stage':RAW_STAGE,
        'checks':receipts(group,raw_entries,False)+finish(raw_entries,False)}
    CASES[group+'-zero-independent-certificates'] = {'source':raw, 'stage':RAW_STAGE, 'checks':certificates(group)}
    CASES[group+'-zero-independent-private'] = {'source':ROWS[prefix+'-alias-named-reentry']['source'],
        'stage':CONTEXT+'-- if pcallcontext.ARGC = 1 -- if pfunction.ENV.NAMESPACE = $ptascii("FloatNumber'+group.title()+'TreeZeroRedirect319") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks':receipts(group,named_entries,True)+finish(named_entries,True)}
    CASES[group+'-affected318-zero-nan'] = {'source':affected.ROWS['deferred-repeated-unary-float-number-tree-finite-nonzero-full-ternary-redirect-wrapper-'+group+'-raw-tagged-results']['source'],
        'stage':RAW_STAGE, 'checks':affected318(group)}

if __name__ == '__main__':
    support = [module for module in tuple(sys.modules.values())
        if getattr(module, '__file__', None) and Path(module.__file__).parent == Path(__file__).parent]
    inputs = {Path(module.__file__) for module in support}
    inputs.update(module.CATALOGUE for module in support if hasattr(module, 'CATALOGUE'))
    protocol.run(CASES, extra_inputs=tuple(sorted(inputs)), runner_flags=('--sl',))
