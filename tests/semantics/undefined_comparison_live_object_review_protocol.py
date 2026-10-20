"""Current CV objects own their lifetimes; saved warning records do not copy them."""
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
    return [target + '_found = $us_seek(' + source + ',' + str(stage) + ',2500)',
            target + r'_found.COMPLETION = NORMAL \/ ' + target + '_found.COMPLETION = BUDGET',
            target + ' = ' + target + '_found[.COMPLETION = NORMAL]']


def front(program, path, greater, throwing):
    line = 27 if greater else 26 if throwing else 20
    operator = 'GREATER' if greater else 'SPACESHIP' if throwing else 'EQUAL'
    original = ('BINARY_RIGHT ' + operator + ' (VARIABLE ($ptascii("source")) z_source) ' + str(line)
                if greater else 'BINARY_RIGHT ' + operator + ' (VARIABLE ($ptascii("missing")) z_missing) ' + str(line))
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S_front', 'S_initial', 0),
        'S = S_front', '$us_stage(S,0)', '$us_guard(S)',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        '$error_read_plan(S) = (perrorread)', '$error_read_source(S,perrorread)',
        '$error_read_valid(S,perrorread)', 'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
        'perrorread.ORIGINAL = ' + original,
        'perrorread.INPUT = VARIABLE ($ptascii("' + ('missing' if greater else 'source') + '")) ' + ('z_missing' if greater else 'z_source'),
        'S.RESULT = perrorread.INPUT',
        'perrorread.TASK = ' + (original if greater else 'BINARY_RIGHT ' + operator + ' (KNOWN PNULL) ' + str(line)),
        'perrorread.RESULT = ' + ('KNOWN PNULL' if greater else 'perrorread.INPUT'),
        'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = ' + str(line),
        '$task_nodes(ERROR_READ_RESULT perrorread) = eps', '$base_nodes(perrorread.BASE) = eps',
        '$lookup(S.ENV,$ptascii("source")) = (n_source)',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 41)',
        '$us_output(S.EVENTS) = eps',
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(line - 1) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
        '~$comparison_read_object_operand(S,KNOWN (POBJECT 0))',
    ]
    if greater:
        values += [
            '$scalar_compare_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
            '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread_left)',
            'perrorread_left =/= perrorread',
            'S.STORE[n_source] = DEFINED (PINT 0)',
            '$scalar_compare_read_other(S,perrorread)', '~$comparison_read_object(S,perrorread)',
            '$lookup(S.ENV,$ptascii("target")) = (n_target)',
            '$lookup(S.ENV,$ptascii("copy")) = (n_copy)',
            r'n_target =/= n_source /\ n_copy =/= n_target /\ n_copy =/= n_source',
            'S.STORE[n_target] = DEFINED (POBJECT n_old)',
            'S.STORE[n_copy] = DEFINED (POBJECT n_old)',
            '$heap_owners($heap_prune($heap_graph(S)),HOBJECT n_old) = 2',
        ]
    else:
        values += [
            '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
            'S.STORE[n_source] = DEFINED (POBJECT n_old)',
            '$comparison_read_object_operand(S,VARIABLE ($ptascii("source")) z_source)',
            '$comparison_read_object(S,perrorread)',
            '~$spaceship_read_other(S,perrorread)' if throwing else '~$scalar_compare_read_other(S,perrorread)',
            '$heap_owners($heap_prune($heap_graph(S)),HOBJECT n_old) = 1',
            'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_old)]',
            '$error_read_valid(S_dead,perrorread)', '~$comparison_read_object(S_dead,perrorread)',
            '$error_read_plan(S_dead) = eps',
        ]
    values += [
        '(HOBJECT n_old) <- S.ALLOCATIONS', 'S.OBJECTS[n_old] = INSTANCE porigin_old',
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


def destructor_checks(target, source, obj, output, result, callback=False):
    return [
        *seek(target, source, 5),
        target + '.TODO = (DESTRUCTOR_ENTER pdestructorcall_' + target + ') :: ptask_destructor_' + target + '*',
        'pdestructorcall_' + target + '.OBJECT = ' + obj,
        'pdestructorcall_' + target + '.PENDING = eps',
        'pdestructorcall_' + target + '.OPERATION = (pdestructionoperation_' + target + ')',
        '$call_task_valid(' + target + ',DESTRUCTOR_ENTER pdestructorcall_' + target + ')',
        'pdestructorcall_' + target + '.CALLER = ' + target + '.CURRENT',
        target + '.CURRENT =/= eps' if callback else target + '.CURRENT = eps',
        obj + ' <- ' + target + '.DESTRUCTION.CALLED',
        '(HOBJECT ' + obj + ') <- ' + target + '.ALLOCATIONS',
        target + '_global = $global_table_view(' + target + ')',
        target + '_global.STORE[n_result] = DEFINED (' + result + ')',
        '$us_output(' + target + '.EVENTS) = ' + text(output), '$us_guard(' + target + ')',
    ]


def invalid_controls(state, greater, throwing):
    line = 27 if greater else 26 if throwing else 20
    operator = 'GREATER' if greater else 'SPACESHIP' if throwing else 'EQUAL'
    left = 'VARIABLE ($ptascii("source")) z_source' if greater else 'VARIABLE ($ptascii("missing")) z_missing'
    task = left if greater else 'KNOWN PNULL'
    return [
        'perrorread_line = perrorread[.ORIGINAL = BINARY_RIGHT ' + operator + ' (' + left + ') 999][.TASK = BINARY_RIGHT ' + operator + ' (' + task + ') 999][.LINE = 999]',
        '$comparison_read_object(' + state + ',perrorread_line)',
        '~$error_read_valid(' + state + ',perrorread_line)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_line])',
        '~$error_read_valid(S[.CODE = eps],perrorread)',
        '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        'perrorread_foreign = perrorread[.ORIGINAL = BINARY_RIGHT BITXOR (' + left + ') ' + str(line) + '][.TASK = BINARY_RIGHT BITXOR (' + task + ') ' + str(line) + ']',
        '~$comparison_read_object(' + state + ',perrorread_foreign)',
        '~$error_read_valid(S,perrorread_foreign)',
    ]


def finish(start, expected):
    return [
        'S_done = $drive_steps(' + start + ',6000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        '~((HOBJECT n_old) <- S_done.ALLOCATIONS)', 'n_old <- S_done.DESTRUCTION.CALLED',
        '$heap_owners($heap_prune($heap_graph(S_done)),HOBJECT n_old) = 0',
        r'S_done.DESTRUCTION.CALLS = eps /\ S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],6000)',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],6000) = S_done',
    ]


