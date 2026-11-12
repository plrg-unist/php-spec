"""Render two bounded, first-callback source-derived checks."""
import json

PREFIX = r'''
dec $aadiscard_review_stage(pstate, bool, ptbytes) : bool
def $aadiscard_review_stage(S, false, ptbytes) = true
  -- if S.TODO = (RETURN_REF_FETCH z) :: ptask*
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ACCESS_RESULT paccess) :: ptask_saved*
  -- if paccess.PHASE = ACCESS_CALL ptbytes
def $aadiscard_review_stage(S, true, ptbytes) = true
  -- if S.TODO = (ACCESS_RESULT paccess) :: ptask*
  -- if paccess.PHASE = ACCESS_CALL ptbytes
def $aadiscard_review_stage(S, b_result, ptbytes) = false -- otherwise
dec $aadiscard_review_seek(pstate, nat, bool, ptbytes) : pstate
def $aadiscard_review_seek(S, n, b_result, ptbytes) = S
  -- if $aadiscard_review_stage(S, b_result, ptbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $aadiscard_review_seek(S, n, b_result, ptbytes) = $aadiscard_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)), b_result, ptbytes)
  -- if ~$aadiscard_review_stage(S, b_result, ptbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $aadiscard_review_seek(S, n, b_result, ptbytes) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def guards(state):
    return [f'$call_current_valid({state})',
            f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def render(kind, program, filename_b64):
    assert kind in ('set', 'unset')
    member, mode, name, value, owners = (
        ('offsetSet', 'ACCESS_SET', 'value', 77, 1) if kind == 'set'
        else ('offsetUnset', 'ACCESS_UNSET', 'shared', 5, 3))
    method = '$ptascii(' + json.dumps(member) + ')'
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
        f'S_paused = $aadiscard_review_seek(S_initial[.COMPLETION = NORMAL], 1000, false, {method})',
        'S = S_paused[.COMPLETION = NORMAL]',
        'S.TODO = (RETURN_REF_FETCH z) :: ptask_tail*',
        'S.CURRENT = (pcallcontext)',
        'S.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ACCESS_RESULT paccess) :: ptask_saved*',
        f'paccess.PHASE = ACCESS_CALL {method}',
        f'paccess.MODE = {mode}',
        'paccess.OFFSET = PINT 1',
        '$access_frame(S, pcallcontext, pframe)',
        '$reference_call_used(S, paccess.SITE)',
        '$reference_callback_used(S, pcallcontext) = (false)',
        '~$reference_return_used(S)',
        '~$reference_verifies(S)',
        '$target_function(S, $context_target(pcallcontext)) = (pfunction)',
        'pfunction.SIGNATURE.BYREF',
        'pfunction.SIGNATURE.RETURNS = eps',
        '$access_reference_signature(pfunction.SIGNATURE)',
        '~$access_reference_signature(pfunction.SIGNATURE[.RETURNS = ([(PTBRANCH ([PTBUILTIN "int"]))])])',
        'pframe_bad = pframe[.TODO = (ACCESS_RESULT paccess[.LINE = $(paccess.LINE + 1)]) :: ptask_saved*]',
        'S_bad = S[.FRAMES = pframe_bad :: pframe_tail*]',
        '$heap_graph(S_bad) = $heap_graph(S)',
        '~$access_frame(S_bad, pcallcontext, pframe_bad)',
        '$reference_callback_used(S_bad, pcallcontext) = eps',
        '~$call_frames_valid(S_bad, S_bad.FRAMES)',
        f'$lookup(S.ENV, $ptascii("{name}")) = (n_return)',
        f'S.STORE[n_return] = DEFINED (PINT {value})',
        f'$heap_owners($heap_graph(S), HCELL n_return) = {owners}',
        *guards('S'),
    ]
    if kind == 'set':
        checks += ['~(n_return <- S.REFCELLS)']
    else:
        checks += [
            'n_return <- S.REFCELLS',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("shared")) = (n_return)',
            '$lookup(S_global.ENV, $ptascii("alias")) = (n_return)',
        ]
    checks += [
        'PhpStep: S ~> S_unwind',
        'S_unwind.COMPLETION = NORMAL',
        'S_unwind.RESULT = KNOWN PNULL',
        'S_unwind.TODO = (RETURN_REF_UNWIND (KNOWN PNULL) z false porigin_return) :: ptask_unwind*',
        'S.ORIGIN = (porigin_return)',
        'S_unwind.REFCELLS = S.REFCELLS',
        'S_unwind.STORE = S.STORE',
        'S_unwind.ALLOCATIONS = S.ALLOCATIONS',
        'S_unwind.EVENTS = S.EVENTS',
        f'$heap_owners($heap_graph(S_unwind), HCELL n_return) = {owners}',
        'S_zero = $drive_steps(S, 0)',
        'S_zero = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S, 1)',
        'S_one.COMPLETION = BUDGET',
        'S_one.TODO = S_unwind.TODO',
        'S_one.RESULT = S_unwind.RESULT',
        'S_one.CURRENT = S_unwind.CURRENT',
        'S_one.FRAMES = S_unwind.FRAMES',
        'S_one.ENV = S_unwind.ENV',
        'S_one.EVENTS = S_unwind.EVENTS',
        'S_one.REFCELLS = S_unwind.REFCELLS',
        '$call_descriptors_valid(S_one)',
        '$heap_valid($heap_graph(S_one))',
        f'S_return_paused = $aadiscard_review_seek(S_one[.COMPLETION = NORMAL], 1000, true, {method})',
        'S_return = S_return_paused[.COMPLETION = NORMAL]',
        'S_return.TODO = (ACCESS_RESULT paccess_return) :: ptask_return*',
        f'paccess_return.PHASE = ACCESS_CALL {method}',
        f'paccess_return.MODE = {mode}',
        'S_return.RESULT = KNOWN PNULL',
        'S_return.CURRENT = eps',
        'S_return.FRAMES = eps',
        '$access_valid(S_return, paccess_return)',
        *guards('S_return'),
    ]
    if kind == 'set':
        checks += [
            '$heap_owners($heap_graph(S_return), HCELL n_return) = 0',
            '$lookup(S_return.ENV, $ptascii("rhs")) = (n_rhs)',
            'S_return.STORE[n_rhs] = DEFINED (PINT 9)',
            'S_read = $quiet_operand(S_return, paccess_return.SELECTED)',
            'S_read.RESULT = KNOWN (PINT 9)',
        ]
    else:
        checks += [
            '$lookup(S_return.ENV, $ptascii("shared")) = (n_return)',
            '$lookup(S_return.ENV, $ptascii("alias")) = (n_return)',
            'S_return.STORE[n_return] = DEFINED (PINT 5)',
            'n_return <- S_return.REFCELLS',
            '$heap_owners($heap_graph(S_return), HCELL n_return) = 2',
        ]
    checks += [
        'PhpStep: S_return ~> S_done',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = ptask_return*',
        'S_done.RESULT = KNOWN (' + ('PINT 9' if kind == 'set' else 'PNULL') + ')',
        *guards('S_done'),
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks))
