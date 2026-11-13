"""Retain the saved REQUEST header at both undefined-key callback boundaries."""
import json

from string_offset_undefined_cv_review import HELPERS, guards, seek


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 0, 'S_key') + [
        'S_key.TODO = (KEY_READ_RESULT pkeyread) :: ptask_tail*',
        r'S_key.CURRENT = eps /\ S_key.FRAMES = eps',
        r'pkeyread.PHASE = KEY_CV /\ pkeyread.VALUE = PNULL',
        'pkeyread.NAME = $ptascii("missing")',
        'pkeyread.INPUT = VARIABLE pkeyread.NAME 21',
        'pkeyread.LINE = 21',
        'pkeyread.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abcde"))',
        'pkeyread.OWNERS = BASE_VALUE (VARIABLE n_base_name* z_base)',
        'n_base_name* = $ptascii("base")',
        '$lookup(S_key.ENV, n_base_name*) = (n_base)',
        'S_key.STORE[n_base] = DEFINED (PINT 99)',
        '$call_reference_operand_valid(S_key, REFERENCE n_base)',
        '$string_read_base_capture(S_key, VARIABLE n_base_name* z_base) = eps',
        'S_key.STORE[2] = DEFINED pkeyread.BASE',
        '~((HCELL 2) <- S_key.ALLOCATIONS)',
        '$lookup(S_key.ENV, $ptascii("keeper")) = (n_keeper)',
        'S_key.STORE[n_keeper] = DEFINED pkeyread.BASE',
        '~(n_keeper <- S_key.REFCELLS)',
        '$string_read_cell(S_key, n_keeper)',
        '$lookup(S_key.ENV, pkeyread.NAME) = (n_key)',
        'S_key.STORE[n_key] = DEFINED (PINT 0)',
        '~(n_key <- S_key.REFCELLS)',
        '$lookup(S_key.ENV, $ptascii("left")) = (n_left)',
        '$lookup(S_key.ENV, $ptascii("right")) = (n_right)',
        'S_key.STRINGDATA = [$ptascii("abcde")]',
        '$key_read_valid(S_key, pkeyread)',
        '$string_read_cv_request(pkeyread)',
        '$string_read_cv_receipt(pkeyread)',
        '$string_read_cv_plan(S_key, pkeyread) = (pstringread)',
        'pstringread = {READ pkeyread, BASECELL eps, KEYCELL eps, KEYREF false, PHASE STRING_CAST}',
        '$string_read_cv_source(S_key, pstringread)',
        '$string_read_retainer(S_key, pstringread, BIND ($ptascii("keeper")) n_keeper)',
        '$string_read_retained(S_key, pstringread, S_key.ENV)',
        '$string_read_provider_ready(S_key, pstringread)',
        '$string_read_key_current(S_key, pstringread) = (PINT 0)',
        'H = $heap_graph(S_key)',
        'H.NODES = [HCELL n_left, HCELL n_right, HCELL n_keeper, HCELL n_base, HCELL n_key]',
        'H.ROOTS = [HCELL n_key, HCELL n_base, HCELL n_keeper, HCELL n_right, HCELL n_left]',
        r'H.EDGES = eps /\ H.DEBTS = eps',
        '$heap_owners(H, HCELL n_keeper) = 1',
        '$task_nodes(KEY_READ_RESULT pkeyread) = eps',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S_key'),
        'S_key.ERRORHANDLER.CALLBACK = (pvalue_handler)',
        'perrorcall_cast = {SITE pkeyread.SITE, LEVEL 2, MESSAGE ($ptascii("String offset cast occurred")), LINE 21, EVENT (DIAGNOSTIC "Warning" ($ptascii("String offset cast occurred")) 21), CALLBACK pvalue_handler, TARGET eps, RESUME (STRING_READ_RESULT pstringread)}',
        'PhpStep: S_key ~> S_dispatch',
        'S_dispatch = S_key[.TODO = (ERROR_HANDLER_INVOKE perrorcall_cast) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.ERRORFATALTRACE = eps]',
        '$heap_graph(S_dispatch) = H',
    ] + seek('S_dispatch', 1, 'S') + [
        'S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        '$lookup(S.ENV, pkeyread.NAME) = (n_key)',
        'S.STORE[n_key] = DEFINED (PINT 4)',
        'S.STORE[n_base] = DEFINED (PINT 99)',
        'S.STORE[n_keeper] = DEFINED pkeyread.BASE',
        '$string_read_source(S, pstringread)',
        '$string_read_provider_ready(S, pstringread)',
        '$string_read_key_current(S, pstringread) = (PINT 4)',
        '$string_read_current_offset(S, pstringread, PINT 4) = (4)',
        '$heap_graph(S) = H',
        'S_byte = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([101]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'PhpStep: S ~> S_after',
        'S_after = S_byte',
        '$heap_graph(S_after) = H',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 1) = S_byte[.COMPLETION = BUDGET]',
        *guards('S_after'),
    ]
    derived_start = len(checks)
    checks += [
        # Initial admission and post-CAST readiness both need a real current owner.
        'S_early_lost = S_key[.ENV = $unbind(S_key.ENV, $ptascii("keeper"))]',
        '$string_read_cv_source(S_early_lost, pstringread)',
        '~$string_read_retained(S_early_lost, pstringread, S_early_lost.ENV)',
        '$string_read_cv_plan(S_early_lost, pkeyread) = eps',
        'S_lost = S[.ENV = $unbind(S.ENV, $ptascii("keeper"))]',
        '$string_read_source(S_lost, pstringread)',
        '~$string_read_provider_ready(S_lost, pstringread)',
        'PhpStep: S_lost ~> S_lost_after',
        'S_lost_after = S_lost[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]',
        'S_marked = S_key[.REFCELLS = n_keeper :: S_key.REFCELLS]',
        '$string_read_cv_source(S_marked, pstringread)',
        '$string_read_cv_plan(S_marked, pkeyread) = eps',
        'pvalue_twin = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("abcde"))',
        'S_twin = S_key[.STRINGDATA = S_key.STRINGDATA ++ [$ptascii("abcde")]][.STORE[n_keeper] = DEFINED pvalue_twin]',
        '$string_carrier_valid(S_twin, pvalue_twin)',
        '$string_read_cv_source(S_twin, pstringread)',
        '$string_read_cv_plan(S_twin, pkeyread) = eps',
        'S_no_base = S[.ENV = $unbind(S.ENV, n_base_name*)]',
        '$string_read_source(S_no_base, pstringread)',
        '$string_read_provider_ready(S_no_base, pstringread)',
        '$string_read_resume(S_no_base, pstringread) = S_no_base[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([101]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    for name, value, byte in (
        ('false', 'PBOOL false', 97),
        ('fraction', 'PFLOAT 4609434218613702656', 98),
        ('text', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("2tail"))', 99),
    ):
        state = 'S_' + name
        checks += [state + ' = S[.STORE[n_key] = DEFINED (' + value + ')]',
                   '$string_read_resume(' + state + ', pstringread) = ' + state + '[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([' + str(byte) + ']))][.BASE = BASE_VALUE (KNOWN PNULL)]']
    checks += [
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("2tail"))',
        'S_request = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("2tail")]][.STORE[n_key] = DEFINED pvalue_request]',
        '$string_read_cv_key(S_request, pkeyread) = (pvalue_request)',
        '$string_read_resume(S_request, pstringread) = S_request[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'n_array = |S.ARRAYS|',
        'S_allocated = $allocate_array(S, $array_empty())',
        'S_array = S_allocated[.RESULT = S.RESULT][.STORE[n_key] = DEFINED (PARRAY n_array)]',
        '$string_read_cv_key(S_array, pkeyread) = (PARRAY n_array)',
        '$string_read_resume(S_array, pstringread) = S_array[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_nonempty = S_array[.ARRAYS[n_array] = $array_insert($array_empty(), KINT 0, DIRECT (PBOOL false))]',
        '$string_read_resume(S_nonempty, pstringread) = S_nonempty[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '~$string_read_cv_request(pkeyread[.PHASE = KEY_NULL])',
        '~$string_read_cv_request(pkeyread[.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)])',
        '~$string_read_cv_source(S, pstringread[.BASECELL = (n_base)])',
        '~$string_read_cv_source(S, pstringread[.KEYCELL = (n_key)])',
    ]
    for field in ('ORIGIN', 'SOURCES', 'CODE', 'STRINGDATA'):
        checks.append('~$string_read_cv_source(S[.' + field + ' = eps], pstringread)')
    derived_count = len(checks) - derived_start
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), derived_count)
