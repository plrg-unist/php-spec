#!/usr/bin/env python3
"""Independent raw numeric NOT, emitted/folded authority and quietness controls."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_numeric_not_cast_chain_return_modulo_error_state as current
import output_final_selected_numeric_not_cast_chain_return_modulo_error_sources as sources

runner = current.runner
CASES = {name: sources.CASES['native-selected-numeric-not-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair', 'warning-right-cv-pair',
                      'warning-deprecated-constant-float']}
PREFIX = current.PREFIX + r'''
dec $or128_drop(pcoccurrence*, pcpath) : pcoccurrence*
def $or128_drop(eps, pcpath) = eps
def $or128_drop((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*, pcpath) = pcoccurrence*
def $or128_drop((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*, pcpath) = (PCOCCURRENCE pcpath_other pcnode) :: $or128_drop(pcoccurrence*, pcpath)
  -- if pcpath_other =/= pcpath
'''


def value(state, expression, origin='porigin_not', function='pfunction_handler'):
    return '$ob_object_cast_chain_value(' + state + ', ' + function + ', ' + origin + ', ' + expression + ')'


def pool(state, raw, result, folded):
    constants = '(PCONSTANT pcpath_raw (' + raw + '))'
    if folded:
        constants += ', (PCONSTANT pcpath_not (' + result + '))'
    return (state + '[.POOLS = ppool_handler[.CONSTANTS = [' + constants +
            '] ++ ppool_handler.CONSTANTS] :: S.POOLS]')


def variant(name, raw, raw_value, result):
    expression = 'NExprBooleanNot (' + raw + ') metadata_not'
    expressions = [expression]
    for index in reversed(range(len(current.CASTS[name]))):
        expressions.insert(0, current.CASTS[name][index][0] + ' (' + expressions[0] + ') metadata_' + current.slot(index))
    statement = 'NStmtReturn (' + expressions[0] + ') metadata_cast_return'
    rows = [('pcpath_cast_return', statement)]
    rows += [('pcpath_' + current.slot(i), expr) for i, expr in enumerate(expressions[:-1])]
    rows += [('pcpath_not', expression), ('pcpath_raw', raw)]
    return pool(control.source_state(rows), raw_value, result, raw_value.startswith('PINT')), statement, expression


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    expression = current.expression(name, len(current.CASTS[name]))
    raw, raw_value, _ = current.RAW[name]
    result = current.NOTS[name][1]
    folded = raw_value.startswith('PINT')
    flag = 'true' if folded else 'false'
    tail = control.tail
    checks += [
        ('numeric NOT preserves a strict Boolean without a heap owner or default-tag collapse',
         value('S', expression) + ' = (' + result + r') /\ $value_nodes(' + result + r') = eps /\ ' +
         tail() + r' /\ S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL'),
        ('the complete NOT operation preserves every state field except the typed result',
         '$boolean_result(S[.RESULT = KNOWN (' + raw_value + ')], true, z_not) = S[.RESULT = KNOWN (' + result + ')]'),
        ('a live BASE change cannot be hidden by checking only the Boolean result',
         value('S[.BASE = BASE_VALUE (KNOWN (PINT 99))]', expression) + ' = eps'),
        ('handler source unit and body retain their original authority',
         '~' + tail(function='pfunction_handler[.CODE.UNIT = $(n_cast_handler + 1)]') + r' /\ ~' +
         tail(function='pfunction_handler[.BODY = pfunction_handler.BODY ++ [PCINDEX 0]]'))]
    abrupt = 'S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]'
    checks += [('a preset exact Boolean cannot certify an abrupt numeric NOT',
                value(abrupt, expression) + r' = eps /\ ~' + tail(abrupt))]
    for role, codepath, line, expected_flag in [('NOT', 'pcpath_not', 'z_not', flag),
                                              ('raw', 'pcpath_raw', 'z_raw', 'true')]:
        for label, changed_line, changed_flag in [('flag', line, 'false' if expected_flag == 'true' else 'true'),
                                                 ('line', '$(' + line + ' + 1)', expected_flag)]:
            checks += [(role + ' CODE ' + label + ' forgery refuses the entire chain',
                        '~' + tail(function=control.code_function(codepath, changed_line, changed_flag)))]
    for label, source_path in [('Return', 'pcpath_cast_return'),
            *[(current.slot(i), 'pcpath_' + current.slot(i)) for i in range(len(current.CASTS[name]))],
            ('NOT', 'pcpath_not'), ('raw', 'pcpath_raw')]:
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or128_drop(pcunit_handler.OCCURRENCES, ' + source_path + ')] :: S.SOURCES]')
        checks += [('removing only ' + label + ' source refuses the whole nested tail', '~' + tail(state))]
    constants = '[(PCONSTANT pcpath_raw (' + raw_value + '))' + (', (PCONSTANT pcpath_not (' + result + '))' if folded else '') + ']'
    no_precision = ('S[.DECLARATIONS = eps][.POOLS = ppool_handler[.CONSTANTS = ' + constants +
                    '] :: S.POOLS][.PRECISIONINI = [51]][.PRECISIONMODIFIED = true]')
    checks += [('numeric NOT depends on exact bits and tags rather than parser or live precision',
                '$compiled_precision(' + no_precision + r', (porigin_not)) = eps /\ ' +
                value(no_precision, expression) + ' = (' + result + ')')]
    for wrong in ['PBOOL false', 'PNULL', 'POBJECT 0', 'PARRAY 0', 'PFLOAT 18446744073709551616']:
        checks += [('raw cache ' + wrong + ' cannot replace the exact numeric source tag or add owners',
                    value(control.pool_state('pcpath_raw', wrong), expression) + ' = eps')]
    wrong = 'PINT 7' if folded else 'PFLOAT 4607182418800017408'
    checks += [('a same-type numeric cache still needs the exact raw bits or integer',
                value(control.pool_state('pcpath_raw', wrong), expression) + ' = eps')]
    if folded:
        for wrong in ['PBOOL false', 'PINT 1', 'PNULL']:
            if wrong != result:
                checks += [('folded NOT cache ' + wrong + ' cannot replace its exact PBOOL result',
                            value(control.pool_state('pcpath_not', wrong), expression) + ' = eps')]
        state = 'S[.POOLS = ppool_handler[.CONSTANTS = [(PCONSTANT pcpath_raw (' + raw_value + '))]] :: S.POOLS]'
        checks += [('a folded INT NOT needs its own fact independently of the child fact', value(state, expression) + ' = eps')]
        for integer in ['$(-9223372036854775808)', '9223372036854775807', '9223372036854775808']:
            leaf = 'NScalarInt (INTEGER ' + integer + ') metadata_raw'
            state, _, expr = variant(name, leaf, 'PINT ' + integer, 'PBOOL false')
            checks += [('source0 raw integer NOT retains the signed64 boundary',
                        value(state, expr) + (' = eps' if integer == '9223372036854775808' else ' = (PBOOL false)'))]
    else:
        checks += [('an emitted FLOAT NOT ignores an unread parent pool and keeps read-eps',
                    r'$compiled_read(S, porigin_not) = eps /\ ' +
                    value(control.pool_state('pcpath_not', 'PBOOL true'), expression) + ' = (' + result + ')')]
        for text, expected in [('8000000000000000', 'PBOOL true'), ('7ff0000000000000', 'PBOOL false')]:
            bits = str(int(text, 16))
            leaf = 'NScalarFloat (FLOAT "' + text + '") metadata_raw'
            state, _, expr = variant(name, leaf, 'PFLOAT ' + bits, expected)
            checks += [('source0 FLOAT NOT preserves signed-zero and infinity truth without folding', value(state, expr) + ' = (' + expected + ')')]
        for text in ['7FF0000000000000', '7ff000000000000', '7ff00000000000000', '7fg0000000000000']:
            leaf = 'NScalarFloat (FLOAT "' + text + '") metadata_raw'
            state, _, expr = variant(name, leaf, raw_value, result)
            checks += [('malformed FLOAT NOT refuses before partial hexadecimal decoding', value(state, expr) + ' = eps')]
        for text in ['7ff8abcdef012345', '7ff0000000000001']:
            bits = str(int(text, 16))
            leaf = 'NScalarFloat (FLOAT "' + text + '") metadata_raw'
            state, _, expr = variant(name, leaf, 'PFLOAT ' + bits, 'PBOOL false')
            masked = 'S_nan_' + text
            bindings += [masked + ' = ' + state + '[.REPORTING = 0][.ERRORHANDLER = {CALLBACK eps, LEVELS 0}]'
                         '[.ERRORFATALTRACE = eps][.RESULT = KNOWN (PBOOL false)]']
            checks += [('source0 NaN NOT remains intrinsically noisy despite masked full-state equality',
                        '$boolean_result(' + masked + '[.RESULT = KNOWN (PFLOAT ' + bits + ')], true, z_not) = ' +
                        masked + r'[.RESULT = KNOWN (PBOOL false)] /\ ~$ob_object_cast_chain_quiet(CASTBOOL, PFLOAT ' + bits + r') /\ ' +
                        value(masked, expr) + ' = eps')]
    for leaf, typed in [('NScalarString (BYTES "MA==") metadata_raw', 'PSTRING ($ptascii("0"))'),
                        ('NExprArray (SEQUENCE eps) metadata_raw', 'PARRAY 0')]:
        state, _, expr = variant(name, leaf, typed, 'PBOOL true')
        checks += [('quiet nonnumeric or owning child stays outside the raw literal contract',
                    '~$ob_object_cast_chain_sign_literal(' + leaf + r') /\ ' + value(state, expr) + ' = eps')]
    bare = 'NStmtReturn (' + expression + ') metadata_cast_return'
    direct = current.CASTS[name][-1][0] + ' (' + expression + ') metadata_' + current.slot(len(current.CASTS[name]) - 1)
    statement = 'NStmtReturn (' + direct + ') metadata_cast_return'
    checks += [('helper acceptance does not broaden bare NOT or the nested-only handler gate',
                '~' + tail(control.source_state([('pcpath_cast_return', bare)]), statement=bare) + r' /\ ~' +
                tail(control.source_state([('pcpath_cast_return', statement), ('pcpath_cast', direct)]), statement=statement))]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('actual retirement keeps strict final/default tags and adds no Boolean owner',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL /\ '
                '$value_nodes(' + current.NOTS[name][1] + r') = eps /\ '
                '$compiled_read(S_report, porigin_raw) = (' + current.RAW[name][1] + ')')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
