"""Reserved literals retain the folded base, Name source and saved reference key."""

import base64

from string_offset_initial_raw_leading_key_peer_review import render as render_reference
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_reference(program, filename_b64)
    for old, new in (
            ('$compiled_read(S_capture,porigin_base) = (PSTRING ($ptascii("abc")))',
             '$compiled_read(S_capture,porigin_base) = eps'),
            ('$compiled_string_value(S_capture,porigin_base,PSTRING ($ptascii("abc"))) = pvalue_base',
             '$string_read_runtime_value(S_capture,porigin_base) = (pvalue_base)')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    body = body.replace('$ptascii("abc")', '$ptascii("1bc")')
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_left expression_right metadata_base)
expression_left = NExprBinaryOpConcat expression_head expression_tail metadata_left
expression_head = NExprConstFetch name_head metadata_head
name_head = NName (BYTES text_name) metadata_name
$base64(text_name) = $ptascii("true")
expression_tail = NExprBinaryOpConcat expression_b expression_c metadata_tail
expression_b = NScalarString (BYTES text_b) metadata_b
expression_c = NScalarString (BYTES text_c) metadata_c
$base64(text_b) = $ptascii("b")
$base64(text_c) = $ptascii("c")
$string_read_literal_bytes(expression_left) = eps
$string_read_folded_concat_bytes(expression_left) = ($ptascii("1bc"))
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
$origin_child((porigin_head),[PCFIELD 0]) = (porigin_name)
$origin_child((porigin_tail),[PCFIELD 0]) = (porigin_b)
$origin_child((porigin_tail),[PCFIELD 1]) = (porigin_c)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_guard)
$origin_child((porigin_right),[PCFIELD 1]) = (porigin_selected)
$origin_child((porigin_right),[PCFIELD 2]) = (porigin_unused)
$origin_child((porigin_guard),[PCFIELD 0]) = (porigin_atom)
porigin_base = PORIGIN n_unit pcpath_base
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
''')
    for node in ('left', 'head', 'tail', 'b', 'c', 'right',
                 'guard', 'selected', 'unused', 'atom'):
        checks += [f'porigin_{node} = PORIGIN n_unit pcpath_{node}',
                   f'$origin_node(S_capture.SOURCES,porigin_{node}) = (expression_{node})']
    checks += lines(r'''
