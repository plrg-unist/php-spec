"""BooleanNot of a nonzero raw integer unary chain preserves its fallback through reference-key rebinding."""
import json

from string_offset_retained_carrier_protocol import PREFIX as RETAINED_PREFIX, lines
from string_offset_undefined_cv_review import guards


PREFIX = RETAINED_PREFIX + r'''
dec $boolean_not_integer_unary_shorthand_raw_peer_front(pstate, nat) : bool
def $boolean_not_integer_unary_shorthand_raw_peer_front(S, 0) = true
  -- if S.TODO = (KEY_READ_DIM (VARIABLE n_name* 18) 18 KEY_R) :: ptask*
  -- if n_name* = $ptascii("key")
def $boolean_not_integer_unary_shorthand_raw_peer_front(S, 1) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_LEADING 1
def $boolean_not_integer_unary_shorthand_raw_peer_front(S, n) = false -- otherwise
dec $boolean_not_integer_unary_shorthand_raw_peer_seek(pstate, nat, nat) : pstate
def $boolean_not_integer_unary_shorthand_raw_peer_seek(S, n_stage, n) = S
  -- if $boolean_not_integer_unary_shorthand_raw_peer_front(S, n_stage)
def $boolean_not_integer_unary_shorthand_raw_peer_seek(S, n_stage, n) = S
  -- if ~$boolean_not_integer_unary_shorthand_raw_peer_front(S, n_stage)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $boolean_not_integer_unary_shorthand_raw_peer_seek(S, n_stage, 0) = S
  -- if ~$boolean_not_integer_unary_shorthand_raw_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $boolean_not_integer_unary_shorthand_raw_peer_seek(S, n_stage, n) = $boolean_not_integer_unary_shorthand_raw_peer_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$boolean_not_integer_unary_shorthand_raw_peer_front(S, n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
'''


