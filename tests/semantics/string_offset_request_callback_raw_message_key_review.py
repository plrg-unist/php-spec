"""A live marked current cell supplies raw Warning message bytes after CAST."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 0, 'S_capture') + lines(r'''
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL (n_original),KEYCELL (n_old),KEYREF false,PHASE STRING_CAST}
pkeyread.PHASE = KEY_NULL /\ pkeyread.VALUE = PBOOL true
pkeyread.INPUT = VARIABLE ($ptascii("key")) 25
pkeyread.LINE = 25
pkeyread.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
n_original = 2 /\ n_old = 3
S_capture.REFCELLS = eps
$lookup(S_capture.ENV,$ptascii("key")) = (n_old)
$lookup(S_capture.ENV,$ptascii("alias")) = eps
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LINE = 25 /\ perrorcall.LEVEL = 2
$error_call_valid(S_before,perrorcall)
''') + guards('S_before') + seek('S_before', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
~pstringread.KEYREF
$string_read_key_reference(S,pstringread.KEYCELL)
n_current_cell? = $lookup(S.ENV,$ptascii("key"))
n_current_cell? = (n_current)
n_current = 12
$lookup(S.ENV,$ptascii("alias")) = (n_old)
$lookup(S.ENV,$ptascii("base")) = (11)
S.STORE[n_old] = DEFINED (PINT 2)
S.STORE[11] = DEFINED (PINT 99)
pvalue_key = PSTRING ($ptascii("String offset cast occurred"))
S.STORE[n_current] = DEFINED pvalue_key
S.REFCELLS = [n_current,11,n_old]
S.STRINGDATA = [$ptascii("abc")]
S.CELL = 3 /\ S.LOCATION = ROOT 3
~((HCELL n_original) <- S.ALLOCATIONS)
$string_read_source(S,pstringread)
$string_read_callback_cast_retained(S,pstringread)
$string_read_provider_ready(S,pstringread)
~$string_read_cast_released(S,pstringread)
$string_read_base_capture(S,pkeyread.INPUT) = eps
$string_read_capture(S,pkeyread.INPUT) = eps
$string_read_key_capture(S,pkeyread.INPUT,pkeyread.BASE) = eps
~$string_read_release_scalar(S,pvalue_key)
~$string_read_callback_request_key_owned(S,pstringread,pvalue_key)
$string_read_callback_raw_key(S,pstringread) = (pvalue_key)
$call_reference_operand_valid(S,REFERENCE n_current)
~$string_read_array_string_cell(S,n_current)
$string_read_current_offset(S,pstringread,pvalue_key) = (0)
$string_read_key_current(S,pstringread) = (pvalue_key)
$string_read_ready(S,pstringread)
H = $heap_graph(S)
$heap_valid(H)
H = {NODES ([HCELL 0,HCELL 1,HCELL 3,HCELL 4,HCELL 11,HCELL 12]),EDGES eps,ROOTS ([HCELL 12,HCELL 11,HCELL 3,HCELL 4,HCELL 1,HCELL 0]),DEBTS eps}
$heap_owners(H,HCELL n_old) = 1
$heap_owners(H,HCELL n_current) = 1
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
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("2:String offset cast occurred;R:a;B:99;K:String offset cast occurred;A:2;Z;")
''') + guards('S') + guards('S_after')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks += ['S = $initial_state(NORMAL)' + ''.join('[.' + field + ' = S.' + field + ']' for field in fields)]
    derived_start = len(checks)
    checks += lines(r'''

pstringread_ref = pstringread[.KEYREF = true]
S_ref = S[.TODO = (STRING_READ_RESULT pstringread_ref) :: ptask_tail*]
$string_read_key_current(S_ref,pstringread_ref) = (PINT 2)
$string_read_resume(S_ref,pstringread_ref) = S_ref[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_ref_raw = S_ref[.STORE[n_old] = DEFINED pvalue_key]
$string_read_callback_raw_key(S_ref_raw,pstringread_ref) = (pvalue_key)
$string_read_key_current(S_ref_raw,pstringread_ref) = (pvalue_key)
S_old_changed = S[.STORE[n_old] = DEFINED (PINT 99)]
$string_read_key_current(S_old_changed,pstringread) = (pvalue_key)
S_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_current)]
$string_read_callback_raw_key(S_unmarked,pstringread) = (pvalue_key)
$string_read_key_current(S_unmarked,pstringread) = (pvalue_key)
S_absent = $unset_name(S,$ptascii("key"))
$string_read_callback_raw_key(S_absent,pstringread) = eps
$string_read_key_current(S_absent,pstringread) = (PNULL)
S_bad_heap = S[.ENV = (BIND ($ptascii("unused")) 99) :: S.ENV]
~$heap_valid($heap_graph(S_bad_heap))
$string_read_callback_raw_key(S_bad_heap,pstringread) = eps
$string_read_key_current(S_bad_heap,pstringread) = eps
S_retired = S[.ALLOCATIONS = $native_remove_one(S.ALLOCATIONS,HCELL n_current)]
~$heap_valid($heap_graph(S_retired))
$string_read_key_current(S_retired,pstringread) = eps
S_backing = S[.PARAMETERBACKINGS = [{FUNCTION pkeyread.SITE,INDEX 0,CELL n_current,LINE 25,VALUE $ptascii("String offset cast occurred")}]]
$string_read_callback_raw_key(S_backing,pstringread) = eps
$string_read_key_current(S_backing,pstringread) = eps
S_unowned = S[.ERRORHANDLERS = eps]
~$string_read_callback_cast_retained(S_unowned,pstringread)
~$string_read_cast_released(S_unowned,pstringread)
$string_read_key_current(S_unowned,pstringread) = eps
$string_read_resume(S_unowned,pstringread) = S_unowned[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
S_hidden = S_unowned[.STORE[4] = DEFINED pkeyread.BASE]
$string_read_provider_ready(S_hidden,pstringread)
$string_read_key_current(S_hidden,pstringread) = eps
$string_read_resume(S_hidden,pstringread) = S_hidden[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]
S_request = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("word")]][.STORE[n_current] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("word")))]
$string_read_callback_raw_key(S_request,pstringread) = eps
$string_read_key_current(S_request,pstringread) = (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("word")))
S_missing_registry = S_request[.STRINGDATA = S.STRINGDATA]
$string_read_key_current(S_missing_registry,pstringread) = eps
S_interned = S[.STORE[n_current] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("word")))]
$string_read_callback_raw_key(S_interned,pstringread) = eps
$string_read_key_current(S_interned,pstringread) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("word")))
S_primitive = S[.STORE[n_current] = DEFINED (PBOOL false)]
$string_read_callback_raw_key(S_primitive,pstringread) = eps
$string_read_key_current(S_primitive,pstringread) = (PBOOL false)
''')
    for name, text, offset, byte in (('word','word',0,97),('numeric','2',2,99),('leading','2x',2,99),('fraction','1.75',1,98),('empty','',0,97),('negative','-1',-1,99)):
        value = 'PSTRING ($ptascii(' + json.dumps(text) + '))'
        state = 'S_' + name
        checks += [state + ' = S[.STORE[n_current] = DEFINED (' + value + ')]',
                   '$string_read_key_capture(' + state + ',pkeyread.INPUT,pkeyread.BASE) = eps',
                   '$string_read_key_current(' + state + ',pstringread) = (' + value + ')',
                   '$string_read_current_offset(' + state + ',pstringread,' + value + ') = (' + str(offset) + ')',
                   '$string_read_resume(' + state + ',pstringread) = ' + state + '[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([' + str(byte) + ']))][.BASE = BASE_VALUE (KNOWN PNULL)]']
    for name, value in (('nul','PSTRING ([50,0,120])'),('invalid','PSTRING ([256])'),('bounds','PSTRING ($ptascii("99"))')):
        state = 'S_' + name
        checks += [state + ' = S[.STORE[n_current] = DEFINED (' + value + ')]',
                   '$string_read_callback_raw_key(' + state + ',pstringread) = eps',
                   '$string_read_current_offset(' + state + ',pstringread,' + value + ') = eps',
                   '$string_read_key_current(' + state + ',pstringread) = eps']
    for field, value in (('CVS','eps'),('RESULT','KNOWN (PINT 0)'),('BASE','BASE_VALUE (KNOWN pkeyread.BASE)'),('REPORTING','2'),('SERVICELEFT','(0)'),('COMPLETION','BUDGET'),('COMPLETION','THROWING 0')):
        checks.append(f'$string_read_key_current(S[.{field} = {value}],pstringread) = eps')
    for field in ('ORIGIN','SOURCES','CODE'):
        checks.append(f'$string_read_key_current(S[.{field} = eps],pstringread) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks), len(checks), len(checks) - derived_start)
