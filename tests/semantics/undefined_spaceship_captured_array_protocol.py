"""Captured TASK/RESULT roots, unpooled table retirement and exact restoration."""
import base64
import json

from undefined_spaceship_protocol import PREFIX, text


def checks(program, path, name):
    left = name == 'captured-left-assignment-empty'
    line = 16 if left else 13
    initial_items = 'eps' if left else '[ENTRY (KINT 0) (DIRECT (PBOOL false))]'
    expected = ('H:1:1:16:1;R:1:1:1:1:1:1;A:1:1:1;END;' if left else
                'H:1:1:13:1;R:1:1:1:1;END;')
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $us_seek(S_initial,0,1400)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$us_stage(S,0)', '$us_guard(S)',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*', 'S.RESULT = perrorread.INPUT',
        '$error_read_shape(perrorread.ORIGINAL,S.RESULT,S.BASE) = (perrorread)',
        'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = ' + str(line),
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        '~$spaceship_read_other(S,perrorread)', '$spaceship_read_array(S,perrorread)',
        '~$scalar_compare_read_array(S,perrorread)',
        '$task_nodes(ERROR_READ_RESULT perrorread) = [HARRAY n_array]',
        '$base_nodes(perrorread.BASE) = eps', 'S.BORROWEDREAD = eps',
        '(HARRAY n_array) <- S.ALLOCATIONS', '$(n_array < |S.ARRAYS|)',
        'S.ARRAYS[n_array].ITEMS = ' + initial_items,
        'S.ARRAYS[n_array].NEXT = 1',
        '~$array_immutable(S,n_array)',
        '$heap_count(HARRAY n_array,$pools_nodes(S.POOLS)) = 0',
        '$spaceship_read_array_value(S,PARRAY n_array)',
        '~$spaceship_read_array_operand(S,KNOWN (PARRAY n_array))',
    ]
    if left:
        values += [
            'perrorread.ORIGINAL = BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_array)) 16',
            'perrorread.TASK = perrorread.ORIGINAL',
            'perrorread.INPUT = VARIABLE ($ptascii("missing")) z_missing',
            'perrorread.RESULT = KNOWN PNULL',
            '$lookup(S.ENV,$ptascii("source")) = (n_source)',
            '$lookup(S.ENV,$ptascii("saved")) = (n_saved)', 'n_saved =/= n_source',
            'S.STORE[n_source] = DEFINED (PARRAY n_array)',
            'S.STORE[n_saved] = DEFINED (PARRAY n_array)',
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_array) = 3',
        ]
    else:
        values += [
            'perrorread.ORIGINAL = BINARY_RIGHT SPACESHIP (VARIABLE ($ptascii("missing")) z_missing) 13',
            'perrorread.TASK = BINARY_RIGHT SPACESHIP (KNOWN PNULL) 13',
            'perrorread.INPUT = KNOWN (PARRAY n_array)', 'perrorread.RESULT = perrorread.INPUT',
            '$lookup(S.ENV,$ptascii("value")) = (n_value)',
            'S.STORE[n_value] = DEFINED (PBOOL false)',
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_array) = 1',
        ]
    values += [
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]',
        'S_warn = $prune_allocations($error_read_begin(S))',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = ' + str(line),
        'perrorcall.MESSAGE = $ptascii("Undefined variable $missing")',
        'perrorcall.EVENT = WARNING ($ptascii("missing")) ' + str(line),
        '$error_call_valid(S_warn,perrorcall)', 'S_warn.EVENTS = S.EVENTS', '$us_guard(S_warn)',
        'S_return_found = $us_seek(S_warn,2,1400)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]',
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        'S_return.RESULT = KNOWN (PBOOL true)', '$us_guard(S_return)',
        '$heap_owners($heap_prune($heap_graph(S_return)),HARRAY n_array) = 1',
        'S_resume_found = $us_seek(S_return,3,1400)',
        r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)', '$spaceship_read_array(S_resume,perrorread)',
        '~$spaceship_read_other(S_resume,perrorread)',
        '~$spaceship_read_again(S_resume,perrorread)', '~$spaceship_checked_missing(S_resume,perrorread)',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HARRAY n_array) = 1',
        '(HARRAY n_array) <- S_resume.ALLOCATIONS',
        'S_resume.ARRAYS[n_array] = S.ARRAYS[n_array]',
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
        'S_resume.STORE[n_missing] = DEFINED (PINT 9)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', 'S_resume.BORROWEDREAD = eps',
        r'S_resume.CURRENT = eps /\ S_resume.FRAMES = eps', '$us_guard(S_resume)',
    ]
    if left:
        values += [
            '$lookup(S_resume.ENV,$ptascii("saved")) = eps',
            '$lookup(S_resume.ENV,$ptascii("source")) = (n_source)',
            'S_resume.STORE[n_source] = DEFINED (PARRAY n_current)', 'n_current =/= n_array',
            'S_resume.ARRAYS[n_current].ITEMS = [ENTRY (KINT 1) (DIRECT (PINT 7))]',
            'S_resume.ARRAYS[n_current].NEXT = 2',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HARRAY n_current) = 1',
        ]
    else:
        values += ['S_resume.STORE[n_value] = DEFINED (PINT 7)']
    values += [
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps',
        '$heap_owners($heap_prune($heap_graph(S_restored)),HARRAY n_array) = 1',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PINT ' + ('0' if left else '$(-1)') + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS', 'S_compared.ARRAYS = S_resume.ARRAYS',
        '$heap_owners($heap_prune($heap_graph(S_compared)),HARRAY n_array) = 0',
        'S_pruned = $prune_allocations(S_compared)', '~((HARRAY n_array) <- S_pruned.ALLOCATIONS)',
        '$us_guard(S_pruned)',
        'S_done = $drive_steps(S_compared,4000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
        'S_done.ARRAYS[n_array] = S.ARRAYS[n_array]',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4000)',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_return,4000) = S_done',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],4000) = S_done',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_array)]',
        '$error_read_valid(S_dead,perrorread)', '~$spaceship_read_array(S_dead,perrorread)',
        '$error_read_plan(S_dead) = eps',
        'S_dead_resume = S_resume[.ALLOCATIONS = $destruction_node_delete(S_resume.ALLOCATIONS,HARRAY n_array)]',
        'PhpStep: S_dead_resume ~> S_refused',
        'S_refused = S_dead_resume[.TODO = eps][.COMPLETION = UNSUPPORTED "spaceship warning changed opposing scalar"]',
        'n_outside = |S.ARRAYS|',
        'S_outside = S[.ALLOCATIONS = (HARRAY n_outside) :: S.ALLOCATIONS]',
        '~$spaceship_read_array_value(S_outside,PARRAY n_outside)',
        '~$spaceship_read_array_entries([ENTRY (KINT 0) (DIRECT (PARRAY n_array))])',
        '~$spaceship_read_array_entries([ENTRY (KINT 0) (ALIAS n_missing)])',
        '~$spaceship_read_array_value(S,PINT 1)',
        'perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT SPACESHIP ' + ('(KNOWN (PARRAY n_array))' if left else '(VARIABLE ($ptascii("missing")) z_missing)') + ' 999][.TASK = BINARY_RIGHT SPACESHIP ' + ('(KNOWN (PARRAY n_array))' if left else '(KNOWN PNULL)') + ' 999][.LINE = 999]',
        '$spaceship_read_array(S,perrorread_bad)', '~$error_read_valid(S,perrorread_bad)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_bad])',
        '~$error_read_valid(S[.CODE = eps],perrorread)', '$error_read_plan(S[.CODE = eps]) = eps',
        '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        'perrorread_foreign = perrorread[.ORIGINAL = BINARY_RIGHT EQUAL ' + ('(KNOWN (PARRAY n_array))' if left else '(VARIABLE ($ptascii("missing")) z_missing)') + ' ' + str(line) + '][.TASK = BINARY_RIGHT EQUAL ' + ('(KNOWN (PARRAY n_array))' if left else '(KNOWN PNULL)') + ' ' + str(line) + ']',
        '~$spaceship_read_array(S,perrorread_foreign)', '$scalar_compare_read_array(S,perrorread_foreign)',
        '~$error_read_valid(S,perrorread_foreign)',
        '$error_read_plan(S[.TODO = perrorread_foreign.ORIGINAL :: ptask_tail*][.RESULT = perrorread_foreign.INPUT][.BASE = perrorread_foreign.BASE]) = eps',
    ]
    if left:
        values += ['S_done.STORE[n_source] = DEFINED (PARRAY n_current)',
                   'S_done.ARRAYS[n_current].ITEMS = [ENTRY (KINT 1) (DIRECT (PINT 7)), ENTRY (KINT 2) (DIRECT (PINT 8))]',
                   'S_done.ARRAYS[n_current].NEXT = 3']
    return values
