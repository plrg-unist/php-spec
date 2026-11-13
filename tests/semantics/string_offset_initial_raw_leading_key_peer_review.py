"""An initial raw reference key fixes its index before the leading Warning."""
import json

from string_offset_retained_carrier_protocol import PREFIX as RETAINED_PREFIX, lines
from string_offset_undefined_cv_review import guards


PREFIX = RETAINED_PREFIX + r'''
dec $initial_raw_peer_front(pstate, nat) : bool
def $initial_raw_peer_front(S, 0) = true
  -- if S.TODO = (KEY_READ_DIM (VARIABLE n_name* 18) 18 KEY_R) :: ptask*
  -- if n_name* = $ptascii("key")
def $initial_raw_peer_front(S, 1) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = STRING_READ_RESULT pstringread
  -- if pstringread.PHASE = STRING_LEADING 1
def $initial_raw_peer_front(S, 2) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_LEADING 1
def $initial_raw_peer_front(S, n) = false -- otherwise
dec $initial_raw_peer_seek(pstate, nat, nat) : pstate
def $initial_raw_peer_seek(S, n_stage, n) = S
  -- if $initial_raw_peer_front(S, n_stage)
def $initial_raw_peer_seek(S, n_stage, n) = S
  -- if ~$initial_raw_peer_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $initial_raw_peer_seek(S, n_stage, 0) = S
  -- if ~$initial_raw_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $initial_raw_peer_seek(S, n_stage, n) = $initial_raw_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$initial_raw_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def seek(start, stage, result):
    return [f'{result}_found = $initial_raw_peer_seek({start},{stage},1000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def render(program, filename_b64):
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture') + lines(r'''
S_capture.TODO = (KEY_READ_DIM poperand 18 KEY_R) :: ptask_capture*
poperand = VARIABLE ($ptascii("key")) 18
pvalue_base = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))
pvalue_raw = PSTRING ($ptascii("1x"))
S_capture.RESULT = KNOWN pvalue_base
$lookup(S_capture.ENV,$ptascii("key")) = (n_old)
$lookup(S_capture.ENV,$ptascii("alias")) = (n_old)
$lookup(S_capture.ENV,$ptascii("got")) = (n_got)
n_old = 0 /\ n_got = 1
S_capture.STORE[n_old] = DEFINED pvalue_raw
S_capture.STORE[n_got] = DEFINED (PINT 99)
S_capture.REFCELLS = [n_old]
S_capture.STRINGDATA = [$ptascii("512")]
S_capture.CELL = 0 /\ S_capture.LOCATION = ROOT 0
$heap_owners($heap_graph(S_capture),HCELL n_old) = 2
$string_read_key_reference(S_capture,(n_old))
$call_reference_operand_valid(S_capture,REFERENCE n_old)
~$string_read_cell(S_capture,n_old)
$string_read_key_capture(S_capture,poperand,pvalue_base) = eps
$string_read_leading(pvalue_base,pvalue_raw) = eps
$string_read_raw_leading(pvalue_base,pvalue_raw) = (1)
$string_read_plan(S_capture) = (pstringread)
$string_read_raw_capture(S_capture,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
pstringread = {READ pkeyread,BASECELL eps,KEYCELL (n_old),KEYREF true,PHASE STRING_LEADING 1}
pkeyread.INPUT = poperand /\ pkeyread.VALUE = pvalue_raw
pkeyread.BASE = pvalue_base /\ pkeyread.OWNERS = BASE_VALUE (KNOWN pvalue_base)
pkeyread.PHASE = KEY_NULL /\ pkeyread.LINE = 18
$origin_child((pkeyread.SITE),[PCFIELD 0]) = (porigin_base)
$compiled_read(S_capture,porigin_base) = (PSTRING ($ptascii("abc")))
$compiled_string_value(S_capture,porigin_base,PSTRING ($ptascii("abc"))) = pvalue_base
$string_read_raw_saved(S_capture,pstringread) = (1)
$string_read_source(S_capture,pstringread)
$key_read_input_source(S_capture,pkeyread)
$key_read_owners_source(S_capture,pkeyread)
$base_nodes(pkeyread.OWNERS) = eps
$task_nodes(KEY_READ_DIM poperand 18 KEY_R) = eps
$task_nodes(STRING_READ_RESULT pstringread) = eps
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 18
perrorcall.MESSAGE = $ptascii("Illegal string offset ") ++ [34] ++ $ptascii("1x") ++ [34]
$error_call_valid(S_before,perrorcall)
''') + guards('S_capture') + guards('S_before') + seek('S_before', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
$lookup(S.ENV,$ptascii("alias")) = (n_old)
$lookup(S.ENV,$ptascii("key")) = (n_current)
n_current =/= n_old
S.STORE[n_old] = DEFINED (PSTRING perrorcall.MESSAGE)
S.STORE[n_current] = DEFINED (PINT 2)
S.STORE[n_got] = DEFINED (PINT 99)
S.REFCELLS = [n_current,n_old]
S.STRINGDATA = [$ptascii("512")]
$heap_owners($heap_graph(S),HCELL n_old) = 1
$heap_owners($heap_graph(S),HCELL n_current) = 1
$string_read_source(S,pstringread)
$string_read_raw_saved(S,pstringread) = (1)
$string_read_ready(S,pstringread)
$string_read_callback_raw_key(S,pstringread) = eps
H = $heap_graph(S)
$heap_valid(H)
H = {NODES ([HCELL n_old,HCELL n_got,HCELL n_current]),EDGES eps,ROOTS ([HCELL n_current,HCELL n_got,HCELL n_old]),DEBTS eps}
S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
$string_read_resume(S,pstringread) = S_expected
PhpStep: S ~> S_after
S_after = S_expected
$heap_graph(S_after) = H /\ S_after.EVENTS = S.EVENTS
$drive_steps(S,0) = S[.COMPLETION = BUDGET]
$drive_steps(S,1) = S_expected[.COMPLETION = BUDGET]
S_done = $drive_steps(S_after,1000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0
S_done.STORE[n_old] = DEFINED (PSTRING perrorcall.MESSAGE)
S_done.STORE[n_current] = DEFINED (PINT 2)
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("512:1x;2:Illegal string offset ") ++ [34] ++ $ptascii("1x") ++ [34] ++ $ptascii(";R:b;K:2;A:Illegal string offset ") ++ [34] ++ $ptascii("1x") ++ [34] ++ $ptascii(";Z;")
''') + guards('S') + guards('S_after')
    derived_start = len(checks)
    checks += lines(r'''
S_unmarked = S_capture[.REFCELLS = eps]
$heap_valid($heap_graph(S_unmarked))
$string_read_raw_capture(S_unmarked,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
S_absent = $unset_name(S,$ptascii("key"))
$heap_valid($heap_graph(S_absent))
$lookup(S_absent.ENV,$ptascii("key")) = eps
$string_read_source(S_absent,pstringread)
$string_read_ready(S_absent,pstringread)
$string_read_resume(S_absent,pstringread) = S_absent[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_no_alias = $unset_name(S_absent,$ptascii("alias"))
$heap_valid($heap_graph(S_no_alias))
~((HCELL n_old) <- $heap_prune($heap_graph(S_no_alias)).NODES)
$heap_owners($heap_graph(S_no_alias),HCELL n_old) = 0
S_no_alias.STORE[n_old] = DEFINED (PSTRING perrorcall.MESSAGE)
$string_read_source(S_no_alias,pstringread)
$string_read_ready(S_no_alias,pstringread)
$string_read_resume(S_no_alias,pstringread) = S_no_alias[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_current_raw = S[.STORE[n_current] = DEFINED (PSTRING ($ptascii("2x")))]
$string_read_ready(S_current_raw,pstringread)
$string_read_resume(S_current_raw,pstringread) = S_current_raw[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
pstringread_false = pstringread[.KEYREF = false]
S_false = S[.TODO = (STRING_READ_RESULT pstringread_false) :: ptask_tail*]
$string_read_source(S_false,pstringread_false)
$string_read_ready(S_false,pstringread_false)
$string_read_resume(S_false,pstringread_false) = S_false[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_bad_heap = S_capture[.ENV = (BIND ($ptascii("ghost")) 99) :: S_capture.ENV]
~$heap_valid($heap_graph(S_bad_heap))
$string_read_raw_capture(S_bad_heap,poperand,pvalue_base) = eps
S_retired = S_capture[.ALLOCATIONS = $native_remove_one(S_capture.ALLOCATIONS,HCELL n_old)]
~$heap_valid($heap_graph(S_retired))
$string_read_raw_capture(S_retired,poperand,pvalue_base) = eps
S_capture_absent = $unset_name($unset_name(S_capture,$ptascii("key")),$ptascii("alias"))
$heap_valid($heap_graph(S_capture_absent))
~((HCELL n_old) <- $heap_prune($heap_graph(S_capture_absent)).NODES)
$string_read_raw_capture(S_capture_absent,poperand,pvalue_base) = eps
S_nopool = S[.POOLS = eps]
$key_read_owners_source(S_nopool,pkeyread)
$string_read_raw_saved(S_nopool,pstringread) = eps
~$string_read_source(S_nopool,pstringread)
~$string_read_ready(S_nopool,pstringread)
$string_read_raw_capture(S_capture[.POOLS = eps],poperand,pvalue_base) = eps
pstringread_cast = pstringread[.PHASE = STRING_CAST]
S_cast = S[.TODO = (STRING_READ_RESULT pstringread_cast) :: ptask_tail*]
~$string_read_source(S_cast,pstringread_cast)
~$string_read_shape(S,pstringread[.PHASE = STRING_LEADING 2])
$string_read_raw_saved(S,pstringread[.KEYCELL = eps]) = eps
$string_read_raw_saved(S,pstringread[.BASECELL = (n_old)]) = eps
$string_read_raw_saved(S,pstringread[.READ.INPUT = KNOWN pvalue_raw]) = eps
$string_read_raw_saved(S,pstringread[.READ.OWNERS = BASE_VALUE poperand]) = eps
$string_read_raw_saved(S,pstringread[.READ.PHASE = KEY_CV]) = eps
$string_read_raw_saved(S,pstringread[.READ.VALUE = PSTRING ($ptascii("2"))]) = eps
$string_read_raw_saved(S,pstringread[.READ.VALUE = PSTRING ($ptascii("word"))]) = eps
$string_read_raw_saved(S,pstringread[.READ.VALUE = PSTRING ($ptascii("1.5x"))]) = eps
''')
    for value in ('PSTRING ([49,0,120])', 'PSTRING ([256])', 'PSTRING ($ptascii("1"))',
                  'PSTRING ($ptascii("word"))', 'PSTRING ($ptascii("1.5x"))'):
        checks += [f'$string_read_raw_leading(pvalue_base,{value}) = eps',
                   f'$string_read_raw_capture(S_capture[.STORE[n_old] = DEFINED ({value})],poperand,pvalue_base) = eps']
    for base in ('PSTRING ($ptascii("abc"))', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))',
                 'PSTRING_CARRIER INTERNED_STRING ([97,0,99])'):
        checks.append(f'$string_read_raw_leading({base},pvalue_raw) = eps')
    for field, value in (('PARAMETERBACKINGS','[{FUNCTION pkeyread.SITE,INDEX 0,CELL n_old,LINE 18,VALUE $ptascii("word")}]'),
                         ('PROPREFS','[{CELL n_old,SOURCES eps}]'),
                         ('REFCOERCIONS','[{CELL n_old,SITE pkeyread.SITE,LINE 18,VALUE $ptascii("word")}]'),
                         ('CVS','eps'),('RESULT','KNOWN PNULL')):
        checks.append(f'$string_read_raw_capture(S_capture[.{field} = {value}],poperand,pvalue_base) = eps')
    for field in ('ORIGIN','SOURCES','CODE'):
        checks.append(f'~$string_read_source(S[.{field} = eps],pstringread)')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
