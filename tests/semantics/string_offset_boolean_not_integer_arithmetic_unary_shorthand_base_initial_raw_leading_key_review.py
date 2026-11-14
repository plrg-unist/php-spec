"""Quiet signed64 arithmetic trees retain a shorthand base and its initial raw offset through a Warning."""
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
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary expression_cond ABSENT (NScalarString (BYTES text_false) metadata_false) metadata)
expression_cond = NExprBooleanNot expression_unary metadata_cond
expression_unary = NExprUnaryMinus expression_sub metadata_minus
expression_sub = NExprBinaryOpMinus expression_add expression_one metadata_sub
expression_add = NExprBinaryOpPlus expression_left expression_right metadata_add
expression_left = NScalarInt (INTEGER 1) metadata_left
expression_right = NScalarInt (INTEGER 2) metadata_right
expression_one = NScalarInt (INTEGER 1) metadata_one
$base64(text_false) = $ptascii("abc")
$compiled_read(S_capture,porigin_base) = eps
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_node(S_capture.SOURCES,porigin_cond) = (expression_cond)
pvalue_cond? = $compiled_read(S_capture,porigin_cond)
pvalue_cond? = (PBOOL false)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_unary)
$origin_node(S_capture.SOURCES,porigin_unary) = (expression_unary)
$compiled_read(S_capture,porigin_unary) = (PINT i_unary)
i_unary = $(-2)
$long_range(i_unary) /\ i_unary =/= 0
$origin_child((porigin_unary),[PCFIELD 0]) = (porigin_sub)
$origin_node(S_capture.SOURCES,porigin_sub) = (expression_sub)
$compiled_read(S_capture,porigin_sub) = (PINT 2)
$origin_child((porigin_sub),[PCFIELD 0]) = (porigin_add)
$origin_node(S_capture.SOURCES,porigin_add) = (expression_add)
$compiled_read(S_capture,porigin_add) = (PINT 3)
$origin_child((porigin_sub),[PCFIELD 1]) = (porigin_one)
$origin_node(S_capture.SOURCES,porigin_one) = (expression_one)
$compiled_read(S_capture,porigin_one) = (PINT 1)
$origin_child((porigin_add),[PCFIELD 0]) = (porigin_left)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
pvalue_leaf? = $compiled_read(S_capture,porigin_left)
pvalue_leaf? = (PINT 1)
$origin_child((porigin_add),[PCFIELD 1]) = (porigin_right)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_right)
$compiled_read(S_capture,porigin_right) = (PINT 2)
$pfshape(expression_add) = PFBINARY ADD expression_left expression_right
$pfshape(expression_sub) = PFBINARY SUBTRACT expression_add expression_one
$binary_apply(S_capture,ADD,PINT 1,PINT 2,12) = S_capture[.RESULT = KNOWN (PINT 3)]
$binary_apply(S_capture,SUBTRACT,PINT 3,PINT 1,12) = S_capture[.RESULT = KNOWN (PINT 2)]
$unary_apply(S_capture,NEGATIVE,PINT 2,12) = S_capture[.RESULT = KNOWN (PINT i_unary)]
$string_read_raw_unary_integer(S_capture,porigin_left,1)
$string_read_raw_unary_integer(S_capture,porigin_right,2)
$string_read_raw_unary_integer(S_capture,porigin_one,1)
$string_read_raw_unary_integer(S_capture,porigin_add,3)
$string_read_raw_unary_integer(S_capture,porigin_sub,2)
$string_read_raw_unary_integer(S_capture,porigin_unary,i_unary)
$string_read_raw_known_base(S_capture,porigin_base,pkeyread.BASE)

