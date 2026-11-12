"""Count an outer ARRAY while its marked cell owns a quiet child once."""
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
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_payload)]',
        '$call_reference_operand_valid(S, REFERENCE n_payload)',
        'S.STORE[n_payload] = DEFINED (PARRAY n_child)',
        'n_child =/= n_array',
        'S.ARRAYS[n_child].ITEMS = eps',
        'H = $heap_graph(S)',
        '(HARRAY n_array) <- $heap_prune(H).NODES',
        '(HCELL n_payload) <- $heap_prune(H).NODES',
        '(HARRAY n_child) <- $heap_prune(H).NODES',
        '$node_children(S, HCELL n_key) = [HARRAY n_array]',
        '$node_children(S, HARRAY n_array) = [HCELL n_payload]',
        '$node_children(S, HCELL n_payload) = [HARRAY n_child]',
        '$node_children(S, HARRAY n_child) = eps',
        '$string_read_array_child(S, PARRAY n_child)',
        '~$literal_reference_plain_cell(S, n_payload)',
        '~$string_read_array_string_cell(S, n_payload)',
        '~$string_read_array_alias_entries(S, S.ARRAYS[n_array].ITEMS)',
        '$string_read_array_child_cell(S, n_payload)',
        '$string_read_array_current_entries(S, S.ARRAYS[n_array].ITEMS)',
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
        # The child table can survive alone; its detached cell cannot authorize.
        'S_detached = S[.ARRAYS[n_array].ITEMS = eps]',
        '$call_reference_operand_valid(S_detached, REFERENCE n_payload)',
        '$string_read_array_child(S_detached, PARRAY n_child)',
        '~((HCELL n_payload) <- $heap_prune($heap_graph(S_detached)).NODES)',
        '~$string_read_array_child_cell(S_detached, n_payload)',
        'S_unmarked = S[.REFCELLS = eps]',
        '$string_read_cv_key(S_unmarked, pstringread.READ) = eps',
        'S_undefined = S[.STORE[n_payload] = UNDEFINED]',
        '$string_read_cv_key(S_undefined, pstringread.READ) = eps',
        'S_missing = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HCELL n_payload)]',
        '$string_read_cv_key(S_missing, pstringread.READ) = eps',
        'S_missing_child = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HARRAY n_child)]',
        '$string_read_cv_key(S_missing_child, pstringread.READ) = eps',
        'S_oob = S[.STORE[n_payload] = DEFINED (PARRAY (|S.ARRAYS|))]',
        '$string_read_cv_key(S_oob, pstringread.READ) = eps',
        'S_typed = S[.PROPREFS = {CELL n_payload, SOURCES eps} :: S.PROPREFS]',
        '$string_read_cv_key(S_typed, pstringread.READ) = eps',
        'S_coercion = S[.REFCOERCIONS = {CELL n_payload, SITE pstringread.READ.SITE, LINE pstringread.READ.LINE, VALUE eps} :: S.REFCOERCIONS]',
        '$string_read_cv_key(S_coercion, pstringread.READ) = eps',
        'S_backing = S[.PARAMETERBACKINGS = {FUNCTION pstringread.READ.SITE, INDEX 0, CELL n_payload, LINE pstringread.READ.LINE, VALUE eps} :: S.PARAMETERBACKINGS]',
        '$string_read_cv_key(S_backing, pstringread.READ) = eps',
        'S_recursive = S[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (ALIAS n_payload)]]',
        '$string_read_cv_key(S_recursive, pstringread.READ) = eps',
        'S_mixed = S[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_child)), ENTRY (KINT 1) (ALIAS n_payload), ENTRY (KINT 2) (DIRECT (PINT 0))]]',
        '$node_children(S_mixed, HARRAY n_array) = [HARRAY n_child, HCELL n_payload]',
        '$node_children(S_mixed, HCELL n_payload) = [HARRAY n_child]',
        '$string_read_current_offset(S_mixed, pstringread, PARRAY n_array) = (1)',
        'S_marked_key = S[.REFCELLS = n_key :: S.REFCELLS]',
        '$string_read_cv_key(S_marked_key, pstringread.READ) = (PARRAY n_array)',
        'S_elsewhere = S[.ENV = [BIND ($ptascii("keeper")) n_key]]',
        '$string_read_array_child_cell(S_elsewhere, n_payload)',
        '$string_read_cv_key(S_elsewhere, pstringread.READ) = (PNULL)',
        '$string_read_current_offset(S_elsewhere, pstringread, PARRAY n_array) = eps',
        '~$string_read_source(S, pstringread[.KEYCELL = (n_key)])',
        '$string_read_phase(pstringread.READ.BASE, PARRAY n_array) = eps',
        '$string_read_resume(S_typed, pstringread) = S_typed[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]',
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
