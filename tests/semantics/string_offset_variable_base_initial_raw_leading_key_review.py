"""A raw leading key freezes the ordinary CV base before its Warning."""
import json

from string_offset_retained_carrier_protocol import PREFIX, seek, lines
from string_offset_undefined_cv_review import guards


def render(program, filename_b64):
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture') + lines(r'''
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL (n_base),KEYCELL (n_key),KEYREF false,PHASE STRING_LEADING 1}
pkeyread.VALUE = PSTRING ($ptascii("1x"))
pkeyread.INPUT = VARIABLE ($ptascii("key")) 17
pkeyread.LINE = 17 /\ pkeyread.PHASE = KEY_NULL
pkeyread.BASE = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))
pkeyread.OWNERS = BASE_VALUE (VARIABLE ($ptascii("base")) 17)
S_capture.RESULT = VARIABLE ($ptascii("base")) 17
n_base = 0 /\ n_key = 1 /\ S_capture.REFCELLS = eps
S_capture.CELL = 1 /\ S_capture.LOCATION = ROOT 0
S_capture.STRINGDATA = [$ptascii("512")]
$lookup(S_capture.ENV,$ptascii("base")) = (n_base)
$lookup(S_capture.ENV,$ptascii("key")) = (n_key)
S_capture.STORE[n_base] = DEFINED pkeyread.BASE
S_capture.STORE[n_key] = DEFINED pkeyread.VALUE
S_capture.STORE[2] = DEFINED (PINT 99)
$string_read_cell(S_capture,n_base) /\ $string_read_cell(S_capture,n_key)
$string_read_capture(S_capture,S_capture.RESULT) = ((pkeyread.BASE,pstringread.BASECELL))
$string_read_base_capture(S_capture,S_capture.RESULT) = ((pkeyread.BASE,pstringread.BASECELL))
$string_read_key_capture(S_capture,pkeyread.INPUT,pkeyread.BASE) = ((pkeyread.VALUE,pstringread.KEYCELL))
$string_read_raw_capture(S_capture,pkeyread.INPUT,pkeyread.BASE) = ((pkeyread.VALUE,pstringread.KEYCELL))
$string_read_raw_leading(pkeyread.BASE,pkeyread.VALUE) = (1)
$string_read_raw_saved(S_capture,pstringread) = (1)
$origin_child((pkeyread.SITE),[PCFIELD 0]) = (porigin_base)
$compiled_read(S_capture,porigin_base) = eps
$error_variable_source(S_capture,(pkeyread.SITE),[PCFIELD 0],$ptascii("base"))
$code_expression_at_source(S_capture,pkeyread.SITE,[PCFIELD 0]) = (17)
$key_read_input_source(S_capture,pkeyread) /\ $key_read_owners_source(S_capture,pkeyread)
$string_read_source(S_capture,pstringread)
$string_read_message(pstringread) = $ptascii("Illegal string offset \"1x\"")
H_capture = {NODES ([HCELL 0,HCELL 1,HCELL 2]),EDGES eps,ROOTS ([HCELL 2,HCELL 1,HCELL 0]),DEBTS eps}
$heap_graph(S_capture) = H_capture
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LINE = 17 /\ perrorcall.LEVEL = 2
perrorcall.MESSAGE = $ptascii("Illegal string offset \"1x\"")
$error_call_valid(S_before,perrorcall)
$heap_graph(S_before) = H_capture
S_before.STORE = S_capture.STORE
$task_nodes(STRING_READ_RESULT pstringread) = eps
''') + guards('S_capture') + guards('S_before') + seek('S_before', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
$lookup(S.ENV,$ptascii("base")) = (n_current_base)
$lookup(S.ENV,$ptascii("key")) = (n_current_key)
$lookup(S.ENV,$ptascii("got")) = (n_got)
pvalue_current_base = PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ"))
S.STORE[n_current_base] = DEFINED pvalue_current_base
pvalue_current = PSTRING ($ptascii("Illegal string offset \"1x\""))
S.STORE[n_current_key] = DEFINED pvalue_current
S.STORE[n_got] = DEFINED (PINT 99)
S.REFCELLS = eps
$numeric_string($ptascii("Illegal string offset \"1x\"")) = NOTNUMERIC
n_current_base_cell? = (n_current_base)
$string_read_base_capture(S,VARIABLE ($ptascii("base")) 17) = ((pvalue_current_base,n_current_base_cell?))
pvalue_current_base =/= pkeyread.BASE
$string_read_raw_capture(S,pkeyread.INPUT,pkeyread.BASE) = eps
$string_read_key_current(S,pstringread) = eps
$string_read_current_offset(S,pstringread,pvalue_current) = eps
$string_read_raw_saved(S,pstringread) = (1)
$string_read_source(S,pstringread)
$string_read_ready(S,pstringread) /\ $string_read_provider_ready(S,pstringread)
H = $heap_graph(S)
H = H_capture
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
$retained_outputs(S_done.EVENTS) = $ptascii("512:1x;2:Illegal string offset \"1x\";R:b;B:XYZ;K:Illegal string offset \"1x\";Z;")
''') + guards('S') + guards('S_after')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE','RESULT')
    checks.append('S_capture = $initial_state(NORMAL)' + ''.join('[.' + f + ' = S_capture.' + f + ']' for f in fields))
    derived_start = len(checks)
    checks += lines(r'''
S_unset = $unset_name($unset_name(S,$ptascii("base")),$ptascii("key"))
$lookup(S_unset.ENV,$ptascii("base")) = eps /\ $lookup(S_unset.ENV,$ptascii("key")) = eps
~((HCELL n_base) <- $heap_prune($heap_graph(S_unset)).NODES)
~((HCELL n_key) <- $heap_prune($heap_graph(S_unset)).NODES)
$heap_owners($heap_graph(S_unset),HCELL n_base) = 0 /\ $heap_owners($heap_graph(S_unset),HCELL n_key) = 0
$heap_valid($heap_graph(S_unset))
$string_read_source(S_unset,pstringread)
$string_read_ready(S_unset,pstringread) /\ $string_read_provider_ready(S_unset,pstringread)
$string_read_resume(S_unset,pstringread) = S_unset[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_marked_base = S_capture[.REFCELLS = [n_base]]
$string_read_base_capture(S_marked_base,S_capture.RESULT) = ((pkeyread.BASE,pstringread.BASECELL))
~$string_read_cell(S_marked_base,n_base)
$string_read_raw_capture(S_marked_base,pkeyread.INPUT,pkeyread.BASE) = eps
$string_read_plan(S_marked_base) = eps
S_marked_key = S_capture[.REFCELLS = [n_key]]
$call_reference_operand_valid(S_marked_key,REFERENCE n_key)
$string_read_raw_capture(S_marked_key,pkeyread.INPUT,pkeyread.BASE) = ((pkeyread.VALUE,pstringread.KEYCELL))
$string_read_plan(S_marked_key) = (pstringread[.KEYREF = true])
S_registry = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("1x")]]
$string_read_plan(S_registry) = (pstringread)
~$string_read_source(S[.ORIGIN = eps],pstringread)
~$string_read_source(S,pstringread[.READ.LINE = 18])
~$string_read_source(S,pstringread[.PHASE = STRING_LEADING 2])
~$string_read_source(S,pstringread[.PHASE = STRING_CAST])
''')
    for value in ('PSTRING eps', 'PSTRING ($ptascii("1"))', 'PSTRING ($ptascii("word"))',
                  'PSTRING ($ptascii("1.5x"))', 'PSTRING ($ptascii("9223372036854775808x"))',
                  'PSTRING ([49,0,120])', 'PSTRING ([256])'):
        checks.append(f'$string_read_raw_leading(pkeyread.BASE,{value}) = eps')
    for value in ('PSTRING ($ptascii("abc"))', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))',
                  'PSTRING_CARRIER INTERNED_STRING ([97,0,99])'):
        checks.append(f'$string_read_raw_leading({value},pkeyread.VALUE) = eps')
    for update in ('.CVS = eps', '.ENV = eps', '.ALLOCATIONS = eps', '.ORIGIN = eps',
                   '.SOURCES = eps', '.CODE = eps', '.RESULT = VARIABLE ($ptascii("base")) 18',
                   '.STORE[n_base] = UNDEFINED', '.STORE[n_key] = UNDEFINED',
                   '.PROPREFS = [{CELL n_base,SOURCES eps}]',
                   '.PROPREFS = [{CELL n_key,SOURCES eps}]',
                   '.REFCOERCIONS = [{CELL n_base,SITE pkeyread.SITE,LINE 17,VALUE $ptascii("word")}]',
                   '.PARAMETERBACKINGS = [{FUNCTION pkeyread.SITE,INDEX 0,CELL n_base,LINE 17,VALUE $ptascii("word")}]'):
        checks.append(f'$string_read_raw_capture(S_capture[{update}],pkeyread.INPUT,pkeyread.BASE) = eps')
    for update in ('.BASECELL = eps', '.KEYCELL = eps', '.READ.PHASE = KEY_CV',
                   '.READ.INPUT = KNOWN pkeyread.VALUE',
                   '.READ.OWNERS = BASE_VALUE (KNOWN pkeyread.BASE)',
                   '.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("base")) 18)'):
        checks += [f'$string_read_raw_saved(S,pstringread[{update}]) = eps',
                   f'~$string_read_source(S,pstringread[{update}])']
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (c if c.startswith('PhpStep:') else 'if ' + c) + '\n' for c in checks),
        len(checks), len(checks) - derived_start)
