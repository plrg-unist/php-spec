#!/usr/bin/env python3
"""Selected MOD Warning capture preserves source authority and real retirement."""
import output_final_selected_warning_modulo_error_state as author
import output_final_default_unrelated_handler_modulo_error_review_state as runner

PREFIX = author.PREFIX
CASES = {name: author.CASES[name] for name in ['constant', 'cv-pair']}


def task(operation='pintegeroperation', phase='INTEGER_RIGHT i_left',
         conversion='pintegerconversion', cursor='1'):
    return '(INTEGER_OPERATOR_WARNING ' + operation + ' (' + phase + ') ' + conversion + ' ' + cursor + ') :: ptask_tail*'


def authority(name, fixture, path):
    if name == 'cv-pair':
        bindings, _ = author.lifecycle(name, fixture, path)
        return bindings, [
            ('the completed callback leaves two retired formals and buffered H at actual Error capture',
             r'$error_handler_finish(S_handler, perrorcall_return) = S /\ '
             r'S_capture.EVENTS = [OUTPUT ([80])] /\ S_capture.OUTPUTBUFFERS[0].BYTES = $ptascii("AH") /\ '
             r'~((HCELL n_cell_level) <- S_capture.ALLOCATIONS) /\ ~((HCELL n_cell_message) <- S_capture.ALLOCATIONS) /\ '
             r'$heap_count(HCELL n_cell_level, $machine_roots(S_capture)) = 0 /\ '
             r'$heap_count(HCELL n_cell_message, $machine_roots(S_capture)) = 0 /\ '
             r'$ob_object_source_birth(pobobjectreturn_capture.SOURCE) = eps /\ '
             r'$task_nodes(OB_USER_OBJECT_STRING pobobjectreturn_capture) = $task_nodes(OB_USER_OBJECT_STRING pobobjectreturn)'),
            ('native unwind releases only its two operand cells after the handler cells have retired',
             r'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HCELL n_cell_left), DESTRUCTION_VALUE (HCELL n_cell_right)] /\ '
             r'S_queue.DESTRUCTION.RELEASES = [pdestructionrelease] /\ '
             r'S_queue.STORE[n_cell_left] = DEFINED pvalue_left /\ S_queue.STORE[n_cell_right] = DEFINED pvalue_right /\ '
             r'~$ob_object_final_cv_ready(S_queue, pobobjectreturn_capture, pdestructionframe, n_exception) /\ '
             r'$heap_count(HCELL n_cell_level, $machine_roots(S_queue)) = 0 /\ '
             r'$heap_count(HCELL n_cell_message, $machine_roots(S_queue)) = 0'),
            ('C0 becomes ready after real operand retirement with the original Error retained once',
             r'$ob_object_final_cv_ready(S_exit, pobobjectreturn_capture, pdestructionframe, n_exception) /\ '
             r'~((HCELL n_cell_left) <- S_exit.ALLOCATIONS) /\ ~((HCELL n_cell_right) <- S_exit.ALLOCATIONS) /\ '
             r'$heap_count(HCELL n_cell_left, $machine_roots(S_exit)) = 0 /\ '
             r'$heap_count(HCELL n_cell_right, $machine_roots(S_exit)) = 0 /\ '
             r'$heap_count(HOBJECT n_exception, $machine_roots(S_exit)) = 1 /\ '
             r'S_exit.ERRORHANDLER = S_binary.ERRORHANDLER /\ S_exit.EVENTS = [OUTPUT ([80])]'),
            ('fatal reporting retires the Error without reviving handler or operand cells',
             r'~((HOBJECT n_exception) <- S_retired.ALLOCATIONS) /\ '
             r'$heap_count(HOBJECT n_exception, $machine_roots(S_retired)) = 0 /\ '
             r'$heap_count(HCELL n_cell_left, $machine_roots(S_retired)) = 0 /\ '
             r'$heap_count(HCELL n_cell_right, $machine_roots(S_retired)) = 0 /\ '
             r'$heap_count(HCELL n_cell_level, $machine_roots(S_retired)) = 0 /\ '
             r'$heap_count(HCELL n_cell_message, $machine_roots(S_retired)) = 0 /\ '
             r'$eager_cleanup_valid(S_retired, pdestructioncleanup) /\ '
             r'~$eager_cleanup_valid(S_receipt_site, pdestructioncleanup_site) /\ '
             r'S_retired.ERRORHANDLER = S_binary.ERRORHANDLER /\ '
             r'pobdeactivate.BUFFERS[0].BYTES = $ptascii("AH") /\ ' + author.prior.public('S_retired'))]

    bindings, _ = author.frontier(name, fixture, path)
    bindings += [
        'S_saved = S[.TODO = ' + task(phase='INTEGER_RIGHT 2') + ']',
        '$integer_conversion(PSTRING_CARRIER INTERNED_STRING ($ptascii("0y"))) = (pintegerconversion_other)',
        'S_snapshot = S[.TODO = ' + task(conversion='pintegerconversion_other') + ']',
        'S_cursor = S[.TODO = ' + task(cursor='0') + ']',
        'S_scratch = S[.RESULT = KNOWN (POBJECT pobobjectreturn.OBJECT)]',
        'S_retarget = S[.ERRORHANDLER = S.ERRORHANDLER[.CALLBACK = (PSTRING ($ptascii("h")))]]',
        'S_retarget_raw = $dz_raw(S_retarget)', 'S_retarget_generated = $throwable_transition(S_retarget, S_retarget_raw)',
        'S.FUNCTIONS = pfunction_handler :: pfunction_tail*',
        'pfunction_changed = pfunction_handler[.ENV = pfunction_handler.ENV[.STRICT = ~pfunction_handler.ENV.STRICT]]',
        'S_descriptor = S[.FUNCTIONS = pfunction_changed :: pfunction_tail*]',
        'S_descriptor_raw = $dz_raw(S_descriptor)', 'S_descriptor_generated = $throwable_transition(S_descriptor, S_descriptor_raw)',
        'S.SOURCES = [pcunit]',
        'pcunit.AST = PROGRAM (statement_declare :: statement_handler :: statement_tail*)',
        'statement_handler = NStmtFunction phpType14_handler phpType4_handler phpType11_handler (SEQUENCE ([phpType17_left, phpType17_right])) phpType18_handler phpType23_handler metadata_handler',
        'phpType17_left = NParam phpType14_param phpType24_param ABSENT phpType4_ref phpType4_variadic phpType10_param phpType5_param phpType37_param metadata_param',
        'phpType17_typed = NParam phpType14_param phpType24_param (NIdentifier (BYTES "aW50") metadata_param) phpType4_ref phpType4_variadic phpType10_param phpType5_param phpType37_param metadata_param',
        'statement_typed = NStmtFunction phpType14_handler phpType4_handler phpType11_handler (SEQUENCE ([phpType17_typed, phpType17_right])) phpType18_handler phpType23_handler metadata_handler',
        'pcunit_typed = $pcsource(pcunit.ID, PROGRAM (statement_declare :: statement_typed :: statement_tail*))',
        'S_rawparam = S[.SOURCES = [pcunit_typed]]',
        'S_rawparam_raw = $dz_raw(S_rawparam)', 'S_rawparam_generated = $throwable_transition(S_rawparam, S_rawparam_raw)']
    checks = [
        ('genuine selected callback completion captures its own live MOD Error',
         author.original(name) + r' /\ $ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror)) /\ '
         r'$declaration_history_valid(S) /\ S.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK) /\ '
         r'S.OUTPUTBUFFERS[0].BYTES = $ptascii("AH")'),
        ('a valid forged left cache cannot replace fresh original conversion despite the same zero Error',
         r'$integer_warning_valid(S_saved, pintegeroperation, INTEGER_RIGHT 2, pintegerconversion, 1) /\ '
         r'$dz_raw(S_saved) = S_request /\ $ob_object_division_error_capture(S_saved, S_generated) = eps'),
        ('an equal-zero singleton Warning snapshot still has to belong to the current RHS',
         r'pintegerconversion_other.VALUE = 0 /\ pintegerconversion_other.NOTICES = pintegerconversion.NOTICES /\ '
         r'$integer_warning_valid(S_snapshot, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion_other, 1) /\ '
         r'$dz_raw(S_snapshot) = S_request /\ $ob_object_division_error_capture(S_snapshot, S_generated) = eps'),
        ('an unconsumed Warning cursor cannot borrow the later native Error',
         r'$integer_warning_valid(S_cursor, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 0) /\ '
         r'$error_handler_eligible(S_cursor, 2) /\ $ob_object_division_error_capture(S_cursor, S_generated) = eps'),
        ('the same actual zero Error does not authorize owning result scratch',
         r'$call_current_valid(S_scratch) /\ $dz_raw(S_scratch) = S_request /\ '
         r'$ob_object_division_error_capture(S_scratch, S_generated) = eps'),
        ('another genuine two-parameter callable cannot replace the completed literal-echo handler',
         r'$error_handler_eligible(S_retarget, 2) /\ $error_handler_target(S_retarget, PSTRING ($ptascii("h"))) =/= eps /\ '
         r'$call_current_valid(S_retarget) /\ S_retarget_raw = S_request[.ERRORHANDLER = S_retarget.ERRORHANDLER] /\ '
         r'$ob_object_return_error_live(S_retarget_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_retarget, S_retarget_generated) = eps'),
        ('a descriptor edit fails the complete source image before Error materialization',
         r'$function_at($all_functions(S_descriptor), pfunction_handler.ORIGIN) = (pfunction_changed) /\ '
         r'~$declaration_history_valid(S_descriptor) /\ '
         r'$integer_warning_valid(S_descriptor, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 1) /\ '
         r'S_descriptor_raw = S_request[.FUNCTIONS = S_descriptor.FUNCTIONS] /\ '
         r'S_descriptor_generated = S_descriptor_raw /\ S_descriptor_generated.OBJECTS = S.OBJECTS /\ '
         r'$ob_object_division_error_capture(S_descriptor, S_descriptor_generated) = eps'),
        ('raw typed parameters cannot borrow an unchanged untyped compiled signature',
         r'S_rawparam.FUNCTIONS = S.FUNCTIONS /\ '
         r'$origin_node(S_rawparam.SOURCES, pfunction_handler.ORIGIN) = (statement_typed) /\ '
         r'~$declaration_history_valid(S_rawparam) /\ '
         r'$integer_warning_valid(S_rawparam, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 1) /\ '
         r'S_rawparam_raw = S_request[.SOURCES = S_rawparam.SOURCES] /\ '
         r'S_rawparam_generated = S_rawparam_raw /\ S_rawparam_generated.OBJECTS = S.OBJECTS /\ '
         r'$ob_object_division_error_capture(S_rawparam, S_rawparam_generated) = eps')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX, runner.authority = CASES, PREFIX, authority
    runner.main()
