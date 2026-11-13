#!/usr/bin/env python3
"""A real selected precision-loss callback returns before native MOD failure."""
import output_final_selected_left_warning_modulo_error_state as left
import output_final_default_left_modulo_deprecation_error_state as precision
import output_final_selected_left_deprecated_modulo_error_sources as sources

prior, runner = left.prior, left.runner
PREFIX = left.PREFIX.replace('pintegerconversion_left.NOTICES = [(2, ptbytes)]',
                             'pintegerconversion_left.NOTICES = [(8192, ptbytes)]')
CASES = {name: sources.CASES['native-selected-left-deprecated-modulo-error-' + name]
         for name in ['constant-float', 'cv-pair-string']}


def bindings_for(name, fixture, path):
    form, _ = name.rsplit('-', 1)
    return left.bindings_for(form, fixture, path)


def converted(condition, kind):
    message = prior.value(precision.message(kind))
    condition = condition.replace('selected_lhs_modulo_handler', 'selected_lhs_modulo_deprecated')
    condition = condition.replace('($ptascii("A non-numeric value encountered"))', message)
    condition = condition.replace('$ptascii("A non-numeric value encountered")', message)
    condition = condition.replace('[(2, ', '[(8192, ')
    condition = condition.replace('$error_handler_eligible(S_warning, 2)', '$error_handler_eligible(S_warning, 8192)')
    condition = condition.replace('S_warning.ERRORHANDLER.LEVELS = 2', 'S_warning.ERRORHANDLER.LEVELS = 8192')
    condition = condition.replace('perrorcall.LEVEL = 2', 'perrorcall.LEVEL = 8192')
    condition = condition.replace('S_return.STORE[n_cell_level] = DEFINED (PINT 2)',
                                  'S_return.STORE[n_cell_level] = DEFINED (PINT 8192)')
    condition = condition.replace('$error_handler_eligible(S, 2)', '~$error_handler_eligible(S, 2)')
    condition = condition.replace('~$error_handler_eligible(S, 8192)', '$error_handler_eligible(S, 8192)')
    condition = condition.replace('S.ERRORHANDLER.LEVELS = 2', 'S.ERRORHANDLER.LEVELS = 8192')
    if kind == 'string':
        condition = condition.replace('(LEADINGNUMBER :: eps)', '(STRINGPRECISIONLOSS :: eps)')
        return condition.replace('$ptascii("1x")', '$ptascii("1.5")')
    condition = condition.replace('pvalue_left = PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))',
                                  'pvalue_left = PFLOAT 4609434218613702656')
    condition = condition.replace('$string_long($ptascii("1x")) = STRINT i_left (LEADINGNUMBER :: eps)',
                                  '$float_long(4609434218613702656, true) = (i_left, [PRECISIONLOSS])')
    condition = condition.replace('pvalue_left_compiled = PSTRING ($ptascii("1x"))',
                                  'pvalue_left_compiled = PFLOAT 4609434218613702656')
    return r' /\ '.join(part for part in condition.split(r' /\ ')
                        if part != '$ob_object_string_value(S, pvalue_left)')


def original(name):
    form, kind = name.rsplit('-', 1)
    return converted(left.original(form), kind)


def frontier(name, fixture, path):
    form, kind = name.rsplit('-', 1)
    bindings, checks = left.frontier(form, fixture, path)
    checks = [(label.replace('Warning', 'Deprecated'), converted(condition, kind))
              for label, condition in checks]
    return bindings, checks


def lifecycle(name, fixture, path):
    form, _ = name.rsplit('-', 1)
    bindings = bindings_for(name, fixture, path)
    _, checks = left.lifecycle(form, fixture, path)
    before = left.original(form)
    assert checks[0][1].count(before) == 1
    checks[0] = ('completed selected Deprecated captures only the authentic nonowning Error source',
                 checks[0][1].replace(before, original(name)))
    checks += [('capture preserves the full actual store after real Deprecated formal retirement',
        r'$error_handler_finish(S_handler, perrorcall_return) = S_resume /\ '
        r'S_capture.STORE = S.STORE /\ '
        r'S_resume.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion_left 1) :: ptask_tail* /\ '
        r'S_capture.OUTPUTBUFFERS[0].BYTES = $ptascii("AH") /\ '
        r'~((HCELL n_cell_level) <- S_capture.ALLOCATIONS) /\ '
        r'~((HCELL n_cell_message) <- S_capture.ALLOCATIONS) /\ '
        r'$heap_count(HCELL n_cell_level, $machine_roots(S_capture)) = 0 /\ '
        r'$heap_count(HCELL n_cell_message, $machine_roots(S_capture)) = 0')]
    return bindings, checks


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
