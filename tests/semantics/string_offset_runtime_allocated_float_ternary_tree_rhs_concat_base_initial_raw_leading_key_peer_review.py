"""Independent FLOAT ternary VALUE, skipped effects and allocated-row review."""

import json

from string_offset_retained_carrier_protocol import PREFIX, lines, seek


def capture(program, filename_b64):
    return ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
            'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture') + lines(r'''
S_capture.TODO = (KEY_READ_DIM poperand 18 KEY_R) :: ptask_capture*
poperand = VARIABLE ($ptascii("key")) 18
pvalue_left = PSTRING_CARRIER (REQUEST_STRING 3) ($ptascii("-10.5bcde"))
pvalue_right = PSTRING_CARRIER (REQUEST_STRING 4) ($ptascii("-12.5"))
pvalue_base = PSTRING_CARRIER (REQUEST_STRING 5) ($ptascii("-10.5bcde-12.5"))
S_capture.RESULT = KNOWN pvalue_base
S_capture.STRINGDATA = [$ptascii("512"),$ptascii("-10.5"),$ptascii("-10.5bc"),$ptascii("-10.5bcde"),$ptascii("-12.5"),$ptascii("-10.5bcde-12.5")]
S_capture.ORIGIN = (porigin_site)
$origin_child((porigin_site),[PCFIELD 0]) = (porigin_base)
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpConcat expression_left expression_right metadata_base)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_right)
expression_right = NExprCastString expression_number metadata_right
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_number)
$origin_node(S_capture.SOURCES,porigin_number) = (expression_number)
S_capture.SOURCES = [pcunit]
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
porigin_right = PORIGIN n_unit pcpath_right
$code_expression(pcode.EXPRESSIONS,pcpath_right) = ((z_right,false))
$string_read_allocated_base(S_capture,porigin_left,pvalue_left)
$string_read_allocated_value(S_capture,porigin_right,pvalue_right)
$concat_constant(S_capture,(porigin_left)) = false
$concat_constant(S_capture,(porigin_right)) = false
S_prefix = S_capture[.STRINGDATA = S_capture.STRINGDATA[0:4]]
S_cast = $cast_apply(S_prefix,CASTSTRING,PFLOAT 13846598529327300608,z_right)
S_cast = S_prefix[.STRINGDATA = S_prefix.STRINGDATA ++ [$ptascii("-12.5")]][.RESULT = KNOWN pvalue_right]
$string_concat(S_cast,pvalue_left,pvalue_right,false,false) = S_cast[.STRINGDATA = S_cast.STRINGDATA ++ [$ptascii("-10.5bcde-12.5")]][.RESULT = KNOWN pvalue_base]
''')


