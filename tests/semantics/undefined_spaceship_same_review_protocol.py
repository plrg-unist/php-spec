"""Same-CV first NULL, live references and source/pair separation."""
from undefined_scalar_compare_review_protocol import PREFIX as COMMON, checks as previous_checks, text

PREFIX = COMMON.replace(r'pbin = EQUAL \/ pbin = LESS', 'pbin = SPACESHIP')


def checks(program, path, name):
    target = name == 'peer-same-missing-spaceship-bound-to-target-reference'
    line = 9 if target else 12
    values = previous_checks(program, path, 'peer-plain-right-becomes-reference-string')
    result = [values[0]]
    for condition in values[1:]:
        if condition in ('$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
                         'S_resume.STORE[n_missing] = DEFINED (PINT 9)'):
            continue
        if condition == '$lookup(S.ENV,$ptascii("right")) = (n_original)':
            if target:
                result.append('$lookup(S.ENV,$ptascii("target")) = (n_original)')
            continue
        if condition == 'S.STORE[n_original] = DEFINED (PINT 0)':
            if target:
                result += ['S.STORE[n_original] = DEFINED pvalue_initial',
                           '$string_plain(pvalue_initial) = PSTRING ($ptascii("0"))']
            continue
        if condition == '$scalar_compare_read_other(S,perrorread)':
            condition = '~$scalar_compare_read_other(S,perrorread)'
        condition = condition.replace('BINARY_RIGHT EQUAL ', 'BINARY_RIGHT SPACESHIP ')
        condition = condition.replace('$ptascii("missing")', '$ptascii("x")')
        condition = condition.replace('$ptascii("right")', '$ptascii("x")')
        condition = condition.replace('Undefined variable $missing', 'Undefined variable $x')
        condition = condition.replace('$scalar_compare_read_other(', '$spaceship_read_other(')
        condition = condition.replace('scalar comparison warning changed right operand',
                                      'spaceship warning changed opposing scalar')
        if condition == 'PhpStep: S_without ~> S_denied':
            condition = 'PhpStep: S_without ~> S_without_restored'
        if condition.startswith('S_denied = S_without['):
            result.append('$spaceship_read_again(S_without,perrorread)')
            condition = 'S_without_restored = S_without[.TODO = perrorread.TASK :: ptask_resume*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]'
        condition = condition.replace(') 13', ') ' + str(line)).replace(' = 13', ' = ' + str(line))
        if condition.startswith('S_compared = '):
            condition = condition.replace('KNOWN (PBOOL false)', 'KNOWN (PINT $(-1))')
        if condition.startswith('perrorread_bad = '):
            condition = ('perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT SPACESHIP '
                         '(VARIABLE ($ptascii("x")) z_left) 999][.LINE = 999]'
                         '[.TASK = BINARY_RIGHT SPACESHIP (KNOWN PNULL) 999]')
        if target:
            condition = condition.replace('$lookup(S_resume.ENV,$ptascii("alias"))',
                                          '$lookup(S_resume.ENV,$ptascii("target"))')
        else:
            if condition == '~(n_original <- S.REFCELLS)':
                result.append('$lookup(S_resume.ENV,$ptascii("x")) = (n_original)')
            if condition == '$lookup(S_resume.ENV,$ptascii("x")) = (n_original)':
                continue
            condition = condition.replace('$heap_owners($heap_prune($heap_graph(S)),HCELL n_original) = 1',
                                          '$heap_owners($heap_prune($heap_graph(S)),HCELL n_original) = 0')
        if condition.startswith('$us_output('):
            expected = ('H:1:1:9;R:1:1;A:1:1;END;' if target else
                        'H:1:1:12;R:1:1:1;A:1;END;')
            condition = '$us_output(S_done.EVENTS) = ' + text(expected)
        result.append(condition)
    result += [
        '$lookup(S.ENV,$ptascii("x")) = eps',
        'perrorread.INPUT = VARIABLE perrorread.NAME z_right',
        '$scalar_compare_missing_pair(S,perrorread)',
        '~$scalar_compare_missing_pair(S_resume,perrorread)',
        '~$error_missing_operand(S_resume,$error_read_operand(perrorread))',
        '~$scalar_compare_missing_pair(S,perrorread_other)',
        'perrorread_right = perrorread[.TASK = perrorread.ORIGINAL][.RESULT = KNOWN PNULL]',
        '~$scalar_compare_missing_pair(S,perrorread_right)',
        '~$error_read_valid(S,perrorread_right)',
        'perrorread_forged = perrorread[.INPUT = VARIABLE ($ptascii("forged_rhs")) z_right][.RESULT = VARIABLE ($ptascii("forged_rhs")) z_right]',
        '$scalar_compare_missing_pair(S,perrorread_forged)',
        '~$error_read_valid(S,perrorread_forged)',
        '$error_read_plan(S[.RESULT = perrorread_forged.INPUT]) = eps',
        'S_defined = S_resume[.TODO = perrorread.ORIGINAL :: ptask_resume*][.RESULT = perrorread.INPUT][.BASE = perrorread.BASE]',
        '$us_guard(S_defined)', '$spaceship_read_other(S_defined,perrorread)',
        '~$scalar_compare_missing_pair(S_defined,perrorread)',
        '$error_read_plan(S_defined) = eps',
        '$scalar_compare_missing_pair(S_without,perrorread)',
        '$error_read_plan(S_without) = eps',
    ]
    return result
