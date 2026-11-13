#!/usr/bin/env python3
"""Completed RHS MOD retains source, current snapshots and full notice vectors."""
import output_final_default_unrelated_handler_modulo_error_review_state as common
import output_final_default_unrelated_warning_handler_modulo_error_review_state as harness
import output_final_default_unrelated_handler_right_modulo_conversion_error_state as author
import output_final_default_unrelated_handler_right_modulo_conversion_error_sources as sources

PAIR = sources.CASES['native-default-unrelated-handler-right-modulo-conversion-error-cv-pair-string']
OWN = PAIR.replace(b'$left = 1;', b'$left = 1; $other = 1;')
CONST = sources.CASES['native-default-unrelated-handler-right-modulo-conversion-error-constant-leading']
UNUSED = CONST.replace(b"return 1 % '0x';", b"$unused = 0; return 1 % '0x';")
RANGE = sources.CASES['native-default-unrelated-handler-right-modulo-conversion-error-cv-pair-finite']
assert OWN != PAIR and UNUSED != CONST
CASES = {'source': OWN, 'snapshots': OWN, 'constant': CONST, 'precision-classes': PAIR,
         'warning-classes': RANGE, 'precision-handlers': PAIR, 'warning-handlers': RANGE,
         'carrier': PAIR, 'unused-cv': UNUSED}
CAPTURE = author.CAPTURE


def task(operation='pintegeroperation', phase='INTEGER_RIGHT i_left',
         conversion='pintegerconversion', cursor='1'):
    return common.task(operation, phase, conversion, cursor)


