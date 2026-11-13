"""A plain CV follows its new reference while an initial wrapper keeps its kind."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64, control_program, control_filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 0, 'S_before') + lines(r'''
$string_read_plan(S_before) = (pstringread)
pstringread.PHASE = STRING_CAST /\ pstringread.READ.PHASE = KEY_NULL
pstringread.READ.KEY = KSTRING eps /\ pstringread.READ.NAME = eps
pstringread.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
pstringread.READ.VALUE = PBOOL false
~pstringread.KEYREF
$string_read_key_reference(S_before,pstringread.KEYCELL) = false
pstringread.READ.INPUT = VARIABLE ($ptascii("key")) 18
pstringread.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("base")) 18)
pstringread.READ.LINE = 18
n_original = 2
n_key_original = 3
pstringread.BASECELL = (n_original) /\ pstringread.KEYCELL = (n_key_original)
$lookup(S_before.ENV,$ptascii("base")) = (n_original)
$lookup(S_before.ENV,$ptascii("key")) = (n_key_original)
S_before.STORE[n_key_original] = DEFINED (PBOOL false)
$lookup(S_before.ENV,$ptascii("got")) = (n_got)
n_got = 4 /\ S_before.STORE[n_got] = DEFINED (PINT 99)
S_before.STORE[n_original] = DEFINED pstringread.READ.BASE
~(n_original <- S_before.REFCELLS)
pvalue_handler = pstringread.READ.BASE
S_before.ERRORHANDLER = {CALLBACK (pvalue_handler),LEVELS 30719}
S_before.ERRORHANDLERS = [{CALLBACK eps,LEVELS 0}]
$string_read_source(S_before,pstringread)
$string_read_provider_ready(S_before,pstringread)
$string_read_ready(S_before,pstringread)
H_before = $heap_graph(S_before)
H_before = {NODES ([HCELL 0,HCELL 1,HCELL 2,HCELL 3,HCELL 4]),EDGES eps,ROOTS ([HCELL 4,HCELL 3,HCELL 2,HCELL 1,HCELL 0]),DEBTS eps}
PhpStep: S_before ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.CALLBACK = pvalue_handler
perrorcall.MESSAGE = $ptascii("String offset cast occurred")
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 18
$error_call_valid(S_dispatch,perrorcall)
$heap_graph(S_dispatch) = H_before
''') + guards('S_before') + seek('S_dispatch', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
$lookup(S.ENV,$ptascii("base")) = (n_base)
n_base =/= n_original
$lookup(S.ENV,$ptascii("key")) = (n_key_current)
n_key_current = 11 /\ n_base = 10
S.STORE[n_key_current] = DEFINED (PINT 2)
~((HCELL n_key_original) <- S.ALLOCATIONS)
S.STORE[n_key_original] = DEFINED (PBOOL false)
S.STORE[n_base] = DEFINED (PINT 99)
S.REFCELLS = [n_key_current,n_base]
$call_reference_operand_valid(S,REFERENCE n_base)
$call_reference_operand_valid(S,REFERENCE n_key_current)
S.STORE[n_got] = DEFINED (PINT 99)
S.STORE[n_original] = DEFINED pstringread.READ.BASE
~((HCELL n_original) <- S.ALLOCATIONS)
S.STRINGDATA = [$ptascii("abc")]
S.ERRORHANDLER = S_before.ERRORHANDLER
S.ERRORHANDLERS = S_before.ERRORHANDLERS
$string_carrier_valid(S,pstringread.READ.BASE)
$error_handler_callable(S,pvalue_handler) = (true)
$error_handler_retained(S,pvalue_handler)
$string_read_callback_has(pstringread.READ.BASE,S.ERRORHANDLER :: S.ERRORHANDLERS)
$string_read_source(S,pstringread)
$string_read_locator(S,VARIABLE ($ptascii("base")) 18,pstringread.BASECELL)
$string_read_locator(S,pstringread.READ.INPUT,pstringread.KEYCELL)
$string_read_base_capture(S,VARIABLE ($ptascii("base")) 18) = eps
$string_read_key_capture(S,pstringread.READ.INPUT,pstringread.READ.BASE) = ((PINT 2,(n_key_current)))
~$string_read_retained(S,pstringread,S.ENV)
~$string_read_callback_retained(S,pstringread)
$string_read_callback_cast_retained(S,pstringread)
$string_read_provider_ready(S,pstringread)
$string_read_key_current(S,pstringread) = (PINT 2)
$string_read_current_offset(S,pstringread,PINT 2) = (2)
~$string_read_cast_released(S,pstringread)
$string_read_ready(S,pstringread)
~$string_read_cv_released(S,pstringread.READ)
$string_read_release_cells(S,0,S.ALLOCATIONS)
$string_read_release_pools(S,S.POOLS)
~$string_read_release_handlers(S,0,S.ERRORHANDLER :: S.ERRORHANDLERS)
$string_read_release_declarations(S.DECLARATIONS)
$string_read_release_tasks(ptask_tail*)
$heap_valid($heap_graph(S))
S.RESULT = KNOWN PNULL
S.BASE = BASE_VALUE (KNOWN PNULL)
$task_nodes(STRING_READ_RESULT pstringread) = eps
$error_handler_roots(S.ERRORHANDLER) = eps
$error_handler_stack_roots(S.ERRORHANDLERS) = eps
H = $heap_graph(S)
H.EDGES = eps /\ H.DEBTS = eps
$heap_owners(H,HCELL n_original) = 0
$heap_owners(H,HCELL n_base) = 1
$heap_owners(H,HCELL n_key_current) = 1
$heap_owners(H,HCELL n_key_original) = 0
$heap_owners(H,HCELL n_got) = 1
S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]
$string_read_resume(S,pstringread) = S_expected
PhpStep: S ~> S_step
S_step = S_expected
$heap_graph(S_step) = H
S_step.EVENTS = S.EVENTS
$drive_steps(S,0) = S[.COMPLETION = BUDGET]
$drive_steps(S,1) = S_expected[.COMPLETION = BUDGET]
S_done = $drive_steps(S_step,1000)
S_done.COMPLETION = NORMAL
S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([99]))
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("2:String offset cast occurred;R:c;B:99;K:2;Z;")
''') + guards('S')
    fields=('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE','RESULT')
    for state in ('S_before','S'):
        checks += [state + ' = $initial_state(NORMAL)' + ''.join('[.'+f+' = '+state+'.'+f+']' for f in fields)]
    checks += [
        'S_control_initial = $php_run(' + control_program + ',0,' + json.dumps(control_filename_b64) + ')',
        'S_control_initial.COMPLETION = BUDGET',
    ] + seek('S_control_initial',0,'S_control_capture') + lines(r'''
$string_read_plan(S_control_capture) = (pstringread_control)
pstringread_control.KEYREF
pstringread_control.KEYCELL = (n_control_old)
n_control_old <- S_control_capture.REFCELLS
$lookup(S_control_capture.ENV,$ptascii("key")) = (n_control_old)
$lookup(S_control_capture.ENV,$ptascii("alias")) = (n_control_old)
$heap_owners($heap_graph(S_control_capture),HCELL n_control_old) = 2
PhpStep: S_control_capture ~> S_control_before
S_control_before.TODO = (ERROR_HANDLER_INVOKE perrorcall_control) :: ptask_control_tail*
perrorcall_control.RESUME = STRING_READ_RESULT pstringread_control
''') + seek('S_control_before',2,'S_control') + lines(r'''
S_control.TODO = (STRING_READ_RESULT pstringread_control) :: ptask_control_tail*
pstringread_control.KEYREF
$lookup(S_control.ENV,$ptascii("key")) = (n_control_current)
$lookup(S_control.ENV,$ptascii("alias")) = (n_control_old)
n_control_current =/= n_control_old
S_control.STORE[n_control_old] = DEFINED (PINT 1)
S_control.STORE[n_control_current] = DEFINED (PINT 2)
n_control_old <- S_control.REFCELLS /\ n_control_current <- S_control.REFCELLS
$heap_owners($heap_graph(S_control),HCELL n_control_old) = 1
$string_read_source(S_control,pstringread_control)
$string_read_callback_cast_retained(S_control,pstringread_control)
$string_read_provider_ready(S_control,pstringread_control)
$string_read_key_capture(S_control,pstringread_control.READ.INPUT,pstringread_control.READ.BASE) = ((PINT 2,(n_control_current)))
$string_read_key_current(S_control,pstringread_control) = eps
S_control_expected = S_control[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]
PhpStep: S_control ~> S_control_step
S_control_step = S_control_expected
$heap_graph(S_control_step) = $heap_graph(S_control)
S_control_step.EVENTS = S_control.EVENTS
''')
    derived_start = len(checks)
    checks += lines(r'''
pstringread_ref = pstringread[.KEYREF = true]
S_ref = S[.TODO = (STRING_READ_RESULT pstringread_ref) :: ptask_tail*]
$string_read_source(S_ref,pstringread_ref)
$string_read_key_current(S_ref,pstringread_ref) = eps
pstringread_absent = pstringread[.KEYCELL = eps][.KEYREF = true]
S_absent = S[.TODO = (STRING_READ_RESULT pstringread_absent) :: ptask_tail*]
~$string_read_source(S_absent,pstringread_absent)
$string_read_key_reference(S,eps) = false
$string_read_key_reference(S,(n_key_current))
~pstringread.KEYREF
S_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_key_current)]
$string_read_key_current(S_unmarked,pstringread) = eps
S_bounds = S[.STORE[n_key_current] = DEFINED (PINT 99)]
$string_read_key_current(S_bounds,pstringread) = eps
$string_read_resume(S_bounds,pstringread) = S_bounds[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]
S_bool = S[.STORE[n_key_current] = DEFINED (PBOOL false)]
$string_read_key_current(S_bool,pstringread) = eps
S_no_cvs = S[.CVS = eps]
$string_read_key_current(S_no_cvs,pstringread) = eps
S_no_owner = S[.ERRORHANDLER.CALLBACK = eps]
~$string_read_callback_cast_retained(S_no_owner,pstringread)
$string_read_key_current(S_no_owner,pstringread) = eps
$string_read_resume(S_no_owner,pstringread) = S_no_owner[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
S_own_result = S[.RESULT = KNOWN (pstringread.READ.BASE)]
$string_read_key_current(S_own_result,pstringread) = eps
S_own_base = S[.BASE = BASE_VALUE (KNOWN (pstringread.READ.BASE))]
$string_read_key_current(S_own_base,pstringread) = eps
S_pending = S[.TODO = (THROW_SEARCH 0) :: ptask_tail*]
$string_read_key_current(S_pending,pstringread) = eps
$string_read_discard(S_pending,pstringread) = S_pending[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
S_control_flag_cleared = S_control[.REFCELLS = $literal_reference_delete(S_control.REFCELLS,n_control_old)]
pstringread_control.KEYREF
$string_read_source(S_control_flag_cleared,pstringread_control)
$string_read_key_current(S_control_flag_cleared,pstringread_control) = eps
''')
    for field in ('ORIGIN','SOURCES','CODE','STRINGDATA'):
        checks.append(' $string_read_key_current(S[.' + field + ' = eps],pstringread) = eps')
    for completion in ('THROWING 0','EXITED 0','BUDGET'):
        checks.append('$string_read_key_current(S[.COMPLETION = ' + completion + '],pstringread) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
