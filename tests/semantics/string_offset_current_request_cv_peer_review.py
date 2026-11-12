"""Review the live current REQUEST key at the independent nonnumeric CAST cut."""
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
        'S.STORE[n_key] = DEFINED pvalue_current',
        'pvalue_current = PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("noise"))',
        'S.STRINGDATA[n_identity] = $ptascii("noise")',
        '$string_carrier_valid(S, pvalue_current)',
        '$string_read_cell(S, n_key)',
        '~(n_key <- S.REFCELLS)',
        '$heap_owners($heap_graph(S), HCELL n_key) = 1',
        '$string_read_source(S, pstringread)',
        '$string_read_cv_key(S, pkeyread) = (pvalue_current)',
        '$string_read_key_current(S, pstringread) = (pvalue_current)',
        '$string_read_current_offset(S, pstringread, pvalue_current) = (0)',
        '$string_read_offset(pvalue_current) = eps',
        '$string_read_ready(S, pstringread)',
        '$value_nodes(pvalue_current) = eps',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
    ]
    derived_start = len(checks)
    checks += [
        # Equal registry bytes never authorize a different or stale identity.
        'n_twin = |S.STRINGDATA|',
        'pvalue_twin = PSTRING_CARRIER (REQUEST_STRING n_twin) ($ptascii("noise"))',
        'S_registry = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("noise")]]',
        '$string_carrier_valid(S_registry, pvalue_twin)',
        '$string_read_current_offset(S_registry, pstringread, pvalue_twin) = eps',
        'S_replaced = S_registry[.STORE[n_key] = DEFINED pvalue_twin]',
        '$string_read_cv_key(S_replaced, pkeyread) = (pvalue_twin)',
        '$string_read_current_offset(S_replaced, pstringread, pvalue_current) = eps',
        '$string_read_current_offset(S_replaced, pstringread, pvalue_twin) = (0)',
        # A selected name and preserved STORE row also need a live ordinary cell.
        'S_dead = S[.ALLOCATIONS = eps]',
        '$string_carrier_valid(S_dead, pvalue_current)',
        '$lookup(S_dead.ENV, pkeyread.NAME) = (n_key)',
        '~$string_read_cell(S_dead, n_key)',
        '$string_read_current_offset(S_dead, pstringread, pvalue_current) = eps',
        'S_absent = S[.ENV = eps]',
        '$string_read_cv_key(S_absent, pkeyread) = (PNULL)',
        '$string_read_current_offset(S_absent, pstringread, pvalue_current) = eps',
        'n_shadow = |S.STORE|',
        'S_shadow = S[.STORE = S.STORE ++ [DEFINED PNULL]][.ALLOCATIONS = S.ALLOCATIONS ++ [HCELL n_shadow]][.ENV = (BIND pkeyread.NAME n_shadow) :: S.ENV]',
        '$string_read_cv_key(S_shadow, pkeyread) = (PNULL)',
        '$string_read_current_offset(S_shadow, pstringread, pvalue_current) = eps',
        'pkeyread_blocked = pkeyread[.NAME = $ptascii("this")][.INPUT = VARIABLE ($ptascii("this")) pkeyread.LINE]',
        'S_blocked = S[.ENV = (BIND ($ptascii("this")) n_key) :: S.ENV]',
        '$string_read_cv_receipt(pkeyread_blocked)',
        '$string_read_current_offset(S_blocked, pstringread[.READ = pkeyread_blocked], pvalue_current) = eps',
        'S_constrained = S[.PROPREFS = {CELL n_key, SOURCES eps} :: S.PROPREFS]',
        '$string_read_cv_key(S_constrained, pkeyread) = eps',
        '$string_read_current_offset(S_constrained, pstringread, pvalue_current) = eps',
        'S_marked = S[.REFCELLS = n_key :: S.REFCELLS]',
        '$string_read_current_offset(S_marked, pstringread, pvalue_current) = (0)',
        '$string_read_current_offset(S[.STRINGDATA = eps], pstringread, pvalue_current) = eps',
        '~$string_read_source(S[.SOURCES = eps], pstringread)',
        '~$string_read_source(S[.CODE = eps], pstringread)',
        '~$string_read_source(S, pstringread[.READ.LINE = $(pkeyread.LINE + 1)])',
    ]
    derived_count = len(checks) - derived_start
    checks += [
        'PhpStep: S ~> S_byte',
        'S_byte.TODO = ptask_tail*',
        'S_byte.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))',
        r'S_byte.STORE = S.STORE /\ S_byte.EVENTS = S.EVENTS',
        r'S_byte.ALLOCATIONS = S.ALLOCATIONS /\ S_byte.ENV = S.ENV',
        r'S_byte.STRINGDATA = S.STRINGDATA /\ S_byte.POOLS = S.POOLS',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 1) = S_byte[.COMPLETION = BUDGET]',
        *guards('S_byte'),
    ]
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), derived_count)
