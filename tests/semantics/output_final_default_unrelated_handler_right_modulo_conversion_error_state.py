#!/usr/bin/env python3
"""A completed single RHS notice retains its exact snapshot and FINAL cleanup."""
import output_final_default_unrelated_handler_modulo_error_state as previous
import output_final_default_unrelated_handler_right_modulo_conversion_error_sources as sources

prior, shared = previous.prior, previous.shared
PREFIX, CAPTURE = previous.PREFIX, previous.CAPTURE
CASES = {name: sources.CASES['native-default-unrelated-handler-right-modulo-conversion-error-' + name]
         for name in ['constant-leading', 'left-cv-string', 'right-cv-float', 'cv-pair-finite']}
VALUES = {
    'leading': ('PSTRING_CARRIER INTERNED_STRING ($ptascii("0x"))', 2,
                b'A non-numeric value encountered', '$string_long($ptascii("0x")) = STRINT 0 [LEADINGNUMBER]'),
    'string': ('PSTRING_CARRIER INTERNED_STRING ($ptascii("0.5"))', 8192,
               b'Implicit conversion from float-string "0.5" to int loses precision',
               '$string_long($ptascii("0.5")) = STRINT 0 [STRINGPRECISIONLOSS]'),
    'float': ('PFLOAT 4602678819172646912', 8192,
              b'Implicit conversion from float 0.5 to int loses precision',
              '$float_long(4602678819172646912, true) = (0, [PRECISIONLOSS])'),
    'finite': ('PFLOAT 4895412794951729152', 2,
               b'The float 1.8446744073709552E+19 is not representable as an int, cast occurred',
               '$float_long(4895412794951729152, true) = (0, [RANGEWARNING])'),
    'infinite': ('PFLOAT 9218868437227405312', 2,
                 b'The float INF is not representable as an int, cast occurred',
                 '$float_long(9218868437227405312, true) = (0, [RANGEWARNING])')}


def shape(name):
    form, kind = name.rsplit('-', 1)
    cells = [side for side in ['left', 'right'] if form == side + '-cv' or form == 'cv-pair']
    return form, kind, 6 + len(cells), cells


def bindings_for(name, fixture, path):
    form, _, _, _ = shape(name)
    bindings, checks = previous.bindings_for(form, fixture, path)
    if form == 'constant':
        assert bindings.count('S_binary.RESULT = KNOWN (PINT 0)') == 1
        assert bindings.count('pvalue_right = PINT 0') == 1
        bindings = [binding.replace('S_binary.RESULT = KNOWN (PINT 0)',
                                    'S_binary.RESULT = KNOWN pvalue_right')
                    for binding in bindings if binding != 'pvalue_right = PINT 0']
        bindings.insert(bindings.index('$integer_operator_plan(S_binary) = (pintegeroperation)'),
                        '$compiled_read(S_binary, porigin_right) = (pvalue_right_compiled)')
    return bindings, checks


