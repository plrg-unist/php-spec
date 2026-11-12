"""Render one source-derived fixture; the paired runner owns its execution."""
import json

PREFIX = r'''
dec $aaexists_review_stage(pstate, bool, paccessmode, bool) : bool
def $aaexists_review_stage(S, false, paccessmode, b_key) = true
  -- if S.TODO = (RETURN_REF_FETCH z) :: ptask*
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ACCESS_RESULT paccess) :: ptask_saved*
  -- if paccess.PHASE = ACCESS_CALL $ptascii("offsetExists")
  -- if paccess.MODE = paccessmode
  -- if paccess.OFFSET = PBOOL b_key
def $aaexists_review_stage(S, true, paccessmode, b_key) = true
  -- if S.TODO = (ACCESS_RESULT paccess) :: ptask*
  -- if paccess.PHASE = ACCESS_CALL $ptascii("offsetExists")
  -- if paccess.MODE = paccessmode
  -- if paccess.OFFSET = PBOOL b_key
def $aaexists_review_stage(S, b_result, paccessmode, b_key) = false -- otherwise
dec $aaexists_review_seek(pstate, nat, bool, paccessmode, bool) : pstate
def $aaexists_review_seek(S, n, b_result, paccessmode, b_key) = S
  -- if $aaexists_review_stage(S, b_result, paccessmode, b_key)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $aaexists_review_seek(S, n, b_result, paccessmode, b_key) = $aaexists_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)), b_result, paccessmode, b_key)
  -- if ~$aaexists_review_stage(S, b_result, paccessmode, b_key)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $aaexists_review_seek(S, n, b_result, paccessmode, b_key) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $aaexists_review_outputs(pevent*) : nat*
def $aaexists_review_outputs(eps) = eps
def $aaexists_review_outputs((OUTPUT n*) :: pevent*) = n* ++ $aaexists_review_outputs(pevent*)
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
        'S_demand_paused = $aaexists_review_seek(S_initial[.COMPLETION = NORMAL], 1000, false, ACCESS_READ (KEY_TEST false), false)',
        'S_demand = S_demand_paused[.COMPLETION = NORMAL]',
        'S_demand.TODO = (RETURN_REF_FETCH z_demand) :: ptask_demand*',
        'S_demand.CURRENT = (pcallcontext_demand)',
        'S_demand.FRAMES = pframe_demand :: pframe_demand_tail*',
        'pframe_demand.TODO = (ACCESS_RESULT paccess_demand) :: ptask_demand_saved*',
        'paccess_demand.PHASE = ACCESS_CALL $ptascii("offsetExists")',
        '$access_frame(S_demand, pcallcontext_demand, pframe_demand)',
        '$reference_callback_used(S_demand, pcallcontext_demand) = (true)',
        '$reference_return_used(S_demand)',
        '~$reference_verifies(S_demand)',
        '$target_function(S_demand, $context_target(pcallcontext_demand)) = (pfunction_demand)',
        'pfunction_demand.SIGNATURE.BYREF',
        'pfunction_demand.SIGNATURE.RETURNS = eps',
        '$access_reference_signature(pfunction_demand.SIGNATURE)',
        '$access_reference_signature(pfunction_demand.SIGNATURE[.RETURNS = ([(PTBRANCH ([PTBUILTIN "mixed"]))])])',
        '~$access_reference_signature(pfunction_demand.SIGNATURE[.RETURNS = ([(PTBRANCH ([PTBUILTIN "bool"]))])])',
        'pframe_bad = pframe_demand[.TODO = (ACCESS_RESULT paccess_demand[.LINE = $(paccess_demand.LINE + 1)]) :: ptask_demand_saved*]',
        'S_bad = S_demand[.FRAMES = pframe_bad :: pframe_demand_tail*]',
        '$heap_graph(S_bad) = $heap_graph(S_demand)',
        '~$access_frame(S_bad, pcallcontext_demand, pframe_bad)',
        '$reference_callback_used(S_bad, pcallcontext_demand) = eps',
        '~$call_frames_valid(S_bad, S_bad.FRAMES)',
        *guards('S_demand'),
    ]
    checks += [
        'paccess_other = paccess_demand[.PHASE = ACCESS_CALL $ptascii("offsetGet")]',
        '~$access_method_selected(S_demand, paccess_other, $context_target(pcallcontext_demand))',
        'S_paused = $aaexists_review_seek(S_demand, 1000, true, ACCESS_READ (KEY_TEST false), false)',
        'S = S_paused[.COMPLETION = NORMAL]',
        'S.TODO = (ACCESS_RESULT paccess) :: ptask_tail*',
        'paccess.PHASE = ACCESS_CALL $ptascii("offsetExists")',
        'paccess.MODE = ACCESS_READ (KEY_TEST false)',
        'paccess.OFFSET = PBOOL false',
        'S.RESULT = REFERENCE n',
        'S.STORE[n] = DEFINED (PBOOL false)',
        'n <- S.REFCELLS',
        '$call_reference_operand_valid(S, S.RESULT)',
        '$access_valid(S, paccess)',
        '~$access_reference_result_pending(S)',
        '$heap_owners($heap_graph(S), HCELL n) = 1',
        'S_read = $quiet_operand(S, S.RESULT)',
        'S_read.RESULT = KNOWN (PBOOL false)',
        'S_read.STORE = S.STORE',
        'S_read.ALLOCATIONS = S.ALLOCATIONS',
        *guards('S'),
        'PhpStep: S ~> S_next',
        'S_next.COMPLETION = NORMAL',
        'S_next.RESULT = KNOWN PNULL',
        'S_next.TODO = ptask_tail*',
        'S_next.EVENTS = S.EVENTS',
        'S_next.CURRENT = S.CURRENT',
        'S_next.FRAMES = S.FRAMES',
        '$heap_owners($heap_graph(S_next), HCELL n) = 0',
        *guards('S_next'),
        'S_zero = $drive_steps(S, 0)',
        'S_zero = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S, 1)',
        'S_one.COMPLETION = BUDGET',
        'S_one.TODO = S_next.TODO',
        'S_one.RESULT = S_next.RESULT',
        'S_one.CURRENT = S_next.CURRENT',
        'S_one.FRAMES = S_next.FRAMES',
        'S_one.ENV = S_next.ENV',
        'S_one.EVENTS = S_next.EVENTS',
        '$heap_owners($heap_graph(S_one), HCELL n) = 0',
        *guards('S_one'),
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks))
