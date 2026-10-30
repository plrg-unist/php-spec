"""Independent reached inner cancellation; uses the common cache transport."""
import base64


CASES = ('tick-invoke-inner-throw-keeps-raw-wrapper-and-persistent-cache',)
DERIVED = {CASES[0]: 1}
HELPERS = r'''
dec $ci_review_notice(pstate, int) : bool
def $ci_review_notice(S, z) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME = $ptascii("inner_notice")
  -- if $error_context_call(S, pcallcontext) = (perrorcall)
  -- if perrorcall.LEVEL = z
def $ci_review_notice(S, z) = false -- otherwise
dec $ci_review_front(pstate, nat, int) : bool
def $ci_review_front(S, 0, z_line) = $ci_review_notice(S, 8192)
def $ci_review_front(S, 1, z_line) = $ci_review_notice(S, 16384)
def $ci_review_front(S, 2, z_line) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET /\ pconfigcall.LINE = z_line
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $ci_review_front(S, 3, z_line) = true
  -- if $ci_review_notice(S, 16384)
  -- if $lookup(S.ENV, $ptascii("raw_token")) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED (POBJECT n_argument)
  -- if S.RESULT = KNOWN PNULL
def $ci_review_front(S, 4, z_line) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("TickInnerArgument")
  -- if $class_method_origin(S.CLASSES, porigin) = (pmethoddesc)
  -- if pmethoddesc.NAME = $ptascii("__destruct")
def $ci_review_front(S, n, z_line) = false -- otherwise
dec $ci_review_seek(pstate, nat, int, nat) : pstate
def $ci_review_seek(S, n_stage, z_line, n) = S -- if $ci_review_front(S, n_stage, z_line)
def $ci_review_seek(S, n_stage, z_line, 0) = S -- if ~$ci_review_front(S, n_stage, z_line)
def $ci_review_seek(S, n_stage, z_line, n) = $ci_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, z_line, $nabs($(n - 1)))
  -- if ~$ci_review_front(S, n_stage, z_line) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $ci_review_seek(S, n_stage, z_line, n) = S
  -- if ~$ci_review_front(S, n_stage, z_line) /\ $(n > 0)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def conditions(name, program, source, expected_stdout):
    assert name == CASES[0]
    path = base64.b64encode(str(source).encode()).decode()
    checks = [f'S_initial = $php_run({program}, 0, "{path}")',
              'S_initial.COMPLETION = BUDGET']

    def reach(label, prior, stage, line=0):
        checks.extend([f'{label}_found = $ci_review_seek({prior}, {stage}, {line}, 4000)',
                       fr'{label}_found.COMPLETION = NORMAL \/ {label}_found.COMPLETION = BUDGET',
                       f'{label} = {label}_found[.COMPLETION = NORMAL]',
                       f'$ci_review_front({label}, {stage}, {line})',
                       f'$call_descriptors_valid({label})',
                       f'$heap_valid($heap_graph({label}))'])

    def owners(state, node, count):
        checks.append(f'$heap_owners($heap_prune($heap_graph({state})), HOBJECT {node}) = {count}')

    reach('S_outer', 'S_initial', 0)
    checks += [
        'S_outer.TICKENTRIES = [ptickentry]',
        'ptickentry.ENTRY.TARGET = CALLBACK_INVOKE_TARGET n_closure',
        'ptickentry.ENTRY.CACHEOBJECT = (n_closure)',
        'ptickentry.ENTRY.ARGS = [pvalue_raw, POBJECT n_argument]',
        '$string_bytes(pvalue_raw) = ($ptascii("7"))',
        '$object_name(S_outer, n_argument) = $ptascii("TickInnerArgument")',
        'ptickentry.ENTRY.RAW = (parray_raw)',
        'S_outer.CURRENT = (pcallcontext_outer)',
        'pcallcontext_outer.INSTANCE = eps',
        'S_outer.FRAMES = [pframe_outer]', 'pframe_outer.CONTEXT = eps',
        '$error_context_call(S_outer, pcallcontext_outer) = (perrorcall_outer)',
        'perrorcall_outer.RESUME = TICK_SEND ptickdispatch_outer 0',
        'ptickdispatch_outer.SENT = eps',
        'ptickdispatch_outer.ENTRY = (ptickentry.ID)',
        '$tick_is_calling(S_outer, ptickentry.ID)',
        # Derived frozen-selector forgery; the original registration is unchanged.
        '~$tick_entry_valid(S_outer, ptickentry[.ENTRY.RAW = ($array_insert(parray_raw, KINT 0, DIRECT (POBJECT n_argument)))])',
    ]
    owners('S_outer', 'n_closure', 1)
    owners('S_outer', 'n_argument', 1)

    reach('S_inner', 'S_outer', 1)
    checks += [
        'S_inner.TICKENTRIES = [ptickentry]',
        'S_inner.CURRENT = (pcallcontext_inner)',
        'pcallcontext_inner.INSTANCE = eps',
        'S_inner.FRAMES = [pframe_inner]', 'pframe_inner.CONTEXT = eps',
        '$error_context_call(S_inner, pcallcontext_inner) = (perrorcall_inner)',
        'perrorcall_inner.RESUME = TICK_INVOKE_ENTER ptickdispatch_inner',
        'ptickdispatch_inner.SENT = [KNOWN pvalue_raw, KNOWN (POBJECT n_argument)]',
        'ptickdispatch_inner.ENTRY = (ptickentry.ID)',
        '$tick_is_calling(S_inner, ptickentry.ID)',
        '$tick_invoke_valid(S_inner, ptickdispatch_inner)',
    ]
    owners('S_inner', 'n_closure', 1)
    owners('S_inner', 'n_argument', 2)

    reach('S_trace', 'S_inner', 3)
    checks += [
        '$lookup(S_trace.ENV, $ptascii("trace")) = (n_trace_cell)',
        'S_trace.STORE[n_trace_cell] = DEFINED (PARRAY n_trace)',
        '|S_trace.ARRAYS[n_trace].ITEMS| = 2',
        '$entry_lookup(S_trace.ARRAYS[n_trace].ITEMS, KINT 1) = (DIRECT (PARRAY n_wrapper))',
        '$entry_lookup(S_trace.ARRAYS[n_wrapper].ITEMS, KSTRING ($ptascii("function"))) = (DIRECT pvalue_function)',
        '$string_bytes(pvalue_function) = ($ptascii("__invoke"))',
        '$entry_lookup(S_trace.ARRAYS[n_wrapper].ITEMS, KSTRING ($ptascii("class"))) = (DIRECT pvalue_class)',
        '$string_bytes(pvalue_class) = ($ptascii("Closure"))',
        '$entry_lookup(S_trace.ARRAYS[n_wrapper].ITEMS, KSTRING ($ptascii("type"))) = (DIRECT pvalue_type)',
        '$string_bytes(pvalue_type) = ($ptascii("->"))',
        '$entry_lookup(S_trace.ARRAYS[n_wrapper].ITEMS, KSTRING ($ptascii("file"))) = (DIRECT pvalue_file)',
        '$string_bytes(pvalue_file) = ($call_sourcefile(S_trace.FILES, ptickdispatch_inner.SITE))',
        '$entry_lookup(S_trace.ARRAYS[n_wrapper].ITEMS, KSTRING ($ptascii("line"))) = (DIRECT (PINT 80))',
        '$entry_lookup(S_trace.ARRAYS[n_wrapper].ITEMS, KSTRING ($ptascii("args"))) = (DIRECT (PARRAY n_raw_args))',
        '$entry_lookup(S_trace.ARRAYS[n_raw_args].ITEMS, KINT 0) = (DIRECT pvalue_raw_trace)',
        '$string_bytes(pvalue_raw_trace) = ($ptascii("7"))',
        '$entry_lookup(S_trace.ARRAYS[n_raw_args].ITEMS, KINT 1) = (DIRECT (POBJECT n_argument))',
    ]

    lines = source.read_bytes().splitlines()
    q_lines = [i for i, line in enumerate(lines, 1) if b'echo "Q:"' in line]
    assert len(q_lines) == 1
    reach('S_cached', 'S_trace', 2, q_lines[0])
    prefix = expected_stdout.split(b'Q:', 1)[0] + b'Q:1:1:'
    checks += [
        'S_cached.TICKENTRIES = [ptickentry]',
        '~$tick_running(S_cached)',
        '$cc_review_output(S_cached.EVENTS) = [' + ','.join(map(str, prefix)) + ']',
    ]
    owners('S_cached', 'n_closure', 1)
    owners('S_cached', 'n_argument', 1)

    reach('S_argument', 'S_cached', 4)
    prefix = expected_stdout.split(b'T:', 1)[0]
    checks += [
        'S_argument.TICKENTRIES = eps',
        '(HOBJECT n_closure) <- S_argument.ALLOCATIONS',
        '$cc_review_output(S_argument.EVENTS) = [' + ','.join(map(str, prefix)) + ']',
    ]
    owners('S_argument', 'n_closure', 2)
    checks += [
        'S_done = $drive_steps(S_argument, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.TICKENTRIES = eps',
        'S_done.DESTRUCTION.FRAMES = eps', 'S_done.DESTRUCTION.RELEASES = eps',
        'S_done.DESTRUCTION.CALLS = eps', 'S_done.DESTRUCTION.OPERATIONS = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        '$cc_review_output(S_done.EVENTS) = [' + ','.join(map(str, expected_stdout)) + ']',
        '~((HOBJECT n_closure) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_argument) <- S_done.ALLOCATIONS)',
    ]
    return checks