def checks(program, path, name):
    greater = name == 'peer-live-object-greater-target-default'
    throwing = name == 'peer-live-object-spaceship-supplied-throw'
    values = front(program, path, greater, throwing)
    if throwing:
        return values + throw_checks()
    line = 27 if greater else 20
    values += [
        *seek('S_return', 'S_warn', 2),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        'S_return.RESULT = KNOWN (PBOOL ' + ('false' if greater else 'true') + ')',
        r'S_return.CURRENT = eps /\ S_return.FRAMES = eps', '$us_guard(S_return)',
        *seek('S_resume', 'S_return', 3),
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER',
        'S_resume.EVENTS = S_return.EVENTS' + (' ++ [$error_default_event(S_return,WARNING ($ptascii("missing")) 27)]' if greater else ''),
        'S_resume.STORE[n_result] = DEFINED (PINT 41)',
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
        'S_resume.STORE[n_missing] = DEFINED (PINT 9)',
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL true)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS', '$us_guard(S_compared)',
    ]
    if greater:
        values += greater_checks()
    else:
        values += [
            '~$comparison_read_object(S_resume,perrorread)', '$scalar_compare_read_other(S_resume,perrorread)',
            'S_resume.STORE[n_source] = DEFINED (PINT 0)',
            '~((HOBJECT n_old) <- S_resume.ALLOCATIONS)', 'n_old <- S_resume.DESTRUCTION.CALLED',
            '$us_output(S_resume.EVENTS) = $ptascii("B;D:1;H:1:1:20:1;")',
            *destructor_checks('S_old_destructor', 'S_warn', 'n_old', 'B;', 'PINT 41', True),
            'S_old_destructor_global.STORE[n_source] = DEFINED (PINT 0)',
            '$lookup(S_old_destructor_global.ENV,$ptascii("missing")) = eps',
            *finish('S_compared', 'B;D:1;H:1:1:20:1;R:1:1:1:1;END;'),
            '$drive_steps(S_old_destructor,6000) = S_done',
            *invalid_controls('S', False, False),
        ]
    values += [
        '$drive_steps(S_return,6000) = S_done', '$drive_steps(S_restored,6000) = S_done',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],6000) = S_done',
    ]
    return values


