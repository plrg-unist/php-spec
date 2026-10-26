"""Two-cell singleton unwrapping and live shared-cell payload replacement."""
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
  -- if $lookup(S_global.ENV,$ptascii("copy")) = (n_copy)
  -- if S_global.STORE[n_copy] = DEFINED (PARRAY n_root)
  -- if S.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_branch)), ENTRY (KINT 1) (DIRECT (PARRAY n_old_branch))]
  -- if S.ARRAYS[n_branch].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_middle))]
  -- if S.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf))]
  -- if S.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object)), ENTRY (KINT 1) (DIRECT (PINT 9))]
  -- if $class_instanceof(S,POBJECT n_object,$ptascii("NewBranchRef122"))
def $us_stage(S, 7) = true
  -- if S.CURRENT =/= eps
  -- if S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("outside")) = (n_cell)
  -- if S_global.STORE[n_cell] = DEFINED (PARRAY n_leaf)
  -- if S.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object)), ENTRY (KINT 1) (DIRECT (PINT 8))]
  -- if $class_instanceof(S,POBJECT n_object,$ptascii("NewHeldRef122"))
  -- if $lookup(S_global.ENV,$ptascii("copy")) = (n_copy)
  -- if S_global.STORE[n_copy] = DEFINED (PARRAY n_copy_root)
  -- if S.ARRAYS[n_copy_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_copy_branch)), ENTRY (KINT 1) (DIRECT (PARRAY n_branch))]
  -- if n_copy_branch =/= n_branch
