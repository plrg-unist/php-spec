"""Return NULL after the real CAST callback retires its last REQUEST owner."""
import json

from string_offset_undefined_cv_review import guards

HELPERS = r'''
dec $release_cast_peer_front(pstate, nat) : bool
def $release_cast_peer_front(S, 0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = STRING_READ_RESULT pstringread
  -- if pstringread.PHASE = STRING_CAST /\ pstringread.READ.PHASE = KEY_CV
def $release_cast_peer_front(S, 1) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_CAST /\ pstringread.READ.PHASE = KEY_CV
def $release_cast_peer_front(S, 2) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = KEY_READ_RESULT pkeyread
  -- if pkeyread.PHASE = KEY_CV
def $release_cast_peer_front(S, n) = false -- otherwise
dec $release_cast_peer_seek(pstate, nat, nat) : pstate
def $release_cast_peer_seek(S, n_stage, n) = S -- if $release_cast_peer_front(S, n_stage)
def $release_cast_peer_seek(S, n_stage, n) = S
  -- if ~$release_cast_peer_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $release_cast_peer_seek(S, n_stage, 0) = S
  -- if ~$release_cast_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $release_cast_peer_seek(S, n_stage, n) = $release_cast_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$release_cast_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def seek(start, stage, result):
    return [f'{result}_found = $release_cast_peer_seek({start}, {stage}, 1000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 2, 'S_start') + [
        'S_start.TODO = (ERROR_HANDLER_INVOKE perrorcall_start) :: ptask_start*',
        'perrorcall_start.RESUME = KEY_READ_RESULT pkeyread',
        'pkeyread.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))',
        'pkeyread.OWNERS = BASE_VALUE (VARIABLE n_base_name* z_base)',
        'n_base_name* = $ptascii("base")',
        '$lookup(S_start.ENV, n_base_name*) = (n_original)',
        '$lookup(S_start.ENV, $ptascii("keeper")) = (n_keeper)',
        '$lookup(S_start.ENV, $ptascii("got")) = (n_got)',
        r'n_original = 2 /\ n_keeper = 3 /\ n_got = 4',
        'S_start.STORE[n_original] = DEFINED pkeyread.BASE',
        'S_start.STORE[n_keeper] = DEFINED pkeyread.BASE',
        '$string_read_cell(S_start, n_keeper)',
        '$heap_owners($heap_graph(S_start), HCELL n_original) = 1',
        '$heap_owners($heap_graph(S_start), HCELL n_keeper) = 1',
        '$error_call_valid(S_start, perrorcall_start)',
    ] + seek('S_start', 0, 'S_before') + [
        'S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall_cast) :: ptask_tail*',
        'perrorcall_cast.RESUME = STRING_READ_RESULT pstringread',
        'pstringread = {READ pkeyread, BASECELL eps, KEYCELL eps, KEYREF false, PHASE STRING_CAST}',
        r'S_before.CURRENT = eps /\ S_before.FRAMES = eps',
        r'pkeyread.PHASE = KEY_CV /\ pkeyread.VALUE = PNULL',
        'pkeyread.NAME = $ptascii("key")',
        'pkeyread.INPUT = VARIABLE pkeyread.NAME 25',
        r'pkeyread.LINE = 25 /\ pkeyread.KEY = KSTRING eps',
        '$lookup(S_before.ENV, n_base_name*) = (n_base)',
        'n_base = 10',
        'S_before.STORE[10] = DEFINED (PINT 99)',
        '$call_reference_operand_valid(S_before, REFERENCE 10)',
        '~((HCELL n_original) <- S_before.ALLOCATIONS)',
        '$lookup(S_before.ENV, $ptascii("keeper")) = (n_keeper)',
        'S_before.STORE[n_keeper] = DEFINED pkeyread.BASE',
        '$lookup(S_before.ENV, pkeyread.NAME) = (n_key)',
        'n_key = 11',
        'S_before.STORE[11] = DEFINED (PINT 4)',
        'S_before.STORE[n_got] = DEFINED (PINT 99)',
        '$string_read_source(S_before, pstringread)',
        '$string_read_retained(S_before, pstringread, S_before.ENV)',
        '$string_read_provider_ready(S_before, pstringread)',
        '~$string_read_cv_released(S_before, pkeyread)',
        '$error_call_valid(S_before, perrorcall_cast)',
        'H_before = $heap_graph(S_before)',
        'H_before.NODES = [HCELL 0, HCELL 1, HCELL 3, HCELL 4, HCELL 10, HCELL 11]',
        'H_before.ROOTS = [HCELL 11, HCELL 10, HCELL 4, HCELL 3, HCELL 1, HCELL 0]',
        r'H_before.EDGES = eps /\ H_before.DEBTS = eps',
        '$heap_owners(H_before, HCELL n_keeper) = 1',
    ] + seek('S_before', 1, 'S') + [
        'S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        'S.ENV = [BIND ($ptascii("key")) 11, BIND n_base_name* 10, BIND ($ptascii("got")) 4, BIND ($ptascii("right")) 1, BIND ($ptascii("left")) 0]',
        'S.STORE[n_original] = DEFINED pkeyread.BASE',
        'S.STORE[n_keeper] = DEFINED pkeyread.BASE',
        r'~((HCELL n_original) <- S.ALLOCATIONS) /\ ~((HCELL n_keeper) <- S.ALLOCATIONS)',
        'S.STORE[0] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("a")))',
        'S.STORE[1] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("bc")))',
        'S.STORE[4] = DEFINED (PINT 99)',
        'S.STORE[10] = DEFINED (PINT 99)',
        'S.STORE[11] = DEFINED (PINT 8)',
        'S.REFCELLS = [10]',
        'S.STRINGDATA = [$ptascii("abc")]',
        'S.ERRORHANDLER = {CALLBACK (perrorcall_cast.CALLBACK), LEVELS 0}',
        'S.ERRORHANDLERS = eps',
        'S.EVENTS = S_before.EVENTS ++ [OUTPUT ($ptascii("2")), OUTPUT ($ptascii(":")), OUTPUT ($ptascii("String offset cast occurred")), OUTPUT ($ptascii(";"))]',
        'S.RESULT = KNOWN PNULL',
        'S.BASE = BASE_VALUE (KNOWN PNULL)',
        r'S.ARRAYS = eps /\ S.OBJECTS = eps',
        '$string_read_source(S, pstringread)',
        '~$string_read_provider_ready(S, pstringread)',
        '$string_read_cv_plan(S, pkeyread) = eps',
        '$string_read_cv_released(S, pkeyread)',
        'H = $heap_graph(S)',
        'H.NODES = [HCELL 0, HCELL 1, HCELL 4, HCELL 10, HCELL 11]',
        'H.ROOTS = [HCELL 11, HCELL 10, HCELL 4, HCELL 1, HCELL 0]',
        r'H.EDGES = eps /\ H.DEBTS = eps',
        '$heap_owners(H, HCELL n_original) = 0',
        '$heap_owners(H, HCELL n_keeper) = 0',
        '$heap_valid(H_before)',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        *guards('S'),
        'S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$string_read_resume(S, pstringread) = S_expected',
        'PhpStep: S ~> S_after',
        'S_after = S_expected',
        '$heap_graph(S_after) = H',
        'S_after.EVENTS = S.EVENTS',
        'S_after.STORE[n_got] = DEFINED (PINT 99)',
        '$drive_steps(S, 0) = S[.COMPLETION = BUDGET]',
        '$drive_steps(S, 1) = S_expected[.COMPLETION = BUDGET]',
        '$drive_steps(S_expected, 1) = $drive_steps(S, 2)',
    ]
    derived_start = len(checks)
    checks += [
        # A marked fresh owner is invisible to the ordinary retainer but stays live.
        'n_shadow = |S.STORE|',
        'S_shadow = S[.STORE = S.STORE ++ [DEFINED pkeyread.BASE]][.ENV = (BIND ($ptascii("shadow")) n_shadow) :: S.ENV][.ALLOCATIONS = S.ALLOCATIONS ++ [HCELL n_shadow]][.REFCELLS = n_shadow :: S.REFCELLS]',
        '$heap_valid($heap_graph(S_shadow))',
        '$heap_owners($heap_graph(S_shadow), HCELL n_shadow) = 1',
        '$string_read_source(S_shadow, pstringread)',
        '~$string_read_provider_ready(S_shadow, pstringread)',
        '~$string_read_cv_released(S_shadow, pkeyread)',
        'PhpStep: S_shadow ~> S_shadow_refused',
        'S_shadow_refused = S_shadow[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]',
        '$heap_graph(S_shadow_refused) = $heap_graph(S_shadow)',
        'S_plain = S_shadow[.REFCELLS = S.REFCELLS]',
        '$string_read_provider_ready(S_plain, pstringread)',
        '~$string_read_cv_released(S_plain, pkeyread)',
        # Equal interned bytes are a different immortal header; raw bytes are unknown.
        'S_interned = S[.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("abc")))]',
        '$string_read_cv_released(S_interned, pkeyread)',
        '$string_read_resume(S_interned, pstringread) = S_interned[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '~$string_read_cv_released(S[.STORE[n_got] = DEFINED (PSTRING ($ptascii("abc")))], pkeyread)',
        # A container outside ENV still supplies an owner; no string heap node exists.
        'S_array = S[.ARRAYS = [$array_insert($array_empty(), KINT 0, DIRECT pkeyread.BASE)]][.ALLOCATIONS = S.ALLOCATIONS ++ [HARRAY 0]][.HELD = [HARRAY 0]]',
        '$heap_valid($heap_graph(S_array))',
        '$heap_owners($heap_graph(S_array), HARRAY 0) = 1',
        '~$string_read_provider_ready(S_array, pstringread)',
        '~$string_read_cv_released(S_array, pkeyread)',
        'S_owned_tail = S[.TODO = (STRING_READ_RESULT pstringread) :: (CONCAT_RIGHT (KNOWN pkeyread.BASE) false false 25) :: ptask_tail*]',
        '$string_read_source(S_owned_tail, pstringread)',
        '~$string_read_cv_released(S_owned_tail, pkeyread)',
        # Retired rows, registry metadata and scratch locators add no owner.
        'S_erased = S[.STORE[n_original] = DEFINED (PINT 0)][.STORE[n_keeper] = DEFINED (PBOOL false)]',
        '$string_read_cv_released(S_erased, pkeyread)',
        '$string_read_cv_released(S[.CELL = n_keeper][.LOCATION = ROOT n_original], pkeyread)',
        'S_unallocated = S[.ENV = (BIND ($ptascii("ghost")) n_keeper) :: S.ENV]',
        '~$heap_valid($heap_graph(S_unallocated))',
        '~$string_read_cv_released(S_unallocated, pkeyread)',
        # Phase, continuation and hidden-value providers keep their own domains.
        '~$string_read_cv_released(S[.RESULT = KNOWN pkeyread.BASE], pkeyread)',
        '~$string_read_cv_released(S[.BASE = BASE_VALUE (KNOWN pkeyread.BASE)], pkeyread)',
        '~$string_read_cv_released(S[.ASSERTCALLBACK = (pkeyread.BASE)], pkeyread)',
        '~$string_read_cv_released(S[.ASSERTIONSMODE.INPUT = pkeyread.BASE], pkeyread)',
        '~$string_read_cv_released(S[.ERRORHANDLER = {CALLBACK (pkeyread.BASE), LEVELS 0}], pkeyread)',
        '$string_read_cv_released(S[.ERRORHANDLER.LEVELS = 2], pkeyread)',
        '~$string_read_cv_released(S[.COMPLETION = BUDGET], pkeyread)',
        '~$string_read_cv_released(S[.TODO = (THROW_SEARCH 0) :: ptask_tail*], pkeyread)',
        '~$string_read_cv_released(S[.TODO = (STRING_READ_RESULT pstringread[.PHASE = STRING_BOUNDS 8]) :: ptask_tail*], pkeyread)',
        '~$string_read_cv_released(S, pkeyread[.PHASE = KEY_NULL])',
        '~$string_read_cv_released(S, pkeyread[.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)])',
    ]
    for field in ('ORIGIN', 'SOURCES', 'CODE', 'STRINGDATA'):
        checks.append(f'~$string_read_cv_released(S[.{field} = eps], pkeyread)')
    return (HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