def seek(start, stage, result):
    return [f'{result}_found = $boolean_not_integer_unary_shorthand_raw_peer_seek({start},{stage},1000)',
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
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary (NExprBooleanNot (NExprUnaryPlus (NExprUnaryMinus (NExprUnaryMinus (NScalarInt (INTEGER i_leaf) metadata_leaf) metadata_inner) metadata_outer) metadata_plus) metadata_cond) ABSENT (NScalarString (BYTES text_right) metadata_right) metadata)
i_leaf = 9223372036854775807 /\ $long_range(i_leaf)
$base64(text_right) = $ptascii("abc")
$compiled_read(S_capture,porigin_base) = eps
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_node(S_capture.SOURCES,porigin_left) = (NExprBooleanNot (NExprUnaryPlus (NExprUnaryMinus (NExprUnaryMinus (NScalarInt (INTEGER i_leaf) metadata_leaf) metadata_inner) metadata_outer) metadata_plus) metadata_cond)
$compiled_read(S_capture,porigin_left) = (PBOOL false)
~$truth(S_capture,PBOOL false)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_plus)
$origin_node(S_capture.SOURCES,porigin_plus) = (NExprUnaryPlus (NExprUnaryMinus (NExprUnaryMinus (NScalarInt (INTEGER i_leaf) metadata_leaf) metadata_inner) metadata_outer) metadata_plus)
$compiled_read(S_capture,porigin_plus) = (PINT i_leaf)
$origin_child((porigin_plus),[PCFIELD 0]) = (porigin_outer)
$origin_node(S_capture.SOURCES,porigin_outer) = (NExprUnaryMinus (NExprUnaryMinus (NScalarInt (INTEGER i_leaf) metadata_leaf) metadata_inner) metadata_outer)
$compiled_read(S_capture,porigin_outer) = (PINT i_leaf)
$origin_child((porigin_outer),[PCFIELD 0]) = (porigin_inner)
$origin_node(S_capture.SOURCES,porigin_inner) = (NExprUnaryMinus (NScalarInt (INTEGER i_leaf) metadata_leaf) metadata_inner)
$compiled_read(S_capture,porigin_inner) = (PINT $(0 - i_leaf))
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
$origin_node(S_capture.SOURCES,porigin_leaf) = (NScalarInt (INTEGER i_leaf) metadata_leaf)
$compiled_read(S_capture,porigin_leaf) = (PINT i_leaf)
$unary_apply(S_capture,NEGATIVE,PINT i_leaf,18) = S_capture[.RESULT = KNOWN (PINT $(0 - i_leaf))]
$unary_apply(S_capture,NEGATIVE,PINT $(0 - i_leaf),18) = S_capture[.RESULT = KNOWN (PINT i_leaf)]
$unary_apply(S_capture,POSITIVE,PINT i_leaf,18) = S_capture[.RESULT = KNOWN (PINT i_leaf)]
$truth(S_capture,PINT i_leaf)
$string_read_raw_unary_integer(S_capture,porigin_leaf,i_leaf)
$string_read_raw_unary_integer(S_capture,porigin_inner,$(0 - i_leaf))
$string_read_raw_unary_integer(S_capture,porigin_outer,i_leaf)
$string_read_raw_unary_integer(S_capture,porigin_plus,i_leaf)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_absent)
$origin_node(S_capture.SOURCES,porigin_absent) = eps
~$truth(S_capture,PBOOL false)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_right)
$compiled_read(S_capture,porigin_right) = (PSTRING ($ptascii("abc")))
$origin_node(S_capture.SOURCES,porigin_right) = (NScalarString (BYTES text_right) metadata_right)
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
porigin_base = PORIGIN n_unit pcpath_base
n_unit = ppool.UNIT
porigin_left = PORIGIN n_unit pcpath_left
porigin_plus = PORIGIN n_unit pcpath_plus
porigin_outer = PORIGIN n_unit pcpath_outer
porigin_inner = PORIGIN n_unit pcpath_inner
porigin_leaf = PORIGIN n_unit pcpath_leaf
porigin_right = PORIGIN n_unit pcpath_right
S_capture.SOURCES = [pcunit]
pcunit.ID = n_unit
~$string_read_raw_unary_integer(S_capture,porigin_plus,$(i_leaf - 1))
~$string_read_raw_unary_integer(S_capture,porigin_left,i_leaf)
''')
    for index, value in enumerate(('PBOOL true', 'PNULL', 'PINT 0', 'PFLOAT 0')):
        checks += [f'S_bad_condition_{index} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left ({value})) :: ppool.CONSTANTS]]]',
                   f'$compiled_read(S_bad_condition_{index},porigin_left) = ({value})',
                   f'~$string_read_raw_known_base(S_bad_condition_{index},porigin_base,pvalue_base)',
                   f'$string_read_plan(S_bad_condition_{index}) = eps']
    for node in ('plus', 'outer', 'inner', 'leaf'):
        for index, value in enumerate(('PINT 0', 'PBOOL true', 'PFLOAT 0')):
            label = f'{node}_{index}'
            checks += [f'S_bad_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{node} ({value})) :: ppool.CONSTANTS]]]',
                       f'$compiled_read(S_bad_{label},porigin_{node}) = ({value})',
                       f'~$string_read_raw_unary_integer(S_bad_{label},porigin_plus,i_leaf)',
                       f'~$string_read_raw_known_base(S_bad_{label},porigin_base,pvalue_base)',
                       f'$string_read_plan(S_bad_{label}) = eps']
    checks += lines(r'''
