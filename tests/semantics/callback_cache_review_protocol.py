"""Independent reached FCC spelling, cached owners and tick-call borrowing."""
import base64


CASES = (
    'tick-raw-object-cache-distinct-from-invoke-array',
    'tick-scoped-method-closure-cache-arguments-before-owner',
)
DERIVED = {CASES[0]: 2, CASES[1]: 2}
HELPERS = r'''
dec $cc_review_front(pstate, nat, int) : bool
def $cc_review_front(S, 0, z_line) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET /\ pconfigcall.LINE = z_line
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $cc_review_front(S, 1, z_line) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.RECEIVER = (n)
  -- if $object_name(S, n) = $ptascii("CacheInvoker")
  -- if $tick_context_kind(S, pcallcontext)
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV, $ptascii("phase")) = (n_phase)
  -- if S_global.STORE[n_phase] = DEFINED (PINT 2)
  -- if $lookup(S_global.ENV, $ptascii("calls")) = (n_calls)
  -- if S_global.STORE[n_calls] = DEFINED (PINT 2)
def $cc_review_front(S, 2, z_line) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_TARGET n_closure
  -- if pcallcontext.RECEIVER = (n)
  -- if $object_name(S, n) = $ptascii("CacheOwner")
  -- if $tick_context_kind(S, pcallcontext)
  -- if $lookup(S.ENV, $ptascii("argument")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n_argument)
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV, $ptascii("calls")) = (n_calls)
  -- if S_global.STORE[n_calls] = DEFINED (PINT 0)
def $cc_review_front(S, 3, z_line) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("CacheToken")
  -- if $class_method_origin(S.CLASSES, porigin) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__destruct")
def $cc_review_front(S, 4, z_line) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("CacheOwner")
  -- if $class_method_origin(S.CLASSES, porigin) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__destruct")
def $cc_review_front(S, 5, z_line) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("CacheInvoker")
  -- if $class_method_origin(S.CLASSES, porigin) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__destruct")
def $cc_review_front(S, n, z_line) = false -- otherwise
dec $cc_review_seek(pstate, nat, int, nat) : pstate
def $cc_review_seek(S, n_stage, z_line, n) = S -- if $cc_review_front(S, n_stage, z_line)
def $cc_review_seek(S, n_stage, z_line, 0) = S -- if ~$cc_review_front(S, n_stage, z_line)
def $cc_review_seek(S, n_stage, z_line, n) = $cc_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, z_line, $nabs($(n - 1)))
  -- if ~$cc_review_front(S, n_stage, z_line) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $cc_review_seek(S, n_stage, z_line, n) = S
  -- if ~$cc_review_front(S, n_stage, z_line) /\ $(n > 0)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $cc_review_output(pevent*) : ptbytes
dec $cc_review_is_output(pevent) : bool
def $cc_review_output(eps) = eps
def $cc_review_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $cc_review_output(pevent_tail*)
def $cc_review_output(pevent :: pevent_tail*) = $cc_review_output(pevent_tail*) -- if ~$cc_review_is_output(pevent)
def $cc_review_is_output(OUTPUT ptbytes) = true
def $cc_review_is_output(pevent) = false -- otherwise
'''


