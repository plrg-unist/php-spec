#!/usr/bin/env python3
"""Two real mixed-severity callbacks return before native FINAL MOD failure."""
import re
import output_final_selected_both_warning_modulo_error_state as both
import output_final_selected_mixed_modulo_error_sources as sources

prior, runner = both.prior, both.runner
PREFIX = both.PREFIX.replace('NOTICES = [(2, ptbytes)]', 'NOTICES = [(z_level, ptbytes)]')
CASES = {name: sources.CASES['native-selected-mixed-modulo-error-' + name]
         for name in ['warning-deprecated-constant-float', 'deprecated-warning-cv-pair-string']}
WARNING = b'A non-numeric value encountered'


def shape(name):
    order, rest = ('warning-deprecated', name.removeprefix('warning-deprecated-')) if name.startswith(
        'warning-deprecated-') else ('deprecated-warning', name.removeprefix('deprecated-warning-'))
    form, kind = rest.rsplit('-', 1)
    return order, form, kind


def message(kind, side):
    number = b'1.5' if side == 'left' else b'0.5'
    value = b'float-string "' + number + b'"' if kind == 'string' else b'float ' + number
    return prior.value(b'Implicit conversion from ' + value + b' to int loses precision')


def converted(condition, name):
    order, _, kind = shape(name)
    side = 'right' if order == 'warning-deprecated' else 'left'
    digit, bits = ('0', 4602678819172646912) if side == 'right' else ('1', 4609434218613702656)
    conversion = 'pintegerconversion' + ('_left' if side == 'left' else '')
    old_messages = ['($ptascii("A non-numeric value encountered"))',
                    '$ptascii("A non-numeric value encountered")', prior.value(WARNING)]
    for old in old_messages:
        condition = condition.replace(conversion + '.NOTICES = [(2, ' + old + ')]',
                                      conversion + '.NOTICES = [(8192, ' + message(kind, side) + ')]')
    old_text = '$ptascii("' + digit + 'x")'
    numeric = r'\$string_long\(\$ptascii\("' + digit + r'x"\)\) = STRINT (\w+) \(LEADINGNUMBER :: eps\)'
    condition = re.sub(numeric, lambda match: (
        '$string_long($ptascii("' + digit + '.5")) = STRINT ' + match.group(1) + ' (STRINGPRECISIONLOSS :: eps)'
        if kind == 'string' else '$float_long(' + str(bits) + ', true) = (' + match.group(1) + ', [PRECISIONLOSS])'), condition)
    if kind == 'string':
        condition = condition.replace(old_text, '$ptascii("' + digit + '.5")')
    else:
        condition = condition.replace('PSTRING_CARRIER INTERNED_STRING (' + old_text + ')', 'PFLOAT ' + str(bits))
        condition = condition.replace('PSTRING (' + old_text + ')', 'PFLOAT ' + str(bits))
        condition = r' /\ '.join(part for part in condition.split(r' /\ ')
                                if part != '$ob_object_string_value(S, pvalue_' + side + ')')
    suffix = '_right' if side == 'right' else ''
    condition = condition.replace('perrorcall' + suffix + '.LEVEL = 2', 'perrorcall' + suffix + '.LEVEL = 8192')
    condition = condition.replace('S_return' + suffix + '.STORE[n_cell_level' + suffix + '] = DEFINED (PINT 2)',
                                  'S_return' + suffix + '.STORE[n_cell_level' + suffix + '] = DEFINED (PINT 8192)')
    for old in old_messages:
        condition = condition.replace('perrorcall' + suffix + '.MESSAGE = ' + old,
                                      'perrorcall' + suffix + '.MESSAGE = ' + message(kind, side))
        condition = condition.replace('$string_bytes(pvalue_message' + suffix + ') = (' + old + ')',
                                      '$string_bytes(pvalue_message' + suffix + ') = (' + message(kind, side) + ')')
    condition = condition.replace('~$error_handler_eligible(S, 8192)', '$error_handler_eligible(S, 8192)')
    for state in ['S', 'S_warning']:
        condition = condition.replace(state + '.ERRORHANDLER.LEVELS = 2', state + '.ERRORHANDLER.LEVELS = 8194')
    if side == 'left':
        condition = condition.replace('$error_handler_eligible(S_warning, 2)', '$error_handler_eligible(S_warning, 8192)')
    return condition.replace('selected_both_modulo_handler', 'selected_modulo_mixed')


def bindings_for(name, fixture, path):
    _, form, _ = shape(name)
    return both.bindings_for(form, fixture, path)


def original(name):
    _, form, _ = shape(name)
    return converted(both.original(form), name)


def frontier(name, fixture, path):
    _, form, _ = shape(name)
    bindings, checks = both.frontier(form, fixture, path)
    checks = [(label.replace('Warning', 'numeric notice'), converted(condition, name)) for label, condition in checks]
    checks[7] = (checks[7][0], checks[7][1] + r' /\ S.STORE = S_handler_right.STORE')
    checks[8] = ('both original mixed conversions authorize only their authentic live Error capture',
                 original(name) + r' /\ $ob_object_division_error_capture(S, S_generated) = ((pobobjectreturn, pobreturnerror))')
    checks[5] = (checks[5][0], checks[5][1] + r' /\ perrorcall.LEVEL =/= perrorcall_right.LEVEL /\ '
        r'perrorcall.MESSAGE =/= perrorcall_right.MESSAGE /\ '
        r'pintegerconversion_left.NOTICES = [(perrorcall.LEVEL, perrorcall.MESSAGE)] /\ '
        r'pintegerconversion.NOTICES = [(perrorcall_right.LEVEL, perrorcall_right.MESSAGE)]')
    return bindings, checks


def lifecycle(name, fixture, path):
    _, form, _ = shape(name)
    bindings, checks = both.lifecycle(form, fixture, path)
    checks = [(label.replace('Warning', 'numeric notice'), converted(condition, name)) for label, condition in checks]
    checks[-1] = (checks[-1][0], checks[-1][1] + r' /\ '
        r'~((HCELL n_cell_level) <- S_capture.ALLOCATIONS) /\ '
        r'~((HCELL n_cell_message) <- S_capture.ALLOCATIONS) /\ '
        r'~((HCELL n_cell_level) <- S_retired.ALLOCATIONS) /\ '
        r'~((HCELL n_cell_message) <- S_retired.ALLOCATIONS)')
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
