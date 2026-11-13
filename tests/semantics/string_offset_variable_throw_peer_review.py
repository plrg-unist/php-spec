"""Retain the selected header after the original VARIABLE cell is retired."""
import json

from string_offset_undefined_cv_review import guards

HELPERS = r'''
dec $variable_throw_peer_front(pstate, nat) : bool
def $variable_throw_peer_front(S, 0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = KEY_READ_RESULT pkeyread
  -- if pkeyread.PHASE = KEY_CV
def $variable_throw_peer_front(S, 1) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = KEY_READ_RESULT pkeyread
  -- if pkeyread.PHASE = KEY_CV
def $variable_throw_peer_front(S, n) = false -- otherwise
dec $variable_throw_peer_seek(pstate, nat, nat) : pstate
def $variable_throw_peer_seek(S, n_stage, n) = S -- if $variable_throw_peer_front(S, n_stage)
def $variable_throw_peer_seek(S, n_stage, n) = S
  -- if ~$variable_throw_peer_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $variable_throw_peer_seek(S, n_stage, 0) = S
  -- if ~$variable_throw_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $variable_throw_peer_seek(S, n_stage, n) = $variable_throw_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$variable_throw_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_before_found = $variable_throw_peer_seek(S_initial, 0, 1000)',
        r'S_before_found.COMPLETION = NORMAL \/ S_before_found.COMPLETION = BUDGET',
        'S_before = S_before_found[.COMPLETION = NORMAL]',
        'S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall_before) :: ptask_before*',
        'perrorcall_before.RESUME = KEY_READ_RESULT pkeyread',
        r'S_before.CURRENT = eps /\ S_before.FRAMES = eps',
        r'pkeyread.PHASE = KEY_CV /\ pkeyread.VALUE = PNULL',
        'pkeyread.NAME = $ptascii("key")',
        'pkeyread.INPUT = VARIABLE pkeyread.NAME 18',
        r'pkeyread.LINE = 18 /\ pkeyread.KEY = KSTRING eps',
        'pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))',
        'pkeyread.OWNERS = BASE_VALUE (VARIABLE n_base_name* z_base)',
        'n_base_name* = $ptascii("base")',
        '$lookup(S_before.ENV, n_base_name*) = (n_original)',
        'S_before.STORE[n_original] = DEFINED pkeyread.BASE',
        '~(n_original <- S_before.REFCELLS)',
        '$lookup(S_before.ENV, pkeyread.NAME) = eps',
        '$lookup(S_before.ENV, $ptascii("supplied")) = (n_supplied)',
        'S_before.STORE[n_supplied] = DEFINED (POBJECT n_exception)',
        '$lookup(S_before.ENV, $ptascii("dst")) = (n_dst)',
        'S_before.STORE[n_dst] = DEFINED (PINT 99)',
        'H_before = $heap_graph(S_before)',
        'H_before.NODES = [HCELL n_original, HARRAY n_trace, HOBJECT n_exception, HCELL n_supplied, HCELL n_dst]',
        'H_before.ROOTS = [HCELL n_dst, HCELL n_supplied, HCELL n_original]',
        'H_before.EDGES = [HEDGE (HOBJECT n_exception) (HARRAY n_trace), HEDGE (HCELL n_supplied) (HOBJECT n_exception)]',
        'H_before.DEBTS = eps',
        '$heap_owners(H_before, HCELL n_original) = 1',
        '$heap_owners(H_before, HOBJECT n_exception) = 1',
        '$error_call_valid(S_before, perrorcall_before)',
        'S_found = $variable_throw_peer_seek(S_before, 1, 1000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = KEY_READ_RESULT pkeyread',
        'perrorcall.CALLBACK = perrorcall_before.CALLBACK',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        'S.STORE[n_original] = DEFINED pkeyread.BASE',
        '~((HCELL n_original) <- S.ALLOCATIONS)',
        '~((HCELL n_original) <- $heap_prune($heap_graph(S)).NODES)',
        '$lookup(S.ENV, n_base_name*) = (n_base)',
        'n_base =/= n_original',
        '$call_reference_operand_valid(S, REFERENCE n_base)',
        'pvalue_current = PSTRING_CARRIER INTERNED_STRING ($ptascii("abcdefghij"))',
        'S.STORE[n_base] = DEFINED pvalue_current',
        '$lookup(S.ENV, pkeyread.NAME) = (n_key)',
        'S.STORE[n_key] = DEFINED (PINT 8)',
        '~(n_key <- S.REFCELLS)',
        'S.REFCELLS = [n_base, n_supplied]',
        '$lookup(S.ENV, $ptascii("supplied")) = (n_supplied)',
        'S.STORE[n_supplied] = DEFINED (POBJECT n_exception)',
        'S.STORE[n_dst] = DEFINED (PINT 99)',
        '$throwable_member(S, n_exception)',
        'S.ERRORHANDLER = {CALLBACK eps, LEVELS 0}',
        'S.ERRORHANDLERS = eps',
        'S.EVENTS = [OUTPUT ($ptascii("U|"))]',
        'S_pop = S[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        '$identity_read_discard(S_pop, perrorcall.RESUME) = S_pop',
        'S_discard = $error_handler_restore(S_pop, perrorcall.CALLBACK)',
        'S_discard = S_pop[.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)]',
        '~$error_handler_eligible(S_discard, 2)',
        '$key_read_valid(S_discard, pkeyread)',
        '$string_read_cv_receipt(pkeyread)',
        '$string_read_cv_plan(S_discard, pkeyread) = (pstringread)',
        'pstringread = {READ pkeyread, BASECELL eps, KEYCELL eps, PHASE STRING_CAST}',
        '$string_read_cv_source(S_discard, pstringread)',
        '$origin_child((pkeyread.SITE), [PCFIELD 0]) = (porigin_base)',
        '$compiled_read(S_discard, porigin_base) = eps',
        'n_base_locator? = (n_base)',
        '$string_read_base_capture(S_discard, VARIABLE n_base_name* z_base) = ((pvalue_current, n_base_locator?))',
        'pvalue_current =/= pkeyread.BASE',
        '$string_read_key_current(S_discard, pstringread) = (PINT 8)',
        '$string_read_current_offset(S_discard, pstringread, PINT 8) = (8)',
        '~$string_read_in_range(pkeyread.BASE, 8)',
        '$string_read_in_range(pvalue_current, 8)',
        'H = $heap_graph(S)',
        'H.NODES = [HARRAY n_trace, HOBJECT n_exception, HCELL n_supplied, HCELL n_dst, HCELL n_base, HCELL n_key]',
        'H.ROOTS = [HCELL n_key, HCELL n_base, HCELL n_dst, HCELL n_supplied, HOBJECT n_exception]',
        'H.EDGES = H_before.EDGES',
        'H.DEBTS = eps',
        '$heap_owners(H, HOBJECT n_exception) = 2',
        '$heap_owners(H, HARRAY n_trace) = 1',
        '$heap_owners(H, HCELL n_base) = 1',
        '$heap_owners(H, HCELL n_key) = 1',
        '$heap_graph(S_discard) = H',
        '$task_nodes(KEY_READ_RESULT pkeyread) = eps',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        'pevent_cast = DIAGNOSTIC "Warning" ($ptascii("String offset cast occurred")) 18',
        'pevent_bounds = DIAGNOSTIC "Warning" ($ptascii("Uninitialized string offset 8")) 18',
        'S_expected = S_discard[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast, pevent_bounds]]',
        'PhpStep: S ~> S_after',
        'S_after = S_expected',
        '$error_read_discard(S_discard, perrorcall.RESUME) = S_expected',
        '$heap_graph(S_after) = H',
        '$heap_valid(H_before)',
        *guards('S_after'),
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 1) = S_expected[.COMPLETION = BUDGET]',
        '$drive_steps(S_expected, 1) = $drive_steps(S, 2)',
    ]
    derived_start = len(checks)
    checks += [
        # Neither a retired slot's bytes nor the current base authenticates history.
        'S_old_erased = S_discard[.STORE[n_original] = DEFINED (PINT 77)]',
        '$string_read_cv_source(S_old_erased, pstringread)',
        '$error_read_discard(S_old_erased, perrorcall.RESUME) = S_old_erased[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast, pevent_bounds]]',
        'S_no_base = S_discard[.ENV = $unbind(S_discard.ENV, n_base_name*)]',
        '$string_read_base_capture(S_no_base, VARIABLE n_base_name* z_base) = eps',
        '$string_read_cv_source(S_no_base, pstringread)',
        '$error_read_discard(S_no_base, perrorcall.RESUME) = S_no_base[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast, pevent_bounds]]',
        'S_current_integer = S_discard[.STORE[n_base] = DEFINED (PINT 99)]',
        '$error_read_discard(S_current_integer, perrorcall.RESUME) = S_current_integer[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast, pevent_bounds]]',
        'S_in_range = S_discard[.STORE[n_key] = DEFINED (PINT 1)]',
        '$error_read_discard(S_in_range, perrorcall.RESUME) = S_in_range[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast]]',
        'S_missing = S_discard[.ENV = $unbind(S_discard.ENV, pkeyread.NAME)]',
        '$error_read_discard(S_missing, perrorcall.RESUME) = S_missing[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast]]',
        'S_eligible = S_discard[.ERRORHANDLER.LEVELS = 2]',
        '$error_read_discard(S_eligible, perrorcall.RESUME) = S_eligible[.ERRORFATALTRACE = eps]',
        'S_return = S_discard[.TODO = (RETURN_UNWIND (KNOWN PNULL) eps) :: ptask_tail*]',
        '$string_read_cv_plan(S_return, pkeyread) = (pstringread)',
        '$error_read_discard(S_return, perrorcall.RESUME) = S_return',
        'S_no_pools = S_discard[.POOLS = eps]',
        '$string_read_cv_source(S_no_pools, pstringread)',
        '$string_read_cv_plan(S_no_pools, pkeyread) = (pstringread)',
        '$error_read_discard(S_no_pools, perrorcall.RESUME) = S_no_pools[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast, pevent_bounds]]',
        '~$string_read_cv_source(S_discard, pstringread[.BASECELL = (n_original)])',
        '~$string_read_cv_source(S_discard, pstringread[.KEYCELL = (n_key)])',
    ]
    for field in ('ORIGIN', 'SOURCES', 'CODE'):
        state = 'S_no_' + field.lower()
        checks += [state + ' = S_discard[.' + field + ' = eps]',
                   '$string_read_cv_plan(' + state + ', pkeyread) = eps',
                   '$error_read_discard(' + state + ', perrorcall.RESUME) = ' + state]
    for record in (
        'pkeyread[.GLOBAL = true]',
        'pkeyread[.MODE = KEY_IS]',
        'pkeyread[.PHASE = KEY_NULL]',
        'pkeyread[.VALUE = PINT 0]',
        'pkeyread[.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)]',
        'pkeyread[.OWNERS = BASE_VALUE pkeyread.INPUT]',
        'pkeyread[.BASE = PSTRING_CARRIER INTERNED_STRING ([97, 0, 99])]',
    ):
        checks.append('$error_read_discard(S_discard, KEY_READ_RESULT (' + record + ')) = S_discard')
    derived_count = len(checks) - derived_start
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), derived_count)
