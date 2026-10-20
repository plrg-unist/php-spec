"""Captured tables retain saved owners through Warning return and throw."""
import base64
import json

from undefined_spaceship_protocol import PREFIX as COMMON, text

PREFIX = COMMON + r'''
def $us_stage(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
'''


def front(program, path, right, throwing=False):
    line = 18 if right else 25 if throwing else 24
    original = ('BINARY_RIGHT SPACESHIP (VARIABLE ($ptascii("missing")) z_missing) 18'
                if right else 'BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_array)) ' + str(line))
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $us_seek(S_initial,0,1600)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$us_stage(S,0)', '$us_guard(S)',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
        'perrorread.ORIGINAL = ' + original,
        'perrorread.INPUT = ' + ('KNOWN (PARRAY n_array)' if right else 'VARIABLE ($ptascii("missing")) z_missing'),
        'S.RESULT = perrorread.INPUT',
        'perrorread.TASK = ' + ('BINARY_RIGHT SPACESHIP (KNOWN PNULL) 18' if right else original),
        'perrorread.RESULT = ' + ('KNOWN (PARRAY n_array)' if right else 'KNOWN PNULL'),
        'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = ' + str(line),
        '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        '$spaceship_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = eps',
        '~$spaceship_read_other(S,perrorread)', '$spaceship_read_array(S,perrorread)',
        '~$scalar_compare_read_array(S,perrorread)',
        '$base_nodes(perrorread.BASE) = eps',
        '$task_nodes(ERROR_READ_RESULT perrorread) = [HARRAY n_array]',
        '(HARRAY n_array) <- S.ALLOCATIONS', '~$array_immutable(S,n_array)',
        '$heap_count(HARRAY n_array,$pools_nodes(S.POOLS)) = 0',
        'S.ARRAYS[n_array].ITEMS = ' + ('[ENTRY (KINT 0) (DIRECT (PBOOL false))]' if right else 'eps'),
        'S.ARRAYS[n_array].NEXT = 1',
        '$lookup(S.ENV,$ptascii("source")) = (n_source)',
        'S.STORE[n_source] = DEFINED (PARRAY n_array)',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_array) = ' + ('4' if right else '2'),
        '$us_output(S.EVENTS) = ' + text('' if right else 'P;'),
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(17 if right else 25 if throwing else 23) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_array)]',
        '~$spaceship_read_array(S_dead,perrorread)', '$error_read_plan(S_dead) = eps',
        '$error_read_valid(S_dead,perrorread)',
    ]
    if right:
        values += [
            '$lookup(S.ENV,$ptascii("copy")) = (n_copy)',
            '$lookup(S.ENV,$ptascii("saved")) = (n_saved)',
            r'n_copy =/= n_source /\ n_saved =/= n_source /\ n_copy =/= n_saved',
            'S.STORE[n_copy] = DEFINED (PARRAY n_array)',
            'S.STORE[n_saved] = DEFINED (PARRAY n_array)',
        ]
    else:
        values += [
            '$lookup(S.ENV,$ptascii("alias")) = (n_source)', 'n_source <- S.REFCELLS',
            '$heap_owners($heap_prune($heap_graph(S)),HCELL n_source) = 2',
        ]
    values += [
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_warn = $prune_allocations($error_read_begin(S))',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = ' + str(line),
        'perrorcall.MESSAGE = $ptascii("Undefined variable $missing")',
        'perrorcall.EVENT = WARNING ($ptascii("missing")) ' + str(line),
        '$error_call_valid(S_warn,perrorcall)', '$us_guard(S_warn)',
        '$heap_owners($heap_prune($heap_graph(S_warn)),HARRAY n_array) = ' + ('4' if right else '2'),
        'S_warn.EVENTS = S.EVENTS',
    ]
    return values


