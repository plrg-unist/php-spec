"""Captured scalar results, live aliases and exact raw Warning restoration."""
import base64
import json

from undefined_spaceship_protocol import PREFIX as COMMON, text

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
    'BINARY_RIGHT pbin poperand z\n  -- if pbin = EQUAL \\/ pbin = GREATER')


def checks(program, path, name):
    equal = name == 'captured-equal-right-zero'
    operator = 'EQUAL' if equal else 'GREATER'
    value = 'PINT 0' if equal else 'PSTRING ($ptascii("0"))'
    original = ('BINARY_RIGHT EQUAL (VARIABLE ($ptascii("missing")) z_missing) 14'
                if equal else 'BINARY_RIGHT GREATER (KNOWN (' + value + ')) 14')
    task = 'BINARY_RIGHT EQUAL (KNOWN PNULL) 14' if equal else original
    saved = 'PINT 9' if equal else 'PSTRING eps'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $us_seek(S_initial,0,1400)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$us_stage(S,0)', '$us_guard(S)',
        '$error_read_plan(S) = (perrorread)', '$error_read_source(S,perrorread)',
        '$error_read_valid(S,perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*', 'S.RESULT = perrorread.INPUT',
        '$error_read_shape(perrorread.ORIGINAL,S.RESULT,S.BASE) = (perrorread)',
        'perrorread.ORIGINAL = ' + original, 'perrorread.TASK = ' + task,
        'perrorread.INPUT = ' + ('KNOWN (' + value + ')' if equal else 'VARIABLE ($ptascii("missing")) z_missing'),
        'perrorread.RESULT = ' + ('perrorread.INPUT' if equal else 'KNOWN PNULL'),
        'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = 14',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$lookup(S.ENV,$ptascii("value")) = (n_value)',
        '$lookup(S.ENV,$ptascii("saved")) = (n_saved)', 'n_saved =/= n_value',
        'S.STORE[n_value] = DEFINED (' + value + ')', 'S.STORE[n_saved] = DEFINED (' + value + ')',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        '$scalar_compare_read_other(S,perrorread)', '~$scalar_compare_read_array(S,perrorread)',
        '~$spaceship_read_array(S,perrorread)', '~$scalar_compare_missing_pair(S,perrorread)',
        '$scalar_compare_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = eps',
        '$task_nodes(ERROR_READ_RESULT perrorread) = eps', '$base_nodes(perrorread.BASE) = eps',
        '$us_output(S.EVENTS) = eps', 'S.BORROWEDREAD = eps',
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]',
        'S_warn = $prune_allocations($error_read_begin(S))',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = 14',
        'perrorcall.MESSAGE = $ptascii("Undefined variable $missing")',
        'perrorcall.EVENT = WARNING ($ptascii("missing")) 14',
        '$error_call_valid(S_warn,perrorcall)', 'S_warn.EVENTS = S.EVENTS', '$us_guard(S_warn)',
        'S_return_found = $us_seek(S_warn,2,1400)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]',
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        'S_return.RESULT = KNOWN (PBOOL true)', '$us_guard(S_return)',
        'S_resume_found = $us_seek(S_return,3,1400)',
        r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)', '$scalar_compare_read_other(S_resume,perrorread)',
        '~$scalar_compare_read_array(S_resume,perrorread)',
        '~$scalar_compare_read_again(S_resume,perrorread)',
        '~$scalar_compare_checked_missing(S_resume,perrorread)',
        '~$scalar_compare_checked_right_missing(S_resume,perrorread)',
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
        'S_resume.STORE[n_missing] = DEFINED (PINT 9)',
        'S_resume.STORE[n_value] = DEFINED (PINT 7)',
        'S_resume.STORE[n_saved] = DEFINED (' + saved + ')',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', 'S_resume.BORROWEDREAD = eps',
        r'S_resume.CURRENT = eps /\ S_resume.FRAMES = eps', '$us_guard(S_resume)',
        '$us_output(S_resume.EVENTS) = $ptascii("H:1:1:14:1;")',
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS', 'S_compared.STORE = S_resume.STORE',
        '$us_guard(S_compared)',
        'S_done = $drive_steps(S_compared,4000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text('H:1:1:14:1;R:1:1:1:1:1;END;'), '$us_guard(S_done)',
        'S_done.STORE[n_missing] = DEFINED (PINT 9)', 'S_done.STORE[n_value] = DEFINED (PINT 7)',
        'S_done.STORE[n_saved] = DEFINED (' + saved + ')',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4000)',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_return,4000) = S_done',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],4000) = S_done',
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (14)',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (14)',
        '~$error_read_source(S[.CODE = eps],perrorread)', '$error_read_plan(S[.CODE = eps]) = eps',
        '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        'perrorread_bad = perrorread[.ORIGINAL = ' + original.rsplit(' ',1)[0] + ' 999][.TASK = ' + task.rsplit(' ',1)[0] + ' 999][.LINE = 999]',
        '$scalar_compare_read_other(S,perrorread_bad)', '~$error_read_valid(S,perrorread_bad)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_bad])',
        'perrorread_foreign = perrorread[.ORIGINAL = ' + original.replace(operator,'BITXOR') + '][.TASK = ' + task.replace(operator,'BITXOR') + ']',
        '~$error_read_source(S,perrorread_foreign)', '~$error_read_valid(S,perrorread_foreign)',
        '$error_read_plan(S[.TODO = perrorread_foreign.ORIGINAL :: ptask_tail*]) = eps',
        'perrorread_object = perrorread' + ('[.INPUT = KNOWN (POBJECT 0)][.RESULT = KNOWN (POBJECT 0)]' if equal else '[.ORIGINAL = BINARY_RIGHT GREATER (KNOWN (POBJECT 0)) 14][.TASK = BINARY_RIGHT GREATER (KNOWN (POBJECT 0)) 14]'),
        '$error_read_shape(perrorread_object.ORIGINAL,perrorread_object.INPUT,perrorread_object.BASE) = (perrorread_object)',
        '~$error_read_source(S,perrorread_object)', '~$error_read_valid(S,perrorread_object)',
        '$error_read_plan(S[.TODO = perrorread_object.ORIGINAL :: ptask_tail*][.RESULT = perrorread_object.INPUT]) = eps',
        'perrorread_null = perrorread' + ('[.INPUT = KNOWN PNULL][.RESULT = KNOWN PNULL]' if equal else '[.ORIGINAL = BINARY_RIGHT GREATER (KNOWN PNULL) 14][.TASK = BINARY_RIGHT GREATER (KNOWN PNULL) 14]'),
        '$error_read_source(S,perrorread_null)', '$error_read_valid(S,perrorread_null)',
        '$scalar_compare_read_other(S,perrorread_null)', '~$scalar_compare_read_array(S,perrorread_null)',
    ]
    if equal:
        values += [
            'perrorread_fetch = perrorread[.ORIGINAL = BINARY_RIGHT EQUAL (VARIABLE ($ptascii("missing")) 999) 14]',
            '$scalar_compare_read_other(S,perrorread_fetch)', '~$error_read_valid(S,perrorread_fetch)',
            'perrorread_name = perrorread[.ORIGINAL = BINARY_RIGHT EQUAL (VARIABLE ($ptascii("foreign")) z_missing) 14][.NAME = $ptascii("foreign")]',
            '$error_read_shape(perrorread_name.ORIGINAL,perrorread_name.INPUT,perrorread_name.BASE) = (perrorread_name)',
            '~$error_read_source(S,perrorread_name)',
        ]
    else:
        values += [
            'perrorread_name = perrorread[.INPUT = VARIABLE ($ptascii("foreign")) z_missing][.NAME = $ptascii("foreign")]',
            '$error_read_shape(perrorread_name.ORIGINAL,perrorread_name.INPUT,perrorread_name.BASE) = (perrorread_name)',
            '~$error_read_source(S,perrorread_name)',
        ]
    return values
