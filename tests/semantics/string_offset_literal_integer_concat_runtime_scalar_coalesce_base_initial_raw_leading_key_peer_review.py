"""A folded raw INT/STRING tree keeps its header and saved reference offset."""

from string_offset_initial_raw_leading_key_peer_review import render as render_literal
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_literal(program, filename_b64)
    for old, new in (
            ('$compiled_read(S_capture,porigin_base) = (PSTRING ($ptascii("abc")))', '$compiled_read(S_capture,porigin_base) = eps'),
            ('$compiled_string_value(S_capture,porigin_base,PSTRING ($ptascii("abc"))) = pvalue_base', '$string_read_runtime_value(S_capture,porigin_base) = (pvalue_base)')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    body = body.replace('$ptascii("abc")', '$ptascii("9223372036854775807bc")')
    body = body.replace('([98])', '([50])').replace(';R:b;', ';R:2;')
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_left expression_right metadata_base)
expression_left = NExprBinaryOpConcat expression_head expression_tail metadata_left
expression_head = NScalarInt (INTEGER i_head) metadata_head
expression_tail = NExprBinaryOpConcat expression_b expression_c metadata_tail
expression_b = NScalarString (BYTES text_b) metadata_b
expression_c = NScalarString (BYTES text_c) metadata_c
i_head = 9223372036854775807
$base64(text_b) = $ptascii("b")
$base64(text_c) = $ptascii("c")
$string_read_literal_bytes(expression_left) = eps
$string_read_folded_concat_bytes(expression_left) = ($ptascii("9223372036854775807bc"))
expression_right = NExprTernary expression_guard expression_selected expression_unused metadata_right
expression_guard = NExprCastInt expression_atom metadata_guard
expression_atom = NScalarInt (INTEGER 1) metadata_atom
expression_selected = NScalarString (BYTES text_selected) metadata_selected
expression_unused = NScalarString (BYTES text_unused) metadata_unused
$base64(text_selected) = $ptascii("XYZ")
$base64(text_unused) = $ptascii("abc")
pvalue_fallback = PSTRING_CARRIER INTERNED_STRING ($ptascii("XYZ"))
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_head)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_tail)
$origin_child((porigin_tail),[PCFIELD 0]) = (porigin_b)
$origin_child((porigin_tail),[PCFIELD 1]) = (porigin_c)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_guard)
$origin_child((porigin_right),[PCFIELD 1]) = (porigin_selected)
$origin_child((porigin_right),[PCFIELD 2]) = (porigin_unused)
$origin_child((porigin_guard),[PCFIELD 0]) = (porigin_atom)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
$origin_node(S_capture.SOURCES,porigin_head) = (expression_head)
$origin_node(S_capture.SOURCES,porigin_tail) = (expression_tail)
$origin_node(S_capture.SOURCES,porigin_b) = (expression_b)
$origin_node(S_capture.SOURCES,porigin_c) = (expression_c)
$origin_node(S_capture.SOURCES,porigin_right) = (expression_right)
$origin_node(S_capture.SOURCES,porigin_guard) = (expression_guard)
$origin_node(S_capture.SOURCES,porigin_selected) = (expression_selected)
$origin_node(S_capture.SOURCES,porigin_unused) = (expression_unused)
$origin_node(S_capture.SOURCES,porigin_atom) = (expression_atom)
porigin_base = PORIGIN n_unit pcpath_base
porigin_left = PORIGIN n_unit pcpath_left
porigin_head = PORIGIN n_unit pcpath_head
porigin_tail = PORIGIN n_unit pcpath_tail
porigin_b = PORIGIN n_unit pcpath_b
porigin_c = PORIGIN n_unit pcpath_c
porigin_right = PORIGIN n_unit pcpath_right
porigin_guard = PORIGIN n_unit pcpath_guard
porigin_selected = PORIGIN n_unit pcpath_selected
porigin_unused = PORIGIN n_unit pcpath_unused
porigin_atom = PORIGIN n_unit pcpath_atom
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
$code_expression(pcode.EXPRESSIONS,pcpath_left) = ((z_left,true))
$(z_left > 0)
$compiled_precision(S_capture,(porigin_base)) = (z_precision)
$compiled_precision(S_capture,(porigin_left)) = (z_precision)
$compiled_read(S_capture,porigin_left) = (PSTRING ($ptascii("9223372036854775807bc")))
$compiled_string_value(S_capture,porigin_left,PSTRING ($ptascii("9223372036854775807bc"))) = pvalue_base
$compiled_identity_value(S_capture,porigin_left) = eps
$string_read_runtime_value(S_capture,porigin_left) = (pvalue_base)
$compiled_read(S_capture,porigin_right) = eps
$string_read_runtime_value(S_capture,porigin_right) = (pvalue_fallback)
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,pvalue_fallback)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("9223372036854775807bc")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("9223372036854775807bc")))
S_folded_budget = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_fallback]
$string_read_runtime_value(S_folded_budget,porigin_base) = eps
$string_read_raw_known_base(S_folded_budget,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_folded_budget,porigin_base,pvalue_fallback)
S_integer_current_three = S[.STORE[n_current] = DEFINED (PINT 3)]
$heap_graph(S_integer_current_three) = H
$string_read_raw_saved(S_integer_current_three,pstringread) = (1)
$string_read_ready(S_integer_current_three,pstringread)
$string_read_resume(S_integer_current_three,pstringread) = S_integer_current_three[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([50]))][.BASE = BASE_VALUE (KNOWN PNULL)]
$string_byte_read(S_integer_current_three,$ptascii("9223372036854775807bc"),3,18) = S_integer_current_three[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([51]))]
''')
    for child in ('head', 'tail', 'b', 'c'):
        checks += [f'$compiled_read(S_capture,porigin_{child}) = eps',
                   f'$code_expression(pcode.EXPRESSIONS,pcpath_{child}) = eps',
                   f'$constant_at(ppool.CONSTANTS,pcpath_{child}) = eps',
                   f'$constant_precision_at(ppool.CONSTANTS,pcpath_{child}) = eps',
                   f'$compiled_precision(S_capture,(porigin_{child})) = (14)']
        state = 'S_folded_ignored_' + child
        checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{child} 0 true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{child} (PSTRING ($ptascii("bad")))) :: (PCCPRECISION pcpath_{child} 17) :: ppool.CONSTANTS]]]',
                   f'$compiled_precision({state},(porigin_{child})) = (17)',
                   f'$string_read_runtime_value({state},porigin_left) = (pvalue_base)',
                   f'$string_read_runtime_value({state},porigin_base) = (pvalue_base)',
                   f'$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, integer, text in (
            ('zero', 0, '0bc'), ('ten', 10, '10bc'),
            ('negative', -1, '-1bc'), ('minimum', -9223372036854775808, '-9223372036854775808bc')):
        literal = str(integer) if integer >= 0 else '$(' + str(integer) + ')'
        checks += lines(f'''
