"""Retain the genuine REQUEST header through two returning Warning callbacks."""
import json

from string_offset_undefined_cv_review import guards

HELPERS = r'''
dec $request_base_peer_front(pstate, nat) : bool
def $request_base_peer_front(S, 0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = KEY_READ_RESULT pkeyread
  -- if pkeyread.PHASE = KEY_CV
def $request_base_peer_front(S, 1) = true
  -- if S.TODO = (KEY_READ_RESULT pkeyread) :: ptask*
  -- if pkeyread.PHASE = KEY_CV
def $request_base_peer_front(S, 2) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_CAST
def $request_base_peer_front(S, 3) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_BOUNDS 8
def $request_base_peer_front(S, n) = false -- otherwise
dec $request_base_peer_seek(pstate, nat, nat) : pstate
def $request_base_peer_seek(S, n_stage, n) = S -- if $request_base_peer_front(S, n_stage)
def $request_base_peer_seek(S, n_stage, n) = S
  -- if ~$request_base_peer_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $request_base_peer_seek(S, n_stage, 0) = S
  -- if ~$request_base_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $request_base_peer_seek(S, n_stage, n) = $request_base_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$request_base_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def seek(start, stage, result):
    return [f'{result}_found = $request_base_peer_seek({start}, {stage}, 1000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 0, 'S_before') + [
        'S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*',
        'perrorcall.RESUME = KEY_READ_RESULT pkeyread',
        r'S_before.CURRENT = eps /\ S_before.FRAMES = eps',
        r'pkeyread.PHASE = KEY_CV /\ pkeyread.VALUE = PNULL',
        'pkeyread.NAME = $ptascii("missing")',
        'pkeyread.INPUT = VARIABLE pkeyread.NAME 21',
        r'pkeyread.LINE = 21 /\ pkeyread.KEY = KSTRING eps',
        'pkeyread.BASE = PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("abc"))',
        'pkeyread.OWNERS = BASE_VALUE (VARIABLE n_base_name* z_base)',
        'n_base_name* = $ptascii("base")',
        '$lookup(S_before.ENV, n_base_name*) = (n_original)',
        'S_before.STORE[n_original] = DEFINED pkeyread.BASE',
        '~(n_original <- S_before.REFCELLS)',
        '$lookup(S_before.ENV, $ptascii("keeper")) = (n_keeper)',
        '$lookup(S_before.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_before.ENV, $ptascii("right")) = (n_right)',
        'n_keeper =/= n_original',
        '$string_read_cell(S_before, n_keeper)',
        'S_before.STORE[n_keeper] = DEFINED pkeyread.BASE',
        '$lookup(S_before.ENV, pkeyread.NAME) = eps',
        '$string_carrier_valid(S_before, pkeyread.BASE)',
        'S_before.STRINGDATA[n_identity] = $ptascii("abc")',
        'H_before = $heap_graph(S_before)',
        'H_before.NODES = [HCELL n_left, HCELL n_right, HCELL n_original, HCELL n_keeper]',
        'H_before.ROOTS = [HCELL n_keeper, HCELL n_original, HCELL n_right, HCELL n_left]',
        r'H_before.EDGES = eps /\ H_before.DEBTS = eps',
        '$heap_owners(H_before, HCELL n_original) = 1',
        '$heap_owners(H_before, HCELL n_keeper) = 1',
        '$error_call_valid(S_before, perrorcall)',
        *guards('S_before'),
    ] + seek('S_before', 1, 'S_key') + [
        'S_key.TODO = (KEY_READ_RESULT pkeyread) :: ptask_tail*',
        r'S_key.CURRENT = eps /\ S_key.FRAMES = eps',
        'S_key.STORE[n_original] = DEFINED pkeyread.BASE',
        '~((HCELL n_original) <- S_key.ALLOCATIONS)',
        '~((HCELL n_original) <- $heap_prune($heap_graph(S_key)).NODES)',
        '$lookup(S_key.ENV, n_base_name*) = (n_base)',
        r'n_base =/= n_original /\ n_base =/= n_keeper',
        '$call_reference_operand_valid(S_key, REFERENCE n_base)',
        'pvalue_current = PSTRING_CARRIER INTERNED_STRING ($ptascii("abcdefghij"))',
        'S_key.STORE[n_base] = DEFINED pvalue_current',
        '$lookup(S_key.ENV, pkeyread.NAME) = (n_key)',
        'S_key.STORE[n_key] = DEFINED (PINT 4)',
        '~(n_key <- S_key.REFCELLS)',
        '$lookup(S_key.ENV, $ptascii("keeper")) = (n_keeper)',
        '$string_read_cell(S_key, n_keeper)',
        'S_key.STORE[n_keeper] = DEFINED pkeyread.BASE',
        'S_key.STRINGDATA[n_identity] = $ptascii("abc")',
        'pstringread = {READ pkeyread, BASECELL eps, KEYCELL eps, KEYREF false, PHASE STRING_CAST}',
        '$key_read_valid(S_key, pkeyread)',
        '$string_read_cv_request(pkeyread)',
        '$string_read_cv_receipt(pkeyread)',
        '$string_read_cv_source(S_key, pstringread)',
        '$string_read_cv_plan(S_key, pkeyread) = (pstringread)',
        '$string_read_retainer(S_key, pstringread, BIND ($ptascii("keeper")) n_keeper)',
        '$string_read_retained(S_key, pstringread, S_key.ENV)',
        '$string_read_provider_ready(S_key, pstringread)',
        '$task_nodes(KEY_READ_RESULT pkeyread) = eps',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        'H = $heap_graph(S_key)',
        'H.NODES = [HCELL n_left, HCELL n_right, HCELL n_keeper, HCELL n_base, HCELL n_key]',
        'H.ROOTS = [HCELL n_key, HCELL n_base, HCELL n_keeper, HCELL n_right, HCELL n_left]',
        r'H.EDGES = eps /\ H.DEBTS = eps',
        '$heap_owners(H, HCELL n_keeper) = 1',
        '$heap_owners(H, HCELL n_base) = 1',
        '$heap_owners(H, HCELL n_key) = 1',
        *guards('S_key'),
        'S_key.ERRORHANDLER = S_before.ERRORHANDLER',
        'S_key.ERRORHANDLERS = S_before.ERRORHANDLERS',
        'S_key.EVENTS = S_before.EVENTS ++ [OUTPUT ($ptascii("2")), OUTPUT ($ptascii(":")), OUTPUT ($ptascii("Undefined variable $missing")), OUTPUT ($ptascii(";"))]',
        'S_key.ERRORHANDLER.CALLBACK = (pvalue_handler)',
        'perrorcall_cast = {SITE pkeyread.SITE, LEVEL 2, MESSAGE ($ptascii("String offset cast occurred")), LINE 21, EVENT (DIAGNOSTIC "Warning" ($ptascii("String offset cast occurred")) 21), CALLBACK pvalue_handler, TARGET eps, RESUME (STRING_READ_RESULT pstringread)}',
        'PhpStep: S_key ~> S_dispatch',
        'S_dispatch = S_key[.TODO = (ERROR_HANDLER_INVOKE perrorcall_cast) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.ERRORFATALTRACE = eps]',
        '$error_call_valid(S_dispatch, perrorcall_cast)',
        '$heap_graph(S_dispatch) = H',
    ] + seek('S_dispatch', 2, 'S_cast') + [
        'S_cast.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*',
        r'S_cast.CURRENT = eps /\ S_cast.FRAMES = eps',
        'S_cast.STORE[n_base] = DEFINED pvalue_current',
        'S_cast.STORE[n_keeper] = DEFINED pkeyread.BASE',
        'S_cast.STORE[n_key] = DEFINED (PINT 8)',
        '$heap_graph(S_cast) = H',
        '$string_read_source(S_cast, pstringread)',
        '$string_read_provider_ready(S_cast, pstringread)',
        '$string_read_key_current(S_cast, pstringread) = (PINT 8)',
        '$string_read_current_offset(S_cast, pstringread, PINT 8) = (8)',
        '~$string_read_in_range(pkeyread.BASE, 8)',
        '$string_read_in_range(pvalue_current, 8)',
        'pstringread_bounds = pstringread[.PHASE = STRING_BOUNDS 8]',
        'perrorcall_bounds = perrorcall_cast[.MESSAGE = $ptascii("Uninitialized string offset 8")][.EVENT = DIAGNOSTIC "Warning" ($ptascii("Uninitialized string offset 8")) 21][.RESUME = STRING_READ_RESULT pstringread_bounds]',
        'PhpStep: S_cast ~> S_bounds_dispatch',
        'S_bounds_dispatch = S_cast[.TODO = (ERROR_HANDLER_INVOKE perrorcall_bounds) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.ERRORFATALTRACE = eps]',
        '$error_call_valid(S_bounds_dispatch, perrorcall_bounds)',
        '$heap_graph(S_bounds_dispatch) = H',
        *guards('S_cast'),
    ] + seek('S_bounds_dispatch', 3, 'S_bounds') + [
        'S_bounds.TODO = (STRING_READ_RESULT pstringread_bounds) :: ptask_tail*',
        '$heap_graph(S_bounds) = H',
        '$string_read_source(S_bounds, pstringread_bounds)',
        'PhpStep: S_bounds ~> S_empty',
        'S_empty = S_bounds[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING eps)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$heap_graph(S_empty) = H',
        '$drive_steps(S_bounds, 0) = S_bounds[.COMPLETION = BUDGET]',
        '$drive_steps(S_bounds, 1) = S_empty[.COMPLETION = BUDGET]',
        *guards('S_empty'),
    ]
    derived_start = len(checks)
    checks += [
        # Early liveness is needed before dispatching mandatory CAST.
        'S_lost = S_key[.ENV = $unbind(S_key.ENV, $ptascii("keeper"))]',
        '$string_read_cv_source(S_lost, pstringread)',
        '~$string_read_retained(S_lost, pstringread, S_lost.ENV)',
        '$string_read_cv_plan(S_lost, pkeyread) = eps',
        'S_early = $key_read_resume(S_lost, pkeyread)',
        'S_early.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"',
        'S_early.EVENTS = S_lost.EVENTS',
        '$heap_graph(S_early) = $heap_graph(S_lost)',
        # Equal registry bytes do not retain the selected string identity.
        'pvalue_twin = PSTRING_CARRIER (REQUEST_STRING (|S_key.STRINGDATA|)) ($ptascii("abc"))',
        'S_twin = S_key[.STRINGDATA = S_key.STRINGDATA ++ [$ptascii("abc")]][.STORE[n_keeper] = DEFINED pvalue_twin]',
        '$string_carrier_valid(S_twin, pvalue_twin)',
        '$string_read_cv_source(S_twin, pstringread)',
        '~$string_read_retained(S_twin, pstringread, S_twin.ENV)',
        '$string_read_cv_plan(S_twin, pkeyread) = eps',
        # Neither a current base nor retired STORE bytes authenticate the keeper.
        'S_erased = S_key[.STORE[n_original] = DEFINED (PINT 77)]',
        '$string_read_cv_plan(S_erased, pkeyread) = (pstringread)',
        'S_no_base = S_key[.ENV = $unbind(S_key.ENV, n_base_name*)]',
        '$string_read_cv_plan(S_no_base, pkeyread) = (pstringread)',
        '~$string_read_cv_source(S_key[.STRINGDATA = eps], pstringread)',
        '~$string_read_provider_ready(S_key[.STRINGDATA = eps], pstringread)',
        'S_marked = S_key[.REFCELLS = n_keeper :: S_key.REFCELLS]',
        '~$string_read_retained(S_marked, pstringread, S_marked.ENV)',
        '$string_read_cv_plan(S_marked, pkeyread) = eps',
        '~$string_read_retainer(S_key, pstringread, BIND n_base_name* n_keeper)',
        # Source authority persists after the second callback loses its keeper.
        'S_cast_lost = S_cast[.ENV = $unbind(S_cast.ENV, $ptascii("keeper"))]',
        '$string_read_source(S_cast_lost, pstringread)',
        '~$string_read_provider_ready(S_cast_lost, pstringread)',
        'PhpStep: S_cast_lost ~> S_cast_refused',
        'S_cast_refused = S_cast_lost[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]',
        '$heap_graph(S_cast_refused) = $heap_graph(S_cast_lost)',
        # Fixed bounds completion reads no remaining CV or owner.
        'S_bounds_absent = S_bounds[.ENV = eps]',
        '$string_read_source(S_bounds_absent, pstringread_bounds)',
        '$string_read_ready(S_bounds_absent, pstringread_bounds)',
        'PhpStep: S_bounds_absent ~> S_fixed',
        'S_fixed = S_bounds_absent[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING eps)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        # Derived first-Undefined throws retain mask-sensitive reporting.
        'S_throw = S_key[.TODO = (THROW_SEARCH 0) :: ptask_tail*]',
        '$string_read_cv_plan(S_throw, pkeyread) = (pstringread)',
        '$error_handler_eligible(S_throw, 2)',
        '$error_read_discard(S_throw, KEY_READ_RESULT pkeyread) = S_throw',
        'S_mask = S_throw[.ERRORHANDLER.LEVELS = 0]',
        '~$error_handler_eligible(S_mask, 2)',
        '$error_read_discard(S_mask, KEY_READ_RESULT pkeyread) = S_mask[.ERRORFATALTRACE = eps][.EVENTS = S_mask.EVENTS ++ [DIAGNOSTIC "Warning" ($ptascii("String offset cast occurred")) 21, DIAGNOSTIC "Warning" ($ptascii("Uninitialized string offset 4")) 21]]',
    ]
    for change in ('[.ORIGIN = eps]', '[.SOURCES = eps]', '[.CODE = eps]'):
        checks.append('~$string_read_cv_source(S_key' + change + ', pstringread)')
    for change in ('[.BASECELL = (n_original)]', '[.KEYCELL = (n_key)]',
                   '[.READ.LINE = 22]', '[.READ.OWNERS = BASE_VALUE pkeyread.INPUT]'):
        checks.append('~$string_read_cv_source(S_key, pstringread' + change + ')')
    for change in ('[.GLOBAL = true]', '[.MODE = KEY_IS]', '[.PHASE = KEY_NULL]',
                   '[.VALUE = PINT 0]', '[.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)]',
                   '[.BASE = PSTRING ($ptascii("abc"))]'):
        checks.append('~$string_read_cv_request(pkeyread' + change + ')')
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
