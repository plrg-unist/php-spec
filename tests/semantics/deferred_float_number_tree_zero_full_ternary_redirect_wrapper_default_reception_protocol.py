"""Exact zero-condition FIELD2 receipts, private caches, malformed facts and resumption."""
import hashlib
import json
from pathlib import Path

import deferred_mixed_number_tree_infinite_full_ternary_redirect_wrapper_default_reception_protocol as prior
import deferred_unary_flat_float_number_tree_finite_nonzero_full_ternary_redirect_wrapper_default_reception_protocol as unary

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_float_number_tree_zero_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
NEGATIVE = 13830554455654793216
NEGZERO = 9223372036854775808
ONE = 4607182418800017408
zero = prior.U('UP', f'NFLOAT {NEGZERO}', prior.U('UM', f'NFLOAT {NEGZERO}', prior.F(0)))
pure_positive = prior.B('MULTIPLY', f'NFLOAT {NEGZERO}', prior.F(ONE), zero)
pure_negative = prior.B('MULTIPLY', 'NFLOAT 0', prior.U('UM', f'NFLOAT {NEGATIVE}', prior.F(ONE)), zero)
mixed_positive = prior.B('MULTIPLY', f'NFLOAT {NEGZERO}', prior.I(1), zero)
mixed_negative = prior.B('MULTIPLY', 'NFLOAT 0', prior.U('UM', 'NINT $(-1)', prior.I(1)), zero)
TREES = {'pure': [pure_positive, pure_negative, pure_negative, pure_positive],
         'mixed': [mixed_positive, mixed_negative, mixed_negative, mixed_positive]}
RAW_BITS = {'pure': [NEGZERO,0,0,NEGZERO], 'mixed': [NEGZERO,0,0,NEGZERO]}
BASE = prior.BASE


def facts(kind, entries, wrapped, cached=False):
    checks = list(BASE)
    has_int = str(kind == 'mixed').lower()
    for index, raw_index, result in entries:
        expected = RAW_BITS[kind][raw_index]
        received = 'PINT 0' if wrapped else result
        checks += [
            f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_default_{index}',
            f'pcpath_full_{index} = pcpath_default_{index}' + (' ++ [PCFIELD 0]' if wrapped else ''),
            f'porigin_full_{index} = PORIGIN n_unit pcpath_full_{index}',
            f'$origin_node(S.SOURCES,porigin_full_{index}) = (NExprTernary expression_cond_{index} expression_skipped_{index} expression_selected_{index} metadata_{index})',
            f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = (expression_cond_{index})',
            f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])) = (expression_selected_{index})',
            f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])) = (expression_skipped_{index})',
            f'expression_skipped_{index} = NExprConstFetch name_skipped_{index} metadata_skipped_{index}',
            f'$pfshape(expression_cond_{index}) = PFBINARY pbin_cond_{index} expression_left_{index} expression_right_{index}',
            f'pbin_cond_{index} <- [ADD,SUBTRACT,MULTIPLY,DIVIDE]',
            f'$lossy_optional_integer_integer_literal(expression_cond_{index}) = eps',
            f'$lossy_optional_integer_float_literal(expression_cond_{index}) = eps',
            f'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = (PFLOAT {expected})',
            f'$code_expression(pcode.EXPRESSIONS,pcpath_full_{index} ++ [PCFIELD 0]) = eps',
            f'$compiled_read(S,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_full_{index} ++ [PCFIELD 0]) = 0',
        ]
        nodes, number = prior.tree_checks(index, TREES[kind][raw_index], tail=(), expression=f'expression_cond_{index}')
        checks += nodes + [
            f'{number} = NFLOAT {expected}',
            f'$lossy_optional_integer_mixed_number_tree_value(S,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = ((NFLOAT {expected},{has_int},true))',
            f'$lossy_optional_integer_numeric(pfunction.ENV,expression_cond_{index}) = (NFLOAT {expected})',
            f'$float_decode({expected}) = FINITE n_sign_{index} n_num_{index} n_den_{index}',
            f'n_num_{index} = 0',
            f'$lossy_optional_integer_condition(pfunction.ENV,expression_cond_{index}) = (false)',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0]))',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = eps',
            f'$lossy_optional_integer_quiet_shape(NExprTernary expression_cond_{index} expression_skipped_{index} expression_selected_{index} metadata_{index})',
            f'$code_expression(pcode.EXPRESSIONS,pcpath_full_{index}) = ((z_{index},false))',
            f'$pool_value(S.POOLS,porigin_full_{index}) = eps',
            f'$compiled_read(S,porigin_full_{index}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_full_{index}) = 1',
            f'$compiled_redirect(S,porigin_full_{index}) = ((PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2]),expression_selected_{index},false,z_{index}))',
            f'$code_expression(pcode.EXPRESSIONS,pcpath_full_{index} ++ [PCFIELD 1]) = eps',
            f'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])) = eps',
            f'$compiled_read(S,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])) = eps',
            f'$code_name(pcode.NAMES,pcpath_full_{index} ++ [PCFIELD 1]) = eps',
            f'$call_name_count(pcode.NAMES,pcpath_full_{index} ++ [PCFIELD 1]) = 0',
            f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1]))',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0]))',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2]))',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])) = ({result})',
        ]
        zero_tail = (1,)
        zero_path = prior.node_path(index,zero_tail)
        checks += [f'$origin_node(S.SOURCES,PORIGIN n_unit ({zero_path})) = (NExprUnaryPlus expression_negzero_{index} metadata_zero_{index})',
            f'$lossy_optional_integer_numeric(pfunction.ENV,expression_negzero_{index}) = (NFLOAT {NEGZERO})',
            f'$lossy_optional_integer_phase_sensitive(pfunction.ENV,NExprUnaryPlus expression_negzero_{index} metadata_zero_{index})',
            f'$pool_value(S.POOLS,PORIGIN n_unit ({zero_path})) = (PFLOAT {NEGZERO})',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,PORIGIN n_unit ({zero_path}))']
        for helper in ('falsey','float_number_tree_finite_nonzero','repeated_unary_float_number_tree_finite_nonzero','infinite_float','computed_infinite_float','float_integer_infinite','integer_float_infinite','float_tree_infinite','mixed_number_tree_infinite','integer_tree_infinite','unary_integer_tree_infinite','unary_float_number_tree_infinite','unary_float_number_tree_finite_nonzero','finite_nonzero_float','nonzero_integer'):
            checks += [f'$lossy_optional_integer_{helper}_full_redirect(S,pfunction.ENV,porigin_full_{index}) = eps']
        checks += [
            f'$lossy_optional_integer_truthy_literal_string_full_redirect(S,porigin_full_{index}) = eps',
            f'$lossy_optional_integer_float_number_tree_zero_full_redirect(S,pfunction.ENV,porigin_full_{index}) = ((PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0]),PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])))',
            f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_full_{index}) = ((PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0]),PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])))',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_full_{index})',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_full_{index})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_full_{index}) = ({result})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({received})',
            f'$lossy_optional_integer_deferred(S,pfunction,{index})',
            f'$default_current_cache(S,pdefault_{index}.ORIGIN) = eps',
        ]
        if cached:
            checks.remove(f'$default_current_cache(S,pdefault_{index}.ORIGIN) = eps')
            checks += [f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {received},CLASS PVSCALAR}}',
                f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
                f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
                f'S.STORE[n_cell_{index}] = DEFINED ({received})',f'~(n_cell_{index} <- S.REFCELLS)',
                f'$heap_owners($heap_graph(S),HCELL n_cell_{index}) = 1']
    return checks


