#!/usr/bin/env python3
"""Own nonzero integer returns precede selected FINAL MOD Error capture."""
import output_final_selected_zero_return_modulo_error_state as zero
import output_final_selected_integer_return_modulo_error_sources as sources

prior, runner = zero.prior, zero.runner
PREFIX = zero.PREFIX.replace('(PINT 0)', '(PINT i_return)')
CASES = {name: sources.CASES['native-selected-integer-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}
VALUES = {'warning-left-constant': 1, 'deprecated-both-cv-pair': 9223372036854775807,
          'warning-right-cv-pair': 4611686018427387905,
          'warning-deprecated-constant-float': 5}


def converted(condition):
    condition = prior.converted(condition).replace('selected_modulo_explicit_null',
                                                  'selected_modulo_integer_return')
    for state in ['S_handler', 'S_handler_right']:
        condition = condition.replace(state + '.RESULT = KNOWN PNULL',
                                      state + '.RESULT = KNOWN (PINT i_return)')
    return condition


def return_bindings(name):
    return [binding.replace('(PINT 0)', '(PINT i_return)').replace('INTEGER 0', 'INTEGER i_return').replace(
        '_zero', '_integer') for binding in zero.return_bindings(name)]


def return_proof(name):
    return (zero.return_proof(name).replace('(PINT 0)', '(PINT i_return)').replace('_zero', '_integer') +
            r' /\ $long_range(i_return) /\ i_return =/= 0 /\ i_return = ' + str(VALUES[name]))


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'nonzero integer'), converted(condition)) for label, condition in checks]
    checks += [('the own raw integer child/read and actual return retain NULL scratch and strict FALSE handling',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(condition)) for label, condition in checks],
        ('the exact integer return and NULL scratch survive capture and real retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
