#!/usr/bin/env python3
"""Precision callbacks preserve distinct messages, snapshots and real retirement."""
import output_final_selected_precision_modulo_error_state as author
import output_final_default_unrelated_handler_modulo_error_review_state as runner

PREFIX = author.PREFIX
CASES = {name: author.sources.CASES['native-selected-precision-modulo-error-' + name]
         for name in ['both-constant-float', 'right-cv-pair-string']}
FORMALS = ['n_cell_level', 'n_cell_message']


def task(phase='INTEGER_RIGHT i_left', conversion='pintegerconversion', cursor='1'):
    return '(INTEGER_OPERATOR_WARNING pintegeroperation (' + phase + ') ' + conversion + ' ' + cursor + ') :: ptask_tail*'


def retired(state, cells):
    return r' /\ '.join('~((HCELL ' + cell + ') <- ' + state + r'.ALLOCATIONS) /\ '
                        '$heap_count(HCELL ' + cell + ', $machine_roots(' + state + ')) = 0'
                        for cell in cells)


def authority(name, fixture, path):
    bindings, _ = author.lifecycle(name, fixture, path)
    line = 6 if name == 'both-constant-float' else 8
    fatal = author.prior.value((
        f'Fatal error: Uncaught DivisionByZeroError: Modulo by zero in {path}:{line}\n'
        'Stack trace:\n#0 [internal function]: T->__toString()\n#1 {main}\n'
        f'  thrown in {path} on line {line}\n').encode())

    if name == 'right-cv-pair-string':
        bindings += [
            '$integer_conversion(PSTRING ($ptascii("0.5"))) = (pintegerconversion_other)',
            'S_snapshot = S[.TODO = ' + task(conversion='pintegerconversion_other') + ']',
            'S_cursor = S[.TODO = ' + task(cursor='0') + ']',
            'S_early = $dz_raw(S_cursor)',
            'S_early.TODO = (ERROR_HANDLER_INVOKE perrorcall_again) :: ptask_tail*']
        return bindings, [
            ('one actual right precision callback retires its formals before full-store capture',
             author.original(name) + r' /\ $error_handler_finish(S_handler, perrorcall_return) = S /\ '
             r'perrorcall.LEVEL = 8192 /\ S_return.STORE[n_cell_level] = DEFINED (PINT 8192) /\ '
             r'$string_bytes(pvalue_message) = (' + author.message('string', 'right') + r') /\ '
             r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
             r'S_capture.STORE = S.STORE /\ S_capture.EVENTS = [OUTPUT ([80])] /\ '
             r'S_capture.OUTPUTBUFFERS[0].BYTES = $ptascii("AH") /\ ' + retired('S_capture', FORMALS)),
            ('equal bytes, zero and precision message do not authorize a different conversion input',
             r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5")) /\ '
             r'pintegerconversion_other.INPUT = PSTRING ($ptascii("0.5")) /\ '
             r'pintegerconversion_other.INPUT =/= pintegerconversion.INPUT /\ '
             r'pintegerconversion_other.VALUE = 0 /\ pintegerconversion_other.NOTICES = pintegerconversion.NOTICES /\ '
             r'$integer_warning_valid(S_snapshot, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion_other, 1) /\ '
             r'$dz_raw(S_snapshot) = S_request /\ $ob_object_division_error_capture(S_snapshot, S_generated) = eps'),
            ('an unconsumed right notice invokes the handler before it can capture the later Error',
             r'$integer_warning_valid(S_cursor, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 0) /\ '
             r'$error_call_valid(S_early, perrorcall_again) /\ perrorcall_again.LEVEL = 8192 /\ '
             r'perrorcall_again.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i_left) pintegerconversion 1 /\ '
             r'$ob_object_division_error_capture(S_cursor, S_generated) = eps'),
            ('native unwind retains both operand cells until their actual release after the callback',
             r'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_cell_left), DESTRUCTION_VALUE (HCELL n_cell_right)] /\ '
             r'S_queue.DESTRUCTION.RELEASES = [pdestructionrelease] /\ '
             r'S_queue.STORE[n_cell_left] = DEFINED pvalue_left /\ S_queue.STORE[n_cell_right] = DEFINED pvalue_right /\ '
             r'~$ob_object_final_cv_ready(S_queue, pobobjectreturn_capture, pdestructionframe, n_exception) /\ '
             + retired('S_queue', FORMALS)),
            ('C0 is ready only after real operand retirement and retains the original Error once',
             r'$ob_object_final_cv_ready(S_exit, pobobjectreturn_capture, pdestructionframe, n_exception) /\ '
             r'$heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ '
             r'S_exit.ERRORHANDLER = S_binary.ERRORHANDLER /\ S_exit.EVENTS = [OUTPUT ([80])] /\ '
             + retired('S_exit', FORMALS + ['n_cell_left', 'n_cell_right'])),
            ('fatal reporting retires the Error without reviving callback or native operand cells',
             r'S_report.EVENTS = [OUTPUT ([80]), STDERR ' + fatal + r'] /\ '
             r'~((HOBJECT n_exception) <- S_retired.ALLOCATIONS) /\ '
             r'$heap_count(HOBJECT n_exception, $machine_roots(S_retired)) = 0 /\ '
             r'$eager_cleanup_valid(S_retired, pdestructioncleanup) /\ '
             r'~$eager_cleanup_valid(S_receipt_site, pdestructioncleanup_site) /\ '
             r'pobdeactivate.BUFFERS[0].BYTES = $ptascii("AH") /\ '
             + retired('S_retired', FORMALS + ['n_cell_left', 'n_cell_right']) + r' /\ '
             + author.prior.public('S_retired'))]

    formals = FORMALS + ['n_cell_level_right', 'n_cell_message_right']
    bindings += [
        'S_saved = S[.TODO = ' + task(phase='INTEGER_RIGHT 2') + ']',
        'S_cursor = S[.TODO = ' + task(cursor='2') + ']',
        'S_scratch = S[.RESULT = KNOWN (POBJECT pobobjectreturn.OBJECT)]',
        'S_retarget = S[.ERRORHANDLER = S.ERRORHANDLER[.CALLBACK = (PSTRING ($ptascii("h")))]]',
        'S_retarget_raw = $dz_raw(S_retarget)', 'S_retarget_generated = $throwable_transition(S_retarget, S_retarget_raw)',
        'S_both = S[.ERRORHANDLER = S.ERRORHANDLER[.LEVELS = 8194]]',
        'S_both_raw = $dz_raw(S_both)', 'S_both_generated = $throwable_transition(S_both, S_both_raw)']
    return bindings, [
        ('two actual precision callbacks preserve their different messages and their own consumed cursors',
         author.original(name) + r' /\ $error_handler_finish(S_handler, perrorcall_return) = S_resume /\ '
         r'$error_handler_finish(S_handler_right, perrorcall_return_right) = S /\ '
         r'perrorcall.LEVEL = 8192 /\ perrorcall_right.LEVEL = 8192 /\ '
         r'perrorcall.MESSAGE = ' + author.message('float', 'left') + r' /\ '
         r'perrorcall_right.MESSAGE = ' + author.message('float', 'right') + r' /\ '
         r'perrorcall.MESSAGE =/= perrorcall_right.MESSAGE /\ '
         r'S_return.STORE[n_cell_level] = DEFINED (PINT 8192) /\ '
         r'S_return_right.STORE[n_cell_level_right] = DEFINED (PINT 8192) /\ '
         r'S_resume.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion_left 1) :: ptask_tail* /\ '
         r'S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i_left) pintegerconversion 1) :: ptask_tail* /\ '
         r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('four distinct formal cells retire before capture preserves the actual full store and buffered AHH',
         r'n_cell_level =/= n_cell_message /\ n_cell_level_right =/= n_cell_message_right /\ '
         r'~(n_cell_level_right <- [n_cell_level, n_cell_message]) /\ '
         r'~(n_cell_message_right <- [n_cell_level, n_cell_message]) /\ '
         r'S_capture.STORE = S.STORE /\ S_capture.EVENTS = [OUTPUT ([80])] /\ '
         r'S_capture.OUTPUTBUFFERS[0].BYTES = $ptascii("AHH") /\ ' + retired('S_capture', formals)),
        ('completed LEFT advances before fresh RIGHT cursor zero invokes the second real handler',
         r'$integer_warning_valid(S_resume, pintegeroperation, INTEGER_LEFT, pintegerconversion_left, 1) /\ '
         r'$dz_raw(S_resume) = S_left_complete /\ '
         r'S_left_complete.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT i_left)) :: ptask_tail* /\ '
         r'$dz_raw(S_left_complete) = S_warning_right /\ '
         r'$integer_warning_valid(S_warning_right, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 0) /\ '
         r'$dz_raw(S_warning_right) = S_invoke_right /\ $error_call_valid(S_invoke_right, perrorcall_right) /\ '
         r'$ob_object_division_error_capture(S_resume, S_generated) = eps /\ '
         r'$ob_object_division_error_capture(S_warning_right, S_generated) = eps'),
        ('a valid false saved left integer cannot borrow the same zero Error',
         r'$integer_warning_valid(S_saved, pintegeroperation, INTEGER_RIGHT 2, pintegerconversion, 1) /\ '
         r'$dz_raw(S_saved) = S_request /\ $ob_object_division_error_capture(S_saved, S_generated) = eps'),
        ('two callbacks do not create another notice in the singleton RHS conversion',
         r'~$integer_warning_valid(S_cursor, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 2) /\ '
         r'$ob_object_division_error_capture(S_cursor, S_generated) = eps'),
        ('owning scratch cannot borrow the actual native MOD Error',
         r'$call_current_valid(S_scratch) /\ $dz_raw(S_scratch) = S_request /\ '
         r'$ob_object_division_error_capture(S_scratch, S_generated) = eps'),
        ('a genuine different current handler body remains outside the literal-body capture',
         r'$error_handler_eligible(S_retarget, 8192) /\ $call_current_valid(S_retarget) /\ '
         r'$error_handler_target(S_retarget, PSTRING ($ptascii("h"))) =/= eps /\ '
         r'S_retarget_raw = S_request[.ERRORHANDLER = S_retarget.ERRORHANDLER] /\ '
         r'$ob_object_return_error_live(S_retarget_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_retarget, S_retarget_generated) = eps'),
        ('a current both-class mask keeps the live Error outside the bounded Deprecated-only capture',
         r'$error_handler_eligible(S_both, 2) /\ $error_handler_eligible(S_both, 8192) /\ '
         r'$call_current_valid(S_both) /\ S_both_raw = S_request[.ERRORHANDLER = S_both.ERRORHANDLER] /\ '
         r'$ob_object_return_error_live(S_both_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_both, S_both_generated) = eps'),
        ('the actual empty native release precedes C0 while all four callback cells remain retired',
         r'pdestructionrelease.JOBS = eps /\ S_stage.DESTRUCTION.RELEASES = [pdestructionrelease] /\ '
         r'~$ob_object_final_cv_ready(S_stage, pobobjectreturn_capture, pdestructionframe, n_exception) /\ '
         r'S_exit.DESTRUCTION.RELEASES = eps /\ '
         r'$ob_object_final_cv_ready(S_exit, pobobjectreturn_capture, pdestructionframe, n_exception) /\ '
         r'$heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ ' + retired('S_exit', formals)),
        ('fatal reporting retires the Error with both completed callbacks still visible only in buffered AHH',
         r'S_report.EVENTS = [OUTPUT ([80]), STDERR ' + fatal + r'] /\ '
         r'~((HOBJECT n_exception) <- S_retired.ALLOCATIONS) /\ '
         r'$heap_count(HOBJECT n_exception, $machine_roots(S_retired)) = 0 /\ '
         r'$eager_cleanup_valid(S_retired, pdestructioncleanup) /\ '
         r'~$eager_cleanup_valid(S_receipt_site, pdestructioncleanup_site) /\ '
         r'S_retired.ERRORHANDLER = S_binary.ERRORHANDLER /\ '
         r'pobdeactivate.BUFFERS[0].BYTES = $ptascii("AHH") /\ '
         + retired('S_retired', formals) + r' /\ ' + author.prior.public('S_retired'))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