$origin_child((porigin_base),[PCFIELD 1]) = (porigin_absent)
$origin_node(S_capture.SOURCES,porigin_absent) = eps
$compiled_read(S_capture,porigin_absent) = eps
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_false)
$origin_node(S_capture.SOURCES,porigin_false) = (NScalarString (BYTES text_false) metadata_false)
$compiled_read(S_capture,porigin_false) = (PSTRING ($ptascii("abc")))
$compiled_string_value(S_capture,porigin_false,PSTRING ($ptascii("abc"))) = pkeyread.BASE
$base_nodes(pkeyread.OWNERS) = eps
$task_nodes(STRING_READ_RESULT pstringread) = eps
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
    checks += lines(r"""
porigin_base = PORIGIN n_unit pcpath_base
porigin_unary = PORIGIN n_unit pcpath_unary
porigin_sub = PORIGIN n_unit pcpath_sub
porigin_add = PORIGIN n_unit pcpath_add
porigin_left = PORIGIN n_unit pcpath_left
porigin_right = PORIGIN n_unit pcpath_right
porigin_one = PORIGIN n_unit pcpath_one
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
S_capture.CODE = [pcode]
pcunit.ID = n_unit /\ ppool.UNIT = n_unit /\ pcode.UNIT = n_unit
~$string_read_raw_unary_integer(S_capture,porigin_unary,2)
~$string_read_raw_unary_integer(S_capture,porigin_sub,3)
~$string_read_raw_unary_integer(S_capture,porigin_add,2)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ")))
""")
    for label, path in (('unary','pcpath_unary'), ('sub','pcpath_sub'),
                        ('add','pcpath_add'), ('left','pcpath_left'),
                        ('right','pcpath_right'), ('one','pcpath_one')):
        for index, value in enumerate(('PINT 7','PFLOAT 0','PINT 9223372036854775808')):
            state = f'S_bad_{label}_{index}'
            checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT {path} ({value})) :: ppool.CONSTANTS]]]',
                       f'~$string_read_raw_unary_integer({state},porigin_unary,i_unary)',
                       f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)',
                       f'$string_read_plan({state}) = eps',
                       f'$string_read_raw_saved({state},pstringread) = eps',
                       f'~$string_read_source({state},pstringread)']
        checks += [f'S_code_{label} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR {path} 12 false) :: pcode.EXPRESSIONS]]]',
                   f'~$string_read_raw_unary_integer(S_code_{label},porigin_unary,i_unary)',
                   f'~$string_read_raw_known_base(S_code_{label},porigin_base,pkeyread.BASE)']
        checks += [f'S_detached_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE {path} (NScalarInt (INTEGER 7) metadata_left)) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_detached_{label},porigin_base,pkeyread.BASE)',
                   f'$string_read_plan(S_detached_{label}) = eps']
    # These local trees are coherent derived controls, with actual source children
    # and matching CODE/pools, but carry no additional source execution credit.
    for label, constructor, operator, left, right, result, accepted in (
            ('add_zero','Plus','ADD',0,2,2,True),
            ('sub_zero','Minus','SUBTRACT',2,2,0,True),
            ('multiply','Mul','MULTIPLY',1,2,2,True),
            ('divide','Div','DIVIDE',2,1,2,True),
            ('modulo','Mod','MODULO',3,2,1,False),
            ('shift','ShiftLeft','SHIFTLEFT',1,1,2,False),
            ('power','Pow','POWER',2,1,2,False),
            ('add_overflow','Plus','ADD',9223372036854775807,1,2,False),
            ('mul_overflow','Mul','MULTIPLY',9223372036854775807,2,2,False)):
        state = f'S_tree_{label}'
        checks += lines(f"""
expression_tree_{label}_left = NScalarInt (INTEGER {left}) metadata_left
expression_tree_{label}_right = NScalarInt (INTEGER {right}) metadata_right
expression_tree_{label} = NExprBinaryOp{constructor} expression_tree_{label}_left expression_tree_{label}_right metadata_sub
{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_sub expression_tree_{label}) :: (PCOCCURRENCE (pcpath_sub ++ [PCFIELD 0]) expression_tree_{label}_left) :: (PCOCCURRENCE (pcpath_sub ++ [PCFIELD 1]) expression_tree_{label}_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_sub (PINT {result})) :: (PCONSTANT (pcpath_sub ++ [PCFIELD 0]) (PINT {left})) :: (PCONSTANT (pcpath_sub ++ [PCFIELD 1]) (PINT {right})) :: ppool.CONSTANTS]]]
$compiled_read({state},porigin_sub) = (PINT {result})
$pfshape(expression_tree_{label}) = PFBINARY {operator} expression_tree_{label}_left expression_tree_{label}_right
$string_read_raw_unary_integer({state},porigin_sub,{result}) = {'true' if accepted else 'false'}
""")
        if accepted:
            checks += [f'$binary_apply({state},{operator},PINT {left},PINT {right},12) = {state}[.RESULT = KNOWN (PINT {result})]']
    checks += lines(r"""
S_bad_condition = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 0]) (PBOOL true)) :: ppool.CONSTANTS]]]
S_bad_selected = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT (pcpath_base ++ [PCFIELD 2]) (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]]
S_bad_parent = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base (PSTRING ($ptascii("abc")))) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 12 true) :: pcode.EXPRESSIONS]]]
""")
    for state in ('S_bad_condition','S_bad_selected','S_bad_parent'):
        checks += [f'~$string_read_raw_known_base({state},porigin_base,pkeyread.BASE)',
                   f'$string_read_raw_saved({state},pstringread) = eps',
                   f'~$string_read_source({state},pstringread)']
    for field in ('SOURCES','CODE','POOLS'):
        checks += [f'~$string_read_raw_known_base(S_capture[.{field} = eps],porigin_base,pkeyread.BASE)',
                   f'$string_read_plan(S_capture[.{field} = eps]) = eps',
                   f'~$string_read_source(S[.{field} = eps],pstringread)']
    checks += lines(r"""
~$string_read_source(S[.ORIGIN = eps],pstringread)
~$string_read_source(S,pstringread[.READ.LINE = 13])
~$string_read_source(S,pstringread[.BASECELL = (n_key)])
~$string_read_source(S,pstringread[.KEYCELL = eps])
~$string_read_source(S,pstringread[.PHASE = STRING_CAST])
""")
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (c if c.startswith('PhpStep:') else 'if ' + c) + '\n' for c in checks),
        len(checks), len(checks) - derived_start)
