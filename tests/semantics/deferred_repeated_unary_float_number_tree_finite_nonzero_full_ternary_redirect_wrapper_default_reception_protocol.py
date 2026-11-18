import hashlib
import closure_call_protocol as protocol
import deferred_float_number_tree_finite_nonzero_full_ternary_redirect_wrapper_default_reception_protocol as previous
import json
from pathlib import Path

import deferred_mixed_number_tree_infinite_full_ternary_redirect_wrapper_default_reception_protocol as prior

CATALOGUE = Path(__file__).with_name('deferred_repeated_unary_float_number_tree_finite_nonzero_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
BASE = prior.BASE
POSITIVE, NEGATIVE = 4607182418800017408, 13830554455654793216
MIXED_POSITIVE, MIXED_NEGATIVE = 4611686018427387904, 13835058055282163712
ZERO = prior.U('UP', 'NFLOAT 9223372036854775808', prior.U('UM', 'NFLOAT 9223372036854775808', prior.F(0)))
PURE = [prior.B('ADD', f'NFLOAT {POSITIVE}', prior.F(POSITIVE), ZERO),
        prior.B('ADD', f'NFLOAT {NEGATIVE}', prior.U('UM', f'NFLOAT {NEGATIVE}', prior.F(POSITIVE)), ZERO)]
MIXED = [prior.B('ADD', f'NFLOAT {MIXED_POSITIVE}', prior.I(2), ZERO),
         prior.B('ADD', f'NFLOAT {MIXED_NEGATIVE}', prior.U('UM', 'NINT $(-2)', prior.I(2)), ZERO)]
TREES = {'pure': [PURE[0], PURE[1], PURE[1], PURE[0]], 'mixed': [MIXED[0], MIXED[1], MIXED[1], MIXED[0]]}
RAW_BITS = {'pure': [POSITIVE, NEGATIVE, NEGATIVE, POSITIVE], 'mixed': [MIXED_POSITIVE, MIXED_NEGATIVE, MIXED_NEGATIVE, MIXED_POSITIVE]}
SIGNS = [('-', '-'), ('+', '+'), ('-', '+', '-'), ('+', '-', '-')]
SIGNBIT = 9223372036854775808
VALUE = '$lossy_optional_integer_repeated_unary_finite_float_tree_value'
ROOT = '$lossy_optional_integer_repeated_unary_float_number_tree_finite_nonzero_full_redirect'


def origin(index, tail=()):
    return f'PORIGIN n_unit ({prior.node_path(index, tail)})'


def facts(kind, entries, wrapped, cached=False):
    checks = list(BASE)
    for index, raw_index, result in entries:
        signs = SIGNS[raw_index]
        received = 'PINT 0' if wrapped else result
        bits = RAW_BITS[kind][raw_index]
        checks += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_default_{index}',
            f'pcpath_full_{index} = pcpath_default_{index}' + (' ++ [PCFIELD 0]' if wrapped else ''),
            f'porigin_full_{index} = PORIGIN n_unit pcpath_full_{index}',
            f'$origin_node(S.SOURCES,porigin_full_{index}) = (NExprTernary expression_cond_{index} expression_selected_{index} expression_skipped_{index} metadata_{index})',
            f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])) = (expression_selected_{index})',
            f'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2])) = (expression_skipped_{index})',
            f'expression_skipped_{index} = NExprConstFetch name_skipped_{index} metadata_skipped_{index}']
        expression = f'expression_cond_{index}'
        for depth, sign in enumerate(signs):
            tail = (0,) * depth
            own = origin(index, tail)
            child = f'expression_sign_{index}_{depth}'
            child_bits = bits ^ (SIGNBIT if sign == '-' else 0)
            checks += [f'$origin_node(S.SOURCES,{own}) = ({expression})',
                f'{expression} = NExprUnary' + ('Minus' if sign == '-' else 'Plus') + f' {child} metadata_sign_{index}_{depth}',
                f'$pool_value(S.POOLS,{own}) = (PFLOAT {bits})',
                f'$code_expression(pcode.EXPRESSIONS,{prior.node_path(index,tail)}) = eps',
                f'$compiled_read(S,{own}) = eps',
                f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,{prior.node_path(index,tail)}) = 0',
                f'$lossy_optional_integer_mixed_number_tree_value(S,{own}) = eps',
                f'{VALUE}(S,{own}) = (({bits},{len(signs)-depth}))',
                f'$number_binary(MULTIPLY,NINT ' + ('$(-1)' if sign == '-' else '1') + f',NFLOAT {child_bits}) = NUM (NFLOAT {bits})']
            expression, bits = child, child_bits
        nodes, number = prior.tree_checks(index,TREES[kind][raw_index],tail=(0,)*len(signs),expression=expression)
        checks += nodes + [f'{number} = NFLOAT {bits}',
            f'{VALUE}(S,{origin(index,(0,)*len(signs))}) = (({bits},0))',
            f'$lossy_optional_integer_mixed_number_tree_value(S,{origin(index,(0,)*len(signs))}) = ((NFLOAT {bits},{str(kind=="mixed").lower()},true))',
            f'$lossy_optional_integer_numeric(pfunction.ENV,expression_cond_{index}) = (NFLOAT {RAW_BITS[kind][raw_index]})',
            f'$float_decode({bits}) = FINITE n_sign_{index} n_numerator_{index} n_denominator_{index}',
            f'n_numerator_{index} =/= 0',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,{origin(index)})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,{origin(index)}) = eps',
            f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,{origin(index)})',
            f'$code_expression(pcode.EXPRESSIONS,pcpath_full_{index}) = ((z_{index},false))',
            f'$pool_value(S.POOLS,porigin_full_{index}) = eps',
            f'$compiled_read(S,porigin_full_{index}) = eps',
            f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_full_{index}) = 1',
            f'$compiled_redirect(S,porigin_full_{index}) = ((PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1]),expression_selected_{index},false,z_{index}))',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])) = ({result})',
            f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 2]))']
        for helper in ('unary_float_number_tree_finite_nonzero','float_number_tree_finite_nonzero','finite_nonzero_float','unary_float_number_tree_infinite','mixed_number_tree_infinite','float_tree_infinite'):
            checks += [f'$lossy_optional_integer_{helper}_full_redirect(S,pfunction.ENV,porigin_full_{index}) = eps']
        checks += [f'{ROOT}(S,pfunction.ENV,porigin_full_{index}) = (({origin(index)},PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])))',
            f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_full_{index}) = (({origin(index)},PORIGIN n_unit (pcpath_full_{index} ++ [PCFIELD 1])))',
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


