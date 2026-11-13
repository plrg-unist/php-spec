"""A late ordinary REQUEST key owns the exact header consumed after Warning."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 0, 'S_capture') + lines(r'''
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL (n_base_old),KEYCELL (n_key),KEYREF false,PHASE STRING_CAST}
pkeyread.INPUT = VARIABLE ($ptascii("key")) 23
pkeyread.LINE = 23 /\ pkeyread.PHASE = KEY_NULL
pkeyread.VALUE = PBOOL true
pkeyread.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
pkeyread.OWNERS = BASE_VALUE (VARIABLE ($ptascii("base")) 23)
n_base_old = 2 /\ n_key = 3
S_capture.REFCELLS = eps
~$string_read_key_reference(S_capture,pstringread.KEYCELL)
$lookup(S_capture.ENV,$ptascii("key")) = (n_key)
$lookup(S_capture.ENV,$ptascii("alias")) = eps
$lookup(S_capture.ENV,$ptascii("got")) = (n_got)
n_got = 4
S_capture.STORE[n_key] = DEFINED (PBOOL true)
$heap_owners($heap_graph(S_capture),HCELL n_key) = 1
pvalue_current = PSTRING_CARRIER INTERNED_STRING ($ptascii("requestReboundKey"))
S_capture.ERRORHANDLER = {CALLBACK (pvalue_current),LEVELS 30719}
S_capture.ERRORHANDLERS = [{CALLBACK (pkeyread.BASE),LEVELS 2},{CALLBACK eps,LEVELS 0}]
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.CALLBACK = pvalue_current
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 23
perrorcall.MESSAGE = $ptascii("String offset cast occurred")
$error_call_valid(S_before,perrorcall)
''') + guards('S_before') + seek('S_before', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
$lookup(S.ENV,$ptascii("base")) = (n_base)
$lookup(S.ENV,$ptascii("key")) = (n_key)
$lookup(S.ENV,$ptascii("alias")) = eps
n_base = 10
S.STORE[n_base_old] = DEFINED pkeyread.BASE
~((HCELL n_base_old) <- S.ALLOCATIONS)
pvalue_key = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("word"))
S.STORE[n_key] = DEFINED pvalue_key
S.STORE[n_base] = DEFINED (PINT 99)
S.STORE[n_got] = DEFINED (PINT 99)
S.REFCELLS = [n_base]
$call_reference_operand_valid(S,REFERENCE n_base)
~$call_reference_operand_valid(S,REFERENCE n_key)
$string_read_cell(S,n_key)
~$literal_reference_plain_cell(S,n_key)
~$string_read_array_string_cell(S,n_key)
S.STRINGDATA = [$ptascii("abc"),$ptascii("word")]
S.ERRORHANDLER = S_capture.ERRORHANDLER
S.ERRORHANDLERS = S_capture.ERRORHANDLERS
$string_carrier_valid(S,pvalue_key)
~$string_read_release_scalar(S,pvalue_key)
$string_read_release_cells(S,0,S.ALLOCATIONS)
~$string_read_release_handlers(S,0,S.ERRORHANDLER :: S.ERRORHANDLERS)
$string_read_source(S,pstringread)
$string_read_callback_cast_retained(S,pstringread)
$string_read_provider_ready(S,pstringread)
~$string_read_cast_released(S,pstringread)
$string_read_capture(S,pkeyread.INPUT) = ((pvalue_key,pstringread.KEYCELL))
$string_read_key_capture(S,pkeyread.INPUT,pkeyread.BASE) = ((pvalue_key,pstringread.KEYCELL))
$string_read_callback_request_key_owned(S,pstringread,pvalue_key)
$string_read_key_current(S,pstringread) = (pvalue_key)
$string_read_current_offset(S,pstringread,pvalue_key) = (0)
$string_read_offset(pvalue_key) = eps
$string_read_ready(S,pstringread)
H = $heap_graph(S)
H = {NODES ([HCELL 0,HCELL 1,HCELL 3,HCELL 4,HCELL 10]),EDGES eps,ROOTS ([HCELL 10,HCELL 4,HCELL 3,HCELL 1,HCELL 0]),DEBTS eps}
$heap_valid(H)
$heap_owners(H,HCELL n_key) = 1
$heap_owners(H,HCELL n_base_old) = 0
$task_nodes(STRING_READ_RESULT pstringread) = eps
S.CELL = 3 /\ S.LOCATION = ROOT 2
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
$retained_outputs(S_done.EVENTS) = $ptascii("2:String offset cast occurred;R:a;B:99;K:word;Z;")
''') + guards('S') + guards('S_after')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks += ['S = $initial_state(NORMAL)' + ''.join('[.' + f + ' = S.' + f + ']' for f in fields)]
    derived_start = len(checks)
    checks += lines(r'''
S_duplicate = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("word")]]
pvalue_duplicate = PSTRING_CARRIER (REQUEST_STRING 2) ($ptascii("word"))
$string_carrier_valid(S_duplicate,pvalue_duplicate)
~$string_read_callback_request_key_owned(S_duplicate,pstringread,pvalue_duplicate)
$string_read_current_offset(S_duplicate,pstringread,pvalue_duplicate) = eps
$string_read_key_current(S_duplicate,pstringread) = (pvalue_key)
S_replaced = S_duplicate[.STORE[n_key] = DEFINED pvalue_duplicate]
$string_read_callback_request_key_owned(S_replaced,pstringread,pvalue_duplicate)
~$string_read_callback_request_key_owned(S_replaced,pstringread,pvalue_key)
$string_read_key_current(S_replaced,pstringread) = (pvalue_duplicate)
S_missing = S[.STRINGDATA = [$ptascii("abc")]]
~$string_carrier_valid(S_missing,pvalue_key)
~$string_read_callback_request_key_owned(S_missing,pstringread,pvalue_key)
$string_read_key_current(S_missing,pstringread) = eps
S_forged = S[.STRINGDATA[1] = $ptascii("1")]
~$string_carrier_valid(S_forged,pvalue_key)
$string_read_key_current(S_forged,pstringread) = eps
S_bad_heap = S[.ENV = (BIND ($ptascii("unused")) 13) :: S.ENV]
~$heap_valid($heap_graph(S_bad_heap))
~$string_read_callback_request_key_owned(S_bad_heap,pstringread,pvalue_key)
$string_read_key_current(S_bad_heap,pstringread) = eps
S_marked = S[.REFCELLS = n_key :: S.REFCELLS]
$string_read_capture(S_marked,pkeyread.INPUT) = eps
~$string_read_callback_request_key_owned(S_marked,pstringread,pvalue_key)
$string_read_key_current(S_marked,pstringread) = eps
S_marked_leading = S_marked[.STRINGDATA[1] = $ptascii("2x")][.STORE[n_key] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("2x")))]
$string_carrier_valid(S_marked_leading,PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("2x")))
~$string_read_callback_request_key_owned(S_marked_leading,pstringread,PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("2x")))
$string_read_key_current(S_marked_leading,pstringread) = eps
pstringread_ref = pstringread[.KEYREF = true]
S_ref = S[.TODO = (STRING_READ_RESULT pstringread_ref) :: ptask_tail*]
~$string_read_callback_request_key_owned(S_ref,pstringread_ref,pvalue_key)
$string_read_key_current(S_ref,pstringread_ref) = eps
S_absent = $unset_name(S,$ptascii("key"))
$lookup(S_absent.ENV,$ptascii("key")) = eps
$heap_valid($heap_graph(S_absent))
~$string_read_callback_request_key_owned(S_absent,pstringread,pvalue_key)
$string_read_current_offset(S_absent,pstringread,pvalue_key) = eps
$string_read_key_current(S_absent,pstringread) = (PNULL)
S_unowned = S[.ERRORHANDLERS = eps]
~$string_read_callback_request_key_owned(S_unowned,pstringread,pvalue_key)
$string_read_key_current(S_unowned,pstringread) = eps
$string_read_cast_released(S_unowned,pstringread)
$string_read_resume(S_unowned,pstringread) = S_unowned[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]
S_keeper = S_unowned[.STORE[n_got] = DEFINED pkeyread.BASE]
$string_read_provider_ready(S_keeper,pstringread)
~$string_read_callback_request_key_owned(S_keeper,pstringread,pvalue_key)
$string_read_resume(S_keeper,pstringread) = S_keeper[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]
S_bounds = S[.STRINGDATA[1] = $ptascii("99x")][.STORE[n_key] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("99x")))]
$string_read_callback_request_key_owned(S_bounds,pstringread,PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("99x")))
$string_read_current_offset(S_bounds,pstringread,PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("99x"))) = (99)
$string_read_key_current(S_bounds,pstringread) = eps
S_nul = S[.STRINGDATA[1] = ([49,0,120])][.STORE[n_key] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ([49,0,120]))]
$string_carrier_valid(S_nul,PSTRING_CARRIER (REQUEST_STRING 1) ([49,0,120]))
~$string_read_callback_request_key_owned(S_nul,pstringread,PSTRING_CARRIER (REQUEST_STRING 1) ([49,0,120]))
$string_read_key_current(S_nul,pstringread) = eps
S_byte = S[.STRINGDATA[1] = ([256])][.STORE[n_key] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ([256]))]
~$string_carrier_valid(S_byte,PSTRING_CARRIER (REQUEST_STRING 1) ([256]))
$string_read_key_current(S_byte,pstringread) = eps
S_raw = S[.STORE[n_key] = DEFINED (PSTRING ($ptascii("word")))]
$string_read_key_current(S_raw,pstringread) = eps
''')
    for name, text, offset, byte in (('numeric','1',1,98), ('leading','2x',2,99), ('fraction','1.75',1,98), ('empty','',0,97)):
        value = 'PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii(' + json.dumps(text) + '))'
        state = 'S_' + name
        checks += [state + ' = S[.STRINGDATA[1] = $ptascii(' + json.dumps(text) + ')][.STORE[n_key] = DEFINED (' + value + ')]',
                   '$string_read_key_current(' + state + ',pstringread) = (' + value + ')',
                   '$string_read_current_offset(' + state + ',pstringread,' + value + ') = (' + str(offset) + ')',
                   '$string_read_resume(' + state + ',pstringread) = ' + state + '[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([' + str(byte) + ']))][.BASE = BASE_VALUE (KNOWN PNULL)]']
    for field, value in (('CVS','eps'), ('RESULT','KNOWN (PINT 0)'), ('BASE','BASE_VALUE (KNOWN pkeyread.BASE)'), ('COMPLETION','BUDGET'), ('COMPLETION','THROWING 0')):
        checks.append(f'$string_read_key_current(S[.{field} = {value}],pstringread) = eps')
    for field in ('ORIGIN','SOURCES','CODE'):
        checks.append(f'~$string_read_callback_request_key_owned(S[.{field} = eps],pstringread,pvalue_key)')
        checks.append(f'$string_read_key_current(S[.{field} = eps],pstringread) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
