"""Initial array roots, current rebinding, exact restore and compiled authority."""
import base64
import json

from undefined_spaceship_protocol import PREFIX as COMMON, text

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
    'BINARY_RIGHT pbin poperand z\n  -- if pbin = SPACESHIP \\/ pbin = EQUAL \\/ pbin = NOTEQUAL \\/ pbin = LESS \\/ pbin = LESSEQUAL \\/ pbin = GREATER \\/ pbin = GREATEREQUAL')


def checks(program, path, name):
    greater = name == 'initial-array-greater-current-string'
    operator, current = ('GREATER', 'left') if greater else ('EQUAL', 'right')
    left, right = ('left', 'missing') if greater else ('missing', 'right')
    original = 'BINARY_RIGHT ' + operator + ' (VARIABLE (' + text(left) + ') z_left) 10'
    task = original if greater else 'BINARY_RIGHT ' + operator + ' (KNOWN PNULL) 10'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $us_seek(S_initial,0,1200)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$us_stage(S,0)', '$us_guard(S)',
        'S.TODO = ptask_original :: ptask_tail*', 'ptask_original = ' + original,
        'S.RESULT = VARIABLE (' + text(right) + ') z_right',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        '$' + ('scalar_compare_right_read_shape' if greater else 'error_read_shape') + '(ptask_original,S.RESULT,S.BASE) = (perrorread)',
        'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = 10',
        'perrorread.TASK = ' + task, 'perrorread.RESULT = ' + ('KNOWN PNULL' if greater else 'S.RESULT'),
        '$lookup(S.ENV,' + text(current) + ') = (n_current)',
        'S.STORE[n_current] = DEFINED (PARRAY n_initial)', '(HARRAY n_initial) <- S.ALLOCATIONS',
        'S.ARRAYS[n_initial].ITEMS = ' + ('eps' if greater else '[ENTRY (KINT 0) (DIRECT (PBOOL false))]'),
        ('' if greater else '~') + '$array_immutable(S,n_initial)',
        'n_initial_pool = $heap_count(HARRAY n_initial,$pools_nodes(S.POOLS))',
        '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_initial) = $(1 + n_initial_pool)',
        '$heap_owners($heap_prune($heap_graph(S)),HCELL n_current) = 1',
        '~(n_current <- S.REFCELLS)', '$lookup(S.ENV,$ptascii("missing")) = eps',
        '~$scalar_compare_read_other(S,perrorread)', '$scalar_compare_read_array(S,perrorread)',
        '~$spaceship_read_array(S,perrorread)',
        '$spaceship_read_array_operand(S,VARIABLE (' + text(current) + ') 10)',
        '~$spaceship_read_array_operand(S,KNOWN (PARRAY n_initial))',
        '$task_nodes(ERROR_READ_RESULT perrorread) = eps', 'S.BORROWEDREAD = eps',
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_warn = $prune_allocations($error_read_begin(S))',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = 10',
        'perrorcall.MESSAGE = $ptascii("Undefined variable $missing")',
        'perrorcall.EVENT = WARNING ($ptascii("missing")) 10',
        '$error_call_valid(S_warn,perrorcall)', 'S_warn.EVENTS = S.EVENTS', '$us_guard(S_warn)',
        'S_return_found = $us_seek(S_warn,2,1200)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]',
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        'S_return.RESULT = KNOWN (PBOOL true)', '$us_guard(S_return)',
        'S_resume_found = $us_seek(S_return,3,1200)',
        r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)',
        '$lookup(S_resume.ENV,' + text(current) + ') = (n_current)',
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
        'S_resume.STORE[n_missing] = DEFINED (PINT 9)',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_current) = 1',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HARRAY n_initial) = n_initial_pool',
        '~$scalar_compare_read_again(S_resume,perrorread)',
        '~$scalar_compare_checked_missing(S_resume,perrorread)',
        '~$scalar_compare_checked_right_missing(S_resume,perrorread)',
        'S_resume.EVENTS = S_return.EVENTS', 'S_resume.ERRORHANDLER = S.ERRORHANDLER',
        r'S_resume.CURRENT = eps /\ S_resume.FRAMES = eps', 'S_resume.BORROWEDREAD = eps', '$us_guard(S_resume)',
    ]
    if greater:
        values += ['S_resume.STORE[n_current] = DEFINED pvalue_current',
                   '$string_plain(pvalue_current) = PSTRING ($ptascii("0"))',
                   '$scalar_compare_read_other(S_resume,perrorread)',
                   '~$scalar_compare_read_array(S_resume,perrorread)']
    else:
        values += ['S_resume.STORE[n_current] = DEFINED (PARRAY n_array)',
                   '(HARRAY n_array) <- S_resume.ALLOCATIONS', 'n_array =/= n_initial',
                   'S_resume.ARRAYS[n_array].ITEMS = eps', '$array_immutable(S_resume,n_array)',
                   'n_pool = $heap_count(HARRAY n_array,$pools_nodes(S_resume.POOLS))',
                   '$heap_owners($heap_prune($heap_graph(S_resume)),HARRAY n_array) = $(1 + n_pool)',
                   '~$scalar_compare_read_other(S_resume,perrorread)',
                   '$scalar_compare_read_array(S_resume,perrorread)']
    values += [
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS', 'S_compared.ARRAYS = S_resume.ARRAYS', '$us_guard(S_compared)',
        'S_done = $drive_steps(S_compared,4000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text('H:1:1:10:1;R:1:1:1:1;A:1:1;END;'), '$us_guard(S_done)',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        '$lookup(S_done.ENV,' + text(current) + ') = (n_current)',
        '$heap_owners($heap_prune($heap_graph(S_done)),HARRAY n_initial) = n_initial_pool',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4000)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_return,4000) = S_done',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_initial)]',
        '~$scalar_compare_read_array(S_dead,perrorread)', '$error_read_plan(S_dead) = eps',
        'perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT ' + operator + ' (VARIABLE (' + text(left) + ') z_left) 999][.TASK = BINARY_RIGHT ' + operator + ' (' + ('VARIABLE (' + text(left) + ') z_left' if greater else 'KNOWN PNULL') + ') 999][.LINE = 999]',
        '$scalar_compare_read_array(S,perrorread_bad)', '~$error_read_valid(S,perrorread_bad)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_bad])',
        '~$error_read_valid(S[.CODE = eps],perrorread)', '$error_read_plan(S[.CODE = eps]) = eps',
        '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        'perrorread_space = perrorread[.ORIGINAL = BINARY_RIGHT SPACESHIP (VARIABLE (' + text(left) + ') z_left) 10][.TASK = BINARY_RIGHT SPACESHIP (' + ('VARIABLE (' + text(left) + ') z_left' if greater else 'KNOWN PNULL') + ') 10]',
        '~$scalar_compare_read_array(S,perrorread_space)', '~$error_read_valid(S,perrorread_space)',
    ]
    if greater:
        values += ['S_done.STORE[n_current] = DEFINED (PINT 7)']
    else:
        values += ['S_done.STORE[n_current] = DEFINED (PARRAY n_final)', 'n_final =/= n_array',
                   'S_done.ARRAYS[n_final].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
                   'S_done.ARRAYS[n_array] = S_resume.ARRAYS[n_array]',
                   '$heap_owners($heap_prune($heap_graph(S_done)),HARRAY n_final) = 1']
    return values
