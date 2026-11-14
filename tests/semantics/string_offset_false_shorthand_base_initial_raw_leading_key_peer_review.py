"""A literal FALSE shorthand keeps its fallback base across raw-key rebinding."""
import json

from string_offset_retained_carrier_protocol import PREFIX as RETAINED_PREFIX, lines
from string_offset_undefined_cv_review import guards


PREFIX = RETAINED_PREFIX + r'''
dec $false_shorthand_raw_peer_front(pstate, nat) : bool
def $false_shorthand_raw_peer_front(S, 0) = true
  -- if S.TODO = (KEY_READ_DIM (VARIABLE n_name* 18) 18 KEY_R) :: ptask*
  -- if n_name* = $ptascii("key")
def $false_shorthand_raw_peer_front(S, 1) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_LEADING 1
def $false_shorthand_raw_peer_front(S, n) = false -- otherwise
dec $false_shorthand_raw_peer_seek(pstate, nat, nat) : pstate
def $false_shorthand_raw_peer_seek(S, n_stage, n) = S
  -- if $false_shorthand_raw_peer_front(S, n_stage)
def $false_shorthand_raw_peer_seek(S, n_stage, n) = S
  -- if ~$false_shorthand_raw_peer_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $false_shorthand_raw_peer_seek(S, n_stage, 0) = S
  -- if ~$false_shorthand_raw_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $false_shorthand_raw_peer_seek(S, n_stage, n) = $false_shorthand_raw_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$false_shorthand_raw_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def seek(start, stage, result):
    return [f'{result}_found = $false_shorthand_raw_peer_seek({start},{stage},1000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def render(program, filename_b64):
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture') + lines(r'''
S_capture.TODO = (KEY_READ_DIM poperand 18 KEY_R) :: ptask_capture*
poperand = VARIABLE ($ptascii("key")) 18
pvalue_base = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))
pvalue_wrong = PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ"))
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
S_capture.CELL = n_old /\ S_capture.LOCATION = ROOT 0
~$string_read_cell(S_capture,n_old)
$call_reference_operand_valid(S_capture,REFERENCE n_old)
$string_read_capture(S_capture,poperand) = eps
$string_read_key_capture(S_capture,poperand,pvalue_base) = eps
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL eps,KEYCELL (n_old),KEYREF true,PHASE STRING_LEADING 1}
pkeyread.INPUT = poperand /\ pkeyread.VALUE = pvalue_raw
pkeyread.BASE = pvalue_base /\ pkeyread.OWNERS = BASE_VALUE (KNOWN pvalue_base)
pkeyread.PHASE = KEY_NULL /\ pkeyread.LINE = 18
$origin_child((pkeyread.SITE),[PCFIELD 0]) = (porigin_base)
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary (NExprConstFetch (NName (BYTES text_cond) metadata_name) metadata_cond) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)
$base64(text_cond) = $ptascii("FaLsE")
$ptlc($base64(text_cond)) = $ptascii("false")
$base64(text_right) = $ptascii("abc")
$compiled_read(S_capture,porigin_base) = eps
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_right)
$compiled_read(S_capture,porigin_left) = (PBOOL false)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_absent)
$origin_node(S_capture.SOURCES,porigin_absent) = eps
~$truth(S_capture,PBOOL false)
$compiled_read(S_capture,porigin_right) = (PSTRING ($ptascii("abc")))
$compiled_string_value(S_capture,porigin_right,PSTRING ($ptascii("abc"))) = pvalue_base
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,pvalue_wrong)
$string_read_raw_capture(S_capture,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
$string_read_raw_saved(S_capture,pstringread) = (1)
$string_read_source(S_capture,pstringread)
$key_read_input_source(S_capture,pkeyread)
$key_read_owners_source(S_capture,pkeyread)
$base_nodes(pkeyread.OWNERS) = eps
$task_nodes(KEY_READ_DIM poperand 18 KEY_R) = eps
$task_nodes(STRING_READ_RESULT pstringread) = eps
H_capture = {NODES ([HCELL n_old,HCELL n_got]),EDGES eps,ROOTS ([HCELL n_got,HCELL n_old,HCELL n_old]),DEBTS eps}
$heap_graph(S_capture) = H_capture
$heap_owners(H_capture,HCELL n_old) = 2
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 18
perrorcall.MESSAGE = $ptascii("Illegal string offset ") ++ [34] ++ $ptascii("1x") ++ [34]
$error_call_valid(S_before,perrorcall)
$heap_graph(S_before) = H_capture /\ S_before.STORE = S_capture.STORE
''') + guards('S_capture') + guards('S_before') + seek('S_before', 1, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.COMPLETION = NORMAL /\ S.CURRENT = eps /\ S.FRAMES = eps
S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
$lookup(S.ENV,$ptascii("alias")) = (n_old)
$lookup(S.ENV,$ptascii("key")) = (n_current)
n_current =/= n_old /\ n_current =/= n_got
S.STORE[n_old] = DEFINED (PSTRING perrorcall.MESSAGE)
S.STORE[n_current] = DEFINED (PINT 2)
S.STORE[n_got] = DEFINED (PINT 99)
n_old <- S.REFCELLS /\ n_current <- S.REFCELLS
$heap_owners($heap_graph(S),HCELL n_old) = 1
$heap_owners($heap_graph(S),HCELL n_current) = 1
$string_read_raw_known_base(S,porigin_base,pvalue_base)
$string_read_source(S,pstringread)
$string_read_raw_saved(S,pstringread) = (1)
$string_read_ready(S,pstringread)
$string_read_provider_ready(S,pstringread)
$string_read_callback_raw_key(S,pstringread) = eps
$task_nodes(STRING_READ_RESULT pstringread) = eps
H = {NODES ([HCELL n_old,HCELL n_got,HCELL n_current]),EDGES eps,ROOTS ([HCELL n_current,HCELL n_got,HCELL n_old]),DEBTS eps}
$heap_graph(S) = H
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
S_done.STORE[n_got] = DEFINED (PSTRING_CARRIER INTERNED_STRING ([98]))
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("512:1x;2:Illegal string offset ") ++ [34] ++ $ptascii("1x") ++ [34] ++ $ptascii(";R:b;K:2;A:Illegal string offset ") ++ [34] ++ $ptascii("1x") ++ [34] ++ $ptascii(";Z;")
''') + guards('S') + guards('S_after') + guards('S_done')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','RESULT','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks.append('S_capture = $initial_state(NORMAL)' + ''.join('[.' + field + ' = S_capture.' + field + ']' for field in fields))
    derived_start = len(checks)
    checks += lines(r'''
S_wrong_base = S_capture[.RESULT = KNOWN pvalue_wrong]
$string_read_raw_capture(S_wrong_base,poperand,pvalue_wrong) = eps
$string_read_plan(S_wrong_base) = eps
~$string_read_raw_known_base(S_capture,porigin_base,PBOOL false)
$string_read_raw_capture(S_capture[.RESULT = KNOWN (PBOOL false)],poperand,PBOOL false) = eps
pstringread_wrong = pstringread[.READ.BASE = pvalue_wrong][.READ.OWNERS = BASE_VALUE (KNOWN pvalue_wrong)]
$string_read_raw_saved(S,pstringread_wrong) = eps
~$string_read_source(S,pstringread_wrong)
S_capture.POOLS = [ppool]
porigin_left = PORIGIN n_unit pcpath_left
n_unit = ppool.UNIT
porigin_right = PORIGIN n_unit pcpath_right
S_wrong_left = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left PNULL) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_wrong_left,porigin_base,pvalue_base)
$string_read_plan(S_wrong_left) = eps
S_wrong_true = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PBOOL true)) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_wrong_true,porigin_base,pvalue_base)
$string_read_plan(S_wrong_true) = eps
S_wrong_right = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PSTRING ($ptascii("bad")))) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_wrong_right,porigin_base,pvalue_base)
S_wrong_condition = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PINT 0)) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_wrong_condition,porigin_base,pvalue_base)
$string_read_plan(S_wrong_condition) = eps
porigin_base = PORIGIN n_unit pcpath_base
S_capture.CODE = [pcode]
n_unit = pcode.UNIT
S_parent_constant = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base (PSTRING ($ptascii("abc")))) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 18 true) :: pcode.EXPRESSIONS]]]
$compiled_read(S_parent_constant,porigin_base) = (PSTRING ($ptascii("abc")))
~$string_read_raw_known_base(S_parent_constant,porigin_base,pvalue_base)
$string_read_plan(S_parent_constant) = eps
S_bad_heap = S_capture[.ENV = (BIND ($ptascii("ghost")) 99) :: S_capture.ENV]
~$heap_valid($heap_graph(S_bad_heap))
$string_read_raw_capture(S_bad_heap,poperand,pvalue_base) = eps
~$string_read_source(S,pstringread[.BASECELL = (n_old)])
~$string_read_source(S,pstringread[.KEYCELL = eps])
~$string_read_source(S,pstringread[.READ.LINE = 19])
~$string_read_source(S,pstringread[.READ.INPUT = KNOWN pvalue_raw])
~$string_read_source(S,pstringread[.READ.PHASE = KEY_CV])
~$string_read_shape(S,pstringread[.PHASE = STRING_LEADING 2])
~$string_read_source(S,pstringread[.PHASE = STRING_CAST])
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
expression_qualified_condition = NExprConstFetch (NNameFullyQualified (BYTES text_cond) metadata_name) metadata_cond
expression_qualified_base = NExprTernary expression_qualified_condition ABSENT (NScalarString (BYTES text_right) metadata_right) metadata
S_qualified = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_qualified_base) :: (PCOCCURRENCE pcpath_left expression_qualified_condition) :: pcunit.OCCURRENCES]]]
$origin_node(S_qualified.SOURCES,porigin_base) = (expression_qualified_base)
$origin_node(S_qualified.SOURCES,porigin_left) = (expression_qualified_condition)
$compiled_read(S_qualified,porigin_left) = (PBOOL false)
~$string_read_raw_known_base(S_qualified,porigin_base,pvalue_base)
$string_read_raw_capture(S_qualified,poperand,pvalue_base) = eps
$string_read_plan(S_qualified) = eps
''')
    for field in ('SOURCES','CODE','POOLS'):
        checks += [f'~$string_read_raw_known_base(S_capture[.{field} = eps],porigin_base,pvalue_base)',
                   f'$string_read_plan(S_capture[.{field} = eps]) = eps',
                   f'~$string_read_source(S[.{field} = eps],pstringread)']
    checks += ['$string_read_plan(S_capture[.ORIGIN = eps]) = eps',
               '~$string_read_source(S[.ORIGIN = eps],pstringread)']
    for value in ('PSTRING ($ptascii("1"))', 'PSTRING ($ptascii("word"))',
                  'PSTRING ($ptascii("1.5x"))', 'PSTRING ($ptascii("9223372036854775808x"))',
                  'PSTRING ([49,0,120])', 'PSTRING ([256])'):
        checks.append(f'$string_read_raw_capture(S_capture[.STORE[n_old] = DEFINED ({value})],poperand,pvalue_base) = eps')
    for value in ('PSTRING ($ptascii("abc"))',
                  'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))',
                  'PSTRING_CARRIER INTERNED_STRING ([97,0,99])'):
        checks.append(f'$string_read_raw_leading({value},pvalue_raw) = eps')
    for update in ('.CVS = eps', '.ENV = eps', '.STORE[n_old] = UNDEFINED',
                   '.PROPREFS = [{CELL n_old,SOURCES eps}]',
                   '.REFCOERCIONS = [{CELL n_old,SITE pkeyread.SITE,LINE 18,VALUE $ptascii("word")}]',
                   '.PARAMETERBACKINGS = [{FUNCTION pkeyread.SITE,INDEX 0,CELL n_old,LINE 18,VALUE $ptascii("word")}]',
                   '.ALLOCATIONS = $native_remove_one(S_capture.ALLOCATIONS,HCELL n_old)'):
        checks.append(f'$string_read_raw_capture(S_capture[{update}],poperand,pvalue_base) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
