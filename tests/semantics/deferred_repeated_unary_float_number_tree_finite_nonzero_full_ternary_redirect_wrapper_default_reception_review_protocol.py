#!/usr/bin/env python3
"""Outer sign counts preserve finite typed trees, phase fences and private defaults."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import deferred_float_number_tree_finite_nonzero_full_ternary_redirect_wrapper_default_reception_review_protocol as prior
from deferred_float_number_tree_finite_nonzero_full_ternary_redirect_wrapper_default_reception_review_protocol import (
    I, F, U, B, ast, walk, flags, value, path, origin, expression, nodes,
    POSINF, NEGZERO, ONE, TWO, NAN, ZERO_SIGN, BASE, CONTEXT, RAW_STAGE, NODE,
)

CATALOGUE = Path(__file__).with_name('deferred_repeated_unary_float_number_tree_finite_nonzero_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
ROOT = '$lossy_optional_integer_repeated_unary_float_number_tree_finite_nonzero_full_redirect'
COUNTED = '$lossy_optional_integer_repeated_unary_finite_float_tree_value'
SIGNS = [('--', False), ('++', True), ('-+-', True), ('+--', False)]


def signed(signs, tree):
    for sign in reversed(signs):
        bits = int(tree[1][7:]) ^ (NEGZERO if sign == '-' else 0)
        tree = U('UM' if sign == '-' else 'UP', bits, tree)
    return tree


def receipts(group, entries, wrapped):
    checks = BASE + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]', '$default_cache_owner(S) = (CACHE_SHARED)']
    for index, raw_index, selected_value in entries:
        signs, negative = SIGNS[raw_index]
        base = prior.NEGATIVE[group] if negative else prior.TREES[group]
        tree = signed(signs, base)
        bits = int(tree[1][7:])
        where, tail = f'pcpath_{index}', (0,) if wrapped else ()
        full, cond, selected, skipped = [origin(where, tail + fields) for fields in [(), (0,), (1,), (2,)]]
        received = 'PINT 0' if wrapped else selected_value
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})', f'pdefault_{index}.ORIGIN = PORIGIN n_unit {where}',
            f'$origin_node(S.SOURCES,{full}) = (NExprTernary expression_cond_{index} expression_selected_{index} expression_skip_{index} metadata_{index})',
            f'$code_expression(pcode.EXPRESSIONS,{path(where,tail)}) = ((z_{index},false))',
            rf'$pool_value(S.POOLS,{full}) = eps /\ $compiled_read(S,{full}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where,tail)}) = 1',
            f'$compiled_redirect(S,{full}) = (({selected},expression_selected_{index},false,z_{index}))',
            f'$float_decode({bits}) = FINITE {bits >> 63} n_numerator_{index} n_denominator_{index}', f'n_numerator_{index} =/= 0',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,{cond})', f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = eps',
            f'{prior.ROOT}(S,pfunction.ENV,{full}) = eps', f'{prior.UNARY}(S,pfunction.ENV,{full}) = eps', f'{prior.FINITE}(S,pfunction.ENV,{full}) = eps',
            f'{ROOT}(S,pfunction.ENV,{full}) = (({cond},{selected}))', f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,{full}) = (({cond},{selected}))',
            f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,{skipped})', f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,{full})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{full}) = ({selected_value})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({received})', f'$lossy_optional_integer_deferred(S,pfunction,{index})',
            f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {received},CLASS PVSCALAR}}', f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})', f'S.STORE[n_private_{index}] = DEFINED ({received})',
            rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
        expr = f'expression_cond_{index}'
        for depth, sign in enumerate(signs):
            at = origin(where, tail+(0,)*(depth+1))
            child_expr = f'expression_sign_{index}_{depth}'
            child_bits = bits ^ (NEGZERO if sign == '-' else 0)
            checks += [f'$origin_node(S.SOURCES,{at}) = ({expr})', f'$pfshape({expr}) = PFUNARY {"NEGATIVE" if sign == "-" else "POSITIVE"} {child_expr}',
                f'$pool_value(S.POOLS,{at}) = (PFLOAT {bits})', f'$code_expression(pcode.EXPRESSIONS,{path(where,tail+(0,)*(depth+1))}) = eps',
                f'$compiled_read(S,{at}) = eps', f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where,tail+(0,)*(depth+1))}) = 0',
                f'{NODE}(S,{at}) = eps', f'{COUNTED}(S,{at}) = (({bits},{len(signs)-depth}))',
                f'$num_mul(NFLOAT {child_bits},NINT ' + ('$(-1)' if sign == '-' else '1') + f') = NFLOAT {bits}']
            expr, bits = child_expr, child_bits
        checks += [f'{expr} = {expression(index,())}', f'{COUNTED}(S,{origin(where,tail+(0,)*(len(signs)+1))}) = (({bits},0))']
        checks += nodes(base, where, tail+(0,)*(len(signs)+1), index)
    return checks


def finish(entries, named):
    checks = [check.replace('x317', 'x318') for check in prior.finish(entries, named)]
    if named:
        checks += ['plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base318"),$ptascii("E_ERROR")),($ptascii("One318"),$ptascii("E_ERROR")),($ptascii("Skipped318"),$ptascii("Unavailable318") ++ [92] ++ $ptascii("Payload"))]]',
            '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_1.ORIGIN)']
    return checks


def install(label, tree):
    constants = [f'(PCONSTANT ({path("pcpath",(0,)+tail)}) ({value(node)}))' for tail,node in walk(tree).items()]
    return [f'expression_{label} = {ast(tree)}',
        f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath (NExprTernary expression_{label} expression_selected expression_skip metadata)),(PCOCCURRENCE (pcpath ++ [PCFIELD 0]) expression_{label})] ++ $pcwalk($pcchildren(expression_{label},pcpath ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
        f'S_{label} = S_source_{label}[.POOLS = [ppool[.CONSTANTS = ([' + ','.join(constants) + '] ++ ppool.CONSTANTS)]]]']


def certificates(group):
    bits, base = prior.BITS[group], prior.TREES[group]
    checks = receipts(group, [(0,0,'PINT 0')], False) + ['pcpath = pcpath_0', 'pdefault = pdefault_0',
        'porigin_cond = '+origin('pcpath',(0,)), 'porigin_selected = '+origin('pcpath',(1,)),
        '$origin_node(S.SOURCES,pdefault.ORIGIN) = (NExprTernary expression_cond expression_selected expression_skip metadata)']
    mutations = {'missing':'S[.CODE = [pcode[.REDIRECTS = eps]]]',
        'duplicate':'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
        'copy':'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 1]) true)]]]]',
        'target':'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 2]) false)]]]]',
        'owncode':'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath z_0 true)] ++ pcode.EXPRESSIONS)]]]',
        'ownpool':'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath (PINT 0))] ++ ppool.CONSTANTS)]]]'}
    for depth in [1,2,3]:
        fields = (0,)*depth
        own_bits = bits ^ (NEGZERO if depth == 2 else 0)
        for tag, val in [('int','PINT 0'),('sign',f'PFLOAT {own_bits ^ NEGZERO}'),('zero','PFLOAT 0'),('negzero',f'PFLOAT {NEGZERO}'),('inf',f'PFLOAT {POSINF}'),('nan',f'PFLOAT {NAN}')]:
            mutations[tag+str(depth)] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath",fields)}) ({val}))] ++ ppool.CONSTANTS)]]]'
        for flag in ['false','true']:
            mutations['code'+str(depth)+flag] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path("pcpath",fields)}) z_0 {flag})] ++ pcode.EXPRESSIONS)]]]'
        mutations['redirect'+str(depth)] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT ({path("pcpath",fields)}) (pcpath ++ [PCFIELD 1]) false)] ++ pcode.REDIRECTS)]]]'
    for label, fields, val in [('rawtag',(0,0,0,0),'PINT '+('1' if group=='pure' else '3')),
            ('zerosign',(0,0,0,1),'PFLOAT 0'),('zerotag',(0,0,0,1,0,0),'PINT 0')]:
        mutations[label] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath",fields)}) ({val}))] ++ ppool.CONSTANTS)]]]'
    for label, update in mutations.items():
        checks += [f'S_{label} = {update}', f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps']
        safe = label in ['code2true','code3true']
        checks += [f'{"" if safe else "~"}$lossy_optional_integer_deferred(S_{label},pfunction,0)']
        if label in ['code1true','code2true','code3true']:
            checks += [f'$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,porigin_cond)']
        if safe:
            checks += [f'{prior.FINITE}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))']
    for fields in [(0,), (0,0), (0,0,0), (0,0,0,1,0,0), (1,), (2,)]:
        label = ''.join(map(str,fields))
        checks += [f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path("pcpath",fields)}) (NScalarInt (INTEGER 99) eps))] ++ pcunit.OCCURRENCES)]]]',
            f'{ROOT}(S_source_{label},pfunction.ENV,pdefault.ORIGIN) = eps', f'~$lossy_optional_integer_deferred(S_source_{label},pfunction,0)']
    controls = [('direct',base,'',0), ('single',signed('+',base),'+',1), ('long',signed('-+-+',base),'-+-+',4),
        ('safe',signed('++',B('ADD',f'NFLOAT {ONE}',F(ONE),F(0))),'++',2),
        ('literal',signed('++',F(ONE)),'',None),
        ('infinite',signed('++',B('ADD',f'NFLOAT {POSINF}',F(POSINF),ZERO_SIGN)),'',None),
        ('zero',signed('++',B('MULTIPLY',f'NFLOAT {NEGZERO}',F(ONE),ZERO_SIGN)),'',None),
        ('nan',signed('++',B('ADD',f'NFLOAT {NAN}',F(NAN),ZERO_SIGN)),'',None),
        ('divzero',signed('++',B('DIVIDE',f'NFLOAT {bits}',F(ONE),ZERO_SIGN)),'',None),
        ('inside',signed('++',B('ADD',f'NFLOAT {TWO if group=="pure" else prior.prior.THREE}',signed('+',base),F(ONE))),'',None),
        ('integer',signed('++',B('ADD','NFLOAT 4890909195324358656',I(9223372036854775807),I(1))),'',None)]
    for label, tree, signs, count in controls:
        checks += install(label,tree)
        checks += [f'{COUNTED}(S_{label},porigin_cond) = '+('eps' if count is None else f'(({tree[1][7:]},{count}))'),
            f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = '+('((porigin_cond,porigin_selected))' if label=='long' else 'eps'),
            f'{prior.ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = '+('((porigin_cond,porigin_selected))' if label=='direct' else 'eps'),
            f'{prior.UNARY}(S_{label},pfunction.ENV,pdefault.ORIGIN) = '+('((porigin_cond,porigin_selected))' if label=='single' else 'eps')]
        if label=='inside':
            checks += [f'{NODE}(S_{label},{origin("pcpath",(0,0,0))}) = eps', f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
        if label=='integer':
            checks += [f'{NODE}(S_{label},{origin("pcpath",(0,0,0))}) = ((NFLOAT 4890909195324358656,true,false))']
        if label=='safe':
            checks += [f'$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,porigin_cond)']
    return checks


CASES = {}
for group in ['pure','mixed']:
    prefix = 'deferred-repeated-unary-float-number-tree-finite-nonzero-full-ternary-redirect-wrapper-'+group
    raw_entries, named_entries = [(0,0,'PINT 0'),(1,1,'PNULL')], [(1,2,'PBOOL false'),(2,3,f'PFLOAT {NEGZERO}')]
    CASES[group+'-repeated-finite-independent-tags'] = {'source':ROWS[prefix+'-raw-tagged-results']['source'], 'stage':RAW_STAGE,
        'checks':receipts(group,raw_entries,False)+finish(raw_entries,False)}
    CASES[group+'-repeated-finite-independent-certificates'] = {'source':ROWS[prefix+'-raw-tagged-results']['source'], 'stage':RAW_STAGE, 'checks':certificates(group)}
    CASES[group+'-repeated-finite-independent-private'] = {'source':ROWS[prefix+'-alias-named-reentry']['source'],
        'stage':CONTEXT+'-- if pcallcontext.ARGC = 1 -- if pfunction.ENV.NAMESPACE = $ptascii("FloatNumber'+group.title()+'TreeFiniteRedirect318") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks':receipts(group,named_entries,True)+finish(named_entries,True)}
    old = prior.certificates(group)
    prefix_end = next(i for i,c in enumerate(old) if c.startswith('S_missing = '))
    start = next(i for i,c in enumerate(old) if c.startswith('expression_nested_unary = '))
    CASES[group+'-affected317-computed-unary'] = {'source':prior.ROWS['deferred-float-number-tree-finite-nonzero-full-ternary-redirect-wrapper-'+group+'-raw-tagged-results']['source'],
        'stage':RAW_STAGE, 'checks':old[:prefix_end]+old[start:]+[ROOT+'(S_nested_unary,pfunction.ENV,pdefault.ORIGIN) = eps']}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE, Path(prior.__file__), prior.CATALOGUE,
        Path(prior.prior.__file__), prior.prior.CATALOGUE, Path(prior.prior.affected.__file__), prior.prior.affected.CATALOGUE,
        Path(prior.prior.previous.__file__), prior.prior.previous.CATALOGUE,
        Path(prior.prior.previous.previous.__file__), prior.prior.previous.previous.CATALOGUE), runner_flags=('--sl',))
