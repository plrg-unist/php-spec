"""Singleton outer unwrapping, child snapshots and delayed outside release."""
import base64
import json

from undefined_spaceship_protocol import text
from undefined_comparison_object_reference_array_review_protocol import (
    PREFIX as COMMON, owners, seek)

PREFIX = COMMON + r'''
def $us_stage(S, 6) = true
  -- if S.CURRENT =/= eps
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("saved")) = (n_current)
  -- if S_global.STORE[n_current] = DEFINED (PARRAY n_parent)
  -- if S.ARRAYS[n_parent].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_child))]
  -- if S.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object)), ENTRY (KINT 1) (DIRECT (PINT 9))]
  -- if $class_instanceof(S,POBJECT n_object,$ptascii("NewCapturedChild119"))
'''


def entered(target, source, obj, output, inside, result='PINT 41'):
    return [
        *seek(target, source, 5),
        target + '.TODO = (DESTRUCTOR_ENTER pdestructorcall_' + target + ') :: ptask_destructor_' + target + '*',
        'pdestructorcall_' + target + '.OBJECT = ' + obj,
        'pdestructorcall_' + target + '.PENDING = eps',
        'pdestructorcall_' + target + '.CALLER = ' + target + '.CURRENT',
        '$call_task_valid(' + target + ',DESTRUCTOR_ENTER pdestructorcall_' + target + ')',
        target + '.CURRENT ' + ('=/= eps' if inside else '= eps'),
        target + '.STORE[n_result] = DEFINED (' + result + ')',
        obj + ' <- ' + target + '.DESTRUCTION.CALLED',
        '(HOBJECT ' + obj + ') <- ' + target + '.ALLOCATIONS',
        '$us_output(' + target + '.EVENTS) = ' + text(output), '$us_guard(' + target + ')',
    ]


def expected(captured):
    before = ('P;B;I:1:1:1:1;N:1:1:1;H:1:1:29:1;' if captured
              else 'B;I:1:1:1:1;O:1:1:1;H:1:1:28:1;')
    after = ('O:1:1:1;R:1:1:1:1:1;END;' if captured
             else 'R:1:1:1:1:1:1:1;A:1:1;N:1:1:1;END;')
    return before, before + after


def initial(program, path):
    return [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S_front', 'S_initial', 0),
        'S = S_front', '$error_read_plan(S) = (perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
    ]


def warning(line):
    return [
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


def returned():
    return [
        *seek('S_return', 'S_warn', 2),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        'S_return.RESULT = KNOWN (PBOOL true)',
        r'S_return.CURRENT = eps /\ S_return.FRAMES = eps', '$us_guard(S_return)',
        *seek('S_resume', 'S_return', 3),
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)', '$us_guard(S_resume)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', 'S_resume.EVENTS = S_return.EVENTS',
    ]


