#!/usr/bin/env python3
"""Fresh integer-cast histories retain strict keyword and emitted-root authority."""
import output_final_selected_constant_float_cast_return_modulo_error_review_state as previous
import output_final_selected_constant_int_cast_return_modulo_error_state as current
import output_final_selected_constant_int_cast_return_modulo_error_sources as sources

runner = current.runner
CASES = {name: sources.CASES['native-selected-constant-int-cast-return-modulo-error-' + name]
         for name in previous.CASES}


def integer(condition):
    conversion = 'n_return = $float_of_int($cast_truth_int(S, pvalue_child))'
    condition = condition.replace(conversion, 'i_return = $cast_truth_int(S, pvalue_child)')
    for value, result in [(0x3ff0000000000000, 1), (0, 0)]:
        condition = condition.replace('n_return = ' + str(value), 'i_return = ' + str(result))
    condition = condition.replace('selected_modulo_constant_float_cast_return',
        'selected_modulo_constant_int_cast_return').replace('NExprCastDouble', 'NExprCastInt').replace(
        'CASTFLOAT', 'CASTINT').replace('(PFLOAT n_return)', '(PINT i_return)').replace(
        '[.RESULT = KNOWN (PFLOAT 0)]', '[.RESULT = KNOWN (PINT 0)]').replace(
        '$plstyle(metadata_cast) = 2', '$plstyle(metadata_cast) = 1').replace(
        '(Mkind 1) :: metadata_cast', '(Mkind 2) :: metadata_cast')
    assert 'n_return' not in condition
    return condition


PREFIX = integer(previous.PREFIX)
assert 'RETURN_UNWIND (KNOWN (PINT i_return))' in PREFIX


def label_integer(label):
    for before, after in [('FLOAT result', 'integer result'), ('FLOAT cast', 'integer cast'),
                          ('FLOAT bits', 'integer value'), ('FLOAT return', 'integer return')]:
        label = label.replace(before, after)
    return label


def frontier(name, fixture, path):
    bindings, checks = previous.frontier(name, fixture, path)
    bindings = [integer(binding) for binding in bindings]
    checks = [(label_integer(label), integer(condition)) for label, condition in checks]
    assert any('(Mkind 2) :: metadata_cast' in condition for _, condition in checks)
    assert any('child pool of PFLOAT 0' in label and 'PCONSTANT pcpath_constant (PFLOAT 0)' in condition
               for label, condition in checks)
    return bindings, checks


def lifecycle(name, fixture, path):
    bindings, checks = previous.lifecycle(name, fixture, path)
    return [integer(binding) for binding in bindings], [
        (label_integer(label), integer(condition)) for label, condition in checks]


if __name__ == '__main__':
    runner.CASES, runner.PREFIX = CASES, PREFIX
    runner.frontier, runner.lifecycle = frontier, lifecycle
    runner.main()
