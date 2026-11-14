#!/usr/bin/env python3
"""Own unary-plus float returns preserve real FINAL MOD Error retirement."""
import output_final_selected_negative_float_return_modulo_error_state as floats
import output_final_selected_positive_float_return_modulo_error_sources as sources

prior, runner = floats.prior, floats.runner
PREFIX = floats.PREFIX
CASES = {name: sources.CASES['native-selected-positive-float-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}
BITS = floats.BITS
RETURN_BITS = BITS


def converted(condition):
    return floats.converted(condition).replace('selected_modulo_negative_float_return',
                                              'selected_modulo_positive_float_return')


def positive(condition):
    return condition.replace('NExprUnaryMinus', 'NExprUnaryPlus').replace(
        '_negative', '_positive').replace('NEGATIVE', 'POSITIVE')


def return_bindings(name):
    return [positive(binding) for binding in floats.return_bindings(name)]


def return_proof(name):
    condition = positive(floats.return_proof(name))
    expected = 'n_return = $hex_bits("' + floats.RETURN_BITS[name] + '", 0)'
    assert condition.count(expected) == 1
    return condition.replace(expected, 'n_return = $hex_bits("' + RETURN_BITS[name] + '", 0)')


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'unary-plus float'), converted(condition)) for label, condition in checks]
    checks += [('the exact unary-plus root and raw float child retain identical bits and NULL scratch',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(condition)) for label, condition in checks],
        ('the full float unary-plus result survives actual formal and native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
