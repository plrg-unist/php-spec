#!/usr/bin/env python3
"""Own emitted FLOAT-to-FLOAT returns preserve real FINAL retirement."""
import output_final_selected_integer_float_cast_return_modulo_error_state as integers
import output_final_selected_float_float_cast_return_modulo_error_sources as sources

prior, runner = integers.prior, integers.runner
PREFIX = integers.PREFIX
CASES = {name: sources.CASES['native-selected-float-float-cast-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}
BITS = {'warning-left-constant': '3ff8000000000000',
        'deprecated-both-cv-pair': '0000000000000001',
        'warning-right-cv-pair': '0000000000000000',
        'warning-deprecated-constant-float': '7ff0000000000000'}
RETURN_VALUES = {name: int(bits, 16) for name, bits in BITS.items()}


def converted(condition):
    return integers.converted(condition).replace('selected_modulo_integer_float_cast_return',
                                                'selected_modulo_float_float_cast_return')


def floated(condition):
    return condition.replace('NScalarInt (INTEGER i_child) metadata_integer',
        'NScalarFloat (FLOAT text_float) metadata_float').replace(
        '_integer', '_float').replace('PINT i_child', 'PFLOAT n_child')


def return_bindings(name):
    return [floated(binding) for binding in integers.return_bindings(name)] + [
        '|text_float| = 16',
        'n_nibble* = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]',
        '(text_float[n_nibble:1] <- ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"])*',
        '$evaluate(NScalarFloat (FLOAT text_float) metadata_float) = VALUE (PFLOAT n_child)']


def return_proof(name):
    condition = floated(integers.return_proof(name))
    conversion = 'n_return = $float_of_int(i_child)'
    input_range = r'$long_range(i_child) /\ '
    input_value = 'i_child = ' + str(integers.VALUES[name]) + r' /\ '
    output_value = 'n_return = ' + str(integers.RETURN_VALUES[name])
    for expected in [conversion, input_range, input_value, output_value]:
        assert condition.count(expected) == 1
    condition = condition.replace(conversion, 'n_return = n_child').replace(input_range, '').replace(
        input_value, 'text_float = "' + BITS[name] + r'" /\ ').replace(
        output_value, 'n_return = ' + str(RETURN_VALUES[name]))
    assert 'i_child' not in condition
    return condition


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'emitted FLOAT identity cast'), converted(condition)) for label, condition in checks]
    checks += [('the canonical emitted FLOAT cast preserves its exact raw child bits without a root pool',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(condition)) for label, condition in checks],
        ('the full emitted FLOAT identity cast survives actual formal and native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
