#!/usr/bin/env python3
"""Own float UnaryPlus Returns bind two reads; local projections retain source0."""
import output_final_selected_positive_float_return_modulo_error_state as author
import output_final_selected_both_mask_modulo_error_review_state as homogeneous
import output_final_selected_mixed_modulo_error_review_state as mixed

runner = homogeneous.runner
PREFIX = author.PREFIX
BASES = {'warning-right-cv-pair': homogeneous,
         'warning-deprecated-constant-float': mixed}
CASES = {name: author.sources.CASES['native-selected-positive-float-return-modulo-error-' + name]
         for name in BASES}
LOCAL = {'signed_zero': ('8000000000000000', 9223372036854775808, 9223372036854775808),
         'signed_infinity': ('fff0000000000000', 18442240474082181120, 18442240474082181120),
         'quiet_nan': ('7ff8abcdef012345', 0x7ff8abcdef012345, 0x7ff8abcdef012345),
         'signaling_nan': ('7ff0000000000001', 0x7ff0000000000001, 0x7ff0000000000001),
         'short': ('000000000000000', 0, 0),
         'long': ('00000000000000000', 0, 0),
         'above': ('10000000000000000', 18446744073709551616, 18446744073709551616),
         'uppercase': ('000000000000000A', 10, 10),
         'nonhex': ('000000000000000g', 0, 0)}