def lifecycle(kind):
    return [check.replace("317", "318") for check in previous.lifecycle(kind)]


def raw_checks(kind):
    checks = facts(kind, [(0,0,'PINT 0'),(1,1,'PNULL')], False, True)
    child_path = prior.node_path(0, (0,0,0))
    poison = 'PFLOAT 4607182418800017408' if kind == 'mixed' else 'PINT 1'
    checks += [f'S_child_tag = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT ({child_path}) ({poison}))] ++ ppool.CONSTANTS)]]]',
        f'$pool_value(S_child_tag.POOLS,PORIGIN n_unit (pcpath_full_0 ++ [PCFIELD 0])) = (PFLOAT {RAW_BITS[kind][0]})',
        f'{VALUE}(S_child_tag,PORIGIN n_unit (pcpath_full_0 ++ [PCFIELD 0])) = eps',
        '$lossy_optional_integer_repeated_unary_float_number_tree_finite_nonzero_full_redirect(S_child_tag,pfunction.ENV,porigin_full_0) = eps',
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
    def paths(tree, tail=()):
        return [tail] + [path for index,child in enumerate(tree[2:]) for path in paths(child, tail+(index,))]
    zero_tail = (0,0,0,1)
    phase_reads = set()
    allpaths = [(),(0,),(0,0)] + [(0,0,0)+tail for tail in paths(TREES[kind][2])]
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
            f'$lossy_optional_integer_repeated_unary_float_number_tree_finite_nonzero_full_redirect(S_{label},pfunction.ENV,porigin_full) = eps']
        if label in phase_reads:
            checks += [f'$lossy_optional_integer_phase_safe(S_{label},pfunction.ENV,PORIGIN n_unit pcpath_cond)',
                f'$lossy_optional_integer_deferred_value_at(S_{label},pfunction.ENV,PORIGIN n_unit pcpath_cond) = (PFLOAT {RAW_BITS[kind][2]})']
            if label == 'noderead0':
                checks += [f'$lossy_optional_integer_finite_nonzero_float_full_redirect(S_{label},pfunction.ENV,porigin_full) = eps',
                    f'$lossy_optional_integer_pruned_ternary(S_{label},pfunction.ENV,porigin_full) = eps',
                    f'~$lossy_optional_integer_deferred_bindings(S_{label},pfunction.ENV,pdefault_1.ORIGIN)',
                    f'~$lossy_optional_integer_deferred(S_{label},pfunction,1)']
            else:
                checks += [f'$lossy_optional_integer_finite_nonzero_float_full_redirect(S_{label},pfunction.ENV,porigin_full) = ((PORIGIN n_unit pcpath_cond,PORIGIN n_unit pcpath_selected))',
                    f'$lossy_optional_integer_deferred(S_{label},pfunction,1)']
        else:
            checks += [f'~$lossy_optional_integer_deferred(S_{label},pfunction,1)']
    checks += ['S_no_names = S[.CODE = [pcode[.NAMES = eps]]]',
        '~$lossy_optional_integer_deferred_bindings(S_no_names,pfunction.ENV,pdefault_1.ORIGIN)',
        '~$lossy_optional_integer_deferred(S_no_names,pfunction,1)']
    return checks + controls(kind)


