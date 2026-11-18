#!/usr/bin/env python3
"""One-sign zero receipts retain exact pools, phase boundaries and private cells."""
import hashlib
import json
from pathlib import Path
import sys

import closure_call_protocol as protocol
import deferred_float_number_tree_zero_full_ternary_redirect_wrapper_default_reception_review_protocol as zero
from deferred_float_number_tree_zero_full_ternary_redirect_wrapper_default_reception_review_protocol import (
    I, F, U, B, walk, flags, path, origin, expression, nodes,
    POSINF, NEGZERO, ONE, NAN, MAX, ZERO_SIGN, BASE, CONTEXT, RAW_STAGE, NODE,
)

CATALOGUE = Path(__file__).with_name('deferred_unary_float_number_tree_zero_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
ROOT = '$lossy_optional_integer_unary_float_number_tree_zero_full_redirect'
FALSEY = '$lossy_optional_integer_falsey_full_redirect'


def receipts(group, entries, wrapped):
    checks = BASE + ['S.CODE = [pcode]', 'n_unit = pcode.UNIT', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
        '$default_cache_owner(S) = (CACHE_SHARED)']
    tree = zero.TREES[group][0]
    for index, negative, selected_value in entries:
        bits, sign, factor = (0,'NEGATIVE','$(-1)') if negative else (NEGZERO,'POSITIVE','1')
        where, tail = f'pcpath_{index}', (0,) if wrapped else ()
        full, cond, child, skipped, selected = [origin(where, tail + fields) for fields in [(), (0,), (0,0), (1,), (2,)]]
        received = 'PINT 0' if wrapped else selected_value
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'pdefault_{index}.ORIGIN = PORIGIN n_unit {where}',
            f'$origin_node(S.SOURCES,{full}) = (NExprTernary expression_cond_{index} expression_skip_{index} expression_selected_{index} metadata_{index})',
            f'$origin_node(S.SOURCES,{cond}) = (expression_cond_{index})',
            f'$pfshape(expression_cond_{index}) = PFUNARY {sign} {expression(index,())}',
            f'$origin_node(S.SOURCES,{skipped}) = (expression_skip_{index})',
            f'$origin_node(S.SOURCES,{selected}) = (expression_selected_{index})',
            f'$pool_value(S.POOLS,{cond}) = (PFLOAT {bits})',
            f'$code_expression(pcode.EXPRESSIONS,{path(where,tail+(0,))}) = eps',
            f'$compiled_read(S,{cond}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where,tail+(0,))}) = 0',
            f'{NODE}(S,{cond}) = eps',
            f'$num_mul(NFLOAT {NEGZERO},NINT {factor}) = NFLOAT {bits}',
            f'$float_decode({bits}) = FINITE {bits >> 63} 0 n_denominator_{index}',
            f'$lossy_optional_integer_numeric(pfunction.ENV,expression_cond_{index}) = (NFLOAT {bits})',
            f'$lossy_optional_integer_condition(pfunction.ENV,expression_cond_{index}) = (false)',
            f'{"~" if negative else ""}$lossy_optional_integer_phase_sensitive(pfunction.ENV,expression_cond_{index})',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,{child})',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,{cond})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = eps',
            f'$code_expression(pcode.EXPRESSIONS,{path(where,tail)}) = ((z_{index},false))',
            rf'$pool_value(S.POOLS,{full}) = eps /\ $compiled_read(S,{full}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where,tail)}) = 1',
            f'$compiled_redirect(S,{full}) = (({selected},expression_selected_{index},false,z_{index}))',
            f'{FALSEY}(S,pfunction.ENV,{full}) = eps', f'{zero.ROOT}(S,pfunction.ENV,{full}) = eps',
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
        checks += nodes(tree, where, tail+(0,0), index)
    return checks


def finish(entries, named):
    return [check.replace('x319','x320').replace('Base319','Base320').replace('One319','One320')
        for check in zero.finish(entries,named)]


