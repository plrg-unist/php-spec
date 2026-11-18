"""Independent numeric-STRING FLOAT casts, byte authority and saved-key review."""

from string_offset_retained_carrier_protocol import PREFIX, lines, seek
from string_offset_runtime_allocated_float_ternary_tree_rhs_concat_base_initial_raw_leading_key_peer_review import capture


def render(program, filename_b64, control_program, control_filename_b64):
    old = 'def $retained_frontier(S, 0) = ($string_read_plan(S) =/= eps)'
    assert PREFIX.count(old) == 1
    prefix = PREFIX.replace(old, '''def $retained_frontier(S, 0) = true
  -- if S.TODO = (KEY_READ_DIM poperand z KEY_R) :: ptask_tail*
  -- if poperand = VARIABLE ($ptascii("key")) z
  -- if S.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING 5) ($ptascii("-10.5bcde-12.5")))''')
    checks = capture(program, filename_b64) + lines(r'''
expression_number = NExprCastDouble expression_input metadata_number
expression_input = NScalarString (BYTES "IC0xMi41MCA=") metadata_input
$origin_child((porigin_number),[PCFIELD 0]) = (porigin_input)
$origin_node(S_capture.SOURCES,porigin_input) = (expression_input)
porigin_number = PORIGIN n_unit pcpath_number
porigin_input = PORIGIN n_unit pcpath_input
$code_expression(pcode.EXPRESSIONS,pcpath_number) = ((z_number,false))
$(z_number > 0)
$compiled_read(S_capture,porigin_number) = eps
$compiled_precision(S_capture,(porigin_base)) = (14)
$compiled_precision(S_capture,(porigin_left)) = (14)
$compiled_precision(S_capture,(porigin_right)) = (14)
$compiled_precision(S_capture,(porigin_number)) = (14)
$compiled_precision(S_capture,(porigin_input)) = (14)
$compiled_read(S_capture,porigin_input) = (PSTRING ($ptascii(" -12.50 ")))
$string_read_runtime_value(S_capture,porigin_input) = (PSTRING_CARRIER INTERNED_STRING ($ptascii(" -12.50 ")))
$string_read_runtime_cast_quiet(CASTFLOAT,PSTRING_CARRIER INTERNED_STRING ($ptascii(" -12.50 ")))
$cast_apply(S_capture,CASTFLOAT,PSTRING_CARRIER INTERNED_STRING ($ptascii(" -12.50 ")),z_number) = S_capture[.RESULT = KNOWN (PFLOAT 13846598529327300608)]
$string_read_runtime_value(S_capture,porigin_number) = (PFLOAT 13846598529327300608)
$truth_value(S_capture,PFLOAT 13846598529327300608,z_number) = S_capture[.RESULT = KNOWN (PBOOL true)]
$string_read_raw_float_sign_tree(expression_number)
~$string_read_raw_float_sign_tree(expression_input)
$string_read_allocated_value(S_capture,porigin_base,pvalue_base)
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL eps,KEYCELL (n_key),KEYREF true,PHASE STRING_LEADING 9}
pkeyread.BASE = pvalue_base /\ pkeyread.INPUT = poperand
pkeyread.VALUE = PSTRING ($ptascii("9x")) /\ pkeyread.LINE = 18
pkeyread.SITE = porigin_site /\ pkeyread.PHASE = KEY_NULL
pkeyread.OWNERS = BASE_VALUE (KNOWN pvalue_base)
$lookup(S_capture.ENV,$ptascii("key")) = (n_key)
$lookup(S_capture.ENV,$ptascii("alias")) = (n_key)
S_capture.REFCELLS = [n_key]
$string_read_raw_capture(S_capture,poperand,pvalue_base) = ((pkeyread.VALUE,pstringread.KEYCELL))
$string_read_raw_saved(S_capture,pstringread) = (9)
$string_read_source(S_capture,pstringread)
PhpStep: S_capture ~> S_dispatch
S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_dispatch*
perrorcall.RESUME = STRING_READ_RESULT pstringread
perrorcall.LEVEL = 2 /\ perrorcall.LINE = 18
S_dispatch.STRINGDATA = S_capture.STRINGDATA
S_dispatch.STORE = S_capture.STORE
$heap_graph(S_dispatch) = $heap_graph(S_capture)
''') + seek('S_dispatch', 2, 'S') + lines(r'''
S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*
S.CURRENT = eps /\ S.FRAMES = eps /\ S.COMPLETION = NORMAL
S.STRINGDATA = S_capture.STRINGDATA
S.STORE[n_key] = DEFINED (PSTRING perrorcall.MESSAGE)
$lookup(S.ENV,$ptascii("alias")) = (n_key)
$lookup(S.ENV,$ptascii("key")) = (n_current)
n_current =/= n_key
S.STORE[n_current] = DEFINED (PINT 13)
$heap_owners($heap_graph(S),HCELL n_key) = 1
$heap_owners($heap_graph(S),HCELL n_current) = 1
$string_read_raw_saved(S,pstringread) = (9)
$string_read_key_current(S,pstringread) = eps
$string_read_ready(S,pstringread)
S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([45]))][.BASE = BASE_VALUE (KNOWN PNULL)]
$string_read_resume(S,pstringread) = S_expected
PhpStep: S ~> S_step
S_step = S_expected
$heap_graph(S_step) = $heap_graph(S)
$drive_steps(S,0) = S[.COMPLETION = BUDGET]
$drive_steps(S,1) = S_expected[.COMPLETION = BUDGET]
S_done = $drive_steps(S_step,2000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0
S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("512:9x;2:Illegal string offset \"9x\";R:-;K:13;A:Illegal string offset \"9x\";Z;")
''')
    derived_start = len(checks)
    for node in ('number', 'input'):
        checks += [f'S_precision_{node} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_precision_{node},porigin_number) = eps',
                   f'~$string_read_allocated_value(S_precision_{node},porigin_base,pvalue_base)',
                   f'$string_read_plan(S_precision_{node}) = eps']
        checks += [f'S_source_{node} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{node} (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]]',
                   f'$string_read_runtime_value(S_source_{node},porigin_number) = eps',
                   f'~$string_read_allocated_value(S_source_{node},porigin_base,pvalue_base)']
    for node in ('number', 'right'):
        checks += [f'S_code_{node} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} 0 true) :: pcode.EXPRESSIONS]]]',
                   f'~$string_read_allocated_value(S_code_{node},porigin_base,pvalue_base)',
                   f'$string_read_plan(S_code_{node}) = eps']
    checks += lines(r'''
S_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_input (PSTRING ($ptascii("-12.5")))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_pool,porigin_input) = eps
$string_read_runtime_value(S_pool,porigin_number) = eps
~$string_read_allocated_value(S_pool,porigin_base,pvalue_base)
$string_read_plan(S_pool) = eps
S_clone = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("-10.5bcde-12.5")]]
pvalue_clone = PSTRING_CARRIER (REQUEST_STRING 6) ($ptascii("-10.5bcde-12.5"))
$string_carrier_valid(S_clone,pvalue_clone)
~$string_read_allocated_value(S_clone,porigin_base,pvalue_clone)
$string_read_raw_capture(S_clone,poperand,pvalue_base) = eps
$string_read_plan(S_clone) = eps
S_later = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("callback"),$ptascii("-10.5bcde-12.5")]]
$string_read_raw_saved(S_later,pstringread) = (9)
$string_read_ready(S_later,pstringread)
$string_read_resume(S_later,pstringread) = S_later[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([45]))][.BASE = BASE_VALUE (KNOWN PNULL)]
S_live17 = S_capture[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]
~$string_read_allocated_value(S_live17,porigin_base,pvalue_base)
S_row = S_capture[.STRINGDATA[4] = $ptascii("-12.50")]
~$string_read_allocated_value(S_row,porigin_base,pvalue_base)
S_left = S_capture[.STRINGDATA[2] = $ptascii("-10.5zz")]
~$string_read_allocated_value(S_left,porigin_base,pvalue_base)
S_abrupt = S_capture[.COMPLETION = UNSUPPORTED "peer-control"]
~$string_read_allocated_value(S_abrupt,porigin_base,pvalue_base)
S_const = S_capture[.CONSTCONTEXT = ({ORIGIN porigin_base,LINE 18,FACTS eps})]
~$string_read_allocated_value(S_const,porigin_base,pvalue_base)

$string_read_raw_float_sign_tree(NExprCastDouble expression_input eps)
$string_read_raw_float_sign_tree(NExprUnaryMinus (NExprCastDouble expression_input eps) eps)
~$string_read_raw_float_sign_tree(NExprCastInt expression_input eps)
~$string_read_raw_float_sign_tree(NExprCastDouble (NScalarInt (INTEGER 25) eps) eps)
~$string_read_raw_float_sign_tree(NExprCastDouble (NExprVariable (BYTES "a2V5") eps) eps)
$string_read_raw_float_sign_tree(NExprCastDouble (NScalarString (BYTES "LTAuMA==") eps) eps)
~$string_read_raw_float_sign_tree(NExprCastDouble (NScalarString (BYTES "LTEyLjVqdW5r") eps) eps)
~$string_read_raw_float_sign_tree(NExprCastDouble (NScalarString (BYTES "LTEyLjUA") eps) eps)
~$string_read_raw_float_sign_tree(NExprCastDouble (NScalarString (BYTES "") eps) eps)
~$string_read_raw_float_sign_tree(NExprCastDouble (NScalarString (BYTES "TkFO") eps) eps)
''')
    control = capture(control_program, control_filename_b64) + lines(r'''
expression_number = NExprBinaryOpDiv expression_cast expression_divisor metadata_number
expression_cast = NExprCastDouble expression_int metadata_cast
expression_int = NExprUnaryMinus expression_positive metadata_int
expression_positive = NScalarInt (INTEGER 25) metadata_positive
expression_divisor = NScalarFloat (FLOAT "4000000000000000") metadata_divisor
$origin_child((porigin_number),[PCFIELD 0]) = (porigin_cast)
$origin_child((porigin_number),[PCFIELD 1]) = (porigin_divisor)
$origin_child((porigin_cast),[PCFIELD 0]) = (porigin_int)
$origin_child((porigin_int),[PCFIELD 0]) = (porigin_positive)
$origin_node(S_capture.SOURCES,porigin_cast) = (expression_cast)
$origin_node(S_capture.SOURCES,porigin_divisor) = (expression_divisor)
$origin_node(S_capture.SOURCES,porigin_int) = (expression_int)
$origin_node(S_capture.SOURCES,porigin_positive) = (expression_positive)
porigin_number = PORIGIN n_unit pcpath_number
porigin_cast = PORIGIN n_unit pcpath_cast
$code_expression(pcode.EXPRESSIONS,pcpath_number) = ((z_number,false))
$code_expression(pcode.EXPRESSIONS,pcpath_cast) = ((z_cast,false))
$(z_number > 0 /\ z_cast > 0)
$compiled_read(S_capture,porigin_number) = eps
$compiled_read(S_capture,porigin_cast) = eps
$compiled_precision(S_capture,(porigin_number)) = (14)
$compiled_precision(S_capture,(porigin_cast)) = (14)
$compiled_precision(S_capture,(porigin_divisor)) = (14)
$compiled_read(S_capture,porigin_int) = (PINT (-25))
$string_read_runtime_value(S_capture,porigin_int) = (PINT (-25))
$cast_apply(S_capture,CASTFLOAT,PINT (-25),z_cast) = S_capture[.RESULT = KNOWN (PFLOAT 13851102128954671104)]
$string_read_runtime_value(S_capture,porigin_cast) = (PFLOAT 13851102128954671104)
$string_read_runtime_value(S_capture,porigin_divisor) = (PFLOAT 4611686018427387904)
$binary_apply(S_capture,DIVIDE,PFLOAT 13851102128954671104,PFLOAT 4611686018427387904,z_number) = S_capture[.RESULT = KNOWN (PFLOAT 13846598529327300608)]
$string_read_runtime_value(S_capture,porigin_number) = (PFLOAT 13846598529327300608)
$truth_value(S_capture,PFLOAT 13846598529327300608,z_number) = S_capture[.RESULT = KNOWN (PBOOL true)]
~$string_read_raw_float_sign_tree(expression_cast)
~$string_read_raw_float_sign_tree(expression_number)
~$string_read_allocated_value(S_capture,porigin_base,pvalue_base)
~$string_read_allocated_base(S_capture,porigin_base,pvalue_base)
$string_read_raw_capture(S_capture,poperand,pvalue_base) = eps
$string_read_plan(S_capture) = eps
''')
    helper = '\ndec $peer_int_float_div_control() : bool\ndef $peer_int_float_div_control() = true\n' + ''.join('  -- if ' + c + '\n' for c in control)
    result = prefix + helper + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + (c if c.startswith('PhpStep:') else 'if ' + c) + '\n' for c in checks)
    return result + '  -- if $peer_int_float_div_control()\n', len(checks) + len(control) + 1, len(checks) - derived_start + len(control) + 1
