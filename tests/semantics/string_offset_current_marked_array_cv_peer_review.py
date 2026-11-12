"""Count the selected marked ARRAY without multiplying its child ownership."""
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
        'pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abcde"))',
        'pkeyread.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)',
        '$lookup(S.ENV, pkeyread.NAME) = (n_current)',
        '$call_reference_operand_valid(S, REFERENCE n_current)',
        'S.STORE[n_current] = DEFINED (PARRAY n_outer)',
        'S.ARRAYS[n_outer].ITEMS = [ENTRY (KINT 0) (ALIAS n_empty), ENTRY (KINT 1) (ALIAS n_leaf), ENTRY (KINT 2) (DIRECT (PARRAY n_child)), ENTRY (KINT 3) (ALIAS n_leaf)]',
        r'n_current =/= n_empty /\ n_current =/= n_leaf /\ n_empty =/= n_leaf',
        '$call_reference_operand_valid(S, REFERENCE n_empty)',
        '$call_reference_operand_valid(S, REFERENCE n_leaf)',
        'S.STORE[n_empty] = DEFINED (PARRAY n_child)',
        'S.STORE[n_leaf] = DEFINED (PBOOL false)',
        'n_child =/= n_outer',
        'S.ARRAYS[n_child].ITEMS = eps',
        'H = $heap_graph(S)',
        # These complete topology facts were measured in the precode snapshot.
        'H.NODES = [HARRAY n_child, HCELL n_empty, HCELL n_leaf, HARRAY n_outer, HCELL n_current]',
        'H.ROOTS = [HCELL n_current, HARRAY n_child]',
        'H.DEBTS = eps',
        '$node_children(S, HCELL n_current) = [HARRAY n_outer]',
        '$node_children(S, HARRAY n_outer) = [HCELL n_empty, HCELL n_leaf, HARRAY n_child, HCELL n_leaf]',
        '$node_children(S, HCELL n_empty) = [HARRAY n_child]',
        '$node_children(S, HCELL n_leaf) = eps',
        '$node_children(S, HARRAY n_child) = eps',
        '$heap_owners(H, HCELL n_current) = 1',
        '$heap_owners(H, HARRAY n_outer) = 1',
        '$heap_owners(H, HCELL n_empty) = 1',
        '$heap_owners(H, HCELL n_leaf) = 2',
        '$heap_owners(H, HARRAY n_child) = 3',
        '$heap_count(HARRAY n_child, $pools_nodes(S.POOLS)) = 1',
        '$string_read_array_child_cell(S, n_empty)',
        '~$string_read_array_child_cell(S, n_current)',
        '$literal_reference_plain_cell(S, n_leaf)',
        '$string_read_array_current_entries(S, S.ARRAYS[n_outer].ITEMS)',
        '$string_read_capture(S, pkeyread.INPUT) = eps',
        '$string_read_base_capture(S, pkeyread.INPUT) = eps',
        '$cast_truth_int(S, PARRAY n_outer) = 1',
        '$cast_truth_int(S, PARRAY n_child) = 0',
        '$cast_truth_int(S, PBOOL false) = 0',
        '$string_read_cv_receipt(pkeyread)',
        '$string_read_source(S, pstringread)',
        '$string_read_cv_key(S, pkeyread) = (PARRAY n_outer)',
        '$string_read_key_current(S, pstringread) = (PARRAY n_outer)',
        '$string_read_current_offset(S, pstringread, PARRAY n_outer) = (1)',
        '$string_read_current_offset(S, pstringread, PARRAY n_child) = eps',
        '$string_read_ready(S, pstringread)',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
    ]
    derived_start = len(checks)
    checks += [
        # Empty tables, including the two formerly refused valid ARRAY resumes.
        'S_empty = S[.ARRAYS[n_outer].ITEMS = eps]',
        '$string_read_cv_key(S_empty, pkeyread) = (PARRAY n_outer)',
        '$string_read_current_offset(S_empty, pstringread, PARRAY n_outer) = (0)',
        '$string_read_resume(S_empty, pstringread) = S_empty[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'n_fresh_array = |S.ARRAYS|',
        'S_fresh_array = S[.ARRAYS = S.ARRAYS ++ [$array_empty()]][.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY n_fresh_array]][.STORE[n_current] = DEFINED (PARRAY n_fresh_array)]',
        '$heap_owners($heap_graph(S_fresh_array), HARRAY n_fresh_array) = 1',
        '$heap_count(HARRAY n_fresh_array, $pools_nodes(S_fresh_array.POOLS)) = 0',
        '$string_read_cv_key(S_fresh_array, pkeyread) = (PARRAY n_fresh_array)',
        '$string_read_resume(S_fresh_array, pstringread) = S_fresh_array[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        # Sharing a wrapper does not duplicate its table edge or impose COW.
        'S_shared = S[.ENV = S.ENV ++ [BIND ($ptascii("keeper")) n_current]]',
        '$heap_owners($heap_graph(S_shared), HCELL n_current) = 2',
        '$heap_owners($heap_graph(S_shared), HARRAY n_outer) = 1',
        '$string_read_cv_key(S_shared, pkeyread) = (PARRAY n_outer)',
        'S_held = S[.HELD = (HARRAY n_outer) :: S.HELD]',
        '$heap_owners($heap_graph(S_held), HARRAY n_outer) = 2',
        '$string_read_current_offset(S_held, pstringread, PARRAY n_outer) = (1)',
        # Current name and exact table identity win over a live former owner.
        'n_fresh_cell = |S.STORE|',
        'S_fresh_cell = S[.STORE = S.STORE ++ [DEFINED (PARRAY n_child)]][.REFCELLS = n_fresh_cell :: S.REFCELLS][.ALLOCATIONS = S.ALLOCATIONS ++ [HCELL n_fresh_cell]][.ENV = [BIND pkeyread.NAME n_fresh_cell, BIND ($ptascii("keeper")) n_current]]',
        '$string_read_cv_key(S_fresh_cell, pkeyread) = (PARRAY n_child)',
        '$string_read_current_offset(S_fresh_cell, pstringread, PARRAY n_child) = (0)',
        '$string_read_current_offset(S_fresh_cell, pstringread, PARRAY n_outer) = eps',
        'S_elsewhere = S[.ENV = [BIND ($ptascii("keeper")) n_current]]',
        '(HARRAY n_outer) <- $heap_prune($heap_graph(S_elsewhere)).NODES',
        '$string_read_cv_key(S_elsewhere, pkeyread) = (PNULL)',
        '$string_read_current_offset(S_elsewhere, pstringread, PARRAY n_outer) = eps',
        'S_orphan = S[.ENV = eps]',
        '(HARRAY n_outer) <- S_orphan.ALLOCATIONS',
        '~((HARRAY n_outer) <- $heap_prune($heap_graph(S_orphan)).NODES)',
        '(HARRAY n_child) <- $heap_prune($heap_graph(S_orphan)).NODES',
        '$string_read_current_offset(S_orphan, pstringread, PARRAY n_outer) = eps',
        'S_missing_cell = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HCELL n_current)]',
        '$string_read_cv_key(S_missing_cell, pkeyread) = eps',
        'S_missing_array = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HARRAY n_outer)]',
        '$string_read_cv_key(S_missing_array, pkeyread) = eps',
        'S_oob = S[.STORE[n_current] = DEFINED (PARRAY (|S.ARRAYS|))]',
        '$string_read_cv_key(S_oob, pkeyread) = eps',
        # All prior finite entry classes reuse the same selected-table proof.
        'S_flat = S[.ARRAYS[n_outer].ITEMS = [ENTRY (KINT 0) (DIRECT PNULL), ENTRY (KINT 1) (DIRECT (PBOOL false)), ENTRY (KINT 2) (DIRECT (PFLOAT 9221120237041090560)), ENTRY (KINT 3) (DIRECT (PSTRING ([0]))), ENTRY (KINT 4) (DIRECT (PSTRING_CARRIER INTERNED_STRING ([0])))]]',
        '$string_read_cv_key(S_flat, pkeyread) = (PARRAY n_outer)',
        '$string_read_current_offset(S_flat, pstringread, PARRAY n_outer) = (1)',
        'S_text = S[.STORE[n_leaf] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("0")))]',
        '$string_read_array_string_cell(S_text, n_leaf)',
        '$string_read_cv_key(S_text, pkeyread) = (PARRAY n_outer)',
        'n_identity = |S.STRINGDATA|',
        'S_request = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("2tail")]][.STORE[n_leaf] = DEFINED (PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("2tail")))]',
        '$string_read_array_string_cell(S_request, n_leaf)',
        '$string_read_current_offset(S_request, pstringread, PARRAY n_outer) = (1)',
        'S_child_scalar = S[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PSTRING ([0])))]]',
        '$string_read_array_child_cell(S_child_scalar, n_empty)',
        '$string_read_cv_key(S_child_scalar, pkeyread) = (PARRAY n_outer)',
        'S_child_typed = S[.PROPREFS = {CELL n_empty, SOURCES eps} :: S.PROPREFS]',
        '$string_read_cv_key(S_child_typed, pkeyread) = eps',
    ]
    for name, entry in (
        ('object', 'DIRECT (POBJECT 0)'),
        ('indirect', 'INDIRECT n_leaf eps'),
        ('uninitialized', 'UNINITIALIZED'),
        ('undefined', 'DIRECT PUNDEFINED'),
        ('missing_alias', 'ALIAS (|S.STORE|)'),
    ):
        state = 'S_' + name
        checks += [
            state + ' = S[.ARRAYS[n_outer].ITEMS = [ENTRY (KINT 0) (' + entry + ')]]',
            '$string_read_cv_key(' + state + ', pkeyread) = eps',
        ]
    checks += [
        'S_recursive = S[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_outer))]]',
        '$string_read_cv_key(S_recursive, pkeyread) = eps',
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
        '$string_read_cv_key(S, pkeyread_null[.INPUT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("1x")))][.VALUE = PSTRING_CARRIER INTERNED_STRING ($ptascii("1x"))]) = eps',
        '$string_read_cv_key(S, pkeyread[.INPUT = KNOWN (PARRAY n_outer)]) = eps',
        '$string_read_cv_key(S, pkeyread[.INPUT = REFERENCE n_current]) = eps',
        '$string_read_cv_key(S, pkeyread[.VALUE = PARRAY n_outer]) = eps',
        '$string_read_phase(pkeyread.BASE, PARRAY n_outer) = eps',
        '~$string_read_source(S[.ORIGIN = eps], pstringread)',
        '~$string_read_source(S, pstringread[.KEYCELL = (n_current)])',
    ]
    derived_count = len(checks) - derived_start
    checks += [
        'PhpStep: S ~> S_byte',
        'S_byte = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$heap_graph(S_byte) = H',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 1) = S_byte[.COMPLETION = BUDGET]',
        *guards('S_byte'),
    ]
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), derived_count)
