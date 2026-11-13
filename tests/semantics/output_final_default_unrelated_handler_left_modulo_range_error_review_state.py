#!/usr/bin/env python3
"""Staged FLOAT range errors retain source, snapshot and full notice authority."""
import output_final_default_unrelated_handler_modulo_error_review_state as common
import output_final_default_unrelated_warning_handler_modulo_error_review_state as harness
import output_final_default_unrelated_handler_left_modulo_range_error_state as author
import output_final_default_unrelated_handler_left_modulo_range_error_sources as sources

ORIGINAL = sources.CASES['native-default-unrelated-handler-left-modulo-range-error-cv-pair-finite']
OWN = ORIGINAL.replace(b'$left = 1e30;', b'$left = 1e30; $other = 1e30;')
CONST = sources.CASES['native-default-unrelated-handler-left-modulo-range-error-constant-infinite']
UNUSED = CONST.replace(b'return 1e999 % 0;', b'$unused = 0; return 1e999 % 0;')
assert OWN != ORIGINAL and UNUSED != CONST
CASES = {'source': OWN, 'snapshots': OWN, 'constant': CONST, 'handlers': ORIGINAL,
         'classes': ORIGINAL, 'rhs-carrier': ORIGINAL, 'unused-cv': UNUSED}
CAPTURE = author.CAPTURE
task = common.task


