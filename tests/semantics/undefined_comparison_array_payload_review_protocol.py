"""Reached ARRAY-to-CELL-to-ARRAY-to-OBJECT ownership and abrupt release."""
import base64
import json

from undefined_spaceship_protocol import text
from undefined_comparison_object_reference_array_review_protocol import (
    PREFIX as COMMON, destructor, owners, seek)

PREFIX = COMMON + r'''
def $us_stage(S, 6) = true
  -- if S.CURRENT =/= eps
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("inner")) = (n_inner)
  -- if $lookup(S_global.ENV,$ptascii("leaf")) = (n_leaf)
  -- if S_global.STORE[n_inner] = DEFINED (PARRAY n_first)
  -- if S_global.STORE[n_leaf] = DEFINED (PARRAY n_changed)
  -- if n_first =/= n_changed
  -- if S.ARRAYS[n_first].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object))]
  -- if S.ARRAYS[n_changed].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object)), ENTRY (KINT 1) (DIRECT (PINT 9))]
'''


def controls():
    return [
        '$comparison_read_array_payload(S,PARRAY n_child_old)',
        '~$comparison_read_array_payload(S,PARRAY n_array)',
        '$spaceship_read_array_entries(S,[ENTRY (KINT 0) (DIRECT (PARRAY n_child_old))])',
        'S_dead_child = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_child_old)]',
        '~$comparison_read_array_payload(S_dead_child,PARRAY n_child_old)',
        '~$spaceship_read_array(S_dead_child,perrorread)', '$error_read_valid(S_dead_child,perrorread)',
        '~$comparison_read_array_payload(S,PARRAY (|S.ARRAYS|))',
        'S_child_alias = S[.ARRAYS[n_child_old].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf)]]',
        '~$comparison_read_array_payload(S_child_alias,PARRAY n_child_old)',
        '~$spaceship_read_array(S_child_alias,perrorread)', '$error_read_valid(S_child_alias,perrorread)',
        'S_child_nested = S[.ARRAYS[n_child_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_array))]]',
        '~$spaceship_read_array(S_child_nested,perrorread)', '$error_read_valid(S_child_nested,perrorread)',
        '~$comparison_read_array_payload(S[.ARRAYS[n_child_old].ITEMS = [ENTRY (KINT 0) UNINITIALIZED]],PARRAY n_child_old)',
        '~$comparison_read_array_payload(S[.ARRAYS[n_child_old].ITEMS = [ENTRY (KINT 0) (INDIRECT n_old ($ptascii("tag")))]],PARRAY n_child_old)',
        'S_dead_object = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_old)]',
        '~$spaceship_read_array(S_dead_object,perrorread)', '$error_read_valid(S_dead_object,perrorread)',
        'S_dead_cell = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HCELL n_leaf)]',
        '~$spaceship_read_array(S_dead_cell,perrorread)',
        '~$spaceship_read_array(S[.REFCELLS = eps],perrorread)',
        '~$spaceship_read_array(S[.STORE[n_leaf] = UNDEFINED],perrorread)',
        '~$spaceship_read_array(S[.STORE[n_leaf] = DEFINED PUNDEFINED],perrorread)',
        '~$spaceship_read_array_entries(S,[ENTRY (KINT 0) (ALIAS (|S.STORE|))])',
        '~$error_read_valid(S[.CODE = eps],perrorread)', '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        'perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_array)) 999][.TASK = BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_array)) 999][.LINE = 999]',
        '$spaceship_read_array(S,perrorread_bad)', '~$error_read_valid(S,perrorread_bad)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_bad])',
        'perrorread_foreign = perrorread[.ORIGINAL = BINARY_RIGHT BITXOR (KNOWN (PARRAY n_array)) perrorread.LINE][.TASK = BINARY_RIGHT BITXOR (KNOWN (PARRAY n_array)) perrorread.LINE]',
        '~$spaceship_read_array(S,perrorread_foreign)', '~$error_read_valid(S,perrorread_foreign)',
    ]


def finish(start, expected):
    return [
        'S_done = $drive_steps(' + start + ',8000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        r'S_done.DESTRUCTION.CALLS = eps /\ S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
        '~((HARRAY n_array) <- S_done.ALLOCATIONS)', '~((HCELL n_leaf) <- S_done.ALLOCATIONS)',
        '~((HARRAY n_child_old) <- S_done.ALLOCATIONS)', '~((HOBJECT n_old) <- S_done.ALLOCATIONS)',
        'n_old <- S_done.DESTRUCTION.CALLED',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],8000)',
    ]


