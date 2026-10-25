"""Reached depth-four COW and current root-cell DAG lifetime checks."""
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
  -- if $lookup(S_global.ENV,$ptascii("saved")) = (n_current)
  -- if S_global.STORE[n_current] = DEFINED (PARRAY n_root)
  -- if S.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_branch))]
  -- if S.ARRAYS[n_branch].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_shared))]
  -- if S.ARRAYS[n_shared].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf)), ENTRY (KINT 1) (DIRECT (PARRAY n_other))]
  -- if S.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object)), ENTRY (KINT 1) (DIRECT (PINT 9))]
  -- if $class_instanceof(S,POBJECT n_object,$ptascii("NewDirectGraph120"))
def $us_stage(S, 7) = true
  -- if S.CURRENT =/= eps
  -- if S.RESULT = KNOWN PNULL
  -- if S.BASE = BASE_VALUE (KNOWN PNULL)
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.RELEASES = eps
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("right")) = (n_current)
  -- if S_global.STORE[n_current] = DEFINED (PARRAY n_root)
  -- if S.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_middle))]
  -- if S.ARRAYS[n_middle].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf))]
  -- if S.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object)), ENTRY (KINT 1) (DIRECT (PINT 7))]
  -- if $class_instanceof(S,POBJECT n_object,$ptascii("NewLiveDirect120"))
