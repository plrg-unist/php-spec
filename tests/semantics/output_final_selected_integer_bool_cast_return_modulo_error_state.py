#!/usr/bin/env python3
"""Own emitted integer-to-Boolean casts retain strict default-diagnostic choice."""
import output_final_selected_integer_cast_return_modulo_error_state as integers
import output_final_selected_true_return_modulo_error_state as yes
import output_final_selected_false_return_modulo_error_state as no
import output_final_selected_integer_bool_cast_return_modulo_error_sources as sources

prior, runner = integers.prior, integers.runner
PREFIX = integers.PREFIX.replace('(PINT i_return)', '(PBOOL b_return)')
CASES = {name: sources.CASES['native-selected-integer-bool-cast-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}
VALUES = {'warning-left-constant': 0, 'deprecated-both-cv-pair': 0,
          'warning-right-cv-pair': 7, 'warning-deprecated-constant-float': 9223372036854775807}


def converted(name, condition):
    if VALUES[name] == 0:
        return no.converted(name, condition).replace('selected_modulo_false_return',
            'selected_modulo_integer_bool_cast_return')
    return yes.converted(condition).replace('selected_modulo_true_return',
        'selected_modulo_integer_bool_cast_return')


def boolean(condition):
    return condition.replace('NExprCastInt', 'NExprCastBool').replace(
        'CASTINT', 'CASTBOOL').replace('(PINT i_return)', '(PBOOL b_return)')


def return_bindings(name):
    bindings = [boolean(binding) for binding in integers.return_bindings(name)]
    if VALUES[name] == 0:
        bindings += ['S_default = $error_default(S_handler, perrorcall_return.EVENT, perrorcall_return.LEVEL)']
        if prior.two_calls(name):
            bindings += ['S_default_right = $error_default(S_handler_right, perrorcall_return_right.EVENT, perrorcall_return_right.LEVEL)']
    return bindings


def return_proof(name):
    condition = boolean(integers.return_proof(name))
    for before, after in [('$long_range(i_return) /\\ ', ''),
                          ('i_child = ' + str(integers.VALUES[name]), 'i_child = ' + str(VALUES[name])),
                          ('i_return = ' + str(integers.RETURN_VALUES[name]),
                           'b_return = ' + str(VALUES[name] != 0).lower())]:
        assert condition.count(before) == 1
        condition = condition.replace(before, after)
    condition += r' /\ $plstyle(metadata_cast) = 1'
    assert 'i_return' not in condition
    if VALUES[name] == 0:
        guard = r'S_handler.RESULT =/= KNOWN (PBOOL false) /\ '
        assert condition.count(guard) == 1
        condition = condition.replace(guard, '')
        resumed = 'S' if name == 'warning-right-cv-pair' else 'S_resume'
        events = no.diagnostics(name)
        condition += (r' /\ $dz_raw(S_handler) = ' + resumed + r' /\ ' +
            no.fallback_proof('S_default', 'perrorcall_return', events[0], resumed))
        if prior.two_calls(name):
            condition += (r' /\ $dz_raw(S_handler_right) = S /\ ' +
                no.fallback_proof('S_default_right', 'perrorcall_return_right', events[1], 'S'))
    return condition


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'integer-to-Boolean cast'), converted(name, condition))
              for label, condition in checks]
    checks += [('canonical emitted BOOL cast retains exact PINT child and strict fallback choice',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(name, condition)) for label, condition in checks],
        ('typed Boolean/default choice survives real formal and native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
