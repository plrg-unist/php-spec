"""Reached descendant reference graphs, COW edges and pending release."""
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
  -- if $lookup(S_global.ENV,$ptascii("outside")) = (n_cell)
  -- if $lookup(S_global.ENV,$ptascii("snapshot")) = (n_snapshot)
  -- if S_global.STORE[n_cell] = DEFINED (PARRAY n_current)
  -- if S_global.STORE[n_snapshot] = DEFINED (PARRAY n_first)
  -- if n_current =/= n_first
  -- if S.ARRAYS[n_current].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object)), ENTRY (KINT 1) (DIRECT (PINT 9))]
  -- if S.ARRAYS[n_first].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object)), ENTRY (KINT 1) (DIRECT (PINT 7))]
  -- if $class_instanceof(S,POBJECT n_object,$ptascii("SharedRefNew122"))
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
        state + '.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_branch))]',
        state + '.ARRAYS[n_branch].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell), ENTRY (KINT 1) (ALIAS n_cell)]',
        state + '.STORE[n_cell] = DEFINED (PARRAY n_payload)',
        state + '.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old)), ENTRY (KINT 1) (DIRECT (PINT 4))]',
    ]


def front(program, path, shared):
    line = 39 if shared else 29
    values = initial(program, path) + [
        '$us_stage(S,0)', '$us_guard(S)', '$error_read_valid(S,perrorread)',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        'perrorread.ORIGINAL = BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_root)) ' + str(line),
        'perrorread.TASK = perrorread.ORIGINAL',
        'perrorread.INPUT = VARIABLE ($ptascii("missing")) z_missing',
        'perrorread.RESULT = KNOWN PNULL', 'S.RESULT = perrorread.INPUT',
        'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = ' + str(line),
        '$task_nodes(ERROR_READ_RESULT perrorread) = [HARRAY n_root]',
        '$base_nodes(perrorread.BASE) = eps',
        '$lookup(S.ENV,$ptascii("source")) = (n_source)',
        'S.STORE[n_source] = DEFINED (PARRAY n_root)',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 41)',
        *graph('S'),
        '$lookup(S.ENV,$ptascii("outside")) = (n_cell)',
        '$lookup(S.ENV,$ptascii("' + ('leaf' if shared else 'payload') + '")) = (n_cell)',
        '$call_reference_operand_valid(S,REFERENCE n_cell)',
        '$node_children(S,HARRAY n_root) = [HARRAY n_branch]',
        '$node_children(S,HARRAY n_branch) = [HCELL n_cell,HCELL n_cell]',
        '$node_children(S,HCELL n_cell) = [HARRAY n_payload]',
        '$node_children(S,HARRAY n_payload) = [HOBJECT n_old]',
        owners('S','HARRAY n_root',3 if shared else 2),
        owners('S','HARRAY n_branch',1), owners('S','HCELL n_cell',4),
        owners('S','HARRAY n_payload',2 if shared else 1), owners('S','HOBJECT n_old',1),
        '$comparison_read_object_value(S,POBJECT n_old)', '~(n_old <- S.DESTRUCTION.CALLED)',
        '$spaceship_read_array(S,perrorread)', '~$spaceship_read_other(S,perrorread)',
        '$comparison_read_array_payload(S,PARRAY n_root)',
        '$us_output(S.EVENTS) = ' + text('P;'),
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(line) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
    ]
    if shared:
        values += [
            '$lookup(S.ENV,$ptascii("copy")) = (n_copy)', 'S.STORE[n_copy] = DEFINED (PARRAY n_root)',
            '$lookup(S.ENV,$ptascii("held")) = (n_held)', 'S.STORE[n_held] = DEFINED (PARRAY n_payload)',
        ]
    return values + [
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


def controls():
    return [
        '$comparison_read_direct_entries(S,[ENTRY (KINT 0) (ALIAS n_cell), ENTRY (KINT 1) (ALIAS n_cell)],[n_root,n_branch])',
        '~$comparison_read_direct_entries(S,[ENTRY (KINT 0) (ALIAS n_cell)],[n_payload])',
        '$comparison_read_array_payload(S[.STORE[n_cell] = DEFINED (PINT 7)],PARRAY n_root)',
        '$comparison_read_array_payload(S[.STORE[n_cell] = DEFINED (POBJECT n_old)],PARRAY n_root)',
        'S_ref_self = S[.STORE[n_cell] = DEFINED (PARRAY n_branch)]',
        '~$spaceship_read_array(S_ref_self,perrorread)', '$error_read_valid(S_ref_self,perrorread)',
        'S_ref_cross = S[.STORE[n_cell] = DEFINED (PARRAY n_root)]',
        '~$comparison_read_array_payload(S_ref_cross,PARRAY n_root)',
        'S_ref_back = S[.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]]',
        '~$spaceship_read_array(S_ref_back,perrorread)', '$error_read_valid(S_ref_back,perrorread)',
        'S_direct_back = S[.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_branch))]]',
        '~$spaceship_read_array(S_direct_back,perrorread)',
        '~$spaceship_read_array(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HCELL n_cell)],perrorread)',
        '~$spaceship_read_array(S[.REFCELLS = eps],perrorread)',
        '~$spaceship_read_array(S[.STORE[n_cell] = UNDEFINED],perrorread)',
        '~$spaceship_read_array(S[.STORE[n_cell] = DEFINED PUNDEFINED],perrorread)',
        '~$spaceship_read_array(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_payload)],perrorread)',
        '~$spaceship_read_array(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_old)],perrorread)',
        '~$spaceship_read_array(S[.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) UNINITIALIZED]],perrorread)',
        '~$spaceship_read_array(S[.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (INDIRECT n_old ($ptascii("tag")))]],perrorread)',
        '~$spaceship_read_array(S[.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT PUNDEFINED)]],perrorread)',
        'n_outside = |S.STORE|',
        'S_two_cells = S[.STORE = S.STORE ++ [DEFINED (PARRAY n_root)]][.REFCELLS = n_outside :: S.REFCELLS][.ALLOCATIONS = (HCELL n_outside) :: S.ALLOCATIONS][.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (ALIAS n_outside)]]',
        '$call_reference_operand_valid(S_two_cells,REFERENCE n_outside)',
        '~$spaceship_read_array(S_two_cells,perrorread)', '$error_read_valid(S_two_cells,perrorread)',
        'S_outside_cell = S[.ARRAYS[n_branch].ITEMS = [ENTRY (KINT 0) (ALIAS n_outside)]][.REFCELLS = n_outside :: S.REFCELLS][.ALLOCATIONS = (HCELL n_outside) :: S.ALLOCATIONS]',
        '~$spaceship_read_array(S_outside_cell,perrorread)',
        'S_outside_array = S[.STORE[n_cell] = DEFINED (PARRAY (|S.ARRAYS|))][.ALLOCATIONS = (HARRAY (|S.ARRAYS|)) :: S.ALLOCATIONS]',
        '~$spaceship_read_array(S_outside_array,perrorread)',
        '~$error_read_valid(S[.CODE = eps],perrorread)', '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        'perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_root)) 999][.TASK = BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_root)) 999][.LINE = 999]',
        '$spaceship_read_array(S,perrorread_bad)', '~$error_read_valid(S,perrorread_bad)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_bad])',
        'perrorread_foreign = perrorread[.ORIGINAL = BINARY_RIGHT BITXOR (KNOWN (PARRAY n_root)) perrorread.LINE][.TASK = BINARY_RIGHT BITXOR (KNOWN (PARRAY n_root)) perrorread.LINE]',
        '~$spaceship_read_array(S,perrorread_foreign)', '~$error_read_valid(S,perrorread_foreign)',
    ]


