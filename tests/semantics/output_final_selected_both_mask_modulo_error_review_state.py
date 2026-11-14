#!/usr/bin/env python3
"""Both-class masks preserve genuine homogeneous callbacks and FINAL retirement."""
import sys
import output_final_selected_both_mask_modulo_error_state as author
import output_final_default_unrelated_handler_modulo_error_review_state as runner

PREFIX = author.PREFIX
CASES = {name: author.sources.CASES['native-selected-both-mask-modulo-error-' + name]
         for name in ['warning-right-cv-pair', 'deprecated-both-constant']}
FORMALS = ['n_cell_level', 'n_cell_message']


def task(phase='INTEGER_RIGHT i_left', conversion='pintegerconversion', cursor='1'):
    return '(INTEGER_OPERATOR_WARNING pintegeroperation (' + phase + ') ' + conversion + ' ' + cursor + ') :: ptask_tail*'


def retired(state, cells):
    return r' /\ '.join('~((HCELL ' + cell + ') <- ' + state + r'.ALLOCATIONS) /\ '
                        '$heap_count(HCELL ' + cell + ', $machine_roots(' + state + ')) = 0'
                        for cell in cells)


def authority(name, fixture, path):
    bindings, _ = author.lifecycle(name, fixture, path)
    level, role, form, kind = author.shape(name)
    line = 8 if form == 'cv-pair' else 6
    fatal = author.prior.value((
        f'Fatal error: Uncaught DivisionByZeroError: Modulo by zero in {path}:{line}\n'
        'Stack trace:\n#0 [internal function]: T->__toString()\n#1 {main}\n'
        f'  thrown in {path} on line {line}\n').encode())
    mask = (r'S.ERRORHANDLER.LEVELS = 8194 /\ '
            r'$error_handler_eligible(S, 2) /\ $error_handler_eligible(S, 8192)')

    if level == 'warning':
        bindings += [
            '$integer_conversion(PSTRING ($ptascii("0x"))) = (pintegerconversion_other)',
            'S_snapshot = S[.TODO = ' + task(conversion='pintegerconversion_other') + ']']
        cells = FORMALS + ['n_cell_left', 'n_cell_right']
        checks = [
            ('the actual Warning arguments and NULL finish precede full-store capture under both eligible classes',
             author.original(name) + r' /\ ' + mask + r' /\ '
             r'$error_handler_finish(S_handler, perrorcall_return) = S /\ '
             r'perrorcall.LEVEL = 2 /\ S_return.STORE[n_cell_level] = DEFINED (PINT 2) /\ '
             r'perrorcall.MESSAGE = $ptascii("A non-numeric value encountered") /\ '
             r'$string_bytes(pvalue_message) = (perrorcall.MESSAGE) /\ '
             r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
             r'S_capture.STORE = S.STORE /\ S_capture.EVENTS = [OUTPUT ([80])] /\ '
             r'S_capture.OUTPUTBUFFERS[0].BYTES = $ptascii("AH") /\ ' + retired('S_capture', FORMALS)),
            ('equal bytes, Warning and zero cannot substitute a different conversion INPUT',
             r'pvalue_right = PSTRING_CARRIER INTERNED_STRING ($ptascii("0x")) /\ '
             r'pintegerconversion_other.INPUT = PSTRING ($ptascii("0x")) /\ '
             r'pintegerconversion_other.INPUT =/= pintegerconversion.INPUT /\ '
             r'pintegerconversion_other.VALUE = 0 /\ pintegerconversion_other.NOTICES = pintegerconversion.NOTICES /\ '
             r'$integer_warning_valid(S_snapshot, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion_other, 1) /\ '
             r'$dz_raw(S_snapshot) = S_request /\ $ob_object_division_error_capture(S_snapshot, S_generated) = eps'),
            ('a genuine pending RIGHT Warning invokes the callback before the later Error can be captured',
             r'$integer_warning_valid(S_warning, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 0) /\ '
             r'$dz_raw(S_warning) = S_invoke /\ $error_call_valid(S_invoke, perrorcall) /\ '
             r'$ob_object_division_error_capture(S_warning, S_generated) = eps'),
            ('both native operand cells survive the actual queue and retire before C0 with both formals absent',
             r'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_cell_left), DESTRUCTION_VALUE (HCELL n_cell_right)] /\ '
             r'S_queue.DESTRUCTION.RELEASES = [pdestructionrelease] /\ '
             r'S_queue.STORE[n_cell_left] = DEFINED pvalue_left /\ S_queue.STORE[n_cell_right] = DEFINED pvalue_right /\ '
             r'~$ob_object_final_cv_ready(S_queue, pobobjectreturn_capture, pdestructionframe, n_exception) /\ '
             r'$ob_object_final_cv_ready(S_exit, pobobjectreturn_capture, pdestructionframe, n_exception) /\ '
             r'$heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ '
             + retired('S_queue', FORMALS) + r' /\ ' + retired('S_exit', cells))]
        buffered = 'AH'
    else:
        cells = FORMALS + ['n_cell_level_right', 'n_cell_message_right']
        bindings += [
            'S_saved = S[.TODO = ' + task(phase='INTEGER_RIGHT 2') + ']',
            'S_cursor = S[.TODO = ' + task(cursor='2') + ']',
            'S_scratch = S[.RESULT = KNOWN (POBJECT pobobjectreturn.OBJECT)]',
            'S_retarget = S[.ERRORHANDLER = S.ERRORHANDLER[.CALLBACK = (PSTRING ($ptascii("h")))]]',
            'S_retarget_raw = $dz_raw(S_retarget)', 'S_retarget_generated = $throwable_transition(S_retarget, S_retarget_raw)']
        checks = [
            ('two real Deprecated calls retain distinct float messages and exact finishes under both eligible classes',
             author.original(name) + r' /\ ' + mask + r' /\ '
             r'$error_handler_finish(S_handler, perrorcall_return) = S_resume /\ '
             r'$error_handler_finish(S_handler_right, perrorcall_return_right) = S /\ '
             r'perrorcall.LEVEL = 8192 /\ perrorcall_right.LEVEL = 8192 /\ '
             r'perrorcall.MESSAGE = ' + author.precision.message(kind, 'left') + r' /\ '
             r'perrorcall_right.MESSAGE = ' + author.precision.message(kind, 'right') + r' /\ '
             r'perrorcall.MESSAGE =/= perrorcall_right.MESSAGE /\ '
             r'S_return.STORE[n_cell_level] = DEFINED (PINT 8192) /\ '
             r'S_return_right.STORE[n_cell_level_right] = DEFINED (PINT 8192) /\ '
             r'pintegerconversion_left.NOTICES = [(8192, perrorcall.MESSAGE)] /\ '
             r'pintegerconversion.NOTICES = [(8192, perrorcall_right.MESSAGE)] /\ '
             r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('four distinct formals retire before full-store capture retains buffered AHH',
             r'n_cell_level =/= n_cell_message /\ n_cell_level_right =/= n_cell_message_right /\ '
             r'~(n_cell_level_right <- [n_cell_level, n_cell_message]) /\ '
             r'~(n_cell_message_right <- [n_cell_level, n_cell_message]) /\ '
             r'S_capture.STORE = S.STORE /\ S_capture.EVENTS = [OUTPUT ([80])] /\ '
             r'S_capture.OUTPUTBUFFERS[0].BYTES = $ptascii("AHH") /\ ' + retired('S_capture', cells)),
            ('completed LEFT advances to fresh RIGHT zero and its real second call before Error capture',
             r'$integer_warning_valid(S_resume, pintegeroperation, INTEGER_LEFT, pintegerconversion_left, 1) /\ '
             r'$dz_raw(S_resume) = S_left_complete /\ '
             r'S_left_complete.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT i_left)) :: ptask_tail* /\ '
             r'$dz_raw(S_left_complete) = S_warning_right /\ '
             r'$integer_warning_valid(S_warning_right, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 0) /\ '
             r'$dz_raw(S_warning_right) = S_invoke_right /\ $error_call_valid(S_invoke_right, perrorcall_right) /\ '
             r'$ob_object_division_error_capture(S_resume, S_generated) = eps /\ '
             r'$ob_object_division_error_capture(S_warning_right, S_generated) = eps'),
            ('an operation-valid false saved LEFT integer cannot borrow the same zero Error',
             r'$integer_warning_valid(S_saved, pintegeroperation, INTEGER_RIGHT 2, pintegerconversion, 1) /\ '
             r'$dz_raw(S_saved) = S_request /\ $ob_object_division_error_capture(S_saved, S_generated) = eps'),
            ('two calls do not create another notice in the singleton RHS conversion',
             r'~$integer_warning_valid(S_cursor, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 2) /\ '
             r'$ob_object_division_error_capture(S_cursor, S_generated) = eps'),
            ('owning scratch cannot borrow the same actual native MOD Error',
             r'$call_current_valid(S_scratch) /\ $dz_raw(S_scratch) = S_request /\ '
             r'$ob_object_division_error_capture(S_scratch, S_generated) = eps'),
            ('a genuine different current handler body stays outside the literal-body capture',
             r'$error_handler_eligible(S_retarget, 2) /\ $error_handler_eligible(S_retarget, 8192) /\ '
             r'$call_current_valid(S_retarget) /\ $error_handler_target(S_retarget, PSTRING ($ptascii("h"))) =/= eps /\ '
             r'S_retarget_raw = S_request[.ERRORHANDLER = S_retarget.ERRORHANDLER] /\ '
             r'$ob_object_return_error_live(S_retarget_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_retarget, S_retarget_generated) = eps'),
            ('the genuine empty native release must finish before C0 while all four formals stay retired',
             r'pdestructionrelease.JOBS = eps /\ S_stage.DESTRUCTION.RELEASES = [pdestructionrelease] /\ '
             r'~$ob_object_final_cv_ready(S_stage, pobobjectreturn_capture, pdestructionframe, n_exception) /\ '
             r'S_exit.DESTRUCTION.RELEASES = eps /\ '
             r'$ob_object_final_cv_ready(S_exit, pobobjectreturn_capture, pdestructionframe, n_exception) /\ '
             r'$heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ ' + retired('S_exit', cells))]
        buffered = 'AHH'

    checks += [('fatal reporting retires the Error without reviving formals or operands',
        r'S_report.EVENTS = [OUTPUT ([80]), STDERR ' + fatal + r'] /\ '
        r'~((HOBJECT n_exception) <- S_retired.ALLOCATIONS) /\ '
        r'$heap_count(HOBJECT n_exception, $machine_roots(S_retired)) = 0 /\ '
        r'$eager_cleanup_valid(S_retired, pdestructioncleanup) /\ '
        r'~$eager_cleanup_valid(S_receipt_site, pdestructioncleanup_site) /\ '
        r'S_retired.ERRORHANDLER = S_binary.ERRORHANDLER /\ '
        r'pobdeactivate.BUFFERS[0].BYTES = $ptascii("' + buffered + r'") /\ '
        + retired('S_retired', cells) + r' /\ ' + author.prior.public('S_retired'))]
    return bindings, checks


def affected_cases():
    import output_final_selected_left_warning_modulo_error_review_state as left
    import output_final_selected_both_warning_modulo_error_review_state as both
    import output_final_selected_left_deprecated_modulo_error_review_state as deprecated
    import output_final_selected_precision_modulo_error_review_state as precision
    return {'left-warning': (left, 'constant'), 'both-warning': (both, 'constant'),
            'left-deprecated': (deprecated, 'constant-float'),
            'both-deprecated': (precision, 'both-constant-float')}


if __name__ == '__main__':
    if '--affected' in sys.argv:
        sys.argv.remove('--affected')
        affected = affected_cases()

        def affected_authority(name, fixture, path):
            review, key = affected[name]
            bindings, _ = review.author.frontier(key, fixture, path)
            _, checks = review.authority(key, fixture, path)
            checks = [(label, condition) for label, condition in checks
                      if '$ob_object_division_error_capture(S_both, S_both_generated)' in condition]
            assert len(checks) == 1 and '= eps' not in checks[0][1]
            assert not any('pobobjectreturn_seed' in binding for binding in bindings)
            bindings += ['S_both = S[.ERRORHANDLER = S.ERRORHANDLER[.LEVELS = 8194]]',
                         'S_both_raw = $dz_raw(S_both)',
                         'S_both_generated = $throwable_transition(S_both, S_both_raw)']
            runner.PREFIX = review.PREFIX
            return bindings, checks

        runner.CASES = {name: review.CASES[key] for name, (review, key) in affected.items()}
        runner.authority = affected_authority
    else:
        runner.CASES, runner.authority = CASES, authority
    runner.PREFIX = PREFIX
    runner.main()
