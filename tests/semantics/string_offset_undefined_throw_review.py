"""Keep the supplied Throwable and destination through the mandatory cast."""
import json

from string_offset_undefined_cv_review import guards
from string_offset_undefined_throw_peer_review import HELPERS


def render(program, filename_b64):
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
        'pkeyread.LINE = 13',
        'pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))',
        'pkeyread.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)',
        '$lookup(S.ENV, pkeyread.NAME) = (n_key)',
        'S.STORE[n_key] = DEFINED (PINT 1)',
        '$call_reference_operand_valid(S, REFERENCE n_key)',
        '$lookup(S.ENV, $ptascii("dst")) = (n_dst)',
        'S.STORE[n_dst] = DEFINED (PINT 99)',
        '$lookup(S.ENV, $ptascii("supplied")) = (n_supplied)',
        'S.STORE[n_supplied] = DEFINED (POBJECT n_exception)',
        'S.OBJECTS[n_exception] = THROWABLE pthrowable',
        'S.ERRORHANDLER = {CALLBACK eps, LEVELS 0}',
        'S.ERRORHANDLERS = eps',
        'S.EVENTS = [OUTPUT ($ptascii("U|"))]',
        'S_pop = S[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        '$identity_read_discard(S_pop, perrorcall.RESUME) = S_pop',
        'S_discard = S_pop[.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)]',
        '$error_handler_restore(S_pop, perrorcall.CALLBACK) = S_discard',
        '~$error_handler_eligible(S_discard, 2)',
        '$key_read_valid(S_discard, pkeyread)',
        '$string_read_cv_receipt(pkeyread)',
        '$string_read_cv_plan(S_discard, pkeyread) = (pstringread)',
        'pstringread = {READ pkeyread, BASECELL eps, KEYCELL eps, KEYREF false, PHASE STRING_CAST}',
        '$string_read_key_current(S_discard, pstringread) = (PINT 1)',
        '$string_read_current_offset(S_discard, pstringread, PINT 1) = (1)',
        'H = $heap_graph(S)',
        '$heap_graph(S_discard) = H',
        '$task_nodes(KEY_READ_RESULT pkeyread) = eps',
        *guards('S'),
        'pevent_cast = DIAGNOSTIC "Warning" ($ptascii("String offset cast occurred")) 13',
        'S_expected = S_discard[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast]]',
        'PhpStep: S ~> S_after',
        'S_after = S_expected',
        '$error_read_discard(S_discard, perrorcall.RESUME) = S_expected',
        'S_after.OBJECTS[n_exception] = THROWABLE pthrowable',
        'S_after.STORE[n_dst] = DEFINED (PINT 99)',
        '$heap_graph(S_after) = H',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 1) = S_expected[.COMPLETION = BUDGET]',
        *guards('S_after'),
    ]
    derived_start = len(checks)
    for name, value in (
        ('false', 'PBOOL false'),
        ('fraction', 'PFLOAT 4609434218613702656'),
        ('text', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("2tail"))'),
    ):
        state = 'S_' + name
        checks += [state + ' = S_discard[.STORE[n_key] = DEFINED (' + value + ')]',
                   '$error_read_discard(' + state + ', perrorcall.RESUME) = ' + state + '[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast]]']
    checks += [
        'n_identity = |S_discard.STRINGDATA|',
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("noise"))',
        'S_request = S_discard[.STRINGDATA = S_discard.STRINGDATA ++ [$ptascii("noise")]][.STORE[n_key] = DEFINED pvalue_request]',
        '$string_read_cv_key(S_request, pkeyread) = (pvalue_request)',
        '$error_read_discard(S_request, perrorcall.RESUME) = S_request[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast]]',
        'n_array = |S_discard.ARRAYS|',
        'S_allocated = $allocate_array(S_discard, $array_empty())',
        'S_array = S_allocated[.RESULT = S_discard.RESULT][.STORE[n_key] = DEFINED (PARRAY n_array)]',
        '$string_read_cv_key(S_array, pkeyread) = (PARRAY n_array)',
        '$error_read_discard(S_array, perrorcall.RESUME) = S_array[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast]]',
        'S_nonempty = S_array[.ARRAYS[n_array] = $array_insert($array_empty(), KINT 0, DIRECT (PBOOL false))]',
        '$string_read_current_offset(S_nonempty, pstringread, PARRAY n_array) = (1)',
        '$error_read_discard(S_nonempty, perrorcall.RESUME) = S_nonempty[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast]]',
        'S_eligible = S_discard[.ERRORHANDLER.LEVELS = 2]',
        '$error_read_discard(S_eligible, perrorcall.RESUME) = S_eligible[.ERRORFATALTRACE = eps]',
        'S_hidden = S_discard[.REPORTING = 0]',
        '$error_read_discard(S_hidden, perrorcall.RESUME) = S_hidden[.ERRORFATALTRACE = eps]',
        'S_return = S_discard[.TODO = (RETURN_UNWIND (KNOWN PNULL) eps) :: ptask_tail*]',
        '$string_read_cv_plan(S_return, pkeyread) = (pstringread)',
        '$error_read_discard(S_return, perrorcall.RESUME) = S_return',
    ]
    for field in ('ORIGIN', 'SOURCES', 'CODE', 'POOLS'):
        state = 'S_no_' + field.lower()
        checks += [state + ' = S_discard[.' + field + ' = eps]',
                   '$string_read_cv_plan(' + state + ', pkeyread) = eps',
                   '$error_read_discard(' + state + ', perrorcall.RESUME) = ' + state]
    for read in (
        'pkeyread[.MODE = KEY_IS]',
        'pkeyread[.OWNERS = BASE_VALUE pkeyread.INPUT]',
        'pkeyread[.BASE = PSTRING_CARRIER INTERNED_STRING ([97, 0, 99])]',
    ):
        checks.append('$error_read_discard(S_discard, KEY_READ_RESULT (' + read + ')) = S_discard')
    derived_count = len(checks) - derived_start
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), derived_count)