def original(name):
    _, kind, line, cells = shape(name)
    right, level, message, conversion = VALUES[kind]
    handler = 8192 if level == 2 else 2
    diagnostic = 'Warning' if level == 2 else 'Deprecated'
    cvs = '[' + ', '.join('$ptascii("' + side + '")' for side in cells) + ']' if cells else 'eps'
    conditions = [f'z = {line}', 'n = 1', 'i_left = 1',
        f'pfunction.CVS = {cvs}', 'S.CVS = pfunction.CVS', f'|S.ENV| = {len(cells)}',
        'pvalue_left = PINT 1', 'pvalue_right = ' + right, conversion,
        'pintegeroperation.OP = MODULO', 'pintegeroperation.SWAPPED = false',
        'pintegeroperation.SITE = porigin_operator', 'pintegeroperation.RIGHT = S_binary.RESULT',
        '$integer_operation_valid(S, pintegeroperation)',
        '$integer_warning_valid(S, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, n)',
        '$integer_conversion(pvalue_left) = (pintegerconversion_left)',
        'pintegerconversion_left.INPUT = pvalue_left', 'pintegerconversion_left.VALUE = i_left',
        'pintegerconversion_left.NOTICES = eps',
        '$integer_conversion(pvalue_right) = (pintegerconversion)',
        'pintegerconversion.INPUT = pvalue_right', 'pintegerconversion.VALUE = 0',
        'pintegerconversion.NOTICES = [(' + str(level) + ', ' + prior.value(message) + ')]',
        '$ob_object_modulo_integer(pvalue_left) = (1)', '$ob_object_modulo_integer(pvalue_right) = eps',
        f'~$error_handler_eligible(S, {level})', f'$error_handler_eligible(S, {handler})',
        f'S.ERRORHANDLER.LEVELS = {handler}', 'S.ERRORHANDLER.CALLBACK =/= eps',
        'S.ERRORHANDLERS = [{CALLBACK eps, LEVELS 0}]',
        'S_binary.EVENTS = [OUTPUT ([80])]',
        'S.EVENTS = [OUTPUT ([80]), DIAGNOSTIC "' + diagnostic + '" ' + prior.value(message) + f' {line}]',
        'S.STORE = S_binary.STORE', 'S.RESULT = KNOWN PNULL',
        'S.ERRORHANDLER = S_binary.ERRORHANDLER', 'S.ERRORHANDLERS = S_binary.ERRORHANDLERS',
        '$value_nodes(pvalue_left) = eps', '$value_nodes(pvalue_right) = eps',
        'S.HELD = eps', '$tasks_nodes(S.TODO) = eps', 'S.RETIREDOWNERS = eps', '$base_nodes(S.BASE) = eps',
        '$call_current_valid(S)', '$ob_object_final_native_method(S) = (pobobjectreturn)',
        '$integer_standard_object_handlers(S, POBJECT pobobjectreturn.OBJECT)',
        '$ob_object_division_operator(S, porigin_operator) = (MODULO)',
        'S_request = $integer_converted(S, pintegeroperation, INTEGER_RIGHT i_left, 0)',
        f'S_request.COMPLETION = THROWN "DivisionByZeroError" ($ptascii("Modulo by zero")) {line}',
        'S_request.TODO = ptask_tail*', 'S_request.RESULT = KNOWN PNULL',
        'S_request.EVENTS = S.EVENTS', 'S_request.STORE = S.STORE',
        'S_request.ERRORHANDLER = S.ERRORHANDLER', 'S_request.ERRORHANDLERS = S.ERRORHANDLERS',
        '$ob_object_division_error_source(S_generated, pfunction, pobreturnerror)',
        '$ob_object_return_error_live(S_generated, pobreturnerror)']
    for side in ['left', 'right']:
        operand = 'pintegeroperation.' + side.upper()
        pointer = operand + 'POINTER'
        conditions += [f'$integer_pointer_select(S, {operand}) = ({pointer})',
            f'$integer_pointer_value(S_binary, {pointer}) = (pvalue_{side})',
            f'$integer_pointer_value(S, {pointer}) = (pvalue_{side})',
            f'$ob_object_error_operand_value(S, {operand}, [PCFIELD {0 if side == "left" else 1}], z) = (pvalue_{side})',
            f'$integer_slot_rank(S, porigin_operator, [PCFIELD {0 if side == "left" else 1}], {operand}) = ({8 if side in cells else 1})',
            f'$code_expression_at_source(S, porigin_operator, [PCFIELD {0 if side == "left" else 1}]) = ({line})']
        if side in cells:
            conditions += [f'n_{side}* = $ptascii("{side}")', f'z_{side} = {line}',
                f'{operand} = VARIABLE n_{side}* z_{side}', f'{pointer} = INTEGER_CV n_{side}*',
                f'$compiled_read(S, porigin_{side}) = eps',
                f'(HCELL n_cell_{side}) <- S.ALLOCATIONS', f'~(n_cell_{side} <- S.REFCELLS)',
                f'$heap_count(HCELL n_cell_{side}, $machine_roots(S)) = 1',
                f'$heap_owners($heap_graph(S), HCELL n_cell_{side}) = 1']
        else:
            conditions += [f'{operand} = KNOWN pvalue_{side}', f'{pointer} = INTEGER_COPY pvalue_{side}']
            if side == 'right' and kind in ['leading', 'string']:
                text = '0x' if kind == 'leading' else '0.5'
                conditions += [f'pvalue_right_compiled = PSTRING ($ptascii("{text}"))',
                    '$compiled_read(S, porigin_right) = (pvalue_right_compiled)',
                    'pvalue_right = $compiled_string_value(S, porigin_right, pvalue_right_compiled)']
            else:
                conditions += [f'$compiled_read(S, porigin_{side}) = (pvalue_{side})']
    if len(cells) == 2:
        conditions += ['n_cell_left =/= n_cell_right']
    if kind in ['leading', 'string']:
        conditions += ['$ob_object_string_value(S, pvalue_right)']
    return r' /\ '.join(conditions)


def frontier(name, fixture, path):
    bindings, _ = bindings_for(name, fixture, path)
    stop = next(i for i, binding in enumerate(bindings) if binding.startswith('pobobjectreturn_seed = '))
    return bindings[:stop], [('genuine completed RHS single notice retains current operands and exact live Error',
                              original(name) + r' /\ $ob_object_division_error_capture(S, S_generated) = eps')]


def lifecycle(name, fixture, path):
    _, _, _, cells = shape(name)
    bindings, checks = bindings_for(name, fixture, path)
    stored = ''.join(f'S_capture.STORE[n_cell_{side}] = DEFINED pvalue_{side} /\\ ' for side in cells)
    checks[0] = ('actual RHS single-notice completion captures only source and exact driver closure',
        original(name) + r' /\ ' + CAPTURE + r' /\ $source_exception_transition(S, S_generated) = S_seed /\ ' +
        shared.seed_identity() + r' /\ ' + shared.post_identity() + r' /\ S_capture_found = $drive_steps(S_seed_post, 0) /\ ' +
        stored + r'$output_final_cv_unwind(S_capture) /\ S_zero = S_capture[.COMPLETION = BUDGET] /\ ' + prior.public('S_capture'))
    checks[2] = ('C0 preserves the actual sole RHS diagnostic and no handler output after retirement', checks[2][1])
    return bindings, checks


if __name__ == '__main__':
    # Reuse the serial SL508 driver, fixed 300-second cap and raw recorder.
    previous.CASES, previous.PREFIX = CASES, PREFIX
    previous.frontier, previous.lifecycle = frontier, lifecycle
    previous.main()
