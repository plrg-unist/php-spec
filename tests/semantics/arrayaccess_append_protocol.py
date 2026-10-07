"""Source-reached computed-RHS append extraction and child compound Set owners."""
from error_handler_protocol import PREFIX as BASE_PREFIX

PREFIX = BASE_PREFIX + r'''
dec $append_leaf(pstate) : bool
def $append_leaf(S) = true
  -- if S.TODO = (KEY_WRITE_DIM (KNOWN (PSTRING ptbytes)) 13 false) :: ptask_tail*
  -- if ptbytes = $ptascii("leaf")
  -- if $container_writer(S.TODO) = (pkeywriter)
  -- if pkeywriter.BASE = BASE_DIM (BASE_RETURNED porigin n) (KNOWN (PSTRING ptbytes)) 13
def $append_leaf(S) = false -- otherwise
dec $seek_append_leaf(pstate, nat) : pstate
def $seek_append_leaf(S, n) = S
  -- if $append_leaf(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $seek_append_leaf(S, n) = $seek_append_leaf($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$append_leaf(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $seek_append_leaf(S, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def guards(state='S'):
    return [f'$call_current_valid({state})', f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})', f'$heap_valid($heap_graph({state}))']


FINISH = ['S_done.COMPLETION = NORMAL', 'S_done.TODO = eps', 'S_done.CURRENT = eps',
          'S_done.FRAMES = eps', 'S_done.HELD = eps', 'S_done.ERRORHANDLER.CALLBACK = eps',
          'S_done.ERRORHANDLERS = eps', *guards('S_done')]

CASES = [
    ('computed-rhs-append-extracts-sole-owned-row-before-leaf-write',
     'intermediate-append-leaf-computed-rhs-before-get',
     'S.TODO = (ACCESS_RESUME paccess) :: ptask_tail* -- if paccess.PHASE = ACCESS_NOTICE', [
        'S.TODO = (ACCESS_RESUME paccess) :: ptask_tail*',
        'paccess.MODE = ACCESS_FETCH false false', 'paccess.PHASE = ACCESS_NOTICE',
        'paccess.LINE = 13', 'paccess.VALUE = PARRAY n_parent',
        'paccess.OBJECT = (n_object)', '$access_valid(S, paccess)',
        '$lookup(S.ENV, $ptascii("o304")) = eps',
        '$container_writer(S.TODO) = (pkeywriter)',
        'pkeywriter.RHS = KNOWN (PINT 13)',
        '$origin_child((pkeywriter.TARGET), [PCFIELD 0]) = (porigin_append)',
        '$origin_child((porigin_append), [PCFIELD 0]) = (paccess.TARGET)',
        '$key_write_append_source(S, porigin_append, 13)',
        '~$key_write_append_source(S, paccess.TARGET, 13)',
        '$heap_owners($heap_prune($heap_graph(S)), HOBJECT n_object) = 1',
        '(HARRAY n_parent) <- $pools_nodes(S.POOLS)',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_parent) = 3',
        *guards(), 'PhpStep: S ~> S_cut', 'n_first = |S.STORE|',
        'S_cut.LOCATION = ROOT n_first',
        'S_cut.STORE[n_first] = DEFINED (PARRAY n_parent)',
        '$container_writer(S_cut.TODO) = (pkeywriter_cut)',
        'pkeywriter_cut.BASE = BASE_DIM (BASE_APPEND (BASE_RETURNED paccess.TARGET n_first) 13) (KNOWN (PSTRING $ptascii("leaf"))) 13',
        '$heap_owners($heap_prune($heap_graph(S_cut)), HCELL n_first) = 1',
        '$heap_owners($heap_prune($heap_graph(S_cut)), HOBJECT n_object) = 0',
        '$key_write_base_source(S_cut, porigin_append, BASE_APPEND (BASE_RETURNED paccess.TARGET n_first) 13)',
        '~$key_write_base_source(S_cut, porigin_append, BASE_DIM (BASE_RETURNED paccess.TARGET n_first) (KNOWN PNULL) 13)',
        '~$key_write_base_source(S_cut, porigin_append, BASE_APPEND (BASE_RETURNED paccess.TARGET n_first) 14)',
        'S_leaf_reached = $seek_append_leaf(S_cut, 100)',
        r'S_leaf_reached.COMPLETION = NORMAL \/ S_leaf_reached.COMPLETION = BUDGET',
        'S_leaf = S_leaf_reached[.COMPLETION = NORMAL]',
        '$container_writer(S_leaf.TODO) = (pkeywriter_leaf)',
        'pkeywriter_leaf.BASE = BASE_DIM (BASE_RETURNED porigin_append n_row) (KNOWN (PSTRING $ptascii("leaf"))) 13',
        'S_leaf.LOCATION = ROOT n_row', 'S_leaf.STORE[n_row] = UNDEFINED',
        '$heap_owners($heap_prune($heap_graph(S_leaf)), HCELL n_first) = 0',
        '~((HCELL n_first) <- S_leaf.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_leaf)), HCELL n_row) = 1',
        '$heap_owners($heap_prune($heap_graph(S_leaf)), HARRAY n_parent) = 2',
        *guards('S_leaf'), 'S_budget = $drive_steps(S_leaf, 1)',
        'S_budget.COMPLETION = BUDGET', *guards('S_budget'),
        'S_done = $drive(S_budget[.COMPLETION = NORMAL], 3000)', *FINISH,
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_row) = 0',
        '$lookup(S_done.ENV, $ptascii("r304")) = (n_result)',
        'S_done.STORE[n_result] = DEFINED (PINT 13)',
        '$entry_lookup(S_done.ARRAYS[n_parent].ITEMS, KINT 0) = eps',
    ]),
    ('child-null-key-append-compound-set-preserves-real-owner-and-result',
     'child-append-compound-uses-null-key-and-sole-returned-object',
     'S.TODO = (ACCESS_RESULT paccess) :: ptask_tail* -- if paccess.TASK = KEY_WRITE_APPEND 25 true -- if paccess.PHASE = ACCESS_CALL $ptascii("offsetSet")', [
        'S.TODO = (ACCESS_RESULT paccess) :: ptask_tail*',
        'paccess.TASK = KEY_WRITE_APPEND 25 true',
        'paccess.MODE = ACCESS_COMPOUND ADD (PINT 5)',
        'paccess.PHASE = ACCESS_CALL $ptascii("offsetSet")',
        'paccess.LINE = 25', 'paccess.KEYLINE = 25', 'paccess.INPUT = KNOWN PNULL',
        'paccess.OFFSET = PNULL', 'paccess.VALUE = PINT 22',
        'paccess.RHS = VARIABLE $ptascii("rhs304") 25', 'paccess.SELECTED = paccess.RHS',
        'paccess.OUTER', '~paccess.LATCH', 'paccess.OBJECT = (n_child)',
        '$access_valid(S, paccess)', '$container_writer(S.TODO) = (pkeywriter)',
        'pkeywriter.BASE = BASE_APPEND (BASE_RETURNED porigin_parent n_parent) 25',
        'S.STORE[n_parent] = DEFINED (POBJECT n_child)',
        '$lookup(S.ENV, $ptascii("inner304")) = eps', '$lookup(S.ENV, $ptascii("o304")) = eps',
        '$task_nodes(ACCESS_RESULT paccess) = [HOBJECT n_child, HOBJECT n_child]',
        '$heap_owners($heap_prune($heap_graph(S)), HOBJECT n_child) = 3',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_parent) = 1',
        '~$access_valid(S, paccess[.INPUT = KNOWN (PINT 1)][.OFFSET = PINT 1])',
        '~$access_valid(S, paccess[.TASK = KEY_WRITE_APPEND 25 false])',
        '~$access_valid(S, paccess[.TASK = KEY_WRITE_APPEND 24 true][.LINE = 24][.KEYLINE = 24])',
        '~$access_valid(S, paccess[.MODE = ACCESS_SET])',
        '~$access_valid(S, paccess[.OBJECT = eps])',
        *guards(), 'PhpStep: S ~> S_raw', 'S_raw.RESULT = KNOWN (PINT 22)',
        'S_raw.TODO = $access_write_end(ptask_tail*)',
        '$heap_owners($heap_prune($heap_graph(S_raw)), HCELL n_parent) = 0',
        '$heap_owners($heap_prune($heap_graph(S_raw)), HOBJECT n_child) = 0',
        'S_budget = $drive_steps(S, 1)', 'S_budget.COMPLETION = BUDGET',
        'S_budget.RESULT = S_raw.RESULT', 'S_budget.TODO = S_raw.TODO',
        '~((HCELL n_parent) <- S_budget.ALLOCATIONS)',
        '~((HOBJECT n_child) <- S_budget.ALLOCATIONS)', *guards('S_budget'),
        'S_done = $drive(S_budget[.COMPLETION = NORMAL], 3000)', *FINISH,
        '$lookup(S_done.ENV, $ptascii("r304")) = (n_result)',
        'S_done.STORE[n_result] = DEFINED (PINT 22)',
        '$lookup(S_done.ENV, $ptascii("saved304")) = (n_saved)',
        'S_done.STORE[n_saved] = DEFINED (PINT 22)',
    ]),
]