def expected(shared):
    return ('P;B;I:1:1:1:1:1:1:1;O:1:1:1;H:1:1:39:1;R:1:1:1:1:1;A:1:1:1;N:1:1:1:1;END;'
            if shared else 'P;B;H:1:1:29:1;D:1:1:1:1:1:1;C:1:1:1:1:1:1:1:1:1;F;END;')


def finish(start, shared, nodes):
    return [
        'S_done = $drive_steps(' + start + ',8000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected(shared)), '$us_guard(S_done)',
        'S_done.STORE[n_result] = DEFINED (PINT ' + ('1' if shared else '41') + ')',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        r'S_done.DESTRUCTION.CALLS = eps /\ S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
        *['~((' + node + ') <- S_done.ALLOCATIONS)' for node in nodes],
        'n_old <- S_done.DESTRUCTION.CALLED',
        *(['n_new <- S_done.DESTRUCTION.CALLED'] if shared else []),
    ]


def sharing():
    return [
        *seek('S_cow','S_warn',6), '$us_guard(S_cow)', 'S_cow_global = $global_table_view(S_cow)',
        'S_cow_global.STORE[n_source] = DEFINED (PARRAY n_source_root)',
        'S_cow_global.STORE[n_copy] = DEFINED (PARRAY n_copy_root)',
        'S_cow_global.STORE[n_held] = DEFINED (PARRAY n_payload)',
        'S_cow_global.STORE[n_cell] = DEFINED (PARRAY n_payload_new)',
        '$lookup(S_cow_global.ENV,$ptascii("snapshot")) = (n_snapshot)',
        'S_cow_global.STORE[n_snapshot] = DEFINED (PARRAY n_payload_first)',
        'S_cow.ARRAYS[n_root].ITEMS = S.ARRAYS[n_root].ITEMS',
        'S_cow.ARRAYS[n_source_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_branch)), ENTRY (KINT 1) (DIRECT (PINT 8))]',
        'S_cow.ARRAYS[n_copy_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_copy_branch))]',
        'S_cow.ARRAYS[n_branch].ITEMS = S.ARRAYS[n_branch].ITEMS',
        'S_cow.ARRAYS[n_copy_branch].ITEMS = S.ARRAYS[n_branch].ITEMS',
        'S_cow.ARRAYS[n_payload].ITEMS = S.ARRAYS[n_payload].ITEMS',
        'S_cow.ARRAYS[n_payload_first].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new)), ENTRY (KINT 1) (DIRECT (PINT 7))]',
        'S_cow.ARRAYS[n_payload_new].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new)), ENTRY (KINT 1) (DIRECT (PINT 9))]',
        'n_source_root =/= n_root', 'n_copy_root =/= n_root', 'n_source_root =/= n_copy_root',
        'n_branch =/= n_copy_branch', 'n_payload_new =/= n_payload_first', 'n_new =/= n_old',
        *[owners('S_cow',node,count) for node,count in (
            ('HARRAY n_root',1),('HARRAY n_source_root',1),('HARRAY n_copy_root',1),
            ('HARRAY n_branch',2),('HARRAY n_copy_branch',1),('HCELL n_cell',6),
            ('HARRAY n_payload',1),('HOBJECT n_old',1),
            ('HARRAY n_payload_first',1),('HARRAY n_payload_new',1),('HOBJECT n_new',2))],
        '$node_children(S_cow,HCELL n_cell) = [HARRAY n_payload_new]',
        '$us_output(S_cow.EVENTS) = ' + text('P;B;'),
        *destructor('S_old','S_cow','n_old','P;B;I:1:1:1:1:1:1:1;',inside=True),
        *seek('S_return','S_old',2), '$us_stage(S_return,2)',
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_return*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread', 'S_return.RESULT = KNOWN (PBOOL true)',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        *seek('S_resume','S_return',3), '$us_stage(S_resume,3)',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_resume*',
        r'S_resume.CURRENT = eps /\ S_resume.FRAMES = eps', '$us_guard(S_resume)',
        '$error_read_valid(S_resume,perrorread)', '$spaceship_read_array(S_resume,perrorread)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', 'S_resume.EVENTS = S_return.EVENTS',
        'S_resume.STORE[n_result] = DEFINED (PINT 41)',
        '$lookup(S_resume.ENV,$ptascii("outside")) = (n_cell)',
        '$lookup(S_resume.ENV,$ptascii("source")) = eps', '$lookup(S_resume.ENV,$ptascii("copy")) = eps',
        '$lookup(S_resume.ENV,$ptascii("leaf")) = eps',
        'S_resume.ARRAYS[n_root].ITEMS = S.ARRAYS[n_root].ITEMS',
        'S_resume.ARRAYS[n_branch].ITEMS = S.ARRAYS[n_branch].ITEMS',
        'S_resume.STORE[n_cell] = DEFINED (PARRAY n_payload_new)',
        *[owners('S_resume',node,count) for node,count in (
            ('HARRAY n_root',1),('HARRAY n_branch',1),('HCELL n_cell',3),
            ('HARRAY n_payload_new',1),('HOBJECT n_new',1))],
        *['~((' + node + ') <- S_resume.ALLOCATIONS)' for node in
          ('HARRAY n_payload','HOBJECT n_old','HARRAY n_source_root','HARRAY n_copy_root','HARRAY n_copy_branch','HARRAY n_payload_first')],
        'n_old <- S_resume.DESTRUCTION.CALLED', '~(n_new <- S_resume.DESTRUCTION.CALLED)',
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_resume*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_resume*][.RESULT = KNOWN (PINT 1)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        owners('S_compared','HARRAY n_root',0), owners('S_compared','HARRAY n_branch',0),
        owners('S_compared','HCELL n_cell',1), owners('S_compared','HOBJECT n_new',1),
        *seek('S_last','S_restored',5),
        'S_last.TODO = (DESTRUCTOR_ENTER pdestructorcall_last) :: ptask_last*',
        'pdestructorcall_last.OBJECT = n_new', 'pdestructorcall_last.PENDING = eps',
        '$call_task_valid(S_last,DESTRUCTOR_ENTER pdestructorcall_last)',
        'S_last.CURRENT = eps', 'S_last.STORE[n_result] = DEFINED (PINT 1)',
        'n_new <- S_last.DESTRUCTION.CALLED', '(HOBJECT n_new) <- S_last.ALLOCATIONS',
        '$us_output(S_last.EVENTS) = ' + text('P;B;I:1:1:1:1:1:1:1;O:1:1:1;H:1:1:39:1;R:1:1:1:1:1;A:1:1:1;'),
        '$us_guard(S_last)',
        '$lookup(S_last.ENV,$ptascii("outside")) = eps',
        *finish('S_last',True,('HARRAY n_root','HARRAY n_branch','HCELL n_cell','HARRAY n_payload','HOBJECT n_old',
                               'HARRAY n_source_root','HARRAY n_copy_root','HARRAY n_copy_branch','HARRAY n_payload_first','HARRAY n_payload_new','HOBJECT n_new')),
    ]


