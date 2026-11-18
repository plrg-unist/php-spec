import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

import deferred_mixed_number_tree_infinite_full_ternary_redirect_wrapper_default_reception_protocol as prior

CATALOGUE = Path(__file__).with_name('deferred_unary_flat_float_number_tree_infinite_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
POSITIVE, NEGATIVE = prior.POSITIVE, prior.NEGATIVE
NEGZERO = 9223372036854775808
ONE = 4607182418800017408
pure_positive = prior.B('DIVIDE', f'NFLOAT {POSITIVE}', prior.F(ONE), prior.F(1))
pure_negative = prior.B('DIVIDE', f'NFLOAT {NEGATIVE}', prior.U('UM', 'NFLOAT 13830554455654793216', prior.F(ONE)), prior.F(1))
mixed_positive = prior.B('DIVIDE', f'NFLOAT {POSITIVE}', prior.I(1), prior.F(1))
mixed_negative = prior.B('DIVIDE', f'NFLOAT {NEGATIVE}', prior.U('UM', 'NINT $(-1)', prior.I(1)), prior.F(1))
TREES = {'pure': [pure_positive, pure_positive, pure_negative, pure_negative],
         'mixed': [mixed_positive, mixed_positive, mixed_negative, mixed_negative]}
CHILD_BITS = [POSITIVE, POSITIVE, NEGATIVE, NEGATIVE]
RAW_BITS = [POSITIVE, NEGATIVE, NEGATIVE, POSITIVE]
RAW_SIGNS = ['POSITIVE', 'NEGATIVE', 'POSITIVE', 'NEGATIVE']
BASE = prior.BASE


def facts(kind, entries, wrapped, cached=False):
    checks = list(BASE)
    has_int = str(kind == 'mixed').lower()
    for index, raw_index, result in entries:
        expected, child_bits, sign = RAW_BITS[raw_index], CHILD_BITS[raw_index], RAW_SIGNS[raw_index]
        factor = '1' if sign == 'POSITIVE' else '$(-1)'
        received = 'PINT 0' if wrapped else result
        checks += [
            f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_default_{index}',
            f'pcpath_full_{index} = pcpath_default_{index}' + (' ++ [PCFIELD 0]' if wrapped else ''),
            f'porigin_full_{index} = PORIGIN n_unit pcpath_full_{index}',
            f'$origin_node(S.SOURCES,porigin_full_{index}) = (NExprTernary expression_cond_{index} expression_selected_{index} expression_skipped_{index} metadata_{index})',
            f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = (expression_cond_{index})',
            f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])) = (expression_selected_{index})',
            f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])) = (expression_skipped_{index})',
            f'expression_skipped_{index} = NExprConstFetch name_skipped_{index} metadata_skipped_{index}',
            f'$pfshape(expression_cond_{index}) = PFUNARY {sign} expression_child_{index}',
            f'$lossy_optional_integer_integer_literal(expression_cond_{index}) = eps',
            f'$lossy_optional_integer_float_literal(expression_cond_{index}) = eps',
            f'$lossy_optional_integer_mixed_number_tree_value(S,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = eps',
            f'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = (PFLOAT {expected})',
            f'$code_expression(pcode.EXPRESSIONS,pcpath_full_{index} ++ [PCFIELD 0]) = eps',
            f'$compiled_read(S,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_full_{index} ++ [PCFIELD 0]) = 0',
            f'$pfshape(expression_child_{index}) = PFBINARY pbin_child_{index} expression_left_{index} expression_right_{index}',
            f'pbin_child_{index} <- [ADD,SUBTRACT,MULTIPLY,DIVIDE]',
            fr'~($lossy_optional_integer_mixed_number_tree_binary(expression_left_{index}) \/ $lossy_optional_integer_mixed_number_tree_binary(expression_right_{index}))',
        ]
        nodes, number = prior.tree_checks(index, TREES[kind][raw_index], tail=(0,), expression=f'expression_child_{index}')
        checks += nodes + [
            f'{number} = NFLOAT {child_bits}',
            f'$lossy_optional_integer_mixed_number_tree_value(S,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0,PCFIELD 0])) = ((NFLOAT {child_bits},{has_int},true))',
            f'$float_decode({child_bits}) = INFINITE n_child_sign_{index}',
            f'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0,PCFIELD 0,PCFIELD 1])) = (PFLOAT 1)',
            '$float_decode(1) = FINITE 0 1 $npow2(1074)',
            '$(1 > 0)',
            f'$number_binary(MULTIPLY,{number},NINT {factor}) = NUM (NFLOAT {expected})',
            f'$lossy_optional_integer_numeric(pfunction.ENV,expression_cond_{index}) = (NFLOAT {expected})',
            f'$float_decode({expected}) = INFINITE n_sign_{index}',
            f'$lossy_optional_integer_condition(pfunction.ENV,expression_cond_{index}) = (true)',
            f'$lossy_optional_integer_phase_safe(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0]))',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0])) = (PFLOAT {expected})',
            f'$lossy_optional_integer_quiet_shape(NExprTernary expression_cond_{index} expression_selected_{index} expression_skipped_{index} metadata_{index})',
            f'$code_expression(pcode.EXPRESSIONS,pcpath_full_{index}) = ((z_{index},false))',
            f'$pool_value(S.POOLS,porigin_full_{index}) = eps',
            f'$compiled_read(S,porigin_full_{index}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_full_{index}) = 1',
            f'$compiled_redirect(S,porigin_full_{index}) = ((PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1]),expression_selected_{index},false,z_{index}))',
            f'$code_expression(pcode.EXPRESSIONS,pcpath_full_{index} ++ [PCFIELD 2]) = eps',
            f'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])) = eps',
            f'$compiled_read(S,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])) = eps',
            f'$code_name(pcode.NAMES,pcpath_full_{index} ++ [PCFIELD 2]) = eps',
            f'$call_name_count(pcode.NAMES,pcpath_full_{index} ++ [PCFIELD 2]) = 0',
            f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2]))',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0]))',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1]))',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])) = ({result})',
        ]
        for helper in ('infinite_float','computed_infinite_float','float_integer_infinite','integer_float_infinite','float_tree_infinite','mixed_number_tree_infinite','integer_tree_infinite','unary_integer_tree_infinite','finite_nonzero_float','nonzero_integer'):
            checks += [f'$lossy_optional_integer_{helper}_full_redirect(S,pfunction.ENV,porigin_full_{index}) = eps']
        checks += [
            f'$lossy_optional_integer_truthy_literal_string_full_redirect(S,porigin_full_{index}) = eps',
            f'$lossy_optional_integer_unary_float_number_tree_infinite_full_redirect(S,pfunction.ENV,porigin_full_{index}) = ((PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0]),PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])))',
            f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_full_{index}) = ((PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 0]),PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])))',
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
    namespace = "UnaryFlatFloatNumber"+kind.title()+"TreeInfiniteRedirect314"
    checks=['S.CURRENT = (pcallcontext)','pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)',
        f'pfunction.ENV.NAMESPACE = $ptascii("{namespace}")',
        '$default_cache_owner(S) = (CACHE_SHARED)']
    for index in (1,2):
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'$lossy_optional_integer_deferred(S,pfunction,{index})',
            f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT 0,CLASS PVSCALAR}}',
            f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
            f'S.STORE[n_private_{index}] = DEFINED (PINT 0)',f'~(n_private_{index} <- S.REFCELLS)',
            f'$heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
    checks += ['pdefault_2.ORIGIN = PORIGIN n_unit pcpath_negative',
        '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_negative ++ [PCFIELD 0])) = (PFLOAT 9223372036854775808)',
        'n_private_1 =/= n_private_2',
        'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_1[.VALUE = PBOOL false])]',
        '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
        '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
        'S_budget = $drive_steps(S,0)','S_budget = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        '$heap_valid($heap_graph(S))','$call_descriptors_valid(S)',
        '$default_caches_valid(S,S.DEFAULTCACHE)',
        'S_done = $drive_steps(S,3010)','S_done.COMPLETION = NORMAL',
        'S_done.CURRENT = eps','S_done.FRAMES = eps','S_done.TODO = eps']
    for index in (1,2):
        checks += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            f'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS)',
            f'$heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
    checks += ['$lookup(S_done.ENV,$ptascii("x314")) = (n_global)',
        'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
        '$heap_valid($heap_graph(S_done))','$call_descriptors_valid(S_done)',
        '$default_caches_valid(S_done,S_done.DEFAULTCACHE)']
    return checks


