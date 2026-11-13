"""A real outside CV retains the selected base after callback ownership ends."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 0, 'S_capture') + lines(r'''
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL (n_original),KEYCELL (n_key),KEYREF false,PHASE STRING_CAST}
pkeyread.INPUT = VARIABLE ($ptascii("key")) 24
pkeyread.LINE = 24 /\ pkeyread.PHASE = KEY_NULL
pkeyread.VALUE = PBOOL true
pkeyread.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
pkeyread.OWNERS = BASE_VALUE (VARIABLE ($ptascii("base")) 24)
$lookup(S_capture.ENV,$ptascii("keeper")) = (n_keeper)
$lookup(S_capture.ENV,$ptascii("got")) = (n_got)
n_original = 2 /\ n_keeper = 3 /\ n_key = 4 /\ n_got = 5
S_capture.REFCELLS = eps
$lookup(S_capture.ENV,$ptascii("base")) = (n_original)
$lookup(S_capture.ENV,$ptascii("key")) = (n_key)
S_capture.STORE[n_original] = DEFINED pkeyread.BASE
S_capture.STORE[n_keeper] = DEFINED pkeyread.BASE
S_capture.STORE[n_key] = DEFINED (PBOOL true)
$heap_owners($heap_graph(S_capture),HCELL n_original) = 1
$heap_owners($heap_graph(S_capture),HCELL n_keeper) = 1
$heap_owners($heap_graph(S_capture),HCELL n_key) = 1
pvalue_callback = PSTRING_CARRIER INTERNED_STRING ($ptascii("requestRawCellOwner"))
S_capture.ERRORHANDLER = {CALLBACK (pvalue_callback),LEVELS 30719}
S_capture.ERRORHANDLERS = [{CALLBACK (pkeyread.BASE),LEVELS 2},{CALLBACK eps,LEVELS 0}]
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.CALLBACK = pvalue_callback
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 24
perrorcall.MESSAGE = $ptascii("String offset cast occurred")
$error_call_valid(S_before,perrorcall)
''') + guards('S_before') + seek('S_before', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
~pstringread.KEYREF
$lookup(S.ENV,$ptascii("base")) = (n_base)
n_base = 11
$lookup(S.ENV,$ptascii("keeper")) = (n_keeper)
$lookup(S.ENV,$ptascii("key")) = (n_key)
$lookup(S.ENV,$ptascii("got")) = (n_got)
pvalue_key = PSTRING ($ptascii("String offset cast occurred"))
S.STORE[n_original] = DEFINED pkeyread.BASE
~((HCELL n_original) <- S.ALLOCATIONS)
S.STORE[n_base] = DEFINED (PINT 99)
S.STORE[n_keeper] = DEFINED pkeyread.BASE
S.STORE[n_key] = DEFINED pvalue_key
S.STORE[n_got] = DEFINED (PINT 99)
S.REFCELLS = [n_base]
S.STRINGDATA = [$ptascii("abc")]
S.CELL = 4 /\ S.LOCATION = ROOT 2
S.ERRORHANDLER = {CALLBACK (pvalue_callback),LEVELS 0}
S.ERRORHANDLERS = eps
~$string_read_callback_has(pkeyread.BASE,S.ERRORHANDLER :: S.ERRORHANDLERS)
~$string_read_callback_retained(S,pstringread)
~$string_read_callback_cast_retained(S,pstringread)
$string_read_source(S,pstringread)
$string_read_base_capture(S,VARIABLE ($ptascii("base")) 24) = eps
$string_read_retainer(S,pstringread,BIND ($ptascii("keeper")) n_keeper)
$string_read_retained(S,pstringread,S.ENV)
$string_read_provider_ready(S,pstringread)
~$string_read_cast_released(S,pstringread)
$string_read_cell(S,n_key)
$string_read_key_capture(S,pkeyread.INPUT,pkeyread.BASE) = ((pvalue_key,pstringread.KEYCELL))
~$string_read_release_scalar(S,pvalue_key)
~$string_read_callback_request_key_owned(S,pstringread,pvalue_key)
$string_read_callback_raw_key(S,pstringread) = (pvalue_key)
$string_read_current_offset(S,pstringread,pvalue_key) = (0)
$string_read_key_current(S,pstringread) = (pvalue_key)
$string_read_ready(S,pstringread)
H = $heap_graph(S)
H = {NODES ([HCELL 0,HCELL 1,HCELL 3,HCELL 4,HCELL 5,HCELL 11]),EDGES eps,ROOTS ([HCELL 11,HCELL 5,HCELL 4,HCELL 3,HCELL 1,HCELL 0]),DEBTS eps}
$heap_owners(H,HCELL n_original) = 0
$heap_owners(H,HCELL n_keeper) = 1
$heap_owners(H,HCELL n_key) = 1
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
S_done.STORE[n_keeper] = DEFINED pkeyread.BASE
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("2:String offset cast occurred;R:a;B:99;K:String offset cast occurred;P:abc;Z;")
''') + guards('S') + guards('S_after')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks += ['S = $initial_state(NORMAL)' + ''.join('[.' + field + ' = S.' + field + ']' for field in fields)]
    derived_start = len(checks)
    checks += lines(r'''
S_without_keeper = $unset_name(S,$ptascii("keeper"))
$heap_valid($heap_graph(S_without_keeper))
S_without_keeper.STORE[n_keeper] = DEFINED pkeyread.BASE
~((HCELL n_keeper) <- $heap_prune($heap_graph(S_without_keeper)).NODES)
~$string_read_provider_ready(S_without_keeper,pstringread)
~$string_read_cast_released(S_without_keeper,pstringread)
$string_read_callback_raw_key(S_without_keeper,pstringread) = eps
$string_read_key_current(S_without_keeper,pstringread) = eps
$string_read_resume(S_without_keeper,pstringread) = S_without_keeper[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
S_other_header = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("abc")]][.STORE[n_keeper] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("abc")))]
$heap_valid($heap_graph(S_other_header))
~$string_read_provider_ready(S_other_header,pstringread)
$string_read_callback_raw_key(S_other_header,pstringread) = eps
$string_read_key_current(S_other_header,pstringread) = eps
S_got_keeper = S_without_keeper[.STORE[n_got] = DEFINED pkeyread.BASE]
$heap_valid($heap_graph(S_got_keeper))
$string_read_retainer(S_got_keeper,pstringread,BIND ($ptascii("got")) n_got)
$string_read_provider_ready(S_got_keeper,pstringread)
$string_read_callback_raw_key(S_got_keeper,pstringread) = (pvalue_key)
$string_read_key_current(S_got_keeper,pstringread) = (pvalue_key)
$string_read_resume(S_got_keeper,pstringread) = S_got_keeper[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_marked = S[.REFCELLS = n_key :: S.REFCELLS]
$heap_valid($heap_graph(S_marked))
$call_reference_operand_valid(S_marked,REFERENCE n_key)
$string_read_callback_raw_key(S_marked,pstringread) = (pvalue_key)
$string_read_key_current(S_marked,pstringread) = (pvalue_key)
S_callback = S_marked[.ERRORHANDLERS = [{CALLBACK (pkeyread.BASE),LEVELS 2}]]
$string_read_callback_cast_retained(S_callback,pstringread)
$string_read_callback_raw_key(S_callback,pstringread) = (pvalue_key)
$string_read_key_current(S_callback,pstringread) = (pvalue_key)
pstringread_ref = pstringread[.KEYREF = true]
S_ref = S_marked[.TODO = (STRING_READ_RESULT pstringread_ref) :: ptask_tail*]
$string_read_source(S_ref,pstringread_ref)
$string_read_callback_raw_key(S_ref,pstringread_ref) = (pvalue_key)
$string_read_key_current(S_ref,pstringread_ref) = (pvalue_key)
S_retarget = S[.ENV = (BIND ($ptascii("key")) n_got) :: $unbind(S.ENV,$ptascii("key"))][.STORE[n_key] = DEFINED (PINT 2)][.STORE[n_got] = DEFINED (PSTRING ($ptascii("2")))]
$heap_valid($heap_graph(S_retarget))
$string_read_callback_raw_key(S_retarget,pstringread) = (PSTRING ($ptascii("2")))
$string_read_key_current(S_retarget,pstringread) = (PSTRING ($ptascii("2")))
$string_read_resume(S_retarget,pstringread) = S_retarget[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_absent = $unset_name(S,$ptascii("key"))
$heap_valid($heap_graph(S_absent))
$string_read_callback_raw_key(S_absent,pstringread) = eps
$string_read_key_current(S_absent,pstringread) = eps
pstringread_initial_raw = pstringread[.READ.VALUE = pvalue_key]
S_initial_raw = S[.TODO = (STRING_READ_RESULT pstringread_initial_raw) :: ptask_tail*]
~$string_read_source(S_initial_raw,pstringread_initial_raw)
$string_read_callback_raw_key(S_initial_raw,pstringread_initial_raw) = eps
S_bad_heap = S[.ENV = (BIND ($ptascii("ghost")) 99) :: S.ENV]
~$heap_valid($heap_graph(S_bad_heap))
$string_read_key_current(S_bad_heap,pstringread) = eps
S_retired = S[.ALLOCATIONS = $native_remove_one(S.ALLOCATIONS,HCELL n_key)]
~$heap_valid($heap_graph(S_retired))
$string_read_key_current(S_retired,pstringread) = eps
''')
    for name, value in (('nul','PSTRING ([50,0,120])'),('invalid','PSTRING ([256])'),
                        ('bounds','PSTRING ($ptascii("99"))'),('array','PARRAY 0')):
        state = 'S_' + name
        checks += [state + ' = S[.STORE[n_key] = DEFINED (' + value + ')]',
                   '$string_read_callback_raw_key(' + state + ',pstringread) = eps',
                   '$string_read_key_current(' + state + ',pstringread) = eps']
    for name, text, offset, byte in (('word','word',0,97),('fraction','1.75',1,98),
                                    ('negative','-1',-1,99),('leading','2x',2,99),('empty','',0,97)):
        value = 'PSTRING ($ptascii(' + json.dumps(text) + '))'
        state = 'S_' + name
        checks += [state + ' = S[.STORE[n_key] = DEFINED (' + value + ')]',
                   '$string_read_callback_raw_key(' + state + ',pstringread) = (' + value + ')',
                   '$string_read_key_current(' + state + ',pstringread) = (' + value + ')',
                   '$string_read_current_offset(' + state + ',pstringread,' + value + ') = (' + str(offset) + ')',
                   '$string_read_resume(' + state + ',pstringread) = ' + state + '[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([' + str(byte) + ']))][.BASE = BASE_VALUE (KNOWN PNULL)]']
    for field, value in (('PARAMETERBACKINGS','[{FUNCTION pkeyread.SITE,INDEX 0,CELL n_key,LINE 24,VALUE $ptascii("word")}]'),
                         ('PROPREFS','[{CELL n_key,SOURCES eps}]'),
                         ('REFCOERCIONS','[{CELL n_key,SITE pkeyread.SITE,LINE 24,VALUE $ptascii("word")}]')):
        checks.append(f'$string_read_key_current(S[.{field} = {value}],pstringread) = eps')
    for field, value in (('CVS','eps'),('RESULT','KNOWN (PINT 0)'),('BASE','BASE_VALUE (KNOWN pkeyread.BASE)'),
                         ('REPORTING','2'),('SERVICELEFT','(0)'),('COMPLETION','BUDGET'),('COMPLETION','THROWING 0'),
                         ('ORIGIN','eps'),('SOURCES','eps'),('CODE','eps')):
        checks.append(f'$string_read_key_current(S[.{field} = {value}],pstringread) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