def certificates(group):
    tree = zero.TREES[group][0]
    checks = receipts(group, [(0,False,'PINT 0')], False) + [
        'pcpath = pcpath_0', 'pdefault = pdefault_0', 'porigin_cond = '+origin('pcpath',(0,)),
        'porigin_child = '+origin('pcpath',(0,0)), 'porigin_selected = '+origin('pcpath',(2,)),
        '$origin_node(S.SOURCES,pdefault.ORIGIN) = (NExprTernary expression_cond expression_skip expression_selected metadata)']
    mutations = {'missing':'S[.CODE = [pcode[.REDIRECTS = eps]]]',
        'duplicate':'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
        'copy':'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 2]) true)]]]]',
        'target':'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 1]) false)]]]]',
        'owncode':'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath z_0 true)] ++ pcode.EXPRESSIONS)]]]',
        'ownpool':'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath (PINT 0))] ++ ppool.CONSTANTS)]]]',
        'condsign':'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath ++ [PCFIELD 0]) (PFLOAT 0))] ++ ppool.CONSTANTS)]]]'}
    node_fields = [(0,)] + [(0,0)+tail for tail in walk(tree)]
    for fields in node_fields:
        label = ''.join(map(str,fields))
        mutations['pool'+label] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath",fields)}) (PINT 7))] ++ ppool.CONSTANTS)]]]'
        for flag in ['false','true']:
            mutations['code'+label+flag] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path("pcpath",fields)}) z_0 {flag})] ++ pcode.EXPRESSIONS)]]]'
        mutations['redirect'+label] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT ({path("pcpath",fields)}) (pcpath ++ [PCFIELD 2]) false)] ++ pcode.REDIRECTS)]]]'
    for label,update in mutations.items():
        checks += [f'S_{label} = {update}', f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
            f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
    for fields in [(),(1,),(2,)] + node_fields:
        label = ''.join(map(str,fields)) or 'root'
        checks += [f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path("pcpath",fields)}) (NScalarInt (INTEGER 99) eps))] ++ pcunit.OCCURRENCES)]]]',
            f'{ROOT}(S_source_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
            f'~$lossy_optional_integer_deferred(S_source_{label},pfunction,0)']
    raw_zero, raw_one = (F(0),F(ONE)) if group == 'pure' else (I(0),I(1))
    safe_negative = B('MULTIPLY',f'NFLOAT {NEGZERO}',raw_one,U('UM',NEGZERO,F(0)))
    safe_positive = B('MULTIPLY','NFLOAT 0',raw_one,F(0))
    promoted = B('ADD','NFLOAT 4890909195324358656',I(MAX),I(1))
    controls = [('addzero',U('UP',0,B('ADD','NFLOAT 0',ZERO_SIGN,raw_zero)),False,True,False),
        ('subzero',U('UP',NEGZERO,B('SUBTRACT',f'NFLOAT {NEGZERO}',ZERO_SIGN,raw_zero)),False,True,False),
        ('mulzero',U('UM',0,tree),False,True,False),
        ('divzeroresult',U('UP',NEGZERO,B('DIVIDE',f'NFLOAT {NEGZERO}',ZERO_SIGN,raw_one)),False,True,False),
        ('phaseown',U('UP',NEGZERO,safe_negative),False,True,False),
        ('safeplus',U('UP',0,safe_positive),True,False,False),
        ('safeminus',U('UM',NEGZERO,safe_positive),True,False,False),
        ('nonzero',U('UP',ONE,B('ADD',f'NFLOAT {ONE}',raw_one,ZERO_SIGN)),False,False,False),
        ('infinite',U('UP',POSINF,B('ADD',f'NFLOAT {POSINF}',F(POSINF),ZERO_SIGN)),False,False,False),
        ('nan',U('UP',NAN,B('ADD',f'NFLOAT {NAN}',F(NAN),ZERO_SIGN)),False,False,False),
        ('diverror',U('UP',ONE,B('DIVIDE',f'NFLOAT {ONE}',raw_one,ZERO_SIGN)),False,False,True),
        ('literal',U('UP',NEGZERO,U('UM',NEGZERO,F(0))),False,False,False),
        ('repeat',U('UP',NEGZERO,U('UP',NEGZERO,tree)),False,False,True),
        ('inside',U('UP',0,B('ADD','NFLOAT 0',U('UP',NEGZERO,tree),F(0))),False,False,True),
        ('promoted',U('UP',0,B('SUBTRACT','NFLOAT 0',promoted,promoted)),True,False,False)]
    for label,condition,safe,accepted,refuses in controls:
        child = condition[2]
        checks += zero.install(label,condition) + [
            f'{NODE}(S_{label},porigin_child) = ' + ('eps' if refuses else f'(({child[1]},{flags(child)}))'),
            f'{NODE}(S_{label},porigin_cond) = ' + (f'(({condition[1]},{flags(condition)}))' if label == 'literal' else 'eps'),
            f'{"" if safe else "~"}$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,porigin_cond)',
            f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ' + ('((porigin_cond,porigin_selected))' if accepted else 'eps'),
            f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
        if label == 'phaseown':
            checks += [f'$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,porigin_child)',
                f'$lossy_optional_integer_phase_sensitive(pfunction.ENV,expression_{label})']
        if label in ['safeplus','safeminus']:
            checks += [f'{FALSEY}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))']
    return checks


def affected319(group):
    checks = BASE + ['S.CODE = [pcode]', 'n_unit = pcode.UNIT', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)', 'pdefault.ORIGIN = PORIGIN n_unit pcpath',
        '$origin_node(S.SOURCES,pdefault.ORIGIN) = (NExprTernary expression_cond expression_skip expression_selected metadata)',
        'porigin_cond = '+origin('pcpath',(0,)), 'porigin_selected = '+origin('pcpath',(2,)),
        f'{zero.ROOT}(S,pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))',
        f'{ROOT}(S,pfunction.ENV,pdefault.ORIGIN) = eps', '$lossy_optional_integer_deferred(S,pfunction,0)']
    condition = U('UP',NEGZERO,zero.TREES[group][0])
    checks += zero.install('outer',condition) + [
        f'{zero.ROOT}(S_outer,pfunction.ENV,pdefault.ORIGIN) = eps',
        f'{ROOT}(S_outer,pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))',
        '~$lossy_optional_integer_deferred(S_outer,pfunction,0)']
    return checks


