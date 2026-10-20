"""Reversed both-missing entry, fresh left references and resume separation."""
from undefined_scalar_compare_right_review_protocol import PREFIX as COMMON, checks as previous_checks, text

PREFIX = COMMON.replace(r'pbin = EQUAL \/ pbin = LESS',
                        r'pbin = GREATER \/ pbin = GREATEREQUAL')


def checks(program, path, name):
    target = name == 'peer-both-missing-greater-equal-left-bound-to-target-reference'
    op, line = ('GREATEREQUAL', 9) if target else ('GREATER', 13)
    values = previous_checks(program, path, 'peer-plain-left-becomes-reference-string')
    result = [values[0]]
    for condition in values[1:]:
        if condition == '$lookup(S.ENV,$ptascii("left")) = (n_original)':
            if target:
                result.append('$lookup(S.ENV,$ptascii("target")) = (n_original)')
            continue
        if not target and condition == 'S.STORE[n_original] = DEFINED (PINT 0)':
            continue
        if condition == '$scalar_compare_read_other(S,perrorread)':
            condition = '~$scalar_compare_read_other(S,perrorread)'
        if condition == '~$error_missing_operand(S,$error_read_operand(perrorread_left))':
            condition = '$error_missing_operand(S,$error_read_operand(perrorread_left))'
        if condition == '$error_read_plan(S_both) = (perrorread_left)':
            condition = '$error_read_plan(S_both) = (perrorread)'
        condition = condition.replace('BINARY_RIGHT EQUAL ', 'BINARY_RIGHT ' + op + ' ')
        condition = condition.replace(') 13', ') ' + str(line)).replace(' = 13', ' = ' + str(line))
        if condition.startswith(('S_compared = ', 'S_right_compared = ')):
            condition = condition.replace('KNOWN (PBOOL false)', 'KNOWN (PBOOL true)')
        if target:
            if condition in ('$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
                             'S_resume.STORE[n_missing] = DEFINED (PINT 9)',
                             '$string_plain(pvalue_string) = PSTRING ($ptascii("0"))'):
                continue
            condition = condition.replace('$lookup(S_resume.ENV,$ptascii("alias"))',
                                          '$lookup(S_resume.ENV,$ptascii("target"))')
            condition = condition.replace('S_resume.STORE[n_original] = DEFINED pvalue_string',
                                          'S_resume.STORE[n_original] = DEFINED (PINT 0)')
        else:
            if condition == '~(n_original <- S.REFCELLS)':
                result.append('$lookup(S_resume.ENV,$ptascii("left")) = (n_original)')
            if condition == '$lookup(S_resume.ENV,$ptascii("left")) = (n_original)':
                continue
            condition = condition.replace('$heap_owners($heap_prune($heap_graph(S)),HCELL n_original) = 1',
                                          '$heap_owners($heap_prune($heap_graph(S)),HCELL n_original) = 0')
        if condition == 'PhpStep: S_without ~> S_denied':
            result.append('$scalar_compare_read_again(S_without,perrorread)')
            condition = 'PhpStep: S_without ~> S_without_restored'
        if condition.startswith('S_denied = S_without['):
            condition = 'S_without_restored = S_without[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]'
        if condition.startswith('$us_output('):
            expected = ('H:1:1:9;R:1:1:1;A:1:1;END;' if target else
                        'H:1:1:13;R:1:1:1:1;A:1;END;')
            condition = '$us_output(S_done.EVENTS) = ' + text(expected)
        result.append(condition)
    result += [
        '$lookup(S.ENV,$ptascii("left")) = eps',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$scalar_compare_missing_pair(S,perrorread)',
        '~$scalar_compare_missing_pair(S_resume,perrorread)',
        '~$scalar_compare_missing_pair(S,perrorread_left)',
        '~$scalar_compare_read_other(S,perrorread_left)',
        '~$scalar_compare_missing_pair(S,perrorread_other)',
        'perrorread_same = perrorread[.INPUT = VARIABLE ($ptascii("left")) z_right][.NAME = $ptascii("left")]',
        '$scalar_compare_right_read_shape(perrorread_same.ORIGINAL,perrorread_same.INPUT,perrorread_same.BASE) = (perrorread_same)',
        '$scalar_compare_missing_pair(S,perrorread_same)',
        '~$error_read_source(S,perrorread_same)',
        '~$error_read_valid(S,perrorread_same)',
        'S_again = $unset_name($unset_name(S_resume,$ptascii("left")),$ptascii("missing"))',
        '$us_guard(S_again)', '$error_read_valid(S_again,perrorread)',
        '$scalar_compare_missing_pair(S_again,perrorread)',
        '~$scalar_compare_read_other(S_again,perrorread)',
        '$scalar_compare_read_again(S_again,perrorread)',
        '$error_read_plan(S_again) = eps',
        'PhpStep: S_again ~> S_again_restored',
        'S_again_restored = S_again[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
    ]
    if target:
        result += ['$lookup(S_resume.ENV,$ptascii("missing")) = eps',
                   '$error_missing_operand(S_resume,perrorread.INPUT)']
    return result
