"""Array copies share embedded primitive cells; saved owners release separately."""
import base64
import json

from undefined_spaceship_protocol import PREFIX as COMMON, text

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
    'BINARY_RIGHT pbin poperand z\n  -- if '
    + r'pbin = EQUAL \/ pbin = NOTEQUAL \/ pbin = LESS \/ pbin = LESSEQUAL \/ pbin = GREATER \/ pbin = GREATEREQUAL \/ pbin = SPACESHIP') + r'''
def $us_stage(S, 4) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = ERROR_READ_RESULT perrorread
'''


def seek(target, source, stage):
    return [target + '_found = $us_seek(' + source + ',' + str(stage) + ',3000)',
            target + r'_found.COMPLETION = NORMAL \/ ' + target + '_found.COMPLETION = BUDGET',
            target + ' = ' + target + '_found[.COMPLETION = NORMAL]']


def owners(state, node, count):
    return '$heap_owners($heap_prune($heap_graph(' + state + ')),' + node + ') = ' + str(count)


def front(program, path, live, throwing):
    line = 21 if live else 28
    original = ('BINARY_RIGHT EQUAL (VARIABLE ($ptascii("missing")) z_missing) 21'
                if live else 'BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_array)) 28')
    task = 'BINARY_RIGHT EQUAL (KNOWN PNULL) 21' if live else original
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
        'S.RESULT = perrorread.INPUT', 'perrorread.NAME = $ptascii("missing")',
        'perrorread.LINE = ' + str(line),
        '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        '$spaceship_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = eps',
        '$scalar_compare_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = ' + ('(perrorread_other)' if live else 'eps'),
        '$base_nodes(perrorread.BASE) = eps',
        '$task_nodes(ERROR_READ_RESULT perrorread) = ' + ('eps' if live else '[HARRAY n_array]'),
        '$lookup(S.ENV,$ptascii("source")) = (n_source)',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)',
        'S.STORE[n_result] = DEFINED (PINT 41)',
        '$lookup(S.ENV,$ptascii("leaf")) = (n_leaf)',
        'S.STORE[n_leaf] = DEFINED (PINT 0)', 'n_leaf <- S.REFCELLS',
        '$call_reference_operand_valid(S,REFERENCE n_leaf)',
        '$node_children(S,HCELL n_leaf) = eps',
        '$us_output(S.EVENTS) = ' + text('' if live else 'P;'),
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(20 if live else 28 if throwing else 27) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
        '~$comparison_read_object(S,perrorread)',
    ]
    if live:
        values += [
            'perrorread_other =/= perrorread',
            'S.STORE[n_source] = DEFINED (PINT 0)',
            '$scalar_compare_read_other(S,perrorread)', '~$scalar_compare_read_array(S,perrorread)',
            '$lookup(S.ENV,$ptascii("target")) = (n_target)',
            '$lookup(S.ENV,$ptascii("copy")) = (n_copy)',
            'S.STORE[n_target] = DEFINED (PARRAY n_array)',
            'S.STORE[n_copy] = DEFINED (PARRAY n_array)',
        ]
    else:
        values += [
            '$lookup(S.ENV,$ptascii("outside")) = (n_leaf)',
            'S.STORE[n_source] = DEFINED (PARRAY n_array)',
            '$spaceship_read_array(S,perrorread)', '~$spaceship_read_other(S,perrorread)',
        ]
        if not throwing:
            values += ['$lookup(S.ENV,$ptascii("copy")) = (n_copy)',
                       'S.STORE[n_copy] = DEFINED (PARRAY n_array)']
    values += [
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf)]',
        'S.ARRAYS[n_array].NEXT = 1', '~$array_immutable(S,n_array)',
        '(HARRAY n_array) <- S.ALLOCATIONS', '(HCELL n_leaf) <- S.ALLOCATIONS',
        '$node_children(S,HARRAY n_array) = [HCELL n_leaf]',
        '$heap_count(HARRAY n_array,$pools_nodes(S.POOLS)) = 0',
        '$spaceship_read_array_entries(S,S.ARRAYS[n_array].ITEMS)',
        owners('S', 'HARRAY n_array', 2 if live or throwing else 3),
        owners('S', 'HCELL n_leaf', 2 if live else 3),
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