def authority(name, fixture, path):
    bindings, checks = BASES[name].authority(name, fixture, path)
    bindings += author.return_bindings(name)
    bindings += [
        'text_float_other = "3ff8000000000000"',
        'n_float_other = $hex_bits(text_float_other, 0)',
        'statement_positive_other = NStmtReturn (NExprUnaryPlus (NScalarFloat (FLOAT text_float_other) metadata_float) metadata_positive) metadata_positive_return',
        'expression_positive_minus = NExprUnaryMinus (NScalarFloat (FLOAT text_float) metadata_float) metadata_positive',
        'statement_positive_minus = NStmtReturn expression_positive_minus metadata_positive_return',
        'statement_positive_raw = NStmtReturn (NScalarFloat (FLOAT text_float) metadata_float) metadata_positive_return',
        'statement_positive_integer = NStmtReturn (NExprUnaryPlus (NScalarInt (INTEGER 0) metadata_float) metadata_positive) metadata_positive_return',
        'statement_positive_bare = NStmtReturn ABSENT metadata_positive_return',
        'pfunction_positive_unit = pfunction_handler[.CODE = pfunction_handler.CODE[.UNIT = $(n_positive_handler + 1)]]',
        'pfunction_positive_body = pfunction_handler[.BODY = pcpath_positive_handler]',
        'S_positive_scratch = S[.RESULT = KNOWN (PFLOAT n_return)]',
        'S_child_scratch = S[.RESULT = KNOWN (PFLOAT n_child)]',
        'S_false_scratch = S[.RESULT = KNOWN (PBOOL false)]',
        'S.SOURCES = [pcunit_positive_projection]',
        'pcunit_positive_projection.ID = n_positive_handler',
        'S_raw_root = S[.SOURCES = [pcunit_positive_projection[.OCCURRENCES = (PCOCCURRENCE pcpath_positive expression_positive_minus) :: pcunit_positive_projection.OCCURRENCES]]]',
        'S_raw_child = S[.SOURCES = [pcunit_positive_projection[.OCCURRENCES = (PCOCCURRENCE pcpath_float (NScalarFloat (FLOAT text_float_other) metadata_float)) :: pcunit_positive_projection.OCCURRENCES]]]']
    for part, codepath, line in [('root', 'pcpath_positive', 'z_positive'),
                                 ('child', 'pcpath_float', 'z_float')]:
        bindings += [
            'z_' + part + '_bad = $(' + line + ' + 1)',
            'pfunction_' + part + '_flag = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR ' + codepath + ' ' + line + ' false) :: pfunction_handler.CODE.EXPRESSIONS]]',
            'pfunction_' + part + '_line = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR ' + codepath + ' z_' + part + '_bad true) :: pfunction_handler.CODE.EXPRESSIONS]]']
    for suffix, root_value, child_value in [
            ('root_other', 'PFLOAT n_float_other', 'PFLOAT n_child'),
            ('child_other', 'PFLOAT n_return', 'PFLOAT n_float_other'),
            ('root_integer', 'PINT 0', 'PFLOAT n_child'),
            ('child_integer', 'PFLOAT n_return', 'PINT 0')]:
        bindings += ['S_' + suffix + '_read = S[.POOLS = [{UNIT n_positive_handler, CONSTANTS ([(PCONSTANT pcpath_positive (' + root_value + ')), (PCONSTANT pcpath_float (' + child_value + '))])}] ++ S.POOLS]']
    for suffix, (text, child_bits, result_bits) in LOCAL.items():
        bindings += [
            'text_local_' + suffix + ' = "' + text + '"',
            'n_local_' + suffix + '_child = ' + str(child_bits),
            'n_local_' + suffix + '_return = ' + str(result_bits),
            'expression_local_' + suffix + ' = NExprUnaryPlus (NScalarFloat (FLOAT text_local_' + suffix + ') metadata_float) metadata_positive',
            'statement_local_' + suffix + ' = NStmtReturn expression_local_' + suffix + ' metadata_positive_return',
            'pcunit_local_' + suffix + ' = pcunit_positive_projection[.OCCURRENCES = [(PCOCCURRENCE pcpath_positive_return statement_local_' + suffix + '), (PCOCCURRENCE pcpath_positive expression_local_' + suffix + '), (PCOCCURRENCE pcpath_float (NScalarFloat (FLOAT text_local_' + suffix + ') metadata_float))] ++ pcunit_positive_projection.OCCURRENCES]',
            'S_local_' + suffix + ' = S[.SOURCES = [pcunit_local_' + suffix + ']][.POOLS = [{UNIT n_positive_handler, CONSTANTS ([(PCONSTANT pcpath_positive (PFLOAT n_local_' + suffix + '_return)), (PCONSTANT pcpath_float (PFLOAT n_local_' + suffix + '_child))])}] ++ S.POOLS]']
    checks = [(label.replace('NULL finish', 'handled positive-float finish'), author.converted(condition))
              for label, condition in checks]
    checks += [
        ('the own UnaryPlus root and raw child retain exact result bits and NULL scratch',
         author.return_proof(name) + r' /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, [statement_positive_return])'),
        ('different raw float, MINUS, bare float, integer and bare or extra Returns cannot replace the body',
         r'text_float_other =/= text_float /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_positive_other]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_positive_minus]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_positive_raw]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_positive_integer]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_positive_bare]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_positive_return, statement_positive_return])'),
        ('local root and child occurrence shadows refuse despite unchanged Return and compiled reads',
         r'S_raw_root.CODE = S.CODE /\ S_raw_child.CODE = S.CODE /\ '
         r'S_raw_root.SOURCES[0].AST = pcunit_positive_projection.AST /\ '
         r'S_raw_child.SOURCES[0].AST = pcunit_positive_projection.AST /\ '
         r'$origin_node(S_raw_root.SOURCES, porigin_positive_return) = (statement_positive_return) /\ '
         r'$origin_node(S_raw_child.SOURCES, porigin_positive_return) = (statement_positive_return) /\ '
         r'$compiled_read(S_raw_root, porigin_positive) = (PFLOAT n_return) /\ '
         r'$compiled_read(S_raw_child, porigin_float) = (PFLOAT n_child) /\ '
         r'~$ob_object_error_handler_tail(S_raw_root, pfunction_handler, [statement_positive_return]) /\ '
         r'~$ob_object_error_handler_tail(S_raw_child, pfunction_handler, [statement_positive_return])')]
    for part, codepath, line in [('root', 'pcpath_positive', 'z_positive'),
                                 ('child', 'pcpath_float', 'z_float')]:
        checks += [('each own ' + part + ' CODE record needs its actual line and true flag',
            '$code_expression(pfunction_' + part + '_flag.CODE.EXPRESSIONS, ' + codepath + ') = ((' + line + r', false)) /\ '
            '$code_expression(pfunction_' + part + '_line.CODE.EXPRESSIONS, ' + codepath + ') = ((z_' + part + r'_bad, true)) /\ '
            'z_' + part + '_bad =/= ' + line + r' /\ '
            '~$ob_object_error_handler_tail(S, pfunction_' + part + r'_flag, [statement_positive_return]) /\ '
            '~$ob_object_error_handler_tail(S, pfunction_' + part + '_line, [statement_positive_return])')]
    checks += [
        ('each populated PFLOAT pool refuses distinct wrong bits even when the original values coincide',
         r'n_float_other =/= n_child /\ n_float_other =/= n_return /\ '
         r'$compiled_read(S_root_other_read, porigin_positive) = (PFLOAT n_float_other) /\ '
         r'$compiled_read(S_root_other_read, porigin_float) = (PFLOAT n_child) /\ '
         r'$compiled_read(S_child_other_read, porigin_positive) = (PFLOAT n_return) /\ '
         r'$compiled_read(S_child_other_read, porigin_float) = (PFLOAT n_float_other) /\ '
         r'~$ob_object_error_handler_tail(S_root_other_read, pfunction_handler, [statement_positive_return]) /\ '
         r'~$ob_object_error_handler_tail(S_child_other_read, pfunction_handler, [statement_positive_return])'),
        ('PINT zero cannot replace either exact PFLOAT read',
         r'$compiled_read(S_root_integer_read, porigin_positive) = (PINT 0) /\ '
         r'$compiled_read(S_root_integer_read, porigin_float) = (PFLOAT n_child) /\ '
         r'$compiled_read(S_child_integer_read, porigin_positive) = (PFLOAT n_return) /\ '
         r'$compiled_read(S_child_integer_read, porigin_float) = (PINT 0) /\ '
         r'~$ob_object_error_handler_tail(S_root_integer_read, pfunction_handler, [statement_positive_return]) /\ '
         r'~$ob_object_error_handler_tail(S_child_integer_read, pfunction_handler, [statement_positive_return])'),
        ('the own unary Return retains its function unit and body',
         r'pfunction_positive_unit.CODE.UNIT =/= n_positive_handler /\ '
         r'pfunction_positive_body.BODY =/= pfunction_handler.BODY /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_positive_unit, [statement_positive_return]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_positive_body, [statement_positive_return])')]
    conditions = []
    for state in ['S_positive_scratch', 'S_child_scratch', 'S_false_scratch']:
        conditions += ['$call_current_valid(' + state + ')', '$dz_raw(' + state + ') = S_request',
                       '$ob_object_division_error_capture(' + state + ', S_generated) = eps']
    checks += [('consumed result, raw child and FALSE cannot replace resumed NULL scratch', r' /\ '.join(conditions))]
    for suffixes, admitted, nan, label in [
            (['signed_zero', 'signed_infinity'], True, False,
             'local negative zero and infinity retain identical bits through the full POSITIVE result'),
            (['quiet_nan', 'signaling_nan'], False, True,
             'local quiet and signaling NaNs refuse despite their exact existing POSITIVE identity result'),
            (['short', 'long', 'above'], False, False,
             'local width15 and width17 payloads refuse before partial binary64 decoding'),
            (['uppercase', 'nonhex'], False, False,
             'local final uppercase and nonhex glyphs refuse before partial decoding')]:
        conditions = []
        for suffix in suffixes:
            state, text, child, result, statement = ('S_local_' + suffix, 'text_local_' + suffix,
                'n_local_' + suffix + '_child', 'n_local_' + suffix + '_return', 'statement_local_' + suffix)
            conditions += [state + '.CODE = S.CODE', state + '.SOURCES[0].AST = pcunit_positive_projection.AST',
                '$origin_node(' + state + '.SOURCES, porigin_positive_return) = (' + statement + ')',
                '$origin_node(' + state + '.SOURCES, porigin_positive) = (expression_local_' + suffix + ')',
                '$origin_node(' + state + '.SOURCES, porigin_float) = (NScalarFloat (FLOAT ' + text + ') metadata_float)',
                '$compiled_read(' + state + ', porigin_positive) = (PFLOAT ' + result + ')',
                '$compiled_read(' + state + ', porigin_float) = (PFLOAT ' + child + ')']
            if admitted or nan:
                conditions += ['|' + text + '| = 16',
                    '$evaluate(NScalarFloat (FLOAT ' + text + ') metadata_float) = VALUE (PFLOAT ' + child + ')',
                    '$float_decode(' + child + ') ' + ('=' if nan else '=/=') + ' NOTNUMBER ' + child,
                    '$unary_apply(' + state + ', POSITIVE, PFLOAT ' + child + ', z_positive) = ' + state + '[.RESULT = KNOWN (PFLOAT ' + result + ')]']
            conditions += [('' if admitted else '~') + '$ob_object_error_handler_tail(' + state + ', pfunction_handler, [' + statement + '])']
        checks += [(label, r' /\ '.join(conditions))]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
