"""Check a source-reached current string key through the delayed silent cast."""
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
        'pkeyread.NAME = $ptascii("missing")',
        'pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))',
        'pkeyread.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)',
        '$lookup(S.ENV, pkeyread.NAME) = (n_key)',
        'pvalue_first = PSTRING_CARRIER INTERNED_STRING ($ptascii("1"))',
        'S.STORE[n_key] = DEFINED pvalue_first',
        '~(n_key <- S.REFCELLS)',
        '$heap_owners($heap_graph(S), HCELL n_key) = 1',
        '$string_read_cv_plan(S, pkeyread) = (pstringread)',
        'pstringread = {READ pkeyread, BASECELL eps, KEYCELL eps, PHASE STRING_CAST}',
        '$string_read_source(S, pstringread)',
        '$string_read_cv_key(S, pkeyread) = (pvalue_first)',
        '$string_read_key_current(S, pstringread) = (pvalue_first)',
        '$string_read_current_offset(S, pstringread, pvalue_first) = (1)',
        '$string_read_offset(pvalue_first) = eps',
        '$string_read_ready(S, pstringread)',
        '$task_nodes(KEY_READ_RESULT pkeyread) = eps',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
        'PhpStep: S ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = STRING_READ_RESULT pstringread',
        'perrorcall.MESSAGE = $ptascii("String offset cast occurred")',
        '$error_call_valid(S_dispatch, perrorcall)',
        r'S_dispatch.STORE = S.STORE /\ S_dispatch.EVENTS = S.EVENTS',
        'S_dispatch.ALLOCATIONS = S.ALLOCATIONS',
        '$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = eps',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 1) = S_dispatch[.COMPLETION = BUDGET]',
        *guards('S_dispatch'),
    ] + seek('S_dispatch', 1, 'S_cast') + [
        'S_cast.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*',
        r'S_cast.CURRENT = eps /\ S_cast.FRAMES = eps',
        '$lookup(S_cast.ENV, pkeyread.NAME) = (n_key)',
        'pvalue_current = PSTRING_CARRIER INTERNED_STRING ($ptascii("2tail"))',
        'S_cast.STORE[n_key] = DEFINED pvalue_current',
        r'pstringread.READ.VALUE = PNULL /\ pstringread.READ.PHASE = KEY_CV',
        '$string_read_source(S_cast, pstringread)',
        '$string_read_key_current(S_cast, pstringread) = (pvalue_current)',
        '$string_read_current_offset(S_cast, pstringread, pvalue_current) = (2)',
        '$string_read_offset(pvalue_current) = eps',
        '$string_read_ready(S_cast, pstringread)',
        *guards('S_cast'),
    ]
    derived_start = len(checks)
    checks += [
        # Conversion/refusal controls derive from the genuine CAST frontier.
        '$string_read_current_offset(S_cast, pstringread, PSTRING_CARRIER INTERNED_STRING ($ptascii("noise"))) = (0)',
        '$string_read_current_offset(S_cast, pstringread, PSTRING_CARRIER INTERNED_STRING ($ptascii("2.75tail"))) = (2)',
        '$string_read_current_offset(S_cast, pstringread, PSTRING_CARRIER INTERNED_STRING ($ptascii("-2tail"))) = (-2)',
        '$string_read_current_offset(S_cast, pstringread, PSTRING_CARRIER INTERNED_STRING ($ptascii("9223372036854775808"))) = (9223372036854775807)',
        '$string_read_current_offset(S_cast, pstringread, PSTRING_CARRIER INTERNED_STRING ($ptascii("-18446744073709551616"))) = (-9223372036854775808)',
        '$string_read_current_offset(S_cast, pstringread, PSTRING ($ptascii("2tail"))) = eps',
        '$string_read_current_offset(S_cast, pstringread, PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("2tail"))) = eps',
        '$string_read_current_offset(S_cast, pstringread, PSTRING_CARRIER INTERNED_STRING ([50, 0, 120])) = eps',
        '$string_read_current_offset(S_cast, pstringread, PSTRING_CARRIER INTERNED_STRING ([256])) = eps',
        'pkeyread_plain = pkeyread[.PHASE = KEY_NULL][.NAME = eps]',
        '$string_read_current_offset(S_cast, pstringread[.READ = pkeyread_plain], pvalue_current) = eps',
        '$string_read_cv_key(S_cast[.REFCELLS = n_key :: S_cast.REFCELLS], pkeyread) = (pvalue_current)',
        '$string_read_cv_key(S_cast[.STORE[n_key] = DEFINED (PSTRING ($ptascii("2tail")))], pkeyread) = eps',
        'n_request = |S_cast.STRINGDATA|',
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_request) ($ptascii("2tail"))',
        'S_request = S_cast[.STRINGDATA = S_cast.STRINGDATA ++ [$ptascii("2tail")]][.STORE[n_key] = DEFINED pvalue_request]',
        '$string_carrier_valid(S_request, pvalue_request)',
        '$string_read_cv_key(S_request, pkeyread) = (pvalue_request)',
        '$string_read_current_offset(S_request, pstringread, pvalue_request) = (2)',
        '$string_read_cv_key(S_cast[.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([50, 0, 120]))], pkeyread) = eps',
        '$string_read_cv_key(S_cast[.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([256]))], pkeyread) = eps',
        '~$string_read_source(S_cast[.ORIGIN = eps], pstringread)',
        '~$string_read_source(S_cast[.POOLS = eps], pstringread)',
        '~$string_read_source(S_cast, pstringread[.KEYCELL = (n_key)])',
    ]
    derived_count = len(checks) - derived_start
    checks += [
        'PhpStep: S_cast ~> S_byte',
        'S_byte.TODO = ptask_tail*',
        'S_byte.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))',
        r'S_byte.STORE = S_cast.STORE /\ S_byte.EVENTS = S_cast.EVENTS',
        'S_byte.ALLOCATIONS = S_cast.ALLOCATIONS',
        r'S_byte.POOLS = S_cast.POOLS /\ S_byte.SOURCES = S_cast.SOURCES',
        '$drive_steps(S_cast, 0) = S_cast[.COMPLETION = BUDGET]',
        '$drive_steps(S_cast, 1) = S_byte[.COMPLETION = BUDGET]',
        *guards('S_byte'),
    ]
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), derived_count)
