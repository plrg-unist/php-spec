"""A captured initial wrapper supplies its own raw payload after CV rebinding."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture') + lines(r'''
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL (n_original),KEYCELL (n_old),KEYREF true,PHASE STRING_CAST}
pkeyread.PHASE = KEY_NULL /\ pkeyread.VALUE = PBOOL true
pkeyread.INPUT = VARIABLE ($ptascii("key")) 25
pkeyread.LINE = 25
pkeyread.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
n_original = 2 /\ n_old = 3
S_capture.REFCELLS = [n_old]
$lookup(S_capture.ENV,$ptascii("key")) = (n_old)
$lookup(S_capture.ENV,$ptascii("alias")) = (n_old)
$heap_owners($heap_graph(S_capture),HCELL n_old) = 2
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LINE = 25 /\ perrorcall.LEVEL = 2
$error_call_valid(S_before,perrorcall)
''') + guards('S_before') + seek('S_before', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
pstringread.KEYREF
$string_read_key_reference(S,pstringread.KEYCELL)
$lookup(S.ENV,$ptascii("key")) = (n_current)
n_current = 11
$lookup(S.ENV,$ptascii("alias")) = (n_old)
$lookup(S.ENV,$ptascii("base")) = (10)
pvalue_key = PSTRING ($ptascii("String offset cast occurred"))
S.STORE[n_old] = DEFINED pvalue_key
S.STORE[n_current] = DEFINED (PINT 2)
S.STORE[10] = DEFINED (PINT 99)
S.REFCELLS = [n_current,10,n_old]
S.STRINGDATA = [$ptascii("abc")]
S.CELL = 3 /\ S.LOCATION = ROOT 3
~((HCELL n_original) <- S.ALLOCATIONS)
$string_read_source(S,pstringread)
$string_read_callback_cast_retained(S,pstringread)
$string_read_provider_ready(S,pstringread)
~$string_read_cast_released(S,pstringread)
$string_read_key_capture(S,pkeyread.INPUT,pkeyread.BASE) = ((PINT 2,(n_current)))
~$string_read_release_scalar(S,pvalue_key)
~$string_read_callback_request_key_owned(S,pstringread,pvalue_key)
$call_reference_operand_valid(S,REFERENCE n_old)
~$string_read_cell(S,n_old)
~$string_read_array_string_cell(S,n_old)
$string_read_callback_raw_key(S,pstringread) = (pvalue_key)
$string_read_current_offset(S,pstringread,pvalue_key) = (0)
$string_read_key_current(S,pstringread) = (pvalue_key)
$string_read_ready(S,pstringread)
H = $heap_graph(S)
$heap_valid(H)
H = {NODES ([HCELL 0,HCELL 1,HCELL 3,HCELL 4,HCELL 10,HCELL 11]),EDGES eps,ROOTS ([HCELL 11,HCELL 10,HCELL 4,HCELL 3,HCELL 1,HCELL 0]),DEBTS eps}
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
$retained_outputs(S_done.EVENTS) = $ptascii("2:String offset cast occurred;R:a;B:99;K:2;A:String offset cast occurred;Z;")
''') + guards('S') + guards('S_after')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks += ['S = $initial_state(NORMAL)' + ''.join('[.' + field + ' = S.' + field + ']' for field in fields)]
    derived_start = len(checks)
    checks += lines(r'''
pstringread_plain = pstringread[.KEYREF = false]
S_plain = S[.TODO = (STRING_READ_RESULT pstringread_plain) :: ptask_tail*]
$string_read_key_current(S_plain,pstringread_plain) = (PINT 2)
$string_read_resume(S_plain,pstringread_plain) = S_plain[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]
pstringread_raw = pstringread[.READ.VALUE = pvalue_key]
S_raw = S[.TODO = (STRING_READ_RESULT pstringread_raw) :: ptask_tail*]
~$string_read_source(S_raw,pstringread_raw)
$string_read_callback_raw_key(S_raw,pstringread_raw) = eps
$string_read_key_current(S_raw,pstringread_raw) = eps
S_current_raw = S[.STORE[n_current] = DEFINED (PSTRING ($ptascii("2")))]
$string_read_callback_raw_key(S_current_raw,pstringread) = (pvalue_key)
$string_read_key_current(S_current_raw,pstringread) = (pvalue_key)
S_marked_current = S[.STORE[n_current] = DEFINED pvalue_key]
$string_read_callback_raw_key(S_marked_current,pstringread) = (pvalue_key)
$string_read_key_current(S_marked_current,pstringread) = (pvalue_key)
S_ordinary_current = S_marked_current[.REFCELLS = $literal_reference_delete(S_marked_current.REFCELLS,n_current)]
$string_read_callback_raw_key(S_ordinary_current,pstringread) = (pvalue_key)
$string_read_key_current(S_ordinary_current,pstringread) = (pvalue_key)
S_absent = $unset_name(S,$ptascii("key"))
$heap_valid($heap_graph(S_absent))
$string_read_callback_raw_key(S_absent,pstringread) = (pvalue_key)
$string_read_key_current(S_absent,pstringread) = (pvalue_key)
S_old_absent = $unset_name(S,$ptascii("alias"))
$heap_valid($heap_graph(S_old_absent))
$string_read_callback_raw_key(S_old_absent,pstringread) = eps
$string_read_key_current(S_old_absent,pstringread) = eps
S_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_old)]
$string_read_key_current(S_unmarked,pstringread) = eps
S_bad_heap = S[.ENV = (BIND ($ptascii("ghost")) 99) :: S.ENV]
~$heap_valid($heap_graph(S_bad_heap))
$string_read_key_current(S_bad_heap,pstringread) = eps
S_retired = S[.ALLOCATIONS = $native_remove_one(S.ALLOCATIONS,HCELL n_old)]
~$heap_valid($heap_graph(S_retired))
$string_read_key_current(S_retired,pstringread) = eps
S_unowned = S[.ERRORHANDLERS = eps]
~$string_read_callback_cast_retained(S_unowned,pstringread)
~$string_read_cast_released(S_unowned,pstringread)
$string_read_key_current(S_unowned,pstringread) = eps
$string_read_resume(S_unowned,pstringread) = S_unowned[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
S_hidden = S_unowned[.STORE[4] = DEFINED pkeyread.BASE]
$string_read_provider_ready(S_hidden,pstringread)
$string_read_key_current(S_hidden,pstringread) = eps
S_interned = S[.STORE[n_old] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("word")))]
$string_read_callback_raw_key(S_interned,pstringread) = eps
$string_read_key_current(S_interned,pstringread) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("word")))
S_request = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("word")]][.STORE[n_old] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("word")))]
$string_read_callback_raw_key(S_request,pstringread) = eps
$string_read_key_current(S_request,pstringread) = (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("word")))
S_missing_registry = S_request[.STRINGDATA = S.STRINGDATA]
$string_read_key_current(S_missing_registry,pstringread) = eps
''')
    for field, value in (('PARAMETERBACKINGS','[{FUNCTION pkeyread.SITE,INDEX 0,CELL n_old,LINE 25,VALUE $ptascii("word")}]'),
                         ('PROPREFS','[{CELL n_old,SOURCES eps}]'),
                         ('REFCOERCIONS','[{CELL n_old,SITE pkeyread.SITE,LINE 25,VALUE $ptascii("word")}]')):
        checks += [f'$string_read_key_current(S[.{field} = {value}],pstringread) = eps']
    for name, text, offset, byte in (('word','word',0,97),('numeric','2',2,99),('leading','2x',2,99),('fraction','1.75',1,98),('empty','',0,97),('negative','-1',-1,99)):
        value = 'PSTRING ($ptascii(' + json.dumps(text) + '))'
        state = 'S_' + name
        checks += [state + ' = S[.STORE[n_old] = DEFINED (' + value + ')]',
                   '$string_read_callback_raw_key(' + state + ',pstringread) = (' + value + ')',
                   '$string_read_key_current(' + state + ',pstringread) = (' + value + ')',
                   '$string_read_current_offset(' + state + ',pstringread,' + value + ') = (' + str(offset) + ')',
                   '$string_read_resume(' + state + ',pstringread) = ' + state + '[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([' + str(byte) + ']))][.BASE = BASE_VALUE (KNOWN PNULL)]']
    for name, value in (('nul','PSTRING ([50,0,120])'),('invalid','PSTRING ([256])'),('bounds','PSTRING ($ptascii("99"))')):
        state = 'S_' + name
        checks += [state + ' = S[.STORE[n_old] = DEFINED (' + value + ')]',
                   '$string_read_callback_raw_key(' + state + ',pstringread) = eps',
                   '$string_read_current_offset(' + state + ',pstringread,' + value + ') = eps',
                   '$string_read_key_current(' + state + ',pstringread) = eps']
    for field, value in (('CVS','eps'),('RESULT','KNOWN (PINT 0)'),('BASE','BASE_VALUE (KNOWN pkeyread.BASE)'),('REPORTING','2'),('SERVICELEFT','(0)'),('COMPLETION','BUDGET'),('COMPLETION','THROWING 0'),('ORIGIN','eps'),('SOURCES','eps'),('CODE','eps')):
        checks.append(f'$string_read_key_current(S[.{field} = {value}],pstringread) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks), len(checks), len(checks) - derived_start)
