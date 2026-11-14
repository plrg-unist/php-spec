#!/usr/bin/env python3
"""Own nonzero integer Returns retain source, exact reads and FINAL retirement."""
import output_final_selected_integer_return_modulo_error_state as author
import output_final_selected_both_mask_modulo_error_review_state as homogeneous
import output_final_selected_mixed_modulo_error_review_state as mixed

runner = homogeneous.runner
PREFIX = author.PREFIX
BASES = {'warning-right-cv-pair': homogeneous,
         'warning-deprecated-constant-float': mixed}
CASES = {name: author.sources.CASES['native-selected-integer-return-modulo-error-' + name]
         for name in BASES}


def authority(name, fixture, path):
    bindings, checks = BASES[name].authority(name, fixture, path)
    bindings += author.return_bindings(name)
    bindings += [
        'i_integer_other = $(i_return + 1)',
        'statement_integer_other = NStmtReturn (NScalarInt (INTEGER i_integer_other) metadata_integer) metadata_integer_return',
        'statement_integer_zero = NStmtReturn (NScalarInt (INTEGER 0) metadata_integer) metadata_integer_return',
        'statement_integer_false = NStmtReturn (NExprConstFetch (NName (BYTES "ZmFsc2U=") metadata_integer) metadata_integer) metadata_integer_return',
        'statement_integer_bare = NStmtReturn ABSENT metadata_integer_return',
        'z_integer_bad = $(z_integer + 1)',
        'pfunction_integer_flag = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_integer z_integer false) :: pfunction_handler.CODE.EXPRESSIONS]]',
        'pfunction_integer_line = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_integer z_integer_bad true) :: pfunction_handler.CODE.EXPRESSIONS]]',
        'pfunction_integer_unit = pfunction_handler[.CODE = pfunction_handler.CODE[.UNIT = $(n_integer_handler + 1)]]',
        'pfunction_integer_body = pfunction_handler[.BODY = pcpath_integer_handler]',
        'S_integer_other_read = S[.POOLS = [{UNIT n_integer_handler, CONSTANTS ([(PCONSTANT pcpath_integer (PINT i_integer_other))])}] ++ S.POOLS]',
        'S_integer_false_read = S[.POOLS = [{UNIT n_integer_handler, CONSTANTS ([(PCONSTANT pcpath_integer (PBOOL false))])}] ++ S.POOLS]',
        'S_integer_scratch = S[.RESULT = KNOWN (PINT i_return)]',
        'S_integer_false_scratch = S[.RESULT = KNOWN (PBOOL false)]',
        'S.SOURCES = [pcunit_integer_range]',
        'pcunit_integer_range.ID = n_integer_handler']
    for suffix, value in [('negative', '$(-1)'), ('minimum', '$(-9223372036854775808)'),
                          ('above', '9223372036854775808'), ('below', '$(-9223372036854775809)')]:
        bindings += [
            'i_range_' + suffix + ' = ' + value,
            'statement_range_' + suffix + ' = NStmtReturn (NScalarInt (INTEGER i_range_' + suffix + ') metadata_integer) metadata_integer_return',
            'pcunit_range_' + suffix + ' = pcunit_integer_range[.OCCURRENCES = (PCOCCURRENCE pcpath_integer_return statement_range_' + suffix + ') :: pcunit_integer_range.OCCURRENCES]',
            'S_range_' + suffix + ' = S[.SOURCES = [pcunit_range_' + suffix + ']][.POOLS = [{UNIT n_integer_handler, CONSTANTS ([(PCONSTANT pcpath_integer (PINT i_range_' + suffix + '))])}] ++ S.POOLS]']
    checks = [(label.replace('NULL finish', 'handled integer finish'), author.converted(condition))
              for label, condition in checks]
    checks += [
        ('the exact own integer Return is non-FALSE and resumes with NULL scratch',
         author.return_proof(name) + r' /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, [statement_integer_return]) /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, eps)'),
        ('different integer, zero, FALSE, bare and extra tails cannot replace this raw Return',
         r'$long_range(i_integer_other) /\ i_integer_other =/= i_return /\ i_integer_other =/= 0 /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_integer_other]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_integer_zero]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_integer_false]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_integer_bare]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_integer_return, statement_integer_return])'),
        ('constructed first child-code flag and line projections refuse the authentic integer source',
         r'$code_expression(pfunction_integer_flag.CODE.EXPRESSIONS, pcpath_integer) = ((z_integer, false)) /\ '
         r'$code_expression(pfunction_integer_line.CODE.EXPRESSIONS, pcpath_integer) = ((z_integer_bad, true)) /\ '
         r'z_integer_bad =/= z_integer /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_integer_flag, [statement_integer_return]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_integer_line, [statement_integer_return])'),
        ('another nonzero integer and Boolean FALSE reads cannot authenticate the exact own PINT',
         r'$compiled_read(S, porigin_integer) = (PINT i_return) /\ '
         r'S_integer_other_read.SOURCES = S.SOURCES /\ S_integer_other_read.CODE = S.CODE /\ '
         r'S_integer_false_read.SOURCES = S.SOURCES /\ S_integer_false_read.CODE = S.CODE /\ '
         r'$compiled_read(S_integer_other_read, porigin_integer) = (PINT i_integer_other) /\ '
         r'$compiled_read(S_integer_false_read, porigin_integer) = (PBOOL false) /\ '
         r'~$ob_object_error_handler_tail(S_integer_other_read, pfunction_handler, [statement_integer_return]) /\ '
         r'~$ob_object_error_handler_tail(S_integer_false_read, pfunction_handler, [statement_integer_return])'),
        ('the own integer Return retains its function unit and body',
         r'pfunction_integer_unit.CODE.UNIT =/= n_integer_handler /\ '
         r'pfunction_integer_body.BODY =/= pfunction_handler.BODY /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_integer_unit, [statement_integer_return]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_integer_body, [statement_integer_return])'),
        ('neither consumed integer nor FALSE can replace NULL scratch despite the same raw Error',
         r'S_integer_scratch.RESULT = KNOWN (PINT i_return) /\ $call_current_valid(S_integer_scratch) /\ '
         r'$dz_raw(S_integer_scratch) = S_request /\ '
         r'$ob_object_division_error_capture(S_integer_scratch, S_generated) = eps /\ '
         r'S_integer_false_scratch.RESULT = KNOWN (PBOOL false) /\ $call_current_valid(S_integer_false_scratch) /\ '
         r'$dz_raw(S_integer_false_scratch) = S_request /\ '
         r'$ob_object_division_error_capture(S_integer_false_scratch, S_generated) = eps')]
    for suffixes, admitted, label in [
            (['negative', 'minimum'], True, 'constructed negative and MININT occurrence/pool projections admit only the local tail'),
            (['above', 'below'], False, 'constructed out-of-range occurrence/pool projections refuse despite matching raw/read facts')]:
        conditions = []
        for suffix in suffixes:
            state, value, statement = 'S_range_' + suffix, 'i_range_' + suffix, 'statement_range_' + suffix
            conditions += [
                ('' if admitted else '~') + '$long_range(' + value + ')', value + ' =/= 0',
                state + '.CODE = S.CODE', state + '.SOURCES[0].AST = pcunit_integer_range.AST',
                '$origin_node(' + state + '.SOURCES, porigin_integer_return) = (' + statement + ')',
                '$compiled_read(' + state + ', porigin_integer) = (PINT ' + value + ')',
                ('' if admitted else '~') + '$ob_object_error_handler_tail(' + state + ', pfunction_handler, [' + statement + '])']
        checks += [(label, r' /\ '.join(conditions))]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
