"""Read the exact current marked CV without capturing a historical key cell."""
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
        'S.STORE[n_key] = DEFINED (PINT 2)',
        '$call_reference_operand_valid(S, REFERENCE n_key)',
        'H = $heap_graph(S)',
        '(HCELL n_key) <- $heap_prune(H).NODES',
        '~$foreach_released_cell(S, n_key)',
        '~$typed_cv_string_released_cell(S, n_key)',
        '~$update_released_cell(S, n_key)',
        '$propref_at(S.PROPREFS, n_key) = eps',
        '$reference_coercion_at(S.REFCOERCIONS, n_key) = eps',
        '$parameter_backing_at(S.PARAMETERBACKINGS, n_key) = eps',
        '~$string_read_cell(S, n_key)',
        '$string_read_capture(S, pkeyread.INPUT) = eps',
        'n_current? = (n_key)',
        '$string_read_key_capture(S, pkeyread.INPUT, pkeyread.BASE) = ((PINT 2, n_current?))',
        '$string_read_cv_receipt(pkeyread)',
        '$string_read_source(S, pstringread)',
        '$string_read_cv_key(S, pkeyread) = (PINT 2)',
        '$string_read_key_current(S, pstringread) = (PINT 2)',
        '$string_read_current_offset(S, pstringread, PINT 2) = (2)',
        '$string_read_ready(S, pstringread)',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
    ]
    derived_start = len(checks)
    for name, value, offset in (
        ('null', 'PNULL', 0),
        ('false', 'PBOOL false', 0),
        ('true', 'PBOOL true', 1),
        ('one', 'PINT 1', 1),
        ('negative', 'PINT -1', -1),
        ('fraction', 'PFLOAT 4609434218613702656', 1),
    ):
        state = 'S_' + name
        checks += [
            state + ' = S[.STORE[n_key] = DEFINED (' + value + ')]',
            '$string_read_cv_key(' + state + ', pkeyread) = (' + value + ')',
            '$string_read_current_offset(' + state + ', pstringread, ' + value + ') = (' + str(offset) + ')',
        ]
    # Exactly the old marked-PINT1 refusal is promoted; ordinary capture stays literal.
    checks += [
        'S_ordinary_one = S_one[.REFCELLS = eps]',
        '$string_read_cell(S_ordinary_one, n_key)',
        '$string_read_cv_key(S_ordinary_one, pkeyread) = (PINT 1)',
        '$string_read_cv_key(S_ordinary_one[.REFCELLS = n_key :: S_ordinary_one.REFCELLS], pkeyread) = (PINT 1)',
    ]
    for name, value in (
        ('wide_int', 'PINT 9223372036854775808'),
        ('infinity', 'PFLOAT 9218868437227405312'),
        ('nan', 'PFLOAT 9221120237041090560'),
        ('wide_float', 'PFLOAT 4890909195324358656'),
        ('raw', 'PSTRING ($ptascii("2"))'),
        ('interned', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("2tail"))'),
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
        'S_undefined = S[.STORE[n_key] = UNDEFINED]',
        '$string_read_cv_key(S_undefined, pkeyread) = eps',
        'S_missing = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HCELL n_key)]',
        '$string_read_cv_key(S_missing, pkeyread) = eps',
        # A live cell at another name does not authorize the missing current CV.
        'S_elsewhere = S[.ENV = [BIND ($ptascii("keeper")) n_key]]',
        '(HCELL n_key) <- $heap_prune($heap_graph(S_elsewhere)).NODES',
        '$string_read_cv_key(S_elsewhere, pkeyread) = (PNULL)',
        # A freshly selected reference may differ from the still-live old cell.
        'n_other = |S.STORE|',
        'S_rebound = S[.STORE = S.STORE ++ [DEFINED (PINT 1)]][.REFCELLS = n_other :: S.REFCELLS][.ALLOCATIONS = S.ALLOCATIONS ++ [HCELL n_other]][.ENV = [BIND pkeyread.NAME n_other, BIND ($ptascii("keeper")) n_key]]',
        '$call_reference_operand_valid(S_rebound, REFERENCE n_other)',
        '(HCELL n_key) <- $heap_prune($heap_graph(S_rebound)).NODES',
        '$string_read_cv_key(S_rebound, pkeyread) = (PINT 1)',
        'S_shared = S[.ENV = S.ENV ++ [BIND ($ptascii("keeper")) n_key]]',
        '$string_read_cv_key(S_shared, pkeyread) = (PINT 2)',
        '~$string_read_cv_receipt(pkeyread[.PHASE = KEY_NULL][.NAME = eps])',
        '~$string_read_cv_receipt(pkeyread[.INPUT = KNOWN (PINT 2)])',
        '~$string_read_cv_receipt(pkeyread[.INPUT = REFERENCE n_key])',
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
