#!/usr/bin/env python3
"""Independent compiler-folding, exact-fact and quiet NOT composition controls."""
import base64
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_certified_not_cast_chain_return_modulo_error_state as current
import output_final_selected_certified_not_cast_chain_return_modulo_error_sources as sources

runner = current.runner
CASES = {name: sources.CASES['native-selected-certified-not-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair-keyword-null',
                      'warning-deprecated-constant-float-string-truthy',
                      'warning-right-cv-pair-emitted-nested']}
PREFIX = current.PREFIX + r'''
dec $or130_drop(pcoccurrence*, pcpath) : pcoccurrence*
def $or130_drop(eps, pcpath) = eps
def $or130_drop((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*, pcpath) = pcoccurrence*
def $or130_drop((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*, pcpath) = (PCOCCURRENCE pcpath_other pcnode) :: $or130_drop(pcoccurrence*, pcpath)
  -- if pcpath_other =/= pcpath
dec $or130_fact_at(pconstant, pcpath) : bool
def $or130_fact_at(PCONSTANT pcpath_fact pvalue, pcpath) = (pcpath_fact = pcpath)
def $or130_fact_at(pconstant, pcpath) = false -- otherwise
dec $or130_fact_drop(pconstant*, pcpath) : pconstant*
def $or130_fact_drop(eps, pcpath) = eps
def $or130_fact_drop(pconstant :: pconstant_tail*, pcpath) = $or130_fact_drop(pconstant_tail*, pcpath)
  -- if $or130_fact_at(pconstant, pcpath)
def $or130_fact_drop(pconstant :: pconstant_tail*, pcpath) = pconstant :: $or130_fact_drop(pconstant_tail*, pcpath)
  -- if ~$or130_fact_at(pconstant, pcpath)
'''


def value(state, expression, origin='porigin_not', function='pfunction_handler'):
    return '$ob_object_cast_chain_value(' + state + ', ' + function + ', ' + origin + ', ' + expression + ')'


def code(rows):
    entries = ', '.join('CODEEXPR ' + path + ' (' + line + ') ' + flag for path, line, flag in rows)
    return 'pfunction_handler[.CODE.EXPRESSIONS = [' + entries + '] ++ pfunction_handler.CODE.EXPRESSIONS]'


def changed(rows, constants, function):
    facts = ', '.join('PCONSTANT ' + path + ' (' + result + ')' for path, result in constants)
    return (control.source_state(rows) + '[.CODE = ' + function + '.CODE :: S.CODE]'
            '[.POOLS = ppool_handler[.CONSTANTS = [' + facts +
            '] ++ ppool_handler.CONSTANTS] :: S.POOLS]')


