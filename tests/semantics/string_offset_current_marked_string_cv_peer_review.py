"""Consume the selected marked REQUEST carrier, preserving its actual owner."""
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
        'S.STORE[n_current] = DEFINED pvalue_current',
        'pvalue_current = PSTRING_CARRIER (REQUEST_STRING n_identity) n_bytes*',
        'n_bytes* = $ptascii("noise")',
        '$(n_identity < |S.STRINGDATA|)',
        'S.STRINGDATA[n_identity] = n_bytes*',
        '$string_carrier_valid(S, pvalue_current)',
        '$c_string(n_bytes*) = n_bytes*',
        'n_capture? = (n_current)',
        '$string_read_base_capture(S, pkeyread.INPUT) = ((pvalue_current, n_capture?))',
        '$string_read_capture(S, pkeyread.INPUT) = eps',
        '~$array_float_key_scalar(S, pvalue_current)',
        'H = $heap_graph(S)',
        'H.NODES = [HCELL n_current]',
        'H.ROOTS = [HCELL n_current]',
        r'H.EDGES = eps /\ H.DEBTS = eps',
        '$heap_owners(H, HCELL n_current) = 1',
        '$node_children(S, HCELL n_current) = eps',
        '$string_read_source(S, pstringread)',
        '$string_read_cv_key(S, pkeyread) = (pvalue_current)',
        '$string_read_key_current(S, pstringread) = (pvalue_current)',
        '$string_read_current_offset(S, pstringread, pvalue_current) = (0)',
        '$string_read_ready(S, pstringread)',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
    ]
    derived_start = len(checks)
    checks += [
        # These layouts cover the seven promoted admission/conversion refusals.
        'pvalue_interned = PSTRING_CARRIER INTERNED_STRING ($ptascii("2tail"))',
        'S_interned = S[.STORE[n_current] = DEFINED pvalue_interned]',
        '$string_read_cv_key(S_interned, pkeyread) = (pvalue_interned)',
        '$string_read_current_offset(S_interned, pstringread, pvalue_interned) = (2)',
        'pvalue_two = PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("2tail"))',
        'S_two = S[.STRINGDATA[n_identity] = $ptascii("2tail")][.STORE[n_current] = DEFINED pvalue_two]',
        '$string_read_cv_key(S_two, pkeyread) = (pvalue_two)',
        '$string_read_current_offset(S_two, pstringread, pvalue_two) = (2)',
        'pvalue_one = PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))',
        'S_one = S[.STORE[n_current] = DEFINED pvalue_one]',
        '$string_read_cv_key(S_one, pkeyread) = (pvalue_one)',
        '$string_read_resume(S_one, pstringread) = S_one[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'pvalue_request_one = PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("1x"))',
        'S_request_one = S[.STRINGDATA[n_identity] = $ptascii("1x")][.STORE[n_current] = DEFINED pvalue_request_one]',
        '$string_read_cv_key(S_request_one, pkeyread) = (pvalue_request_one)',
        '$string_read_current_offset(S_request_one, pstringread, pvalue_request_one) = (1)',
        # Equal registry bytes authenticate identities but do not select a key.
        'n_twin = |S.STRINGDATA|',
        'pvalue_twin = PSTRING_CARRIER (REQUEST_STRING n_twin) n_bytes*',
        'S_twin = S[.STRINGDATA = S.STRINGDATA ++ [n_bytes*]]',
        '$string_carrier_valid(S_twin, pvalue_twin)',
        '$string_read_cv_key(S_twin, pkeyread) = (pvalue_current)',
        '$string_read_current_offset(S_twin, pstringread, pvalue_twin) = eps',
        'S_selected = S_twin[.STORE[n_current] = DEFINED pvalue_twin]',
        '$string_read_cv_key(S_selected, pkeyread) = (pvalue_twin)',
        '$string_read_current_offset(S_selected, pstringread, pvalue_current) = eps',
        '$string_read_current_offset(S_selected, pstringread, pvalue_twin) = (0)',
        '$heap_graph(S_selected) = H',
        'n_fresh = |S.STORE|',
        'S_fresh = S_twin[.STORE = S.STORE ++ [DEFINED pvalue_twin]][.REFCELLS = n_fresh :: S.REFCELLS][.ALLOCATIONS = S.ALLOCATIONS ++ [HCELL n_fresh]][.ENV = [BIND pkeyread.NAME n_fresh, BIND ($ptascii("keeper")) n_current]]',
        '$string_read_cv_key(S_fresh, pkeyread) = (pvalue_twin)',
        '$string_read_current_offset(S_fresh, pstringread, pvalue_current) = eps',
        '$string_read_current_offset(S_fresh, pstringread, pvalue_twin) = (0)',
        'S_wrong = S[.STRINGDATA[n_identity] = $ptascii("other")]',
        '$string_read_cv_key(S_wrong, pkeyread) = eps',
        'S_id = S[.STORE[n_current] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) n_bytes*)]',
        '$string_read_cv_key(S_id, pkeyread) = eps',
        'S_nul = S[.STRINGDATA[n_identity] = [110, 0]][.STORE[n_current] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_identity) ([110, 0]))]',
        '$string_carrier_valid(S_nul, PSTRING_CARRIER (REQUEST_STRING n_identity) ([110, 0]))',
        '$string_read_cv_key(S_nul, pkeyread) = eps',
        'S_raw = S[.STORE[n_current] = DEFINED (PSTRING n_bytes*)]',
        '$string_read_cv_key(S_raw, pkeyread) = eps',
        # Current-name and live-cell authority stay distinct from registry data.
        'S_shared = S[.ENV = S.ENV ++ [BIND ($ptascii("keeper")) n_current]]',
        '$heap_owners($heap_graph(S_shared), HCELL n_current) = 2',
        '$string_read_cv_key(S_shared, pkeyread) = (pvalue_current)',
        'S_elsewhere = S[.ENV = [BIND ($ptascii("keeper")) n_current]]',
        '$string_carrier_valid(S_elsewhere, pvalue_current)',
        '$string_read_cv_key(S_elsewhere, pkeyread) = (PNULL)',
        '$string_read_current_offset(S_elsewhere, pstringread, pvalue_current) = eps',
        'S_dead = S[.ENV = eps]',
        '$string_carrier_valid(S_dead, pvalue_current)',
        '~((HCELL n_current) <- $heap_prune($heap_graph(S_dead)).NODES)',
        '$string_read_base_capture(S_dead, pkeyread.INPUT) = eps',
        '$string_read_current_offset(S_dead, pstringread, pvalue_current) = eps',
        'S_missing = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HCELL n_current)]',
        '$string_read_cv_key(S_missing, pkeyread) = eps',
        'S_undefined = S[.STORE[n_current] = UNDEFINED]',
        '$string_read_cv_key(S_undefined, pkeyread) = eps',
        'S_unmarked = S[.REFCELLS = eps]',
        '$string_read_cv_key(S_unmarked, pkeyread) = (pvalue_current)',
        '$string_read_current_offset(S_unmarked, pstringread, pvalue_current) = (0)',
        'S_primitive = S[.STORE[n_current] = DEFINED (PFLOAT 4613937818241073152)]',
        '$string_read_cv_key(S_primitive, pkeyread) = (PFLOAT 4613937818241073152)',
        '$string_read_current_offset(S_primitive, pstringread, PFLOAT 4613937818241073152) = (3)',
        # The earlier ARRAY refusal now returns its count-selected byte.
        'n_array = |S.ARRAYS|',
        'S_array = S[.ARRAYS = S.ARRAYS ++ [$array_empty()]][.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY n_array]][.STORE[n_current] = DEFINED (PARRAY n_array)]',
        '$string_read_array_child(S_array, PARRAY n_array)',
        '$string_read_cv_key(S_array, pkeyread) = (PARRAY n_array)',
        '$string_read_resume(S_array, pstringread) = S_array[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
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
        'pkeyread_null = pkeyread[.PHASE = KEY_NULL][.NAME = eps]',
        '$string_read_cv_key(S, pkeyread_null) = eps',
        '$string_read_cv_key(S, pkeyread_null[.INPUT = KNOWN pvalue_interned][.VALUE = pvalue_interned]) = eps',
        '$string_read_cv_key(S, pkeyread[.INPUT = KNOWN pvalue_current]) = eps',
        '$string_read_cv_key(S, pkeyread[.INPUT = REFERENCE n_current]) = eps',
        '~$string_read_source(S[.ORIGIN = eps], pstringread)',
        '~$string_read_source(S, pstringread[.KEYCELL = (n_current)])',
    ]
    derived_count = len(checks) - derived_start
    checks += [
        'PhpStep: S ~> S_byte',
        'S_byte = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$heap_graph(S_byte) = H',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 1) = S_byte[.COMPLETION = BUDGET]',
        *guards('S_byte'),
    ]
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), derived_count)
