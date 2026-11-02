"""Independent reached selection and receiver owners for attributed Closures."""
import base64


CASES = (
    'scoped-rebound-closure-vm-flags-retain-selected-receiver',
    'scoped-rebound-closure-wrapper-flags-retain-selected-receiver',
)
HELPERS = r'''
dec $ce_review_front(pstate, nat) : bool
def $ce_review_front(S, 0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = NODISCARD_RESUME pframe
  -- if perrorcall.LEVEL = 16384
def $ce_review_front(S, 1) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = NODISCARD_RESUME pframe
  -- if perrorcall.LEVEL = 512
def $ce_review_front(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CLOSURE_INVOKE_INNER ptask
  -- if perrorcall.LEVEL = 8192
def $ce_review_front(S, 3) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = CLOSURE_INVOKE_ENTER ptask
  -- if perrorcall.LEVEL = 16384
def $ce_review_front(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n
  -- if $lookup(S.ENV, $ptascii("snapshot")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (PINT 7)
def $ce_review_front(S, 5) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("Rebound")
  -- if $class_method_origin(S.CLASSES, porigin) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__destruct")
def $ce_review_front(S, n) = false -- otherwise
dec $ce_review_seek(pstate, nat, nat) : pstate
def $ce_review_seek(S, n_stage, n) = S -- if $ce_review_front(S, n_stage)
def $ce_review_seek(S, n_stage, 0) = S -- if ~$ce_review_front(S, n_stage)
def $ce_review_seek(S, n_stage, n) = $ce_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$ce_review_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ce_review_seek(S, n_stage, n) = S
  -- if ~$ce_review_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $ce_review_output(pevent*) : ptbytes
dec $ce_review_is_output(pevent) : bool
def $ce_review_output(eps) = eps
def $ce_review_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $ce_review_output(pevent_tail*)
def $ce_review_output(pevent :: pevent_tail*) = $ce_review_output(pevent_tail*) -- if ~$ce_review_is_output(pevent)
def $ce_review_is_output(OUTPUT ptbytes) = true
def $ce_review_is_output(pevent) = false -- otherwise
'''


