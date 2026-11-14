#!/usr/bin/env python3
"""Own float Returns retain exact bits; malformed and local projections stay separate."""
import output_final_selected_float_return_modulo_error_state as author
import output_final_selected_both_mask_modulo_error_review_state as homogeneous
import output_final_selected_mixed_modulo_error_review_state as mixed

runner = homogeneous.runner
PREFIX = author.PREFIX
BASES = {'warning-right-cv-pair': homogeneous,
         'warning-deprecated-constant-float': mixed}
CASES = {name: author.sources.CASES['native-selected-float-return-modulo-error-' + name]
         for name in BASES}
LOCAL = {'negative_zero': ('8000000000000000', 9223372036854775808),
         'nan_payload': ('7ff8abcdef012345', 0x7ff8abcdef012345),
         'nan_maximum': ('ffffffffffffffff', 18446744073709551615),
         'short': ('000000000000000', 0),
         'long': ('00000000000000000', 0),
         'above': ('10000000000000000', 18446744073709551616),
         'uppercase': ('000000000000000A', 10),
         'nonhex': ('000000000000000g', 0)}


def authority(name, fixture, path):
    bindings, checks = BASES[name].authority(name, fixture, path)
    bindings += author.return_bindings(name)
    bindings += [
        'text_float_other = "3ff8000000000000"',
        'n_float_other = 4609434218613702656',
        'statement_float_other = NStmtReturn (NScalarFloat (FLOAT text_float_other) metadata_float) metadata_float_return',
        'statement_float_integer = NStmtReturn (NScalarInt (INTEGER 0) metadata_float) metadata_float_return',
        'statement_float_false = NStmtReturn (NExprConstFetch (NName (BYTES "ZmFsc2U=") metadata_float) metadata_float) metadata_float_return',
        'statement_float_bare = NStmtReturn ABSENT metadata_float_return',
        'z_float_bad = $(z_float + 1)',
        'pfunction_float_flag = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_float z_float false) :: pfunction_handler.CODE.EXPRESSIONS]]',
        'pfunction_float_line = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_float z_float_bad true) :: pfunction_handler.CODE.EXPRESSIONS]]',
        'pfunction_float_unit = pfunction_handler[.CODE = pfunction_handler.CODE[.UNIT = $(n_float_handler + 1)]]',
        'pfunction_float_body = pfunction_handler[.BODY = pcpath_float_handler]',
        'S_float_other_read = S[.POOLS = [{UNIT n_float_handler, CONSTANTS ([(PCONSTANT pcpath_float (PFLOAT n_float_other))])}] ++ S.POOLS]',
        'S_float_integer_read = S[.POOLS = [{UNIT n_float_handler, CONSTANTS ([(PCONSTANT pcpath_float (PINT 0))])}] ++ S.POOLS]',
        'S_float_scratch = S[.RESULT = KNOWN (PFLOAT n_return)]',
        'S_float_false_scratch = S[.RESULT = KNOWN (PBOOL false)]',
        'S.SOURCES = [pcunit_float_projection]',
        'pcunit_float_projection.ID = n_float_handler']
    for suffix, (text, bits) in LOCAL.items():
        bindings += [
            'text_local_' + suffix + ' = "' + text + '"',
            'n_local_' + suffix + ' = ' + str(bits),
            'statement_local_' + suffix + ' = NStmtReturn (NScalarFloat (FLOAT text_local_' + suffix + ') metadata_float) metadata_float_return',
            'pcunit_local_' + suffix + ' = pcunit_float_projection[.OCCURRENCES = (PCOCCURRENCE pcpath_float_return statement_local_' + suffix + ') :: pcunit_float_projection.OCCURRENCES]',
            'S_local_' + suffix + ' = S[.SOURCES = [pcunit_local_' + suffix + ']][.POOLS = [{UNIT n_float_handler, CONSTANTS ([(PCONSTANT pcpath_float (PFLOAT n_local_' + suffix + '))])}] ++ S.POOLS]']
    bindings += [
        'S_local_zero_read = S_local_negative_zero[.POOLS = [{UNIT n_float_handler, CONSTANTS ([(PCONSTANT pcpath_float (PFLOAT 0))])}] ++ S.POOLS]',
        'S_local_nan_read = S_local_nan_payload[.POOLS = [{UNIT n_float_handler, CONSTANTS ([(PCONSTANT pcpath_float (PFLOAT n_local_nan_maximum))])}] ++ S.POOLS]']
    checks = [(label.replace('NULL finish', 'handled float finish'), author.converted(condition))
              for label, condition in checks]
    checks += [
        ('the exact own float Return retains raw bits and resumes with NULL scratch',
         author.return_proof(name) + r' /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, [statement_float_return]) /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, eps)'),
        ('different float bits, integer zero, FALSE, bare and extra tails cannot replace the raw Return',
         r'text_float_other =/= text_float /\ n_float_other =/= n_return /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_float_other]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_float_integer]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_float_false]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_float_bare]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_float_return, statement_float_return])'),
        ('constructed first child-code flag and line projections refuse the authentic float source',
         r'$code_expression(pfunction_float_flag.CODE.EXPRESSIONS, pcpath_float) = ((z_float, false)) /\ '
         r'$code_expression(pfunction_float_line.CODE.EXPRESSIONS, pcpath_float) = ((z_float_bad, true)) /\ '
         r'z_float_bad =/= z_float /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_float_flag, [statement_float_return]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_float_line, [statement_float_return])'),
        ('different PFLOAT bits and PINT zero reads cannot authenticate the exact float',
         r'$compiled_read(S, porigin_float) = (PFLOAT n_return) /\ '
         r'S_float_other_read.SOURCES = S.SOURCES /\ S_float_other_read.CODE = S.CODE /\ '
         r'S_float_integer_read.SOURCES = S.SOURCES /\ S_float_integer_read.CODE = S.CODE /\ '
         r'$compiled_read(S_float_other_read, porigin_float) = (PFLOAT n_float_other) /\ '
         r'$compiled_read(S_float_integer_read, porigin_float) = (PINT 0) /\ '
         r'~$ob_object_error_handler_tail(S_float_other_read, pfunction_handler, [statement_float_return]) /\ '
         r'~$ob_object_error_handler_tail(S_float_integer_read, pfunction_handler, [statement_float_return])'),
        ('the own float Return retains its function unit and body',
         r'pfunction_float_unit.CODE.UNIT =/= n_float_handler /\ '
         r'pfunction_float_body.BODY =/= pfunction_handler.BODY /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_float_unit, [statement_float_return]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_float_body, [statement_float_return])'),
        ('neither consumed PFLOAT nor FALSE can replace NULL scratch despite the same raw Error',
         r'S_float_scratch.RESULT = KNOWN (PFLOAT n_return) /\ $call_current_valid(S_float_scratch) /\ '
         r'$dz_raw(S_float_scratch) = S_request /\ '
         r'$ob_object_division_error_capture(S_float_scratch, S_generated) = eps /\ '
         r'S_float_false_scratch.RESULT = KNOWN (PBOOL false) /\ $call_current_valid(S_float_false_scratch) /\ '
         r'$dz_raw(S_float_false_scratch) = S_request /\ '
         r'$ob_object_division_error_capture(S_float_false_scratch, S_generated) = eps')]
    for suffixes, admitted, label in [
            (['negative_zero', 'nan_payload', 'nan_maximum'], True,
             'local canonical negative-zero and distinct NaN payload projections admit only the tail'),
            (['short', 'long', 'above'], False,
             'local width15 and width17 projections refuse despite matching raw and pool facts'),
            (['uppercase', 'nonhex'], False,
             'local width16 final uppercase and nonhex glyphs refuse before partial decoding')]:
        conditions = []
        for suffix in suffixes:
            state, text, bits, statement = ('S_local_' + suffix, 'text_local_' + suffix,
                                            'n_local_' + suffix, 'statement_local_' + suffix)
            conditions += [
                state + '.CODE = S.CODE', state + '.SOURCES[0].AST = pcunit_float_projection.AST',
                '$origin_node(' + state + '.SOURCES, porigin_float_return) = (' + statement + ')',
                '$compiled_read(' + state + ', porigin_float) = (PFLOAT ' + bits + ')']
            if admitted:
                conditions += ['|'+ text + '| = 16',
                    '$evaluate(NScalarFloat (FLOAT ' + text + ') metadata_float) = VALUE (PFLOAT ' + bits + ')',
                    '$(' + bits + ' < 18446744073709551616)']
            conditions += [('' if admitted else '~') +
                '$ob_object_error_handler_tail(' + state + ', pfunction_handler, [' + statement + '])']
        checks += [(label, r' /\ '.join(conditions))]
    checks += [
        ('local signed-zero and NaN projections require their exact bits rather than numeric classes',
         r'n_local_negative_zero = 9223372036854775808 /\ '
         r'$float_decode(n_local_nan_payload) = NOTNUMBER n_local_nan_payload /\ '
         r'$float_decode(n_local_nan_maximum) = NOTNUMBER n_local_nan_maximum /\ '
         r'n_local_nan_payload =/= n_local_nan_maximum /\ '
         r'$compiled_read(S_local_zero_read, porigin_float) = (PFLOAT 0) /\ '
         r'$compiled_read(S_local_nan_read, porigin_float) = (PFLOAT n_local_nan_maximum) /\ '
         r'~$ob_object_error_handler_tail(S_local_zero_read, pfunction_handler, [statement_local_negative_zero]) /\ '
         r'~$ob_object_error_handler_tail(S_local_nan_read, pfunction_handler, [statement_local_nan_payload])')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
