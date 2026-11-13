"""A plain compiled CV reads its same ordinary text slot after the cast Warning."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial',0,'S_capture') + lines(r'''
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL (n_base_old),KEYCELL (n_key_old),KEYREF false,PHASE STRING_CAST}
pkeyread.INPUT = VARIABLE ($ptascii("key")) 21
pkeyread.LINE = 21 /\ pkeyread.PHASE = KEY_NULL
pkeyread.VALUE = PBOOL true
pkeyread.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
pkeyread.OWNERS = BASE_VALUE (VARIABLE ($ptascii("base")) 21)
n_base_old = 2 /\ n_key_old = 3
S_capture.REFCELLS = eps
~$string_read_key_reference(S_capture,pstringread.KEYCELL)
$lookup(S_capture.ENV,$ptascii("key")) = (n_key_old)
$lookup(S_capture.ENV,$ptascii("alias")) = eps
$lookup(S_capture.ENV,$ptascii("got")) = (n_got)
n_got = 4
S_capture.STORE[n_key_old] = DEFINED (PBOOL true)
$heap_owners($heap_graph(S_capture),HCELL n_key_old) = 1
pvalue_current = PSTRING_CARRIER INTERNED_STRING ($ptascii("requestReboundKey"))
S_capture.ERRORHANDLER = {CALLBACK (pvalue_current),LEVELS 30719}
S_capture.ERRORHANDLERS = [{CALLBACK (pkeyread.BASE),LEVELS 2},{CALLBACK eps,LEVELS 0}]
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.CALLBACK = pvalue_current
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 21
perrorcall.MESSAGE = $ptascii("String offset cast occurred")
$error_call_valid(S_before,perrorcall)
''') + guards('S_before') + seek('S_before',2,'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
$lookup(S.ENV,$ptascii("base")) = (n_base)
$lookup(S.ENV,$ptascii("key")) = (n_key_current)
$lookup(S.ENV,$ptascii("alias")) = eps
n_base = 10 /\ n_key_current = n_key_old
n_key_current = n_key_old
S.STORE[n_base_old] = DEFINED pkeyread.BASE
~((HCELL n_base_old) <- S.ALLOCATIONS)
S.STORE[n_key_old] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("2x")))
S.STORE[n_key_current] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("2x")))
S.STORE[n_base] = DEFINED (PINT 99)
S.STORE[n_got] = DEFINED (PINT 99)
S.REFCELLS = [n_base]
~$call_reference_operand_valid(S,REFERENCE n_key_old)
~$call_reference_operand_valid(S,REFERENCE n_key_current)
$string_read_cell(S,n_key_current)
~$literal_reference_plain_cell(S,n_key_old)
~$string_read_array_string_cell(S,n_key_old)
$string_read_release_scalar(S,PSTRING_CARRIER INTERNED_STRING ($ptascii("2x")))
(HCELL n_key_old) <- $heap_prune($heap_graph(S)).NODES
~$foreach_released_cell(S,n_key_old)
~$typed_cv_string_released_cell(S,n_key_old)
~$update_released_cell(S,n_key_old)
$ptascii("key") <- S.CVS
S.STRINGDATA = [$ptascii("abc")]
S.ERRORHANDLER = S_capture.ERRORHANDLER
S.ERRORHANDLERS = S_capture.ERRORHANDLERS
$string_read_source(S,pstringread)
$string_read_callback_cast_retained(S,pstringread)
$string_read_provider_ready(S,pstringread)
~$string_read_cast_released(S,pstringread)
$string_read_key_capture(S,pkeyread.INPUT,pkeyread.BASE) = ((PSTRING_CARRIER INTERNED_STRING ($ptascii("2x")),(n_key_current)))
$string_read_key_current(S,pstringread) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("2x")))
$string_read_current_offset(S,pstringread,PSTRING_CARRIER INTERNED_STRING ($ptascii("2x"))) = (2)
$string_read_ready(S,pstringread)
H = $heap_graph(S)
H = {NODES ([HCELL 0,HCELL 1,HCELL 3,HCELL 4,HCELL 10]),EDGES eps,ROOTS ([HCELL 10,HCELL 4,HCELL 3,HCELL 1,HCELL 0]),DEBTS eps}
$heap_owners(H,HCELL n_key_old) = 1
$heap_owners(H,HCELL n_key_current) = 1
$heap_owners(H,HCELL n_base_old) = 0
$task_nodes(STRING_READ_RESULT pstringread) = eps
S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]
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
$retained_outputs(S_done.EVENTS) = $ptascii("2:String offset cast occurred;R:c;B:99;K:2x;Z;")
''') + guards('S') + guards('S_after')
    fields=('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks += ['S = $initial_state(NORMAL)' + ''.join('[.'+field+' = S.'+field+']' for field in fields)]
    checks += lines(r'''
$heap_valid(H)
S.CELL = 3 /\ S.LOCATION = ROOT 2
''')
    derived_start=len(checks)
    checks += lines(r'''
pstringread_ref = pstringread[.KEYREF = true]
S_ref = S[.TODO = (STRING_READ_RESULT pstringread_ref) :: ptask_tail*]
$string_read_source(S_ref,pstringread_ref)
$string_read_key_current(S_ref,pstringread_ref) = eps
S_primitive = S[.STORE[n_key_old] = DEFINED (PINT 1)]
$string_read_key_current(S_primitive,pstringread) = (PINT 1)
$string_read_resume(S_primitive,pstringread) = S_primitive[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_numeric = S[.STORE[n_key_old] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("1")))]
$string_read_key_current(S_numeric,pstringread) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("1")))
$string_read_resume(S_numeric,pstringread) = S_numeric[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_marked = S[.REFCELLS = n_key_old :: S.REFCELLS]
$string_read_key_current(S_marked,pstringread) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("2x")))
S_marked_numeric = S_numeric[.REFCELLS = n_key_old :: S.REFCELLS]
$string_read_key_capture(S_marked_numeric,pkeyread.INPUT,pkeyread.BASE) = eps
$string_read_key_current(S_marked_numeric,pstringread) = eps
S_absent = $unset_name(S,$ptascii("key"))
$lookup(S_absent.ENV,$ptascii("key")) = eps
$heap_valid($heap_graph(S_absent))
$string_read_key_capture(S_absent,pkeyread.INPUT,pkeyread.BASE) = eps
$string_read_key_current(S_absent,pstringread) = (PNULL)
$string_read_resume(S_absent,pstringread) = S_absent[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_absent_ref = S_absent[.TODO = (STRING_READ_RESULT pstringread_ref) :: ptask_tail*]
$string_read_key_current(S_absent_ref,pstringread_ref) = eps
S_retired = S_absent[.ALLOCATIONS = $native_remove_one(S_absent.ALLOCATIONS,HCELL n_key_old)]
$heap_valid($heap_graph(S_retired))
$string_read_key_current(S_retired,pstringread) = (PNULL)
S_bad_heap = S_absent[.ENV = (BIND ($ptascii("other")) 11) :: S_absent.ENV]
~$heap_valid($heap_graph(S_bad_heap))
$string_read_key_current(S_bad_heap,pstringread) = eps
S_text_bounds = S[.STORE[n_key_old] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("99x")))]
$string_read_key_current(S_text_bounds,pstringread) = eps
S_nul = S[.STORE[n_key_old] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([49,0,120]))]
$string_read_key_current(S_nul,pstringread) = eps
S_request = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("2x")]][.STORE[n_key_old] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("2x")))]
$string_carrier_valid(S_request,PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("2x")))
$string_read_key_current(S_request,pstringread) = eps
S_unowned = S[.ERRORHANDLERS = eps]
~$string_read_callback_cast_retained(S_unowned,pstringread)
$string_read_cast_released(S_unowned,pstringread)
$string_read_key_current(S_unowned,pstringread) = eps
$string_read_resume(S_unowned,pstringread) = S_unowned[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]
''')
    for field,value in (("CVS","eps"),("RESULT","KNOWN (PINT 0)"),("BASE","BASE_VALUE (KNOWN pkeyread.BASE)"),("COMPLETION","BUDGET"),("COMPLETION","THROWING 0")):
        checks.append(f'$string_read_key_current(S[.{field} = {value}],pstringread) = eps')
    for field in ("ORIGIN","SOURCES","CODE","STRINGDATA"):
        checks.append(f'$string_read_key_current(S[.{field} = eps],pstringread) = eps')
    return (PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join(
        '  -- '+(check if check.startswith('PhpStep:') else 'if '+check)+'\n' for check in checks),len(checks),len(checks)-derived_start)
