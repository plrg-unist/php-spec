"""Saved object identity, owner release and destructor timing at missing reads."""
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


def seek(target, source, stage, budget=2000):
    return [target + '_found = $us_seek(' + source + ',' + str(stage) + ',' + str(budget) + ')',
            target + r'_found.COMPLETION = NORMAL \/ ' + target + '_found.COMPLETION = BUDGET',
            target + ' = ' + target + '_found[.COMPLETION = NORMAL]']


def front(program, path, right, throwing):
    line = 23 if right else 29 if throwing else 27
    operator = 'GREATEREQUAL' if right else 'LESS' if throwing else 'EQUAL'
    original = ('BINARY_RIGHT ' + operator + ' (VARIABLE ($ptascii("missing")) z_missing) ' + str(line)
                if right else 'BINARY_RIGHT ' + operator + ' (KNOWN (POBJECT n_object)) ' + str(line))
    task = 'BINARY_RIGHT ' + operator + ' (KNOWN PNULL) ' + str(line) if right else original
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        *seek('S_front', 'S_initial', 0),
        'S = S_front', '$us_stage(S,0)', '$us_guard(S)',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
        'perrorread.ORIGINAL = ' + original,
        'perrorread.INPUT = ' + ('KNOWN (POBJECT n_object)' if right else 'VARIABLE ($ptascii("missing")) z_missing'),
        'S.RESULT = perrorread.INPUT', 'perrorread.TASK = ' + task,
        'perrorread.RESULT = ' + ('KNOWN (POBJECT n_object)' if right else 'KNOWN PNULL'),
        'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = ' + str(line),
        '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        '$spaceship_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = eps',
        '$scalar_compare_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = eps',
        '$comparison_read_object(S,perrorread)',
        '$comparison_read_object_value(S,POBJECT n_object)',
        '~$scalar_compare_read_other(S,perrorread)',
        '~$scalar_compare_read_array(S,perrorread)', '~$spaceship_read_array(S,perrorread)',
        '~$scalar_compare_missing_pair(S,perrorread)',
        '$base_nodes(perrorread.BASE) = eps',
        '$task_nodes(ERROR_READ_RESULT perrorread) = [HOBJECT n_object]',
        '(HOBJECT n_object) <- S.ALLOCATIONS', 'S.OBJECTS[n_object] = INSTANCE porigin_class',
        '$instanceof_dynamic_class(S,POBJECT n_object) = (ptbytes_class)',
        '~$class_instanceof(S,POBJECT n_object,$ptascii("Stringable"))',
        '~$instance_storage_freeing(S,n_object)', '~(n_object <- S.DESTRUCTION.CALLED)',
        '$lookup(S.ENV,$ptascii("source")) = (n_source)',
        'S.STORE[n_source] = DEFINED (POBJECT n_object)',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)',
        'S.STORE[n_result] = DEFINED (PINT 41)',
        '$heap_owners($heap_prune($heap_graph(S)),HOBJECT n_object) = ' + ('3' if right else '2'),
        '$us_output(S.EVENTS) = ' + text('' if right else 'P;'),
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(22 if right else 28 if throwing else 26) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_object)]',
        '$error_read_valid(S_dead,perrorread)', '~$comparison_read_object(S_dead,perrorread)',
        '~$comparison_read_object_value(S_dead,POBJECT n_object)', '$error_read_plan(S_dead) = eps',
        '~$scalar_compare_read_other(S_dead,perrorread)',
        '~$comparison_read_object_value(S,PNULL)',
        '~$comparison_read_object_value(S,PARRAY 0)',
        '~$comparison_read_object_value(S,POBJECT (|S.OBJECTS|))',
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_warn = $prune_allocations($error_read_begin(S))',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = ' + str(line),
        'perrorcall.MESSAGE = $ptascii("Undefined variable $missing")',
        'perrorcall.EVENT = WARNING ($ptascii("missing")) ' + str(line),
        '$error_call_valid(S_warn,perrorcall)', '$us_guard(S_warn)',
        'S_warn.EVENTS = S.EVENTS',
        '$heap_owners($heap_prune($heap_graph(S_warn)),HOBJECT n_object) = ' + ('3' if right else '2'),
    ]
    if right:
        values += ['$lookup(S.ENV,$ptascii("saved")) = (n_saved)', 'n_saved =/= n_source',
                   'S.STORE[n_saved] = DEFINED (POBJECT n_object)']
    return values


