#!/usr/bin/env python3
"""Independent exact raw/sign/NOT composition and intrinsic-boundary controls."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as control
import output_final_selected_numeric_not_cast_chain_return_modulo_error_review_state as truth
import output_final_selected_signed_numeric_not_cast_chain_return_modulo_error_state as current
import output_final_selected_signed_numeric_not_cast_chain_return_modulo_error_sources as sources

runner = current.runner
CASES = {name: sources.CASES['native-selected-signed-numeric-not-cast-chain-return-modulo-error-' + name]
         for name in ['deprecated-both-cv-pair', 'warning-right-cv-pair',
                      'warning-deprecated-constant-float']}
PREFIX = current.PREFIX + r'''
dec $or129_drop(pcoccurrence*, pcpath) : pcoccurrence*
def $or129_drop(eps, pcpath) = eps
def $or129_drop((PCOCCURRENCE pcpath pcnode) :: pcoccurrence*, pcpath) = pcoccurrence*
def $or129_drop((PCOCCURRENCE pcpath_other pcnode) :: pcoccurrence*, pcpath) = (PCOCCURRENCE pcpath_other pcnode) :: $or129_drop(pcoccurrence*, pcpath)
  -- if pcpath_other =/= pcpath
'''
value = truth.value


def constants(leaf, signed, result, folded):
    rows = [('pcpath_leaf', leaf), ('pcpath_raw', signed)]
    if folded:
        rows += [('pcpath_not', result)]
    return '[' + ', '.join('(PCONSTANT ' + path + ' (' + typed + '))' for path, typed in rows) + ']'


def variant(name, leaf, leaf_value, sign=None, signed=None, result=None):
    sign = sign or current.SIGNS[name][0]
    signed = signed or current.RAW[name][1]
    result = result or current.NOTS[name][1]
    expression_sign = sign + ' (' + leaf + ') metadata_raw'
    expression_not = 'NExprBooleanNot (' + expression_sign + ') metadata_not'
    expressions = [expression_not]
    for index in reversed(range(len(current.CASTS[name]))):
        expressions.insert(0, current.CASTS[name][index][0] + ' (' + expressions[0] + ') metadata_' + current.slot(index))
    statement = 'NStmtReturn (' + expressions[0] + ') metadata_cast_return'
    rows = [('pcpath_cast_return', statement)]
    rows += [('pcpath_' + current.slot(i), expr) for i, expr in enumerate(expressions[:-1])]
    rows += [('pcpath_not', expression_not), ('pcpath_raw', expression_sign), ('pcpath_leaf', leaf)]
    state = (control.source_state(rows) + '[.POOLS = ppool_handler[.CONSTANTS = ' +
             constants(leaf_value, signed, result, signed.startswith('PINT')) +
             ' ++ ppool_handler.CONSTANTS] :: S.POOLS]')
    return state, expression_sign, expression_not


def frontier(name, fixture, path):
    bindings, checks = current.frontier(name, fixture, path)
    bindings += ['$source_unit(S.SOURCES, n_cast_handler) = (pcunit_handler)',
                 '$pool_at(S.POOLS, n_cast_handler) = (ppool_handler)']
    expression = current.expression(name, len(current.CASTS[name]))
    sign, signed, _ = current.RAW[name]
    leaf, leaf_value = current.LEAVES[name]
    result = current.NOTS[name][1]
    folded = signed.startswith('PINT')
    tail = control.tail
    checks += [
        ('the full unary and NOT operations compose with strict Boolean and nonowning results',
         value('S', sign, 'porigin_raw') + ' = (' + signed + r') /\ ' +
         value('S', expression) + ' = (' + result + r') /\ $value_nodes(' + result + r') = eps /\ ' + tail()),
        ('a live BASE change preserves the sign but defeats the full NOT equality',
         value('S[.BASE = BASE_VALUE (KNOWN (PINT 99))]', sign, 'porigin_raw') + ' = (' + signed + r') /\ ' +
         value('S[.BASE = BASE_VALUE (KNOWN (PINT 99))]', expression) + ' = eps')]
    for role, codepath, line, flag in [('NOT', 'pcpath_not', 'z_not', 'true' if folded else 'false'),
                                     ('sign', 'pcpath_raw', 'z_raw', 'true'),
                                     ('literal', 'pcpath_leaf', 'z_leaf', 'true')]:
        for label, changed_line, changed_flag in [('flag', line, 'false' if flag == 'true' else 'true'),
                                                 ('line', '$(' + line + ' + 1)', flag)]:
            checks += [(role + ' CODE ' + label + ' cannot be borrowed from an adjacent node',
                        '~' + tail(function=control.code_function(codepath, changed_line, changed_flag)))]
        state = ('S[.SOURCES = pcunit_handler[.OCCURRENCES = '
                 '$or129_drop(pcunit_handler.OCCURRENCES, ' + codepath + ')] :: S.SOURCES]')
        checks += [('removing only ' + role + ' source defeats the complete chain', '~' + tail(state))]
    rows = [('literal', 'pcpath_leaf', leaf_value), ('sign', 'pcpath_raw', signed)]
    if folded:
        rows += [('NOT', 'pcpath_not', result)]
    for role, removed, _ in rows:
        kept = '[' + ', '.join('(PCONSTANT ' + p + ' (' + v + '))' for _, p, v in rows if p != removed) + ']'
        state = 'S[.POOLS = ppool_handler[.CONSTANTS = ' + kept + '] :: S.POOLS]'
        checks += [('the ' + role + ' fact remains independently required even for equal-valued zero',
                    value(state, expression) + ' = eps')]
    for role, codepath in [('literal', 'pcpath_leaf'), ('sign', 'pcpath_raw')]:
        for wrong in ['PBOOL false', 'POBJECT 0', 'PFLOAT 18446744073709551616']:
            checks += [(role + ' malformed or owning cache cannot supply a numeric certificate',
                        value(control.pool_state(codepath, wrong), expression) + ' = eps')]
    wrong = 'PINT 7' if folded else 'PFLOAT 4607182418800017408'
    checks += [('a fitting raw-literal cache still needs exact integer or binary64 bits',
                value(control.pool_state('pcpath_leaf', wrong), expression) + ' = eps')]
    wrong = 'PINT 7' if folded else ('PFLOAT 0' if name == 'warning-deprecated-constant-float' else 'PFLOAT 4607182418800017408')
    checks += [('the folded sign needs exact bits even when a forged sign has identical Boolean truth',
                value(control.pool_state('pcpath_raw', wrong), expression) + ' = eps')]
    no_precision = ('S[.DECLARATIONS = eps][.POOLS = ppool_handler[.CONSTANTS = ' +
                    constants(leaf_value, signed, result, folded) +
                    '] :: S.POOLS][.PRECISIONINI = [51]][.PRECISIONMODIFIED = true]')
    checks += [('raw bits, full unary state and NOT do not depend on parser or live print precision',
                '$compiled_precision(' + no_precision + r', (porigin_not)) = eps /\ ' + value(no_precision, expression) + ' = (' + result + ')')]
    abrupt = 'S[.COMPLETION = BUDGET][.RESULT = KNOWN (' + result + ')]'
    checks += [('a preset exact Boolean cannot authenticate an abrupt signed child', value(abrupt, expression) + ' = eps')]
    nested = 'NExprBooleanNot (' + expression + ') metadata_cast_1'
    function = control.code_function('pcpath_cast_1', 'z_cast_1', 'true' if folded else 'false')
    state = (control.source_state([('pcpath_cast_1', nested)]) + '[.CODE = ' + function + '.CODE :: S.CODE]')
    if folded:
        state += control.pool_state('pcpath_cast_1', 'PBOOL false' if result == 'PBOOL true' else 'PBOOL true')[1:]
    checks += [('a valid inner numeric NOT cannot certify a nested outer NOT with coherent parent source',
                value(state, expression, function=function) + ' = (' + result + r') /\ ' +
                value(state, nested, 'porigin_cast_1', function) + ' = eps')]
    child = current.expression(name, 1)
    outer = 'NExprBooleanNot (' + child + ') metadata_cast'
    state = control.source_state([('pcpath_cast', outer)])
    checks += [('a valid quiet cast child cannot broaden numeric NOT despite coherent parent source',
                value(state, child, 'porigin_cast_1') + ' = (' + current.CASTS[name][1][3] + r') /\ ' +
                value(state, outer, 'porigin_cast') + ' = eps')]
    if folded:
        checks += [('a folded signed INT NOT retains a strict PBOOL fact distinct from integer one',
                    value(control.pool_state('pcpath_not', 'PINT 1'), expression) + ' = eps')]
        raw = 'NScalarInt (INTEGER $(-9223372036854775808)) metadata_leaf'
        state, expr_sign, _ = variant(name, raw, 'PINT $(-9223372036854775808)',
                                      'NExprUnaryMinus', 'PFLOAT 4890909195324358656', 'PBOOL false')
        checks += [('source0 INT_MIN promotion remains outside the pre-existing same-type sign proof',
                    '$unary_apply(' + state + '[.RESULT = KNOWN (PINT $(-9223372036854775808))], NEGATIVE, PINT $(-9223372036854775808), z_raw) = ' +
                    state + r'[.RESULT = KNOWN (PFLOAT 4890909195324358656)] /\ ' + value(state, expr_sign, 'porigin_raw') + ' = eps')]
    else:
        checks += [('signed FLOAT NOT remains emitted even when a parent pool contains a fitting Boolean',
                    r'$compiled_read(S, porigin_not) = eps /\ ' + value(control.pool_state('pcpath_not', result), expression) + ' = (' + result + ')')]
        for text in ['000000000000000', '00000000000000000', '000000000000000A', '000000000000000g']:
            raw = 'NScalarFloat (FLOAT "' + text + '") metadata_leaf'
            state, _, expr = variant(name, raw, leaf_value)
            checks += [('malformed literal below both sign and NOT refuses before partial decode', value(state, expr) + ' = eps')]
        for text in ['7ff8abcdef012345', '7ff0000000000001']:
            bits = str(int(text, 16))
            raw = 'NScalarFloat (FLOAT "' + text + '") metadata_leaf'
            state, expr_sign, expr = variant(name, raw, 'PFLOAT ' + bits, 'NExprUnaryPlus', 'PFLOAT ' + bits, 'PBOOL false')
            local = 'S_nan_' + text
            bindings += [local + ' = ' + state + '[.REPORTING = 0][.ERRORHANDLER = {CALLBACK eps, LEVELS 0}]'
                         '[.ERRORFATALTRACE = eps][.RESULT = KNOWN (PBOOL false)]']
            checks += [('masked full-state equality cannot erase the inherited sign noNaN boundary',
                        '$unary_apply(' + local + '[.RESULT = KNOWN (PFLOAT ' + bits + ')], POSITIVE, PFLOAT ' + bits + ', z_raw) = ' +
                        local + '[.RESULT = KNOWN (PFLOAT ' + bits + r')] /\ ' + value(local, expr_sign, 'porigin_raw') + r' = eps /\ ' + value(local, expr) + ' = eps')]
    raw = 'NScalarString (BYTES "Nw==") metadata_leaf'
    state, expr_sign, expr = variant(name, raw, 'PSTRING ($ptascii("7"))', 'NExprUnaryPlus', 'PINT 7', 'PBOOL false')
    checks += [('a quiet coercive sign cannot broaden the raw numeric child contract',
                '~$ob_object_cast_chain_sign_literal(' + raw + r') /\ ' + value(state, expr_sign, 'porigin_raw') + r' = eps /\ ' + value(state, expr) + ' = eps')]
    raw = 'NExprUnaryPlus (' + leaf + ') metadata_leaf'
    state, expr_sign, expr = variant(name, raw, leaf_value)
    checks += [('a second sign remains outside the one-sign raw numeric composition',
                '$ob_object_cast_chain_sign_kind(' + raw + r') /\ ~$ob_object_cast_chain_sign_literal(' + raw + r') /\ ' + value(state, expr_sign, 'porigin_raw') + r' = eps /\ ' + value(state, expr) + ' = eps')]
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = current.lifecycle(name, fixture, path)
    checks += [('retirement preserves separate raw/sign facts and the strict nonowning final tag',
                'S_handler.RESULT = KNOWN (' + current.root_value(name) + r') /\ S.RESULT = KNOWN PNULL /\ '
                '$compiled_read(S_report, porigin_leaf) = (' + current.LEAVES[name][1] + r') /\ '
                '$compiled_read(S_report, porigin_raw) = (' + current.RAW[name][1] + r') /\ '
                '$value_nodes(' + current.NOTS[name][1] + ') = eps')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
