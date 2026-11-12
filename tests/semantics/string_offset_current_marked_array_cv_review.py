"""Count the selected marked ARRAY without adding a cell or table owner."""
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
        '$call_reference_operand_valid(S, REFERENCE n_key)',
        'S.STORE[n_key] = DEFINED (PARRAY n_array)',
        '$(n_array < |S.ARRAYS|)',
        '(HARRAY n_array) <- S.ALLOCATIONS',
        'S.ARRAYS[n_array].ITEMS = eps',
        'H = $heap_graph(S)',
        '(HCELL n_key) <- $heap_prune(H).NODES',
        '(HARRAY n_array) <- $heap_prune(H).NODES',
        '$node_children(S, HCELL n_key) = [HARRAY n_array]',
        '~$foreach_released_cell(S, n_key)',
        '~$typed_cv_string_released_cell(S, n_key)',
        '~$update_released_cell(S, n_key)',
        '$propref_at(S.PROPREFS, n_key) = eps',
        '$reference_coercion_at(S.REFCOERCIONS, n_key) = eps',
        '$parameter_backing_at(S.PARAMETERBACKINGS, n_key) = eps',
        '$string_read_capture(S, pkeyread.INPUT) = eps',
        '$string_read_array_current_entries(S, S.ARRAYS[n_array].ITEMS)',
        '$string_read_source(S, pstringread)',
        '$string_read_cv_key(S, pkeyread) = (PARRAY n_array)',
        '$string_read_key_current(S, pstringread) = (PARRAY n_array)',
        '$string_read_current_offset(S, pstringread, PARRAY n_array) = (0)',
        '$string_read_ready(S, pstringread)',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
    ]
    derived_start = len(checks)
    checks += [
        # Canonical allocated flat tables cover the earlier nonempty promotions.
        'n_flat = |S.ARRAYS|',
        'S_allocated = $allocate_array(S, $array_insert($array_empty(), KINT 0, DIRECT (PINT 7)))',
        'S_flat = S_allocated[.RESULT = S.RESULT][.STORE[n_key] = DEFINED (PARRAY n_flat)]',
        '$string_read_cv_key(S_flat, pkeyread) = (PARRAY n_flat)',
        '$string_read_current_offset(S_flat, pstringread, PARRAY n_flat) = (1)',
        '(HARRAY n_array) <- $heap_prune($heap_graph(S_flat)).NODES',
        '$string_read_current_offset(S_flat, pstringread, PARRAY n_array) = eps',
        # A fresh name binding wins while the former cell/table survives elsewhere.
        'n_fresh = |S_flat.STORE|',
        'S_fresh = S_flat[.STORE = S_flat.STORE ++ [DEFINED (PARRAY n_array)]][.REFCELLS = n_fresh :: S_flat.REFCELLS][.ALLOCATIONS = S_flat.ALLOCATIONS ++ [HCELL n_fresh]][.ENV = [BIND pkeyread.NAME n_fresh, BIND ($ptascii("keeper")) n_key]]',
        '$call_reference_operand_valid(S_fresh, REFERENCE n_fresh)',
        '$string_read_cv_key(S_fresh, pkeyread) = (PARRAY n_array)',
        '$string_read_current_offset(S_fresh, pstringread, PARRAY n_array) = (0)',
        '$string_read_current_offset(S_fresh, pstringread, PARRAY n_flat) = eps',
        # Another alias owns the same cell, whose table edge occurs only once.
        'S_shared = S[.ENV = S.ENV ++ [BIND ($ptascii("keeper")) n_key]]',
        'H_shared = $heap_graph(S_shared)',
        '$heap_owners(H_shared, HCELL n_key) = 2',
        '$heap_owners(H_shared, HARRAY n_array) = $heap_owners(H, HARRAY n_array)',
        '$string_read_cv_key(S_shared, pkeyread) = (PARRAY n_array)',
        'S_elsewhere = S[.ENV = [BIND ($ptascii("keeper")) n_key]]',
        '(HARRAY n_array) <- $heap_prune($heap_graph(S_elsewhere)).NODES',
        '$string_read_cv_key(S_elsewhere, pkeyread) = (PNULL)',
        '$string_read_current_offset(S_elsewhere, pstringread, PARRAY n_array) = eps',
        'S_unmarked = S[.REFCELLS = eps]',
        '$string_read_cv_key(S_unmarked, pkeyread) = (PARRAY n_array)',
        'S_missing_cell = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HCELL n_key)]',
        '(HARRAY n_array) <- $heap_prune($heap_graph(S_missing_cell)).NODES',
        '$string_read_cv_key(S_missing_cell, pkeyread) = eps',
        'S_missing_table = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HARRAY n_array)]',
        '$string_read_cv_key(S_missing_table, pkeyread) = eps',
        'S_undefined = S[.STORE[n_key] = UNDEFINED]',
        '$string_read_cv_key(S_undefined, pkeyread) = eps',
        'S_oob = S[.STORE[n_key] = DEFINED (PARRAY (|S.ARRAYS|))]',
        '$string_read_cv_key(S_oob, pkeyread) = eps',
        'S_object = S_flat[.ARRAYS[n_flat] = $array_insert($array_empty(), KINT 0, DIRECT (POBJECT 0))]',
        '$string_read_cv_key(S_object, pkeyread) = eps',
        'S_recursive = S_flat[.ARRAYS[n_flat] = $array_insert($array_empty(), KINT 0, ALIAS n_key)]',
        '$string_read_cv_key(S_recursive, pkeyread) = eps',
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
        'pkeyread_null = pkeyread[.PHASE = KEY_NULL][.NAME = eps][.VALUE = PARRAY n_array]',
        '$string_read_cv_key(S, pkeyread_null) = eps',
        '$string_read_cv_key(S, pkeyread[.INPUT = KNOWN (PARRAY n_array)]) = eps',
        '$string_read_cv_key(S, pkeyread[.INPUT = REFERENCE n_key]) = eps',
        '~$string_read_source(S[.ORIGIN = eps], pstringread)',
        '~$string_read_source(S, pstringread[.KEYCELL = (n_key)])',
        '$string_read_phase(pkeyread.BASE, PARRAY n_array) = eps',
        '$string_read_resume(S_typed, pstringread) = S_typed[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]',
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
