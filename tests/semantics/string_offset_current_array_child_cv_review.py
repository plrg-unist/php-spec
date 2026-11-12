"""Count an outer current ARRAY while preserving its quiet DIRECT child."""
import json

from string_offset_undefined_cv_review import HELPERS, guards, seek


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 1, 'S') + [
        'S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        r'pstringread.PHASE = STRING_CAST /\ pstringread.READ.PHASE = KEY_CV /\ pstringread.READ.VALUE = PNULL',
        r'pstringread.BASECELL = eps /\ pstringread.KEYCELL = eps',
        '$lookup(S.ENV, pstringread.READ.NAME) = (n_key)',
        'S.STORE[n_key] = DEFINED (PARRAY n_array)',
        'n_capture_cell? = (n_key)',
        '$string_read_capture(S, pstringread.READ.INPUT) = ((PARRAY n_array, n_capture_cell?))',
        '~(n_key <- S.REFCELLS)',
        '$(n_array < |S.ARRAYS|)',
        '(HARRAY n_array) <- S.ALLOCATIONS',
        'H = $heap_graph(S)',
        '(HARRAY n_array) <- $heap_prune(H).NODES',
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_child))]',
        'n_child =/= n_array',
        '$(n_child < |S.ARRAYS|)',
        '(HARRAY n_child) <- S.ALLOCATIONS',
        '(HARRAY n_child) <- $heap_prune(H).NODES',
        'S.ARRAYS[n_child].ITEMS = eps',
        '$node_children(S, HCELL n_key) = [HARRAY n_array]',
        '$node_children(S, HARRAY n_array) = [HARRAY n_child]',
        '$node_children(S, HARRAY n_child) = eps',
        '$string_read_array_entries(S.ARRAYS[n_child].ITEMS)',
        '$string_read_array_child(S, PARRAY n_child)',
        '~$string_read_array_entries(S.ARRAYS[n_array].ITEMS)',
        '~$string_read_array_alias_entries(S, S.ARRAYS[n_array].ITEMS)',
        '$string_read_array_current_entries(S, S.ARRAYS[n_array].ITEMS)',
        '$string_read_cv_receipt(pstringread.READ)',
        '$string_read_source(S, pstringread)',
        '$string_read_cv_key(S, pstringread.READ) = (PARRAY n_array)',
        '$string_read_current_offset(S, pstringread, PARRAY n_array) = (1)',
        '$cast_truth_int(S, PARRAY n_child) = 0',
        '$string_read_current_offset(S, pstringread, PARRAY n_child) = eps',
        '$string_read_ready(S, pstringread)',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
    ]
    derived_start = len(checks)
    checks += [
        # Admission checks a real quiet child; only the outer count is converted.
        '~$string_read_array_child(S, PINT 0)',
        '~$string_read_array_child(S, PARRAY (|S.ARRAYS|))',
        '~$string_read_array_child(S, PARRAY n_array)',
        'S_missing = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HARRAY n_child)]',
        '~$string_read_array_child(S_missing, PARRAY n_child)',
        '$string_read_cv_key(S_missing, pstringread.READ) = eps',
        'S_orphan = S[.ENV = eps][.POOLS = eps]',
        '(HARRAY n_child) <- S_orphan.ALLOCATIONS',
        '~((HARRAY n_child) <- $heap_prune($heap_graph(S_orphan)).NODES)',
        '~$string_read_array_child(S_orphan, PARRAY n_child)',
        'S_loop = S[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_array))]]',
        '~$string_read_array_child(S_loop, PARRAY n_child)',
        '$string_read_cv_key(S_loop, pstringread.READ) = eps',
        'S_alias_child = S[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (ALIAS n_key)]]',
        '~$string_read_array_child(S_alias_child, PARRAY n_child)',
        '$string_read_cv_key(S_alias_child, pstringread.READ) = eps',
        'S_indirect = S[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (INDIRECT n_key eps)]]',
        '$string_read_cv_key(S_indirect, pstringread.READ) = eps',
        'S_uninitialized = S[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) UNINITIALIZED]]',
        '$string_read_cv_key(S_uninitialized, pstringread.READ) = eps',
        'S_undefined = S[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT PUNDEFINED)]]',
        '$string_read_cv_key(S_undefined, pstringread.READ) = eps',
        'S_object = S[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT 0))]]',
        '$string_read_cv_key(S_object, pstringread.READ) = eps',
        'S_nonempty_child = S[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]]',
        '$string_read_current_offset(S_nonempty_child, pstringread, PARRAY n_array) = (1)',
        'S_marked = S[.REFCELLS = n_key :: S.REFCELLS]',
        '$string_read_cv_key(S_marked, pstringread.READ) = (PARRAY n_array)',
        'S_typed = S[.PROPREFS = {CELL n_key, SOURCES eps} :: S.PROPREFS]',
        '$string_read_cv_key(S_typed, pstringread.READ) = eps',
        'S_kept = S[.ENV = eps]',
        '(HARRAY n_array) <- $heap_prune($heap_graph(S_kept)).NODES',
        '$string_read_cv_key(S_kept, pstringread.READ) = (PNULL)',
        '$string_read_current_offset(S_kept, pstringread, PARRAY n_array) = eps',
        '~$string_read_source(S, pstringread[.KEYCELL = (n_key)])',
        '~$string_read_source(S[.POOLS = eps], pstringread)',
        '$string_read_phase(pstringread.READ.BASE, PARRAY n_array) = eps',
        '$string_read_resume(S_loop, pstringread) = S_loop[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]',
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
