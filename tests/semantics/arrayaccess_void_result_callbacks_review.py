"""A discarded implicit void Get still materializes its demanded NULL RV."""
import json

PREFIX = r'''
dec $aavoidresult_review_stage(pstate) : bool
def $aavoidresult_review_stage(S) = true
  -- if S.TODO = (REF_RETURN_NOTICE_RESULT porigin (KNOWN PNULL) z REF_NOTICE_NULL) :: eps
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ACCESS_RESULT paccess) :: ptask_saved*
  -- if paccess.PHASE = ACCESS_CALL $ptascii("offsetGet")
def $aavoidresult_review_stage(S) = false -- otherwise
dec $aavoidresult_review_seek(pstate, nat) : pstate
def $aavoidresult_review_seek(S, n) = S
  -- if $aavoidresult_review_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $aavoidresult_review_seek(S, n) = $aavoidresult_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$aavoidresult_review_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $aavoidresult_review_seek(S, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def guards(state):
    return [f'$call_current_valid({state})',
            f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_paused = $aavoidresult_review_seek(S_initial[.COMPLETION = NORMAL], 1000)',
        r'S_paused.COMPLETION = NORMAL \/ S_paused.COMPLETION = BUDGET',
        'S = S_paused[.COMPLETION = NORMAL]',
        'S.TODO = [REF_RETURN_NOTICE_RESULT porigin (KNOWN PNULL) z REF_NOTICE_NULL]',
        'S.CURRENT = (pcallcontext)',
        'S.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ACCESS_RESULT paccess) :: ptask_saved*',
        'paccess.PHASE = ACCESS_CALL $ptascii("offsetGet")',
        'paccess.MODE = ACCESS_READ KEY_R',
        'paccess.OFFSET = PINT 1',
        'paccess.OBJECT = (n_receiver)',
        '$target_function(S, $context_target(pcallcontext)) = (pfunction)',
        '$call_function_name(S, pfunction) = $ptascii("VoidResultReview::offsetGet")',
        'pfunction.SIGNATURE.BYREF',
        'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "void"]))]',
        '$arrayaccess_signature($ptascii("offsetGet")).RETURNS =/= pfunction.SIGNATURE.RETURNS',
        'porigin = pfunction.ORIGIN',
        'S.ORIGIN = (pfunction.ORIGIN)',
        'z = pfunction.ENDLINE',
        '$reference_return_null_valid(S, z)',
        '$reference_notice_source(S, porigin, KNOWN PNULL, z, REF_NOTICE_NULL)',
        '~$reference_notice_source(S, porigin, KNOWN PNULL, $(z + 1), REF_NOTICE_NULL)',
        '$reference_notice_stage(S, porigin, KNOWN PNULL, z, REF_NOTICE_NULL)',
        '$call_task_valid(S, REF_RETURN_NOTICE_RESULT porigin (KNOWN PNULL) z REF_NOTICE_NULL)',
        '~$access_reference_signature(pfunction.SIGNATURE)',
        '~$access_reference_scalar_types(pfunction.SIGNATURE.RETURNS)',
        '$access_reference_call_signature(pfunction.SIGNATURE, $ptascii("offsetGet"))',
        '$access_reference_call_signature(pfunction.SIGNATURE, $ptascii("offsetExists"))',
        '$access_frame(S, pcallcontext, pframe)',
        '~$reference_call_used(S, paccess.SITE)',
        '$reference_callback_used(S, pcallcontext) = (true)',
        '$reference_return_used(S)',
        '~$finally_return_pending(S)',
        '$reference_notice_count(S.TODO) = 0',
        *guards('S'),
        'n = |S.STORE|',
        'S_materialized = $reference_notice_materialize($hold_task_inputs(S), KNOWN PNULL)',
        'S_materialized.RESULT = REFERENCE n',
        'S_materialized.STORE = S.STORE ++ [DEFINED PNULL]',
        'S_materialized.ALLOCATIONS = S.ALLOCATIONS ++ [HCELL n]',
        'n <- S_materialized.REFCELLS',
        '$heap_owners($heap_prune($heap_graph(S_materialized)), HCELL n) = 1',
        'S_materialized.CURRENT = S.CURRENT',
        'S_materialized.FRAMES = S.FRAMES',
        'S_materialized.EVENTS = S.EVENTS',
        'PhpStep: S ~> S_after',
        'S_after.COMPLETION = NORMAL',
        'S_after.RESULT = REFERENCE n',
        'S_after.STORE[n] = DEFINED PNULL',
        '(HCELL n) <- S_after.ALLOCATIONS',
        'n <- S_after.REFCELLS',
        '$heap_owners($heap_prune($heap_graph(S_after)), HCELL n) = 1',
        'S_after.TODO = pframe.TODO',
        'S_after.CURRENT = pframe.CONTEXT',
        'S_after.FRAMES = pframe_tail*',
        'S_after.ORIGIN = pframe.ORIGIN',
        'S_after.EVENTS = S.EVENTS',
        '$reference_notice_count(S_after.TODO) = 0',
        '$access_valid(S_after, paccess)',
        *guards('S_after'),
        'S_zero = $drive_steps(S, 0)',
        'S_zero = S[.COMPLETION = BUDGET]',
        'S_after.GC.BUFFER = eps',
        'S_after.GC.FREE = eps',
        'S_after.GC.ACTIVE = eps',
        'S_after.GC.PLAN = eps',
        'S_after.GC.WORKER = eps',
        '$gc_possible_root(S_after, HOBJECT n_receiver)',
        'S_one = $drive_steps(S, 1)',
        'S_one.COMPLETION = BUDGET',
        'S_one.RESULT = REFERENCE n',
        'S_one.TODO = S_after.TODO',
        'S_one.CURRENT = S_after.CURRENT',
        'S_one.FRAMES = S_after.FRAMES',
        'S_one.ORIGIN = S_after.ORIGIN',
        'S_one.STORE = S_after.STORE',
        'S_one.REFCELLS = S_after.REFCELLS',
        'S_one.ALLOCATIONS = S_after.ALLOCATIONS',
        'S_one.EVENTS = S_after.EVENTS',
        '$heap_owners($heap_prune($heap_graph(S_one)), HCELL n) = 1',
        # drive_steps applies receiver-owner bookkeeping after the raw return:
        # 40:literal_reference_debt_step -> 301:gc_transition_owners/decrement.
        # The surviving ordinary receiver enters the empty buffer; collection
        # stays inactive and every other GC field retains its raw value.
        'S_one.GC = S_after.GC[.BUFFER = [GC_ROOT (HOBJECT n_receiver)]]',
        *guards('S_one'),
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks))
