"""Fresh reversed-opcode sources with complete reference-cell state checks."""
from undefined_scalar_compare_ne_le_review_protocol import PREFIX as COMMON, checks as previous_checks, text

PREFIX = COMMON.replace(r'pbin = NOTEQUAL \/ pbin = LESSEQUAL',
                        r'pbin = GREATER \/ pbin = GREATEREQUAL')


def checks(program, path, name):
    left = name == 'peer-missing-left-right-reference-both-operators'
    previous = ('peer-missing-left-reference-both-operators' if left
                else 'peer-missing-right-left-reference-rebound-string')
    values = previous_checks(program, path, previous)
    # Retain the actual checked source. Only reached consumers, their predicates
    # and the independently selected multiline source locations change.
    result = [values[0]]
    for condition in values[1:]:
        if left:
            condition = condition.replace('BINARY_RIGHT NOTEQUAL ', 'BINARY_RIGHT GREATEREQUAL ')
            condition = condition.replace(') 11', ') 13').replace(' = 11', ' = 13')
            if condition == 'PhpStep: S_without ~> S_without_restored':
                condition = 'PhpStep: S_without ~> S_denied'
            if condition.startswith('S_without_restored = S_without['):
                condition = 'S_denied = S_without[.TODO = eps][.COMPLETION = UNSUPPORTED "scalar comparison warning changed right operand"]'
            if condition == '$error_read_plan(S_both) = (perrorread)':
                result += [
                    '$scalar_compare_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread_both_right)',
                    '$error_read_plan(S_both) = (perrorread_both_right)',
                ]
                continue
            if condition.startswith('S_compared = '):
                condition = condition.replace('KNOWN (PBOOL true)', 'KNOWN (PBOOL false)')
            if condition.startswith('$us_output('):
                condition = '$us_output(S_done.EVENTS) = ' + text(
                    'H:1:1:13;G:1:1:1;H:1:1:16;P:1:1:1;A:1;END;')
        else:
            condition = condition.replace('BINARY_RIGHT LESSEQUAL ', 'BINARY_RIGHT GREATER ')
            if condition == '$error_read_plan(S_both) = (perrorread_left)':
                condition = '$error_read_plan(S_both) = (perrorread)'
            if condition == 'PhpStep: S_without ~> S_denied':
                result.append('$scalar_compare_read_again(S_without,perrorread)')
                condition = 'PhpStep: S_without ~> S_without_restored'
            if condition.startswith('S_denied = S_without['):
                condition = 'S_without_restored = S_without[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]'
            if condition.startswith(('S_compared = ', 'S_right_compared = ')):
                condition = condition.replace('KNOWN (PBOOL false)', 'KNOWN (PBOOL true)')
        if condition.startswith('S_denied = S_without['):
            result.append('~$scalar_compare_read_again(S_without,perrorread)')
        result.append(condition)
    return result
