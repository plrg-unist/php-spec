"""Same-CV state fronts preserve actual source and the complete read protocol."""
from undefined_spaceship_both_protocol import PREFIX, checks as previous_checks


def checks(program, path, name):
    plain = name == 'same-spaceship-string'
    values = previous_checks(program, path, 'both-spaceship-string' if plain else 'both-spaceship-false')
    result = [values[0]]
    omitted = {
        'S_resume.STORE[n_x] = DEFINED (PINT 9)',
        'perrorread_right =/= perrorread',
        '~$scalar_compare_missing_pair(S,perrorread_right)',
        '~$spaceship_read_other(S,perrorread_right)',
        '~$scalar_compare_missing_pair(S,perrorread[.INPUT = VARIABLE ($ptascii("x")) z_right])',
    }
    for condition in values[1:]:
        if condition in omitted:
            continue
        if condition == '~$error_read_valid(S_resume,perrorread[.NAME = $ptascii("right")])':
            condition = condition.replace('"right"', '"forged"')
        if condition == '~$error_read_valid(S_resume,perrorread[.INPUT = VARIABLE ($ptascii("x")) z_right])':
            condition = condition.replace('"x"', '"forged"')
        if condition.startswith('$spaceship_right_read_shape(ptask_original,'):
            condition = condition.replace(' = (perrorread_right)', ' = eps')
        if condition == '$spaceship_read_other(S_defined,perrorread)':
            condition = '~' + condition
        if condition == '~$scalar_compare_missing_pair(S_defined,perrorread)':
            condition = condition[1:]
        condition = condition.replace('$ptascii("right")', '$ptascii("x")')
        condition = condition.replace('S_defined', 'S_missing_again')
        result.append(condition)
    result += [
        'n_x = n_right',
        'perrorread.INPUT = VARIABLE ($ptascii("x")) z_right',
        '$error_read_source(S_missing_again,perrorread)',
        '$us_guard(S_missing_again)',
    ]
    for op in ('EQUAL', 'GREATER'):
        record = 'perrorread_' + op.lower()
        result += [
            record + ' = perrorread[.ORIGINAL = BINARY_RIGHT ' + op + ' (VARIABLE ($ptascii("x")) z_left) perrorread.LINE][.TASK = BINARY_RIGHT ' + op + ' (KNOWN PNULL) perrorread.LINE]',
            '$error_read_state_shape(S,' + record + '.ORIGINAL,' + record + '.INPUT,' + record + '.BASE) = (' + record + ')',
            ('~$error_read_valid(S,' if op == 'EQUAL' else '~$scalar_compare_missing_pair(S,') + record + ')',
        ]
    if plain:
        result += ['$scalar_compare_missing_pair(S_removed,perrorread)']
    else:
        result += ['$scalar_compare_missing_pair(S_without,perrorread)']
    return result
