"""Array owners retain object children; saved reads never duplicate child edges."""
import base64
import json

from undefined_spaceship_protocol import PREFIX as COMMON, text

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
    'BINARY_RIGHT pbin poperand z\n  -- if '
    + r'pbin = EQUAL \/ pbin = NOTEQUAL \/ pbin = LESS \/ pbin = LESSEQUAL \/ pbin = GREATER \/ pbin = GREATEREQUAL \/ pbin = SPACESHIP') + r'''
def $us_stage(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
def $us_stage(S, 5) = true -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask*
'''


def seek(target, source, stage):
    return [target + '_found = $us_seek(' + source + ',' + str(stage) + ',3000)',
            target + r'_found.COMPLETION = NORMAL \/ ' + target + '_found.COMPLETION = BUDGET',
            target + ' = ' + target + '_found[.COMPLETION = NORMAL]']


def front(program, path, live, throwing):
    line = 27 if live else 33 if throwing else 29
    operator = 'EQUAL' if live else 'LESSEQUAL' if throwing else 'SPACESHIP'
    read = '$scalar_compare_read_array' if live or throwing else '$spaceship_read_array'
    original = 'BINARY_RIGHT ' + operator + ' (' + (
        'VARIABLE ($ptascii("missing")) z_missing' if live else 'KNOWN (PARRAY n_array)') + ') ' + str(line)
    task = 'BINARY_RIGHT EQUAL (KNOWN PNULL) 27' if live else original
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S_front', 'S_initial', 0),
        'S = S_front', '$us_stage(S,0)', '$us_guard(S)',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
        'perrorread.ORIGINAL = ' + original, 'perrorread.TASK = ' + task,
        'perrorread.INPUT = VARIABLE ($ptascii("' + ('source' if live else 'missing') + '")) ' + ('z_source' if live else 'z_missing'),
        'perrorread.RESULT = ' + ('perrorread.INPUT' if live else 'KNOWN PNULL'),
        'S.RESULT = perrorread.INPUT',
        'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = ' + str(line),
        '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        '$spaceship_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = eps',
        '$scalar_compare_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = ' + ('(perrorread_other)' if live else 'eps'),
        '$base_nodes(perrorread.BASE) = eps',
        '$task_nodes(ERROR_READ_RESULT perrorread) = ' + ('eps' if live else '[HARRAY n_array]'),
        '$lookup(S.ENV,$ptascii("source")) = (n_source)',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)',
        'S.STORE[n_result] = DEFINED (PINT 41)',
        '$us_output(S.EVENTS) = ' + text('' if live else 'P;'),
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(26 if live else 33 if throwing else 28) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
        '~$comparison_read_object(S,perrorread)',
    ]
    if live:
        values += [
            'S.STORE[n_source] = DEFINED (PINT 0)',
            'perrorread_other =/= perrorread',
            '$scalar_compare_read_other(S,perrorread)', '~' + read + '(S,perrorread)',
            '$lookup(S.ENV,$ptascii("target")) = (n_target)',
            '$lookup(S.ENV,$ptascii("copy")) = (n_copy)',
            r'n_source =/= n_target /\ n_copy =/= n_target /\ n_copy =/= n_source',
            'S.STORE[n_target] = DEFINED (PARRAY n_copy_array)',
            'S.STORE[n_copy] = DEFINED (PARRAY n_copy_array)',
            'S.ARRAYS[n_copy_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]',
            '$heap_count(HARRAY n_copy_array,$pools_nodes(S.POOLS)) = 0',
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_copy_array) = 2',
            '$heap_owners($heap_prune($heap_graph(S)),HOBJECT n_old) = 1',
            '(HOBJECT n_old) <- S.ALLOCATIONS', '~(n_old <- S.DESTRUCTION.CALLED)',
        ]
    else:
        values += [
            'S.STORE[n_source] = DEFINED (PARRAY n_array)',
            'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object))]',
            'S.ARRAYS[n_array].NEXT = 1', '~$array_immutable(S,n_array)',
            '(HARRAY n_array) <- S.ALLOCATIONS', '(HOBJECT n_object) <- S.ALLOCATIONS',
            'S.OBJECTS[n_object] = INSTANCE porigin_class',
            '$comparison_read_object_value(S,POBJECT n_object)',
            '$spaceship_read_array_entries(S,S.ARRAYS[n_array].ITEMS)',
            '$heap_count(HARRAY n_array,$pools_nodes(S.POOLS)) = 0',
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_array) = 2',
            '$heap_owners($heap_prune($heap_graph(S)),HOBJECT n_object) = 1',
            '$node_children(S,HARRAY n_array) = [HOBJECT n_object]',
            '~(n_object <- S.DESTRUCTION.CALLED)', read + '(S,perrorread)',
            '~$scalar_compare_read_other(S,perrorread)' if throwing else '~$spaceship_read_other(S,perrorread)',
        ]
        if throwing:
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
        '$error_call_valid(S_warn,perrorcall)', '$us_guard(S_warn)', 'S_warn.EVENTS = S.EVENTS',
    ]
    return values


