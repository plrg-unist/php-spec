"""Boolean captured snapshots and real throw unwind, preserving each program."""
import re

from undefined_spaceship_captured_array_review_protocol import PREFIX as COMMON, checks as old_checks

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
    'BINARY_RIGHT pbin poperand z\n  -- if pbin = EQUAL \\/ pbin = NOTEQUAL \\/ pbin = LESS \\/ pbin = LESSEQUAL \\/ pbin = GREATER \\/ pbin = GREATEREQUAL')


def checks(program, path, name):
    right = name == 'peer-captured-greater-equal-right-default'
    throwing = name == 'peer-captured-less-supplied-throw'
    previous = ('peer-captured-right-assignment-default' if right else
                'peer-captured-runtime-supplied-throw' if throwing else
                'peer-captured-left-returned-runtime')
    operator = 'GREATEREQUAL' if right else 'LESS' if throwing else 'EQUAL'
    original = old_checks(program, path, previous)
    values = [original[0]]
    for condition in original[1:]:
        if condition == '~$scalar_compare_read_array(S,perrorread)':
            values.append('~$spaceship_read_array(S,perrorread)')
            continue
        if condition == '$scalar_compare_read_array(S,perrorread_foreign)':
            values.append('~$spaceship_read_array(S,perrorread_foreign)')
            continue
        if condition.startswith('perrorread_foreign = '):
            condition = condition.replace('BINARY_RIGHT EQUAL', 'BINARY_RIGHT BITXOR')
        condition = condition.replace('SPACESHIP', operator)
        for old, new in (
            ('spaceship_right_read_shape', 'scalar_compare_right_read_shape'),
            ('spaceship_read_other', 'scalar_compare_read_other'),
            ('spaceship_read_array', 'scalar_compare_read_array'),
            ('spaceship_read_again', 'scalar_compare_read_again'),
            ('spaceship_checked_missing', 'scalar_compare_checked_missing')):
            condition = condition.replace('$' + old + '(', '$' + new + '(')
        if condition.startswith('S_compared = '):
            condition = condition.replace('KNOWN (PINT $(-1))', 'KNOWN (PBOOL true)').replace('KNOWN (PINT 0)', 'KNOWN (PBOOL true)')
        if right:
            condition = re.sub(r'\b18\b', '19', condition)
            condition = condition.replace('[PCFIELD 0]) = (17)', '[PCFIELD 0]) = (18)')
            condition = condition.replace('n_empty', 'n_rebound')
            condition = condition.replace('S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PBOOL false))]', 'S.ARRAYS[n_array].ITEMS = eps')
            condition = condition.replace('S_resume.ARRAYS[n_current].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]', 'S_resume.ARRAYS[n_current].ITEMS = [ENTRY (KINT 1) (DIRECT (PINT 7))]')
            condition = condition.replace('S_resume.ARRAYS[n_rebound].ITEMS = eps', 'S_resume.ARRAYS[n_rebound].ITEMS = [ENTRY (KINT 0) (DIRECT (PBOOL false))]')
            condition = condition.replace('S_done.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8))]', 'S_done.ARRAYS[n_array].ITEMS = [ENTRY (KINT 1) (DIRECT (PINT 8))]')
        values.append(condition)
    if right:
        values += ['S_resume.ARRAYS[n_current].NEXT = 2', 'S_done.ARRAYS[n_array].NEXT = 2']
    if not throwing:
        values += [
            'perrorread_null = perrorread' + ('[.INPUT = KNOWN PNULL][.RESULT = KNOWN PNULL]' if right else '[.ORIGINAL = BINARY_RIGHT EQUAL (KNOWN PNULL) 24][.TASK = BINARY_RIGHT EQUAL (KNOWN PNULL) 24]'),
            '$scalar_compare_read_other(S,perrorread_null)',
            '~$scalar_compare_read_array(S,perrorread_null)',
        ]
    return values
