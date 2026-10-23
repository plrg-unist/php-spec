"""Captured buckets preserve cells; current cell writes select object lifetime."""
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
    return [target + '_found = $us_seek(' + source + ',' + str(stage) + ',3500)',
            target + r'_found.COMPLETION = NORMAL \/ ' + target + '_found.COMPLETION = BUDGET',
            target + ' = ' + target + '_found[.COMPLETION = NORMAL]']


def owners(state, node, count):
    return '$heap_owners($heap_prune($heap_graph(' + state + ')),' + node + ') = ' + str(count)


def destructor(target, source, obj, output, pending='eps', inside=False, result='PINT 41'):
    return [
        *seek(target, source, 5),
        target + '.TODO = (DESTRUCTOR_ENTER pdestructorcall_' + target + ') :: ptask_destructor_' + target + '*',
        'pdestructorcall_' + target + '.OBJECT = ' + obj,
        'pdestructorcall_' + target + '.PENDING = ' + pending,
        'pdestructorcall_' + target + '.OPERATION = (pdestructionoperation_' + target + ')',
        '$call_task_valid(' + target + ',DESTRUCTOR_ENTER pdestructorcall_' + target + ')',
        target + '.CURRENT ' + ('=/= eps' if inside else '= eps'),
        target + '.STORE[n_result] = DEFINED (' + result + ')',
        obj + ' <- ' + target + '.DESTRUCTION.CALLED',
        '(HOBJECT ' + obj + ') <- ' + target + '.ALLOCATIONS',
        '$us_output(' + target + '.EVENTS) = ' + text(output), '$us_guard(' + target + ')',
    ]


def front(program, path, live, throwing):
    line = 30 if live else 34 if throwing else 40
    original = ('BINARY_RIGHT GREATER (VARIABLE ($ptascii("source")) z_source) 30'
                if live else 'BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_array)) ' + str(line))
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S_front', 'S_initial', 0),
        'S = S_front', '$us_stage(S,0)', '$us_guard(S)',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
        'perrorread.ORIGINAL = ' + original, 'perrorread.TASK = perrorread.ORIGINAL',
        'perrorread.INPUT = VARIABLE ($ptascii("missing")) z_missing',
        'perrorread.RESULT = KNOWN PNULL', 'S.RESULT = perrorread.INPUT',
        'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = ' + str(line),
        '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = ' + ('(perrorread_other)' if live else '(perrorread)'),
        '$scalar_compare_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = ' + ('(perrorread)' if live else 'eps'),
        '$spaceship_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = eps',
        '$base_nodes(perrorread.BASE) = eps',
        '$task_nodes(ERROR_READ_RESULT perrorread) = ' + ('eps' if live else '[HARRAY n_array]'),
        '$lookup(S.ENV,$ptascii("source")) = (n_source)',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 41)',
        '$lookup(S.ENV,$ptascii("leaf")) = (n_leaf)',
        'S.STORE[n_leaf] = DEFINED (POBJECT n_old)',
        '$call_reference_operand_valid(S,REFERENCE n_leaf)',
        '$comparison_read_object_value(S,POBJECT n_old)',
        '$node_children(S,HCELL n_leaf) = [HOBJECT n_old]',
        '$us_output(S.EVENTS) = ' + text('' if live else 'P;'),
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(29 if live else 34 if throwing else 39) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
        '~$comparison_read_object(S,perrorread)',
    ]
    if live:
        values += [
            'perrorread_other =/= perrorread', 'S.STORE[n_source] = DEFINED (PINT 0)',
            '$scalar_compare_read_other(S,perrorread)', '~$scalar_compare_read_array(S,perrorread)',
            '$lookup(S.ENV,$ptascii("target")) = (n_target)',
            '$lookup(S.ENV,$ptascii("copy")) = (n_copy)',
            'S.STORE[n_target] = DEFINED (PARRAY n_array)', 'S.STORE[n_copy] = DEFINED (PARRAY n_array)',
        ]
    else:
        values += [
            '$lookup(S.ENV,$ptascii("outside")) = (n_leaf)',
            'S.STORE[n_source] = DEFINED (PARRAY n_array)',
            '$spaceship_read_array(S,perrorread)', '~$spaceship_read_other(S,perrorread)',
        ]
        if not throwing:
            values += ['$lookup(S.ENV,$ptascii("copy")) = (n_copy)', 'S.STORE[n_copy] = DEFINED (PARRAY n_array)']
    values += [
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf)]',
        'S.ARRAYS[n_array].NEXT = 1', '~$array_immutable(S,n_array)',
        '$node_children(S,HARRAY n_array) = [HCELL n_leaf]',
        '$heap_count(HARRAY n_array,$pools_nodes(S.POOLS)) = 0',
        '$spaceship_read_array_entries(S,S.ARRAYS[n_array].ITEMS)',
        '$duplicate_item(S,n_array,ALIAS n_leaf) = ALIAS n_leaf',
        owners('S', 'HARRAY n_array', 2 if live or throwing else 3),
        owners('S', 'HCELL n_leaf', 2 if live else 3), owners('S', 'HOBJECT n_old', 1),
        '~(n_old <- S.DESTRUCTION.CALLED)',
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


