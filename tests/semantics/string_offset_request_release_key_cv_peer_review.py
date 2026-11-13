"""The closed zero-owner return does not convert the current string key."""
from string_offset_request_release_distinct_cv_peer_review import render as render_distinct


def render(program, filename_b64):
    fixture, count, derived = render_distinct(program, filename_b64)
    previous = '  -- if S.STORE[n_key] = DEFINED (PINT 8)\n'
    assert fixture.count(previous) == 1
    fixture = fixture.replace(previous,
        '  -- if S.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("not-an-offset")))\n')
    checks = [
        'pvalue_key = PSTRING_CARRIER INTERNED_STRING ($ptascii("not-an-offset"))',
        '$string_read_cv_key(S, pkeyread) = (pvalue_key)',
        '~$array_float_key_scalar(S, pvalue_key)',
        '$string_read_current_offset(S, pstringread, pvalue_key) = (0)',
        # The existing distinct-header closure also authenticates this current key.
        'S_request_key = S[.STORE[n_key] = DEFINED pvalue_bystander]',
        '$heap_valid($heap_graph(S_request_key))',
        '$string_read_cv_key(S_request_key, pkeyread) = (pvalue_bystander)',
        '~$string_read_provider_ready(S_request_key, pstringread)',
        '$string_read_cv_released(S_request_key, pkeyread)',
        '$string_read_resume(S_request_key, pstringread) = S_request_key[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_request_key_marked = S_request_key[.REFCELLS = n_key :: S.REFCELLS]',
        '$heap_valid($heap_graph(S_request_key_marked))',
        '$string_read_cv_released(S_request_key_marked, pkeyread)',
        '$string_read_resume(S_request_key_marked, pstringread) = S_request_key_marked[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        # A key that owns the selected header still prevents the zero-owner return.
        'S_key_same = S[.STORE[n_key] = DEFINED pkeyread.BASE]',
        '$heap_valid($heap_graph(S_key_same))',
        '$string_read_provider_ready(S_key_same, pstringread)',
        '~$string_read_cv_released(S_key_same, pkeyread)',
        'S_key_same_marked = S_key_same[.REFCELLS = n_key :: S.REFCELLS]',
        '$heap_valid($heap_graph(S_key_same_marked))',
        '$heap_owners($heap_graph(S_key_same_marked), HCELL n_key) = 1',
        '$string_read_source(S_key_same_marked, pstringread)',
        '~$string_read_provider_ready(S_key_same_marked, pstringread)',
        '~$string_read_cv_released(S_key_same_marked, pkeyread)',
        'PhpStep: S_key_same_marked ~> S_key_same_refused',
        'S_key_same_refused = S_key_same_marked[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]',
        '$heap_graph(S_key_same_refused) = $heap_graph(S_key_same_marked)',
        # No cell, NUL or unknown-header bound changes with the removed key read.
        '~$string_read_cv_released(S[.STORE[n_key] = DEFINED (PSTRING ($ptascii("not-an-offset")))], pkeyread)',
        '~$string_read_cv_released(S[.STORE[n_key] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([0]))], pkeyread)',
        '$string_read_cv_released(S[.CELL = n_key][.LOCATION = ROOT n_key], pkeyread)',
    ]
    return (fixture + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), count + len(checks), derived + len(checks))
