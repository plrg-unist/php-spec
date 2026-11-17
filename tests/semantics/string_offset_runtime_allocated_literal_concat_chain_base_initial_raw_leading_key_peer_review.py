"""A literal CONCAT chain keeps its owned header and saved raw reference key."""

from string_offset_initial_raw_leading_key_peer_review import render as render_reference
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_reference(program, filename_b64)
    body = body.replace('~$string_read_shape(S,pstringread[.PHASE = STRING_LEADING 2])',
                        '~$string_read_shape(S,pstringread[.PHASE = STRING_LEADING 4])')
    for line in body.splitlines():
        if line.endswith(' = (1)'):
            assert '$string_read_raw_leading(' in line or '$string_read_raw_saved(' in line
    body = body.replace(' = (1)\n', ' = (3)\n').replace('STRING_LEADING 1', 'STRING_LEADING 3')
    body = body.replace('$ptascii("abc")', '$ptascii("10bcde")')
    body = body.replace('$ptascii("1x")', '$ptascii("3x")')
    body = body.replace('512:1x;', '512:3x;').replace(';R:b;K:2;A:', ';R:c;K:4;A:')
    body = body.replace('([98])', '([99])')
    body = body.replace('STORE[n_current] = DEFINED (PINT 2)',
                        'STORE[n_current] = DEFINED (PINT 4)')
    body = body.replace('pvalue_base = PSTRING_CARRIER INTERNED_STRING ($ptascii("10bcde"))',
                        'pvalue_base = PSTRING_CARRIER (REQUEST_STRING 3) ($ptascii("10bcde"))')
    body = body.replace('STRINGDATA = [$ptascii("512")]',
                        'STRINGDATA = [$ptascii("512"),$ptascii("10"),$ptascii("10bc"),$ptascii("10bcde")]')
    body = body.replace('$string_read_raw_leading(', '$string_read_allocated_leading(S_capture,')
    for old, new in (
            ('$compiled_read(S_capture,porigin_base) = (PSTRING ($ptascii("10bcde")))',
             '$compiled_read(S_capture,porigin_base) = eps'),
            ('$compiled_string_value(S_capture,porigin_base,PSTRING ($ptascii("10bcde"))) = pvalue_base',
             '$string_read_allocated_base(S_capture,porigin_base,pvalue_base)')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_chain expression_right metadata_base)