def authority(name, fixture, path):
    if name in ['source', 'snapshots', 'unused-cv']:
        bindings, checks = common.authority(name, fixture, path)
        form = 'constant' if name == 'unused-cv' else 'cv-pair'
        old = common.author.original(form)
        new = author.original(form + ('-infinite' if form == 'constant' else '-finite'))
        if name == 'unused-cv':
            old = old.replace('pfunction.CVS = eps', 'pfunction.CVS = [$ptascii("unused")]').replace('|S.ENV| = 0', '|S.ENV| = 1')
            new = new.replace('pfunction.CVS = eps', 'pfunction.CVS = [$ptascii("unused")]').replace('|S.ENV| = 0', '|S.ENV| = 1')
        else:
            for source, replacement in [
                ('pfunction.CVS = [$ptascii("left"), $ptascii("right")]',
                 'pfunction.CVS = [$ptascii("left"), $ptascii("other"), $ptascii("right")]'),
                ('|S.ENV| = 2', '|S.ENV| = 3')]:
                old, new = old.replace(source, replacement), new.replace(source, replacement)
        assert sum(old in condition for _, condition in checks) == 1
        return bindings, [(label.replace('actual warning', 'actual FLOAT range Warning'), condition.replace(old, new))
                          for label, condition in checks]
    bindings, _ = author.frontier('constant-infinite' if name == 'constant' else 'cv-pair-finite', fixture, path)
    genuine = author.original('constant-infinite' if name == 'constant' else 'cv-pair-finite')
    if name == 'constant':
        negative = 'PFLOAT 18442240474082181120'
        bindings += [
            '$integer_conversion(' + negative + ') = (pintegerconversion_negative)',
            '(z_level_negative, ptbytes_notice_negative)* = pintegerconversion_negative.NOTICES',
            'pintegeroperation_negative = pintegeroperation[.LEFT = KNOWN (' + negative + ')][.LEFTPOINTER = INTEGER_COPY (' + negative + ')]',
            'S_negative = S[.TODO = ' + task('pintegeroperation_negative') + ']',
            'pintegeroperation_false = pintegeroperation[.RIGHT = KNOWN (PBOOL false)][.RIGHTPOINTER = INTEGER_COPY (PBOOL false)]',
            '$integer_conversion(PBOOL false) = (pintegerconversion_false)',
            'S_false = S[.TODO = ' + task('pintegeroperation_false', conversion='pintegerconversion_false') + ']']
        return bindings, [
            ('genuine infinite CONST operands retain the real zero-cell staged Error', genuine + r' /\ ' + CAPTURE),
            ('equal integer and sole Warning class cannot replace the actual compiled FLOAT constant',
             r'pintegerconversion_negative.VALUE = i_left /\ i_left = 0 /\ z_level_negative* = [2] /\ '
             r'$typed_tag(' + negative + r') = "float" /\ '
             r'$integer_pointer_select(S_negative, pintegeroperation_negative.LEFT) = (pintegeroperation_negative.LEFTPOINTER) /\ '
             r'$integer_slot_rank(S_negative, porigin_operator, [PCFIELD 0], pintegeroperation_negative.LEFT) = (1) /\ '
             r'~$integer_operand_source(S_negative, porigin_operator, [PCFIELD 0], pintegeroperation_negative.LEFT) /\ '
             r'$ob_object_return_error_live(S_generated, pobreturnerror) /\ '
             r'$ob_object_division_error_capture(S_negative, S_generated) = eps'),
            ('a quiet BOOL-zero snapshot cannot replace the compiled PINT-zero source',
             r'pintegerconversion_false.VALUE = 0 /\ pintegerconversion_false.NOTICES = eps /\ '
             r'~$integer_operand_source(S_false, porigin_operator, [PCFIELD 1], pintegeroperation_false.RIGHT) /\ '
             r'$ob_object_division_error_capture(S_false, S_generated) = eps')]
    if name == 'handlers':
        checks = []
        for levels, label in [(2, 'Warning'), (8194, 'both numeric'), (8, 'unrelated Notice')]:
            state = 'S_mask_' + str(levels)
            bindings += [state + ' = S[.ERRORHANDLER.LEVELS = ' + str(levels) + ']',
                         state + '_raw = $dz_raw(' + state + ')',
                         state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)']
            flags = ('$error_handler_eligible(' + state + ', 2)' if levels != 8 else
                     '~$error_handler_eligible(' + state + r', 2) /\ ~$error_handler_eligible(' + state + ', 8192)')
            checks += [('a selected ' + label + ' mask cannot use this default-Warning staged producer',
                (genuine + r' /\ ' + CAPTURE + r' /\ ' if not checks else '') +
                '$call_current_valid(' + state + r') /\ ' + flags + r' /\ ' +
                '$integer_warning_valid(' + state + r', pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, 0) /\ ' +
                state + '_raw = S_request[.ERRORHANDLER = ' + state + r'.ERRORHANDLER] /\ ' +
                '$ob_object_return_error_live(' + state + r'_generated, pobreturnerror) /\ ' +
                '$ob_object_division_error_capture(' + state + ', ' + state + '_generated) = eps')]
        return bindings, checks
    if name == 'classes':
        checks = []
        for suffix, value, levels, accepted in [
            ('infinite', 'PFLOAT 9218868437227405312', '[2]', True),
            ('negative_infinite', 'PFLOAT 18442240474082181120', '[2]', True),
            ('nan', 'PFLOAT 9221120237041090560', '[2, 8192]', False),
            ('precision', 'PFLOAT 4609434218613702656', '[8192]', False),
            ('quiet_int', 'PINT 1', 'eps', True),
            ('leading', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))', '[2]', True)]:
            state, conversion = 'S_class_' + suffix, 'pintegerconversion_class_' + suffix
            bindings += ['$integer_conversion(' + value + ') = (' + conversion + ')',
                         'i_saved_' + suffix + ' = ' + conversion + '.VALUE',
                         '(z_level_' + suffix + ', ptbytes_notice_' + suffix + ')* = ' + conversion + '.NOTICES',
                         state + ' = S[.STORE = $set_cell(S.STORE, n_cell_left, DEFINED (' + value + '))][.TODO = ' +
                         task(phase='INTEGER_RIGHT i_saved_' + suffix) + ']',
                         state + '_raw = $dz_raw(' + state + ')',
                         state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)']
            checks += [('current ' + suffix + ' retains its full intrinsic notice vector and own integer cache',
                (genuine + r' /\ ' + CAPTURE + r' /\ ' if not checks else '') +
                'z_level_' + suffix + '* = ' + levels + r' /\ ' +
                '$ob_object_error_operand_value(' + state + ', pintegeroperation.LEFT, [PCFIELD 0], z) = (' + value + r') /\ ' +
                '$integer_warning_valid(' + state + ', pintegeroperation, INTEGER_RIGHT i_saved_' + suffix + r', pintegerconversion, 0) /\ ' +
                state + '_raw = S_request[.STORE = ' + state + r'.STORE] /\ ' +
                '$ob_object_return_error_live(' + state + r'_generated, pobreturnerror) /\ ' +
                '$ob_object_division_error_capture(' + state + ', ' + state + '_generated) = ' +
                ('((pobobjectreturn, pobreturnerror))' if accepted else 'eps'))]
        return bindings, checks
    bindings += [
        'pvalue_request_right = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0"))',
        '$integer_conversion(pvalue_request_right) = (pintegerconversion_request)',
        'S_carrier = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("0")]][.STORE = $set_cell(S.STORE, n_cell_right, DEFINED pvalue_request_right)][.TODO = ' + task(conversion='pintegerconversion_request') + ']',
        'S_carrier_raw = $dz_raw(S_carrier)', 'S_carrier_generated = $throwable_transition(S_carrier, S_carrier_raw)',
        'S_invalid = S_carrier[.STRINGDATA = S.STRINGDATA]',
        'S_invalid_next = S_carrier_generated[.STRINGDATA = S.STRINGDATA]']
    return bindings, [
        ('the current authenticated REQUEST-zero RHS retains its own exact snapshot beside a FLOAT range left',
         genuine + r' /\ ' + CAPTURE + r' /\ '
         r'$call_current_valid(S_carrier) /\ pintegerconversion_request.VALUE = 0 /\ pintegerconversion_request.NOTICES = eps /\ '
         r'$ob_object_error_operand_value(S_carrier, pintegeroperation.RIGHT, [PCFIELD 1], z) = (pvalue_request_right) /\ '
         r'S_carrier_raw = S_request[.STORE = S_carrier.STORE][.STRINGDATA = S_carrier.STRINGDATA] /\ '
         r'$ob_object_return_error_live(S_carrier_generated, pobreturnerror) /\ '
         r'$ob_object_division_error_capture(S_carrier, S_carrier_generated) = ((pobobjectreturn, pobreturnerror))'),
        ('missing REQUEST identity refuses the current RHS and the same live Error',
         r'~$ob_object_string_value(S_invalid, pvalue_request_right) /\ '
         r'$ob_object_error_operand_value(S_invalid, pintegeroperation.RIGHT, [PCFIELD 1], z) = eps /\ '
         r'$ob_object_division_error_capture(S_invalid, S_invalid_next) = eps')]


if __name__ == '__main__':
    # Reuse the existing serial SL508 driver, fixed 300-second cap and raw recorder.
    harness.CASES, harness.PREFIX, harness.authority = CASES, author.PREFIX, authority
    harness.main()
