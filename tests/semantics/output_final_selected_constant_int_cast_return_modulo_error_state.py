#!/usr/bin/env python3
"""Own emitted Boolean/null-to-integer returns preserve real FINAL retirement."""
import output_final_selected_constant_float_cast_return_modulo_error_state as constants
import output_final_selected_constant_int_cast_return_modulo_error_sources as sources

prior, runner = constants.prior, constants.runner
PREFIX = constants.PREFIX.replace('(PFLOAT n_return)', '(PINT i_return)')
CASES = {name: sources.CASES['native-selected-constant-int-cast-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}
KEYWORDS = {name: (keyword, value, 1 if value == 'PBOOL true' else 0)
            for name, (keyword, value, _) in constants.KEYWORDS.items()}


def converted(condition):
    return constants.converted(condition).replace('selected_modulo_constant_float_cast_return',
        'selected_modulo_constant_int_cast_return').replace('(PFLOAT n_return)', '(PINT i_return)')


def integer(condition):
    return condition.replace('NExprCastDouble', 'NExprCastInt').replace(
        'CASTFLOAT', 'CASTINT').replace('(PFLOAT n_return)', '(PINT i_return)')


def return_bindings(name):
    return [integer(binding) for binding in constants.return_bindings(name)]


def return_proof(name):
    condition = integer(constants.return_proof(name))
    conversion = 'n_return = $float_of_int($cast_truth_int(S, pvalue_child))'
    expected = 'n_return = ' + str(constants.KEYWORDS[name][2])
    style = '$plstyle(metadata_cast) = 2'
    for text in [conversion, expected, style]:
        assert condition.count(text) == 1
    condition = condition.replace(conversion, 'i_return = $cast_truth_int(S, pvalue_child)').replace(
        expected, 'i_return = ' + str(KEYWORDS[name][2])).replace(style, '$plstyle(metadata_cast) = 1')
    assert 'n_return' not in condition
    return condition


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'emitted Boolean/null integer cast'), converted(condition))
              for label, condition in checks]
    checks += [('the canonical emitted cast returns PINT1 or zero from its exact keyword child',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(condition)) for label, condition in checks],
        ('the full Boolean/null integer cast survives actual formal and native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
