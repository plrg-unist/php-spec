#!/usr/bin/env python3
"""Own float UnaryMinus Returns bind two reads; local projections retain source0."""
import output_final_selected_negative_float_return_modulo_error_state as author
import output_final_selected_both_mask_modulo_error_review_state as homogeneous
import output_final_selected_mixed_modulo_error_review_state as mixed

runner = homogeneous.runner
PREFIX = author.PREFIX
BASES = {'warning-right-cv-pair': homogeneous,
         'warning-deprecated-constant-float': mixed}
CASES = {name: author.sources.CASES['native-selected-negative-float-return-modulo-error-' + name]
         for name in BASES}
LOCAL = {'negative_zero': ('8000000000000000', 9223372036854775808, 0),
         'negative_infinity': ('fff0000000000000', 18442240474082181120, 9218868437227405312),
         'quiet_nan': ('7ff8abcdef012345', 0x7ff8abcdef012345, 0x7ff8abcdef012345),
         'signaling_nan': ('7ff0000000000001', 0x7ff0000000000001, 0x7ff8000000000001),
         'short': ('000000000000000', 0, 9223372036854775808),
         'long': ('00000000000000000', 0, 9223372036854775808),
         'above': ('10000000000000000', 18446744073709551616, 0),
         'uppercase': ('000000000000000A', 10, 9223372036854775818),
         'nonhex': ('000000000000000g', 0, 9223372036854775808)}


