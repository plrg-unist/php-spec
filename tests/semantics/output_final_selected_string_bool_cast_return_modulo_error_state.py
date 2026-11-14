#!/usr/bin/env python3
"""Own emitted literal-string BOOL casts retain strict default-diagnostic choice."""
import output_final_selected_integer_bool_cast_return_modulo_error_state as integers
import output_final_selected_string_bool_cast_return_modulo_error_sources as sources

prior, runner = integers.prior, integers.runner
PREFIX = integers.PREFIX
CASES = {name: sources.CASES['native-selected-string-bool-cast-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'deprecated-both-cv-pair']}
STRINGS = {'warning-left-constant': '', 'deprecated-both-cv-pair': '0',
           'warning-right-cv-pair': '00', 'warning-deprecated-constant-float': 'x'}


def converted(name, condition):
    return integers.converted(name, condition).replace('selected_modulo_integer_bool_cast_return',
        'selected_modulo_string_bool_cast_return')


def stringed(condition):
    return condition.replace('NScalarInt (INTEGER i_child) metadata_integer',
        'NScalarString (BYTES text_string) metadata_string').replace(
        '_integer', '_string').replace('PINT i_child', 'PSTRING n_string*').replace(
        '$cast_apply(S, CASTBOOL, PSTRING n_string*, z_cast)',
        '$cast_apply(S, CASTBOOL, PSTRING_CARRIER INTERNED_STRING n_string*, z_cast)')


def return_bindings(name):
    return [stringed(binding) for binding in integers.return_bindings(name)] + [
        '$evaluate(NScalarString (BYTES text_string) metadata_string) = VALUE (PSTRING n_string*)']


def return_proof(name):
    condition = stringed(integers.return_proof(name))
    input_range = r'$long_range(i_child) /\ '
    input_value = 'i_child = ' + str(integers.VALUES[name])
    for expected in [input_range, input_value]:
        assert condition.count(expected) == 1
    condition = condition.replace(input_range, '').replace(input_value,
        'n_string* = $ptascii("' + STRINGS[name] + '")')
    assert 'i_child' not in condition
    condition += (r' /\ $base64(text_string) = n_string* /\ ~(0 <- n_string*) /\ '
        r'$value_nodes(PSTRING_CARRIER INTERNED_STRING n_string*) = eps /\ '
        r'b_return = $truth(S, PSTRING_CARRIER INTERNED_STRING n_string*)')
    for state in ['S_return', 'S', *(['S_return_right'] if prior.two_calls(name) else [])]:
        condition += (' /\\ $compiled_string_value(' + state + ', porigin_string, PSTRING n_string*) = '
                      'PSTRING_CARRIER INTERNED_STRING n_string*')
    return condition


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'interned-string-to-Boolean cast'), converted(name, condition))
              for label, condition in checks]
    checks += [('canonical BOOL cast authenticates raw bytes and its nonowning runtime carrier',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(name, condition)) for label, condition in checks],
        ('typed literal-string BOOL/default choice survives real formal and native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