porigin_name = PORIGIN n_unit pcpath_name
$origin_node(S_capture.SOURCES,porigin_name) = (name_head)
$pcwalk([PCOCCURRENCE pcpath_left expression_left]) = [PCOCCURRENCE pcpath_left expression_left,PCOCCURRENCE pcpath_head expression_head,PCOCCURRENCE pcpath_name name_head,PCOCCURRENCE pcpath_tail expression_tail,PCOCCURRENCE pcpath_b expression_b,PCOCCURRENCE pcpath_c expression_c]
$code_expression(pcode.EXPRESSIONS,pcpath_base) = ((z_base,false))
$(z_base > 0)
$compiled_precision(S_capture,(porigin_base)) = (z_precision)
z_precision = 14
$constant_at(ppool.CONSTANTS,pcpath_base) = eps
$compiled_read(S_capture,porigin_left) = (PSTRING ($ptascii("1bc")))
$compiled_string_value(S_capture,porigin_left,PSTRING ($ptascii("1bc"))) = pvalue_base
$compiled_identity_value(S_capture,porigin_left) = (PSTRING ($ptascii("1bc")))
$compiled_read(S_capture,porigin_right) = eps
$string_read_runtime_value(S_capture,porigin_left) = (pvalue_base)
$string_read_runtime_value(S_capture,porigin_right) = (pvalue_fallback)
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,pvalue_fallback)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("1bc")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("1bc")))
S_folded_budget = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_fallback]
$string_read_runtime_value(S_folded_budget,porigin_base) = eps
$string_read_raw_known_base(S_folded_budget,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_folded_budget,porigin_base,pvalue_fallback)
$string_byte_read(S,$ptascii("1bc"),2,18) = S[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))]
''')
    for node, value in (
            ('left', 'PSTRING ($ptascii("1bc"))'),
            ('head', 'PBOOL true'),
            ('tail', 'PSTRING ($ptascii("bc"))')):
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{node}) = ((z_{node},true))',
                   f'$(z_{node} > 0)',
                   f'$constant_at(ppool.CONSTANTS,pcpath_{node}) = ({value})',
                   f'$constant_precision_at(ppool.CONSTANTS,pcpath_{node}) = eps',
                   f'$compiled_precision(S_capture,(porigin_{node})) = (z_precision)',
                   f'$compiled_read(S_capture,porigin_{node}) = ({value})',
                   f'$compiled_identity_value(S_capture,porigin_{node}) = ({value})']
    for node in ('name', 'b', 'c'):
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{node}) = eps',
                   f'$constant_at(ppool.CONSTANTS,pcpath_{node}) = eps',
                   f'$constant_precision_at(ppool.CONSTANTS,pcpath_{node}) = eps',
                   f'$compiled_read(S_capture,porigin_{node}) = eps',
                   f'$compiled_identity_value(S_capture,porigin_{node}) = eps',
                   f'$compiled_precision(S_capture,(porigin_{node})) = (z_precision)']
    for label, node in (
            ('head', 'NExprConstFetch name_head eps'),
            ('name', 'NName (BYTES text_name) eps'),
            ('tail', 'NExprBinaryOpConcat expression_b expression_c eps'),
            ('b', 'NScalarString (BYTES text_b) eps'),
            ('c', 'NScalarString (BYTES text_c) eps')):
        state = 'S_keyword_shadow_' + label
        checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'$compiled_read({state},porigin_left) = (PSTRING ($ptascii("1bc")))',
                   f'$string_read_runtime_value({state},porigin_left) = eps',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, update in (
            ('left_emitted', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left z_left false) :: pcode.EXPRESSIONS]]'),
            ('left_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 0 true) :: pcode.EXPRESSIONS]]'),
            ('left_bytes', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PSTRING ($ptascii("XYZ")))) :: ppool.CONSTANTS]]'),
            ('left_type', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PINT 1)) :: ppool.CONSTANTS]]'),
            ('root_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 0 false) :: pcode.EXPRESSIONS]]'),
            ('root_folded', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base z_base true) :: pcode.EXPRESSIONS]]'),
            ('root_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_base $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('left_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('left_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_left (NExprBinaryOpConcat expression_head expression_tail eps)) :: pcunit.OCCURRENCES]]'),
            ('right_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right (NExprTernary expression_guard expression_selected expression_unused eps)) :: pcunit.OCCURRENCES]]')):
        state = 'S_keyword_bad_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, update in (
            ('head_code', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_head 0 false) :: pcode.EXPRESSIONS]]'),
            ('head_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_head (PBOOL false)) :: ppool.CONSTANTS]]'),
            ('tail_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_tail (PSTRING ($ptascii("wrong")))) :: ppool.CONSTANTS]]')):
        state = 'S_keyword_retained_bad_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$compiled_read({state},porigin_left) = (PSTRING ($ptascii("1bc")))',
                   f'$compiled_string_value({state},porigin_left,PSTRING ($ptascii("1bc"))) = PSTRING ($ptascii("1bc"))',
                   f'$string_read_runtime_value({state},porigin_left) = eps',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, update in (
            ('right_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 0 false) :: pcode.EXPRESSIONS]]'),
            ('right_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('guard_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_guard 0 false) :: pcode.EXPRESSIONS]]'),
            ('guard_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_guard $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('atom_emitted', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_atom 18 false) :: pcode.EXPRESSIONS]]'),
            ('selected_bytes', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_selected (PSTRING ($ptascii("bad")))) :: ppool.CONSTANTS]]'),
            ('unused_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_unused (NScalarString (BYTES text_unused) eps)) :: pcunit.OCCURRENCES]]')):
        state = 'S_keyword_skipped_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_right) = eps',
                   f'$string_read_runtime_value({state},porigin_base) = (pvalue_base)',
                   f'$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    # Coherent constructed source changes add no original-source credit.
    for label, constructor, spelling, value, text in (
            ('true', 'NName', 'TrUe', 'PBOOL true', '1bc'),
            ('false', 'NName', 'FALSE', 'PBOOL false', 'bc'),
            ('null', 'NName', 'NuLl', 'PNULL', 'bc'),
            ('fqn', 'NNameFullyQualified', 'TrUe', 'PBOOL true', '1bc')):
        encoded = base64.b64encode(spelling.encode()).decode()
        primitive_text = '1' if value == 'PBOOL true' else ''
        checks += lines(f'''