def authority(name, fixture, path):
    bindings, checks = BASES[name].authority(name, fixture, path)
    bindings += author.return_bindings(name)
    bindings += [
        'text_float_other = "3ff8000000000000"',
        'statement_negative_other = NStmtReturn (NExprUnaryMinus (NScalarFloat (FLOAT text_float_other) metadata_float) metadata_negative) metadata_negative_return',
        'expression_negative_plus = NExprUnaryPlus (NScalarFloat (FLOAT text_float) metadata_float) metadata_negative',
        'statement_negative_plus = NStmtReturn expression_negative_plus metadata_negative_return',
        'statement_negative_raw = NStmtReturn (NScalarFloat (FLOAT text_float) metadata_float) metadata_negative_return',
        'statement_negative_integer = NStmtReturn (NExprUnaryMinus (NScalarInt (INTEGER 0) metadata_float) metadata_negative) metadata_negative_return',
        'statement_negative_bare = NStmtReturn ABSENT metadata_negative_return',
        'pfunction_negative_unit = pfunction_handler[.CODE = pfunction_handler.CODE[.UNIT = $(n_negative_handler + 1)]]',
        'pfunction_negative_body = pfunction_handler[.BODY = pcpath_negative_handler]',
        'S_negative_scratch = S[.RESULT = KNOWN (PFLOAT n_return)]',
        'S_child_scratch = S[.RESULT = KNOWN (PFLOAT n_child)]',
        'S_false_scratch = S[.RESULT = KNOWN (PBOOL false)]',
        'S.SOURCES = [pcunit_negative_projection]',
        'pcunit_negative_projection.ID = n_negative_handler',
        'S_raw_root = S[.SOURCES = [pcunit_negative_projection[.OCCURRENCES = (PCOCCURRENCE pcpath_negative expression_negative_plus) :: pcunit_negative_projection.OCCURRENCES]]]',
        'S_raw_child = S[.SOURCES = [pcunit_negative_projection[.OCCURRENCES = (PCOCCURRENCE pcpath_float (NScalarFloat (FLOAT text_float_other) metadata_float)) :: pcunit_negative_projection.OCCURRENCES]]]']
    for part, codepath, line in [('root', 'pcpath_negative', 'z_negative'),
                                 ('child', 'pcpath_float', 'z_float')]:
        bindings += [
            'z_' + part + '_bad = $(' + line + ' + 1)',
            'pfunction_' + part + '_flag = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR ' + codepath + ' ' + line + ' false) :: pfunction_handler.CODE.EXPRESSIONS]]',
            'pfunction_' + part + '_line = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR ' + codepath + ' z_' + part + '_bad true) :: pfunction_handler.CODE.EXPRESSIONS]]']
    for suffix, root_value, child_value in [
            ('root_other', 'PFLOAT n_child', 'PFLOAT n_child'),
            ('child_other', 'PFLOAT n_return', 'PFLOAT n_return'),
            ('root_integer', 'PINT 0', 'PFLOAT n_child'),
            ('child_integer', 'PFLOAT n_return', 'PINT 0')]:
        bindings += ['S_' + suffix + '_read = S[.POOLS = [{UNIT n_negative_handler, CONSTANTS ([(PCONSTANT pcpath_negative (' + root_value + ')), (PCONSTANT pcpath_float (' + child_value + '))])}] ++ S.POOLS]']
    for suffix, (text, child_bits, result_bits) in LOCAL.items():
        bindings += [
            'text_local_' + suffix + ' = "' + text + '"',
            'n_local_' + suffix + '_child = ' + str(child_bits),
            'n_local_' + suffix + '_return = ' + str(result_bits),
            'expression_local_' + suffix + ' = NExprUnaryMinus (NScalarFloat (FLOAT text_local_' + suffix + ') metadata_float) metadata_negative',
            'statement_local_' + suffix + ' = NStmtReturn expression_local_' + suffix + ' metadata_negative_return',
            'pcunit_local_' + suffix + ' = pcunit_negative_projection[.OCCURRENCES = [(PCOCCURRENCE pcpath_negative_return statement_local_' + suffix + '), (PCOCCURRENCE pcpath_negative expression_local_' + suffix + '), (PCOCCURRENCE pcpath_float (NScalarFloat (FLOAT text_local_' + suffix + ') metadata_float))] ++ pcunit_negative_projection.OCCURRENCES]',
            'S_local_' + suffix + ' = S[.SOURCES = [pcunit_local_' + suffix + ']][.POOLS = [{UNIT n_negative_handler, CONSTANTS ([(PCONSTANT pcpath_negative (PFLOAT n_local_' + suffix + '_return)), (PCONSTANT pcpath_float (PFLOAT n_local_' + suffix + '_child))])}] ++ S.POOLS]']
    checks = [(label.replace('NULL finish', 'handled negative-float finish'), author.converted(condition))
              for label, condition in checks]
    checks += [
        ('the own UnaryMinus root and raw child retain exact result bits and NULL scratch',
         author.return_proof(name) + r' /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, [statement_negative_return])'),
        ('different raw float, PLUS, bare float, integer and bare or extra Returns cannot replace the body',
         r'text_float_other =/= text_float /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_negative_other]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_negative_plus]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_negative_raw]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_negative_integer]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_negative_bare]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_negative_return, statement_negative_return])'),
        ('local root and child occurrence shadows refuse despite unchanged Return and compiled reads',
         r'S_raw_root.CODE = S.CODE /\ S_raw_child.CODE = S.CODE /\ '
         r'S_raw_root.SOURCES[0].AST = pcunit_negative_projection.AST /\ '
         r'S_raw_child.SOURCES[0].AST = pcunit_negative_projection.AST /\ '
         r'$origin_node(S_raw_root.SOURCES, porigin_negative_return) = (statement_negative_return) /\ '
         r'$origin_node(S_raw_child.SOURCES, porigin_negative_return) = (statement_negative_return) /\ '
         r'$compiled_read(S_raw_root, porigin_negative) = (PFLOAT n_return) /\ '
         r'$compiled_read(S_raw_child, porigin_float) = (PFLOAT n_child) /\ '
         r'~$ob_object_error_handler_tail(S_raw_root, pfunction_handler, [statement_negative_return]) /\ '
         r'~$ob_object_error_handler_tail(S_raw_child, pfunction_handler, [statement_negative_return])')]
    for part, codepath, line in [('root', 'pcpath_negative', 'z_negative'),
                                 ('child', 'pcpath_float', 'z_float')]:
        checks += [('each own ' + part + ' CODE record needs its actual line and true flag',
            '$code_expression(pfunction_' + part + '_flag.CODE.EXPRESSIONS, ' + codepath + ') = ((' + line + r', false)) /\ '
            '$code_expression(pfunction_' + part + '_line.CODE.EXPRESSIONS, ' + codepath + ') = ((z_' + part + r'_bad, true)) /\ '
            'z_' + part + '_bad =/= ' + line + r' /\ '
            '~$ob_object_error_handler_tail(S, pfunction_' + part + r'_flag, [statement_negative_return]) /\ '
            '~$ob_object_error_handler_tail(S, pfunction_' + part + '_line, [statement_negative_return])')]
    checks += [
        ('root and child PFLOAT pools cannot exchange their different exact bits',
         r'n_child =/= n_return /\ '
         r'$compiled_read(S_root_other_read, porigin_negative) = (PFLOAT n_child) /\ '
         r'$compiled_read(S_root_other_read, porigin_float) = (PFLOAT n_child) /\ '
         r'$compiled_read(S_child_other_read, porigin_negative) = (PFLOAT n_return) /\ '
         r'$compiled_read(S_child_other_read, porigin_float) = (PFLOAT n_return) /\ '
         r'~$ob_object_error_handler_tail(S_root_other_read, pfunction_handler, [statement_negative_return]) /\ '
         r'~$ob_object_error_handler_tail(S_child_other_read, pfunction_handler, [statement_negative_return])'),
        ('PINT zero cannot replace either exact PFLOAT read',
         r'$compiled_read(S_root_integer_read, porigin_negative) = (PINT 0) /\ '
         r'$compiled_read(S_root_integer_read, porigin_float) = (PFLOAT n_child) /\ '
         r'$compiled_read(S_child_integer_read, porigin_negative) = (PFLOAT n_return) /\ '
         r'$compiled_read(S_child_integer_read, porigin_float) = (PINT 0) /\ '
         r'~$ob_object_error_handler_tail(S_root_integer_read, pfunction_handler, [statement_negative_return]) /\ '
         r'~$ob_object_error_handler_tail(S_child_integer_read, pfunction_handler, [statement_negative_return])'),
        ('the own unary Return retains its function unit and body',
         r'pfunction_negative_unit.CODE.UNIT =/= n_negative_handler /\ '
         r'pfunction_negative_body.BODY =/= pfunction_handler.BODY /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_negative_unit, [statement_negative_return]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_negative_body, [statement_negative_return])')]
    conditions = []
    for state in ['S_negative_scratch', 'S_child_scratch', 'S_false_scratch']:
        conditions += ['$call_current_valid(' + state + ')', '$dz_raw(' + state + ') = S_request',
                       '$ob_object_division_error_capture(' + state + ', S_generated) = eps']
    checks += [('consumed result, raw child and FALSE cannot replace resumed NULL scratch', r' /\ '.join(conditions))]
    for suffixes, admitted, nan, label in [
            (['negative_zero', 'negative_infinity'], True, False,
             'local negative-child zero and infinity admit only their exact full unary result'),
            (['quiet_nan', 'signaling_nan'], False, True,
             'local quiet and signaling NaNs refuse despite their exact existing multiply result'),
            (['short', 'long', 'above'], False, False,
             'local width15 and width17 payloads refuse before partial binary64 decoding'),
            (['uppercase', 'nonhex'], False, False,
             'local final uppercase and nonhex glyphs refuse before partial decoding')]:
        conditions = []
        for suffix in suffixes:
            state, text, child, result, statement = ('S_local_' + suffix, 'text_local_' + suffix,
                'n_local_' + suffix + '_child', 'n_local_' + suffix + '_return', 'statement_local_' + suffix)
            conditions += [state + '.CODE = S.CODE', state + '.SOURCES[0].AST = pcunit_negative_projection.AST',
                '$origin_node(' + state + '.SOURCES, porigin_negative_return) = (' + statement + ')',
                '$origin_node(' + state + '.SOURCES, porigin_negative) = (expression_local_' + suffix + ')',
                '$origin_node(' + state + '.SOURCES, porigin_float) = (NScalarFloat (FLOAT ' + text + ') metadata_float)',
                '$compiled_read(' + state + ', porigin_negative) = (PFLOAT ' + result + ')',
                '$compiled_read(' + state + ', porigin_float) = (PFLOAT ' + child + ')']
            if admitted or nan:
                conditions += ['|' + text + '| = 16',
                    '$evaluate(NScalarFloat (FLOAT ' + text + ') metadata_float) = VALUE (PFLOAT ' + child + ')',
                    '$float_decode(' + child + ') ' + ('=' if nan else '=/=') + ' NOTNUMBER ' + child,
                    '$unary_apply(' + state + ', NEGATIVE, PFLOAT ' + child + ', z_negative) = ' + state + '[.RESULT = KNOWN (PFLOAT ' + result + ')]']
            conditions += [('' if admitted else '~') + '$ob_object_error_handler_tail(' + state + ', pfunction_handler, [' + statement + '])']
        checks += [(label, r' /\ '.join(conditions))]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