def checks(program, path, name):
    shared = name == 'child-alias-shared-inner-cow'
    assert shared or name == 'child-alias-supplied-throw'
    line = 36 if shared else 28
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S_front', 'S_initial', 0),
        'S = S_front', '$us_stage(S,0)', '$us_guard(S)',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
        'perrorread.ORIGINAL = BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_array)) ' + str(line),
        'perrorread.TASK = perrorread.ORIGINAL',
        'perrorread.INPUT = VARIABLE ($ptascii("missing")) z_missing',
        'perrorread.RESULT = KNOWN PNULL', 'S.RESULT = perrorread.INPUT',
        'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = ' + str(line),
        '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        '$base_nodes(perrorread.BASE) = eps', '$task_nodes(ERROR_READ_RESULT perrorread) = [HARRAY n_array]',
        '$lookup(S.ENV,$ptascii("source")) = (n_source)', 'S.STORE[n_source] = DEFINED (PARRAY n_array)',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 41)',
        '$lookup(S.ENV,$ptascii("leaf")) = (n_leaf)', '$lookup(S.ENV,$ptascii("outside")) = (n_leaf)',
        'S.STORE[n_leaf] = DEFINED (PARRAY n_child_old)', '$call_reference_operand_valid(S,REFERENCE n_leaf)',
        'n_child_old =/= n_array',
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf)]', 'S.ARRAYS[n_array].NEXT = 1',
        'S.ARRAYS[n_child_old].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old))]',
        'S.ARRAYS[n_child_old].NEXT = 1',
        '$comparison_read_object_value(S,POBJECT n_old)',
        '$node_children(S,HARRAY n_array) = [HCELL n_leaf]',
        '$node_children(S,HCELL n_leaf) = [HARRAY n_child_old]',
        '$node_children(S,HARRAY n_child_old) = [HOBJECT n_old]',
        '$heap_count(HARRAY n_array,$pools_nodes(S.POOLS)) = 0',
        '$heap_count(HARRAY n_child_old,$pools_nodes(S.POOLS)) = 0',
        '$spaceship_read_array(S,perrorread)', '~$spaceship_read_other(S,perrorread)',
        '$duplicate_item(S,n_array,ALIAS n_leaf) = ALIAS n_leaf',
        owners('S', 'HARRAY n_array', 3 if shared else 2),
        owners('S', 'HCELL n_leaf', 3), owners('S', 'HARRAY n_child_old', 1), owners('S', 'HOBJECT n_old', 1),
        '~(n_old <- S.DESTRUCTION.CALLED)', '$us_output(S.EVENTS) = ' + text('P;'),
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(35 if shared else 28) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_warn = $prune_allocations($error_read_begin(S))',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread', 'perrorcall.LEVEL = 2',
        'perrorcall.LINE = ' + str(line), 'perrorcall.MESSAGE = $ptascii("Undefined variable $missing")',
        'perrorcall.EVENT = WARNING ($ptascii("missing")) ' + str(line),
        '$error_call_valid(S_warn,perrorcall)', '$us_guard(S_warn)', 'S_warn.EVENTS = S.EVENTS',
        *controls(),
    ]
    if not shared:
        return values + throw_checks()
    return values + [
        '$lookup(S.ENV,$ptascii("copy")) = (n_copy)', 'S.STORE[n_copy] = DEFINED (PARRAY n_array)',
        *destructor('S_old', 'S_warn', 'n_old', 'P;B;', inside=True),
        'S_old.STORE[n_leaf] = DEFINED (PARRAY n_child_first)',
        'S_old.ARRAYS[n_child_first].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new))]',
        'n_new =/= n_old', 'n_child_first =/= n_child_old',
        '$comparison_read_array_payload(S_old,PARRAY n_child_first)',
        *seek('S_cow', 'S_warn', 6), '$us_guard(S_cow)',
        'S_cow_global = $global_table_view(S_cow)',
        '$lookup(S_cow_global.ENV,$ptascii("inner")) = (n_inner)',
        'S_cow_global.STORE[n_inner] = DEFINED (PARRAY n_child_first)',
        'S_cow_global.STORE[n_leaf] = DEFINED (PARRAY n_child_final)',
        'n_child_final =/= n_child_first',
        'S_cow.ARRAYS[n_child_first].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new))]',
        'S_cow.ARRAYS[n_child_final].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new)), ENTRY (KINT 1) (DIRECT (PINT 9))]',
        '$us_output(S_cow.EVENTS) = ' + text('P;B;O:1;'),
        *seek('S_return', 'S_warn', 2),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        'S_return.RESULT = KNOWN (PBOOL true)', '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        *seek('S_resume', 'S_return', 3),
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)', '$spaceship_read_array(S_resume,perrorread)',
        r'S_resume.CURRENT = eps /\ S_resume.FRAMES = eps', '$us_guard(S_resume)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', 'S_resume.EVENTS = S_return.EVENTS',
        'S_resume.STORE[n_result] = DEFINED (PINT 41)',
        'S_resume.STORE[n_leaf] = DEFINED (PARRAY n_child_final)',
        'S_resume.ARRAYS[n_array] = S.ARRAYS[n_array]',
        'S_resume.ARRAYS[n_child_final] = S_cow.ARRAYS[n_child_final]',
        '$node_children(S_resume,HCELL n_leaf) = [HARRAY n_child_final]',
        '$node_children(S_resume,HARRAY n_child_final) = [HOBJECT n_new]',
        '~((HARRAY n_child_old) <- S_resume.ALLOCATIONS)', '~((HARRAY n_child_first) <- S_resume.ALLOCATIONS)',
        '~((HOBJECT n_old) <- S_resume.ALLOCATIONS)', 'n_old <- S_resume.DESTRUCTION.CALLED',
        '~(n_new <- S_resume.DESTRUCTION.CALLED)',
        owners('S_resume', 'HARRAY n_array', 1), owners('S_resume', 'HCELL n_leaf', 1),
        owners('S_resume', 'HARRAY n_child_final', 1), owners('S_resume', 'HOBJECT n_new', 1),
        *['$lookup(S_resume.ENV,$ptascii("' + name + '")) = eps' for name in ('source', 'copy', 'outside', 'leaf', 'inner')],
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps', 'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PINT 1)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS',
        owners('S_compared', 'HARRAY n_array', 0), owners('S_compared', 'HCELL n_leaf', 0),
        owners('S_compared', 'HARRAY n_child_final', 0), owners('S_compared', 'HOBJECT n_new', 0),
        *destructor('S_last', 'S_restored', 'n_new', 'P;B;O:1;I:1:1:1:1:1;H:1:1:36:1;'),
        'pdestructionoperation_S_last.SOURCE = perrorread.TASK',
        'pdestructionoperation_S_last.VALUE = KNOWN (PINT 1)',
        *finish('S_last', 'P;B;O:1;I:1:1:1:1:1;H:1:1:36:1;N:1:1:1;R:1:1:1:1:1:1:1:1;END;'),
        '~((HARRAY n_child_final) <- S_done.ALLOCATIONS)', '~((HOBJECT n_new) <- S_done.ALLOCATIONS)',
        'n_new <- S_done.DESTRUCTION.CALLED',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],8000) = S_done',
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
        '~$comparison_read_array_payload(S_throw[.ARRAYS[n_child_old].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_exception))]],PARRAY n_child_old)',
        *['$lookup(S_throw.ENV,$ptascii("' + name + '")) = eps' for name in ('source', 'outside', 'leaf')],
        'S_throw.STORE[n_result] = DEFINED (PINT 41)', '$spaceship_read_array(S_throw,perrorread)',
        owners('S_throw', 'HARRAY n_array', 1), owners('S_throw', 'HCELL n_leaf', 1),
        owners('S_throw', 'HARRAY n_child_old', 1), owners('S_throw', 'HOBJECT n_old', 1),
        '$us_output(S_throw.EVENTS) = ' + text('P;B;H:1:1:28:1;'),
        'PhpStep: S_throw ~> S_discarded',
        'S_discarded = S_throw[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*][.ERRORHANDLER = S.ERRORHANDLER]',
        owners('S_discarded', 'HARRAY n_array', 0), owners('S_discarded', 'HCELL n_leaf', 0),
        owners('S_discarded', 'HARRAY n_child_old', 0), owners('S_discarded', 'HOBJECT n_old', 0),
        *destructor('S_pending', 'S_throw', 'n_old', 'P;B;H:1:1:28:1;', '(n_exception)'),
        'pdestructionoperation_S_pending.SOURCE = THROW_SEARCH n_exception',
        *finish('S_pending', 'P;B;H:1:1:28:1;D:1:1:1;C:1:1:1:1:1:1:1:1;F;END;'),
        'S_done.STORE[n_result] = DEFINED (PINT 41)',
        'S_zero = $drive_steps(S_throw,0)', 'S_zero = S_throw[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],8000) = S_done',
    ]
