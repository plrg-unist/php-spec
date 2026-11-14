#!/usr/bin/env python3
"""Own emitted keyword-to-Boolean casts retain strict default-diagnostic choice."""
import output_final_selected_integer_bool_cast_return_modulo_error_state as integers
import output_final_selected_constant_bool_cast_return_modulo_error_sources as sources

prior, runner = integers.prior, integers.runner
PREFIX = integers.PREFIX
CASES = {name: sources.CASES['native-selected-constant-bool-cast-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}
KEYWORDS = {'warning-left-constant': ('FaLsE', 'PBOOL false'),
            'deprecated-both-cv-pair': ('NULL', 'PNULL'),
            'warning-right-cv-pair': ('true', 'PBOOL true'),
            'warning-deprecated-constant-float': ('TrUe', 'PBOOL true')}


def converted(name, condition):
    return integers.converted(name, condition).replace('selected_modulo_integer_bool_cast_return',
        'selected_modulo_constant_bool_cast_return')


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
    keyword, value = KEYWORDS[name]
    condition = constant(integers.return_proof(name))
    input_range = r'$long_range(i_child) /\ '
    input_value = 'i_child = ' + str(integers.VALUES[name])
    for expected in [input_range, input_value]:
        assert condition.count(expected) == 1
    condition = condition.replace(input_range, '').replace(input_value, 'pvalue_child = ' + value)
    assert 'i_child' not in condition
    return ('$base64(text_constant) = $ptascii("' + keyword + r'") /\ '
        r'$origin_child((porigin_constant), [PCFIELD 0]) = (porigin_constant_name) /\ '
        r'$origin_node(S.SOURCES, porigin_constant_name) = (NName (BYTES text_constant) metadata_name) /\ '
        r'$special_constant($base64(text_constant)) = (pvalue_child) /\ '
        r'b_return = $truth(S, pvalue_child) /\ ' + condition)


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'keyword-to-Boolean cast'), converted(name, condition))
              for label, condition in checks]
    checks += [('canonical emitted BOOL cast retains its exact typed and indexed keyword child',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(name, condition)) for label, condition in checks],
        ('typed keyword BOOL/default choice survives real formal and native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
