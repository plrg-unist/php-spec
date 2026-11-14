"""Literal true first signs preserve the shorthand base through initial-key reference rebinding."""
import base64
import json

from string_offset_retained_carrier_protocol import PREFIX as RETAINED_PREFIX, lines
from string_offset_undefined_cv_review import guards


PREFIX = RETAINED_PREFIX + r'''
dec $true_unary_peer_front(pstate, nat) : bool
def $true_unary_peer_front(S, 0) = true
  -- if S.TODO = (KEY_READ_DIM (VARIABLE n_name* 18) 18 KEY_R) :: ptask*
  -- if n_name* = $ptascii("key")
def $true_unary_peer_front(S, 1) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_LEADING 1
def $true_unary_peer_front(S, n) = false -- otherwise
dec $true_unary_peer_seek(pstate, nat, nat) : pstate
def $true_unary_peer_seek(S, n_stage, n) = S
  -- if $true_unary_peer_front(S, n_stage)
def $true_unary_peer_seek(S, n_stage, n) = S
  -- if ~$true_unary_peer_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $true_unary_peer_seek(S, n_stage, 0) = S
  -- if ~$true_unary_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $true_unary_peer_seek(S, n_stage, n) = $true_unary_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$true_unary_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def seek(start, stage, result):
    return [f'{result}_found = $true_unary_peer_seek({start},{stage},1000)',
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
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary (NExprBooleanNot (NExprUnaryPlus (NExprUnaryMinus (NExprConstFetch (NName (BYTES text_input) metadata_name) metadata_leaf) metadata_minus) metadata_plus) metadata_cond) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata_base)
$base64(text_input) = $ptascii("TrUe")
$ptlc($base64(text_input)) = $ptascii("true")
i = $(-1)
$long_range(i) /\ i =/= 0
$coerce_number(PBOOL true) = COERCED (NINT 1) false
$base64(text_right) = $ptascii("abc")
$compiled_read(S_capture,porigin_base) = eps
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBooleanNot (NExprUnaryPlus (NExprUnaryMinus (NExprConstFetch (NName (BYTES text_input) metadata_name) metadata_leaf) metadata_minus) metadata_plus) metadata_cond)
$compiled_read(S_capture,porigin_cond) = (PBOOL false)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_plus)
$origin_node(S_capture.SOURCES,porigin_plus) = (NExprUnaryPlus (NExprUnaryMinus (NExprConstFetch (NName (BYTES text_input) metadata_name) metadata_leaf) metadata_minus) metadata_plus)
$compiled_read(S_capture,porigin_plus) = (PINT i)
$origin_child((porigin_plus),[PCFIELD 0]) = (porigin_minus)
$origin_node(S_capture.SOURCES,porigin_minus) = (NExprUnaryMinus (NExprConstFetch (NName (BYTES text_input) metadata_name) metadata_leaf) metadata_minus)
$compiled_read(S_capture,porigin_minus) = (PINT i)
$origin_child((porigin_minus),[PCFIELD 0]) = (porigin_leaf)
$origin_node(S_capture.SOURCES,porigin_leaf) = (NExprConstFetch (NName (BYTES text_input) metadata_name) metadata_leaf)
$compiled_read(S_capture,porigin_leaf) = (PBOOL true)
$origin_child((porigin_leaf),[PCFIELD 0]) = (porigin_name)
$origin_node(S_capture.SOURCES,porigin_name) = (NName (BYTES text_input) metadata_name)
$compiled_read(S_capture,porigin_name) = eps
~$string_read_raw_unary_integer(S_capture,porigin_leaf,i)
$string_read_raw_unary_integer(S_capture,porigin_minus,i)
$string_read_raw_unary_integer(S_capture,porigin_plus,i)
$unary_apply(S_capture,NEGATIVE,PBOOL true,18) = S_capture[.RESULT = KNOWN (PINT i)]
$unary_apply(S_capture,POSITIVE,PINT i,18) = S_capture[.RESULT = KNOWN (PINT i)]
~$truth(S_capture,PBOOL false) /\ $truth(S_capture,PINT i)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_absent)
$origin_node(S_capture.SOURCES,porigin_absent) = eps
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_right)
$origin_node(S_capture.SOURCES,porigin_right) = (NScalarString (BYTES text_right) metadata_right)
$compiled_read(S_capture,porigin_right) = (PSTRING ($ptascii("abc")))
$compiled_string_value(S_capture,porigin_right,PSTRING ($ptascii("abc"))) = pvalue_base
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
$string_read_raw_capture(S_capture,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
$string_read_raw_saved(S_capture,pstringread) = (1)
$string_read_source(S_capture,pstringread)
H_capture = {NODES ([HCELL n_old,HCELL n_got]),EDGES eps,ROOTS ([HCELL n_got,HCELL n_old,HCELL n_old]),DEBTS eps}
$heap_graph(S_capture) = H_capture
$heap_owners(H_capture,HCELL n_old) = 2
$base_nodes(pkeyread.OWNERS) = eps
$task_nodes(STRING_READ_RESULT pstringread) = eps
PhpStep: S_capture ~> S_before
S_before.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_before*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 18
perrorcall.MESSAGE = $ptascii("Illegal string offset \"1x\"")
$error_call_valid(S_before,perrorcall)
$heap_graph(S_before) = H_capture /\ S_before.STORE = S_capture.STORE
$drive_steps(S_capture,0) = S_capture[.COMPLETION = BUDGET]
$drive_steps(S_capture,1) = S_before[.COMPLETION = BUDGET]
$drive_steps(S_before,1) = $drive_steps(S_capture,2)
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
$string_read_raw_saved(S,pstringread) = (1)
$string_read_source(S,pstringread)
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
$retained_outputs(S_done.EVENTS) = $ptascii("512:1x;2:Illegal string offset \"1x\";R:b;K:2;A:Illegal string offset \"1x\";Z;")
''') + guards('S') + guards('S_after') + guards('S_done')
    fields = ('DECLARATIONS','STRINGDATA','ERRORHANDLER','ERRORHANDLERS','FUNCTIONS','CALLABLES','SYMBOLS','CVS','TODO','EVENTS','ENV','STORE','REFCELLS','RESULT','ALLOCATIONS','SOURCES','ORIGIN','POOLS','FILES','CODE')
    checks.append('S_capture = $initial_state(NORMAL)' + ''.join('[.' + field + ' = S_capture.' + field + ']' for field in fields))
    derived_start = len(checks)
    checks += lines(r'''
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
S_capture.CODE = [pcode]
porigin_base = PORIGIN n_unit pcpath_base
porigin_cond = PORIGIN n_unit pcpath_cond
porigin_plus = PORIGIN n_unit pcpath_plus
porigin_minus = PORIGIN n_unit pcpath_minus
porigin_leaf = PORIGIN n_unit pcpath_leaf
porigin_name = PORIGIN n_unit pcpath_name
porigin_right = PORIGIN n_unit pcpath_right
pcunit.ID = n_unit /\ ppool.UNIT = n_unit /\ pcode.UNIT = n_unit
~$string_read_raw_unary_integer(S_capture,porigin_minus,1)
~$string_read_raw_unary_integer(S_capture,porigin_plus,1)
$coerce_number(PBOOL false) = COERCED (NINT 0) false
$coerce_number(PNULL) = COERCED (NINT 0) false
$unary_apply(S_capture,NEGATIVE,PBOOL false,18) = S_capture[.RESULT = KNOWN (PINT 0)]
$unary_apply(S_capture,POSITIVE,PNULL,18) = S_capture[.RESULT = KNOWN (PINT 0)]
''')
    # Rebuild the entire source chain and its constant leaf, so name refusals
    # cannot succeed merely because an enclosing occurrence was left stale.
    for label, constructor, raw, pool, admitted in (
            ('upper', 'NName', b'TRUE', 'PBOOL true', True),
            ('lower', 'NName', b'true', 'PBOOL true', True),
            ('false', 'NName', b'false', 'PBOOL false', False),
            ('null', 'NName', b'null', 'PNULL', False),
            ('false_spoof', 'NName', b'false', 'PBOOL true', False),
            ('null_spoof', 'NName', b'null', 'PBOOL true', False),
            ('other', 'NName', b'other', 'PBOOL true', False),
            ('qualified', 'NName', b'Foo\\true', 'PBOOL true', False),
            ('fqn', 'NNameFullyQualified', b'true', 'PBOOL true', False),
            ('relative', 'NNameRelative', b'true', 'PBOOL true', False),
            ('nul', 'NName', b'true\0', 'PBOOL true', False)):
        payload = base64.b64encode(raw).decode()
        value = '0' if label in ('false', 'null') else 'i'
        checks += lines(f'''
name_{label} = {constructor} (BYTES "{payload}") metadata_name
expression_{label}_leaf = NExprConstFetch name_{label} metadata_leaf
expression_{label}_minus = NExprUnaryMinus expression_{label}_leaf metadata_minus
expression_{label}_plus = NExprUnaryPlus expression_{label}_minus metadata_plus
expression_{label}_cond = NExprBooleanNot expression_{label}_plus metadata_cond
expression_{label}_base = NExprTernary expression_{label}_cond ABSENT (NScalarString (BYTES text_right) metadata_right) metadata_base
S_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_plus expression_{label}_plus) :: (PCOCCURRENCE pcpath_minus expression_{label}_minus) :: (PCOCCURRENCE pcpath_leaf expression_{label}_leaf) :: (PCOCCURRENCE pcpath_name name_{label}) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_plus (PINT {value})) :: (PCONSTANT pcpath_minus (PINT {value})) :: (PCONSTANT pcpath_leaf ({pool})) :: ppool.CONSTANTS]]]
''')
        for node in ('minus', 'plus'):
            checks.append(f'{"" if admitted else "~"}$string_read_raw_unary_integer(S_{label},porigin_{node},{value})')
        checks.append(f'{"" if admitted else "~"}$string_read_raw_known_base(S_{label},porigin_base,pvalue_base)')
        if not admitted:
            checks.append(f'$string_read_plan(S_{label}) = eps')
    for node, values in (('leaf', ('PBOOL false', 'PNULL', 'PINT 1', 'PFLOAT 4607182418800017408', 'PSTRING ($ptascii("1"))')),
                         ('minus', ('PINT 0', 'PINT 1', 'PINT 9223372036854775808', 'PFLOAT 13830554455654793216')),
                         ('plus', ('PINT 0', 'PINT 1', 'PINT 9223372036854775808', 'PBOOL true')),
                         ('cond', ('PBOOL true', 'PINT 0')),
                         ('right', ('PSTRING ($ptascii("XYZ"))',))):
        for index, value in enumerate(values):
            label = f'{node}_{index}'
            checks += [f'S_pool_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{node} ({value})) :: ppool.CONSTANTS]]]',
                       f'~$string_read_raw_known_base(S_pool_{label},porigin_base,pvalue_base)',
                       f'$string_read_plan(S_pool_{label}) = eps']
            if node in ('leaf', 'minus'):
                checks.append(f'~$string_read_raw_unary_integer(S_pool_{label},porigin_minus,i)')
    checks += lines(r'''
S_detached_name = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_name (NName (BYTES "VFJVRQ==") metadata_name)) :: pcunit.OCCURRENCES]]]
~$string_read_raw_unary_integer(S_detached_name,porigin_minus,i)
~$string_read_raw_unary_integer(S_detached_name,porigin_plus,i)
~$string_read_raw_known_base(S_detached_name,porigin_base,pvalue_base)
$string_read_plan(S_detached_name) = eps
S_detached_leaf = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_leaf expression_upper_leaf) :: pcunit.OCCURRENCES]]]
~$string_read_raw_unary_integer(S_detached_leaf,porigin_minus,i)
~$string_read_raw_known_base(S_detached_leaf,porigin_base,pvalue_base)
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
''')
    for node in ('cond', 'plus', 'minus', 'leaf', 'right'):
        checks += [f'S_code_{node} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} 18 false) :: pcode.EXPRESSIONS]]]',
                   f'~$string_read_raw_known_base(S_code_{node},porigin_base,pvalue_base)',
                   f'$string_read_plan(S_code_{node}) = eps']
    for field in ('SOURCES','CODE','POOLS'):
        checks += [f'~$string_read_raw_known_base(S_capture[.{field} = eps],porigin_base,pvalue_base)',
                   f'$string_read_plan(S_capture[.{field} = eps]) = eps',
                   f'~$string_read_source(S[.{field} = eps],pstringread)']
    for value in ('PBOOL false', 'PSTRING ($ptascii("abc"))',
                  'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("abc"))',
                  'PSTRING_CARRIER INTERNED_STRING ([97,0,99])'):
        checks.append(f'$string_read_raw_capture(S_capture[.RESULT = KNOWN ({value})],poperand,{value}) = eps')
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks), len(checks) - derived_start)
