"""Both-missing spaceship state fronts using complete scalar-read conditions."""
from undefined_scalar_compare_both_protocol import PREFIX as COMMON, checks as previous_checks

PREFIX = COMMON.replace(r'pbin = EQUAL \/ pbin = NOTEQUAL \/ pbin = LESS \/ pbin = LESSEQUAL',
                        'pbin = SPACESHIP')


def checks(program, path, name):
    plain = name == 'both-spaceship-string'
    values = previous_checks(program, path, 'equal-both-init' if plain else 'less-equal-both-false')
    result = [values[0]]
    for condition in values[1:]:
        # The old non-spaceship default guard becomes the actual entry domain
        # guard here; the separate negative condition checks its missing RHS.
        if condition == '$spaceship_read_other(S,perrorread)':
            continue
        condition = condition.replace('BINARY_RIGHT EQUAL ', 'BINARY_RIGHT SPACESHIP ')
        condition = condition.replace('BINARY_RIGHT LESSEQUAL ', 'BINARY_RIGHT SPACESHIP ')
        condition = condition.replace('$scalar_compare_read_other(', '$spaceship_read_other(')
        condition = condition.replace('$scalar_compare_right_read_shape(', '$spaceship_right_read_shape(')
        condition = condition.replace('scalar comparison warning changed right operand',
                                      'spaceship warning changed opposing scalar')
        for state, restored in (('S_removed', 'S_removed_refused'), ('S_without', 'S_denied')):
            if condition == restored + ' = ' + state + '[.TODO = eps][.COMPLETION = UNSUPPORTED "spaceship warning changed opposing scalar"]':
                condition = restored + ' = ' + state + '[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]'
        if condition.startswith('S_compared = '):
            condition = condition.replace('KNOWN (PBOOL true)', 'KNOWN (PINT $(-1))')
        if plain and condition == 'S_resume.STORE[n_right] = DEFINED (PINT 0)':
            result += ['S_resume.STORE[n_right] = DEFINED pvalue_string',
                       '$string_plain(pvalue_string) = PSTRING ($ptascii("0"))']
            continue
        result.append(condition)
    return result
