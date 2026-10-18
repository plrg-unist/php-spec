"""Independent reference-rebinding and captured-value spaceship state checks."""
import base64
import json

from undefined_spaceship_protocol import PREFIX, text


def checks(program, path, name):
    rebound = name == 'peer-null-string-reference-rebind'
    line = 14 if rebound else 10
    expected = ('H:1:1:14;R:1:1:1:1;A:1:1;END;' if rebound
                else 'H:1:1:1:10;R:1:1:1;END;')
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $us_seek(S_initial,0,1200)',
        'S = S_found[.COMPLETION = NORMAL]', '$us_stage(S,0)', '$us_guard(S)',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        'perrorread.NAME = ' + text('missing'), 'perrorread.LINE = ' + str(line),
        'perrorread.TASK = BINARY_RIGHT SPACESHIP (KNOWN PNULL) ' + str(line),
        '$lookup(S.ENV,' + text('right') + ') = (n_original)',
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
        '$error_call_valid(S_warn,perrorcall)',
        'perrorcall.MESSAGE = ' + text('Undefined variable $missing'),
        'perrorcall.LINE = ' + str(line), '$us_guard(S_warn)',
        'S_resume_found = $us_seek(S_warn,3,1200)',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]', '$us_stage(S_resume,3)',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_resume*',
        '$error_read_valid(S_resume,perrorread)', '$spaceship_read_other(S_resume,perrorread)',
        '$lookup(S_resume.ENV,' + text('missing') + ') = (n_missing)',
        'S_resume.STORE[n_missing] = DEFINED (PINT 9)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', '$us_guard(S_resume)',
        'PhpStep: S_resume ~> S_restored',
        'S_restored.TODO = (BINARY_RIGHT SPACESHIP (KNOWN PNULL) ' + str(line) + ') :: ptask_resume*',
        'PhpStep: S_restored ~> S_compared', 'S_compared.RESULT = KNOWN (PINT $(-1))',
        'S_compared.STORE = S_resume.STORE', 'S_compared.OBJECTS = S_resume.OBJECTS',
        'S_compared.ARRAYS = S_resume.ARRAYS', 'S_compared.ALLOCATIONS = S_resume.ALLOCATIONS',
        'S_compared.EVENTS = S_resume.EVENTS', '$us_guard(S_compared)',
        'S_done = $drive_steps(S_compared,4000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4000)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],4000) = S_done',
        '~$error_read_valid(S_resume,perrorread[.LINE = 999])',
        '~$error_read_valid(S_resume[.ORIGIN = eps],perrorread)',
        '~$error_call_valid(S_warn,perrorcall[.LEVEL = 8])',
        '~$error_call_valid(S_warn,perrorcall[.MESSAGE = eps])',
    ]
    if rebound:
        values += [
            'perrorread.INPUT = VARIABLE ($ptascii("right")) z_right',
            'perrorread.RESULT = VARIABLE ($ptascii("right")) z_right',
            '$lookup(S.ENV,$ptascii("old")) = (n_original)',
            'S.STORE[n_original] = DEFINED (PINT 2)', 'n_original <- S.REFCELLS',
            '$heap_owners($heap_prune($heap_graph(S)),HCELL n_original) = 2',
            '$task_nodes(ERROR_READ_RESULT perrorread) = eps',
            '$lookup(S_resume.ENV,$ptascii("right")) = (n_target)',
            '$lookup(S_resume.ENV,$ptascii("target")) = (n_target)', 'n_target =/= n_original',
            '$lookup(S_resume.ENV,$ptascii("old")) = (n_original)',
            'S_resume.STORE[n_original] = DEFINED (PINT 2)', 'n_target <- S_resume.REFCELLS',
            'S_resume.STORE[n_target] = DEFINED pvalue_target',
            '$string_plain(pvalue_target) = PSTRING ($ptascii("0"))',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_original) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_target) = 2',
            'S_restored.RESULT = VARIABLE ($ptascii("right")) z_right',
            '$lookup(S_done.ENV,$ptascii("right")) = (n_target)',
            '$lookup(S_done.ENV,$ptascii("old")) = (n_original)',
            'S_done.STORE[n_original] = DEFINED (PINT 2)',
            'S_done.STORE[n_target] = DEFINED pvalue_after',
            '$string_plain(pvalue_after) = PSTRING ($ptascii("after"))',
            '$heap_owners($heap_prune($heap_graph(S_done)),HCELL n_original) = 1',
            '$heap_owners($heap_prune($heap_graph(S_done)),HCELL n_target) = 2',
        ]
    else:
        values += [
            'perrorread.INPUT = KNOWN (PINT 1)', 'perrorread.RESULT = KNOWN (PINT 1)',
            'S.STORE[n_original] = DEFINED (PINT 1)',
            '$lookup(S_resume.ENV,$ptascii("right")) = (n_original)',
            'S_resume.STORE[n_original] = DEFINED (PINT 0)',
            'S_restored.RESULT = KNOWN (PINT 1)',
            '$task_nodes(ERROR_READ_RESULT perrorread) = eps',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_original) = 1',
        ]
    return values
