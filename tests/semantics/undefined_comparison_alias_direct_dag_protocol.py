"""Singleton deep payload COW and live CELL-to-DAG snapshot lifetime."""
import base64
import json

from undefined_spaceship_protocol import text
from undefined_comparison_object_reference_array_review_protocol import (
    PREFIX as COMMON, destructor, owners, seek)

PREFIX = COMMON + r'''
def $us_stage(S, 6) = true
  -- if S.CURRENT =/= eps
  -- if S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("saved")) = (n_current)
  -- if S_global.STORE[n_current] = DEFINED (PARRAY n_root)
  -- if S.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_payload))]
  -- if S.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_shared))]
  -- if S.ARRAYS[n_shared].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf)), ENTRY (KINT 1) (DIRECT (PARRAY n_other))]
  -- if S.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object)), ENTRY (KINT 1) (DIRECT (PINT 9))]
  -- if $class_instanceof(S,POBJECT n_object,$ptascii("NewAliasDag121"))
def $us_stage(S, 7) = true
  -- if S.CURRENT =/= eps
  -- if S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("payload")) = (n_current)
  -- if S_global.STORE[n_current] = DEFINED (PARRAY n_payload)
  -- if S.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_middle))]
  -- if S.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf))]
  -- if S.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object)), ENTRY (KINT 1) (DIRECT (PINT 7))]
  -- if $class_instanceof(S,POBJECT n_object,$ptascii("NewLiveAliasDag121"))
'''


def initial(program, path):
    return [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S_front', 'S_initial', 0),
        'S = S_front', '$error_read_plan(S) = (perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
    ]


def graph(state):
    return [
        state + '.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]',
        state + '.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_shared))]',
        state + '.ARRAYS[n_shared].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf)), ENTRY (KINT 1) (DIRECT (PARRAY n_leaf))]',
        state + '.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old)), ENTRY (KINT 1) (DIRECT (PINT 4))]',
    ]


def old_nodes():
    return ('HARRAY n_root', 'HCELL n_cell', 'HARRAY n_payload', 'HARRAY n_shared', 'HARRAY n_leaf', 'HOBJECT n_old')


def old_owners(state, root_count, cell_count, payload_count):
    return [owners(state, node, count) for node, count in zip(old_nodes(),
            (root_count, cell_count, payload_count, 1, 2, 1))]


def controls(captured):
    read = '$spaceship_read_array' if captured else '$scalar_compare_read_array'
    return [
        '$comparison_read_array_payload(S,PARRAY n_payload)',
        '~$comparison_read_array_payload(S,PARRAY n_root)',
        '~$comparison_read_direct_array(S,PARRAY n_root,eps)',
        '$comparison_read_direct_entries(S,[ENTRY (KINT 0) (DIRECT (PARRAY n_leaf)), ENTRY (KINT 1) (DIRECT (PARRAY n_leaf))],[n_payload,n_shared])',
        '~$comparison_read_direct_array(S,PARRAY n_leaf,[n_leaf])',
        'S_dead_cell = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HCELL n_cell)]',
        '~' + read + '(S_dead_cell,perrorread)', '$error_read_valid(S_dead_cell,perrorread)',
        '~' + read + '(S[.REFCELLS = eps],perrorread)',
        '~' + read + '(S[.STORE[n_cell] = UNDEFINED],perrorread)',
        '~' + read + '(S[.STORE[n_cell] = DEFINED PUNDEFINED],perrorread)',
        'S_child_alias = S[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]]',
        '~' + read + '(S_child_alias,perrorread)', '$error_read_valid(S_child_alias,perrorread)',
        'S_cycle = S[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_payload))]]',
        '~' + read + '(S_cycle,perrorread)', '$error_read_valid(S_cycle,perrorread)',
        '~$comparison_read_array_payload(S[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) UNINITIALIZED]],PARRAY n_payload)',
        '~$comparison_read_array_payload(S[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (INDIRECT n_old ($ptascii("tag")))]],PARRAY n_payload)',
        '~$comparison_read_array_payload(S[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT PUNDEFINED)]],PARRAY n_payload)',
        'S_dead_payload = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_payload)]',
        '~' + read + '(S_dead_payload,perrorread)',
        'S_dead_object = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_old)]',
        '~' + read + '(S_dead_object,perrorread)',
        '~$comparison_read_array_payload(S,PARRAY (|S.ARRAYS|))',
        'S_outside = S[.ALLOCATIONS = (HARRAY (|S.ARRAYS|)) :: S.ALLOCATIONS]',
        '~$comparison_read_array_payload(S_outside,PARRAY (|S.ARRAYS|))',
        '~$error_read_valid(S[.CODE = eps],perrorread)', '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        '~$error_call_valid(S_warn,perrorcall[.LEVEL = 8])',
        '~$error_call_valid(S_warn,perrorcall[.MESSAGE = eps])',
    ]


