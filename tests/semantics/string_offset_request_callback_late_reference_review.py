"""An initially plain key follows its CV after a handler retains its old cell."""
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
pstringread.KEYCELL = (n_key_old)
n_key_old = 3
pstringread.READ.VALUE = PBOOL false
pstringread.READ.INPUT = VARIABLE ($ptascii("key")) 21
pstringread.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
S_before.REFCELLS = eps
$lookup(S_before.ENV,$ptascii("alias")) = eps
$heap_owners($heap_graph(S_before),HCELL n_key_old) = 1
PhpStep: S_before ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.CALLBACK = pstringread.READ.BASE
$error_call_valid(S_dispatch,perrorcall)
''') + guards('S_before') + seek('S_dispatch', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
~pstringread.KEYREF
$lookup(S.ENV,$ptascii("alias")) = (n_key_old)
$lookup(S.ENV,$ptascii("key")) = (n_key_current)
$lookup(S.ENV,$ptascii("base")) = (n_base)
n_key_current = 12 /\ n_base = 11
S.STORE[n_key_old] = DEFINED (PINT 1)
S.STORE[n_key_current] = DEFINED (PINT 2)
S.STORE[n_base] = DEFINED (PINT 99)
S.STORE[4] = DEFINED (PINT 99)
S.REFCELLS = [n_key_current,n_base,n_key_old]
$literal_reference_plain_cell(S,n_key_old)
$call_reference_operand_valid(S,REFERENCE n_key_current)
$string_read_source(S,pstringread)
$string_read_callback_cast_retained(S,pstringread)
$string_read_provider_ready(S,pstringread)
$string_read_key_capture(S,pstringread.READ.INPUT,pstringread.READ.BASE) = ((PINT 2,(n_key_current)))
$string_read_key_current(S,pstringread) = (PINT 2)
$string_read_ready(S,pstringread)
H = $heap_graph(S)
H = {NODES ([HCELL 0,HCELL 1,HCELL 3,HCELL 4,HCELL 11,HCELL 12]),EDGES eps,ROOTS ([HCELL 12,HCELL 11,HCELL 3,HCELL 4,HCELL 1,HCELL 0]),DEBTS eps}
$heap_owners(H,HCELL n_key_old) = 1
$heap_owners(H,HCELL n_key_current) = 1
$heap_owners(H,HCELL 2) = 0
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
S_done.STORE[4] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([99]))
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("2:String offset cast occurred;R:c;B:99;K:2;A:1;Z;")
''') + guards('S')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks += ['S = $initial_state(NORMAL)' + ''.join('[.' + field + ' = S.' + field + ']' for field in fields)]
    derived_start = len(checks)
    checks += lines(r'''
pstringread_ref = pstringread[.KEYREF = true]
S_ref = S[.TODO = (STRING_READ_RESULT pstringread_ref) :: ptask_tail*]
$string_read_source(S_ref,pstringread_ref)
$string_read_key_current(S_ref,pstringread_ref) = (PINT 1)
$string_read_resume(S_ref,pstringread_ref) = S_ref[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_old_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_key_old)]
$string_read_key_current(S_old_unmarked,pstringread) = (PINT 2)
S_old_bounds = S[.STORE[n_key_old] = DEFINED (PINT 99)]
$string_read_key_current(S_old_bounds,pstringread) = (PINT 2)
S_current_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_key_current)]
$string_read_key_current(S_current_unmarked,pstringread) = eps
S_current_bool = S[.STORE[n_key_current] = DEFINED (PBOOL false)]
$string_read_key_current(S_current_bool,pstringread) = (PBOOL false)
$string_read_resume(S_current_bool,pstringread) = S_current_bool[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_current_bounds = S[.STORE[n_key_current] = DEFINED (PINT 99)]
$string_read_key_current(S_current_bounds,pstringread) = eps
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