def lifecycle(kind):
    return [check.replace('UnaryFlatFloatNumber', 'FloatNumber').replace('TreeFiniteRedirect316', 'TreeZeroRedirect319').replace('x316', 'x319')
            for check in unary.lifecycle(kind)]


def raw_checks(kind):
    checks = facts(kind, [(0,0,'PINT 0'),(1,1,'PNULL')], False, True)
    child_path = prior.node_path(0, (0,))
    poison = 'PFLOAT 4607182418800017408' if kind == 'mixed' else 'PINT 1'
    checks += [f'S_child_tag = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({child_path}) ({poison}))] ++ ppool.CONSTANTS)]]]',
        f'$pool_value(S_child_tag.POOLS,PORIGIN n_unit (pcpath_full_0 ++ [PCFIELD 0])) = (PFLOAT {RAW_BITS[kind][0]})',
        '$lossy_optional_integer_mixed_number_tree_value(S_child_tag,PORIGIN n_unit (pcpath_full_0 ++ [PCFIELD 0])) = eps',
        '$lossy_optional_integer_float_number_tree_zero_full_redirect(S_child_tag,pfunction.ENV,porigin_full_0) = eps',
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


def certificate_checks(kind):
    checks = facts(kind, [(1,2,'PBOOL false'),(2,3,'PFLOAT 9223372036854775808')], True)
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
        'condsign': f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_cond (PFLOAT {NEGZERO}))] ++ ppool.CONSTANTS)]]]',
    }
    def paths(tree, tail=()):
        return [tail] + [path for index,child in enumerate(tree[2:]) for path in paths(child, tail+(index,))]
    zero_tail = (1,)
    phase_reads = set()
    for serial,tail in enumerate(paths(TREES[kind][2])):
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
            f'$lossy_optional_integer_float_number_tree_zero_full_redirect(S_{label},pfunction.ENV,porigin_full) = eps']
        if label in phase_reads:
            checks += [f'$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,PORIGIN n_unit pcpath_cond)',
                f'$lossy_optional_integer_deferred_value_at(S_{label},pfunction.ENV,PORIGIN n_unit pcpath_cond) = (PFLOAT {RAW_BITS[kind][2]})']
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


CASES = {}
for kind in ('pure','mixed'):
    prefix = 'deferred-float-number-tree-zero-full-ternary-redirect-wrapper-' + kind + '-'
    context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
        '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
    named_context = context + '-- if pfunction.ENV.NAMESPACE = $ptascii("FloatNumber'+kind.title()+'TreeZeroRedirect319") -- if |pfunction.SIGNATURE.PARAMETERS| = 4 '
    CASES[kind+'-direct-zero-float-tree-raw'] = {
        'source': ROWS[prefix+'raw-tagged-results']['source'],
        'stage': context+'-- if pcallcontext.ARGC = 0 -- if |pfunction.SIGNATURE.PARAMETERS| = 2 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks': raw_checks(kind),
    }
    CASES[kind+'-direct-zero-float-tree-certificate'] = {
        'source': ROWS[prefix+'alias-named-reentry']['source'],
        'stage': named_context+'-- if pcallcontext.ARGC = 4 -- if S.TODO = [NAMED_PREFLIGHT porigin_function 0]',
        'checks': certificate_checks(kind),
    }
    CASES[kind+'-direct-zero-float-tree-private'] = {
        'source': ROWS[prefix+'alias-named-reentry']['source'],
        'stage': named_context+'-- if pcallcontext.ARGC = 1 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks': lifecycle(kind),
    }
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE, Path(prior.__file__), prior.CATALOGUE, Path(unary.__file__), unary.CATALOGUE), runner_flags=('--sl',))