def ast(tree):
    tag, number = tree[:2]
    if tag == 'I': return f'NScalarInt (INTEGER {number[5:]}) eps'
    if tag == 'F': return f'NScalarFloat (FLOAT "{int(number[7:]):016x}") eps'
    if tag in ('UP','UM'):
        return 'NExprUnary' + ('Plus' if tag == 'UP' else 'Minus') + f' ({ast(tree[2])}) eps'
    name = {'ADD':'Plus','SUBTRACT':'Minus','MULTIPLY':'Mul','DIVIDE':'Div','POWER':'Pow'}[tag]
    return f'NExprBinaryOp{name} ({ast(tree[2])}) ({ast(tree[3])}) eps'


def walk(tree, tail=()):
    return [(tail,tree)] + [(path,node) for index,child in enumerate(tree[2:]) for path,node in walk(child,tail+(index,))]


def wrap(tree, signs):
    for sign in reversed(signs):
        bits = int(tree[1][7:]) ^ (SIGNBIT if sign == '-' else 0)
        tree = prior.U('UM' if sign == '-' else 'UP',f'NFLOAT {bits}',tree)
    return tree


def controls(kind):
    base = TREES[kind][0]
    bits = RAW_BITS[kind][0]
    proper = prior.B('ADD',f'NFLOAT {4611686018427387904 if kind=="pure" else 4613937818241073152}',base,prior.F(POSITIVE))
    safe = prior.B('ADD',f'NFLOAT {POSITIVE}',prior.F(POSITIVE),prior.F(0))
    infinite = prior.B('ADD','NFLOAT 9218868437227405312',prior.F(9218868437227405312),ZERO)
    zero = prior.B('MULTIPLY',f'NFLOAT {SIGNBIT}',prior.F(POSITIVE),ZERO)
    nan = prior.B('ADD','NFLOAT 9221120237041090560',prior.F(9221120237041090560),ZERO)
    division = prior.B('DIVIDE',f'NFLOAT {POSITIVE}',prior.F(POSITIVE),prior.F(0))
    power = prior.B('POWER',f'NFLOAT {POSITIVE}',prior.F(POSITIVE),prior.F(POSITIVE))
    nested = prior.B('ADD',proper[1],prior.U('UP',base[1],base),prior.F(POSITIVE))
    integer = prior.U('UP',f'NFLOAT {MIXED_POSITIVE}',prior.U('UP',f'NFLOAT {MIXED_POSITIVE}',prior.B('ADD','NINT 2',prior.I(1),prior.I(1))))
    cases = [('direct',base,(bits,0),False), ('one',wrap(base,('+',)),(bits,1),False),
        ('four',wrap(base,('+','-','-','+')),(bits,4),True),
        ('proper',wrap(proper,('+','+')),(int(proper[1][7:]),2),True),
        ('safe',wrap(safe,('+','+')),(POSITIVE,2),False),
        ('infinite',wrap(infinite,('+','+')),None,False), ('zero',wrap(zero,('+','+')),None,False),
        ('nan',wrap(nan,('+','+')),None,False), ('divzero',wrap(division,('+','+')),None,False),
        ('power',wrap(power,('+','+')),None,False), ('nested',wrap(nested,('+','+')),None,False),
        ('integer',integer,None,False)]
    checks = []
    for label,tree,receipt,accepted in cases:
        constants = [f'(PCONSTANT ({prior.node_path(1,tail)}) ({node[1].replace("NFLOAT","PFLOAT").replace("NINT","PINT")}))' for tail,node in walk(tree)]
        checks += [f'expression_{label} = {ast(tree)}',
            f'S_source_{label} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_full (NExprTernary expression_{label} expression_selected_1 expression_skipped_1 metadata_1)),(PCOCCURRENCE pcpath_cond expression_{label})] ++ $pcwalk($pcchildren(expression_{label},pcpath_cond)) ++ pcunit.OCCURRENCES)]]]',
            f'S_{label} = S_source_{label}[.POOLS = [ppool[.CONSTANTS = ([' + ','.join(constants) + '] ++ ppool.CONSTANTS)]]]',
            f'{VALUE}(S_{label},PORIGIN n_unit pcpath_cond) = ' + ('eps' if receipt is None else f'(({receipt[0]},{receipt[1]}))'),
            f'{ROOT}(S_{label},pfunction.ENV,porigin_full) = ' + ('((PORIGIN n_unit pcpath_cond,PORIGIN n_unit pcpath_selected))' if accepted else 'eps')]
        if label in ('direct','one','safe'):
            old = {'direct':'float_number_tree_finite_nonzero','one':'unary_float_number_tree_finite_nonzero','safe':'finite_nonzero_float'}[label]
            checks += [f'$lossy_optional_integer_{old}_full_redirect(S_{label},pfunction.ENV,porigin_full) = ((PORIGIN n_unit pcpath_cond,PORIGIN n_unit pcpath_selected))']
        if label == 'safe':
            checks += ['$lossy_optional_integer_phase_safe(S_safe,pfunction.ENV,PORIGIN n_unit pcpath_cond)',
                f'$lossy_optional_integer_deferred_value_at(S_safe,pfunction.ENV,PORIGIN n_unit pcpath_cond) = (PFLOAT {POSITIVE})']
    return checks


