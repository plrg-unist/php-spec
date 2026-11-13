#!/usr/bin/env python3
"""Two real selected Warning calls return before native MOD failure."""
import output_final_selected_left_warning_modulo_error_state as left
import output_final_default_unrelated_handler_both_modulo_conversion_error_state as both
import output_final_selected_both_warning_modulo_error_sources as sources

prior, runner = left.prior, left.runner
PREFIX = left.PREFIX.replace('def $dp_phase(S, n) = false -- otherwise', r'''
def $dp_phase(S, 14) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 0) :: ptask_tail*
  -- if pintegerconversion.NOTICES = [(2, ptbytes)]
def $dp_phase(S, 15) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 1
def $dp_phase(S, 16) = true
  -- if S.TODO = (RETURN_UNWIND (KNOWN PNULL) porigin?) :: ptask_tail*
  -- if S.FRAMES = pframe_handler :: pframe :: eps
  -- if pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_handler*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 1
def $dp_phase(S, 17) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 1
def $dp_phase(S, n) = false -- otherwise''')
CASES = {name: sources.CASES['native-selected-both-warning-modulo-error-' + name]
         for name in ['constant', 'left-cv', 'right-cv', 'cv-pair']}


def bindings_for(name, fixture, path):
    bindings = left.bindings_for(name, fixture, path)
    before = prior.seek('S', 'S_resume', 9)
    index = bindings.index(before[0])
    assert bindings[index:index + len(before)] == before
    bindings[index:index + len(before)] = [
        *prior.seek('S_warning_right', 'S_resume', 14),
        'S_warning_right.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i_left) pintegerconversion 0) :: ptask_tail*',
        *prior.seek('S_invoke_right', 'S_warning_right', 15),
        'S_invoke_right.TODO = (ERROR_HANDLER_INVOKE perrorcall_right) :: ptask_tail*',
        'perrorcall_right.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i_left) pintegerconversion 1',
        '$error_handler_target(S_invoke_right, perrorcall_right.CALLBACK) = (pcalltarget_handler_right)',
        '$target_function(S_invoke_right, pcalltarget_handler_right) = (pfunction_handler)',
        *prior.seek('S_return_right', 'S_invoke_right', 16),
        'S_return_right.CURRENT = (pcallcontext_handler_right)',
        'pcallcontext_handler_right.TARGET = API_BORROWED_TARGET pshutdownproducer_handler_right',
        'S_return_right.FRAMES = pframe_handler_right :: pframe :: eps',
        '$lookup(S_return_right.ENV, $ptascii("level")) = (n_cell_level_right)',
        '$lookup(S_return_right.ENV, $ptascii("message")) = (n_cell_message_right)',
        'S_return_right.STORE[n_cell_message_right] = DEFINED pvalue_message_right',
        *prior.seek('S_handler_right', 'S_return_right', 17),
        'S_handler_right.TODO = (ERROR_HANDLER_RESULT perrorcall_return_right) :: ptask_tail*',
        *prior.seek('S', 'S_handler_right', 9)]
    return bindings


def original(name):
    condition = both.original(name + '-leading')
    line = 6 + (name in ['left-cv', 'cv-pair']) + (name in ['right-cv', 'cv-pair'])
    diagnostic = 'DIAGNOSTIC "Warning" ' + prior.value(b'A non-numeric value encountered') + f' {line}'
    replacements = {
        '~$error_handler_eligible(S, 2)': '$error_handler_eligible(S, 2)',
        '$error_handler_eligible(S, 8192)': '~$error_handler_eligible(S, 8192)',
        'S.ERRORHANDLER.LEVELS = 8192': 'S.ERRORHANDLER.LEVELS = 2',
        'S.EVENTS = [OUTPUT ([80]), ' + diagnostic + ', ' + diagnostic + ']': 'S.EVENTS = [OUTPUT ([80])]',
        'S.STORE = S_binary.STORE': 'S.STORE[0:|S_binary.STORE|] = S_binary.STORE'}
    for before, after in replacements.items():
        assert condition.count(before) == 1
        condition = condition.replace(before, after)
    return condition


