"""Fresh >/>= fronts using complete source-reached scalar continuation checks."""
from undefined_scalar_compare_protocol import PREFIX as COMMON, checks as left_checks
from undefined_scalar_compare_right_protocol import checks as right_checks

PREFIX = COMMON.replace(r'pbin = EQUAL \/ pbin = LESS',
                        r'pbin = GREATER \/ pbin = GREATEREQUAL')


def checks(program, path, name):
    left = name == 'gt-missing-left'
    values = (left_checks(program, path, 'equal-live-plain') if left else
              right_checks(program, path, 'right-less-false-default'))
    old, new = (('BINARY_RIGHT EQUAL ', 'BINARY_RIGHT GREATER ') if left else
                ('BINARY_RIGHT LESS ', 'BINARY_RIGHT GREATEREQUAL '))
    # Keep the actual checked source program; adapt only the reached consumer
    # and its result. Diagnostic, ownership and complete raw-state checks remain.
    result = [values[0]]
    for condition in values[1:]:
        if left and condition == '$error_read_plan(S_missing_entry) = (perrorread)':
            result += [
                '$scalar_compare_right_read_shape(ptask_original,S.RESULT,S.BASE) = (perrorread_right)',
                '$error_read_plan(S_missing_entry) = (perrorread_right)',
            ]
            continue
        condition = condition.replace(old, new)
        if not left and condition.startswith('$scalar_compare_right_read_shape(BINARY_RIGHT '):
            result += [condition.replace(' = eps', ' = (perrorread_same)'),
                       '~$error_read_source(S,perrorread_same)',
                       '~$error_read_valid(S,perrorread_same)']
            continue
        if left and condition.startswith('S_removed_refused = S_removed['):
            result.append('~$scalar_compare_read_again(S_removed,perrorread)')
            condition = 'S_removed_refused = S_removed[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = perrorread.BASE]'
        if condition.startswith('S_compared = '):
            old_result, new_result = ('true', 'false') if left else ('false', 'true')
            condition = condition.replace('KNOWN (PBOOL ' + old_result + ')',
                                          'KNOWN (PBOOL ' + new_result + ')')
        result.append(condition)
    return result