def front(program, path, captured):
    original = ('BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_root)) 31' if captured
                else 'BINARY_RIGHT EQUAL (VARIABLE ($ptascii("missing")) z_missing) 31')
    task = original if captured else 'BINARY_RIGHT EQUAL (KNOWN PNULL) 31'
    values = initial(program, path) + [
        '$us_stage(S,0)', '$us_guard(S)', '$error_read_valid(S,perrorread)',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        'perrorread.ORIGINAL = ' + original, 'perrorread.TASK = ' + task,
        'perrorread.INPUT = VARIABLE ($ptascii("' + ('missing' if captured else 'right') + '")) ' + ('z_missing' if captured else 'z_right'),
        'perrorread.RESULT = ' + ('KNOWN PNULL' if captured else 'perrorread.INPUT'),
        'S.RESULT = perrorread.INPUT', 'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = 31',
        '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        '$base_nodes(perrorread.BASE) = eps',
        '$task_nodes(ERROR_READ_RESULT perrorread) = ' + ('[HARRAY n_root]' if captured else 'eps'),
        '$lookup(S.ENV,$ptascii("' + ('saved' if captured else 'right') + '")) = (n_current)',
        'S.STORE[n_current] = DEFINED (PARRAY n_root)',
        '$lookup(S.ENV,$ptascii("copy")) = (n_copy)', 'S.STORE[n_copy] = DEFINED (PARRAY n_root)',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 41)',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        graph('S')[0], 'S.STORE[n_cell] = DEFINED (PARRAY n_payload)', *graph('S')[1:],
        '$call_reference_operand_valid(S,REFERENCE n_cell)', '$comparison_read_object_value(S,POBJECT n_old)',
        '$node_children(S,HARRAY n_root) = [HCELL n_cell]', '$node_children(S,HCELL n_cell) = [HARRAY n_payload]',
        '$node_children(S,HARRAY n_payload) = [HARRAY n_shared]',
        '$node_children(S,HARRAY n_shared) = [HARRAY n_leaf,HARRAY n_leaf]',
        '$node_children(S,HARRAY n_leaf) = [HOBJECT n_old]',
        *old_owners('S', 3 if captured else 2, 1 if captured else 3, 1 if captured else 2),
        *['$heap_count(HARRAY ' + node + ',$pools_nodes(S.POOLS)) = 0'
          for node in ('n_root', 'n_payload', 'n_shared', 'n_leaf')],
        '~(n_old <- S.DESTRUCTION.CALLED)', '$us_output(S.EVENTS) = ' + text('P;' if captured else ''),
        'S.ORIGIN = (porigin)', '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (31)',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (31)',
    ]
    if captured:
        values += ['$lookup(S.ENV,$ptascii("payload")) = eps',
                   '$duplicate_item(S,n_root,ALIAS n_cell) = DIRECT (PARRAY n_payload)',
                   '$spaceship_read_array(S,perrorread)', '~$spaceship_read_other(S,perrorread)']
    else:
        values += ['$lookup(S.ENV,$ptascii("payload")) = (n_cell)', '$lookup(S.ENV,$ptascii("outside")) = (n_cell)',
                   '$lookup(S.ENV,$ptascii("held")) = (n_held)', 'S.STORE[n_held] = DEFINED (PARRAY n_payload)',
                   '$duplicate_item(S,n_root,ALIAS n_cell) = ALIAS n_cell',
                   '$scalar_compare_read_array(S,perrorread)', '~$scalar_compare_read_other(S,perrorread)']
    return values + [
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_warn = $prune_allocations($error_read_begin(S))',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread', 'perrorcall.LEVEL = 2', 'perrorcall.LINE = 31',
        'perrorcall.MESSAGE = $ptascii("Undefined variable $missing")', 'perrorcall.EVENT = WARNING ($ptascii("missing")) 31',
        '$error_call_valid(S_warn,perrorcall)', '$us_guard(S_warn)', 'S_warn.EVENTS = S.EVENTS',
        *controls(captured),
    ]