S_wrong_right = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PSTRING ($ptascii("bad")))) :: ppool.CONSTANTS]]]
~$string_read_raw_known_base(S_wrong_right,porigin_base,pvalue_base)
$string_read_plan(S_wrong_right) = eps
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
expression_detached_fallback = NExprBinaryOpConcat (NScalarString (BYTES "YQ==") metadata_right) (NScalarString (BYTES "YmM=") metadata_right) metadata_right
S_detached_fallback = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right expression_detached_fallback) :: pcunit.OCCURRENCES]]]
$compiled_read(S_detached_fallback,porigin_right) = (PSTRING ($ptascii("abc")))
$compiled_string_value(S_detached_fallback,porigin_right,PSTRING ($ptascii("abc"))) = pvalue_base
~$string_read_raw_known_base(S_detached_fallback,porigin_base,pvalue_base)
$string_read_plan(S_detached_fallback) = eps
''')
    for node, value in (('plus', 'i_leaf'), ('outer', 'i_leaf'), ('inner', '$(0 - i_leaf)')):
        checks += [f'expression_detached_{node} = NScalarInt (INTEGER {value}) metadata_leaf',
                   f'S_detached_{node} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{node} expression_detached_{node}) :: pcunit.OCCURRENCES]]]',
                   f'$compiled_read(S_detached_{node},porigin_{node}) = (PINT {value})',
                   f'$string_read_raw_unary_integer(S_detached_{node},porigin_{node},{value})',
                   f'~$string_read_raw_known_base(S_detached_{node},porigin_base,pvalue_base)',
                   f'$string_read_plan(S_detached_{node}) = eps']
    # These raw signed leaves and source/pool variants are constructed source-zero guards.
    for label, leaf, v, good in (
            ('small', 'NScalarInt (INTEGER 1) metadata_leaf', '1', True),
            ('negative', 'NScalarInt (INTEGER i_negative) metadata_leaf', 'i_negative', True),
            ('zero', 'NScalarInt (INTEGER 0) metadata_leaf', '0', False),
            ('wide', 'NScalarInt (INTEGER 9223372036854775808) metadata_leaf', '9223372036854775808', False),
            ('name', 'NExprConstFetch (NName (BYTES "UEhQX0lOVF9NQVg=") metadata_leaf) metadata_leaf', 'i_leaf', False),
            ('float', 'NScalarFloat (FLOAT "43e0000000000000") metadata_leaf', 'i_leaf', False)):
        if label == 'negative':
            checks += ['i_negative = $(-7)']
        expressions = [('leaf', leaf),
                       ('inner', f'NExprUnaryMinus expression_{label}_leaf metadata_inner'),
                       ('outer', f'NExprUnaryMinus expression_{label}_inner metadata_outer'),
                       ('plus', f'NExprUnaryPlus expression_{label}_outer metadata_plus'),
                       ('left', f'NExprBooleanNot expression_{label}_plus metadata_cond'),
                       ('base', f'NExprTernary expression_{label}_left ABSENT (NScalarString (BYTES text_right) metadata_right) metadata')]
        checks += [f'expression_{label}_{node} = {expression}' for node, expression in expressions]
        occurrences = ' :: '.join(f'(PCOCCURRENCE pcpath_{node} expression_{label}_{node})' for node, _ in reversed(expressions))
        constants = ' :: '.join(f'(PCONSTANT pcpath_{node} (PINT {value}))' for node, value in
                               [('leaf', v), ('inner', f'$(0 - {v})'), ('outer', v), ('plus', v)])
        checks += [f'S_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = {occurrences} :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = {constants} :: ppool.CONSTANTS]]]',
                   f'$compiled_read(S_{label},porigin_plus) = (PINT {v})',
                   f'$compiled_read(S_{label},porigin_left) = (PBOOL false)']
        if good:
            checks += [f'$string_read_raw_unary_integer(S_{label},porigin_plus,{v})',
                       f'$string_read_raw_known_base(S_{label},porigin_base,pvalue_base)']
        else:
            checks += [f'~$string_read_raw_known_base(S_{label},porigin_base,pvalue_base)',
                       f'$string_read_plan(S_{label}) = eps']
            if label == 'zero':
                checks += ['$string_read_raw_unary_integer(S_zero,porigin_plus,0)']
            else:
                checks += [f'~$string_read_raw_unary_integer(S_{label},porigin_plus,{v})']
    checks += lines(r'''