def controls(state, live, obj, line):
    array = 'n_live_array' if live else 'n_array'
    read = '$scalar_compare_read_array' if live else '$spaceship_read_array'
    operator = 'GREATER' if live else 'SPACESHIP'
    left = 'VARIABLE ($ptascii("source")) z_source' if live else 'KNOWN (PARRAY n_array)'
    return [
        '$spaceship_read_array_entries(' + state + ',[ENTRY (KINT 0) (DIRECT PNULL), ENTRY (KINT 1) (ALIAS n_leaf), ENTRY (KINT 2) (DIRECT (POBJECT ' + obj + '))])',
        '~$spaceship_read_array_entries(' + state + ',[ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) UNINITIALIZED])',
        'S_dead_object = ' + state + '[.ALLOCATIONS = $destruction_node_delete(' + state + '.ALLOCATIONS,HOBJECT ' + obj + ')]',
        '$error_read_valid(S_dead_object,perrorread)', '~' + read + '(S_dead_object,perrorread)',
        'S_dead_cell = ' + state + '[.ALLOCATIONS = $destruction_node_delete(' + state + '.ALLOCATIONS,HCELL n_leaf)]',
        '~' + read + '(S_dead_cell,perrorread)',
        '~$spaceship_read_array_entries(' + state + '[.REFCELLS = eps],[ENTRY (KINT 0) (ALIAS n_leaf)])',
        '~$spaceship_read_array_entries(' + state + '[.STORE[n_leaf] = UNDEFINED],[ENTRY (KINT 0) (ALIAS n_leaf)])',
        '~$spaceship_read_array_entries(' + state + '[.STORE[n_leaf] = DEFINED PUNDEFINED],[ENTRY (KINT 0) (ALIAS n_leaf)])',
        'S_nested = ' + state + '[.STORE[n_leaf] = DEFINED (PARRAY ' + array + ')]',
        '~' + read + '(S_nested,perrorread)', '$error_read_valid(S_nested,perrorread)',
        '~$spaceship_read_array_entries(' + state + ',[ENTRY (KINT 0) (ALIAS (|' + state + '.STORE|))])',
        '~$error_read_valid(' + state + '[.CODE = eps],perrorread)',
        '~$error_read_valid(' + state + '[.ORIGIN = eps],perrorread)',
        'perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT ' + operator + ' (' + left + ') 999][.TASK = BINARY_RIGHT ' + operator + ' (' + left + ') 999][.LINE = 999]',
        read + '(' + state + ',perrorread_bad)', '~$error_read_valid(' + state + ',perrorread_bad)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_bad])',
        'perrorread_foreign = perrorread[.ORIGINAL = BINARY_RIGHT BITXOR (' + left + ') ' + line + '][.TASK = BINARY_RIGHT BITXOR (' + left + ') ' + line + ']',
        '~' + read + '(' + state + ',perrorread_foreign)', '~$error_read_valid(' + state + ',perrorread_foreign)',
    ]


