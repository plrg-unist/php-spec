#!/usr/bin/env python3
"""Mixed notice callbacks preserve ordered arguments, exact caches and retirement."""
import output_final_selected_mixed_modulo_error_state as author
import output_final_default_unrelated_handler_modulo_error_review_state as runner

PREFIX = author.PREFIX
CASES = {name: author.sources.CASES['native-selected-mixed-modulo-error-' + name]
         for name in ['warning-deprecated-cv-pair-string', 'deprecated-warning-constant-float']}
FORMALS = ['n_cell_level', 'n_cell_message', 'n_cell_level_right', 'n_cell_message_right']


def task(phase='INTEGER_RIGHT i_left', conversion='pintegerconversion', cursor='1'):
    return '(INTEGER_OPERATOR_WARNING pintegeroperation (' + phase + ') ' + conversion + ' ' + cursor + ') :: ptask_tail*'


def retired(state, cells):
    return r' /\ '.join('~((HCELL ' + cell + ') <- ' + state + r'.ALLOCATIONS) /\ '
                        '$heap_count(HCELL ' + cell + ', $machine_roots(' + state + ')) = 0'
                        for cell in cells)


def authority(name, fixture, path):
    bindings, _ = author.lifecycle(name, fixture, path)
    order, form, kind = author.shape(name)
    warning = author.prior.value(b'A non-numeric value encountered')
    left_level, right_level = (2, 8192) if order == 'warning-deprecated' else (8192, 2)
    left_message = warning if left_level == 2 else author.message(kind, 'left')
    right_message = warning if right_level == 2 else author.message(kind, 'right')
    line = 8 if form == 'cv-pair' else 6
    fatal = author.prior.value((
        f'Fatal error: Uncaught DivisionByZeroError: Modulo by zero in {path}:{line}\n'
        'Stack trace:\n#0 [internal function]: T->__toString()\n#1 {main}\n'
        f'  thrown in {path} on line {line}\n').encode())
    checks = [
        ('both actual calls authenticate their ordered levels and messages under the real two-class mask',
         author.original(name) + r' /\ S.ERRORHANDLER.LEVELS = 8194 /\ '
         r'$error_handler_eligible(S, 2) /\ $error_handler_eligible(S, 8192) /\ '
         r'$error_handler_finish(S_handler, perrorcall_return) = S_resume /\ '
         r'$error_handler_finish(S_handler_right, perrorcall_return_right) = S /\ '
         f'perrorcall.LEVEL = {left_level}' + r' /\ ' + f'perrorcall_right.LEVEL = {right_level}' + r' /\ '
         r'perrorcall.MESSAGE = ' + left_message + r' /\ perrorcall_right.MESSAGE = ' + right_message + r' /\ '
         r'perrorcall.MESSAGE =/= perrorcall_right.MESSAGE /\ '
         f'S_return.STORE[n_cell_level] = DEFINED (PINT {left_level})' + r' /\ '
         f'S_return_right.STORE[n_cell_level_right] = DEFINED (PINT {right_level})' + r' /\ '
         r'$string_bytes(pvalue_message) = (' + left_message + r') /\ '
         r'$string_bytes(pvalue_message_right) = (' + right_message + r') /\ '
         r'pintegerconversion_left.NOTICES = [(perrorcall.LEVEL, perrorcall.MESSAGE)] /\ '
         r'pintegerconversion.NOTICES = [(perrorcall_right.LEVEL, perrorcall_right.MESSAGE)] /\ '
         r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('four distinct formals retire before capture preserves the full actual store and buffered AHH',
         r'n_cell_level =/= n_cell_message /\ n_cell_level_right =/= n_cell_message_right /\ '
         r'~(n_cell_level_right <- [n_cell_level, n_cell_message]) /\ '
         r'~(n_cell_message_right <- [n_cell_level, n_cell_message]) /\ '
         r'S_capture.STORE = S.STORE /\ S_capture.EVENTS = [OUTPUT ([80])] /\ '
         r'S_capture.OUTPUTBUFFERS[0].BYTES = $ptascii("AHH") /\ ' + retired('S_capture', FORMALS)),
        ('LEFT cursor one advances to fresh RIGHT zero and its real second call before capture is possible',
         r'S_resume.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion_left 1) :: ptask_tail* /\ '
         r'$integer_warning_valid(S_resume, pintegeroperation, INTEGER_LEFT, pintegerconversion_left, 1) /\ '
         r'$dz_raw(S_resume) = S_left_complete /\ '
         r'S_left_complete.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT i_left)) :: ptask_tail* /\ '
         r'$dz_raw(S_left_complete) = S_warning_right /\ '
         r'$integer_warning_valid(S_warning_right, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 0) /\ '
         r'$dz_raw(S_warning_right) = S_invoke_right /\ $error_call_valid(S_invoke_right, perrorcall_right) /\ '
         r'S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i_left) pintegerconversion 1) :: ptask_tail* /\ '
         r'$ob_object_division_error_capture(S_resume, S_generated) = eps /\ '
         r'$ob_object_division_error_capture(S_warning_right, S_generated) = eps')]

    if form == 'cv-pair':
        bindings += [
            '$integer_conversion(PSTRING ($ptascii("0.5"))) = (pintegerconversion_other)',
            'S_snapshot = S[.TODO = ' + task(conversion='pintegerconversion_other') + ']']
        checks += [
            ('equal bytes, zero and Deprecated message cannot substitute a different conversion INPUT',
             r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5")) /\ '
             r'pintegerconversion_other.INPUT = PSTRING ($ptascii("0.5")) /\ '
             r'pintegerconversion_other.INPUT =/= pintegerconversion.INPUT /\ '
             r'pintegerconversion_other.VALUE = 0 /\ pintegerconversion_other.NOTICES = pintegerconversion.NOTICES /\ '
             r'$integer_warning_valid(S_snapshot, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion_other, 1) /\ '
             r'$dz_raw(S_snapshot) = S_request /\ $ob_object_division_error_capture(S_snapshot, S_generated) = eps'),
            ('both native cells survive the real release queue and retire before C0 with all four formals still absent',
             r'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_cell_left), DESTRUCTION_VALUE (HCELL n_cell_right)] /\ '
             r'S_queue.DESTRUCTION.RELEASES = [pdestructionrelease] /\ '
             r'S_queue.STORE[n_cell_left] = DEFINED pvalue_left /\ S_queue.STORE[n_cell_right] = DEFINED pvalue_right /\ '
             r'~$ob_object_final_cv_ready(S_queue, pobobjectreturn_capture, pdestructionframe, n_exception) /\ '
             r'$ob_object_final_cv_ready(S_exit, pobobjectreturn_capture, pdestructionframe, n_exception) /\ '
             r'$heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ '
             + retired('S_queue', FORMALS) + r' /\ ' + retired('S_exit', FORMALS + ['n_cell_left', 'n_cell_right']))]
        cells = FORMALS + ['n_cell_left', 'n_cell_right']
    else:
        bindings += [
            'S_saved = S[.TODO = ' + task(phase='INTEGER_RIGHT 2') + ']',
            'S_cursor = S[.TODO = ' + task(cursor='2') + ']',
            'S_scratch = S[.RESULT = KNOWN (POBJECT pobobjectreturn.OBJECT)]',
            'S_retarget = S[.ERRORHANDLER = S.ERRORHANDLER[.CALLBACK = (PSTRING ($ptascii("h")))]]',
            'S_retarget_raw = $dz_raw(S_retarget)', 'S_retarget_generated = $throwable_transition(S_retarget, S_retarget_raw)']
        for level in [2, 8192]:
            state = 'S_mask_' + str(level)
            bindings += [state + ' = S[.ERRORHANDLER = S.ERRORHANDLER[.LEVELS = ' + str(level) + ']]',
                         state + '_raw = $dz_raw(' + state + ')',
                         state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)']
        checks += [
            ('a valid false saved LEFT integer cannot borrow the same zero Error',
             r'$integer_warning_valid(S_saved, pintegeroperation, INTEGER_RIGHT 2, pintegerconversion, 1) /\ '
             r'$dz_raw(S_saved) = S_request /\ $ob_object_division_error_capture(S_saved, S_generated) = eps'),
            ('two callbacks do not create a second notice within the singleton RHS conversion',
             r'~$integer_warning_valid(S_cursor, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 2) /\ '
             r'$ob_object_division_error_capture(S_cursor, S_generated) = eps'),
            ('owning result scratch cannot borrow the actual native MOD Error',
             r'$call_current_valid(S_scratch) /\ $dz_raw(S_scratch) = S_request /\ '
             r'$ob_object_division_error_capture(S_scratch, S_generated) = eps'),
            ('a different genuine current handler body remains outside the literal-body capture',
             r'$error_handler_eligible(S_retarget, 2) /\ $error_handler_eligible(S_retarget, 8192) /\ '
             r'$call_current_valid(S_retarget) /\ $error_handler_target(S_retarget, PSTRING ($ptascii("h"))) =/= eps /\ '
             r'S_retarget_raw = S_request[.ERRORHANDLER = S_retarget.ERRORHANDLER] /\ '
             r'$ob_object_return_error_live(S_retarget_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_retarget, S_retarget_generated) = eps')]
        for level, other in [(2, 8192), (8192, 2)]:
            state = 'S_mask_' + str(level)
            checks += [('a current mask eligible only for level ' + str(level) + ' retains the live Error outside mixed capture',
                '$error_handler_eligible(' + state + ', ' + str(level) + r') /\ '
                '~$error_handler_eligible(' + state + ', ' + str(other) + r') /\ '
                '$call_current_valid(' + state + r') /\ '
                + state + '_raw = S_request[.ERRORHANDLER = ' + state + r'.ERRORHANDLER] /\ '
                '$ob_object_return_error_live(' + state + r'_generated, pobreturnerror) /\ '
                '$ob_object_division_error_capture(' + state + ', ' + state + '_generated) = eps')]
        checks += [
            ('the actual empty native release must complete before C0 while all four formals stay retired',
             r'pdestructionrelease.JOBS = eps /\ S_stage.DESTRUCTION.RELEASES = [pdestructionrelease] /\ '
             r'~$ob_object_final_cv_ready(S_stage, pobobjectreturn_capture, pdestructionframe, n_exception) /\ '
             r'S_exit.DESTRUCTION.RELEASES = eps /\ '
             r'$ob_object_final_cv_ready(S_exit, pobobjectreturn_capture, pdestructionframe, n_exception) /\ '
             r'$heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ ' + retired('S_exit', FORMALS))]
        cells = FORMALS

    checks += [('fatal reporting retires the Error without reviving formals or operands, preserving buffered AHH',
        r'S_report.EVENTS = [OUTPUT ([80]), STDERR ' + fatal + r'] /\ '
        r'~((HOBJECT n_exception) <- S_retired.ALLOCATIONS) /\ '
        r'$heap_count(HOBJECT n_exception, $machine_roots(S_retired)) = 0 /\ '
        r'$eager_cleanup_valid(S_retired, pdestructioncleanup) /\ '
        r'~$eager_cleanup_valid(S_receipt_site, pdestructioncleanup_site) /\ '
        r'S_retired.ERRORHANDLER = S_binary.ERRORHANDLER /\ '
        r'pobdeactivate.BUFFERS[0].BYTES = $ptascii("AHH") /\ '
        + retired('S_retired', cells) + r' /\ ' + author.prior.public('S_retired'))]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
