"""Source-reached right-first missing warnings and current-left state checks."""
from undefined_scalar_compare_protocol import PREFIX as COMMON
from undefined_scalar_compare_right_protocol import checks as previous_checks

PREFIX = COMMON.replace(r'pbin = EQUAL \/ pbin = LESS',
                        r'pbin = GREATER \/ pbin = GREATEREQUAL')


def checks(program, path, name):
    plain = name == 'ge-both-init'
    previous = 'right-equal-live-plain' if plain else 'right-less-false-default'
    values = previous_checks(program, path, previous)
    omitted = {
        '$lookup(S.ENV,$ptascii("left")) = (n_left)',
        '$heap_owners($heap_prune($heap_graph(S)),HCELL n_left) = 1',
        '$error_read_plan(S_entry_array) = eps',
        '$error_read_state_shape(S_entry_missing,ptask_original,S.RESULT,S.BASE) = (perrorread_left)',
        '$error_read_plan(S_entry_missing) = (perrorread_left)',
    }
    result = [values[0]]
    for condition in values[1:]:
        if condition in omitted or condition.startswith((
                'S.STORE[n_left] = ', 'S_entry_array = ', 'S_entry_missing = ')):
            continue
        if condition == '$scalar_compare_read_other(S,perrorread)':
            condition = '~$scalar_compare_read_other(S,perrorread)'
        old, new = (('BINARY_RIGHT EQUAL ', 'BINARY_RIGHT GREATEREQUAL ') if plain
                    else ('BINARY_RIGHT LESS ', 'BINARY_RIGHT GREATER '))
        condition = condition.replace(old, new)
        if not plain and condition.startswith('S_compared = '):
            condition = condition.replace('KNOWN (PBOOL false)', 'KNOWN (PBOOL true)')
        result.append(condition)
    result += [
        '$lookup(S.ENV,$ptascii("left")) = eps',
        '$lookup(S.ENV,$ptascii("x")) = eps',
        '$error_missing_operand(S,VARIABLE ($ptascii("left")) z_left)',
        '$scalar_compare_missing_pair(S,perrorread)',
        '~$scalar_compare_missing_pair(S_resume,perrorread)',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_left) = 1',
        '$error_read_state_shape(S,ptask_original,S.RESULT,S.BASE) = (perrorread_left)',
        'perrorread_left.NAME = $ptascii("left")',
        '~$scalar_compare_missing_pair(S,perrorread_left)',
        'S_defined = $unset_name(S_resume,$ptascii("x"))[.TODO = ptask_original :: ptask_tail*][.RESULT = perrorread.INPUT][.BASE = perrorread.BASE]',
        '$scalar_compare_read_other(S_defined,perrorread)',
        '~$scalar_compare_missing_pair(S_defined,perrorread)',
        '$error_read_plan(S_defined) = (perrorread)',
        'S_again = $unset_name($unset_name(S_resume,$ptascii("left")),$ptascii("x"))',
        '$error_read_valid(S_again,perrorread)',
        '$scalar_compare_missing_pair(S_again,perrorread)',
        '~$scalar_compare_read_other(S_again,perrorread)',
        'PhpStep: S_again ~> S_denied',
        'S_denied = S_again[.TODO = eps][.COMPLETION = UNSUPPORTED "scalar comparison warning changed left operand"]',
    ]
    if plain:
        result += [
            'PhpStep: S_missing_right_restored ~> S_missing_right_compared',
            'S_missing_right_compared = S_missing_right_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        ]
    return result
