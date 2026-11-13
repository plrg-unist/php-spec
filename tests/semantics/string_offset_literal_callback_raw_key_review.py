"""A selected literal base reads the actual plain CV after a CAST callback."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture') + lines(r'''
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL eps,KEYCELL (n_key),KEYREF false,PHASE STRING_CAST}
pkeyread.PHASE = KEY_NULL /\ pkeyread.VALUE = PBOOL true
pkeyread.INPUT = VARIABLE ($ptascii("key")) 12
pkeyread.LINE = 12
pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))
pkeyread.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)
n_key = 0
S_capture.REFCELLS = eps /\ S_capture.STRINGDATA = eps
$lookup(S_capture.ENV,$ptascii("key")) = (n_key)
$heap_owners($heap_graph(S_capture),HCELL n_key) = 1
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LINE = 12 /\ perrorcall.LEVEL = 2
$error_call_valid(S_before,perrorcall)
''') + guards('S_before') + seek('S_before', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
$lookup(S.ENV,$ptascii("key")) = (n_key)
$lookup(S.ENV,$ptascii("got")) = (1)
pvalue_key = PSTRING ($ptascii("String offset cast occurred"))
S.STORE[n_key] = DEFINED pvalue_key
S.STORE[1] = DEFINED (PINT 99)
S.REFCELLS = eps /\ S.STRINGDATA = eps
S.CELL = 0 /\ S.LOCATION = ROOT 0
S.ERRORHANDLER = {CALLBACK (PSTRING_CARRIER INTERNED_STRING ($ptascii("literalRawKey"))),LEVELS 0}
S.ERRORHANDLERS = eps
~$string_read_callback_retained(S,pstringread)
~$string_read_callback_cast_retained(S,pstringread)
$origin_child((pkeyread.SITE),[PCFIELD 0]) = (porigin_base)
$compiled_read(S,porigin_base) = (PSTRING ($ptascii("abc")))
$compiled_string_value(S,porigin_base,PSTRING ($ptascii("abc"))) = pkeyread.BASE
$key_read_owners_source(S,pkeyread)
$string_read_source(S,pstringread)
$string_read_provider_ready(S,pstringread)
~$string_read_cast_released(S,pstringread)
$string_read_cell(S,n_key)
$string_read_key_capture(S,pkeyread.INPUT,pkeyread.BASE) = ((pvalue_key,pstringread.KEYCELL))
~$string_read_release_scalar(S,pvalue_key)
$string_read_callback_raw_key(S,pstringread) = (pvalue_key)
$string_read_current_offset(S,pstringread,pvalue_key) = (0)
$string_read_key_current(S,pstringread) = (pvalue_key)
$string_read_ready(S,pstringread)
H = $heap_graph(S)
$heap_valid(H)
H = {NODES ([HCELL 0,HCELL 1]),EDGES eps,ROOTS ([HCELL 1,HCELL 0]),DEBTS eps}
$heap_owners(H,HCELL n_key) = 1
$base_nodes(pkeyread.OWNERS) = eps
$task_nodes(STRING_READ_RESULT pstringread) = eps
S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
$string_read_resume(S,pstringread) = S_expected
PhpStep: S ~> S_after
S_after = S_expected
$heap_graph(S_after) = H /\ S_after.EVENTS = S.EVENTS
$drive_steps(S,0) = S[.COMPLETION = BUDGET]
$drive_steps(S,1) = S_expected[.COMPLETION = BUDGET]
S_done = $drive_steps(S_after,1000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("2:String offset cast occurred;R:a;K:String offset cast occurred;Z;")
''') + guards('S') + guards('S_after')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks += ['S = $initial_state(NORMAL)' + ''.join('[.' + field + ' = S.' + field + ']' for field in fields)]
    derived_start = len(checks)
    checks += lines(r'''
S_marked = S[.REFCELLS = [n_key]]
$call_reference_operand_valid(S_marked,REFERENCE n_key)
~$string_read_cell(S_marked,n_key)
$string_read_callback_raw_key(S_marked,pstringread) = (pvalue_key)
$string_read_key_current(S_marked,pstringread) = (pvalue_key)
pstringread_ref = pstringread[.KEYREF = true]
S_ref = S_marked[.TODO = (STRING_READ_RESULT pstringread_ref) :: ptask_tail*]
$string_read_callback_raw_key(S_ref,pstringread_ref) = (pvalue_key)
$string_read_key_current(S_ref,pstringread_ref) = (pvalue_key)
S_unmarked_ref = S[.TODO = (STRING_READ_RESULT pstringread_ref) :: ptask_tail*]
$string_read_callback_raw_key(S_unmarked_ref,pstringread_ref) = eps
$string_read_key_current(S_unmarked_ref,pstringread_ref) = eps
S_absent = $unset_name(S,$ptascii("key"))
$heap_valid($heap_graph(S_absent))
~((HCELL n_key) <- $heap_prune($heap_graph(S_absent)).NODES)
S_absent.STORE[n_key] = DEFINED pvalue_key
$string_read_provider_ready(S_absent,pstringread)
$string_read_callback_raw_key(S_absent,pstringread) = eps
$string_read_key_current(S_absent,pstringread) = eps
$string_read_resume(S_absent,pstringread) = S_absent[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]
pstringread_initial_raw = pstringread[.READ.VALUE = pvalue_key]
S_initial_raw = S[.TODO = (STRING_READ_RESULT pstringread_initial_raw) :: ptask_tail*]
~$string_read_source(S_initial_raw,pstringread_initial_raw)
$string_read_callback_raw_key(S_initial_raw,pstringread_initial_raw) = eps
pvalue_raw = PSTRING ($ptascii("abc"))
pkeyread_raw = pkeyread[.BASE = pvalue_raw][.OWNERS = BASE_VALUE (KNOWN pvalue_raw)]
$key_read_owners_source(S,pkeyread_raw)
pstringread_raw = pstringread[.READ = pkeyread_raw]
S_raw = S[.TODO = (STRING_READ_RESULT pstringread_raw) :: ptask_tail*]
~$string_read_source(S_raw,pstringread_raw)
$string_read_callback_raw_key(S_raw,pstringread_raw) = eps
pvalue_request = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
pkeyread_request = pkeyread[.BASE = pvalue_request][.OWNERS = BASE_VALUE (KNOWN pvalue_request)]
pstringread_request = pstringread[.READ = pkeyread_request]
S_request = S[.STRINGDATA = [$ptascii("abc")]][.TODO = (STRING_READ_RESULT pstringread_request) :: ptask_tail*]
$string_carrier_valid(S_request,pvalue_request)
$string_read_provider_ready(S_request,pstringread_request)
~$key_read_owners_source(S_request,pkeyread_request)
~$string_read_source(S_request,pstringread_request)
$string_read_callback_raw_key(S_request,pstringread_request) = eps
S_registry = S[.STRINGDATA = [$ptascii("String offset cast occurred")]]
$string_read_callback_raw_key(S_registry,pstringread) = (pvalue_key)
pstringread_wrong = pstringread[.READ.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abd"))][.READ.OWNERS = BASE_VALUE (KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("abd"))))]
S_wrong = S[.TODO = (STRING_READ_RESULT pstringread_wrong) :: ptask_tail*]
~$string_read_source(S_wrong,pstringread_wrong)
$string_read_callback_raw_key(S_wrong,pstringread_wrong) = eps
S_bad_heap = S[.ENV = (BIND ($ptascii("ghost")) 99) :: S.ENV]
~$heap_valid($heap_graph(S_bad_heap))
$string_read_callback_raw_key(S_bad_heap,pstringread) = eps
S_retired = S[.ALLOCATIONS = $native_remove_one(S.ALLOCATIONS,HCELL n_key)]
~$heap_valid($heap_graph(S_retired))
$string_read_callback_raw_key(S_retired,pstringread) = eps
''')
    for name, text, offset, byte in (('word','word',0,97),('leading','2x',2,99),('negative','-1',-1,99)):
        value = 'PSTRING ($ptascii(' + json.dumps(text) + '))'
        state = 'S_' + name
        checks += [state + ' = S[.STORE[n_key] = DEFINED (' + value + ')]',
                   '$string_read_callback_raw_key(' + state + ',pstringread) = (' + value + ')',
                   '$string_read_key_current(' + state + ',pstringread) = (' + value + ')',
                   '$string_read_current_offset(' + state + ',pstringread,' + value + ') = (' + str(offset) + ')',
                   '$string_read_resume(' + state + ',pstringread) = ' + state + '[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([' + str(byte) + ']))][.BASE = BASE_VALUE (KNOWN PNULL)]']
    for name, value in (('nul','PSTRING ([50,0,120])'),('invalid','PSTRING ([256])'),('bounds','PSTRING ($ptascii("99"))')):
        state = 'S_' + name
        checks += [state + ' = S[.STORE[n_key] = DEFINED (' + value + ')]',
                   '$string_read_callback_raw_key(' + state + ',pstringread) = eps',
                   '$string_read_current_offset(' + state + ',pstringread,' + value + ') = eps',
                   '$string_read_key_current(' + state + ',pstringread) = eps']
    for field, value in (('PARAMETERBACKINGS','[{FUNCTION pkeyread.SITE,INDEX 0,CELL n_key,LINE 12,VALUE $ptascii("word")}]'),
                         ('PROPREFS','[{CELL n_key,SOURCES eps}]'),
                         ('REFCOERCIONS','[{CELL n_key,SITE pkeyread.SITE,LINE 12,VALUE $ptascii("word")}]')):
        checks.append(f'$string_read_callback_raw_key(S[.{field} = {value}],pstringread) = eps')
    for field, value in (('CVS','eps'),('RESULT','KNOWN (PINT 0)'),('BASE','BASE_VALUE (KNOWN pkeyread.BASE)'),('REPORTING','2'),('SERVICELEFT','(0)'),('COMPLETION','BUDGET'),('COMPLETION','THROWING 0'),('ORIGIN','eps'),('SOURCES','eps'),('CODE','eps')):
        checks.append(f'$string_read_callback_raw_key(S[.{field} = {value}],pstringread) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks), len(checks), len(checks) - derived_start)
