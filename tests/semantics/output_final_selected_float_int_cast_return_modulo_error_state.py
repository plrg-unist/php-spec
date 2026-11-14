#!/usr/bin/env python3
"""Own intrinsically quiet FLOAT-to-int returns preserve FINAL retirement."""
import output_final_selected_integer_cast_return_modulo_error_state as integers
import output_final_selected_float_int_cast_return_modulo_error_sources as sources

prior, runner = integers.prior, integers.runner
PREFIX = integers.PREFIX
CASES = {name: sources.CASES['native-selected-float-int-cast-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}
BITS = {'warning-left-constant': '3ff8000000000000',
        'deprecated-both-cv-pair': '0000000000000001',
        'warning-right-cv-pair': '0000000000000000',
        'warning-deprecated-constant-float': '401e000000000000'}
RETURN_VALUES = {'warning-left-constant': 1, 'deprecated-both-cv-pair': 0,
                 'warning-right-cv-pair': 0, 'warning-deprecated-constant-float': 7}


def converted(condition):
    return integers.converted(condition).replace('selected_modulo_integer_cast_return',
                                                'selected_modulo_float_int_cast_return')


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
    input_range = r'$long_range(i_child) /\ '
    input_value = 'i_child = ' + str(integers.VALUES[name]) + r' /\ '
    output_value = 'i_return = ' + str(integers.RETURN_VALUES[name])
    for expected in [input_range, input_value, output_value]:
        assert condition.count(expected) == 1
    condition = condition.replace(input_range, '').replace(
        input_value, 'text_float = "' + BITS[name] + r'" /\ ').replace(
        output_value, 'i_return = ' + str(RETURN_VALUES[name]))
    assert 'i_child' not in condition
    return condition + r' /\ $float_long(n_child, false) = (i_return, eps)'


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'quiet float int cast'), converted(condition)) for label, condition in checks]
    checks += [('the emitted cast retains its raw PFLOAT child and intrinsically empty notice vector',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(condition)) for label, condition in checks],
        ('the intrinsic quiet float cast preserves the actual PINT through real retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