'''


def initial(program, path):
    return [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', *seek('S_front', 'S_initial', 0),
        'S = S_front', '$error_read_plan(S) = (perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
    ]


def graph(state, captured):
    values = []
    if captured:
        values += [state + '.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_branch))]',
                   state + '.ARRAYS[n_branch].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_shared))]']
    else:
        values += [state + '.ARRAYS[n_root].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_shared))]']
    return values + [
        state + '.ARRAYS[n_shared].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf)), ENTRY (KINT 1) (DIRECT (PARRAY n_leaf))]',
        state + '.ARRAYS[n_leaf].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_old)), ENTRY (KINT 1) (DIRECT (PINT 4))]',
    ]


def graph_owners(state, root_count, captured):
    nodes = [('HARRAY n_root', root_count), ('HARRAY n_shared', 1),
             ('HARRAY n_leaf', 2), ('HOBJECT n_old', 1)]
    if captured:
        nodes.insert(1, ('HARRAY n_branch', 1))
    return [owners(state, node, count) for node, count in nodes]


def warning(line):
    return [
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_warn = $prune_allocations($error_read_begin(S))',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread', 'perrorcall.LEVEL = 2',
        'perrorcall.LINE = ' + str(line),
        'perrorcall.MESSAGE = $ptascii("Undefined variable $missing")',
        'perrorcall.EVENT = WARNING ($ptascii("missing")) ' + str(line),
        '$error_call_valid(S_warn,perrorcall)', '$us_guard(S_warn)', 'S_warn.EVENTS = S.EVENTS',
    ]


def front(program, path, captured):
    line = 31 if captured else 30
    original = ('BINARY_RIGHT SPACESHIP (KNOWN (PARRAY n_root)) 31' if captured
                else 'BINARY_RIGHT EQUAL (VARIABLE ($ptascii("missing")) z_missing) 30')
    task = original if captured else 'BINARY_RIGHT EQUAL (KNOWN PNULL) 30'
    values = initial(program, path) + [
        '$us_stage(S,0)', '$us_guard(S)', '$error_read_valid(S,perrorread)',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        'perrorread.ORIGINAL = ' + original, 'perrorread.TASK = ' + task,
        'perrorread.INPUT = VARIABLE ($ptascii("' + ('missing' if captured else 'right') + '")) ' + ('z_missing' if captured else 'z_right'),
        'perrorread.RESULT = ' + ('KNOWN PNULL' if captured else 'perrorread.INPUT'),
        'S.RESULT = perrorread.INPUT', 'perrorread.NAME = $ptascii("missing")',
        'perrorread.LINE = ' + str(line),
        '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        '$base_nodes(perrorread.BASE) = eps',
        '$task_nodes(ERROR_READ_RESULT perrorread) = ' + ('[HARRAY n_root]' if captured else 'eps'),
        '$lookup(S.ENV,$ptascii("' + ('saved' if captured else 'right') + '")) = (n_current)',
        'S.STORE[n_current] = DEFINED (PARRAY n_root)',
        '$lookup(S.ENV,$ptascii("copy")) = (n_copy)', 'S.STORE[n_copy] = DEFINED (PARRAY n_root)',
        '$lookup(S.ENV,$ptascii("result")) = (n_result)', 'S.STORE[n_result] = DEFINED (PINT 41)',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        *graph('S', captured), *graph_owners('S', 3, captured),
        '$node_children(S,HARRAY n_root) = [HARRAY ' + ('n_branch' if captured else 'n_shared') + ']',
        '$node_children(S,HARRAY n_shared) = [HARRAY n_leaf,HARRAY n_leaf]',
        '$node_children(S,HARRAY n_leaf) = [HOBJECT n_old]',
        '$comparison_read_object_value(S,POBJECT n_old)',
        '$comparison_read_direct_array(S,PARRAY n_root,eps)',
        '$comparison_read_direct_entries(S,[ENTRY (KINT 0) (DIRECT (PARRAY n_leaf)), ENTRY (KINT 1) (DIRECT (PARRAY n_leaf))],[n_root,n_shared])',
        '~$comparison_read_direct_array(S,PARRAY n_leaf,[n_leaf])',
        '~(n_old <- S.DESTRUCTION.CALLED)',
        '$us_output(S.EVENTS) = ' + text('P;' if captured else ''),
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(line) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
        *['$heap_count(HARRAY ' + node + ',$pools_nodes(S.POOLS)) = 0'
          for node in (('n_root', 'n_branch', 'n_shared', 'n_leaf') if captured else ('n_root', 'n_shared', 'n_leaf'))],
    ]
    if captured:
        values += [
            '$node_children(S,HARRAY n_branch) = [HARRAY n_shared]',
            '$spaceship_read_array(S,perrorread)', '~$spaceship_read_other(S,perrorread)',
        ]
    else:
        values += [
            '$lookup(S.ENV,$ptascii("outside")) = (n_current)',
            '$lookup(S.ENV,$ptascii("held")) = (n_held)', 'S.STORE[n_held] = DEFINED (PARRAY n_root)',
            '$call_reference_operand_valid(S,REFERENCE n_current)',
            '$node_children(S,HCELL n_current) = [HARRAY n_root]', owners('S', 'HCELL n_current', 2),
            '$scalar_compare_read_array(S,perrorread)', '~$scalar_compare_read_other(S,perrorread)',
        ]
    return values + warning(line) + [
        '~$error_read_valid(S[.CODE = eps],perrorread)', '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        '~$error_call_valid(S_warn,perrorcall[.LEVEL = 8])',
        '~$error_call_valid(S_warn,perrorcall[.MESSAGE = eps])',
    ]


def returned(start):
    return [
        *seek('S_return', start, 2),
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        'S_return.RESULT = KNOWN (PBOOL true)',
        r'S_return.CURRENT = eps /\ S_return.FRAMES = eps', '$us_guard(S_return)',
        *seek('S_resume', 'S_return', 3),
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)', '$us_guard(S_resume)',
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', 'S_resume.EVENTS = S_return.EVENTS',
        'S_resume.STORE[n_result] = DEFINED (PINT 41)',
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
        'S_resume.STORE[n_missing] = DEFINED (PBOOL true)',
    ]


def restore(captured):
    return [
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps', 'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (' + ('PINT 1' if captured else 'PBOOL false') + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS', 'S_compared.STORE = S_resume.STORE',
    ]


def expected(captured):
    return ('P;B;I:1:1:1:1:1;N:1:1:1;H:1:1:31:1;O:1:1:1;R:1:1:1:1:1;END;'
            if captured else 'B;I:1:1:1:1;O:1:1:1;H:1:1:30:1;R:1:1:1:1:1;A:1:1;N:1:1:1;END;')


def finish(start, captured):
    nodes = ['HARRAY n_root', 'HARRAY n_shared', 'HARRAY n_leaf', 'HOBJECT n_old', 'HOBJECT n_new']
    if captured:
        nodes += ['HARRAY n_branch', 'HARRAY n_root_new', 'HARRAY n_branch_new', 'HARRAY n_shared_new', 'HARRAY n_leaf_new']
    else:
        nodes += ['HCELL n_current', 'HARRAY n_root_new', 'HARRAY n_middle_new', 'HARRAY n_leaf_new']
    return [
        'S_done = $drive_steps(' + start + ',8000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected(captured)), '$us_guard(S_done)',
        'S_done.STORE[n_result] = DEFINED (' + ('PINT 1' if captured else 'PBOOL false') + ')',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        r'S_done.DESTRUCTION.CALLS = eps /\ S_done.DESTRUCTION.RELEASES = eps /\ S_done.DESTRUCTION.OPERATIONS = eps',
        *['~((' + node + ') <- S_done.ALLOCATIONS)' for node in nodes],
        'n_old <- S_done.DESTRUCTION.CALLED', 'n_new <- S_done.DESTRUCTION.CALLED',
    ]


def core(program, path, captured):
    values = front(program, path, captured)
    if not captured:
        return values + live()
    return values + [
        *seek('S_cow', 'S_warn', 6), '$us_guard(S_cow)', 'S_cow_global = $global_table_view(S_cow)',
        'S_cow_global.STORE[n_current] = DEFINED (PARRAY n_root_new)',
        'S_cow_global.STORE[n_copy] = DEFINED (PARRAY n_root)',
        'S_cow.ARRAYS[n_root_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_branch_new))]',
        'S_cow.ARRAYS[n_branch_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_shared_new))]',
        'S_cow.ARRAYS[n_shared_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf_new)), ENTRY (KINT 1) (DIRECT (PARRAY n_leaf))]',
        'S_cow.ARRAYS[n_leaf_new].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new)), ENTRY (KINT 1) (DIRECT (PINT 9))]',
        'n_new =/= n_old',
        *[new + ' =/= ' + old for new, old in (('n_root_new', 'n_root'), ('n_branch_new', 'n_branch'), ('n_shared_new', 'n_shared'), ('n_leaf_new', 'n_leaf'))],
        *graph('S_cow', True),
        owners('S_cow', 'HARRAY n_root', 2), owners('S_cow', 'HARRAY n_branch', 1),
        owners('S_cow', 'HARRAY n_shared', 1), owners('S_cow', 'HARRAY n_leaf', 3),
        *[owners('S_cow', node, 1) for node in ('HARRAY n_root_new', 'HARRAY n_branch_new', 'HARRAY n_shared_new', 'HARRAY n_leaf_new', 'HOBJECT n_old', 'HOBJECT n_new')],
        '$us_output(S_cow.EVENTS) = ' + text('P;B;'),
        *destructor('S_inline', 'S_cow', 'n_new', 'P;B;I:1:1:1:1:1;', inside=True),
        *returned('S_inline'),
        '$spaceship_read_array(S_resume,perrorread)',
        *graph('S_resume', True), *graph_owners('S_resume', 1, True),
        'S_resume.STORE[n_current] = DEFINED (PARRAY n_empty)', 'S_resume.ARRAYS[n_empty].ITEMS = eps',
        'S_resume.STORE[n_copy] = DEFINED (PARRAY n_copy_empty)', 'S_resume.ARRAYS[n_copy_empty].ITEMS = eps',
        '$us_output(S_resume.EVENTS) = ' + text('P;B;I:1:1:1:1:1;N:1:1:1;H:1:1:31:1;'),
        'n_new <- S_resume.DESTRUCTION.CALLED', '~(n_old <- S_resume.DESTRUCTION.CALLED)',
        *['~((' + node + ') <- S_resume.ALLOCATIONS)' for node in ('HARRAY n_root_new', 'HARRAY n_branch_new', 'HARRAY n_shared_new', 'HARRAY n_leaf_new', 'HOBJECT n_new')],
        *restore(True),
        *[owners('S_compared', node, 0) for node in ('HARRAY n_root', 'HARRAY n_branch', 'HARRAY n_shared', 'HARRAY n_leaf', 'HOBJECT n_old')],
        *destructor('S_last', 'S_restored', 'n_old', 'P;B;I:1:1:1:1:1;N:1:1:1;H:1:1:31:1;'),
        'pdestructionoperation_S_last.SOURCE = perrorread.TASK',
        'pdestructionoperation_S_last.VALUE = KNOWN (PINT 1)',
        *finish('S_last', True),
    ]


def live():
    return [
        *seek('S_rebound', 'S_warn', 7), '$us_guard(S_rebound)',
        'S_rebound_global = $global_table_view(S_rebound)',
        'S_rebound_global.STORE[n_current] = DEFINED (PARRAY n_root_new)',
        'S_rebound_global.STORE[n_copy] = DEFINED (PARRAY n_root)',
        'S_rebound_global.STORE[n_held] = DEFINED (PARRAY n_root)',
        'S_rebound.ARRAYS[n_root_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_middle_new))]',
        'S_rebound.ARRAYS[n_middle_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf_new))]',
        'S_rebound.ARRAYS[n_leaf_new].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_new)), ENTRY (KINT 1) (DIRECT (PINT 7))]',
        'n_root_new =/= n_root', 'n_new =/= n_old', *graph('S_rebound', False),
        *graph_owners('S_rebound', 2, False), owners('S_rebound', 'HCELL n_current', 2),
        *[owners('S_rebound', node, 1) for node in ('HARRAY n_root_new', 'HARRAY n_middle_new', 'HARRAY n_leaf_new', 'HOBJECT n_new')],
        '$us_output(S_rebound.EVENTS) = ' + text('B;'),
        *destructor('S_old', 'S_rebound', 'n_old', 'B;I:1:1:1:1;', inside=True),
        *returned('S_old'), '$scalar_compare_read_array(S_resume,perrorread)',
        'S_resume.STORE[n_current] = DEFINED (PARRAY n_root_new)',
        'S_resume.STORE[n_copy] = DEFINED (PARRAY n_empty)', 'S_resume.ARRAYS[n_empty].ITEMS = eps',
        'S_resume.STORE[n_held] = DEFINED (PARRAY n_held_empty)', 'S_resume.ARRAYS[n_held_empty].ITEMS = eps',
        '$lookup(S_resume.ENV,$ptascii("right")) = (n_current)',
        '$lookup(S_resume.ENV,$ptascii("outside")) = (n_current)',
        '$node_children(S_resume,HCELL n_current) = [HARRAY n_root_new]',
        owners('S_resume', 'HCELL n_current', 2),
        *[owners('S_resume', node, 1) for node in ('HARRAY n_root_new', 'HARRAY n_middle_new', 'HARRAY n_leaf_new', 'HOBJECT n_new')],
        *['~((' + node + ') <- S_resume.ALLOCATIONS)' for node in ('HARRAY n_root', 'HARRAY n_shared', 'HARRAY n_leaf', 'HOBJECT n_old')],
        'n_old <- S_resume.DESTRUCTION.CALLED', '~(n_new <- S_resume.DESTRUCTION.CALLED)',
        '$us_output(S_resume.EVENTS) = ' + text('B;I:1:1:1:1;O:1:1:1;H:1:1:30:1;'),
        'S_nested_alias = S_resume[.ARRAYS[n_leaf_new].ITEMS = [ENTRY (KINT 0) (ALIAS n_current)]]',
        '~$scalar_compare_read_array(S_nested_alias,perrorread)', '$error_read_valid(S_nested_alias,perrorread)',
        'PhpStep: S_nested_alias ~> S_denied',
        'S_denied = S_nested_alias[.TODO = eps][.COMPLETION = UNSUPPORTED "scalar comparison warning changed right operand"]',
        *restore(False),
        owners('S_compared', 'HCELL n_current', 2), owners('S_compared', 'HARRAY n_root_new', 1),
        *destructor('S_last', 'S_compared', 'n_new', 'B;I:1:1:1:1;O:1:1:1;H:1:1:30:1;R:1:1:1:1:1;A:1:1;', result='PBOOL false'),
        '$lookup(S_last.ENV,$ptascii("right")) = eps', '$lookup(S_last.ENV,$ptascii("outside")) = eps',
        *finish('S_last', False),
    ]


def budgets(program, path, captured):
    return initial(program, path) + [
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]',
        *seek('S_return', 'S_warn', 2), *seek('S_cut', 'S_return', 3),
        'S_done = $drive_steps(S_cut,8000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected(captured)), '$us_guard(S_done)',
        'S_one = $drive_steps(S_cut,1)', 'S_one.COMPLETION = BUDGET',
        '$drive_steps(S_one[.COMPLETION = NORMAL],8000) = S_done',
        'S_zero = $drive_steps(S_cut,0)', 'S_zero = S_cut[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],8000) = S_done',
    ]


def checks(program, path, name):
    captured = name.startswith('direct-graph-captured-depth-four-')
    assert captured or name.startswith('direct-graph-live-root-alias-')
    return (budgets if name.endswith('-budget') else core)(program, path, captured)
