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
            if condition.startswith('S_compared = '):
                condition = condition.replace('KNOWN (PBOOL true)', 'KNOWN (PBOOL false)')
            if condition.startswith('$us_output('):
                condition = '$us_output(S_done.EVENTS) = ' + text(
                    'H:1:1:13;G:1:1:1;H:1:1:16;P:1:1:1;A:1;END;')
        else:
            condition = condition.replace('BINARY_RIGHT LESSEQUAL ', 'BINARY_RIGHT GREATER ')
            if condition.startswith(('S_compared = ', 'S_right_compared = ')):
                condition = condition.replace('KNOWN (PBOOL false)', 'KNOWN (PBOOL true)')
        result.append(condition)
    return result
