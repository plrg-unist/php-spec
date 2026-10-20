"""Captured/current tables and transitive child release at missing reads."""
import base64
import json

from undefined_spaceship_protocol import PREFIX as COMMON, text

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
    'BINARY_RIGHT pbin poperand z\n  -- if pbin = SPACESHIP \\/ pbin = EQUAL') + r'''
def $us_stage(S, 4) = true -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask*
'''


def seek(target, source, stage):
    return [target + '_found = $us_seek(' + source + ',' + str(stage) + ',2200)',
            target + r'_found.COMPLETION = NORMAL \/ ' + target + '_found.COMPLETION = BUDGET',
            target + ' = ' + target + '_found[.COMPLETION = NORMAL]']


def checks(program, path, name):
    captured = name == 'object-array-captured-spaceship-left'
    operator = 'SPACESHIP' if captured else 'EQUAL'
    line = 20 if captured else 18
    original = ('BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_array)) 20' if captured else
                'BINARY_RIGHT EQUAL (VARIABLE ($ptascii("missing")) z_missing) 18')
    task = original if captured else 'BINARY_RIGHT EQUAL (KNOWN PNULL) 18'
    result = 'PINT 1' if captured else 'PBOOL true'
    before = 'H:1:1:' + str(line) + ':1;'
    expected = before + ('D:1:1;R:1:1:1:1;END;' if captured else 'D:1:1;A;R:1:1:1:1;END;')
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S_front', 'S_initial', 0),
        'S = S_front', '$us_stage(S,0)', '$us_guard(S)',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        '$error_read_plan(S) = (perrorread)', '$error_read_source(S,perrorread)',
        '$error_read_valid(S,perrorread)', 'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
        'S.RESULT = perrorread.INPUT', 'perrorread.ORIGINAL = ' + original,
        'perrorread.TASK = ' + task,
        'perrorread.INPUT = VARIABLE ($ptascii("' + ('missing' if captured else 'right') + '")) ' + ('z_missing' if captured else 'z_right'),
        'perrorread.RESULT = ' + ('KNOWN PNULL' if captured else 'perrorread.INPUT'),
        'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = ' + str(line),
        '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        '$spaceship_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = eps',
        '$task_nodes(ERROR_READ_RESULT perrorread) = ' + ('[HARRAY n_array]' if captured else 'eps'),
        '$base_nodes(perrorread.BASE) = eps',
        '$lookup(S.ENV,$ptascii("' + ('saved' if captured else 'right') + '")) = (n_current)',
        'S.STORE[n_current] = DEFINED (PARRAY n_array)',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 41)',
        '(HARRAY n_array) <- S.ALLOCATIONS', '~(n_array <- S.IMMUTABLE)',
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object))]',
        'S.ARRAYS[n_array].NEXT = 1',
        '(HOBJECT n_object) <- S.ALLOCATIONS', 'S.OBJECTS[n_object] = INSTANCE porigin_class',
        '$comparison_read_object_value(S,POBJECT n_object)',
        '~$instance_storage_freeing(S,n_object)', '~(n_object <- S.DESTRUCTION.CALLED)',
        '$spaceship_read_array_entries(S,S.ARRAYS[n_array].ITEMS)',
        '$spaceship_read_array_value(S,PARRAY n_array)',
        '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_array) = ' + ('2' if captured else '1'),
        '$heap_owners($heap_prune($heap_graph(S)),HOBJECT n_object) = 1',
        '$us_output(S.EVENTS) = eps', 'S.BORROWEDREAD = eps',
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(line) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
    ]
    if captured:
        values += ['$spaceship_read_array(S,perrorread)', '~$spaceship_read_other(S,perrorread)']
    else:
        values += ['$scalar_compare_read_array(S,perrorread)', '~$scalar_compare_read_other(S,perrorread)']
    values += [
        '~$comparison_read_object(S,perrorread)',
        'S_dead_child = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_object)]',
        '$error_read_valid(S_dead_child,perrorread)',
        '~$spaceship_read_array_value(S_dead_child,PARRAY n_array)', '$error_read_plan(S_dead_child) = eps',
        'S_dead_table = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_array)]',
        '$error_read_valid(S_dead_table,perrorread)', '$error_read_plan(S_dead_table) = eps',
        '~$spaceship_read_array_entries(S,[ENTRY (KINT 0) (ALIAS n_current)])',
        '~$spaceship_read_array_entries(S,[ENTRY (KINT 0) (DIRECT (PARRAY n_array))])',
        '~$spaceship_read_array_entries(S,[ENTRY (KINT 0) (DIRECT PUNDEFINED)])',
        '~$spaceship_read_array_entries(S,[ENTRY (KINT 0) (DIRECT (POBJECT (|S.OBJECTS|)))])',
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_warn = $prune_allocations($error_read_begin(S))',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = ' + str(line),
        'perrorcall.MESSAGE = $ptascii("Undefined variable $missing")',
        'perrorcall.EVENT = WARNING ($ptascii("missing")) ' + str(line),
        '$error_call_valid(S_warn,perrorcall)', '$us_guard(S_warn)', 'S_warn.EVENTS = S.EVENTS',
        *seek('S_return', 'S_warn', 2),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        'S_return.RESULT = KNOWN (PBOOL true)',
        r'S_return.CURRENT = eps /\ S_return.FRAMES = eps', '$us_guard(S_return)',
        *seek('S_resume', 'S_return', 3),
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)',
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
        'S_resume.STORE[n_missing] = DEFINED (PINT 9)',
        'S_resume.STORE[n_current] = DEFINED (PARRAY n_empty)', 'n_empty =/= n_array',
        'S_resume.ARRAYS[n_empty].ITEMS = eps',
        'S_resume.STORE[n_result] = DEFINED (PINT 41)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', 'S_resume.EVENTS = S_return.EVENTS', '$us_guard(S_resume)',
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (' + result + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS', 'S_compared.STORE = S_resume.STORE',
        '$heap_owners($heap_prune($heap_graph(S_compared)),HARRAY n_array) = 0',
        '$heap_owners($heap_prune($heap_graph(S_compared)),HOBJECT n_object) = 0',
        '$us_guard(S_compared)',
    ]
    if captured:
        values += [
            '$spaceship_read_array(S_resume,perrorread)',
            '(HARRAY n_array) <- S_resume.ALLOCATIONS', '(HOBJECT n_object) <- S_resume.ALLOCATIONS',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HARRAY n_array) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HOBJECT n_object) = 1',
            '~(n_object <- S_resume.DESTRUCTION.CALLED)', '$us_output(S_resume.EVENTS) = ' + text(before),
            *seek('S_destructor', 'S_restored', 4), 'S_destructor.CURRENT = eps',
            'S_destructor_global = $global_table_view(S_destructor)',
            '$us_output(S_destructor.EVENTS) = ' + text(before),
        ]
    else:
        values += [
            '$scalar_compare_read_array(S_resume,perrorread)',
            '~((HARRAY n_array) <- S_resume.ALLOCATIONS)', '~((HOBJECT n_object) <- S_resume.ALLOCATIONS)',
            'n_object <- S_resume.DESTRUCTION.CALLED',
            '$us_output(S_resume.EVENTS) = ' + text(before + 'D:1:1;A;'),
            *seek('S_destructor', 'S_warn', 4), 'S_destructor.CURRENT =/= eps',
            'S_destructor_global = $global_table_view(S_destructor)',
            'S_destructor_global.STORE[n_current] = DEFINED (PARRAY n_empty)',
            '$lookup(S_destructor_global.ENV,$ptascii("missing")) = eps',
            '$us_output(S_destructor.EVENTS) = ' + text(before),
        ]
    values += [
        'S_destructor.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_destructor*',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.PENDING = eps',
        'pdestructorcall.OPERATION = (pdestructionoperation)',
        *(['pdestructionoperation.SOURCE = perrorread.TASK',
           'pdestructionoperation.VALUE = KNOWN (PINT 1)'] if captured else []),
        'pdestructorcall.CALLER = S_destructor.CURRENT',
        '$call_task_valid(S_destructor,DESTRUCTOR_ENTER pdestructorcall)',
        'S_destructor_global.STORE[n_result] = DEFINED (PINT 41)',
        '(HOBJECT n_object) <- S_destructor.ALLOCATIONS', 'n_object <- S_destructor.DESTRUCTION.CALLED',
        '$us_guard(S_destructor)',
        'S_done = $drive_steps(S_destructor,6000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        'S_done.STORE[n_result] = DEFINED (' + result + ')',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
        r'S_done.DESTRUCTION.CALLS = eps /\ S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],6000)',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],6000) = S_done',
        '$drive_steps(S_return,6000) = S_done', '$drive_steps(S_restored,6000) = S_done',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],6000) = S_done',
        '~$error_read_valid(S[.CODE = eps],perrorread)', '$error_read_plan(S[.CODE = eps]) = eps',
        '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        'perrorread_line = perrorread[.ORIGINAL = ' + original.rsplit(' ', 1)[0] + ' 999][.TASK = ' + task.rsplit(' ', 1)[0] + ' 999][.LINE = 999]',
        ('$spaceship_read_array(S,perrorread_line)' if captured else '$scalar_compare_read_array(S,perrorread_line)'),
        '~$error_read_valid(S,perrorread_line)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_line])',
        'perrorread_foreign = perrorread[.ORIGINAL = ' + original.replace(operator, 'BITXOR') + '][.TASK = ' + task.replace(operator, 'BITXOR') + ']',
        '~$error_read_valid(S,perrorread_foreign)',
        '$error_read_plan(S[.TODO = perrorread_foreign.ORIGINAL :: ptask_tail*]) = eps',
    ]
    return values
