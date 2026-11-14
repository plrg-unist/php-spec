#!/usr/bin/env python3
"""Bare callbacks retain own statement authority and real FINAL retirement."""
import output_final_selected_bare_return_modulo_error_state as author
import output_final_selected_both_mask_modulo_error_review_state as homogeneous
import output_final_selected_mixed_modulo_error_review_state as mixed

runner = homogeneous.runner
PREFIX = author.PREFIX
BASES = {'warning-right-cv-pair': homogeneous,
         'warning-deprecated-constant-float': mixed}
CASES = {name: author.sources.CASES['native-selected-bare-return-modulo-error-' + name]
         for name in BASES}


def authority(name, fixture, path):
    bindings, checks = BASES[name].authority(name, fixture, path)
    bindings += author.return_bindings(name)
    bindings += [
        'statement_bare_null = NStmtReturn (NExprConstFetch (NName (BYTES "bnVsbA==") metadata_bare_return) metadata_bare_return) metadata_bare_return',
        'statement_bare_true = NStmtReturn (NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_bare_return) metadata_bare_return) metadata_bare_return',
        'z_bare_bad = $(z_bare_return + 1)',
        'pfunction_bare_flag = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_bare_return z_bare_return true) :: pfunction_handler.CODE.EXPRESSIONS]]',
        'pfunction_bare_line = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_bare_return z_bare_bad false) :: pfunction_handler.CODE.EXPRESSIONS]]',
        'pfunction_bare_unit = pfunction_handler[.CODE = pfunction_handler.CODE[.UNIT = $(n_bare_handler + 1)]]',
        'pfunction_bare_body = pfunction_handler[.BODY = pcpath_bare_handler]']
    checks = [(label, author.converted(condition)) for label, condition in checks]
    checks += [
        ('the actual bare Return retains its own statement code without a NULL child or read',
         author.return_proof(name) + r' /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, [statement_bare_return]) /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, eps)'),
        ('expressed NULL, other values and extra tails cannot replace the raw bare Return',
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_bare_null]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_bare_true]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_bare_return, statement_bare_return])'),
        ('raw bare source does not authorize a folded flag or a different emitted statement line',
         r'$code_expression(pfunction_bare_flag.CODE.EXPRESSIONS, pcpath_bare_return) = ((z_bare_return, true)) /\ '
         r'$code_expression(pfunction_bare_line.CODE.EXPRESSIONS, pcpath_bare_return) = ((z_bare_bad, false)) /\ '
         r'z_bare_bad =/= z_bare_return /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_bare_flag, [statement_bare_return]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_bare_line, [statement_bare_return])'),
        ('the bare Return stays tied to its actual function source unit and body',
         r'pfunction_bare_unit.CODE.UNIT =/= n_bare_handler /\ '
         r'pfunction_bare_body.BODY =/= pfunction_handler.BODY /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_bare_unit, [statement_bare_return]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_bare_body, [statement_bare_return])')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
