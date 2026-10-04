"""Reached nested quiet owners, memoized lines and aborted writable temporaries."""
from error_handler_protocol import PREFIX as BASE_PREFIX

PREFIX = BASE_PREFIX + r'''
dec $coalesce_tail_stage(pstate) : bool
def $coalesce_tail_stage(S) = true
  -- if S.TODO = (KEY_READ_RESULT pkeyread) :: ptask_tail*
  -- if pkeyread.PHASE = KEY_FLOAT PRECISIONLOSS eps
def $coalesce_tail_stage(S) = false -- otherwise
dec $seek_coalesce_tail(pstate, nat) : pstate
def $seek_coalesce_tail(S, n) = S -- if $coalesce_tail_stage(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $seek_coalesce_tail(S, n) = $seek_coalesce_tail($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$coalesce_tail_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $seek_coalesce_tail(S, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $coalesce_temp_stage(pstate) : bool
def $coalesce_temp_stage(S) = true
  -- if S.TODO = (KEY_WRITE_DIM poperand z b) :: ptask_tail*
  -- if S.LOCATION = NOWHERE
  -- if $key_coalesce_walk(S.TODO)
def $coalesce_temp_stage(S) = false -- otherwise
dec $seek_coalesce_temp(pstate, nat) : pstate
def $seek_coalesce_temp(S, n) = S -- if $coalesce_temp_stage(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $seek_coalesce_temp(S, n) = $seek_coalesce_temp($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$coalesce_temp_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $seek_coalesce_temp(S, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $coalesce_rhs_stage(pstate) : bool
def $coalesce_rhs_stage(S) = true -- if S.TODO = (KEY_COALESCE_RHS_RESULT pcoalesceread) :: ptask_tail*
def $coalesce_rhs_stage(S) = false -- otherwise
dec $seek_coalesce_rhs(pstate, nat) : pstate
def $seek_coalesce_rhs(S, n) = S -- if $coalesce_rhs_stage(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $seek_coalesce_rhs(S, n) = $seek_coalesce_rhs($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$coalesce_rhs_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $seek_coalesce_rhs(S, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''

GUARDS = ['$call_current_valid(S)', '$call_frames_valid(S, S.FRAMES)',
          '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
FINISH = ['S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
          'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
          'S_done.BORROWEDREAD = eps', 'S_done.TRACE = eps',
          'S_done.ERRORHANDLER.CALLBACK = eps', 'S_done.ERRORHANDLERS = eps',
          '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']

CASES = [
    ('nan-quiet-prefix-keeps-one-protection-and-real-child',
     'nan-prefix-ordered-tail-retains-moved-parent-and-real-cell',
     'S.TODO = (KEY_READ_RESULT pkeyread) :: ptask_tail* -- if pkeyread.PHASE = KEY_FLOAT RANGEWARNING ([PRECISIONLOSS])', [
        'S.TODO = (KEY_READ_RESULT pkeyread) :: ptask_tail*',
        'S.ORIGIN = (pkeyread.SITE)', 'pkeyread.LINE = 7',
        '~pkeyread.GLOBAL', 'pkeyread.MODE = KEY_IS',
        'pkeyread.PHASE = KEY_FLOAT RANGEWARNING ([PRECISIONLOSS])',
        'pkeyread.INPUT = VARIABLE $ptascii("key") 7', 'pkeyread.VALUE = PFLOAT n_bits',
        '$float_long(n_bits, true) = (0, [RANGEWARNING, PRECISIONLOSS])',
        'pkeyread.KEY = KINT 0', 'pkeyread.NAME = eps',
        'pkeyread.BASE = PARRAY n_parent',
        'pkeyread.OWNERS = BASE_VALUE (VARIABLE $ptascii("a") 7)',
        '$key_read_valid(S, pkeyread)', '$call_task_valid(S, KEY_READ_RESULT pkeyread)',
        '$task_nodes(KEY_READ_RESULT pkeyread) = [HARRAY n_parent]',
        '~$key_read_valid(S, pkeyread[.SITE = PORIGIN 999 eps])',
        '~$key_read_valid(S, pkeyread[.LINE = 999])',
        '~$key_read_valid(S, pkeyread[.MODE = KEY_R])',
        '~$key_read_valid(S, pkeyread[.PHASE = KEY_FLOAT RANGEWARNING eps])',
        '~$key_read_valid(S, pkeyread[.PHASE = KEY_FLOAT PRECISIONLOSS ([RANGEWARNING])])',
        '~$key_read_valid(S, pkeyread[.KEY = KINT 1])',
        '~$key_read_valid(S, pkeyread[.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)])',
        '$lookup(S.ENV, $ptascii("a")) = eps', '$lookup(S.ENV, $ptascii("cell")) = eps',
        '$lookup(S.ENV, $ptascii("held")) = (n_held)',
        'S.STORE[n_held] = DEFINED (PARRAY n_parent)',
        '~((HARRAY n_parent) <- $pools_nodes(S.POOLS))',
        '$entry_lookup(S.ARRAYS[n_parent].ITEMS, KINT 0) = (DIRECT (PARRAY n_child))',
        '$entry_lookup(S.ARRAYS[n_child].ITEMS, KINT 1) = (ALIAS n_cell)',
        'S.STORE[n_cell] = DEFINED (PINT 17)',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_parent) = 2',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_child) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_cell) = 2',
        '$outputs(S.EVENTS) = $ptascii("W;")', *GUARDS,
        'PhpStep: S ~> S_next',
        'S_next.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = KEY_READ_RESULT pkeyread_next',
        'pkeyread_next = pkeyread[.PHASE = KEY_FLOAT PRECISIONLOSS eps]',
        'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 7', '$error_call_valid(S_next, perrorcall)',
        '$heap_owners($heap_prune($heap_graph(S_next)), HARRAY n_parent) = 2',
        'S_tail_reached = $seek_coalesce_tail(S_next, 1500)', 'S_tail = S_tail_reached[.COMPLETION = NORMAL]',
        'S_tail.TODO = (KEY_READ_RESULT pkeyread_next) :: ptask_tail*',
        '$key_read_valid(S_tail, pkeyread_next)', '$outputs(S_tail.EVENTS) = $ptascii("W;D;")',
        'PhpStep: S_tail ~> S_selected',
        'S_selected.RESULT = KNOWN (PARRAY n_child)', 'S_selected.TODO = ptask_tail*',
        '$heap_owners($heap_prune($heap_graph(S_selected)), HARRAY n_parent) = 1',
        '$heap_owners($heap_prune($heap_graph(S_selected)), HARRAY n_child) = 2',
        'S_done = $drive(S_selected, 3000)', *FINISH,
        'S_done.STORE[n_cell] = DEFINED (PINT 17)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_cell) = 2',
     ]),
    ('multiline-prefix-write-and-late-rhs-have-distinct-lines',
     'multiline-late-rhs-uses-final-memoized-write-line',
     'S.TODO = (KEY_WRITE_RESULT pkeywrite) :: ptask_tail* -- if pkeywrite.READ.LINE = 7', [
        'S.TODO = (KEY_WRITE_RESULT pkeywrite) :: ptask_tail*',
        'pkeyread = pkeywrite.READ', 'S.ORIGIN = (pkeyread.SITE)',
        'pkeyread.LINE = 7', '~pkeyread.GLOBAL', 'pkeyread.MODE = KEY_R', '~pkeywrite.RW',
        'pkeyread.PHASE = KEY_FLOAT PRECISIONLOSS eps',
        'pkeyread.INPUT = KNOWN (PFLOAT 4609434218613702656)',
        'pkeyread.VALUE = PFLOAT 4609434218613702656', 'pkeyread.KEY = KINT 1',
        'pkeyread.OWNERS = BASE_VALUE (KNOWN PNULL)',
        'pkeyread.BASE = PARRAY n_parent',
        'ptask_tail* = (ORIGIN_RETURN (porigin_target)) :: (KEY_WRITE_DIM (VARIABLE $ptascii("inner") 10) 10 false) :: (ORIGIN_RETURN (porigin_assign)) :: (KEY_WRITE_FINISH pkeywriter) :: ptask_after*',
        'pkeywriter.TARGET = porigin_target', 'pkeywriter.SITE = porigin_assign',
        '$origin_child((porigin_target), [PCFIELD 0]) = (pkeyread.SITE)',
        'pkeywriter.TASK = COALESCE_ASSIGN_WRITE pkeywriter.BASE false z_task',
        '$code_expression_at_source(S, porigin_assign, eps) = (z_task)',
        'pkeywriter.RHS = VARIABLE $ptascii("missing") 11', 'pkeywriter.TEMP = eps',
        '$key_writer_valid(S, pkeywriter, ptask_after*)', '$key_write_valid(S, pkeywrite)',
        '$key_coalesce_write_context(S, S.TODO, pkeyread.SITE)',
        'pkeyread_view = $key_coalesce_read_view(S, pkeyread)', 'pkeyread_view.LINE = 8',
        '$key_read_input_source(S, pkeyread_view)',
        '~$key_write_valid(S, pkeywrite[.READ.LINE = 8])',
        '~$key_write_valid(S, pkeywrite[.READ.LINE = 10])',
        '~$key_write_valid(S, pkeywrite[.READ.MODE = KEY_IS])',
        '~$key_write_valid(S, pkeywrite[.RW = true])',
        '~$key_write_valid(S, pkeywrite[.READ.SITE = PORIGIN 999 eps])',
        '~$key_writer_valid(S, pkeywriter[.TARGET = pkeyread.SITE], ptask_after*)',
        '$lookup(S.ENV, $ptascii("a")) = (n_a)', 'S.STORE[n_a] = DEFINED (PARRAY n_parent)',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_parent) = 2',
        '$outputs(S.EVENTS) = $ptascii("K;D:8;D:10;D:7;")', *GUARDS,
        'PhpStep: S ~> S_selected', 'S_selected.LOCATION = ELEMENT n_parent (KINT 1)',
        'S_selected.TODO = ptask_tail*',
        'S_rhs_reached = $seek_coalesce_rhs(S_selected, 1500)', 'S_rhs = S_rhs_reached[.COMPLETION = NORMAL]',
        'S_rhs.TODO = (KEY_COALESCE_RHS_RESULT pcoalesceread) :: ptask_after_rhs*',
        '$key_coalesce_rhs_valid(S_rhs, pcoalesceread)',
        'pcoalesceread.LINE = 10', 'pcoalesceread.NAME = $ptascii("missing")',
        'pcoalesceread.WRITER.TARGET = porigin_target',
        'pcoalesceread.PLACE = ELEMENT n_child (KINT 1)',
        '$entry_lookup(S_rhs.ARRAYS[n_parent].ITEMS, KINT 1) = (DIRECT (PARRAY n_child))',
        '$entry_lookup(S_rhs.ARRAYS[n_child].ITEMS, KINT 1) = (DIRECT PNULL)',
        '$task_nodes(KEY_COALESCE_RHS_RESULT pcoalesceread) = eps',
        '~$key_coalesce_rhs_valid(S_rhs, pcoalesceread[.LINE = 11])',
        '~$key_coalesce_rhs_valid(S_rhs, pcoalesceread[.NAME = $ptascii("outer")])',
        '~$key_coalesce_rhs_valid(S_rhs, pcoalesceread[.PLACE = PROPERTY n_child eps])',
        '$lookup(S_rhs.ENV, $ptascii("missing")) = (n_missing)', 'S_rhs.STORE[n_missing] = DEFINED (PINT 37)',
        '$outputs(S_rhs.EVENTS) = $ptascii("K;D:8;D:10;D:7;D:10;U:10;")',
        'PhpStep: S_rhs ~> S_written', 'S_written.TODO = ptask_after_rhs*',
        'S_written.RESULT = KNOWN PNULL', 'S_written.STORE[n_missing] = DEFINED (PINT 37)',
        '$entry_lookup(S_written.ARRAYS[n_child].ITEMS, KINT 1) = (DIRECT PNULL)',
        'S_done = $drive(S_written, 3000)', *FINISH,
     ]),
    ('aborted-prefix-temporary-retains-computed-array-rhs-once',
     'computed-array-rhs-retains-real-cell-through-prefix-abort',
     'S.TODO = (KEY_WRITE_RESULT pkeywrite) :: ptask_tail* -- if pkeywrite.READ.PHASE = KEY_FLOAT PRECISIONLOSS eps -- if pkeywrite.READ.LINE = 6', [
        'S.TODO = (KEY_WRITE_RESULT pkeywrite) :: ptask_tail*',
        'pkeywrite.READ.LINE = 6', 'pkeywrite.READ.MODE = KEY_R', '~pkeywrite.RW',
        'pkeywrite.READ.BASE = PARRAY n_parent',
        'pkeywrite.READ.PHASE = KEY_FLOAT PRECISIONLOSS eps',
        'ptask_tail* = (ORIGIN_RETURN (porigin_target)) :: (KEY_WRITE_DIM (KNOWN (PINT 1)) 6 false) :: (ORIGIN_RETURN (porigin_assign)) :: (KEY_WRITE_FINISH pkeywriter) :: ptask_after*',
        'pkeywriter.SITE = porigin_assign', 'pkeywriter.TARGET = porigin_target', 'pkeywriter.TEMP = eps',
        'pkeywriter.RHS = KNOWN (PARRAY n_rhs)',
        '$key_write_valid(S, pkeywrite)', '$key_writer_valid(S, pkeywriter, ptask_after*)',
        '$entry_lookup(S.ARRAYS[n_rhs].ITEMS, KINT 0) = (ALIAS n_cell)',
        'S.STORE[n_cell] = DEFINED (PINT 5)',
        '~((HARRAY n_rhs) <- $pools_nodes(S.POOLS))',
        '$lookup(S.ENV, $ptascii("cell")) = eps', '$lookup(S.ENV, $ptascii("key")) = eps',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_parent) = 3',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_rhs) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HCELL n_cell) = 2',
        '~$key_write_single(S, pkeywrite)', '$outputs(S.EVENTS) = $ptascii("D;D;")', *GUARDS,
        'PhpStep: S ~> S_aborted', 'S_aborted.LOCATION = NOWHERE', 'S_aborted.TODO = ptask_tail*',
        'S_temp_reached = $seek_coalesce_temp(S_aborted, 1500)', 'S_temp = S_temp_reached[.COMPLETION = NORMAL]',
        'S_temp.ORIGIN = (porigin_target)',
        'S_temp.TODO = (KEY_WRITE_DIM (KNOWN (PINT 1)) 6 false) :: ptask_finish*',
        'n_temp = |S_temp.STORE|', 'PhpStep: S_temp ~> S_owned',
        'S_owned.TODO = (KEY_WRITE_DIM (KNOWN (PINT 1)) 6 false) :: (ORIGIN_RETURN (porigin_assign)) :: (KEY_WRITE_FINISH pkeywriter_owned) :: ptask_after*',
        'pkeywriter_owned.TEMP = ((pkeywrite.READ.SITE, n_temp))',
        'pkeywriter_owned.TASK = pkeywriter.TASK',
        'pkeywriter_owned.BASE = BASE_DIM (BASE_PLACE pkeywrite.READ.SITE NOWHERE) (KNOWN (PINT 1)) 6',
        'pkeywriter_owned.RHS = KNOWN (PARRAY n_rhs)', 'S_owned.LOCATION = ROOT n_temp',
        'S_owned.STORE[n_temp] = DEFINED PNULL', '(HCELL n_temp) <- S_owned.ALLOCATIONS',
        '$key_writer_valid(S_owned, pkeywriter_owned, ptask_after*)',
        '~$key_writer_valid(S_owned, pkeywriter_owned[.TEMP = eps], ptask_after*)',
        '~$key_writer_valid(S_owned, pkeywriter_owned[.BASE = BASE_DIM (BASE_PLACE pkeywrite.READ.SITE (ROOT n_temp)) (KNOWN (PINT 1)) 6], ptask_after*)',
        '~$key_writer_valid(S_owned, pkeywriter_owned[.BASE = BASE_DIM (BASE_PLACE pkeywrite.READ.SITE (ELEMENT n_parent (KINT 1))) (KNOWN (PINT 1)) 6], ptask_after*)',
        '$heap_owners($heap_prune($heap_graph(S_owned)), HCELL n_temp) = 1',
        '$heap_owners($heap_prune($heap_graph(S_owned)), HARRAY n_rhs) = 1',
        '$heap_owners($heap_prune($heap_graph(S_owned)), HCELL n_cell) = 2',
        'S_done = $drive(S_owned, 3000)', *FINISH,
        '~((HCELL n_temp) <- S_done.ALLOCATIONS)',
        'S_done.STORE[n_cell] = DEFINED (PINT 17)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_cell) = 2',
     ]),
]