def throwing():
    return [
        *seek('S_throw','S_warn',4), '$us_stage(S_throw,4)',
        'S_throw.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_throw*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        r'S_throw.CURRENT = eps /\ S_throw.FRAMES = eps', '$us_guard(S_throw)',
        '$lookup(S_throw.ENV,$ptascii("exception")) = (n_exception_cell)',
        'S_throw.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
        '~$comparison_read_array_payload(S_throw[.STORE[n_cell] = DEFINED (POBJECT n_exception)],PARRAY n_root)',
        *graph('S_throw'),
        *[owners('S_throw',node,count) for node,count in (
            ('HARRAY n_root',1),('HARRAY n_branch',1),('HCELL n_cell',2),('HARRAY n_payload',1),('HOBJECT n_old',1))],
        '$lookup(S_throw.ENV,$ptascii("source")) = eps', '$lookup(S_throw.ENV,$ptascii("payload")) = eps',
        '$lookup(S_throw.ENV,$ptascii("outside")) = eps',
        'S_throw.STORE[n_result] = DEFINED (PINT 41)', '$spaceship_read_array(S_throw,perrorread)',
        '$us_output(S_throw.EVENTS) = ' + text('P;B;H:1:1:29:1;'),
        'PhpStep: S_throw ~> S_discarded',
        'S_discarded = S_throw[.TODO = (THROW_SEARCH n_exception) :: ptask_throw*][.ERRORHANDLER = S.ERRORHANDLER]',
        *[owners('S_discarded',node,0) for node in ('HARRAY n_root','HARRAY n_branch','HCELL n_cell','HARRAY n_payload','HOBJECT n_old')],
        *destructor('S_pending','S_throw','n_old','P;B;H:1:1:29:1;','(n_exception)'),
        'pdestructionoperation_S_pending.SOURCE = THROW_SEARCH n_exception',
        *finish('S_pending',False,('HARRAY n_root','HARRAY n_branch','HCELL n_cell','HARRAY n_payload','HOBJECT n_old')),
    ]


