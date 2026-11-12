"""Silently cast the exact current marked string without a saved key owner."""
import json

from string_offset_undefined_cv_review import HELPERS, guards, seek


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 1, 'S') + [
        'S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        'pkeyread = pstringread.READ',
        r'pstringread.PHASE = STRING_CAST /\ pkeyread.PHASE = KEY_CV /\ pkeyread.VALUE = PNULL',
        r'pstringread.BASECELL = eps /\ pstringread.KEYCELL = eps',
        'pkeyread.NAME = $ptascii("missing")',
        'pkeyread.INPUT = VARIABLE pkeyread.NAME pkeyread.LINE',
        'pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))',
        '$lookup(S.ENV, pkeyread.NAME) = (n_key)',
        'pvalue_current = PSTRING_CARRIER INTERNED_STRING ($ptascii("2tail"))',
        'S.STORE[n_key] = DEFINED pvalue_current',
        '$call_reference_operand_valid(S, REFERENCE n_key)',
        '$string_carrier_valid(S, pvalue_current)',
        'H = $heap_graph(S)',
        '(HCELL n_key) <- $heap_prune(H).NODES',
        '~$string_read_cell(S, n_key)',
        '$string_read_capture(S, pkeyread.INPUT) = eps',
        'n_current? = (n_key)',
        '$string_read_base_capture(S, pkeyread.INPUT) = ((pvalue_current, n_current?))',
        '$string_read_cv_receipt(pkeyread)',
        '$string_read_source(S, pstringread)',
        '$string_read_cv_key(S, pkeyread) = (pvalue_current)',
        '$string_read_key_current(S, pstringread) = (pvalue_current)',
        '$string_read_current_offset(S, pstringread, pvalue_current) = (2)',
        '$string_read_offset(pvalue_current) = eps',
        '$string_read_ready(S, pstringread)',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
    ]
    derived_start = len(checks)
    for name, text, offset in (
        ('noise', 'noise', 0),
        ('one', '1x', 1),
        ('negative', '-1tail', -1),
    ):
        state = 'S_' + name
        value = 'PSTRING_CARRIER INTERNED_STRING ($ptascii("' + text + '"))'
        checks += [
            state + ' = S[.STORE[n_key] = DEFINED (' + value + ')]',
            '$string_read_cv_key(' + state + ', pkeyread) = (' + value + ')',
            '$string_read_current_offset(' + state + ', pstringread, ' + value + ') = (' + str(offset) + ')',
        ]
    # Registry bytes alone cannot authorize an unselected REQUEST identity.
    checks += [
        'n_identity = |S.STRINGDATA|',
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("2tail"))',
        'S_registry = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("2tail")]]',
        '$string_carrier_valid(S_registry, pvalue_request)',
        '$string_read_cv_key(S_registry, pkeyread) = (pvalue_current)',
        '$string_read_current_offset(S_registry, pstringread, pvalue_request) = eps',
        'S_request = S_registry[.STORE[n_key] = DEFINED pvalue_request]',
        '$string_read_cv_key(S_request, pkeyread) = (pvalue_request)',
        '$string_read_current_offset(S_request, pstringread, pvalue_request) = (2)',
        'pvalue_request_one = PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("1x"))',
        'S_request_one = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("1x")]][.STORE[n_key] = DEFINED pvalue_request_one]',
        '$string_read_cv_key(S_request_one, pkeyread) = (pvalue_request_one)',
        '$string_read_current_offset(S_request_one, pstringread, pvalue_request_one) = (1)',
        'n_twin = |S_request.STRINGDATA|',
        'pvalue_twin = PSTRING_CARRIER (REQUEST_STRING n_twin) ($ptascii("2tail"))',
        'S_twin = S_request[.STRINGDATA = S_request.STRINGDATA ++ [$ptascii("2tail")]]',
        '$string_carrier_valid(S_twin, pvalue_twin)',
        '$string_read_current_offset(S_twin, pstringread, pvalue_twin) = eps',
        'S_selected = S_twin[.STORE[n_key] = DEFINED pvalue_twin]',
        '$string_read_cv_key(S_selected, pkeyread) = (pvalue_twin)',
        '$string_read_current_offset(S_selected, pstringread, pvalue_request) = eps',
        '$string_read_current_offset(S_selected, pstringread, pvalue_twin) = (2)',
        'S_wrong = S_request[.STRINGDATA[n_identity] = $ptascii("2oops")]',
        '$string_read_cv_key(S_wrong, pkeyread) = eps',
        'S_missing_registry = S_request[.STRINGDATA = eps]',
        '$string_read_cv_key(S_missing_registry, pkeyread) = eps',
        # Preserve the exact marked-string refusal replacements from older cuts.
        '$string_read_resume(S_one, pstringread) = S_one[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_shared = S_request[.ENV = S_request.ENV ++ [BIND ($ptascii("keeper")) n_key]]',
        '$string_read_cv_key(S_shared, pkeyread) = (pvalue_request)',
        'S_elsewhere = S_shared[.ENV = [BIND ($ptascii("keeper")) n_key]]',
        '(HCELL n_key) <- $heap_prune($heap_graph(S_elsewhere)).NODES',
        '$string_read_cv_key(S_elsewhere, pkeyread) = (PNULL)',
        '$string_read_current_offset(S_elsewhere, pstringread, pvalue_request) = eps',
        'S_undefined = S[.STORE[n_key] = UNDEFINED]',
        '$string_read_cv_key(S_undefined, pkeyread) = eps',
        'S_missing = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HCELL n_key)]',
        '$string_read_cv_key(S_missing, pkeyread) = eps',
        'S_unmarked = S[.REFCELLS = eps]',
        '$string_read_cv_key(S_unmarked, pkeyread) = (pvalue_current)',
    ]
    for name, value in (
        ('raw', 'PSTRING ($ptascii("2tail"))'),
        ('nul', 'PSTRING_CARRIER INTERNED_STRING ([50, 0, 120])'),
        ('bad_bytes', 'PSTRING_CARRIER INTERNED_STRING ([256])'),
        ('array', 'PARRAY 0'),
        ('object', 'POBJECT 0'),
    ):
        state = 'S_' + name
        checks += [
            state + ' = S[.STORE[n_key] = DEFINED (' + value + ')]',
            '$string_read_cv_key(' + state + ', pkeyread) = eps',
        ]
    for name, field, record in (
        ('typed', 'PROPREFS', '{CELL n_key, SOURCES eps}'),
        ('coercion', 'REFCOERCIONS', '{CELL n_key, SITE pkeyread.SITE, LINE pkeyread.LINE, VALUE eps}'),
        ('backing', 'PARAMETERBACKINGS', '{FUNCTION pkeyread.SITE, INDEX 0, CELL n_key, LINE pkeyread.LINE, VALUE eps}'),
    ):
        state = 'S_' + name
        checks += [
            state + ' = S[.' + field + ' = ' + record + ' :: S.' + field + ']',
            '$string_read_cv_key(' + state + ', pkeyread) = eps',
        ]
    checks += [
        'pkeyread_null = pkeyread[.PHASE = KEY_NULL][.NAME = eps]',
        '$string_read_cv_key(S, pkeyread_null) = eps',
        '$string_read_cv_key(S, pkeyread[.INPUT = KNOWN pvalue_current]) = eps',
        '$string_read_cv_key(S, pkeyread[.INPUT = REFERENCE n_key]) = eps',
        '~$string_read_source(S[.ORIGIN = eps], pstringread)',
        '~$string_read_source(S, pstringread[.KEYCELL = (n_key)])',
        '$string_read_resume(S_typed, pstringread) = S_typed[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]',
    ]
    derived_count = len(checks) - derived_start
    checks += [
        'PhpStep: S ~> S_byte',
        'S_byte = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$heap_graph(S_byte) = H',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 1) = S_byte[.COMPLETION = BUDGET]',
        *guards('S_byte'),
    ]
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), derived_count)
