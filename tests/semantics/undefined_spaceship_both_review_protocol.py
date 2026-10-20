"""Fresh right references and entry/resume separation for both-missing <=>."""
from undefined_scalar_compare_both_review_protocol import PREFIX as COMMON, checks as previous_checks, text

PREFIX = COMMON.replace(r'pbin = EQUAL \/ pbin = LESS', 'pbin = SPACESHIP')


def checks(program, path, name):
    target = name == 'peer-both-missing-spaceship-right-bound-to-target-reference'
    old_name = ('peer-both-missing-less-right-bound-to-target-reference' if target else
                'peer-both-missing-equal-right-reference-created')
    values = previous_checks(program, path, old_name)
    result = [values[0]]
    for condition in values[1:]:
        if target and condition in (
                '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
                'S_resume.STORE[n_missing] = DEFINED (PINT 9)'):
            continue
        condition = condition.replace('BINARY_RIGHT EQUAL ', 'BINARY_RIGHT SPACESHIP ')
        condition = condition.replace('BINARY_RIGHT LESS ', 'BINARY_RIGHT SPACESHIP ')
        condition = condition.replace('$scalar_compare_read_other(', '$spaceship_read_other(')
        condition = condition.replace('scalar comparison warning changed right operand',
                                      'spaceship warning changed opposing scalar')
        if condition == '~$scalar_compare_missing_pair(S,perrorread[.INPUT = VARIABLE ($ptascii("missing")) z_right][.RESULT = VARIABLE ($ptascii("missing")) z_right])':
            condition = condition.replace('$scalar_compare_missing_pair(', '$error_read_valid(')
        if target:
            condition = condition.replace(') 10', ') 9').replace(' = 10', ' = 9')
        if condition.startswith('perrorread_bad = '):
            condition = ('perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT SPACESHIP '
                         '(VARIABLE ($ptascii("missing")) z_left) 999][.LINE = 999]'
                         '[.TASK = BINARY_RIGHT SPACESHIP (KNOWN PNULL) 999]')
        if condition.startswith('S_compared = '):
            condition = condition.replace('KNOWN (PBOOL true)', 'KNOWN (PINT $(-1))')
        if condition == '$spaceship_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = eps':
            condition = condition.replace(' = eps', ' =/= (perrorread)')
        if condition.startswith('$us_output('):
            expected = ('H:1:1:9;R:1:1:1;A:1:1;END;' if target else
                        'H:1:1:13;R:1:1:1:1;A:1;END;')
            condition = '$us_output(S_done.EVENTS) = ' + text(expected)
        if not target and condition == 'S_resume.STORE[n_original] = DEFINED (PINT 0)':
            result += ['S_resume.STORE[n_original] = DEFINED pvalue_string',
                       '$string_plain(pvalue_string) = PSTRING ($ptascii("0"))']
            continue
        result.append(condition)
    if target:
        result += ['$lookup(S_resume.ENV,$ptascii("missing")) = eps',
                   '$error_missing_operand(S_resume,$error_read_operand(perrorread))']
    result += [
        '$spaceship_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread_right)',
        'perrorread_right =/= perrorread', '$error_read_valid(S,perrorread_right)',
        '~$scalar_compare_missing_pair(S,perrorread_right)',
        '~$spaceship_read_other(S,perrorread_right)',
        'S_defined = $unset_name(S_resume,$ptascii("missing"))[.TODO = perrorread.ORIGINAL :: ptask_resume*][.RESULT = perrorread.INPUT][.BASE = perrorread.BASE]',
        '$spaceship_read_other(S_defined,perrorread)',
        '~$scalar_compare_missing_pair(S_defined,perrorread)',
        '$error_read_plan(S_defined) = (perrorread)',
    ]
    return result
