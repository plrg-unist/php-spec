#!/usr/bin/env python3
"""Literal sign chains retain zero bits, phase bounds and private defaults."""
import hashlib
import json
from pathlib import Path
import sys

import closure_call_protocol as protocol
import deferred_float_number_tree_zero_full_ternary_redirect_wrapper_default_reception_review_protocol as zero
import deferred_unary_float_number_tree_zero_full_ternary_redirect_wrapper_default_reception_review_protocol as affected
from deferred_float_number_tree_zero_full_ternary_redirect_wrapper_default_reception_review_protocol import (
    I, F, U, walk, path, origin, expression, nodes,
    POSINF, NEGZERO, ONE, NAN, ZERO_SIGN, BASE, CONTEXT, RAW_STAGE,
)

CATALOGUE = Path(__file__).with_name('deferred_literal_float_zero_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
ROOT = '$lossy_optional_integer_literal_float_zero_full_redirect'
FALSEY = '$lossy_optional_integer_falsey_full_redirect'
TREES = [ZERO_SIGN,U('UM',0,ZERO_SIGN)]


def receipts(entries, wrapped):
    checks = BASE + ['S.CODE = [pcode]', 'n_unit = pcode.UNIT', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
        '$default_cache_owner(S) = (CACHE_SHARED)']
    for index, positive, selected_value in entries:
        tree = TREES[positive]
        bits = int(tree[1][7:])
        where, tail = f'pcpath_{index}', (0,) if wrapped else ()
        full, cond, skipped, selected = [origin(where,tail+fields) for fields in [(),(0,),(1,),(2,)]]
        received = 'PINT 0' if wrapped else selected_value
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'pdefault_{index}.ORIGIN = PORIGIN n_unit {where}',
            f'$origin_node(S.SOURCES,{full}) = (NExprTernary {expression(index,())} expression_skip_{index} expression_selected_{index} metadata_{index})',
            f'$origin_node(S.SOURCES,{skipped}) = (expression_skip_{index})',
            f'$origin_node(S.SOURCES,{selected}) = (expression_selected_{index})',
            f'$lossy_optional_integer_float_literal({expression(index,())}) = ({bits})',
            f'$lossy_optional_integer_numeric(pfunction.ENV,{expression(index,())}) = (NFLOAT {bits})',
            f'$float_decode({bits}) = FINITE {bits >> 63} 0 n_denominator_{index}',
            f'$lossy_optional_integer_condition(pfunction.ENV,{expression(index,())}) = (false)',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,{cond})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{cond}) = eps',
            f'$code_expression(pcode.EXPRESSIONS,{path(where,tail)}) = ((z_{index},false))',
            rf'$pool_value(S.POOLS,{full}) = eps /\ $compiled_read(S,{full}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{path(where,tail)}) = 1',
            f'$compiled_redirect(S,{full}) = (({selected},expression_selected_{index},false,z_{index}))',
            f'{FALSEY}(S,pfunction.ENV,{full}) = eps', f'{zero.ROOT}(S,pfunction.ENV,{full}) = eps',
            f'{affected.ROOT}(S,pfunction.ENV,{full}) = eps',
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
        checks += nodes(tree,where,tail+(0,),index)
    return checks


def finish(entries, named):
    return [check.replace('x319','x321').replace('Base319','Base321').replace('One319','One321')
        for check in zero.finish(entries,named)]


