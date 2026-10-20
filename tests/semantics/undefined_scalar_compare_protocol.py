"""Source-reached scalar ==/< warnings, frozen NULL and current right CVs."""
import base64
import json

from undefined_spaceship_protocol import PREFIX as COMMON, text

PREFIX = COMMON.replace(
    'BINARY_RIGHT SPACESHIP poperand z',
    'BINARY_RIGHT pbin poperand z\n  -- if pbin = EQUAL \\/ pbin = LESS')


def checks(program, path, name):
    plain = name == 'equal-live-plain'
    op, line, initial = ('EQUAL', 10, 2) if plain else ('LESS', 8, 0)
    expected = 'H:1:10:1;R:1:1:1;END;' if plain else 'H:1:8;R:1:1:1;END;'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $us_seek(S_initial,0,1200)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$us_stage(S,0)', '$us_guard(S)',
        'S.TODO = ptask_original :: ptask_tail*',
        'ptask_original = BINARY_RIGHT ' + op + ' (VARIABLE ($ptascii("x")) z_left) ' + str(line),
        'S.RESULT = VARIABLE ($ptascii("right")) z_right',
        '$error_read_plan(S) = (perrorread)',
        '$error_read_state_shape(S,ptask_original,S.RESULT,S.BASE) = (perrorread)',
        'perrorread.NAME = $ptascii("x")', 'perrorread.LINE = ' + str(line),
        'perrorread.TASK = BINARY_RIGHT ' + op + ' (KNOWN PNULL) ' + str(line),
        'perrorread.RESULT = S.RESULT', '$error_read_valid(S,perrorread)',
        '$scalar_compare_read_other(S,perrorread)', '$spaceship_read_other(S,perrorread)',
        '$error_missing_operand(S,$error_read_operand(perrorread))',
        '$lookup(S.ENV,$ptascii("right")) = (n_right)',
        'S.STORE[n_right] = DEFINED (PINT ' + str(initial) + ')',
        '$heap_owners($heap_prune($heap_graph(S)),HCELL n_right) = 1',
        '$task_nodes(ERROR_READ_RESULT perrorread) = eps', 'S.BORROWEDREAD = eps',
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_warn = $prune_allocations($error_read_begin(S))',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = ' + str(line),
        'perrorcall.MESSAGE = $ptascii("Undefined variable $x")',
        'perrorcall.EVENT = WARNING ($ptascii("x")) ' + str(line),
        '$error_call_valid(S_warn,perrorcall)', 'S_warn.EVENTS = S.EVENTS', '$us_guard(S_warn)',
        'S_return_found = $us_seek(S_warn,2,1200)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]',
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)', '$us_guard(S_return)',
        'S_resume_found = $us_seek(S_return,3,1200)',
        r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)', '$scalar_compare_read_other(S_resume,perrorread)',
        '$lookup(S_resume.ENV,$ptascii("x")) = (n_x)', 'S_resume.STORE[n_x] = DEFINED (PINT 9)',
        '$lookup(S_resume.ENV,$ptascii("right")) = (n_right)',
        'S_resume.BORROWEDREAD = eps', 'S_resume.ERRORHANDLER = S.ERRORHANDLER', '$us_guard(S_resume)',
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$us_guard(S_compared)', 'S_done = $drive_steps(S_compared,4000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4000)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],4000) = S_done',
        '~$error_read_valid(S_resume,perrorread[.LINE = 999])',
        '~$error_read_valid(S_resume,perrorread[.NAME = $ptascii("right")])',
        '~$error_read_valid(S_resume,perrorread[.TASK = ptask_original])',
        '~$error_read_valid(S_resume,perrorread[.INPUT = VARIABLE ($ptascii("x")) z_right])',
        '~$error_read_valid(S_resume[.ORIGIN = eps],perrorread)',
        '~$error_call_valid(S_warn,perrorcall[.LEVEL = 8])',
        '~$error_call_valid(S_warn,perrorcall[.MESSAGE = eps])',
    ]
    if plain:
        values += [
            'S_resume.STORE[n_right] = DEFINED (PINT 0)', 'S_resume.EVENTS = S_return.EVENTS',
            'S_array_entry = S[.STORE = $set_cell(S.STORE,n_right,DEFINED (PARRAY 0))]',
            '$error_read_plan(S_array_entry) = eps',
            'S_missing_entry = S[.STORE = $set_cell(S.STORE,n_right,UNDEFINED)]',
            '$error_read_plan(S_missing_entry) = (perrorread)',
            'S_array = S_resume[.STORE = $set_cell(S_resume.STORE,n_right,DEFINED (PARRAY 0))]',
            '$error_read_valid(S_array,perrorread)', '~$scalar_compare_read_other(S_array,perrorread)',
            'PhpStep: S_array ~> S_array_refused',
            'S_array_refused = S_array[.TODO = eps][.COMPLETION = UNSUPPORTED "scalar comparison warning changed right operand"]',
            'S_removed = $unset_name(S_resume,$ptascii("right"))',
            '$error_read_valid(S_removed,perrorread)', '~$scalar_compare_read_other(S_removed,perrorread)',
            'PhpStep: S_removed ~> S_removed_refused',
            'S_removed_refused = S_removed[.TODO = eps][.COMPLETION = UNSUPPORTED "scalar comparison warning changed right operand"]',
        ]
    else:
        values += [
            'S_return.RESULT = KNOWN (PBOOL false)',
            'S_resume.STORE[n_right] = DEFINED pvalue_right', '$string_plain(pvalue_right) = PSTRING ($ptascii("0"))',
            'S_resume.EVENTS = S_return.EVENTS ++ [$error_default_event(S_return,WARNING ($ptascii("x")) ' + str(line) + ')]',
        ]
    return values