def controls(state, live):
    array = 'n_live' if live else 'n_array'
    read = '$scalar_compare_read_array' if live else '$spaceship_read_array'
    operator = 'EQUAL' if live else 'SPACESHIP'
    left = 'VARIABLE ($ptascii("missing")) z_missing' if live else 'KNOWN (PARRAY n_array)'
    task_left = 'KNOWN PNULL' if live else left
    return [
        '$spaceship_read_array_entries(' + state + ',eps)',
        '$spaceship_read_array_entries(' + state + ',[ENTRY (KINT 0) (DIRECT PNULL), ENTRY (KINT 1) (ALIAS n_leaf), ENTRY (KINT 2) (DIRECT (PINT 8))])',
        '~$spaceship_read_array_entries(' + state + ',[ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) UNINITIALIZED])',
        '~$spaceship_read_array_entries(' + state + ',[ENTRY (KINT 0) (DIRECT (PARRAY ' + array + '))])',
        '~$spaceship_read_array_entries(' + state + ',[ENTRY (KINT 0) (ALIAS (|' + state + '.STORE|))])',
        'S_dead_cell = ' + state + '[.ALLOCATIONS = $destruction_node_delete(' + state + '.ALLOCATIONS,HCELL n_leaf)]',
        '~$call_reference_operand_valid(S_dead_cell,REFERENCE n_leaf)',
        '~' + read + '(S_dead_cell,perrorread)', '$error_read_valid(S_dead_cell,perrorread)',
        'S_not_ref = ' + state + '[.REFCELLS = eps]',
        '~$spaceship_read_array_entries(S_not_ref,[ENTRY (KINT 0) (ALIAS n_leaf)])',
        'S_undefined = ' + state + '[.STORE = $set_cell(' + state + '.STORE,n_leaf,UNDEFINED)]',
        '~$call_reference_operand_valid(S_undefined,REFERENCE n_leaf)',
        '~' + read + '(S_undefined,perrorread)',
        'S_nested = ' + state + '[.STORE = $set_cell(' + state + '.STORE,n_leaf,DEFINED (PARRAY ' + array + '))]',
        '$call_reference_operand_valid(S_nested,REFERENCE n_leaf)',
        '~$spaceship_read_array_entries(S_nested,[ENTRY (KINT 0) (ALIAS n_leaf)])',
        '~' + read + '(S_nested,perrorread)', '$error_read_valid(S_nested,perrorread)',
        'S_object = ' + state + '[.STORE = $set_cell(' + state + '.STORE,n_leaf,DEFINED (POBJECT 0))]',
        '~$spaceship_read_array_entries(S_object,[ENTRY (KINT 0) (ALIAS n_leaf)])',
        'S_dead_array = ' + state + '[.ALLOCATIONS = $destruction_node_delete(' + state + '.ALLOCATIONS,HARRAY ' + array + ')]',
        '~' + read + '(S_dead_array,perrorread)', '$error_read_valid(S_dead_array,perrorread)',
        '~$error_read_valid(' + state + '[.CODE = eps],perrorread)',
        '~$error_read_valid(' + state + '[.ORIGIN = eps],perrorread)',
        'perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT ' + operator + ' (' + left + ') 999][.TASK = BINARY_RIGHT ' + operator + ' (' + task_left + ') 999][.LINE = 999]',
        read + '(' + state + ',perrorread_bad)', '~$error_read_valid(' + state + ',perrorread_bad)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_bad])',
        'perrorread_foreign = perrorread[.ORIGINAL = BINARY_RIGHT BITXOR (' + left + ') ' + ('21' if live else '28') + '][.TASK = BINARY_RIGHT BITXOR (' + task_left + ') ' + ('21' if live else '28') + ']',
        '~' + read + '(' + state + ',perrorread_foreign)',
        '~$error_read_valid(' + state + ',perrorread_foreign)',
    ]


def finish(start, expected, leaf_value, leaf_owners):
    return [
        'S_done = $drive_steps(' + start + ',7000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],7000)',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],7000) = S_done',
        'S_done.STORE[n_leaf] = DEFINED (PINT ' + str(leaf_value) + ')',
        '$call_reference_operand_valid(S_done,REFERENCE n_leaf)',
        '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
        owners('S_done', 'HCELL n_leaf', leaf_owners),
    ]


