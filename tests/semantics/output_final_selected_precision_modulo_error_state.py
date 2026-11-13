#!/usr/bin/env python3
"""Real precision-loss callbacks complete before the native FINAL MOD Error."""
import re
import output_final_selected_warning_modulo_error_state as right
import output_final_selected_both_warning_modulo_error_state as both
import output_final_selected_precision_modulo_error_sources as sources

prior, runner = both.prior, both.runner
PREFIX = both.PREFIX.replace('NOTICES = [(2, ptbytes)]', 'NOTICES = [(8192, ptbytes)]')
PREFIX = PREFIX.replace('def $dp_phase(S, n) = false -- otherwise', r'''
def $dp_phase(S, 18) = true
  -- if S.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 0) :: ptask_tail*
  -- if pintegerconversion.NOTICES = [(8192, ptbytes)]
def $dp_phase(S, 19) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 1
def $dp_phase(S, 20) = true
  -- if S.TODO = (RETURN_UNWIND (KNOWN PNULL) porigin?) :: ptask_tail*
  -- if S.FRAMES = pframe_handler :: pframe :: eps
  -- if pframe_handler.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_handler*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 1
def $dp_phase(S, 21) = true
  -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT i) pintegerconversion 1
def $dp_phase(S, n) = false -- otherwise''')
CASES = {name: sources.CASES['native-selected-precision-modulo-error-' + name]
         for name in ['right-constant-float', 'both-cv-pair-string']}


def shape(name):
    role, rest = name.split('-', 1)
    form, kind = rest.rsplit('-', 1)
    return (both if role == 'both' else right), role, form, kind


def message(kind, side):
    number = b'1.5' if side == 'left' else b'0.5'
    value = b'float-string "' + number + b'"' if kind == 'string' else b'float ' + number
    return prior.value(b'Implicit conversion from ' + value + b' to int loses precision')


def converted(condition, kind, notice_side):
    old_messages = ['($ptascii("A non-numeric value encountered"))',
                    prior.value(b'A non-numeric value encountered')]
    for side, digit, bits, variable in [('left', '1', 4609434218613702656, 'pintegerconversion_left'),
                                        ('right', '0', 4602678819172646912, 'pintegerconversion')]:
        for old_message in old_messages:
            condition = condition.replace(variable + '.NOTICES = [(2, ' + old_message + ')]',
                                          variable + '.NOTICES = [(8192, ' + message(kind, side) + ')]')
        old = '$ptascii("' + digit + 'x")'
        if kind == 'string':
            condition = condition.replace(old, '$ptascii("' + digit + '.5")')
        else:
            condition = re.sub(r'\$string_long\(\$ptascii\("' + digit + r'x"\)\) = STRINT (\w+) \(LEADINGNUMBER :: eps\)',
                lambda match: f'$float_long({bits}, true) = (' + match.group(1) + ', [PRECISIONLOSS])', condition)
            condition = condition.replace('PSTRING_CARRIER INTERNED_STRING (' + old + ')', 'PFLOAT ' + str(bits))
            condition = condition.replace('PSTRING (' + old + ')', 'PFLOAT ' + str(bits))
            condition = r' /\ '.join(part for part in condition.split(r' /\ ')
                                    if part != '$ob_object_string_value(S, pvalue_' + side + ')')
    condition = condition.replace('(LEADINGNUMBER :: eps)', '(STRINGPRECISIONLOSS :: eps)')
    for old_message in old_messages:
        condition = condition.replace(old_message, message(kind, notice_side))
    condition = condition.replace('$ptascii("A non-numeric value encountered")', message(kind, notice_side))
    condition = condition.replace('[(2, ', '[(8192, ')
    condition = condition.replace(r'$error_handler_eligible(S, 2) /\ ~$error_handler_eligible(S, 8192)',
                                  r'~$error_handler_eligible(S, 2) /\ $error_handler_eligible(S, 8192)')
    for field in ['S.ERRORHANDLER.LEVELS', 'S_warning.ERRORHANDLER.LEVELS', 'perrorcall.LEVEL', 'perrorcall_right.LEVEL']:
        condition = condition.replace(field + ' = 2', field + ' = 8192')
    condition = condition.replace('$error_handler_eligible(S_warning, 2)', '$error_handler_eligible(S_warning, 8192)')
    condition = condition.replace('DEFINED (PINT 2)', 'DEFINED (PINT 8192)')
    for name in ['selected_rhs_modulo_handler', 'selected_lhs_modulo_handler', 'selected_both_modulo_handler']:
        condition = condition.replace(name, 'selected_modulo_precision')
    return condition


def bindings_for(name, fixture, path):
    base, role, form, _ = shape(name)
    bindings = base.bindings_for(form, fixture, path)
    if role == 'both':
        return bindings
    bindings, _ = bindings
    for target, start, phase in [('S_warning', 'S_binary', 10), ('S_invoke', 'S_warning', 11),
                                  ('S_return', 'S_invoke', 12), ('S_handler', 'S_return', 13)]:
        old = prior.seek(target, start, phase)
        index = bindings.index(old[0])
        assert bindings[index:index + len(old)] == old
        bindings[index:index + len(old)] = prior.seek(target, start, phase + 8)
    return bindings


def original(name):
    base, role, form, kind = shape(name)
    return converted(base.original(form), kind, 'left' if role == 'both' else 'right')


def frontier(name, fixture, path):
    base, role, form, kind = shape(name)
    bindings = bindings_for(name, fixture, path)
    stop = next(i for i, binding in enumerate(bindings) if binding.startswith('pobobjectreturn_seed = '))
    _, checks = base.frontier(form, fixture, path)
    checks = [(label.replace('Warning', 'Deprecated'), converted(condition, kind,
               'right' if role == 'right' or index in [5, 6] else 'left'))
              for index, (label, condition) in enumerate(checks)]
    if role == 'both':
        checks[5] = (checks[5][0], checks[5][1] +
            r' /\ perrorcall.MESSAGE =/= perrorcall_right.MESSAGE /\ '
            r'pintegerconversion_left.NOTICES = [(8192, perrorcall.MESSAGE)] /\ '
            r'pintegerconversion.NOTICES = [(8192, perrorcall_right.MESSAGE)]')
        checks[7] = (checks[7][0], checks[7][1] + r' /\ S.STORE = S_handler_right.STORE')
    else:
        checks[3] = (checks[3][0], checks[3][1] + r' /\ S.STORE = S_handler.STORE')
    return bindings[:stop], checks


def lifecycle(name, fixture, path):
    base, role, form, kind = shape(name)
    bindings = bindings_for(name, fixture, path)
    _, checks = base.lifecycle(form, fixture, path)
    checks = [(label.replace('Warning', 'Deprecated'), converted(condition, kind,
               'left' if role == 'both' else 'right')) for label, condition in checks]
    if role == 'right':
        checks += [('capture preserves the full actual store after real right Deprecated formal retirement',
            r'$error_handler_finish(S_handler, perrorcall_return) = S /\ S_capture.STORE = S.STORE /\ '
            r'S_capture.OUTPUTBUFFERS[0].BYTES = $ptascii("AH") /\ '
            r'~((HCELL n_cell_level) <- S_capture.ALLOCATIONS) /\ ~((HCELL n_cell_message) <- S_capture.ALLOCATIONS) /\ '
            r'$heap_count(HCELL n_cell_level, $machine_roots(S_capture)) = 0 /\ '
            r'$heap_count(HCELL n_cell_message, $machine_roots(S_capture)) = 0')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
