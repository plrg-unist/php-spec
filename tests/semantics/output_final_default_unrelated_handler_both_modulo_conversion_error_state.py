#!/usr/bin/env python3
"""Two completed same-class notices preserve the actual FINAL MOD cleanup."""
import output_final_default_unrelated_handler_right_modulo_conversion_error_state as previous
import output_final_default_unrelated_handler_both_modulo_conversion_error_sources as sources

prior, shared = previous.prior, previous.shared
PREFIX, CAPTURE = previous.PREFIX, previous.CAPTURE
CASES = {name: sources.CASES['native-default-unrelated-handler-both-modulo-conversion-error-' + name]
         for name in ['constant-leading', 'left-cv-string', 'right-cv-float', 'cv-pair-finite', 'same-cv-infinite']}
LEFT = {
    'leading': ('PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))', 1,
                b'A non-numeric value encountered'),
    'string': ('PSTRING_CARRIER INTERNED_STRING ($ptascii("1.5"))', 1,
               b'Implicit conversion from float-string "1.5" to int loses precision'),
    'float': ('PFLOAT 4609434218613702656', 1,
              b'Implicit conversion from float 1.5 to int loses precision'),
    'finite': ('PFLOAT 5055640609639927018', 5076964154930102272,
               b'The float 1.0E+30 is not representable as an int, cast occurred'),
    'infinite': ('PFLOAT 9218868437227405312', 0,
                 b'The float INF is not representable as an int, cast occurred')}


def shape(name):
    form, kind = name.rsplit('-', 1)
    cells = ['left', 'right'] if form == 'same-cv' else previous.shape(name)[3]
    return form, kind, 7 if form == 'same-cv' else 6 + len(cells), cells


def bindings_for(name, fixture, path):
    return previous.bindings_for(name.replace('same-cv-', 'cv-pair-'), fixture, path)


