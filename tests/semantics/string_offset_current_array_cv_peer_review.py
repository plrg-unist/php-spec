"""Review immediate count conversion from the current empty ARRAY CV."""
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
        r'pkeyread.PHASE = KEY_CV /\ pkeyread.VALUE = PNULL',
        r'pkeyread.NAME = $ptascii("missing") /\ pkeyread.KEY = KSTRING eps',
        'pkeyread.INPUT = VARIABLE pkeyread.NAME pkeyread.LINE',
        'pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))',
        'pkeyread.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)',
        r'pstringread.BASECELL = eps /\ pstringread.KEYCELL = eps',
        '$lookup(S.ENV, pkeyread.NAME) = (n_key)',
        'S.STORE[n_key] = DEFINED (PARRAY n_array)',
        'n_capture_cell? = (n_key)',
        '$string_read_capture(S, pkeyread.INPUT) = ((PARRAY n_array, n_capture_cell?))',
        '$string_read_cell(S, n_key)',
        '~(n_key <- S.REFCELLS)',
        '$heap_owners($heap_graph(S), HCELL n_key) = 1',
        '$(n_array < |S.ARRAYS|)',
        '(HARRAY n_array) <- S.ALLOCATIONS',
        '(HARRAY n_array) <- $heap_prune($heap_graph(S)).NODES',
        '$node_children(S, HCELL n_key) = [HARRAY n_array]',
        'S.ARRAYS[n_array].ITEMS = eps',
        '$string_read_array_entries(S.ARRAYS[n_array].ITEMS)',
        '$string_read_source(S, pstringread)',
        '$string_read_cv_key(S, pkeyread) = (PARRAY n_array)',
        '$string_read_key_current(S, pstringread) = (PARRAY n_array)',
        '$string_read_current_offset(S, pstringread, PARRAY n_array) = (0)',
        '$string_read_offset(PARRAY n_array) = eps',
        '$string_read_ready(S, pstringread)',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
    ]
    derived_start = len(checks)
    checks += [
        # An outside keeper cannot substitute for the selected current name.
        'S_elsewhere = S[.ENV = [BIND ($ptascii("keeper")) n_key]]',
        '(HARRAY n_array) <- $heap_prune($heap_graph(S_elsewhere)).NODES',
        '$string_read_cv_key(S_elsewhere, pkeyread) = (PNULL)',
        '$string_read_current_offset(S_elsewhere, pstringread, PARRAY n_array) = eps',
        # Equal table contents need their own physical, logical and current ID.
        'n_other = |S.ARRAYS|',
        'S_metadata = S[.ARRAYS = S.ARRAYS ++ [S.ARRAYS[n_array]]]',
        '$string_read_current_offset(S_metadata, pstringread, PARRAY n_other) = eps',
        'S_unallocated = S_metadata[.STORE[n_key] = DEFINED (PARRAY n_other)]',
        '$string_read_cv_key(S_unallocated, pkeyread) = eps',
        '$string_read_current_offset(S_unallocated, pstringread, PARRAY n_other) = eps',
        'S_selected = S_unallocated[.ALLOCATIONS = S_unallocated.ALLOCATIONS ++ [HARRAY n_other]]',
        '$string_read_cv_key(S_selected, pkeyread) = (PARRAY n_other)',
        '$string_read_current_offset(S_selected, pstringread, PARRAY n_other) = (0)',
        '$string_read_current_offset(S_selected, pstringread, PARRAY n_array) = eps',
        'S_dead = S[.ALLOCATIONS = eps]',
        '$string_read_current_offset(S_dead, pstringread, PARRAY n_array) = eps',
        'S_marked = S[.REFCELLS = n_key :: S.REFCELLS]',
        '$string_read_cv_key(S_marked, pkeyread) = (PARRAY n_array)',
        '$string_read_current_offset(S_marked, pstringread, PARRAY n_array) = (0)',
        'S_constrained = S[.PROPREFS = {CELL n_key, SOURCES eps} :: S.PROPREFS]',
        '$string_read_current_offset(S_constrained, pstringread, PARRAY n_array) = eps',
        # Initial ARRAY keys keep the separate illegal-offset path.
        '$string_read_phase(pkeyread.BASE, PARRAY n_array) = eps',
        'pkeyread_initial = pkeyread[.PHASE = KEY_NULL][.VALUE = PARRAY n_array][.NAME = eps]',
        '$string_read_cv_key(S, pkeyread_initial) = eps',
        '$string_read_current_offset(S, pstringread[.READ = pkeyread_initial], PARRAY n_array) = eps',
        '~$string_read_array_entries([ENTRY (KINT 0) UNINITIALIZED])',
        '~$string_read_array_entries([ENTRY (KINT 0) (ALIAS n_key)])',
        '~$string_read_array_entries([ENTRY (KINT 0) (DIRECT (PARRAY n_array))])',
        '~$string_read_array_entries([ENTRY (KINT 0) (DIRECT (POBJECT 0))])',
        '~$string_read_array_entries([ENTRY (KINT 0) (DIRECT PUNDEFINED)])',
        'S_hole = S[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) UNINITIALIZED]]',
        '$string_read_cv_key(S_hole, pkeyread) = eps',
        '$string_read_current_offset(S_hole, pstringread, PARRAY n_array) = eps',
        '~$string_read_source(S[.ORIGIN = eps], pstringread)',
        '~$string_read_source(S[.POOLS = eps], pstringread)',
    ]
    derived_count = len(checks) - derived_start
    checks += [
        'PhpStep: S ~> S_byte',
        'S_byte.TODO = ptask_tail*',
        'S_byte.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))',
        r'S_byte.STORE = S.STORE /\ S_byte.EVENTS = S.EVENTS',
        r'S_byte.ARRAYS = S.ARRAYS /\ S_byte.ALLOCATIONS = S.ALLOCATIONS',
        r'S_byte.ENV = S.ENV /\ S_byte.POOLS = S.POOLS',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 1) = S_byte[.COMPLETION = BUDGET]',
        *guards('S_byte'),
    ]
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), derived_count)
