"""Current Boolean array operands, pooled tables and unchanged scalar entry."""
from undefined_spaceship_array_resume_protocol import checks as array_checks
from undefined_spaceship_protocol import PREFIX as COMMON

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
    'BINARY_RIGHT pbin poperand z\n  -- if pbin = EQUAL \\/ pbin = NOTEQUAL \\/ pbin = LESS \\/ pbin = LESSEQUAL \\/ pbin = GREATER \\/ pbin = GREATEREQUAL')


def checks(program, path, name):
    greater = name == 'boolean-array-greater-nonempty'
    operator = 'GREATER' if greater else 'EQUAL'
    old_name = 'array-resume-missing-right-empty' if greater else 'array-resume-missing-left-empty'
    values = []
    for value in array_checks(program, path, old_name):
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
        if value == 'S.STORE[n_current] = DEFINED (PINT 2)':
            if greater:
                values.append('S.STORE[n_current] = DEFINED (PINT 0)')
            else:
                values += ['S.STORE[n_current] = DEFINED pvalue_initial',
                           '$string_plain(pvalue_initial) = PSTRING ($ptascii("0"))']
            continue
        if greater:
            if value == 'S_resume.ARRAYS[n_array].ITEMS = eps':
                value = 'S_resume.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PBOOL false))]'
            elif value == '$array_immutable(S_resume,n_array)':
                value = '~$array_immutable(S_resume,n_array)'
            elif value == 'S_done.ARRAYS[n_array].ITEMS = eps':
                value = 'S_done.ARRAYS[n_array] = S_resume.ARRAYS[n_array]'
        if value.startswith('S_compared = '):
            value = value.replace('KNOWN (PINT 0)', 'KNOWN (PBOOL true)')
        value = value.replace('spaceship warning changed opposing scalar',
                              'scalar comparison warning changed ' + ('left' if greater else 'right') + ' operand')
        values.append(value)
    values += [
        '~$spaceship_read_array(S_resume,perrorread)',
        '~$scalar_compare_checked_right_missing(S_resume,perrorread)',
        'ptask_second = BINARY_RIGHT ' + operator + ' (KNOWN PNULL) 10',
        '$error_read_shape(ptask_second,VARIABLE ($ptascii("' + ('left' if greater else 'right') + '")) 10,perrorread.BASE) = (perrorread_second)',
        '~$scalar_compare_read_array(S_resume,perrorread_second)',
    ]
    if greater:
        values += ['$(n_pool_owners > 0)',
                   '$heap_owners($heap_prune($heap_graph(S_done)),HARRAY n_array) = n_pool_owners']
    return values
