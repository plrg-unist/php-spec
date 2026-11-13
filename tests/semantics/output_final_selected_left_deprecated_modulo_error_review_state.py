#!/usr/bin/env python3
"""Selected precision-loss return preserves original caches and real retirement."""
import output_final_selected_left_deprecated_modulo_error_state as author
import output_final_selected_warning_modulo_error_review_state as right_review

runner = right_review.runner
PREFIX = author.PREFIX
CASES = {name: author.CASES[name] for name in ['constant-float', 'cv-pair-string']}


def task(phase='INTEGER_RIGHT i_left', conversion='pintegerconversion', cursor='0'):
    return '(INTEGER_OPERATOR_WARNING pintegeroperation (' + phase + ') ' + conversion + ' ' + cursor + ') :: ptask_tail*'


def authority(name, fixture, path):
    if name == 'cv-pair-string':
        bindings, _ = author.lifecycle(name, fixture, path)
        _, checks = right_review.authority('cv-pair', fixture, path)
        before = '$error_handler_finish(S_handler, perrorcall_return) = S /\\ '
        assert checks[0][1].count(before) == 1
        checks[0] = ('the actual Deprecated callback retires both formals before quiet RHS conversion and capture',
            checks[0][1].replace(before,
                '$error_handler_finish(S_handler, perrorcall_return) = S_resume /\\ ') +
            r' /\ S_resume.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion_left 1) :: ptask_tail* /\ '
            r'S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i_left) pintegerconversion 0) :: ptask_tail* /\ '
            r'pintegerconversion.NOTICES = eps /\ S_capture.STORE = S.STORE /\ '
            r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))')
        return bindings, checks

    bindings, _ = author.frontier(name, fixture, path)
    bindings += [
        'S_saved = S[.TODO = ' + task(phase='INTEGER_RIGHT 2') + ']',
        '$integer_conversion(PBOOL false) = (pintegerconversion_false)',
        'S_snapshot = S[.TODO = ' + task(conversion='pintegerconversion_false') + ']',
        'S_cursor = S[.TODO = ' + task(cursor='1') + ']',
        'S_scratch = S[.RESULT = KNOWN (POBJECT pobobjectreturn.OBJECT)]',
        'S_retarget = S[.ERRORHANDLER = S.ERRORHANDLER[.CALLBACK = (PSTRING ($ptascii("h")))]]',
        'S_retarget_raw = $dz_raw(S_retarget)', 'S_retarget_generated = $throwable_transition(S_retarget, S_retarget_raw)',
        'S_both = S[.ERRORHANDLER = S.ERRORHANDLER[.LEVELS = 8194]]',
        'S_both_raw = $dz_raw(S_both)', 'S_both_generated = $throwable_transition(S_both, S_both_raw)']
    return bindings, [
        ('the real precision-loss callback completes LEFT before the original quiet RHS Error',
         author.original(name) + r' /\ $ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'$error_handler_finish(S_handler, perrorcall_return) = S_resume /\ '
         r'perrorcall.LEVEL = 8192 /\ S_return.STORE[n_cell_level] = DEFINED (PINT 8192) /\ '
         r'S.OUTPUTBUFFERS[0].BYTES = $ptascii("AH") /\ S.EVENTS = [OUTPUT ([80])]'),
        ('an operation-valid false saved left integer cannot borrow the same zero Error',
         r'$integer_warning_valid(S_saved, pintegeroperation, INTEGER_RIGHT 2, pintegerconversion, 0) /\ '
         r'$dz_raw(S_saved) = S_request /\ $ob_object_division_error_capture(S_saved, S_generated) = eps'),
        ('an equally quiet zero BOOL snapshot cannot replace the current PINT RHS record',
         r'pintegerconversion_false.INPUT = PBOOL false /\ pintegerconversion_false.VALUE = 0 /\ '
         r'pintegerconversion_false.NOTICES = eps /\ '
         r'$integer_warning_valid(S_snapshot, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion_false, 0) /\ '
         r'$dz_raw(S_snapshot) = S_request /\ $ob_object_division_error_capture(S_snapshot, S_generated) = eps'),
        ('the quiet RHS has no consumed notice at cursor one',
         r'~$integer_warning_valid(S_cursor, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 1) /\ '
         r'$ob_object_division_error_capture(S_cursor, S_generated) = eps'),
        ('completed LEFT conversion advances normally before fresh quiet RIGHT conversion',
         r'$integer_warning_valid(S_resume, pintegeroperation, INTEGER_LEFT, pintegerconversion_left, 1) /\ '
         r'$dz_raw(S_resume) = S_left_complete /\ S_left_complete.COMPLETION = NORMAL /\ '
         r'S_left_complete.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT i_left)) :: ptask_tail* /\ '
         r'$ob_object_division_error_capture(S_resume, S_generated) = eps'),
        ('owning scratch cannot borrow the same actual native MOD Error',
         r'$call_current_valid(S_scratch) /\ $dz_raw(S_scratch) = S_request /\ '
         r'$ob_object_division_error_capture(S_scratch, S_generated) = eps'),
        ('a genuine other current handler body remains outside the literal-body capture',
         r'$error_handler_eligible(S_retarget, 8192) /\ $call_current_valid(S_retarget) /\ '
         r'$error_handler_target(S_retarget, PSTRING ($ptascii("h"))) =/= eps /\ '
         r'S_retarget_raw = S_request[.ERRORHANDLER = S_retarget.ERRORHANDLER] /\ '
         r'$ob_object_return_error_live(S_retarget_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_retarget, S_retarget_generated) = eps'),
        ('a handler eligible for both numeric notice classes retains the Error outside this bounded mask',
         r'$error_handler_eligible(S_both, 2) /\ $error_handler_eligible(S_both, 8192) /\ '
         r'$call_current_valid(S_both) /\ S_both_raw = S_request[.ERRORHANDLER = S_both.ERRORHANDLER] /\ '
         r'$ob_object_return_error_live(S_both_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_both, S_both_generated) = eps')]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