def conditions(name, program, source, expected_stdout):
    assert name in CASES
    raw = name == CASES[0]
    encoded_path = base64.b64encode(str(source).encode()).decode()
    lines = source.read_bytes().splitlines()

    def source_line(marker):
        matches = [i for i, line in enumerate(lines, 1) if marker in line]
        assert len(matches) == 1
        return matches[0]

    checks = [f'S_initial = $php_run({program}, 0, "{encoded_path}")',
              'S_initial.COMPLETION = BUDGET']

    def reach(label, prior, stage, line=0):
        checks.extend([f'{label}_found = $cc_review_seek({prior}, {stage}, {line}, 4000)',
                       fr'{label}_found.COMPLETION = NORMAL \/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$cc_review_front({label}, {stage}, {line})',
                       f'$call_descriptors_valid({label})',
                       f'$heap_valid($heap_graph({label}))'])

    reach('S_registered', 'S_initial', 0, source_line(b'echo "P:"'))
    if raw:
        checks += [
            'S_registered.TICKENTRIES = [ptickentry_raw, ptickentry_array]',
            'ptickentry_raw.ID = 0', 'ptickentry_array.ID = 1',
            'ptickentry_raw.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (POBJECT n_object))]',
            'ptickentry_array.ENTRY.CALL.SENT = [NAMED_SENT (KNOWN (PARRAY n_array))]',
            'ptickentry_raw.ENTRY.CACHEOBJECT = (n_object)',
            'ptickentry_array.ENTRY.CACHEOBJECT = (n_object)',
            'ptickentry_raw.ENTRY.ARGS = eps', 'ptickentry_array.ENTRY.ARGS = eps',
            '~$tick_same(S_registered, ptickentry_raw.ENTRY, ptickentry_array.ENTRY)',
            '$heap_owners($heap_prune($heap_graph(S_registered)), HOBJECT n_object) = 3',
            # Derived metadata forgery; not another reached source.
            '~$tick_entry_valid(S_registered, ptickentry_raw[.ENTRY.CACHEOBJECT = eps])',
        ]
        reach('S_removed_arrays', 'S_registered', 0, source_line(b'echo "U:"'))
        checks += [
            'S_removed_arrays.TICKENTRIES = [ptickentry_raw]',
            '$heap_owners($heap_prune($heap_graph(S_removed_arrays)), HOBJECT n_object) = 2',
            '$cc_review_output(S_removed_arrays.EVENTS) = $ptascii("P:1;C:1;C:1;A:1;U:")',
        ]
        reach('S_body', 'S_removed_arrays', 1)
        checks += [
            'S_body.CURRENT = (pcallcontext_body)',
            'pcallcontext_body.RECEIVER = (n_object)',
            'pcallcontext_body.INSTANCE = eps',
            '$tick_context_valid(S_body, pcallcontext_body)',
            # Derived forged borrowed context without its real tick caller.
            '~$call_context_valid(S_body[.FRAMES = eps], pcallcontext_body, S_body.CVS)',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_object) = 2',
            '$cc_review_output(S_body.EVENTS) = $ptascii("P:1;C:1;C:1;A:1;U:1:1;")',
        ]
        reach('S_receiver', 'S_body', 5)
        checks += [
            'S_receiver.CURRENT = (pcallcontext_receiver)',
            'pcallcontext_receiver.TARGET = METHOD_TARGET n_object porigin_destructor',
            'S_receiver.TICKENTRIES = eps',
            '$cc_review_output(S_receiver.EVENTS) = $ptascii("P:1;C:1;C:1;A:1;U:1:1;C:1;B:1;")',
        ]
        retired = ('n_object',)
    else:
        checks += [
            'S_registered.TICKENTRIES = [ptickentry]',
            'ptickentry.ENTRY.TARGET = CLOSURE_TARGET n_closure',
            'ptickentry.ENTRY.CACHEOBJECT = (n_receiver)',
            'ptickentry.ENTRY.ARGS = [POBJECT n_argument]',
            '$target_receiver(S_registered, CLOSURE_TARGET n_closure) = (n_receiver)',
            '$object_name(S_registered, n_receiver) = $ptascii("CacheOwner")',
            '$object_name(S_registered, n_argument) = $ptascii("CacheToken")',
            '$heap_owners($heap_prune($heap_graph(S_registered)), HOBJECT n_closure) = 1',
            '$heap_owners($heap_prune($heap_graph(S_registered)), HOBJECT n_receiver) = 2',
            '$heap_owners($heap_prune($heap_graph(S_registered)), HOBJECT n_argument) = 1',
            # Derived metadata forgery; not another reached source.
            '~$tick_entry_valid(S_registered, ptickentry[.ENTRY.CACHEOBJECT = (n_argument)])',
        ]
        reach('S_body', 'S_registered', 2)
        checks += [
            'S_body.CURRENT = (pcallcontext_body)',
            'pcallcontext_body.TARGET = CLOSURE_TARGET n_closure',
            'pcallcontext_body.INSTANCE = (n_closure)',
            'pcallcontext_body.RECEIVER = (n_receiver)',
            '$tick_context_valid(S_body, pcallcontext_body)',
            '$lookup(S_body.ENV, $ptascii("argument")) = (n_argument_cell)',
            'S_body.STORE[n_argument_cell] = DEFINED (POBJECT n_argument)',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_closure) = 2',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_receiver) = 2',
            '$heap_owners($heap_prune($heap_graph(S_body)), HOBJECT n_argument) = 2',
            '$cc_review_output(S_body.EVENTS) = $ptascii("P:1:1:1;")',
        ]
        reach('S_argument', 'S_body', 3)
        checks += [
            'S_argument.TICKENTRIES = eps',
            '$heap_owners($heap_prune($heap_graph(S_argument)), HOBJECT n_closure) = 2',
            '$heap_owners($heap_prune($heap_graph(S_argument)), HOBJECT n_receiver) = 2',
            '$cc_review_output(S_argument.EVENTS) = $ptascii("P:1:1:1;C:1:1:1;A:1;")',
        ]
        reach('S_receiver', 'S_argument', 4)
        checks += [
            'S_receiver.CURRENT = (pcallcontext_receiver)',
            'pcallcontext_receiver.TARGET = METHOD_TARGET n_receiver porigin_destructor',
            '~((HOBJECT n_closure) <- S_receiver.ALLOCATIONS)',
            '~((HOBJECT n_argument) <- S_receiver.ALLOCATIONS)',
            '$cc_review_output(S_receiver.EVENTS) = $ptascii("P:1:1:1;C:1:1:1;A:1;T:1:1:1;")',
            '$closure_scope_at(S_receiver.CLOSURESCOPES, n_closure) = eps',
            'S_receiver.DESTRUCTION.CALLS = pdestructorcall_receiver :: pdestructorcall_tail*',
            'pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)',
            'pdestructionoperation_receiver.SOURCE = TICK_UNREGISTER_SOURCE pshutdownentry_query ptickentry_selected pshutdownproducer_selected',
            '$eager_operation_source_valid(S_receiver, pdestructionoperation_receiver)',
            # Derived dropped lookup metadata after the actual Closure retires.
            '~$eager_operation_source_valid(S_receiver, pdestructionoperation_receiver[.SOURCE = TICK_UNREGISTER_SOURCE pshutdownentry_query ptickentry_selected (pshutdownproducer_selected[.SCOPE = eps])])',
        ]
        retired = ('n_closure', 'n_receiver', 'n_argument')
    checks += [
        'S_done = $drive_steps(S_receiver, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.TICKENTRIES = eps',
        'S_done.DESTRUCTION.FRAMES = eps', 'S_done.DESTRUCTION.RELEASES = eps',
        'S_done.DESTRUCTION.CALLS = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$cc_review_output(S_done.EVENTS) = [' + ','.join(map(str, expected_stdout)) + ']',
        *[f'~((HOBJECT {node}) <- S_done.ALLOCATIONS)' for node in retired],
    ]
    return checks