def budget_setup():
    return initial('unused','unused')[1:] + [
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        *seek('S_budget_cow','S_warn',6), '$us_stage(S_budget_cow,6)',
        *seek('S_budget_destructor','S_budget_cow',5), '$us_stage(S_budget_destructor,5)',
        *seek('S_return','S_budget_destructor',2), '$us_stage(S_return,2)',
        *seek('S_cut','S_return',3), '$us_stage(S_cut,3)',
    ]


def budgets(program, path, shared):
    if shared:
        run = '$php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')'
        values = ['S_cut = $reference_graph_peer_budget_cut(' + run + ')']
    else:
        values = initial(program,path) + [
            'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
            'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
            *seek('S_cut','S_warn',4), '$us_stage(S_cut,4)',
        ]
    return values + [
        'S_done = $drive_steps(S_cut,8000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected(shared)), '$us_guard(S_done)',
        'S_one = $drive_steps(S_cut,1)', 'S_one.COMPLETION = BUDGET',
        '$drive_steps(S_one[.COMPLETION = NORMAL],8000) = S_done',
        'S_zero = $drive_steps(S_cut,0)', 'S_zero = S_cut[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],8000) = S_done',
    ]


PREFIX += '\ndec $reference_graph_peer_budget_cut(pstate) : pstate\ndef $reference_graph_peer_budget_cut(S_initial) = S_cut\n'
PREFIX += ''.join('  -- if ' + condition + '\n' for condition in budget_setup())


def checks(program, path, name):
    shared = name.startswith('reference-graph-shared-descendant-replacement-')
    assert shared or name.startswith('reference-graph-supplied-throw-')
    if name.endswith('-budget'):
        return budgets(program,path,shared)
    values = front(program,path,shared)
    if shared and name.endswith('-domain'):
        return values + controls()
    return values + (sharing() if shared else throwing())
