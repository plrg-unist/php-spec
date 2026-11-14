#!/usr/bin/env python3
"""Own unary-minus integer returns preserve real FINAL MOD Error retirement."""
import output_final_selected_zero_return_modulo_error_state as zero
import output_final_selected_negative_integer_return_modulo_error_sources as sources

prior, runner = zero.prior, zero.runner
PREFIX = zero.PREFIX.replace('(PINT 0)', '(PINT i_return)')
CASES = {name: sources.CASES['native-selected-negative-integer-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}
VALUES = {'warning-left-constant': 1, 'deprecated-both-cv-pair': 7,
          'warning-right-cv-pair': 0,
          'warning-deprecated-constant-float': 9223372036854775807}
RETURN_VALUES = {name: -value for name, value in VALUES.items()}


def converted(condition):
    condition = prior.converted(condition).replace('selected_modulo_explicit_null',
                                                  'selected_modulo_negative_integer_return')
    for state in ['S_handler', 'S_handler_right']:
        condition = condition.replace(state + '.RESULT = KNOWN PNULL',
                                      state + '.RESULT = KNOWN (PINT i_return)')
    return condition


def return_bindings(name):
    return [binding.replace('NScalarInt (INTEGER 0) metadata_zero',
        'NExprUnaryMinus (NScalarInt (INTEGER i_child) metadata_integer) metadata_negative').replace(
        '(PINT 0)', '(PINT i_return)').replace('_zero', '_negative')
        for binding in zero.return_bindings(name)] + [
        '$origin_node(S.SOURCES, porigin_negative) = (NExprUnaryMinus (NScalarInt (INTEGER i_child) metadata_integer) metadata_negative)',
        '$origin_child((porigin_negative), [PCFIELD 0]) = (porigin_integer)',
        'porigin_integer = PORIGIN n_negative_handler pcpath_integer',
        '$origin_node(S.SOURCES, porigin_integer) = (NScalarInt (INTEGER i_child) metadata_integer)',
        '$code_expression(pfunction_handler.CODE.EXPRESSIONS, pcpath_integer) = ((z_integer, b_integer))']


def return_proof(name):
    condition = zero.return_proof(name).replace('(PINT 0)', '(PINT i_return)').replace(
        '_zero', '_negative').replace('z_negative = $source_line(metadata_negative)',
        'z_negative = $expression_line(NScalarInt (INTEGER i_child) metadata_integer)')
    condition += (r' /\ pcpath_integer = pcpath_negative ++ [PCFIELD 0] /\ '
        r'z_integer = $source_line(metadata_integer) /\ b_integer /\ z_negative = z_integer /\ '
        r'$long_range(i_child) /\ $long_range(i_return) /\ i_child = ' + str(VALUES[name]) +
        r' /\ i_return = ' + str(RETURN_VALUES[name]) + r' /\ '
        r'$unary_apply(S, NEGATIVE, PINT i_child, z_negative) = S[.RESULT = KNOWN (PINT i_return)] /\ '
        r'$compiled_read(S_return, porigin_integer) = (PINT i_child) /\ '
        r'$compiled_read(S, porigin_integer) = (PINT i_child)')
    if prior.two_calls(name):
        condition += r' /\ $compiled_read(S_return_right, porigin_integer) = (PINT i_child)'
    return condition


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'negative integer'), converted(condition)) for label, condition in checks]
    checks += [('the exact unary root and raw integer child retain their folded PINTs and NULL scratch',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(condition)) for label, condition in checks],
        ('the full integer unary result survives actual formal and native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