def raw_checks(kind):
    checks = facts(kind, [(0,0,'PINT 0'),(1,1,'PNULL')], False, True)
    child_path = prior.node_path(0, (0,0))
    poison = 'PFLOAT 4607182418800017408' if kind == 'mixed' else 'PINT 1'
    checks += [f'S_child_tag = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({child_path}) ({poison}))] ++ ppool.CONSTANTS)]]]',
        f'$pool_value(S_child_tag.POOLS,PORIGIN n_unit (pcpath_full_0 ++ [PCFIELD 0])) = (PFLOAT {POSITIVE})',
        '$lossy_optional_integer_mixed_number_tree_value(S_child_tag,PORIGIN n_unit (pcpath_full_0 ++ [PCFIELD 0,PCFIELD 0])) = eps',
        '$lossy_optional_integer_unary_float_number_tree_infinite_full_redirect(S_child_tag,pfunction.ENV,porigin_full_0) = eps',
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
        'pcpath_selected = pcpath_full ++ [PCFIELD 1]', 'pcpath_skipped = pcpath_full ++ [PCFIELD 2]']
    mutations = {
        'duplicate': 'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ [(CODEREDIRECT pcpath_full pcpath_selected false)])]]]',
        'copy': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_full pcpath_selected true)]]]]',
        'target': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_full pcpath_skipped false)]]]]',
        'owncode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_full z_1 true)] ++ pcode.EXPRESSIONS)]]]',
        'ownpool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_full (PBOOL false))] ++ ppool.CONSTANTS)]]]',
        'condsign': f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_cond (PFLOAT {POSITIVE}))] ++ ppool.CONSTANTS)]]]',
    }
    for serial,tail in enumerate([(), (0,), (0,0), (0,0,0), (0,1)]):
        path = prior.node_path(1, tail)
        mutations[f'nodepool{serial}'] = f'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({path}) (PINT 7))] ++ ppool.CONSTANTS)]]]'
        mutations[f'nodecode{serial}'] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path}) z_1 false)] ++ pcode.EXPRESSIONS)]]]'
        mutations[f'noderead{serial}'] = f'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR ({path}) z_1 true)] ++ pcode.EXPRESSIONS)]]]'
        mutations[f'noderedirect{serial}'] = f'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT ({path}) pcpath_selected false)] ++ pcode.REDIRECTS)]]]'
        mutations[f'nodesource{serial}'] = f'S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE ({path}) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]'
    for label,expression in mutations.items():
        checks += [f'S_{label} = {expression}',
            f'$lossy_optional_integer_unary_float_number_tree_infinite_full_redirect(S_{label},pfunction.ENV,porigin_full) = eps',
            f'~$lossy_optional_integer_deferred(S_{label},pfunction,1)']
    checks += ['S_no_names = S[.CODE = [pcode[.NAMES = eps]]]',
        '~$lossy_optional_integer_deferred_bindings(S_no_names,pfunction.ENV,pdefault_1.ORIGIN)',
        '~$lossy_optional_integer_deferred(S_no_names,pfunction,1)']
    return checks


