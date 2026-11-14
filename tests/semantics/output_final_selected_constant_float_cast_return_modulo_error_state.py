#!/usr/bin/env python3
"""Own emitted Boolean/null-to-FLOAT returns preserve real FINAL retirement."""
import output_final_selected_integer_float_cast_return_modulo_error_state as integers
import output_final_selected_constant_float_cast_return_modulo_error_sources as sources

prior, runner = integers.prior, integers.runner
PREFIX = integers.PREFIX
CASES = {name: sources.CASES['native-selected-constant-float-cast-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}
KEYWORDS = {'warning-left-constant': ('true', 'PBOOL true', 0x3ff0000000000000),
            'deprecated-both-cv-pair': ('false', 'PBOOL false', 0),
            'warning-right-cv-pair': ('null', 'PNULL', 0),
            'warning-deprecated-constant-float': ('TrUe', 'PBOOL true', 0x3ff0000000000000)}


def converted(condition):
    return integers.converted(condition).replace('selected_modulo_integer_float_cast_return',
                                                'selected_modulo_constant_float_cast_return')


def constant(condition):
    return condition.replace('NScalarInt (INTEGER i_child) metadata_integer',
        'NExprConstFetch (NName (BYTES text_constant) metadata_name) metadata_constant').replace(
        '_integer', '_constant').replace('PINT i_child', 'pvalue_child')


def return_bindings(name):
    return [constant(binding) for binding in integers.return_bindings(name)] + [
        '$origin_child((porigin_constant), [PCFIELD 0]) = (porigin_constant_name)',
        '$origin_node(S.SOURCES, porigin_constant_name) = (NName (BYTES text_constant) metadata_name)',
        '$special_constant($base64(text_constant)) = (pvalue_child)']


def return_proof(name):
    keyword, value, result = KEYWORDS[name]
    condition = constant(integers.return_proof(name))
    conversion = 'n_return = $float_of_int(i_child)'
    input_range = r'$long_range(i_child) /\ '
    input_value = 'i_child = ' + str(integers.VALUES[name]) + r' /\ '
    output_value = 'n_return = ' + str(integers.RETURN_VALUES[name])
    for expected in [conversion, input_range, input_value, output_value]:
        assert condition.count(expected) == 1
    condition = condition.replace(conversion, 'n_return = $float_of_int($cast_truth_int(S, pvalue_child))').replace(
        input_range, '').replace(input_value, 'pvalue_child = ' + value + r' /\ ').replace(
        output_value, 'n_return = ' + str(result))
    assert 'i_child' not in condition
    return ('$base64(text_constant) = $ptascii("' + keyword + r'") /\ '
        r'$origin_child((porigin_constant), [PCFIELD 0]) = (porigin_constant_name) /\ '
        r'$origin_node(S.SOURCES, porigin_constant_name) = (NName (BYTES text_constant) metadata_name) /\ '
        r'$special_constant($base64(text_constant)) = (pvalue_child) /\ ' + condition)


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'emitted Boolean/null FLOAT cast'), converted(condition))
              for label, condition in checks]
    checks += [('the canonical emitted cast returns PFLOAT1 or positive zero from its exact keyword child',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(condition)) for label, condition in checks],
        ('the full Boolean/null FLOAT cast survives actual formal and native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
