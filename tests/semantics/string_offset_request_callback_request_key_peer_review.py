"""A live initial wrapper owns late REQUEST text after its current name is unset."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 0, 'S_capture') + lines(r'''
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL (n_base_old),KEYCELL (n_key_old),KEYREF true,PHASE STRING_CAST}
pkeyread.INPUT = VARIABLE ($ptascii("key")) 26
pkeyread.LINE = 26 /\ pkeyread.PHASE = KEY_NULL
pkeyread.VALUE = PBOOL true
pkeyread.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
pkeyread.OWNERS = BASE_VALUE (VARIABLE ($ptascii("base")) 26)
n_base_old = 2 /\ n_key_old = 3
S_capture.REFCELLS = [n_key_old]
$string_read_key_reference(S_capture,pstringread.KEYCELL)
$lookup(S_capture.ENV,$ptascii("key")) = (n_key_old)
$lookup(S_capture.ENV,$ptascii("alias")) = (n_key_old)
$lookup(S_capture.ENV,$ptascii("got")) = (n_got)
n_got = 4
S_capture.STORE[n_key_old] = DEFINED (PBOOL true)
$heap_owners($heap_graph(S_capture),HCELL n_key_old) = 2
pvalue_current = PSTRING_CARRIER INTERNED_STRING ($ptascii("requestReferencedKey"))
S_capture.ERRORHANDLER = {CALLBACK (pvalue_current),LEVELS 30719}
S_capture.ERRORHANDLERS = [{CALLBACK (pkeyread.BASE),LEVELS 2},{CALLBACK eps,LEVELS 0}]
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.CALLBACK = pvalue_current
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 26
perrorcall.MESSAGE = $ptascii("String offset cast occurred")
$error_call_valid(S_before,perrorcall)
''') + guards('S_before') + seek('S_before', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
$lookup(S.ENV,$ptascii("base")) = (n_base)
$lookup(S.ENV,$ptascii("key")) = eps
$lookup(S.ENV,$ptascii("alias")) = (n_key_old)
n_base = 10
pvalue_request = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("2x"))
S.STORE[n_base_old] = DEFINED pkeyread.BASE
~((HCELL n_base_old) <- S.ALLOCATIONS)
S.STORE[n_key_old] = DEFINED pvalue_request
S.STORE[n_base] = DEFINED (PINT 99)
S.STORE[n_got] = DEFINED (PINT 99)
S.REFCELLS = [n_base,n_key_old]
S.STRINGDATA = [$ptascii("abc"),$ptascii("2x")]
S.CELL = 3 /\ S.LOCATION = ROOT 2
S.ERRORHANDLER = S_capture.ERRORHANDLER
S.ERRORHANDLERS = S_capture.ERRORHANDLERS
$call_reference_operand_valid(S,REFERENCE n_key_old)
$string_read_array_string_cell(S,n_key_old)
~$string_read_cell(S,n_key_old)
~$literal_reference_plain_cell(S,n_key_old)
~$string_read_release_scalar(S,pvalue_request)
$string_read_source(S,pstringread)
$string_read_callback_cast_retained(S,pstringread)
$string_read_provider_ready(S,pstringread)
~$string_read_cast_released(S,pstringread)
$string_read_key_capture(S,pkeyread.INPUT,pkeyread.BASE) = eps
$string_read_callback_request_key_owned(S,pstringread,pvalue_request)
$string_read_key_current(S,pstringread) = (pvalue_request)
$string_read_current_offset(S,pstringread,pvalue_request) = (2)
$string_read_ready(S,pstringread)
H = $heap_graph(S)
H = {NODES ([HCELL 0,HCELL 1,HCELL 3,HCELL 4,HCELL 10]),EDGES eps,ROOTS ([HCELL 10,HCELL 4,HCELL 3,HCELL 1,HCELL 0]),DEBTS eps}
$heap_owners(H,HCELL n_key_old) = 1
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
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0
$lookup(S_done.ENV,$ptascii("key")) = eps
S_done.STORE[n_key_old] = DEFINED pvalue_request
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("2:String offset cast occurred;R:c;B:99;K:;A:2x;Z;")
''') + guards('S') + guards('S_after')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks += ['S = $initial_state(NORMAL)' + ''.join('[.' + field + ' = S.' + field + ']' for field in fields)]
    derived_start = len(checks)
    checks += lines(r'''
pstringread_plain = pstringread[.KEYREF = false]
S_plain = S[.TODO = (STRING_READ_RESULT pstringread_plain) :: ptask_tail*]
$string_read_source(S_plain,pstringread_plain)
~$string_read_callback_request_key_owned(S_plain,pstringread_plain,pvalue_request)
$string_read_current_offset(S_plain,pstringread_plain,pvalue_request) = eps
$string_read_key_current(S_plain,pstringread_plain) = (PNULL)
$string_read_resume(S_plain,pstringread_plain) = S_plain[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_retarget = S[.ENV = (BIND ($ptascii("key")) n_got) :: S.ENV][.STORE[n_got] = DEFINED (PINT 1)]
$heap_valid($heap_graph(S_retarget))
$string_read_key_current(S_retarget,pstringread) = (pvalue_request)
S_retarget_plain = S_retarget[.TODO = (STRING_READ_RESULT pstringread_plain) :: ptask_tail*]
$string_read_key_current(S_retarget_plain,pstringread_plain) = (PINT 1)
$string_read_resume(S_retarget_plain,pstringread_plain) = S_retarget_plain[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_equal = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("2x")]]
pvalue_equal = PSTRING_CARRIER (REQUEST_STRING 2) ($ptascii("2x"))
$string_carrier_valid(S_equal,pvalue_equal)
~$string_read_callback_request_key_owned(S_equal,pstringread,pvalue_equal)
$string_read_current_offset(S_equal,pstringread,pvalue_equal) = eps
$string_read_key_current(S_equal,pstringread) = (pvalue_request)
S_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_key_old)]
$heap_valid($heap_graph(S_unmarked))
~$string_read_callback_request_key_owned(S_unmarked,pstringread,pvalue_request)
$string_read_key_current(S_unmarked,pstringread) = eps
S_unrooted = S[.ENV = $unbind(S.ENV,$ptascii("alias"))]
$heap_valid($heap_graph(S_unrooted))
~((HCELL n_key_old) <- $heap_prune($heap_graph(S_unrooted)).NODES)
~$string_read_callback_request_key_owned(S_unrooted,pstringread,pvalue_request)
$string_read_key_current(S_unrooted,pstringread) = eps
S_retired = S_unrooted[.ALLOCATIONS = $native_remove_one(S_unrooted.ALLOCATIONS,HCELL n_key_old)][.REFCELLS = $literal_reference_delete(S_unrooted.REFCELLS,n_key_old)]
$heap_valid($heap_graph(S_retired))
S_retired.STORE[n_key_old] = DEFINED pvalue_request
$string_carrier_valid(S_retired,pvalue_request)
$string_read_source(S_retired,pstringread)
~$string_read_callback_request_key_owned(S_retired,pstringread,pvalue_request)
$string_read_key_current(S_retired,pstringread) = eps
S_bad_heap = S[.ENV = (BIND ($ptascii("other")) 99) :: S.ENV]
~$heap_valid($heap_graph(S_bad_heap))
~$string_read_callback_request_key_owned(S_bad_heap,pstringread,pvalue_request)
$string_read_key_current(S_bad_heap,pstringread) = eps
S_missing_registry = S[.STRINGDATA = [$ptascii("abc")]]
~$string_carrier_valid(S_missing_registry,pvalue_request)
~$string_read_callback_request_key_owned(S_missing_registry,pstringread,pvalue_request)
$string_read_key_current(S_missing_registry,pstringread) = eps
S_wrong_registry = S[.STRINGDATA[1] = $ptascii("word")]
~$string_carrier_valid(S_wrong_registry,pvalue_request)
$string_read_key_current(S_wrong_registry,pstringread) = eps
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING 1) ([50,0,120])
S_nul = S[.STRINGDATA[1] = [50,0,120]][.STORE[n_key_old] = DEFINED pvalue_nul]
$string_carrier_valid(S_nul,pvalue_nul)
~$string_read_callback_request_key_owned(S_nul,pstringread,pvalue_nul)
$string_read_key_current(S_nul,pstringread) = eps
pvalue_bounds = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("99x"))
S_bounds = S[.STRINGDATA[1] = $ptascii("99x")][.STORE[n_key_old] = DEFINED pvalue_bounds]
$string_read_callback_request_key_owned(S_bounds,pstringread,pvalue_bounds)
$string_read_current_offset(S_bounds,pstringread,pvalue_bounds) = (99)
$string_read_key_current(S_bounds,pstringread) = eps
pvalue_word = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("word"))
S_word = S[.STRINGDATA[1] = $ptascii("word")][.STORE[n_key_old] = DEFINED pvalue_word]
$string_read_key_current(S_word,pstringread) = (pvalue_word)
$string_read_resume(S_word,pstringread) = S_word[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_unowned = S[.ERRORHANDLERS = eps]
~$string_read_callback_cast_retained(S_unowned,pstringread)
~$string_read_callback_request_key_owned(S_unowned,pstringread,pvalue_request)
$string_read_cast_released(S_unowned,pstringread)
$string_read_key_current(S_unowned,pstringread) = eps
$string_read_resume(S_unowned,pstringread) = S_unowned[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]
S_keeper = S_unowned[.STORE[n_got] = DEFINED pkeyread.BASE]
$string_read_provider_ready(S_keeper,pstringread)
~$string_read_callback_request_key_owned(S_keeper,pstringread,pvalue_request)
$string_read_key_current(S_keeper,pstringread) = eps
$string_read_resume(S_keeper,pstringread) = S_keeper[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]
S_backing = S[.PARAMETERBACKINGS = [{FUNCTION pkeyread.SITE,INDEX 0,CELL n_key_old,LINE 26,VALUE $ptascii("2x")}]]
~$string_read_callback_request_key_owned(S_backing,pstringread,pvalue_request)
$string_read_key_current(S_backing,pstringread) = eps
''')
    for field, value in (('CVS','eps'),('RESULT','KNOWN (PINT 0)'),('BASE','BASE_VALUE (KNOWN pkeyread.BASE)'),('PARAMETERSEQ','1'),('SERVICELEFT','(0)'),('REPORTING','2'),('COMPLETION','BUDGET'),('COMPLETION','THROWING 0')):
        checks.append(f'$string_read_key_current(S[.{field} = {value}],pstringread) = eps')
    for field in ('ORIGIN','SOURCES','CODE','STRINGDATA'):
        checks.append(f'$string_read_key_current(S[.{field} = eps],pstringread) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks), len(checks), len(checks) - derived_start)