expression_chain = NExprBinaryOpConcat expression_inner expression_de metadata_chain
expression_inner = NExprBinaryOpConcat expression_cast expression_bc metadata_inner
expression_cast = NExprCastString expression_atom metadata_cast
expression_atom = NScalarInt (INTEGER 10) metadata_atom
expression_bc = NScalarString (BYTES text_bc) metadata_bc
expression_de = NScalarString (BYTES text_de) metadata_de
$base64(text_bc) = $ptascii("bc")
$base64(text_de) = $ptascii("de")
expression_right = NExprTernary expression_guard expression_selected expression_unused metadata_right
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_chain)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)
$origin_child((porigin_chain),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_chain),[PCFIELD 1]) = (porigin_de)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_cast)
$origin_child((porigin_inner),[PCFIELD 1]) = (porigin_bc)
$origin_child((porigin_cast),[PCFIELD 0]) = (porigin_atom)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_guard)
$origin_child((porigin_right),[PCFIELD 1]) = (porigin_selected)
$origin_child((porigin_right),[PCFIELD 2]) = (porigin_unused)
porigin_base = PORIGIN n_unit pcpath_base
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
pvalue_cast = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("10"))
pvalue_inner = PSTRING_CARRIER (REQUEST_STRING 2) ($ptascii("10bc"))
$string_read_allocated_value(S_capture,porigin_cast,pvalue_cast)
$string_read_allocated_value(S_capture,porigin_inner,pvalue_inner)
$string_read_allocated_value(S_capture,porigin_chain,pvalue_base)
$string_read_allocated_base(S_capture,porigin_chain,pvalue_base)
$string_read_allocated_base(S_capture,porigin_base,pvalue_base)
~$string_read_allocated_value(S_capture,porigin_base,pvalue_base)
~$string_read_allocated_value(S_capture,porigin_inner,pvalue_base)
~$string_read_allocated_value(S_capture,porigin_chain,pvalue_inner)
$string_read_runtime_value(S_capture,porigin_chain) = eps
$string_read_runtime_value(S_capture,porigin_base) = eps
$concat_constant(S_capture,(porigin_cast)) = false
$concat_constant(S_capture,(porigin_inner)) = false
$concat_constant(S_capture,(porigin_bc)) = true
$concat_constant(S_capture,(porigin_de)) = true
$string_read_provider_ready(S_capture,pstringread)
$string_byte_read(S,$ptascii("10bcde"),4,18) = S[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([100]))]
S_cast_prefix = S_capture[.STRINGDATA = [$ptascii("512")]]
$cast_apply(S_cast_prefix,CASTSTRING,PINT 10,18) = S_cast_prefix[.STRINGDATA = [$ptascii("512"),$ptascii("10")]][.RESULT = KNOWN pvalue_cast]
S_inner_prefix = S_capture[.STRINGDATA = [$ptascii("512"),$ptascii("10")]]
$string_concat(S_inner_prefix,pvalue_cast,PSTRING_CARRIER INTERNED_STRING ($ptascii("bc")),false,true) = S_inner_prefix[.STRINGDATA = [$ptascii("512"),$ptascii("10"),$ptascii("10bc")]][.RESULT = KNOWN pvalue_inner]
S_chain_prefix = S_capture[.STRINGDATA = [$ptascii("512"),$ptascii("10"),$ptascii("10bc")]]
$string_concat(S_chain_prefix,pvalue_inner,PSTRING_CARRIER INTERNED_STRING ($ptascii("de")),false,true) = S_chain_prefix[.STRINGDATA = S_capture.STRINGDATA][.RESULT = KNOWN pvalue_base]
$heap_graph(S_cast_prefix) = $heap_graph(S_capture)
$heap_graph(S_inner_prefix) = $heap_graph(S_capture)
$heap_graph(S_chain_prefix) = $heap_graph(S_capture)
''')
    nodes = dict(chain='expression_chain', inner='expression_inner', cast='expression_cast',
                 atom='expression_atom', bc='expression_bc', de='expression_de',
                 right='expression_right', guard='expression_guard',
                 selected='expression_selected', unused='expression_unused')
    for name, expression in nodes.items():
        checks += [f'porigin_{name} = PORIGIN n_unit pcpath_{name}',
                   f'$origin_node(S_capture.SOURCES,porigin_{name}) = ({expression})']
    for name in ('base', 'chain', 'inner', 'cast'):
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}) = ((z_{name},false))',
                   f'$(z_{name} > 0)',
                   f'$compiled_precision(S_capture,(porigin_{name})) = (14)',
                   f'$compiled_read(S_capture,porigin_{name}) = eps',
                   f'$compiled_identity_value(S_capture,porigin_{name}) = eps',
                   f'$constant_at(ppool.CONSTANTS,pcpath_{name}) = eps']
    for name, value in (('atom', 'PINT 10'), ('bc', 'PSTRING ($ptascii("bc"))'),
                        ('de', 'PSTRING ($ptascii("de"))')):
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{name}) = ((z_{name},true))',
                   f'$(z_{name} > 0)',
                   f'$compiled_precision(S_capture,(porigin_{name})) = (14)',
                   f'$compiled_read(S_capture,porigin_{name}) = ({value})',
                   f'$compiled_identity_value(S_capture,porigin_{name}) = ({value})',
                   f'$constant_at(ppool.CONSTANTS,pcpath_{name}) = ({value})']
    checks += lines(r'''
