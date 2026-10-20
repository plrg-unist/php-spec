"""Forward comparison booleans preserve the two authentic frozen-NULL reads."""
from undefined_spaceship_second_review_protocol import PREFIX as COMMON, checks as previous_checks

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
                        'BINARY_RIGHT pbin poperand z\n  -- if '
                        + r'pbin = EQUAL \/ pbin = NOTEQUAL \/ pbin = LESS \/ pbin = LESSEQUAL')


def checks(program, path, name):
    target = name == 'peer-second-warning-less-unset-right-target-reference'
    operator = 'LESS' if target else 'EQUAL'
    value = 'false' if target else 'true'
    previous = ('peer-second-warning-spaceship-unset-right-target-reference' if target else
                'peer-second-warning-spaceship-fresh-reference')
    values = previous_checks(program, path, previous)
    result = [values[0]]
    for condition in values[1:]:
        if condition.startswith('perrorread_equal = '):
            condition = condition.replace('BINARY_RIGHT EQUAL ', 'BINARY_RIGHT GREATER ')
        condition = condition.replace('perrorread_equal', 'perrorread_reversed')
        condition = condition.replace('BINARY_RIGHT SPACESHIP ', 'BINARY_RIGHT ' + operator + ' ')
        condition = condition.replace('$spaceship_read_again(', '$scalar_compare_read_again(')
        condition = condition.replace('$spaceship_read_other(', '$scalar_compare_read_other(')
        condition = condition.replace('$spaceship_right_read_shape(', '$scalar_compare_right_read_shape(')
        condition = condition.replace('spaceship warning changed opposing scalar',
                                      'scalar comparison warning changed right operand')
        if condition.startswith('S_wrong_denied = '):
            condition = condition.replace('changed right operand', 'changed left operand')
        if condition.startswith('S_compared = '):
            condition = condition.replace('KNOWN (PINT 0)', 'KNOWN (PBOOL ' + value + ')')
        result.append(condition)
    line = 13 if target else 16
    result += [
        '~$error_read_valid(S_first_resume,perrorread_reversed)',
        'perrorread_value = perrorread_second[.ORIGINAL = BINARY_RIGHT ' + operator + ' (KNOWN (PINT 1)) ' + str(line) + '][.TASK = BINARY_RIGHT ' + operator + ' (KNOWN (PINT 1)) ' + str(line) + ']',
        '$error_read_shape(perrorread_value.ORIGINAL,perrorread_value.INPUT,perrorread_value.BASE) = (perrorread_value)',
        '~$error_read_valid(S_first_restored,perrorread_value)',
    ]
    return result
