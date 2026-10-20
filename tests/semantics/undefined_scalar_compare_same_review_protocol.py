"""Shared-CV nonreflexivity with independent late-reference state checks."""
from undefined_spaceship_same_review_protocol import PREFIX as COMMON, checks as previous_checks, text

PREFIX = COMMON.replace('pbin = SPACESHIP', r'pbin = EQUAL \/ pbin = LESS')


def checks(program, path, name):
    target = name == 'peer-same-forward-less-notequal-target-reference'
    previous = ('peer-same-missing-spaceship-bound-to-target-reference' if target else
                'peer-same-missing-spaceship-fresh-reference')
    op, line, answer = ('LESS', 9, 'true') if target else ('EQUAL', 12, 'false')
    values = previous_checks(program, path, previous)
    result = [values[0]]
    for condition in values[1:]:
        condition = condition.replace('BINARY_RIGHT SPACESHIP ', 'BINARY_RIGHT ' + op + ' ')
        condition = condition.replace('$spaceship_read_other(', '$scalar_compare_read_other(')
        condition = condition.replace('$spaceship_right_read_shape(', '$scalar_compare_right_read_shape(')
        condition = condition.replace('spaceship warning changed opposing scalar',
                                      'scalar comparison warning changed right operand')
        if condition.startswith('S_compared = '):
            condition = condition.replace('KNOWN (PINT $(-1))', 'KNOWN (PBOOL ' + answer + ')')
        if condition == 'PhpStep: S_without ~> S_without_restored':
            result.append('$scalar_compare_read_again(S_without,perrorread)')
        if condition.startswith('$us_output('):
            expected = ('H:1:1:9;H:1:1:11;R:1:1:1:1;A:1:1:1;END;' if target else
                        'H:1:1:12;R:1:1:1;A:1:1;END;')
            condition = '$us_output(S_done.EVENTS) = ' + text(expected)
        result.append(condition)
    result += [
        '$error_read_shape(perrorread.TASK,perrorread.RESULT,perrorread.BASE) = (perrorread_second)',
        '$error_read_source(S_without,perrorread_second)',
        '$error_read_valid(S_without,perrorread_second)',
        'S.ORIGIN = (porigin_same)',
        '$code_expression_at_source(S,porigin_same,[PCFIELD 0]) = (z_left)',
        '$code_expression_at_source(S,porigin_same,[PCFIELD 1]) = (' + str(line) + ')',
        'perrorread_reversed = perrorread[.ORIGINAL = BINARY_RIGHT GREATER (VARIABLE ($ptascii("x")) z_left) ' + str(line) + '][.TASK = BINARY_RIGHT GREATER (KNOWN PNULL) ' + str(line) + ']',
        '$error_read_shape(perrorread_reversed.ORIGINAL,perrorread_reversed.INPUT,perrorread_reversed.BASE) = (perrorread_reversed)',
        '~$scalar_compare_missing_pair(S,perrorread_reversed)',
        '~$error_read_valid(S,perrorread_reversed)',
    ]
    return result
