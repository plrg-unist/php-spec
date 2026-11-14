#!/usr/bin/env python3
"""Own quiet FLOAT-to-INT casts require intrinsic notices; projections retain source0."""
import output_final_selected_float_int_cast_return_modulo_error_state as author
import output_final_selected_both_mask_modulo_error_review_state as homogeneous
import output_final_selected_mixed_modulo_error_review_state as mixed

runner = homogeneous.runner
PREFIX = author.PREFIX
BASES = {'warning-right-cv-pair': homogeneous,
         'warning-deprecated-constant-float': mixed}
CASES = {name: author.sources.CASES['native-selected-float-int-cast-return-modulo-error-' + name]
         for name in BASES}
LOCAL = {'negative_zero': ('8000000000000000', 0x8000000000000000, '0'),
         'negative_fraction': ('bff8000000000000', 0xbff8000000000000, '$(-1)'),
         'minimum': ('c3e0000000000000', 0xc3e0000000000000, '$(-9223372036854775808)'),
         'positive_range': ('43e0000000000000', 0x43e0000000000000, '$(-9223372036854775808)'),
         'infinity': ('7ff0000000000000', 0x7ff0000000000000, '0'),
         'quiet_nan': ('7ff8abcdef012345', 0x7ff8abcdef012345, '0'),
         'signaling_nan': ('7ff0000000000001', 0x7ff0000000000001, '0'),
         'short': ('000000000000000', 0, '0'),
         'long': ('00000000000000000', 0, '0'),
         'above': ('10000000000000000', 18446744073709551616, '0'),
         'uppercase': ('000000000000000A', 10, '0'),
         'nonhex': ('000000000000000g', 0, '0')}


