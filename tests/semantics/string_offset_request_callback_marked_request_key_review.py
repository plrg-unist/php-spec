"""A captured plain key follows its live later-marked REQUEST current cell."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 0, 'S_capture') + lines(r'''
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL (n_original),KEYCELL (n_key_old),KEYREF false,PHASE STRING_CAST}
pkeyread.PHASE = KEY_NULL /\ pkeyread.VALUE = PBOOL true
pkeyread.INPUT = VARIABLE ($ptascii("key")) 27
pkeyread.LINE = 27
pkeyread.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
pkeyread.OWNERS = BASE_VALUE (VARIABLE ($ptascii("base")) 27)
n_original = 2 /\ n_key_old = 3
$lookup(S_capture.ENV,$ptascii("base")) = (n_original)
$lookup(S_capture.ENV,$ptascii("key")) = (n_key_old)
$lookup(S_capture.ENV,$ptascii("alias")) = eps
$lookup(S_capture.ENV,$ptascii("got")) = (n_got)
n_got = 4
S_capture.STORE[n_key_old] = DEFINED (PBOOL true)
S_capture.REFCELLS = eps
~$string_read_key_reference(S_capture,pstringread.KEYCELL)
S_capture.STRINGDATA = [$ptascii("abc")]
pvalue_callback = PSTRING_CARRIER INTERNED_STRING ($ptascii("requestReferencedKey"))
S_capture.ERRORHANDLER = {CALLBACK (pvalue_callback),LEVELS 30719}
S_capture.ERRORHANDLERS = [{CALLBACK (pkeyread.BASE),LEVELS 2},{CALLBACK eps,LEVELS 0}]
$heap_owners($heap_graph(S_capture),HCELL n_key_old) = 1
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.CALLBACK = pvalue_callback
perrorcall.LINE = 27 /\ perrorcall.LEVEL = 2
perrorcall.MESSAGE = $ptascii("String offset cast occurred")
$error_call_valid(S_before,perrorcall)
$string_read_source(S_before,pstringread)
''') + guards('S_before') + seek('S_before', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
~pstringread.KEYREF
$lookup(S.ENV,$ptascii("alias")) = (n_key_old)
$lookup(S.ENV,$ptascii("base")) = (n_base)
n_current_cell? = $lookup(S.ENV,$ptascii("key"))
n_current_cell? = (n_key_current)
n_base = 11 /\ n_key_current = 14
S.STORE[n_original] = DEFINED pkeyread.BASE
~((HCELL n_original) <- S.ALLOCATIONS)
S.STORE[n_key_old] = DEFINED (PINT 2)
S.STORE[n_got] = DEFINED (PINT 99)
S.STORE[n_base] = DEFINED (PINT 99)
pvalue_key = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("word"))
S.STORE[n_key_current] = DEFINED pvalue_key
S.REFCELLS = [n_key_current,n_base,n_key_old]
$string_read_key_reference(S,pstringread.KEYCELL)
$literal_reference_plain_cell(S,n_key_old)
$call_reference_operand_valid(S,REFERENCE n_key_current)
$string_read_array_string_cell(S,n_key_current)
~$string_read_cell(S,n_key_current)
~$foreach_released_cell(S,n_key_current)
~$typed_cv_string_released_cell(S,n_key_current)
~$update_released_cell(S,n_key_current)
$propref_at(S.PROPREFS,n_key_current) = eps
$reference_coercion_at(S.REFCOERCIONS,n_key_current) = eps
$parameter_backing_at(S.PARAMETERBACKINGS,n_key_current) = eps
S.STRINGDATA = [$ptascii("abc"),$ptascii("word")]
$string_carrier_valid(S,pvalue_key)
$string_read_base_capture(S,pkeyread.INPUT) = ((pvalue_key,n_current_cell?))
$string_read_capture(S,pkeyread.INPUT) = eps
$string_read_key_capture(S,pkeyread.INPUT,pkeyread.BASE) = eps
$string_read_callback_request_key_owned(S,pstringread,pvalue_key)
$string_read_source(S,pstringread)
$string_read_callback_cast_retained(S,pstringread)
~$string_read_retained(S,pstringread,S.ENV)
$string_read_provider_ready(S,pstringread)
~$string_read_cast_released(S,pstringread)
$string_read_key_current(S,pstringread) = (pvalue_key)
$string_read_current_offset(S,pstringread,pvalue_key) = (0)
$string_read_ready(S,pstringread)
H = $heap_graph(S)
$heap_valid(H)
H.NODES = [HCELL 0,HCELL 1,HCELL 3,HCELL 4,HCELL 11,HCELL 14]
H.EDGES = eps /\ H.DEBTS = eps
$heap_owners(H,HCELL n_key_old) = 1
$heap_owners(H,HCELL n_key_current) = 1
$heap_owners(H,HCELL n_original) = 0
$task_nodes(STRING_READ_RESULT pstringread) = eps
S.CELL = 3 /\ S.LOCATION = ROOT 3
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
$retained_outputs(S_done.EVENTS) = $ptascii("2:String offset cast occurred;R:a;B:99;K:word;A:2;Z;")
''') + guards('S') + guards('S_after')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks += ['S = $initial_state(NORMAL)' + ''.join('[.' + field + ' = S.' + field + ']' for field in fields)]
    derived_start = len(checks)
    checks += lines(r'''
pstringread_ref = pstringread[.KEYREF = true]
S_ref = S[.TODO = (STRING_READ_RESULT pstringread_ref) :: ptask_tail*]
$string_read_key_current(S_ref,pstringread_ref) = (PINT 2)
$string_read_resume(S_ref,pstringread_ref) = S_ref[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_old_changed = S[.STORE[n_key_old] = DEFINED (PINT 99)]
$string_read_key_current(S_old_changed,pstringread) = (pvalue_key)
S_old_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_key_old)]
$string_read_key_current(S_old_unmarked,pstringread) = (pvalue_key)
S_current_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_key_current)]
$string_read_key_current(S_current_unmarked,pstringread) = (pvalue_key)
S_same_slot = S[.ENV = (BIND ($ptascii("key")) n_key_old) :: $unbind(S.ENV,$ptascii("key"))][.STORE[n_key_old] = DEFINED pvalue_key]
$heap_valid($heap_graph(S_same_slot))
$string_read_key_capture(S_same_slot,pkeyread.INPUT,pkeyread.BASE) = eps
$string_read_callback_request_key_owned(S_same_slot,pstringread,pvalue_key)
$string_read_key_current(S_same_slot,pstringread) = (pvalue_key)
S_duplicate = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("word")]]
pvalue_duplicate = PSTRING_CARRIER (REQUEST_STRING 2) ($ptascii("word"))
$string_carrier_valid(S_duplicate,pvalue_duplicate)
~$string_read_callback_request_key_owned(S_duplicate,pstringread,pvalue_duplicate)
$string_read_current_offset(S_duplicate,pstringread,pvalue_duplicate) = eps
$string_read_key_current(S_duplicate,pstringread) = (pvalue_key)
S_replaced = S_duplicate[.STORE[n_key_current] = DEFINED pvalue_duplicate]
$string_read_callback_request_key_owned(S_replaced,pstringread,pvalue_duplicate)
~$string_read_callback_request_key_owned(S_replaced,pstringread,pvalue_key)
$string_read_key_current(S_replaced,pstringread) = (pvalue_duplicate)
S_missing_registry = S[.STRINGDATA = [$ptascii("abc")]]
~$string_carrier_valid(S_missing_registry,pvalue_key)
$string_read_key_current(S_missing_registry,pstringread) = eps
S_wrong_registry = S[.STRINGDATA[1] = $ptascii("2x")]
~$string_carrier_valid(S_wrong_registry,pvalue_key)
$string_read_key_current(S_wrong_registry,pstringread) = eps
S_bad_heap = S[.ENV = (BIND ($ptascii("unused")) 99) :: S.ENV]
~$heap_valid($heap_graph(S_bad_heap))
~$string_read_callback_request_key_owned(S_bad_heap,pstringread,pvalue_key)
$string_read_key_current(S_bad_heap,pstringread) = eps
S_absent = $unset_name(S,$ptascii("key"))
$lookup(S_absent.ENV,$ptascii("key")) = eps
~$string_read_callback_request_key_owned(S_absent,pstringread,pvalue_key)
$string_read_key_current(S_absent,pstringread) = (PNULL)
S_backing = S[.PARAMETERBACKINGS = [{FUNCTION pkeyread.SITE,INDEX 0,CELL n_key_current,LINE 27,VALUE $ptascii("word")}]]
$string_read_base_capture(S_backing,pkeyread.INPUT) = eps
~$string_read_callback_request_key_owned(S_backing,pstringread,pvalue_key)
$string_read_key_current(S_backing,pstringread) = eps
S_unowned = S[.ERRORHANDLERS = eps]
~$string_read_callback_request_key_owned(S_unowned,pstringread,pvalue_key)
$string_read_cast_released(S_unowned,pstringread)
$string_read_key_current(S_unowned,pstringread) = eps
S_interned = S[.STORE[n_key_current] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("word")))]
$string_read_key_capture(S_interned,pkeyread.INPUT,pkeyread.BASE) = eps
$string_read_key_current(S_interned,pstringread) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("word")))
S_raw = S[.STORE[n_key_current] = DEFINED (PSTRING ($ptascii("word")))]
$string_read_key_current(S_raw,pstringread) = (PSTRING ($ptascii("word")))
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING 1) ([49,0,120])
S_nul = S[.STRINGDATA[1] = [49,0,120]][.STORE[n_key_current] = DEFINED pvalue_nul]
$string_carrier_valid(S_nul,pvalue_nul)
~$string_read_callback_request_key_owned(S_nul,pstringread,pvalue_nul)
$string_read_key_current(S_nul,pstringread) = eps
pvalue_bounds = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("99x"))
S_bounds = S[.STRINGDATA[1] = $ptascii("99x")][.STORE[n_key_current] = DEFINED pvalue_bounds]
$string_read_callback_request_key_owned(S_bounds,pstringread,pvalue_bounds)
$string_read_current_offset(S_bounds,pstringread,pvalue_bounds) = (99)
$string_read_key_current(S_bounds,pstringread) = eps
''')
    for name, text, offset, byte in (('numeric','1',1,98), ('leading','2x',2,99), ('fraction','1.75',1,98), ('empty','',0,97), ('negative','-1',-1,99)):
        value = 'PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii(' + json.dumps(text) + '))'
        state = 'S_' + name
        checks += [state + ' = S[.STRINGDATA[1] = $ptascii(' + json.dumps(text) + ')][.STORE[n_key_current] = DEFINED (' + value + ')]',
                   '$string_read_key_current(' + state + ',pstringread) = (' + value + ')',
                   '$string_read_current_offset(' + state + ',pstringread,' + value + ') = (' + str(offset) + ')',
                   '$string_read_resume(' + state + ',pstringread) = ' + state + '[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([' + str(byte) + ']))][.BASE = BASE_VALUE (KNOWN PNULL)]']
    for field, value in (('CVS','eps'), ('RESULT','KNOWN (PINT 0)'), ('BASE','BASE_VALUE (KNOWN pkeyread.BASE)'), ('REPORTING','2'), ('COMPLETION','BUDGET'), ('COMPLETION','THROWING 0')):
        checks.append(f'$string_read_key_current(S[.{field} = {value}],pstringread) = eps')
    for field in ('ORIGIN','SOURCES','CODE'):
        checks.append(f'$string_read_key_current(S[.{field} = eps],pstringread) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
