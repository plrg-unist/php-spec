"""Actual right-first shared-CV entry and both captured NULLs."""
from undefined_scalar_compare_both_reversed_protocol import checks as entry_checks
from undefined_scalar_compare_second_reversed_protocol import PREFIX, checks as second_checks


def checks(program, path, name):
    entry = name == 'reversed-same-greater-equal-false'
    values = (entry_checks(program, path, 'ge-both-init') if entry else
              second_checks(program, path, 'second-reversed-greaterequal-false'))
    result = [values[0]]
    for condition in values[1:]:
        if entry:
            if 'perrorread_same' in condition:
                continue
            if condition == '~$error_read_valid(S_resume,perrorread[.NAME = $ptascii("left")])':
                condition = condition.replace('"left"', '"forged"')
            if condition in ('S_resume.STORE[n_right] = DEFINED (PINT 9)',
                             'PhpStep: S_missing_right_restored ~> S_missing_right_compared'):
                continue
            if condition.startswith('S_missing_right_compared = '):
                continue
            if condition in ('$scalar_compare_read_other(S_defined,perrorread)',
                             '$scalar_compare_read_other(S_missing_right,perrorread)'):
                condition = '~' + condition
            if condition == '~$scalar_compare_missing_pair(S_defined,perrorread)':
                condition = condition[1:]
            condition = condition.replace('$ptascii("left")', '$ptascii("x")')
            if condition == 'S_resume.STORE[n_left] = DEFINED (PINT 0)':
                result += ['S_resume.STORE[n_left] = DEFINED pvalue_left',
                           '$string_plain(pvalue_left) = PSTRING ($ptascii("0"))']
                continue
            if condition == 'S_resume.EVENTS = S_return.EVENTS':
                condition += ' ++ [$error_default_event(S_return,WARNING ($ptascii("x")) 10)]'
        else:
            if condition in ('$lookup(S_resume_1.ENV,$ptascii("right")) = (n_right)',
                             'S_resume_1.STORE[n_right] = DEFINED (PINT 9)'):
                continue
            if condition == '$error_read_valid(S_0,perrorread_left)':
                condition = '~' + condition
            condition = condition.replace('$ptascii("left")', '$ptascii("x")')
            condition = condition.replace('$ptascii("right")', '$ptascii("x")')
            condition = condition.replace('Undefined variable $left', 'Undefined variable $x')
            condition = condition.replace('Undefined variable $right', 'Undefined variable $x')
            if condition.startswith('$scalar_compare_right_read_shape(perrorread_forward.'):
                condition = condition.replace(' = (perrorread_forward)', ' = eps')
            for index in (1, 2):
                if condition.startswith('S_return_' + str(index) + '.RESULT = '):
                    condition = 'S_return_' + str(index) + '.RESULT = KNOWN (PBOOL true)'
                if condition.startswith('S_resume_' + str(index) + '.EVENTS = '):
                    condition = 'S_resume_' + str(index) + '.EVENTS = S_return_' + str(index) + '.EVENTS'
            if condition.startswith('$us_output('):
                condition = '$us_output(S_done.EVENTS) = $ptascii("H:1:1:10:1;H:1:1:10:2;R:1:1:1;END;")'
        result.append(condition)
    if entry:
        result += [
            'n_left = n_right', 'S_return.RESULT = KNOWN (PBOOL false)',
            '$scalar_compare_read_again(S_missing_right,perrorread)',
            '$error_read_plan(S_missing_right_restored) = (perrorread_second)',
            '$error_read_source(S_missing_right_restored,perrorread_second)',
            'perrorread_second.INPUT = KNOWN PNULL', 'perrorread_second.RESULT = KNOWN PNULL',
            'perrorread_second.TASK = BINARY_RIGHT GREATEREQUAL (KNOWN PNULL) 10',
            '~$scalar_compare_read_again(S_missing_right_restored,perrorread_second)',
        ]
    else:
        result += ['$lookup(S_resume_1.ENV,$ptascii("x")) = eps',
                   'perrorread_first.NAME = perrorread_second.NAME']
    return list(dict.fromkeys(result))
