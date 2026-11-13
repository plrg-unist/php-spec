#!/usr/bin/env python3
"""Two same-class MOD notices retain full conversions and one-cell identity."""
import output_final_default_unrelated_handler_right_modulo_conversion_error_review_state as previous
import output_final_default_unrelated_handler_both_modulo_conversion_error_state as author
import output_final_default_unrelated_handler_both_modulo_conversion_error_sources as sources

PREFIX = 'native-default-unrelated-handler-both-modulo-conversion-error-'
PAIR = sources.CASES[PREFIX + 'cv-pair-string']
OWN = PAIR.replace(b"$left = '1.5';", b"$left = '1.5'; $other = '1.5';")
CONST = sources.CASES[PREFIX + 'constant-leading']
UNUSED = CONST.replace(b"return '1x' % '0x';", b"$unused = 0; return '1x' % '0x';")
RANGE = sources.CASES[PREFIX + 'cv-pair-finite']
SAME = sources.CASES[PREFIX + 'same-cv-infinite']
assert OWN != PAIR and UNUSED != CONST
CASES = {'source': OWN, 'snapshots': OWN, 'constant': CONST, 'precision-classes': PAIR,
         'warning-classes': RANGE, 'precision-handlers': PAIR, 'warning-handlers': RANGE,
         'carrier': PAIR, 'unused-cv': UNUSED, 'left-vectors': PAIR, 'same-cv': SAME}
CAPTURE = author.CAPTURE
task = previous.task

# Reuse the existing guard campaign with genuine two-notice source fronts.
previous.author = author