def authority(name, fixture, path):
    selected = ('constant-leading' if name in ['constant', 'unused-cv'] else
                'cv-pair-finite' if name in ['warning-classes', 'warning-handlers'] else 'cv-pair-string')
    bindings, _ = author.frontier(selected, fixture, path)
    genuine = author.original(selected)
    if name in ['source', 'snapshots']:
        genuine = genuine.replace('pfunction.CVS = [$ptascii("left"), $ptascii("right")]',
                                  'pfunction.CVS = [$ptascii("left"), $ptascii("other"), $ptascii("right")]')
        genuine = genuine.replace('|S.ENV| = 2', '|S.ENV| = 3')
    if name == 'source':
        bindings += ['pintegeroperation_other = pintegeroperation[.LEFT = VARIABLE ($ptascii("other")) z_left][.LEFTPOINTER = INTEGER_CV ($ptascii("other"))]',
                     'S_other = S[.TODO = ' + task('pintegeroperation_other') + ']']
        checks = [('the reached pair retains its completed RHS notice and real live Error', genuine + r' /\ ' + CAPTURE),
                  ('an equal foreign left CV cannot replace the original compiled read',
                   r'$integer_pointer_value(S_other, pintegeroperation_other.LEFTPOINTER) = (pvalue_left) /\ '
                   r'~$integer_operation_source(S_other, pintegeroperation_other) /\ '
                   r'$ob_object_division_error_capture(S_other, S_generated) = eps')]
        for label, changes in [
            ('each operand retains its own compiled line', [('left_line', '[.LEFT = VARIABLE n_left* $(z_left + 1)]'),
                                                          ('right_line', '[.RIGHT = VARIABLE n_right* $(z_right + 1)]')]),
            ('KNOWN values cannot replace the actual private CV producers',
             [('left_known', '[.LEFT = KNOWN pvalue_left][.LEFTPOINTER = INTEGER_COPY pvalue_left]'),
              ('right_known', '[.RIGHT = KNOWN pvalue_right][.RIGHTPOINTER = INTEGER_COPY pvalue_right]')])]:
            conditions = []
            for suffix, update in changes:
                operation, state = 'pintegeroperation_' + suffix, 'S_' + suffix
                bindings += [operation + ' = pintegeroperation' + update, state + ' = S[.TODO = ' + task(operation) + ']']
                conditions += ['~$integer_operation_source(' + state + ', ' + operation + ')',
                               '$ob_object_division_error_capture(' + state + ', S_generated) = eps']
            checks += [(label, r' /\ '.join(conditions))]
        conditions = []
        for side, field in [('left', 0), ('right', 1)]:
            state = 'S_reference_' + side
            bindings += [state + ' = S[.REFCELLS = S.REFCELLS ++ [n_cell_' + side + ']]']
            conditions += ['$ob_object_error_operand_value(' + state + ', pintegeroperation.' + side.upper() + ', [PCFIELD ' + str(field) + '], z) = eps',
                           '$ob_object_division_error_capture(' + state + ', S_generated) = eps']
        return bindings, checks + [('either reference-marked cell refuses the private-CV contour', r' /\ '.join(conditions))]
    if name == 'snapshots':
        bindings += [
            'S_saved = S[.TODO = ' + task(phase='INTEGER_RIGHT 2') + ']',
            'S_saved_raw = $dz_raw(S_saved)', 'S_saved_generated = $throwable_transition(S_saved, S_saved_raw)',
            '$integer_conversion(PFLOAT 4602678819172646912) = (pintegerconversion_float)',
            'S_snapshot = S[.TODO = ' + task(conversion='pintegerconversion_float') + ']',
            'S_snapshot_raw = $dz_raw(S_snapshot)', 'S_snapshot_generated = $throwable_transition(S_snapshot, S_snapshot_raw)',
            '$lookup(S.ENV, $ptascii("other")) = (n_cell_other)',
            'pintegeroperation_foreign = pintegeroperation[.LEFTPOINTER = INTEGER_CELL n_cell_other]',
            'S_foreign = S[.REFCELLS = S.REFCELLS ++ [n_cell_other]][.TODO = ' + task('pintegeroperation_foreign') + ']',
            'S_foreign_raw = $dz_raw(S_foreign)', 'S_foreign_generated = $throwable_transition(S_foreign, S_foreign_raw)',
            'S_cursor_zero = S[.TODO = ' + task(cursor='0') + ']',
            'S_cursor_two = S[.TODO = ' + task(cursor='2') + ']',
            'S_phase = S[.TODO = ' + task(phase='INTEGER_LEFT') + ']', 'S_phase_raw = $dz_raw(S_phase)',
            'S_scratch = S[.RESULT = KNOWN (POBJECT pobobjectreturn.OBJECT)]',
            'S_scratch_raw = $dz_raw(S_scratch)', 'S_scratch_generated = $throwable_transition(S_scratch, S_scratch_raw)']
        return bindings, [
            ('a forged left cache preserves the zero Error but fails fresh quiet reconversion',
             genuine + r' /\ ' + CAPTURE + r' /\ '
             r'$integer_warning_valid(S_saved, pintegeroperation, INTEGER_RIGHT 2, pintegerconversion, 1) /\ '
             r'S_saved_raw = S_request /\ S_saved_generated = S_generated /\ '
             r'$ob_object_division_error_capture(S_saved, S_saved_generated) = eps'),
            ('a valid zero FLOAT snapshot cannot replace the current zero STRING snapshot',
             r'pintegerconversion_float.INPUT = PFLOAT 4602678819172646912 /\ '
             r'pintegerconversion_float.VALUE = 0 /\ |pintegerconversion_float.NOTICES| = 1 /\ '
             r'$integer_warning_valid(S_snapshot, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion_float, 1) /\ '
             r'S_snapshot_raw = S_request /\ S_snapshot_generated = S_generated /\ '
             r'$ob_object_division_error_capture(S_snapshot, S_snapshot_generated) = eps'),
            ('a valid live foreign CELL pointer still fails canonical selection',
             r'n_cell_other =/= n_cell_left /\ (HCELL n_cell_other) <- S_foreign.ALLOCATIONS /\ '
             r'$integer_warning_valid(S_foreign, pintegeroperation_foreign, INTEGER_RIGHT i_left, pintegerconversion, 1) /\ '
             r'$integer_pointer_value(S_foreign, pintegeroperation_foreign.LEFTPOINTER) = (pvalue_left) /\ '
             r'$integer_pointer_select(S_foreign, pintegeroperation.LEFT) = (pintegeroperation.LEFTPOINTER) /\ '
             r'pintegeroperation_foreign.LEFTPOINTER =/= pintegeroperation.LEFTPOINTER /\ '
             r'S_foreign_raw = S_request[.REFCELLS = S_foreign.REFCELLS] /\ '
             r'$ob_object_return_error_live(S_foreign_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_foreign, S_foreign_generated) = eps'),
            ('cursor zero has an unconsumed notice and cursor two exceeds the full singleton',
             r'$integer_warning_valid(S_cursor_zero, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 0) /\ '
             r'~$integer_warning_valid(S_cursor_two, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 2) /\ '
             r'$ob_object_division_error_capture(S_cursor_zero, S_generated) = eps /\ '
             r'$ob_object_division_error_capture(S_cursor_two, S_generated) = eps'),
            ('a completed LEFT phase advances normally and cannot borrow the RIGHT Error',
             r'$integer_warning_valid(S_phase, pintegeroperation, INTEGER_LEFT, pintegerconversion, 1) /\ '
             r'S_phase_raw.COMPLETION = NORMAL /\ S_phase_raw.RESULT = KNOWN PNULL /\ '
             r'S_phase_raw.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 0)) :: ptask_tail* /\ '
             r'$ob_object_division_error_capture(S_phase, S_generated) = eps'),
            ('owning scratch adds a real root despite producing the same raw Error',
             r'$call_current_valid(S_scratch) /\ '
             r'$integer_warning_valid(S_scratch, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 1) /\ '
             r'$operand_nodes(S_scratch.RESULT) = [HOBJECT pobobjectreturn.OBJECT] /\ '
             r'$heap_count(HOBJECT pobobjectreturn.OBJECT, $machine_roots(S_scratch)) = $($heap_count(HOBJECT pobobjectreturn.OBJECT, $machine_roots(S)) + 1) /\ '
             r'S_scratch_raw = S_request /\ S_scratch_generated = S_generated /\ '
             r'$ob_object_division_error_capture(S_scratch, S_scratch_generated) = eps')]
    if name == 'constant':
        value = 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0y"))'
        request = 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0x"))'
        bindings += [
            '$integer_conversion(' + value + ') = (pintegerconversion_other)',
            'pintegeroperation_other = pintegeroperation[.RIGHT = KNOWN (' + value + ')][.RIGHTPOINTER = INTEGER_COPY (' + value + ')]',
            'S_other = S[.TODO = ' + task('pintegeroperation_other', conversion='pintegerconversion_other') + ']',
            'pvalue_request = ' + request,
            '$integer_conversion(pvalue_request) = (pintegerconversion_request)',
            'pintegeroperation_request = pintegeroperation[.RIGHT = KNOWN pvalue_request][.RIGHTPOINTER = INTEGER_COPY pvalue_request]',
            'S_request_right = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("0x")]][.TODO = ' + task('pintegeroperation_request', conversion='pintegerconversion_request') + ']',
            'S_request_next = S_generated[.STRINGDATA = S_request_right.STRINGDATA]']
        return bindings, [
            ('the actual CONST pair has cursor one and no operand cells', genuine + r' /\ ' + CAPTURE),
            ('equal zero and identical Warning text cannot replace the compiled RHS bytes',
             r'pintegerconversion_other.VALUE = 0 /\ pintegerconversion_other.NOTICES = pintegerconversion.NOTICES /\ '
             r'$integer_pointer_select(S_other, pintegeroperation_other.RIGHT) = (pintegeroperation_other.RIGHTPOINTER) /\ '
             r'$integer_slot_rank(S_other, porigin_operator, [PCFIELD 1], pintegeroperation_other.RIGHT) = (1) /\ '
             r'~$integer_operand_source(S_other, porigin_operator, [PCFIELD 1], pintegeroperation_other.RIGHT) /\ '
             r'$ob_object_division_error_capture(S_other, S_generated) = eps'),
            ('authenticated same-byte REQUEST cannot replace the compiled INTERNED RHS',
             r'$ob_object_string_value(S_request_right, pvalue_request) /\ '
             r'pintegerconversion_request.VALUE = 0 /\ pintegerconversion_request.NOTICES = pintegerconversion.NOTICES /\ '
             r'~$integer_operand_source(S_request_right, porigin_operator, [PCFIELD 1], pintegeroperation_request.RIGHT) /\ '
             r'$ob_object_return_error_live(S_request_next, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_request_right, S_request_next) = eps')]
    if name in ['precision-classes', 'warning-classes']:
        variants = ([('float', 'PFLOAT 4602678819172646912', '[8192]', '1', True),
                     ('nan', 'PFLOAT 9221120237041090560', '[2, 8192]', '2', False),
                     ('two_string', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5x"))', '[2, 8192]', '2', False),
                     ('quiet', 'PINT 0', 'eps', '1', False)] if name == 'precision-classes' else
                    [('leading', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0x"))', '[2]', '1', True),
                     ('infinite', 'PFLOAT 9218868437227405312', '[2]', '1', True),
                     ('precision', 'PFLOAT 4602678819172646912', '[8192]', '1', False)])
        checks = []
        for suffix, value, levels, cursor, accepted in variants:
            state, conversion = 'S_class_' + suffix, 'pintegerconversion_class_' + suffix
            bindings += ['$integer_conversion(' + value + ') = (' + conversion + ')',
                         '(z_level_' + suffix + ', ptbytes_notice_' + suffix + ')* = ' + conversion + '.NOTICES',
                         state + ' = S[.STORE = $set_cell(S.STORE, n_cell_right, DEFINED (' + value + '))][.TODO = ' + task(conversion=conversion, cursor=cursor) + ']']
            conditions = ([genuine, CAPTURE] if not checks else []) + [
                conversion + '.VALUE = 0', 'z_level_' + suffix + '* = ' + levels,
                '$ob_object_error_operand_value(' + state + ', pintegeroperation.RIGHT, [PCFIELD 1], z) = (' + value + ')']
            if suffix == 'quiet':
                conditions += ['~$integer_warning_valid(' + state + ', pintegeroperation, INTEGER_RIGHT i_left, ' + conversion + ', 1)']
                generated = 'S_generated'
            else:
                bindings += [state + '_raw = $dz_raw(' + state + ')', state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)']
                conditions += ['$integer_warning_valid(' + state + ', pintegeroperation, INTEGER_RIGHT i_left, ' + conversion + ', ' + cursor + ')',
                               state + '_raw = S_request[.STORE = ' + state + '.STORE]',
                               '$ob_object_return_error_live(' + state + '_generated, pobreturnerror)']
                generated = state + '_generated'
                if cursor == '2':
                    pending = state + '_pending'
                    bindings += [pending + ' = ' + state + '[.TODO = ' + task(conversion=conversion) + ']']
                    conditions += ['$integer_warning_valid(' + pending + ', pintegeroperation, INTEGER_RIGHT i_left, ' + conversion + ', 1)',
                                   '$ob_object_division_error_capture(' + pending + ', ' + generated + ') = eps']
            conditions += ['$ob_object_division_error_capture(' + state + ', ' + generated + ') = ' +
                           ('((pobobjectreturn, pobreturnerror))' if accepted else 'eps')]
            checks += [('current ' + suffix + ' retains its complete intrinsic RHS vector', r' /\ '.join(conditions))]
        return bindings, checks
    if name in ['precision-handlers', 'warning-handlers']:
        used = 8192 if name == 'precision-handlers' else 2
        checks = []
        for levels in [used, 8194, 8]:
            state = 'S_mask_' + str(levels)
            bindings += [state + ' = S[.ERRORHANDLER.LEVELS = ' + str(levels) + ']',
                         state + '_raw = $dz_raw(' + state + ')', state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)']
            checks += [('mask ' + str(levels) + ' refuses the opposite-handler single-notice contour',
                (genuine + r' /\ ' + CAPTURE + r' /\ ' if not checks else '') +
                '$call_current_valid(' + state + r') /\ ' +
                '$integer_warning_valid(' + state + r', pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 1) /\ ' +
                state + '_raw = S_request[.ERRORHANDLER = ' + state + r'.ERRORHANDLER] /\ ' +
                '$ob_object_return_error_live(' + state + r'_generated, pobreturnerror) /\ ' +
                '$ob_object_division_error_capture(' + state + ', ' + state + '_generated) = eps')]
        return bindings, checks
    if name == 'carrier':
        bindings += [
            'pvalue_request_right = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0.5"))',
            '$integer_conversion(pvalue_request_right) = (pintegerconversion_request)',
            'S_carrier = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("0.5")]][.STORE = $set_cell(S.STORE, n_cell_right, DEFINED pvalue_request_right)][.TODO = ' + task(conversion='pintegerconversion_request') + ']',
            'S_carrier_raw = $dz_raw(S_carrier)', 'S_carrier_generated = $throwable_transition(S_carrier, S_carrier_raw)',
            'S_invalid = S_carrier[.STRINGDATA = S.STRINGDATA]', 'S_invalid_next = S_carrier_generated[.STRINGDATA = S.STRINGDATA]']
        return bindings, [
            ('current authenticated REQUEST RHS keeps its exact singleton snapshot',
             genuine + r' /\ ' + CAPTURE + r' /\ $call_current_valid(S_carrier) /\ '
             r'pintegerconversion_request.VALUE = 0 /\ |pintegerconversion_request.NOTICES| = 1 /\ '
             r'$ob_object_error_operand_value(S_carrier, pintegeroperation.RIGHT, [PCFIELD 1], z) = (pvalue_request_right) /\ '
             r'S_carrier_raw = S_request[.STORE = S_carrier.STORE][.STRINGDATA = S_carrier.STRINGDATA] /\ '
             r'$ob_object_return_error_live(S_carrier_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_carrier, S_carrier_generated) = ((pobobjectreturn, pobreturnerror))'),
            ('missing REQUEST identity refuses the same current snapshot and live Error',
             r'~$ob_object_string_value(S_invalid, pvalue_request_right) /\ '
             r'$ob_object_error_operand_value(S_invalid, pintegeroperation.RIGHT, [PCFIELD 1], z) = eps /\ '
             r'$ob_object_division_error_capture(S_invalid, S_invalid_next) = eps')]
    genuine = genuine.replace('pfunction.CVS = eps', 'pfunction.CVS = [$ptascii("unused")]').replace('|S.ENV| = 0', '|S.ENV| = 1')
    bindings += ['$lookup(S.ENV, $ptascii("unused")) = (n_unused)', 'S.STORE[n_unused] = DEFINED (PINT 0)']
    return bindings, [('a genuine unused cell preserves the CONST-pair empty-CV refusal',
        genuine + r' /\ (HCELL n_unused) <- S.ALLOCATIONS /\ '
        r'$heap_count(HCELL n_unused, $machine_roots(S_generated)) = 1 /\ '
        r'$ob_object_division_error_capture(S, S_generated) = eps')]


if __name__ == '__main__':
    # The serial SL508 driver retains the fixed 300-second cap and source0 credit.
    harness.CASES, harness.PREFIX, harness.authority = CASES, author.PREFIX, authority
    harness.main()
