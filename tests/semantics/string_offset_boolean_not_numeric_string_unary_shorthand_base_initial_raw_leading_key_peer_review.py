"""Quiet numeric-string first signs preserve the shorthand base through key-reference rebinding."""
import base64
import json

from string_offset_retained_carrier_protocol import PREFIX as RETAINED_PREFIX, lines
from string_offset_undefined_cv_review import guards


PREFIX = RETAINED_PREFIX + r'''
dec $numeric_string_unary_peer_front(pstate, nat) : bool
def $numeric_string_unary_peer_front(S, 0) = true
  -- if S.TODO = (KEY_READ_DIM (VARIABLE n_name* 18) 18 KEY_R) :: ptask*
  -- if n_name* = $ptascii("key")
def $numeric_string_unary_peer_front(S, 1) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_LEADING 1
def $numeric_string_unary_peer_front(S, n) = false -- otherwise
dec $numeric_string_unary_peer_seek(pstate, nat, nat) : pstate
def $numeric_string_unary_peer_seek(S, n_stage, n) = S
  -- if $numeric_string_unary_peer_front(S, n_stage)
def $numeric_string_unary_peer_seek(S, n_stage, n) = S
  -- if ~$numeric_string_unary_peer_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $numeric_string_unary_peer_seek(S, n_stage, 0) = S
  -- if ~$numeric_string_unary_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $numeric_string_unary_peer_seek(S, n_stage, n) = $numeric_string_unary_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$numeric_string_unary_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def seek(start, stage, result):
    return [f'{result}_found = $numeric_string_unary_peer_seek({start},{stage},1000)',
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
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary (NExprBooleanNot (NExprUnaryPlus (NScalarString (BYTES text_input) metadata_leaf) metadata_sign) metadata_cond) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata_base)
n_input* = $base64(text_input)
n_input* = $ptascii("-9223372036854775808")
i_min = $(-9223372036854775808)
$long_range(i_min) /\ i_min =/= 0
$startup_bytes(n_input*) /\ $c_string(n_input*) = n_input*
$numeric_string(n_input*) = FULLNUM (NINT i_min)
$coerce_number(PSTRING_CARRIER INTERNED_STRING n_input*) = COERCED (NINT i_min) false
$base64(text_right) = $ptascii("abc")
$compiled_read(S_capture,porigin_base) = eps
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBooleanNot (NExprUnaryPlus (NScalarString (BYTES text_input) metadata_leaf) metadata_sign) metadata_cond)
$compiled_read(S_capture,porigin_cond) = (PBOOL false)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_sign)
$origin_node(S_capture.SOURCES,porigin_sign) = (NExprUnaryPlus (NScalarString (BYTES text_input) metadata_leaf) metadata_sign)
$compiled_read(S_capture,porigin_sign) = (PINT i_min)
$origin_child((porigin_sign),[PCFIELD 0]) = (porigin_leaf)
$origin_node(S_capture.SOURCES,porigin_leaf) = (NScalarString (BYTES text_input) metadata_leaf)
$compiled_read(S_capture,porigin_leaf) = (PSTRING n_input*)
$compiled_string_value(S_capture,porigin_leaf,PSTRING n_input*) = PSTRING_CARRIER INTERNED_STRING n_input*
~$string_read_raw_unary_integer(S_capture,porigin_leaf,i_min)
$string_read_raw_unary_integer(S_capture,porigin_sign,i_min)
$unary_apply(S_capture,POSITIVE,PSTRING_CARRIER INTERNED_STRING n_input*,18) = S_capture[.RESULT = KNOWN (PINT i_min)]
~$truth(S_capture,PBOOL false) /\ $truth(S_capture,PINT i_min)
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
porigin_sign = PORIGIN n_unit pcpath_sign
porigin_leaf = PORIGIN n_unit pcpath_leaf
porigin_right = PORIGIN n_unit pcpath_right
pcunit.ID = n_unit /\ ppool.UNIT = n_unit /\ pcode.UNIT = n_unit
~$string_read_raw_unary_integer(S_capture,porigin_sign,$(i_min + 1))
$numeric_string($ptascii("-9223372036854775808 ")) = FULLNUM (NFLOAT 14114281232179134464)
$unary_apply(S_capture,POSITIVE,PSTRING_CARRIER INTERNED_STRING ($ptascii("-9223372036854775808 ")),18) = S_capture[.RESULT = KNOWN (PFLOAT 14114281232179134464)]
$unary_apply(S_capture,NEGATIVE,PSTRING_CARRIER INTERNED_STRING n_input*,18) = S_capture[.RESULT = KNOWN (PFLOAT 4890909195324358656)]
$coerce_number(PSTRING_CARRIER INTERNED_STRING ($ptascii("2x"))) = COERCED (NINT 2) true
$coerce_number(PSTRING_CARRIER INTERNED_STRING ([50,0])) = COERCED (NINT 2) true
''')
    for label, value in (
            ('other_raw', 'PSTRING ($ptascii("1"))'),
            ('interned', 'PSTRING_CARRIER INTERNED_STRING n_input*'),
            ('request', 'PSTRING_CARRIER (REQUEST_STRING 0) n_input*'),
            ('int', 'PINT i_min'), ('float', 'PFLOAT 14114281232179134464'),
            ('bool', 'PBOOL false'), ('nul', 'PSTRING ([49,0])')):
        checks += [f'S_pool_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_unary_integer(S_pool_{label},porigin_sign,i_min)',
                   f'~$string_read_raw_known_base(S_pool_{label},porigin_base,pvalue_base)',
                   f'$string_read_plan(S_pool_{label}) = eps']
    # Replace all related occurrences and pools together, leaving classification
    # and the complete unary result as the only reason to accept or refuse.
    for label, raw, value, negative, admitted in (
            ('spaced', b' 2 ', '2', False, True),
            ('negative', b'-2', '$(-2)', False, True),
            ('max', b'9223372036854775807', '9223372036854775807', False, True),
            ('minus', b'-1', '1', True, True),
            ('zero', b'0', '0', False, False),
            ('min_space', b'-9223372036854775808 ', 'i_min', False, False),
            ('min_minus', b'-9223372036854775808', 'i_min', True, False),
            ('decimal', b'2.0', '2', False, False),
            ('exponent', b'2e0', '2', False, False),
            ('overflow', b'9223372036854775808', '2', False, False),
            ('leading', b'2x', '2', False, False),
            ('nul', b'2\0', '2', False, False),
            ('junk', b'x', '2', False, False)):
        payload = base64.b64encode(raw).decode()
        constructor = 'NExprUnaryMinus' if negative else 'NExprUnaryPlus'
        checks += lines(f'''
expression_{label}_leaf = NScalarString (BYTES "{payload}") metadata_leaf
expression_{label}_sign = {constructor} expression_{label}_leaf metadata_sign
expression_{label}_cond = NExprBooleanNot expression_{label}_sign metadata_cond
expression_{label}_base = NExprTernary expression_{label}_cond ABSENT (NScalarString (BYTES text_right) metadata_right) metadata_base
S_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_sign expression_{label}_sign) :: (PCOCCURRENCE pcpath_leaf expression_{label}_leaf) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_sign (PINT {value})) :: (PCONSTANT pcpath_leaf (PSTRING ($base64("{payload}")))) :: ppool.CONSTANTS]]]
''')
        checks += [f'{"" if admitted or label == "zero" else "~"}$string_read_raw_unary_integer(S_{label},porigin_sign,{value})',
                   f'{"" if admitted else "~"}$string_read_raw_known_base(S_{label},porigin_base,pvalue_base)']
        if not admitted:
            checks += [f'$string_read_plan(S_{label}) = eps']
    for node, value in (('cond', 'PBOOL true'), ('cond', 'PINT 0'),
                        ('sign', 'PFLOAT 14114281232179134464'),
                        ('sign', 'PINT 9223372036854775808'),
                        ('right', 'PSTRING ($ptascii("XYZ"))')):
        label = len(checks)
        checks += [f'S_pool_wrong_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{node} ({value})) :: ppool.CONSTANTS]]]',
                   f'~$string_read_raw_known_base(S_pool_wrong_{label},porigin_base,pvalue_base)',
                   f'$string_read_plan(S_pool_wrong_{label}) = eps']
    checks += lines(r'''
S_detached = S_spaced[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_leaf expression_spaced_leaf) :: pcunit.OCCURRENCES]]]
~$string_read_raw_unary_integer(S_detached,porigin_sign,2)
~$string_read_raw_known_base(S_detached,porigin_base,pvalue_base)
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
    for node in ('cond', 'sign', 'leaf', 'right'):
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