def restored(captured):
    result = 'PINT 1' if captured else 'PBOOL true'
    return [
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps', 'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (' + result + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS', 'S_compared.STORE = S_resume.STORE', '$us_guard(S_compared)',
    ]


def controls(captured):
    read = '$spaceship_read_array' if captured else '$scalar_compare_read_array'
    return [
        '$comparison_read_array_payload(S,PARRAY n_child_old)',
        '~$comparison_read_array_payload(S,PARRAY n_array)',
        '~$spaceship_read_array_entries(S,[ENTRY (KINT 0) (DIRECT (PARRAY n_child_old))])',
        'S_dead_child = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_child_old)]',
        '~$comparison_read_array_payload(S_dead_child,PARRAY n_child_old)',
        '~' + read + '(S_dead_child,perrorread)', '$error_read_valid(S_dead_child,perrorread)',
        '~$comparison_read_array_payload(S,PARRAY (|S.ARRAYS|))',
        'S_cycle = S[.ARRAYS[n_child_old].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf)]]',
        '~$comparison_read_array_payload(S_cycle,PARRAY n_child_old)',
        '~' + read + '(S_cycle,perrorread)', '$error_read_valid(S_cycle,perrorread)',
        'S_deeper = S[.ARRAYS[n_child_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_array))]]',
        '~' + read + '(S_deeper,perrorread)', '$error_read_valid(S_deeper,perrorread)',
        '~$comparison_read_array_payload(S[.ARRAYS[n_child_old].ITEMS = [ENTRY (KINT 0) UNINITIALIZED]],PARRAY n_child_old)',
        'S_dead_object = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_old)]',
        '~' + read + '(S_dead_object,perrorread)', '$error_read_valid(S_dead_object,perrorread)',
        '~' + read + '(S[.REFCELLS = eps],perrorread)',
        '~' + read + '(S[.STORE[n_leaf] = UNDEFINED],perrorread)',
        '~' + read + '(S[.STORE[n_leaf] = DEFINED PUNDEFINED],perrorread)',
        '~$error_read_valid(S[.CODE = eps],perrorread)', '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        '~$error_call_valid(S_warn,perrorcall[.LEVEL = 8])',
        '~$error_call_valid(S_warn,perrorcall[.MESSAGE = eps])',
    ]


def core(program, path, captured):
    line = 29 if captured else 28
    original = ('BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_array)) 29' if captured
                else 'BINARY_RIGHT EQUAL (VARIABLE ($ptascii("missing")) z_missing) 28')
    task = original if captured else 'BINARY_RIGHT EQUAL (KNOWN PNULL) 28'
    before, output = expected(captured)
    values = initial(program, path) + [
        '$us_stage(S,0)', '$us_guard(S)', '$error_read_valid(S,perrorread)',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        'perrorread.ORIGINAL = ' + original, 'perrorread.TASK = ' + task,
        'perrorread.INPUT = VARIABLE ($ptascii("' + ('missing' if captured else 'right') + '")) ' + ('z_missing' if captured else 'z_right'),
        'perrorread.RESULT = ' + ('KNOWN PNULL' if captured else 'perrorread.INPUT'),
        'S.RESULT = perrorread.INPUT', 'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = ' + str(line),
        '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        '$base_nodes(perrorread.BASE) = eps',
        '$task_nodes(ERROR_READ_RESULT perrorread) = ' + ('[HARRAY n_array]' if captured else 'eps'),
        '$lookup(S.ENV,$ptascii("' + ('saved' if captured else 'right') + '")) = (n_current)',
        'S.STORE[n_current] = DEFINED (PARRAY n_array)',
        '$lookup(S.ENV,$ptascii("copy")) = (n_copy)', 'S.STORE[n_copy] = DEFINED (PARRAY n_array)',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 41)',
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf)]', 'S.ARRAYS[n_array].NEXT = 1',
        'S.STORE[n_leaf] = DEFINED (PARRAY n_child_old)', 'n_child_old =/= n_array',
        'S.ARRAYS[n_child_old].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old)), ENTRY (KINT 1) (DIRECT (PINT 4))]',
        'S.ARRAYS[n_child_old].NEXT = 2', '$comparison_read_object_value(S,POBJECT n_old)',
        '$call_reference_operand_valid(S,REFERENCE n_leaf)', '~$array_immutable(S,n_child_old)',
        '$heap_count(HARRAY n_child_old,$pools_nodes(S.POOLS)) = 0',
        '$node_children(S,HARRAY n_array) = [HCELL n_leaf]',
        '$node_children(S,HCELL n_leaf) = [HARRAY n_child_old]',
        '$node_children(S,HARRAY n_child_old) = [HOBJECT n_old]',
        owners('S', 'HARRAY n_array', 3 if captured else 2),
        owners('S', 'HCELL n_leaf', 1 if captured else 3),
        owners('S', 'HARRAY n_child_old', 1 if captured else 2), owners('S', 'HOBJECT n_old', 1),
        '$us_output(S.EVENTS) = ' + text('P;' if captured else ''),
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(line) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
    ]
    if captured:
        values += [
            '$lookup(S.ENV,$ptascii("leaf")) = eps',
            '$duplicate_item(S,n_array,ALIAS n_leaf) = DIRECT (PARRAY n_child_old)',
            '$spaceship_read_array(S,perrorread)', '~$spaceship_read_other(S,perrorread)',
        ]
    else:
        values += [
            '$lookup(S.ENV,$ptascii("leaf")) = (n_leaf)', '$lookup(S.ENV,$ptascii("outside")) = (n_leaf)',
            '$lookup(S.ENV,$ptascii("held")) = (n_held)', 'S.STORE[n_held] = DEFINED (PARRAY n_child_old)',
            '$duplicate_item(S,n_array,ALIAS n_leaf) = ALIAS n_leaf',
            '$scalar_compare_read_array(S,perrorread)', '~$scalar_compare_read_other(S,perrorread)',
        ]
    values += warning(line) + controls(captured) + returned() + [
        'S_resume.STORE[n_result] = DEFINED (PINT 41)',
        'S_resume.STORE[n_current] = DEFINED (PARRAY n_empty)', 'S_resume.ARRAYS[n_empty].ITEMS = eps',
        '$us_output(S_resume.EVENTS) = ' + text(before),
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
        'S_resume.STORE[n_missing] = DEFINED (' + ('PBOOL true' if captured else 'PINT 9') + ')',
    ] + restored(captured)
    if captured:
        values += [
            'S_resume.STORE[n_leaf] = DEFINED (PARRAY n_child_old)',
            'S_resume.STORE[n_copy] = DEFINED (PARRAY n_copy_empty)', 'S_resume.ARRAYS[n_copy_empty].ITEMS = eps',
            owners('S_resume', 'HARRAY n_array', 1), owners('S_resume', 'HCELL n_leaf', 1),
            owners('S_resume', 'HARRAY n_child_old', 1), owners('S_resume', 'HOBJECT n_old', 1),
            owners('S_compared', 'HARRAY n_array', 0), owners('S_compared', 'HCELL n_leaf', 0),
            owners('S_compared', 'HARRAY n_child_old', 0), owners('S_compared', 'HOBJECT n_old', 0),
            *seek('S_cow', 'S_warn', 6), '$us_guard(S_cow)', 'S_cow_global = $global_table_view(S_cow)',
            'S_cow_global.STORE[n_current] = DEFINED (PARRAY n_parent_new)', 'n_parent_new =/= n_array',
            'S_cow.ARRAYS[n_parent_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_child_new))]',
            'n_child_new =/= n_child_old',
            'S_cow.ARRAYS[n_child_new].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new)), ENTRY (KINT 1) (DIRECT (PINT 9))]',
            'S_cow.STORE[n_leaf] = DEFINED (PARRAY n_child_old)',
            'S_cow.ARRAYS[n_child_old] = S.ARRAYS[n_child_old]',
            '$node_children(S_cow,HARRAY n_parent_new) = [HARRAY n_child_new]',
            '$node_children(S_cow,HARRAY n_child_new) = [HOBJECT n_new]',
            '$us_output(S_cow.EVENTS) = ' + text('P;B;'),
            *entered('S_inline', 'S_warn', 'n_new', 'P;B;I:1:1:1:1;', True),
            'n_new <- S_resume.DESTRUCTION.CALLED', '~((HOBJECT n_new) <- S_resume.ALLOCATIONS)',
            '~((HARRAY n_child_new) <- S_resume.ALLOCATIONS)',
            *entered('S_last', 'S_restored', 'n_old', before, False),
            'pdestructorcall_S_last.OPERATION = (pdestructionoperation_last)',
            'pdestructionoperation_last.SOURCE = perrorread.TASK', 'pdestructionoperation_last.VALUE = KNOWN (PINT 1)',
        ]
    else:
        values += [
            'S_resume.STORE[n_leaf] = DEFINED (PARRAY n_child_new)',
            'n_child_new =/= n_child_old',
            'S_resume.ARRAYS[n_child_new].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new)), ENTRY (KINT 1) (DIRECT (PINT 7))]',
            'S_resume.STORE[n_copy] = DEFINED (PARRAY n_array)', 'S_resume.STORE[n_held] = DEFINED (PARRAY n_held_empty)',
            'S_resume.ARRAYS[n_held_empty].ITEMS = eps',
            '~((HARRAY n_child_old) <- S_resume.ALLOCATIONS)', '~((HOBJECT n_old) <- S_resume.ALLOCATIONS)',
            'n_old <- S_resume.DESTRUCTION.CALLED', '~(n_new <- S_resume.DESTRUCTION.CALLED)',
            '$node_children(S_resume,HCELL n_leaf) = [HARRAY n_child_new]',
            owners('S_resume', 'HARRAY n_array', 1), owners('S_resume', 'HCELL n_leaf', 3),
            owners('S_resume', 'HARRAY n_child_new', 1), owners('S_resume', 'HOBJECT n_new', 1),
            owners('S_compared', 'HARRAY n_child_new', 1), owners('S_compared', 'HOBJECT n_new', 1),
            *entered('S_old', 'S_warn', 'n_old', 'B;I:1:1:1:1;', True),
            'S_old.STORE[n_leaf] = DEFINED (PARRAY n_child_new)',
            *entered('S_last', 'S_compared', 'n_new', before + 'R:1:1:1:1:1:1:1;A:1:1;', False, 'PBOOL true'),
        ]
    return values + [
        'S_done = $drive_steps(S_last,8000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        'S_done.STORE[n_result] = DEFINED (' + ('PINT 1' if captured else 'PBOOL true') + ')',
        '$us_output(S_done.EVENTS) = ' + text(output), '$us_guard(S_done)',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        *['~((' + node + ') <- S_done.ALLOCATIONS)' for node in
          ('HARRAY n_array', 'HCELL n_leaf', 'HARRAY n_child_old', 'HARRAY n_child_new', 'HOBJECT n_old', 'HOBJECT n_new')],
        r'S_done.DESTRUCTION.CALLS = eps /\ S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
        'n_old <- S_done.DESTRUCTION.CALLED', 'n_new <- S_done.DESTRUCTION.CALLED',
    ]


def budgets(program, path, captured):
    _, output = expected(captured)
    return initial(program, path) + [
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]',
        *seek('S_return', 'S_warn', 2), *seek('S_resume', 'S_return', 3),
        'PhpStep: S_resume ~> S_restored', 'PhpStep: S_restored ~> S_compared',
        'S_done = $drive_steps(S_compared,8000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(output), '$us_guard(S_done)',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],8000)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],8000) = S_done',
    ]


def checks(program, path, name):
    captured = name.startswith('array-payload-captured-singleton-')
    assert captured or name.startswith('array-payload-live-replacement-')
    return (budgets if name.endswith('-budget') else core)(program, path, captured)
