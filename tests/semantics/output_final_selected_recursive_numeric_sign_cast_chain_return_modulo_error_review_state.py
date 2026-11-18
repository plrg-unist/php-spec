#!/usr/bin/env python3
"""Independent recursive-sign authority, type and retirement controls."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_state as current
import output_final_selected_recursive_numeric_sign_cast_chain_return_modulo_error_sources as sources

runner = current.runner
CASES = {name: sources.CASES['native-selected-recursive-numeric-sign-cast-chain-return-modulo-error-' + name]
         for name in ['warning-left-constant-folded-int-double',
                      'warning-left-constant-emitted-not-int',
                      'warning-right-cv-pair-emitted-float-zero']}
PREFIX = current.PREFIX + r'''
dec $or131_drop(pcoccurrence*, pcpath) : pcoccurrence*
def $or131_drop(eps, pcpath) = eps
def $or131_drop((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*, pcpath) = $or131_drop(pcoccurrence*, pcpath)
def $or131_drop((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*, pcpath) = (PCOCCURRENCE pcpath_other pcnode) :: $or131_drop(pcoccurrence*, pcpath)
  -- if pcpath_other =/= pcpath
dec $or131_fact_at(pconstant, pcpath) : bool
def $or131_fact_at(PCONSTANT pcpath_fact pvalue, pcpath) = (pcpath_fact = pcpath)
def $or131_fact_at(pconstant, pcpath) = false -- otherwise
dec $or131_fact_drop(pconstant*, pcpath) : pconstant*
def $or131_fact_drop(eps, pcpath) = eps
def $or131_fact_drop(pconstant :: pconstant_tail*, pcpath) = $or131_fact_drop(pconstant_tail*, pcpath)
  -- if $or131_fact_at(pconstant, pcpath)
def $or131_fact_drop(pconstant :: pconstant_tail*, pcpath) = pconstant :: $or131_fact_drop(pconstant_tail*, pcpath)
  -- if ~$or131_fact_at(pconstant, pcpath)
'''


def value(state, expression, origin='porigin_sign', function='pfunction_handler'):
    return '$ob_object_cast_chain_value(' + state + ', ' + function + ', ' + origin + ', ' + expression + ')'


def changed(rows, codes, constants):
    entries = ', '.join('CODEEXPR ' + path + ' (' + line + ') ' + flag for path, line, flag in codes)
    function = 'pfunction_handler[.CODE.EXPRESSIONS = [' + entries + '] ++ pfunction_handler.CODE.EXPRESSIONS]'
    facts = ', '.join('PCONSTANT ' + path + ' (' + result + ')' for path, result in constants)
    state = (control.source_state(rows) + '[.CODE = ' + function + '.CODE :: S.CODE]'
             '[.POOLS = ppool_handler[.CONSTANTS = [' + facts + '] ++ ppool_handler.CONSTANTS] :: S.POOLS]')
    return state, function


def raw_sign(kind, leaf, raw, result, name=None):
    expression = kind + ' (' + leaf + ') metadata_sign'
    rows = [('pcpath_sign', expression), ('pcpath_child_3', leaf)]
    if name is not None:
        rows += [('(pcpath_child_3 ++ [PCFIELD 0])', name)]
    state, function = changed(rows,
        [('pcpath_sign', '$expression_line(' + leaf + ')', 'true'),
         ('pcpath_child_3', '$source_line(metadata_child_3)', 'true')],
        [('pcpath_child_3', raw), ('pcpath_sign', result)])
    return state, expression, function


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    expression, result = current.expression(name, 2), current.nodes(name)[2][3]
    checks += [
        ('the actual numeric sign has its exact scalar tag and no owner',
         value('S', expression) + ' = (' + result + r') /\ $value_nodes(' + result + ') = eps'),
        ('a preset numeric result cannot replace NORMAL source authority',
         value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps'),
        ('the recursive handler retains its own CODE unit and BODY',
         '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + r' /\ ~' +
         control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for index, (_, _, _, typed, folded) in enumerate(current.nodes(name)):
        slot = current.slot(index)
        flag = 'true' if folded else 'false'
        for label, line, changed_flag in [('flag', 'z_' + slot, 'false' if folded else 'true'),
                                          ('line', '$(z_' + slot + ' + 1)', flag)]:
            checks += [(slot + ' exact CODE ' + label + ' is required through the whole tail',
                        '~' + control.tail(function=control.code_function('pcpath_' + slot, line, changed_flag)))]
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or131_drop(pcunit_handler.OCCURRENCES, pcpath_' + slot + ')] :: S.SOURCES]')
        checks += [('removing only ' + slot + ' source refuses the entire tail', '~' + control.tail(state))]
        if folded:
            state = ('S[.POOLS = ppool_handler[.CONSTANTS = '
                     '$or131_fact_drop(ppool_handler.CONSTANTS, pcpath_' + slot + ')] :: S.POOLS]')
            checks += [(slot + ' folded fact cannot be replaced by the other intact descendants', '~' + control.tail(state)),
                       (slot + ' raw fact keeps its exact type',
                        '~' + control.tail(control.pool_state('pcpath_' + slot, 'POBJECT 0')))]
    if current.nodes(name)[2][4]:
        checks += [('a folded sign keeps its own value independently of valid child facts',
                    value(control.pool_state('pcpath_sign', 'PINT 8'), expression) + ' = eps')]
        global_code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_sign z_sign false) :: '
                       'pfunction_handler.CODE.EXPRESSIONS]')
        checks += [('an unread folded pool cannot replace the genuine global CODE flag',
                    value('S[.CODE = ' + global_code + ' :: S.CODE]', expression) + ' = eps')]
    else:
        checks += [('an emitted sign ignores an unread forged pool without becoming folded',
                    r'$compiled_read(S, porigin_sign) = eps /\ ' +
                    value(control.pool_state('pcpath_sign', 'POBJECT 0'), expression) + ' = (' + result + ')')]
        global_code = ('pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_sign z_sign true) :: '
                       'pfunction_handler.CODE.EXPRESSIONS]')
        state = control.pool_state('pcpath_sign', result) + '[.CODE = ' + global_code + ' :: S.CODE]'
        checks += [('an exact forged global read cannot replace emitted sign authority',
                    '$compiled_read(' + state + ', porigin_sign) = (' + result + r') /\ ' +
                    value(state, expression) + ' = eps')]
    if current.DETAILS[name][1] == 'folded-int-double':
        for kind, text, raw, signed, expected in [
                ('NExprUnaryPlus', '8000000000000000', 'PFLOAT 9223372036854775808', 'PFLOAT 9223372036854775808', True),
                ('NExprUnaryMinus', '8000000000000000', 'PFLOAT 9223372036854775808', 'PFLOAT 0', True),
                ('NExprUnaryMinus', '7ff0000000000000', 'PFLOAT 9218868437227405312', 'PFLOAT 18442240474082181120', True),
                ('NExprUnaryPlus', '7ff8abcdef012345', 'PFLOAT 9221309138007565125', 'PFLOAT 9221309138007565125', False),
                ('NExprUnaryPlus', '7ff0000000000001', 'PFLOAT 9218868437227405313', 'PFLOAT 9218868437227405313', False)]:
            leaf = 'NScalarFloat (FLOAT "' + text + '") metadata_child_3'
            state, expr, function = raw_sign(kind, leaf, raw, signed)
            checks += [('source0 sign preserves signed-zero/infinity bits while refusing either NaN class',
                        value(state, leaf, 'porigin_child_3', function) + ' = (' + raw + r') /\ ' +
                        value(state, expr, function=function) + (' = (' + signed + ')' if expected else ' = eps'))]
        leaf = 'NScalarInt (INTEGER $(-9223372036854775808)) metadata_child_3'
        state, expr, function = raw_sign('NExprUnaryMinus', leaf, 'PINT $(-9223372036854775808)', 'PFLOAT 4890909195324358656')
        checks += [('a genuine minimum INT child still cannot promote under this same-type certificate',
                    value(state, leaf, 'porigin_child_3', function) + r' = (PINT $(-9223372036854775808)) /\ ' +
                    value(state, expr, function=function) + ' = eps')]
        for keyword, raw in [('false', 'PBOOL false'), ('null', 'PNULL')]:
            payload = 'ZmFsc2U=' if keyword == 'false' else 'bnVsbA=='
            node = 'NName (BYTES "' + payload + '") metadata_child_4'
            leaf = 'NExprConstFetch (' + node + ') metadata_child_3'
            state, expr, function = raw_sign('NExprUnaryPlus', leaf, raw, 'PINT 0', name=node)
            checks += [('a certified ' + keyword + ' child enters a quiet primitive sign',
                        value(state, leaf, 'porigin_child_3', function) + ' = (' + raw + r') /\ ' +
                        value(state, expr, function=function) + ' = (PINT 0)')]
        leaf = 'NScalarString (BYTES "Nw==") metadata_child_3'
        state, expr, function = raw_sign('NExprUnaryPlus', leaf, 'PSTRING ($ptascii("7"))', 'PINT 7')
        checks += [('a genuine fully numeric STRING carrier enters a quiet primitive sign',
                    value(state, leaf, 'porigin_child_3', function) + r' = (PSTRING_CARRIER INTERNED_STRING ($ptascii("7"))) /\ ' +
                    value(state, expr, function=function) + ' = (PINT 7)')]
        raw = 'NScalarInt (INTEGER 1) metadata_child_4'
        child = 'NExprBooleanNot (' + raw + ') metadata_child_3'
        expr = 'NExprUnaryPlus (' + child + ') metadata_sign'
        state, function = changed([('pcpath_sign', expr), ('pcpath_child_3', child), ('pcpath_child_4', raw)],
            [('pcpath_sign', '$expression_line(' + child + ')', 'true'),
             ('pcpath_child_3', '$expression_line(' + raw + ')', 'true'),
             ('pcpath_child_4', '$source_line(metadata_child_4)', 'true')],
            [('pcpath_sign', 'PINT 0'), ('pcpath_child_3', 'PBOOL false'), ('pcpath_child_4', 'PINT 1')])
        checks += [('a fully certified NOT retains Boolean input to a quiet primitive sign',
                    value(state, child, 'porigin_child_3', function) + r' = (PBOOL false) /\ ' +
                    value(state, expr, function=function) + ' = (PINT 0)')]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = current.nodes(name)[1][0] + ' (' + expression + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('recursive helper composition preserves bare and single-cast handler fences',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + r' /\ ~' +
                control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('the actual numeric subtree and strict handler result survive real cell retirement',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL /\ ' +
                value('S', current.expression(name, 2)) + ' = (' + current.nodes(name)[2][3] + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
