"""Frozen NULL, scalar CV timing, authentic handlers and whole-state budgets."""
import base64
import json

PREFIX = r'''
dec $us_stage(pstate, nat) : bool
def $us_stage(S, 0) = true
  -- if $error_read_plan(S) = (perrorread)
  -- if perrorread.ORIGINAL = BINARY_RIGHT SPACESHIP poperand z
def $us_stage(S, 1) = true -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
def $us_stage(S, 2) = true -- if S.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask*
def $us_stage(S, 3) = true -- if S.TODO = (ERROR_READ_RESULT perrorread) :: ptask*
def $us_stage(S, n) = false -- otherwise
dec $us_seek(pstate, nat, nat) : pstate
def $us_seek(S, n_stage, n) = S
  -- if $us_stage(S, n_stage) \/ n = 0
def $us_seek(S, n_stage, n) = $us_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$us_stage(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $us_seek(S, n_stage, n) = S -- otherwise
dec $us_output(pevent*) : nat*
dec $us_event_output(pevent) : nat*
def $us_event_output(OUTPUT n*) = n*
def $us_event_output(pevent) = eps -- otherwise
def $us_output(eps) = eps
def $us_output(pevent :: pevent_tail*) = $us_event_output(pevent) ++ $us_output(pevent_tail*)
dec $us_guard(pstate) : bool
def $us_guard(S) = ($call_descriptors_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''


def text(value):
    return '$ptascii(' + json.dumps(value) + ')'


def checks(program, path, name):
    right = name == 'missing-right-constant'
    live = name == 'missing-left-cv'
    expected = 'H:2:10:1;R:' + ('1:1' if right else '0:1' if live else '-1:1') + ':9:0;END;'
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $us_seek(S_initial,0,1000)',
        'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$us_stage(S,0)', '$us_guard(S)',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        'perrorread.NAME = ' + text('x'), 'perrorread.LINE = 10',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*', 'S.RESULT = perrorread.INPUT',
        r'S.CURRENT = eps /\ S.FRAMES = eps', '$error_missing_operand(S,$error_read_operand(perrorread))',
        '$spaceship_read_other(S,perrorread)',
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_warn = $prune_allocations($error_read_begin(S))',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
        r'perrorcall.LEVEL = 2 /\ perrorcall.LINE = 10',
        'perrorcall.MESSAGE = $ptascii("Undefined variable $x")',
        'perrorcall.EVENT = WARNING ($ptascii("x")) 10', '$error_call_valid(S_warn,perrorcall)',
        'S_warn.EVENTS = S.EVENTS', '$us_guard(S_warn)',
        'S_return_found = $us_seek(S_warn,2,1000)',
        'S_return_found.COMPLETION = NORMAL \\/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]',
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        r'S_return.CURRENT = eps /\ S_return.FRAMES = eps', '$us_guard(S_return)',
        'S_resume_found = $us_seek(S_return,3,1000)',
        'S_resume_found.COMPLETION = NORMAL \\/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)', '$spaceship_read_other(S_resume,perrorread)',
        '$lookup(S_resume.ENV,' + text('x') + ') = (n_x)', 'S_resume.STORE[n_x] = DEFINED (PINT 9)',
        '$lookup(S_resume.ENV,' + text('y') + ') = (n_y)', 'S_resume.STORE[n_y] = DEFINED (PINT 0)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', '$us_guard(S_resume)',
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PINT ' + ('1' if right else '0' if live else '$(-1)') + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$us_guard(S_compared)',
        'S_done = $drive_steps(S_compared,4000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4000)',
        'S_pause = $drive_steps(S_resume,0)', 'S_pause = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_pause[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],4000) = S_done',
        '~$error_read_valid(S_resume,perrorread[.LINE = 999])',
        '~$error_read_valid(S_resume[.ORIGIN = eps],perrorread)',
        '~$error_call_valid(S_warn,perrorcall[.LEVEL = 8])',
        '~$error_call_valid(S_warn,perrorcall[.MESSAGE = eps])',
        r'~$spaceship_read_scalar(PARRAY 0) /\ ~$spaceship_read_scalar(POBJECT 0)',
        '~$spaceship_read_scalar(PUNDEFINED)',
    ]
    if live:
        values += ['perrorread.INPUT = VARIABLE ($ptascii("y")) z_y',
            'perrorread.TASK = BINARY_RIGHT SPACESHIP (KNOWN PNULL) 10',
            '$lookup(S.ENV,$ptascii("y")) = (n_y_initial)', 'S.STORE[n_y_initial] = DEFINED (PINT 2)',
            '$error_read_plan(S[.RESULT = KNOWN (PARRAY 0)]) = eps',
            '$error_read_plan(S[.RESULT = VARIABLE ($ptascii("forged")) z_y]) = eps',
            'S_changed = S_resume[.STORE = $set_cell(S_resume.STORE,n_y,DEFINED (PARRAY 0))]',
            '$error_read_valid(S_changed,perrorread)', '~$spaceship_read_other(S_changed,perrorread)',
            'PhpStep: S_changed ~> S_refused',
            'S_refused = S_changed[.TODO = eps][.COMPLETION = UNSUPPORTED "spaceship warning changed opposing scalar"]',
            'S_undefined = S_resume[.STORE = $set_cell(S_resume.STORE,n_y,UNDEFINED)]',
            '$error_read_valid(S_undefined,perrorread)', '~$spaceship_read_other(S_undefined,perrorread)',
            'PhpStep: S_undefined ~> S_undefined_refused',
            'S_undefined_refused = S_undefined[.TODO = eps][.COMPLETION = UNSUPPORTED "spaceship warning changed opposing scalar"]']
    return values
