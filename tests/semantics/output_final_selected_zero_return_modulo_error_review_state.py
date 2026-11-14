#!/usr/bin/env python3
"""Integer-zero callbacks retain typed authority and strict FALSE handling."""
import output_final_selected_zero_return_modulo_error_state as author
import output_final_selected_both_mask_modulo_error_review_state as homogeneous
import output_final_selected_mixed_modulo_error_review_state as mixed

runner = homogeneous.runner
PREFIX = author.PREFIX
BASES = {'warning-right-cv-pair': homogeneous,
         'warning-deprecated-constant-float': mixed}
CASES = {name: author.sources.CASES['native-selected-zero-return-modulo-error-' + name]
         for name in BASES}


def authority(name, fixture, path):
    bindings, checks = BASES[name].authority(name, fixture, path)
    bindings += author.return_bindings(name)
    bindings += [
        'statement_zero_one = NStmtReturn (NScalarInt (INTEGER 1) metadata_zero) metadata_zero_return',
        'statement_zero_false = NStmtReturn (NExprConstFetch (NName (BYTES "ZmFsc2U=") metadata_zero) metadata_zero) metadata_zero_return',
        'statement_zero_bare = NStmtReturn ABSENT metadata_zero_return',
        'z_zero_bad = $(z_zero + 1)',
        'pfunction_zero_flag = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_zero z_zero false) :: pfunction_handler.CODE.EXPRESSIONS]]',
        'pfunction_zero_line = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_zero z_zero_bad true) :: pfunction_handler.CODE.EXPRESSIONS]]',
        'pfunction_zero_unit = pfunction_handler[.CODE = pfunction_handler.CODE[.UNIT = $(n_zero_handler + 1)]]',
        'pfunction_zero_body = pfunction_handler[.BODY = pcpath_zero_handler]',
        'S_zero_false_read = S[.POOLS = [{UNIT n_zero_handler, CONSTANTS ([(PCONSTANT pcpath_zero (PBOOL false))])}] ++ S.POOLS]',
        'S_zero_scratch = S[.RESULT = KNOWN (PINT 0)]']
    checks = [(label.replace('NULL finish', 'handled integer-zero finish'), author.converted(condition))
              for label, condition in checks]
    checks += [
        ('the own integer-zero return is consumed normally while resumed scratch remains NULL',
         author.return_proof(name) + r' /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, [statement_zero_return]) /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, eps)'),
        ('nonzero, FALSE, bare and extra tails cannot replace the raw zero Return',
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_zero_one]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_zero_false]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_zero_bare]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_zero_return, statement_zero_return])'),
        ('constructed code, FALSE-read and integer-scratch projections retain their distinct guards',
         r'$code_expression(pfunction_zero_flag.CODE.EXPRESSIONS, pcpath_zero) = ((z_zero, false)) /\ '
         r'$code_expression(pfunction_zero_line.CODE.EXPRESSIONS, pcpath_zero) = ((z_zero_bad, true)) /\ '
         r'z_zero_bad =/= z_zero /\ $compiled_read(S, porigin_zero) = (PINT 0) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_zero_flag, [statement_zero_return]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_zero_line, [statement_zero_return]) /\ '
         r'S_zero_false_read.SOURCES = S.SOURCES /\ S_zero_false_read.CODE = S.CODE /\ '
         r'$compiled_read(S_zero_false_read, porigin_zero) = (PBOOL false) /\ '
         r'~$ob_object_error_handler_tail(S_zero_false_read, pfunction_handler, [statement_zero_return]) /\ '
         r'S_zero_scratch.RESULT = KNOWN (PINT 0) /\ $call_current_valid(S_zero_scratch) /\ '
         r'$dz_raw(S_zero_scratch) = S_request /\ '
         r'$ob_object_division_error_capture(S_zero_scratch, S_generated) = eps'),
        ('the zero Return stays tied to its actual function source unit and body',
         r'pfunction_zero_unit.CODE.UNIT =/= n_zero_handler /\ '
         r'pfunction_zero_body.BODY =/= pfunction_handler.BODY /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_zero_unit, [statement_zero_return]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_zero_body, [statement_zero_return])')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
