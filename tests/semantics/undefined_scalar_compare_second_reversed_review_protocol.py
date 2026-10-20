"""Independent physical right-first records across two complete Warnings."""
from undefined_spaceship_second_review_protocol import PREFIX as COMMON, checks as previous_checks

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
                        'BINARY_RIGHT pbin poperand z\n  -- if pbin = GREATER \\/ pbin = GREATEREQUAL')


def physical_names(condition):
    condition = condition.replace('"left"', '"__first__"').replace('"right"', '"left"').replace('"__first__"', '"right"')
    condition = condition.replace('variable $left', 'variable $__first__').replace('variable $right', 'variable $left').replace('variable $__first__', 'variable $right')
    return condition.replace('z_left', 'z_first').replace('z_right', 'z_left').replace('z_first', 'z_right')


def checks(program, path, name):
    target = name == 'peer-second-warning-greaterequal-unset-left-target-reference'
    previous = ('peer-second-warning-spaceship-unset-right-target-reference' if target else
                'peer-second-warning-spaceship-fresh-reference')
    op, line, boolean = ('GREATEREQUAL', 13, 'true') if target else ('GREATER', 16, 'false')
    values = previous_checks(program, path, previous)
    # Keep the actual parsed program. The inherited steps/budgets still run both
    # handlers; only the physical operand names and source-oriented records differ.
    result = [values[0]]
    for original in values[1:]:
        condition = physical_names(original)
        condition = condition.replace('BINARY_RIGHT SPACESHIP ', 'BINARY_RIGHT ' + op + ' ')
        condition = condition.replace('$spaceship_read_other(', '$scalar_compare_read_other(')
        condition = condition.replace('$spaceship_read_again(', '$scalar_compare_read_again(')
        condition = condition.replace('$spaceship_right_read_shape(', '$scalar_compare_right_read_shape(')
        condition = condition.replace('perrorread_right', 'perrorread_left')
        reason = ('scalar comparison warning changed right operand' if original.startswith('S_wrong_denied = ')
                  else 'scalar comparison warning changed left operand')
        condition = condition.replace('spaceship warning changed opposing scalar', reason)
        if original.startswith('ptask_original = '):
            condition = 'ptask_original = BINARY_RIGHT ' + op + ' (VARIABLE ($ptascii("left")) z_left) ' + str(line)
        elif original == 'S.RESULT = VARIABLE ($ptascii("right")) z_right':
            condition = 'S.RESULT = VARIABLE ($ptascii("right")) z_right'
        elif original == '$error_read_shape(ptask_original,S.RESULT,S.BASE) = (perrorread_first)':
            condition = '$scalar_compare_right_read_shape(ptask_original,S.RESULT,S.BASE) = (perrorread_first)'
        elif original.startswith('perrorread_first.TASK = '):
            condition = 'perrorread_first.TASK = ptask_original'
        elif original == 'perrorread_first.RESULT = S.RESULT':
            condition = 'perrorread_first.RESULT = KNOWN PNULL'
        elif original == '$error_missing_operand(S_first_resume,perrorread_first.INPUT)':
            condition = '$error_missing_operand(S_first_resume,VARIABLE ($ptascii("left")) z_left)'
        elif original.startswith('S_first_restored.RESULT = '):
            condition = 'S_first_restored.RESULT = KNOWN PNULL'
        elif original == 'perrorread_second.TASK = perrorread_first.TASK':
            condition = 'perrorread_second.TASK = BINARY_RIGHT ' + op + ' (KNOWN PNULL) ' + str(line)
        elif original == 'perrorread_second.INPUT = perrorread_first.INPUT':
            condition = 'perrorread_second.INPUT = KNOWN PNULL'
        elif original.startswith('S_compared = '):
            condition = condition.replace('KNOWN (PINT 0)', 'KNOWN (PBOOL ' + boolean + ')')
        elif original.startswith('S_wrong_denied = '):
            condition = 'S_wrong_denied = S_wrong[.TODO = perrorread_left.TASK :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = perrorread_left.BASE]'
        elif original.startswith('perrorread_bad = '):
            condition = 'perrorread_bad = perrorread_first[.ORIGINAL = BINARY_RIGHT ' + op + ' (VARIABLE ($ptascii("left")) z_left) 999][.TASK = BINARY_RIGHT ' + op + ' (VARIABLE ($ptascii("left")) z_left) 999][.LINE = 999]'
        elif original == '$error_read_shape(perrorread_bad.ORIGINAL,perrorread_bad.INPUT,perrorread_bad.BASE) = (perrorread_bad)':
            condition = '$scalar_compare_right_read_shape(perrorread_bad.ORIGINAL,perrorread_bad.INPUT,perrorread_bad.BASE) = (perrorread_bad)'
        elif original.startswith('perrorread_second_bad = '):
            condition = 'perrorread_second_bad = perrorread_second[.ORIGINAL = BINARY_RIGHT ' + op + ' (VARIABLE ($ptascii("left")) z_left) 999][.TASK = BINARY_RIGHT ' + op + ' (KNOWN PNULL) 999][.LINE = 999]'
        elif original.startswith('perrorread_equal = '):
            condition = 'perrorread_equal = perrorread_first[.ORIGINAL = BINARY_RIGHT EQUAL (VARIABLE ($ptascii("left")) z_left) ' + str(line) + '][.TASK = BINARY_RIGHT EQUAL (VARIABLE ($ptascii("left")) z_left) ' + str(line) + ']'
        elif original == '$error_read_shape(perrorread_equal.ORIGINAL,perrorread_equal.INPUT,perrorread_equal.BASE) = (perrorread_equal)':
            condition = '$scalar_compare_right_read_shape(perrorread_equal.ORIGINAL,perrorread_equal.INPUT,perrorread_equal.BASE) = (perrorread_equal)'
        elif original == '$spaceship_right_read_shape(ptask_original,S.RESULT,S.BASE) = (perrorread_right)':
            condition = '$error_read_shape(ptask_original,S.RESULT,S.BASE) = (perrorread_left)'
        result.append(condition)
    result += [
        'perrorread_nonnull = perrorread_second[.INPUT = KNOWN (POBJECT 0)][.RESULT = KNOWN (POBJECT 0)]',
        '$error_read_shape(perrorread_nonnull.ORIGINAL,perrorread_nonnull.INPUT,perrorread_nonnull.BASE) = (perrorread_nonnull)',
        '~$error_read_valid(S_first_restored,perrorread_nonnull)',
        '~$error_read_source(S_first_restored,perrorread_nonnull)',
        'perrorread_left_line = perrorread_second[.ORIGINAL = BINARY_RIGHT ' + op + ' (VARIABLE ($ptascii("left")) 999) ' + str(line) + ']',
        '$error_read_shape(perrorread_left_line.ORIGINAL,perrorread_left_line.INPUT,perrorread_left_line.BASE) = (perrorread_left_line)',
        '~$error_read_valid(S_first_restored,perrorread_left_line)',
        '~$error_read_source(S_first_restored,perrorread_left_line)',
        'S_first_restored.ORIGIN = (porigin_second)',
        '$code_expression_at_source(S_first_restored,porigin_second,[PCFIELD 0]) = (z_left)',
        '$code_expression_at_source(S_first_restored,porigin_second,[PCFIELD 1]) = (' + str(line) + ')',
    ]
    return result