def invalid_controls(state, live, throwing):
    line = 27 if live else 33 if throwing else 29
    operator = 'EQUAL' if live else 'LESSEQUAL' if throwing else 'SPACESHIP'
    read = '$scalar_compare_read_array' if live or throwing else '$spaceship_read_array'
    obj = 'n_new' if live else 'n_object'
    arr = 'n_live' if live else 'n_array'
    left = 'VARIABLE ($ptascii("missing")) z_missing' if live else 'KNOWN (PARRAY n_array)'
    task = 'KNOWN PNULL' if live else left
    return [
        'perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT ' + operator + ' (' + left + ') 999][.TASK = BINARY_RIGHT ' + operator + ' (' + task + ') 999][.LINE = 999]',
        read + '(' + state + ',perrorread_bad)', '~$error_read_valid(' + state + ',perrorread_bad)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_bad])',
        '~$error_read_valid(' + state + '[.CODE = eps],perrorread)',
        '~$error_read_valid(' + state + '[.ORIGIN = eps],perrorread)',
        'perrorread_foreign = perrorread[.ORIGINAL = BINARY_RIGHT BITXOR (' + left + ') ' + str(line) + '][.TASK = BINARY_RIGHT BITXOR (' + task + ') ' + str(line) + ']',
        '~' + read + '(' + state + ',perrorread_foreign)',
        '~$error_read_valid(' + state + ',perrorread_foreign)',
        'S_dead = ' + state + '[.ALLOCATIONS = $destruction_node_delete(' + state + '.ALLOCATIONS,HOBJECT ' + obj + ')]',
        '$error_read_valid(S_dead,perrorread)', '~' + read + '(S_dead,perrorread)',
        '~$spaceship_read_array_value(S_dead,PARRAY ' + arr + ')',
        '~$spaceship_read_array_entries(S_dead,[ENTRY (KINT 0) (DIRECT (POBJECT ' + obj + '))])',
        '$spaceship_read_array_entries(' + state + ',eps)',
        '$spaceship_read_array_entries(' + state + ',[ENTRY (KINT 0) (DIRECT (POBJECT ' + obj + ')), ENTRY (KINT 1) (DIRECT PNULL)])',
        '~$spaceship_read_array_entries(' + state + ',[ENTRY (KINT 0) (DIRECT (PARRAY ' + arr + '))])',
        '~$spaceship_read_array_entries(' + state + ',[ENTRY (KINT 0) (ALIAS n_source)])',
        '~$spaceship_read_array_entries(' + state + ',[ENTRY (KINT 0) UNINITIALIZED])',
        '~$spaceship_read_array_entries(' + state + ',[ENTRY (KINT 0) (DIRECT PUNDEFINED)])',
        '~$spaceship_read_array_value(' + state + ',PARRAY (|' + state + '.ARRAYS|))',
    ]


def destructor(target, source, obj, before, result, pending='eps'):
    return [
        *seek(target, source, 5),
        target + '.TODO = (DESTRUCTOR_ENTER pdestructorcall_' + target + ') :: ptask_destructor_' + target + '*',
        'pdestructorcall_' + target + '.OBJECT = ' + obj,
        'pdestructorcall_' + target + '.PENDING = ' + pending,
        'pdestructorcall_' + target + '.OPERATION = (pdestructionoperation_' + target + ')',
        '$call_task_valid(' + target + ',DESTRUCTOR_ENTER pdestructorcall_' + target + ')',
        target + '.CURRENT = eps',
        obj + ' <- ' + target + '.DESTRUCTION.CALLED', '(HOBJECT ' + obj + ') <- ' + target + '.ALLOCATIONS',
        '$lookup(' + target + '.ENV,$ptascii("result")) = (n_result)',
        target + '.STORE[n_result] = DEFINED (' + result + ')',
        '$us_output(' + target + '.EVENTS) = ' + text(before), '$us_guard(' + target + ')',
    ]


