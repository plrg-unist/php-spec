#!/usr/bin/env python3
"""Real homogeneous callbacks finish under both eligible numeric notice levels."""
import output_final_selected_warning_modulo_error_state as right
import output_final_selected_left_warning_modulo_error_state as left
import output_final_selected_both_warning_modulo_error_state as both
import output_final_selected_left_deprecated_modulo_error_state as left_deprecated
import output_final_selected_precision_modulo_error_state as precision
import output_final_selected_both_mask_modulo_error_sources as sources

prior, runner = both.prior, both.runner
PREFIX = precision.PREFIX.replace('NOTICES = [(8192, ptbytes)]', 'NOTICES = [(z_level, ptbytes)]')
CASES = {name: sources.CASES['native-selected-both-mask-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}


def shape(name):
    level, role, form = name.split('-', 2)
    return level, role, form, 'float' if form == 'constant' else 'string'


def base_for(name):
    level, role, form, kind = shape(name)
    if level == 'warning':
        return {'left': left, 'right': right, 'both': both}[role], form
    if role == 'left':
        return left_deprecated, form + '-' + kind
    return precision, role + '-' + form + '-' + kind


def converted(condition):
    for level in [2, 8192]:
        condition = condition.replace(f'~$error_handler_eligible(S, {level})',
                                      f'$error_handler_eligible(S, {level})')
        for state in ['S', 'S_warning']:
            condition = condition.replace(f'{state}.ERRORHANDLER.LEVELS = {level}',
                                          f'{state}.ERRORHANDLER.LEVELS = 8194')
    for name in ['selected_rhs_modulo_handler', 'selected_lhs_modulo_handler',
                 'selected_both_modulo_handler', 'selected_lhs_modulo_deprecated',
                 'selected_modulo_precision']:
        condition = condition.replace(name, 'selected_modulo_both_mask')
    return condition


def phases(name, bindings):
    if shape(name)[:2] == ('warning', 'right'):
        for target, start, phase in [('S_warning', 'S_binary', 10), ('S_invoke', 'S_warning', 11),
                                      ('S_return', 'S_invoke', 12), ('S_handler', 'S_return', 13)]:
            old = prior.seek(target, start, phase)
            index = bindings.index(old[0])
            assert bindings[index:index + len(old)] == old
            bindings[index:index + len(old)] = prior.seek(target, start, phase + 8)
    return bindings


def bindings_for(name, fixture, path):
    base, key = base_for(name)
    bindings = base.bindings_for(key, fixture, path)
    return phases(name, bindings[0] if isinstance(bindings, tuple) else bindings)


def original(name):
    base, key = base_for(name)
    return converted(base.original(key))


def frontier(name, fixture, path):
    base, key = base_for(name)
    bindings, checks = base.frontier(key, fixture, path)
    checks = [(label, converted(condition)) for label, condition in checks]
    role = shape(name)[1]
    final_handler = {'left': 'S_resume', 'right': 'S_handler', 'both': 'S_handler_right'}[role]
    checks[-1] = (checks[-1][0], checks[-1][1] + r' /\ S.ERRORHANDLER.LEVELS = 8194 /\ '
        r'$error_handler_eligible(S, 2) /\ $error_handler_eligible(S, 8192) /\ '
        'S.STORE = ' + final_handler + '.STORE')
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return phases(name, bindings), checks


def lifecycle(name, fixture, path):
    base, key = base_for(name)
    bindings, checks = base.lifecycle(key, fixture, path)
    return phases(name, bindings), [(label, converted(condition)) for label, condition in checks]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
