"""Reached shared DIRECT DAGs, physical edges, deep COW and pending cleanup."""
import base64
import json

from undefined_spaceship_protocol import text
from undefined_comparison_object_reference_array_review_protocol import (
    PREFIX as COMMON, destructor, owners, seek)

PREFIX = COMMON + r'''
def $us_stage(S, 6) = true
  -- if S.CURRENT =/= eps
  -- if S.RESULT = KNOWN PNULL
  -- if S.BASE = BASE_VALUE (KNOWN PNULL)
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("source")) = (n_current)
  -- if S_global.STORE[n_current] = DEFINED (PARRAY n_top)
  -- if S.ARRAYS[n_top].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_branch)), ENTRY (KINT 1) (DIRECT (PARRAY n_other))]
  -- if S.ARRAYS[n_branch].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_middle))]
  -- if S.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf)), ENTRY (KINT 1) (DIRECT (PARRAY n_old_leaf))]
  -- if S.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object)), ENTRY (KINT 1) (DIRECT (PINT 9))]
  -- if $class_instanceof(S,POBJECT n_object,$ptascii("CapturedDagNew120"))
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
        state + '.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_branch)), ENTRY (KINT 1) (DIRECT (PARRAY n_branch))]',
        state + '.ARRAYS[n_branch].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_shared))]',
        state + '.ARRAYS[n_shared].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf)), ENTRY (KINT 1) (DIRECT (PARRAY n_leaf))]',
        state + '.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old)), ENTRY (KINT 1) (DIRECT (PINT 4))]',
    ]


def graph_owners(state, root_count):
    return [owners(state, node, count) for node, count in (
        ('HARRAY n_root', root_count), ('HARRAY n_branch', 2),
        ('HARRAY n_shared', 1), ('HARRAY n_leaf', 2), ('HOBJECT n_old', 1))]


def dropped(state):
    return [owners(state, node, 0) for node in
            ('HARRAY n_root', 'HARRAY n_branch', 'HARRAY n_shared', 'HARRAY n_leaf', 'HOBJECT n_old')]


def controls():
    return [
        '$comparison_read_direct_array(S,PARRAY n_branch,eps)',
        '$comparison_read_direct_array(S,PARRAY n_shared,[n_root,n_branch])',
        '$comparison_read_direct_entries(S,[ENTRY (KINT 0) (DIRECT (PARRAY n_leaf)), ENTRY (KINT 1) (DIRECT (PARRAY n_leaf))],[n_root,n_branch,n_shared])',
        '~$comparison_read_direct_array(S,PARRAY n_leaf,[n_leaf])',
        '$comparison_read_array_payload(S,PARRAY n_leaf)',
        '~$comparison_read_array_payload(S,PARRAY n_shared)',
        '~$comparison_read_array_payload(S,PARRAY n_root)',
        'S_self = S[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf))]]',
        '~$comparison_read_direct_array(S_self,PARRAY n_branch,eps)',
        '~$spaceship_read_array(S_self,perrorread)', '$error_read_valid(S_self,perrorread)',
        'S_cross = S[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_branch))]]',
        '~$comparison_read_direct_array(S_cross,PARRAY n_branch,eps)',
        '~$spaceship_read_array(S_cross,perrorread)', '$error_read_valid(S_cross,perrorread)',
        'S_alias = S[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (ALIAS n_source)]]',
        '~$comparison_read_direct_array(S_alias,PARRAY n_branch,eps)',
        '~$comparison_read_direct_entries(S,[ENTRY (KINT 0) (ALIAS n_source)],eps)',
        '~$spaceship_read_array(S_alias,perrorread)',
        '~$comparison_read_direct_entries(S,[ENTRY (KINT 0) UNINITIALIZED],eps)',
        '~$comparison_read_direct_entries(S,[ENTRY (KINT 0) (INDIRECT n_old ($ptascii("tag")))],eps)',
        '~$comparison_read_direct_entries(S,[ENTRY (KINT 0) (DIRECT PUNDEFINED)],eps)',
        'S_dead_branch = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_branch)]',
        '~$spaceship_read_array(S_dead_branch,perrorread)', '$error_read_valid(S_dead_branch,perrorread)',
        'S_dead_leaf = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_leaf)]',
        '~$comparison_read_direct_array(S_dead_leaf,PARRAY n_branch,eps)',
        'S_dead_object = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_old)]',
        '~$spaceship_read_array(S_dead_object,perrorread)',
        '~$comparison_read_direct_array(S,PARRAY (|S.ARRAYS|),eps)',
        'S_outside = S[.ALLOCATIONS = (HARRAY (|S.ARRAYS|)) :: S.ALLOCATIONS]',
        '~$comparison_read_direct_array(S_outside,PARRAY (|S.ARRAYS|),eps)',
        '~$error_read_valid(S[.CODE = eps],perrorread)', '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        'perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_root)) 999][.TASK = BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_root)) 999][.LINE = 999]',
        '$spaceship_read_array(S,perrorread_bad)', '~$error_read_valid(S,perrorread_bad)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_bad])',
        'perrorread_foreign = perrorread[.ORIGINAL = BINARY_RIGHT BITXOR (KNOWN (PARRAY n_root)) perrorread.LINE][.TASK = BINARY_RIGHT BITXOR (KNOWN (PARRAY n_root)) perrorread.LINE]',
        '~$spaceship_read_array(S,perrorread_foreign)', '~$error_read_valid(S,perrorread_foreign)',
    ]


def front(program, path, captured):
    line = 34 if captured else 30
    return initial(program, path) + [
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
        '$lookup(S.ENV,$ptascii("result")) = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 41)',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        *graph('S'),
        '$node_children(S,HARRAY n_root) = [HARRAY n_branch,HARRAY n_branch]',
        '$node_children(S,HARRAY n_branch) = [HARRAY n_shared]',
        '$node_children(S,HARRAY n_shared) = [HARRAY n_leaf,HARRAY n_leaf]',
        '$node_children(S,HARRAY n_leaf) = [HOBJECT n_old]',
        *graph_owners('S', 3 if captured else 2),
        *['$heap_count(HARRAY ' + n + ',$pools_nodes(S.POOLS)) = 0'
          for n in ('n_root', 'n_branch', 'n_shared', 'n_leaf')],
        '$comparison_read_object_value(S,POBJECT n_old)',
        '~(n_old <- S.DESTRUCTION.CALLED)',
        '$spaceship_read_array(S,perrorread)', '~$spaceship_read_other(S,perrorread)',
        '$us_output(S.EVENTS) = ' + text('P;'),
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(line) + ')',
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


def finish(start, output, value):
    return [
        'S_done = $drive_steps(' + start + ',8000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(output), '$us_guard(S_done)',
        'S_done.STORE[n_result] = DEFINED (' + value + ')',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        r'S_done.DESTRUCTION.CALLS = eps /\ S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
        *['~((' + node + ') <- S_done.ALLOCATIONS)' for node in
          ('HARRAY n_root', 'HARRAY n_branch', 'HARRAY n_shared', 'HARRAY n_leaf', 'HOBJECT n_old')],
        'n_old <- S_done.DESTRUCTION.CALLED',
    ]


def expected(captured):
    return ('P;B;I:1:1:1:1:1;N:1:1:1:1:1;H:1:1:34:1;O:1:1:1:1;R:1:1:1:1:1;END;'
            if captured else 'P;B;H:1:1:30:1;D:1:1:1;C:1:1:1:1:1:1:1:1:1;F;END;')


def core(program, path, captured):
    values = front(program, path, captured)
    if not captured:
        return values + throwing()
    return values + [
        '$lookup(S.ENV,$ptascii("copy")) = (n_copy)', 'S.STORE[n_copy] = DEFINED (PARRAY n_root)',
        *seek('S_cow', 'S_warn', 6), '$us_guard(S_cow)', 'S_cow_global = $global_table_view(S_cow)',
        'S_cow_global.STORE[n_source] = DEFINED (PARRAY n_root_new)',
        'S_cow_global.STORE[n_copy] = DEFINED (PARRAY n_root)',
        'S_cow.ARRAYS[n_root_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_branch_new)), ENTRY (KINT 1) (DIRECT (PARRAY n_branch))]',
        'S_cow.ARRAYS[n_branch_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_shared_new))]',
        'S_cow.ARRAYS[n_shared_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf_new)), ENTRY (KINT 1) (DIRECT (PARRAY n_leaf))]',
        'S_cow.ARRAYS[n_leaf_new].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new)), ENTRY (KINT 1) (DIRECT (PINT 9))]',
        'n_new =/= n_old',
        *[new + ' =/= ' + old for new, old in (('n_root_new','n_root'),('n_branch_new','n_branch'),('n_shared_new','n_shared'),('n_leaf_new','n_leaf'))],
        *graph('S_cow'),
        owners('S_cow', 'HARRAY n_root', 2), owners('S_cow', 'HARRAY n_branch', 3),
        owners('S_cow', 'HARRAY n_shared', 1), owners('S_cow', 'HARRAY n_leaf', 3),
        *[owners('S_cow', node, 1) for node in
          ('HARRAY n_root_new','HARRAY n_branch_new','HARRAY n_shared_new','HARRAY n_leaf_new','HOBJECT n_new','HOBJECT n_old')],
        '$us_output(S_cow.EVENTS) = ' + text('P;B;'),
        *destructor('S_inline', 'S_cow', 'n_new', 'P;B;I:1:1:1:1:1;', inside=True),
        *seek('S_return', 'S_inline', 2),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread', 'S_return.RESULT = KNOWN (PBOOL true)',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        *seek('S_resume', 'S_return', 3),
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)', '$spaceship_read_array(S_resume,perrorread)', '$us_guard(S_resume)',
        r'S_resume.CURRENT = eps /\ S_resume.FRAMES = eps',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', 'S_resume.EVENTS = S_return.EVENTS',
        'S_resume.STORE[n_result] = DEFINED (PINT 41)',
        *graph('S_resume'), *graph_owners('S_resume', 1),
        '~(n_old <- S_resume.DESTRUCTION.CALLED)', 'n_new <- S_resume.DESTRUCTION.CALLED',
        *['~((' + node + ') <- S_resume.ALLOCATIONS)' for node in
          ('HARRAY n_root_new','HARRAY n_branch_new','HARRAY n_shared_new','HARRAY n_leaf_new','HOBJECT n_new')],
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PINT 1)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        *dropped('S_compared'),
        *destructor('S_last', 'S_restored', 'n_old', 'P;B;I:1:1:1:1:1;N:1:1:1:1:1;H:1:1:34:1;'),
        'pdestructionoperation_S_last.SOURCE = perrorread.TASK', 'pdestructionoperation_S_last.VALUE = KNOWN (PINT 1)',
        *finish('S_last', expected(True), 'PINT 1'),
    ]


def throwing():
    return [
        *seek('S_throw', 'S_warn', 4),
        'S_throw.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        r'S_throw.CURRENT = eps /\ S_throw.FRAMES = eps', '$us_guard(S_throw)',
        '$lookup(S_throw.ENV,$ptascii("exception")) = (n_exception_cell)',
        'S_throw.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
        '~$comparison_read_object_value(S_throw,POBJECT n_exception)',
        'S_internal = S_throw[.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_exception))]]',
        '~$comparison_read_direct_array(S_internal,PARRAY n_branch,eps)',
        *graph('S_throw'), *graph_owners('S_throw', 1),
        '$lookup(S_throw.ENV,$ptascii("source")) = eps',
        'S_throw.STORE[n_result] = DEFINED (PINT 41)', '$spaceship_read_array(S_throw,perrorread)',
        '$us_output(S_throw.EVENTS) = ' + text('P;B;H:1:1:30:1;'),
        'PhpStep: S_throw ~> S_discarded',
        'S_discarded = S_throw[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*][.ERRORHANDLER = S.ERRORHANDLER]',
        *dropped('S_discarded'),
        *destructor('S_pending', 'S_throw', 'n_old', 'P;B;H:1:1:30:1;', '(n_exception)'),
        'pdestructionoperation_S_pending.SOURCE = THROW_SEARCH n_exception',
        *finish('S_pending', expected(False), 'PINT 41'),
    ]


def budgets(program, path, captured):
    values = initial(program, path) + [
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]',
    ]
    if captured:
        values += [*seek('S_return','S_warn',2), *seek('S_cut','S_return',3)]
    else:
        values += seek('S_cut','S_warn',4)
    return values + [
        'S_done = $drive_steps(S_cut,8000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected(captured)), '$us_guard(S_done)',
        'S_one = $drive_steps(S_cut,1)', 'S_one.COMPLETION = BUDGET',
        '$drive_steps(S_one[.COMPLETION = NORMAL],8000) = S_done',
        'S_zero = $drive_steps(S_cut,0)', 'S_zero = S_cut[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],8000) = S_done',
    ]


def checks(program, path, name):
    captured = name.startswith('direct-dag-captured-cow-')
    assert captured or name.startswith('direct-dag-supplied-throw-')
    return (budgets if name.endswith('-budget') else core)(program, path, captured)
