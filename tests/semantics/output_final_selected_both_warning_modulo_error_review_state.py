#!/usr/bin/env python3
"""Two selected MOD callbacks preserve real completion, caches and retirement."""
import output_final_selected_both_warning_modulo_error_state as author
import output_final_selected_warning_modulo_error_review_state as right_review

runner = right_review.runner
PREFIX = author.PREFIX
CASES = {name: author.CASES[name] for name in ['constant', 'cv-pair']}
FORMALS = ['n_cell_level', 'n_cell_message', 'n_cell_level_right', 'n_cell_message_right']


def task(phase='INTEGER_RIGHT i_left', conversion='pintegerconversion', cursor='1'):
    return '(INTEGER_OPERATOR_WARNING pintegeroperation (' + phase + ') ' + conversion + ' ' + cursor + ') :: ptask_tail*'


def retired_formals(state):
    return r' /\ '.join('~((HCELL ' + cell + ') <- ' + state + r'.ALLOCATIONS) /\ '
                        '$heap_count(HCELL ' + cell + ', $machine_roots(' + state + ')) = 0'
                        for cell in FORMALS)


def authority(name, fixture, path):
    if name == 'cv-pair':
        bindings, _ = author.lifecycle(name, fixture, path)
        return bindings, [
            ('both exact callback finishes precede capture with four retired formals and buffered AHH',
             r'$error_handler_finish(S_handler, perrorcall_return) = S_resume /\ '
             r'$error_handler_finish(S_handler_right, perrorcall_return_right) = S /\ '
             r'S_capture.EVENTS = [OUTPUT ([80])] /\ S_capture.OUTPUTBUFFERS[0].BYTES = $ptascii("AHH") /\ '
             r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ '
             r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn) /\ '
             + retired_formals('S_capture')),
            ('native unwind releases only its two original operand cells after both callback retirements',
             r'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_cell_left), DESTRUCTION_VALUE (HCELL n_cell_right)] /\ '
             r'S_queue.DESTRUCTION.RELEASES = [pdestructionrelease] /\ '
             r'S_queue.STORE[n_cell_left] = DEFINED pvalue_left /\ S_queue.STORE[n_cell_right] = DEFINED pvalue_right /\ '
             r'~$ob_object_final_cv_ready(S_queue, pobobjectreturn_capture, pdestructionframe, n_exception) /\ '
             + retired_formals('S_queue')),
            ('C0 becomes ready only after operand retirement with the original Error retained once',
             r'$ob_object_final_cv_ready(S_exit, pobobjectreturn_capture, pdestructionframe, n_exception) /\ '
             r'~((HCELL n_cell_left) <- S_exit.ALLOCATIONS) /\ ~((HCELL n_cell_right) <- S_exit.ALLOCATIONS) /\ '
             r'$heap_count(HCELL n_cell_left, $machine_roots(S_exit)) = 0 /\ '
             r'$heap_count(HCELL n_cell_right, $machine_roots(S_exit)) = 0 /\ '
             r'$heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ '
             r'S_exit.ERRORHANDLER = S_binary.ERRORHANDLER /\ S_exit.ERRORHANDLERS = S_binary.ERRORHANDLERS /\ '
             r'S_exit.EVENTS = [OUTPUT ([80])] /\ ' + retired_formals('S_exit')),
            ('fatal reporting retires the Error without reviving either callback or its operands',
             r'~((HOBJECT n_exception) <- S_retired.ALLOCATIONS) /\ '
             r'$heap_count(HOBJECT n_exception, $machine_roots(S_retired)) = 0 /\ '
             r'$heap_count(HCELL n_cell_left, $machine_roots(S_retired)) = 0 /\ '
             r'$heap_count(HCELL n_cell_right, $machine_roots(S_retired)) = 0 /\ '
             r'$eager_cleanup_valid(S_retired, pdestructioncleanup) /\ '
             r'~$eager_cleanup_valid(S_receipt_site, pdestructioncleanup_site) /\ '
             r'S_retired.ERRORHANDLER = S_binary.ERRORHANDLER /\ '
             r'pobdeactivate.BUFFERS[0].BYTES = $ptascii("AHH") /\ '
             + retired_formals('S_retired') + r' /\ ' + author.prior.public('S_retired'))]

    bindings, _ = author.frontier(name, fixture, path)
    bindings += [
        'S_saved = S[.TODO = ' + task(phase='INTEGER_RIGHT 2') + ']',
        '$integer_conversion(PSTRING_CARRIER INTERNED_STRING ($ptascii("0y"))) = (pintegerconversion_other)',
        'S_snapshot = S[.TODO = ' + task(conversion='pintegerconversion_other') + ']',
        'S_cursor = S[.TODO = ' + task(cursor='2') + ']',
        'S_scratch = S[.RESULT = KNOWN (POBJECT pobobjectreturn.OBJECT)]',
        'S_retarget = S[.ERRORHANDLER = S.ERRORHANDLER[.CALLBACK = (PSTRING ($ptascii("h")))]]',
        'S_retarget_raw = $dz_raw(S_retarget)', 'S_retarget_generated = $throwable_transition(S_retarget, S_retarget_raw)',
        'S_both = S[.ERRORHANDLER = S.ERRORHANDLER[.LEVELS = 8194]]',
        'S_both_raw = $dz_raw(S_both)', 'S_both_generated = $throwable_transition(S_both, S_both_raw)']
    return bindings, [
        ('both actual NULL callbacks restore their own cursors before authentic MOD Error capture',
         author.original(name) + r' /\ $ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'$error_handler_finish(S_handler, perrorcall_return) = S_resume /\ '
         r'$error_handler_finish(S_handler_right, perrorcall_return_right) = S /\ '
         r'S_resume.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion_left 1) :: ptask_tail* /\ '
         r'S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i_left) pintegerconversion 1) :: ptask_tail* /\ '
         r'S.OUTPUTBUFFERS[0].BYTES = $ptascii("AHH") /\ S.EVENTS = [OUTPUT ([80])]'),
        ('the same zero Error cannot authorize a false saved left integer',
         r'$integer_warning_valid(S_saved, pintegeroperation, INTEGER_RIGHT 2, pintegerconversion, 1) /\ '
         r'$dz_raw(S_saved) = S_request /\ $ob_object_division_error_capture(S_saved, S_generated) = eps'),
        ('an equal-zero equal-Warning record still has to belong to the current original RHS',
         r'pintegerconversion_other.VALUE = 0 /\ pintegerconversion_other.NOTICES = pintegerconversion.NOTICES /\ '
         r'pintegerconversion_other.INPUT =/= pintegerconversion.INPUT /\ '
         r'$integer_warning_valid(S_snapshot, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion_other, 1) /\ '
         r'$dz_raw(S_snapshot) = S_request /\ $ob_object_division_error_capture(S_snapshot, S_generated) = eps'),
        ('the completed first callback advances its saved LEFT conversion instead of borrowing the later Error',
         r'$integer_warning_valid(S_resume, pintegeroperation, INTEGER_LEFT, pintegerconversion_left, 1) /\ '
         r'$dz_raw(S_resume) = S_left_complete /\ S_left_complete.COMPLETION = NORMAL /\ '
         r'S_left_complete.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT i_left)) :: ptask_tail* /\ '
         r'$ob_object_division_error_capture(S_resume, S_generated) = eps'),
        ('the genuine unconsumed RIGHT Warning invokes the second handler before Error capture',
         r'$integer_warning_valid(S_warning_right, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 0) /\ '
         r'$dz_raw(S_warning_right) = S_invoke_right /\ '
         r'$error_call_valid(S_invoke_right, perrorcall_right) /\ '
         r'$ob_object_division_error_capture(S_warning_right, S_generated) = eps'),
        ('two callbacks do not create a second notice in the one-notice RHS vector',
         r'~$integer_warning_valid(S_cursor, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 2) /\ '
         r'$ob_object_division_error_capture(S_cursor, S_generated) = eps'),
        ('owning scratch cannot borrow the same native MOD Error',
         r'$call_current_valid(S_scratch) /\ $dz_raw(S_scratch) = S_request /\ '
         r'$ob_object_division_error_capture(S_scratch, S_generated) = eps'),
        ('a genuine different current handler body remains outside this literal-body capture',
         r'$error_handler_eligible(S_retarget, 2) /\ $call_current_valid(S_retarget) /\ '
         r'$error_handler_target(S_retarget, PSTRING ($ptascii("h"))) =/= eps /\ '
         r'S_retarget_raw = S_request[.ERRORHANDLER = S_retarget.ERRORHANDLER] /\ '
         r'$ob_object_return_error_live(S_retarget_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_retarget, S_retarget_generated) = eps'),
        ('the current both-class mask captures the same authentic homogeneous Warning Error',
         r'$error_handler_eligible(S_both, 2) /\ $error_handler_eligible(S_both, 8192) /\ '
         r'$call_current_valid(S_both) /\ S_both_raw = S_request[.ERRORHANDLER = S_both.ERRORHANDLER] /\ '
         r'$ob_object_return_error_live(S_both_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_both, S_both_generated) = ((pobobjectreturn, pobreturnerror))')]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