'''


def initial(program, path):
    return [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S_front','S_initial',0),
        'S = S_front', '$error_read_plan(S) = (perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
    ]


def graph(state, captured):
    return [
        state + '.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_branch)), ENTRY (KINT 1) (DIRECT (PARRAY n_branch))]',
    ] + ([
        state + '.ARRAYS[n_branch].ITEMS = [ENTRY (KINT 0) (ALIAS n_outer_cell)]',
        state + '.STORE[n_outer_cell] = DEFINED (PARRAY n_middle)',
        state + '.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]',
    ] if captured else [
        state + '.ARRAYS[n_branch].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]',
    ]) + [
        state + '.STORE[n_cell] = DEFINED (PARRAY n_leaf)',
        state + '.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old)), ENTRY (KINT 1) (DIRECT (PINT 4))]',
    ]


def old_nodes(captured):
    return ('HARRAY n_root','HARRAY n_branch',
            *(('HCELL n_outer_cell','HARRAY n_middle') if captured else ()),
            'HCELL n_cell','HARRAY n_leaf','HOBJECT n_old')


def front(program, path, captured):
    original = ('BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_root)) 33' if captured
                else 'BINARY_RIGHT EQUAL (VARIABLE ($ptascii("missing")) z_missing) 33')
    values = initial(program,path) + [
        '$us_stage(S,0)', '$us_guard(S)', '$error_read_valid(S,perrorread)',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        'perrorread.ORIGINAL = ' + original,
        'perrorread.TASK = ' + (original if captured else 'BINARY_RIGHT EQUAL (KNOWN PNULL) 33'),
        'perrorread.INPUT = VARIABLE ($ptascii("' + ('missing' if captured else 'right') + '")) ' + ('z_missing' if captured else 'z_right'),
        'perrorread.RESULT = ' + ('KNOWN PNULL' if captured else 'perrorread.INPUT'),
        'S.RESULT = perrorread.INPUT', 'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = 33',
        '$base_nodes(perrorread.BASE) = eps',
        '$task_nodes(ERROR_READ_RESULT perrorread) = ' + ('[HARRAY n_root]' if captured else 'eps'),
        '$lookup(S.ENV,$ptascii("' + ('saved' if captured else 'right') + '")) = (n_current)',
        'S.STORE[n_current] = DEFINED (PARRAY n_root)',
        '$lookup(S.ENV,$ptascii("copy")) = (n_copy)', 'S.STORE[n_copy] = DEFINED (PARRAY n_root)',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 41)',
        '$lookup(S.ENV,$ptascii("missing")) = eps', *graph('S',captured),
        '$call_reference_operand_valid(S,REFERENCE n_cell)', '$comparison_read_object_value(S,POBJECT n_old)',
        owners('S','HARRAY n_root',3 if captured else 2), owners('S','HARRAY n_branch',2),
        owners('S','HCELL n_cell',1 if captured else 2), owners('S','HARRAY n_leaf',1 if captured else 2),
        owners('S','HOBJECT n_old',1),
        '$node_children(S,HARRAY n_root) = [HARRAY n_branch,HARRAY n_branch]',
        '$node_children(S,HCELL n_cell) = [HARRAY n_leaf]',
        '$node_children(S,HARRAY n_leaf) = [HOBJECT n_old]',
        '$comparison_read_array_payload(S,PARRAY n_root)', '~(n_old <- S.DESTRUCTION.CALLED)',
        '$us_output(S.EVENTS) = ' + text('P;' if captured else ''),
        'S.ORIGIN = (porigin)', '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (33)',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (33)',
    ]
    if captured:
        values += [
            '$call_reference_operand_valid(S,REFERENCE n_outer_cell)',
            owners('S','HCELL n_outer_cell',1), owners('S','HARRAY n_middle',1),
            '$node_children(S,HARRAY n_branch) = [HCELL n_outer_cell]',
            '$node_children(S,HCELL n_outer_cell) = [HARRAY n_middle]',
            '$node_children(S,HARRAY n_middle) = [HCELL n_cell]',
            '$duplicate_item(S,n_branch,ALIAS n_outer_cell) = DIRECT (PARRAY n_middle)',
            '$duplicate_item(S,n_middle,ALIAS n_cell) = DIRECT (PARRAY n_leaf)',
            '$spaceship_read_array(S,perrorread)', '~$spaceship_read_other(S,perrorread)',
        ]
    else:
        values += [
            '$lookup(S.ENV,$ptascii("outside")) = (n_cell)',
            '$lookup(S.ENV,$ptascii("held")) = (n_held)', 'S.STORE[n_held] = DEFINED (PARRAY n_leaf)',
            '$node_children(S,HARRAY n_branch) = [HCELL n_cell]',
            '$duplicate_item(S,n_branch,ALIAS n_cell) = ALIAS n_cell',
            '$scalar_compare_read_array(S,perrorread)', '~$scalar_compare_read_other(S,perrorread)',
        ]
    return values + [
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_warn = $prune_allocations($error_read_begin(S))',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread', 'perrorcall.LEVEL = 2', 'perrorcall.LINE = 33',
        'perrorcall.MESSAGE = $ptascii("Undefined variable $missing")', 'perrorcall.EVENT = WARNING ($ptascii("missing")) 33',
        '$error_call_valid(S_warn,perrorcall)', '$us_guard(S_warn)', 'S_warn.EVENTS = S.EVENTS',
    ]


def returned(start, captured):
    return [
        *seek('S_return',start,2), '$us_stage(S_return,2)',
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_return*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)', 'S_return.RESULT = KNOWN (PBOOL true)',
        r'S_return.CURRENT = eps /\ S_return.FRAMES = eps', '$us_guard(S_return)',
        *seek('S_resume','S_return',3), '$us_stage(S_resume,3)',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_resume*',
        '$error_read_valid(S_resume,perrorread)', '$us_guard(S_resume)',
        ('$spaceship_read_array' if captured else '$scalar_compare_read_array') + '(S_resume,perrorread)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', 'S_resume.EVENTS = S_return.EVENTS',
        'S_resume.STORE[n_result] = DEFINED (PINT 41)',
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)', 'S_resume.STORE[n_missing] = DEFINED (PBOOL true)',
    ]


def restored(captured):
    return [
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_resume*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_resume*][.RESULT = KNOWN (' + ('PINT 1' if captured else 'PBOOL false') + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS', 'S_compared.STORE = S_resume.STORE',
    ]


def expected(captured):
    return ('P;B;I:1:1:1:1:1;N:1:1:1;H:1:1:33:1:1;O:1:1:1;R:1:1:1:1:1:1;END;'
            if captured else 'B;I:1:1:1:1:1;O:1:1:1;H:1:1:33:1:1;R:1:1:1:1;A:1:1;N:1:1:1;END;')


def finish(start, captured, extra):
    return [
        'S_done = $drive_steps(' + start + ',8000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected(captured)), '$us_guard(S_done)',
        'S_done.STORE[n_result] = DEFINED (' + ('PINT 1' if captured else 'PBOOL false') + ')',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        r'S_done.DESTRUCTION.CALLS = eps /\ S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
        *['~((' + node + ') <- S_done.ALLOCATIONS)' for node in (*old_nodes(captured),*extra)],
        'n_old <- S_done.DESTRUCTION.CALLED', 'n_new <- S_done.DESTRUCTION.CALLED',
    ]


def captured_core():
    new_arrays = ('n_root_new','n_branch_new','n_middle_new','n_leaf_new')
    return [
        *seek('S_cow','S_warn',6), '$us_guard(S_cow)', 'S_cow_global = $global_table_view(S_cow)',
        'S_cow_global.STORE[n_current] = DEFINED (PARRAY n_root)',
        'S_cow_global.STORE[n_copy] = DEFINED (PARRAY n_root_new)',
        'S_cow.ARRAYS[n_root_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_branch_new)), ENTRY (KINT 1) (DIRECT (PARRAY n_branch))]',
        'S_cow.ARRAYS[n_branch_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_middle_new))]',
        'S_cow.ARRAYS[n_middle_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf_new))]',
        'S_cow.ARRAYS[n_leaf_new].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new)), ENTRY (KINT 1) (DIRECT (PINT 9))]',
        'n_new =/= n_old', *graph('S_cow',True),
        *[new + ' =/= ' + old for new,old in zip(new_arrays,('n_root','n_branch','n_middle','n_leaf'))],
        *[owners('S_cow',node,count) for node,count in zip(old_nodes(True),(2,3,1,1,1,1,1))],
        *[owners('S_cow',node,1) for node in (*('HARRAY '+n for n in new_arrays),'HOBJECT n_new')],
        '$node_children(S_cow,HARRAY n_branch_new) = [HARRAY n_middle_new]',
        '$node_children(S_cow,HARRAY n_middle_new) = [HARRAY n_leaf_new]',
        '$us_output(S_cow.EVENTS) = ' + text('P;B;I:1:1:1:1:1;'),
        *destructor('S_inline','S_cow','n_new','P;B;I:1:1:1:1:1;',inside=True),
        *returned('S_inline',True), *graph('S_resume',True),
        *[owners('S_resume',node,count) for node,count in zip(old_nodes(True),(1,2,1,1,1,1,1))],
        'S_resume.STORE[n_current] = DEFINED (PARRAY n_empty)', 'S_resume.ARRAYS[n_empty].ITEMS = eps',
        'S_resume.STORE[n_copy] = DEFINED (PARRAY n_copy_empty)', 'S_resume.ARRAYS[n_copy_empty].ITEMS = eps',
        'n_new <- S_resume.DESTRUCTION.CALLED', '~(n_old <- S_resume.DESTRUCTION.CALLED)',
        *['~((' + node + ') <- S_resume.ALLOCATIONS)' for node in (*('HARRAY '+n for n in new_arrays),'HOBJECT n_new')],
        '$us_output(S_resume.EVENTS) = ' + text('P;B;I:1:1:1:1:1;N:1:1:1;H:1:1:33:1:1;'),
        *restored(True), *[owners('S_compared',node,0) for node in old_nodes(True)],
        *destructor('S_last','S_restored','n_old','P;B;I:1:1:1:1:1;N:1:1:1;H:1:1:33:1:1;'),
        'pdestructionoperation_S_last.SOURCE = perrorread.TASK', 'pdestructionoperation_S_last.VALUE = KNOWN (PINT 1)',
        *finish('S_last',True,(*('HARRAY '+n for n in new_arrays),'HOBJECT n_new')),
    ]


def live_core():
    return [
        *seek('S_rebound','S_warn',7), '$us_guard(S_rebound)', 'S_rebound_global = $global_table_view(S_rebound)',
        'S_rebound_global.STORE[n_current] = DEFINED (PARRAY n_root)',
        'S_rebound_global.STORE[n_copy] = DEFINED (PARRAY n_copy_root)',
        'S_rebound_global.STORE[n_held] = DEFINED (PARRAY n_leaf)',
        'S_rebound_global.STORE[n_cell] = DEFINED (PARRAY n_leaf_new)',
        'S_rebound.ARRAYS[n_root].ITEMS = S.ARRAYS[n_root].ITEMS',
        'S_rebound.ARRAYS[n_copy_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_copy_branch)), ENTRY (KINT 1) (DIRECT (PARRAY n_branch))]',
        'S_rebound.ARRAYS[n_branch].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]',
        'S_rebound.ARRAYS[n_copy_branch].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]',
        'S_rebound.ARRAYS[n_leaf].ITEMS = S.ARRAYS[n_leaf].ITEMS',
        'S_rebound.ARRAYS[n_leaf_new].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new)), ENTRY (KINT 1) (DIRECT (PINT 8))]',
        'n_copy_root =/= n_root', 'n_copy_branch =/= n_branch', 'n_leaf_new =/= n_leaf', 'n_new =/= n_old',
        *[owners('S_rebound',node,count) for node,count in (
            ('HARRAY n_root',1),('HARRAY n_copy_root',1),('HARRAY n_branch',3),('HARRAY n_copy_branch',1),
            ('HCELL n_cell',3),('HARRAY n_leaf',1),('HOBJECT n_old',1),('HARRAY n_leaf_new',1),('HOBJECT n_new',1))],
        '$node_children(S_rebound,HCELL n_cell) = [HARRAY n_leaf_new]',
        '$duplicate_item(S_rebound,n_branch,ALIAS n_cell) = ALIAS n_cell',
        '$us_output(S_rebound.EVENTS) = ' + text('B;'),
        *destructor('S_old','S_rebound','n_old','B;I:1:1:1:1:1;',inside=True),
        *returned('S_old',False),
        'S_resume.STORE[n_current] = DEFINED (PARRAY n_root)', 'S_resume.STORE[n_cell] = DEFINED (PARRAY n_leaf_new)',
        'S_resume.ARRAYS[n_root].ITEMS = S.ARRAYS[n_root].ITEMS',
        'S_resume.ARRAYS[n_branch].ITEMS = S.ARRAYS[n_branch].ITEMS',
        '$lookup(S_resume.ENV,$ptascii("outside")) = (n_cell)',
        'S_resume.STORE[n_copy] = DEFINED (PARRAY n_empty)', 'S_resume.ARRAYS[n_empty].ITEMS = eps',
        'S_resume.STORE[n_held] = DEFINED (PARRAY n_held_empty)', 'S_resume.ARRAYS[n_held_empty].ITEMS = eps',
        *[owners('S_resume',node,count) for node,count in (
            ('HARRAY n_root',1),('HARRAY n_branch',2),('HCELL n_cell',2),('HARRAY n_leaf_new',1),('HOBJECT n_new',1))],
        *['~((' + node + ') <- S_resume.ALLOCATIONS)' for node in ('HARRAY n_leaf','HOBJECT n_old','HARRAY n_copy_root','HARRAY n_copy_branch')],
        'n_old <- S_resume.DESTRUCTION.CALLED', '~(n_new <- S_resume.DESTRUCTION.CALLED)',
        '$us_output(S_resume.EVENTS) = ' + text('B;I:1:1:1:1:1;O:1:1:1;H:1:1:33:1:1;'),
        *restored(False), owners('S_compared','HARRAY n_root',1), owners('S_compared','HCELL n_cell',2),
        *seek('S_last','S_compared',5),
        'S_last.TODO = (DESTRUCTOR_ENTER pdestructorcall_last) :: ptask_last*',
        'pdestructorcall_last.OBJECT = n_new', 'pdestructorcall_last.PENDING = eps',
        '$call_task_valid(S_last,DESTRUCTOR_ENTER pdestructorcall_last)',
        'S_last.CURRENT = eps', 'S_last.STORE[n_result] = DEFINED (PBOOL false)',
        'n_new <- S_last.DESTRUCTION.CALLED', '(HOBJECT n_new) <- S_last.ALLOCATIONS',
        '$us_output(S_last.EVENTS) = ' + text('B;I:1:1:1:1:1;O:1:1:1;H:1:1:33:1:1;R:1:1:1:1;A:1:1;'), '$us_guard(S_last)',
        '$lookup(S_last.ENV,$ptascii("outside")) = eps',
        *finish('S_last',False,('HARRAY n_copy_root','HARRAY n_copy_branch','HARRAY n_leaf_new','HOBJECT n_new')),
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
    return ['S_cut = $reference_graph_author_budget_cut(' + run + ',' + ('true' if captured else 'false') + ')'] + [
        'S_done = $drive_steps(S_cut,8000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected(captured)), '$us_guard(S_done)',
        'S_one = $drive_steps(S_cut,1)', 'S_one.COMPLETION = BUDGET', '$drive_steps(S_one[.COMPLETION = NORMAL],8000) = S_done',
        'S_zero = $drive_steps(S_cut,0)', 'S_zero = S_cut[.COMPLETION = BUDGET]', '$drive_steps(S_zero[.COMPLETION = NORMAL],8000) = S_done',
    ]


PREFIX += '\ndec $reference_graph_author_budget_cut(pstate, bool) : pstate\n'
for captured in (True,False):
    PREFIX += 'def $reference_graph_author_budget_cut(S_initial,' + ('true' if captured else 'false') + ') = S_cut\n'
    PREFIX += ''.join('  -- if ' + condition + '\n' for condition in budget_setup(captured))


def checks(program, path, name):
    captured = name.startswith('reference-graph-captured-shared-branches-')
    assert captured or name.startswith('reference-graph-live-held-payload-')
    if name.endswith('-budget'):
        return budgets(program,path,captured)
    return front(program,path,captured) + (captured_core() if captured else live_core())
