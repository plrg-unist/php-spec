"""Reread the rebound current reference without saving a KEYCELL locator."""
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
        'pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abcd"))',
        'pkeyread.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)',
        '$lookup(S.ENV, pkeyread.NAME) = (n_current)',
        '$call_reference_operand_valid(S, REFERENCE n_current)',
        'pvalue_current = PFLOAT 4613937818241073152',
        'S.STORE[n_current] = DEFINED pvalue_current',
        'n_capture? = (n_current)',
        '$string_read_key_capture(S, pkeyread.INPUT, pkeyread.BASE) = ((pvalue_current, n_capture?))',
        '~$string_read_cell(S, n_current)',
        '$string_read_capture(S, pkeyread.INPUT) = eps',
        '$array_float_key_scalar(S, pvalue_current)',
        '$string_read_key_quiet(pvalue_current)',
        'H = $heap_graph(S)',
        'H.NODES = [HCELL n_current]',
        'H.ROOTS = [HCELL n_current]',
        r'H.EDGES = eps /\ H.DEBTS = eps',
        '$heap_owners(H, HCELL n_current) = 1',
        '$node_children(S, HCELL n_current) = eps',
        # The complete precode snapshot retains the overwritten ordinary value.
        'S.STORE[3] = DEFINED (PINT 1)',
        '~((HCELL 3) <- S.ALLOCATIONS)',
        '$string_read_cv_receipt(pkeyread)',
        '$string_read_source(S, pstringread)',
        '$string_read_cv_key(S, pkeyread) = (pvalue_current)',
        '$string_read_key_current(S, pstringread) = (pvalue_current)',
        '$string_read_current_offset(S, pstringread, pvalue_current) = (3)',
        '$string_read_ready(S, pstringread)',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
    ]
    derived_start = len(checks)
    checks += [
        # A fresh current binding wins over a still-live former owner.
        'n_fresh = |S.STORE|',
        'S_fresh = S[.STORE = S.STORE ++ [DEFINED (PINT 1)]][.REFCELLS = n_fresh :: S.REFCELLS][.ALLOCATIONS = S.ALLOCATIONS ++ [HCELL n_fresh]][.ENV = [BIND pkeyread.NAME n_fresh, BIND ($ptascii("keeper")) n_current]]',
        '$string_read_cv_key(S_fresh, pkeyread) = (PINT 1)',
        '$string_read_key_current(S_fresh, pstringread) = (PINT 1)',
        'S_shared = S[.ENV = [BIND pkeyread.NAME n_current, BIND ($ptascii("keeper")) n_current]]',
        '$heap_owners($heap_graph(S_shared), HCELL n_current) = 2',
        '$string_read_cv_key(S_shared, pkeyread) = (pvalue_current)',
        'S_elsewhere = S[.ENV = [BIND ($ptascii("keeper")) n_current]]',
        '(HCELL n_current) <- $heap_prune($heap_graph(S_elsewhere)).NODES',
        '$string_read_cv_key(S_elsewhere, pkeyread) = (PNULL)',
        '$string_read_key_current(S_elsewhere, pstringread) = (PNULL)',
        'S_stale = S[.ENV = [BIND pkeyread.NAME 3]][.REFCELLS = 3 :: S.REFCELLS]',
        '$string_read_cv_key(S_stale, pkeyread) = eps',
        'S_missing = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HCELL n_current)]',
        '$string_read_cv_key(S_missing, pkeyread) = eps',
        'S_undefined = S[.STORE[n_current] = UNDEFINED]',
        '$string_read_cv_key(S_undefined, pkeyread) = eps',
        'S_unmarked = S[.REFCELLS = eps]',
        '$string_read_cv_key(S_unmarked, pkeyread) = (pvalue_current)',
        '$string_read_cv_key(S_undefined[.REFCELLS = eps], pkeyread) = (PNULL)',
        # Explicit primitives keep broader String key-capture domains separate.
        'S_string = S[.STORE[n_current] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("1x")))]',
        '$string_carrier_valid(S_string, PSTRING_CARRIER INTERNED_STRING ($ptascii("1x")))',
        '$string_read_cv_key(S_string, pkeyread) = eps',
        'n_identity = |S.STRINGDATA|',
        'S_request = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("1x")]][.STORE[n_current] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("1x")))]',
        '$string_carrier_valid(S_request, PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("1x")))',
        '$string_read_cv_key(S_request, pkeyread) = eps',
        'n_array = |S.ARRAYS|',
        'S_array = S[.ARRAYS = S.ARRAYS ++ [$array_empty()]][.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY n_array]][.STORE[n_current] = DEFINED (PARRAY n_array)]',
        '(HARRAY n_array) <- $heap_prune($heap_graph(S_array)).NODES',
        '$string_read_array_child(S_array, PARRAY n_array)',
        '$string_read_cv_key(S_array, pkeyread) = eps',
        # Reconstruct the sole promoted old marked-current PINT1 layout.
        'S_one = S[.STORE[n_current] = DEFINED (PINT 1)]',
        '$string_read_cv_key(S_one, pkeyread) = (PINT 1)',
        '$string_read_cv_key(S[.STORE[n_current] = DEFINED (PINT 9223372036854775808)], pkeyread) = eps',
        'S_nan = S[.STORE[n_current] = DEFINED (PFLOAT 9221120237041090560)]',
        '~$string_read_key_quiet(PFLOAT 9221120237041090560)',
        '$string_read_cv_key(S_nan, pkeyread) = eps',
        'S_range = S[.STORE[n_current] = DEFINED (PFLOAT 4890909195324358656)]',
        '~$string_read_key_quiet(PFLOAT 4890909195324358656)',
        '$string_read_cv_key(S_range, pkeyread) = eps',
    ]
    for name, field, record in (
        ('typed', 'PROPREFS', '{CELL n_current, SOURCES eps}'),
        ('coercion', 'REFCOERCIONS', '{CELL n_current, SITE pkeyread.SITE, LINE pkeyread.LINE, VALUE eps}'),
        ('backing', 'PARAMETERBACKINGS', '{FUNCTION pkeyread.SITE, INDEX 0, CELL n_current, LINE pkeyread.LINE, VALUE eps}'),
    ):
        state = 'S_' + name
        checks += [
            state + ' = S[.' + field + ' = ' + record + ' :: S.' + field + ']',
            '$string_read_cv_key(' + state + ', pkeyread) = eps',
        ]
    checks += [
        # PHASE and INPUT authenticate CV rereads; KEYCELL absence alone cannot.
        'pkeyread_null = pkeyread[.PHASE = KEY_NULL][.NAME = eps]',
        '$string_read_cv_key(S, pkeyread_null) = eps',
        'pkeyread_literal = pkeyread_null[.INPUT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("1x")))][.VALUE = PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))]',
        '$string_read_cv_key(S, pkeyread_literal) = eps',
        '$string_read_cv_key(S, pkeyread[.INPUT = KNOWN pvalue_current]) = eps',
        '$string_read_cv_key(S, pkeyread[.INPUT = REFERENCE n_current]) = eps',
        '~$string_read_source(S[.ORIGIN = eps], pstringread)',
        '~$string_read_source(S, pstringread[.KEYCELL = (n_current)])',
        '$string_read_resume(S_string, pstringread) = S_string[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]',
    ]
    derived_count = len(checks) - derived_start
    checks += [
        'PhpStep: S ~> S_byte',
        'S_byte = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([100]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$heap_graph(S_byte) = H',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 1) = S_byte[.COMPLETION = BUDGET]',
        *guards('S_byte'),
    ]
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), derived_count)
