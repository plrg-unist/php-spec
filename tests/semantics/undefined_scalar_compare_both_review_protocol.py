"""Both-missing reference creation with distinct entry and resume guards."""
from undefined_scalar_compare_review_protocol import PREFIX, checks as previous_checks, text


def checks(program, path, name):
    target = name == 'peer-both-missing-less-right-bound-to-target-reference'
    line = 10 if target else 13
    values = previous_checks(program, path, 'peer-plain-right-becomes-reference-string')
    result = [values[0]]
    for condition in values[1:]:
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
        if condition == '$error_read_plan(S_both) = eps':
            condition = '$error_read_plan(S_both) = (perrorread)'
        if condition.startswith('S_compared = '):
            condition = condition.replace('KNOWN (PBOOL false)', 'KNOWN (PBOOL true)')
        if target:
            condition = condition.replace('BINARY_RIGHT EQUAL ', 'BINARY_RIGHT LESS ')
            condition = condition.replace(') 13', ') 10').replace(' = 13', ' = 10')
            condition = condition.replace('$lookup(S_resume.ENV,$ptascii("alias"))',
                                          '$lookup(S_resume.ENV,$ptascii("target"))')
        else:
            if condition == '~(n_original <- S.REFCELLS)':
                result.append('$lookup(S_resume.ENV,$ptascii("right")) = (n_original)')
            if condition == '$lookup(S_resume.ENV,$ptascii("right")) = (n_original)':
                continue
            if condition == '$string_plain(pvalue_string) = PSTRING ($ptascii("0"))':
                continue
            condition = condition.replace('S_resume.STORE[n_original] = DEFINED pvalue_string',
                                          'S_resume.STORE[n_original] = DEFINED (PINT 0)')
            condition = condition.replace('$heap_owners($heap_prune($heap_graph(S)),HCELL n_original) = 1',
                                          '$heap_owners($heap_prune($heap_graph(S)),HCELL n_original) = 0')
        if condition.startswith('$us_output('):
            expected = ('H:1:1:10;R:1:1:1;A:1:1;END;' if target else
                        'H:1:1:13;R:1:1:1:1;A:1;END;')
            condition = '$us_output(S_done.EVENTS) = ' + text(expected)
        result.append(condition)
    result += [
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$lookup(S.ENV,$ptascii("right")) = eps',
        '$error_missing_operand(S,perrorread.INPUT)',
        '$scalar_compare_missing_pair(S,perrorread)',
        '~$scalar_compare_missing_pair(S_resume,perrorread)',
        'perrorread_reverse = perrorread[.ORIGINAL = BINARY_RIGHT GREATER (VARIABLE ($ptascii("missing")) z_left) ' + str(line) + '][.TASK = BINARY_RIGHT GREATER (KNOWN PNULL) ' + str(line) + ']',
        '$error_read_shape(perrorread_reverse.ORIGINAL,perrorread_reverse.INPUT,perrorread_reverse.BASE) = (perrorread_reverse)',
        '~$scalar_compare_missing_pair(S,perrorread_reverse)',
        '~$error_read_valid(S,perrorread_reverse)',
        '~$scalar_compare_missing_pair(S,perrorread[.INPUT = VARIABLE ($ptascii("missing")) z_right][.RESULT = VARIABLE ($ptascii("missing")) z_right])',
        'S_again = $unset_name($unset_name(S_resume,$ptascii("missing")),$ptascii("right"))',
        '$us_guard(S_again)', '$error_read_valid(S_again,perrorread)',
        '$scalar_compare_missing_pair(S_again,perrorread)',
        '~$scalar_compare_read_other(S_again,perrorread)',
        '$error_read_plan(S_again) = eps',
        'PhpStep: S_again ~> S_again_denied',
        'S_again_denied = S_again[.TODO = eps][.COMPLETION = UNSUPPORTED "scalar comparison warning changed right operand"]',
    ]
    return result
