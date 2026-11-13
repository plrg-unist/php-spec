"""Read the saved interned header while both current CV payloads change."""
import json

from string_offset_undefined_cv_review import HELPERS, guards, seek


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 0, 'S') + [
        'S.TODO = (KEY_READ_RESULT pkeyread) :: ptask_tail*',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        r'pkeyread.PHASE = KEY_CV /\ pkeyread.VALUE = PNULL',
        'pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))',
        'pkeyread.OWNERS = BASE_VALUE (VARIABLE n_base_name* z_base)',
        'n_base_name* = $ptascii("base")',
        '$lookup(S.ENV, n_base_name*) = (n_base)',
        'n_base <- S.REFCELLS',
        'pvalue_now = PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ"))',
        'S.STORE[n_base] = DEFINED pvalue_now',
        'n_locator? = (n_base)',
        '$string_read_base_capture(S, VARIABLE n_base_name* z_base) = ((pvalue_now, n_locator?))',
        'pvalue_now =/= pkeyread.BASE',
        '$lookup(S.ENV, pkeyread.NAME) = (n_key)',
        'S.STORE[n_key] = DEFINED (PINT 1)',
        '~(n_key <- S.REFCELLS)',
        '$key_read_valid(S, pkeyread)',
        '$string_read_cv_receipt(pkeyread)',
        '$string_read_cv_plan(S, pkeyread) = (pstringread)',
        'pstringread = {READ pkeyread, BASECELL eps, KEYCELL eps, KEYREF false, PHASE STRING_CAST}',
        '$string_read_cv_source(S, pstringread)',
        '$string_read_source(S, pstringread)',
        '$string_read_key_current(S, pstringread) = (PINT 1)',
        '$string_read_ready(S, pstringread)',
        '$task_nodes(KEY_READ_RESULT pkeyread) = eps',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        'H = $heap_graph(S)',
        *guards('S'),
        'S.ERRORHANDLER.CALLBACK = (pvalue_handler)',
        'perrorcall_cast = {SITE pkeyread.SITE, LEVEL 2, MESSAGE ($ptascii("String offset cast occurred")), LINE pkeyread.LINE, EVENT (DIAGNOSTIC "Warning" ($ptascii("String offset cast occurred")) pkeyread.LINE), CALLBACK pvalue_handler, TARGET eps, RESUME (STRING_READ_RESULT pstringread)}',
        'PhpStep: S ~> S_dispatch',
        'S_dispatch = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall_cast) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.ERRORFATALTRACE = eps]',
        '$error_call_valid(S_dispatch, perrorcall_cast)',
        '$heap_graph(S_dispatch) = H',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 1) = S_dispatch[.COMPLETION = BUDGET]',
        *guards('S_dispatch'),
    ] + seek('S_dispatch', 1, 'S_cast') + [
        'S_cast.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*',
        r'S_cast.CURRENT = eps /\ S_cast.FRAMES = eps',
        'S_cast.STORE[n_base] = DEFINED pvalue_now',
        '$lookup(S_cast.ENV, pkeyread.NAME) = (n_key)',
        'pvalue_current = PSTRING_CARRIER INTERNED_STRING ($ptascii("2tail"))',
        'S_cast.STORE[n_key] = DEFINED pvalue_current',
        '$call_reference_operand_valid(S_cast, REFERENCE n_key)',
        '$string_read_source(S_cast, pstringread)',
        '$string_read_provider_ready(S_cast, pstringread)',
        '$string_read_cv_key(S_cast, pkeyread) = (pvalue_current)',
        '$string_read_current_offset(S_cast, pstringread, pvalue_current) = (2)',
        '$string_read_offset(pvalue_current) = eps',
        'H_cast = $heap_graph(S_cast)',
        *guards('S_cast'),
    ]
    derived_start = len(checks)
    # Both ordinary and marked current cells retain the existing primitive domain.
    for ordinary in (False, True):
        for name, value, offset in (
            ('null', 'PNULL', 0), ('false', 'PBOOL false', 0),
            ('true', 'PBOOL true', 1), ('negative', 'PINT (-1)', -1),
            ('fraction', 'PFLOAT 4609434218613702656', 1),
        ):
            state = 'S_' + ('ordinary_' if ordinary else 'marked_') + name
            checks += [state + ' = S_cast[.STORE[n_key] = DEFINED (' + value + ')]' +
                       ('[.REFCELLS = eps]' if ordinary else ''),
                       '$string_read_cv_key(' + state + ', pkeyread) = (' + value + ')',
                       '$string_read_current_offset(' + state + ', pstringread, ' + value + ') = (' + str(offset) + ')']
    checks += [
        # The exact current REQUEST identity is required, even with equal bytes.
        'n_identity = |S_cast.STRINGDATA|',
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("noise"))',
        'S_registry = S_cast[.STRINGDATA = S_cast.STRINGDATA ++ [$ptascii("noise")]]',
        '$string_read_current_offset(S_registry, pstringread, pvalue_request) = eps',
        'S_request = S_registry[.STORE[n_key] = DEFINED pvalue_request]',
        '$string_read_cv_key(S_request, pkeyread) = (pvalue_request)',
        '$string_read_current_offset(S_request, pstringread, pvalue_request) = (0)',
        'S_request_plain = S_request[.REFCELLS = eps]',
        '$string_read_cv_key(S_request_plain, pkeyread) = (pvalue_request)',
        'pvalue_twin = PSTRING_CARRIER (REQUEST_STRING (|S_request.STRINGDATA|)) ($ptascii("noise"))',
        'S_twin = S_request[.STRINGDATA = S_request.STRINGDATA ++ [$ptascii("noise")]]',
        '$string_carrier_valid(S_twin, pvalue_twin)',
        '$string_read_current_offset(S_twin, pstringread, pvalue_twin) = eps',
        # No new primitive/string distinction restricts current ARRAY conversion.
        'n_array = |S_cast.ARRAYS|',
        'S_allocated = $allocate_array(S_cast, $array_empty())',
        'S_array = S_allocated[.RESULT = S_cast.RESULT][.STORE[n_key] = DEFINED (PARRAY n_array)]',
        '$string_read_cv_key(S_array, pkeyread) = (PARRAY n_array)',
        '$string_read_current_offset(S_array, pstringread, PARRAY n_array) = (0)',
        'S_nonempty = S_array[.ARRAYS[n_array] = $array_insert($array_empty(), KINT 0, DIRECT (PBOOL false))]',
        '$string_read_cv_key(S_nonempty, pkeyread) = (PARRAY n_array)',
        '$string_read_current_offset(S_nonempty, pstringread, PARRAY n_array) = (1)',
        'S_array_plain = S_nonempty[.REFCELLS = eps]',
        '$string_read_cv_key(S_array_plain, pkeyread) = (PARRAY n_array)',
        r'$string_read_cv_receipt(pkeyread[.OWNERS = BASE_VALUE pkeyread.INPUT]) /\ ~$string_read_cv_source(S_cast, pstringread[.READ.OWNERS = BASE_VALUE pkeyread.INPUT])',
        # The immortal selected header survives disappearance of its former name.
        'S_no_base = S_cast[.ENV = $unbind(S_cast.ENV, n_base_name*)]',
        '$string_read_base_capture(S_no_base, VARIABLE n_base_name* z_base) = eps',
        '$string_read_source(S_no_base, pstringread)',
        '$string_read_ready(S_no_base, pstringread)',
        '$string_read_resume(S_no_base, pstringread) = S_no_base[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'pstringread_bounds = pstringread[.PHASE = STRING_BOUNDS 5]',
        '$string_read_source(S_no_base, pstringread_bounds)',
        '$string_read_resume(S_no_base, pstringread_bounds) = S_no_base[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING eps)][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    for record in (
        'pkeyread[.GLOBAL = true]', 'pkeyread[.MODE = KEY_IS]',
        'pkeyread[.PHASE = KEY_NULL][.NAME = eps]', 'pkeyread[.VALUE = PINT 1]',
        'pkeyread[.BASE = PSTRING ($ptascii("abc"))]',
        'pkeyread[.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))]',
    ):
        checks.append('~$string_read_cv_receipt(' + record + ')')
    for read in (
        'pstringread[.BASECELL = (n_base)]', 'pstringread[.KEYCELL = (n_key)]',
        'pstringread[.READ.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)]',
        'pstringread[.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("other")) z_base)]',
        'pstringread[.READ.OWNERS = BASE_VALUE (VARIABLE n_base_name* $(z_base + 1))]',
        'pstringread[.READ.BASE = PSTRING_CARRIER INTERNED_STRING ([97, 0, 99])]',
    ):
        checks.append('~$string_read_cv_source(S_cast, ' + read + ')')
    for field in ('ORIGIN', 'SOURCES', 'CODE'):
        checks.append('~$string_read_cv_source(S_cast[.' + field + ' = eps], pstringread)')
    derived_count = len(checks) - derived_start
    checks += [
        'PhpStep: S_cast ~> S_byte',
        'S_byte = S_cast[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$heap_graph(S_byte) = H_cast',
        '$drive_steps(S_cast, 0) = S_cast[.COMPLETION = BUDGET]',
        '$drive_steps(S_cast, 1) = S_byte[.COMPLETION = BUDGET]',
        *guards('S_byte'),
    ]
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), derived_count)
