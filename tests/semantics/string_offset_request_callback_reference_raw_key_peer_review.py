"""The initial reference keeps its raw payload independently of its CV name."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 0, 'S_capture') + lines(r'''
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL (n_base_old),KEYCELL (n_key),KEYREF true,PHASE STRING_CAST}
pkeyread.INPUT = VARIABLE ($ptascii("key")) 22
pkeyread.LINE = 22 /\ pkeyread.PHASE = KEY_NULL
pkeyread.VALUE = PBOOL true
pkeyread.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
pkeyread.OWNERS = BASE_VALUE (VARIABLE ($ptascii("base")) 22)
n_base_old = 2 /\ n_key = 3
S_capture.REFCELLS = [n_key]
$string_read_key_reference(S_capture,pstringread.KEYCELL)
$lookup(S_capture.ENV,$ptascii("key")) = (n_key)
$lookup(S_capture.ENV,$ptascii("alias")) = (n_key)
$lookup(S_capture.ENV,$ptascii("got")) = (n_got)
n_got = 4
S_capture.STORE[n_key] = DEFINED (PBOOL true)
$heap_owners($heap_graph(S_capture),HCELL n_key) = 2
pvalue_callback = PSTRING_CARRIER INTERNED_STRING ($ptascii("requestReferencedKey"))
S_capture.ERRORHANDLER = {CALLBACK (pvalue_callback),LEVELS 30719}
S_capture.ERRORHANDLERS = [{CALLBACK (pkeyread.BASE),LEVELS 2},{CALLBACK eps,LEVELS 0}]
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.CALLBACK = pvalue_callback
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 22
perrorcall.MESSAGE = $ptascii("String offset cast occurred")
$error_call_valid(S_before,perrorcall)
''') + guards('S_before') + seek('S_before', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
pstringread.KEYREF
$lookup(S.ENV,$ptascii("key")) = (n_key)
$lookup(S.ENV,$ptascii("alias")) = (n_key)
$lookup(S.ENV,$ptascii("base")) = (n_base)
n_base = 10
pvalue_key = PSTRING ($ptascii("String offset cast occurred"))
S.STORE[n_base_old] = DEFINED pkeyread.BASE
~((HCELL n_base_old) <- S.ALLOCATIONS)
S.STORE[n_key] = DEFINED pvalue_key
S.STORE[n_base] = DEFINED (PINT 99)
S.STORE[n_got] = DEFINED (PINT 99)
S.REFCELLS = [n_base,n_key]
S.STRINGDATA = [$ptascii("abc")]
S.CELL = 3 /\ S.LOCATION = ROOT 2
S.ERRORHANDLER = S_capture.ERRORHANDLER
S.ERRORHANDLERS = S_capture.ERRORHANDLERS
$call_reference_operand_valid(S,REFERENCE n_key)
~$string_read_cell(S,n_key)
~$string_read_array_string_cell(S,n_key)
~$literal_reference_plain_cell(S,n_key)
~$string_read_release_scalar(S,pvalue_key)
~$string_read_callback_request_key_owned(S,pstringread,pvalue_key)
$string_read_source(S,pstringread)
$string_read_callback_cast_retained(S,pstringread)
$string_read_provider_ready(S,pstringread)
~$string_read_cast_released(S,pstringread)
$string_read_capture(S,pkeyread.INPUT) = eps
$string_read_base_capture(S,pkeyread.INPUT) = eps
$string_read_key_capture(S,pkeyread.INPUT,pkeyread.BASE) = eps
$string_read_callback_raw_key(S,pstringread) = (pvalue_key)
$string_read_key_current(S,pstringread) = (pvalue_key)
$string_read_current_offset(S,pstringread,pvalue_key) = (0)
$string_read_ready(S,pstringread)
H = $heap_graph(S)
H = {NODES ([HCELL 0,HCELL 1,HCELL 3,HCELL 4,HCELL 10]),EDGES eps,ROOTS ([HCELL 10,HCELL 4,HCELL 3,HCELL 3,HCELL 1,HCELL 0]),DEBTS eps}
$heap_owners(H,HCELL n_key) = 2
$heap_owners(H,HCELL n_base_old) = 0
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
S_done.STORE[n_key] = DEFINED pvalue_key
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("2:String offset cast occurred;R:a;B:99;K:String offset cast occurred;A:String offset cast occurred;Z;")
''') + guards('S') + guards('S_after')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks += ['S = $initial_state(NORMAL)' + ''.join('[.' + field + ' = S.' + field + ']' for field in fields)]
    derived_start = len(checks)
    checks += lines(r'''
S_absent = $unset_name(S,$ptascii("key"))
$heap_valid($heap_graph(S_absent))
$lookup(S_absent.ENV,$ptascii("key")) = eps
$heap_owners($heap_graph(S_absent),HCELL n_key) = 1
$string_read_callback_raw_key(S_absent,pstringread) = (pvalue_key)
$string_read_key_current(S_absent,pstringread) = (pvalue_key)
$string_read_resume(S_absent,pstringread) = S_absent[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_retarget = S[.ENV = (BIND ($ptascii("key")) n_got) :: $unbind(S.ENV,$ptascii("key"))][.STORE[n_got] = DEFINED (PINT 2)]
$heap_valid($heap_graph(S_retarget))
$heap_owners($heap_graph(S_retarget),HCELL n_key) = 1
$heap_owners($heap_graph(S_retarget),HCELL n_got) = 2
$string_read_key_capture(S_retarget,pkeyread.INPUT,pkeyread.BASE) = ((PINT 2,(n_got)))
$string_read_callback_raw_key(S_retarget,pstringread) = (pvalue_key)
$string_read_key_current(S_retarget,pstringread) = (pvalue_key)
$string_read_resume(S_retarget,pstringread) = S_retarget[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
pstringread_plain = pstringread[.KEYREF = false]
S_plain = S_retarget[.TODO = (STRING_READ_RESULT pstringread_plain) :: ptask_tail*]
$string_read_callback_raw_key(S_plain,pstringread_plain) = eps
$string_read_key_current(S_plain,pstringread_plain) = (PINT 2)
$string_read_resume(S_plain,pstringread_plain) = S_plain[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_swapped = S_retarget[.REFCELLS = n_got :: S_retarget.REFCELLS][.STORE[n_key] = DEFINED (PINT 2)][.STORE[n_got] = DEFINED (PSTRING ($ptascii("word")))]
$heap_valid($heap_graph(S_swapped))
$string_read_callback_raw_key(S_swapped,pstringread) = eps
$string_read_key_current(S_swapped,pstringread) = (PINT 2)
$string_read_resume(S_swapped,pstringread) = S_swapped[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_key)]
$string_read_cell(S_unmarked,n_key)
$string_read_callback_raw_key(S_unmarked,pstringread) = eps
$string_read_key_current(S_unmarked,pstringread) = eps
S_bad_heap = S[.ENV = (BIND ($ptascii("ghost")) 99) :: S.ENV]
~$heap_valid($heap_graph(S_bad_heap))
$string_read_key_current(S_bad_heap,pstringread) = eps
S_retired = S[.ALLOCATIONS = $native_remove_one(S.ALLOCATIONS,HCELL n_key)]
~$heap_valid($heap_graph(S_retired))
$string_read_key_current(S_retired,pstringread) = eps
S_backing = S[.PARAMETERBACKINGS = [{FUNCTION pkeyread.SITE,INDEX 0,CELL n_key,LINE 22,VALUE $ptascii("2")}]]
$string_read_key_current(S_backing,pstringread) = eps
S_prop = S[.PROPREFS = [{CELL n_key,SOURCES eps}]]
$string_read_key_current(S_prop,pstringread) = eps
S_coercion = S[.REFCOERCIONS = [{CELL n_key,SITE pkeyread.SITE,LINE 22,VALUE $ptascii("2")}]]
$string_read_key_current(S_coercion,pstringread) = eps
S_unowned = S[.ERRORHANDLERS = eps]
~$string_read_callback_cast_retained(S_unowned,pstringread)
~$string_read_cast_released(S_unowned,pstringread)
$string_read_key_current(S_unowned,pstringread) = eps
$string_read_resume(S_unowned,pstringread) = S_unowned[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
S_hidden = S_unowned[.STORE[n_got] = DEFINED pkeyread.BASE]
$string_read_provider_ready(S_hidden,pstringread)
~$string_read_cast_released(S_hidden,pstringread)
$string_read_key_current(S_hidden,pstringread) = eps
S_registry = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("String offset cast occurred")]]
$string_read_callback_raw_key(S_registry,pstringread) = (pvalue_key)
$string_read_key_current(S_registry,pstringread) = (pvalue_key)
pvalue_carrier = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("String offset cast occurred"))
$string_carrier_valid(S_registry,pvalue_carrier)
~$string_read_callback_request_key_owned(S_registry,pstringread,pvalue_carrier)
$string_read_current_offset(S_registry,pstringread,pvalue_carrier) = eps
pstringread_initial_raw = pstringread[.READ.VALUE = pvalue_key]
S_initial_raw = S[.TODO = (STRING_READ_RESULT pstringread_initial_raw) :: ptask_tail*]
~$string_read_source(S_initial_raw,pstringread_initial_raw)
$string_read_callback_raw_key(S_initial_raw,pstringread_initial_raw) = eps
$string_read_key_current(S_initial_raw,pstringread_initial_raw) = eps
pstringread_missing = pstringread[.KEYCELL = eps]
S_missing = S[.TODO = (STRING_READ_RESULT pstringread_missing) :: ptask_tail*]
$string_read_callback_raw_key(S_missing,pstringread_missing) = eps
$string_read_key_current(S_missing,pstringread_missing) = eps
''')
    for name, value in (('array','PARRAY 0'),('nul','PSTRING ([50,0,120])'),
                        ('invalid','PSTRING ([256])'),('bounds','PSTRING ($ptascii("99"))')):
        state = 'S_' + name
        checks += [state + ' = S[.STORE[n_key] = DEFINED (' + value + ')]',
                   '$string_read_callback_raw_key(' + state + ',pstringread) = eps',
                   '$string_read_key_current(' + state + ',pstringread) = eps']
    for name, text, offset, byte in (('word','word',0,97),('fraction','1.75',1,98),
                                    ('negative','-1',-1,99),('numeric','2',2,99),('empty','',0,97)):
        value = 'PSTRING ($ptascii(' + json.dumps(text) + '))'
        state = 'S_' + name
        checks += [state + ' = S[.STORE[n_key] = DEFINED (' + value + ')]',
                   '$string_read_key_capture(' + state + ',pkeyread.INPUT,pkeyread.BASE) = eps',
                   '$string_read_callback_raw_key(' + state + ',pstringread) = (' + value + ')',
                   '$string_read_key_current(' + state + ',pstringread) = (' + value + ')',
                   '$string_read_current_offset(' + state + ',pstringread,' + value + ') = (' + str(offset) + ')',
                   '$string_read_resume(' + state + ',pstringread) = ' + state + '[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([' + str(byte) + ']))][.BASE = BASE_VALUE (KNOWN PNULL)]']
    for field, value in (('CVS','eps'),('RESULT','KNOWN (PINT 0)'),('BASE','BASE_VALUE (KNOWN pkeyread.BASE)'),
                         ('REPORTING','2'),('SERVICELEFT','(0)'),('COMPLETION','BUDGET'),('COMPLETION','THROWING 0')):
        checks.append(f'$string_read_key_current(S[.{field} = {value}],pstringread) = eps')
    for field in ('ORIGIN','SOURCES','CODE'):
        checks.append(f'$string_read_key_current(S[.{field} = eps],pstringread) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
