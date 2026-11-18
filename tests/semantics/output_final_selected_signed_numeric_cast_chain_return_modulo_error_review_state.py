#!/usr/bin/env python3
"""Independent folded-sign cache, type and intrinsic-boundary controls."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_signed_numeric_cast_chain_return_modulo_error_state as current
import output_final_selected_signed_numeric_cast_chain_return_modulo_error_sources as sources

runner = current.runner
CASES = {name: sources.CASES['native-selected-signed-numeric-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair', 'warning-right-cv-pair',
                      'warning-deprecated-constant-float']}
PREFIX = current.PREFIX + r'''
dec $or127_drop(pcoccurrence*, pcpath) : pcoccurrence*
def $or127_drop(eps, pcpath) = eps
def $or127_drop((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*, pcpath) = pcoccurrence*
def $or127_drop((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*, pcpath) = (PCOCCURRENCE pcpath_other pcnode) :: $or127_drop(pcoccurrence*, pcpath)
  -- if pcpath_other =/= pcpath
'''


def value(state, expression, origin='porigin_sign'):
    return '$ob_object_cast_chain_value(' + state + ', pfunction_handler, ' + origin + ', ' + expression + ')'


def pool(state, raw, signed):
    return (state + '[.POOLS = ppool_handler[.CONSTANTS = [(PCONSTANT pcpath_raw (' + raw +
            ')), (PCONSTANT pcpath_sign (' + signed + '))] ++ ppool_handler.CONSTANTS] :: S.POOLS]')


def variant(name, raw=None, raw_value=None, sign=None, sign_value=None, extra=()):
    raw = raw or current.RAW[name][0]
    sign = sign or current.SIGNS[name][0]
    expression_sign = sign + ' (' + raw + ') metadata_sign'
    expressions = [expression_sign]
    for index in reversed(range(len(current.CASTS[name]))):
        expressions.insert(0, current.CASTS[name][index][0] + ' (' + expressions[0] + ') metadata_' + current.slot(index))
    statement = 'NStmtReturn (' + expressions[0] + ') metadata_cast_return'
    rows = [('pcpath_cast_return', statement)]
    rows += [('pcpath_' + current.slot(i), expr) for i, expr in enumerate(expressions[:-1])]
    rows += [('pcpath_sign', expression_sign), ('pcpath_raw', raw), *extra]
    state = control.source_state(rows)
    state = pool(state, raw_value or current.RAW[name][1], sign_value or current.SIGNS[name][2])
    return state, statement, expression_sign


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)',
                 'pcpath_name = pcpath_raw ++ [PCFIELD 0]']
    sign_expression = current.expression(name, len(current.CASTS[name]))
    raw_expression, raw_value, _ = current.RAW[name]
    _, operator, sign_value = current.SIGNS[name]
    tail = control.tail
    checks += [
        ('the folded sign and raw child keep separate exact pools and proper source paths',
         value('S', sign_expression) + ' = (' + sign_value + r') /\ '
         '$compiled_read(S, porigin_sign) = (' + sign_value + r') /\ '
         '$compiled_read(S, porigin_raw) = (' + raw_value + r') /\ '
         r'pcpath_raw = pcpath_sign ++ [PCFIELD 0] /\ b_sign /\ b_raw'),
        ('the full unary result preserves type and every state field except its result',
         '$type_bytes(' + sign_value + ') = $type_bytes(' + raw_value + r') /\ '
         '$unary_apply(S[.RESULT = KNOWN (' + raw_value + ')], ' + operator + ', ' + raw_value + ', z_sign) = '
         'S[.RESULT = KNOWN (' + sign_value + r')] /\ $value_nodes(' + sign_value + ') = eps'),
        ('the real chain retains its exact Boolean/default or numeric/suppress choice',
         tail() + r' /\ S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL')]
    for role, origin, codepath, line in [('sign', 'porigin_sign', 'pcpath_sign', 'z_sign'),
                                       ('raw', 'porigin_raw', 'pcpath_raw', 'z_raw')]:
        for label, changed_line, flag in [('flag', line, 'false'), ('line', '$(' + line + ' + 1)', 'true')]:
            checks += [(role + ' CODE ' + label + ' forgery refuses the whole tail',
                        '~' + tail(function=control.code_function(codepath, changed_line, flag)))]
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or127_drop(pcunit_handler.OCCURRENCES, ' + codepath + ')] :: S.SOURCES]')
        checks += [('removing only ' + role + ' source refuses the folded value', value(state, sign_expression) + ' = eps')]
    for role, kept_path, kept_value in [('sign', 'pcpath_raw', raw_value), ('raw', 'pcpath_sign', sign_value)]:
        state = ('S[.POOLS = ppool_handler[.CONSTANTS = [(PCONSTANT ' + kept_path + ' (' + kept_value +
                 '))]] :: S.POOLS]')
        checks += [('the ' + role + ' cache cannot be borrowed from the other equal-valued node',
                    '$compiled_read(' + state + ', PORIGIN n_cast_handler ' + kept_path + ') = (' + kept_value + r') /\ '
                    + value(state, sign_expression) + ' = eps')]
    for role, path in [('sign', 'pcpath_sign'), ('raw', 'pcpath_raw')]:
        for wrong in ['PBOOL false', 'PNULL', 'PSTRING ($ptascii("7"))', 'PFLOAT 18446744073709551616']:
            state = control.pool_state(path, wrong)
            checks += [(role + ' pool ' + wrong + ' refuses before unsafe decoding or coercion', value(state, sign_expression) + ' = eps')]
    wrong = 'PINT 8' if raw_value.startswith('PINT') else 'PFLOAT 4607182418800017408'
    checks += [('a fitting same-type but incorrect folded value fails the full unary equality',
                value(control.pool_state('pcpath_sign', wrong), sign_expression) + ' = eps')]
    abrupt = 'S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + sign_value + ')]'
    checks += [('a preset signed result cannot bypass NORMAL', value(abrupt, sign_expression) + r' = eps /\ ~' + tail(abrupt)),
               ('the helper rejects an out-of-width signed FLOAT pool before partial decode',
                r'~$ob_object_cast_chain_sign_number(PFLOAT 18446744073709551616)')]
    for integer, sign, result, admitted in [('$(-9223372036854775808)', 'NExprUnaryPlus', 'PINT $(-9223372036854775808)', True),
                                           ('$(-9223372036854775808)', 'NExprUnaryMinus', 'PFLOAT 4890909195324358656', False)]:
        raw = 'NScalarInt (INTEGER ' + integer + ') metadata_raw'
        state, statement, expr = variant(name, raw, 'PINT ' + integer, sign, result)
        op = 'POSITIVE' if sign == 'NExprUnaryPlus' else 'NEGATIVE'
        checks += [('source0 raw INT_MIN sign preserves the bounded same-type policy',
                    '$unary_apply(' + state + '[.RESULT = KNOWN (PINT ' + integer + ')], ' + op + ', PINT ' + integer + ', z_sign) = ' +
                    state + '[.RESULT = KNOWN (' + result + r')] /\ ' + value(state, expr) +
                    (' = (' + result + ')' if admitted else ' = eps') + (r' /\ ' if admitted else r' /\ ~') + tail(state, statement=statement))]
    raw = 'NScalarFloat (FLOAT "0000000000000000") metadata_raw'
    state, statement, expr = variant(name, raw, 'PFLOAT 0', 'NExprUnaryMinus', 'PFLOAT 9223372036854775808')
    checks += [('source0 unary-minus zero keeps negative-zero bits rather than equal positive zero',
                value(state, expr) + r' = (PFLOAT 9223372036854775808) /\ '
                + value(pool(state, 'PFLOAT 0', 'PFLOAT 0'), expr) + ' = eps')]
    for text in ['7FF0000000000000', '7ff000000000000', '7ff00000000000000', '7fg0000000000000']:
        raw = 'NScalarFloat (FLOAT "' + text + '") metadata_raw'
        state, _, expr = variant(name, raw, 'PFLOAT 9218868437227405312', 'NExprUnaryPlus', 'PFLOAT 9218868437227405312')
        checks += [('malformed raw binary64 text refuses before decode despite fitting exact pools', value(state, expr) + ' = eps')]
    raw = 'NScalarFloat (FLOAT "7ff0000000000000") metadata_raw'
    state, _, expr = variant(name, raw, 'PFLOAT 9218868437227405312', 'NExprUnaryMinus', 'PFLOAT 18442240474082181120')
    checks += [('source0 nonNaN infinity remains a quiet same-type folded sign',
                '$unary_apply(' + state + '[.RESULT = KNOWN (PFLOAT 9218868437227405312)], NEGATIVE, PFLOAT 9218868437227405312, z_sign) = ' +
                state + r'[.RESULT = KNOWN (PFLOAT 18442240474082181120)] /\ ' + value(state, expr) + ' = (PFLOAT 18442240474082181120)')]
    nan_value = 'PFLOAT ' + str(int('7ff8abcdef012345', 16))
    for text, signed in [('7ff8abcdef012345', nan_value),
                          ('3ff0000000000000', nan_value)]:
        bits = str(int(text, 16))
        raw = 'NScalarFloat (FLOAT "' + text + '") metadata_raw'
        state, statement, expr = variant(name, raw, 'PFLOAT ' + bits, 'NExprUnaryPlus', signed)
        masked = 'S_nan_' + ('input' if text.startswith('7ff8') else 'output')
        bindings += [masked + ' = ' + state + '[.REPORTING = 0][.ERRORHANDLER = {CALLBACK eps, LEVELS 0}]'
                     '[.ERRORFATALTRACE = eps][.RESULT = KNOWN (' + signed + ')]']
        condition = (value(masked, expr) + r' = eps /\ ~' + tail(masked, statement=statement))
        if text.startswith('7ff8'):
            condition = ('$unary_apply(' + masked + '[.RESULT = KNOWN (PFLOAT ' + bits + ')], POSITIVE, PFLOAT ' + bits + ', z_sign) = ' +
                         masked + '[.RESULT = KNOWN (PFLOAT ' + bits + r')] /\ ' + condition)
        checks += [('source0 nonNaN input/output bound survives reporting masks and preset result', condition)]
    for raw, typed, result, extra in [
            ('NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_raw) metadata_raw', 'PBOOL true', 'PINT 1',
             [('pcpath_name', 'NName (BYTES "dHJ1ZQ==") metadata_raw')]),
            ('NScalarString (BYTES "Nw==") metadata_raw', 'PSTRING ($ptascii("7"))', 'PINT 7', [])]:
        state, statement, expr = variant(name, raw, typed, 'NExprUnaryPlus', result, extra)
        actual = 'PBOOL true' if typed == 'PBOOL true' else 'PSTRING_CARRIER INTERNED_STRING ($ptascii("7"))'
        checks += [('quiet coercive signs retain separate primitive rather than raw-numeric authority',
                    '~$ob_object_cast_chain_sign_literal(' + raw + r') /\ '
                    '$unary_apply(' + state + '[.RESULT = KNOWN (' + actual + ')], POSITIVE, ' + actual + ', z_sign) = ' +
                    state + '[.RESULT = KNOWN (' + result + r')] /\ ' + value(state, expr) + ' = (' + result + ')')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('real retirement preserves exact folded and final cast types without a heap owner',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL /\ '
                '$compiled_read(S_report, porigin_sign) = (' + current.SIGNS[name][2] + r') /\ '
                '$compiled_read(S_report, porigin_raw) = (' + current.RAW[name][1] + r') /\ '
                '$value_nodes(' + current.SIGNS[name][2] + ') = eps')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
