"""The selected header dies before a new nonnumeric current key is converted."""
from string_offset_request_release_distinct_cv_review import render as distinct_render


def render(program, filename_b64):
    text, premises, derived = distinct_render(program, filename_b64)
    for old, new in (
        ('S.STORE[12] = DEFINED (PINT 4)', 'S.STORE[12] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("not-an-offset")))'),
        ('$string_read_cv_key(S, pkeyread) = (PINT 4)', '$string_read_cv_key(S, pkeyread) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("not-an-offset")))'),
    ):
        assert text.count(old) == 1
        text = text.replace(old, new)
    checks = [
        # The source reached a nonprimitive key, but death precedes conversion.
        'pvalue_key = PSTRING_CARRIER INTERNED_STRING ($ptascii("not-an-offset"))',
        '$string_read_cv_key(S, pkeyread) = (pvalue_key)',
        '~$array_float_key_scalar(S, pvalue_key)',
        '$string_read_release_cells(S, 0, S.ALLOCATIONS)',
        # Another REQUEST header in the current key is no selected-header owner.
        'S_request_key = S[.STORE[12] = DEFINED pvalue_bystander]',
        '$heap_valid($heap_graph(S_request_key))',
        '~$string_read_provider_ready(S_request_key, pstringread)',
        '$string_read_cv_released(S_request_key, pkeyread)',
        '$key_read_resume(S_request_key, pkeyread) = S_request_key[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_marked_key = S_request_key[.REFCELLS = 12 :: S_request_key.REFCELLS]',
        '$heap_valid($heap_graph(S_marked_key))',
        '$string_read_cv_released(S_marked_key, pkeyread)',
        # The unused key value may itself own the selected header.
        'S_selected_key = S[.STORE[12] = DEFINED pkeyread.BASE]',
        '$string_read_provider_ready(S_selected_key, pstringread)',
        '~$string_read_cv_released(S_selected_key, pkeyread)',
        'S_selected_marked = S_selected_key[.REFCELLS = 12 :: S_selected_key.REFCELLS]',
        '$heap_valid($heap_graph(S_selected_marked))',
        '~$string_read_provider_ready(S_selected_marked, pstringread)',
        '~$string_read_cv_released(S_selected_marked, pkeyread)',
        'PhpStep: S_selected_marked ~> S_selected_refused',
        'S_selected_refused = S_selected_marked[.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"]',
        '$heap_graph(S_selected_refused) = $heap_graph(S_selected_marked)',
        # Current-key classification grants no new provider or byte authority.
        '~$string_read_cv_released(S[.STORE[12] = DEFINED ($string_plain(pvalue_key))], pkeyread)',
        '~$string_read_cv_released(S[.STORE[12] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([0]))], pkeyread)',
        'S_key_array = S[.ARRAYS = [$array_empty()]][.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY 0]][.STORE[12] = DEFINED (PARRAY 0)]',
        '$heap_valid($heap_graph(S_key_array))',
        '~$string_read_cv_released(S_key_array, pkeyread)',
    ]
    text += ''.join('  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks)
    return text, premises + len(checks), derived + len(checks)