CASES = {}
for group in ['pure','mixed']:
    prefix = 'deferred-unary-float-number-tree-zero-full-ternary-redirect-wrapper-'+group
    raw_entries, named_entries = [(0,False,'PINT 0'),(1,True,'PNULL')], [(1,True,'PBOOL false'),(2,False,f'PFLOAT {NEGZERO}')]
    raw = ROWS[prefix+'-raw-tagged-results']['source']
    CASES[group+'-unary-zero-independent-tags'] = {'source':raw, 'stage':RAW_STAGE,
        'checks':receipts(group,raw_entries,False)+finish(raw_entries,False)}
    CASES[group+'-unary-zero-independent-certificates'] = {'source':raw, 'stage':RAW_STAGE, 'checks':certificates(group)}
    CASES[group+'-unary-zero-independent-private'] = {'source':ROWS[prefix+'-alias-named-reentry']['source'],
        'stage':CONTEXT+'-- if pcallcontext.ARGC = 1 -- if pfunction.ENV.NAMESPACE = $ptascii("UnaryFloatNumber'+group.title()+'TreeZeroRedirect320") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks':receipts(group,named_entries,True)+finish(named_entries,True)}
    CASES[group+'-affected319-direct-zero'] = {'source':zero.ROWS['deferred-float-number-tree-zero-full-ternary-redirect-wrapper-'+group+'-raw-tagged-results']['source'],
        'stage':RAW_STAGE,'checks':affected319(group)}

if __name__ == '__main__':
    support = [module for module in tuple(sys.modules.values())
        if getattr(module,'__file__',None) and Path(module.__file__).parent == Path(__file__).parent]
    inputs = {Path(module.__file__) for module in support}
    inputs.update(module.CATALOGUE for module in support if hasattr(module,'CATALOGUE'))
    protocol.run(CASES,extra_inputs=tuple(sorted(inputs)),runner_flags=('--sl',))
