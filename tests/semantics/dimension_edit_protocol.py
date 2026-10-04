"""Reached unset ownership and coalesce quiet-to-write continuations."""
from error_handler_protocol import PREFIX as BASE_PREFIX

PREFIX = BASE_PREFIX + r'''
dec $edit_write_stage(pstate) : bool
def $edit_write_stage(S) = true -- if S.TODO = (KEY_WRITE_RESULT pkeywrite) :: ptask_tail*
def $edit_write_stage(S) = false -- otherwise
dec $seek_edit_write(pstate, nat) : pstate
def $seek_edit_write(S, n) = S -- if $edit_write_stage(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $seek_edit_write(S, n) = $seek_edit_write($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$edit_write_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $seek_edit_write(S, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $edit_unset_tail_stage(pstate) : bool
def $edit_unset_tail_stage(S) = true
  -- if S.TODO = (KEY_UNSET_RESULT pkeyread) :: ptask_tail*
  -- if pkeyread.PHASE = KEY_FLOAT PRECISIONLOSS eps
def $edit_unset_tail_stage(S) = false -- otherwise
dec $seek_edit_unset_tail(pstate, nat) : pstate
def $seek_edit_unset_tail(S, n) = S -- if $edit_unset_tail_stage(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $seek_edit_unset_tail(S, n) = $seek_edit_unset_tail($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$edit_unset_tail_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $seek_edit_unset_tail(S, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''

GUARDS = ['$call_current_valid(S)', '$call_frames_valid(S, S.FRAMES)',
          '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
FINISH = ['S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
          'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.GLOBALTABLE = eps',
          'S_done.HELD = eps', 'S_done.BORROWEDREAD = eps', 'S_done.TRACE = eps',
          'S_done.ERRORHANDLER.CALLBACK = eps', 'S_done.ERRORHANDLERS = eps',
          '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']
UNSET = ['S.TODO = (KEY_UNSET_RESULT pkeyread) :: ptask_tail*',
         'ptask_tail* = (KEY_UNSET_FINISH pkeyread.SITE pbase) :: ptask_after*',
         'pbase = BASE_DIM (BASE_VALUE (VARIABLE $ptascii("a249") z_base)) pkeyread.INPUT pkeyread.LINE',
         'S.ORIGIN = (pkeyread.SITE)', 'pkeyread.LINE = 4',
         '~pkeyread.GLOBAL', 'pkeyread.MODE = KEY_R',
         'pkeyread.OWNERS = BASE_VALUE (KNOWN PNULL)',
         'pkeyread.BASE = PARRAY n_selected',
         '$key_unset_source(S, pkeyread.SITE, pbase)',
         '$key_unset_valid(S, pkeyread)', '$call_task_valid(S, KEY_UNSET_RESULT pkeyread)',
         '$task_nodes(KEY_UNSET_FINISH pkeyread.SITE pbase) = eps',
         '~((HARRAY n_selected) <- $pools_nodes(S.POOLS))',
         '~$key_unset_valid(S, pkeyread[.SITE = PORIGIN 999 eps])',
         '~$key_unset_valid(S, pkeyread[.LINE = 999])',
         '~$key_unset_valid(S, pkeyread[.MODE = KEY_IS])',
         '~$key_unset_valid(S, pkeyread[.GLOBAL = true])',
         '~$key_unset_valid(S[.ORIGIN = eps], pkeyread)',
         '~$key_unset_valid(S, pkeyread[.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)])',
         '~$key_unset_source(S, pkeyread.SITE, BASE_DIM (BASE_VALUE (KNOWN pkeyread.BASE)) pkeyread.INPUT pkeyread.LINE)']

CASES = [
    ('unset-undefined-key-deletes-shared-table-without-null-notice',
     'unset-undefined-key-keeps-empty-key-without-null-notice',
     'S.TODO = (KEY_UNSET_RESULT pkeyread) :: ptask_tail* -- if pkeyread.PHASE = KEY_CV', [
        *UNSET, 'pkeyread.PHASE = KEY_CV',
        'pkeyread.INPUT = VARIABLE $ptascii("key249") 4', 'pkeyread.NAME = $ptascii("key249")',
        'pkeyread.VALUE = PNULL', 'pkeyread.KEY = KSTRING eps',
        '$task_nodes(KEY_UNSET_RESULT pkeyread) = eps',
        '$lookup(S.ENV, $ptascii("a249")) = (n_a)',
        '$lookup(S.ENV, $ptascii("held249")) = (n_held)', 'n_a =/= n_held',
        'S.STORE[n_a] = DEFINED (PARRAY n_selected)', 'S.STORE[n_held] = DEFINED (PARRAY n_selected)',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_selected) = 2',
        '$entry_lookup(S.ARRAYS[n_selected].ITEMS, KSTRING eps) = (DIRECT (PINT 5))',
        '$lookup(S.ENV, $ptascii("key249")) = (n_key)',
        'S.STORE[n_key] = DEFINED (PSTRING $ptascii("changed"))',
        '$key_unset_live(S, pkeyread)', '$outputs(S.EVENTS) = $ptascii("U;")',
        '~$key_unset_valid(S, pkeyread[.PHASE = KEY_NULL])',
        '~$key_unset_valid(S, pkeyread[.KEY = KINT 0])',
        '~$key_unset_valid(S, pkeyread[.INPUT = KNOWN PNULL])',
        *GUARDS, 'PhpStep: S ~> S_deleted', 'S_deleted.TODO = ptask_tail*',
        'S_deleted.RESULT = KNOWN PNULL', 'S_deleted.LOCATION = NOWHERE',
        'S_deleted.ENV = S.ENV', 'S_deleted.STORE = S.STORE',
        '$entry_lookup(S_deleted.ARRAYS[n_selected].ITEMS, KSTRING eps) = eps',
        'S_deleted.ARRAYS[n_selected].POSITIONS = eps',
        'S_deleted.ARRAYS[n_selected].NEXT = S.ARRAYS[n_selected].NEXT',
        '$outputs(S_deleted.EVENTS) = $ptascii("U;")',
        'S_done = $drive(S_deleted, 3000)', *FINISH,
        'S_done.STORE[n_a] = DEFINED (PARRAY n_selected)',
        'S_done.STORE[n_held] = DEFINED (PARRAY n_selected)',
        'S_done.STORE[n_key] = DEFINED (PSTRING $ptascii("changed"))',
        '$lookup(S_done.ENV, $ptascii("hits249")) = (n_hits)', 'S_done.STORE[n_hits] = DEFINED (PINT 1)',
        '$entry_lookup(S_done.ARRAYS[n_selected].ITEMS, KSTRING eps) = eps',
     ]),
    ('unset-nan-tail-keeps-protection-and-deletes-moved-table',
     'unset-nan-tail-retains-table-through-moved-keeper',
     'S.TODO = (KEY_UNSET_RESULT pkeyread) :: ptask_tail* -- if pkeyread.PHASE = KEY_FLOAT RANGEWARNING ([PRECISIONLOSS])', [
        *UNSET, 'pkeyread.PHASE = KEY_FLOAT RANGEWARNING ([PRECISIONLOSS])',
        'pkeyread.INPUT = VARIABLE $ptascii("key249") 4', 'pkeyread.NAME = eps',
        'pkeyread.VALUE = PFLOAT n_bits', '$float_long(n_bits, true) = (0, [RANGEWARNING, PRECISIONLOSS])',
        'pkeyread.KEY = KINT 0', '$task_nodes(KEY_UNSET_RESULT pkeyread) = [HARRAY n_selected]',
        '$lookup(S.ENV, $ptascii("a249")) = eps', '$lookup(S.ENV, $ptascii("held249")) = (n_held)',
        'S.STORE[n_held] = DEFINED (PARRAY n_selected)',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_selected) = 2',
        '$entry_lookup(S.ARRAYS[n_selected].ITEMS, KINT 0) = (DIRECT (PINT 5))',
        '$entry_lookup(S.ARRAYS[n_selected].ITEMS, KINT 7) = (DIRECT (PINT 11))',
        '$lookup(S.ENV, $ptascii("key249")) = (n_key)',
        'S.STORE[n_key] = DEFINED (PFLOAT 4620130267728707584)',
        '$key_unset_live(S, pkeyread)', '$outputs(S.EVENTS) = $ptascii("W;")',
        '~$key_unset_valid(S, pkeyread[.PHASE = KEY_FLOAT RANGEWARNING eps])',
        '~$key_unset_valid(S, pkeyread[.PHASE = KEY_FLOAT PRECISIONLOSS ([RANGEWARNING])])',
        '~$key_unset_valid(S, pkeyread[.PHASE = KEY_FLOAT RANGEWARNING (RANGEWARNING :: [PRECISIONLOSS])])',
        '~$key_unset_valid(S, pkeyread[.KEY = KINT 1])',
        *GUARDS, 'PhpStep: S ~> S_next',
        'S_next.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = KEY_UNSET_RESULT pkeyread_next',
        'pkeyread_next = pkeyread[.PHASE = KEY_FLOAT PRECISIONLOSS eps]',
        'perrorcall.LEVEL = 8192', 'perrorcall.LINE = 4',
        '$error_call_valid(S_next, perrorcall)',
        '$heap_owners($heap_prune($heap_graph(S_next)), HARRAY n_selected) = 2',
        'S_final_reached = $seek_edit_unset_tail(S_next, 1500)', 'S_final = S_final_reached[.COMPLETION = NORMAL]',
        'S_final.TODO = (KEY_UNSET_RESULT pkeyread_next) :: ptask_tail*',
        '$outputs(S_final.EVENTS) = $ptascii("W;D;")',
        '$key_unset_valid(S_final, pkeyread_next)',
        'PhpStep: S_final ~> S_deleted', 'S_deleted.TODO = ptask_tail*',
        '$entry_lookup(S_deleted.ARRAYS[n_selected].ITEMS, KINT 0) = eps',
        '$entry_lookup(S_deleted.ARRAYS[n_selected].ITEMS, KINT 7) = (DIRECT (PINT 11))',
        '$heap_owners($heap_prune($heap_graph(S_deleted)), HARRAY n_selected) = 1',
        'S_done = $drive(S_deleted, 3000)', *FINISH,
        'S_done.STORE[n_held] = DEFINED (PARRAY n_selected)', '$lookup(S_done.ENV, $ptascii("a249")) = eps',
        'S_done.STORE[n_key] = DEFINED (PFLOAT 4620130267728707584)',
        '$entry_lookup(S_done.ARRAYS[n_selected].ITEMS, KINT 0) = eps',
     ]),
    ('coalesce-captured-quiet-null-precedes-rhs-and-write-abort',
     'coalesce-null-quiet-capture-precedes-rhs-and-write-copy-abort',
     'S.TODO = (KEY_READ_RESULT pkeyread) :: ptask_tail* -- if pkeyread.PHASE = KEY_NULL', [
        'S.TODO = (KEY_READ_RESULT pkeyread) :: ptask_tail*',
        'ptask_tail* = (ORIGIN_RETURN (porigin_root)) :: (KEY_READ_FINISH porigin_root (KEY_COALESCE_RESULT pbase false z_coalesce)) :: ptask_after*',
        '$key_coalesce_source(S, porigin_root, pbase, false, z_coalesce) = (pkeyread.SITE)',
        'pbase = BASE_DIM (BASE_VALUE (VARIABLE $ptascii("a249") z_base)) (KNOWN PNULL) 5',
        'pkeyread.MODE = KEY_IS', '~pkeyread.GLOBAL', 'pkeyread.PHASE = KEY_NULL',
        'pkeyread.INPUT = KNOWN PNULL', 'pkeyread.VALUE = PNULL', 'pkeyread.KEY = KSTRING eps',
        'pkeyread.LINE = 5', 'pkeyread.BASE = PARRAY n_old',
        'pkeyread.OWNERS = BASE_VALUE (VARIABLE $ptascii("a249") z_base)',
        '$key_read_valid(S, pkeyread)', '$task_nodes(KEY_READ_RESULT pkeyread) = [HARRAY n_old]',
        '$task_nodes(KEY_READ_FINISH porigin_root (KEY_COALESCE_RESULT pbase false z_coalesce)) = eps',
        '~((HARRAY n_old) <- $pools_nodes(S.POOLS))',
        '$lookup(S.ENV, $ptascii("a249")) = (n_a)', 'S.STORE[n_a] = DEFINED (PARRAY n_new)', 'n_new =/= n_old',
        '$lookup(S.ENV, $ptascii("held249")) = (n_held)', 'S.STORE[n_held] = DEFINED (PARRAY n_old)',
        '$entry_lookup(S.ARRAYS[n_old].ITEMS, KSTRING eps) = (DIRECT PNULL)',
        '$entry_lookup(S.ARRAYS[n_new].ITEMS, KSTRING eps) = (DIRECT (PINT 13))',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_old) = 2',
        '$outputs(S.EVENTS) = $ptascii("D1;")',
        '~$key_read_valid(S, pkeyread[.INPUT = KNOWN (PINT 0)])',
        '~$key_read_valid(S, pkeyread[.KEY = KINT 0])',
        '$key_coalesce_source(S, porigin_root, pbase, true, z_coalesce) = eps',
        *GUARDS, 'PhpStep: S ~> S_quiet', 'S_quiet.RESULT = KNOWN PNULL', 'S_quiet.TODO = ptask_tail*',
        'S_write_reached = $seek_edit_write(S_quiet, 2000)', 'S_write = S_write_reached[.COMPLETION = NORMAL]',
        'S_write.TODO = (KEY_WRITE_RESULT pkeywrite) :: ptask_write_tail*',
        'pkeywrite.READ.BASE = PARRAY n_new', 'pkeywrite.READ.INPUT = KNOWN PNULL',
        'pkeywrite.READ.MODE = KEY_R', 'pkeywrite.READ.PHASE = KEY_NULL', 'pkeywrite.READ.KEY = KSTRING eps',
        '~pkeywrite.RW', 'pkeywrite.PLACE = ROOT n_a',
        '$lookup(S_write.ENV, $ptascii("later249")) = (n_later)', 'S_write.STORE[n_later] = DEFINED (PARRAY n_new)',
        '$heap_owners($heap_prune($heap_graph(S_write)), HARRAY n_new) = 3',
        '~$key_write_single(S_write, pkeywrite)', '$key_write_valid(S_write, pkeywrite)',
        '$outputs(S_write.EVENTS) = $ptascii("D1;S;D2;")',
        'ptask_write_tail* = (ORIGIN_RETURN (porigin_root)) :: (KEY_WRITE_FINISH pkeywriter) :: ptask_after*',
        'pkeywriter.TASK = COALESCE_ASSIGN_WRITE pkeywriter.BASE false z_coalesce',
        'pkeywriter.RHS = KNOWN (PINT 7)', 'pkeywriter.TEMP = eps',
        '$key_writer_valid(S_write, pkeywriter, ptask_after*)',
        '$heap_valid($heap_graph(S_write))', 'PhpStep: S_write ~> S_aborted',
        'S_aborted.LOCATION = NOWHERE', 'S_aborted.RESULT = KNOWN PNULL',
        'S_aborted.TODO = ptask_write_tail*',
        '$heap_owners($heap_prune($heap_graph(S_aborted)), HARRAY n_new) = 2',
        'S_done = $drive(S_aborted, 3000)', *FINISH,
        'S_done.STORE[n_a] = DEFINED (PARRAY n_new)', 'S_done.STORE[n_later] = DEFINED (PARRAY n_new)',
        '$entry_lookup(S_done.ARRAYS[n_new].ITEMS, KSTRING eps) = (DIRECT (PINT 13))',
        '$entry_lookup(S_done.ARRAYS[n_old].ITEMS, KSTRING eps) = (DIRECT PNULL)',
        '$lookup(S_done.ENV, $ptascii("result249")) = (n_result)', 'S_done.STORE[n_result] = DEFINED PNULL',
     ]),
]