def certificates():
    tree = TREES[0]
    checks = receipts([(0,0,'PINT 0')],False) + ['pcpath = pcpath_0', 'pdefault = pdefault_0',
        'porigin_cond = '+origin('pcpath',(0,)), 'porigin_selected = '+origin('pcpath',(2,)),
        '$origin_node(S.SOURCES,pdefault.ORIGIN) = (NExprTernary expression_cond expression_skip expression_selected metadata)']
    mutations = {'missing':'S[.CODE = [pcode[.REDIRECTS = eps]]]',
        'duplicate':'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
        'copy':'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 2]) true)]]]]',
        'target':'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath (pcpath ++ [PCFIELD 1]) false)]]]]',
        'owncode':'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath z_0 true)] ++ pcode.EXPRESSIONS)]]]',
        'ownpool':'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath (PINT 0))] ++ ppool.CONSTANTS)]]]'}
    fields = [(0,)+tail for tail in walk(tree)]
    for at in fields:
        label = ''.join(map(str,at))
        mutations['tag'+label] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath",at)}) (PINT 0))] ++ ppool.CONSTANTS)]]]'
        bits = int(walk(tree)[at[1:]][1][7:])
        mutations['sign'+label] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path("pcpath",at)}) (PFLOAT {bits ^ NEGZERO}))] ++ ppool.CONSTANTS)]]]'
        for flag in ['false','true']:
            mutations['code'+label+flag] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path("pcpath",at)}) z_0 {flag})] ++ pcode.EXPRESSIONS)]]]'
        mutations['redirect'+label] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT ({path("pcpath",at)}) (pcpath ++ [PCFIELD 2]) false)] ++ pcode.REDIRECTS)]]]'
    for label,update in mutations.items():
        checks += [f'S_{label} = {update}', f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
            f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
    for at in [(),(1,),(2,)] + fields:
        label = ''.join(map(str,at)) or 'root'
        checks += [f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path("pcpath",at)}) (NScalarInt (INTEGER 99) eps))] ++ pcunit.OCCURRENCES)]]]',
            f'{ROOT}(S_source_{label},pfunction.ENV,pdefault.ORIGIN) = eps',
            f'~$lossy_optional_integer_deferred(S_source_{label},pfunction,0)']
    controls = [('longnegative',U('UP',NEGZERO,ZERO_SIGN),False,True,True,True),
        ('longpositive',U('UM',0,U('UP',NEGZERO,ZERO_SIGN)),False,True,True,True),
        ('safezero',F(0),True,False,True,True),
        ('safenegative',U('UM',NEGZERO,F(0)),True,False,True,True),
        ('safeplus',U('UP',0,F(0)),True,False,True,True),
        ('nonzero',U('UP',ONE,F(ONE)),True,False,True,True),
        ('infinite',U('UP',POSINF,F(POSINF)),True,False,True,True),
        ('nan',U('UP',NAN,F(NAN)),True,False,True,True),
        ('integer',I(0),True,False,False,False),
        ('binary',zero.TREES['pure'][0],False,False,False,True),
        ('computed',U('UP',NEGZERO,zero.TREES['pure'][0]),False,False,False,False),
        ('repeatedcomputed',U('UP',NEGZERO,U('UP',NEGZERO,zero.TREES['pure'][0])),False,False,False,False)]
    for label,condition,safe,accepted,literal,collected in controls:
        checks += zero.install(label,condition) + [
            f'$lossy_optional_integer_float_literal(expression_{label}) = '+(f'({condition[1][7:]})' if literal else 'eps'),
            f'$lossy_optional_integer_float_tree_value(S_{label},porigin_cond) = '+(f'({condition[1][7:]})' if collected else 'eps'),
            f'{"" if safe else "~"}$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,porigin_cond)',
            f'{ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = '+('((porigin_cond,porigin_selected))' if accepted else 'eps'),
            f'~$lossy_optional_integer_deferred(S_{label},pfunction,0)']
        if label in ['safezero','safenegative','safeplus','integer']:
            checks += [f'{FALSEY}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))']
        if label == 'binary': checks += [f'{zero.ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))']
        if label == 'computed': checks += [f'{affected.ROOT}(S_{label},pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))']
    return checks


def affected320():
    checks = BASE + ['S.CODE = [pcode]', 'n_unit = pcode.UNIT', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
        '$default_at(pfunction.DEFAULTS,0) = (pdefault)', 'pdefault.ORIGIN = PORIGIN n_unit pcpath',
        '$origin_node(S.SOURCES,pdefault.ORIGIN) = (NExprTernary expression_cond expression_skip expression_selected metadata)',
        'porigin_cond = '+origin('pcpath',(0,)), 'porigin_selected = '+origin('pcpath',(2,)),
        f'{affected.ROOT}(S,pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))',
        f'{ROOT}(S,pfunction.ENV,pdefault.ORIGIN) = eps', '$lossy_optional_integer_deferred(S,pfunction,0)']
    checks += zero.install('literal',TREES[0]) + [
        f'{affected.ROOT}(S_literal,pfunction.ENV,pdefault.ORIGIN) = eps',
        f'{ROOT}(S_literal,pfunction.ENV,pdefault.ORIGIN) = ((porigin_cond,porigin_selected))',
        '~$lossy_optional_integer_deferred(S_literal,pfunction,0)']
    return checks


raw_entries, named_entries = [(0,0,'PINT 0'),(1,1,'PNULL')], [(1,1,'PBOOL false'),(2,0,f'PFLOAT {NEGZERO}')]
prefix = 'deferred-literal-float-zero-full-ternary-redirect-wrapper-'
raw = ROWS[prefix+'raw-tagged-results']['source']
CASES = {
    'literal-zero-independent-tags': {'source':raw,'stage':RAW_STAGE,'checks':receipts(raw_entries,False)+finish(raw_entries,False)},
    'literal-zero-independent-certificates': {'source':raw,'stage':RAW_STAGE,'checks':certificates()},
    'literal-zero-independent-private': {'source':ROWS[prefix+'alias-named-reentry']['source'],
        'stage':CONTEXT+'-- if pcallcontext.ARGC = 1 -- if pfunction.ENV.NAMESPACE = $ptascii("LiteralFloatZeroRedirect321") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks':receipts(named_entries,True)+finish(named_entries,True)},
    'affected320-computed-zero': {'source':affected.ROWS['deferred-unary-float-number-tree-zero-full-ternary-redirect-wrapper-pure-raw-tagged-results']['source'],
        'stage':RAW_STAGE,'checks':affected320()},
}

if __name__ == '__main__':
    support = [module for module in tuple(sys.modules.values())
        if getattr(module,'__file__',None) and Path(module.__file__).parent == Path(__file__).parent]
    inputs = {Path(module.__file__) for module in support}
    inputs.update(module.CATALOGUE for module in support if hasattr(module,'CATALOGUE'))
    protocol.run(CASES,extra_inputs=tuple(sorted(inputs)),runner_flags=('--sl',))
