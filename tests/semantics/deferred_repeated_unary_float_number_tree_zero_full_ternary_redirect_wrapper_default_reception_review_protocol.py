#!/usr/bin/env python3
"""Repeated computed-zero signs retain counted pools, phase bounds and cells."""
import hashlib
import json
from pathlib import Path
import sys

import closure_call_protocol as protocol
import deferred_float_number_tree_zero_full_ternary_redirect_wrapper_default_reception_review_protocol as zero
import deferred_unary_float_number_tree_zero_full_ternary_redirect_wrapper_default_reception_review_protocol as unary
import deferred_literal_float_zero_full_ternary_redirect_wrapper_default_reception_review_protocol as literal
from deferred_float_number_tree_zero_full_ternary_redirect_wrapper_default_reception_review_protocol import (
    I, F, U, B, walk, path, origin, expression, nodes,
    POSINF, NEGZERO, ONE, NAN, MAX, ZERO_SIGN, BASE, CONTEXT, RAW_STAGE,
)

CATALOGUE = Path(__file__).with_name('deferred_repeated_unary_float_number_tree_zero_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
ROOT = '$lossy_optional_integer_repeated_unary_float_number_tree_zero_full_redirect'
COUNTED = '$lossy_optional_integer_repeated_unary_zero_float_tree_value'
FALSEY = '$lossy_optional_integer_falsey_full_redirect'


def signed(signs, tree):
    for sign in reversed(signs):
        bits = int(tree[1][7:]) ^ (NEGZERO if sign == '-' else 0)
        tree = U('UM' if sign == '-' else 'UP',bits,tree)
    return tree


def receipts(group, entries, wrapped):
    checks = BASE + ['S.CODE = [pcode]', 'n_unit = pcode.UNIT', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
        '$default_cache_owner(S) = (CACHE_SHARED)']
    base = zero.TREES[group][0]
    for index, signs, selected_value in entries:
        bits = int(signed(signs,base)[1][7:])
        where, tail = f'pcpath_{index}', (0,) if wrapped else ()
        full, cond, skipped, selected = [origin(where,tail+fields) for fields in [(),(0,),(1,),(2,)]]
        received = 'PINT 0' if wrapped else selected_value
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'pdefault_{index}.ORIGIN = PORIGIN n_unit {where}',
            f'$origin_node(S.SOURCES,{full}) = (NExprTernary expression_cond_{index} expression_skip_{index} expression_selected_{index} metadata_{index})',
            f'$origin_node(S.SOURCES,{skipped}) = (expression_skip_{index})',
            f'$origin_node(S.SOURCES,{selected}) = (expression_selected_{index})',
            f'$float_decode({bits}) = FINITE {bits >> 63} 0 n_denominator_{index}',
            f'$lossy_optional_integer_numeric(pfunction.ENV,expression_cond_{index}) = (NFLOAT {bits})',
            f'$lossy_optional_integer_condition(pfunction.ENV,expression_cond_{index}) = (false)',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,{cond})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = eps',
            f'$code_expression(pcode.EXPRESSIONS,{path(where,tail)}) = ((z_{index},false))',
            rf'$pool_value(S.POOLS,{full}) = eps /\ $compiled_read(S,{full}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where,tail)}) = 1',
            f'$compiled_redirect(S,{full}) = (({selected},expression_selected_{index},false,z_{index}))',
            f'{FALSEY}(S,pfunction.ENV,{full}) = eps', f'{zero.ROOT}(S,pfunction.ENV,{full}) = eps',
            f'{unary.ROOT}(S,pfunction.ENV,{full}) = eps', f'{literal.ROOT}(S,pfunction.ENV,{full}) = eps',
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
        expr = f'expression_cond_{index}'
        for depth,sign in enumerate(signs):
            at = origin(where,tail+(0,)*(depth+1))
            child = f'expression_sign_{index}_{depth}'
            child_bits = bits ^ (NEGZERO if sign == '-' else 0)
            checks += [f'$origin_node(S.SOURCES,{at}) = ({expr})',
                f'$pfshape({expr}) = PFUNARY {"NEGATIVE" if sign == "-" else "POSITIVE"} {child}',
                f'$pool_value(S.POOLS,{at}) = (PFLOAT {bits})',
                f'$code_expression(pcode.EXPRESSIONS,{path(where,tail+(0,)*(depth+1))}) = eps',
                f'$compiled_read(S,{at}) = eps',
                f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where,tail+(0,)*(depth+1))}) = 0',
                f'{COUNTED}(S,{at}) = (({bits},{len(signs)-depth}))',
                f'$num_mul(NFLOAT {child_bits},NINT '+('$(-1)' if sign == '-' else '1')+f') = NFLOAT {bits}']
            expr,bits = child,child_bits
        base_origin = origin(where,tail+(0,)*(len(signs)+1))
        checks += [f'{expr} = {expression(index,())}', f'{COUNTED}(S,{base_origin}) = (({NEGZERO},0))']
        checks += nodes(base,where,tail+(0,)*(len(signs)+1),index)
    return checks


