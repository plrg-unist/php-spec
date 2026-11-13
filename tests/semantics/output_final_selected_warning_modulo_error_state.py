#!/usr/bin/env python3
"""A real selected RHS Warning callback returns before native MOD failure."""
import output_final_default_unrelated_handler_right_modulo_conversion_error_state as previous
import output_final_selected_warning_modulo_error_sources as sources

prior, shared = previous.prior, previous.shared
PREFIX = previous.PREFIX.replace('def $dp_phase(S, n) = false -- otherwise', r'''
def $dp_phase(S, 10) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 0) :: ptask_tail*
  -- if pintegerconversion.NOTICES = [(2, ptbytes)]
def $dp_phase(S, 11) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 1
def $dp_phase(S, 12) = true
  -- if S.TODO = (RETURN_UNWIND (KNOWN PNULL) porigin?) :: ptask_tail*
  -- if S.FRAMES = pframe_handler :: pframe :: eps
  -- if pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_handler*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 1
def $dp_phase(S, 13) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 1
def $dp_phase(S, n) = false -- otherwise''')
CASES = {name: sources.CASES['native-selected-warning-modulo-error-' + name]
         for name in ['constant', 'left-cv', 'right-cv', 'cv-pair']}


def bindings_for(name, fixture, path):
    bindings, checks = previous.bindings_for(name + '-leading', fixture, path)
    old = prior.seek('S', 'S_binary', 9)
    index = bindings.index(old[0])
    assert bindings[index:index + len(old)] == old
    bindings[index:index + len(old)] = [
        *prior.seek('S_warning', 'S_binary', 10),
        'S_warning.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i_left) pintegerconversion 0) :: ptask_tail*',
        *prior.seek('S_invoke', 'S_warning', 11),
        'S_invoke.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i_left) pintegerconversion 1',
        '$error_handler_target(S_invoke, perrorcall.CALLBACK) = (pcalltarget_handler)',
        '$target_function(S_invoke, pcalltarget_handler) = (pfunction_handler)',
        *prior.seek('S_return', 'S_invoke', 12),
        'S_return.CURRENT = (pcallcontext_handler)',
        'pcallcontext_handler.TARGET = API_BORROWED_TARGET pshutdownproducer_handler',
        'S_return.FRAMES = pframe_handler :: pframe :: eps',
        '$lookup(S_return.ENV, $ptascii("level")) = (n_cell_level)',
        '$lookup(S_return.ENV, $ptascii("message")) = (n_cell_message)',
        'S_return.STORE[n_cell_message] = DEFINED pvalue_message',
        *prior.seek('S_handler', 'S_return', 13),
        'S_handler.TODO = (ERROR_HANDLER_RESULT perrorcall_return) :: ptask_tail*',
        *prior.seek('S', 'S_handler', 9)]
    return bindings, checks


def original(name):
    source = previous.original(name + '-leading')
    replacements = {
        '~$error_handler_eligible(S, 2)': '$error_handler_eligible(S, 2)',
        '$error_handler_eligible(S, 8192)': '~$error_handler_eligible(S, 8192)',
        'S.ERRORHANDLER.LEVELS = 8192': 'S.ERRORHANDLER.LEVELS = 2',
        'S.STORE = S_binary.STORE': 'S.STORE[0:|S_binary.STORE|] = S_binary.STORE'}
    line = 6 + (name in ['left-cv', 'cv-pair']) + (name in ['right-cv', 'cv-pair'])
    replacements['S.EVENTS = [OUTPUT ([80]), DIAGNOSTIC "Warning" ' +
        prior.value(b'A non-numeric value encountered') + f' {line}]'] = 'S.EVENTS = [OUTPUT ([80])]'
    for before, after in replacements.items():
        assert source.count(before) == 1
        source = source.replace(before, after)
    return source