def render(program, filename_b64, control_program, control_filename_b64):
    old = 'def $retained_frontier(S, 0) = ($string_read_plan(S) =/= eps)'
    assert PREFIX.count(old) == 1
    prefix = PREFIX.replace(old, '''def $retained_frontier(S, 0) = true
  -- if S.TODO = (KEY_READ_DIM poperand z KEY_R) :: ptask_tail*
  -- if poperand = VARIABLE ($ptascii("key")) z
  -- if S.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING 5) ($ptascii("-10.5bcde-12.5")))''')
    checks = capture(program, filename_b64) + lines(r'''
expression_number = NExprBinaryOpDiv expression_numerator expression_denominator metadata_number
expression_numerator = NExprBinaryOpPlus expression_difference expression_zero_sum metadata_numerator
expression_difference = NExprBinaryOpMinus expression_ternary expression_product metadata_difference
expression_ternary = NExprTernary expression_condition expression_selected expression_skipped metadata_ternary
expression_condition = NExprCastDouble expression_one metadata_condition
expression_one = NScalarFloat (FLOAT "3ff0000000000000") metadata_one
expression_selected = NExprCastDouble expression_negative metadata_selected
expression_negative = NExprUnaryMinus expression_atom metadata_negative
expression_atom = NScalarFloat (FLOAT "4039000000000000") metadata_atom
expression_skipped = NExprCastDouble expression_bad_div metadata_skipped
expression_bad_div = NExprBinaryOpDiv expression_bad_one expression_bad_zero metadata_bad_div
expression_bad_one = NScalarFloat (FLOAT "3ff0000000000000") metadata_bad_one
expression_bad_zero = NScalarFloat (FLOAT "0000000000000000") metadata_bad_zero
expression_product = NExprBinaryOpMul expression_zero_product expression_two metadata_product
expression_zero_product = NScalarFloat (FLOAT "0000000000000000") metadata_zero_product
expression_two = NScalarFloat (FLOAT "4000000000000000") metadata_two
expression_zero_sum = NScalarFloat (FLOAT "0000000000000000") metadata_zero_sum
expression_denominator = NExprCastDouble expression_denominator_sum metadata_denominator
expression_denominator_sum = NExprBinaryOpPlus expression_one_left expression_one_right metadata_denominator_sum
expression_one_left = NScalarFloat (FLOAT "3ff0000000000000") metadata_one_left
expression_one_right = NScalarFloat (FLOAT "3ff0000000000000") metadata_one_right
''')
    children = [('number', 0, 'numerator'), ('number', 1, 'denominator'),
                ('numerator', 0, 'difference'), ('numerator', 1, 'zero_sum'),
                ('difference', 0, 'ternary'), ('difference', 1, 'product'),
                ('ternary', 0, 'condition'), ('ternary', 1, 'selected'), ('ternary', 2, 'skipped'),
                ('condition', 0, 'one'), ('selected', 0, 'negative'), ('negative', 0, 'atom'),
                ('skipped', 0, 'bad_div'), ('bad_div', 0, 'bad_one'), ('bad_div', 1, 'bad_zero'),
                ('product', 0, 'zero_product'), ('product', 1, 'two'),
                ('denominator', 0, 'denominator_sum'),
                ('denominator_sum', 0, 'one_left'), ('denominator_sum', 1, 'one_right')]
    for parent, field, child in children:
        checks += [f'$origin_child((porigin_{parent}),[PCFIELD {field}]) = (porigin_{child})',
                   f'$origin_node(S_capture.SOURCES,porigin_{child}) = (expression_{child})']
    demanded = ('base', 'left', 'right', 'number', 'numerator', 'difference', 'ternary',
                'condition', 'selected', 'denominator', 'denominator_sum', 'product', 'zero_sum')
    for node in demanded:
        checks += [f'porigin_{node} = PORIGIN n_unit pcpath_{node}',
                   f'$compiled_precision(S_capture,(porigin_{node})) = (14)']
    for node in demanded[:-3]:
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{node}) = ((z_{node},false))',
                   f'$(z_{node} > 0)', f'$compiled_read(S_capture,porigin_{node}) = eps']
    checks += lines(r'''
porigin_negative = PORIGIN n_unit pcpath_negative
porigin_atom = PORIGIN n_unit pcpath_atom
porigin_skipped = PORIGIN n_unit pcpath_skipped
porigin_bad_div = PORIGIN n_unit pcpath_bad_div
porigin_one = PORIGIN n_unit pcpath_one
$string_read_runtime_value(S_capture,porigin_condition) = (PFLOAT 4607182418800017408)
$truth_value(S_capture,PFLOAT 4607182418800017408,z_ternary) = S_capture[.RESULT = KNOWN (PBOOL true)]
$string_read_runtime_value(S_capture,porigin_selected) = (PFLOAT 13851102128954671104)
$string_read_runtime_value(S_capture,porigin_ternary) = (PFLOAT 13851102128954671104)
$string_read_runtime_value(S_capture,porigin_number) = (PFLOAT 13846598529327300608)
$string_read_runtime_value(S_capture,porigin_skipped) = eps
$string_read_runtime_value(S_capture,porigin_bad_div) = eps
$string_read_raw_float_sign_tree(expression_number)
$string_read_raw_float_sign_tree(expression_ternary)
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
    for node in ('ternary', 'condition', 'selected'):
        checks += [f'S_precision_{node} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_precision_{node},porigin_ternary) = eps',
                   f'~$string_read_allocated_value(S_precision_{node},porigin_base,pvalue_base)',
                   f'$string_read_plan(S_precision_{node}) = eps']
    for node in ('ternary', 'condition', 'selected', 'skipped'):
        checks += [f'S_source_{node} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{node} (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]]',
                   f'$string_read_runtime_value(S_source_{node},porigin_ternary) = eps',
                   f'~$string_read_allocated_value(S_source_{node},porigin_base,pvalue_base)']
    checks += lines(r'''
S_skip = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_skipped 17) :: (PCCPRECISION pcpath_bad_div 17) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_skipped 0 true) :: (CODEEXPR pcpath_bad_div 0 true) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_skip,porigin_ternary) = (PFLOAT 13851102128954671104)
$string_read_allocated_value(S_skip,porigin_base,pvalue_base)
$string_read_plan(S_skip) = (pstringread)
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
$string_read_raw_float_sign_tree(NExprTernary expression_atom expression_atom expression_atom eps)
~$string_read_raw_float_sign_tree(NExprTernary expression_atom ABSENT expression_atom eps)
~$string_read_raw_float_sign_tree(NExprTernary (NScalarInt (INTEGER 1) eps) expression_atom expression_atom eps)
~$string_read_raw_float_sign_tree(NExprTernary expression_atom (NScalarInt (INTEGER 1) eps) expression_atom eps)
~$string_read_raw_float_sign_tree(NExprTernary expression_atom expression_atom (NScalarString (BYTES "MQ==") eps) eps)
''')
    control = capture(control_program, control_filename_b64) + lines(r'''