def frontier(name, fixture, path):
    bindings = bindings_for(name, fixture, path)
    stop = next(i for i, binding in enumerate(bindings) if binding.startswith('pobobjectreturn_seed = '))
    _, inherited = left.frontier(name, fixture, path)
    checks = [(label, condition.replace('selected_lhs_modulo_handler', 'selected_both_modulo_handler'))
              for label, condition in inherited[:4]]
    checks += [
        ('completed LEFT notice advances its saved integer before the fresh RHS Warning snapshot',
         r'S_resume.RESULT = KNOWN PNULL /\ '
         r'$integer_warning_valid(S_resume, pintegeroperation, INTEGER_LEFT, pintegerconversion_left, 1) /\ '
         r'S_left_complete = $integer_converted(S_resume, pintegeroperation, INTEGER_LEFT, i_left) /\ '
         r'S_left_complete.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT i_left)) :: ptask_tail* /\ '
         r'S_warning_right = $dz_raw(S_left_complete) /\ '
         r'$integer_warning_valid(S_warning_right, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 0) /\ '
         r'S_warning_right.RESULT = KNOWN PNULL /\ S_warning_right.EVENTS = S_resume.EVENTS /\ '
         r'S_warning_right.STORE = S_resume.STORE /\ S_warning_right.ERRORHANDLER = S_resume.ERRORHANDLER /\ '
         r'S_warning_right.OUTPUTBUFFERS[0].BYTES = $ptascii("AH")'),
        ('the second Warning selects the same ordinary handler after exact first-call restoration',
         r'$error_call_valid(S_invoke_right, perrorcall_right) /\ perrorcall_right.TARGET = eps /\ '
         r'perrorcall_right.CALLBACK = perrorcall.CALLBACK /\ perrorcall_right.LEVEL = 2 /\ '
         r'perrorcall_right.MESSAGE = $ptascii("A non-numeric value encountered") /\ '
         r'perrorcall_right.SITE = pintegeroperation.SITE /\ perrorcall_right.LINE = pintegeroperation.LINE /\ '
         r'S_invoke_right.CURRENT = S_binary.CURRENT /\ S_invoke_right.FRAMES = S_binary.FRAMES /\ '
         r'S_invoke_right.REPORTING = S_binary.REPORTING /\ S_invoke_right.EVENTS = [OUTPUT ([80])]'),
        ('the second borrowed NULL return uses two fresh formals while both first-call cells stay retired',
         r'pcallcontext_handler_right.FUNCTION = pfunction_handler.ORIGIN /\ '
         r'pshutdownproducer_handler_right.TARGET = pcalltarget_handler_right /\ '
         r'pshutdownproducer_handler_right.SITE = (perrorcall_right.SITE) /\ '
         r'pshutdownproducer_handler_right.INTERNAL /\ pshutdownproducer_handler_right.CLONE = eps /\ '
         r'$consumer_producer_snapshot(pshutdownproducer_handler_right) /\ '
         r'$target_function(S_return_right, pcallcontext_handler_right.TARGET) = (pfunction_handler) /\ '
         r'S_return_right.STORE[n_cell_level_right] = DEFINED (PINT 2) /\ '
         r'$string_bytes(pvalue_message_right) = ($ptascii("A non-numeric value encountered")) /\ '
         r'n_cell_level_right =/= n_cell_message_right /\ '
         r'~(n_cell_level_right <- [n_cell_level, n_cell_message]) /\ '
         r'~(n_cell_message_right <- [n_cell_level, n_cell_message]) /\ '
         r'~((HCELL n_cell_level) <- S_return_right.ALLOCATIONS) /\ '
         r'~((HCELL n_cell_message) <- S_return_right.ALLOCATIONS) /\ '
         r'pframe_handler_right.CONTEXT = S_binary.CURRENT /\ '
         r'S_return_right.ERRORHANDLER.CALLBACK = eps /\ '
         r'S_return_right.EVENTS = [OUTPUT ([80])] /\ '
         r'S_return_right.OUTPUTBUFFERS[0].BYTES = $ptascii("AHH")'),
        ('the second real formal retirement and exact finish restore the RHS cursor before Error issuance',
         r'S_handler_right.RESULT = KNOWN PNULL /\ S_handler_right.ERRORHANDLER.CALLBACK = eps /\ '
         r'$call_task_valid(S_handler_right, ERROR_HANDLER_RESULT perrorcall_return_right) /\ '
         r'perrorcall_return_right.RESUME = perrorcall_right.RESUME /\ '
         r'perrorcall_return_right.CALLBACK = perrorcall_right.CALLBACK /\ '
         r'perrorcall_return_right.TARGET = (pcallcontext_handler_right.TARGET) /\ '
         r'$error_selected_roots(perrorcall_return_right.TARGET) = eps /\ '
         r'~$destructor_operational(S_handler_right) /\ S_handler_right.DESTRUCTION.CLEANUPS = eps /\ '
         r'S_handler_right.CURRENT = S_binary.CURRENT /\ S_handler_right.FRAMES = S_binary.FRAMES /\ '
         r'S_handler_right.CVS = S_binary.CVS /\ S_handler_right.ENV = S_binary.ENV /\ '
         r'S_handler_right.REPORTING = S_binary.REPORTING /\ '
         r'S_handler_right.ERRORHANDLERS = S_binary.ERRORHANDLERS /\ '
         r'$error_handler_finish(S_handler_right, perrorcall_return_right) = S /\ '
         r'~((HCELL n_cell_level_right) <- S_handler_right.ALLOCATIONS) /\ '
         r'~((HCELL n_cell_message_right) <- S_handler_right.ALLOCATIONS) /\ '
         r'S_handler_right.EVENTS = [OUTPUT ([80])]'),
        ('both completed original conversions and exact live Error authorize their original capture',
         original(name) + r' /\ $ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('two callback histories preserve native source roots and buffered AHH without reviving any formal',
         r'$declaration_history_valid(S_return) /\ $declaration_history_valid(S_return_right) /\ '
         r'$declaration_history_valid(S) /\ $call_current_valid(S) /\ '
         r'$ob_object_final_native_method(S) = (pobobjectreturn) /\ '
         r'$integer_standard_object_handlers(S, POBJECT n_object) /\ '
         r'$heap_count(HOBJECT n_object, $machine_roots(S)) = 2 /\ '
         r'$heap_count(HCELL n_cell_level, $machine_roots(S)) = 0 /\ '
         r'$heap_count(HCELL n_cell_message, $machine_roots(S)) = 0 /\ '
         r'$heap_count(HCELL n_cell_level_right, $machine_roots(S)) = 0 /\ '
         r'$heap_count(HCELL n_cell_message_right, $machine_roots(S)) = 0 /\ '
         r'S.OUTPUTBUFFERS = S_handler_right.OUTPUTBUFFERS /\ '
         r'S.OUTPUTBUFFERS[0].BYTES = $ptascii("AHH") /\ '
         r'S.DESTRUCTION = S_binary.DESTRUCTION /\ S.DECLARATIONS = S_binary.DECLARATIONS /\ '
         r'S.TRACE = S_binary.TRACE /\ S.ERRORFATALTRACE = S_binary.ERRORFATALTRACE /\ ' + prior.public('S'))]
    return bindings[:stop], checks


