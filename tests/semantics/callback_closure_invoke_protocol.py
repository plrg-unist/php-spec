"""Reached outer/inner tick-wrapper owners and callback return cleanup."""
import base64
import callback_closure_invoke_review_protocol as reviewed

AUTHOR_CASES = (
    'tick-invoke-warning-phases-weak-receive-and-unused-result',
    'tick-invoke-reference-warning-between-outer-and-inner',
    'tick-invoke-outer-throw-before-raw-copy-keeps-cache',
)
CASES = AUTHOR_CASES + reviewed.CASES
DERIVED = {AUTHOR_CASES[0]: 1, **reviewed.DERIVED}
AUTHOR_HELPERS = r'''
dec $ci_test_weak(pstate, ptbytes) : nat?
def $ci_test_weak(S, ptbytes) = (n_object)
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV, ptbytes) = (n_cell)
  -- if S_global.STORE[n_cell] = DEFINED (POBJECT n_weak)
  -- if $object_body(S.OBJECTS[n_weak]) = WEAKREFERENCE (n_object)
def $ci_test_weak(S, ptbytes) = eps -- otherwise
dec $ci_test_notice(pstate, int) : perrorcall?
def $ci_test_notice(S, z) = (perrorcall)
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S, pcallcontext) = (perrorcall)
  -- if perrorcall.LEVEL = z
def $ci_test_notice(S, z) = eps -- otherwise
dec $ci_test_front(pstate, nat) : bool
def $ci_test_front(S, 0) = ($ci_test_notice(S, 8192) =/= eps)
def $ci_test_front(S, 1) = ($ci_test_notice(S, 16384) =/= eps)
def $ci_test_front(S, 2) = ($ci_test_notice(S, 2) =/= eps)
def $ci_test_front(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CALLBACK_INVOKE_TARGET n
  -- if $lookup(S.ENV, $ptascii("value")) = (n_value)
  -- if S.STORE[n_value] = DEFINED (PINT 7)
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV, $ptascii("body")) = (n_body)
  -- if S_global.STORE[n_body] = DEFINED (PINT 0)
def $ci_test_front(S, 4) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("TickInvokeValue")
  -- if $class_method_origin(S.CLASSES, porigin) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__destruct")
def $ci_test_front(S, n) = false -- otherwise
dec $ci_test_seek(pstate, nat, nat) : pstate
def $ci_test_seek(S, n_stage, n) = S -- if $ci_test_front(S, n_stage)
def $ci_test_seek(S, n_stage, 0) = S -- if ~$ci_test_front(S, n_stage)
def $ci_test_seek(S, n_stage, n) = $ci_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$ci_test_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ci_test_seek(S, n_stage, n) = S
  -- if ~$ci_test_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''

HELPERS = AUTHOR_HELPERS + reviewed.HELPERS


def conditions(name, program, source, expected_stdout):
    if name in reviewed.CASES:
        return reviewed.conditions(name, program, source, expected_stdout)
    assert name in AUTHOR_CASES
    normal, reference = name == CASES[0], name == CASES[1]
    path = base64.b64encode(str(source).encode()).decode()
    checks = [f'S_initial = $php_run({program}, 0, "{path}")',
              'S_initial.COMPLETION = BUDGET']

    def reach(label, prior, stage):
        checks.extend([f'{label}_found = $ci_test_seek({prior}, {stage}, 4000)',
                       fr'{label}_found.COMPLETION = NORMAL \/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$ci_test_front({label}, {stage})',
                       f'$call_descriptors_valid({label})',
                       f'$heap_valid($heap_graph({label}))'])

    def owners(state, node, count):
        checks.append(f'$heap_owners($heap_prune($heap_graph({state})), HOBJECT {node}) = {count}')

    reach('S_outer', 'S_initial', 0)
    checks += [
        '$ci_test_notice(S_outer, 8192) = (perrorcall_outer)',
        'perrorcall_outer.RESUME = TICK_SEND ptickdispatch_outer 0',
        'ptickdispatch_outer.SENT = eps',
        'S_outer.TICKENTRIES = [ptickentry]',
        '$ci_test_weak(S_outer, $ptascii("weak_cb")) = (n_closure)',
        'ptickentry.ENTRY.TARGET = CALLBACK_INVOKE_TARGET n_closure',
        '$tick_is_calling(S_outer, ptickentry.ID)',
    ]
    owners('S_outer', 'n_closure', 1)
    if normal:
        checks += ['$drive_steps($drive_steps(S_outer, 1)[.COMPLETION = NORMAL], 1) = $drive_steps(S_outer, 2)']
    if not reference:
        checks += ['$ci_test_weak(S_outer, $ptascii("weak_recv")) = (n_receiver)',
                   '$ci_test_weak(S_outer, $ptascii("weak_arg")) = (n_argument)']
        owners('S_outer', 'n_receiver', 1)
        owners('S_outer', 'n_argument', 1)
    if reference:
        reach('S_reference', 'S_outer', 2)
        checks += [
            '$ci_test_notice(S_reference, 2) = (perrorcall_reference)',
            'perrorcall_reference.RESUME = TICK_REFERENCE ptickdispatch_reference 0',
            'ptickdispatch_reference.SENT = eps',
            'S_reference.TICKENTRIES = [ptickentry]',
            'ptickentry.ENTRY.ARGS = [PINT 7]',
            'S_global = $global_table_view(S_reference)',
            '$lookup(S_global.ENV, $ptascii("input")) = (n_input)',
            '$lookup(S_global.ENV, $ptascii("alias")) = (n_input)',
            'S_reference.STORE[n_input] = DEFINED (PINT 7)',
        ]
        owners('S_reference', 'n_closure', 1)
        prior = 'S_reference'
    else:
        prior = 'S_outer'
    if normal or reference:
        reach('S_inner', prior, 1)
        checks += [
            '$ci_test_notice(S_inner, 16384) = (perrorcall_inner)',
            'perrorcall_inner.RESUME = TICK_INVOKE_ENTER ptickdispatch_inner',
            'S_inner.TICKENTRIES = [ptickentry]',
            '$tick_is_calling(S_inner, ptickentry.ID)',
        ]
        owners('S_inner', 'n_closure', 1)
        if normal:
            checks += ['ptickdispatch_inner.SENT = [KNOWN pvalue_raw, KNOWN (POBJECT n_argument)]',
                       '$string_bytes(pvalue_raw) = ($ptascii("7"))']
            owners('S_inner', 'n_receiver', 1)
            owners('S_inner', 'n_argument', 2)
        else:
            checks += [
                'ptickdispatch_inner.SENT = [REFERENCE n_private]',
                'n_private =/= n_input', 'S_inner.STORE[n_private] = DEFINED (PINT 7)',
                '$heap_owners($heap_prune($heap_graph(S_inner)), HCELL n_private) = 1',
            ]
        reach('S_body', 'S_inner', 3)
        checks += ['S_body.CURRENT = (pcallcontext_body)',
                   'pcallcontext_body.TARGET = CALLBACK_INVOKE_TARGET n_closure',
                   'pcallcontext_body.INSTANCE = (n_closure)',
                   '$tick_context_valid(S_body, pcallcontext_body)']
        owners('S_body', 'n_closure', 2)
        if normal:
            owners('S_body', 'n_receiver', 1)
            owners('S_body', 'n_argument', 3)
            checks += [
                # Derived missing genuine tick caller; never another reached state.
                '~$call_context_valid(S_body[.FRAMES = eps], pcallcontext_body, S_body.CVS)',
                'pcallcontext_body.WRAPPER = ({SLOTS ([NAMED_SENT (KNOWN pvalue_raw), NAMED_SENT (KNOWN (POBJECT n_argument))]), NAMED eps})',
            ]
            reach('S_value', 'S_body', 4)
            owners('S_value', 'n_closure', 1)
            owners('S_value', 'n_receiver', 1)
            owners('S_value', 'n_argument', 1)
            checks += ['S_value.CURRENT = (pcallcontext_value)',
                       'pcallcontext_value.TARGET = METHOD_TARGET n_value porigin_value',
                       'S_value.TICKENTRIES = [ptickentry]']
            last, retired = 'S_value', ('n_closure', 'n_receiver', 'n_argument', 'n_value')
        else:
            checks += [
                '$lookup(S_body.ENV, $ptascii("value")) = (n_private)',
                'pcallcontext_body.WRAPPER = ({SLOTS ([NAMED_SENT (REFERENCE n_private)]), NAMED eps})',
                '$heap_owners($heap_prune($heap_graph(S_body)), HCELL n_private) = 2',
            ]
            last, retired = 'S_body', ('n_closure',)
    else:
        checks += [
            'S_catch_found = $cc_review_seek(S_outer, 0, 80, 4000)',
            r'S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET',
            'S_catch = S_catch_found[.COMPLETION = NORMAL]',
            '$cc_review_front(S_catch, 0, 80)',
            '$call_descriptors_valid(S_catch)', '$heap_valid($heap_graph(S_catch))',
            'S_catch.TICKENTRIES = [ptickentry]', '~$tick_running(S_catch)',
            '$cc_review_output(S_catch.EVENTS) = $ptascii("O:1:1:1:1:1;C:1:1:1:")',
        ]
        owners('S_catch', 'n_closure', 1)
        owners('S_catch', 'n_receiver', 1)
        owners('S_catch', 'n_argument', 1)
        last, retired = 'S_catch', ('n_closure', 'n_receiver', 'n_argument')
    stream = ', '.join(str(byte) for byte in expected_stdout)
    checks += [f'S_final = $drive_steps({last}, 4000)', 'S_final.COMPLETION = NORMAL',
               f'$cc_review_output(S_final.EVENTS) = [{stream}]',
               '$call_descriptors_valid(S_final)', '$heap_valid($heap_graph(S_final))',
               'S_final.TICKENTRIES = eps', 'S_final.FRAMES = eps',
               'S_final.DESTRUCTION.CALLS = eps', 'S_final.DESTRUCTION.FRAMES = eps',
               'S_final.DESTRUCTION.RELEASES = eps', 'S_final.DESTRUCTION.OPERATIONS = eps']
    for node in retired:
        checks.append(f'~((HOBJECT {node}) <- S_final.ALLOCATIONS)')
    if reference:
        checks += ['S_final.STORE[n_input] = DEFINED (PINT 7)',
                   '~((HCELL n_private) <- S_final.ALLOCATIONS)']
    return checks