def returned(start):
    return [
        *seek('S_return', start, 2),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)', 'S_return.RESULT = KNOWN (PBOOL true)',
        r'S_return.CURRENT = eps /\ S_return.FRAMES = eps', '$us_guard(S_return)',
        *seek('S_resume', 'S_return', 3), 'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)', '$us_guard(S_resume)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', 'S_resume.EVENTS = S_return.EVENTS',
        'S_resume.STORE[n_result] = DEFINED (PINT 41)',
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)', 'S_resume.STORE[n_missing] = DEFINED (PBOOL true)',
    ]


def restored(captured):
    return [
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps', 'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (' + ('PINT 1' if captured else 'PBOOL false') + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS', 'S_compared.STORE = S_resume.STORE',
    ]


def expected(captured):
    return ('P;B;I:1:1:1:1:1;N:1:1:1;H:1:1:31:1;O:1:1:1;R:1:1:1:1:1;END;'
            if captured else 'B;I:1:1:1:1;O:1:1:1;H:1:1:31:1;R:1:1:1:1:1;A:1:1;N:1:1:1;END;')


def finish(start, captured):
    new_arrays = (('n_root_new', 'n_payload_new', 'n_shared_new', 'n_leaf_new') if captured
                  else ('n_payload_new', 'n_middle_new', 'n_leaf_new'))
    return [
        'S_done = $drive_steps(' + start + ',8000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected(captured)), '$us_guard(S_done)',
        'S_done.STORE[n_result] = DEFINED (' + ('PINT 1' if captured else 'PBOOL false') + ')',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        r'S_done.DESTRUCTION.CALLS = eps /\ S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
        *['~((' + node + ') <- S_done.ALLOCATIONS)' for node in
          (*old_nodes(), *('HARRAY ' + n for n in new_arrays), 'HOBJECT n_new')],
        'n_old <- S_done.DESTRUCTION.CALLED', 'n_new <- S_done.DESTRUCTION.CALLED',
    ]


def core(program, path, captured):
    values = front(program, path, captured)
    if not captured:
        return values + live()
    return values + [
        *seek('S_cow', 'S_warn', 6), '$us_guard(S_cow)', 'S_cow_global = $global_table_view(S_cow)',
        'S_cow_global.STORE[n_current] = DEFINED (PARRAY n_root_new)', 'S_cow_global.STORE[n_copy] = DEFINED (PARRAY n_root)',
        'S_cow.ARRAYS[n_root_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_payload_new))]',
        'S_cow.ARRAYS[n_payload_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_shared_new))]',
        'S_cow.ARRAYS[n_shared_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf_new)), ENTRY (KINT 1) (DIRECT (PARRAY n_leaf))]',
        'S_cow.ARRAYS[n_leaf_new].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new)), ENTRY (KINT 1) (DIRECT (PINT 9))]',
        'n_new =/= n_old',
        *[new + ' =/= ' + old for new, old in (('n_root_new','n_root'), ('n_payload_new','n_payload'), ('n_shared_new','n_shared'), ('n_leaf_new','n_leaf'))],
        *graph('S_cow'), 'S_cow.STORE[n_cell] = DEFINED (PARRAY n_payload)',
        owners('S_cow','HARRAY n_root',2), owners('S_cow','HCELL n_cell',1),
        owners('S_cow','HARRAY n_payload',1), owners('S_cow','HARRAY n_shared',1), owners('S_cow','HARRAY n_leaf',3),
        *[owners('S_cow',node,1) for node in ('HARRAY n_root_new','HARRAY n_payload_new','HARRAY n_shared_new','HARRAY n_leaf_new','HOBJECT n_old','HOBJECT n_new')],
        '$node_children(S_cow,HARRAY n_root_new) = [HARRAY n_payload_new]', '$node_children(S_cow,HCELL n_cell) = [HARRAY n_payload]',
        '$us_output(S_cow.EVENTS) = ' + text('P;B;'),
        *destructor('S_inline','S_cow','n_new','P;B;I:1:1:1:1:1;',inside=True),
        *returned('S_inline'), '$spaceship_read_array(S_resume,perrorread)',
        *graph('S_resume'), 'S_resume.STORE[n_cell] = DEFINED (PARRAY n_payload)',
        *old_owners('S_resume',1,1,1),
        'S_resume.STORE[n_current] = DEFINED (PARRAY n_empty)', 'S_resume.ARRAYS[n_empty].ITEMS = eps',
        'S_resume.STORE[n_copy] = DEFINED (PARRAY n_copy_empty)', 'S_resume.ARRAYS[n_copy_empty].ITEMS = eps',
        '$us_output(S_resume.EVENTS) = ' + text('P;B;I:1:1:1:1:1;N:1:1:1;H:1:1:31:1;'),
        'n_new <- S_resume.DESTRUCTION.CALLED', '~(n_old <- S_resume.DESTRUCTION.CALLED)',
        *['~((' + node + ') <- S_resume.ALLOCATIONS)' for node in ('HARRAY n_root_new','HARRAY n_payload_new','HARRAY n_shared_new','HARRAY n_leaf_new','HOBJECT n_new')],
        *restored(True), *[owners('S_compared',node,0) for node in old_nodes()],
        *destructor('S_last','S_restored','n_old','P;B;I:1:1:1:1:1;N:1:1:1;H:1:1:31:1;'),
        'pdestructionoperation_S_last.SOURCE = perrorread.TASK', 'pdestructionoperation_S_last.VALUE = KNOWN (PINT 1)',
        *finish('S_last',True),
    ]


def live():
    return [
        *seek('S_rebound','S_warn',7), '$us_guard(S_rebound)', 'S_rebound_global = $global_table_view(S_rebound)',
        'S_rebound_global.STORE[n_cell] = DEFINED (PARRAY n_payload_new)',
        'S_rebound_global.STORE[n_current] = DEFINED (PARRAY n_root)', 'S_rebound_global.STORE[n_copy] = DEFINED (PARRAY n_root)',
        'S_rebound_global.STORE[n_held] = DEFINED (PARRAY n_payload)',
        'S_rebound.ARRAYS[n_payload_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_middle_new))]',
        'S_rebound.ARRAYS[n_middle_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf_new))]',
        'S_rebound.ARRAYS[n_leaf_new].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new)), ENTRY (KINT 1) (DIRECT (PINT 7))]',
        'n_payload_new =/= n_payload', 'n_new =/= n_old', *graph('S_rebound'),
        *old_owners('S_rebound',2,3,1),
        *[owners('S_rebound',node,1) for node in ('HARRAY n_payload_new','HARRAY n_middle_new','HARRAY n_leaf_new','HOBJECT n_new')],
        '$node_children(S_rebound,HCELL n_cell) = [HARRAY n_payload_new]', '$us_output(S_rebound.EVENTS) = ' + text('B;'),
        *destructor('S_old','S_rebound','n_old','B;I:1:1:1:1;',inside=True),
        *returned('S_old'), '$scalar_compare_read_array(S_resume,perrorread)',
        'S_resume.STORE[n_cell] = DEFINED (PARRAY n_payload_new)', 'S_resume.STORE[n_current] = DEFINED (PARRAY n_root)',
        'S_resume.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]',
        'S_resume.STORE[n_copy] = DEFINED (PARRAY n_empty)', 'S_resume.ARRAYS[n_empty].ITEMS = eps',
        'S_resume.STORE[n_held] = DEFINED (PARRAY n_held_empty)', 'S_resume.ARRAYS[n_held_empty].ITEMS = eps',
        '$lookup(S_resume.ENV,$ptascii("right")) = (n_current)',
        '$lookup(S_resume.ENV,$ptascii("payload")) = (n_cell)', '$lookup(S_resume.ENV,$ptascii("outside")) = (n_cell)',
        owners('S_resume','HARRAY n_root',1), owners('S_resume','HCELL n_cell',3),
        *[owners('S_resume',node,1) for node in ('HARRAY n_payload_new','HARRAY n_middle_new','HARRAY n_leaf_new','HOBJECT n_new')],
        *['~((' + node + ') <- S_resume.ALLOCATIONS)' for node in ('HARRAY n_payload','HARRAY n_shared','HARRAY n_leaf','HOBJECT n_old')],
        'n_old <- S_resume.DESTRUCTION.CALLED', '~(n_new <- S_resume.DESTRUCTION.CALLED)',
        '$us_output(S_resume.EVENTS) = ' + text('B;I:1:1:1:1;O:1:1:1;H:1:1:31:1;'),
        'S_child_alias_resume = S_resume[.ARRAYS[n_leaf_new].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]]',
        '~$scalar_compare_read_array(S_child_alias_resume,perrorread)', '$error_read_valid(S_child_alias_resume,perrorread)',
        'PhpStep: S_child_alias_resume ~> S_denied',
        'S_denied = S_child_alias_resume[.TODO = eps][.COMPLETION = UNSUPPORTED "scalar comparison warning changed right operand"]',
        *restored(False), owners('S_compared','HARRAY n_root',1), owners('S_compared','HCELL n_cell',3),
        *destructor('S_last','S_compared','n_new','B;I:1:1:1:1;O:1:1:1;H:1:1:31:1;R:1:1:1:1:1;A:1:1;',result='PBOOL false'),
        '$lookup(S_last.ENV,$ptascii("right")) = eps', '$lookup(S_last.ENV,$ptascii("payload")) = eps', '$lookup(S_last.ENV,$ptascii("outside")) = eps',
        *finish('S_last',False),
    ]


def budget_setup(captured):
    return initial('unused','unused')[1:] + [
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        *seek('S_budget_middle','S_warn',6 if captured else 7), '$us_stage(S_budget_middle,' + ('6' if captured else '7') + ')',
        *seek('S_budget_destructor','S_budget_middle',5), '$us_stage(S_budget_destructor,5)',
        *seek('S_return','S_budget_destructor',2), '$us_stage(S_return,2)',
        *seek('S_cut','S_return',3), '$us_stage(S_cut,3)',
    ]


def budgets(program, path, captured):
    run = '$php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')'
    return ['S_cut = $alias_dag_author_budget_cut(' + run + ',' + ('true' if captured else 'false') + ')'] + [
        'S_done = $drive_steps(S_cut,8000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected(captured)), '$us_guard(S_done)',
        'S_one = $drive_steps(S_cut,1)', 'S_one.COMPLETION = BUDGET', '$drive_steps(S_one[.COMPLETION = NORMAL],8000) = S_done',
        'S_zero = $drive_steps(S_cut,0)', 'S_zero = S_cut[.COMPLETION = BUDGET]', '$drive_steps(S_zero[.COMPLETION = NORMAL],8000) = S_done',
    ]


PREFIX += '\ndec $alias_dag_author_budget_cut(pstate, bool) : pstate\n'
for captured in (True,False):
    PREFIX += 'def $alias_dag_author_budget_cut(S_initial,' + ('true' if captured else 'false') + ') = S_cut\n'
    PREFIX += ''.join('  -- if ' + condition + '\n' for condition in budget_setup(captured))


def checks(program, path, name):
    captured = name.startswith('alias-dag-captured-singleton-')
    assert captured or name.startswith('alias-dag-live-held-snapshot-')
    return (budgets if name.endswith('-budget') else core)(program,path,captured)