expression_integer_{label}_head = NScalarInt (INTEGER {literal}) metadata_head
expression_integer_{label}_left = NExprBinaryOpConcat expression_integer_{label}_head expression_tail metadata_left
expression_integer_{label}_base = NExprBinaryOpCoalesce expression_integer_{label}_left expression_right metadata_base
S_integer_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_integer_{label}_base) :: (PCOCCURRENCE pcpath_left expression_integer_{label}_left) :: (PCOCCURRENCE pcpath_head expression_integer_{label}_head) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PSTRING ($ptascii("{text}")))) :: ppool.CONSTANTS]]]
$string_read_literal_bytes(expression_integer_{label}_left) = eps
$string_read_folded_concat_bytes(expression_integer_{label}_left) = ($ptascii("{text}"))
$compiled_read(S_integer_{label},porigin_left) = (PSTRING ($ptascii("{text}")))
$compiled_string_value(S_integer_{label},porigin_left,PSTRING ($ptascii("{text}"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("{text}"))
$string_read_runtime_value(S_integer_{label},porigin_left) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("{text}")))
$string_read_runtime_value(S_integer_{label},porigin_base) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("{text}")))
$string_read_raw_known_base(S_integer_{label},porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("{text}")))
''')
    for label, node, text in (
            ('overflow', 'NScalarInt (INTEGER 9223372036854775808) metadata_head', '9223372036854775808bc'),
            ('underflow', 'NScalarInt (INTEGER $(-9223372036854775809)) metadata_head', '-9223372036854775809bc'),
            ('float', 'NScalarFloat (FLOAT "3ff0000000000000") metadata_head', '1bc')):
        checks += lines(f'''
