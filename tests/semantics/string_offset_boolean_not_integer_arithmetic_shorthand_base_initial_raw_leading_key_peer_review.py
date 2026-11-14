"""Direct integer arithmetic preserves a shorthand base through initial-key reference rebinding."""
import json

from string_offset_retained_carrier_protocol import PREFIX as RETAINED_PREFIX, lines
from string_offset_undefined_cv_review import guards


PREFIX = RETAINED_PREFIX + r'''
dec $integer_arithmetic_peer_front(pstate, nat) : bool
def $integer_arithmetic_peer_front(S, 0) = true
  -- if S.TODO = (KEY_READ_DIM (VARIABLE n_name* 18) 18 KEY_R) :: ptask*
  -- if n_name* = $ptascii("key")
def $integer_arithmetic_peer_front(S, 1) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_LEADING 1
def $integer_arithmetic_peer_front(S, n) = false -- otherwise
dec $integer_arithmetic_peer_seek(pstate, nat, nat) : pstate
def $integer_arithmetic_peer_seek(S, n_stage, n) = S
  -- if $integer_arithmetic_peer_front(S, n_stage)
def $integer_arithmetic_peer_seek(S, n_stage, n) = S
  -- if ~$integer_arithmetic_peer_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $integer_arithmetic_peer_seek(S, n_stage, 0) = S
  -- if ~$integer_arithmetic_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $integer_arithmetic_peer_seek(S, n_stage, n) = $integer_arithmetic_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$integer_arithmetic_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def seek(start, stage, result):
    return [f'{result}_found = $integer_arithmetic_peer_seek({start},{stage},1000)',
            rf'{result}_found.COMPLETION = NORMAL \/ {result}_found.COMPLETION = BUDGET',
            f'{result} = {result}_found[.COMPLETION = NORMAL]']


def render(program, filename_b64):
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture') + lines(r'''
$integer_arithmetic_peer_front(S_capture,0)
S_capture.CURRENT = eps /\ S_capture.FRAMES = eps
poperand = VARIABLE ($ptascii("key")) 18
S_capture.TODO = (KEY_READ_DIM poperand 18 KEY_R) :: ptask_tail*
pvalue_base = PSTRING_CARRIER INTERNED_STRING ($ptascii("abc"))
pvalue_raw = PSTRING ($ptascii("1x"))
S_capture.RESULT = KNOWN pvalue_base
$lookup(S_capture.ENV,$ptascii("key")) = (n_old)
$lookup(S_capture.ENV,$ptascii("alias")) = (n_old)
$lookup(S_capture.ENV,$ptascii("got")) = (n_got)
n_old = 0 /\ n_got = 1
n_key_cell? = (n_old)
S_capture.STORE[n_old] = DEFINED pvalue_raw
S_capture.STORE[n_got] = DEFINED (PINT 99)
S_capture.REFCELLS = [n_old]
~$string_read_cell(S_capture,n_old)
$call_reference_operand_valid(S_capture,REFERENCE n_old)
$heap_owners($heap_graph(S_capture),HCELL n_old) = 2
$heap_owners($heap_graph(S_capture),HCELL n_got) = 1
$heap_valid($heap_graph(S_capture))
$string_read_capture(S_capture,poperand) = eps
$string_read_key_capture(S_capture,poperand,pvalue_base) = eps
$string_read_raw_capture(S_capture,poperand,pvalue_base) = ((pvalue_raw,n_key_cell?))
$string_read_base_capture(S_capture,S_capture.RESULT) = ((pvalue_base,eps))
$string_read_raw_leading(pvalue_base,pvalue_raw) = (1)
S_capture.ORIGIN = (porigin)
$origin_child((porigin),[PCFIELD 0]) = (porigin_base)
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary (NExprBooleanNot (NExprBinaryOpMul (NExprUnaryPlus (NExprConstFetch (NName (BYTES text_input) metadata_name) metadata_leaf) metadata_inner) (NScalarInt (INTEGER 2) metadata_right) metadata_product) metadata_cond) ABSENT (NScalarString (BYTES text_false) metadata_false) metadata)
$base64(text_input) = $ptascii("TrUe")
$ptlc($base64(text_input)) = $ptascii("true")
i_left = 1
i_result = 2
$long_range(i_left) /\ $long_range(i_result)
i_result =/= 0
$coerce_number(PBOOL true) = COERCED (NINT 1) false
$base64(text_false) = $ptascii("abc")
$compiled_read(S_capture,porigin_base) = eps
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_node(S_capture.SOURCES,porigin_cond) = (NExprBooleanNot (NExprBinaryOpMul (NExprUnaryPlus (NExprConstFetch (NName (BYTES text_input) metadata_name) metadata_leaf) metadata_inner) (NScalarInt (INTEGER 2) metadata_right) metadata_product) metadata_cond)
pvalue_cond? = $compiled_read(S_capture,porigin_cond)
pvalue_cond? = (PBOOL false)
~$truth(S_capture,PBOOL false)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_product)
$origin_node(S_capture.SOURCES,porigin_product) = (NExprBinaryOpMul (NExprUnaryPlus (NExprConstFetch (NName (BYTES text_input) metadata_name) metadata_leaf) metadata_inner) (NScalarInt (INTEGER 2) metadata_right) metadata_product)
$compiled_read(S_capture,porigin_product) = (PINT i_result)
$origin_child((porigin_product),[PCFIELD 0]) = (porigin_inner)
$origin_node(S_capture.SOURCES,porigin_inner) = (NExprUnaryPlus (NExprConstFetch (NName (BYTES text_input) metadata_name) metadata_leaf) metadata_inner)
$compiled_read(S_capture,porigin_inner) = (PINT i_left)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
$origin_node(S_capture.SOURCES,porigin_leaf) = (NExprConstFetch (NName (BYTES text_input) metadata_name) metadata_leaf)
pvalue_leaf? = $compiled_read(S_capture,porigin_leaf)
pvalue_leaf? = (PBOOL true)
$origin_child((porigin_leaf),[PCFIELD 0]) = (porigin_name)
$origin_node(S_capture.SOURCES,porigin_name) = (NName (BYTES text_input) metadata_name)
$compiled_read(S_capture,porigin_name) = eps
$origin_child((porigin_product),[PCFIELD 1]) = (porigin_right)
$origin_node(S_capture.SOURCES,porigin_right) = (NScalarInt (INTEGER 2) metadata_right)
$compiled_read(S_capture,porigin_right) = (PINT 2)
$unary_apply(S_capture,POSITIVE,PBOOL true,18) = S_capture[.RESULT = KNOWN (PINT i_left)]
$binary_apply(S_capture,MULTIPLY,PINT i_left,PINT 2,18) = S_capture[.RESULT = KNOWN (PINT i_result)]
~$string_read_raw_unary_integer(S_capture,porigin_leaf,i_left)
$string_read_raw_unary_integer(S_capture,porigin_inner,i_left)
$string_read_raw_unary_integer(S_capture,porigin_right,2)
$string_read_raw_unary_integer(S_capture,porigin_product,i_result)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_absent)
$origin_node(S_capture.SOURCES,porigin_absent) = eps
$compiled_read(S_capture,porigin_absent) = eps
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_node(S_capture.SOURCES,porigin_false) = (NScalarString (BYTES text_false) metadata_false)
$compiled_read(S_capture,porigin_false) = (PSTRING ($ptascii("abc")))
$compiled_string_value(S_capture,porigin_false,PSTRING ($ptascii("abc"))) = pvalue_base
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
pkeyread = {SITE porigin,GLOBAL false,MODE KEY_R,INPUT poperand,VALUE pvalue_raw,BASE pvalue_base,OWNERS BASE_VALUE S_capture.RESULT,LINE 18,PHASE KEY_NULL,KEY KSTRING eps,NAME eps}
$key_read_input_source(S_capture,pkeyread)
$key_read_owners_source(S_capture,pkeyread)
pstringread = {READ pkeyread,BASECELL eps,KEYCELL (n_old),KEYREF true,PHASE STRING_LEADING 1}
$string_read_key_reference(S_capture,pstringread.KEYCELL)
$string_read_raw_saved(S_capture,pstringread) = (1)
$string_read_source(S_capture,pstringread)
$base_nodes(pkeyread.OWNERS) = eps
$task_nodes(STRING_READ_RESULT pstringread) = eps
$string_read_plan(S_capture) = (pstringread)
$error_handler_eligible(S_capture,2)
S_capture.STRINGDATA = [$ptascii("512")]
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
    checks += lines(r"""
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
S_capture.CODE = [pcode]
porigin_base = PORIGIN n_unit pcpath_base
porigin_cond = PORIGIN n_unit pcpath_cond
porigin_product = PORIGIN n_unit pcpath_product
porigin_inner = PORIGIN n_unit pcpath_inner
porigin_leaf = PORIGIN n_unit pcpath_leaf
porigin_right = PORIGIN n_unit pcpath_right
porigin_false = PORIGIN n_unit pcpath_false
pcunit.ID = n_unit /\ ppool.UNIT = n_unit /\ pcode.UNIT = n_unit
~$string_read_raw_unary_integer(S_capture,porigin_product,3)
""")
    for label, left, right in (
            ('uncertified_left', 'NScalarInt (INTEGER 3) metadata_inner', 'NScalarInt (INTEGER 2) metadata_right'),
            ('uncertified_right', 'NExprUnaryPlus (NExprConstFetch (NName (BYTES text_input) metadata_name) metadata_leaf) metadata_inner', 'NScalarInt (INTEGER 3) metadata_right'),
            ('direct_true', 'NExprConstFetch (NName (BYTES text_input) metadata_name) metadata_leaf', 'NScalarInt (INTEGER 2) metadata_right')):
        checks += lines(f"""
expression_{label}_left = {left}
expression_{label}_right = {right}
expression_{label}_product = NExprBinaryOpMul expression_{label}_left expression_{label}_right metadata_product
expression_{label}_cond = NExprBooleanNot expression_{label}_product metadata_cond
expression_{label}_base = NExprTernary expression_{label}_cond ABSENT (NScalarString (BYTES text_false) metadata_false) metadata
S_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_product expression_{label}_product) :: (PCOCCURRENCE pcpath_inner expression_{label}_left) :: (PCOCCURRENCE pcpath_right expression_{label}_right) :: pcunit.OCCURRENCES]]]
$compiled_read(S_{label},porigin_inner) = (PINT 1)
$compiled_read(S_{label},porigin_right) = (PINT 2)
$binary_apply(S_{label},MULTIPLY,PINT 1,PINT 2,0) = S_{label}[.RESULT = KNOWN (PINT 2)]
~$string_read_raw_unary_integer(S_{label},porigin_product,2)
~$string_read_raw_known_base(S_{label},porigin_base,pvalue_base)
$string_read_plan(S_{label}) = eps
""")

    def integer(value):
        return str(value) if value >= 0 else f'$({value})'

    maximum = 9223372036854775807
    minimum = -9223372036854775808
    for label, constructor, left, right, result, admitted in (
            ('add', 'NExprBinaryOpPlus', 5, 2, 7, True),
            ('sub', 'NExprBinaryOpMinus', 5, 2, 3, True),
            ('mul', 'NExprBinaryOpMul', 3, 2, 6, True),
            ('zero_add', 'NExprBinaryOpPlus', 0, 0, 0, True),
            ('zero_sub', 'NExprBinaryOpMinus', 2, 2, 0, True),
            ('max_ok', 'NExprBinaryOpPlus', maximum-1, 1, maximum, True),
            ('overflow_add', 'NExprBinaryOpPlus', maximum, 1, minimum, False),
            ('overflow_sub', 'NExprBinaryOpMinus', -maximum, 2, minimum, False),
            ('overflow_mul', 'NExprBinaryOpMul', maximum, 2, maximum, False),
            ('divide', 'NExprBinaryOpDiv', 4, 2, 2, False),
            ('mod', 'NExprBinaryOpMod', 4, 3, 1, False),
            ('shift', 'NExprBinaryOpShiftLeft', 1, 1, 2, False),
            ('bitwise', 'NExprBinaryOpBitwiseOr', 1, 2, 3, False),
            ('power', 'NExprBinaryOpPow', 2, 2, 4, False)):
        l, r, value = map(integer, (left, right, result))
        left_expression = f'NScalarInt (INTEGER {l}) metadata_inner'
        source_extra = pool_extra = ''
        if left < 0:
            positive = integer(-left)
            left_expression = f'NExprUnaryMinus (NScalarInt (INTEGER {positive}) metadata_leaf) metadata_inner'
            source_extra = f'(PCOCCURRENCE pcpath_leaf (NScalarInt (INTEGER {positive}) metadata_leaf)) :: '
            pool_extra = f'(PCONSTANT pcpath_leaf (PINT {positive})) :: '
        checks += lines(f"""
expression_{label}_left = {left_expression}
expression_{label}_right = NScalarInt (INTEGER {r}) metadata_right
expression_{label}_product = {constructor} expression_{label}_left expression_{label}_right metadata_product
expression_{label}_cond = NExprBooleanNot expression_{label}_product metadata_cond
expression_{label}_base = NExprTernary expression_{label}_cond ABSENT (NScalarString (BYTES text_false) metadata_false) metadata
S_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_product expression_{label}_product) :: (PCOCCURRENCE pcpath_inner expression_{label}_left) :: (PCOCCURRENCE pcpath_right expression_{label}_right) :: {source_extra}pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_product (PINT {value})) :: (PCONSTANT pcpath_inner (PINT {l})) :: (PCONSTANT pcpath_right (PINT {r})) :: {pool_extra}ppool.CONSTANTS]]]
""")
        checks += [f'{"" if admitted else "~"}$string_read_raw_unary_integer(S_{label},porigin_product,{value})',
                   f'{"" if admitted and result != 0 else "~"}$string_read_raw_known_base(S_{label},porigin_base,pvalue_base)']
        if not admitted or result == 0:
            checks.append(f'$string_read_plan(S_{label}) = eps')
    # Coherent raw INTEGER roots exercise the arm subsumed by the general proof.
    # Raw MININT and outside-range nodes remain local fixtures with source credit 0.
    for label, value, admitted in (
            ('minimum', minimum, True), ('maximum', maximum, True),
            ('one', 1, True), ('zero', 0, False),
            ('too_large', maximum + 1, False), ('too_small', minimum - 1, False)):
        value_text = integer(value)
        checks += lines(f"""
expression_literal_{label} = NScalarInt (INTEGER {value_text}) metadata_product
expression_literal_{label}_cond = NExprBooleanNot expression_literal_{label} metadata_cond
expression_literal_{label}_base = NExprTernary expression_literal_{label}_cond ABSENT (NScalarString (BYTES text_false) metadata_false) metadata
S_literal_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_literal_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_literal_{label}_cond) :: (PCOCCURRENCE pcpath_product expression_literal_{label}) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_product (PINT {value_text})) :: ppool.CONSTANTS]]]
$compiled_read(S_literal_{label},porigin_product) = (PINT {value_text})
$string_read_raw_unary_integer(S_literal_{label},porigin_product,{value_text}) = {'true' if minimum <= value <= maximum else 'false'}
$string_read_raw_known_base(S_literal_{label},porigin_base,pvalue_base) = {'true' if admitted else 'false'}
""")
        if not admitted:
            checks.append(f'$string_read_plan(S_literal_{label}) = eps')
    checks += lines(r"""
S_literal_wrong_pool = S_literal_one[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_product (PINT 2)) :: ppool.CONSTANTS]]]
$compiled_read(S_literal_wrong_pool,porigin_product) = (PINT 2)
~$string_read_raw_unary_integer(S_literal_wrong_pool,porigin_product,2)
~$string_read_raw_known_base(S_literal_wrong_pool,porigin_base,pvalue_base)
$string_read_plan(S_literal_wrong_pool) = eps
S_literal_detached = S_literal_one[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_literal_one_base) :: (PCOCCURRENCE pcpath_cond expression_literal_one_cond) :: (PCOCCURRENCE pcpath_product (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]]
$string_read_raw_unary_integer(S_literal_detached,porigin_product,1)
~$string_read_raw_known_base(S_literal_detached,porigin_base,pvalue_base)
$string_read_plan(S_literal_detached) = eps
""")
    for node, values in (
            ('product', ('PINT 0','PINT 3','PFLOAT 0','PINT 9223372036854775808')),
            ('inner', ('PINT 2','PBOOL true','PINT 9223372036854775808')),
            ('right', ('PINT 1','PFLOAT 0','PINT 9223372036854775808')),
            ('leaf', ('PBOOL false','PINT 1','PSTRING ($ptascii("1"))')),
            ('cond', ('PBOOL true','PINT 0')),
            ('false', ('PSTRING ($ptascii("XYZ"))',))):
        for index, value in enumerate(values):
            label = f'{node}_{index}'
            checks += [f'S_pool_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{node} ({value})) :: ppool.CONSTANTS]]]',
                       f'~$string_read_raw_known_base(S_pool_{label},porigin_base,pvalue_base)',
                       f'$string_read_plan(S_pool_{label}) = eps']
    checks += lines(r"""
S_detached_left = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_inner (NScalarInt (INTEGER 1) metadata_inner)) :: pcunit.OCCURRENCES]]]
$string_read_raw_unary_integer(S_detached_left,porigin_inner,1)
~$string_read_raw_unary_integer(S_detached_left,porigin_product,2)
~$string_read_raw_known_base(S_detached_left,porigin_base,pvalue_base)
S_detached_right = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right (NScalarInt (INTEGER 2) eps)) :: pcunit.OCCURRENCES]]]
$string_read_raw_unary_integer(S_detached_right,porigin_right,2)
~$string_read_raw_unary_integer(S_detached_right,porigin_product,2)
~$string_read_raw_known_base(S_detached_right,porigin_base,pvalue_base)
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
""")
    for node in ('cond','product','inner','right','false'):
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
