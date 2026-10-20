"""Captured TASK/RESULT objects survive callbacks and retire before the store."""
import base64
import json

from undefined_spaceship_protocol import PREFIX as COMMON, text

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
    'BINARY_RIGHT pbin poperand z\n  -- if pbin = SPACESHIP \\/ pbin = EQUAL') + r'''
def $us_stage(S, 4) = true -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask*
'''


def seek(target, source, stage):
    return [target + '_found = $us_seek(' + source + ',' + str(stage) + ',2000)',
            target + r'_found.COMPLETION = NORMAL \/ ' + target + '_found.COMPLETION = BUDGET',
            target + ' = ' + target + '_found[.COMPLETION = NORMAL]']


def checks(program, path, name):
    equal = name == 'captured-object-equal-right'
    operator = 'EQUAL' if equal else 'SPACESHIP'
    line = 24 if equal else 18
    original = ('BINARY_RIGHT EQUAL (VARIABLE ($ptascii("missing")) z_missing) 24'
                if equal else 'BINARY_RIGHT SPACESHIP (KNOWN (POBJECT n_object)) 18')
    task = 'BINARY_RIGHT EQUAL (KNOWN PNULL) 24' if equal else original
    result = 'PBOOL false' if equal else 'PINT 1'
    before = 'H:1:1:' + str(line) + ':1;'
    expected = before + ('D:1:1;R:1:1:1:1:1:1;END;' if equal else 'D:1;R:1:1:1:1;END;')
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S_front', 'S_initial', 0),
        'S = S_front', '$us_stage(S,0)', '$us_guard(S)',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        '$error_read_plan(S) = (perrorread)', '$error_read_source(S,perrorread)',
        '$error_read_valid(S,perrorread)', 'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
        'S.RESULT = perrorread.INPUT', 'perrorread.ORIGINAL = ' + original,
        'perrorread.TASK = ' + task,
        'perrorread.INPUT = ' + ('KNOWN (POBJECT n_object)' if equal else 'VARIABLE ($ptascii("missing")) z_missing'),
        'perrorread.RESULT = ' + ('perrorread.INPUT' if equal else 'KNOWN PNULL'),
        'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = ' + str(line),
        '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        '$spaceship_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = eps',
        '$scalar_compare_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = eps',
        '$comparison_read_object(S,perrorread)', '$comparison_read_object_value(S,POBJECT n_object)',
        '~$spaceship_read_array(S,perrorread)', '~$scalar_compare_read_array(S,perrorread)',
        '~$scalar_compare_missing_pair(S,perrorread)',
        '$task_nodes(ERROR_READ_RESULT perrorread) = [HOBJECT n_object]',
        '$base_nodes(perrorread.BASE) = eps',
        '(HOBJECT n_object) <- S.ALLOCATIONS', 'S.OBJECTS[n_object] = INSTANCE porigin_class',
        '~$instance_storage_freeing(S,n_object)',
        '~$class_instanceof(S,POBJECT n_object,$ptascii("Stringable"))',
        '~(n_object <- S.DESTRUCTION.CALLED)',
        '$lookup(S.ENV,$ptascii("saved")) = (n_saved)',
        'S.STORE[n_saved] = DEFINED (POBJECT n_object)',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 41)',
        '$heap_owners($heap_prune($heap_graph(S)),HOBJECT n_object) = ' + ('3' if equal else '2'),
        '$us_output(S.EVENTS) = eps', 'S.BORROWEDREAD = eps',
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_warn = $prune_allocations($error_read_begin(S))',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = ' + str(line),
        'perrorcall.MESSAGE = $ptascii("Undefined variable $missing")',
        'perrorcall.EVENT = WARNING ($ptascii("missing")) ' + str(line),
        '$error_call_valid(S_warn,perrorcall)', 'S_warn.EVENTS = S.EVENTS', '$us_guard(S_warn)',
        *seek('S_return', 'S_warn', 2),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        'S_return.RESULT = KNOWN (PBOOL true)',
        r'S_return.CURRENT = eps /\ S_return.FRAMES = eps', '$us_guard(S_return)',
        *seek('S_resume', 'S_return', 3),
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)', '$comparison_read_object(S_resume,perrorread)',
        '~$spaceship_read_again(S_resume,perrorread)',
        '~$scalar_compare_read_again(S_resume,perrorread)',
        '~$spaceship_checked_missing(S_resume,perrorread)',
        '~$scalar_compare_checked_missing(S_resume,perrorread)',
        '~$scalar_compare_checked_right_missing(S_resume,perrorread)',
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
        'S_resume.STORE[n_missing] = DEFINED (PINT 9)',
        'S_resume.STORE[n_result] = DEFINED (PINT 41)',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HOBJECT n_object) = 1',
        '(HOBJECT n_object) <- S_resume.ALLOCATIONS', '~(n_object <- S_resume.DESTRUCTION.CALLED)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', 'S_resume.EVENTS = S_return.EVENTS',
        '$us_output(S_resume.EVENTS) = ' + text(before), '$us_guard(S_resume)',
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps',
        '$heap_owners($heap_prune($heap_graph(S_restored)),HOBJECT n_object) = 1',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (' + result + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS', 'S_compared.STORE = S_resume.STORE',
        '$heap_owners($heap_prune($heap_graph(S_compared)),HOBJECT n_object) = 0',
        *seek('S_destructor', 'S_restored', 4),
        'S_destructor.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_destructor*',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.PENDING = eps',
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = perrorread.TASK',
        'pdestructionoperation.VALUE = KNOWN (' + result + ')',
        '$call_task_valid(S_destructor,DESTRUCTOR_ENTER pdestructorcall)',
        '(HOBJECT n_object) <- S_destructor.ALLOCATIONS',
        'n_object <- S_destructor.DESTRUCTION.CALLED',
        'S_destructor.STORE[n_result] = DEFINED (PINT 41)',
        '$us_output(S_destructor.EVENTS) = ' + text(before), '$us_guard(S_destructor)',
        'S_done = $drive_steps(S_destructor,5000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        'S_done.STORE[n_result] = DEFINED (' + result + ')',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_done)),HOBJECT n_object) = 0',
        'n_object <- S_done.DESTRUCTION.CALLED',
        r'S_done.DESTRUCTION.CALLS = eps /\ S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],5000)',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],5000) = S_done',
        '$drive_steps(S_return,5000) = S_done', '$drive_steps(S_restored,5000) = S_done',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],5000) = S_done',
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(line) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
        '~$error_read_valid(S[.CODE = eps],perrorread)', '$error_read_plan(S[.CODE = eps]) = eps',
        '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_object)]',
        '$error_read_valid(S_dead,perrorread)', '~$comparison_read_object(S_dead,perrorread)',
        '$error_read_plan(S_dead) = eps',
        '~$comparison_read_object_value(S,POBJECT (|S.OBJECTS|))',
        '~$comparison_read_object_value(S,PUNDEFINED)',
        '~$comparison_read_object_value(S,PARRAY 0)',
        'perrorread_line = perrorread[.ORIGINAL = ' + original.rsplit(' ', 1)[0] + ' 999][.TASK = ' + task.rsplit(' ', 1)[0] + ' 999][.LINE = 999]',
        '$comparison_read_object(S,perrorread_line)', '~$error_read_valid(S,perrorread_line)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_line])',
        'perrorread_foreign = perrorread[.ORIGINAL = ' + original.replace(operator, 'BITXOR') + '][.TASK = ' + task.replace(operator, 'BITXOR') + ']',
        '~$comparison_read_object(S,perrorread_foreign)', '~$error_read_valid(S,perrorread_foreign)',
        '$error_read_plan(S[.TODO = perrorread_foreign.ORIGINAL :: ptask_tail*]) = eps',
        '$error_read_shape(BINARY_RIGHT ' + operator + ' (VARIABLE ($ptascii("missing")) 1) ' + str(line) + ',VARIABLE ($ptascii("saved")) 2,perrorread.BASE) = (perrorread_variable)',
        '$comparison_read_object(S,perrorread_variable)',
        '~$error_read_source(S,perrorread_variable)', '~$error_read_valid(S,perrorread_variable)',
    ]
    if equal:
        values += [
            '~$scalar_compare_read_other(S,perrorread)', '~$scalar_compare_read_other(S_dead,perrorread)',
            '$lookup(S.ENV,$ptascii("source")) = (n_source)',
            '$lookup(S.ENV,$ptascii("alias")) = (n_source)', 'n_source =/= n_saved',
            'S.STORE[n_source] = DEFINED (POBJECT n_object)', 'n_source <- S.REFCELLS',
            '$heap_owners($heap_prune($heap_graph(S)),HCELL n_source) = 2',
            '$lookup(S_resume.ENV,$ptascii("alias")) = eps',
            'S_resume.STORE[n_source] = DEFINED PNULL',
            'S_resume.STORE[n_saved] = DEFINED PNULL',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_source) = 1',
            'perrorread_name = perrorread[.ORIGINAL = BINARY_RIGHT EQUAL (VARIABLE ($ptascii("foreign")) z_missing) 24][.NAME = $ptascii("foreign")]',
        ]
    else:
        values += [
            '~$spaceship_read_other(S,perrorread)', '~$spaceship_read_other(S_dead,perrorread)',
            '$lookup(S_resume.ENV,$ptascii("saved")) = eps',
            'perrorread_name = perrorread[.INPUT = VARIABLE ($ptascii("foreign")) z_missing][.NAME = $ptascii("foreign")]',
        ]
    values += [
        '$error_read_shape(perrorread_name.ORIGINAL,perrorread_name.INPUT,perrorread_name.BASE) = (perrorread_name)',
        '~$error_read_source(S,perrorread_name)',
    ]
    return values