CASES = {}
for kind in ('pure','mixed'):
    prefix = 'deferred-repeated-unary-float-number-tree-finite-nonzero-full-ternary-redirect-wrapper-' + kind + '-'
    context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin_function '
        '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
    named_context = context + '-- if pfunction.ENV.NAMESPACE = $ptascii("FloatNumber'+kind.title()+'TreeFiniteRedirect318") -- if |pfunction.SIGNATURE.PARAMETERS| = 4 '
    CASES[kind+'-repeated-finite-tree-raw'] = {'source':ROWS[prefix+'raw-tagged-results']['source'],
        'stage':context+'-- if pcallcontext.ARGC = 0 -- if |pfunction.SIGNATURE.PARAMETERS| = 2 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks':raw_checks(kind)}
    CASES[kind+'-repeated-finite-tree-certificate'] = {'source':ROWS[prefix+'alias-named-reentry']['source'],
        'stage':named_context+'-- if pcallcontext.ARGC = 4 -- if S.TODO = [NAMED_PREFLIGHT porigin_function 0]',
        'checks':certificate_checks(kind)}
    CASES[kind+'-repeated-finite-tree-private'] = {'source':ROWS[prefix+'alias-named-reentry']['source'],
        'stage':named_context+'-- if pcallcontext.ARGC = 1 -- if S.TODO = $function_tasks(S,pfunction)',
        'checks':lifecycle(kind)}
if __name__ == '__main__':
    protocol.run(CASES,extra_inputs=(Path(__file__),CATALOGUE,Path(prior.__file__),prior.CATALOGUE,
        Path(previous.__file__),previous.CATALOGUE,Path(previous.unary.__file__),previous.unary.CATALOGUE),runner_flags=('--sl',))
