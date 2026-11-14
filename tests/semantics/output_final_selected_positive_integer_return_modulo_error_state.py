#!/usr/bin/env python3
"""Own unary-plus integer returns preserve real FINAL MOD Error retirement."""
import output_final_selected_negative_integer_return_modulo_error_state as integers
import output_final_selected_positive_integer_return_modulo_error_sources as sources

prior, runner = integers.prior, integers.runner
PREFIX = integers.PREFIX
CASES = {name: sources.CASES['native-selected-positive-integer-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}
VALUES = integers.VALUES
RETURN_VALUES = VALUES


def converted(condition):
    return integers.converted(condition).replace('selected_modulo_negative_integer_return',
                                                'selected_modulo_positive_integer_return')


def positive(condition):
    return condition.replace('NExprUnaryMinus', 'NExprUnaryPlus').replace(
        '_negative', '_positive').replace('NEGATIVE', 'POSITIVE')


def return_bindings(name):
    return [positive(binding) for binding in integers.return_bindings(name)]


def return_proof(name):
    condition = positive(integers.return_proof(name))
    expected = 'i_return = ' + str(integers.RETURN_VALUES[name])
    assert condition.count(expected) == 1
    return condition.replace(expected, 'i_return = ' + str(RETURN_VALUES[name]))


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'positive integer'), converted(condition)) for label, condition in checks]
    checks += [('the exact unary-plus root and raw integer child retain identical PINTs and NULL scratch',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(condition)) for label, condition in checks],
        ('the full integer unary-plus result survives actual formal and native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