def invalid_controls(right, line, operator):
    left = 'VARIABLE ($ptascii("missing")) z_missing' if right else 'KNOWN (POBJECT n_object)'
    frozen = 'KNOWN PNULL' if right else left
    return [
        'perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT ' + operator + ' (' + left + ') 999][.TASK = BINARY_RIGHT ' + operator + ' (' + frozen + ') 999][.LINE = 999]',
        '$comparison_read_object(S,perrorread_bad)', '~$error_read_valid(S,perrorread_bad)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_bad])',
        '~$error_read_valid(S[.CODE = eps],perrorread)', '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        'perrorread_foreign = perrorread[.ORIGINAL = BINARY_RIGHT BITXOR (' + left + ') ' + str(line) + '][.TASK = BINARY_RIGHT BITXOR (' + frozen + ') ' + str(line) + ']',
        '~$comparison_read_object(S,perrorread_foreign)', '~$error_read_valid(S,perrorread_foreign)',
        '$error_read_shape(BINARY_RIGHT ' + operator + ' (VARIABLE ($ptascii("missing")) 1) ' + str(line) + ',VARIABLE ($ptascii("source")) 2,perrorread.BASE) = (perrorread_variable)',
        '~$comparison_read_object(S,perrorread_variable)',
        '$scalar_compare_right_read_shape(BINARY_RIGHT ' + operator + ' (VARIABLE ($ptascii("source")) 1) ' + str(line) + ',VARIABLE ($ptascii("missing")) 2,perrorread.BASE) = (perrorread_right)',
        '~$comparison_read_object(S,perrorread_right)',
        'perrorread_undefined = perrorread' + ('[.INPUT = KNOWN PUNDEFINED][.RESULT = KNOWN PUNDEFINED]' if right else
            '[.ORIGINAL = BINARY_RIGHT ' + operator + ' (KNOWN PUNDEFINED) ' + str(line) + '][.TASK = BINARY_RIGHT ' + operator + ' (KNOWN PUNDEFINED) ' + str(line) + ']'),
        '~$error_read_source(S,perrorread_undefined)',
    ]


def done_checks(start, expected):
    return [
        'S_done = $drive_steps(' + start + ',5000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_done)),HOBJECT n_object) = 0',
        'n_object <- S_done.DESTRUCTION.CALLED',
        r'S_done.DESTRUCTION.CALLS = eps /\ S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],5000)',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],5000) = S_done',
    ]


def destructor_checks(start, before, result, pending='eps'):
    return [
        *seek('S_destructor', start, 5),
        'S_destructor.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_destructor*',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.PENDING = ' + pending,
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        '$call_task_valid(S_destructor,DESTRUCTOR_ENTER pdestructorcall)',
        'n_object <- S_destructor.DESTRUCTION.CALLED',
        '(HOBJECT n_object) <- S_destructor.ALLOCATIONS',
        '$lookup(S_destructor.ENV,$ptascii("result")) = (n_result)',
        'S_destructor.STORE[n_result] = DEFINED (' + result + ')',
        '$us_output(S_destructor.EVENTS) = ' + text(before), '$us_guard(S_destructor)',
    ]


