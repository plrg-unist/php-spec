#!/usr/bin/env python3
"""Own integer UnaryMinus Returns bind two reads; local projections retain source0."""
import output_final_selected_negative_integer_return_modulo_error_state as author
import output_final_selected_both_mask_modulo_error_review_state as homogeneous
import output_final_selected_mixed_modulo_error_review_state as mixed

runner = homogeneous.runner
PREFIX = author.PREFIX
BASES = {'warning-right-cv-pair': homogeneous,
         'warning-deprecated-constant-float': mixed}
CASES = {name: author.sources.CASES['native-selected-negative-integer-return-modulo-error-' + name]
         for name in BASES}
LOCAL = {'minus_one': ('$(-1)', '1'),
         'minus_maximum': ('$(-9223372036854775807)', '9223372036854775807'),
         'minimum': ('$(-9223372036854775808)', '9223372036854775808'),
         'above': ('9223372036854775808', '$(-9223372036854775808)'),
         'below': ('$(-9223372036854775809)', '9223372036854775809')}


def authority(name, fixture, path):
    bindings, checks = BASES[name].authority(name, fixture, path)
    bindings += author.return_bindings(name)
    bindings += [
        'i_integer_other = 1',
        'statement_negative_other = NStmtReturn (NExprUnaryMinus (NScalarInt (INTEGER i_integer_other) metadata_integer) metadata_negative) metadata_negative_return',
        'expression_negative_plus = NExprUnaryPlus (NScalarInt (INTEGER i_child) metadata_integer) metadata_negative',
        'statement_negative_plus = NStmtReturn expression_negative_plus metadata_negative_return',
        'statement_negative_raw = NStmtReturn (NScalarInt (INTEGER i_child) metadata_integer) metadata_negative_return',
        'statement_negative_float = NStmtReturn (NExprUnaryMinus (NScalarFloat (FLOAT "0000000000000000") metadata_integer) metadata_negative) metadata_negative_return',
        'statement_negative_bare = NStmtReturn ABSENT metadata_negative_return',
        'pfunction_negative_unit = pfunction_handler[.CODE = pfunction_handler.CODE[.UNIT = $(n_negative_handler + 1)]]',
        'pfunction_negative_body = pfunction_handler[.BODY = pcpath_negative_handler]',
        'S_negative_scratch = S[.RESULT = KNOWN (PINT i_return)]',
        'S_child_scratch = S[.RESULT = KNOWN (PINT i_child)]',
        'S_false_scratch = S[.RESULT = KNOWN (PBOOL false)]',
        'S.SOURCES = [pcunit_negative_projection]',
        'pcunit_negative_projection.ID = n_negative_handler',
        'S_raw_root = S[.SOURCES = [pcunit_negative_projection[.OCCURRENCES = (PCOCCURRENCE pcpath_negative expression_negative_plus) :: pcunit_negative_projection.OCCURRENCES]]]',
        'S_raw_child = S[.SOURCES = [pcunit_negative_projection[.OCCURRENCES = (PCOCCURRENCE pcpath_integer (NScalarInt (INTEGER i_integer_other) metadata_integer)) :: pcunit_negative_projection.OCCURRENCES]]]']
    for part, codepath, line in [('root', 'pcpath_negative', 'z_negative'),
                                 ('child', 'pcpath_integer', 'z_integer')]:
        bindings += [
            'z_' + part + '_bad = $(' + line + ' + 1)',
            'pfunction_' + part + '_flag = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR ' + codepath + ' ' + line + ' false) :: pfunction_handler.CODE.EXPRESSIONS]]',
            'pfunction_' + part + '_line = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR ' + codepath + ' z_' + part + '_bad true) :: pfunction_handler.CODE.EXPRESSIONS]]']
    for suffix, root_value, child_value in [
            ('root_other', 'PINT i_integer_other', 'PINT i_child'),
            ('child_other', 'PINT i_return', 'PINT i_integer_other'),
            ('root_false', 'PBOOL false', 'PINT i_child'),
            ('child_false', 'PINT i_return', 'PBOOL false'),
            ('root_float', 'PFLOAT 0', 'PINT i_child'),
            ('child_float', 'PINT i_return', 'PFLOAT 0')]:
        bindings += ['S_' + suffix + '_read = S[.POOLS = [{UNIT n_negative_handler, CONSTANTS ([(PCONSTANT pcpath_negative (' + root_value + ')), (PCONSTANT pcpath_integer (' + child_value + '))])}] ++ S.POOLS]']
    for suffix, (child, result) in LOCAL.items():
        bindings += [
            'i_local_' + suffix + '_child = ' + child,
            'i_local_' + suffix + '_return = ' + result,
            'expression_local_' + suffix + ' = NExprUnaryMinus (NScalarInt (INTEGER i_local_' + suffix + '_child) metadata_integer) metadata_negative',
            'statement_local_' + suffix + ' = NStmtReturn expression_local_' + suffix + ' metadata_negative_return',
            'pcunit_local_' + suffix + ' = pcunit_negative_projection[.OCCURRENCES = [(PCOCCURRENCE pcpath_negative_return statement_local_' + suffix + '), (PCOCCURRENCE pcpath_negative expression_local_' + suffix + '), (PCOCCURRENCE pcpath_integer (NScalarInt (INTEGER i_local_' + suffix + '_child) metadata_integer))] ++ pcunit_negative_projection.OCCURRENCES]',
            'S_local_' + suffix + ' = S[.SOURCES = [pcunit_local_' + suffix + ']][.POOLS = [{UNIT n_negative_handler, CONSTANTS ([(PCONSTANT pcpath_negative (PINT i_local_' + suffix + '_return)), (PCONSTANT pcpath_integer (PINT i_local_' + suffix + '_child))])}] ++ S.POOLS]']
    bindings += ['S_minimum_float = S_local_minimum[.POOLS = [{UNIT n_negative_handler, CONSTANTS ([(PCONSTANT pcpath_negative (PFLOAT 4890909195324358656)), (PCONSTANT pcpath_integer (PINT i_local_minimum_child))])}] ++ S.POOLS]']
    checks = [(label.replace('NULL finish', 'handled negative-integer finish'), author.converted(condition))
              for label, condition in checks]
    checks += [
        ('the own UnaryMinus root and raw child retain exact integers and NULL scratch',
         author.return_proof(name) + r' /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, [statement_negative_return])'),
        ('different integer, PLUS, raw integer, FLOAT and bare or extra Returns cannot replace the body',
         r'i_integer_other =/= i_child /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_negative_other]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_negative_plus]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_negative_raw]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_negative_float]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_negative_bare]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_negative_return, statement_negative_return])'),
        ('local root and child occurrence shadows refuse despite unchanged Return and compiled reads',
         r'S_raw_root.CODE = S.CODE /\ S_raw_child.CODE = S.CODE /\ '
         r'S_raw_root.SOURCES[0].AST = pcunit_negative_projection.AST /\ '
         r'S_raw_child.SOURCES[0].AST = pcunit_negative_projection.AST /\ '
         r'$origin_node(S_raw_root.SOURCES, porigin_negative_return) = (statement_negative_return) /\ '
         r'$origin_node(S_raw_child.SOURCES, porigin_negative_return) = (statement_negative_return) /\ '
         r'$compiled_read(S_raw_root, porigin_negative) = (PINT i_return) /\ '
         r'$compiled_read(S_raw_child, porigin_integer) = (PINT i_child) /\ '
         r'~$ob_object_error_handler_tail(S_raw_root, pfunction_handler, [statement_negative_return]) /\ '
         r'~$ob_object_error_handler_tail(S_raw_child, pfunction_handler, [statement_negative_return])')]
    for part, codepath, line in [('root', 'pcpath_negative', 'z_negative'),
                                 ('child', 'pcpath_integer', 'z_integer')]:
        checks += [('each own ' + part + ' CODE record needs its actual line and true flag',
            '$code_expression(pfunction_' + part + '_flag.CODE.EXPRESSIONS, ' + codepath + ') = ((' + line + r', false)) /\ '
            '$code_expression(pfunction_' + part + '_line.CODE.EXPRESSIONS, ' + codepath + ') = ((z_' + part + r'_bad, true)) /\ '
            'z_' + part + '_bad =/= ' + line + r' /\ '
            '~$ob_object_error_handler_tail(S, pfunction_' + part + r'_flag, [statement_negative_return]) /\ '
            '~$ob_object_error_handler_tail(S, pfunction_' + part + '_line, [statement_negative_return])')]
    for suffixes, root_type, child_type, label in [
            (['root_other', 'child_other'], 'PINT i_integer_other', 'PINT i_integer_other',
             'each populated integer pool refuses a distinct wrong value even when the original is zero'),
            (['root_false', 'child_false'], 'PBOOL false', 'PBOOL false',
             'Boolean FALSE cannot replace either exact PINT pool'),
            (['root_float', 'child_float'], 'PFLOAT 0', 'PFLOAT 0',
             'FLOAT positive zero cannot replace either exact PINT pool')]:
        root, child = 'S_' + suffixes[0] + '_read', 'S_' + suffixes[1] + '_read'
        checks += [(label, r'i_integer_other =/= i_return /\ i_integer_other =/= i_child /\ '
            '$compiled_read(' + root + ', porigin_negative) = (' + root_type + r') /\ '
            '$compiled_read(' + root + r', porigin_integer) = (PINT i_child) /\ '
            '$compiled_read(' + child + r', porigin_negative) = (PINT i_return) /\ '
            '$compiled_read(' + child + ', porigin_integer) = (' + child_type + r') /\ '
            '~$ob_object_error_handler_tail(' + root + r', pfunction_handler, [statement_negative_return]) /\ '
            '~$ob_object_error_handler_tail(' + child + ', pfunction_handler, [statement_negative_return])')]
    checks += [('the own unary Return retains its function unit and body',
        r'pfunction_negative_unit.CODE.UNIT =/= n_negative_handler /\ '
        r'pfunction_negative_body.BODY =/= pfunction_handler.BODY /\ '
        r'~$ob_object_error_handler_tail(S, pfunction_negative_unit, [statement_negative_return]) /\ '
        r'~$ob_object_error_handler_tail(S, pfunction_negative_body, [statement_negative_return])')]
    conditions = []
    for state in ['S_negative_scratch', 'S_child_scratch', 'S_false_scratch']:
        conditions += ['$call_current_valid(' + state + ')', '$dz_raw(' + state + ') = S_request',
                       '$ob_object_division_error_capture(' + state + ', S_generated) = eps']
    checks += [('consumed result, raw child and FALSE cannot replace resumed NULL scratch', r' /\ '.join(conditions))]
    for suffixes, admitted, label in [
            (['minus_one', 'minus_maximum'], True,
             'local raw negative children admit only their exact quiet signed64 unary results'),
            (['minimum', 'above', 'below'], False,
             'local MIN overflow and out-of-range children or results refuse despite matching raw and pool facts')]:
        conditions = []
        for suffix in suffixes:
            state, child, result, statement = ('S_local_' + suffix, 'i_local_' + suffix + '_child',
                'i_local_' + suffix + '_return', 'statement_local_' + suffix)
            conditions += [state + '.CODE = S.CODE', state + '.SOURCES[0].AST = pcunit_negative_projection.AST',
                '$origin_node(' + state + '.SOURCES, porigin_negative_return) = (' + statement + ')',
                '$origin_node(' + state + '.SOURCES, porigin_negative) = (expression_local_' + suffix + ')',
                '$origin_node(' + state + '.SOURCES, porigin_integer) = (NScalarInt (INTEGER ' + child + ') metadata_integer)',
                '$compiled_read(' + state + ', porigin_negative) = (PINT ' + result + ')',
                '$compiled_read(' + state + ', porigin_integer) = (PINT ' + child + ')']
            if admitted:
                conditions += ['$long_range(' + child + ')', '$long_range(' + result + ')',
                    '$unary_apply(' + state + ', NEGATIVE, PINT ' + child + ', z_negative) = ' + state + '[.RESULT = KNOWN (PINT ' + result + ')]']
            else:
                conditions += ['~($long_range(' + child + r') /\ $long_range(' + result + '))']
            conditions += [('' if admitted else '~') + '$ob_object_error_handler_tail(' + state + ', pfunction_handler, [' + statement + '])']
        checks += [(label, r' /\ '.join(conditions))]
    checks += [('local MIN overflow retains its actual FLOAT result and cannot borrow the integer arm',
        r'$long_range(i_local_minimum_child) /\ ~$long_range(i_local_minimum_return) /\ '
        r'S_minimum_float.CODE = S.CODE /\ S_minimum_float.SOURCES = S_local_minimum.SOURCES /\ '
        r'$compiled_read(S_minimum_float, porigin_negative) = (PFLOAT 4890909195324358656) /\ '
        r'$compiled_read(S_minimum_float, porigin_integer) = (PINT i_local_minimum_child) /\ '
        r'$unary_apply(S_minimum_float, NEGATIVE, PINT i_local_minimum_child, z_negative) = S_minimum_float[.RESULT = KNOWN (PFLOAT 4890909195324358656)] /\ '
        r'~$ob_object_error_handler_tail(S_minimum_float, pfunction_handler, [statement_local_minimum])')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
