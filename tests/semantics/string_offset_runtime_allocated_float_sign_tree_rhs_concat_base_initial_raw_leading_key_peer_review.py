"""Independent FLOAT sign-tree source, allocation and saved-key review."""

import json

from string_offset_retained_carrier_protocol import PREFIX, lines, seek


def render(program, filename_b64, control_program, control_filename_b64):
    old = 'def $retained_frontier(S, 0) = ($string_read_plan(S) =/= eps)'
    assert PREFIX.count(old) == 1
    prefix = PREFIX.replace(old, '''def $retained_frontier(S, 0) = true
  -- if S.TODO = (KEY_READ_DIM poperand z KEY_R) :: ptask_tail*
  -- if poperand = VARIABLE ($ptascii("key")) z
  -- if S.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING 5) ($ptascii("-10.5bcde-12.5")))''')
    checks = ['S_initial = $php_run(' + program + ',0,' + json.dumps(filename_b64) + ')',
              'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture')
    checks += lines(r'''
S_capture.TODO = (KEY_READ_DIM poperand 18 KEY_R) :: ptask_capture*
poperand = VARIABLE ($ptascii("key")) 18
pvalue_base = PSTRING_CARRIER (REQUEST_STRING 5) ($ptascii("-10.5bcde-12.5"))
pvalue_left = PSTRING_CARRIER (REQUEST_STRING 3) ($ptascii("-10.5bcde"))
pvalue_right = PSTRING_CARRIER (REQUEST_STRING 4) ($ptascii("-12.5"))
S_capture.RESULT = KNOWN pvalue_base
S_capture.STRINGDATA = [$ptascii("512"),$ptascii("-10.5"),$ptascii("-10.5bc"),$ptascii("-10.5bcde"),$ptascii("-12.5"),$ptascii("-10.5bcde-12.5")]
S_capture.ORIGIN = (porigin_site)
$origin_child((porigin_site),[PCFIELD 0]) = (porigin_base)
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpConcat expression_left expression_right metadata_base)
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_right)
expression_left = NExprBinaryOpCoalesce expression_selected expression_skipped metadata_left
expression_right = NExprCastString expression_number metadata_right
expression_number = NExprUnaryMinus expression_sign1 metadata_number
expression_sign1 = NExprUnaryMinus expression_sign2 metadata_sign1
expression_sign2 = NExprUnaryPlus expression_sign3 metadata_sign2
expression_sign3 = NExprUnaryMinus expression_atom metadata_sign3
expression_atom = NScalarFloat (FLOAT "4029000000000000") metadata_atom
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_number)
$origin_node(S_capture.SOURCES,porigin_number) = (expression_number)
$origin_child((porigin_number),[PCFIELD 0]) = (porigin_sign1)
$origin_child((porigin_sign1),[PCFIELD 0]) = (porigin_sign2)
$origin_child((porigin_sign2),[PCFIELD 0]) = (porigin_sign3)
$origin_child((porigin_sign3),[PCFIELD 0]) = (porigin_atom)
$origin_node(S_capture.SOURCES,porigin_sign1) = (expression_sign1)
$origin_node(S_capture.SOURCES,porigin_sign2) = (expression_sign2)
$origin_node(S_capture.SOURCES,porigin_sign3) = (expression_sign3)
$string_read_runtime_value(S_capture,porigin_sign1) = (PFLOAT 4623226492472524800)
$string_read_runtime_value(S_capture,porigin_sign2) = (PFLOAT 13846598529327300608)
$string_read_runtime_value(S_capture,porigin_sign3) = (PFLOAT 13846598529327300608)
$origin_node(S_capture.SOURCES,porigin_atom) = (expression_atom)
porigin_atom = PORIGIN n_unit pcpath_atom
$compiled_read(S_capture,porigin_number) = (PFLOAT 13846598529327300608)
$compiled_special_concat_bytes(S_capture,porigin_number) = ($ptascii("-12.5"))
$parser_literal_at(expression_number,14) = eps
$parser_literal_at(expression_atom,14) = (PFLOAT 4623226492472524800)
$unary_apply(S_capture,NEGATIVE,PFLOAT 4623226492472524800,0) = S_capture[.RESULT = KNOWN (PFLOAT 13846598529327300608)]
S_capture.SOURCES = [pcunit]
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
$string_carrier_valid(S_capture,pvalue_base)
$string_carrier_valid(S_capture,pvalue_left)
$string_carrier_valid(S_capture,pvalue_right)
$string_read_allocated_base(S_capture,porigin_left,pvalue_left)
~$string_read_allocated_value(S_capture,porigin_left,pvalue_left)
$string_read_allocated_value(S_capture,porigin_right,pvalue_right)
$string_read_runtime_value(S_capture,porigin_number) = (PFLOAT 13846598529327300608)
$string_read_runtime_value(S_capture,porigin_right) = eps
$string_read_runtime_value(S_capture,porigin_base) = eps
$concat_constant(S_capture,(porigin_left)) = false
$concat_constant(S_capture,(porigin_right)) = false
''')
    for node in ('base', 'left', 'right', 'number', 'sign1', 'sign2', 'sign3'):
        checks += [f'porigin_{node} = PORIGIN n_unit pcpath_{node}',
                   f'$compiled_precision(S_capture,(porigin_{node})) = (14)']
    for node in ('base', 'left', 'right'):
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{node}) = ((z_{node},false))',
                   f'$(z_{node} > 0)', f'$compiled_read(S_capture,porigin_{node}) = eps']
    checks += lines(r'''
S_prefix = S_capture[.STRINGDATA = S_capture.STRINGDATA[0:4]]
S_cast = $cast_apply(S_prefix,CASTSTRING,PFLOAT 13846598529327300608,z_right)
S_cast = S_prefix[.STRINGDATA = S_prefix.STRINGDATA ++ [$ptascii("-12.5")]][.RESULT = KNOWN pvalue_right]
$string_concat(S_cast,pvalue_left,pvalue_right,false,false) = S_cast[.STRINGDATA = S_cast.STRINGDATA ++ [$ptascii("-10.5bcde-12.5")]][.RESULT = KNOWN pvalue_base]
$string_read_allocated_value(S_capture,porigin_base,pvalue_base)
$string_read_plan(S_capture) = (pstringread)
pstringread = {READ pkeyread,BASECELL eps,KEYCELL (n_key),KEYREF true,PHASE STRING_LEADING 9}
pkeyread.BASE = pvalue_base /\ pkeyread.INPUT = poperand
pkeyread.VALUE = PSTRING ($ptascii("9x")) /\ pkeyread.LINE = 18
pkeyread.SITE = porigin_site /\ pkeyread.PHASE = KEY_NULL
pkeyread.OWNERS = BASE_VALUE (KNOWN pvalue_base)
$lookup(S_capture.ENV,$ptascii("key")) = (n_key)
$lookup(S_capture.ENV,$ptascii("alias")) = (n_key)
$lookup(S_capture.ENV,$ptascii("got")) = (n_got)
S_capture.REFCELLS = [n_key]
S_capture.STORE[n_key] = DEFINED (PSTRING ($ptascii("9x")))
S_capture.STORE[n_got] = DEFINED (PINT 99)
$string_read_raw_capture(S_capture,poperand,pvalue_base) = ((pkeyread.VALUE,pstringread.KEYCELL))
$string_read_raw_saved(S_capture,pstringread) = (9)
$string_read_source(S_capture,pstringread)
$string_read_provider_ready(S_capture,pstringread)
$task_nodes(STRING_READ_RESULT pstringread) = eps
$base_nodes(pkeyread.OWNERS) = eps
$heap_valid($heap_graph(S_capture))
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
S.STORE[n_got] = DEFINED (PINT 99)
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
pvalue_byte = PSTRING_CARRIER INTERNED_STRING ([45])
$string_byte_read(S,$ptascii("-10.5bcde-12.5"),13,18) = S[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([53]))]
S_expected = S[.TODO = ptask_tail*][.RESULT = KNOWN pvalue_byte][.BASE = BASE_VALUE (KNOWN PNULL)]
$string_read_resume(S,pstringread) = S_expected
PhpStep: S ~> S_step
S_step = S_expected
$heap_graph(S_step) = $heap_graph(S)
$drive_steps(S,0) = S[.COMPLETION = BUDGET]
$drive_steps(S,1) = S_expected[.COMPLETION = BUDGET]
$drive_steps(S,2) = $drive_steps(S_expected,1)
S_done = $drive_steps(S_step,2000)
S_done.COMPLETION = NORMAL /\ S_done.EXITSTATUS = 0
S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps
$retained_outputs_only(S_done.EVENTS)
$retained_outputs(S_done.EVENTS) = $ptascii("512:9x;2:Illegal string offset \"9x\";R:-;K:13;A:Illegal string offset \"9x\";Z;")
''')
    derived_start = len(checks)
    checks += lines(r'''
S_sentinel = S_prefix[.RESULT = KNOWN (PINT 777)][.BASE = BASE_VALUE (KNOWN (PINT 888))]
S_sentinel_cast = $cast_apply(S_sentinel,CASTSTRING,PFLOAT 13846598529327300608,z_right)
S_sentinel_cast = S_sentinel[.STRINGDATA = S_sentinel.STRINGDATA ++ [$ptascii("-12.5")]][.RESULT = KNOWN pvalue_right]
$string_concat(S_sentinel_cast,pvalue_left,pvalue_right,false,false) = S_sentinel_cast[.STRINGDATA = S_sentinel_cast.STRINGDATA ++ [$ptascii("-10.5bcde-12.5")]][.RESULT = KNOWN pvalue_base]
S_prefix_bad = S_capture[.STRINGDATA[2] = $ptascii("-10.5zz")]
$string_carrier_valid(S_prefix_bad,pvalue_left)
$string_carrier_valid(S_prefix_bad,pvalue_base)
~$string_read_allocated_base(S_prefix_bad,porigin_left,pvalue_left)
~$string_read_allocated_value(S_prefix_bad,porigin_base,pvalue_base)
$string_read_plan(S_prefix_bad) = eps
S_right_bad = S_capture[.STRINGDATA[4] = $ptascii("-12.50")]
$string_carrier_valid(S_right_bad,pvalue_base)
$string_read_allocated_base(S_right_bad,porigin_left,pvalue_left)
~$string_read_allocated_value(S_right_bad,porigin_right,pvalue_right)
~$string_read_allocated_value(S_right_bad,porigin_base,pvalue_base)
$string_read_plan(S_right_bad) = eps
S_clone = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("-10.5bcde-12.5")]]
pvalue_clone = PSTRING_CARRIER (REQUEST_STRING 6) ($ptascii("-10.5bcde-12.5"))
$string_carrier_valid(S_clone,pvalue_clone)
$string_same(pvalue_base,pvalue_clone) = (false)
$string_read_allocated_value(S_clone,porigin_base,pvalue_base)
~$string_read_allocated_value(S_clone,porigin_base,pvalue_clone)
$string_read_raw_capture(S_clone,poperand,pvalue_base) = eps
$string_read_plan(S_clone) = eps
S_later = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("callback"),$ptascii("-10.5bcde-12.5")]]
$heap_graph(S_later) = $heap_graph(S)
$string_read_allocated_value(S_later,porigin_base,pvalue_base)
$string_read_raw_saved(S_later,pstringread) = (9)
$string_read_ready(S_later,pstringread)
$string_read_resume(S_later,pstringread) = S_later[.TODO = ptask_tail*][.RESULT = KNOWN pvalue_byte][.BASE = BASE_VALUE (KNOWN PNULL)]
pvalue_later_clone = PSTRING_CARRIER (REQUEST_STRING 7) ($ptascii("-10.5bcde-12.5"))
$string_carrier_valid(S_later,pvalue_later_clone)
pstringread_clone = pstringread[.READ.BASE = pvalue_later_clone][.READ.OWNERS = BASE_VALUE (KNOWN pvalue_later_clone)]
$string_read_provider_ready(S_later,pstringread_clone)
$string_read_raw_saved(S_later,pstringread_clone) = eps
~$string_read_source(S_later,pstringread_clone)
~$string_read_ready(S_later,pstringread_clone)
S_number_bad = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_number (PFLOAT 13846739266815655936)) :: ppool.CONSTANTS]]]
~$string_read_allocated_value(S_number_bad,porigin_base,pvalue_base)
expression_new = NExprBinaryOpConcat expression_left (NExprCastString (NExprUnaryMinus (NExprUnaryMinus (NExprUnaryPlus (NExprUnaryMinus (NScalarFloat (FLOAT "4029800000000000") metadata_atom) metadata_sign3) metadata_sign2) metadata_sign1) metadata_number) metadata_right) metadata_base
pcoccurrence_new* = $pcwalk([PCOCCURRENCE pcpath_base expression_new])
S_source_bits = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_new* ++ pcunit.OCCURRENCES]]]
$compiled_read(S_source_bits,porigin_number) = (PFLOAT 13846598529327300608)
~$string_read_allocated_value(S_source_bits,porigin_base,pvalue_base)
S_atom_bits_bad = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_atom (NScalarFloat (FLOAT "4029800000000000") metadata_atom)) :: pcunit.OCCURRENCES]]]
~$string_read_allocated_value(S_atom_bits_bad,porigin_base,pvalue_base)
S_live17 = S_capture[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]
~$string_read_allocated_value(S_live17,porigin_base,pvalue_base)
S_post17 = S[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]
$string_read_raw_saved(S_post17,pstringread) = eps
S_abrupt = S_capture[.COMPLETION = UNSUPPORTED "peer-control"]
~$string_read_allocated_value(S_abrupt,porigin_base,pvalue_base)
S_const = S_capture[.CONSTCONTEXT = ({ORIGIN porigin_base,LINE 18,FACTS eps})]
~$string_read_allocated_value(S_const,porigin_base,pvalue_base)
''')
    for node, expression in (('left', 'NExprBinaryOpCoalesce expression_selected expression_skipped eps'),
                             ('right', 'NExprCastString expression_number eps'),
                             ('number', 'NExprUnaryMinus expression_sign1 eps'),
                             ('sign1', 'NExprUnaryMinus expression_sign2 eps'),
                             ('sign2', 'NExprUnaryPlus expression_sign3 eps'),
                             ('sign3', 'NExprUnaryMinus expression_atom eps'),
                             ('atom', 'NScalarFloat (FLOAT "4029000000000000") eps')):
        checks += [f'S_source_{node} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{node} ({expression})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_allocated_value(S_source_{node},porigin_base,pvalue_base)']
    for node in ('base', 'left', 'right'):
        for label, line, folded in (('line', '0', 'false'), ('folded', f'z_{node}', 'true')):
            state = f'S_code_{node}_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} {line} {folded}) :: pcode.EXPRESSIONS]]]',
                       f'~$string_read_allocated_value({state},porigin_base,pvalue_base)',
                       f'$string_read_plan({state}) = eps']
    for node in ('base', 'left', 'right', 'number', 'sign1', 'sign2', 'sign3'):
        state = 'S_precision_' + node
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'~$string_read_allocated_value({state},porigin_base,pvalue_base)']
    for update in ('.BASECELL = (n_key)', '.KEYCELL = eps', '.READ.PHASE = KEY_CV',
                   '.READ.OWNERS = BASE_VALUE (KNOWN pvalue_left)'):
        checks += [f'$string_read_raw_saved(S,pstringread[{update}]) = eps',
                   f'~$string_read_source(S,pstringread[{update}])']
    # The deepest literal unary checks its operand against its folded pool;
    # an independent precision fact for the raw atom does not add authority.
    checks += lines(r'''
$string_read_raw_float_sign_tree(expression_number)
$string_read_raw_float_sign_tree(expression_atom)
$string_read_raw_float_sign_tree(NExprUnaryPlus expression_number eps)
$string_read_raw_float_sign_tree(NExprUnaryMinus expression_number eps)
$string_read_raw_float_sign_tree(NScalarFloat (FLOAT "7ff0000000000000") eps)
$string_read_raw_float_sign_tree(NExprUnaryMinus (NScalarFloat (FLOAT "7ff0000000000000") eps) eps)
~$string_read_raw_float_sign_tree(NScalarInt (INTEGER 12) eps)
~$string_read_raw_float_sign_tree(NScalarString (BYTES "MTIuNQ==") eps)
~$string_read_raw_float_sign_tree(NExprVariable (BYTES "a2V5") eps)
$string_read_raw_float_sign_tree(NExprCastDouble expression_atom eps)
$string_read_raw_float_sign_tree(NExprUnaryPlus (NExprCastDouble expression_atom eps) eps)
~$string_read_raw_float_sign_tree(NExprBitwiseNot expression_atom eps)
~$string_read_raw_float_sign_tree(NExprBinaryOpPlus expression_atom expression_atom eps)
S_atom_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_atom 17) :: ppool.CONSTANTS]]]
$string_read_allocated_value(S_atom_precision,porigin_base,pvalue_base)
$string_read_plan(S_atom_precision) = (pstringread)
''')
    control = ['S_initial = $php_run(' + control_program + ',0,' + json.dumps(control_filename_b64) + ')',
               'S_initial.COMPLETION = BUDGET'] + seek('S_initial', 0, 'S_capture') + lines(r'''
S_capture.TODO = (KEY_READ_DIM poperand 18 KEY_R) :: ptask_tail*
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
expression_number = NExprUnaryPlus expression_cast metadata_number
expression_cast = NExprCastDouble (NExprUnaryMinus (NScalarFloat (FLOAT "4029000000000000") metadata_atom) metadata_inner) metadata_cast
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_number)
$origin_node(S_capture.SOURCES,porigin_number) = (expression_number)
$string_read_runtime_value(S_capture,porigin_number) = (PFLOAT 13846598529327300608)
$string_read_allocated_base(S_capture,porigin_left,pvalue_left)
$string_read_allocated_value(S_capture,porigin_right,pvalue_right)
$concat_constant(S_capture,(porigin_left)) = false
$concat_constant(S_capture,(porigin_right)) = false
S_capture.CODE = [pcode]
porigin_right = PORIGIN n_unit pcpath_right
porigin_number = PORIGIN n_unit pcpath_number
$origin_child((porigin_number),[PCFIELD 0]) = (porigin_cast)
$origin_node(S_capture.SOURCES,porigin_cast) = (expression_cast)
porigin_cast = PORIGIN n_unit pcpath_cast
$code_expression(pcode.EXPRESSIONS,pcpath_number) = ((z_number,false))
$(z_number > 0)
$compiled_read(S_capture,porigin_number) = eps
$code_expression(pcode.EXPRESSIONS,pcpath_cast) = ((z_cast,false))
$(z_cast > 0)
$compiled_read(S_capture,porigin_cast) = eps
$string_read_runtime_value(S_capture,porigin_cast) = (PFLOAT 13846598529327300608)
$code_expression(pcode.EXPRESSIONS,pcpath_right) = ((z_right,false))
S_prefix = S_capture[.STRINGDATA = S_capture.STRINGDATA[0:4]]
S_cast = $cast_apply(S_prefix,CASTSTRING,PFLOAT 13846598529327300608,z_right)
S_cast = S_prefix[.STRINGDATA = S_prefix.STRINGDATA ++ [$ptascii("-12.5")]][.RESULT = KNOWN pvalue_right]
$string_concat(S_cast,pvalue_left,pvalue_right,false,false) = S_cast[.STRINGDATA = S_cast.STRINGDATA ++ [$ptascii("-10.5bcde-12.5")]][.RESULT = KNOWN pvalue_base]
$string_read_raw_float_sign_tree(expression_number)
$string_read_allocated_value(S_capture,porigin_base,pvalue_base)
$string_read_allocated_base(S_capture,porigin_base,pvalue_base)
$string_read_raw_capture(S_capture,poperand,pvalue_base) =/= eps
$string_read_plan(S_capture) =/= eps
''')
    helper = '\ndec $peer_cast_float_leaf() : bool\ndef $peer_cast_float_leaf() = true\n' + ''.join(
        '  -- if ' + check + '\n' for check in control)
    body = prefix + helper + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n' for check in checks)
    body += '  -- if $peer_cast_float_leaf()\n'
    return body, len(checks) + len(control) + 1, len(checks) - derived_start + len(control) + 1
