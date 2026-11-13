"""Preserve a retired VARIABLE base header through supplied-throw discard."""
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
        'pkeyread.INPUT = VARIABLE pkeyread.NAME 18',
        'pkeyread.LINE = 18',
        'pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abcde"))',
        'pkeyread.OWNERS = BASE_VALUE (VARIABLE n_base_name* z_base)',
        'n_base_name* = $ptascii("base")',
        '$lookup(S.ENV, n_base_name*) = (n_base)',
        'S.STORE[n_base] = DEFINED (PINT 99)',
        '$call_reference_operand_valid(S, REFERENCE n_base)',
        '$string_read_base_capture(S, VARIABLE n_base_name* z_base) = eps',
        # Historical STORE bytes do not keep the former base cell alive.
        'S.STORE[0] = DEFINED pkeyread.BASE',
        '~((HCELL 0) <- S.ALLOCATIONS)',
        '$lookup(S.ENV, pkeyread.NAME) = (n_key)',
        'S.STORE[n_key] = DEFINED (PINT 4)',
        '~(n_key <- S.REFCELLS)',
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
        '$string_read_cv_source(S_discard, pstringread)',
        '$origin_child((pkeyread.SITE), [PCFIELD 0]) = (porigin_base)',
        '$compiled_read(S_discard, porigin_base) = eps',
        '$string_read_key_current(S_discard, pstringread) = (PINT 4)',
        '$string_read_current_offset(S_discard, pstringread, PINT 4) = (4)',
        '$string_read_in_range(pkeyread.BASE, 4)',
        'H = $heap_graph(S)',
        '~((HCELL 0) <- H.NODES)',
        '$heap_owners(H, HCELL n_base) = 1',
        '$heap_owners(H, HCELL n_key) = 1',
        '$heap_owners(H, HCELL n_dst) = 1',
        '$heap_owners(H, HCELL n_supplied) = 1',
        '$heap_owners(H, HOBJECT n_exception) = 2',
        '$heap_graph(S_discard) = H',
        '$task_nodes(KEY_READ_RESULT pkeyread) = eps',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
        'pevent_cast = DIAGNOSTIC "Warning" ($ptascii("String offset cast occurred")) 18',
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
        ('null', 'PNULL'),
        ('false', 'PBOOL false'),
        ('fraction', 'PFLOAT 4609434218613702656'),
        ('text', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("2tail"))'),
    ):
        state = 'S_' + name
        checks += [state + ' = S_discard[.STORE[n_key] = DEFINED (' + value + ')]',
                   '$error_read_discard(' + state + ', perrorcall.RESUME) = ' + state + '[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast]]',
                   '$error_read_discard(' + state + '[.REFCELLS = n_key :: ' + state + '.REFCELLS], perrorcall.RESUME) = ' + state + '[.REFCELLS = n_key :: ' + state + '.REFCELLS][.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast]]']
    checks += [
        'S_no_base = S_discard[.ENV = $unbind(S_discard.ENV, n_base_name*)]',
        '$string_read_cv_source(S_no_base, pstringread)',
        '$error_read_discard(S_no_base, perrorcall.RESUME) = S_no_base[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast]]',
        'S_no_key = S_discard[.ENV = $unbind(S_discard.ENV, pkeyread.NAME)]',
        '$string_read_cv_key(S_no_key, pkeyread) = (PNULL)',
        '$error_read_discard(S_no_key, perrorcall.RESUME) = S_no_key[.ERRORFATALTRACE = eps][.EVENTS = S.EVENTS ++ [pevent_cast]]',
        'n_identity = |S_discard.STRINGDATA|',
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("2tail"))',
        'S_request = S_discard[.STRINGDATA = S_discard.STRINGDATA ++ [$ptascii("2tail")]][.STORE[n_key] = DEFINED pvalue_request]',
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
    for field in ('ORIGIN', 'SOURCES', 'CODE'):
        state = 'S_no_' + field.lower()
        checks += [state + ' = S_discard[.' + field + ' = eps]',
                   '$string_read_cv_plan(' + state + ', pkeyread) = eps',
                   '$error_read_discard(' + state + ', perrorcall.RESUME) = ' + state]
    for read in (
        'pkeyread[.MODE = KEY_IS]',
        'pkeyread[.PHASE = KEY_NULL]',
        'pkeyread[.OWNERS = BASE_VALUE pkeyread.INPUT]',
        'pkeyread[.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)]',
        'pkeyread[.BASE = PSTRING_CARRIER INTERNED_STRING ([97, 0, 99])]',
    ):
        checks.append('$error_read_discard(S_discard, KEY_READ_RESULT (' + read + ')) = S_discard')
    derived_count = len(checks) - derived_start
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), derived_count)
