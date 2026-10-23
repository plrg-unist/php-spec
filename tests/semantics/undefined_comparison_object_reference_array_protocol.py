"""Source-reached object reference snapshots, COW and eager release."""
import base64
import json

from undefined_spaceship_protocol import PREFIX as COMMON, text

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
    'BINARY_RIGHT pbin poperand z\n  -- if pbin = SPACESHIP \\/ pbin = EQUAL') + r'''
def $us_stage(S, 4) = true -- if S.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask*
def $us_stage(S, 5) = true
  -- if S.CURRENT =/= eps
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("saved")) = (n_current)
  -- if S_global.STORE[n_current] = DEFINED (PARRAY n_new)
  -- if S.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object))]
  -- if $class_instanceof(S,POBJECT n_object,$ptascii("NewCapturedReference118"))
'''


def seek(target, source, stage):
    return [target + '_found = $us_seek(' + source + ',' + str(stage) + ',2600)',
            target + r'_found.COMPLETION = NORMAL \/ ' + target + '_found.COMPLETION = BUDGET',
            target + ' = ' + target + '_found[.COMPLETION = NORMAL]']


def checks(program, path, name):
    captured = name == 'object-reference-array-captured-singleton'
    operator = 'SPACESHIP' if captured else 'EQUAL'
    line = 27 if captured else 25
    original = ('BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_array)) 27' if captured else
                'BINARY_RIGHT EQUAL (VARIABLE ($ptascii("missing")) z_missing) 25')
    task = original if captured else 'BINARY_RIGHT EQUAL (KNOWN PNULL) 25'
    result = 'PINT 1' if captured else 'PBOOL true'
    before = ('B;N:1:1:1;H:1:1:27:1;' if captured else 'B;O:1:1:1;H:1:1:25:1;')
    expected = before + ('O:1:1:1;R:1:1:1:1:1;END;' if captured else
                         'R:1:1:1:1;A:1:1;N:1:1:1;END;')
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
        '$lookup(S.ENV,$ptascii("copy")) = (n_copy)', 'S.STORE[n_copy] = DEFINED (PARRAY n_array)',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 41)',
        '(HARRAY n_array) <- S.ALLOCATIONS', '~$array_immutable(S,n_array)',
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf)]', 'S.ARRAYS[n_array].NEXT = 1',
        'S.STORE[n_leaf] = DEFINED (POBJECT n_old_object)',
        '$call_reference_operand_valid(S,REFERENCE n_leaf)',
        '(HOBJECT n_old_object) <- S.ALLOCATIONS', 'S.OBJECTS[n_old_object] = INSTANCE porigin_old',
        '$comparison_read_object_value(S,POBJECT n_old_object)',
        '$node_children(S,HARRAY n_array) = [HCELL n_leaf]',
        '$node_children(S,HCELL n_leaf) = [HOBJECT n_old_object]',
        '$spaceship_read_array_entries(S,S.ARRAYS[n_array].ITEMS)',
        '$spaceship_read_array_value(S,PARRAY n_array)',
        '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_array) = ' + ('3' if captured else '2'),
        '$heap_owners($heap_prune($heap_graph(S)),HCELL n_leaf) = ' + ('1' if captured else '3'),
        '$heap_owners($heap_prune($heap_graph(S)),HOBJECT n_old_object) = 1',
        '$us_output(S.EVENTS) = eps', 'S.BORROWEDREAD = eps',
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(line) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
    ]
    if captured:
        values += ['$lookup(S.ENV,$ptascii("leaf")) = eps',
                   '$duplicate_item(S,n_array,ALIAS n_leaf) = DIRECT (POBJECT n_old_object)',
                   '$spaceship_read_array(S,perrorread)', '~$spaceship_read_other(S,perrorread)']
    else:
        values += ['$lookup(S.ENV,$ptascii("leaf")) = (n_leaf)',
                   '$lookup(S.ENV,$ptascii("outside")) = (n_leaf)',
                   '$duplicate_item(S,n_array,ALIAS n_leaf) = ALIAS n_leaf',
                   '$scalar_compare_read_array(S,perrorread)', '~$scalar_compare_read_other(S,perrorread)']
    values += [
        '~$comparison_read_object(S,perrorread)',
        'S_dead_child = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_old_object)]',
        '$error_read_valid(S_dead_child,perrorread)',
        '~$spaceship_read_array_value(S_dead_child,PARRAY n_array)', '$error_read_plan(S_dead_child) = eps',
        'S_dead_cell = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HCELL n_leaf)]',
        '$error_read_valid(S_dead_cell,perrorread)', '$error_read_plan(S_dead_cell) = eps',
        '~$spaceship_read_array_value(S[.REFCELLS = eps],PARRAY n_array)',
        '~$spaceship_read_array_value(S[.STORE[n_leaf] = UNDEFINED],PARRAY n_array)',
        '~$spaceship_read_array_value(S[.STORE[n_leaf] = DEFINED PUNDEFINED],PARRAY n_array)',
        '~$spaceship_read_array_value(S[.STORE[n_leaf] = DEFINED (PARRAY n_array)],PARRAY n_array)',
        '$spaceship_read_array_value(S[.STORE[n_leaf] = DEFINED PNULL],PARRAY n_array)',
        '$spaceship_read_array_value(S[.STORE[n_leaf] = DEFINED (PINT 7)],PARRAY n_array)',
        '~$spaceship_read_array_entries(S,[ENTRY (KINT 0) (ALIAS (|S.STORE|))])',
        '~$spaceship_read_array_entries(S,[ENTRY (KINT 0) (ALIAS n_leaf), ENTRY (KINT 1) UNINITIALIZED])',
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
        'S_resume.STORE[n_missing] = DEFINED (' + ('PBOOL true' if captured else 'PINT 9') + ')',
        'S_resume.STORE[n_current] = DEFINED (PARRAY n_empty)', 'n_empty =/= n_array',
        'S_resume.ARRAYS[n_empty].ITEMS = eps',
        'S_resume.STORE[n_result] = DEFINED (PINT 41)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', 'S_resume.EVENTS = S_return.EVENTS', '$us_guard(S_resume)',
        '$us_output(S_resume.EVENTS) = ' + text(before),
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (' + result + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS', 'S_compared.STORE = S_resume.STORE',
        '$us_guard(S_compared)',
    ]
    if captured:
        values += [
            'S_resume.STORE[n_copy] = DEFINED (PARRAY n_copy_empty)',
            'S_resume.ARRAYS[n_copy_empty].ITEMS = eps',
            '$spaceship_read_array(S_resume,perrorread)',
            'S_resume.STORE[n_leaf] = DEFINED (POBJECT n_old_object)',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HARRAY n_array) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_leaf) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HOBJECT n_old_object) = 1',
            '$heap_owners($heap_prune($heap_graph(S_compared)),HARRAY n_array) = 0',
            '$heap_owners($heap_prune($heap_graph(S_compared)),HCELL n_leaf) = 0',
            '$heap_owners($heap_prune($heap_graph(S_compared)),HOBJECT n_old_object) = 0',
            '~(n_old_object <- S_resume.DESTRUCTION.CALLED)',
            *seek('S_cow', 'S_warn', 5), 'S_cow_global = $global_table_view(S_cow)',
            'S_cow_global.STORE[n_current] = DEFINED (PARRAY n_cow)', 'n_cow =/= n_array',
            'S_cow.ARRAYS[n_cow].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new_object))]',
            'n_new_object =/= n_old_object',
            'S_cow.STORE[n_leaf] = DEFINED (POBJECT n_old_object)',
            '$node_children(S_cow,HARRAY n_array) = [HCELL n_leaf]',
            '$node_children(S_cow,HARRAY n_cow) = [HOBJECT n_new_object]',
            '$us_output(S_cow.EVENTS) = ' + text('B;'), '$us_guard(S_cow)',
            *seek('S_new_destructor', 'S_warn', 4),
            'S_new_destructor.CURRENT =/= eps',
            'S_new_destructor.TODO = (DESTRUCTOR_ENTER pdestructorcall_new) :: ptask_new*',
            'pdestructorcall_new.OBJECT = n_new_object',
            '$us_output(S_new_destructor.EVENTS) = ' + text('B;'),
            'n_new_object <- S_resume.DESTRUCTION.CALLED',
            '~((HOBJECT n_new_object) <- S_resume.ALLOCATIONS)',
            *seek('S_destructor', 'S_restored', 4), 'S_destructor.CURRENT = eps',
            '$us_output(S_destructor.EVENTS) = ' + text(before),
        ]
    else:
        values += [
            '$scalar_compare_read_array(S_resume,perrorread)',
            '~((HOBJECT n_old_object) <- S_resume.ALLOCATIONS)',
            'n_old_object <- S_resume.DESTRUCTION.CALLED',
            'S_resume.STORE[n_leaf] = DEFINED (POBJECT n_new_object)',
            'n_new_object =/= n_old_object',
            '$comparison_read_object_value(S_resume,POBJECT n_new_object)',
            'S_resume.STORE[n_copy] = DEFINED (PARRAY n_array)',
            '$node_children(S_resume,HCELL n_leaf) = [HOBJECT n_new_object]',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HARRAY n_array) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_leaf) = 3',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HOBJECT n_new_object) = 1',
            '$heap_owners($heap_prune($heap_graph(S_compared)),HCELL n_leaf) = 3',
            '$heap_owners($heap_prune($heap_graph(S_compared)),HOBJECT n_new_object) = 1',
            *seek('S_destructor', 'S_warn', 4), 'S_destructor.CURRENT =/= eps',
            '$us_output(S_destructor.EVENTS) = ' + text('B;'),
        ]
    values += [
        'S_destructor_global = $global_table_view(S_destructor)',
        'S_destructor.TODO = (DESTRUCTOR_ENTER pdestructorcall) :: ptask_destructor*',
        'pdestructorcall.OBJECT = n_old_object', 'pdestructorcall.PENDING = eps',
        'pdestructorcall.CALLER = S_destructor.CURRENT',
        '$call_task_valid(S_destructor,DESTRUCTOR_ENTER pdestructorcall)',
        'S_destructor_global.STORE[n_result] = DEFINED (PINT 41)',
        '(HOBJECT n_old_object) <- S_destructor.ALLOCATIONS',
        'n_old_object <- S_destructor.DESTRUCTION.CALLED', '$us_guard(S_destructor)',
    ]
    if captured:
        values += ['pdestructorcall.OPERATION = (pdestructionoperation)',
                   'pdestructionoperation.SOURCE = perrorread.TASK',
                   'pdestructionoperation.VALUE = KNOWN (PINT 1)']
    else:
        values += ['S_destructor_global.STORE[n_leaf] = DEFINED (POBJECT n_new_object)']
    values += [
        'S_done = $drive_steps(S_restored,7000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        'S_done.STORE[n_result] = DEFINED (' + result + ')',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
        '~((HCELL n_leaf) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_old_object) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_new_object) <- S_done.ALLOCATIONS)',
        r'S_done.DESTRUCTION.CALLS = eps /\ S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],7000)',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],7000) = S_done',
        '$drive_steps(S_return,7000) = S_done',
        '$drive_steps(S_destructor,7000) = S_done',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],7000) = S_done',
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