def checks(program, path, name):
    right = name == 'peer-captured-object-greater-equal-default'
    throwing = name == 'peer-captured-object-less-throw'
    values = front(program, path, right, throwing)
    if throwing:
        return values + throw_checks()
    line = 23 if right else 27
    operator = 'GREATEREQUAL' if right else 'EQUAL'
    values += [
        *seek('S_return', 'S_warn', 2),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        'S_return.RESULT = KNOWN (PBOOL ' + ('false' if right else 'true') + ')',
        r'S_return.CURRENT = eps /\ S_return.FRAMES = eps', '$us_guard(S_return)',
        *seek('S_resume', 'S_return', 3),
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)', '$comparison_read_object(S_resume,perrorread)',
        '~$scalar_compare_read_other(S_resume,perrorread)',
        '~$scalar_compare_read_again(S_resume,perrorread)',
        '~$scalar_compare_checked_missing(S_resume,perrorread)',
        '~$scalar_compare_checked_right_missing(S_resume,perrorread)',
        'S_resume.EVENTS = S_return.EVENTS' + (' ++ [$error_default_event(S_return,WARNING ($ptascii("missing")) 23)]' if right else ''),
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', '$us_guard(S_resume)',
        'S_resume.STORE[n_result] = DEFINED (PINT 41)',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HOBJECT n_object) = ' + ('1' if right else '2'),
        '~(n_object <- S_resume.DESTRUCTION.CALLED)',
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps',
        '$heap_owners($heap_prune($heap_graph(S_restored)),HOBJECT n_object) = ' + ('1' if right else '2'),
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS',
        '$heap_owners($heap_prune($heap_graph(S_compared)),HOBJECT n_object) = ' + ('0' if right else '1'),
        *invalid_controls(right, line, operator),
    ]
    if right:
        values += [
            '$lookup(S_resume.ENV,$ptascii("source")) = eps',
            '$lookup(S_resume.ENV,$ptascii("saved")) = eps',
            '$lookup(S_resume.ENV,$ptascii("missing")) = eps',
            *destructor_checks('S_restored', 'H:1:1:23:1;', 'PINT 41'),
            'pdestructionoperation.SOURCE = perrorread.TASK',
            'pdestructionoperation.VALUE = KNOWN (PBOOL false)',
            *done_checks('S_destructor', 'H:1:1:23:1;D:1:1;R:1:1:1:1:1;END;'),
        ]
    else:
        values += [
            'S_resume.STORE[n_source] = DEFINED PNULL',
            '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
            'S_resume.STORE[n_missing] = DEFINED (POBJECT n_object)',
            '$us_guard(S_compared)',
            *destructor_checks('S_compared', 'P;H:1:1:27:1;R:1:1:1:1;', 'PBOOL false'),
            *done_checks('S_destructor', 'P;H:1:1:27:1;R:1:1:1:1;D:1:1;END;'),
        ]
    values += [
        '$drive_steps(S_return,5000) = S_done',
        '$drive_steps(S_restored,5000) = S_done',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],5000) = S_done',
    ]
    return values


def throw_checks():
    return [
        *seek('S_throw', 'S_warn', 4),
        'S_throw.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        r'S_throw.CURRENT = eps /\ S_throw.FRAMES = eps', '$us_guard(S_throw)',
        '$lookup(S_throw.ENV,$ptascii("chosen")) = (n_exception_cell)',
        'S_throw.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
        'n_exception =/= n_object',
        '~$comparison_read_object_value(S_throw,POBJECT n_exception)',
        'perrorread_internal = perrorread[.ORIGINAL = BINARY_RIGHT LESS (KNOWN (POBJECT n_exception)) 29][.TASK = BINARY_RIGHT LESS (KNOWN (POBJECT n_exception)) 29]',
        '$error_read_valid(S_throw,perrorread_internal)',
        '~$comparison_read_object(S_throw,perrorread_internal)',
        '~$scalar_compare_read_other(S_throw,perrorread_internal)',
        '$lookup(S_throw.ENV,$ptascii("source")) = eps',
        '$lookup(S_throw.ENV,$ptascii("missing")) = (n_missing)',
        'S_throw.STORE[n_missing] = DEFINED (PINT 9)',
        'S_throw.STORE[n_result] = DEFINED (PINT 41)',
        '$heap_owners($heap_prune($heap_graph(S_throw)),HOBJECT n_object) = 1',
        '(HOBJECT n_object) <- S_throw.ALLOCATIONS', '~(n_object <- S_throw.DESTRUCTION.CALLED)',
        'PhpStep: S_throw ~> S_discarded',
        'S_discarded = S_throw[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*][.ERRORHANDLER = S.ERRORHANDLER]',
        '$heap_owners($heap_prune($heap_graph(S_discarded)),HOBJECT n_object) = 0',
        *destructor_checks('S_throw', 'P;H:1:1:29:1;', 'PINT 41', '(n_exception)'),
        'pdestructionoperation.PENDING = (n_exception)',
        'pdestructionoperation.SOURCE = THROW_SEARCH n_exception',
        *done_checks('S_destructor', 'P;H:1:1:29:1;D:1:1;C:1:1:1:1:1;F;END;'),
        'S_done.STORE[n_result] = DEFINED (PINT 41)',
        '$drive_steps(S_throw,5000) = S_done',
        'S_zero = $drive_steps(S_throw,0)', 'S_zero = S_throw[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],5000) = S_done',
    ]