expression_number = NExprTernary expression_condition ABSENT expression_skipped metadata_number
expression_condition = NExprCastDouble (NExprUnaryMinus (NScalarFloat (FLOAT "4029000000000000") metadata_atom_condition) metadata_negative_condition) metadata_condition
expression_skipped = NExprCastDouble (NExprUnaryMinus (NScalarFloat (FLOAT "4029000000000000") metadata_atom_skipped) metadata_negative_skipped) metadata_skipped
$origin_child((porigin_number),[PCFIELD 0]) = (porigin_condition)
$origin_child((porigin_number),[PCFIELD 2]) = (porigin_skipped)
$origin_node(S_capture.SOURCES,porigin_condition) = (expression_condition)
$origin_node(S_capture.SOURCES,porigin_skipped) = (expression_skipped)
$string_read_runtime_value(S_capture,porigin_condition) = (PFLOAT 13846598529327300608)
$truth_value(S_capture,PFLOAT 13846598529327300608,18) = S_capture[.RESULT = KNOWN (PBOOL true)]
$string_read_runtime_value(S_capture,porigin_number) = (PFLOAT 13846598529327300608)
~$string_read_raw_float_sign_tree(expression_number)
~$string_read_allocated_value(S_capture,porigin_base,pvalue_base)
~$string_read_allocated_base(S_capture,porigin_base,pvalue_base)
$string_read_raw_capture(S_capture,poperand,pvalue_base) = eps
$string_read_plan(S_capture) = eps
''')
    helper = '\ndec $peer_float_shorthand_control() : bool\ndef $peer_float_shorthand_control() = true\n' + ''.join('  -- if ' + c + '\n' for c in control)
    body = prefix + helper + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + (c if c.startswith('PhpStep:') else 'if ' + c) + '\n' for c in checks)
    return body + '  -- if $peer_float_shorthand_control()\n', len(checks) + len(control) + 1, len(checks) - derived_start + len(control) + 1
