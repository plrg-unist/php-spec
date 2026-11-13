"""Three plain CV slots select quiet scalar values, independently of old aliases."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(bool_program, bool_path, null_program, null_path, float_program, float_path):
    inputs=((bool_program,bool_path,'PBOOL false','PINT 2','PBOOL true',21,98,False,'2:String offset cast occurred;R:b;B:99;K:1;A:2;Z;'),
            (null_program,null_path,'PBOOL true','PINT 2','PNULL',25,97,True,'2:String offset cast occurred;R:a;B:99;K:;A:2;Z;'),
            (float_program,float_path,'PBOOL false','PINT 1','PFLOAT 4613374868287651840',21,99,False,'2:String offset cast occurred;R:c;B:99;K:2.75;A:1;Z;'))
    body=PREFIX
    written=derived_written=0
    for index,(program,path,initial,old,current,line,byte,prior,stdout) in enumerate(inputs):
        checks=[
            'S_initial = $php_run('+program+',0,'+json.dumps(path)+')',
            'S_initial.COMPLETION = BUDGET',
            'pvalue_initial = '+initial,'pvalue_old = '+old,'pvalue_current = '+current,
        ]+seek('S_initial',0,'S_before')+lines(r'''
$string_read_plan(S_before) = (pstringread)
~pstringread.KEYREF
pstringread.KEYCELL = (n_old)
n_old = 3
pstringread.READ.VALUE = pvalue_initial
pstringread.READ.BASE = PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))
S_before.REFCELLS = eps
$lookup(S_before.ENV,$ptascii("key")) = (n_old)
$lookup(S_before.ENV,$ptascii("alias")) = eps
$heap_owners($heap_graph(S_before),HCELL n_old) = 1
PhpStep: S_before ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LEVEL = 2
perrorcall.MESSAGE = $ptascii("String offset cast occurred")
$error_call_valid(S_dispatch,perrorcall)
''')+guards('S_before')+seek('S_dispatch',2,'S')+lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
~pstringread.KEYREF
$string_read_key_reference(S,pstringread.KEYCELL)
$lookup(S.ENV,$ptascii("alias")) = (n_old)
$lookup(S.ENV,$ptascii("key")) = (n_current)
$lookup(S.ENV,$ptascii("base")) = (n_base)
n_base = 11 /\ n_current = 12
n_current =/= n_old
S.STORE[n_old] = DEFINED pvalue_old
S.STORE[n_current] = DEFINED pvalue_current
S.STORE[n_base] = DEFINED (PINT 99)
S.STORE[4] = DEFINED (PINT 99)
S.REFCELLS = [n_current,n_base,n_old]
$call_reference_operand_valid(S,REFERENCE n_current)
$string_read_key_quiet(pvalue_current)
$string_read_offset(pvalue_current) = (i_current)
$string_read_in_range(pstringread.READ.BASE,i_current)
$string_read_source(S,pstringread)
$string_read_callback_cast_retained(S,pstringread)
$string_read_provider_ready(S,pstringread)
~$string_read_cast_released(S,pstringread)
$string_read_key_capture(S,pstringread.READ.INPUT,pstringread.READ.BASE) = ((pvalue_read,n_read?))
pvalue_read = pvalue_current
n_read? = (n_current)
pvalue_selected? = $string_read_key_current(S,pstringread)
pvalue_selected? = (pvalue_current)
$string_read_current_offset(S,pstringread,pvalue_current) = (i_current)
$string_read_ready(S,pstringread)
H = $heap_graph(S)
H = {NODES ([HCELL 0,HCELL 1,HCELL 3,HCELL 4,HCELL 11,HCELL 12]),EDGES eps,ROOTS ([HCELL 12,HCELL 11,HCELL 3,HCELL 4,HCELL 1,HCELL 0]),DEBTS eps}
$heap_owners(H,HCELL n_old) = 1
$heap_owners(H,HCELL n_current) = 1
$heap_owners(H,HCELL 2) = 0
$task_nodes(STRING_READ_RESULT pstringread) = eps
''')
        checks += [f'pstringread.READ.INPUT = VARIABLE ($ptascii("key")) {line}',
                   f'pstringread.READ.LINE = {line}',
                   'S.ERRORHANDLER.CALLBACK = ('+('PSTRING_CARRIER INTERNED_STRING ($ptascii("requestReferencedKey"))' if prior else 'pstringread.READ.BASE')+')',
                   'S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING (['+str(byte)+']))][.BASE = BASE_VALUE (KNOWN PNULL)]',
                   '$string_read_resume(S,pstringread) = S_expected',
                   'PhpStep: S ~> S_after','S_after = S_expected',
                   '$heap_graph(S_after) = H','S_after.EVENTS = S.EVENTS',
                   '$drive_steps(S,0) = S[.COMPLETION = BUDGET]',
                   '$drive_steps(S,1) = S_expected[.COMPLETION = BUDGET]',
                   'S_done = $drive_steps(S_after,1000)','S_done.COMPLETION = NORMAL',
                   '$retained_outputs_only(S_done.EVENTS)',
                   '$retained_outputs(S_done.EVENTS) = $ptascii('+json.dumps(stdout)+')']+guards('S')+guards('S_after')
        fields=('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
        checks+=['S = $initial_state(NORMAL)'+''.join('[.'+field+' = S.'+field+']' for field in fields)]
        derived_start=len(checks)
        checks+=lines(r'''
pstringread_ref = pstringread[.KEYREF = true]
S_ref = S[.TODO = (STRING_READ_RESULT pstringread_ref) :: ptask_tail*]
$string_read_source(S_ref,pstringread_ref)
pvalue_ref? = $string_read_key_current(S_ref,pstringread_ref)
pvalue_ref? = (pvalue_old)
S_old_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_old)]
pvalue_unmarked? = $string_read_key_current(S_old_unmarked,pstringread)
pvalue_unmarked? = (pvalue_current)
S_old_dead = S[.ENV = $unbind(S.ENV,$ptascii("alias"))][.ALLOCATIONS = $native_remove_one(S.ALLOCATIONS,HCELL n_old)][.REFCELLS = $literal_reference_delete(S.REFCELLS,n_old)]
$heap_valid($heap_graph(S_old_dead))
pvalue_dead? = $string_read_key_current(S_old_dead,pstringread)
pvalue_dead? = (pvalue_current)
S_false = S[.STORE[n_current] = DEFINED (PBOOL false)]
$string_read_key_current(S_false,pstringread) = (PBOOL false)
$string_read_resume(S_false,pstringread) = S_false[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([97]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_bounds = S[.STORE[n_current] = DEFINED (PINT 99)]
$string_read_key_current(S_bounds,pstringread) = eps
S_unmarked = S[.REFCELLS = $literal_reference_delete(S.REFCELLS,n_current)]
pvalue_ordinary? = $string_read_key_current(S_unmarked,pstringread)
pvalue_ordinary? = (pvalue_current)
S_string = S[.STORE[n_current] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("1x")))]
$string_read_key_current(S_string,pstringread) = eps
S_inf = S[.STORE[n_current] = DEFINED (PFLOAT 9218868437227405312)]
~$string_read_key_quiet(PFLOAT 9218868437227405312)
$string_read_key_current(S_inf,pstringread) = eps
S_nan = S[.STORE[n_current] = DEFINED (PFLOAT 9221120237041090560)]
~$string_read_key_quiet(PFLOAT 9221120237041090560)
$string_read_key_current(S_nan,pstringread) = eps
S_range = S[.STORE[n_current] = DEFINED (PFLOAT 4895412794951729152)]
~$string_read_key_quiet(PFLOAT 4895412794951729152)
$string_read_key_current(S_range,pstringread) = eps
S_range_ordinary = S_range[.REFCELLS = $literal_reference_delete(S_range.REFCELLS,n_current)]
$string_read_key_current(S_range_ordinary,pstringread) = eps
S_negative = S[.STORE[n_current] = DEFINED (PFLOAT 13836746905142427648)]
$string_read_key_current(S_negative,pstringread) = (PFLOAT 13836746905142427648)
$string_read_resume(S_negative,pstringread) = S_negative[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_unowned = S[.ERRORHANDLER = {CALLBACK (PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))),LEVELS 30719}][.ERRORHANDLERS = eps]
~$string_read_callback_cast_retained(S_unowned,pstringread)
$string_read_key_current(S_unowned,pstringread) = eps
$string_read_cast_released(S_unowned,pstringread)
$string_read_resume(S_unowned,pstringread) = S_unowned[.TODO = ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]
S_keeper = S_unowned[.STORE[4] = DEFINED pstringread.READ.BASE]
$string_read_provider_ready(S_keeper,pstringread)
~$string_read_callback_cast_retained(S_keeper,pstringread)
$string_read_key_current(S_keeper,pstringread) = eps
S_pending = S[.TODO = (THROW_SEARCH 0) :: ptask_tail*]
$string_read_key_current(S_pending,pstringread) = eps
$string_read_discard(S_pending,pstringread) = S_pending[.COMPLETION = UNSUPPORTED "string offset borrowed carrier after callback"]
''')
        for field,value in (('CVS','eps'),('RESULT','KNOWN (PINT 0)'),('BASE','BASE_VALUE (KNOWN pstringread.READ.BASE)'),('COMPLETION','BUDGET'),('COMPLETION','THROWING 0')):
            checks.append(f'$string_read_key_current(S[.{field} = {value}],pstringread) = eps')
        for field in ('ORIGIN','SOURCES','CODE','STRINGDATA'):
            checks.append(f'$string_read_key_current(S[.{field} = eps],pstringread) = eps')
        body+='\ndec $scalar_peer_'+str(index)+'() : bool\ndef $scalar_peer_'+str(index)+'() = true\n'+''.join('  -- '+(check if check.startswith('PhpStep:') else 'if '+check)+'\n' for check in checks)
        written+=len(checks);derived_written+=len(checks)-derived_start
    body+='\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if $scalar_peer_'+str(index)+'()\n' for index in range(3))
    return body,written+3,derived_written
