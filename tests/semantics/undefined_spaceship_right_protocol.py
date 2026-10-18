"""Source-reached live-left CV reads, frozen missing right and ordered reporting."""
import base64
import json

from undefined_spaceship_protocol import PREFIX, text


def checks(program, path, name):
    plain = name == 'right-live-plain'
    line, left, initial, result = (10, 'y', 2, 0) if plain else (8, 'left', 0, 1)
    expected = 'H:2:10:1;R:0:1:9:0;END;' if plain else 'H:1:8;R:1:1:1;END;'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $us_seek(S_initial,0,1200)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$us_stage(S,0)', '$us_guard(S)',
        'S.TODO = ptask_original :: ptask_tail*', 'S.RESULT = VARIABLE ($ptascii("x")) z_right',
        'ptask_original = BINARY_RIGHT SPACESHIP (VARIABLE (' + text(left) + ') z_left) ' + str(line),
        '$error_read_plan(S) = (perrorread)',
        '$spaceship_right_read_shape(ptask_original,S.RESULT,S.BASE) = (perrorread)',
        '$error_read_state_shape(S,ptask_original,S.RESULT,S.BASE) =/= (perrorread)',
        'perrorread.NAME = $ptascii("x")', 'perrorread.TASK = ptask_original',
        'perrorread.RESULT = KNOWN PNULL', 'perrorread.LINE = ' + str(line),
        '$error_read_valid(S,perrorread)', '$spaceship_read_other(S,perrorread)',
        '$error_missing_operand(S,$error_read_operand(perrorread))',
        '$lookup(S.ENV,' + text(left) + ') = (n_left)', 'S.STORE[n_left] = DEFINED (PINT ' + str(initial) + ')',
        '$heap_owners($heap_prune($heap_graph(S)),HCELL n_left) = 1',
        '$task_nodes(ERROR_READ_RESULT perrorread) = eps', 'S.BORROWEDREAD = eps',
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
        'perrorcall.LINE = ' + str(line), 'perrorcall.LEVEL = 2',
        'perrorcall.MESSAGE = $ptascii("Undefined variable $x")',
        '$error_call_valid(S_warn,perrorcall)', 'S_warn.EVENTS = S.EVENTS', '$us_guard(S_warn)',
        'S_return_found = $us_seek(S_warn,2,1200)',
        'S_return_found.COMPLETION = NORMAL \\/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]',
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)', '$us_guard(S_return)',
        'S_resume_found = $us_seek(S_return,3,1200)',
        'S_resume_found.COMPLETION = NORMAL \\/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)', '$spaceship_read_other(S_resume,perrorread)',
        '$lookup(S_resume.ENV,$ptascii("x")) = (n_right)', 'S_resume.STORE[n_right] = DEFINED (PINT 9)',
        '$lookup(S_resume.ENV,' + text(left) + ') = (n_left)',
        'S_resume.BORROWEDREAD = eps', 'S_resume.ERRORHANDLER = S.ERRORHANDLER', '$us_guard(S_resume)',
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = ptask_original :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = perrorread.BASE]',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PINT ' + str(result) + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$us_guard(S_compared)', 'S_done = $drive_steps(S_compared,4000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4000)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],4000) = S_done',
        '~$error_read_valid(S_resume,perrorread[.LINE = 999])',
        '~$error_read_valid(S_resume,perrorread[.NAME = ' + text(left) + '])',
        '~$error_read_valid(S_resume,perrorread[.TASK = BINARY_RIGHT SPACESHIP (KNOWN PNULL) ' + str(line) + '])',
        '~$error_read_valid(S_resume[.ORIGIN = eps],perrorread)',
        '~$error_call_valid(S_warn,perrorcall[.LEVEL = 8])',
        '$spaceship_right_read_shape(BINARY_RIGHT SPACESHIP (VARIABLE ($ptascii("x")) z_left) ' + str(line) + ',VARIABLE ($ptascii("x")) z_right,S.BASE) = eps',
    ]
    if plain:
        values += [
            'S_resume.STORE[n_left] = DEFINED (PINT 0)', 'S_resume.EVENTS = S_return.EVENTS',
            'S_array = S_resume[.STORE = $set_cell(S_resume.STORE,n_left,DEFINED (PARRAY 0))]',
            '$error_read_valid(S_array,perrorread)', '~$spaceship_read_other(S_array,perrorread)',
            'PhpStep: S_array ~> S_array_refused',
            'S_array_refused = S_array[.TODO = eps][.COMPLETION = UNSUPPORTED "spaceship warning changed opposing scalar"]',
            'S_missing = S_resume[.STORE = $set_cell(S_resume.STORE,n_left,UNDEFINED)]',
            '$error_read_valid(S_missing,perrorread)', '~$spaceship_read_other(S_missing,perrorread)',
            'PhpStep: S_missing ~> S_missing_refused',
            'S_missing_refused = S_missing[.TODO = eps][.COMPLETION = UNSUPPORTED "spaceship warning changed opposing scalar"]',
        ]
    else:
        values += [
            'S_return.RESULT = KNOWN (PBOOL false)',
            'S_resume.STORE[n_left] = DEFINED pvalue_left', '$string_plain(pvalue_left) = PSTRING ($ptascii("0"))',
            'S_resume.EVENTS = S_return.EVENTS ++ [$error_default_event(S_return,WARNING ($ptascii("x")) ' + str(line) + ')]',
        ]
    return values