def finish(start, expected):
    return [
        'S_done = $drive_steps(' + start + ',7000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        r'S_done.DESTRUCTION.CALLS = eps /\ S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],7000)',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],7000) = S_done',
    ]


def checks(program, path, name):
    live = name == 'peer-object-array-equal-target-default'
    throwing = name == 'peer-object-array-captured-supplied-throw'
    values = front(program, path, live, throwing)
    if throwing:
        return values + throw_checks()
    read = '$scalar_compare_read_array' if live else '$spaceship_read_array'
    values += [
        *seek('S_return', 'S_warn', 2),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        'S_return.RESULT = KNOWN (PBOOL ' + ('false' if live else 'true') + ')',
        r'S_return.CURRENT = eps /\ S_return.FRAMES = eps', '$us_guard(S_return)',
        *seek('S_resume', 'S_return', 3), 'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)', read + '(S_resume,perrorread)',
        '~$comparison_read_object(S_resume,perrorread)',
        '~$scalar_compare_read_other(S_resume,perrorread)' if live else '~$spaceship_read_other(S_resume,perrorread)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', '$us_guard(S_resume)',
        'S_resume.STORE[n_result] = DEFINED (PINT 41)',
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
        'S_resume.STORE[n_missing] = DEFINED (PBOOL true)',
        'S_resume.EVENTS = S_return.EVENTS' + (' ++ [$error_default_event(S_return,WARNING ($ptascii("missing")) 27)]' if live else ''),
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (' + ('PBOOL false' if live else 'PINT 1') + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS',
    ]
    if live:
        values += live_checks()
    else:
        values += [
            'S_resume.ARRAYS[n_array] = S.ARRAYS[n_array]',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HARRAY n_array) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HOBJECT n_object) = 1',
            'S_resume.STORE[n_source] = DEFINED (PARRAY n_empty)',
            'S_resume.ARRAYS[n_empty].ITEMS = eps', 'n_empty =/= n_array',
            '~(n_object <- S_resume.DESTRUCTION.CALLED)',
            '$heap_owners($heap_prune($heap_graph(S_compared)),HARRAY n_array) = 0',
            '$heap_owners($heap_prune($heap_graph(S_compared)),HOBJECT n_object) = 0',
            'H_compared = $heap_prune($heap_graph(S_compared))',
            '~((HARRAY n_array) <- H_compared.NODES)',
            '~((HOBJECT n_object) <- H_compared.NODES)',
            *invalid_controls('S', False, False),
            *destructor('S_destructor', 'S_restored', 'n_object', 'P;B;H:1:1:29:1;', 'PINT 41'),
            'pdestructionoperation_S_destructor.SOURCE = perrorread.TASK',
            'pdestructionoperation_S_destructor.VALUE = KNOWN (PINT 1)',
            *finish('S_destructor', 'P;B;H:1:1:29:1;D:1:1;R:1:1:1:1;A:1:1;END;'),
            '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
            'n_object <- S_done.DESTRUCTION.CALLED',
            '$heap_owners($heap_prune($heap_graph(S_done)),HOBJECT n_object) = 0',
        ]
    values += [
        '$drive_steps(S_return,7000) = S_done', '$drive_steps(S_restored,7000) = S_done',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],7000) = S_done',
    ]
    return values