def finish(entries, named):
    return [check.replace('x319','x322').replace('Base319','Base322').replace('One319','One322')
        for check in zero.finish(entries,named)]


def certificates():
    base = zero.TREES['pure'][0]
    tree = signed('+-',base)
    checks = receipts('pure',[(0,'+-','PINT 0')],False) + ['pcpath = pcpath_0', 'pdefault = pdefault_0',
        'porigin_cond = '+origin('pcpath',(0,)), 'porigin_selected = '+origin('pcpath',(2,)),
        '$origin_node(S.SOURCES,pdefault.ORIGIN) = (NExprTernary expression_cond expression_skip expression_selected metadata)']
    mutations = {'missing':'S[.CODE = [pcode[.REDIRECTS = eps]]]',
        'duplicate':'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
        'copy':'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 2]) true)]]]]',
        'target':'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 1]) false)]]]]',
        'owncode':'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath z_0 true)] ++ pcode.EXPRESSIONS)]]]',
        'ownpool':'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath (PINT 0))] ++ ppool.CONSTANTS)]]]'}
    phase_reads = {(0,0),(0,0,0),(0,0,0,1)}
    fields = [(0,)+tail for tail in walk(tree)]
    for at in fields:
        label = ''.join(map(str,at))
        bits = int(walk(tree)[at[1:]][1][7:])
        for tag,value in [('tag','PINT 7'),('sign',f'PFLOAT {bits ^ NEGZERO}')]:
            mutations[tag+label] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath",at)}) ({value}))] ++ ppool.CONSTANTS)]]]'
        for flag in ['false','true']:
            mutations['code'+label+flag] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path("pcpath",at)}) z_0 {flag})] ++ pcode.EXPRESSIONS)]]]'
        mutations['redirect'+label] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT ({path("pcpath",at)}) (pcpath ++ [PCFIELD 2]) false)] ++ pcode.REDIRECTS)]]]'
    safe_labels = {'code'+''.join(map(str,at))+'true' for at in phase_reads}
    for label,update in mutations.items():
        checks += [f'S_{label} = {update}', f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps']
        if label in safe_labels or label == 'code0true':
            checks += [f'$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,porigin_cond)',
                f'$lossy_optional_integer_deferred_value_at(S_{label},pfunction.ENV,porigin_cond) = (PFLOAT 0)',
                f'{FALSEY}(S_{label},pfunction.ENV,pdefault.ORIGIN) = '+('((porigin_cond,porigin_selected))' if label in safe_labels else 'eps')]
        checks += [f'{"" if label in safe_labels else "~"}$lossy_optional_integer_deferred(S_{label},pfunction,0)']
    for at in [(),(1,),(2,)] + fields:
        label = ''.join(map(str,at)) or 'root'
        checks += [f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path("pcpath",at)}) (NScalarInt (INTEGER 99) eps))] ++ pcunit.OCCURRENCES)]]]',
            f'{ROOT}(S_source_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
            f'~$lossy_optional_integer_deferred(S_source_{label},pfunction,0)']
    safe_negative = B('MULTIPLY',f'NFLOAT {NEGZERO}',F(ONE),U('UM',NEGZERO,F(0)))
    promoted = B('ADD','NFLOAT 4890909195324358656',I(MAX),I(1))
    controls = [('base',base,0,False,False),('single',signed('+',base),1,False,False),
        ('double',tree,2,False,True),('long',signed('-+-+',base),4,False,True),
        ('phaseown',signed('++',safe_negative),2,False,True),
        ('safe',signed('--',B('MULTIPLY','NFLOAT 0',F(ONE),F(0))),2,True,False),
        ('literal',signed('+',ZERO_SIGN),None,False,False),
        ('nonzero',signed('++',B('ADD',f'NFLOAT {ONE}',F(ONE),ZERO_SIGN)),None,False,False),
        ('infinite',signed('++',B('ADD',f'NFLOAT {POSINF}',F(POSINF),ZERO_SIGN)),None,False,False),
        ('nan',signed('++',B('ADD',f'NFLOAT {NAN}',F(NAN),ZERO_SIGN)),None,False,False),
        ('diverror',signed('++',B('DIVIDE',f'NFLOAT {ONE}',F(ONE),ZERO_SIGN)),None,False,False),
        ('inside',signed('++',B('ADD','NFLOAT 0',U('UP',NEGZERO,base),F(0))),None,False,False),
        ('integer',signed('++',B('SUBTRACT','NFLOAT 0',promoted,promoted)),None,True,False)]
    for label,condition,count,safe,accepted in controls:
        checks += zero.install(label,condition) + [
            f'{COUNTED}(S_{label},porigin_cond) = '+('eps' if count is None else f'(({condition[1][7:]},{count}))'),
            f'{"" if safe else "~"}$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,porigin_cond)',
            f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = '+('((porigin_cond,porigin_selected))' if accepted else 'eps'),
            f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
        if label == 'base': checks += [f'{zero.ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))']
        if label == 'single': checks += [f'{unary.ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))']
        if label == 'literal': checks += [f'{literal.ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))']
        if label == 'safe': checks += [f'{FALSEY}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))']
        if label == 'phaseown':
            checks += [f'$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,{origin("pcpath",(0,0,0))})',
                f'$lossy_optional_integer_phase_sensitive(pfunction.ENV,expression_{label})']
    return checks



raw_entries,named_entries = [(0,'+-','PINT 0'),(1,'-+-','PNULL')],[(1,'-+-','PBOOL false'),(2,'+-',f'PFLOAT {NEGZERO}')]
prefix = 'deferred-repeated-unary-float-number-tree-zero-full-ternary-redirect-wrapper-'
raw = ROWS[prefix+'raw-tagged-results']['source']
CASES = {
    'repeated-zero-independent-tags': {'source':raw,'stage':RAW_STAGE,'checks':receipts('pure',raw_entries,False)+finish(raw_entries,False)},
    'repeated-zero-independent-certificates': {'source':raw,'stage':RAW_STAGE,'checks':certificates()},
    'repeated-zero-independent-private': {'source':ROWS[prefix+'alias-named-reentry']['source'],
        'stage':CONTEXT+'-- if pcallcontext.ARGC = 1 -- if pfunction.ENV.NAMESPACE = $ptascii("RepeatedFloatZeroRedirect322") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks':receipts('mixed',named_entries,True)+finish(named_entries,True)},
}

if __name__ == '__main__':
    support = [module for module in tuple(sys.modules.values())
        if getattr(module,'__file__',None) and Path(module.__file__).parent == Path(__file__).parent]
    inputs = {Path(module.__file__) for module in support}
    inputs.update(module.CATALOGUE for module in support if hasattr(module,'CATALOGUE'))
    protocol.run(CASES,extra_inputs=tuple(sorted(inputs)),runner_flags=('--sl',))
