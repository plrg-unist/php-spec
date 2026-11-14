#!/usr/bin/env python3
"""Canonical FLOAT casts round raw Int children; local projections retain source0."""
import output_final_selected_integer_float_cast_return_modulo_error_state as author
import output_final_selected_both_mask_modulo_error_review_state as homogeneous
import output_final_selected_mixed_modulo_error_review_state as mixed

runner = homogeneous.runner
PREFIX = author.PREFIX
BASES = {'warning-right-cv-pair': homogeneous,
         'warning-deprecated-constant-float': mixed}
CASES = {name: author.sources.CASES['native-selected-integer-float-cast-return-modulo-error-' + name]
         for name in BASES}
LOCAL = {'minus_one': ('$(-1)', '13830554455654793216'),
         'minimum': ('$(-9223372036854775808)', '14114281232179134464'),
         'above': ('9223372036854775808', '4890909195324358656'),
         'below': ('$(-9223372036854775809)', '14114281232179134464')}


def authority(name, fixture, path):
    bindings, checks = BASES[name].authority(name, fixture, path)
    bindings += author.return_bindings(name)
    bindings += [
        'i_integer_other = 1',
        'statement_cast_other = NStmtReturn (NExprCastDouble (NScalarInt (INTEGER i_integer_other) metadata_integer) metadata_cast) metadata_cast_return',
        'expression_cast_other_kind = NExprCastInt (NScalarInt (INTEGER i_child) metadata_integer) metadata_cast',
        'statement_cast_other_kind = NStmtReturn expression_cast_other_kind metadata_cast_return',
        'statement_cast_raw = NStmtReturn (NScalarInt (INTEGER i_child) metadata_integer) metadata_cast_return',
        'statement_cast_float = NStmtReturn (NExprCastDouble (NScalarFloat (FLOAT "0000000000000000") metadata_integer) metadata_cast) metadata_cast_return',
        'statement_cast_bare = NStmtReturn ABSENT metadata_cast_return',
        'pfunction_cast_unit = pfunction_handler[.CODE = pfunction_handler.CODE[.UNIT = $(n_cast_handler + 1)]]',
        'pfunction_cast_body = pfunction_handler[.BODY = pcpath_cast_handler]',
        'S_cast_scratch = S[.RESULT = KNOWN (PFLOAT n_return)]',
        'S_integer_scratch = S[.RESULT = KNOWN (PINT i_child)]',
        'S_false_scratch = S[.RESULT = KNOWN (PBOOL false)]',
        'S.SOURCES = [pcunit_cast_projection]',
        'pcunit_cast_projection.ID = n_cast_handler',
        'S_raw_root = S[.SOURCES = [pcunit_cast_projection[.OCCURRENCES = (PCOCCURRENCE pcpath_cast expression_cast_other_kind) :: pcunit_cast_projection.OCCURRENCES]]]',
        'S_raw_child = S[.SOURCES = [pcunit_cast_projection[.OCCURRENCES = (PCOCCURRENCE pcpath_integer (NScalarInt (INTEGER i_integer_other) metadata_integer)) :: pcunit_cast_projection.OCCURRENCES]]]']
    bindings += [
        'metadata_cast = (MendFilePos z_cast_end_file) :: (MendLine z_cast_end_line) :: (MendTokenPos z_cast_end_token) :: (Mkind 2) :: metadata_cast_positions',
        'metadata_cast_missing = [(MendFilePos z_cast_end_file), (MendLine z_cast_end_line), (MendTokenPos z_cast_end_token)] ++ metadata_cast_positions',
        'metadata_cast_double = [(MendFilePos z_cast_end_file), (MendLine z_cast_end_line), (MendTokenPos z_cast_end_token), (Mkind 1)] ++ metadata_cast_positions',
        'metadata_cast_real = [(MendFilePos z_cast_end_file), (MendLine z_cast_end_line), (MendTokenPos z_cast_end_token), (Mkind 3)] ++ metadata_cast_positions']
    for style in ['double', 'real', 'missing']:
        bindings += [
            'expression_style_' + style + ' = NExprCastDouble (NScalarInt (INTEGER i_child) metadata_integer) metadata_cast_' + style,
            'statement_style_' + style + ' = NStmtReturn expression_style_' + style + ' metadata_cast_return',
            'S_style_' + style + ' = S[.SOURCES = [pcunit_cast_projection[.OCCURRENCES = [(PCOCCURRENCE pcpath_cast_return statement_style_' + style + '), (PCOCCURRENCE pcpath_cast expression_style_' + style + ')] ++ pcunit_cast_projection.OCCURRENCES]]]']
    for part, codepath, line in [('root', 'pcpath_cast', 'z_cast'),
                                 ('child', 'pcpath_integer', 'z_integer')]:
        expected, wrong = ('false', 'true') if part == 'root' else ('true', 'false')
        bindings += [
            'z_' + part + '_bad = $(' + line + ' + 1)',
            'pfunction_' + part + '_flag = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR ' + codepath + ' ' + line + ' ' + wrong + ') :: pfunction_handler.CODE.EXPRESSIONS]]',
            'pfunction_' + part + '_line = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR ' + codepath + ' z_' + part + '_bad ' + expected + ') :: pfunction_handler.CODE.EXPRESSIONS]]']
    for suffix, value in [('child_other', 'PINT i_integer_other'),
                          ('child_false', 'PBOOL false'), ('child_float', 'PFLOAT 0')]:
        bindings += ['S_' + suffix + '_read = S[.POOLS = [{UNIT n_cast_handler, CONSTANTS ([(PCONSTANT pcpath_integer (' + value + '))])}] ++ S.POOLS]']
    bindings += [
        '$code_at(S.CODE, n_cast_handler) = (pcode_cast)',
        'pcode_cast_folded = pcode_cast[.EXPRESSIONS = (CODEEXPR pcpath_cast z_cast true) :: pcode_cast.EXPRESSIONS]',
        'S_root_folded = S[.CODE = pcode_cast_folded :: S.CODE][.POOLS = [{UNIT n_cast_handler, CONSTANTS ([(PCONSTANT pcpath_cast (PFLOAT n_return)), (PCONSTANT pcpath_integer (PINT i_child))])}] ++ S.POOLS]',
        'S_root_unread = S[.POOLS = [{UNIT n_cast_handler, CONSTANTS ([(PCONSTANT pcpath_cast (PBOOL false)), (PCONSTANT pcpath_integer (PINT i_child))])}] ++ S.POOLS]',
        'S_non_normal = S[.COMPLETION = BUDGET][.RESULT = KNOWN (PFLOAT n_return)]']
    for suffix, (child, result) in LOCAL.items():
        bindings += [
            'i_local_' + suffix + '_child = ' + child,
            'n_local_' + suffix + '_return = ' + result,
            'expression_local_' + suffix + ' = NExprCastDouble (NScalarInt (INTEGER i_local_' + suffix + '_child) metadata_integer) metadata_cast',
            'statement_local_' + suffix + ' = NStmtReturn expression_local_' + suffix + ' metadata_cast_return',
            'pcunit_local_' + suffix + ' = pcunit_cast_projection[.OCCURRENCES = [(PCOCCURRENCE pcpath_cast_return statement_local_' + suffix + '), (PCOCCURRENCE pcpath_cast expression_local_' + suffix + '), (PCOCCURRENCE pcpath_integer (NScalarInt (INTEGER i_local_' + suffix + '_child) metadata_integer))] ++ pcunit_cast_projection.OCCURRENCES]',
            'S_local_' + suffix + ' = S[.SOURCES = [pcunit_local_' + suffix + ']][.POOLS = [{UNIT n_cast_handler, CONSTANTS ([(PCONSTANT pcpath_integer (PINT i_local_' + suffix + '_child))])}] ++ S.POOLS]']
    checks = [(label.replace('NULL finish', 'handled cast-FLOAT finish'), author.converted(condition))
              for label, condition in checks]
    checks += [
        ('the own emitted cast root and pooled integer child retain the exact FLOAT result and NULL scratch',
         author.return_proof(name) + r' /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, [statement_cast_return])'),
        ('different integer, cast kind, raw integer, FLOAT and bare or extra Returns cannot replace the body',
         r'i_integer_other =/= i_child /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_cast_other]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_cast_other_kind]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_cast_raw]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_cast_float]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_cast_bare]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_cast_return, statement_cast_return])'),
        ('local root and child occurrence shadows refuse despite unchanged Return and compiled reads',
         r'S_raw_root.CODE = S.CODE /\ S_raw_child.CODE = S.CODE /\ '
         r'S_raw_root.SOURCES[0].AST = pcunit_cast_projection.AST /\ '
         r'S_raw_child.SOURCES[0].AST = pcunit_cast_projection.AST /\ '
         r'$origin_node(S_raw_root.SOURCES, porigin_cast_return) = (statement_cast_return) /\ '
         r'$origin_node(S_raw_child.SOURCES, porigin_cast_return) = (statement_cast_return) /\ '
         r'$compiled_read(S_raw_root, porigin_cast) = eps /\ '
         r'$compiled_read(S_raw_child, porigin_integer) = (PINT i_child) /\ '
         r'~$ob_object_error_handler_tail(S_raw_root, pfunction_handler, [statement_cast_return]) /\ '
         r'~$ob_object_error_handler_tail(S_raw_child, pfunction_handler, [statement_cast_return])')]
    for part, codepath, line in [('root', 'pcpath_cast', 'z_cast'),
                                 ('child', 'pcpath_integer', 'z_integer')]:
        expected, wrong = ('false', 'true') if part == 'root' else ('true', 'false')
        checks += [('each own ' + part + ' CODE record retains its actual line and emitted or folded flag',
            '$code_expression(pfunction_' + part + '_flag.CODE.EXPRESSIONS, ' + codepath + ') = ((' + line + ', ' + wrong + r')) /\ '
            '$code_expression(pfunction_' + part + '_line.CODE.EXPRESSIONS, ' + codepath + ') = ((z_' + part + '_bad, ' + expected + r')) /\ '
            'z_' + part + '_bad =/= ' + line + r' /\ '
            '~$ob_object_error_handler_tail(S, pfunction_' + part + r'_flag, [statement_cast_return]) /\ '
            '~$ob_object_error_handler_tail(S, pfunction_' + part + '_line, [statement_cast_return])')]
    for suffix, value, label in [
            ('child_other', 'PINT i_integer_other', 'a distinct wrong integer cannot replace the raw child pool'),
            ('child_false', 'PBOOL false', 'Boolean FALSE cannot replace the exact integer child pool'),
            ('child_float', 'PFLOAT 0', 'FLOAT zero cannot replace the exact integer child pool')]:
        state = 'S_' + suffix + '_read'
        checks += [(label, r'i_integer_other =/= i_child /\ '
            '$compiled_read(' + state + r', porigin_cast) = eps /\ '
            '$compiled_read(' + state + ', porigin_integer) = (' + value + r') /\ '
            '~$ob_object_error_handler_tail(' + state + ', pfunction_handler, [statement_cast_return])')]
    checks += [
        ('a locally folded root refuses even with matching integer source and both populated typed values',
         r'$compiled_read(S_root_folded, porigin_cast) = (PFLOAT n_return) /\ '
         r'$compiled_read(S_root_folded, porigin_integer) = (PINT i_child) /\ '
         r'~$ob_object_error_handler_tail(S_root_folded, pfunction_handler, [statement_cast_return])'),
        ('a local unread root pool is not authority and cannot supply its Boolean FALSE value',
         r'$compiled_read(S_root_unread, porigin_cast) = eps /\ '
         r'$compiled_read(S_root_unread, porigin_integer) = (PINT i_child) /\ '
         r'$ob_object_error_handler_tail(S_root_unread, pfunction_handler, [statement_cast_return])'),
        ('NORMAL is required even when a non-NORMAL no-op satisfies a tautological result update',
         r'S_non_normal.COMPLETION =/= NORMAL /\ S_non_normal.RESULT = KNOWN (PFLOAT n_return) /\ '
         r'$cast_apply(S_non_normal, CASTFLOAT, PINT i_child, z_cast) = S_non_normal /\ '
         r'$cast_apply(S_non_normal, CASTFLOAT, PINT i_child, z_cast) = S_non_normal[.RESULT = KNOWN (PFLOAT n_return)] /\ '
         r'~$ob_object_error_handler_tail(S_non_normal, pfunction_handler, [statement_cast_return])')]
    checks += [('the own emitted cast Return retains its function unit and body',
        r'pfunction_cast_unit.CODE.UNIT =/= n_cast_handler /\ '
        r'pfunction_cast_body.BODY =/= pfunction_handler.BODY /\ '
        r'~$ob_object_error_handler_tail(S, pfunction_cast_unit, [statement_cast_return]) /\ '
        r'~$ob_object_error_handler_tail(S, pfunction_cast_body, [statement_cast_return])')]
    conditions = []
    for state in ['S_cast_scratch', 'S_integer_scratch', 'S_false_scratch']:
        conditions += ['$call_current_valid(' + state + ')', '$dz_raw(' + state + ') = S_request',
                       '$ob_object_division_error_capture(' + state + ', S_generated) = eps']
    checks += [('consumed FLOAT result, integer input and FALSE cannot replace resumed NULL scratch', r' /\ '.join(conditions))]
    for suffixes, admitted, label in [
            (['minus_one', 'minimum'], True,
             'local raw negative and MIN children admit only their quiet rounded binary64 cast results'),
            (['above', 'below'], False,
             'local out-of-range children refuse despite matching raw and pool facts')]:
        conditions = []
        for suffix in suffixes:
            state, child, result, statement = ('S_local_' + suffix, 'i_local_' + suffix + '_child',
                'n_local_' + suffix + '_return', 'statement_local_' + suffix)
            conditions += [state + '.CODE = S.CODE', state + '.SOURCES[0].AST = pcunit_cast_projection.AST',
                '$origin_node(' + state + '.SOURCES, porigin_cast_return) = (' + statement + ')',
                '$origin_node(' + state + '.SOURCES, porigin_cast) = (expression_local_' + suffix + ')',
                '$origin_node(' + state + '.SOURCES, porigin_integer) = (NScalarInt (INTEGER ' + child + ') metadata_integer)',
                '$compiled_read(' + state + ', porigin_cast) = eps',
                '$compiled_read(' + state + ', porigin_integer) = (PINT ' + child + ')',
                result + ' = $float_of_int(' + child + ')']
            if admitted:
                conditions += ['$long_range(' + child + ')',
                    '$cast_apply(' + state + ', CASTFLOAT, PINT ' + child + ', z_cast) = ' + state + '[.RESULT = KNOWN (PFLOAT ' + result + ')]']
            else:
                conditions += ['~$long_range(' + child + ')']
            conditions += [('' if admitted else '~') + '$ob_object_error_handler_tail(' + state + ', pfunction_handler, [' + statement + '])']
        checks += [(label, r' /\ '.join(conditions))]
    checks += [('canonical cast keyword: own kind2 remains admitted',
        r'$plstyle(metadata_cast) = 2 /\ '
        r'$compiled_read(S, porigin_cast) = eps /\ '
        r'$compiled_read(S, porigin_integer) = (PINT i_child) /\ '
        r'$ob_object_error_handler_tail(S, pfunction_handler, [statement_cast_return])')]
    for style, kind in [('double', 1), ('real', 3), ('missing', 0)]:
        state = 'S_style_' + style
        checks += [('canonical cast keyword: ' + style + ' metadata refuses locally',
            '$plstyle(metadata_cast_' + style + ') = ' + str(kind) + r' /\ '
            + state + r'.CODE = S.CODE /\ ' + state + r'.POOLS = S.POOLS /\ '
            + state + r'.SOURCES[0].AST = pcunit_cast_projection.AST /\ '
            '$origin_node(' + state + '.SOURCES, porigin_cast_return) = (statement_style_' + style + r') /\ '
            '$origin_node(' + state + '.SOURCES, porigin_cast) = (expression_style_' + style + r') /\ '
            '$compiled_read(' + state + r', porigin_cast) = eps /\ '
            '$compiled_read(' + state + r', porigin_integer) = (PINT i_child) /\ '
            '~$ob_object_error_handler_tail(' + state + ', pfunction_handler, [statement_style_' + style + '])')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
