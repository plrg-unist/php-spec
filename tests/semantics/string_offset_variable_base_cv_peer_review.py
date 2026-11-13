"""Keep the selected header after its old base cell and current key retire."""
import json

from string_offset_undefined_cv_review import HELPERS, guards, seek


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 0, 'S_key') + [
        'S_key.TODO = (KEY_READ_RESULT pkeyread) :: ptask_tail*',
        r'S_key.CURRENT = eps /\ S_key.FRAMES = eps',
        r'pkeyread.PHASE = KEY_CV /\ pkeyread.VALUE = PNULL',
        'pkeyread.NAME = $ptascii("missing")',
        'pkeyread.INPUT = VARIABLE pkeyread.NAME pkeyread.LINE',
        'pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abcde"))',
        'pkeyread.OWNERS = BASE_VALUE (VARIABLE n_base_name* z_base)',
        'n_base_name* = $ptascii("base")',
        '$lookup(S_key.ENV, n_base_name*) = (n_base)',
        '$call_reference_operand_valid(S_key, REFERENCE n_base)',
        'S_key.STORE[n_base] = DEFINED (PINT 99)',
        '$string_read_base_capture(S_key, VARIABLE n_base_name* z_base) = eps',
        '$lookup(S_key.ENV, pkeyread.NAME) = (n_key_before)',
        'S_key.STORE[n_key_before] = DEFINED (PINT 3)',
        '~(n_key_before <- S_key.REFCELLS)',
        # The precode snapshot measured the retired base and these complete roots.
        'S_key.STORE[0] = DEFINED pkeyread.BASE',
        '~((HCELL 0) <- S_key.ALLOCATIONS)',
        'H_before = $heap_graph(S_key)',
        'H_before.NODES = [HARRAY n_pool, HCELL n_base, HCELL n_key_before]',
        'H_before.ROOTS = [HCELL n_key_before, HCELL n_base, HARRAY n_pool]',
        r'H_before.EDGES = eps /\ H_before.DEBTS = eps',
        '$heap_owners(H_before, HCELL n_base) = 1',
        '$heap_owners(H_before, HCELL n_key_before) = 1',
        '$key_read_owners_source(S_key, pkeyread)',
        '$key_read_valid(S_key, pkeyread)',
        '$string_read_cv_receipt(pkeyread)',
        '$string_read_cv_plan(S_key, pkeyread) = (pstringread)',
        'pstringread = {READ pkeyread, BASECELL eps, KEYCELL eps, KEYREF false, PHASE STRING_CAST}',
        '$string_read_cv_source(S_key, pstringread)',
        '$task_nodes(KEY_READ_RESULT pkeyread) = eps',
        *guards('S_key'),
        'S_key.ERRORHANDLER.CALLBACK = (pvalue_handler)',
        'perrorcall_cast = {SITE pkeyread.SITE, LEVEL 2, MESSAGE ($ptascii("String offset cast occurred")), LINE pkeyread.LINE, EVENT (DIAGNOSTIC "Warning" ($ptascii("String offset cast occurred")) pkeyread.LINE), CALLBACK pvalue_handler, TARGET eps, RESUME (STRING_READ_RESULT pstringread)}',
        'PhpStep: S_key ~> S_dispatch',
        'S_dispatch = S_key[.TODO = (ERROR_HANDLER_INVOKE perrorcall_cast) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.ERRORFATALTRACE = eps]',
        '$error_call_valid(S_dispatch, perrorcall_cast)',
        '$heap_graph(S_dispatch) = H_before',
    ] + seek('S_dispatch', 1, 'S') + [
        'S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        'S.STORE[n_base] = DEFINED (PINT 99)',
        '$lookup(S.ENV, pkeyread.NAME) = (n_current)',
        'n_current =/= n_key_before',
        '~((HCELL n_key_before) <- S.ALLOCATIONS)',
        'S.STORE[n_key_before] = DEFINED (PINT 3)',
        '$call_reference_operand_valid(S, REFERENCE n_current)',
        'S.STORE[n_current] = DEFINED (PARRAY n_outer)',
        'S.ARRAYS[n_outer].ITEMS = [ENTRY (KINT 0) (ALIAS n_empty), ENTRY (KINT 1) (DIRECT (PARRAY n_child))]',
        'S.STORE[n_empty] = DEFINED (PARRAY n_child)',
        'n_child = n_pool',
        'S.ARRAYS[n_child].ITEMS = eps',
        'H = $heap_graph(S)',
        '$node_children(S, HCELL n_current) = [HARRAY n_outer]',
        '$node_children(S, HARRAY n_outer) = [HCELL n_empty, HARRAY n_child]',
        '$node_children(S, HCELL n_empty) = [HARRAY n_child]',
        '$heap_count(HARRAY n_child, $pools_nodes(S.POOLS)) = 1',
        '$heap_owners(H, HCELL n_current) = 1',
        '$heap_owners(H, HARRAY n_outer) = 1',
        '$heap_owners(H, HARRAY n_child) = 3',
        '$string_read_array_current_entries(S, S.ARRAYS[n_outer].ITEMS)',
        '$string_read_source(S, pstringread)',
        '$string_read_cv_key(S, pkeyread) = (PARRAY n_outer)',
        '$string_read_key_current(S, pstringread) = (PARRAY n_outer)',
        '$string_read_current_offset(S, pstringread, PARRAY n_outer) = (1)',
        '$string_read_current_offset(S, pstringread, PARRAY n_child) = eps',
        '$string_read_ready(S, pstringread)',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
    ]
    derived_start = len(checks)
    checks += [
        # Structural receipt admission never authenticates the wrong source owner.
        'pkeyread_wrong = pkeyread[.OWNERS = BASE_VALUE pkeyread.INPUT]',
        '$string_read_cv_receipt(pkeyread_wrong)',
        '~$string_read_cv_source(S, pstringread[.READ = pkeyread_wrong])',
        '~$string_read_cv_source(S, pstringread[.READ.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)])',
        '~$string_read_cv_source(S, pstringread[.READ.OWNERS = BASE_VALUE (VARIABLE n_base_name* $(z_base + 1))])',
        # The old header needs neither a live former name nor its retired CELL0.
        'S_no_base = S[.ENV = $unbind(S.ENV, n_base_name*)]',
        '~((HCELL n_base) <- $heap_prune($heap_graph(S_no_base)).NODES)',
        '$string_read_source(S_no_base, pstringread)',
        '$string_read_ready(S_no_base, pstringread)',
        '$string_read_resume(S_no_base, pstringread) = S_no_base[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        # Missing/ordinary UNDEFINED keeps NULL; marked UNDEFINED stays refused.
        'S_no_key = S[.ENV = $unbind(S.ENV, pkeyread.NAME)]',
        '$string_read_cv_key(S_no_key, pkeyread) = (PNULL)',
        '$string_read_current_offset(S_no_key, pstringread, PARRAY n_outer) = eps',
        '$string_read_resume(S_no_key, pstringread) = S_no_key[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_undefined = S[.STORE[n_current] = UNDEFINED]',
        '$string_read_cv_key(S_undefined, pkeyread) = eps',
        '$string_read_cv_source(S_undefined, pstringread)',
        'S_plain_undefined = S_undefined[.REFCELLS = eps]',
        '$string_read_cv_key(S_plain_undefined, pkeyread) = (PNULL)',
        '$string_read_current_offset(S_plain_undefined, pstringread, PNULL) = (0)',
        # Shared current names keep one payload edge; other quiet kinds compose.
        'S_shared = S[.ENV = S.ENV ++ [BIND ($ptascii("keeper")) n_current]]',
        '$heap_owners($heap_graph(S_shared), HCELL n_current) = 2',
        '$heap_owners($heap_graph(S_shared), HARRAY n_outer) = 1',
        '$string_read_cv_key(S_shared, pkeyread) = (PARRAY n_outer)',
        'S_integer = S[.STORE[n_current] = DEFINED (PINT 4)]',
        '$string_read_current_offset(S_integer, pstringread, PINT 4) = (4)',
        '$string_read_resume(S_integer, pstringread) = S_integer[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([101]))][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'n_identity = |S.STRINGDATA|',
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_identity) ($ptascii("2tail"))',
        'S_request = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("2tail")]][.STORE[n_current] = DEFINED pvalue_request]',
        '$string_read_cv_key(S_request, pkeyread) = (pvalue_request)',
        '$string_read_current_offset(S_request, pstringread, pvalue_request) = (2)',
        'pvalue_twin = PSTRING_CARRIER (REQUEST_STRING (|S_request.STRINGDATA|)) ($ptascii("2tail"))',
        'S_twin = S_request[.STRINGDATA = S_request.STRINGDATA ++ [$ptascii("2tail")]]',
        '$string_carrier_valid(S_twin, pvalue_twin)',
        '$string_read_current_offset(S_twin, pstringread, pvalue_twin) = eps',
        'S_object = S[.ARRAYS[n_outer].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT 0))]]',
        '$string_read_cv_source(S_object, pstringread)',
        '$string_read_cv_key(S_object, pkeyread) = eps',
        # A fixed BOUNDS result ignores the later current key and base binding.
        'pstringread_bounds = pstringread[.PHASE = STRING_BOUNDS 5]',
        'S_bounds = S_no_base[.TODO = (STRING_READ_RESULT pstringread_bounds) :: ptask_tail*][.STORE[n_current] = DEFINED (PINT 0)]',
        '$string_read_source(S_bounds, pstringread_bounds)',
        '$string_read_resume(S_bounds, pstringread_bounds) = S_bounds[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING eps)][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    for name, field, record in (
        ('typed', 'PROPREFS', '{CELL n_current, SOURCES eps}'),
        ('coercion', 'REFCOERCIONS', '{CELL n_current, SITE pkeyread.SITE, LINE pkeyread.LINE, VALUE eps}'),
        ('backing', 'PARAMETERBACKINGS', '{FUNCTION pkeyread.SITE, INDEX 0, CELL n_current, LINE pkeyread.LINE, VALUE eps}'),
    ):
        state = 'S_' + name
        checks += [state + ' = S[.' + field + ' = ' + record + ' :: S.' + field + ']',
                   '$string_read_cv_source(' + state + ', pstringread)',
                   '$string_read_cv_key(' + state + ', pkeyread) = eps']
    checks += [
        '~$string_read_cv_receipt(pkeyread[.PHASE = KEY_NULL][.NAME = eps])',
        '~$string_read_cv_receipt(pkeyread[.INPUT = KNOWN (PINT 3)])',
        '~$string_read_cv_receipt(pkeyread[.OWNERS = BASE_VALUE (REFERENCE n_base)])',
        '~$string_read_cv_source(S, pstringread[.BASECELL = (n_base)])',
        '~$string_read_cv_source(S, pstringread[.KEYCELL = (n_current)])',
        '~$string_read_cv_source(S, pstringread[.READ.BASE = PSTRING_CARRIER INTERNED_STRING ([97, 0, 99])])',
        '~$string_read_cv_receipt(pkeyread[.BASE = PSTRING ($ptascii("abcde"))])',
        '~$string_read_cv_receipt(pkeyread[.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abcde"))])',
    ]
    for field in ('ORIGIN', 'SOURCES', 'CODE'):
        checks.append('~$string_read_cv_source(S[.' + field + ' = eps], pstringread)')
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
