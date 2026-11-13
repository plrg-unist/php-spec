"""Frozen interned base and raw key survive rebinding both reference CVs."""
import json

from string_offset_retained_carrier_protocol import PREFIX as RETAINED_PREFIX, lines
from string_offset_undefined_cv_review import guards


PREFIX = RETAINED_PREFIX + r'''
dec $marked_raw_peer_front(pstate, nat) : bool
def $marked_raw_peer_front(S, 0) = true
  -- if S.TODO = (KEY_READ_DIM (VARIABLE n_name* 23) 23 KEY_R) :: ptask*
  -- if n_name* = $ptascii("key")
def $marked_raw_peer_front(S, 1) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_LEADING 1
def $marked_raw_peer_front(S, n) = false -- otherwise
dec $marked_raw_peer_seek(pstate, nat, nat) : pstate
def $marked_raw_peer_seek(S, n_stage, n) = S
  -- if $marked_raw_peer_front(S, n_stage)
def $marked_raw_peer_seek(S, n_stage, n) = S
  -- if ~$marked_raw_peer_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $marked_raw_peer_seek(S, n_stage, 0) = S
  -- if ~$marked_raw_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $marked_raw_peer_seek(S, n_stage, n) = $marked_raw_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$marked_raw_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def seek(start, stage, result):
    return [f'{result}_found = $marked_raw_peer_seek({start},{stage},1000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def render(program, filename_b64):
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture') + lines(r'''
S_capture.TODO = (KEY_READ_DIM poperand 23 KEY_R) :: ptask_capture*
poperand = VARIABLE ($ptascii("key")) 23
poperand_base = VARIABLE ($ptascii("base")) 23
pvalue_base = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))
pvalue_raw = PSTRING ($ptascii("1x"))
S_capture.RESULT = poperand_base
$lookup(S_capture.ENV,$ptascii("base")) = (n_base)
$lookup(S_capture.ENV,$ptascii("baseAlias")) = (n_base)
$lookup(S_capture.ENV,$ptascii("key")) = (n_old)
$lookup(S_capture.ENV,$ptascii("keyAlias")) = (n_old)
$lookup(S_capture.ENV,$ptascii("got")) = (n_got)
n_base = 0 /\ n_old = 1 /\ n_got = 2
S_capture.STORE[n_base] = DEFINED pvalue_base
S_capture.STORE[n_old] = DEFINED pvalue_raw
S_capture.STORE[n_got] = DEFINED (PINT 99)
S_capture.REFCELLS = [n_old,n_base]
S_capture.STRINGDATA = [$ptascii("512")]
S_capture.CELL = n_old /\ S_capture.LOCATION = ROOT 0
$heap_owners($heap_graph(S_capture),HCELL n_base) = 2
$heap_owners($heap_graph(S_capture),HCELL n_old) = 2
~$string_read_cell(S_capture,n_base) /\ ~$string_read_cell(S_capture,n_old)
$call_reference_operand_valid(S_capture,REFERENCE n_base)
$call_reference_operand_valid(S_capture,REFERENCE n_old)
$string_read_capture(S_capture,poperand_base) = eps
$string_read_capture(S_capture,poperand) = eps
$string_read_key_capture(S_capture,poperand,pvalue_base) = eps
$string_read_raw_leading(pvalue_base,pvalue_raw) = (1)
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL (n_base),KEYCELL (n_old),KEYREF true,PHASE STRING_LEADING 1}
$string_read_raw_capture(S_capture,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
pkeyread.INPUT = poperand /\ pkeyread.VALUE = pvalue_raw
pkeyread.BASE = pvalue_base /\ pkeyread.OWNERS = BASE_VALUE poperand_base
pkeyread.PHASE = KEY_NULL /\ pkeyread.LINE = 23
$origin_child((pkeyread.SITE),[PCFIELD 0]) = (porigin_base)
$compiled_read(S_capture,porigin_base) = eps
$error_variable_source(S_capture,(pkeyread.SITE),[PCFIELD 0],$ptascii("base"))
$code_expression_at_source(S_capture,pkeyread.SITE,[PCFIELD 0]) = (23)
$string_read_base_capture(S_capture,poperand_base) = ((pvalue_base,pstringread.BASECELL))
$string_read_raw_saved(S_capture,pstringread) = (1)
$string_read_source(S_capture,pstringread)
$key_read_input_source(S_capture,pkeyread)
$key_read_owners_source(S_capture,pkeyread)
$base_nodes(pkeyread.OWNERS) = eps
$task_nodes(KEY_READ_DIM poperand 23 KEY_R) = eps
$task_nodes(STRING_READ_RESULT pstringread) = eps
H_capture = {NODES ([HCELL n_base,HCELL n_old,HCELL n_got]),EDGES eps,ROOTS ([HCELL n_got,HCELL n_old,HCELL n_old,HCELL n_base,HCELL n_base]),DEBTS eps}
$heap_graph(S_capture) = H_capture
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 23
perrorcall.MESSAGE = $ptascii("Illegal string offset ") ++ [34] ++ $ptascii("1x") ++ [34]
$error_call_valid(S_before,perrorcall)
$heap_graph(S_before) = H_capture /\ S_before.STORE = S_capture.STORE
''') + guards('S_capture') + guards('S_before') + seek('S_before', 1, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
$lookup(S.ENV,$ptascii("baseAlias")) = (n_base)
$lookup(S.ENV,$ptascii("keyAlias")) = (n_old)
$lookup(S.ENV,$ptascii("base")) = (n_current_base)
$lookup(S.ENV,$ptascii("key")) = (n_current_key)
n_current_base =/= n_base /\ n_current_base =/= n_old /\ n_current_base =/= n_got
n_current_key =/= n_base /\ n_current_key =/= n_old /\ n_current_key =/= n_got
n_current_key =/= n_current_base
S.STORE[n_base] = DEFINED pvalue_base
S.STORE[n_old] = DEFINED (PSTRING perrorcall.MESSAGE)
S.STORE[n_current_base] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S.STORE[n_current_key] = DEFINED (PINT 2)
S.STORE[n_got] = DEFINED (PINT 99)
n_base <- S.REFCELLS /\ n_old <- S.REFCELLS
n_current_base <- S.REFCELLS /\ n_current_key <- S.REFCELLS
$heap_owners($heap_graph(S),HCELL n_base) = 1
$heap_owners($heap_graph(S),HCELL n_old) = 1
$heap_owners($heap_graph(S),HCELL n_current_base) = 1
$heap_owners($heap_graph(S),HCELL n_current_key) = 1
$string_read_base_capture(S,poperand_base) =/= ((pvalue_base,pstringread.BASECELL))
$string_read_raw_capture(S,poperand,pvalue_base) = eps
$string_read_source(S,pstringread)
$string_read_raw_saved(S,pstringread) = (1)
$string_read_ready(S,pstringread)
$string_read_provider_ready(S,pstringread)
$string_read_callback_raw_key(S,pstringread) = eps
$task_nodes(STRING_READ_RESULT pstringread) = eps
H = $heap_graph(S)
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
S_done.STORE[n_base] = DEFINED pvalue_base
S_done.STORE[n_old] = DEFINED (PSTRING perrorcall.MESSAGE)
S_done.STORE[n_current_base] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
S_done.STORE[n_current_key] = DEFINED (PINT 2)
S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([98]))
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("512:1x;2:Illegal string offset ") ++ [34] ++ $ptascii("1x") ++ [34] ++ $ptascii(";R:b;B:XYZ;A:abc;K:2;KA:Illegal string offset ") ++ [34] ++ $ptascii("1x") ++ [34] ++ $ptascii(";Z;")
''') + guards('S') + guards('S_after') + guards('S_done')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','RESULT','CELL','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks.append('S_capture = $initial_state(NORMAL)' + ''.join('[.' + field + ' = S_capture.' + field + ']' for field in fields))
    derived_start = len(checks)
    checks += lines(r'''
S_single_base = $unset_name(S_capture,$ptascii("baseAlias"))
$heap_owners($heap_graph(S_single_base),HCELL n_base) = 1
$heap_valid($heap_graph(S_single_base))
$string_read_plan(S_single_base) = (pstringread)
S_lost_base = $unset_name(S_single_base,$ptascii("base"))
~((HCELL n_base) <- $heap_prune($heap_graph(S_lost_base)).NODES)
$heap_valid($heap_graph(S_lost_base))
$string_read_plan(S_lost_base) = eps
~$string_read_shape(S,pstringread[.PHASE = STRING_LEADING 2])
~$string_read_source(S,pstringread[.READ.LINE = 24])
~$string_read_source(S,pstringread[.PHASE = STRING_CAST])
~$string_read_source(S,pstringread[.BASECELL = eps])
~$string_read_source(S,pstringread[.KEYCELL = eps])
~$string_read_source(S,pstringread[.READ.PHASE = KEY_CV])
~$string_read_source(S,pstringread[.READ.INPUT = KNOWN pvalue_raw])
~$string_read_source(S,pstringread[.READ.OWNERS = BASE_VALUE (KNOWN pvalue_base)])
~$string_read_source(S,pstringread[.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("base")) 24)])
''')
    for field in ('ORIGIN','SOURCES','CODE'):
        checks += [f'$string_read_plan(S_capture[.{field} = eps]) = eps',
                   f'~$string_read_source(S[.{field} = eps],pstringread)']
    for value in ('PSTRING ($ptascii("1"))', 'PSTRING ($ptascii("word"))',
                  'PSTRING ($ptascii("1.5x"))', 'PSTRING ($ptascii("9223372036854775808x"))',
                  'PSTRING ([49,0,120])', 'PSTRING ([256])'):
        checks.append(f'$string_read_plan(S_capture[.STORE[n_old] = DEFINED ({value})]) = eps')
    for value in ('PSTRING ($ptascii("abc"))',
                  'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))',
                  'PSTRING_CARRIER INTERNED_STRING ([97,0,99])'):
        checks.append(f'$string_read_plan(S_capture[.STORE[n_base] = DEFINED ({value})]) = eps')
    for update in ('.CVS = eps', '.RESULT = VARIABLE ($ptascii("base")) 24',
                   '.STORE[n_base] = UNDEFINED', '.STORE[n_old] = UNDEFINED',
                   '.PROPREFS = [{CELL n_base,SOURCES eps}]',
                   '.REFCOERCIONS = [{CELL n_base,SITE pkeyread.SITE,LINE 23,VALUE $ptascii("word")}]',
                   '.PARAMETERBACKINGS = [{FUNCTION pkeyread.SITE,INDEX 0,CELL n_base,LINE 23,VALUE $ptascii("word")}]',
                   '.ALLOCATIONS = $native_remove_one(S_capture.ALLOCATIONS,HCELL n_base)'):
        checks.append(f'$string_read_plan(S_capture[{update}]) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
