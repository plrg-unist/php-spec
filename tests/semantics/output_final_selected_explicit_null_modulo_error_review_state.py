#!/usr/bin/env python3
"""Explicit NULL callbacks retain own Return authority and real FINAL retirement."""
import output_final_selected_explicit_null_modulo_error_state as author
import output_final_selected_both_mask_modulo_error_review_state as homogeneous
import output_final_selected_mixed_modulo_error_review_state as mixed

runner = homogeneous.runner
PREFIX = author.PREFIX
BASES = {'warning-right-cv-pair': homogeneous,
         'warning-deprecated-constant-float': mixed}
CASES = {name: author.sources.CASES['native-selected-explicit-null-modulo-error-' + name]
         for name in BASES}


def authority(name, fixture, path):
    bindings, checks = BASES[name].authority(name, fixture, path)
    bindings += author.return_bindings(name)
    bindings += [
        'statement_explicit_true = NStmtReturn (NExprConstFetch (NName (BYTES "dHJ1ZQ==") metadata_explicit_null_name) metadata_explicit_null) metadata_explicit_return',
        'statement_explicit_bare = NStmtReturn ABSENT metadata_explicit_return',
        'z_explicit_bad = $(z_explicit_null + 1)',
        'pfunction_explicit_line = pfunction_handler[.CODE = pfunction_handler.CODE[.EXPRESSIONS = (CODEEXPR pcpath_explicit_null z_explicit_bad b_explicit_null) :: pfunction_handler.CODE.EXPRESSIONS]]']
    checks = [(label, author.converted(condition)) for label, condition in checks]
    checks += [
        ('the genuine explicit Return retains its own NULL source while the implicit tail stays compatible',
         author.return_proof(name) + r' /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, [statement_explicit_return]) /\ '
         r'$ob_object_error_handler_tail(S, pfunction_handler, eps)'),
        ('non-NULL, bare and extra Return tails remain outside the literal NULL source contour',
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_explicit_true]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_explicit_bare]) /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_handler, [statement_explicit_return, statement_explicit_return])'),
        ('the genuine PNULL read cannot authorize a wrong compiled source line for its own Return child',
         r'$compiled_read(S, porigin_explicit_null) = (PNULL) /\ '
         r'$code_expression(pfunction_explicit_line.CODE.EXPRESSIONS, pcpath_explicit_null) = ((z_explicit_bad, b_explicit_null)) /\ '
         r'z_explicit_bad =/= z_explicit_null /\ '
         r'~$ob_object_error_handler_tail(S, pfunction_explicit_line, [statement_explicit_return])')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