def conditions(name, program, source, expected_stdout):
    assert name in CASES
    wrapper = name == CASES[1]
    encoded_path = base64.b64encode(str(source).encode()).decode()
    checks = [f'S_initial = $php_run({program}, 0, "{encoded_path}")',
              'S_initial.COMPLETION = BUDGET']

    def reach(label, prior, stage):
        checks.extend([f'{label}_found = $ce_review_seek({prior}, {stage}, 4000)',
                       fr'{label}_found.COMPLETION = NORMAL \/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$ce_review_front({label}, {stage})',
                       f'$call_descriptors_valid({label})',
                       f'$heap_valid($heap_graph({label}))'])

    reach('S_first', 'S_initial', 2 if wrapper else 0)
    checks += ['S_first.TODO = (ERROR_HANDLER_INVOKE perrorcall_first) :: ptask_tail*',
               'S_first.CURRENT = eps', 'S_first.FRAMES = eps',
               '$ce_review_output(S_first.EVENTS) = eps',
               '$error_call_valid(S_first, perrorcall_first)']
    if wrapper:
        checks += [
            'perrorcall_first.RESUME = CLOSURE_INVOKE_INNER ptask_source',
            '$closure_invoke_source(ptask_source) = ((CLOSURE_TARGET n_closure, pnamedargs, porigin_call, z_call))',
            'pnamedargs.SLOTS = eps', 'pnamedargs.NAMED = eps',
            '$closure_invoke_valid(S_first, ptask_source)',
        ]
    else:
        checks += [
            'perrorcall_first.RESUME = NODISCARD_RESUME pframe_first',
            'pframe_first.CONTEXT = (pcallcontext_first)',
            'pcallcontext_first.TARGET = CLOSURE_TARGET n_closure',
            'pcallcontext_first.INSTANCE = (n_closure)',
            'pcallcontext_first.WRAPPER = eps',
            '$nodiscard_frame_valid(S_first, pframe_first)',
        ]
    checks += [
        '$object_body(S_first.OBJECTS[n_closure]) = REALCLOSURE porigin_function ([DIRECT (PINT 7)]) eps',
        '$target_function(S_first, CLOSURE_TARGET n_closure) = (pfunction)',
        'pfunction.NAME = $ptascii("{closure:Origin::make():7}")',
        'pfunction.LINE = 7',
        '$target_receiver(S_first, CLOSURE_TARGET n_closure) = (n_receiver)',
        '$object_name(S_first, n_receiver) = $ptascii("Rebound")',
        '$target_lexical_class(S_first, CLOSURE_TARGET n_closure) = (porigin_scope)',
        '$target_called_class(S_first, CLOSURE_TARGET n_closure) = (porigin_scope)',
        '$class_at(S_first.CLASSES, porigin_scope) = (pclassdesc_scope)',
        'pclassdesc_scope.NAME = $ptascii("Rebound")',
        '$heap_owners($heap_prune($heap_graph(S_first)), HOBJECT n_closure) = 2',
        '$heap_owners($heap_prune($heap_graph(S_first)), HOBJECT n_receiver) = 1',
    ]
    reach('S_second', 'S_first', 3 if wrapper else 1)
    checks += [
        'S_second.TODO = (ERROR_HANDLER_INVOKE perrorcall_second) :: ptask_second_tail*',
        'S_second.CURRENT = eps', 'S_second.FRAMES = eps',
        '$error_call_valid(S_second, perrorcall_second)',
        '$heap_owners($heap_prune($heap_graph(S_second)), HOBJECT n_closure) = 1',
        '$heap_owners($heap_prune($heap_graph(S_second)), HOBJECT n_receiver) = 1',
        '$object_body(S_second.OBJECTS[n_closure]) = REALCLOSURE porigin_function ([DIRECT (PINT 7)]) eps',
        '$lookup(S_second.ENV, $ptascii("closure")) = (n_outside)',
        'S_second.STORE[n_outside] = DEFINED (POBJECT n_replacement)',
        'n_replacement =/= n_closure',
        '$lookup(S_second.ENV, $ptascii("input")) = (n_input)',
        'S_second.STORE[n_input] = DEFINED (PINT 8)',
    ]
    if wrapper:
        checks += [
            'perrorcall_second.RESUME = CLOSURE_INVOKE_ENTER ptask_source',
            '$closure_invoke_valid(S_second, ptask_source)',
            '$ce_review_output(S_second.EVENTS) = $ptascii("W:1:1:1:1:1;")',
        ]
    else:
        checks += [
            'perrorcall_second.RESUME = NODISCARD_RESUME pframe_second',
            'pframe_second.CONTEXT = pframe_first.CONTEXT',
            '$nodiscard_frame_valid(S_second, pframe_second)',
            '$ce_review_output(S_second.EVENTS) = $ptascii("D:1:1:1:1:1;")',
        ]
    reach('S_body', 'S_second', 4)
    checks += [
        'S_body.CURRENT = (pcallcontext_body)',
        'pcallcontext_body.TARGET = CLOSURE_TARGET n_closure',
        'pcallcontext_body.INSTANCE = (n_closure)',
        'pcallcontext_body.RECEIVER = (n_receiver)',
        'pcallcontext_body.LEXICAL_CLASS = (porigin_scope)',
        'pcallcontext_body.CALLED_CLASS = (porigin_scope)',
        '$lookup(S_body.ENV, $ptascii("snapshot")) = (n_snapshot)',
        'S_body.STORE[n_snapshot] = DEFINED (PINT 7)',
        '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_closure) = ' + ('2' if wrapper else '1'),
        '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_receiver) = 1',
        'pcallcontext_body.WRAPPER = ' + ('(pnamedargs)' if wrapper else 'eps'),
        '$ce_review_output(S_body.EVENTS) = $ptascii("' + ('W:1:1:1:1:1;U:1:1:1:1;' if wrapper else 'D:1:1:1:1:1;N:1:1:1:1;') + '")',
    ]
    reach('S_receiver', 'S_body', 5)
    checks += [
        'S_receiver.CURRENT = (pcallcontext_receiver)',
        'pcallcontext_receiver.TARGET = METHOD_TARGET n_receiver porigin_destructor',
        '~((HOBJECT n_closure) <- S_receiver.ALLOCATIONS)',
        '$ce_review_output(S_receiver.EVENTS) = $ptascii("' + ('W:1:1:1:1:1;U:1:1:1:1;' if wrapper else 'D:1:1:1:1:1;N:1:1:1:1;') + 'B:1:1:1:1;")',
        'S_done = $drive_steps(S_receiver, 4000)',
        'S_done.COMPLETION = NORMAL',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.DESTRUCTION.FRAMES = eps', 'S_done.DESTRUCTION.RELEASES = eps',
        'S_done.DESTRUCTION.CALLS = eps',
        '~((HOBJECT n_closure) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$ce_review_output(S_done.EVENTS) = [' + ','.join(map(str, expected_stdout)) + ']',
    ]
    return checks
