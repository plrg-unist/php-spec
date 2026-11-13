"""A plain CV keeps its silent zero conversion when its current name is absent."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 0, 'S_before') + lines(r'''
$string_read_plan(S_before) = (pstringread)
~pstringread.KEYREF
pstringread.KEYCELL = (n_old)
n_old = 3
pstringread.READ.VALUE = PBOOL true
pstringread.READ.INPUT = VARIABLE ($ptascii("key")) 20
pstringread.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
S_before.REFCELLS = eps
S_before.STORE[n_old] = DEFINED (PBOOL true)
$lookup(S_before.ENV,$ptascii("key")) = (n_old)
$lookup(S_before.ENV,$ptascii("alias")) = eps
$heap_owners($heap_graph(S_before),HCELL n_old) = 1
PhpStep: S_before ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.CALLBACK = pstringread.READ.BASE
$error_call_valid(S_dispatch,perrorcall)
''') + guards('S_before') + seek('S_dispatch', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
$lookup(S.ENV,$ptascii("key")) = eps
$lookup(S.ENV,$ptascii("alias")) = (n_old)
$lookup(S.ENV,$ptascii("base")) = (11)
S.STORE[n_old] = DEFINED (PINT 2)
S.STORE[11] = DEFINED (PINT 99)
S.STORE[4] = DEFINED (PINT 99)
S.REFCELLS = [11,n_old]
$literal_reference_plain_cell(S,n_old)
(HCELL n_old) <- $heap_prune($heap_graph(S)).NODES
$ptascii("key") <- S.CVS
$string_read_key_capture(S,pstringread.READ.INPUT,pstringread.READ.BASE) = eps
$string_read_source(S,pstringread)
$string_read_callback_cast_retained(S,pstringread)
$string_read_provider_ready(S,pstringread)
$string_read_key_current(S,pstringread) = (PNULL)
$string_read_current_offset(S,pstringread,PNULL) = (0)
$string_read_ready(S,pstringread)
S.CELL = 3 /\ S.LOCATION = ROOT 2
H = $heap_graph(S)
H = {NODES ([HCELL 0,HCELL 1,HCELL 3,HCELL 4,HCELL 11]),EDGES eps,ROOTS ([HCELL 11,HCELL 3,HCELL 4,HCELL 1,HCELL 0]),DEBTS eps}
$heap_owners(H,HCELL n_old) = 1
$heap_owners(H,HCELL 2) = 0
$task_nodes(STRING_READ_RESULT pstringread) = eps
S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
$string_read_resume(S,pstringread) = S_expected
PhpStep: S ~> S_after
S_after = S_expected
$heap_graph(S_after) = H
S_after.EVENTS = S.EVENTS
$drive_steps(S,0) = S[.COMPLETION = BUDGET]
$drive_steps(S,1) = S_expected[.COMPLETION = BUDGET]
S_done = $drive_steps(S_after,1000)
S_done.COMPLETION = NORMAL
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("2:String offset cast occurred;R:a;B:99;K:;A:2;Z;")
''') + guards('S') + guards('S_after')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks += ['S = $initial_state(NORMAL)' + ''.join('[.' + field + ' = S.' + field + ']' for field in fields)]
    derived_start = len(checks)
    checks += lines(r'''
pstringread_ref = pstringread[.KEYREF = true]
S_ref = S[.TODO = (STRING_READ_RESULT pstringread_ref) :: ptask_tail*]
$string_read_source(S_ref,pstringread_ref)
$string_read_key_current(S_ref,pstringread_ref) = (PINT 2)
$string_read_resume(S_ref,pstringread_ref) = S_ref[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_same = S[.ENV = (BIND ($ptascii("key")) n_old) :: S.ENV]
$heap_valid($heap_graph(S_same))
$heap_owners($heap_graph(S_same),HCELL n_old) = 2
$string_read_key_current(S_same,pstringread) = (PINT 2)
$string_read_resume(S_same,pstringread) = S_same[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_same_text = S_same[.STORE[n_old] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("2x")))]
$string_read_key_current(S_same_text,pstringread) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("2x")))
$string_read_resume(S_same_text,pstringread) = S_same_text[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_old_bounds = S[.STORE[n_old] = DEFINED (PINT 99)]
$string_read_key_current(S_old_bounds,pstringread) = (PNULL)
$string_read_resume(S_old_bounds,pstringread) = S_old_bounds[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_old)]
$string_read_key_current(S_unmarked,pstringread) = (PNULL)
S_bad_heap = S[.ENV = (BIND ($ptascii("unused")) 12) :: S.ENV]
~$heap_valid($heap_graph(S_bad_heap))
$string_read_key_current(S_bad_heap,pstringread) = eps
S_unowned = S[.ERRORHANDLER.CALLBACK = (PSTRING_CARRIER INTERNED_STRING ($ptascii("abc")))]
~$string_read_callback_cast_retained(S_unowned,pstringread)
$string_read_key_current(S_unowned,pstringread) = eps
$string_read_cast_released(S_unowned,pstringread)
$string_read_resume(S_unowned,pstringread) = S_unowned[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]
S_keeper = S_unowned[.STORE[4] = DEFINED pstringread.READ.BASE]
$string_read_provider_ready(S_keeper,pstringread)
$string_read_key_current(S_keeper,pstringread) = eps
$string_read_resume(S_keeper,pstringread) = S_keeper[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]
''')
    for field, value in (('CVS','eps'), ('RESULT','KNOWN (PINT 0)'), ('BASE','BASE_VALUE (KNOWN pstringread.READ.BASE)'), ('COMPLETION','BUDGET'), ('COMPLETION','THROWING 0')):
        checks.append(f'$string_read_key_current(S[.{field} = {value}],pstringread) = eps')
    for field in ('ORIGIN','SOURCES','CODE','STRINGDATA'):
        checks.append(f'$string_read_key_current(S[.{field} = eps],pstringread) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