def checks(program, path, name):
    live = name == 'peer-reference-array-equal-target-default'
    throwing = name == 'peer-reference-array-captured-supplied-throw'
    values = front(program, path, live, throwing)
    if throwing:
        return values + throw_checks()
    values += [
        *seek('S_return', 'S_warn', 2),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        'S_return.RESULT = KNOWN (PBOOL ' + ('false' if live else 'true') + ')',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        r'S_return.CURRENT = eps /\ S_return.FRAMES = eps', '$us_guard(S_return)',
        *seek('S_resume', 'S_return', 3),
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)',
        ('$scalar_compare_read_array' if live else '$spaceship_read_array') + '(S_resume,perrorread)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', '$us_guard(S_resume)',
        'S_resume.STORE[n_result] = DEFINED (PINT 41)',
        'S_resume.STORE[n_leaf] = DEFINED (PINT 7)',
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
        'S_resume.STORE[n_missing] = DEFINED (PBOOL true)',
        'S_resume.EVENTS = S_return.EVENTS' + (' ++ [$error_default_event(S_return,WARNING ($ptascii("missing")) 21)]' if live else ''),
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (' + ('PBOOL false' if live else 'PINT 1') + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS', '$us_guard(S_compared)',
        'S_resume.ARRAYS[n_array] = S.ARRAYS[n_array]',
    ]
    if live:
        values += [
            '$lookup(S_resume.ENV,$ptascii("source")) = (n_target)',
            '$lookup(S_resume.ENV,$ptascii("target")) = (n_target)', 'n_target <- S_resume.REFCELLS',
            'S_resume.STORE[n_target] = DEFINED (PARRAY n_live)', 'n_live =/= n_array',
            'n_live = |S.ARRAYS|',
            'S_resume.ARRAYS[n_live].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) (DIRECT (PINT 8))]',
            'S_resume.ARRAYS[n_live].NEXT = 2', '$node_children(S_resume,HARRAY n_live) = [HCELL n_leaf]',
            '$duplicate_item(S,n_array,ALIAS n_leaf) = ALIAS n_leaf',
            owners('S_resume', 'HCELL n_target', 2),
            owners('S_resume', 'HARRAY n_live', 1), owners('S_resume', 'HARRAY n_array', 1),
            owners('S_resume', 'HCELL n_leaf', 3), owners('S_compared', 'HCELL n_leaf', 3),
            *controls('S_resume', True),
            'PhpStep: S_nested ~> S_denied',
            'S_denied = S_nested[.TODO = eps][.COMPLETION = UNSUPPORTED "scalar comparison warning changed right operand"]',
            *finish('S_compared', 'H:1:1:21:1;R:1:1:1:1:1:1:1;A:1:1;W:1:1:1;Z:1;END;', 12, 1),
            '~((HARRAY n_live) <- S_done.ALLOCATIONS)', '~((HCELL n_target) <- S_done.ALLOCATIONS)',
            '$lookup(S_done.ENV,$ptascii("source")) = eps',
            '$lookup(S_done.ENV,$ptascii("target")) = eps',
        ]
    else:
        values += [
            'S_resume.STORE[n_source] = DEFINED (PARRAY n_empty)', 'n_empty =/= n_array',
            'S_resume.ARRAYS[n_empty].ITEMS = eps',
            'n_cow = |S.ARRAYS|',
            'S_resume.ARRAYS[n_cow].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) (DIRECT (PINT 8))]',
            '~((HARRAY n_cow) <- S_resume.ALLOCATIONS)',
            '$duplicate_item(S,n_array,ALIAS n_leaf) = ALIAS n_leaf',
            owners('S_resume', 'HARRAY n_array', 2), owners('S_resume', 'HCELL n_leaf', 3),
            owners('S_compared', 'HARRAY n_array', 1), owners('S_compared', 'HCELL n_leaf', 3),
            *controls('S', False),
            *finish('S_compared', 'P;B;I:1:1:1;H:1:1:28:1;R:1:1:1:1:1:1:1;A:1:1;L:1:1;END;', 11, 2),
            '$lookup(S_done.ENV,$ptascii("copy")) = eps',
        ]
    values += [
        '$drive_steps(S_return,7000) = S_done', '$drive_steps(S_restored,7000) = S_done',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],7000) = S_done',
    ]
    return values


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
        '$lookup(S_throw.ENV,$ptascii("source")) = eps',
        '$lookup(S_throw.ENV,$ptascii("outside")) = (n_leaf)',
        'S_throw.STORE[n_leaf] = DEFINED (PINT 7)',
        '$call_reference_operand_valid(S_throw,REFERENCE n_leaf)',
        'S_throw.STORE[n_result] = DEFINED (PINT 41)', '$spaceship_read_array(S_throw,perrorread)',
        owners('S_throw', 'HARRAY n_array', 1), owners('S_throw', 'HCELL n_leaf', 3),
        '$us_output(S_throw.EVENTS) = ' + text('P;B;H:1:1:28:1;'),
        'PhpStep: S_throw ~> S_discarded',
        'S_discarded = S_throw[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*][.ERRORHANDLER = S.ERRORHANDLER]',
        owners('S_discarded', 'HARRAY n_array', 0), owners('S_discarded', 'HCELL n_leaf', 2),
        *controls('S', False),
        *finish('S_discarded', 'P;B;H:1:1:28:1;C:1:1:1:1:1:1:1:1;F;Z:1;END;', 11, 2),
        'S_done.STORE[n_result] = DEFINED (PINT 41)',
        '$drive_steps(S_throw,7000) = S_done',
        'S_zero = $drive_steps(S_throw,0)', 'S_zero = S_throw[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],7000) = S_done',
    ]
