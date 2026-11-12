"""Check the undefined-CV receipt through mandatory CAST and fixed bounds."""
import json

HELPERS = r'''
dec $undefined_cv_review_front(pstate, nat) : bool
def $undefined_cv_review_front(S, 0) = true
  -- if S.TODO = (KEY_READ_RESULT pkeyread) :: ptask*
  -- if ~pkeyread.GLOBAL /\ pkeyread.PHASE = KEY_CV
def $undefined_cv_review_front(S, 1) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_CAST
def $undefined_cv_review_front(S, 2) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_BOUNDS 5
def $undefined_cv_review_front(S, n) = false -- otherwise
dec $undefined_cv_review_seek(pstate, nat, nat) : pstate
def $undefined_cv_review_seek(S, n_stage, n) = S
  -- if $undefined_cv_review_front(S, n_stage)
def $undefined_cv_review_seek(S, n_stage, n) = S
  -- if ~$undefined_cv_review_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $undefined_cv_review_seek(S, n_stage, 0) = S
  -- if ~$undefined_cv_review_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $undefined_cv_review_seek(S, n_stage, n) = $undefined_cv_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$undefined_cv_review_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def seek(start, stage, result):
    return [f'{result}_found = $undefined_cv_review_seek({start}, {stage}, 1000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def guards(state):
    return [f'$call_current_valid({state})',
            f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 0, 'S') + [
        'S.TODO = (KEY_READ_RESULT pkeyread) :: ptask_tail*',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        r'pkeyread.PHASE = KEY_CV /\ pkeyread.VALUE = PNULL',
        r'pkeyread.NAME = $ptascii("missing") /\ pkeyread.KEY = KSTRING eps',
        'pkeyread.INPUT = VARIABLE pkeyread.NAME pkeyread.LINE',
        'pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))',
        'pkeyread.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)',
        '$lookup(S.ENV, pkeyread.NAME) = (n_key)',
        'S.STORE[n_key] = DEFINED (PINT 1)',
        '~(n_key <- S.REFCELLS)',
        '$heap_owners($heap_graph(S), HCELL n_key) = 1',
        '$key_read_valid(S, pkeyread)',
        '$string_read_cv_receipt(pkeyread)',
        '$string_read_cv_plan(S, pkeyread) = (pstringread)',
        'pstringread = {READ pkeyread, BASECELL eps, KEYCELL eps, PHASE STRING_CAST}',
        '$string_read_cv_source(S, pstringread)',
        '$string_read_source(S, pstringread)',
        '$string_read_cv_key(S, pkeyread) = (PINT 1)',
        '$string_read_key_current(S, pstringread) = (PINT 1)',
        '$string_read_ready(S, pstringread)',
        '$origin_child((pkeyread.SITE), [PCFIELD 0]) = (porigin_base)',
        '$compiled_read(S, porigin_base) = (PSTRING ($ptascii("abc")))',
        '$compiled_string_value(S, porigin_base, PSTRING ($ptascii("abc"))) = pkeyread.BASE',
        '$task_nodes(KEY_READ_RESULT pkeyread) = eps',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
        # Derived receipt, source, ownership and current-key counterexamples.
        '~$string_read_cv_receipt(pkeyread[.GLOBAL = true])',
        '~$string_read_cv_receipt(pkeyread[.MODE = KEY_IS])',
        '~$string_read_cv_receipt(pkeyread[.PHASE = KEY_NULL])',
        '~$string_read_cv_receipt(pkeyread[.VALUE = PINT 1])',
        '~$string_read_cv_receipt(pkeyread[.NAME = eps])',
        '~$string_read_cv_receipt(pkeyread[.BASE = PSTRING ($ptascii("abc"))])',
        '~$string_read_cv_receipt(pkeyread[.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))])',
        '~$string_read_cv_receipt(pkeyread[.OWNERS = BASE_VALUE pkeyread.INPUT])',
        '~$string_read_cv_source(S[.ORIGIN = eps], pstringread)',
        '~$string_read_cv_source(S[.SOURCES = eps], pstringread)',
        '~$string_read_cv_source(S[.CODE = eps], pstringread)',
        '~$string_read_cv_source(S[.POOLS = eps], pstringread)',
        '~$string_read_cv_source(S, pstringread[.BASECELL = (n_key)])',
        '~$string_read_cv_source(S, pstringread[.KEYCELL = (n_key)])',
        '~$string_read_cv_source(S, pstringread[.READ.LINE = $(pkeyread.LINE + 1)])',
        'pvalue_wrong = PSTRING_CARRIER INTERNED_STRING ($ptascii("abd"))',
        'pkeyread_wrong = pkeyread[.BASE = pvalue_wrong][.OWNERS = BASE_VALUE (KNOWN pvalue_wrong)]',
        '~$string_read_cv_source(S, pstringread[.READ = pkeyread_wrong])',
        'S_absent = S[.ENV = eps]',
        '$string_read_cv_key(S_absent, pkeyread) = (PNULL)',
        'S_undefined = S[.STORE[n_key] = UNDEFINED]',
        '$string_read_cv_key(S_undefined, pkeyread) = (PNULL)',
        '$string_read_cv_key(S[.REFCELLS = n_key :: S.REFCELLS], pkeyread) = eps',
        '$string_read_cv_key(S_undefined[.REFCELLS = n_key :: S_undefined.REFCELLS], pkeyread) = eps',
        '$string_read_cv_key(S[.STORE[n_key] = DEFINED (PINT 9223372036854775808)], pkeyread) = eps',
        '$string_read_cv_key(S[.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("1")))], pkeyread) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("1")))',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_cast) :: ptask_tail*',
        'perrorcall_cast.RESUME = STRING_READ_RESULT pstringread',
        'perrorcall_cast.MESSAGE = $ptascii("String offset cast occurred")',
        r'perrorcall_cast.LEVEL = 2 /\ perrorcall_cast.LINE = pkeyread.LINE',
        '$error_call_valid(S_dispatch, perrorcall_cast)',
        '~$error_call_valid(S_dispatch, perrorcall_cast[.MESSAGE = eps])',
        r'S_dispatch.STORE = S.STORE /\ S_dispatch.EVENTS = S.EVENTS',
        'S_dispatch.ALLOCATIONS = S.ALLOCATIONS',
        '$task_nodes(ERROR_HANDLER_INVOKE perrorcall_cast) = eps',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 1) = S_dispatch[.COMPLETION = BUDGET]',
        *guards('S_dispatch'),
    ] + seek('S_dispatch', 1, 'S_cast') + [
        'S_cast.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*',
        r'S_cast.CURRENT = eps /\ S_cast.FRAMES = eps',
        '$lookup(S_cast.ENV, pkeyread.NAME) = (n_key)',
        'S_cast.STORE[n_key] = DEFINED (PINT 5)',
        r'pstringread.READ.VALUE = PNULL /\ pstringread.READ.PHASE = KEY_CV',
        '$string_read_source(S_cast, pstringread)',
        '$string_read_key_current(S_cast, pstringread) = (PINT 5)',
        '$string_read_ready(S_cast, pstringread)',
        'PhpStep: S_cast ~> S_bounds_dispatch',
        'S_bounds_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall_bounds) :: ptask_tail*',
        'perrorcall_bounds.RESUME = STRING_READ_RESULT pstringread_bounds',
        'pstringread_bounds = pstringread[.PHASE = STRING_BOUNDS 5]',
        'perrorcall_bounds.MESSAGE = $ptascii("Uninitialized string offset 5")',
        '$error_call_valid(S_bounds_dispatch, perrorcall_bounds)',
        '$string_read_source(S_bounds_dispatch, pstringread_bounds)',
        '~$string_read_source(S_bounds_dispatch, pstringread[.PHASE = STRING_BOUNDS 0])',
        'S_bounds_dispatch.STORE = S_cast.STORE',
        'S_bounds_dispatch.EVENTS = S_cast.EVENTS',
        '$drive_steps(S_cast, 1) = S_bounds_dispatch[.COMPLETION = BUDGET]',
        *guards('S_bounds_dispatch'),
    ] + seek('S_bounds_dispatch', 2, 'S_bounds') + [
        'S_bounds.TODO = (STRING_READ_RESULT pstringread_bounds) :: ptask_tail*',
        r'S_bounds.CURRENT = eps /\ S_bounds.FRAMES = eps',
        '$lookup(S_bounds.ENV, pkeyread.NAME) = (n_key)',
        'S_bounds.STORE[n_key] = DEFINED (PINT 0)',
        '$string_read_source(S_bounds, pstringread_bounds)',
        '$string_read_key_current(S_bounds, pstringread_bounds) = (PINT 0)',
        '$string_read_ready(S_bounds, pstringread_bounds)',
        '$string_read_ready(S_bounds[.ENV = eps], pstringread_bounds)',
        '$error_read_discard(S_bounds, STRING_READ_RESULT pstringread_bounds) = S_bounds',
        'PhpStep: S_bounds ~> S_empty',
        'S_empty.TODO = ptask_tail*',
        'S_empty.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING eps)',
        r'S_empty.STORE = S_bounds.STORE /\ S_empty.EVENTS = S_bounds.EVENTS',
        'S_empty.ALLOCATIONS = S_bounds.ALLOCATIONS',
        r'S_empty.POOLS = S_bounds.POOLS /\ S_empty.SOURCES = S_bounds.SOURCES',
        '$drive_steps(S_bounds, 0) = S_bounds[.COMPLETION = BUDGET]',
        '$drive_steps(S_bounds, 1) = S_empty[.COMPLETION = BUDGET]',
        *guards('S_empty'),
    ]
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks))
