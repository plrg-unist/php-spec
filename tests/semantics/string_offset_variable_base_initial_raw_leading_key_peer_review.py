"""A raw reference key freezes its index and ordinary CV base before Warning."""
import json

from string_offset_retained_carrier_protocol import PREFIX as RETAINED_PREFIX, lines
from string_offset_undefined_cv_review import guards


PREFIX = RETAINED_PREFIX + r'''
dec $cv_raw_peer_front(pstate, nat) : bool
def $cv_raw_peer_front(S, 0) = true
  -- if S.TODO = (KEY_READ_DIM (VARIABLE n_name* 21) 21 KEY_R) :: ptask*
  -- if n_name* = $ptascii("key")
def $cv_raw_peer_front(S, 1) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask*
  -- if perrorcall.RESUME = STRING_READ_RESULT pstringread
  -- if pstringread.PHASE = STRING_LEADING 1
def $cv_raw_peer_front(S, 2) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_LEADING 1
def $cv_raw_peer_front(S, n) = false -- otherwise
dec $cv_raw_peer_seek(pstate, nat, nat) : pstate
def $cv_raw_peer_seek(S, n_stage, n) = S
  -- if $cv_raw_peer_front(S, n_stage)
def $cv_raw_peer_seek(S, n_stage, n) = S
  -- if ~$cv_raw_peer_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $cv_raw_peer_seek(S, n_stage, 0) = S
  -- if ~$cv_raw_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $cv_raw_peer_seek(S, n_stage, n) = $cv_raw_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$cv_raw_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def seek(start, stage, result):
    return [f'{result}_found = $cv_raw_peer_seek({start},{stage},1000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def render(program, filename_b64):
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture') + lines(r'''
S_capture.TODO = (KEY_READ_DIM poperand 21 KEY_R) :: ptask_capture*
poperand = VARIABLE ($ptascii("key")) 21
poperand_base = VARIABLE ($ptascii("base")) 21
pvalue_base = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))
pvalue_raw = PSTRING ($ptascii("1x"))
S_capture.RESULT = poperand_base
$lookup(S_capture.ENV,$ptascii("base")) = (n_base)
$lookup(S_capture.ENV,$ptascii("key")) = (n_old)
$lookup(S_capture.ENV,$ptascii("alias")) = (n_old)
$lookup(S_capture.ENV,$ptascii("got")) = (n_got)
n_base = 0 /\ n_old = 1 /\ n_got = 2
S_capture.STORE[n_base] = DEFINED pvalue_base
S_capture.STORE[n_old] = DEFINED pvalue_raw
S_capture.STORE[n_got] = DEFINED (PINT 99)
S_capture.REFCELLS = [n_old]
S_capture.STRINGDATA = [$ptascii("512")]
S_capture.CELL = n_old /\ S_capture.LOCATION = ROOT 0
$heap_owners($heap_graph(S_capture),HCELL n_base) = 1
$heap_owners($heap_graph(S_capture),HCELL n_old) = 2
$string_read_cell(S_capture,n_base)
$string_read_key_reference(S_capture,(n_old))
$call_reference_operand_valid(S_capture,REFERENCE n_old)
~$string_read_cell(S_capture,n_old)
$string_read_key_capture(S_capture,poperand,pvalue_base) = eps
$string_read_raw_leading(pvalue_base,pvalue_raw) = (1)
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL (n_base),KEYCELL (n_old),KEYREF true,PHASE STRING_LEADING 1}
$string_read_raw_capture(S_capture,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
pkeyread.INPUT = poperand /\ pkeyread.VALUE = pvalue_raw
pkeyread.BASE = pvalue_base /\ pkeyread.OWNERS = BASE_VALUE poperand_base
pkeyread.PHASE = KEY_NULL /\ pkeyread.LINE = 21
$origin_child((pkeyread.SITE),[PCFIELD 0]) = (porigin_base)
$compiled_read(S_capture,porigin_base) = eps
$error_variable_source(S_capture,(pkeyread.SITE),[PCFIELD 0],$ptascii("base"))
$code_expression_at_source(S_capture,pkeyread.SITE,[PCFIELD 0]) = (21)
$string_read_base_capture(S_capture,poperand_base) = ((pvalue_base,pstringread.BASECELL))
$string_read_raw_saved(S_capture,pstringread) = (1)
$string_read_source(S_capture,pstringread)
$key_read_input_source(S_capture,pkeyread)
$key_read_owners_source(S_capture,pkeyread)
$base_nodes(pkeyread.OWNERS) = eps
$task_nodes(KEY_READ_DIM poperand 21 KEY_R) = eps
$task_nodes(STRING_READ_RESULT pstringread) = eps
H_capture = $heap_graph(S_capture)
H_capture = {NODES ([HCELL n_base,HCELL n_old,HCELL n_got]),EDGES eps,ROOTS ([HCELL n_got,HCELL n_old,HCELL n_old,HCELL n_base]),DEBTS eps}
$heap_valid(H_capture)
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 21
perrorcall.MESSAGE = $ptascii("Illegal string offset ") ++ [34] ++ $ptascii("1x") ++ [34]
$error_call_valid(S_before,perrorcall)
$heap_graph(S_before) = H_capture /\ S_before.STORE = S_capture.STORE
''') + guards('S_capture') + guards('S_before') + seek('S_before', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
$lookup(S.ENV,$ptascii("base")) = (n_base)
$lookup(S.ENV,$ptascii("alias")) = (n_old)
$lookup(S.ENV,$ptascii("key")) = (n_current)
n_current =/= n_old /\ n_current =/= n_base /\ n_current =/= n_got
S.STORE[n_base] = DEFINED (PINT 99)
S.STORE[n_old] = DEFINED (PSTRING perrorcall.MESSAGE)
S.STORE[n_current] = DEFINED (PINT 2)
S.STORE[n_got] = DEFINED (PINT 99)
$heap_owners($heap_graph(S),HCELL n_base) = 1
$heap_owners($heap_graph(S),HCELL n_old) = 1
$heap_owners($heap_graph(S),HCELL n_current) = 1
$string_read_base_capture(S,poperand_base) =/= ((pvalue_base,pstringread.BASECELL))
$string_read_source(S,pstringread)
$string_read_raw_saved(S,pstringread) = (1)
$string_read_ready(S,pstringread)
$string_read_provider_ready(S,pstringread)
$string_read_callback_raw_key(S,pstringread) = eps
H = $heap_graph(S)
$heap_valid(H)
H = {NODES ([HCELL n_base,HCELL n_old,HCELL n_got,HCELL n_current]),EDGES eps,ROOTS ([HCELL n_current,HCELL n_got,HCELL n_old,HCELL n_base]),DEBTS eps}
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
S_done.STORE[n_old] = DEFINED (PSTRING perrorcall.MESSAGE)
S_done.STORE[n_current] = DEFINED (PINT 2)
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("512:1x;2:Illegal string offset ") ++ [34] ++ $ptascii("1x") ++ [34] ++ $ptascii(";R:b;B:99;K:2;A:Illegal string offset ") ++ [34] ++ $ptascii("1x") ++ [34] ++ $ptascii(";Z;")
''') + guards('S') + guards('S_after')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','CELL','LOCATION','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE','RESULT')
    checks.append('S_capture = $initial_state(NORMAL)' + ''.join('[.' + f + ' = S_capture.' + f + ']' for f in fields))
    derived_start = len(checks)
    checks += lines(r'''
S_unset_base = $unset_name(S,$ptascii("base"))
$heap_valid($heap_graph(S_unset_base))
$lookup(S_unset_base.ENV,$ptascii("base")) = eps
~((HCELL n_base) <- $heap_prune($heap_graph(S_unset_base)).NODES)
$string_read_source(S_unset_base,pstringread)
$string_read_ready(S_unset_base,pstringread)
$string_read_resume(S_unset_base,pstringread) = S_unset_base[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_unset_key = $unset_name($unset_name(S_unset_base,$ptascii("key")),$ptascii("alias"))
$heap_valid($heap_graph(S_unset_key))
~((HCELL n_old) <- $heap_prune($heap_graph(S_unset_key)).NODES)
$string_read_source(S_unset_key,pstringread)
$string_read_ready(S_unset_key,pstringread)
$string_read_resume(S_unset_key,pstringread) = S_unset_key[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_current_raw = S[.STORE[n_current] = DEFINED (PSTRING ($ptascii("2x")))]
$string_read_ready(S_current_raw,pstringread)
$string_read_resume(S_current_raw,pstringread) = S_current_raw[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([98]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_marked_base = S_capture[.REFCELLS = [n_base,n_old]]
$call_reference_operand_valid(S_marked_base,REFERENCE n_base)
~$string_read_cell(S_marked_base,n_base)
$string_read_plan(S_marked_base) = (pstringread)
S_capture_absent = $unset_name(S_capture,$ptascii("base"))
$heap_valid($heap_graph(S_capture_absent))
$string_read_plan(S_capture_absent) = eps
~$string_read_shape(S,pstringread[.PHASE = STRING_LEADING 2])
~$string_read_source(S,pstringread[.READ.LINE = 22])
~$string_read_source(S,pstringread[.PHASE = STRING_CAST])
~$string_read_source(S,pstringread[.BASECELL = eps])
~$string_read_source(S,pstringread[.KEYCELL = eps])
~$string_read_source(S,pstringread[.READ.PHASE = KEY_CV])
~$string_read_source(S,pstringread[.READ.INPUT = KNOWN pvalue_raw])
~$string_read_source(S,pstringread[.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("other")) 21)])
~$string_read_source(S,pstringread[.READ.OWNERS = BASE_VALUE (VARIABLE ($ptascii("base")) 22)])
$string_read_plan(S_capture[.CVS = [$ptascii("key"),$ptascii("alias"),$ptascii("got")]]) = eps
$string_read_plan(S_capture[.CVS = [$ptascii("base"),$ptascii("alias"),$ptascii("got")]]) = eps
''')
    for field in ('ORIGIN','SOURCES','CODE'):
        checks += [f'$string_read_plan(S_capture[.{field} = eps]) = eps',
                   f'~$string_read_source(S[.{field} = eps],pstringread)']
    for value in ('PSTRING ([49,0,120])', 'PSTRING ([256])', 'PSTRING ($ptascii("1"))',
                  'PSTRING ($ptascii("word"))', 'PSTRING ($ptascii("1.5x"))'):
        checks.append(f'$string_read_plan(S_capture[.STORE[n_old] = DEFINED ({value})]) = eps')
    for value in ('PSTRING ($ptascii("abc"))',
                  'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))',
                  'PSTRING_CARRIER INTERNED_STRING ([97,0,99])'):
        checks.append(f'$string_read_plan(S_capture[.STORE[n_base] = DEFINED ({value})]) = eps')
    for field, value in (('PROPREFS','[{CELL n_base,SOURCES eps}]'),
                         ('REFCOERCIONS','[{CELL n_base,SITE pkeyread.SITE,LINE 21,VALUE $ptascii("word")}]'),
                         ('PARAMETERBACKINGS','[{FUNCTION pkeyread.SITE,INDEX 0,CELL n_base,LINE 21,VALUE $ptascii("word")}]'),
                         ('ALLOCATIONS','$native_remove_one(S_capture.ALLOCATIONS,HCELL n_base)')):
        checks.append(f'$string_read_plan(S_capture[.{field} = {value}]) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
