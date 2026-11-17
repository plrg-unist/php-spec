"""Direct reserved-tag signs retain the folded header and reference offset six."""

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
    for line in body.splitlines():
        if line.endswith(' = (1)'):
            assert '$string_read_raw_leading(' in line or '$string_read_raw_saved(' in line
    body = body.replace(' = (1)\n', ' = (6)\n')
    body = body.replace('STRING_LEADING 1', 'STRING_LEADING 6')
    body = body.replace('$ptascii("abc")', '$ptascii("1-1000bc")')
    body = body.replace('$ptascii("1x")', '$ptascii("6x")')
    body = body.replace('512:1x;', '512:6x;').replace(';K:2;A:', ';K:7;A:')
    body = body.replace('STORE[n_current] = DEFINED (PINT 2)',
                        'STORE[n_current] = DEFINED (PINT 7)')
    concats = [
        ('left', 'left_pair', 'right_group', '1-1000bc'),
        ('left_pair', 'plus_true', 'minus_true', '1-1'),
        ('right_group', 'zero_pair', 'null_tail', '000bc'),
        ('zero_pair', 'minus_false', 'plus_null', '00'),
        ('null_tail', 'minus_null', 'bc', '0bc'),
    ]
    signs = [
        ('plus_true', 'NExprUnaryPlus', 'true', 1),
        ('minus_true', 'NExprUnaryMinus', 'true', -1),
        ('minus_false', 'NExprUnaryMinus', 'false', 0),
        ('plus_null', 'NExprUnaryPlus', 'null', 0),
        ('minus_null', 'NExprUnaryMinus', 'null', 0),
    ]
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_left expression_right metadata_base)
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
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_guard)
$origin_child((porigin_right),[PCFIELD 1]) = (porigin_selected)
$origin_child((porigin_right),[PCFIELD 2]) = (porigin_unused)
$origin_child((porigin_guard),[PCFIELD 0]) = (porigin_atom)
porigin_base = PORIGIN n_unit pcpath_base
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
''')
    nodes = {}
    shadows = {}
    values = {}
    for node, left, right, text in concats:
        nodes[node] = 'expression_' + node
        shadows[node] = f'NExprBinaryOpConcat expression_{left} expression_{right} eps'
        values[node] = f'PSTRING ($ptascii("{text}"))'
        checks += [f'expression_{node} = NExprBinaryOpConcat expression_{left} expression_{right} metadata_{node}',
                   f'$origin_child((porigin_{node}),[PCFIELD 0]) = (porigin_{left})',
                   f'$origin_child((porigin_{node}),[PCFIELD 1]) = (porigin_{right})']
    checks += lines(r'''
expression_bc = NScalarString (BYTES text_bc) metadata_bc
$base64(text_bc) = $ptascii("bc")
''')
    for node, constructor, tag, integer in signs:
        literal = str(integer) if integer >= 0 else '$(' + str(integer) + ')'
        primitive = 'PNULL' if tag == 'null' else 'PBOOL ' + tag
        nodes[node] = 'expression_' + node
        nodes[node + '_cf'] = 'expression_' + node + '_cf'
        nodes[node + '_name'] = 'name_' + node
        shadows[node] = f'{constructor} expression_{node}_cf eps'
        shadows[node + '_cf'] = f'NExprConstFetch name_{node} eps'
        shadows[node + '_name'] = f'NName (BYTES text_{node}) eps'
        values[node] = 'PINT ' + literal
        values[node + '_cf'] = primitive
        checks += [f'expression_{node} = {constructor} expression_{node}_cf metadata_{node}',
                   f'expression_{node}_cf = NExprConstFetch name_{node} metadata_{node}_cf',
                   f'name_{node} = NName (BYTES text_{node}) metadata_{node}_name',
                   f'$base64(text_{node}) = $ptascii("{tag}")',
                   f'$origin_child((porigin_{node}),[PCFIELD 0]) = (porigin_{node}_cf)',
                   f'$origin_child((porigin_{node}_cf),[PCFIELD 0]) = (porigin_{node}_name)']
    nodes['bc'] = 'expression_bc'
    shadows['bc'] = 'NScalarString (BYTES text_bc) eps'
    values['bc'] = 'PSTRING ($ptascii("bc"))'
    for node in [*nodes, 'right', 'guard', 'selected', 'unused', 'atom']:
        expression = nodes.get(node, 'expression_' + node)
        checks += [f'porigin_{node} = PORIGIN n_unit pcpath_{node}',
                   f'$origin_node(S_capture.SOURCES,porigin_{node}) = ({expression})']
    preorder = ['left', 'left_pair', 'plus_true', 'plus_true_cf', 'plus_true_name',
                'minus_true', 'minus_true_cf', 'minus_true_name', 'right_group',
                'zero_pair', 'minus_false', 'minus_false_cf', 'minus_false_name',
                'plus_null', 'plus_null_cf', 'plus_null_name', 'null_tail',
                'minus_null', 'minus_null_cf', 'minus_null_name', 'bc']
    checks.append('$pcwalk([PCOCCURRENCE pcpath_left expression_left]) = [' + ','.join(
        f'PCOCCURRENCE pcpath_{node} {nodes[node]}' for node in preorder) + ']')
    checks += lines(r'''
