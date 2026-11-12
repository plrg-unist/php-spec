"""Render one source-derived fixture; the paired runner owns its execution."""
import json

from arrayaccess_reference_exists_review_cases import CASES

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
    previous = 'S_demand'
    for label, mode, key, result in (
            ('isfalse', 'KEY_TEST false', False, 'PNULL'),
            ('istrue', 'KEY_TEST false', True, 'PINT 1'),
            ('emptyfalse', 'KEY_TEST true', False, 'PNULL'),
            ('emptytrue', 'KEY_TEST true', True, None),
            ('coalescefalse', 'KEY_IS', False, 'PNULL'),
            ('coalescetrue', 'KEY_IS', True, None)):
        state, access, cell = 'S_' + label, 'paccess_' + label, 'n_' + label
        value = 'PBOOL ' + str(key).lower()
        checks += [
            f'{state}_paused = $aaexists_review_seek({previous}, 1000, true, ACCESS_READ ({mode}), {str(key).lower()})',
            f'{state} = {state}_paused[.COMPLETION = NORMAL]',
            f'{state}.TODO = (ACCESS_RESULT {access}) :: ptask_{label}*',
            f'{access}.PHASE = ACCESS_CALL $ptascii("offsetExists")',
            f'{access}.MODE = ACCESS_READ ({mode})',
            f'{access}.OFFSET = {value}',
            f'{state}.RESULT = REFERENCE {cell}',
            f'{state}.STORE[{cell}] = DEFINED ({value})',
            f'{cell} <- {state}.REFCELLS',
            f'$call_reference_operand_valid({state}, {state}.RESULT)',
            f'$access_valid({state}, {access})',
            f'~$access_reference_result_pending({state})',
            f'$heap_owners($heap_graph({state}), HCELL {cell}) = 1',
            f'{state}_read = $quiet_operand({state}, {state}.RESULT)',
            f'{state}_read.RESULT = KNOWN ({value})',
            f'{state}_read.STORE = {state}.STORE',
            f'{state}_read.ALLOCATIONS = {state}.ALLOCATIONS',
            *guards(state),
            f'PhpStep: {state} ~> {state}_next',
            f'{state}_next.COMPLETION = NORMAL',
            f'{state}_next.EVENTS = {state}.EVENTS',
            f'{state}_next.CURRENT = {state}.CURRENT',
            f'{state}_next.FRAMES = {state}.FRAMES',
            f'$heap_owners($heap_graph({state}_next), HCELL {cell}) = 0',
        ]
        if result is None:
            checks += [
                f'{state}_next.TODO = (CALL_ARGS pcalltarget_{label} eps 1 ([KNOWN ({value})]) ({access}.SITE) {access}.LINE) :: (ACCESS_RESULT paccess_get_{label}) :: ptask_get_{label}*',
                f'paccess_get_{label}.PHASE = ACCESS_CALL $ptascii("offsetGet")',
                f'paccess_get_{label}.MODE = {access}.MODE',
                f'paccess_get_{label}.OBJECT = {access}.OBJECT',
                f'$access_pending({state}_next, pcalltarget_{label}, {access}.SITE)',
            ]
        else:
            checks += [f'{state}_next.RESULT = KNOWN ({result})',
                       f'{state}_next.TODO = ptask_{label}*']
        checks += guards(state + '_next')
        previous = state + '_next'
    checks += [
        'S_zero = $drive_steps(S_isfalse, 0)',
        'S_zero = S_isfalse[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S_isfalse, 1)',
        'S_one.COMPLETION = BUDGET',
        *guards('S_one'),
        'S_done = $drive(' + previous + ', 1500)',
        'S_resumed = $drive(S_one[.COMPLETION = NORMAL], 1500)',
        'S_done = S_resumed',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        'S_done.CURRENT = eps',
        'S_done.FRAMES = eps',
        '$aaexists_review_outputs(S_done.EVENTS) = $ptascii(' + json.dumps(CASES[0]['expected_stdout']) + ')',
        *guards('S_done'),
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks))