S_suffix_entry = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("callback"),$ptascii("10bcde")]]
$string_read_allocated_base(S_suffix_entry,porigin_base,pvalue_base)
$string_read_raw_capture(S_suffix_entry,poperand,pvalue_base) = eps
$string_read_plan(S_suffix_entry) = eps
S_suffix_saved = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("callback"),$ptascii("10bcde")]]
$heap_graph(S_suffix_saved) = H
$string_read_raw_saved(S_suffix_saved,pstringread) = (3)
$string_read_source(S_suffix_saved,pstringread)
$string_read_provider_ready(S_suffix_saved,pstringread)
$string_read_ready(S_suffix_saved,pstringread)
$string_read_resume(S_suffix_saved,pstringread) = S_suffix_saved[.TODO = ptask_tail*][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ([99]))][.BASE = BASE_VALUE (KNOWN PNULL)]
pvalue_same = PSTRING_CARRIER (REQUEST_STRING 5) ($ptascii("10bcde"))
$string_carrier_valid(S_suffix_saved,pvalue_same)
$string_same(pvalue_base,pvalue_same) = (false)
$string_read_raw_saved(S_suffix_saved,pstringread[.READ.BASE = pvalue_same]) = eps
$string_read_raw_saved(S_suffix_saved,pstringread[.READ.OWNERS = BASE_VALUE (KNOWN pvalue_same)]) = eps
~$string_read_source(S_suffix_saved,pstringread[.READ.BASE = pvalue_same])
~$string_read_provider_ready(S_suffix_saved,pstringread[.READ.BASE = pvalue_same])
S_clone = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("10bcde")]]
pvalue_clone = PSTRING_CARRIER (REQUEST_STRING 4) ($ptascii("10bcde"))
$string_carrier_valid(S_clone,pvalue_clone)
~$string_read_allocated_value(S_clone,porigin_chain,pvalue_clone)
$string_read_raw_capture(S_clone[.RESULT = KNOWN pvalue_clone],poperand,pvalue_clone) = eps
S_nul = S_capture[.STRINGDATA = [$ptascii("512"),$ptascii("10"),$ptascii("10bc"),[49,48,98,99,0,100,101]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING 3) ([49,48,98,99,0,100,101])
$string_carrier_valid(S_nul,pvalue_nul)
~$string_read_allocated_base(S_nul,porigin_base,pvalue_nul)
$string_read_allocated_leading(S_nul,pvalue_nul,pvalue_raw) = eps
$string_read_raw_capture(S_nul[.RESULT = KNOWN pvalue_nul],poperand,pvalue_nul) = eps
''')
    for name, expression in (
            ('chain', 'NExprBinaryOpConcat expression_inner expression_de eps'),
            ('inner', 'NExprBinaryOpConcat expression_cast expression_bc eps'),
            ('cast', 'NExprCastString expression_atom eps'),
            ('atom', 'NScalarInt (INTEGER 10) eps'),
            ('bc', 'NScalarString (BYTES text_bc) eps'),
            ('de', 'NScalarString (BYTES text_de) eps'),
            ('right', 'NExprTernary expression_guard expression_selected expression_unused eps')):
        state = 'S_chain_shadow_' + name
        checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{name} ({expression})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                   f'$string_read_raw_capture({state},poperand,pvalue_base) = eps']
    updates = [(name + '_line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{name} 0 false) :: pcode.EXPRESSIONS]]')
               for name in ('base', 'chain', 'inner', 'cast')]
    updates += [(name + '_folded', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{name} z_{name} true) :: pcode.EXPRESSIONS]]')
                for name in ('base', 'chain', 'inner', 'cast')]
    updates += [(name + '_precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{name} 17) :: ppool.CONSTANTS]]')
                for name in ('base', 'chain', 'inner', 'cast', 'atom', 'bc', 'de')]
    updates += [(name + '_flag', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{name} z_{name} false) :: pcode.EXPRESSIONS]]')
                for name in ('bc', 'de')]
    updates += [('atom_type', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PSTRING ($ptascii("10")))) :: ppool.CONSTANTS]]'),
                ('cast_prefix', '.STRINGDATA = [$ptascii("512"),$ptascii("wrong"),$ptascii("10bc"),$ptascii("10bcde")]'),
                ('inner_prefix', '.STRINGDATA = [$ptascii("512"),$ptascii("10"),$ptascii("wrong"),$ptascii("10bcde")]'),
                ('result_prefix', '.STRINGDATA = [$ptascii("512"),$ptascii("10"),$ptascii("10bc"),$ptascii("wrong")]'),
                ('constant_context', '.CONSTCONTEXT = ({ORIGIN porigin_base,LINE 18,FACTS eps})')]
    for label, update in updates:
        state = 'S_chain_bad_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                   f'$string_read_raw_capture({state},poperand,pvalue_base) = eps']
    for label, update in (
            ('guard_line', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_guard 0 false) :: pcode.EXPRESSIONS]]'),
            ('selected_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_selected (PSTRING ($ptascii("wrong")))) :: ppool.CONSTANTS]]'),
            ('right_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right 17) :: ppool.CONSTANTS]]')):
        state = 'S_chain_skipped_' + label
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_allocated_base({state},porigin_base,pvalue_base)',
                   f'$string_read_raw_capture({state},poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
