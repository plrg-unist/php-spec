"""Independent current-CV wrapper and old-alias ownership checks."""
import base64
import json

from undefined_spaceship_protocol import PREFIX, text


def checks(program, path, name):
    rebound = name == 'peer-reference-left-rebinds-new-cell'
    line = 12 if rebound else 13
    order = 0 if rebound else 1
    expected = ('H:1:1:12;R:1:1:1:1;A:1:1;END;' if rebound
                else 'H:1:1:13;R:1:1:1:1;A:1:1;END;')
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $us_seek(S_initial,0,1200)',
        'S = S_found[.COMPLETION = NORMAL]', '$us_stage(S,0)', '$us_guard(S)',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        '$spaceship_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        '$error_read_state_shape(S,perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) =/= (perrorread)',
        'perrorread.ORIGINAL = BINARY_RIGHT SPACESHIP (VARIABLE ($ptascii("left")) z_left) ' + str(line),
        'perrorread.TASK = perrorread.ORIGINAL', 'perrorread.RESULT = KNOWN PNULL',
        'perrorread.INPUT = VARIABLE ($ptascii("missing")) z_right',
        'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = ' + str(line),
        '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread_left)',
        'perrorread_left.NAME = $ptascii("left")',
        '~$error_missing_operand(S,$error_read_operand(perrorread_left))',
        '$task_nodes(ERROR_READ_RESULT perrorread) = eps',
        '$lookup(S.ENV,$ptascii("left")) = (n_original)',
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
        '$error_call_valid(S_warn,perrorcall)',
        'perrorcall.MESSAGE = $ptascii("Undefined variable $missing")',
        'perrorcall.LINE = ' + str(line), '$us_guard(S_warn)',
        'S_resume_found = $us_seek(S_warn,3,1200)',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]', '$us_stage(S_resume,3)',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_resume*',
        '$error_read_valid(S_resume,perrorread)', '$spaceship_read_other(S_resume,perrorread)',
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
        'S_resume.STORE[n_missing] = DEFINED (PINT 9)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', '$us_guard(S_resume)',
        'PhpStep: S_resume ~> S_restored',
        'S_restored.RESULT = KNOWN PNULL',
        'S_restored.TODO = perrorread.ORIGINAL :: ptask_resume*',
        'PhpStep: S_restored ~> S_compared',
        'S_compared.RESULT = KNOWN (PINT ' + str(order) + ')',
        'S_compared.STORE = S_resume.STORE', 'S_compared.ARRAYS = S_resume.ARRAYS',
        'S_compared.OBJECTS = S_resume.OBJECTS', 'S_compared.ALLOCATIONS = S_resume.ALLOCATIONS',
        'S_compared.EVENTS = S_resume.EVENTS', '$us_guard(S_compared)',
        'S_done = $drive_steps(S_compared,4000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4000)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],4000) = S_done',
        'perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT SPACESHIP (VARIABLE ($ptascii("left")) 999) ' + str(line) + '][.TASK = BINARY_RIGHT SPACESHIP (VARIABLE ($ptascii("left")) 999) ' + str(line) + ']',
        '$spaceship_right_read_shape(perrorread_bad.ORIGINAL,perrorread_bad.INPUT,perrorread_bad.BASE) = (perrorread_bad)',
        '~$error_read_valid(S_resume,perrorread_bad)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_bad])',
        '~$error_read_valid(S_resume[.ORIGIN = eps],perrorread)',
        'S_without = $unset_name(S_resume,$ptascii("left"))', '$us_guard(S_without)',
        '$error_read_valid(S_without,perrorread)', '~$spaceship_read_other(S_without,perrorread)',
        'PhpStep: S_without ~> S_denied',
        'S_denied = S_without[.TODO = (BINARY_RIGHT SPACESHIP (KNOWN PNULL) ' + str(line) + ') :: ptask_resume*][.RESULT = KNOWN PNULL][.BASE = perrorread.BASE]',
        'S_denied.EVENTS = S_resume.EVENTS',
    ]
    if rebound:
        values += [
            '$lookup(S.ENV,$ptascii("old")) = (n_original)',
            'S.STORE[n_original] = DEFINED (PINT 2)', 'n_original <- S.REFCELLS',
            '$heap_owners($heap_prune($heap_graph(S)),HCELL n_original) = 2',
            '$lookup(S_resume.ENV,$ptascii("left")) = (n_target)',
            '$lookup(S_resume.ENV,$ptascii("target")) = (n_target)', 'n_target =/= n_original',
            '$lookup(S_resume.ENV,$ptascii("old")) = (n_original)',
            'S_resume.STORE[n_original] = DEFINED (PINT 2)', 'n_target <- S_resume.REFCELLS',
            'S_resume.STORE[n_target] = DEFINED (PINT 0)',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_original) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_target) = 2',
            '$lookup(S_done.ENV,$ptascii("left")) = (n_target)',
            'S_done.STORE[n_original] = DEFINED (PINT 2)',
            'S_done.STORE[n_target] = DEFINED pvalue_after',
            '$string_plain(pvalue_after) = PSTRING ($ptascii("after"))',
        ]
    else:
        values += [
            'S.STORE[n_original] = DEFINED (PINT 0)', '~(n_original <- S.REFCELLS)',
            '$heap_owners($heap_prune($heap_graph(S)),HCELL n_original) = 1',
            '$lookup(S_resume.ENV,$ptascii("left")) = (n_original)',
            '$lookup(S_resume.ENV,$ptascii("alias")) = (n_original)',
            'n_original <- S_resume.REFCELLS',
            'S_resume.STORE[n_original] = DEFINED pvalue_string',
            '$string_plain(pvalue_string) = PSTRING ($ptascii("0"))',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_original) = 2',
            'S_done.STORE[n_original] = DEFINED (PINT 5)',
        ]
    return values
