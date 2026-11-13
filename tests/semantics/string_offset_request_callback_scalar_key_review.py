"""Three actual old-wrapper scalar results and their retarget boundaries."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards
from string_offset_request_callback_scalar_key_cases import CASES


def render(bool_program, bool_path, null_program, null_path, float_program, float_path):
    checks = ['S_initial.COMPLETION = BUDGET'] + seek('S_initial',0,'S_before') + lines(r'''
    $string_read_plan(S_before) = (pstringread)
    pstringread.KEYREF
    pstringread.KEYCELL = (n_old)
    n_old = 3
    pstringread.READ.VALUE = pvalue_initial
    pstringread.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
    S_before.REFCELLS = [n_old]
    $lookup(S_before.ENV,$ptascii("key")) = (n_old)
    $lookup(S_before.ENV,$ptascii("alias")) = (n_old)
    $heap_owners($heap_graph(S_before),HCELL n_old) = 2
    PhpStep: S_before ~> S_dispatch
    S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
    perrorcall.RESUME = STRING_READ_RESULT pstringread
    $error_call_valid(S_dispatch,perrorcall)
    ''') + guards('S_before') + seek('S_dispatch',2,'S') + lines(r'''
    S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
    S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
    pstringread.KEYREF
    $lookup(S.ENV,$ptascii("alias")) = (n_old)
    $lookup(S.ENV,$ptascii("key")) = (n_current)
    $lookup(S.ENV,$ptascii("base")) = (n_base)
    n_base = 10 /\ n_current = 11
    S.STORE[n_old] = DEFINED pvalue_old
    S.STORE[n_current] = DEFINED pvalue_current
    S.STORE[n_base] = DEFINED (PINT 99)
    S.STORE[4] = DEFINED (PINT 99)
    S.REFCELLS = [n_current,n_base,n_old]
    $literal_reference_plain_cell(S,n_old)
    $call_reference_operand_valid(S,REFERENCE n_current)
    $string_read_key_quiet(pvalue_old)
    $string_read_offset(pvalue_old) = (i_old)
    $string_read_in_range(pstringread.READ.BASE,i_old)
    $string_read_source(S,pstringread)
    $string_read_callback_cast_retained(S,pstringread)
    $string_read_provider_ready(S,pstringread)
    $string_read_key_capture(S,pstringread.READ.INPUT,pstringread.READ.BASE) = ((pvalue_read,n_key?))
    pvalue_read = pvalue_current
    n_key? = (n_current)
    $string_read_key_current(S,pstringread) = (pvalue_selected)
    pvalue_selected = pvalue_old
    $string_read_ready(S,pstringread)
    H = $heap_graph(S)
    H = {NODES ([HCELL 0,HCELL 1,HCELL 3,HCELL 4,HCELL 10,HCELL 11]),EDGES eps,ROOTS ([HCELL 11,HCELL 10,HCELL 4,HCELL 3,HCELL 1,HCELL 0]),DEBTS eps}
    $heap_owners(H,HCELL n_old) = 1
    $heap_owners(H,HCELL n_current) = 1
    $heap_owners(H,HCELL 2) = 0
    S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([n_byte]))][.BASE = BASE_VALUE (KNOWN PNULL)]
    $string_read_resume(S,pstringread) = S_expected
    PhpStep: S ~> S_step
    S_step = S_expected
    $heap_graph(S_step) = H
    S_step.EVENTS = S.EVENTS
    $drive_steps(S,0) = S[.COMPLETION = BUDGET]
    $drive_steps(S,1) = S_expected[.COMPLETION = BUDGET]
    S_done = $drive_steps(S_step,1000)
    S_done.COMPLETION = NORMAL
    S_done.STORE[4] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([n_byte]))
    $retained_outputs_only(S_done.EVENTS)
    $retained_outputs(S_done.EVENTS) = n_expected*
    ''') + guards('S')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks += ['S = $initial_state(NORMAL)' + ''.join('[.' + field + ' = S.' + field + ']' for field in fields)]
    derived_start = len(checks)
    checks += lines(r'''
pstringread_plain = pstringread[.KEYREF = false]
S_plain = S[.TODO = (STRING_READ_RESULT pstringread_plain) :: ptask_tail*]
$string_read_key_current(S_plain,pstringread_plain) = (pvalue_plain)
pvalue_plain = pvalue_current
$string_read_resume(S_plain,pstringread_plain) = S_plain[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([n_current_byte]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_old_null = S[.STORE[n_old] = DEFINED PNULL]
$string_read_key_current(S_old_null,pstringread) = (PNULL)
$string_read_resume(S_old_null,pstringread) = S_old_null[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_old_float = S[.STORE[n_old] = DEFINED (PFLOAT 4613374868287651840)]
$string_read_key_current(S_old_float,pstringread) = (PFLOAT 4613374868287651840)
$string_read_resume(S_old_float,pstringread) = S_old_float[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_old_bool = S[.STORE[n_old] = DEFINED (PBOOL false)]
$string_read_key_current(S_old_bool,pstringread) = (PBOOL false)
$string_read_resume(S_old_bool,pstringread) = S_old_bool[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_old_range = S[.STORE[n_old] = DEFINED (PFLOAT 4895412794951729152)]
~$string_read_key_quiet(PFLOAT 4895412794951729152)
$string_read_offset(PFLOAT 4895412794951729152) = (0)
$string_read_key_current(S_old_range,pstringread) = eps
S_old_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_old)]
$string_read_key_current(S_old_unmarked,pstringread) = eps
S_current_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_current)]
$string_read_key_current(S_current_unmarked,pstringread) = eps
S_current_range = S[.STORE[n_current] = DEFINED (PFLOAT 4895412794951729152)]
$string_read_key_current(S_current_range,pstringread) = eps
S_current_string = S[.STORE[n_current] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("1tail")))]
$string_read_key_current(S_current_string,pstringread) = eps
S_old_string = S[.STORE[n_old] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("1tail")))]
$string_read_key_current(S_old_string,pstringread) = eps
S_unowned = S[.ERRORHANDLER.CALLBACK = (PSTRING_CARRIER INTERNED_STRING ($ptascii("abc")))][.ERRORHANDLERS = eps]
~$string_read_callback_cast_retained(S_unowned,pstringread)
$string_read_cast_released(S_unowned,pstringread)
$string_read_resume(S_unowned,pstringread) = S_unowned[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]
S_keeper = S_unowned[.STORE[4] = DEFINED pstringread.READ.BASE]
$string_read_provider_ready(S_keeper,pstringread)
$string_read_key_current(S_keeper,pstringread) = eps
$string_read_resume(S_keeper,pstringread) = S_keeper[.COMPLETION = UNSUPPORTED "string offset changed key locator after callback"]
''')
    for field, value in (('CVS','eps'), ('RESULT','KNOWN (PINT 0)'), ('BASE','BASE_VALUE (KNOWN pstringread.READ.BASE)'), ('COMPLETION','BUDGET'), ('COMPLETION','THROWING 0')):
        checks.append(f'$string_read_key_current(S[.{field} = {value}],pstringread) = eps')
    for field in ('ORIGIN','SOURCES','CODE','STRINGDATA'):
        checks.append(f'$string_read_key_current(S[.{field} = eps],pstringread) = eps')
    text = PREFIX + '\ndec $scalar_key_old_checks(pstate, pvalue, pvalue, pvalue, nat, nat, nat*) : bool\ndef $scalar_key_old_checks(S_initial, pvalue_initial, pvalue_old, pvalue_current, n_byte, n_current_byte, n_expected*) = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks)
    values = [
        ('PBOOL false','PBOOL true','PNULL','98','97'),
        ('PBOOL true','PNULL','PBOOL true','97','98'),
        ('PBOOL true','PFLOAT 4613374868287651840','PBOOL false','99','97'),
    ]
    text += '\ndec $main() : bool\ndef $main() = true\n'
    for program, path, case, args in zip((bool_program,null_program,float_program), (bool_path,null_path,float_path), CASES[:3], values, strict=True):
        text += '  -- if $scalar_key_old_checks($php_run(' + program + ',0,' + json.dumps(path) + '),' + ','.join(args) + ',$ptascii(' + json.dumps(case['expected_stdout']) + '))\n'
    return text, len(checks) + 3, len(checks) - derived_start