def authority(name, fixture, path):
    if name not in ['left-vectors', 'same-cv']:
        bindings, checks = previous.authority(name, fixture, path)
        return bindings, [(label.replace('fresh quiet reconversion', 'fresh left reconversion').replace(
            'opposite-handler single-notice contour', 'same-class two-notice contour'), condition)
            for label, condition in checks]
    selected = 'same-cv-infinite' if name == 'same-cv' else 'cv-pair-string'
    bindings, _ = author.frontier(selected, fixture, path)
    genuine = author.original(selected)
    if name == 'left-vectors':
        checks = []
        for suffix, value, saved, levels, accepted in [
            ('quiet', 'PINT 1', 1, 'eps', True),
            ('leading', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))', 1, '[2]', False),
            ('nan', 'PFLOAT 9221120237041090560', 0, '[2, 8192]', False)]:
            state, conversion = 'S_left_' + suffix, 'pintegerconversion_left_' + suffix
            bindings += ['$integer_conversion(' + value + ') = (' + conversion + ')',
                         'i_saved_' + suffix + ' = ' + conversion + '.VALUE',
                         '(z_level_' + suffix + ', ptbytes_notice_' + suffix + ')* = ' + conversion + '.NOTICES',
                         state + ' = S[.STORE = $set_cell(S.STORE, n_cell_left, DEFINED (' + value + '))][.TODO = ' +
                         task(phase='INTEGER_RIGHT i_saved_' + suffix) + ']',
                         state + '_raw = $dz_raw(' + state + ')',
                         state + '_generated = $throwable_transition(' + state + ', ' + state + '_raw)']
            conditions = ([genuine, CAPTURE] if not checks else []) + [
                conversion + '.VALUE = ' + str(saved), 'z_level_' + suffix + '* = ' + levels,
                '$ob_object_error_operand_value(' + state + ', pintegeroperation.LEFT, [PCFIELD 0], z) = (' + value + ')',
                '$integer_warning_valid(' + state + ', pintegeroperation, INTEGER_RIGHT i_saved_' + suffix + ', pintegerconversion, 1)',
                state + '_raw = S_request[.STORE = ' + state + '.STORE]',
                '$ob_object_return_error_live(' + state + '_generated, pobreturnerror)',
                '$ob_object_division_error_capture(' + state + ', ' + state + '_generated) = ' +
                    ('((pobobjectreturn, pobreturnerror))' if accepted else 'eps')]
            label = ('a freshly quiet left retains the literal OB95 cursor-one producer' if suffix == 'quiet' else
                     'a mixed left Warning cannot join a precision RHS' if suffix == 'leading' else
                     'the full two-notice left vector cannot masquerade as one matching Deprecated')
            checks += [(label, r' /\ '.join(conditions))]
        bindings += ['$integer_conversion(PINT 0) = (pintegerconversion_quiet_right)',
                     'S_right_quiet = S[.STORE = $set_cell(S.STORE, n_cell_right, DEFINED (PINT 0))][.TODO = ' +
                     task(conversion='pintegerconversion_quiet_right', cursor='0') + ']',
                     'S_right_quiet_raw = $dz_raw(S_right_quiet)',
                     'S_right_quiet_generated = $throwable_transition(S_right_quiet, S_right_quiet_raw)']
        checks += [('a quiet RHS retains the earlier precision-left cursor-zero producer', r' /\ '.join([
            'pintegerconversion_quiet_right.VALUE = 0', 'pintegerconversion_quiet_right.NOTICES = eps',
            '$integer_warning_valid(S_right_quiet, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion_quiet_right, 0)',
            'S_right_quiet_raw = S_request[.STORE = S_right_quiet.STORE]',
            '$ob_object_return_error_live(S_right_quiet_generated, pobreturnerror)',
            '$ob_object_division_error_capture(S_right_quiet, S_right_quiet_generated) = ((pobobjectreturn, pobreturnerror))']))]
        return bindings, checks
    bindings += ['S_saved = S[.TODO = ' + task(phase='INTEGER_RIGHT 1') + ']',
                 'S_saved_raw = $dz_raw(S_saved)', 'S_saved_generated = $throwable_transition(S_saved, S_saved_raw)',
                 'S_reference = S[.REFCELLS = S.REFCELLS ++ [n_cell_left]]']
    return bindings, [
        ('the two source reads and two INF notices borrow one actual private cell', r' /\ '.join([
            genuine, CAPTURE, 'n_cell_left = n_cell_right',
            'pintegeroperation.LEFTPOINTER = pintegeroperation.RIGHTPOINTER',
            '$operand_nodes(pintegeroperation.LEFT) = eps', '$operand_nodes(pintegeroperation.RIGHT) = eps',
            '$heap_count(HCELL n_cell_left, $machine_roots(S)) = 1',
            '$heap_owners($heap_graph(S), HCELL n_cell_left) = 1'])),
        ('a forged shared-cell cache still produces the same Error but cannot replace the saved zero', r' /\ '.join([
            '$integer_warning_valid(S_saved, pintegeroperation, INTEGER_RIGHT 1, pintegerconversion, 1)',
            'pintegerconversion_left.VALUE = 0', 'S_saved_raw = S_request', 'S_saved_generated = S_generated',
            '$ob_object_division_error_capture(S_saved, S_saved_generated) = eps'])),
        ('reference marking the shared cell changes canonical left selection and refuses both private reads', r' /\ '.join([
            '$integer_pointer_select(S_reference, pintegeroperation.LEFT) = (INTEGER_CELL n_cell_left)',
            '$integer_pointer_value(S_reference, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
            '$ob_object_error_operand_value(S_reference, pintegeroperation.LEFT, [PCFIELD 0], z) = eps',
            '$ob_object_error_operand_value(S_reference, pintegeroperation.RIGHT, [PCFIELD 1], z) = eps',
            '$ob_object_division_error_capture(S_reference, S_generated) = eps']))]


if __name__ == '__main__':
    # The reused serial SL508 driver preserves cap300, raw records and source0.
    harness = previous.harness
    harness.CASES, harness.PREFIX, harness.authority = CASES, author.PREFIX, authority
    harness.main()