def original(name):
    form, kind, line, cells = shape(name)
    right, level, right_message, conversion = previous.VALUES[kind]
    left, cache, left_message = LEFT[kind]
    if form == 'same-cv':
        left, cache, left_message = right, 0, right_message
    handler = 8192 if level == 2 else 2
    diagnostic = 'Warning' if level == 2 else 'Deprecated'
    cv_names = ['value'] if form == 'same-cv' else cells
    cvs = '[' + ', '.join('$ptascii("' + side + '")' for side in cv_names) + ']' if cv_names else 'eps'
    conditions = [f'z = {line}', 'n = 1', f'i_left = {cache}',
        f'pfunction.CVS = {cvs}', 'S.CVS = pfunction.CVS', f'|S.ENV| = {len(cv_names)}',
        'pvalue_left = ' + left, 'pvalue_right = ' + right, conversion,
        'pintegeroperation.OP = MODULO', 'pintegeroperation.SWAPPED = false',
        'pintegeroperation.SITE = porigin_operator', 'pintegeroperation.RIGHT = S_binary.RESULT',
        '$integer_operation_valid(S, pintegeroperation)',
        '$integer_warning_valid(S, pintegeroperation, INTEGER_RIGHT i_left, pintegerconversion, n)',
        '$integer_conversion(pvalue_left) = (pintegerconversion_left)',
        'pintegerconversion_left.INPUT = pvalue_left', 'pintegerconversion_left.VALUE = i_left',
        'pintegerconversion_left.NOTICES = [(' + str(level) + ', ' + prior.value(left_message) + ')]',
        '$integer_conversion(pvalue_right) = (pintegerconversion)',
        'pintegerconversion.INPUT = pvalue_right', 'pintegerconversion.VALUE = 0',
        'pintegerconversion.NOTICES = [(' + str(level) + ', ' + prior.value(right_message) + ')]',
        '$ob_object_modulo_integer(pvalue_left) = eps', '$ob_object_modulo_integer(pvalue_right) = eps',
        f'~$error_handler_eligible(S, {level})', f'$error_handler_eligible(S, {handler})',
        f'S.ERRORHANDLER.LEVELS = {handler}', 'S.ERRORHANDLER.CALLBACK =/= eps',
        'S.ERRORHANDLERS = [{CALLBACK eps, LEVELS 0}]',
        'S_binary.EVENTS = [OUTPUT ([80])]',
        'S.EVENTS = [OUTPUT ([80]), DIAGNOSTIC "' + diagnostic + '" ' + prior.value(left_message) + f' {line}, ' +
            'DIAGNOSTIC "' + diagnostic + '" ' + prior.value(right_message) + f' {line}]',
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
            cv = 'value' if form == 'same-cv' else side
            conditions += [f'n_{side}* = $ptascii("{cv}")', f'z_{side} = {line}',
                f'{operand} = VARIABLE n_{side}* z_{side}', f'{pointer} = INTEGER_CV n_{side}*',
                f'$compiled_read(S, porigin_{side}) = eps',
                f'(HCELL n_cell_{side}) <- S.ALLOCATIONS', f'~(n_cell_{side} <- S.REFCELLS)',
                f'$heap_count(HCELL n_cell_{side}, $machine_roots(S)) = 1',
                f'$heap_owners($heap_graph(S), HCELL n_cell_{side}) = 1']
        else:
            conditions += [f'{operand} = KNOWN pvalue_{side}', f'{pointer} = INTEGER_COPY pvalue_{side}']
            if kind in ['leading', 'string']:
                text = {'leading': ('1x', '0x'), 'string': ('1.5', '0.5')}[kind][side == 'right']
                conditions += [f'pvalue_{side}_compiled = PSTRING ($ptascii("{text}"))',
                    f'$compiled_read(S, porigin_{side}) = (pvalue_{side}_compiled)',
                    f'pvalue_{side} = $compiled_string_value(S, porigin_{side}, pvalue_{side}_compiled)']
            else:
                conditions += [f'$compiled_read(S, porigin_{side}) = (pvalue_{side})']
        if kind in ['leading', 'string']:
            conditions += [f'$ob_object_string_value(S, pvalue_{side})']
    if len(cells) == 2:
        conditions += ['n_cell_left ' + ('=' if form == 'same-cv' else '=/=') + ' n_cell_right']
    return r' /\ '.join(conditions)


def frontier(name, fixture, path):
    bindings, _ = bindings_for(name, fixture, path)
    stop = next(i for i, binding in enumerate(bindings) if binding.startswith('pobobjectreturn_seed = '))
    return bindings[:stop], [('genuine two-notice completion retains current operands, snapshots and exact live Error',
                              original(name) + r' /\ $ob_object_division_error_capture(S, S_generated) = eps')]


def lifecycle(name, fixture, path):
    form, _, line, cells = shape(name)
    bindings, checks = bindings_for(name, fixture, path)
    stored = ''.join(f'S_capture.STORE[n_cell_{side}] = DEFINED pvalue_{side} /\\ ' for side in cells)
    checks[0] = ('actual same-class two-notice completion captures source and exact driver closure',
        original(name) + r' /\ ' + CAPTURE + r' /\ $source_exception_transition(S, S_generated) = S_seed /\ ' +
        shared.seed_identity() + r' /\ ' + shared.post_identity() + r' /\ S_capture_found = $drive_steps(S_seed_post, 0) /\ ' +
        stored + r'$output_final_cv_unwind(S_capture) /\ S_zero = S_capture[.COMPLETION = BUDGET] /\ ' + prior.public('S_capture'))
    if form == 'same-cv':
        checks[1] = (checks[1][0], checks[1][1].replace('[HCELL n_cell_left, HCELL n_cell_right]', '[HCELL n_cell_left]').replace(
            '[DESTRUCTION_VALUE (HCELL n_cell_left), DESTRUCTION_VALUE (HCELL n_cell_right)]', '[DESTRUCTION_VALUE (HCELL n_cell_left)]'))
        def fatal(number):
            return (b'Fatal error: Uncaught DivisionByZeroError: Modulo by zero in ' + bytes(path) + b':' + str(number).encode() +
                    b'\nStack trace:\n#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + bytes(path) +
                    b' on line ' + str(number).encode() + b'\n')
        checks[2] = (checks[2][0], checks[2][1].replace(prior.value(fatal(8)), prior.value(fatal(line))).replace(' 8 /\\ ', f' {line} /\\ '))
    checks[2] = ('C0 preserves both ordered intrinsic notices and no handler output after retirement', checks[2][1])
    return bindings, checks


if __name__ == '__main__':
    # Reuse the serial SL508 driver, fixed 300-second cap and raw recorder.
    previous.previous.CASES, previous.previous.PREFIX = CASES, PREFIX
    previous.previous.frontier, previous.previous.lifecycle = frontier, lifecycle
    previous.previous.main()
