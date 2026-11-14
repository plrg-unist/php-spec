#!/usr/bin/env python3
"""Selected LEFT Warning capture retains original caches and native retirement."""
import output_final_selected_left_warning_modulo_error_state as author
import output_final_selected_warning_modulo_error_review_state as right_review

runner = right_review.runner
PREFIX = author.PREFIX
CASES = {name: author.CASES[name] for name in ['constant', 'cv-pair']}


def task(phase='INTEGER_RIGHT i_left', conversion='pintegerconversion', cursor='0'):
    return '(INTEGER_OPERATOR_WARNING pintegeroperation (' + phase + ') ' + conversion + ' ' + cursor + ') :: ptask_tail*'


def authority(name, fixture, path):
    if name == 'cv-pair':
        bindings, _ = author.lifecycle(name, fixture, path)
        _, checks = right_review.authority(name, fixture, path)
        before = '$error_handler_finish(S_handler, perrorcall_return) = S /\\ '
        assert checks[0][1].count(before) == 1
        checks[0] = ('the real LEFT callback retires its formals before quiet RHS conversion and Error capture',
            checks[0][1].replace(before,
                '$error_handler_finish(S_handler, perrorcall_return) = S_resume /\\ ') +
            r' /\ S_resume.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion_left 1) :: ptask_tail* /\ '
            r'S_left_complete.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT i_left)) :: ptask_tail* /\ '
            r'S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i_left) pintegerconversion 0) :: ptask_tail* /\ '
            r'pintegerconversion.NOTICES = eps /\ S.STORE = S_resume.STORE')
        return bindings, checks

    bindings, _ = author.frontier(name, fixture, path)
    bindings += [
        'S_saved = S[.TODO = ' + task(phase='INTEGER_RIGHT 2') + ']',
        '$integer_conversion(PBOOL false) = (pintegerconversion_false)',
        'S_snapshot = S[.TODO = ' + task(conversion='pintegerconversion_false') + ']',
        'S_cursor = S[.TODO = ' + task(cursor='1') + ']',
        'S_phase = S[.TODO = ' + task(phase='INTEGER_LEFT') + ']', 'S_phase_raw = $dz_raw(S_phase)',
        'S_scratch = S[.RESULT = KNOWN (POBJECT pobobjectreturn.OBJECT)]',
        'S_retarget = S[.ERRORHANDLER = S.ERRORHANDLER[.CALLBACK = (PSTRING ($ptascii("h")))]]',
        'S_retarget_raw = $dz_raw(S_retarget)', 'S_retarget_generated = $throwable_transition(S_retarget, S_retarget_raw)',
        'S_both = S[.ERRORHANDLER = S.ERRORHANDLER[.LEVELS = 8194]]',
        'S_both_raw = $dz_raw(S_both)', 'S_both_generated = $throwable_transition(S_both, S_both_raw)']
    return bindings, [
        ('the genuine completed LEFT Warning preserves its own quiet RHS snapshot and live MOD Error',
         author.original(name) + r' /\ $ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'$error_handler_finish(S_handler, perrorcall_return) = S_resume /\ '
         r'S.OUTPUTBUFFERS[0].BYTES = $ptascii("AH") /\ S.EVENTS = [OUTPUT ([80])]'),
        ('an operation-valid false saved left integer produces the same Error but fails fresh conversion',
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
        ('a valid LEFT phase with this quiet record advances instead of borrowing the later Error',
         r'$integer_warning_valid(S_phase, pintegeroperation, INTEGER_LEFT, pintegerconversion, 0) /\ '
         r'S_phase_raw.COMPLETION = NORMAL /\ S_phase_raw.RESULT = KNOWN PNULL /\ '
         r'S_phase_raw.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 0)) :: ptask_tail* /\ '
         r'S_phase_raw.EVENTS = S.EVENTS /\ S_phase_raw.STORE = S.STORE /\ '
         r'$ob_object_division_error_capture(S_phase, S_generated) = eps'),
        ('owning result scratch cannot borrow the same raw zero Error',
         r'$call_current_valid(S_scratch) /\ $dz_raw(S_scratch) = S_request /\ '
         r'$ob_object_division_error_capture(S_scratch, S_generated) = eps'),
        ('another genuine two-parameter handler body remains outside this literal-echo contour',
         r'$error_handler_eligible(S_retarget, 2) /\ $call_current_valid(S_retarget) /\ '
         r'$error_handler_target(S_retarget, PSTRING ($ptascii("h"))) =/= eps /\ '
         r'S_retarget_raw = S_request[.ERRORHANDLER = S_retarget.ERRORHANDLER] /\ '
         r'$ob_object_return_error_live(S_retarget_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_retarget, S_retarget_generated) = eps'),
        ('a handler eligible for both notice classes captures the same authentic live Error',
         r'$error_handler_eligible(S_both, 2) /\ $error_handler_eligible(S_both, 8192) /\ '
         r'$call_current_valid(S_both) /\ S_both_raw = S_request[.ERRORHANDLER = S_both.ERRORHANDLER] /\ '
         r'$ob_object_return_error_live(S_both_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_both, S_both_generated) = ((pobobjectreturn, pobreturnerror))')]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
