"""Read the outer count without copying its repeated pooled child table."""
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
        '$lookup(S.ENV, pkeyread.NAME) = (n_key)',
        'S.STORE[n_key] = DEFINED (PARRAY n_array)',
        'n_capture_cell? = (n_key)',
        '$string_read_capture(S, pkeyread.INPUT) = ((PARRAY n_array, n_capture_cell?))',
        '$string_read_cell(S, n_key)',
        '$(n_array < |S.ARRAYS|)',
        '(HARRAY n_array) <- S.ALLOCATIONS',
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 0)), ENTRY (KINT 1) (DIRECT (PARRAY n_child)), ENTRY (KINT 2) (DIRECT (PARRAY n_child))]',
        'n_child =/= n_array',
        '$(n_child < |S.ARRAYS|)',
        '(HARRAY n_child) <- S.ALLOCATIONS',
        'S.ARRAYS[n_child].ITEMS = eps',
        'H = $heap_graph(S)',
        '(HARRAY n_array) <- $heap_prune(H).NODES',
        '(HARRAY n_child) <- $heap_prune(H).NODES',
        '$node_children(S, HCELL n_key) = [HARRAY n_array]',
        '$node_children(S, HARRAY n_array) = [HARRAY n_child, HARRAY n_child]',
        '$node_children(S, HARRAY n_child) = eps',
        # These counts are grounded by the preserved complete precode snapshot.
        'H.ROOTS = [HCELL n_key, HARRAY n_child]',
        '$heap_owners(H, HARRAY n_child) = 3',
        '$cast_truth_int(S, PARRAY n_child) = 0',
        '$cast_truth_int(S, PARRAY n_array) = 1',
        '$string_read_array_entries(S.ARRAYS[n_child].ITEMS)',
        '$string_read_array_child(S, PARRAY n_child)',
        '~$string_read_array_entries(S.ARRAYS[n_array].ITEMS)',
        '~$string_read_array_alias_entries(S, S.ARRAYS[n_array].ITEMS)',
        '$string_read_array_current_entries(S, S.ARRAYS[n_array].ITEMS)',
        '$string_read_cv_receipt(pkeyread)',
        '$string_read_source(S, pstringread)',
        '$string_read_cv_key(S, pkeyread) = (PARRAY n_array)',
        '$string_read_current_offset(S, pstringread, PARRAY n_array) = (1)',
        '$string_read_current_offset(S, pstringread, PARRAY n_child) = eps',
        '$string_read_ready(S, pstringread)',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
    ]
    derived_start = len(checks)
    checks += [
        # Child admission validates one real table, with no uniqueness condition.
        '~$string_read_array_child(S, PINT 0)',
        '~$string_read_array_child(S, PARRAY (|S.ARRAYS|))',
        '~$string_read_array_child(S, PARRAY n_array)',
        'S_missing = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HARRAY n_child)]',
        '~$string_read_array_child(S_missing, PARRAY n_child)',
        '$string_read_cv_key(S_missing, pkeyread) = eps',
        'n_ghost = |S.ARRAYS|',
        'S_ghost = S[.ARRAYS = S.ARRAYS ++ [S.ARRAYS[n_child]]][.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY n_ghost]]',
        '~((HARRAY n_ghost) <- $heap_prune($heap_graph(S_ghost)).NODES)',
        '~$string_read_array_child(S_ghost, PARRAY n_ghost)',
        'S_one = S_ghost[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_ghost))]]',
        '$heap_owners($heap_graph(S_one), HARRAY n_ghost) = 1',
        '$string_read_array_child(S_one, PARRAY n_ghost)',
        '$string_read_current_offset(S_one, pstringread, PARRAY n_array) = (1)',
        'S_two = S_one[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_ghost)), ENTRY (KINT 1) (DIRECT (PARRAY n_ghost))]]',
        '$heap_owners($heap_graph(S_two), HARRAY n_ghost) = 2',
        '$string_read_array_child(S_two, PARRAY n_ghost)',
        '$string_read_current_offset(S_two, pstringread, PARRAY n_array) = (1)',
        # The exact selected CV still authorizes the outer table, not a child.
        'S_elsewhere = S[.ENV = [BIND ($ptascii("keeper")) n_key]]',
        '$string_read_array_child(S_elsewhere, PARRAY n_child)',
        '$string_read_cv_key(S_elsewhere, pkeyread) = (PNULL)',
        '$string_read_current_offset(S_elsewhere, pstringread, PARRAY n_array) = eps',
        'S_marked = S[.REFCELLS = n_key :: S.REFCELLS]',
        '$string_read_cv_key(S_marked, pkeyread) = eps',
        'S_typed = S[.PROPREFS = {CELL n_key, SOURCES eps} :: S.PROPREFS]',
        '$string_read_cv_key(S_typed, pkeyread) = eps',
        'S_coercion = S[.REFCOERCIONS = {CELL n_key, SITE pkeyread.SITE, LINE pkeyread.LINE, VALUE eps} :: S.REFCOERCIONS]',
        '$string_read_cv_key(S_coercion, pkeyread) = eps',
        'S_backing = S[.PARAMETERBACKINGS = {FUNCTION pkeyread.SITE, INDEX 0, CELL n_key, LINE pkeyread.LINE, VALUE eps} :: S.PARAMETERBACKINGS]',
        '$string_read_cv_key(S_backing, pkeyread) = eps',
        # Preserve old DIRECT scalar admission, including raw NUL byte strings.
        'S_scalar = S[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT (PBOOL false)), ENTRY (KINT 1) (DIRECT (PSTRING ([0])))]]',
        '$string_read_array_child(S_scalar, PARRAY n_child)',
        '$string_read_current_offset(S_scalar, pstringread, PARRAY n_array) = (1)',
        'S_empty = S[.ARRAYS[n_array].ITEMS = eps]',
        '$string_read_current_offset(S_empty, pstringread, PARRAY n_array) = (0)',
        # The new DIRECT-child guard does not admit owning ALIAS payloads.
        'n_payload = |S.STORE|',
        'S_alias = S[.STORE = S.STORE ++ [DEFINED (PARRAY n_child)]][.REFCELLS = n_payload :: S.REFCELLS][.ALLOCATIONS = S.ALLOCATIONS ++ [HCELL n_payload]][.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_payload)]]',
        '$call_reference_operand_valid(S_alias, REFERENCE n_payload)',
        '(HCELL n_payload) <- $heap_prune($heap_graph(S_alias)).NODES',
        '~$string_read_array_current_entries(S_alias, S_alias.ARRAYS[n_array].ITEMS)',
        '$string_read_cv_key(S_alias, pkeyread) = eps',
        'S_mix = S_alias[.STORE[n_payload] = DEFINED (PBOOL false)][.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_child)), ENTRY (KINT 1) (ALIAS n_payload), ENTRY (KINT 2) (DIRECT PNULL)]]',
        '$string_read_array_current_entries(S_mix, S_mix.ARRAYS[n_array].ITEMS)',
        '$string_read_current_offset(S_mix, pstringread, PARRAY n_array) = (1)',
    ]
    for name, item in (
        ('cycle', 'DIRECT (PARRAY n_child)'),
        ('backedge', 'DIRECT (PARRAY n_array)'),
        ('alias', 'ALIAS n_key'),
        ('object', 'DIRECT (POBJECT 0)'),
        ('undefined', 'DIRECT PUNDEFINED'),
        ('indirect', 'INDIRECT n_key eps'),
        ('uninitialized', 'UNINITIALIZED'),
    ):
        state = 'S_child_' + name
        checks += [
            state + ' = S[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (' + item + ')]]',
            '~$string_read_array_child(' + state + ', PARRAY n_child)',
            '$string_read_cv_key(' + state + ', pkeyread) = eps',
        ]
    checks += [
        '$string_read_resume(S_child_cycle, pstringread) = S_child_cycle[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]',
        '~$string_read_source(S[.ORIGIN = eps], pstringread)',
        '~$string_read_source(S, pstringread[.KEYCELL = (n_key)])',
        '$string_read_phase(pkeyread.BASE, PARRAY n_array) = eps',
        'pkeyread_initial = pkeyread[.PHASE = KEY_NULL][.VALUE = PARRAY n_array][.NAME = eps]',
        '$string_read_cv_key(S, pkeyread_initial) = eps',
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