def finish(start, expected):
    return [
        'S_done = $drive_steps(' + start + ',8000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        r'S_done.DESTRUCTION.CALLS = eps /\ S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],8000)',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],8000) = S_done',
        '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HCELL n_leaf) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_old) <- S_done.ALLOCATIONS)', 'n_old <- S_done.DESTRUCTION.CALLED',
    ]


def checks(program, path, name):
    live = name == 'peer-object-reference-array-greater-target-default'
    throwing = name == 'peer-object-reference-array-captured-supplied-throw'
    values = front(program, path, live, throwing)
    if throwing:
        return values + throw_checks()
    values += [
        *destructor('S_old', 'S_warn', 'n_old', '' if live else 'P;B;', inside=True),
        'S_old.STORE[n_leaf] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
        '$comparison_read_object_value(S_old,POBJECT n_new)',
        'n_new_table = |S.ARRAYS|',
        'S_old.ARRAYS[n_new_table].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) (DIRECT (PINT 8))]',
        'S_old.ARRAYS[n_array].ITEMS = S.ARRAYS[n_array].ITEMS',
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
        'S_resume.STORE[n_leaf] = DEFINED (POBJECT n_new)',
        '$node_children(S_resume,HCELL n_leaf) = [HOBJECT n_new]',
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
        'S_resume.STORE[n_missing] = DEFINED (PBOOL true)',
        'S_resume.EVENTS = S_return.EVENTS' + (' ++ [$error_default_event(S_return,WARNING ($ptascii("missing")) 30)]' if live else ''),
        '~((HOBJECT n_old) <- S_resume.ALLOCATIONS)', 'n_old <- S_resume.DESTRUCTION.CALLED',
        '~(n_new <- S_resume.DESTRUCTION.CALLED)', owners('S_resume', 'HOBJECT n_new', 1),
        'S_resume.ARRAYS[n_array] = S.ARRAYS[n_array]',
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (' + ('PBOOL true' if live else 'PINT 1') + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS',
    ]
    if live:
        expected = 'O:1;H:1:1:30:1;R:1:1:1:1:1:1:1;A:1;K:1;N:1:1;END;'
        values += [
            '$lookup(S_resume.ENV,$ptascii("source")) = (n_target)',
            '$lookup(S_resume.ENV,$ptascii("target")) = (n_target)',
            'n_target <- S_resume.REFCELLS', 'S_resume.STORE[n_target] = DEFINED (PARRAY n_live_array)',
            'n_live_array = n_new_table',
            'S_resume.ARRAYS[n_live_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) (DIRECT (PINT 8))]',
            '$node_children(S_resume,HARRAY n_live_array) = [HCELL n_leaf]',
            '~$scalar_compare_read_array(S_resume,perrorread_other)',
            owners('S_resume', 'HCELL n_target', 2), owners('S_resume', 'HARRAY n_live_array', 1),
            owners('S_resume', 'HARRAY n_array', 1), owners('S_resume', 'HCELL n_leaf', 3),
            owners('S_compared', 'HCELL n_leaf', 3), owners('S_compared', 'HOBJECT n_new', 1),
            *controls('S_resume', True, 'n_new', '30'),
            'PhpStep: S_nested ~> S_denied',
            'S_denied = S_nested[.TODO = eps][.COMPLETION = UNSUPPORTED "scalar comparison warning changed left operand"]',
            *destructor('S_last', 'S_compared', 'n_new', 'O:1;H:1:1:30:1;R:1:1:1:1:1:1:1;A:1;K:1;', result='PBOOL true'),
            *finish('S_last', expected),
            '~((HARRAY n_live_array) <- S_done.ALLOCATIONS)', '~((HCELL n_target) <- S_done.ALLOCATIONS)',
        ]
    else:
        expected = 'P;B;O:1;I:1:1:1;H:1:1:40:1;N:1:1:1;R:1:1:1:1:1:1:1;END;'
        values += [
            '$lookup(S_resume.ENV,$ptascii("source")) = eps', '$lookup(S_resume.ENV,$ptascii("copy")) = eps',
            '$lookup(S_resume.ENV,$ptascii("leaf")) = eps', '$lookup(S_resume.ENV,$ptascii("outside")) = eps',
            '~((HARRAY n_new_table) <- S_resume.ALLOCATIONS)',
            owners('S_resume', 'HARRAY n_array', 1), owners('S_resume', 'HCELL n_leaf', 1),
            owners('S_compared', 'HARRAY n_array', 0), owners('S_compared', 'HCELL n_leaf', 0),
            owners('S_compared', 'HOBJECT n_new', 0),
            *controls('S', False, 'n_old', '40'),
            *destructor('S_last_saved', 'S_restored', 'n_new', 'P;B;O:1;I:1:1:1;H:1:1:40:1;'),
            'pdestructionoperation_S_last_saved.SOURCE = perrorread.TASK',
            'pdestructionoperation_S_last_saved.VALUE = KNOWN (PINT 1)',
            *finish('S_last_saved', expected),
        ]
    values += [
        '~((HOBJECT n_new) <- S_done.ALLOCATIONS)', 'n_new <- S_done.DESTRUCTION.CALLED',
        '$drive_steps(S_old,8000) = S_done', '$drive_steps(S_return,8000) = S_done',
        '$drive_steps(S_restored,8000) = S_done',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],8000) = S_done',
    ]
    return values