expression_min_leaf = NScalarInt (INTEGER $(-9223372036854775808)) metadata_leaf
expression_min_inner = NExprUnaryMinus expression_min_leaf metadata_inner
expression_min_outer = NExprUnaryMinus expression_min_inner metadata_outer
expression_min_plus = NExprUnaryPlus expression_min_outer metadata_plus
expression_min_left = NExprBooleanNot expression_min_plus metadata_cond
expression_min_base = NExprTernary expression_min_left ABSENT (NScalarString (BYTES text_right) metadata_right) metadata
S_min_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_min_base) :: (PCOCCURRENCE pcpath_left expression_min_left) :: (PCOCCURRENCE pcpath_plus expression_min_plus) :: (PCOCCURRENCE pcpath_outer expression_min_outer) :: (PCOCCURRENCE pcpath_inner expression_min_inner) :: (PCOCCURRENCE pcpath_leaf expression_min_leaf) :: pcunit.OCCURRENCES]]]
S_min_wrapped = S_min_source[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PINT $(-9223372036854775808))) :: (PCONSTANT pcpath_inner (PINT $(-9223372036854775808))) :: (PCONSTANT pcpath_outer (PINT $(-9223372036854775808))) :: (PCONSTANT pcpath_plus (PINT $(-9223372036854775808))) :: ppool.CONSTANTS]]]
$string_read_raw_unary_integer(S_min_wrapped,porigin_leaf,$(-9223372036854775808))
$unary_apply(S_min_wrapped,NEGATIVE,PINT $(-9223372036854775808),18) = S_min_wrapped[.RESULT = KNOWN (PFLOAT $float_of_int(9223372036854775808))]
~$string_read_raw_unary_integer(S_min_wrapped,porigin_inner,$(-9223372036854775808))
~$string_read_raw_unary_integer(S_min_wrapped,porigin_plus,$(-9223372036854775808))
~$string_read_raw_known_base(S_min_wrapped,porigin_base,pvalue_base)
$string_read_plan(S_min_wrapped) = eps
S_min_float = S_min_source[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf (PINT $(-9223372036854775808))) :: (PCONSTANT pcpath_inner (PFLOAT $float_of_int(9223372036854775808))) :: (PCONSTANT pcpath_outer (PFLOAT $float_of_int($(-9223372036854775808)))) :: (PCONSTANT pcpath_plus (PFLOAT $float_of_int($(-9223372036854775808)))) :: ppool.CONSTANTS]]]
~$string_read_raw_unary_integer(S_min_float,porigin_plus,$(-9223372036854775808))
~$string_read_raw_known_base(S_min_float,porigin_base,pvalue_base)
$string_read_plan(S_min_float) = eps
''')
    for label, expression in (
            ('bitnot', 'NExprBitwiseNot (NScalarInt (INTEGER i_leaf) metadata_leaf) metadata_plus'),
            ('cast', 'NExprCastInt (NScalarInt (INTEGER i_leaf) metadata_leaf) metadata_plus'),
            ('sum', 'NExprBinaryOpPlus (NScalarInt (INTEGER i_leaf) metadata_leaf) (NScalarInt (INTEGER 0) metadata_leaf) metadata_plus')):
        checks += [f'expression_{label} = {expression}',
                   f'expression_{label}_left = NExprBooleanNot expression_{label} metadata_cond',
                   f'expression_{label}_base = NExprTernary expression_{label}_left ABSENT (NScalarString (BYTES text_right) metadata_right) metadata',
                   f'S_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_left expression_{label}_left) :: (PCOCCURRENCE pcpath_plus expression_{label}) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_unary_integer(S_{label},porigin_plus,i_leaf)',
                   f'~$string_read_raw_known_base(S_{label},porigin_base,pvalue_base)',
                   f'$string_read_plan(S_{label}) = eps']
    for field in ('SOURCES', 'CODE', 'POOLS'):
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
