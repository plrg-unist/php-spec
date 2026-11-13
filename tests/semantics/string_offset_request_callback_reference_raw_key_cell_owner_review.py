"""A saved initial raw key survives callback-owner loss with its real base CV."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture') + lines(r'''
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL (n_base),KEYCELL (n_old),KEYREF true,PHASE STRING_CAST}
pkeyread.PHASE = KEY_NULL /\ pkeyread.VALUE = PBOOL true
pkeyread.INPUT = VARIABLE ($ptascii("key")) 24
pkeyread.LINE = 24
pkeyread.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
n_base = 2 /\ n_old = 3
S_capture.REFCELLS = [n_old]
$lookup(S_capture.ENV,$ptascii("base")) = (n_base)
$lookup(S_capture.ENV,$ptascii("key")) = (n_old)
$lookup(S_capture.ENV,$ptascii("alias")) = (n_old)
$heap_owners($heap_graph(S_capture),HCELL n_old) = 2
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LINE = 24 /\ perrorcall.LEVEL = 2
$error_call_valid(S_before,perrorcall)
''') + guards('S_before') + seek('S_before', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
$lookup(S.ENV,$ptascii("base")) = (n_base)
$lookup(S.ENV,$ptascii("key")) = (n_current)
$lookup(S.ENV,$ptascii("alias")) = (n_old)
n_current = 10
S.STORE[n_base] = DEFINED pkeyread.BASE
pvalue_key = PSTRING ($ptascii("String offset cast occurred"))
S.STORE[n_old] = DEFINED pvalue_key
S.STORE[n_current] = DEFINED (PINT 2)
S.REFCELLS = [n_current,n_old] /\ S.STRINGDATA = [$ptascii("abc")]
S.CELL = 10 /\ S.LOCATION = ROOT 3
S.ERRORHANDLER = {CALLBACK (PSTRING_CARRIER INTERNED_STRING ($ptascii("requestRawInitialOwner"))),LEVELS 0}
S.ERRORHANDLERS = eps
~$string_read_callback_has(pkeyread.BASE,S.ERRORHANDLER :: S.ERRORHANDLERS)
~$string_read_callback_retained(S,pstringread)
~$string_read_callback_cast_retained(S,pstringread)
$string_read_source(S,pstringread)
$string_read_base_capture(S,VARIABLE ($ptascii("base")) 24) = ((pkeyread.BASE,pstringread.BASECELL))
~$string_read_retained(S,pstringread,S.ENV)
$string_read_provider_ready(S,pstringread)
~$string_read_cast_released(S,pstringread)
$string_read_cell(S,n_base)
$call_reference_operand_valid(S,REFERENCE n_old)
~$string_read_cell(S,n_old)
$string_read_key_reference(S,pstringread.KEYCELL)
$string_read_key_capture(S,pkeyread.INPUT,pkeyread.BASE) = ((PINT 2,(n_current)))
~$string_read_release_scalar(S,pvalue_key)
~$string_read_callback_request_key_owned(S,pstringread,pvalue_key)
$string_read_callback_raw_key(S,pstringread) = (pvalue_key)
$string_read_current_offset(S,pstringread,pvalue_key) = (0)
$string_read_key_current(S,pstringread) = (pvalue_key)
$string_read_ready(S,pstringread)
H = $heap_graph(S)
$heap_valid(H)
H = {NODES ([HCELL 0,HCELL 1,HCELL 2,HCELL 3,HCELL 4,HCELL 10]),EDGES eps,ROOTS ([HCELL 10,HCELL 4,HCELL 3,HCELL 2,HCELL 1,HCELL 0]),DEBTS eps}
$heap_owners(H,HCELL n_base) = 1 /\ $heap_owners(H,HCELL n_old) = 1
$heap_owners(H,HCELL n_current) = 1
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
$retained_outputs(S_done.EVENTS) = $ptascii("2:String offset cast occurred;R:a;B:abc;K:2;A:String offset cast occurred;Z;")
''') + guards('S') + guards('S_after')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks += ['S = $initial_state(NORMAL)' + ''.join('[.' + field + ' = S.' + field + ']' for field in fields)]
    derived_start = len(checks)
    checks += lines(r'''
pstringread_plain = pstringread[.KEYREF = false]
S_plain = S[.TODO = (STRING_READ_RESULT pstringread_plain) :: ptask_tail*]
$string_read_callback_raw_key(S_plain,pstringread_plain) = eps
$string_read_key_current(S_plain,pstringread_plain) = eps
pstringread_raw = pstringread[.READ.VALUE = pvalue_key]
S_raw = S[.TODO = (STRING_READ_RESULT pstringread_raw) :: ptask_tail*]
~$string_read_source(S_raw,pstringread_raw)
$string_read_callback_raw_key(S_raw,pstringread_raw) = eps
$string_read_key_current(S_raw,pstringread_raw) = eps
S_current_raw = S[.STORE[n_current] = DEFINED (PSTRING ($ptascii("2")))]
$string_read_callback_raw_key(S_current_raw,pstringread) = (pvalue_key)
$string_read_key_current(S_current_raw,pstringread) = (pvalue_key)
$string_read_resume(S_current_raw,pstringread) = S_current_raw[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_absent = $unset_name(S,$ptascii("key"))
$heap_valid($heap_graph(S_absent))
$string_read_callback_raw_key(S_absent,pstringread) = (pvalue_key)
$string_read_key_current(S_absent,pstringread) = (pvalue_key)
S_old_absent = $unset_name(S,$ptascii("alias"))
~((HCELL n_old) <- $heap_prune($heap_graph(S_old_absent)).NODES)
$string_read_callback_raw_key(S_old_absent,pstringread) = eps
$string_read_key_current(S_old_absent,pstringread) = eps
S_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_old)]
$string_read_callback_raw_key(S_unmarked,pstringread) = eps
$string_read_key_current(S_unmarked,pstringread) = eps
S_no_provider = S[.STORE[n_base] = DEFINED (PINT 99)]
~$string_read_provider_ready(S_no_provider,pstringread)
~$string_read_cast_released(S_no_provider,pstringread)
$string_read_callback_raw_key(S_no_provider,pstringread) = eps
$string_read_key_current(S_no_provider,pstringread) = eps
$string_read_resume(S_no_provider,pstringread) = S_no_provider[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
S_unbound_base = $unset_name(S,$ptascii("base"))
S_unbound_base.STORE[n_base] = DEFINED pkeyread.BASE
~$string_read_provider_ready(S_unbound_base,pstringread)
$string_read_callback_raw_key(S_unbound_base,pstringread) = eps
S_equal_interned = S[.STORE[n_base] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("abc")))]
~$string_read_provider_ready(S_equal_interned,pstringread)
$string_read_callback_raw_key(S_equal_interned,pstringread) = eps
S_distinct_identity = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("abc")]][.STORE[n_base] = DEFINED (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("abc")))]
$string_carrier_valid(S_distinct_identity,pkeyread.BASE)
~$string_read_provider_ready(S_distinct_identity,pstringread)
$string_read_callback_raw_key(S_distinct_identity,pstringread) = eps
S_stale_keeper = S_no_provider[.STORE[5] = DEFINED pkeyread.BASE]
~((HCELL 5) <- S_stale_keeper.ALLOCATIONS)
~$string_read_provider_ready(S_stale_keeper,pstringread)
$string_read_callback_raw_key(S_stale_keeper,pstringread) = eps
S_real_keeper = S_no_provider[.STORE[4] = DEFINED pkeyread.BASE]
$string_read_retainer(S_real_keeper,pstringread,BIND ($ptascii("got")) 4)
$string_read_provider_ready(S_real_keeper,pstringread)
$string_read_callback_raw_key(S_real_keeper,pstringread) = (pvalue_key)
$string_read_key_current(S_real_keeper,pstringread) = (pvalue_key)
S_bad_heap = S[.ENV = (BIND ($ptascii("ghost")) 99) :: S.ENV]
~$heap_valid($heap_graph(S_bad_heap))
$string_read_callback_raw_key(S_bad_heap,pstringread) = eps
S_retired = S[.ALLOCATIONS = $native_remove_one(S.ALLOCATIONS,HCELL n_old)]
~$heap_valid($heap_graph(S_retired))
$string_read_callback_raw_key(S_retired,pstringread) = eps
''')
    for cell in ('n_base', 'n_old'):
        for field, value in (('PARAMETERBACKINGS','[{FUNCTION pkeyread.SITE,INDEX 0,CELL ' + cell + ',LINE 24,VALUE $ptascii("word")}]'),
                             ('PROPREFS','[{CELL ' + cell + ',SOURCES eps}]'),
                             ('REFCOERCIONS','[{CELL ' + cell + ',SITE pkeyread.SITE,LINE 24,VALUE $ptascii("word")}]')):
            checks.append(f'$string_read_callback_raw_key(S[.{field} = {value}],pstringread) = eps')
    for name, text, offset, byte in (('word','word',0,97),('leading','2x',2,99),('negative','-1',-1,99)):
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
        checks.append(f'$string_read_callback_raw_key(S[.{field} = {value}],pstringread) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks), len(checks), len(checks) - derived_start)