$string_read_literal_bytes(expression_left) = eps
$string_read_folded_concat_bytes(expression_left) = ($ptascii("1-1000bc"))
$code_expression(pcode.EXPRESSIONS,pcpath_base) = ((z_base,false))
$(z_base > 0)
$constant_at(ppool.CONSTANTS,pcpath_base) = eps
$compiled_precision(S_capture,(porigin_base)) = (z_precision)
z_precision = 14
$compiled_read(S_capture,porigin_left) = (PSTRING ($ptascii("1-1000bc")))
$compiled_string_value(S_capture,porigin_left,PSTRING ($ptascii("1-1000bc"))) = pvalue_base
$string_read_runtime_value(S_capture,porigin_left) = (pvalue_base)
$compiled_read(S_capture,porigin_right) = eps
$string_read_runtime_value(S_capture,porigin_right) = (pvalue_fallback)
$string_read_raw_known_base(S_capture,porigin_base,pvalue_base)
~$string_read_raw_known_base(S_capture,porigin_base,pvalue_fallback)
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("1-1000bc")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("1-1000bc")))
$string_byte_read(S,$ptascii("1-1000bc"),7,18) = S[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))]
S_folded_budget = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN pvalue_fallback]
$string_read_runtime_value(S_folded_budget,porigin_base) = eps
$string_read_raw_known_base(S_folded_budget,porigin_base,pvalue_base)
''')
    for node, value in values.items():
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{node}) = ((z_{node},true))',
                   f'$(z_{node} > 0)',
                   f'$constant_at(ppool.CONSTANTS,pcpath_{node}) = ({value})',
                   f'$constant_precision_at(ppool.CONSTANTS,pcpath_{node}) = eps',
                   f'$compiled_precision(S_capture,(porigin_{node})) = (z_precision)',
                   f'$compiled_read(S_capture,porigin_{node}) = ({value})',
                   f'$compiled_identity_value(S_capture,porigin_{node}) = ({value})']
    for node, _, _, _ in signs:
        name = node + '_name'
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}) = eps',
                   f'$constant_at(ppool.CONSTANTS,pcpath_{name}) = eps',
                   f'$constant_precision_at(ppool.CONSTANTS,pcpath_{name}) = eps',
                   f'$compiled_precision(S_capture,(porigin_{name})) = (z_precision)',
                   f'$compiled_read(S_capture,porigin_{name}) = eps']
        state = 'S_unary_keyword_pruned_' + name
        checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{name} 0 true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{name} (PSTRING ($ptascii("wrong")))) :: (PCCPRECISION pcpath_{name} 17) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value({state},porigin_left) = (pvalue_base)',
                   f'$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for node, shadow in shadows.items():
        if node == 'left':
            continue
        state = 'S_unary_keyword_shadow_' + node
        checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{node} ({shadow})) :: pcunit.OCCURRENCES]]]',
                   f'$compiled_read({state},porigin_left) = (PSTRING ($ptascii("1-1000bc")))',
                   f'$string_read_runtime_value({state},porigin_left) = eps',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    poisons = [(node, 'PSTRING ($ptascii("wrong"))') for node, _, _, _ in concats if node != 'left']
    for node, _, tag, _ in signs:
        poisons += [(node, 'PINT 9'),
                    (node + '_cf', 'PBOOL false' if tag == 'true' else 'PBOOL true')]
    for node, value in poisons:
        state = 'S_unary_keyword_pool_' + node
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{node} ({value})) :: ppool.CONSTANTS]]]',
                   f'$compiled_read({state},porigin_left) = (PSTRING ($ptascii("1-1000bc")))',
                   f'$compiled_string_value({state},porigin_left,PSTRING ($ptascii("1-1000bc"))) = PSTRING ($ptascii("1-1000bc"))',
                   f'$string_read_runtime_value({state},porigin_left) = eps',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, update in (
            ('left_emitted', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left z_left false) :: pcode.EXPRESSIONS]]'),
            ('left_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left 0 true) :: pcode.EXPRESSIONS]]'),
            ('left_bytes', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PSTRING ($ptascii("wrong")))) :: ppool.CONSTANTS]]'),
            ('left_type', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left (PINT 1)) :: ppool.CONSTANTS]]'),
            ('root_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base 0 false) :: pcode.EXPRESSIONS]]'),
            ('root_folded', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base z_base true) :: pcode.EXPRESSIONS]]'),
            ('root_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_base $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('left_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('left_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_left (NExprBinaryOpConcat expression_left_pair expression_right_group eps)) :: pcunit.OCCURRENCES]]'),
            ('right_source', '.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right (NExprTernary expression_guard expression_selected expression_unused eps)) :: pcunit.OCCURRENCES]]')):
        state = 'S_unary_keyword_bad_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_base) = eps',
                   f'~$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for label, update in (
            ('right_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 0 false) :: pcode.EXPRESSIONS]]'),
            ('right_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right $(z_precision + 1)) :: ppool.CONSTANTS]]'),
            ('guard_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_guard 0 false) :: pcode.EXPRESSIONS]]'),
            ('selected_bytes', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_selected (PSTRING ($ptascii("wrong")))) :: ppool.CONSTANTS]]')):
        state = 'S_unary_keyword_skipped_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_runtime_value({state},porigin_right) = eps',
                   f'$string_read_runtime_value({state},porigin_base) = (pvalue_base)',
                   f'$string_read_raw_known_base({state},porigin_base,pvalue_base)']
    for constructor, sign in [('NExprUnaryPlus', 1), ('NExprUnaryMinus', -1)]:
        for spelling, integer in [('true', 1), ('false', 0), ('null', 0)]:
            for word in [spelling, spelling.upper()]:
                encoded = base64.b64encode(word.encode()).decode()
                operand = f'NExprConstFetch (NName (BYTES "{encoded}") eps) eps'
                checks.append(f'$string_read_folded_concat_bytes({constructor} ({operand}) eps) = ($ptascii("{integer * sign}"))')
        checks.append(f'$string_read_folded_concat_bytes({constructor} (NExprConstFetch (NNameFullyQualified (BYTES "dHJ1ZQ==") eps) eps) eps) = ($ptascii("{sign}"))')
        for name in ['NName (BYTES "b3JkaW5hcnk=") eps',
                     'NNameRelative (BYTES "dHJ1ZQ==") eps']:
            checks.append(f'$string_read_folded_concat_bytes({constructor} (NExprConstFetch ({name}) eps) eps) = eps')
        for child in ['NExprUnaryPlus expression_plus_true_cf eps',
                      'NExprUnaryMinus expression_plus_true_cf eps',
                      'NScalarString (BYTES "dHJ1ZQ==") eps',
                      'NScalarFloat (FLOAT "3ff0000000000000") eps']:
            checks.append(f'$string_read_folded_concat_bytes({constructor} ({child}) eps) = eps')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
