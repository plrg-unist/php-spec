"""Forward Boolean results reuse the complete two-Warning state fronts."""
from undefined_spaceship_second_protocol import PREFIX as COMMON, checks as previous_checks

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
                        'BINARY_RIGHT pbin poperand z\n  -- if pbin = EQUAL \\/ pbin = NOTEQUAL \\/ pbin = LESS \\/ pbin = LESSEQUAL')


def checks(program, path, name):
    false = name == 'second-forward-less-equal-false'
    op = 'LESSEQUAL' if false else 'EQUAL'
    values = previous_checks(program, path, 'second-spaceship-string')
    result = [values[0]]
    for condition in values[1:]:
        if condition.startswith('perrorread_other = '):
            condition = condition.replace('BINARY_RIGHT NOTEQUAL ', 'BINARY_RIGHT GREATER ')
        condition = condition.replace('BINARY_RIGHT SPACESHIP ', 'BINARY_RIGHT ' + op + ' ')
        condition = condition.replace('$spaceship_read_again(', '$scalar_compare_read_again(')
        condition = condition.replace('$spaceship_read_other(', '$scalar_compare_read_other(')
        condition = condition.replace('$spaceship_right_read_shape(', '$scalar_compare_right_read_shape(')
        reason = ('scalar comparison warning changed left operand' if condition.startswith('S_right_refused = ')
                  else 'scalar comparison warning changed right operand')
        condition = condition.replace('spaceship warning changed opposing scalar', reason)
        if condition.startswith(('S_compared = ', 'S_again_compared = ')):
            condition = condition.replace('KNOWN (PINT 0)', 'KNOWN (PBOOL true)')
        if false:
            for index, variable in ((1, 'left'), (2, 'right')):
                if condition == 'S_return_' + str(index) + '.RESULT = KNOWN (PBOOL true)':
                    condition = condition.replace('PBOOL true', 'PBOOL false')
                if condition == 'S_resume_' + str(index) + '.EVENTS = S_return_' + str(index) + '.EVENTS':
                    condition += ' ++ [$error_default_event(S_return_' + str(index) + ',WARNING ($ptascii("' + variable + '")) 10)]'
        result.append(condition)
    result += [
        '~$spaceship_checked_missing(S_right_missing,perrorread_right)',
        'perrorread_nonnull = perrorread_second[.ORIGINAL = BINARY_RIGHT ' + op + ' (KNOWN PUNDEFINED) 10][.TASK = BINARY_RIGHT ' + op + ' (KNOWN PUNDEFINED) 10]',
        '$error_read_shape(perrorread_nonnull.ORIGINAL,perrorread_nonnull.INPUT,perrorread_nonnull.BASE) = (perrorread_nonnull)',
        '~$error_read_valid(S_restored_1,perrorread_nonnull)',
        '~$error_read_source(S_restored_1,perrorread_nonnull)',
        '~$scalar_compare_read_again(S_resume_1,perrorread_first[.INPUT = VARIABLE ($ptascii("left")) z_right][.RESULT = VARIABLE ($ptascii("left")) z_right])',
        'S_restored_1.ORIGIN = (porigin_second)',
        '$code_expression_at_source(S_restored_1,porigin_second,[PCFIELD 0]) = (z_left)',
        'S_no_code = S_restored_1[.CODE = eps]',
        '~$error_read_valid(S_no_code,perrorread_second)',
        '~$error_read_source(S_no_code,perrorread_second)',
    ]
    return result