name_keyword_{label} = {constructor} (BYTES "{encoded}") metadata_name
expression_keyword_{label}_head = NExprConstFetch name_keyword_{label} metadata_head
expression_keyword_{label}_left = NExprBinaryOpConcat expression_keyword_{label}_head expression_tail metadata_left
expression_keyword_{label}_base = NExprBinaryOpCoalesce expression_keyword_{label}_left expression_right metadata_base
S_keyword_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_keyword_{label}_base) :: (PCOCCURRENCE pcpath_left expression_keyword_{label}_left) :: (PCOCCURRENCE pcpath_head expression_keyword_{label}_head) :: (PCOCCURRENCE pcpath_name name_keyword_{label}) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PSTRING ($ptascii("{text}")))) :: (PCONSTANT pcpath_head ({value})) :: ppool.CONSTANTS]]]
$string_read_literal_bytes(expression_keyword_{label}_left) = eps
$string_read_folded_concat_bytes(expression_keyword_{label}_head) = ($ptascii("{primitive_text}"))
$string_read_folded_concat_bytes(expression_keyword_{label}_left) = ($ptascii("{text}"))
$compiled_read(S_keyword_{label},porigin_head) = ({value})
$compiled_read(S_keyword_{label},porigin_left) = (PSTRING ($ptascii("{text}")))
$compiled_string_value(S_keyword_{label},porigin_left,PSTRING ($ptascii("{text}"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("{text}"))
$string_read_runtime_value(S_keyword_{label},porigin_left) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("{text}")))
$string_read_runtime_value(S_keyword_{label},porigin_base) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("{text}")))
$string_read_raw_known_base(S_keyword_{label},porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("{text}")))
''')
    for label, name in (
            ('ordinary', 'NName (BYTES "b3JkaW5hcnk=") metadata_name'),
            ('empty', 'NName (BYTES "") metadata_name'),
            ('relative', 'NNameRelative (BYTES "dHJ1ZQ==") metadata_name')):
        checks += lines(f'''
name_keyword_bad_{label} = {name}
expression_keyword_bad_{label}_head = NExprConstFetch name_keyword_bad_{label} metadata_head
expression_keyword_bad_{label}_left = NExprBinaryOpConcat expression_keyword_bad_{label}_head expression_tail metadata_left
expression_keyword_bad_{label}_base = NExprBinaryOpCoalesce expression_keyword_bad_{label}_left expression_right metadata_base
S_keyword_bad_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_keyword_bad_{label}_base) :: (PCOCCURRENCE pcpath_left expression_keyword_bad_{label}_left) :: (PCOCCURRENCE pcpath_head expression_keyword_bad_{label}_head) :: (PCOCCURRENCE pcpath_name name_keyword_bad_{label}) :: pcunit.OCCURRENCES]]]
$compiled_read(S_keyword_bad_{label},porigin_head) = (PBOOL true)
$compiled_read(S_keyword_bad_{label},porigin_left) = (PSTRING ($ptascii("1bc")))
$compiled_string_value(S_keyword_bad_{label},porigin_left,PSTRING ($ptascii("1bc"))) = PSTRING_CARRIER INTERNED_STRING ($ptascii("1bc"))
$string_read_folded_concat_bytes(expression_keyword_bad_{label}_left) = eps
$string_read_runtime_value(S_keyword_bad_{label},porigin_left) = eps
$string_read_runtime_value(S_keyword_bad_{label},porigin_base) = eps
~$string_read_raw_known_base(S_keyword_bad_{label},porigin_base,pvalue_base)
''')
    for node in ('name', 'b', 'c'):
        state = 'S_keyword_pruned_' + node
        checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} 0 true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{node} (PSTRING ($ptascii("wrong")))) :: (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value({state},porigin_left) = (pvalue_base)',
                   f'$string_read_runtime_value({state},porigin_base) = (pvalue_base)',
                   f'$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    checks += lines(r'''
expression_keyword_nul_b = NScalarString (BYTES "AA==") metadata_b
expression_keyword_nul_tail = NExprBinaryOpConcat expression_keyword_nul_b expression_c metadata_tail
expression_keyword_nul_left = NExprBinaryOpConcat expression_head expression_keyword_nul_tail metadata_left
expression_keyword_nul_base = NExprBinaryOpCoalesce expression_keyword_nul_left expression_right metadata_base
n_keyword_nul* = $ptascii("1") ++ [0,99]
S_keyword_nul = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_keyword_nul_base) :: (PCOCCURRENCE pcpath_left expression_keyword_nul_left) :: (PCOCCURRENCE pcpath_tail expression_keyword_nul_tail) :: (PCOCCURRENCE pcpath_b expression_keyword_nul_b) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PSTRING n_keyword_nul*)) :: (PCONSTANT pcpath_tail (PSTRING ([0,99]))) :: ppool.CONSTANTS]]]
$string_read_folded_concat_bytes(expression_keyword_nul_left) = (n_keyword_nul*)
$compiled_string_value(S_keyword_nul,porigin_left,PSTRING n_keyword_nul*) = PSTRING_CARRIER INTERNED_STRING n_keyword_nul*
$string_read_runtime_value(S_keyword_nul,porigin_left) = eps
$string_read_runtime_value(S_keyword_nul,porigin_base) = eps
~$string_read_raw_known_base(S_keyword_nul,porigin_base,PSTRING_CARRIER INTERNED_STRING n_keyword_nul*)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
