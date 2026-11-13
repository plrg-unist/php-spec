"""Keep the supplied Throwable while mandatory cast/bounds diagnostics complete."""
import json

HELPERS = r'''
dec $undefined_throw_peer_front(pstate) : bool
def $undefined_throw_peer_front(S) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = KEY_READ_RESULT pkeyread
  -- if pkeyread.PHASE = KEY_CV
def $undefined_throw_peer_front(S) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask*
  -- if perrorcall.RESUME = STRING_READ_RESULT pstringread
  -- if pstringread.READ.PHASE = KEY_NULL
def $undefined_throw_peer_front(S) = false -- otherwise
dec $undefined_throw_peer_seek(pstate, nat) : pstate
def $undefined_throw_peer_seek(S, n) = S -- if $undefined_throw_peer_front(S)
def $undefined_throw_peer_seek(S, n) = S
  -- if ~$undefined_throw_peer_front(S)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $undefined_throw_peer_seek(S, 0) = S
  -- if ~$undefined_throw_peer_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $undefined_throw_peer_seek(S, n) = $undefined_throw_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$undefined_throw_peer_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def render(program, filename_b64, control_program, control_filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $undefined_throw_peer_seek(S_initial, 1000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = KEY_READ_RESULT pkeyread',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        r'pkeyread.PHASE = KEY_CV /\ pkeyread.VALUE = PNULL',
        'pkeyread.NAME = $ptascii("key")',
        'pkeyread.INPUT = VARIABLE pkeyread.NAME 13',
        r'pkeyread.LINE = 13 /\ pkeyread.KEY = KSTRING eps',
        'pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))',
        'pkeyread.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)',
        '$lookup(S.ENV, pkeyread.NAME) = (n_key)',
        'S.STORE[n_key] = DEFINED (PINT 8)',
        '$lookup(S.ENV, $ptascii("dst")) = (n_dst)',
        'S.STORE[n_dst] = DEFINED (PINT 99)',
        '$lookup(S.ENV, $ptascii("supplied")) = (n_supplied)',
        'S.STORE[n_supplied] = DEFINED (POBJECT n_exception)',
        '$throwable_member(S, n_exception)',
        'S.REFCELLS = [n_supplied, n_key]',
        'S.ERRORHANDLER = {CALLBACK eps, LEVELS 0}',
        'S.ERRORHANDLERS = eps',
        'S.EVENTS = [OUTPUT ($ptascii("U|"))]',
        'S_pop = S[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        '$identity_read_discard(S_pop, perrorcall.RESUME) = S_pop',
        'S_discard = $error_handler_restore(S_pop, perrorcall.CALLBACK)',
        'S_discard = S_pop[.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)]',
        'S_discard.ERRORHANDLER.LEVELS = 0',
        '~$error_handler_eligible(S_discard, 2)',
        '$key_read_valid(S_discard, pkeyread)',
        '$string_read_cv_plan(S_discard, pkeyread) = (pstringread)',
        'pstringread = {READ pkeyread, BASECELL eps, KEYCELL eps, PHASE STRING_CAST}',
        '$string_read_cv_source(S_discard, pstringread)',
        '$string_read_key_current(S_discard, pstringread) = (PINT 8)',
        '$string_read_current_offset(S_discard, pstringread, PINT 8) = (8)',
        '~$string_read_in_range(pkeyread.BASE, 8)',
        'H = $heap_graph(S)',
        'H.NODES = [HARRAY n_trace, HOBJECT n_exception, HCELL n_supplied, HCELL n_dst, HCELL n_key]',
        'H.EDGES = [HEDGE (HOBJECT n_exception) (HARRAY n_trace), HEDGE (HCELL n_supplied) (HOBJECT n_exception)]',
        'H.ROOTS = [HCELL n_key, HCELL n_dst, HCELL n_supplied, HOBJECT n_exception]',
        'H.DEBTS = eps',
        '$heap_owners(H, HOBJECT n_exception) = 2',
        '$heap_owners(H, HARRAY n_trace) = 1',
        '$heap_owners(H, HCELL n_key) = 1',
        '$heap_owners(H, HCELL n_supplied) = 1',
        '$heap_owners(H, HCELL n_dst) = 1',
        '$heap_graph(S_discard) = H',
        '$task_nodes(KEY_READ_RESULT pkeyread) = eps',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        'pevent_cast = DIAGNOSTIC "Warning" ($ptascii("String offset cast occurred")) 13',
        'pevent_bounds = DIAGNOSTIC "Warning" ($ptascii("Uninitialized string offset 8")) 13',
        'S_expected = S_discard[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast, pevent_bounds]]',
        'PhpStep: S ~> S_after',
        'S_after = S_expected',
        '$error_read_discard(S_discard, perrorcall.RESUME) = S_expected',
        '$heap_graph(S_after) = H',
        '$call_current_valid(S_after)',
        '$call_frames_valid(S_after, S_after.FRAMES)',
        '$call_descriptors_valid(S_after)',
        '$heap_valid(H)',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 1) = S_expected[.COMPLETION = BUDGET]',
        '$drive_steps(S_expected, 1) = $drive_steps(S, 2)',
    ]
    derived_start = len(checks)
    checks += [
        # A pending exception prevents an eligible callback from being invoked.
        'S_eligible = S_discard[.ERRORHANDLER.LEVELS = 2]',
        '$error_handler_eligible(S_eligible, 2)',
        '$error_read_discard(S_eligible, perrorcall.RESUME) = S_eligible[.ERRORFATALTRACE = eps]',
        # An absent callback still permits both default warnings with mask2.
        'S_absent_handler = S_eligible[.ERRORHANDLER.CALLBACK = eps]',
        '~$error_handler_eligible(S_absent_handler, 2)',
        '$error_read_discard(S_absent_handler, perrorcall.RESUME) = S_absent_handler[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast, pevent_bounds]]',
        # This admission adds no path for return, exit or other task prefixes.
        'S_no_pending = S_discard[.TODO = ptask_tail*]',
        '$error_read_discard(S_no_pending, perrorcall.RESUME) = S_no_pending',
        'S_hidden = S_discard[.REPORTING = 0]',
        '$error_read_discard(S_hidden, perrorcall.RESUME) = S_hidden[.ERRORFATALTRACE = eps]',
        # Conversion uses the current key, with no destination write or owner.
        'S_in_range = S_discard[.STORE[n_key] = DEFINED (PINT 1)]',
        '$error_read_discard(S_in_range, perrorcall.RESUME) = S_in_range[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast]]',
        'S_negative = S_discard[.STORE[n_key] = DEFINED (PINT (-1))]',
        '$error_read_discard(S_negative, perrorcall.RESUME) = S_negative[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast]]',
        'S_missing = S_discard[.ENV = $unbind(S_discard.ENV, pkeyread.NAME)]',
        '$string_read_cv_key(S_missing, pkeyread) = (PNULL)',
        '$error_read_discard(S_missing, perrorcall.RESUME) = S_missing[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast]]',
        'S_undefined = S_discard[.STORE[n_key] = UNDEFINED]',
        '$string_read_cv_key(S_undefined, pkeyread) = eps',
        '$error_read_discard(S_undefined, perrorcall.RESUME) = S_undefined[.EVENTS = S.EVENTS ++ [pevent_cast]][.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]',
    ]
    for field in ('ORIGIN', 'SOURCES', 'CODE', 'POOLS'):
        state = 'S_no_' + field.lower()
        checks += [state + ' = S_discard[.' + field + ' = eps]',
                   '$string_read_cv_plan(' + state + ', pkeyread) = eps',
                   '$error_read_discard(' + state + ', perrorcall.RESUME) = ' + state]
    for record in (
        'pkeyread[.GLOBAL = true]',
        'pkeyread[.MODE = KEY_IS]',
        'pkeyread[.PHASE = KEY_NULL]',
        'pkeyread[.VALUE = PINT 0]',
        'pkeyread[.OWNERS = BASE_VALUE pkeyread.INPUT]',
        'pkeyread[.BASE = PSTRING ($ptascii("abc"))]',
        'pkeyread[.BASE = PSTRING_CARRIER INTERNED_STRING ([97, 0, 99])]',
    ):
        checks.append('$error_read_discard(S_discard, KEY_READ_RESULT (' + record + ')) = S_discard')
    # A fresh literal-true source reaches a genuine old KEY_NULL history. Its
    # generic plan succeeds, so this control discriminates the explicit receipt.
    checks += [
        'S_control_initial = $php_run(' + control_program + ', 0, ' + json.dumps(control_filename_b64) + ')',
        'S_control_initial.COMPLETION = BUDGET',
        'S_control_found = $undefined_throw_peer_seek(S_control_initial, 1000)',
        r'S_control_found.COMPLETION = NORMAL \/ S_control_found.COMPLETION = BUDGET',
        'S_control = S_control_found[.COMPLETION = NORMAL]',
        'S_control.TODO = (THROW_SEARCH n_control) :: (ERROR_HANDLER_RESULT perrorcall_control) :: ptask_control*',
        'perrorcall_control.RESUME = STRING_READ_RESULT pstringread_control',
        'pstringread_control.PHASE = STRING_CAST',
        'pstringread_control.READ.PHASE = KEY_NULL',
        'pstringread_control.READ.NAME = eps',
        'pstringread_control.READ.INPUT = KNOWN (PBOOL true)',
        'pstringread_control.READ.VALUE = PBOOL true',
        'pstringread_control.READ.OWNERS = BASE_VALUE (KNOWN pstringread_control.READ.BASE)',
        r'pstringread_control.BASECELL = eps /\ pstringread_control.KEYCELL = eps',
        'S_control_pop = S_control[.TODO = (THROW_SEARCH n_control) :: ptask_control*]',
        'S_control_restore = $error_handler_restore($identity_read_discard(S_control_pop, perrorcall_control.RESUME), perrorcall_control.CALLBACK)',
        '$string_read_source(S_control_restore, pstringread_control)',
        '$string_read_cv_plan(S_control_restore, pstringread_control.READ) = (pstringread_control)',
        '~$string_read_cv_receipt(pstringread_control.READ)',
        '$error_read_discard(S_control_restore, KEY_READ_RESULT pstringread_control.READ) = S_control_restore',
        '$error_read_discard(S_control_restore, perrorcall_control.RESUME) = S_control_restore[.ERRORFATALTRACE = eps]',
        'PhpStep: S_control ~> S_control_after',
        'S_control_after = S_control_restore[.ERRORFATALTRACE = eps]',
        '$heap_graph(S_control_after) = $heap_graph(S_control)',
    ]
    derived_count = len(checks) - derived_start
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), derived_count)
