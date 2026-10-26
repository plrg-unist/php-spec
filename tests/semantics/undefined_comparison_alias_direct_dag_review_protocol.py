"""Reached CELL-to-DAG COW, physical child owners and transitive cleanup."""
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
  -- if $lookup(S_global.ENV,$ptascii("deep")) = (n_cell)
  -- if $lookup(S_global.ENV,$ptascii("inner")) = (n_inner)
  -- if S_global.STORE[n_cell] = DEFINED (PARRAY n_payload)
  -- if S_global.STORE[n_inner] = DEFINED (PARRAY n_snapshot)
  -- if n_payload =/= n_snapshot
  -- if S.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_middle))]
  -- if S.ARRAYS[n_snapshot].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_first_middle))]
  -- if S.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf)), ENTRY (KINT 1) (DIRECT (PARRAY n_first_leaf))]
  -- if S.ARRAYS[n_first_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_first_leaf)), ENTRY (KINT 1) (DIRECT (PARRAY n_first_leaf))]
  -- if S.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object)), ENTRY (KINT 1) (DIRECT (PINT 9))]
  -- if S.ARRAYS[n_first_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object)), ENTRY (KINT 1) (DIRECT (PINT 7))]
  -- if $class_instanceof(S,POBJECT n_object,$ptascii("SharedDagNew121"))
