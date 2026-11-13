"""The current callback keeps a header across an immutable primitive key read."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 0, 'S_before') + lines(r'''
$string_read_plan(S_before) = (pstringread)
pstringread.PHASE = STRING_CAST /\ pstringread.READ.PHASE = KEY_NULL
pstringread.READ.KEY = KSTRING eps /\ pstringread.READ.NAME = eps
pstringread.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
pstringread.READ.VALUE = PBOOL false
pstringread.READ.INPUT = KNOWN (PBOOL false)
pstringread.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("base")) 14)
pstringread.READ.LINE = 14
n_original = 2
pstringread.BASECELL = (n_original) /\ pstringread.KEYCELL = eps
$lookup(S_before.ENV,$ptascii("base")) = (n_original)
$lookup(S_before.ENV,$ptascii("key")) = eps
$lookup(S_before.ENV,$ptascii("got")) = (n_got)
n_got = 3 /\ S_before.STORE[n_got] = DEFINED (PINT 99)
S_before.STORE[n_original] = DEFINED pstringread.READ.BASE
~(n_original <- S_before.REFCELLS)
S_before.ERRORHANDLER = {CALLBACK (pstringread.READ.BASE),LEVELS 30719}
S_before.ERRORHANDLERS = [{CALLBACK eps,LEVELS 0}]
$string_read_source(S_before,pstringread)
$string_read_provider_ready(S_before,pstringread)
$string_read_ready(S_before,pstringread)
H_before = $heap_graph(S_before)
H_before = {NODES ([HCELL 0,HCELL 1,HCELL 2,HCELL 3]),EDGES eps,ROOTS ([HCELL 3,HCELL 2,HCELL 1,HCELL 0]),DEBTS eps}
PhpStep: S_before ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.CALLBACK = pstringread.READ.BASE
perrorcall.MESSAGE = $ptascii("String offset cast occurred")
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 14
$error_call_valid(S_dispatch,perrorcall)
$heap_graph(S_dispatch) = H_before
''') + guards('S_before') + seek('S_dispatch', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
$lookup(S.ENV,$ptascii("base")) = (n_base)
n_base =/= n_original
$lookup(S.ENV,$ptascii("key")) = eps
S.STORE[n_base] = DEFINED (PINT 99)
S.REFCELLS = [n_base]
$call_reference_operand_valid(S,REFERENCE n_base)
S.STORE[n_got] = DEFINED (PINT 99)
S.STORE[n_original] = DEFINED pstringread.READ.BASE
~((HCELL n_original) <- S.ALLOCATIONS)
S.STRINGDATA = [$ptascii("abc")]
S.ERRORHANDLER = S_before.ERRORHANDLER
S.ERRORHANDLERS = S_before.ERRORHANDLERS
$string_carrier_valid(S,pstringread.READ.BASE)
$error_handler_callable(S,pstringread.READ.BASE) = (true)
$error_handler_retained(S,pstringread.READ.BASE)
$string_read_callback_has(pstringread.READ.BASE,S.ERRORHANDLER :: S.ERRORHANDLERS)
$string_read_source(S,pstringread)
$string_read_locator(S,VARIABLE ($ptascii("base")) 14,pstringread.BASECELL)
$string_read_locator(S,pstringread.READ.INPUT,pstringread.KEYCELL)
$string_read_base_capture(S,VARIABLE ($ptascii("base")) 14) = eps
$string_read_key_capture(S,pstringread.READ.INPUT,pstringread.READ.BASE) = ((PBOOL false,eps))
~$string_read_retained(S,pstringread,S.ENV)
~$string_read_callback_retained(S,pstringread)
$string_read_callback_cast_retained(S,pstringread)
$string_read_provider_ready(S,pstringread)
$string_read_key_current(S,pstringread) = (PBOOL false)
$string_read_current_offset(S,pstringread,PBOOL false) = (0)
$string_read_ready(S,pstringread)
~$string_read_cv_released(S,pstringread.READ)
$string_read_release_cells(S,0,S.ALLOCATIONS)
$string_read_release_pools(S,S.POOLS)
~$string_read_release_handlers(S,0,S.ERRORHANDLER :: S.ERRORHANDLERS)
$task_nodes(STRING_READ_RESULT pstringread) = eps
$error_handler_roots(S.ERRORHANDLER) = eps
$error_handler_stack_roots(S.ERRORHANDLERS) = eps
H = $heap_graph(S)
H.EDGES = eps /\ H.DEBTS = eps
$heap_owners(H,HCELL n_original) = 0
$heap_owners(H,HCELL n_base) = 1
$heap_owners(H,HCELL n_got) = 1
S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
PhpStep: S ~> S_step
S_step = S_expected
$heap_graph(S_step) = H
S_step.EVENTS = S.EVENTS
$drive_steps(S,0) = S[.COMPLETION = BUDGET]
$drive_steps(S,1) = S_expected[.COMPLETION = BUDGET]
S_done = $drive_steps(S_step,1000)
S_done.COMPLETION = NORMAL
S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([97]))
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("2:String offset cast occurred;R:a;B:99;Z;")
''') + guards('S')
    fields=('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE','RESULT')
    for state in ('S_before','S'):
        checks += [state + ' = $initial_state(NORMAL)' + ''.join('[.'+f+' = '+state+'.'+f+']' for f in fields)]
    derived_start = len(checks)
    checks += lines(r'''
$string_read_callback_cast_retained(S[.ERRORHANDLER.LEVELS = 0],pstringread)
S_prior = S[.ERRORHANDLER.CALLBACK = (PSTRING_CARRIER INTERNED_STRING ($ptascii("abc")))][.ERRORHANDLERS = [{CALLBACK eps,LEVELS 9},{CALLBACK (pstringread.READ.BASE),LEVELS 0}]]
$string_read_callback_cast_retained(S_prior,pstringread)
$string_read_resume(S_prior,pstringread) = S_prior[.TODO = ptask_tail*][.RESULT = S_expected.RESULT][.BASE = S_expected.BASE]
$string_read_locator(S,KNOWN (PBOOL false),eps)
~$string_read_locator(S,KNOWN (PBOOL false),(n_base))
~$string_read_locator(S,VARIABLE ($ptascii("base")) 14,eps)
~$string_read_locator(S,REFERENCE n_base,eps)
pstringread_some = pstringread[.KEYCELL = (n_base)]
S_some = S[.TODO = (STRING_READ_RESULT pstringread_some) :: ptask_tail*]
~$string_read_source(S_some,pstringread_some)
~$string_read_callback_cast_retained(S_some,pstringread_some)
pstringread_variable = pstringread[.READ.INPUT = VARIABLE ($ptascii("base")) 14]
S_variable = S[.TODO = (STRING_READ_RESULT pstringread_variable) :: ptask_tail*]
~$string_read_source(S_variable,pstringread_variable)
~$string_read_callback_cast_retained(S_variable,pstringread_variable)
pstringread_reference = pstringread[.READ.INPUT = REFERENCE n_base]
S_reference = S[.TODO = (STRING_READ_RESULT pstringread_reference) :: ptask_tail*]
~$string_read_source(S_reference,pstringread_reference)
~$string_read_callback_cast_retained(S_reference,pstringread_reference)
pstringread_value = pstringread[.READ.VALUE = PBOOL true]
S_value = S[.TODO = (STRING_READ_RESULT pstringread_value) :: ptask_tail*]
~$string_read_source(S_value,pstringread_value)
~$string_read_callback_cast_retained(S_value,pstringread_value)
S_absent = S[.ERRORHANDLER.CALLBACK = eps]
~$string_read_callback_cast_retained(S_absent,pstringread)
~$string_read_provider_ready(S_absent,pstringread)
~$string_read_cv_released(S_absent,pstringread.READ)
$string_read_resume(S_absent,pstringread) = S_absent[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
pvalue_other = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("abc"))
S_other = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("abc")]][.ERRORHANDLER.CALLBACK = (pvalue_other)]
$string_carrier_valid(S_other,pvalue_other)
$error_handler_callable(S_other,pvalue_other) = (true)
~$string_read_callback_cast_retained(S_other,pstringread)
~$string_read_provider_ready(S_other,pstringread)
~$string_read_cv_released(S_other,pstringread.READ)
~$string_read_callback_cast_retained(S[.ERRORHANDLER.CALLBACK = (PSTRING ($ptascii("abc")))],pstringread)
~$string_read_callback_cast_retained(S[.ERRORHANDLER.CALLBACK = (PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("abc")))],pstringread)
~$string_read_callback_cast_retained(S[.ERRORHANDLER.CALLBACK = (PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abd")))],pstringread)
~$string_read_callback_cast_retained(S[.FUNCTIONS = eps][.CALLABLES = eps],pstringread)
~$string_read_callback_cast_retained(S_dispatch,pstringread)
~$string_read_callback_cast_retained(S[.TODO = ptask_tail*],pstringread)
S_pending = S[.TODO = (THROW_SEARCH 0) :: ptask_tail*]
~$string_read_callback_cast_retained(S_pending,pstringread)
~$string_read_provider_ready(S_pending,pstringread)
$string_read_discard(S_pending,pstringread) = S_pending[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
~$string_read_callback_cast_retained(S[.COMPLETION = THROWING 0],pstringread)
~$string_read_callback_cast_retained(S[.COMPLETION = EXITED 0],pstringread)
~$string_read_callback_cast_retained(S[.COMPLETION = BUDGET],pstringread)
~$string_read_callback_cast_retained(S,pstringread[.PHASE = STRING_LEADING 0])
~$string_read_callback_cast_retained(S,pstringread[.PHASE = STRING_BOUNDS 8])
~$string_read_callback_cast_retained(S,pstringread[.READ.PHASE = KEY_CV])
~$string_read_callback_cast_retained(S,pstringread[.BASECELL = eps])
''')
    for field in ('ORIGIN','SOURCES','CODE','STRINGDATA'):
        checks.append('~$string_read_callback_cast_retained(S[.' + field + ' = eps],pstringread)')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
