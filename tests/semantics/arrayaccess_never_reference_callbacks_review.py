"""A genuine never callback EOF throws before any reference return or Notice."""
import json

PREFIX = r'''
dec $aanever_review_stage(pstate) : bool
def $aanever_review_stage(S) = true
  -- if S.TODO = (TYPE_FALLTHROUGH porigin) :: ptask*
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ACCESS_RESULT paccess) :: ptask_saved*
  -- if paccess.PHASE = ACCESS_CALL $ptascii("offsetExists")
def $aanever_review_stage(S) = false -- otherwise
dec $aanever_review_seek(pstate, nat) : pstate
def $aanever_review_seek(S, n) = S
  -- if $aanever_review_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $aanever_review_seek(S, n) = $aanever_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$aanever_review_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $aanever_review_seek(S, n) = S
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
        'S_paused = $aanever_review_seek(S_initial[.COMPLETION = NORMAL], 1000)',
        r'S_paused.COMPLETION = NORMAL \/ S_paused.COMPLETION = BUDGET',
        'S = S_paused[.COMPLETION = NORMAL]',
        'S.TODO = (TYPE_FALLTHROUGH porigin) :: ptask_tail*',
        'S.CURRENT = (pcallcontext)',
        'S.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ACCESS_RESULT paccess) :: ptask_saved*',
        'paccess.PHASE = ACCESS_CALL $ptascii("offsetExists")',
        'paccess.MODE = ACCESS_READ (KEY_TEST false)',
        'paccess.OFFSET = PINT 1',
        '$target_function(S, $context_target(pcallcontext)) = (pfunction)',
        'pfunction.SIGNATURE.BYREF',
        'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "never"]))]',
        'porigin = pfunction.ORIGIN',
        'S.ORIGIN = (pfunction.ORIGIN)',
        '$typed_fallthrough_valid(S, porigin)',
        '~$call_task_valid(S, TYPE_FALLTHROUGH paccess.SITE)',
        '~$access_reference_signature(pfunction.SIGNATURE)',
        '~$access_reference_scalar_types(pfunction.SIGNATURE.RETURNS)',
    ]
    for member in ('offsetGet', 'offsetExists', 'offsetSet', 'offsetUnset'):
        checks.append(f'$access_reference_call_signature(pfunction.SIGNATURE, $ptascii("{member}"))')
    checks += [
        '$access_frame(S, pcallcontext, pframe)',
        '$reference_callback_used(S, pcallcontext) = (true)',
        '$reference_return_used(S)',
        '$call_function_kind(S) = $ptascii("method")',
        '$call_function_name(S, pfunction) = $ptascii("NeverReferenceCallbacks::offsetExists")',
        'S.EVENTS = [OUTPUT ($ptascii("E;"))]',
        '$reference_notice_count(S.TODO) = 0',
        *guards('S'),
        'n_message* = $ptascii("NeverReferenceCallbacks::offsetExists(): never-returning method must not implicitly return")',
        'PhpStep: S ~> S_raw',
        'S_raw.COMPLETION = THROWN "TypeError" n_message* pfunction.ENDLINE',
        'S_raw.TODO = S.TODO',
        'S_raw.STORE = S.STORE',
        'S_raw.ALLOCATIONS = S.ALLOCATIONS',
        'S_raw.REFCELLS = S.REFCELLS',
        'S_raw.EVENTS = S.EVENTS',
        'S_zero = $drive_steps(S, 0)',
        'S_zero = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S, 1)',
        'S_one.COMPLETION = BUDGET',
        'S_one.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'n_error = |S.OBJECTS|',
        'S_one.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "TypeError"',
        '$throwable_field(S_one, n_error, "line") = PINT pfunction.ENDLINE',
        '$string_bytes($throwable_field(S_one, n_error, "message")) = (n_message*)',
        'S_one.RESULT = KNOWN PNULL',
        'S_one.CURRENT = S.CURRENT',
        'S_one.FRAMES = S.FRAMES',
        'S_one.STORE = S.STORE',
        'S_one.REFCELLS = S.REFCELLS',
        'S_one.EVENTS = S.EVENTS',
        '$reference_notice_count(S_one.TODO) = 0',
        *guards('S_one'),
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks))
