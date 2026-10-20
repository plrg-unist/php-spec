"""Boolean predicates over the independently reached array reference/COW fronts."""
from undefined_spaceship_array_resume_review_protocol import PREFIX as COMMON, checks as array_checks

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
    'BINARY_RIGHT pbin poperand z\n  -- if pbin = EQUAL \\/ pbin = NOTEQUAL \\/ pbin = LESS \\/ pbin = LESSEQUAL \\/ pbin = GREATER \\/ pbin = GREATEREQUAL')


def checks(program, path, name):
    greater = name == 'peer-boolean-array-greater-rebound-reference-default'
    operator = 'GREATER' if greater else 'EQUAL'
    old_name = ('peer-array-right-missing-rebound-reference-default' if greater else
                'peer-array-left-missing-fresh-reference-cow')
    old = array_checks(program, path, old_name)
    if greater:
        start = old.index('$spaceship_checked_missing(S_removed,perrorread)')
        old = old[:start] + [
            '$spaceship_read_again(S_removed,perrorread)',
            '~$spaceship_checked_missing(S_removed,perrorread)',
            'PhpStep: S_removed ~> S_removed_restored',
            'S_removed_restored = S_removed[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
            '$error_read_plan(S_removed_restored) = (perrorread_second)',
            'perrorread_second.NAME = $ptascii("left")',
            'perrorread_second.INPUT = KNOWN PNULL',
            'perrorread_second.RESULT = KNOWN PNULL',
        ]
    values = []
    for value in old:
        if value.startswith('S_initial = $php_run('):
            values.append(value)
            continue
        value = value.replace('BINARY_RIGHT SPACESHIP', 'BINARY_RIGHT ' + operator)
        value = value.replace('$spaceship_right_read_shape', '$scalar_compare_right_read_shape')
        value = value.replace('$spaceship_read_other', '$scalar_compare_read_other')
        value = value.replace('$spaceship_read_array(', '$scalar_compare_read_array(')
        value = value.replace('$spaceship_read_again', '$scalar_compare_read_again')
        value = value.replace('$spaceship_checked_missing', '$scalar_compare_checked_missing')
        if 'perrorread_equal' in value:
            value = value.replace('perrorread_equal', 'perrorread_space')
            value = value.replace('BINARY_RIGHT EQUAL', 'BINARY_RIGHT SPACESHIP')
        if value.startswith('S_compared = '):
            value = value.replace('KNOWN (PINT ' + ('1' if greater else '0') + ')',
                                  'KNOWN (PBOOL true)')
        values.append(value)
    values += [
        '~$spaceship_read_array(S_resume,perrorread)',
        '~$scalar_compare_checked_right_missing(S_resume,perrorread)',
        '~$scalar_compare_read_array(S_resume,perrorread_second)',
    ]
    return values