def live_checks():
    return [
        '$lookup(S_resume.ENV,$ptascii("source")) = (n_target)',
        '~$scalar_compare_read_array(S_resume,perrorread_other)',
        '$lookup(S_resume.ENV,$ptascii("target")) = (n_target)',
        'n_target <- S_resume.REFCELLS',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_target) = 2',
        'S_resume.STORE[n_target] = DEFINED (PARRAY n_live)', 'n_live =/= n_copy_array',
        'S_resume.ARRAYS[n_live].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new))]',
        'n_new =/= n_old', '(HOBJECT n_new) <- S_resume.ALLOCATIONS',
        '$spaceship_read_array_entries(S_resume,S_resume.ARRAYS[n_live].ITEMS)',
        'S_resume.STORE[n_copy] = DEFINED (PARRAY n_copy_array)',
        'S_resume.ARRAYS[n_copy_array] = S.ARRAYS[n_copy_array]',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HARRAY n_live) = 1',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HARRAY n_copy_array) = 1',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HOBJECT n_new) = 1',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HOBJECT n_old) = 1',
        r'~(n_new <- S_resume.DESTRUCTION.CALLED) /\ ~(n_old <- S_resume.DESTRUCTION.CALLED)',
        '$heap_owners($heap_prune($heap_graph(S_compared)),HARRAY n_live) = 1',
        '$heap_owners($heap_prune($heap_graph(S_compared)),HOBJECT n_new) = 1',
        '$heap_owners($heap_prune($heap_graph(S_compared)),HOBJECT n_old) = 1',
        '$us_guard(S_compared)',
        *invalid_controls('S_resume', True, False),
        'PhpStep: S_dead ~> S_denied',
        'S_denied = S_dead[.TODO = eps][.COMPLETION = UNSUPPORTED "scalar comparison warning changed right operand"]',
        *destructor('S_new_destructor', 'S_compared', 'n_new',
                    'H:1:1:27:1;R:1:1:1:1:1:1;A:1:1:1;', 'PBOOL false'),
        '$lookup(S_new_destructor.ENV,$ptascii("source")) = eps',
        '$lookup(S_new_destructor.ENV,$ptascii("target")) = eps',
        '(HOBJECT n_old) <- S_new_destructor.ALLOCATIONS', '~(n_old <- S_new_destructor.DESTRUCTION.CALLED)',
        'S_new_started = $drive_steps(S_new_destructor,1)',
        'S_new_started.COMPLETION = BUDGET',
        *destructor('S_old_destructor', 'S_new_started[.COMPLETION = NORMAL]', 'n_old',
                    'H:1:1:27:1;R:1:1:1:1:1:1;A:1:1:1;N:1;', 'PBOOL false'),
        *finish('S_old_destructor', 'H:1:1:27:1;R:1:1:1:1:1:1;A:1:1:1;N:1;O:1;END;'),
        '~((HOBJECT n_new) <- S_done.ALLOCATIONS)', '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_live) <- S_done.ALLOCATIONS)', '~((HARRAY n_copy_array) <- S_done.ALLOCATIONS)',
        r'n_new <- S_done.DESTRUCTION.CALLED /\ n_old <- S_done.DESTRUCTION.CALLED',
    ]


def throw_checks():
    return [
        *seek('S_throw', 'S_warn', 4),
        'S_throw.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        r'S_throw.CURRENT = eps /\ S_throw.FRAMES = eps', '$us_guard(S_throw)',
        '$lookup(S_throw.ENV,$ptascii("exception")) = (n_exception_cell)',
        'S_throw.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
        '~$comparison_read_object_value(S_throw,POBJECT n_exception)',
        '~$spaceship_read_array_entries(S_throw,[ENTRY (KINT 0) (DIRECT (POBJECT n_exception))])',
        '$lookup(S_throw.ENV,$ptascii("source")) = eps', '$lookup(S_throw.ENV,$ptascii("alias")) = eps',
        '$lookup(S_throw.ENV,$ptascii("missing")) = (n_missing)',
        'S_throw.STORE[n_missing] = DEFINED (PBOOL true)',
        'S_throw.STORE[n_result] = DEFINED (PINT 41)',
        '$scalar_compare_read_array(S_throw,perrorread)',
        '$heap_owners($heap_prune($heap_graph(S_throw)),HARRAY n_array) = 1',
        '$heap_owners($heap_prune($heap_graph(S_throw)),HOBJECT n_object) = 1',
        '(HOBJECT n_object) <- S_throw.ALLOCATIONS', '~(n_object <- S_throw.DESTRUCTION.CALLED)',
        '$us_output(S_throw.EVENTS) = ' + text('P;B;H:1:1:33:1;'),
        'PhpStep: S_throw ~> S_discarded',
        'S_discarded = S_throw[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*][.ERRORHANDLER = S.ERRORHANDLER]',
        '$heap_owners($heap_prune($heap_graph(S_discarded)),HARRAY n_array) = 0',
        '$heap_owners($heap_prune($heap_graph(S_discarded)),HOBJECT n_object) = 0',
        *invalid_controls('S', False, True),
        *destructor('S_destructor', 'S_throw', 'n_object', 'P;B;H:1:1:33:1;', 'PINT 41', '(n_exception)'),
        'pdestructionoperation_S_destructor.PENDING = (n_exception)',
        'pdestructionoperation_S_destructor.SOURCE = THROW_SEARCH n_exception',
        *finish('S_destructor', 'P;B;H:1:1:33:1;D:1:1:1;C:1:1:1:1:1:1;F;END;'),
        'S_done.STORE[n_result] = DEFINED (PINT 41)',
        '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
        'n_object <- S_done.DESTRUCTION.CALLED',
        '$drive_steps(S_throw,7000) = S_done',
        'S_zero = $drive_steps(S_throw,0)', 'S_zero = S_throw[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],7000) = S_done',
    ]