def greater_checks():
    return [
        '$lookup(S_resume.ENV,$ptascii("source")) = (n_current)',
        '$lookup(S_resume.ENV,$ptascii("target")) = (n_current)',
        'n_current =/= n_source', 'n_current <- S_resume.REFCELLS',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_current) = 2',
        'S_resume.STORE[n_current] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
        'S_resume.STORE[n_copy] = DEFINED (POBJECT n_old)',
        '$comparison_read_object(S_resume,perrorread)', '~$scalar_compare_read_other(S_resume,perrorread)',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HOBJECT n_new) = 1',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HOBJECT n_old) = 1',
        r'~(n_new <- S_resume.DESTRUCTION.CALLED) /\ ~(n_old <- S_resume.DESTRUCTION.CALLED)',
        '$heap_owners($heap_prune($heap_graph(S_compared)),HOBJECT n_new) = 1',
        '$heap_owners($heap_prune($heap_graph(S_compared)),HOBJECT n_old) = 1',
        'S_dead_resume = S_resume[.ALLOCATIONS = $destruction_node_delete(S_resume.ALLOCATIONS,HOBJECT n_new)]',
        '$error_read_valid(S_dead_resume,perrorread)', '~$comparison_read_object(S_dead_resume,perrorread)',
        'PhpStep: S_dead_resume ~> S_denied',
        'S_denied = S_dead_resume[.TODO = eps][.COMPLETION = UNSUPPORTED "scalar comparison warning changed left operand"]',
        *destructor_checks('S_new_destructor', 'S_compared', 'n_new', 'H:1:1:27:1;R:1:1:1:1:1:1;', 'PBOOL true'),
        '(HOBJECT n_old) <- S_new_destructor.ALLOCATIONS', '~(n_old <- S_new_destructor.DESTRUCTION.CALLED)',
        '$lookup(S_new_destructor_global.ENV,$ptascii("source")) = eps',
        '$lookup(S_new_destructor_global.ENV,$ptascii("target")) = eps',
        *finish('S_new_destructor', 'H:1:1:27:1;R:1:1:1:1:1:1;N:1;O:1;END;'),
        '~((HOBJECT n_new) <- S_done.ALLOCATIONS)', 'n_new <- S_done.DESTRUCTION.CALLED',
        *invalid_controls('S_resume', True, False),
    ]


def throw_checks():
    return [
        *seek('S_throw', 'S_warn', 4),
        'S_throw.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        r'S_throw.CURRENT = eps /\ S_throw.FRAMES = eps', '$us_guard(S_throw)',
        '$lookup(S_throw.ENV,$ptascii("chosen")) = (n_exception_cell)',
        'S_throw.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
        '$lookup(S_throw.ENV,$ptascii("source")) = (n_current)',
        'S_throw.STORE[n_current] = DEFINED (POBJECT n_new)', 'n_new =/= n_old',
        '$lookup(S_throw.ENV,$ptascii("missing")) = (n_missing)',
        'S_throw.STORE[n_missing] = DEFINED (PINT 9)',
        'S_throw.STORE[n_result] = DEFINED (PINT 41)',
        '~((HOBJECT n_old) <- S_throw.ALLOCATIONS)', 'n_old <- S_throw.DESTRUCTION.CALLED',
        '$heap_owners($heap_prune($heap_graph(S_throw)),HOBJECT n_new) = 1',
        '~(n_new <- S_throw.DESTRUCTION.CALLED)',
        '$comparison_read_object(S_throw,perrorread)',
        '~$comparison_read_object_value(S_throw,POBJECT n_exception)',
        '$us_output(S_throw.EVENTS) = $ptascii("B;O:1;H:1:1:26:1;")',
        'PhpStep: S_throw ~> S_discarded',
        'S_discarded = S_throw[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*][.ERRORHANDLER = S.ERRORHANDLER]',
        '$heap_owners($heap_prune($heap_graph(S_discarded)),HOBJECT n_new) = 1',
        '$us_guard(S_discarded)',
        *destructor_checks('S_new_destructor', 'S_discarded', 'n_new', 'B;O:1;H:1:1:26:1;C:1:1:1:1:1;F;', 'PINT 41'),
        '$lookup(S_new_destructor_global.ENV,$ptascii("source")) = eps',
        *finish('S_new_destructor', 'B;O:1;H:1:1:26:1;C:1:1:1:1:1;F;N:1;END;'),
        'S_done.STORE[n_result] = DEFINED (PINT 41)',
        '~((HOBJECT n_new) <- S_done.ALLOCATIONS)', 'n_new <- S_done.DESTRUCTION.CALLED',
        '$drive_steps(S_throw,6000) = S_done', '$drive_steps(S_discarded,6000) = S_done',
        'S_zero = $drive_steps(S_throw,0)', 'S_zero = S_throw[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],6000) = S_done',
        *invalid_controls('S', False, True),
    ]
