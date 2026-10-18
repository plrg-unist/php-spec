"""Fresh !=/<= fronts using the established full scalar-read state checks."""
from undefined_scalar_compare_protocol import PREFIX as COMMON, checks as left_checks
from undefined_scalar_compare_right_protocol import checks as right_checks

PREFIX = COMMON.replace(r'pbin = EQUAL \/ pbin = LESS',
                        r'pbin = NOTEQUAL \/ pbin = LESSEQUAL')


def checks(program, path, name):
    if name == 'ne-missing-left':
        values = left_checks(program, path, 'equal-live-plain')
        old, new = 'BINARY_RIGHT EQUAL ', 'BINARY_RIGHT NOTEQUAL '
    else:
        values = right_checks(program, path, 'right-less-false-default')
        old, new = 'BINARY_RIGHT LESS ', 'BINARY_RIGHT LESSEQUAL '
    # Preserve the actual checked source program; only consumer atoms and the
    # changed != result predicate differ from the earlier complete conditions.
    result = [values[0]]
    for condition in values[1:]:
        condition = condition.replace(old, new)
        if name == 'ne-missing-left' and condition.startswith('S_compared = '):
            condition = condition.replace('KNOWN (PBOOL true)', 'KNOWN (PBOOL false)')
        result.append(condition)
    return result
