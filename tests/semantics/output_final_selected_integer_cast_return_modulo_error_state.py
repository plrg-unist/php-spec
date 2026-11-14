#!/usr/bin/env python3
"""Own emitted int casts preserve real FINAL MOD Error retirement."""
import output_final_selected_positive_integer_return_modulo_error_state as integers
import output_final_selected_integer_cast_return_modulo_error_sources as sources

prior, runner = integers.prior, integers.runner
PREFIX = integers.PREFIX
CASES = {name: sources.CASES['native-selected-integer-cast-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}
VALUES, RETURN_VALUES = integers.VALUES, integers.RETURN_VALUES


def converted(condition):
    return integers.converted(condition).replace('selected_modulo_positive_integer_return',
                                                'selected_modulo_integer_cast_return')


def casted(condition):
    return condition.replace('NExprUnaryPlus', 'NExprCastInt').replace(
        '_positive', '_cast').replace('$unary_apply(S, POSITIVE, ', '$cast_apply(S, CASTINT, ')


def return_bindings(name):
    return [casted(binding) for binding in integers.return_bindings(name)]


def return_proof(name):
    condition = casted(integers.return_proof(name))
    assert condition.count(r' /\ b_cast /\ ') == 1
    condition = condition.replace(r' /\ b_cast /\ ', r' /\ ~b_cast /\ ')
    for state in ['S_return', 'S', *(['S_return_right'] if prior.two_calls(name) else [])]:
        read = '$compiled_read(' + state + ', porigin_cast) = (PINT i_return)'
        assert condition.count(read) == 1
        condition = condition.replace(read, '$compiled_read(' + state + ', porigin_cast) = eps')
    return r'S.COMPLETION = NORMAL /\ ' + condition


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'emitted integer cast'), converted(condition)) for label, condition in checks]
    checks += [('the emitted cast has CODEfalse/read-eps while its raw child retains CODEtrue/PINT authority',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(condition)) for label, condition in checks],
        ('the full quiet emitted cast result survives actual formal and native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