def lifecycle(name, fixture, path):
    bindings = bindings_for(name, fixture, path)
    _, checks = left.lifecycle(name, fixture, path)
    before = left.original(name)
    assert checks[0][1].count(before) == 1
    checks[0] = ('two completed selected Warnings capture only their authentic nonowning Error source',
                 checks[0][1].replace(before, original(name)))
    checks = [(label, condition.replace('$ptascii("AH")', '$ptascii("AHH")'))
              for label, condition in checks]
    checks += [('both second-call formals stay retired while capture preserves the actual full store',
        r'$error_handler_finish(S_handler_right, perrorcall_return_right) = S /\ '
        r'S_capture.STORE = S.STORE /\ '
        r'~((HCELL n_cell_level_right) <- S_capture.ALLOCATIONS) /\ '
        r'~((HCELL n_cell_message_right) <- S_capture.ALLOCATIONS) /\ '
        r'$heap_count(HCELL n_cell_level_right, $machine_roots(S_capture)) = 0 /\ '
        r'$heap_count(HCELL n_cell_message_right, $machine_roots(S_capture)) = 0 /\ '
        r'$heap_count(HCELL n_cell_level_right, $machine_roots(S_retired)) = 0 /\ '
        r'$heap_count(HCELL n_cell_message_right, $machine_roots(S_retired)) = 0 /\ '
        r'S_capture.OUTPUTBUFFERS[0].BYTES = $ptascii("AHH") /\ '
        r'S_retired.ERRORHANDLER = S_binary.ERRORHANDLER')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
