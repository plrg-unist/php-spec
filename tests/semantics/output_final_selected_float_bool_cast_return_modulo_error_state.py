#!/usr/bin/env python3
"""Own emitted FLOAT-to-Boolean casts retain strict default-diagnostic choice."""
import output_final_selected_integer_bool_cast_return_modulo_error_state as integers
import output_final_selected_float_bool_cast_return_modulo_error_sources as sources

prior, runner = integers.prior, integers.runner
PREFIX = integers.PREFIX
CASES = {name: sources.CASES['native-selected-float-bool-cast-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}
BITS = {'warning-left-constant': '0000000000000000',
        'deprecated-both-cv-pair': '0000000000000000',
        'warning-right-cv-pair': '0000000000000001',
        'warning-deprecated-constant-float': '7ff0000000000000'}


def converted(name, condition):
    return integers.converted(name, condition).replace('selected_modulo_integer_bool_cast_return',
        'selected_modulo_float_bool_cast_return')


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
    assert condition.count(input_range) == 1
    condition = condition.replace(input_range, '')
    value = 'i_child = ' + str(integers.VALUES[name])
    assert condition.count(value) == 1
    condition = condition.replace(value, 'text_float = "' + BITS[name] +
        '" /\\ n_child = ' + str(int(BITS[name], 16)))
    assert 'i_child' not in condition
    return r'$number_bool(NFLOAT n_child) = (b_return, false) /\ ' + condition


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'FLOAT-to-Boolean cast'), converted(name, condition))
              for label, condition in checks]
    checks += [('canonical emitted BOOL cast retains exact raw FLOAT and intrinsic quiet truth',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(name, condition)) for label, condition in checks],
        ('typed FLOAT-to-BOOL/default choice survives real formal and native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