def throw_checks():
    expected = 'P;B;H:1:1:34:1;D:1:1:1;C:1:1:1:1:1:1:1:1;F;END;'
    return [
        *seek('S_throw', 'S_warn', 4),
        'S_throw.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        r'S_throw.CURRENT = eps /\ S_throw.FRAMES = eps', '$us_guard(S_throw)',
        '$lookup(S_throw.ENV,$ptascii("exception")) = (n_exception_cell)',
        'S_throw.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
        '~$comparison_read_object_value(S_throw,POBJECT n_exception)',
        '~$spaceship_read_array_entries(S_throw[.STORE[n_leaf] = DEFINED (POBJECT n_exception)],[ENTRY (KINT 0) (ALIAS n_leaf)])',
        '$lookup(S_throw.ENV,$ptascii("source")) = eps', '$lookup(S_throw.ENV,$ptascii("leaf")) = eps',
        '$lookup(S_throw.ENV,$ptascii("outside")) = eps',
        'S_throw.STORE[n_result] = DEFINED (PINT 41)', '$spaceship_read_array(S_throw,perrorread)',
        owners('S_throw', 'HARRAY n_array', 1), owners('S_throw', 'HCELL n_leaf', 1), owners('S_throw', 'HOBJECT n_old', 1),
        '$us_output(S_throw.EVENTS) = ' + text('P;B;H:1:1:34:1;'),
        'PhpStep: S_throw ~> S_discarded',
        'S_discarded = S_throw[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*][.ERRORHANDLER = S.ERRORHANDLER]',
        owners('S_discarded', 'HARRAY n_array', 0), owners('S_discarded', 'HCELL n_leaf', 0), owners('S_discarded', 'HOBJECT n_old', 0),
        *controls('S', False, 'n_old', '34'),
        *destructor('S_throw_destructor', 'S_throw', 'n_old', 'P;B;H:1:1:34:1;', '(n_exception)'),
        'pdestructionoperation_S_throw_destructor.SOURCE = THROW_SEARCH n_exception',
        *finish('S_throw_destructor', expected),
        'S_done.STORE[n_result] = DEFINED (PINT 41)',
        '$drive_steps(S_throw,8000) = S_done',
        'S_zero = $drive_steps(S_throw,0)', 'S_zero = S_throw[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],8000) = S_done',
    ]
