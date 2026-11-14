#!/usr/bin/env python3
"""TRUE callbacks retain typed return authority and real FINAL retirement."""
import output_final_selected_true_return_modulo_error_state as author
import output_final_selected_both_mask_modulo_error_review_state as homogeneous
import output_final_selected_mixed_modulo_error_review_state as mixed

runner = homogeneous.runner
PREFIX = author.PREFIX
BASES = {'warning-right-cv-pair': homogeneous,
         'warning-deprecated-constant-float': mixed}
CASES = {name: author.sources.CASES['native-selected-true-return-modulo-error-' + name]
         for name in BASES}


def authority(name, fixture, path):
    bindings, checks = BASES[name].authority(name, fixture, path)
    bindings += author.return_bindings(name)
    bindings += [
        'statement_true_null = NStmtReturn (NExprConstFetch (NName (BYTES "bnVsbA==") metadata_true_name) metadata_true) metadata_true_return',
        'statement_true_false = NStmtReturn (NExprConstFetch (NName (BYTES "ZmFsc2U=") metadata_true_name) metadata_true) metadata_true_return',
        'statement_true_bare = NStmtReturn ABSENT metadata_true_return',
        'z_true_bad = $(z_true + 1)',
        'pfunction_true_flag = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_true z_true false) :: pfunction_handler.CODE.EXPRESSIONS]]',
        'pfunction_true_line = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_true z_true_bad true) :: pfunction_handler.CODE.EXPRESSIONS]]',
        'pfunction_true_unit = pfunction_handler[.CODE = pfunction_handler.CODE[.UNIT = $(n_true_handler + 1)]]',
        'pfunction_true_body = pfunction_handler[.BODY = pcpath_true_handler]',
        'S_true_null_read = S[.POOLS = [{UNIT n_true_handler, CONSTANTS ([(PCONSTANT pcpath_true PNULL)])}] ++ S.POOLS]']
    checks = [(label.replace('NULL finish', 'handled TRUE finish'), author.converted(condition))
              for label, condition in checks]
    checks += [
        ('the own TRUE child and Boolean return stay distinct from reset NULL scratch',
         author.return_proof(name) + r' /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, [statement_true_return]) /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, eps)'),
        ('NULL, FALSE, bare and extra tails cannot replace the raw TRUE Return',
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_true_null]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_true_false]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_true_bare]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_true_return, statement_true_return])'),
        ('constructed code and pool projections cannot borrow the real TRUE child authority',
         r'$code_expression(pfunction_true_flag.CODE.EXPRESSIONS, pcpath_true) = ((z_true, false)) /\ '
         r'$code_expression(pfunction_true_line.CODE.EXPRESSIONS, pcpath_true) = ((z_true_bad, true)) /\ '
         r'z_true_bad =/= z_true /\ $compiled_read(S, porigin_true) = (PBOOL true) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_true_flag, [statement_true_return]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_true_line, [statement_true_return]) /\ '
         r'S_true_null_read.SOURCES = S.SOURCES /\ S_true_null_read.CODE = S.CODE /\ '
         r'$compiled_read(S_true_null_read, porigin_true) = (PNULL) /\ '
         r'~$ob_object_error_handler_tail(S_true_null_read, pfunction_handler, [statement_true_return])'),
        ('the TRUE Return stays tied to its actual function source unit and body',
         r'pfunction_true_unit.CODE.UNIT =/= n_true_handler /\ '
         r'pfunction_true_body.BODY =/= pfunction_handler.BODY /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_true_unit, [statement_true_return]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_true_body, [statement_true_return])')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
