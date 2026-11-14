#!/usr/bin/env python3
"""Own canonical float returns precede selected FINAL MOD Error capture."""
import output_final_selected_zero_return_modulo_error_state as zero
import output_final_selected_float_return_modulo_error_sources as sources

prior, runner = zero.prior, zero.runner
PREFIX = zero.PREFIX.replace('(PINT 0)', '(PFLOAT n_return)')
CASES = {name: sources.CASES['native-selected-float-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}
BITS = {'warning-left-constant': '3ff8000000000000', 'deprecated-both-cv-pair': '0000000000000001',
        'warning-right-cv-pair': '0000000000000000',
        'warning-deprecated-constant-float': '7ff0000000000000'}


def converted(condition):
    condition = prior.converted(condition).replace('selected_modulo_explicit_null',
                                                  'selected_modulo_float_return')
    for state in ['S_handler', 'S_handler_right']:
        condition = condition.replace(state + '.RESULT = KNOWN PNULL',
                                      state + '.RESULT = KNOWN (PFLOAT n_return)')
    return condition


def return_bindings(name):
    return [binding.replace('NScalarInt (INTEGER 0)', 'NScalarFloat (FLOAT text_float)').replace(
        '(PINT 0)', '(PFLOAT n_return)').replace('_zero', '_float')
        for binding in zero.return_bindings(name)] + [
            '|text_float| = 16',
            'n_nibble* = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]',
            '(text_float[n_nibble:1] <- ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"])*']


def return_proof(name):
    return (zero.return_proof(name).replace('(PINT 0)', '(PFLOAT n_return)').replace('_zero', '_float') +
            r' /\ text_float = "' + BITS[name] + r'" /\ |text_float| = 16 /\ '
            r'$evaluate(NScalarFloat (FLOAT text_float) metadata_float) = VALUE (PFLOAT n_return) /\ '
            r'n_return = $hex_bits(text_float, 0)')


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'float'), converted(condition)) for label, condition in checks]
    checks += [('the own raw float bits/read and actual return retain NULL scratch and strict FALSE handling',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(condition)) for label, condition in checks],
        ('the exact float return and NULL scratch survive capture and real retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
