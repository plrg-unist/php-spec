"""Independent reached ownership fronts for an unused aliased wrapper result."""
import base64


CASES = ('invoke-unused-aliased-result-outlives-later-raw-argument',)
HELPERS = r'''
dec $cr_review_front(pstate, nat) : bool
def $cr_review_front(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("AliasMarker")
def $cr_review_front(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("AliasToken")
def $cr_review_front(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("AliasCarrier")
  -- if $class_method_origin(S.CLASSES, porigin) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__destruct")
def $cr_review_front(S, n) = false -- otherwise
dec $cr_review_seek(pstate, nat, nat) : pstate
def $cr_review_seek(S, n_stage, n) = S -- if $cr_review_front(S, n_stage)
def $cr_review_seek(S, n_stage, 0) = S -- if ~$cr_review_front(S, n_stage)
def $cr_review_seek(S, n_stage, n) = $cr_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$cr_review_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $cr_review_seek(S, n_stage, n) = S
  -- if ~$cr_review_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $cr_review_output(pevent*) : ptbytes
dec $cr_review_is_output(pevent) : bool
def $cr_review_output(eps) = eps
def $cr_review_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $cr_review_output(pevent_tail*)
def $cr_review_output(pevent :: pevent_tail*) = $cr_review_output(pevent_tail*) -- if ~$cr_review_is_output(pevent)
def $cr_review_is_output(OUTPUT ptbytes) = true
def $cr_review_is_output(pevent) = false -- otherwise
'''


def conditions(name, program, source, expected_stdout):
    assert name in CASES
    encoded_path = base64.b64encode(str(source).encode()).decode()
    checks = [f'S_initial = $php_run({program}, 0, "{encoded_path}")',
              'S_initial.COMPLETION = BUDGET']

    def reach(label, prior, stage):
        checks.extend([f'{label}_found = $cr_review_seek({prior}, {stage}, 4000)',
                       fr'{label}_found.COMPLETION = NORMAL \/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$cr_review_front({label}, {stage})',
                       f'$call_descriptors_valid({label})',
                       f'$heap_valid($heap_graph({label}))'])

    reach('S_marker', 'S_initial', 0)
    checks += [
        'S_marker.CURRENT = (pcallcontext_marker)',
        'pcallcontext_marker.TARGET = METHOD_TARGET n_marker porigin_marker',
        'S_marker.DESTRUCTION.RELEASES = [pdestructionrelease_marker]',
        'pdestructionrelease_marker.JOBS = [DESTRUCTION_VALUE (HOBJECT n_token), DESTRUCTION_VALUE (HOBJECT n_closure)]',
        '$object_name(S_marker, n_token) = $ptascii("AliasToken")',
        '$target_receiver(S_marker, CLOSURE_TARGET n_closure) = (n_receiver)',
        '$object_name(S_marker, n_receiver) = $ptascii("AliasCarrier")',
        'S_marker.DESTRUCTION.FRAMES = [pdestructionframe_return]',
        'pdestructionframe_return.VALUE = KNOWN PNULL',
        'pdestructionframe_return.PENDING = eps',
        '$heap_owners($heap_prune($heap_graph(S_marker)), HOBJECT n_token) = 1',
        '$heap_owners($heap_prune($heap_graph(S_marker)), HOBJECT n_closure) = 1',
        '$heap_owners($heap_prune($heap_graph(S_marker)), HOBJECT n_receiver) = 1',
    ]
    reach('S_token', 'S_marker', 1)
    checks += [
        'S_token.CURRENT = (pcallcontext_token)',
        'pcallcontext_token.TARGET = METHOD_TARGET n_token porigin_token',
        '~((HOBJECT n_marker) <- S_token.ALLOCATIONS)',
        'S_token.DESTRUCTION.RELEASES = [pdestructionrelease_token]',
        'pdestructionrelease_token.JOBS = [DESTRUCTION_VALUE (HOBJECT n_closure)]',
        'S_token.DESTRUCTION.FRAMES = [pdestructionframe_return]',
        '$heap_owners($heap_prune($heap_graph(S_token)), HOBJECT n_closure) = 1',
        '$heap_owners($heap_prune($heap_graph(S_token)), HOBJECT n_receiver) = 1',
    ]
    reach('S_receiver', 'S_token', 2)
    checks += [
        'S_receiver.CURRENT = (pcallcontext_receiver)',
        'pcallcontext_receiver.TARGET = METHOD_TARGET n_receiver porigin_receiver',
        '~((HOBJECT n_marker) <- S_receiver.ALLOCATIONS)',
        '~((HOBJECT n_token) <- S_receiver.ALLOCATIONS)',
        '~((HOBJECT n_closure) <- S_receiver.ALLOCATIONS)',
        'S_receiver.DESTRUCTION.FRAMES = [pdestructionframe_return]',
        'S_done = $drive_steps(S_receiver, 4000)',
        'S_done.COMPLETION = NORMAL',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.DESTRUCTION.FRAMES = eps',
        'S_done.DESTRUCTION.RELEASES = eps',
        'S_done.DESTRUCTION.CALLS = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$cr_review_output(S_done.EVENTS) = [' + ','.join(map(str, expected_stdout)) + ']',
    ]
    return checks
