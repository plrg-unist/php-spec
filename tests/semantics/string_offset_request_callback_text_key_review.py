"""Late text follows the current ordinary CV through the retained CAST callback."""
from string_offset_request_callback_ordinary_key_review import render as ordinary
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    text, count, derived = ordinary(program, filename_b64)
    assert text.count('PINT 2') == 5
    text = text.replace('PINT 2', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("2x"))')
    text = text.replace('R:c;B:99;K:2;A:1;Z;', 'R:c;B:99;K:2x;A:1;Z;')
    checks = lines(r'''
$string_read_current_offset(S,pstringread,PSTRING_CARRIER INTERNED_STRING ($ptascii("2x"))) = (2)
$string_read_offset(PSTRING_CARRIER INTERNED_STRING ($ptascii("2x"))) = eps
S_fraction = S[.STORE[n_key_current] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("1.75")))]
$string_read_key_current(S_fraction,pstringread) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("1.75")))
$string_read_current_offset(S_fraction,pstringread,PSTRING_CARRIER INTERNED_STRING ($ptascii("1.75"))) = (1)
$string_read_resume(S_fraction,pstringread) = S_fraction[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_nonnumeric = S[.STORE[n_key_current] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("word")))]
$string_read_key_current(S_nonnumeric,pstringread) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("word")))
$string_read_resume(S_nonnumeric,pstringread) = S_nonnumeric[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_empty = S[.STORE[n_key_current] = DEFINED (PSTRING_CARRIER INTERNED_STRING eps)]
$string_read_key_current(S_empty,pstringread) = (PSTRING_CARRIER INTERNED_STRING eps)
$string_read_resume(S_empty,pstringread) = S_empty[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_nul = S[.STORE[n_key_current] = DEFINED (PSTRING_CARRIER INTERNED_STRING [49,0,120])]
$string_read_key_current(S_nul,pstringread) = eps
S_bad_bytes = S[.STORE[n_key_current] = DEFINED (PSTRING_CARRIER INTERNED_STRING [256])]
$string_read_key_current(S_bad_bytes,pstringread) = eps
S_request = S[.STORE[n_key_current] = DEFINED pstringread.READ.BASE]
$string_carrier_valid(S_request,pstringread.READ.BASE)
$string_read_key_current(S_request,pstringread) = eps
S_marked = S[.REFCELLS = n_key_current :: S.REFCELLS]
$string_read_key_current(S_marked,pstringread) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("2x")))
$string_read_resume(S_marked,pstringread) = S_marked[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_marked_numeric = S_marked[.STORE[n_key_current] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("1")))]
$string_read_key_current(S_marked_numeric,pstringread) = eps
S.CELL = 3 /\ S.LOCATION = ROOT 2
''')
    return text + ''.join('  -- if ' + check + '\n' for check in checks), count + len(checks), derived + len(checks)
