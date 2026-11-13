"""Read a rebound plain key while preserving initial-reference provenance."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64, control_program, control_filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 0, 'S_capture') + lines(r'''
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread, BASECELL (n_original), KEYCELL (n_key), KEYREF false, PHASE STRING_CAST}
pkeyread.PHASE = KEY_NULL /\ pkeyread.VALUE = PBOOL true
pkeyread.INPUT = VARIABLE ($ptascii("key")) 22
pkeyread.LINE = 22 /\ pkeyread.NAME = eps
pkeyread.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
pkeyread.OWNERS = BASE_VALUE (VARIABLE ($ptascii("base")) 22)
n_original = 2 /\ n_key = 3
S_capture.REFCELLS = eps
$string_read_key_reference(S_capture, pstringread.KEYCELL) = false
$lookup(S_capture.ENV, $ptascii("key")) = (n_key)
S_capture.STORE[n_key] = DEFINED (PBOOL true)
$lookup(S_capture.ENV, $ptascii("got")) = (n_got)
n_got = 4
pvalue_current = PSTRING_CARRIER INTERNED_STRING ($ptascii("requestReboundKey"))
S_capture.ERRORHANDLER = {CALLBACK (pvalue_current), LEVELS 30719}
S_capture.ERRORHANDLERS = [{CALLBACK (pkeyread.BASE), LEVELS 2}, {CALLBACK eps, LEVELS 0}]
H_before = $heap_graph(S_capture)
H_before = {NODES ([HCELL 0,HCELL 1,HCELL 2,HCELL 3,HCELL 4]), EDGES eps, ROOTS ([HCELL 4,HCELL 3,HCELL 2,HCELL 1,HCELL 0]), DEBTS eps}
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.CALLBACK = pvalue_current
perrorcall.MESSAGE = $ptascii("String offset cast occurred")
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 22
$error_call_valid(S_before, perrorcall)
$heap_graph(S_before) = H_before
''') + guards('S_before') + seek('S_before', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.CURRENT = eps /\ S.FRAMES = eps
~pstringread.KEYREF
$lookup(S.ENV, $ptascii("base")) = (n_base)
$lookup(S.ENV, $ptascii("key")) = (n_key_current)
n_base = 10 /\ n_key_current = 11
S.STORE[n_original] = DEFINED pkeyread.BASE
S.STORE[n_key] = DEFINED (PBOOL true)
~((HCELL n_original) <- S.ALLOCATIONS) /\ ~((HCELL n_key) <- S.ALLOCATIONS)
S.STORE[n_base] = DEFINED (PINT 99)
S.STORE[n_key_current] = DEFINED (PINT 0)
S.STORE[n_got] = DEFINED (PINT 99)
S.REFCELLS = [n_key_current,n_base]
$call_reference_operand_valid(S, REFERENCE n_key_current)
$call_reference_operand_valid(S, REFERENCE n_base)
$ptascii("key") <- S.CVS
S.STRINGDATA = [$ptascii("abc")]
S.ERRORHANDLER = S_capture.ERRORHANDLER
S.ERRORHANDLERS = S_capture.ERRORHANDLERS
$string_read_source(S, pstringread)
~$string_read_retained(S, pstringread, S.ENV)
~$string_read_callback_retained(S, pstringread)
$string_read_callback_cast_retained(S, pstringread)
$string_read_provider_ready(S, pstringread)
~$string_read_release_handlers(S, 0, S.ERRORHANDLER :: S.ERRORHANDLERS)
~$string_read_cast_released(S, pstringread)
$string_read_key_capture(S, pkeyread.INPUT, pkeyread.BASE) = ((PINT 0,(n_key_current)))
pstringread.KEYCELL = (n_key) /\ n_key =/= n_key_current
$string_read_key_current(S, pstringread) = (PINT 0)
$string_read_ready(S, pstringread)
H = $heap_graph(S)
H = {NODES ([HCELL 0,HCELL 1,HCELL 4,HCELL 10,HCELL 11]), EDGES eps, ROOTS ([HCELL 11,HCELL 10,HCELL 4,HCELL 1,HCELL 0]), DEBTS eps}
$heap_owners(H, HCELL n_key) = 0
$heap_owners(H, HCELL n_key_current) = 1
S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
$string_read_resume(S, pstringread) = S_expected
PhpStep: S ~> S_after
S_after = S_expected
$heap_graph(S_after) = H
S_after.EVENTS = S.EVENTS
$drive_steps(S,0) = S[.COMPLETION = BUDGET]
$drive_steps(S,1) = S_expected[.COMPLETION = BUDGET]
''') + guards('S') + guards('S_after')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks += ['S = $initial_state(NORMAL)' + ''.join('[.' + f + ' = S.' + f + ']' for f in fields)]
    checks += [
        'S_control_initial = $php_run(' + control_program + ', 0, ' + json.dumps(control_filename_b64) + ')',
        'S_control_initial.COMPLETION = BUDGET',
    ] + seek('S_control_initial', 0, 'S_control_capture') + lines(r'''
$string_read_plan(S_control_capture) = (pstringread_control)
pstringread_control.KEYREF
pstringread_control.PHASE = STRING_CAST /\ pstringread_control.READ.PHASE = KEY_NULL
pstringread_control.KEYCELL = (n_control_old)
n_control_old = 3
n_control_old <- S_control_capture.REFCELLS
$string_read_key_reference(S_control_capture, pstringread_control.KEYCELL)
pstringread_control.READ.INPUT = VARIABLE ($ptascii("key")) 21
pstringread_control.READ.VALUE = PBOOL false
PhpStep: S_control_capture ~> S_control_before
S_control_before.TODO = (ERROR_HANDLER_INVOKE perrorcall_control) :: ptask_control_tail*
perrorcall_control.RESUME = STRING_READ_RESULT pstringread_control
$error_call_valid(S_control_before, perrorcall_control)
''') + seek('S_control_before', 2, 'S_control') + lines(r'''
S_control.TODO = (STRING_READ_RESULT pstringread_control) :: ptask_control_tail*
S_control.COMPLETION = NORMAL /\ S_control.CURRENT = eps /\ S_control.FRAMES = eps
pstringread_control.KEYREF
$lookup(S_control.ENV, $ptascii("alias")) = (n_control_old)
$lookup(S_control.ENV, $ptascii("base")) = (n_control_base)
$lookup(S_control.ENV, $ptascii("key")) = (n_control_current)
$lookup(S_control.ENV, $ptascii("got")) = (n_control_got)
n_control_current =/= n_control_old
n_control_old <- S_control.REFCELLS /\ n_control_current <- S_control.REFCELLS
(HCELL n_control_old) <- S_control.ALLOCATIONS
S_control.STORE[n_control_old] = DEFINED (PINT 1)
S_control.STORE[n_control_current] = DEFINED (PINT 2)
S_control.STORE[n_control_base] = DEFINED (PINT 99)
$call_reference_operand_valid(S_control, REFERENCE n_control_old)
$call_reference_operand_valid(S_control, REFERENCE n_control_current)
$string_read_source(S_control, pstringread_control)
$string_read_callback_cast_retained(S_control, pstringread_control)
$string_read_provider_ready(S_control, pstringread_control)
$string_read_key_capture(S_control, pstringread_control.READ.INPUT, pstringread_control.READ.BASE) = ((PINT 2,(n_control_current)))
$string_read_key_current(S_control, pstringread_control) = (PINT 1)
S_control_expected = S_control[.TODO = ptask_control_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
$string_read_resume(S_control, pstringread_control) = S_control_expected
PhpStep: S_control ~> S_control_after
S_control_after = S_control_expected
$heap_graph(S_control_after) = $heap_graph(S_control)
S_control_after.EVENTS = S_control.EVENTS
''') + guards('S_control')
    checks += ['S_control = $initial_state(NORMAL)' + ''.join('[.' + f + ' = S_control.' + f + ']' for f in fields)]
    derived_start = len(checks)
    checks += lines(r'''
S_control_cleared = S_control[.ENV = $unbind(S_control.ENV,$ptascii("alias"))][.ALLOCATIONS = $native_remove_one(S_control.ALLOCATIONS,HCELL n_control_old)][.REFCELLS = $literal_reference_delete(S_control.REFCELLS,n_control_old)]
$heap_valid($heap_graph(S_control_cleared))
~(n_control_old <- S_control_cleared.REFCELLS)
~((HCELL n_control_old) <- S_control_cleared.ALLOCATIONS)
pstringread_control.KEYREF
$string_read_source(S_control_cleared,pstringread_control)
$string_read_callback_cast_retained(S_control_cleared,pstringread_control)
$string_read_key_current(S_control_cleared,pstringread_control) = eps
$string_read_resume(S_control_cleared,pstringread_control) = S_control_cleared[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]
S_control_same = S_control[.ENV = (BIND ($ptascii("key")) n_control_old) :: $unbind(S_control.ENV,$ptascii("key"))][.ALLOCATIONS = $native_remove_one(S_control.ALLOCATIONS,HCELL n_control_current)]
$heap_valid($heap_graph(S_control_same))
$string_read_source(S_control_same,pstringread_control)
$string_read_key_capture(S_control_same,pstringread_control.READ.INPUT,pstringread_control.READ.BASE) = ((PINT 1,(n_control_old)))
$string_read_key_current(S_control_same,pstringread_control) = (PINT 1)
$string_read_resume(S_control_same,pstringread_control) = S_control_same[.TODO = ptask_control_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
pstringread_ref = pstringread[.KEYREF = true]
S_ref = S[.TODO = (STRING_READ_RESULT pstringread_ref) :: ptask_tail*]
$string_read_source(S_ref,pstringread_ref)
$string_read_key_current(S_ref,pstringread_ref) = eps
pstringread_absent = pstringread[.KEYCELL = eps][.KEYREF = true]
S_absent = S[.TODO = (STRING_READ_RESULT pstringread_absent) :: ptask_tail*]
~$string_read_source(S_absent,pstringread_absent)
$string_read_key_reference(S,eps) = false
S_unowned = S[.ERRORHANDLERS = eps]
~$string_read_callback_cast_retained(S_unowned,pstringread)
$string_read_key_current(S_unowned,pstringread) = eps
$string_read_cast_released(S_unowned,pstringread)
$string_read_resume(S_unowned,pstringread) = S_unowned[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]
S_keeper = S_unowned[.STORE[n_got] = DEFINED pkeyread.BASE]
$string_read_provider_ready(S_keeper,pstringread)
~$string_read_callback_cast_retained(S_keeper,pstringread)
$string_read_key_current(S_keeper,pstringread) = eps
$string_read_resume(S_keeper,pstringread) = S_keeper[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]
S_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_key_current)]
$string_read_key_capture(S_unmarked,pkeyread.INPUT,pkeyread.BASE) = ((PINT 0,(n_key_current)))
$string_read_key_current(S_unmarked,pstringread) = eps
S_bounds = S[.STORE[n_key_current] = DEFINED (PINT 99)]
$string_read_key_current(S_bounds,pstringread) = eps
$string_read_resume(S_bounds,pstringread) = S_bounds[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]
S_bool = S[.STORE[n_key_current] = DEFINED (PBOOL false)]
$string_read_key_current(S_bool,pstringread) = (PBOOL false)
S_pending = S[.TODO = (THROW_SEARCH 0) :: ptask_tail*]
$string_read_key_current(S_pending,pstringread) = eps
$string_read_discard(S_pending,pstringread) = S_pending[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
''')
    for field, value in (
        ('RESULT', 'KNOWN (PINT 0)'), ('BASE', 'BASE_VALUE (KNOWN pkeyread.BASE)'),
        ('CVS', 'eps'), ('COMPLETION', 'THROWING 0'),
        ('COMPLETION', 'EXITED 23'), ('COMPLETION', 'BUDGET'),
    ):
        checks.append(f'$string_read_key_current(S[.{field} = {value}],pstringread) = eps')
    for field in ('ORIGIN','SOURCES','CODE','STRINGDATA'):
        checks.append(f'$string_read_key_current(S[.{field} = eps],pstringread) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
