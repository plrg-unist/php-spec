"""A literal base reads the saved initial wrapper independently of its name."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture') + lines(r'''
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL eps,KEYCELL (n_old),KEYREF true,PHASE STRING_CAST}
pkeyread.INPUT = VARIABLE ($ptascii("key")) 16
pkeyread.LINE = 16 /\ pkeyread.PHASE = KEY_NULL
pkeyread.VALUE = PBOOL true
pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))
pkeyread.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)
n_old = 0
$lookup(S_capture.ENV,$ptascii("key")) = (n_old)
$lookup(S_capture.ENV,$ptascii("alias")) = (n_old)
$lookup(S_capture.ENV,$ptascii("got")) = (n_got)
n_got = 1
S_capture.REFCELLS = [n_old]
S_capture.STORE[n_old] = DEFINED (PBOOL true)
$heap_owners($heap_graph(S_capture),HCELL n_old) = 2
$string_read_key_reference(S_capture,pstringread.KEYCELL)
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 16
perrorcall.MESSAGE = $ptascii("String offset cast occurred")
$error_call_valid(S_before,perrorcall)
''') + guards('S_before') + seek('S_before', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
$lookup(S.ENV,$ptascii("key")) = (n_current)
$lookup(S.ENV,$ptascii("alias")) = (n_old)
$lookup(S.ENV,$ptascii("got")) = (n_got)
n_current = 7
pvalue_key = PSTRING ($ptascii("String offset cast occurred"))
S.STORE[n_old] = DEFINED pvalue_key
S.STORE[n_current] = DEFINED (PINT 2)
S.STORE[n_got] = DEFINED (PINT 99)
S.REFCELLS = [n_current,n_old]
S.CELL = 7 /\ S.LOCATION = ROOT 0
S.STRINGDATA = eps
S.ERRORHANDLER = {CALLBACK (PSTRING_CARRIER INTERNED_STRING ($ptascii("literalRawReferenceKey"))),LEVELS 0}
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
$string_read_key_reference(S,pstringread.KEYCELL)
$call_reference_operand_valid(S,REFERENCE n_old)
~$string_read_cell(S,n_old)
$string_read_key_capture(S,pkeyread.INPUT,pkeyread.BASE) = ((PINT 2,(n_current)))
~$string_read_release_scalar(S,pvalue_key)
~$string_read_callback_request_key_owned(S,pstringread,pvalue_key)
$string_read_callback_raw_key(S,pstringread) = (pvalue_key)
$string_read_current_offset(S,pstringread,pvalue_key) = (0)
$string_read_key_current(S,pstringread) = (pvalue_key)
$string_read_ready(S,pstringread)
H = $heap_graph(S)
$heap_valid(H)
H = {NODES ([HCELL 0,HCELL 1,HCELL 7]),EDGES eps,ROOTS ([HCELL 7,HCELL 1,HCELL 0]),DEBTS eps}
$heap_owners(H,HCELL n_old) = 1
$heap_owners(H,HCELL n_current) = 1
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
S_done.STORE[n_old] = DEFINED pvalue_key
S_done.STORE[n_current] = DEFINED (PINT 2)
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("2:String offset cast occurred;R:a;K:2;A:String offset cast occurred;Z;")
''') + guards('S') + guards('S_after')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks += ['S = $initial_state(NORMAL)' + ''.join('[.' + field + ' = S.' + field + ']' for field in fields)]
    derived_start = len(checks)
    checks += lines(r'''
S_current_raw = S[.STORE[n_current] = DEFINED (PSTRING ($ptascii("2")))]
$heap_valid($heap_graph(S_current_raw))
$string_read_callback_raw_key(S_current_raw,pstringread) = (pvalue_key)
$string_read_key_current(S_current_raw,pstringread) = (pvalue_key)
$string_read_resume(S_current_raw,pstringread) = S_current_raw[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
pstringread_plain = pstringread[.KEYREF = false]
S_plain = S_current_raw[.TODO = (STRING_READ_RESULT pstringread_plain) :: ptask_tail*]
$string_read_callback_raw_key(S_plain,pstringread_plain) = (PSTRING ($ptascii("2")))
$string_read_key_current(S_plain,pstringread_plain) = (PSTRING ($ptascii("2")))
$string_read_resume(S_plain,pstringread_plain) = S_plain[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_absent = $unset_name(S,$ptascii("key"))
$heap_valid($heap_graph(S_absent))
$lookup(S_absent.ENV,$ptascii("key")) = eps
$heap_owners($heap_graph(S_absent),HCELL n_old) = 1
$string_read_callback_raw_key(S_absent,pstringread) = (pvalue_key)
$string_read_key_current(S_absent,pstringread) = (pvalue_key)
$string_read_resume(S_absent,pstringread) = S_absent[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_same_slot = S_absent[.ENV = (BIND ($ptascii("key")) n_old) :: S_absent.ENV]
$heap_valid($heap_graph(S_same_slot))
$heap_owners($heap_graph(S_same_slot),HCELL n_old) = 2
$string_read_key_current(S_same_slot,pstringread) = (pvalue_key)
S_dead = $unset_name(S,$ptascii("alias"))
$heap_valid($heap_graph(S_dead))
S_dead.STORE[n_old] = DEFINED pvalue_key
~((HCELL n_old) <- $heap_prune($heap_graph(S_dead)).NODES)
$heap_owners($heap_graph(S_dead),HCELL n_old) = 0
$string_read_provider_ready(S_dead,pstringread)
$string_read_callback_raw_key(S_dead,pstringread) = eps
$string_read_key_current(S_dead,pstringread) = eps
$string_read_resume(S_dead,pstringread) = S_dead[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]
S_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_old)]
$heap_valid($heap_graph(S_unmarked))
$string_read_cell(S_unmarked,n_old)
$string_read_callback_raw_key(S_unmarked,pstringread) = eps
$string_read_key_current(S_unmarked,pstringread) = eps
S_bad_heap = S[.ENV = (BIND ($ptascii("ghost")) 99) :: S.ENV]
~$heap_valid($heap_graph(S_bad_heap))
$string_read_key_current(S_bad_heap,pstringread) = eps
S_retired = S[.ALLOCATIONS = $native_remove_one(S.ALLOCATIONS,HCELL n_old)]
~$heap_valid($heap_graph(S_retired))
$string_read_key_current(S_retired,pstringread) = eps
pstringread_raw_base = pstringread[.READ.BASE = PSTRING ($ptascii("abc"))][.READ.OWNERS = BASE_VALUE (KNOWN (PSTRING ($ptascii("abc"))))]
S_raw_base = S[.TODO = (STRING_READ_RESULT pstringread_raw_base) :: ptask_tail*]
~$string_read_source(S_raw_base,pstringread_raw_base)
$string_read_callback_raw_key(S_raw_base,pstringread_raw_base) = eps
pvalue_request = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
pstringread_request = pstringread[.READ.BASE = pvalue_request][.READ.OWNERS = BASE_VALUE (KNOWN pvalue_request)]
S_request = S[.TODO = (STRING_READ_RESULT pstringread_request) :: ptask_tail*][.STRINGDATA = [$ptascii("abc")]]
$string_carrier_valid(S_request,pvalue_request)
$string_read_provider_ready(S_request,pstringread_request)
~$string_read_source(S_request,pstringread_request)
$string_read_callback_raw_key(S_request,pstringread_request) = eps
S_registry = S[.STRINGDATA = [$ptascii("String offset cast occurred")]]
$string_read_key_current(S_registry,pstringread) = (pvalue_key)
pvalue_carrier = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("String offset cast occurred"))
$string_carrier_valid(S_registry,pvalue_carrier)
~$string_read_callback_request_key_owned(S_registry,pstringread,pvalue_carrier)
$string_read_current_offset(S_registry,pstringread,pvalue_carrier) = eps
pstringread_initial_raw = pstringread[.READ.VALUE = pvalue_key]
S_initial_raw = S[.TODO = (STRING_READ_RESULT pstringread_initial_raw) :: ptask_tail*]
~$string_read_source(S_initial_raw,pstringread_initial_raw)
$string_read_callback_raw_key(S_initial_raw,pstringread_initial_raw) = eps
pstringread_missing = pstringread[.KEYCELL = eps]
S_missing = S[.TODO = (STRING_READ_RESULT pstringread_missing) :: ptask_tail*]
$string_read_callback_raw_key(S_missing,pstringread_missing) = eps
''')
    for name, value in (('nul','PSTRING ([50,0,120])'),('invalid','PSTRING ([256])'),
                        ('bounds','PSTRING ($ptascii("99"))'),('array','PARRAY 0')):
        state = 'S_' + name
        checks += [state + ' = S[.STORE[n_old] = DEFINED (' + value + ')]',
                   '$string_read_callback_raw_key(' + state + ',pstringread) = eps',
                   '$string_read_key_current(' + state + ',pstringread) = eps']
    for name, text, offset, byte in (('word','word',0,97),('fraction','1.75',1,98),
                                    ('negative','-1',-1,99),('leading','2x',2,99),('empty','',0,97)):
        value = 'PSTRING ($ptascii(' + json.dumps(text) + '))'
        state = 'S_' + name
        checks += [state + ' = S[.STORE[n_old] = DEFINED (' + value + ')]',
                   '$string_read_callback_raw_key(' + state + ',pstringread) = (' + value + ')',
                   '$string_read_key_current(' + state + ',pstringread) = (' + value + ')',
                   '$string_read_current_offset(' + state + ',pstringread,' + value + ') = (' + str(offset) + ')',
                   '$string_read_resume(' + state + ',pstringread) = ' + state + '[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([' + str(byte) + ']))][.BASE = BASE_VALUE (KNOWN PNULL)]']
    for field, value in (('PARAMETERBACKINGS','[{FUNCTION pkeyread.SITE,INDEX 0,CELL n_old,LINE 16,VALUE $ptascii("word")}]'),
                         ('PROPREFS','[{CELL n_old,SOURCES eps}]'),
                         ('REFCOERCIONS','[{CELL n_old,SITE pkeyread.SITE,LINE 16,VALUE $ptascii("word")}]')):
        checks.append(f'$string_read_key_current(S[.{field} = {value}],pstringread) = eps')
    for field, value in (('CVS','eps'),('RESULT','KNOWN (PINT 0)'),('BASE','BASE_VALUE (KNOWN pkeyread.BASE)'),
                         ('REPORTING','2'),('SERVICELEFT','(0)'),('COMPLETION','BUDGET'),('COMPLETION','THROWING 0'),
                         ('ORIGIN','eps'),('SOURCES','eps'),('CODE','eps')):
        checks.append(f'$string_read_key_current(S[.{field} = {value}],pstringread) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