CASES = {}
for kind in ('pure','mixed'):
    prefix = 'deferred-unary-flat-float-number-tree-infinite-full-ternary-redirect-wrapper-' + kind + '-'
    context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
        '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
    named_context = context + '-- if pfunction.ENV.NAMESPACE = $ptascii("UnaryFlatFloatNumber'+kind.title()+'TreeInfiniteRedirect314") -- if |pfunction.SIGNATURE.PARAMETERS| = 4 '
    CASES[kind+'-unary-flat-float-tree-raw'] = {
        'source': ROWS[prefix+'raw-tagged-results']['source'],
        'stage': context+'-- if pcallcontext.ARGC = 0 -- if |pfunction.SIGNATURE.PARAMETERS| = 2 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks': raw_checks(kind),
    }
    CASES[kind+'-unary-flat-float-tree-certificate'] = {
        'source': ROWS[prefix+'alias-named-reentry']['source'],
        'stage': named_context+'-- if pcallcontext.ARGC = 4 -- if S.TODO = [NAMED_PREFLIGHT porigin_function 0]',
        'checks': certificate_checks(kind),
    }
    CASES[kind+'-unary-flat-float-tree-private'] = {
        'source': ROWS[prefix+'alias-named-reentry']['source'],
        'stage': named_context+'-- if pcallcontext.ARGC = 1 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks': lifecycle(kind),
    }
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE, Path(prior.__file__), prior.CATALOGUE), runner_flags=('--sl',))
