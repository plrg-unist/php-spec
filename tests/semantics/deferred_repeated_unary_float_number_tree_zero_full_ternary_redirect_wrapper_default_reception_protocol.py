"""Repeated computed-zero sign receipts, private cells, mutations and resumption."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import deferred_unary_flat_float_number_tree_finite_nonzero_full_ternary_redirect_wrapper_default_reception_protocol as unary

import deferred_mixed_number_tree_infinite_full_ternary_redirect_wrapper_default_reception_protocol as prior

CATALOGUE = Path(__file__).with_name('deferred_repeated_unary_float_number_tree_zero_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
NEGZERO = 9223372036854775808
ONE = 4607182418800017408
ZERO = prior.U('UP', f'NFLOAT {NEGZERO}', prior.U('UM', f'NFLOAT {NEGZERO}', prior.F(0)))
TREES = {'pure': prior.B('MULTIPLY', f'NFLOAT {NEGZERO}', prior.F(ONE), ZERO),
         'mixed': prior.B('MULTIPLY', f'NFLOAT {NEGZERO}', prior.I(1), ZERO)}
SIGNS = [('+','-'), ('-','+','-'), ('-','+','-'), ('+','-')]
RAW_BITS = [0, NEGZERO, NEGZERO, 0]
VALUE = '$lossy_optional_integer_repeated_unary_zero_float_tree_value'
ROOT = '$lossy_optional_integer_repeated_unary_float_number_tree_zero_full_redirect'


def origin(index, tail=()):
    return f'PORIGIN n_unit ({prior.node_path(index,tail)})'


def facts(kind, entries, wrapped, cached=False):
    checks = list(prior.BASE)
    for index, raw_index, result in entries:
        bits = RAW_BITS[raw_index]
        signs = SIGNS[raw_index]
        received = 'PINT 0' if wrapped else result
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_default_{index}',
            f'pcpath_full_{index} = pcpath_default_{index}' + (' ++ [PCFIELD 0]' if wrapped else ''),
            f'porigin_full_{index} = PORIGIN n_unit pcpath_full_{index}',
            f'$origin_node(S.SOURCES,porigin_full_{index}) = (NExprTernary expression_cond_{index} expression_skipped_{index} expression_selected_{index} metadata_{index})',
            f'$origin_node(S.SOURCES,{origin(index)}) = (expression_cond_{index})',
            f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])) = (expression_skipped_{index})',
            f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])) = (expression_selected_{index})',
            f'expression_skipped_{index} = NExprConstFetch name_skipped_{index} metadata_skipped_{index}',
            f'$lossy_optional_integer_float_literal(expression_cond_{index}) = eps',
            f'$lossy_optional_integer_integer_literal(expression_cond_{index}) = eps']
        expression = f'expression_cond_{index}'
        for depth, sign in enumerate(signs):
            tail = (0,)*depth
            child = f'expression_sign_{index}_{depth}'
            child_bits = bits ^ (NEGZERO if sign == '-' else 0)
            checks += [f'$origin_node(S.SOURCES,{origin(index,tail)}) = ({expression})',
                f'{expression} = NExprUnary' + ('Minus' if sign == '-' else 'Plus') + f' {child} metadata_sign_{index}_{depth}',
                f'$pool_value(S.POOLS,{origin(index,tail)}) = (PFLOAT {bits})',
                f'$code_expression(pcode.EXPRESSIONS,{prior.node_path(index,tail)}) = eps',
                f'$compiled_read(S,{origin(index,tail)}) = eps',
                f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{prior.node_path(index,tail)}) = 0',
                f'$lossy_optional_integer_mixed_number_tree_value(S,{origin(index,tail)}) = eps',
                f'{VALUE}(S,{origin(index,tail)}) = (({bits},{len(signs)-depth}))',
                f'$number_binary(MULTIPLY,NINT ' + ('$(-1)' if sign == '-' else '1') + f',NFLOAT {child_bits}) = NUM (NFLOAT {bits})']
            expression,bits = child,child_bits
        nodes,number = prior.tree_checks(index,TREES[kind],tail=(0,)*len(signs),expression=expression)
        checks += nodes + [f'{number} = NFLOAT {NEGZERO}',
            f'{VALUE}(S,{origin(index,(0,)*len(signs))}) = (({NEGZERO},0))',
            f'$lossy_optional_integer_mixed_number_tree_value(S,{origin(index,(0,)*len(signs))}) = ((NFLOAT {NEGZERO},{str(kind=="mixed").lower()},true))',
            f'$lossy_optional_integer_numeric(pfunction.ENV,expression_cond_{index}) = (NFLOAT {RAW_BITS[raw_index]})',
            f'$float_decode({RAW_BITS[raw_index]}) = FINITE n_sign_{index} 0 n_denominator_{index}',
            f'$lossy_optional_integer_condition(pfunction.ENV,expression_cond_{index}) = (false)',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,{origin(index)})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{origin(index)}) = eps',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,{origin(index)})',
            f'$code_expression(pcode.EXPRESSIONS,pcpath_full_{index}) = ((z_{index},false))',
            f'$pool_value(S.POOLS,porigin_full_{index}) = eps',
            f'$compiled_read(S,porigin_full_{index}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_full_{index}) = 1',
            f'$compiled_redirect(S,porigin_full_{index}) = ((PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2]),expression_selected_{index},false,z_{index}))',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2]))',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])) = ({result})',
            f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1]))',
            f'$code_name(pcode.NAMES,pcpath_full_{index} ++ [PCFIELD 1]) = eps',
            f'$call_name_count(pcode.NAMES,pcpath_full_{index} ++ [PCFIELD 1]) = 0']
        for helper in ('falsey','float_number_tree_zero','unary_float_number_tree_zero','literal_float_zero','finite_nonzero_float','float_number_tree_finite_nonzero','unary_float_number_tree_finite_nonzero','repeated_unary_float_number_tree_finite_nonzero','infinite_float'):
            checks += [f'$lossy_optional_integer_{helper}_full_redirect(S,pfunction.ENV,porigin_full_{index}) = eps']
        checks += [f'{ROOT}(S,pfunction.ENV,porigin_full_{index}) = (({origin(index)},PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])))',
            f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_full_{index}) = (({origin(index)},PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])))',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_full_{index})',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_full_{index})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_full_{index}) = ({result})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({received})',
            f'$lossy_optional_integer_deferred(S,pfunction,{index})',
            f'$default_current_cache(S,pdefault_{index}.ORIGIN) = eps']
        if cached:
            checks.remove(f'$default_current_cache(S,pdefault_{index}.ORIGIN) = eps')
            checks += [f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {received},CLASS PVSCALAR}}',
                f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
                f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
                f'S.STORE[n_cell_{index}] = DEFINED ({received})', f'~(n_cell_{index} <- S.REFCELLS)',
                f'$heap_owners($heap_graph(S),HCELL n_cell_{index}) = 1']
    return checks


def raw_checks():
    checks = facts('pure', [(0,0,'PINT 0'),(1,1,'PNULL')], False, True)
    path = prior.node_path(0, (0,0,0))
    checks += [f'S_child_tag = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path}) (PINT 1))] ++ ppool.CONSTANTS)]]]',
        '$pool_value(S_child_tag.POOLS,PORIGIN n_unit (pcpath_full_0 ++ [PCFIELD 0])) = (PFLOAT 0)',
        f'{VALUE}(S_child_tag,PORIGIN n_unit (pcpath_full_0 ++ [PCFIELD 0])) = eps',
        f'{ROOT}(S_child_tag,pfunction.ENV,porigin_full_0) = eps',
        '~$lossy_optional_integer_deferred(S_child_tag,pfunction,0)']
    for index in range(2):
        checks += [f'S_wrong_cache_{index} = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_{index}[.VALUE = PBOOL false])]',
            f'$default_caches_valid(S_wrong_cache_{index},S_wrong_cache_{index}.DEFAULTCACHE)',
            f'~$lossy_optional_integer_deferred(S_wrong_cache_{index},pfunction,{index})']
    checks += ['S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        'S_done = $drive_steps(S,3010)', 'S_done.COMPLETION = NORMAL',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.TODO = eps',
        '$heap_valid($heap_graph(S_done))', '$default_caches_valid(S_done,S_done.DEFAULTCACHE)']
    for index in range(2):
        checks += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            f'~((HCELL n_cell_{index}) <- S_done.ALLOCATIONS)',
            f'$heap_owners($heap_graph(S_done),HCELL n_cell_{index}) = 0']
    return checks


def certificate_checks():
    checks = facts('mixed', [(1,2,'PBOOL false'),(2,3,'PFLOAT 9223372036854775808')], True)
    checks += ['pcallcontext.HOLES = [1,2]', 'S.SOURCES = [pcunit]',
        'pcpath_full = pcpath_full_1', 'porigin_full = porigin_full_1',
        'pcpath_cond = pcpath_full ++ [PCFIELD 0]',
        'pcpath_selected = pcpath_full ++ [PCFIELD 2]', 'pcpath_skipped = pcpath_full ++ [PCFIELD 1]']
    mutations = {
        'duplicate': 'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ [(CODEREDIRECT pcpath_full pcpath_selected false)])]]]',
        'copy': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_full pcpath_selected true)]]]]',
        'target': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_full pcpath_skipped false)]]]]',
        'owncode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_full z_1 true)] ++ pcode.EXPRESSIONS)]]]',
        'ownpool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_full (PBOOL false))] ++ ppool.CONSTANTS)]]]',
        'condsign': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_cond (PFLOAT 0))] ++ ppool.CONSTANTS)]]]',
    }
    def paths(tree, tail=()):
        return [tail] + [path for index,child in enumerate(tree[2:]) for path in paths(child,tail+(index,))]
    zero_tail = (0,0,0,1)
    allpaths = [(),(0,),(0,0)] + [(0,0,0)+tail for tail in paths(TREES['mixed'])]
    phase_reads = set()
    for serial,tail in enumerate(allpaths):
        if zero_tail[:len(tail)] == tail:
            phase_reads.add('noderead'+str(serial))
        path = prior.node_path(1, tail)
        mutations[f'nodepool{serial}'] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path}) (PINT 7))] ++ ppool.CONSTANTS)]]]'
        mutations[f'nodecode{serial}'] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path}) z_1 false)] ++ pcode.EXPRESSIONS)]]]'
        mutations[f'noderead{serial}'] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path}) z_1 true)] ++ pcode.EXPRESSIONS)]]]'
        mutations[f'noderedirect{serial}'] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT ({path}) pcpath_selected false)] ++ pcode.REDIRECTS)]]]'
        mutations[f'nodesource{serial}'] = f'S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path}) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]'
    for label,expression in mutations.items():
        checks += [f'S_{label} = {expression}',
            f'{ROOT}(S_{label},pfunction.ENV,porigin_full) = eps']
        if label in phase_reads:
            checks += [f'$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,PORIGIN n_unit pcpath_cond)',
                f'$lossy_optional_integer_deferred_value_at(S_{label},pfunction.ENV,PORIGIN n_unit pcpath_cond) = (PFLOAT {RAW_BITS[2]})']
            if label == 'noderead0':
                checks += [f'$lossy_optional_integer_falsey_full_redirect(S_{label},pfunction.ENV,porigin_full) = eps',
                    f'$lossy_optional_integer_pruned_ternary(S_{label},pfunction.ENV,porigin_full) = eps',
                    f'~$lossy_optional_integer_deferred_bindings(S_{label},pfunction.ENV,pdefault_1.ORIGIN)',
                    f'~$lossy_optional_integer_deferred(S_{label},pfunction,1)']
            else:
                checks += [f'$lossy_optional_integer_falsey_full_redirect(S_{label},pfunction.ENV,porigin_full) = ((PORIGIN n_unit pcpath_cond,PORIGIN n_unit pcpath_selected))',
                    f'$lossy_optional_integer_deferred(S_{label},pfunction,1)']
        else:
            checks += [f'~$lossy_optional_integer_deferred(S_{label},pfunction,1)']
    checks += ['S_no_names = S[.CODE = [pcode[.NAMES = eps]]]',
        '~$lossy_optional_integer_deferred_bindings(S_no_names,pfunction.ENV,pdefault_1.ORIGIN)',
        '~$lossy_optional_integer_deferred(S_no_names,pfunction,1)']
    return checks


def lifecycle():
    return [check.replace('UnaryFlatFloatNumberPureTreeFiniteRedirect316', 'RepeatedFloatZeroRedirect322').replace('x316', 'x322')
            for check in unary.lifecycle('pure')]


context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
prefix = 'deferred-repeated-unary-float-number-tree-zero-full-ternary-redirect-wrapper-'
named_context = context + '-- if pfunction.ENV.NAMESPACE = $ptascii("RepeatedFloatZeroRedirect322") -- if |pfunction.SIGNATURE.PARAMETERS| = 4 '
CASES = {
    'repeated-sign-zero-raw': {'source':ROWS[prefix+'raw-tagged-results']['source'],
        'stage':context+'-- if pcallcontext.ARGC = 0 -- if |pfunction.SIGNATURE.PARAMETERS| = 2 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks':raw_checks()},
    'repeated-sign-zero-certificate': {'source':ROWS[prefix+'alias-named-reentry']['source'],
        'stage':named_context+'-- if pcallcontext.ARGC = 4 -- if S.TODO = [NAMED_PREFLIGHT porigin_function 0]',
        'checks':certificate_checks()},
    'repeated-sign-zero-private': {'source':ROWS[prefix+'alias-named-reentry']['source'],
        'stage':named_context+'-- if pcallcontext.ARGC = 1 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks':lifecycle()},
}
if __name__ == '__main__':
    protocol.run(CASES,extra_inputs=(Path(__file__),CATALOGUE,Path(prior.__file__),prior.CATALOGUE,
        Path(unary.__file__),unary.CATALOGUE),runner_flags=('--sl',))