expression_integer_bad_{label}_head = {node}
expression_integer_bad_{label}_left = NExprBinaryOpConcat expression_integer_bad_{label}_head expression_tail metadata_left
expression_integer_bad_{label}_base = NExprBinaryOpCoalesce expression_integer_bad_{label}_left expression_right metadata_base
S_integer_bad_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_integer_bad_{label}_base) :: (PCOCCURRENCE pcpath_left expression_integer_bad_{label}_left) :: (PCOCCURRENCE pcpath_head expression_integer_bad_{label}_head) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PSTRING ($ptascii("{text}")))) :: ppool.CONSTANTS]]]
$parser_literal_at(expression_integer_bad_{label}_left,z_precision) = (PSTRING ($ptascii("{text}")))
$compiled_read(S_integer_bad_{label},porigin_left) = (PSTRING ($ptascii("{text}")))
$compiled_string_value(S_integer_bad_{label},porigin_left,PSTRING ($ptascii("{text}"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("{text}"))
$string_read_folded_concat_bytes(expression_integer_bad_{label}_left) = eps
$string_read_runtime_value(S_integer_bad_{label},porigin_left) = eps
$string_read_runtime_value(S_integer_bad_{label},porigin_base) = eps
~$string_read_raw_known_base(S_integer_bad_{label},porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("{text}")))
''')
    checks += lines(r'''
expression_integer_nul_b = NScalarString (BYTES "AA==") metadata_b
expression_integer_nul_tail = NExprBinaryOpConcat expression_integer_nul_b expression_c metadata_tail
expression_integer_nul_left = NExprBinaryOpConcat expression_head expression_integer_nul_tail metadata_left
expression_integer_nul_base = NExprBinaryOpCoalesce expression_integer_nul_left expression_right metadata_base
n_integer_nul* = $ptascii("9223372036854775807") ++ [0,99]
S_integer_nul = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_integer_nul_base) :: (PCOCCURRENCE pcpath_left expression_integer_nul_left) :: (PCOCCURRENCE pcpath_tail expression_integer_nul_tail) :: (PCOCCURRENCE pcpath_b expression_integer_nul_b) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PSTRING n_integer_nul*)) :: ppool.CONSTANTS]]]
$string_read_folded_concat_bytes(expression_integer_nul_left) = (n_integer_nul*)
$compiled_string_value(S_integer_nul,porigin_left,PSTRING n_integer_nul*) = PSTRING_CARRIER INTERNED_STRING n_integer_nul*
$string_read_runtime_value(S_integer_nul,porigin_left) = eps
$string_read_runtime_value(S_integer_nul,porigin_base) = eps
~$string_read_raw_known_base(S_integer_nul,porigin_base,PSTRING_CARRIER INTERNED_STRING n_integer_nul*)
$string_read_folded_concat_bytes(NExprConstFetch (NName (BYTES "ZmFsc2U=") eps) eps) = eps
$string_read_folded_concat_bytes(NExprConstFetch (NName (BYTES "bnVsbA==") eps) eps) = eps
$string_read_folded_concat_bytes(NExprUnaryMinus (NScalarInt (INTEGER 1) eps) eps) = ($ptascii("-1"))
''')
    for label, node in (
            ('head', 'NScalarInt (INTEGER i_head) eps'),
            ('tail', 'NExprBinaryOpConcat expression_b expression_c eps'),
            ('b', 'NScalarString (BYTES text_b) eps'),
            ('c', 'NScalarString (BYTES text_c) eps')):
        state = 'S_folded_shadow_' + label
        checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'$compiled_read({state},porigin_left) = (PSTRING ($ptascii("9223372036854775807bc")))',
                   f'$compiled_string_value({state},porigin_left,PSTRING ($ptascii("9223372036854775807bc"))) = pvalue_base',
                   f'$string_read_runtime_value({state},porigin_left) = eps',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, update in (
            ('left_emitted', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left z_left false) :: pcode.EXPRESSIONS]]'),
            ('left_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 0 true) :: pcode.EXPRESSIONS]]'),
            ('left_bytes', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]'),
            ('left_type', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PINT 1)) :: ppool.CONSTANTS]]'),
            ('root_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 0 false) :: pcode.EXPRESSIONS]]'),
            ('root_folded', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 18 true) :: pcode.EXPRESSIONS]]'),
            ('root_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_base $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('left_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('left_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_left (NExprBinaryOpConcat expression_head expression_tail eps)) :: pcunit.OCCURRENCES]]'),
            ('right_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right (NExprTernary expression_guard expression_selected expression_unused eps)) :: pcunit.OCCURRENCES]]')):
        state = 'S_folded_bad_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, update in (
            ('right_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 0 false) :: pcode.EXPRESSIONS]]'),
            ('right_folded', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 18 true) :: pcode.EXPRESSIONS]]'),
            ('right_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('guard_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_guard 0 false) :: pcode.EXPRESSIONS]]'),
            ('guard_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_guard $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('atom_emitted', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_atom 18 false) :: pcode.EXPRESSIONS]]'),
            ('selected_bytes', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_selected (PSTRING ($ptascii("bad")))) :: ppool.CONSTANTS]]'),
            ('selected_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_selected $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('selected_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_selected (NScalarString (BYTES text_selected) eps)) :: pcunit.OCCURRENCES]]'),
            ('unused_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_unused (NScalarString (BYTES text_unused) eps)) :: pcunit.OCCURRENCES]]')):
        state = 'S_folded_skipped_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_right) = eps',
                   f'$string_read_runtime_value({state},porigin_base) = (pvalue_base)',
                   f'$string_read_raw_known_base({state},porigin_base,pvalue_base)',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_fallback)']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
