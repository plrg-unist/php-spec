"""Release before CAST through a nonowning prior callback stack and default mask."""
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
        'pkeyread.INPUT = VARIABLE pkeyread.NAME 25',
        'pkeyread.LINE = 25',
        'pkeyread.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))',
        'pkeyread.OWNERS = BASE_VALUE (VARIABLE n_base_name* z_base)',
        'n_base_name* = $ptascii("base")',
        '$lookup(S_before.ENV, n_base_name*) = (n_original)',
        '$lookup(S_before.ENV, $ptascii("keeper")) = (n_keeper)',
        '$lookup(S_before.ENV, $ptascii("got")) = (n_got)',
        r'n_original = 2 /\ n_keeper = 3 /\ n_got = 4',
        'S_before.STORE[n_original] = DEFINED pkeyread.BASE',
        'S_before.STORE[n_keeper] = DEFINED pkeyread.BASE',
        'S_before.STORE[n_got] = DEFINED (PINT 99)',
        '$lookup(S_before.ENV, pkeyread.NAME) = eps',
        'H_before = $heap_graph(S_before)',
        'H_before = {NODES ([HCELL 0, HCELL 1, HCELL 2, HCELL 3, HCELL 4]), EDGES eps, ROOTS ([HCELL 4, HCELL 3, HCELL 2, HCELL 1, HCELL 0]), DEBTS eps}',
        '$heap_owners(H_before, HCELL n_original) = 1',
        '$heap_owners(H_before, HCELL n_keeper) = 1',
        '$error_call_valid(S_before, perrorcall)',
        '~$string_read_cv_released(S_before, pkeyread)',
        *guards('S_before'),
    ] + seek('S_before', 1, 'S') + [
        'S.TODO = (KEY_READ_RESULT pkeyread) :: ptask_tail*',
        'S.ENV = [BIND ($ptascii("key")) 11, BIND n_base_name* 10, BIND ($ptascii("got")) n_got, BIND ($ptascii("right")) 1, BIND ($ptascii("left")) 0]',
        'S.REFCELLS = [10]',
        'S.STORE[0] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("a")))',
        'S.STORE[1] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("bc")))',
        'S.STORE[n_original] = DEFINED pkeyread.BASE',
        'S.STORE[n_keeper] = DEFINED pkeyread.BASE',
        r'~((HCELL n_original) <- S.ALLOCATIONS) /\ ~((HCELL n_keeper) <- S.ALLOCATIONS)',
        'S.STORE[n_got] = DEFINED (PINT 99)',
        'S.STORE[10] = DEFINED (PINT 99)',
        'S.STORE[11] = DEFINED (PINT 4)',
        '$call_reference_operand_valid(S, REFERENCE 10)',
        '$lookup(S.ENV, $ptascii("keeper")) = eps',
        'S.STRINGDATA = [$ptascii("abc")]',
        'S.ERRORHANDLER = {CALLBACK (perrorcall.CALLBACK), LEVELS 30719}',
        'S.ERRORHANDLERS = [{CALLBACK (PSTRING_CARRIER INTERNED_STRING ($ptascii("requestReleasePrior"))), LEVELS 2}, {CALLBACK eps, LEVELS 0}]',
        '$error_handler_eligible(S, 2)',
        'S_before.ERRORHANDLER = S.ERRORHANDLER',
        'S_before.ERRORHANDLERS = S.ERRORHANDLERS',
        '$error_handler_roots(S.ERRORHANDLER) = eps',
        '$error_handler_stack_roots(S.ERRORHANDLERS) = eps',
        'pstringread = {READ pkeyread, BASECELL eps, KEYCELL eps, PHASE STRING_CAST}',
        '$key_read_valid(S, pkeyread)',
        '$string_read_cv_source(S, pstringread)',
        '$string_read_cv_plan(S, pkeyread) = eps',
        '~$string_read_retained(S, pstringread, S.ENV)',
        '~$string_read_provider_ready(S, pstringread)',
        '$string_read_cv_key(S, pkeyread) = (PINT 4)',
        '$string_read_cv_released(S, pkeyread)',
        'H = $heap_graph(S)',
        'H = {NODES ([HCELL 0, HCELL 1, HCELL 4, HCELL 10, HCELL 11]), EDGES eps, ROOTS ([HCELL 11, HCELL 10, HCELL 4, HCELL 1, HCELL 0]), DEBTS eps}',
        '$heap_owners(H, HCELL n_original) = 0',
        '$heap_owners(H, HCELL n_keeper) = 0',
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
        # Real current owners, including marked cells, defeat zero-owner release.
        'S_keeper = S[.ENV = (BIND ($ptascii("extra")) n_original) :: S.ENV][.ALLOCATIONS = S.ALLOCATIONS ++ [HCELL n_original]]',
        '$heap_valid($heap_graph(S_keeper))',
        '$string_read_provider_ready(S_keeper, pstringread)',
        '~$string_read_cv_released(S_keeper, pkeyread)',
        'S_marked = S_keeper[.REFCELLS = n_original :: S_keeper.REFCELLS]',
        '~$string_read_provider_ready(S_marked, pstringread)',
        '~$string_read_cv_released(S_marked, pkeyread)',
        'S_current = S[.STORE[10] = DEFINED pkeyread.BASE]',
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
        'S_tail = S[.TODO = (KEY_READ_RESULT pkeyread) :: (CONCAT_RIGHT (KNOWN pkeyread.BASE) false false 25) :: ptask_tail*]',
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
        '~$string_read_cv_released(S[.TODO = (STRING_READ_RESULT pstringread[.KEYCELL = (11)]) :: ptask_tail*], pkeyread)',
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
