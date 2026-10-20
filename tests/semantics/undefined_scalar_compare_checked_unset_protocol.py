"""Forward Boolean quiet folds reuse complete checked-CV/alias state fronts."""
from undefined_spaceship_checked_unset_protocol import PREFIX as COMMON, checks as previous_checks

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
                        'BINARY_RIGHT pbin poperand z\n  -- if '
                        + r'pbin = EQUAL \/ pbin = NOTEQUAL \/ pbin = LESS \/ pbin = LESSEQUAL')


def checks(program, path, name):
    reference = name == 'checked-lessequal-reference-unset'
    op = 'LESSEQUAL' if reference else 'EQUAL'
    previous = 'checked-left-unset-reference' if reference else 'checked-left-unset-plain'
    values = previous_checks(program, path, previous)
    result = [values[0]]
    for condition in values[1:]:
        if condition.startswith('perrorread_equal = '):
            condition = condition.replace('BINARY_RIGHT EQUAL ', 'BINARY_RIGHT GREATER ')
        condition = condition.replace('BINARY_RIGHT SPACESHIP ', 'BINARY_RIGHT ' + op + ' ')
        condition = condition.replace('$spaceship_right_read_shape(', '$scalar_compare_right_read_shape(')
        condition = condition.replace('$spaceship_read_other(', '$scalar_compare_read_other(')
        condition = condition.replace('$spaceship_read_again(', '$scalar_compare_read_again(')
        condition = condition.replace('$spaceship_checked_missing(', '$scalar_compare_checked_missing(')
        condition = condition.replace('spaceship warning changed opposing scalar', 'scalar comparison warning changed left operand')
        if condition.startswith('S_compared = '):
            condition = condition.replace('KNOWN (PINT 0)', 'KNOWN (PBOOL true)')
        result.append(condition)
    result += [
        'perrorread_space = perrorread[.ORIGINAL = BINARY_RIGHT SPACESHIP (VARIABLE ($ptascii("left")) z_left) 10][.TASK = BINARY_RIGHT SPACESHIP (VARIABLE ($ptascii("left")) z_left) 10]',
        '$spaceship_right_read_shape(perrorread_space.ORIGINAL,perrorread_space.INPUT,perrorread_space.BASE) = (perrorread_space)',
        '$spaceship_checked_missing(S_resume,perrorread_space)',
        '~$scalar_compare_checked_missing(S_resume,perrorread_space)',
        '~$error_read_valid(S_resume,perrorread_space)',
    ]
    return result
