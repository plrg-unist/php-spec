#!/usr/bin/env python3
"""Own string-to-numeric returns preserve typed values and real FINAL retirement."""
import output_final_selected_integer_cast_return_modulo_error_state as integers
import output_final_selected_integer_float_cast_return_modulo_error_state as floats
import output_final_selected_string_numeric_cast_return_modulo_error_sources as sources

prior, runner = integers.prior, integers.runner
PREFIX = integers.PREFIX.replace('(PINT i_return)', 'pvalue_return')
CASES = {name: sources.CASES['native-selected-string-numeric-cast-return-modulo-error-' + name]
         for name in ['warning-left-constant', 'warning-right-cv-pair']}
STRINGS = {'warning-left-constant': '', 'deprecated-both-cv-pair': '-4.75tail',
           'warning-right-cv-pair': 'x', 'warning-deprecated-constant-float': '0.125tail'}
KINDS = {name: ('int' if name in ['warning-left-constant', 'deprecated-both-cv-pair'] else 'float')
         for name in STRINGS}
VALUES = {'warning-left-constant': 0, 'deprecated-both-cv-pair': -4,
          'warning-right-cv-pair': 0, 'warning-deprecated-constant-float': 0x3fc0000000000000}


def base_for(name):
    return integers if KINDS[name] == 'int' else floats


def converted(name, condition):
    return base_for(name).converted(condition).replace('selected_modulo_integer_float_cast_return',
        'selected_modulo_string_numeric_cast_return').replace('selected_modulo_integer_cast_return',
        'selected_modulo_string_numeric_cast_return')


def stringed(condition):
    return condition.replace('NScalarInt (INTEGER i_child) metadata_integer',
        'NScalarString (BYTES text_string) metadata_string').replace('_integer', '_string').replace(
        'PINT i_child', 'PSTRING n_string*').replace(
        'CASTINT, PSTRING n_string*,', 'CASTINT, PSTRING_CARRIER INTERNED_STRING n_string*,').replace(
        'CASTFLOAT, PSTRING n_string*,', 'CASTFLOAT, PSTRING_CARRIER INTERNED_STRING n_string*,')


def return_bindings(name):
    return [stringed(binding) for binding in base_for(name).return_bindings(name)] + [
        '$evaluate(NScalarString (BYTES text_string) metadata_string) = VALUE (PSTRING n_string*)']


def return_proof(name):
    condition = stringed(base_for(name).return_proof(name))
    input_range = r'$long_range(i_child) /\ '
    input_value = 'i_child = ' + str(integers.VALUES[name])
    result = 'i_return' if KINDS[name] == 'int' else 'n_return'
    output_value = result + ' = ' + str(base_for(name).RETURN_VALUES[name])
    for expected in [input_range, input_value, output_value]:
        assert condition.count(expected) == 1
    condition = condition.replace(input_range, '').replace(input_value,
        'n_string* = $ptascii("' + STRINGS[name] + '")').replace(
        output_value, result + ' = ' + str(VALUES[name]))
    if KINDS[name] == 'float':
        conversion = 'n_return = $float_of_int(i_child)'
        assert condition.count(conversion) == 1
        condition = condition.replace(conversion, 'n_return = $string_cast_float(n_string*)')
    else:
        condition += r' /\ $plstyle(metadata_cast) = 1 /\ i_return = $string_cast_integer(n_string*)'
    assert 'i_child' not in condition
    condition += (r' /\ $base64(text_string) = n_string* /\ ~(0 <- n_string*) /\ '
        r'$value_nodes(PSTRING_CARRIER INTERNED_STRING n_string*) = eps')
    for state in ['S_return', 'S', *(['S_return_right'] if prior.two_calls(name) else [])]:
        condition += (' /\\ $compiled_string_value(' + state + ', porigin_string, PSTRING n_string*) = '
                      'PSTRING_CARRIER INTERNED_STRING n_string*')
    return condition


def frontier(name, fixture, path):
    bindings, checks = prior.base_for(name).frontier(name, fixture, path)
    bindings += return_bindings(name)
    checks = [(label.replace('NULL', 'string-to-numeric cast'), converted(name, condition))
              for label, condition in checks]
    checks += [('the exact raw string and mandatory carrier produce the precise typed numeric return',
                return_proof(name))]
    assert not any('pobobjectreturn_seed' in binding for binding in bindings)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = prior.base_for(name).lifecycle(name, fixture, path)
    return bindings + return_bindings(name), [
        *[(label, converted(name, condition)) for label, condition in checks],
        ('numeric zero stays distinct from FALSE through actual formal and native-cell retirement', return_proof(name))]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
