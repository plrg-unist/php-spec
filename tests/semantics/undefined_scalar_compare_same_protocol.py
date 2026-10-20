"""Actual shared-CV fronts preserve frozen NULL versus the current value."""
from undefined_spaceship_same_protocol import PREFIX as COMMON, checks as previous_checks

PREFIX = COMMON.replace('pbin = SPACESHIP',
                        r'pbin = EQUAL \/ pbin = NOTEQUAL \/ pbin = LESS \/ pbin = LESSEQUAL')


def checks(program, path, name):
    plain = name == 'same-forward-equal-string'
    op, answer = ('EQUAL', 'false') if plain else ('LESSEQUAL', 'true')
    values = previous_checks(program, path, 'same-spaceship-string' if plain else 'same-spaceship-false')
    result = [values[0]]
    for condition in values[1:]:
        if condition.startswith('perrorread_equal = '):
            condition = condition.replace('BINARY_RIGHT EQUAL ', 'BINARY_RIGHT ' + ('NOTEQUAL' if plain else 'EQUAL') + ' ')
        condition = condition.replace('perrorread_equal', 'perrorread_other')
        condition = condition.replace('BINARY_RIGHT SPACESHIP ', 'BINARY_RIGHT ' + op + ' ')
        condition = condition.replace('$spaceship_read_other(', '$scalar_compare_read_other(')
        condition = condition.replace('$spaceship_right_read_shape(', '$scalar_compare_right_read_shape(')
        condition = condition.replace('spaceship warning changed opposing scalar', 'scalar comparison warning changed right operand')
        if condition.startswith('S_compared = '):
            condition = condition.replace('KNOWN (PINT $(-1))', 'KNOWN (PBOOL ' + answer + ')')
        if not plain and condition == '$string_plain(pvalue_right) = PSTRING ($ptascii("0"))':
            condition = 'pvalue_right = PINT 0'
        result.append(condition)
    result += [
        '$scalar_compare_read_again(S_missing_again,perrorread)',
        '$scalar_compare_right_read_shape(ptask_original,S.RESULT,S.BASE) = eps',
        '$error_read_source(S,perrorread)',
        'S.ORIGIN = (porigin_same)',
        '$error_variable_source(S,S.ORIGIN,[PCFIELD 0],$ptascii("x"))',
        '$error_variable_source(S,S.ORIGIN,[PCFIELD 1],$ptascii("x"))',
        '$code_expression_at_source(S,porigin_same,[PCFIELD 0]) = (z_left)',
        '$code_expression_at_source(S,porigin_same,[PCFIELD 1]) = (perrorread.LINE)',
        'S_no_code = S[.CODE = eps]', '~$error_read_source(S_no_code,perrorread)',
        '~$error_read_valid(S_no_code,perrorread)',
        'S_defined = S_resume[.TODO = ptask_original :: ptask_tail*][.RESULT = perrorread.INPUT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_defined) = eps',
        'perrorread_second = perrorread[.ORIGINAL = BINARY_RIGHT ' + op + ' (KNOWN PNULL) perrorread.LINE][.TASK = BINARY_RIGHT ' + op + ' (KNOWN PNULL) perrorread.LINE][.RESULT = KNOWN PNULL]',
        '$error_read_shape(perrorread_second.ORIGINAL,perrorread_second.INPUT,perrorread_second.BASE) = (perrorread_second)',
        '$error_read_valid(S_missing_again,perrorread_second)',
        '$error_read_source(S_missing_again,perrorread_second)',
    ]
    return result