def checks(program, path, name):
    right = name == 'peer-captured-right-assignment-default'
    throwing = name == 'peer-captured-runtime-supplied-throw'
    values = front(program, path, right, throwing)
    if throwing:
        return values + throw_checks()
    line = 18 if right else 24
    expected = ('H:1:1:18:1;R:1:1:1:1:1:1;A:1:1:1:1;END;' if right else
                'P;H:1:1:24:1;R:1:1:1:1:1:1;A:1:1:1;END;')
    values += [
        'S_return_found = $us_seek(S_warn,2,1600)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]',
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        'S_return.RESULT = KNOWN (PBOOL ' + ('false' if right else 'true') + ')',
        r'S_return.CURRENT = eps /\ S_return.FRAMES = eps', '$us_guard(S_return)',
        'S_resume_found = $us_seek(S_return,3,1600)',
        r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]', '$us_stage(S_resume,3)',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)', '$spaceship_read_array(S_resume,perrorread)',
        '~$spaceship_read_other(S_resume,perrorread)', '~$spaceship_read_again(S_resume,perrorread)',
        '~$spaceship_checked_missing(S_resume,perrorread)',
        'S_resume.ARRAYS[n_array] = S.ARRAYS[n_array]',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HARRAY n_array) = ' + ('2' if right else '1'),
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
        'S_resume.STORE[n_missing] = DEFINED (PINT 9)',
        'S_resume.EVENTS = S_return.EVENTS' + (' ++ [$error_default_event(S_return,WARNING ($ptascii("missing")) 18)]' if right else ''),
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', '$us_guard(S_resume)',
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$heap_owners($heap_prune($heap_graph(S_restored)),HARRAY n_array) = ' + ('2' if right else '1'),
        '$error_read_plan(S_restored) = eps',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PINT ' + ('$(-1)' if right else '0') + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS', 'S_compared.ARRAYS = S_resume.ARRAYS',
        '$heap_owners($heap_prune($heap_graph(S_compared)),HARRAY n_array) = ' + ('1' if right else '0'),
        '$us_guard(S_compared)',
        'S_done = $drive_steps(S_compared,4000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4000)',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_return,4000) = S_done',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],4000) = S_done',
        'perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT SPACESHIP (' + ('VARIABLE ($ptascii("missing")) z_missing' if right else 'KNOWN (PARRAY n_array)') + ') 999][.TASK = BINARY_RIGHT SPACESHIP (' + ('KNOWN PNULL' if right else 'KNOWN (PARRAY n_array)') + ') 999][.LINE = 999]',
        '$spaceship_read_array(S,perrorread_bad)', '~$error_read_valid(S,perrorread_bad)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_bad])',
        '~$error_read_valid(S[.CODE = eps],perrorread)', '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        'perrorread_foreign = perrorread[.ORIGINAL = BINARY_RIGHT EQUAL (' + ('VARIABLE ($ptascii("missing")) z_missing' if right else 'KNOWN (PARRAY n_array)') + ') ' + str(line) + '][.TASK = BINARY_RIGHT EQUAL (' + ('KNOWN PNULL' if right else 'KNOWN (PARRAY n_array)') + ') ' + str(line) + ']',
        '~$spaceship_read_array(S,perrorread_foreign)', '$scalar_compare_read_array(S,perrorread_foreign)',
        '~$error_read_valid(S,perrorread_foreign)',
    ]
    if right:
        values += [
            'S_resume.STORE[n_source] = DEFINED (PARRAY n_current)', 'n_current =/= n_array',
            'S_resume.ARRAYS[n_current].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
            'S_resume.STORE[n_copy] = DEFINED (PARRAY n_array)',
            'S_resume.STORE[n_saved] = DEFINED (PARRAY n_empty)', 'n_empty =/= n_array',
            'S_resume.ARRAYS[n_empty].ITEMS = eps',
            'S_done.STORE[n_copy] = DEFINED (PARRAY n_array)',
            'S_done.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 8))]',
            '$heap_owners($heap_prune($heap_graph(S_done)),HARRAY n_array) = 1',
            'S_done.ARRAYS[n_current] = S_resume.ARRAYS[n_current]',
        ]
    else:
        values += [
            '$lookup(S_resume.ENV,$ptascii("source")) = eps',
            '$lookup(S_resume.ENV,$ptascii("alias")) = (n_source)',
            'S_resume.STORE[n_source] = DEFINED (PARRAY n_current)', 'n_current =/= n_array',
            'S_resume.ARRAYS[n_current].ITEMS = [ENTRY (KINT 1) (DIRECT (PINT 7))]',
            'S_resume.ARRAYS[n_current].NEXT = 2',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_source) = 1',
            '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
            'S_done.ARRAYS[n_current].ITEMS = [ENTRY (KINT 1) (DIRECT (PINT 7)), ENTRY (KINT 2) (DIRECT (PINT 8))]',
            'S_done.ARRAYS[n_current].NEXT = 3',
            '$heap_owners($heap_prune($heap_graph(S_done)),HARRAY n_current) = 1',
        ]
    return values


def throw_checks():
    return [
        'S_throw_found = $us_seek(S_warn,4,2000)',
        r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
        'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$us_stage(S_throw,4)',
        'S_throw.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        r'S_throw.CURRENT = eps /\ S_throw.FRAMES = eps', '$us_guard(S_throw)',
        '$lookup(S_throw.ENV,$ptascii("exception")) = (n_exception_cell)',
        'S_throw.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
        '$lookup(S_throw.ENV,$ptascii("source")) = eps',
        '$lookup(S_throw.ENV,$ptascii("alias")) = (n_source)',
        'S_throw.STORE[n_source] = DEFINED (PARRAY n_current)', 'n_current =/= n_array',
        'S_throw.ARRAYS[n_current].ITEMS = [ENTRY (KINT 1) (DIRECT (PINT 7))]',
        'S_throw.ARRAYS[n_current].NEXT = 2',
        'S_throw.ARRAYS[n_array] = S.ARRAYS[n_array]',
        '$heap_owners($heap_prune($heap_graph(S_throw)),HARRAY n_array) = 1',
        'PhpStep: S_throw ~> S_discarded',
        'S_discarded = S_throw[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*][.ERRORHANDLER = S.ERRORHANDLER]',
        '$heap_owners($heap_prune($heap_graph(S_discarded)),HARRAY n_array) = 0',
        'S_pruned = $prune_allocations(S_discarded)',
        '~((HARRAY n_array) <- S_pruned.ALLOCATIONS)',
        '(HARRAY n_current) <- S_pruned.ALLOCATIONS', '$us_guard(S_pruned)',
        'S_done = $drive_steps(S_pruned,4000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = $ptascii("P;H:1:1:25:1;C:1:1:1:1:1:1:1;F;A:1:1:1;END;")',
        '$lookup(S_done.ENV,$ptascii("result")) = (n_result)',
        'S_done.STORE[n_result] = DEFINED (PINT 41)',
        'S_done.ARRAYS[n_current].ITEMS = [ENTRY (KINT 1) (DIRECT (PINT 7)), ENTRY (KINT 2) (DIRECT (PINT 8))]',
        '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '$us_guard(S_done)',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4000)',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_discarded,4000) = S_done',
        'S_zero = $drive_steps(S_throw,0)', 'S_zero = S_throw[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],4000) = S_done',
    ]
