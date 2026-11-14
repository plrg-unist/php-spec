#!/usr/bin/env python3
"""Own FALSE returns report ordered diagnostics before FINAL MOD retirement."""
import output_final_selected_false_return_modulo_error_state as author
import output_final_selected_both_mask_modulo_error_review_state as homogeneous
import output_final_selected_mixed_modulo_error_review_state as mixed

runner = homogeneous.runner
PREFIX = author.PREFIX
BASES = {'warning-right-cv-pair': homogeneous,
         'warning-deprecated-constant-float': mixed}
CASES = {name: author.sources.CASES['native-selected-false-return-modulo-error-' + name]
         for name in BASES}


def authority(name, fixture, path):
    bindings, checks = BASES[name].authority(name, fixture, path)
    bindings += author.return_bindings(name)
    bindings += [
        'statement_false_true = NStmtReturn (NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_false_name) metadata_false) metadata_false_return',
        'statement_false_null = NStmtReturn (NExprConstFetch (NName (BYTES "bnVsbA==") metadata_false_name) metadata_false) metadata_false_return',
        'statement_false_zero = NStmtReturn (NScalarInt (INTEGER 0) metadata_false) metadata_false_return',
        'statement_false_bare = NStmtReturn ABSENT metadata_false_return',
        'z_false_bad = $(z_false + 1)',
        'pfunction_false_flag = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_false z_false false) :: pfunction_handler.CODE.EXPRESSIONS]]',
        'pfunction_false_line = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_false z_false_bad true) :: pfunction_handler.CODE.EXPRESSIONS]]',
        'pfunction_false_unit = pfunction_handler[.CODE = pfunction_handler.CODE[.UNIT = $(n_false_handler + 1)]]',
        'pfunction_false_body = pfunction_handler[.BODY = pcpath_false_handler]',
        'S_false_zero_read = S[.POOLS = [{UNIT n_false_handler, CONSTANTS ([(PCONSTANT pcpath_false (PINT 0))])}] ++ S.POOLS]',
        'S_false_true_read = S[.POOLS = [{UNIT n_false_handler, CONSTANTS ([(PCONSTANT pcpath_false (PBOOL true))])}] ++ S.POOLS]',
        'S_false_direct_finish = $error_handler_finish(S_handler, perrorcall_return)',
        'S_false_scratch = S[.RESULT = KNOWN (PBOOL false)]']
    checks = [(label.replace('NULL finish', 'FALSE default reporting'),
               author.converted(name, condition)) for label, condition in checks]
    resumed = 'S' if name == 'warning-right-cv-pair' else 'S_resume'
    checks += [
        ('the own raw FALSE child and actual fallback remain distinct from resumed NULL scratch',
         author.return_proof(name) + r' /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, [statement_false_return]) /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, eps)'),
        ('TRUE, NULL, integer zero, bare and extra tails cannot replace the own raw FALSE Return',
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_false_true]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_false_null]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_false_zero]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_false_bare]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_false_return, statement_false_return])'),
        ('constructed first child-code flag and line projections refuse the genuine FALSE source',
         r'$code_expression(pfunction_false_flag.CODE.EXPRESSIONS, pcpath_false) = ((z_false, false)) /\ '
         r'$code_expression(pfunction_false_line.CODE.EXPRESSIONS, pcpath_false) = ((z_false_bad, true)) /\ '
         r'z_false_bad =/= z_false /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_false_flag, [statement_false_return]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_false_line, [statement_false_return])'),
        ('equal-zero integer and TRUE pool projections cannot authenticate the raw Boolean FALSE read',
         r'$compiled_read(S, porigin_false) = (PBOOL false) /\ '
         r'S_false_zero_read.SOURCES = S.SOURCES /\ S_false_zero_read.CODE = S.CODE /\ '
         r'S_false_true_read.SOURCES = S.SOURCES /\ S_false_true_read.CODE = S.CODE /\ '
         r'$compiled_read(S_false_zero_read, porigin_false) = (PINT 0) /\ '
         r'$compiled_read(S_false_true_read, porigin_false) = (PBOOL true) /\ '
         r'~$ob_object_error_handler_tail(S_false_zero_read, pfunction_handler, [statement_false_return]) /\ '
         r'~$ob_object_error_handler_tail(S_false_true_read, pfunction_handler, [statement_false_return])'),
        ('the FALSE Return stays tied to its own function source unit and body',
         r'pfunction_false_unit.CODE.UNIT =/= n_false_handler /\ '
         r'pfunction_false_body.BODY =/= pfunction_handler.BODY /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_false_unit, [statement_false_return]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_false_body, [statement_false_return])'),
        ('the genuine atomic FALSE fallback appends its diagnostic before the same normal finish',
         '$dz_raw(S_handler) = ' + resumed + r' /\ '
         r'S_false_direct_finish.RESULT = KNOWN PNULL /\ '
         r'S_false_direct_finish.BASE = BASE_VALUE (KNOWN PNULL) /\ '
         'S_false_direct_finish.ERRORHANDLER = ' + resumed + r'.ERRORHANDLER /\ '
         r'S_false_direct_finish.EVENTS = S_handler.EVENTS /\ '
         + resumed + '.EVENTS = S_false_direct_finish.EVENTS ++ [' + author.diagnostics(name)[0] + r'] /\ '
         + resumed + r' =/= S_false_direct_finish'),
        ('consumed FALSE cannot remain in capture scratch despite the same raw MOD Error',
         r'S_false_scratch.RESULT = KNOWN (PBOOL false) /\ $call_current_valid(S_false_scratch) /\ '
         r'$dz_raw(S_false_scratch) = S_request /\ '
         r'$ob_object_division_error_capture(S_false_scratch, S_generated) = eps')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
