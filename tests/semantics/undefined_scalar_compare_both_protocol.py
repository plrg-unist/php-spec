"""Source-reached both-missing ingress and current-right continuation checks."""
from undefined_scalar_compare_protocol import PREFIX as COMMON, checks as previous_checks

PREFIX = COMMON.replace(r'pbin = EQUAL \/ pbin = LESS',
                        r'pbin = EQUAL \/ pbin = NOTEQUAL \/ pbin = LESS \/ pbin = LESSEQUAL')


def checks(program, path, name):
    plain = name == 'equal-both-init'
    previous = 'equal-live-plain' if plain else 'less-false-default'
    values = previous_checks(program, path, previous)
    # Preserve the actual program. A right cell is first allocated by the
    # handler, so pre-handler facts and controls cannot name that later cell.
    omitted = {
        '$lookup(S.ENV,$ptascii("right")) = (n_right)',
        '$heap_owners($heap_prune($heap_graph(S)),HCELL n_right) = 1',
        '$error_read_plan(S_array_entry) = eps',
        '$error_read_plan(S_missing_entry) = (perrorread)',
    }
    result = [values[0]]
    for condition in values[1:]:
        if condition in omitted or condition.startswith((
                'S.STORE[n_right] = ', 'S_array_entry = ', 'S_missing_entry = ')):
            continue
        if condition == '$scalar_compare_read_other(S,perrorread)':
            condition = '~$scalar_compare_read_other(S,perrorread)'
        if not plain:
            condition = condition.replace('BINARY_RIGHT LESS ', 'BINARY_RIGHT LESSEQUAL ')
        result.append(condition)
    result += [
        '$lookup(S.ENV,$ptascii("x")) = eps',
        '$lookup(S.ENV,$ptascii("right")) = eps',
        '$error_missing_operand(S,perrorread.INPUT)',
        '$scalar_compare_missing_pair(S,perrorread)',
        '~$scalar_compare_missing_pair(S_resume,perrorread)',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_right) = 1',
        '$scalar_compare_right_read_shape(ptask_original,S.RESULT,S.BASE) = (perrorread_right)',
        'perrorread_right =/= perrorread',
        '~$scalar_compare_missing_pair(S,perrorread_right)',
        '~$scalar_compare_read_other(S,perrorread_right)',
        '~$scalar_compare_missing_pair(S,perrorread[.INPUT = VARIABLE ($ptascii("x")) z_right])',
        'S_defined = $unset_name(S_resume,$ptascii("x"))[.TODO = ptask_original :: ptask_tail*][.RESULT = perrorread.INPUT][.BASE = perrorread.BASE]',
        '$scalar_compare_read_other(S_defined,perrorread)',
        '~$scalar_compare_missing_pair(S_defined,perrorread)',
        '$error_read_plan(S_defined) = (perrorread)',
    ]
    if not plain:
        result += [
            'S_without = $unset_name(S_resume,$ptascii("right"))',
            '$error_read_valid(S_without,perrorread)',
            '~$scalar_compare_read_other(S_without,perrorread)',
            'PhpStep: S_without ~> S_denied',
            'S_denied = S_without[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        ]
    return result
