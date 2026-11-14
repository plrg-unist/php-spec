#!/usr/bin/env python3
"""Own emitted float casts preserve real FINAL MOD Error retirement."""
import output_final_selected_integer_cast_return_modulo_error_state as integers
import output_final_selected_integer_float_cast_return_modulo_error_sources as sources

prior, runner = integers.prior, integers.runner
PREFIX = integers.PREFIX.replace('(PINT i_return)', '(PFLOAT n_return)')
CASES = {name: sources.CASES['native-selected-integer-float-cast-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}
VALUES = integers.VALUES
RETURN_VALUES = {'warning-left-constant': 0x3ff0000000000000,
                 'deprecated-both-cv-pair': 0x401c000000000000,
                 'warning-right-cv-pair': 0,
                 'warning-deprecated-constant-float': 0x43e0000000000000}


def converted(condition):
    return integers.converted(condition).replace('selected_modulo_integer_cast_return',
        'selected_modulo_integer_float_cast_return').replace('(PINT i_return)', '(PFLOAT n_return)')


def floated(condition):
    return condition.replace('NExprCastInt', 'NExprCastDouble').replace(
        'CASTINT', 'CASTFLOAT').replace('(PINT i_return)', '(PFLOAT n_return)')


def return_bindings(name):
    return [floated(binding) for binding in integers.return_bindings(name)]


def return_proof(name):
    condition = floated(integers.return_proof(name))
    result_range = r' /\ $long_range(i_return)'
    expected = 'i_return = ' + str(VALUES[name])
    assert condition.count(result_range) == condition.count(expected) == 1
    condition = condition.replace(result_range, '').replace(expected, 'n_return = ' + str(RETURN_VALUES[name]))
    assert 'i_return' not in condition
    return r'$plstyle(metadata_cast) = 2 /\ n_return = $float_of_int(i_child) /\ ' + condition


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'emitted FLOAT cast'), converted(condition)) for label, condition in checks]
    checks += [('the canonical emitted FLOAT cast rounds its true PINT child without a root pool',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(condition)) for label, condition in checks],
        ('the full quiet emitted FLOAT cast survives actual formal and native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