def frontier(name, fixture, path):
    bindings, _ = bindings_for(name, fixture, path)
    stop = next(i for i, binding in enumerate(bindings) if binding.startswith('pobobjectreturn_seed = '))
    checks = [
        ('genuine source reaches selected Warning invocation with the cached RHS and incremented cursor',
         r'$integer_warning_valid(S_warning, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 0) /\ '
         r'S_warning.RESULT = KNOWN PNULL /\ $error_handler_eligible(S_warning, 2) /\ '
         r'S_warning.ERRORHANDLER.LEVELS = 2 /\ '
         r'$error_call_valid(S_invoke, perrorcall) /\ perrorcall.TARGET = eps /\ '
         r'perrorcall.LEVEL = 2 /\ perrorcall.MESSAGE = $ptascii("A non-numeric value encountered") /\ '
         r'perrorcall.SITE = pintegeroperation.SITE /\ perrorcall.LINE = pintegeroperation.LINE /\ '
         r'S_invoke.EVENTS = [OUTPUT ([80])] /\ S_invoke.CURRENT = S_binary.CURRENT /\ '
         r'S_invoke.FRAMES = S_binary.FRAMES /\ S_invoke.REPORTING = S_binary.REPORTING'),
        ('ordinary callback body returns NULL with its two live formal cells and the native caller saved',
         r'pcallcontext_handler.FUNCTION = pfunction_handler.ORIGIN /\ '
         r'pshutdownproducer_handler.TARGET = pcalltarget_handler /\ '
         r'pshutdownproducer_handler.SITE = (perrorcall.SITE) /\ '
         r'pshutdownproducer_handler.INTERNAL /\ pshutdownproducer_handler.CLONE = eps /\ '
         r'$consumer_producer_snapshot(pshutdownproducer_handler) /\ '
         r'$target_function(S_return, pcallcontext_handler.TARGET) = (pfunction_handler) /\ '
         r'pfunction_handler.NAME = $ptascii("selected_rhs_modulo_handler") /\ '
         r'pfunction_handler.CVS = [$ptascii("level"), $ptascii("message")] /\ '
         r'~pfunction_handler.SIGNATURE.BYREF /\ '
         r'pfunction_handler.SIGNATURE.RETURNS = eps /\ '
         r'pfunction_handler.SIGNATURE.PARAMETERS = '
         r'[{NAME ($ptascii("level")), TYPE eps, BYREF false, VARIADIC false, REQUIRED true, DEFAULT PSNONE}, '
         r'{NAME ($ptascii("message")), TYPE eps, BYREF false, VARIADIC false, REQUIRED true, DEFAULT PSNONE}]'),
        ('actual callback formals retain the Warning arguments while the literal echo stays buffered',
         r'S_return.STORE[n_cell_level] = DEFINED (PINT 2) /\ '
         r'$string_bytes(pvalue_message) = ($ptascii("A non-numeric value encountered")) /\ '
         r'n_cell_level =/= n_cell_message /\ S_return.ERRORHANDLER.CALLBACK = eps /\ '
         r'pframe_handler.CONTEXT = S_binary.CURRENT /\ '
         r'S_return.EVENTS = [OUTPUT ([80])] /\ '
         r'S_binary.OUTPUTBUFFERS[0].BYTES = $ptascii("A") /\ '
         r'S_return.OUTPUTBUFFERS[0].BYTES = $ptascii("AH")'),
        ('completed callback restores the native caller before the handled NULL result resumes conversion',
         r'S_handler.RESULT = KNOWN PNULL /\ S_handler.ERRORHANDLER.CALLBACK = eps /\ '
         r'$call_task_valid(S_handler, ERROR_HANDLER_RESULT perrorcall_return) /\ '
         r'perrorcall_return.RESUME = perrorcall.RESUME /\ '
         r'perrorcall_return.CALLBACK = perrorcall.CALLBACK /\ '
         r'perrorcall_return.TARGET = (pcallcontext_handler.TARGET) /\ '
         r'$error_selected_roots(perrorcall_return.TARGET) = eps /\ '
         r'~$destructor_operational(S_handler) /\ S_handler.DESTRUCTION.CLEANUPS = eps /\ '
         r'S_handler.CURRENT = S_binary.CURRENT /\ S_handler.FRAMES = S_binary.FRAMES /\ '
         r'S_handler.CVS = S_binary.CVS /\ S_handler.ENV = S_binary.ENV /\ '
         r'S_handler.REPORTING = S_binary.REPORTING /\ S_handler.ERRORHANDLERS = S_binary.ERRORHANDLERS /\ '
         r'$error_handler_finish(S_handler, perrorcall_return) = S /\ '
         r'~((HCELL n_cell_level) <- S_handler.ALLOCATIONS) /\ '
         r'~((HCELL n_cell_message) <- S_handler.ALLOCATIONS) /\ '
         r'S_handler.EVENTS = [OUTPUT ([80])]'),
        ('consumed RHS Warning resumes the original native MOD Error without new source authority',
         r'n = 1 /\ i_left = 1 /\ pintegerconversion.INPUT = pvalue_right /\ '
         r'pintegerconversion.VALUE = 0 /\ pintegerconversion.NOTICES = [(2, ($ptascii("A non-numeric value encountered")))] /\ '
         r'S.RESULT = KNOWN PNULL /\ S.CURRENT = S_binary.CURRENT /\ S.FRAMES = S_binary.FRAMES /\ '
         r'S.ORIGIN = S_binary.ORIGIN /\ S.CVS = S_binary.CVS /\ S.ENV = S_binary.ENV /\ '
         r'S.ERRORHANDLER = S_binary.ERRORHANDLER /\ S.ERRORHANDLERS = S_binary.ERRORHANDLERS /\ '
         r'S.REPORTING = S_binary.REPORTING /\ S.EVENTS = [OUTPUT ([80])] /\ '
         r'$integer_warning_valid(S, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, n) /\ '
         r'$integer_pointer_value(S, pintegeroperation.LEFTPOINTER) = (pvalue_left) /\ '
         r'$integer_pointer_value(S, pintegeroperation.RIGHTPOINTER) = (pvalue_right) /\ '
         r'S_request.RESULT = KNOWN PNULL /\ S_request.EVENTS = S.EVENTS /\ '
         r'S_request.STORE = S.STORE /\ S_request.TODO = ptask_tail* /\ '
         r'S_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) z /\ '
         r'$ob_object_division_error_source(S_generated, pfunction, pobreturnerror) /\ '
         r'$ob_object_return_error_live(S_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))')]
    checks += [
        ('restored native state retains full original source, current operands and fixed Error authority', original(name)),
        ('ordinary callback history and roots remain valid without replacing the live machine',
         r'$declaration_history_valid(S_return) /\ $declaration_history_valid(S) /\ $call_current_valid(S) /\ '
         r'$ob_object_final_native_method(S) = (pobobjectreturn) /\ '
         r'$integer_standard_object_handlers(S, POBJECT n_object) /\ '
         r'$heap_count(HOBJECT n_object, $machine_roots(S)) = 2 /\ '
         r'$heap_count(HCELL n_cell_level, $machine_roots(S)) = 0 /\ '
         r'$heap_count(HCELL n_cell_message, $machine_roots(S)) = 0 /\ '
         r'S.OUTPUTBUFFERS = S_handler.OUTPUTBUFFERS /\ '
         r'S.OUTPUTBUFFERS[0].BYTES = $ptascii("AH") /\ '
         r'S.DESTRUCTION = S_binary.DESTRUCTION /\ '
         r'S.DECLARATIONS = S_binary.DECLARATIONS /\ '
         r'S.TRACE = S_binary.TRACE /\ S.ERRORFATALTRACE = S_binary.ERRORFATALTRACE /\ ' + prior.public('S'))]
    return bindings[:stop], checks


