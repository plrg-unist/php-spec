"""Both actual same-CV Warnings retain NULL despite later writes."""
from undefined_spaceship_second_protocol import PREFIX as COMMON, checks as previous_checks

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
                        'BINARY_RIGHT pbin poperand z\n  -- if ' +
                        r'pbin = EQUAL \/ pbin = NOTEQUAL \/ pbin = LESS \/ pbin = LESSEQUAL')


def checks(program, path, name):
    false = name == 'same-second-less-equal-false'
    op = 'LESSEQUAL' if false else 'EQUAL'
    values = previous_checks(program, path, 'second-spaceship-same-false')
    result = [values[0]]
    for condition in values[1:]:
        if condition.startswith('perrorread_other = '):
            condition = condition.replace('BINARY_RIGHT NOTEQUAL ', 'BINARY_RIGHT GREATER ')
        condition = condition.replace('BINARY_RIGHT SPACESHIP ', 'BINARY_RIGHT ' + op + ' ')
        condition = condition.replace('$spaceship_read_again(', '$scalar_compare_read_again(')
        condition = condition.replace('$spaceship_read_other(', '$scalar_compare_read_other(')
        condition = condition.replace('spaceship warning changed opposing scalar', 'scalar comparison warning changed right operand')
        if condition.startswith(('S_compared = ', 'S_again_compared = ')):
            condition = condition.replace('KNOWN (PINT 0)', 'KNOWN (PBOOL true)')
        for index in (1, 2):
            if condition.startswith('S_return_' + str(index) + '.RESULT = '):
                condition = 'S_return_' + str(index) + '.RESULT = KNOWN (PBOOL ' + ('false' if false else 'true') + ')'
            if condition.startswith('S_resume_' + str(index) + '.EVENTS = '):
                condition = 'S_resume_' + str(index) + '.EVENTS = S_return_' + str(index) + '.EVENTS'
                if false:
                    condition += ' ++ [$error_default_event(S_return_' + str(index) + ',WARNING ($ptascii("x")) 10)]'
        if not false and condition == 'S_resume_2.STORE[n_right] = DEFINED (PBOOL true)':
            result += ['S_resume_2.STORE[n_right] = DEFINED pvalue_right',
                       '$string_plain(pvalue_right) = PSTRING ($ptascii("0"))']
            continue
        result.append(condition)
    result += [
        '$scalar_compare_right_read_shape(ptask_original,S_0.RESULT,S_0.BASE) = eps',
        'perrorread_first.NAME = perrorread_second.NAME',
        'S_restored_1.ORIGIN = (porigin_same)',
        '$error_variable_source(S_restored_1,(porigin_same),[PCFIELD 0],$ptascii("x"))',
        '$error_variable_source(S_restored_1,(porigin_same),[PCFIELD 1],$ptascii("x"))',
        '$code_expression_at_source(S_restored_1,porigin_same,[PCFIELD 0]) = (z_left)',
        '$code_expression_at_source(S_restored_1,porigin_same,[PCFIELD 1]) = (10)',
        'S_no_code = S_restored_1[.CODE = eps]',
        '~$error_read_source(S_no_code,perrorread_second)',
        '~$error_read_valid(S_no_code,perrorread_second)',
        'perrorread_nonnull = perrorread_second[.ORIGINAL = BINARY_RIGHT ' + op + ' (KNOWN (PINT 1)) 10][.TASK = BINARY_RIGHT ' + op + ' (KNOWN (PINT 1)) 10]',
        '$error_read_shape(perrorread_nonnull.ORIGINAL,perrorread_nonnull.INPUT,perrorread_nonnull.BASE) = (perrorread_nonnull)',
        '~$error_read_source(S_restored_1,perrorread_nonnull)',
        '~$error_read_valid(S_restored_1,perrorread_nonnull)',
        'perrorread_reversed = perrorread_first[.ORIGINAL = BINARY_RIGHT GREATER (VARIABLE ($ptascii("x")) z_left) 10][.TASK = BINARY_RIGHT GREATER (KNOWN PNULL) 10]',
        '$error_read_shape(perrorread_reversed.ORIGINAL,perrorread_reversed.INPUT,perrorread_reversed.BASE) = (perrorread_reversed)',
        '~$scalar_compare_missing_pair(S_0,perrorread_reversed)',
        '~$scalar_compare_read_again(S_resume_1,perrorread_reversed)',
        '~$error_read_valid(S_resume_1,perrorread_reversed)',
    ]
    return list(dict.fromkeys(result))