def raw_not(leaf, raw, result, folded=True, name_node=None):
    expression = 'NExprBooleanNot (' + leaf + ') metadata_not'
    rows = [('pcpath_not', expression), ('pcpath_child_3', leaf)]
    if name_node is not None:
        rows += [('(pcpath_child_3 ++ [PCFIELD 0])', name_node)]
    function = code([('pcpath_not', '$expression_line(' + leaf + ')', 'true' if folded else 'false'),
                     ('pcpath_child_3', '$source_line(metadata_child_3)', 'true')])
    constants = [('pcpath_child_3', raw)] + ([('pcpath_not', result)] if folded else [])
    return changed(rows, constants, function), expression, function


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    expression = current.expression(name, 2)
    result = current.nodes(name)[2][3]
    checks += [
        ('the certified NOT preserves its strict Boolean without an owner or tag collapse',
         value('S', expression) + ' = (' + result + r') /\ $value_nodes(' + result + r') = eps /\ ' + control.tail()),
        ('a preset exact Boolean cannot replace NORMAL child and parent authority',
         value('S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]', expression) + ' = eps'),
        ('the full Boolean state rejects a changed live BASE',
         value('S[.BASE = BASE_VALUE (KNOWN (PINT 99))]', expression) + ' = eps'),
        ('source unit and handler body cannot be borrowed from another function',
         '~' + control.tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + r' /\ ~' +
         control.tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    for index, (_, _, _, typed, folded) in enumerate(current.nodes(name)):
        slot = current.slot(index)
        flag = 'true' if folded else 'false'
        for label, line, changed_flag in [('flag', 'z_' + slot, 'false' if folded else 'true'),
                                          ('line', '$(z_' + slot + ' + 1)', flag)]:
            checks += [(slot + ' CODE ' + label + ' remains exact for the entire tail',
                        '~' + control.tail(function=control.code_function('pcpath_' + slot, line, changed_flag)))]
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or130_drop(pcunit_handler.OCCURRENCES, pcpath_' + slot + ')] :: S.SOURCES]')
        checks += [('removing only ' + slot + ' source refuses the entire tail', '~' + control.tail(state))]
        if folded:
            wrong = 'PINT 0' if typed.startswith(('PBOOL', 'PNULL')) else 'PBOOL false'
            checks += [(slot + ' constant fact retains its exact type despite equal falsey truth',
                        value(control.pool_state('pcpath_' + slot, wrong), expression) + ' = eps')]
    if current.nodes(name)[2][4]:
        state = ('S[.POOLS = ppool_handler[.CONSTANTS = '
                 '$or130_fact_drop(ppool_handler.CONSTANTS, pcpath_not)] :: S.POOLS]')
        checks += [('a folded NOT needs its own PBOOL independently of the still-certified child',
                    value(state, current.expression(name, 3), 'porigin_child_3') +
                    ' = (' + current.nodes(name)[3][3] + r') /\ ' + value(state, expression) + ' = eps')]
    else:
        checks += [('an emitted NOT keeps read-eps even with an unread forged parent pool',
                    r'$compiled_read(S, porigin_not) = eps /\ ' +
                    value(control.pool_state('pcpath_not', 'PINT 99'), expression) + ' = (' + result + ')')]
    variant = current.DETAILS[name][1]
    if variant == 'keyword-null':
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or130_drop(pcunit_handler.OCCURRENCES, pcpath_child_3 ++ [PCFIELD 0])] :: S.SOURCES]')
        checks += [('the simple keyword still needs its own indexed NName source', value(state, expression) + ' = eps')]
        checks += [('NULL cannot borrow the equally falsey FALSE child tag',
                    value(control.pool_state('pcpath_child_3', 'PBOOL false'), expression) + ' = eps')]
        for keyword, raw, expected in [('true', 'PBOOL true', 'PBOOL false'),
                                        ('FaLsE', 'PBOOL false', 'PBOOL true'),
                                        ('NULL', 'PNULL', 'PBOOL true'),
                                        ('missing130', 'PNULL', None)]:
            text = base64.b64encode(keyword.encode()).decode()
            node = 'NName (BYTES "' + text + '") metadata_leaf_name'
            leaf = 'NExprConstFetch (' + node + ') metadata_child_3'
            state, expr, function = raw_not(leaf, raw, expected or 'PBOOL true', name_node=node)
            checks += [('source0 keyword NOT retains exact spelling and strict child tag',
                        value(state, expr, function=function) + (' = (' + expected + ')' if expected else ' = eps'))]
    elif variant == 'string-truthy':
        checks += [('raw PSTRING facts remain distinct from nonowning compiled INTERNED carriers',
                    r'$compiled_read(S, porigin_child_3) = (PSTRING ($ptascii("x"))) /\ '
                    r'$compiled_string_value(S, porigin_child_3, PSTRING ($ptascii("x"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("x")) /\ ' +
                    value(control.pool_state('pcpath_child_3', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("x"))'), expression) + ' = eps')]
        checks += [('the raw STRING fact needs exact bytes even when another string has identical truth',
                    value(control.pool_state('pcpath_child_3', 'PSTRING ($ptascii("y"))'), expression) + ' = eps')]
        state = ('S[.DECLARATIONS = eps][.POOLS = ppool_handler[.CONSTANTS = '
                 '[PCONSTANT pcpath_child_3 (PSTRING ($ptascii("x"))), PCONSTANT pcpath_not (PBOOL false)]] :: S.POOLS]')
        checks += [('raw bytes alone cannot replace the precision-backed INTERNED carrier',
                    '$compiled_read(' + state + r', porigin_child_3) = (PSTRING ($ptascii("x"))) /\ ' +
                    value(state, expression) + ' = eps')]
        for payload, expected in [(b'', 'PBOOL true'), (b'0', 'PBOOL true'),
                                   (b'00', 'PBOOL false'), (b'x\x00', None)]:
            leaf = 'NScalarString (BYTES "' + base64.b64encode(payload).decode() + '") metadata_child_3'
            raw = 'PSTRING ($base64("' + base64.b64encode(payload).decode() + '"))'
            state, expr, function = raw_not(leaf, raw, expected or 'PBOOL false')
            checks += [('source0 byte truth distinguishes empty, sole zero, other bytes and held NUL',
                        value(state, expr, function=function) + (' = (' + expected + ')' if expected else ' = eps'))]
        for leaf, raw in [('NExprArray (SEQUENCE eps) metadata_child_3', 'PARRAY 0'),
                           ('NScalarString (BYTES "eA==") metadata_child_3', 'POBJECT 0')]:
            state, expr, function = raw_not(leaf, raw, 'PBOOL false')
            checks += [('an owning or wrong-tag child cannot borrow a quiet raw certificate', value(state, expr, function=function) + ' = eps')]
    else:
        for text in ['7ff8abcdef012345', '7ff0000000000001']:
            bits = str(int(text, 16))
            raw = 'NScalarFloat (FLOAT "' + text + '") metadata_child_4'
            child = 'NExprCastDouble (' + raw + ') ((Mkind 2) :: metadata_child_3)'
            expr = 'NExprBooleanNot (' + child + ') metadata_not'
            function = code([('pcpath_not', '$expression_line(' + child + ')', 'false'),
                             ('pcpath_child_3', '$expression_line(' + raw + ')', 'false'),
                             ('pcpath_child_4', '$source_line(metadata_child_4)', 'true')])
            state = changed([('pcpath_not', expr), ('pcpath_child_3', child), ('pcpath_child_4', raw)],
                            [('pcpath_child_4', 'PFLOAT ' + bits)], function)
            masked = 'S_nan_' + text
            bindings += [masked + ' = ' + state + '[.REPORTING = 0][.ERRORHANDLER = {CALLBACK eps, LEVELS 0}]'
                         '[.ERRORFATALTRACE = eps][.RESULT = KNOWN (PBOOL false)]']
            checks += [('source0 quiet FLOAT identity child cannot mask intrinsically noisy NaN NOT',
                        value(masked, child, 'porigin_child_3', function) + ' = (PFLOAT ' + bits + r') /\ ' +
                        '$boolean_result(' + masked + '[.RESULT = KNOWN (PFLOAT ' + bits + ')], true, z_not) = ' +
                        masked + r'[.RESULT = KNOWN (PBOOL false)] /\ ~$ob_object_cast_chain_quiet(CASTBOOL, PFLOAT ' + bits + r') /\ ' +
                        value(masked, expr, function=function) + ' = eps')]
        raw = 'NScalarFloat (FLOAT "43e0000000000000") metadata_child_4'
        child = 'NExprCastInt (' + raw + ') ((Mkind 1) :: metadata_child_3)'
        expr = 'NExprBooleanNot (' + child + ') metadata_not'
        function = code([('pcpath_not', '$expression_line(' + child + ')', 'false'),
                         ('pcpath_child_3', '$expression_line(' + raw + ')', 'false'),
                         ('pcpath_child_4', '$source_line(metadata_child_4)', 'true')])
        state = changed([('pcpath_not', expr), ('pcpath_child_3', child), ('pcpath_child_4', raw)],
                        [('pcpath_child_4', 'PFLOAT 4890909195324358656')], function)
        checks += [('a noisy range-to-INT cast child remains outside generic NOT even with reporting masked',
                    '~$ob_object_cast_chain_quiet(CASTINT, PFLOAT 4890909195324358656)' + r' /\ ' +
                    value(state + '[.REPORTING = 0][.ERRORHANDLER = {CALLBACK eps, LEVELS 0}]', expr, function=function) + ' = eps')]
        raw = 'NScalarInt (INTEGER 1) metadata_child_5'
        inner = 'NExprUnaryPlus (' + raw + ') metadata_child_4'
        child = 'NExprUnaryPlus (' + inner + ') metadata_child_3'
        expr = 'NExprBooleanNot (' + child + ') metadata_not'
        function = code([('pcpath_not', '$expression_line(' + child + ')', 'true'),
                         ('pcpath_child_3', '$expression_line(' + inner + ')', 'true'),
                         ('pcpath_child_4', '$expression_line(' + raw + ')', 'true'),
                         ('pcpath_child_5', '$source_line(metadata_child_5)', 'true')])
        state = changed([('pcpath_not', expr), ('pcpath_child_3', child),
                         ('pcpath_child_4', inner), ('pcpath_child_5', raw)],
                        [('pcpath_not', 'PBOOL false'), ('pcpath_child_3', 'PINT 1'),
                         ('pcpath_child_4', 'PINT 1'), ('pcpath_child_5', 'PINT 1')], function)
        checks += [('a fully certified nested numeric sign now composes with strict folded NOT',
                    value(state, inner, 'porigin_child_4', function) + r' = (PINT 1) /\ ' +
                    value(state, expr, function=function) + ' = (PBOOL false)')]
        raw = 'NScalarString (BYTES "MA==") metadata_child_4'
        child = 'NExprUnaryPlus (' + raw + ') metadata_child_3'
        expr = 'NExprBooleanNot (' + child + ') metadata_not'
        function = code([('pcpath_not', '$expression_line(' + child + ')', 'true'),
                         ('pcpath_child_3', '$expression_line(' + raw + ')', 'true'),
                         ('pcpath_child_4', '$source_line(metadata_child_4)', 'true')])
        state = changed([('pcpath_not', expr), ('pcpath_child_3', child), ('pcpath_child_4', raw)],
                        [('pcpath_not', 'PBOOL true'), ('pcpath_child_3', 'PINT 0'),
                         ('pcpath_child_4', 'PSTRING ($ptascii("0"))')], function)
        checks += [('generic NOT cannot admit a numeric-string coercive sign child',
                    '~$ob_object_cast_chain_sign_literal(' + raw + r') /\ ' +
                    value(state, expr, function=function) + ' = eps')]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    single = current.nodes(name)[1][0] + ' (' + expression + ') metadata_cast_1'
    statement = 'NStmtReturn (' + single + ') metadata_cast_return'
    checks += [('helper composition preserves the bare and single-cast handler refusals',
                '~' + control.tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + r' /\ ~' +
                control.tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', single)]), statement=statement))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('actual formal and native-cell retirement keeps the typed return and Boolean nonownership',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL /\ '
                '$value_nodes(' + current.nodes(name)[2][3] + ') = eps')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