'''


def initial(program, path):
    return [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S_front', 'S_initial', 0),
        'S = S_front', '$error_read_plan(S) = (perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
    ]


def old_graph(state):
    return [
        state + '.ARRAYS[n_payload].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_middle))]',
        state + '.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf)), ENTRY (KINT 1) (DIRECT (PARRAY n_leaf))]',
        state + '.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old)), ENTRY (KINT 1) (DIRECT (PINT 4))]',
    ]


def old_owners(state, payload_count):
    return [owners(state, node, count) for node, count in (
        ('HARRAY n_payload', payload_count), ('HARRAY n_middle', 1),
        ('HARRAY n_leaf', 2), ('HOBJECT n_old', 1))]


def controls():
    return [
        '$comparison_read_array_payload(S,PARRAY n_payload)',
        '$comparison_read_array_payload(S,PARRAY n_middle)',
        '$comparison_read_array_payload(S,PARRAY n_root)',
        '$comparison_read_direct_entries(S,[ENTRY (KINT 0) (DIRECT (PARRAY n_leaf)), ENTRY (KINT 1) (DIRECT (PARRAY n_leaf))],[n_payload,n_middle])',
        '~$comparison_read_direct_array(S,PARRAY n_leaf,[n_leaf])',
        'S_self = S[.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_middle))]]',
        '~$comparison_read_array_payload(S_self,PARRAY n_payload)', '~$spaceship_read_array(S_self,perrorread)',
        'S_cross = S[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_payload))]]',
        '~$comparison_read_array_payload(S_cross,PARRAY n_payload)', '~$spaceship_read_array(S_cross,perrorread)',
        'S_alias = S[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]]',
        '~$comparison_read_array_payload(S_alias,PARRAY n_payload)', '~$spaceship_read_array(S_alias,perrorread)',
        '$error_read_valid(S_alias,perrorread)',
        '~$comparison_read_array_payload(S[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) UNINITIALIZED]],PARRAY n_payload)',
        '~$comparison_read_array_payload(S[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (INDIRECT n_old ($ptascii("tag")))]],PARRAY n_payload)',
        '~$comparison_read_array_payload(S[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT PUNDEFINED)]],PARRAY n_payload)',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_payload)]',
        '~$spaceship_read_array(S_dead,perrorread)', '$error_read_valid(S_dead,perrorread)',
        '~$comparison_read_array_payload(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_old)],PARRAY n_payload)',
        '~$spaceship_read_array(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HCELL n_cell)],perrorread)',
        '~$spaceship_read_array(S[.REFCELLS = eps],perrorread)',
        '~$spaceship_read_array(S[.STORE[n_cell] = UNDEFINED],perrorread)',
        '~$spaceship_read_array(S[.STORE[n_cell] = DEFINED PUNDEFINED],perrorread)',
        '~$comparison_read_array_payload(S,PARRAY (|S.ARRAYS|))',
        '~$comparison_read_array_payload(S[.ALLOCATIONS = (HARRAY (|S.ARRAYS|)) :: S.ALLOCATIONS],PARRAY (|S.ARRAYS|))',
        '~$error_read_valid(S[.CODE = eps],perrorread)', '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        'perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_root)) 999][.TASK = BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_root)) 999][.LINE = 999]',
        '$spaceship_read_array(S,perrorread_bad)', '~$error_read_valid(S,perrorread_bad)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_bad])',
        'perrorread_foreign = perrorread[.ORIGINAL = BINARY_RIGHT BITXOR (KNOWN (PARRAY n_root)) perrorread.LINE][.TASK = BINARY_RIGHT BITXOR (KNOWN (PARRAY n_root)) perrorread.LINE]',
        '~$spaceship_read_array(S,perrorread_foreign)', '~$error_read_valid(S,perrorread_foreign)',
    ]


def front(program, path, shared):
    line = 41 if shared else 29
    values = initial(program, path) + [
        '$us_stage(S,0)', '$us_guard(S)', '$error_read_valid(S,perrorread)',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        'perrorread.ORIGINAL = BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_root)) ' + str(line),
        'perrorread.TASK = perrorread.ORIGINAL',
        'perrorread.INPUT = VARIABLE ($ptascii("missing")) z_missing',
        'perrorread.RESULT = KNOWN PNULL', 'S.RESULT = perrorread.INPUT',
        'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = ' + str(line),
        '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        '$base_nodes(perrorread.BASE) = eps', '$task_nodes(ERROR_READ_RESULT perrorread) = [HARRAY n_root]',
        '$lookup(S.ENV,$ptascii("source")) = (n_source)', 'S.STORE[n_source] = DEFINED (PARRAY n_root)',
        '$lookup(S.ENV,$ptascii("deep")) = (n_cell)', '$lookup(S.ENV,$ptascii("outside")) = (n_cell)',
        'S.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell)]',
        'S.STORE[n_cell] = DEFINED (PARRAY n_payload)', '$call_reference_operand_valid(S,REFERENCE n_cell)',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 41)',
        *old_graph('S'), *old_owners('S', 2 if shared else 1),
        owners('S', 'HARRAY n_root', 3 if shared else 2), owners('S', 'HCELL n_cell', 3),
        '$node_children(S,HARRAY n_root) = [HCELL n_cell]', '$node_children(S,HCELL n_cell) = [HARRAY n_payload]',
        '$node_children(S,HARRAY n_payload) = [HARRAY n_middle]',
        '$node_children(S,HARRAY n_middle) = [HARRAY n_leaf,HARRAY n_leaf]', '$node_children(S,HARRAY n_leaf) = [HOBJECT n_old]',
        '$comparison_read_object_value(S,POBJECT n_old)', '~(n_old <- S.DESTRUCTION.CALLED)',
        '$spaceship_read_array(S,perrorread)', '~$spaceship_read_other(S,perrorread)',
        '$us_output(S.EVENTS) = ' + text('P;'),
        'S.ORIGIN = (porigin)', '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(line) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
        *['$heap_count(HARRAY ' + n + ',$pools_nodes(S.POOLS)) = 0' for n in ('n_root','n_payload','n_middle','n_leaf')],
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
    if shared:
        values += ['$lookup(S.ENV,$ptascii("copy")) = (n_copy)', 'S.STORE[n_copy] = DEFINED (PARRAY n_root)',
                   '$lookup(S.ENV,$ptascii("held")) = (n_held)', 'S.STORE[n_held] = DEFINED (PARRAY n_payload)']
    return values


def expected(shared):
    return ('P;B;I:1:1:1:1:1:1:1;O:1:1:1;H:1:1:41:1;R:1:1:1:1:1;A:1:1:1;N:1:1:1:1;END;'
            if shared else 'P;B;H:1:1:29:1;D:1:1:1:1:1:1;C:1:1:1:1:1:1:1:1:1;F;END;')


def finish(start, shared):
    nodes = ['HARRAY n_root','HCELL n_cell','HARRAY n_payload','HARRAY n_middle','HARRAY n_leaf','HOBJECT n_old']
    if shared:
        nodes += ['HARRAY n_root_new','HARRAY n_copy_root','HARRAY n_payload_first','HARRAY n_middle_first',
                  'HARRAY n_leaf_first','HARRAY n_payload_new','HARRAY n_middle_new','HARRAY n_leaf_new','HOBJECT n_new']
    return [
        'S_done = $drive_steps(' + start + ',8000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected(shared)), '$us_guard(S_done)',
        'S_done.STORE[n_result] = DEFINED (PINT ' + ('1' if shared else '41') + ')',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        r'S_done.DESTRUCTION.CALLS = eps /\ S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
        *['~((' + node + ') <- S_done.ALLOCATIONS)' for node in nodes], 'n_old <- S_done.DESTRUCTION.CALLED',
        *(['n_new <- S_done.DESTRUCTION.CALLED'] if shared else []),
    ]


def core(program, path, shared):
    values = front(program, path, shared)
    return values + (sharing() if shared else throwing())


def sharing():
    return [
        *seek('S_cow','S_warn',6), '$us_guard(S_cow)', 'S_cow_global = $global_table_view(S_cow)',
        'S_cow_global.STORE[n_source] = DEFINED (PARRAY n_root_new)',
        'S_cow_global.STORE[n_copy] = DEFINED (PARRAY n_copy_root)',
        'S_cow_global.STORE[n_held] = DEFINED (PARRAY n_payload)',
        'S_cow_global.STORE[n_cell] = DEFINED (PARRAY n_payload_new)',
        '$lookup(S_cow_global.ENV,$ptascii("inner")) = (n_inner)',
        'S_cow_global.STORE[n_inner] = DEFINED (PARRAY n_payload_first)',
        'S_cow.ARRAYS[n_root_new].ITEMS = [ENTRY (KINT 0) (ALIAS n_cell), ENTRY (KINT 1) (DIRECT (PINT 8))]',
        'S_cow.ARRAYS[n_root].ITEMS = S.ARRAYS[n_root].ITEMS',
        'S_cow.ARRAYS[n_copy_root].ITEMS = S.ARRAYS[n_root].ITEMS',
        'S_cow.ARRAYS[n_payload_first].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_middle_first))]',
        'S_cow.ARRAYS[n_middle_first].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf_first)), ENTRY (KINT 1) (DIRECT (PARRAY n_leaf_first))]',
        'S_cow.ARRAYS[n_leaf_first].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new)), ENTRY (KINT 1) (DIRECT (PINT 7))]',
        'S_cow.ARRAYS[n_payload_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_middle_new))]',
        'S_cow.ARRAYS[n_middle_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf_new)), ENTRY (KINT 1) (DIRECT (PARRAY n_leaf_first))]',
        'S_cow.ARRAYS[n_leaf_new].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new)), ENTRY (KINT 1) (DIRECT (PINT 9))]',
        'n_root_new =/= n_root', 'n_copy_root =/= n_root', 'n_copy_root =/= n_root_new',
        'n_payload_new =/= n_payload_first',
        'n_middle_new =/= n_middle_first', 'n_leaf_new =/= n_leaf_first', 'n_new =/= n_old',
        *old_graph('S_cow'), *old_owners('S_cow',1),
        owners('S_cow','HARRAY n_root',1), owners('S_cow','HARRAY n_root_new',1),
        owners('S_cow','HARRAY n_copy_root',1), owners('S_cow','HCELL n_cell',5),
        *[owners('S_cow',node,count) for node,count in (
            ('HARRAY n_payload_first',1),('HARRAY n_middle_first',1),('HARRAY n_leaf_first',3),
            ('HARRAY n_payload_new',1),('HARRAY n_middle_new',1),('HARRAY n_leaf_new',1),('HOBJECT n_new',2))],
        '$node_children(S_cow,HCELL n_cell) = [HARRAY n_payload_new]',
        '$us_output(S_cow.EVENTS) = ' + text('P;B;'),
        *destructor('S_old','S_cow','n_old','P;B;I:1:1:1:1:1:1:1;',inside=True),
        *seek('S_return','S_old',2),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread', 'S_return.RESULT = KNOWN (PBOOL true)',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        *seek('S_resume','S_return',3),
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        r'S_resume.CURRENT = eps /\ S_resume.FRAMES = eps', '$us_guard(S_resume)',
        '$error_read_valid(S_resume,perrorread)', '$spaceship_read_array(S_resume,perrorread)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', 'S_resume.EVENTS = S_return.EVENTS',
        'S_resume.STORE[n_result] = DEFINED (PINT 41)',
        '$lookup(S_resume.ENV,$ptascii("outside")) = (n_cell)',
        '$lookup(S_resume.ENV,$ptascii("source")) = eps', '$lookup(S_resume.ENV,$ptascii("copy")) = eps',
        '$lookup(S_resume.ENV,$ptascii("deep")) = eps',
        'S_resume.STORE[n_cell] = DEFINED (PARRAY n_payload_new)',
        owners('S_resume','HARRAY n_root',1), owners('S_resume','HCELL n_cell',2),
        *[owners('S_resume',node,1) for node in ('HARRAY n_payload_new','HARRAY n_middle_new','HARRAY n_leaf_new','HARRAY n_leaf_first')],
        owners('S_resume','HOBJECT n_new',2),
        *['~((' + node + ') <- S_resume.ALLOCATIONS)' for node in ('HARRAY n_payload','HARRAY n_middle','HARRAY n_leaf','HOBJECT n_old','HARRAY n_root_new','HARRAY n_copy_root','HARRAY n_payload_first','HARRAY n_middle_first')],
        'n_old <- S_resume.DESTRUCTION.CALLED', '~(n_new <- S_resume.DESTRUCTION.CALLED)',
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PINT 1)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        owners('S_compared','HARRAY n_root',0), owners('S_compared','HCELL n_cell',1),
        owners('S_compared','HOBJECT n_new',2),
        *destructor('S_last','S_restored','n_new','P;B;I:1:1:1:1:1:1:1;O:1:1:1;H:1:1:41:1;R:1:1:1:1:1;A:1:1:1;',result='PINT 1'),
        '$lookup(S_last.ENV,$ptascii("outside")) = eps',
        *finish('S_last',True),
    ]


def throwing():
    return [
        *seek('S_throw','S_warn',4),
        'S_throw.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        r'S_throw.CURRENT = eps /\ S_throw.FRAMES = eps', '$us_guard(S_throw)',
        '$lookup(S_throw.ENV,$ptascii("exception")) = (n_exception_cell)',
        'S_throw.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
        '~$comparison_read_object_value(S_throw,POBJECT n_exception)',
        '~$comparison_read_array_payload(S_throw[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_exception))]],PARRAY n_payload)',
        'S_throw.ARRAYS[n_root].ITEMS = S.ARRAYS[n_root].ITEMS',
        'S_throw.STORE[n_cell] = DEFINED (PARRAY n_payload)', *old_graph('S_throw'), *old_owners('S_throw',1),
        owners('S_throw','HARRAY n_root',1), owners('S_throw','HCELL n_cell',1),
        '$lookup(S_throw.ENV,$ptascii("source")) = eps', '$lookup(S_throw.ENV,$ptascii("deep")) = eps',
        '$lookup(S_throw.ENV,$ptascii("outside")) = eps',
        'S_throw.STORE[n_result] = DEFINED (PINT 41)', '$spaceship_read_array(S_throw,perrorread)',
        '$us_output(S_throw.EVENTS) = ' + text('P;B;H:1:1:29:1;'),
        'PhpStep: S_throw ~> S_discarded',
        'S_discarded = S_throw[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*][.ERRORHANDLER = S.ERRORHANDLER]',
        *[owners('S_discarded',node,0) for node in ('HARRAY n_root','HCELL n_cell','HARRAY n_payload','HARRAY n_middle','HARRAY n_leaf','HOBJECT n_old')],
        *destructor('S_pending','S_throw','n_old','P;B;H:1:1:29:1;','(n_exception)'),
        'pdestructionoperation_S_pending.SOURCE = THROW_SEARCH n_exception',
        *finish('S_pending',False),
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
        values = ['S_cut = $alias_dag_peer_budget_cut(' + run + ')']
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


PREFIX += '\ndec $alias_dag_peer_budget_cut(pstate) : pstate\ndef $alias_dag_peer_budget_cut(S_initial) = S_cut\n'
PREFIX += ''.join('  -- if ' + condition + '\n' for condition in budget_setup())


def checks(program,path,name):
    shared = name.startswith('alias-dag-shared-cell-replacement-')
    assert shared or name.startswith('alias-dag-supplied-throw-')
    if shared and (name.endswith('-domain') or name.endswith('-lifetime')):
        values = core(program,path,True)
        setup = front(program,path,True)
        domain = controls()
        offsets = [i for i in range(len(setup)-len(domain)+1)
                   if setup[i:i+len(domain)] == domain]
        assert len(offsets) == 1
        offset, = offsets
        if name.endswith('-domain'):
            return values[:offset+len(domain)]
        return values[:offset] + values[offset+len(domain):]
    return (budgets if name.endswith('-budget') else core)(program,path,shared)