def authority(name, fixture, path):
    bindings, checks = BASES[name].authority(name, fixture, path)
    bindings += author.return_bindings(name)
    bindings += [
        'text_float_other = "3ff8000000000000"',
        'n_float_other = $hex_bits(text_float_other, 0)',
        'statement_cast_other = NStmtReturn (NExprCastInt (NScalarFloat (FLOAT text_float_other) metadata_float) metadata_cast) metadata_cast_return',
        'expression_cast_other_kind = NExprCastDouble (NScalarFloat (FLOAT text_float) metadata_float) metadata_cast',
        'statement_cast_other_kind = NStmtReturn expression_cast_other_kind metadata_cast_return',
        'statement_cast_raw = NStmtReturn (NScalarFloat (FLOAT text_float) metadata_float) metadata_cast_return',
        'statement_cast_integer = NStmtReturn (NExprCastInt (NScalarInt (INTEGER 0) metadata_float) metadata_cast) metadata_cast_return',
        'statement_cast_bare = NStmtReturn ABSENT metadata_cast_return',
        'pfunction_cast_unit = pfunction_handler[.CODE = pfunction_handler.CODE[.UNIT = $(n_cast_handler + 1)]]',
        'pfunction_cast_body = pfunction_handler[.BODY = pcpath_cast_handler]',
        'S_cast_scratch = S[.RESULT = KNOWN (PINT i_return)]',
        'S_float_scratch = S[.RESULT = KNOWN (PFLOAT n_child)]',
        'S_false_scratch = S[.RESULT = KNOWN (PBOOL false)]',
        'S.SOURCES = [pcunit_cast_projection]',
        'pcunit_cast_projection.ID = n_cast_handler',
        'S_raw_root = S[.SOURCES = [pcunit_cast_projection[.OCCURRENCES = (PCOCCURRENCE pcpath_cast expression_cast_other_kind) :: pcunit_cast_projection.OCCURRENCES]]]',
        'S_raw_child = S[.SOURCES = [pcunit_cast_projection[.OCCURRENCES = (PCOCCURRENCE pcpath_float (NScalarFloat (FLOAT text_float_other) metadata_float)) :: pcunit_cast_projection.OCCURRENCES]]]']
    bindings += [
        'metadata_cast = (MendFilePos z_cast_end_file) :: (MendLine z_cast_end_line) :: (MendTokenPos z_cast_end_token) :: (Mkind 1) :: metadata_cast_positions',
        'metadata_cast_missing = [(MendFilePos z_cast_end_file), (MendLine z_cast_end_line), (MendTokenPos z_cast_end_token)] ++ metadata_cast_positions',
        'metadata_cast_alias = [(MendFilePos z_cast_end_file), (MendLine z_cast_end_line), (MendTokenPos z_cast_end_token), (Mkind 2)] ++ metadata_cast_positions']
    for style in ['alias', 'missing']:
        bindings += [
            'expression_style_' + style + ' = NExprCastInt (NScalarFloat (FLOAT text_float) metadata_float) metadata_cast_' + style,
            'statement_style_' + style + ' = NStmtReturn expression_style_' + style + ' metadata_cast_return',
            'S_style_' + style + ' = S[.SOURCES = [pcunit_cast_projection[.OCCURRENCES = [(PCOCCURRENCE pcpath_cast_return statement_style_' + style + '), (PCOCCURRENCE pcpath_cast expression_style_' + style + ')] ++ pcunit_cast_projection.OCCURRENCES]]]']
    for part, codepath, line in [('root', 'pcpath_cast', 'z_cast'),
                                 ('child', 'pcpath_float', 'z_float')]:
        expected, wrong = ('false', 'true') if part == 'root' else ('true', 'false')
        bindings += [
            'z_' + part + '_bad = $(' + line + ' + 1)',
            'pfunction_' + part + '_flag = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR ' + codepath + ' ' + line + ' ' + wrong + ') :: pfunction_handler.CODE.EXPRESSIONS]]',
            'pfunction_' + part + '_line = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR ' + codepath + ' z_' + part + '_bad ' + expected + ') :: pfunction_handler.CODE.EXPRESSIONS]]']
    for suffix, value in [('child_other', 'PFLOAT n_float_other'),
                          ('child_integer', 'PINT 0'), ('child_false', 'PBOOL false')]:
        bindings += ['S_' + suffix + '_read = S[.POOLS = [{UNIT n_cast_handler, CONSTANTS ([(PCONSTANT pcpath_float (' + value + '))])}] ++ S.POOLS]']

    bindings += [
        '$code_at(S.CODE, n_cast_handler) = (pcode_cast)',
        'pcode_cast_folded = pcode_cast[.EXPRESSIONS = (CODEEXPR pcpath_cast z_cast true) :: pcode_cast.EXPRESSIONS]',
        'S_root_folded = S[.CODE = pcode_cast_folded :: S.CODE][.POOLS = [{UNIT n_cast_handler, CONSTANTS ([(PCONSTANT pcpath_cast (PINT i_return)), (PCONSTANT pcpath_float (PFLOAT n_child))])}] ++ S.POOLS]',
        'S_root_unread = S[.POOLS = [{UNIT n_cast_handler, CONSTANTS ([(PCONSTANT pcpath_cast (PBOOL false)), (PCONSTANT pcpath_float (PFLOAT n_child))])}] ++ S.POOLS]',
        'S_non_normal = S[.COMPLETION = BUDGET][.RESULT = KNOWN (PINT i_return)]']
    for suffix, (text, child, result) in LOCAL.items():
        bindings += [
            'text_local_' + suffix + ' = "' + text + '"',
            'n_local_' + suffix + '_child = ' + str(child),
            'i_local_' + suffix + '_return = ' + result,
            'expression_local_' + suffix + ' = NExprCastInt (NScalarFloat (FLOAT text_local_' + suffix + ') metadata_float) metadata_cast',
            'statement_local_' + suffix + ' = NStmtReturn expression_local_' + suffix + ' metadata_cast_return',
            'pcunit_local_' + suffix + ' = pcunit_cast_projection[.OCCURRENCES = [(PCOCCURRENCE pcpath_cast_return statement_local_' + suffix + '), (PCOCCURRENCE pcpath_cast expression_local_' + suffix + '), (PCOCCURRENCE pcpath_float (NScalarFloat (FLOAT text_local_' + suffix + ') metadata_float))] ++ pcunit_cast_projection.OCCURRENCES]',
            'S_local_' + suffix + ' = S[.SOURCES = [pcunit_local_' + suffix + ']][.POOLS = [{UNIT n_cast_handler, CONSTANTS ([(PCONSTANT pcpath_float (PFLOAT n_local_' + suffix + '_child))])}] ++ S.POOLS]']
    bindings += ['S_suppressed = S_local_positive_range[.REPORTING = 0][.ERRORHANDLER = {CALLBACK eps, LEVELS 0}][.ERRORFATALTRACE = eps]']
    checks = [(label.replace('NULL finish', 'handled cast-integer finish'), author.converted(condition))
              for label, condition in checks]
    checks += [
        ('the own emitted cast retains its PFLOAT child, intrinsically empty vector and PINT result',
         author.return_proof(name) + r' /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, [statement_cast_return])'),
        ('different float, cast kind, raw float, integer and bare or extra Returns cannot replace the body',
         r'n_float_other =/= n_child /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_cast_other]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_cast_other_kind]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_cast_raw]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_cast_integer]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_cast_bare]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_cast_return, statement_cast_return])'),
        ('local root and child occurrence shadows refuse despite unchanged Return and compiled reads',
         r'S_raw_root.CODE = S.CODE /\ S_raw_child.CODE = S.CODE /\ '
         r'S_raw_root.SOURCES[0].AST = pcunit_cast_projection.AST /\ '
         r'S_raw_child.SOURCES[0].AST = pcunit_cast_projection.AST /\ '
         r'$origin_node(S_raw_root.SOURCES, porigin_cast_return) = (statement_cast_return) /\ '
         r'$origin_node(S_raw_child.SOURCES, porigin_cast_return) = (statement_cast_return) /\ '
         r'$compiled_read(S_raw_root, porigin_cast) = eps /\ '
         r'$compiled_read(S_raw_child, porigin_float) = (PFLOAT n_child) /\ '
         r'~$ob_object_error_handler_tail(S_raw_root, pfunction_handler, [statement_cast_return]) /\ '
         r'~$ob_object_error_handler_tail(S_raw_child, pfunction_handler, [statement_cast_return])')]
    for part, codepath, line in [('root', 'pcpath_cast', 'z_cast'),
                                 ('child', 'pcpath_float', 'z_float')]:
        expected, wrong = ('false', 'true') if part == 'root' else ('true', 'false')
        checks += [('each own ' + part + ' CODE record retains its actual line and emitted or folded flag',
            '$code_expression(pfunction_' + part + '_flag.CODE.EXPRESSIONS, ' + codepath + ') = ((' + line + ', ' + wrong + r')) /\ '
            '$code_expression(pfunction_' + part + '_line.CODE.EXPRESSIONS, ' + codepath + ') = ((z_' + part + '_bad, ' + expected + r')) /\ '
            'z_' + part + '_bad =/= ' + line + r' /\ '
            '~$ob_object_error_handler_tail(S, pfunction_' + part + r'_flag, [statement_cast_return]) /\ '
            '~$ob_object_error_handler_tail(S, pfunction_' + part + '_line, [statement_cast_return])')]
    for suffix, value, label in [
            ('child_other', 'PFLOAT n_float_other', 'different bits cannot replace the raw FLOAT child pool'),
            ('child_integer', 'PINT 0', 'PINT zero cannot replace the raw PFLOAT child pool'),
            ('child_false', 'PBOOL false', 'Boolean FALSE cannot replace the raw PFLOAT child pool')]:
        state = 'S_' + suffix + '_read'
        checks += [(label, r'n_float_other =/= n_child /\ '
            '$compiled_read(' + state + r', porigin_cast) = eps /\ '
            '$compiled_read(' + state + ', porigin_float) = (' + value + r') /\ '
            '~$ob_object_error_handler_tail(' + state + ', pfunction_handler, [statement_cast_return])')]
    checks += [
        ('a locally folded root refuses even with matching raw child and populated PINT result',
         r'$compiled_read(S_root_folded, porigin_cast) = (PINT i_return) /\ '
         r'$compiled_read(S_root_folded, porigin_float) = (PFLOAT n_child) /\ '
         r'~$ob_object_error_handler_tail(S_root_folded, pfunction_handler, [statement_cast_return])'),
        ('a local unread root pool is not authority and cannot supply its Boolean FALSE value',
         r'$compiled_read(S_root_unread, porigin_cast) = eps /\ '
         r'$compiled_read(S_root_unread, porigin_float) = (PFLOAT n_child) /\ '
         r'$ob_object_error_handler_tail(S_root_unread, pfunction_handler, [statement_cast_return])'),
        ('NORMAL is required even when a non-NORMAL no-op satisfies a tautological result update',
         r'S_non_normal.COMPLETION =/= NORMAL /\ S_non_normal.RESULT = KNOWN (PINT i_return) /\ '
         r'$cast_apply(S_non_normal, CASTINT, PFLOAT n_child, z_cast) = S_non_normal /\ '
         r'$cast_apply(S_non_normal, CASTINT, PFLOAT n_child, z_cast) = S_non_normal[.RESULT = KNOWN (PINT i_return)] /\ '
         r'~$ob_object_error_handler_tail(S_non_normal, pfunction_handler, [statement_cast_return])')]
    checks += [('the own emitted cast Return retains its function unit and body',
        r'pfunction_cast_unit.CODE.UNIT =/= n_cast_handler /\ '
        r'pfunction_cast_body.BODY =/= pfunction_handler.BODY /\ '
        r'~$ob_object_error_handler_tail(S, pfunction_cast_unit, [statement_cast_return]) /\ '
        r'~$ob_object_error_handler_tail(S, pfunction_cast_body, [statement_cast_return])')]
    conditions = []
    for state in ['S_cast_scratch', 'S_float_scratch', 'S_false_scratch']:
        conditions += ['$call_current_valid(' + state + ')', '$dz_raw(' + state + ') = S_request',
                       '$ob_object_division_error_capture(' + state + ', S_generated) = eps']
    checks += [('consumed integer, raw FLOAT and FALSE cannot replace resumed NULL scratch', r' /\ '.join(conditions))]
    for suffixes, admitted, valid, label in [
            (['negative_zero', 'negative_fraction', 'minimum'], True, True,
             'local fitting negative values retain intrinsic quietness and exact signed integer results'),
            (['positive_range', 'infinity', 'quiet_nan', 'signaling_nan'], False, True,
             'local range and nonfinite children refuse despite their correct intrinsic result and notice'),
            (['short', 'long', 'above'], False, False,
             'local width15 and width17 payloads refuse before partial binary64 decoding'),
            (['uppercase', 'nonhex'], False, False,
             'local final uppercase and nonhex glyphs refuse before partial decoding')]:
        conditions = []
        for suffix in suffixes:
            state, text, child, result, statement = ('S_local_' + suffix, 'text_local_' + suffix,
                'n_local_' + suffix + '_child', 'i_local_' + suffix + '_return', 'statement_local_' + suffix)
            conditions += [state + '.CODE = S.CODE', state + '.SOURCES[0].AST = pcunit_cast_projection.AST',
                '$origin_node(' + state + '.SOURCES, porigin_cast_return) = (' + statement + ')',
                '$origin_node(' + state + '.SOURCES, porigin_cast) = (expression_local_' + suffix + ')',
                '$origin_node(' + state + '.SOURCES, porigin_float) = (NScalarFloat (FLOAT ' + text + ') metadata_float)',
                '$compiled_read(' + state + ', porigin_cast) = eps',
                '$compiled_read(' + state + ', porigin_float) = (PFLOAT ' + child + ')']
            if valid:
                conditions += ['|' + text + '| = 16',
                    '$evaluate(NScalarFloat (FLOAT ' + text + ') metadata_float) = VALUE (PFLOAT ' + child + ')',
                    '$float_long(' + child + ', false) = (' + result + ', ' + ('eps' if admitted else '[RANGEWARNING]') + ')',
                    '$long_range(' + result + ')']
            if admitted:
                conditions += ['$cast_apply(' + state + ', CASTINT, PFLOAT ' + child + ', z_cast) = ' + state + '[.RESULT = KNOWN (PINT ' + result + ')]']
            conditions += [('' if admitted else '~') + '$ob_object_error_handler_tail(' + state + ', pfunction_handler, [' + statement + '])']
        checks += [(label, r' /\ '.join(conditions))]
    checks += [('suppressed finite overflow cannot substitute observed silence for an empty intrinsic vector',
        r'S_suppressed.COMPLETION = NORMAL /\ S_suppressed.REPORTING = 0 /\ '
        r'S_suppressed.ERRORHANDLER.CALLBACK = eps /\ S_suppressed.ERRORFATALTRACE = eps /\ '
        r'$compiled_read(S_suppressed, porigin_cast) = eps /\ '
        r'$compiled_read(S_suppressed, porigin_float) = (PFLOAT n_local_positive_range_child) /\ '
        r'$float_long(n_local_positive_range_child, false) = (i_local_positive_range_return, [RANGEWARNING]) /\ '
        r'$cast_apply(S_suppressed, CASTINT, PFLOAT n_local_positive_range_child, z_cast) = S_suppressed[.RESULT = KNOWN (PINT i_local_positive_range_return)] /\ '
        r'~$ob_object_error_handler_tail(S_suppressed, pfunction_handler, [statement_local_positive_range])')]
    checks += [('canonical cast keyword: own kind1 remains admitted',
        r'$plstyle(metadata_cast) = 1 /\ '
        r'$compiled_read(S, porigin_cast) = eps /\ '
        r'$compiled_read(S, porigin_float) = (PFLOAT n_child) /\ '
        r'$ob_object_error_handler_tail(S, pfunction_handler, [statement_cast_return])')]
    for style, kind in [('alias', 2), ('missing', 0)]:
        state = 'S_style_' + style
        checks += [('canonical cast keyword: ' + style + ' metadata refuses locally',
            '$plstyle(metadata_cast_' + style + ') = ' + str(kind) + r' /\ '
            + state + r'.CODE = S.CODE /\ ' + state + r'.POOLS = S.POOLS /\ '
            + state + r'.SOURCES[0].AST = pcunit_cast_projection.AST /\ '
            '$origin_node(' + state + '.SOURCES, porigin_cast_return) = (statement_style_' + style + r') /\ '
            '$origin_node(' + state + '.SOURCES, porigin_cast) = (expression_style_' + style + r') /\ '
            '$compiled_read(' + state + r', porigin_cast) = eps /\ '
            '$compiled_read(' + state + r', porigin_float) = (PFLOAT n_child) /\ '
            '~$ob_object_error_handler_tail(' + state + ', pfunction_handler, [statement_style_' + style + '])')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
