"""Count the current array without converting its owned string reference."""
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
        '$string_read_cell(S, n_key)',
        '$(n_array < |S.ARRAYS|)',
        '(HARRAY n_array) <- S.ALLOCATIONS',
        'H = $heap_graph(S)',
        '(HARRAY n_array) <- $heap_prune(H).NODES',
        'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_payload)]',
        'pvalue_payload = PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))',
        'S.STORE[n_payload] = DEFINED pvalue_payload',
        '$call_reference_operand_valid(S, REFERENCE n_payload)',
        '(HCELL n_payload) <- $heap_prune(H).NODES',
        '$string_carrier_valid(S, pvalue_payload)',
        '~$literal_reference_plain_cell(S, n_payload)',
        '$string_read_array_string_cell(S, n_payload)',
        '$node_children(S, HCELL n_key) = [HARRAY n_array]',
        '$node_children(S, HARRAY n_array) = [HCELL n_payload]',
        '$node_children(S, HCELL n_payload) = eps',
        '$string_read_source(S, pstringread)',
        '~$string_read_array_entries(S.ARRAYS[n_array].ITEMS)',
        '~$string_read_array_alias_entries(S, S.ARRAYS[n_array].ITEMS)',
        '$string_read_array_current_entries(S, S.ARRAYS[n_array].ITEMS)',
        '$string_read_cv_key(S, pstringread.READ) = (PARRAY n_array)',
        '$string_read_current_offset(S, pstringread, PARRAY n_array) = (1)',
        '$string_read_current_offset(S, pstringread, pvalue_payload) = (0)',
        '$string_read_ready(S, pstringread)',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
    ]
    derived_start = len(checks)
    checks += [
        # Only these four older string-payload refusals are superseded.
        'S_legacy_one = S[.STORE[n_payload] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("safe")))]',
        '$string_read_cv_key(S_legacy_one, pstringread.READ) = (PARRAY n_array)',
        'S_legacy_two = S[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_payload), ENTRY (KINT 1) (ALIAS n_payload)]]',
        '$string_read_cv_key(S_legacy_two, pstringread.READ) = (PARRAY n_array)',
        'S_legacy_mixed = S[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 0)), ENTRY (KINT 1) (ALIAS n_payload)]]',
        '$string_read_cv_key(S_legacy_mixed, pstringread.READ) = (PARRAY n_array)',
        'S_legacy_three = S[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS n_payload), ENTRY (KINT 1) (DIRECT (PBOOL false)), ENTRY (KINT 2) (ALIAS n_payload)]]',
        '$string_read_cv_key(S_legacy_three, pstringread.READ) = (PARRAY n_array)',
        'S_empty_text = S[.STORE[n_payload] = DEFINED (PSTRING_CARRIER INTERNED_STRING eps)]',
        '$string_read_current_offset(S_empty_text, pstringread, PARRAY n_array) = (1)',
        'S_raw = S[.STORE[n_payload] = DEFINED (PSTRING ([48]))]',
        '$string_read_cv_key(S_raw, pstringread.READ) = eps',
        'S_nul = S[.STORE[n_payload] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([0]))]',
        '$string_carrier_valid(S_nul, PSTRING_CARRIER INTERNED_STRING ([0]))',
        '$string_read_cv_key(S_nul, pstringread.READ) = eps',
        'S_bad_byte = S[.STORE[n_payload] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([256]))]',
        '$string_read_cv_key(S_bad_byte, pstringread.READ) = eps',
        'S_request_missing = S[.STORE[n_payload] = DEFINED (PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ([48]))]',
        '$string_read_cv_key(S_request_missing, pstringread.READ) = eps',
        'S_typed = S[.PROPREFS = {CELL n_payload, SOURCES eps} :: S.PROPREFS]',
        '$string_read_cv_key(S_typed, pstringread.READ) = eps',
        'S_coercion = S[.REFCOERCIONS = {CELL n_payload, SITE pstringread.READ.SITE, LINE pstringread.READ.LINE, VALUE eps} :: S.REFCOERCIONS]',
        '$string_read_cv_key(S_coercion, pstringread.READ) = eps',
        'S_backing = S[.PARAMETERBACKINGS = {FUNCTION pstringread.READ.SITE, INDEX 0, CELL n_payload, LINE pstringread.READ.LINE, VALUE eps} :: S.PARAMETERBACKINGS]',
        '$string_read_cv_key(S_backing, pstringread.READ) = eps',
        'S_unmarked = S[.REFCELLS = eps]',
        '$string_read_cv_key(S_unmarked, pstringread.READ) = eps',
        'S_undefined = S[.STORE[n_payload] = UNDEFINED]',
        '$string_read_cv_key(S_undefined, pstringread.READ) = eps',
        'S_missing = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HCELL n_payload)]',
        '$string_read_cv_key(S_missing, pstringread.READ) = eps',
        'S_bad_cell = S[.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (ALIAS (|S.STORE|))]]',
        '$string_read_cv_key(S_bad_cell, pstringread.READ) = eps',
        'S_dead = S[.ENV = eps]',
        '$call_reference_operand_valid(S_dead, REFERENCE n_payload)',
        '$string_carrier_valid(S_dead, pvalue_payload)',
        '~((HCELL n_payload) <- $heap_prune($heap_graph(S_dead)).NODES)',
        '~$string_read_array_string_cell(S_dead, n_payload)',
        '$string_read_current_offset(S_dead, pstringread, PARRAY n_array) = eps',
        '$string_read_resume(S_nul, pstringread) = S_nul[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]',
        '$string_read_phase(pstringread.READ.BASE, PARRAY n_array) = eps',
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
