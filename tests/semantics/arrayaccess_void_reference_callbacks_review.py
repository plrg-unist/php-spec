"""A void Set boundary still schedules its mandatory Notice without an RV."""
import json

PREFIX = r'''
dec $aavoid_review_stage(pstate) : bool
def $aavoid_review_stage(S) = true
  -- if S.TODO = (RETURN_REF_NULL z) :: ptask*
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ACCESS_RESULT paccess) :: ptask_saved*
  -- if paccess.PHASE = ACCESS_CALL $ptascii("offsetSet")
def $aavoid_review_stage(S) = false -- otherwise
dec $aavoid_review_seek(pstate, nat) : pstate
def $aavoid_review_seek(S, n) = S
  -- if $aavoid_review_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $aavoid_review_seek(S, n) = $aavoid_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$aavoid_review_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $aavoid_review_seek(S, n) = S
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
        'S_paused = $aavoid_review_seek(S_initial[.COMPLETION = NORMAL], 1000)',
        r'S_paused.COMPLETION = NORMAL \/ S_paused.COMPLETION = BUDGET',
        'S = S_paused[.COMPLETION = NORMAL]',
        'S.TODO = (RETURN_REF_NULL z) :: ptask_tail*',
        'S.CURRENT = (pcallcontext)',
        'S.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ACCESS_RESULT paccess) :: ptask_saved*',
        'paccess.PHASE = ACCESS_CALL $ptascii("offsetSet")',
        'paccess.MODE = ACCESS_SET',
        'paccess.OFFSET = PINT 1',
        '$target_function(S, $context_target(pcallcontext)) = (pfunction)',
        'pfunction.SIGNATURE.BYREF',
        'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "void"]))]',
        '$arrayaccess_signature($ptascii("offsetSet")).RETURNS = pfunction.SIGNATURE.RETURNS',
        '$reference_returning(S)',
        '~$access_reference_signature(pfunction.SIGNATURE)',
        '~$access_reference_scalar_types(pfunction.SIGNATURE.RETURNS)',
        '$access_reference_call_signature(pfunction.SIGNATURE, $ptascii("offsetSet"))',
        '$access_reference_call_signature(pfunction.SIGNATURE, $ptascii("offsetUnset"))',
        '$access_reference_call_signature(pfunction.SIGNATURE, $ptascii("offsetGet"))',
        '$access_reference_call_signature(pfunction.SIGNATURE, $ptascii("offsetExists"))',
        'S.ORIGIN = (pfunction.ORIGIN)',
        'z = pfunction.ENDLINE',
        '$reference_return_null_valid(S, z)',
        '$reference_notice_source(S, pfunction.ORIGIN, KNOWN PNULL, z, REF_NOTICE_NULL)',
        '~$call_task_valid(S, RETURN_REF_NULL $(z + 1))',
        '$access_frame(S, pcallcontext, pframe)',
        '$reference_call_used(S, paccess.SITE)',
        '$reference_callback_used(S, pcallcontext) = (false)',
        '~$reference_return_used(S)',
        '$lookup(S.ENV, $ptascii("rhs")) = (n_rhs)',
        'S_global = $global_table_view(S)',
        '$lookup(S_global.ENV, $ptascii("rhs")) = (n_rhs)',
        '$lookup(S_global.ENV, $ptascii("alias")) = (n_rhs)',
        'S.STORE[n_rhs] = DEFINED (PINT 9)',
        'n_rhs <- S.REFCELLS',
        '$heap_owners($heap_graph(S), HCELL n_rhs) = 3',
        *guards('S'),
        'PhpStep: S ~> S_unwind',
        'S_unwind.COMPLETION = NORMAL',
        'S_unwind.TODO = (RETURN_REF_UNWIND (KNOWN PNULL) z false pfunction.ORIGIN) :: ptask_unwind*',
        '$reference_notice_count(S_unwind.TODO) = 1',
        '$reference_notice_end(S_unwind.TODO, pfunction.ORIGIN, z, REF_NOTICE_NULL)',
        '$reference_notice_presence(S_unwind)',
        '$task_nodes(REF_RETURN_NOTICE pfunction.ORIGIN z REF_NOTICE_NULL) = eps',
        'S_unwind.RESULT = KNOWN PNULL',
        'S_unwind.STORE = S.STORE',
        'S_unwind.REFCELLS = S.REFCELLS',
        'S_unwind.ALLOCATIONS = S.ALLOCATIONS',
        'S_unwind.EVENTS = S.EVENTS',
        '$heap_owners($heap_graph(S_unwind), HCELL n_rhs) = 3',
        *guards('S_unwind'),
        'S_zero = $drive_steps(S, 0)',
        'S_zero = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S, 1)',
        'S_one.COMPLETION = BUDGET',
        'S_one.TODO = S_unwind.TODO',
        'S_one.RESULT = S_unwind.RESULT',
        'S_one.CURRENT = S_unwind.CURRENT',
        'S_one.FRAMES = S_unwind.FRAMES',
        'S_one.STORE = S_unwind.STORE',
        'S_one.REFCELLS = S_unwind.REFCELLS',
        'S_one.EVENTS = S_unwind.EVENTS',
        '$call_descriptors_valid(S_one)',
        '$heap_valid($heap_graph(S_one))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks))
