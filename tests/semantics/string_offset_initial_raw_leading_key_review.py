"""Initial raw string keys freeze their integer before the leading Warning."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture') + lines(r'''
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL eps,KEYCELL (n_key),KEYREF false,PHASE STRING_LEADING 1}
pkeyread.VALUE = PSTRING ($ptascii("1x"))
pkeyread.INPUT = VARIABLE ($ptascii("key")) 12
pkeyread.LINE = 12 /\ pkeyread.PHASE = KEY_NULL
pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))
pkeyread.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)
S_capture.RESULT = KNOWN pkeyread.BASE
n_key = 0 /\ S_capture.REFCELLS = eps
S_capture.CELL = 0 /\ S_capture.LOCATION = ROOT 0
S_capture.STRINGDATA = [$ptascii("512")]
$lookup(S_capture.ENV,$ptascii("key")) = (n_key)
S_capture.STORE[n_key] = DEFINED pkeyread.VALUE
$string_read_cell(S_capture,n_key)
$string_read_capture(S_capture,pkeyread.INPUT) = ((pkeyread.VALUE,pstringread.KEYCELL))
$string_read_key_capture(S_capture,pkeyread.INPUT,pkeyread.BASE) = ((pkeyread.VALUE,pstringread.KEYCELL))
$string_read_raw_capture(S_capture,pkeyread.INPUT,pkeyread.BASE) = ((pkeyread.VALUE,pstringread.KEYCELL))
$string_read_raw_leading(pkeyread.BASE,pkeyread.VALUE) = (1)
$string_read_raw_saved(S_capture,pstringread) = (1)
$origin_child((pkeyread.SITE),[PCFIELD 0]) = (porigin_base)
$compiled_read(S_capture,porigin_base) = (PSTRING ($ptascii("abc")))
$compiled_string_value(S_capture,porigin_base,PSTRING ($ptascii("abc"))) = pkeyread.BASE
$string_read_source(S_capture,pstringread)
$string_read_message(pstringread) = $ptascii("Illegal string offset \"1x\"")
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LINE = 12 /\ perrorcall.LEVEL = 2
perrorcall.MESSAGE = $ptascii("Illegal string offset \"1x\"")
$error_call_valid(S_before,perrorcall)
$heap_graph(S_before) = $heap_graph(S_capture)
S_before.STORE = S_capture.STORE
''') + guards('S_capture') + guards('S_before') + seek('S_before', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
$lookup(S.ENV,$ptascii("key")) = (n_key)
$lookup(S.ENV,$ptascii("got")) = (1)
pvalue_current = PSTRING ($ptascii("Illegal string offset \"1x\""))
S.STORE[n_key] = DEFINED pvalue_current
S.STORE[1] = DEFINED (PINT 99)
S.REFCELLS = eps
$numeric_string($ptascii("Illegal string offset \"1x\"")) = NOTNUMERIC
$string_read_key_current(S,pstringread) = eps
$string_read_current_offset(S,pstringread,pvalue_current) = eps
$string_read_raw_saved(S,pstringread) = (1)
$string_read_source(S,pstringread)
$string_read_ready(S,pstringread)
$string_read_provider_ready(S,pstringread)
~$string_read_callback_cast_retained(S,pstringread)
H = $heap_graph(S)
H = {NODES ([HCELL 0,HCELL 1]),EDGES eps,ROOTS ([HCELL 1,HCELL 0]),DEBTS eps}
$heap_valid(H)
$task_nodes(STRING_READ_RESULT pstringread) = eps
S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
$string_read_resume(S,pstringread) = S_expected
PhpStep: S ~> S_after
S_after = S_expected
$heap_graph(S_after) = H /\ S_after.EVENTS = S.EVENTS
$drive_steps(S,0) = S[.COMPLETION = BUDGET]
$drive_steps(S,1) = S_expected[.COMPLETION = BUDGET]
$drive_steps(S_expected,1) = $drive_steps(S,2)
S_done = $drive_steps(S_after,1000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("512:1x;2:Illegal string offset \"1x\";R:b;K:Illegal string offset \"1x\";Z;")
''') + guards('S') + guards('S_after')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE','RESULT')
    checks.append('S_capture = $initial_state(NORMAL)' + ''.join('[.' + f + ' = S_capture.' + f + ']' for f in fields))
    derived_start = len(checks)
    checks += lines(r'''
S_unset = $unset_name(S,$ptascii("key"))
$heap_valid($heap_graph(S_unset))
~((HCELL n_key) <- $heap_prune($heap_graph(S_unset)).NODES)
$heap_owners($heap_graph(S_unset),HCELL n_key) = 0
$lookup(S_unset.ENV,$ptascii("key")) = eps
$string_read_source(S_unset,pstringread)
$string_read_key_current(S_unset,pstringread) = eps
$string_read_ready(S_unset,pstringread)
$string_read_resume(S_unset,pstringread) = S_unset[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_marked = S_capture[.REFCELLS = [n_key]]
$call_reference_operand_valid(S_marked,REFERENCE n_key)
~$string_read_cell(S_marked,n_key)
$string_read_key_capture(S_marked,pkeyread.INPUT,pkeyread.BASE) = eps
$string_read_raw_capture(S_marked,pkeyread.INPUT,pkeyread.BASE) = ((pkeyread.VALUE,pstringread.KEYCELL))
$string_read_plan(S_marked) = (pstringread[.KEYREF = true])
S_registry = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("1x")]]
$string_read_raw_capture(S_registry,pkeyread.INPUT,pkeyread.BASE) = ((pkeyread.VALUE,pstringread.KEYCELL))
$string_read_plan(S_registry) = (pstringread)
S_nopool = S_capture[.POOLS = eps]
$key_read_owners_source(S_nopool,pkeyread)
$string_read_raw_capture(S_nopool,pkeyread.INPUT,pkeyread.BASE) = eps
$string_read_raw_saved(S_nopool,pstringread) = eps
~$string_read_source(S_nopool,pstringread)
$string_read_plan(S_nopool) = eps
$string_offset(S_capture,PSTRING ($ptascii("1")),12) = S_capture[.KEY = KINT 1]
$string_read_raw_leading(pkeyread.BASE,PSTRING ($ptascii("2x"))) = (2)
$string_read_raw_leading(pkeyread.BASE,PSTRING ($ptascii("-1x"))) = (-1)
pstringread_far = pstringread[.READ.VALUE = PSTRING ($ptascii("9x"))][.PHASE = STRING_LEADING 9]
S_far = S[.TODO = (STRING_READ_RESULT pstringread_far) :: ptask_tail*]
$string_read_source(S_far,pstringread_far)
$string_read_raw_saved(S,pstringread_far) = (9)
$string_read_ready(S_far,pstringread_far)
S_far_warning = $string_read_resume(S_far,pstringread_far)
S_far_warning.TODO = (ERROR_HANDLER_INVOKE perrorcall_far) :: ptask_far*
pstringread_bounds = pstringread_far[.PHASE = STRING_BOUNDS 9]
perrorcall_far.RESUME = STRING_READ_RESULT pstringread_bounds
perrorcall_far.MESSAGE = $ptascii("Uninitialized string offset 9")
$error_call_valid(S_far_warning,perrorcall_far)
$string_read_shape(S_far_warning,pstringread_bounds)
S_bounds = S[.TODO = (STRING_READ_RESULT pstringread_bounds) :: ptask_tail*]
$string_read_source(S_bounds,pstringread_bounds)
$string_read_resume(S_bounds,pstringread_bounds) = S_bounds[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING eps)][.BASE = BASE_VALUE (KNOWN PNULL)]
~$string_read_shape(S,pstringread[.PHASE = STRING_LEADING 2])
~$string_read_source(S[.ORIGIN = eps],pstringread)
~$string_read_source(S,pstringread[.READ.LINE = 13])
~$string_read_source(S,pstringread[.PHASE = STRING_CAST])
$string_read_plan(S_capture[.ORIGIN = eps]) = eps
$string_read_plan(S_capture[.SOURCES = eps]) = eps
$string_read_plan(S_capture[.CODE = eps]) = eps
$string_read_plan(S_capture[.TODO = (KEY_READ_DIM pkeyread.INPUT 13 KEY_R) :: ptask_tail*]) = eps
''')
    for value in ('PSTRING eps', 'PSTRING ($ptascii("1"))', 'PSTRING ($ptascii("word"))',
                  'PSTRING ($ptascii("1.5x"))', 'PSTRING ($ptascii("9223372036854775808x"))',
                  'PSTRING ([49,0,120])', 'PSTRING ([256])'):
        checks.append(f'$string_read_raw_leading(pkeyread.BASE,{value}) = eps')
    for value in ('PSTRING ($ptascii("abc"))', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))'):
        checks += [f'$string_read_raw_leading({value},pkeyread.VALUE) = eps',
                   f'$string_read_raw_capture(S_capture[.RESULT = KNOWN ({value})],pkeyread.INPUT,{value}) = eps']
    for update in ('.CVS = eps', '.ENV = eps', '.ALLOCATIONS = eps',
                   '.RESULT = VARIABLE ($ptascii("base")) 12',
                   '.PARAMETERBACKINGS = [{FUNCTION pkeyread.SITE,INDEX 0,CELL n_key,LINE 12,VALUE $ptascii("word")}]',
                   '.PROPREFS = [{CELL n_key,SOURCES eps}]',
                   '.REFCOERCIONS = [{CELL n_key,SITE pkeyread.SITE,LINE 12,VALUE $ptascii("word")}]'):
        checks.append(f'$string_read_raw_capture(S_capture[{update}],pkeyread.INPUT,pkeyread.BASE) = eps')
    for update in ('.BASECELL = (n_key)', '.KEYCELL = eps', '.READ.PHASE = KEY_CV',
                   '.READ.INPUT = KNOWN pkeyread.VALUE',
                   '.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("base")) 12)'):
        checks += [f'$string_read_raw_saved(S,pstringread[{update}]) = eps',
                   f'~$string_read_source(S,pstringread[{update}])']
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (c if c.startswith('PhpStep:') else 'if ' + c) + '\n' for c in checks),
        len(checks), len(checks) - derived_start)
