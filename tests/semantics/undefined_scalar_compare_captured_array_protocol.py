"""Captured Boolean arrays, live-domain guards and stable source certificates."""
from undefined_spaceship_captured_array_protocol import checks as saved_checks
from undefined_spaceship_protocol import PREFIX as COMMON, text

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
    'BINARY_RIGHT pbin poperand z\n  -- if pbin = EQUAL \\/ pbin = GREATER')


def checks(program, path, name):
    equal = name == 'captured-equal-right-empty'
    line, operator = (16, 'EQUAL') if equal else (14, 'GREATER')
    original = ('BINARY_RIGHT EQUAL (VARIABLE ($ptascii("missing")) z_missing) 16'
                if equal else 'BINARY_RIGHT GREATER (KNOWN (PARRAY n_array)) 14')
    task = 'BINARY_RIGHT EQUAL (KNOWN PNULL) 16' if equal else original
    old_name = 'captured-left-assignment-empty' if equal else 'captured-right-runtime-array'
    source = saved_checks(program, path, old_name)
    exact = {
        'perrorread.ORIGINAL = ' + ('BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_array)) 16' if equal else
            'BINARY_RIGHT SPACESHIP (VARIABLE ($ptascii("missing")) z_missing) 13'):
            'perrorread.ORIGINAL = ' + original,
        ('perrorread.TASK = perrorread.ORIGINAL' if equal else
            'perrorread.TASK = BINARY_RIGHT SPACESHIP (KNOWN PNULL) 13'):
            'perrorread.TASK = ' + task,
        ('perrorread.INPUT = VARIABLE ($ptascii("missing")) z_missing' if equal else
            'perrorread.INPUT = KNOWN (PARRAY n_array)'):
            'perrorread.INPUT = ' + ('KNOWN (PARRAY n_array)' if equal else 'VARIABLE ($ptascii("missing")) z_missing'),
        ('perrorread.RESULT = KNOWN PNULL' if equal else 'perrorread.RESULT = perrorread.INPUT'):
            'perrorread.RESULT = ' + ('KNOWN (PARRAY n_array)' if equal else 'KNOWN PNULL'),
        '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_array) = 1':
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_array) = 2',
    }
    if not equal:
        exact.update({
            'perrorread.LINE = 13': 'perrorread.LINE = 14',
            'perrorcall.LINE = 13': 'perrorcall.LINE = 14',
            'perrorcall.EVENT = WARNING ($ptascii("missing")) 13':
                'perrorcall.EVENT = WARNING ($ptascii("missing")) 14',
        })
    values = [source[0]]  # Preserve the actual checked source program verbatim.
    for condition in source[1:]:
        if condition == '~$scalar_compare_read_array(S,perrorread)':
            continue
        if condition.startswith('perrorread_bad = '):
            value = ('perrorread_bad = perrorread[.ORIGINAL = ' + original.rsplit(' ', 1)[0] + ' 999]'
                     '[.TASK = ' + task.rsplit(' ', 1)[0] + ' 999][.LINE = 999]')
        elif condition.startswith('perrorread_foreign = '):
            value = ('perrorread_foreign = perrorread[.ORIGINAL = ' + original.replace(operator, 'BITXOR') + ']'
                     '[.TASK = ' + task.replace(operator, 'BITXOR') + ']')
        elif condition == '$scalar_compare_read_array(S,perrorread_foreign)':
            value = '~$scalar_compare_read_array(S,perrorread_foreign)'
        elif condition == '~$spaceship_read_array(S,perrorread_foreign)':
            value = condition
        elif condition in exact:
            value = exact[condition]
        else:
            value = condition.replace('$spaceship_read_array(', '$scalar_compare_read_array(')
            value = value.replace('$spaceship_read_other(', '$scalar_compare_read_other(')
            value = value.replace('$spaceship_read_again(', '$scalar_compare_read_again(')
            value = value.replace('$spaceship_checked_missing(', '$scalar_compare_checked_missing(')
            value = value.replace('UNSUPPORTED "spaceship warning changed opposing scalar"',
                'UNSUPPORTED "scalar comparison warning changed right operand"')
            value = value.replace('KNOWN (PINT ' + ('0' if equal else '$(-1)') + ')][.BASE',
                'KNOWN (PBOOL true)][.BASE')
            if condition.startswith('$us_output(S_done.EVENTS) = '):
                value = '$us_output(S_done.EVENTS) = ' + text(
                    'H:1:1:16:1;R:1:1:1:1:1:1;A:1:1:1;END;' if equal else
                    'H:1:1:14:1;R:1:1:1:1:1;END;')
        values.append(value)
    values += [
        '~$spaceship_read_array(S,perrorread)', '~$scalar_compare_missing_pair(S,perrorread)',
        '~$scalar_compare_checked_right_missing(S_resume,perrorread)',
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(line) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
    ]
    if equal:
        values += [
            'perrorread_fetch = perrorread[.ORIGINAL = BINARY_RIGHT EQUAL (VARIABLE ($ptascii("missing")) 999) 16]',
            '$scalar_compare_read_array(S,perrorread_fetch)', '~$error_read_valid(S,perrorread_fetch)',
        ]
    else:
        values += [
            '$lookup(S.ENV,$ptascii("saved")) = (n_saved)',
            'S.STORE[n_saved] = DEFINED (PARRAY n_array)',
            'S_resume.STORE[n_saved] = DEFINED (PARRAY n_empty)',
            'S_resume.ARRAYS[n_empty].ITEMS = eps', '$array_immutable(S_resume,n_empty)',
            'n_empty =/= n_array', 'S_done.STORE[n_saved] = DEFINED (PARRAY n_empty)',
            'n_pool_empty = $heap_count(HARRAY n_empty,$pools_nodes(S_resume.POOLS))',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HARRAY n_empty) = $(1 + n_pool_empty)',
            'perrorread_null = perrorread[.ORIGINAL = BINARY_RIGHT GREATER (KNOWN PNULL) 14][.TASK = BINARY_RIGHT GREATER (KNOWN PNULL) 14]',
            '$scalar_compare_read_other(S,perrorread_null)', '~$scalar_compare_read_array(S,perrorread_null)',
        ]
    return values
