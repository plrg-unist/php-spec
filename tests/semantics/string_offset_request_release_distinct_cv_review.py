"""Release before CAST beside a live equal-byte independent REQUEST header."""
import json

from string_offset_request_base_cv_peer_review import HELPERS, seek
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 0, 'S_before') + [
        'S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*',
        'perrorcall.RESUME = KEY_READ_RESULT pkeyread',
        r'pkeyread.PHASE = KEY_CV /\ pkeyread.VALUE = PNULL',
        'pkeyread.NAME = $ptascii("key")',
        'pkeyread.INPUT = VARIABLE pkeyread.NAME 26',
        'pkeyread.LINE = 26',
        'pkeyread.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))',
        'pkeyread.OWNERS = BASE_VALUE (VARIABLE n_base_name* z_base)',
        'n_base_name* = $ptascii("base")',
        '$lookup(S_before.ENV, n_base_name*) = (n_original)',
        '$lookup(S_before.ENV, $ptascii("keeper")) = (n_keeper)',
        '$lookup(S_before.ENV, $ptascii("got")) = (n_got)',
        r'n_original = 2 /\ n_keeper = 3 /\ n_got = 5',
        'S_before.STORE[n_original] = DEFINED pkeyread.BASE',
        'S_before.STORE[n_keeper] = DEFINED pkeyread.BASE',
        'S_before.STORE[n_got] = DEFINED (PINT 99)',
        '$lookup(S_before.ENV, $ptascii("bystander")) = (n_bystander)',
        'n_bystander = 4',
        'pvalue_bystander = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("abc"))',
        'S_before.STORE[n_bystander] = DEFINED pvalue_bystander',
        '$string_same(pkeyread.BASE, pvalue_bystander) = (false)',
        '$lookup(S_before.ENV, pkeyread.NAME) = eps',
        'H_before = $heap_graph(S_before)',
        'H_before = {NODES ([HCELL 0, HCELL 1, HCELL 2, HCELL 3, HCELL 4, HCELL 5]), EDGES eps, ROOTS ([HCELL 5, HCELL 4, HCELL 3, HCELL 2, HCELL 1, HCELL 0]), DEBTS eps}',
        '$heap_owners(H_before, HCELL n_original) = 1',
        '$heap_owners(H_before, HCELL n_keeper) = 1',
        '$error_call_valid(S_before, perrorcall)',
        '~$string_read_cv_released(S_before, pkeyread)',
        *guards('S_before'),
    ] + seek('S_before', 1, 'S') + [
        'S.TODO = (KEY_READ_RESULT pkeyread) :: ptask_tail*',
        'S.ENV = [BIND ($ptascii("key")) 12, BIND n_base_name* 11, BIND ($ptascii("got")) n_got, BIND ($ptascii("bystander")) n_bystander, BIND ($ptascii("right")) 1, BIND ($ptascii("left")) 0]',
        'S.REFCELLS = [11]',
        'S.STORE[0] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("a")))',
        'S.STORE[1] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("bc")))',
        'S.STORE[n_original] = DEFINED pkeyread.BASE',
        'S.STORE[n_keeper] = DEFINED pkeyread.BASE',
        r'~((HCELL n_original) <- S.ALLOCATIONS) /\ ~((HCELL n_keeper) <- S.ALLOCATIONS)',
        'S.STORE[n_got] = DEFINED (PINT 99)',
        'S.STORE[11] = DEFINED (PINT 99)',
        'S.STORE[12] = DEFINED (PINT 4)',
        '$call_reference_operand_valid(S, REFERENCE 11)',
        '$lookup(S.ENV, $ptascii("keeper")) = eps',
        'S.STRINGDATA = [$ptascii("abc"), $ptascii("abc")]',
        'S.STORE[n_bystander] = DEFINED pvalue_bystander',
        '$string_carrier_valid(S, pvalue_bystander)',
        '$string_bytes(pvalue_bystander) = $string_bytes(pkeyread.BASE)',
        'S.ERRORHANDLER = {CALLBACK (perrorcall.CALLBACK), LEVELS 30719}',
        'S.ERRORHANDLERS = [{CALLBACK (PSTRING_CARRIER INTERNED_STRING ($ptascii("requestReleasePrior"))), LEVELS 2}, {CALLBACK eps, LEVELS 0}]',
        '$error_handler_eligible(S, 2)',
        'S_before.ERRORHANDLER = S.ERRORHANDLER',
        'S_before.ERRORHANDLERS = S.ERRORHANDLERS',
        '$error_handler_roots(S.ERRORHANDLER) = eps',
        '$error_handler_stack_roots(S.ERRORHANDLERS) = eps',
        'pstringread = {READ pkeyread, BASECELL eps, KEYCELL eps, KEYREF false, PHASE STRING_CAST}',
        '$key_read_valid(S, pkeyread)',
        '$string_read_cv_source(S, pstringread)',
        '$string_read_cv_plan(S, pkeyread) = eps',
        '~$string_read_retained(S, pstringread, S.ENV)',
        '~$string_read_provider_ready(S, pstringread)',
        '$string_read_cv_key(S, pkeyread) = (PINT 4)',
        '$string_read_cv_released(S, pkeyread)',
        'H = $heap_graph(S)',
        'H = {NODES ([HCELL 0, HCELL 1, HCELL 4, HCELL 5, HCELL 11, HCELL 12]), EDGES eps, ROOTS ([HCELL 12, HCELL 11, HCELL 5, HCELL 4, HCELL 1, HCELL 0]), DEBTS eps}',
        '$heap_owners(H, HCELL n_original) = 0',
        '$heap_owners(H, HCELL n_keeper) = 0',
        '$heap_owners(H, HCELL n_bystander) = 1',
        '$string_read_release_cells(S, 0, S.ALLOCATIONS)',
        '~$string_read_release_cells(S, 1, S.ALLOCATIONS)',
        '$task_nodes(KEY_READ_RESULT pkeyread) = eps',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
        'S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$key_read_resume(S, pkeyread) = S_expected',
        'PhpStep: S ~> S_after',
        'S_after = S_expected',
        '$heap_graph(S_after) = H',
        'S_after.EVENTS = S.EVENTS',
        'S_after.STORE[n_got] = DEFINED (PINT 99)',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 1) = S_expected[.COMPLETION = BUDGET]',
        *guards('S_after'),
    ]
    derived_start = len(checks)
    checks += [
        # Live equal-byte headers are distinct owners, including ordinary wrappers.
        '~$string_read_release_scalar(S, pvalue_bystander)',
        'S_marked_other = S[.REFCELLS = n_bystander :: S.REFCELLS]',
        '$heap_valid($heap_graph(S_marked_other))',
        '~$string_read_provider_ready(S_marked_other, pstringread)',
        '$string_read_cv_released(S_marked_other, pkeyread)',
        '$key_read_resume(S_marked_other, pkeyread) = S_marked_other[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        # An exact selected-header owner must still defeat release after a prefix.
        'S_same = S[.STORE[n_bystander] = DEFINED pkeyread.BASE]',
        '$heap_valid($heap_graph(S_same))',
        '$string_read_provider_ready(S_same, pstringread)',
        '~$string_read_cv_released(S_same, pkeyread)',
        'S_same_marked = S_same[.REFCELLS = n_bystander :: S_same.REFCELLS]',
        '$heap_valid($heap_graph(S_same_marked))',
        '~$string_read_provider_ready(S_same_marked, pstringread)',
        '~$string_read_cv_released(S_same_marked, pkeyread)',
        'PhpStep: S_same_marked ~> S_same_refused',
        'S_same_refused = S_same_marked[.COMPLETION = UNSUPPORTED "error-handler ingress requires a producer continuation"]',
        '$heap_graph(S_same_refused) = $heap_graph(S_same_marked)',
        # Every other REQUEST header needs its own immutable registry binding.
        'S_bad_payload = S[.STORE[n_bystander] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("bad")))]',
        '~$string_read_cv_released(S_bad_payload, pkeyread)',
        'S_bad_index = S[.STORE[n_bystander] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 2) ($ptascii("abc")))]',
        '~$string_read_cv_released(S_bad_index, pkeyread)',
        'S_raw_other = S[.STORE[n_bystander] = DEFINED ($string_plain(pvalue_bystander))]',
        '~$string_read_cv_released(S_raw_other, pkeyread)',
        'pvalue_nul = PSTRING_CARRIER (REQUEST_STRING 2) ([0])',
        'S_nul_other = S[.STRINGDATA = S.STRINGDATA ++ [([0])]][.STORE[n_bystander] = DEFINED pvalue_nul]',
        '$string_carrier_valid(S_nul_other, pvalue_nul)',
        '~$string_read_cv_released(S_nul_other, pkeyread)',
        'pvalue_other = PSTRING_CARRIER (REQUEST_STRING 2) ($ptascii("xyz"))',
        'S_other_bytes = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("xyz")]][.STORE[n_bystander] = DEFINED pvalue_other]',
        '$string_carrier_valid(S_other_bytes, pvalue_other)',
        '$string_read_cv_released(S_other_bytes, pkeyread)',
        'S_multiple = S_other_bytes[.ENV = (BIND ($ptascii("extra")) n_original) :: S_other_bytes.ENV][.STORE[n_original] = DEFINED pvalue_bystander][.ALLOCATIONS = S_other_bytes.ALLOCATIONS ++ [HCELL n_original]]',
        '$heap_valid($heap_graph(S_multiple))',
        '$string_read_cv_released(S_multiple, pkeyread)',
        # Other authenticated headers are also nonowners in callback providers.
        '$string_read_cv_released(S[.ERRORHANDLER.CALLBACK = (pvalue_bystander)], pkeyread)',
        '$string_read_cv_released(S[.ERRORHANDLERS = S.ERRORHANDLERS ++ [{CALLBACK (pvalue_bystander), LEVELS 0}]], pkeyread)',
        # Real current owners, including marked cells, defeat zero-owner release.
        'S_keeper = S[.ENV = (BIND ($ptascii("extra")) n_original) :: S.ENV][.ALLOCATIONS = S.ALLOCATIONS ++ [HCELL n_original]]',
        '$heap_valid($heap_graph(S_keeper))',
        '$string_read_provider_ready(S_keeper, pstringread)',
        '~$string_read_cv_released(S_keeper, pkeyread)',
        'S_marked = S_keeper[.REFCELLS = n_original :: S_keeper.REFCELLS]',
        '~$string_read_provider_ready(S_marked, pstringread)',
        '~$string_read_cv_released(S_marked, pkeyread)',
        'S_current = S[.STORE[11] = DEFINED pkeyread.BASE]',
        '~$string_read_provider_ready(S_current, pstringread)',
        '~$string_read_cv_released(S_current, pkeyread)',
        'S_unallocated = S[.ENV = (BIND ($ptascii("extra")) n_original) :: S.ENV]',
        '~$heap_valid($heap_graph(S_unallocated))',
        '~$string_read_cv_released(S_unallocated, pkeyread)',
        # Immutable registry and retired STORE entries supply no current owner.
        '$string_read_cv_released(S[.CELL = n_keeper][.LOCATION = ROOT n_original], pkeyread)',
        'S_array = S[.ARRAYS = [$array_insert($array_empty(), KINT 0, DIRECT pkeyread.BASE)]][.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY 0]][.STORE[n_got] = DEFINED (PARRAY 0)]',
        '$heap_valid($heap_graph(S_array))',
        '~$string_read_provider_ready(S_array, pstringread)',
        '~$string_read_cv_released(S_array, pkeyread)',
        'S_tail = S[.TODO = (KEY_READ_RESULT pkeyread) :: (CONCAT_RIGHT (KNOWN pkeyread.BASE) false false 26) :: ptask_tail*]',
        '~$string_read_cv_released(S_tail, pkeyread)',
        'ppool = S.POOLS[0]',
        'ppool.CONSTANTS = (PCONSTANT pcpath pvalue_pool) :: pconstant_tail*',
        'S_pool = S[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath pkeyread.BASE) :: pconstant_tail*]]]',
        '~$string_read_cv_released(S_pool, pkeyread)',
        'pdefaultcache = {ORIGIN pkeyread.SITE, VALUE pkeyread.BASE, CLASS (PVSTRING false)}',
        'puserconstant = {NAME ($ptascii("retainer")), ORIGIN pkeyread.SITE, VALUE pkeyread.BASE, CLASS (PVSTRING false), READS eps, RECEIVES eps}',
    ]
    for field, value in (
        ('RESULT', 'KNOWN pkeyread.BASE'),
        ('BASE', 'BASE_VALUE (KNOWN pkeyread.BASE)'),
        ('DEFAULTCACHE', '[pdefaultcache]'),
        ('USERCONSTANTS', '[puserconstant]'),
        ('ASSERTIONSRAW', 'pkeyread.BASE'),
        ('ASSERTIONSORIGINAL', 'pkeyread.BASE'),
        ('ERRORHANDLER', '{CALLBACK (pkeyread.BASE), LEVELS 2}'),
        ('ERRORHANDLERS', '[{CALLBACK (pkeyread.BASE), LEVELS 0}]'),
        ('REPORTING', '0'),
    ):
        checks.append(f'~$string_read_cv_released(S[.{field} = {value}], pkeyread)')
    for field in ('ORIGIN', 'SOURCES', 'CODE', 'STRINGDATA'):
        checks.append(f'~$string_read_cv_released(S[.{field} = eps], pkeyread)')
    for change in (
        '.PHASE = KEY_NULL', '.GLOBAL = true', '.MODE = KEY_IS',
        '.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)',
    ):
        checks.append(f'~$string_read_cv_released(S, pkeyread[{change}])')
    checks += [
        '~$string_read_cv_released(S[.TODO = (STRING_READ_RESULT pstringread[.BASECELL = (n_original)]) :: ptask_tail*], pkeyread)',
        '~$string_read_cv_released(S[.TODO = (STRING_READ_RESULT pstringread[.KEYCELL = (12)]) :: ptask_tail*], pkeyread)',
        '~$string_read_cv_released(S[.TODO = (STRING_READ_RESULT pstringread[.PHASE = STRING_BOUNDS 8]) :: ptask_tail*], pkeyread)',
        '~$string_read_cv_released(S[.TODO = (THROW_SEARCH 0) :: ptask_tail*], pkeyread)',
    ]
    checks += [
        # Integer masks and nonowning saved callbacks add no selected-header owner.
        '$string_read_cv_released(S[.ERRORHANDLERS = eps], pkeyread)',
        'S_restored = S[.ERRORHANDLER.LEVELS = 0][.ERRORHANDLERS = eps]',
        '$string_read_cv_released(S_restored, pkeyread)',
        '$key_read_resume(S_restored, pkeyread) = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$string_read_cv_released(S[.ERRORHANDLER.LEVELS = 3], pkeyread)',
        '$string_read_cv_released(S[.ERRORHANDLERS = S.ERRORHANDLERS ++ S.ERRORHANDLERS], pkeyread)',
        '~$string_read_cv_released(S[.ERRORHANDLERS = [{CALLBACK (PNULL), LEVELS 0}]], pkeyread)',
        '~$string_read_cv_released(S[.ERRORHANDLER.CALLBACK = ($string_plain(perrorcall.CALLBACK))], pkeyread)',
    ]
    for name, update in (
        ('mask0', '.ERRORHANDLER.LEVELS = 0'),
        ('mask2', '.ERRORHANDLER.LEVELS = 2'),
        ('mask2_empty', '.ERRORHANDLER.LEVELS = 2][.ERRORHANDLERS = eps'),
        ('mask0_none', '.ERRORHANDLER.LEVELS = 0][.ERRORHANDLERS = [{CALLBACK eps, LEVELS 0}]'),
        ('mask3_none', '.ERRORHANDLER.LEVELS = 3][.ERRORHANDLERS = [{CALLBACK eps, LEVELS 0}]'),
        ('two_none', '.ERRORHANDLERS = [{CALLBACK eps, LEVELS 0}, {CALLBACK eps, LEVELS 0}]'),
        ('none2', '.ERRORHANDLERS = [{CALLBACK eps, LEVELS 2}]'),
        ('prior', '.ERRORHANDLERS = [{CALLBACK (perrorcall.CALLBACK), LEVELS 0}]'),
    ):
        checks += [
            f'S_{name} = S[{update}]',
            f'$string_read_cv_released(S_{name}, pkeyread)',
            f'$key_read_resume(S_{name}, pkeyread) = S_{name}[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        ]
    checks += [
        # Raw, NUL and unknown callback payloads cannot close the provider frontier.
        '~$string_read_cv_released(S[.ERRORHANDLERS = [{CALLBACK ($string_plain(perrorcall.CALLBACK)), LEVELS 2}]], pkeyread)',
        '~$string_read_cv_released(S[.ERRORHANDLERS = [{CALLBACK (PSTRING_CARRIER INTERNED_STRING ([0])), LEVELS 2}]], pkeyread)',
        '~$string_read_cv_released(S[.ERRORHANDLERS = [{CALLBACK (POBJECT 0), LEVELS 2}]], pkeyread)',
        '~$string_read_cv_released(S[.ERRORHANDLER.CALLBACK = eps], pkeyread)',
    ]
    derived_count = len(checks) - derived_start
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), derived_count)