def lifecycle(name, fixture, path):
    bindings, _ = bindings_for(name, fixture, path)
    _, checks = previous.lifecycle(name + '-leading', fixture, path)
    before = previous.original(name + '-leading')
    assert checks[0][1].count(before) == 1
    checks[0] = ('completed selected Warning captures only the authentic nonowning Error source',
                 checks[0][1].replace(before, original(name)))
    checks[2] = ('C0 reports the original fatal Error after retiring the native CVs', checks[2][1])
    checks += [('handler output stays buffered while its real formals remain retired through FINAL reporting',
        r'$error_handler_finish(S_handler, perrorcall_return) = S /\ '
        r'S_capture.EVENTS = [OUTPUT ([80])] /\ '
        r'S_capture.OUTPUTBUFFERS[0].BYTES = $ptascii("AH") /\ '
        r'pobdeactivate.BUFFERS[0].BYTES = $ptascii("AH") /\ '
        r'$heap_count(HCELL n_cell_level, $machine_roots(S_capture)) = 0 /\ '
        r'$heap_count(HCELL n_cell_message, $machine_roots(S_capture)) = 0 /\ '
        r'$heap_count(HCELL n_cell_level, $machine_roots(S_retired)) = 0 /\ '
        r'$heap_count(HCELL n_cell_message, $machine_roots(S_retired)) = 0 /\ '
        r'S_retired.ERRORHANDLER = S_binary.ERRORHANDLER /\ '
        r'S_retired.ERRORHANDLERS = S_binary.ERRORHANDLERS')]
    return bindings, checks


if __name__ == '__main__':
    previous.previous.CASES, previous.previous.PREFIX = CASES, PREFIX
    previous.previous.frontier = frontier
    previous.previous.lifecycle = lifecycle
    previous.previous.main()
