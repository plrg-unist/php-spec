"""Check the existing CV verifier at one typed ArrayAccess reference return."""
import json

PREFIX = r'''
dec $aatyped_review_stage(pstate) : bool
def $aatyped_review_stage(S) = true
  -- if S.TODO = (RETURN_REF_FETCH z) :: ptask*
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ACCESS_RESULT paccess) :: ptask_saved*
  -- if paccess.PHASE = ACCESS_CALL $ptascii("offsetGet")
def $aatyped_review_stage(S) = false -- otherwise
dec $aatyped_review_seek(pstate, nat) : pstate
def $aatyped_review_seek(S, n) = S
  -- if $aatyped_review_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $aatyped_review_seek(S, n) = $aatyped_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$aatyped_review_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $aatyped_review_seek(S, n) = S
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
        'S_paused = $aatyped_review_seek(S_initial[.COMPLETION = NORMAL], 1000)',
        'S = S_paused[.COMPLETION = NORMAL]',
        'S.TODO = (RETURN_REF_FETCH z) :: ptask_tail*',
        'S.CURRENT = (pcallcontext)',
        'S.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ACCESS_RESULT paccess) :: ptask_saved*',
        'paccess.PHASE = ACCESS_CALL $ptascii("offsetGet")',
        'paccess.MODE = ACCESS_READ KEY_R',
        'paccess.OFFSET = PINT 17',
        '$target_function(S, $context_target(pcallcontext)) = (pfunction)',
        'pfunction.SIGNATURE.BYREF',
        'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))]',
        '~pfunction.CODE.STRICT',
        '$reference_verifies(S)',
        '~$access_reference_signature(pfunction.SIGNATURE)',
        '$access_reference_call_signature(pfunction.SIGNATURE, $ptascii("offsetGet"))',
        '$access_reference_call_signature(pfunction.SIGNATURE, $ptascii("offsetExists"))',
        '$access_reference_call_signature(pfunction.SIGNATURE, $ptascii("offsetSet"))',
        '$access_reference_call_signature(pfunction.SIGNATURE, $ptascii("offsetUnset"))',
        'pssignature_string = pfunction.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "string"]))]]',
        '~$access_reference_call_signature(pssignature_string, $ptascii("offsetGet"))',
        'pssignature_eps = pfunction.SIGNATURE[.RETURNS = eps]',
        'pssignature_mixed = pfunction.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "mixed"]))]]',
    ]
    for member in ('offsetGet', 'offsetExists', 'offsetSet', 'offsetUnset'):
        for signature in ('eps', 'mixed'):
            checks.append(f'$access_reference_call_signature(pssignature_{signature}, $ptascii("{member}"))')
    checks += [
        '$access_frame(S, pcallcontext, pframe)',
        '$access_reference_get(S, paccess)',
        '$reference_callback_used(S, pcallcontext) = (true)',
        '$reference_return_used(S)',
        '$reference_return_fetch_valid(S, z)',
        '~$call_task_valid(S, RETURN_REF_FETCH $(z + 1))',
        'pframe_bad = pframe[.TODO = (ACCESS_RESULT paccess[.LINE = $(paccess.LINE + 1)]) :: ptask_saved*]',
        'S_bad = S[.FRAMES = pframe_bad :: pframe_tail*]',
        '$heap_graph(S_bad) = $heap_graph(S)',
        '~$access_frame(S_bad, pcallcontext, pframe_bad)',
        '$reference_callback_used(S_bad, pcallcontext) = eps',
        '~$call_frames_valid(S_bad, S_bad.FRAMES)',
        'S.BASE = BASE_VALUE (VARIABLE ($ptascii("value")) z_name)',
        '$lookup(S.ENV, $ptascii("value")) = (n_value)',
        'S.STORE[n_value] = DEFINED (PINT 17)',
        '~(n_value <- S.REFCELLS)',
        '$heap_owners($heap_graph(S), HCELL n_value) = 1',
        '~$typed_reference_name_source(S, $ptascii("value"))',
        'S_read = $read_name(S, $ptascii("value"), z)',
        'S_read.RESULT = KNOWN (PINT 17)',
        'S_checked = $typed_return_checked(S_read, z, false)',
        'S_checked = S_read',
        *guards('S'),
        'PhpStep: S ~> S_unwind',
        'S_unwind.COMPLETION = NORMAL',
        'S_unwind.TODO = (RETURN_REF_UNWIND (REFERENCE n_value) z false porigin_return) :: ptask_unwind*',
        'S.ORIGIN = (porigin_return)',
        'S_unwind.RESULT = KNOWN PNULL',
        'S_unwind.REFCELLS = n_value :: S.REFCELLS',
        'S_unwind.STORE = S.STORE',
        'S_unwind.ALLOCATIONS = S.ALLOCATIONS',
        'S_unwind.PROPREFS = S.PROPREFS',
        'S_unwind.EVENTS = S.EVENTS',
        '$heap_owners($heap_graph(S_unwind), HCELL n_value) = 2',
        '~$typed_reference_name_source(S_unwind, $ptascii("value"))',
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
        'S_one.PROPREFS = S_unwind.PROPREFS',
        'S_one.EVENTS = S_unwind.EVENTS',
        '$call_descriptors_valid(S_one)',
        '$heap_valid($heap_graph(S_one))',
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks))
