"""Folded string-only suffix trees retain their allocated base and saved index."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_literal_concat_chain_base_initial_raw_leading_key_review import render as render_chain


def render(program, filename_b64, reference=False):
    body, _, _ = render_chain(program, filename_b64, reference=reference)
    if reference:
        body = body.replace('$ptascii("10bc")', '$ptascii("10bcde")')
        body = body.replace('$ptascii("bc")', '$ptascii("bcde")')
        body = body.replace('$ptascii("de")', '$ptascii("")')
        old = '$compiled_identity_value(S_capture,porigin_inner_suffix) = (PSTRING ($ptascii("bcde")))'
        assert body.count(old) == 1
        body = body.replace(old, '$compiled_identity_value(S_capture,porigin_inner_suffix) = eps')
    definitions = lines(r'''
expression_inner_suffix = NExprBinaryOpConcat expression_bc_left expression_bc_right metadata_inner_suffix
expression_suffix = NExprBinaryOpConcat expression_de_left expression_de_right metadata_suffix
expression_bc_left = NScalarString (BYTES text_b) metadata_b
expression_de_left = NScalarString (BYTES text_d) metadata_d
expression_de_right = NScalarString (BYTES text_e) metadata_e
$base64(text_b) = $ptascii("b")
''')
    if reference:
        definitions += lines(r'''
expression_bc_right = NExprBinaryOpConcat expression_c expression_tail metadata_nested
expression_c = NScalarString (BYTES text_c) metadata_c
expression_tail = NScalarString (BYTES text_tail) metadata_tail
$base64(text_c) = $ptascii("c")
$base64(text_tail) = $ptascii("de")
$base64(text_d) = eps
$base64(text_e) = eps
''')
    else:
        definitions += lines(r'''
expression_bc_right = NScalarString (BYTES text_c) metadata_c
$base64(text_c) = $ptascii("c")
$base64(text_d) = $ptascii("d")
$base64(text_e) = $ptascii("e")
''')
    old = '  -- if expression_inner_suffix = NScalarString (BYTES text_inner_suffix) metadata_inner_suffix\n'
    assert body.count(old) == 1
    body = body.replace(old, ''.join('  -- if ' + line + '\n' for line in definitions))
    for prefix in ('expression_suffix = NScalarString ', '$base64(text_inner_suffix)', '$base64(text_suffix)'):
        body = '\n'.join(line for line in body.split('\n') if not line.startswith('  -- if ' + prefix))
    body = body.replace('NScalarString (BYTES text_inner_suffix) eps',
                        'NExprBinaryOpConcat expression_bc_left expression_bc_right eps')
    body = body.replace('NScalarString (BYTES text_suffix) eps',
                        'NExprBinaryOpConcat expression_de_left expression_de_right eps')
    checks = lines(r'''
$string_read_literal_bytes(expression_inner_suffix) = ($ptascii("bc"))
$string_read_literal_bytes(expression_suffix) = ($ptascii("de"))
$string_read_runtime_value(S_capture,porigin_inner_suffix) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("bc")))
$string_read_runtime_value(S_capture,porigin_suffix) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("de")))
$origin_child((porigin_inner_suffix),[PCFIELD 0]) = (porigin_bc_left)
$origin_child((porigin_inner_suffix),[PCFIELD 1]) = (porigin_bc_right)
$origin_child((porigin_suffix),[PCFIELD 0]) = (porigin_de_left)
$origin_child((porigin_suffix),[PCFIELD 1]) = (porigin_de_right)
''')
    if reference:
        checks = [line.replace('$ptascii("bc")', '$ptascii("bcde")').replace('$ptascii("de")', '$ptascii("")') for line in checks]
        checks += lines(r'''
$origin_child((porigin_bc_right),[PCFIELD 0]) = (porigin_c)
$origin_child((porigin_bc_right),[PCFIELD 1]) = (porigin_tail)
$string_same(pvalue_inner,pvalue_base) = (false)
S_prefix_empty = S_capture[.STRINGDATA = S_capture.STRINGDATA[0:3]]
$string_concat(S_prefix_empty,pvalue_inner,PSTRING_CARRIER INTERNED_STRING eps,false,true) = S_prefix_empty[.STRINGDATA = S_capture.STRINGDATA][.RESULT = KNOWN pvalue_base]
$string_concat(S_prefix_empty,pvalue_inner,PSTRING_CARRIER INTERNED_STRING eps,false,false) = S_prefix_empty[.RESULT = KNOWN pvalue_inner]
''')
    pruned = [('bc_left', 'expression_bc_left'), ('bc_right', 'expression_bc_right'),
              ('de_left', 'expression_de_left'), ('de_right', 'expression_de_right')]
    if reference:
        pruned += [('c', 'expression_c'), ('tail', 'expression_tail')]
    for node, expression in pruned:
        checks += [f'porigin_{node} = PORIGIN n_unit pcpath_{node}',
                   f'$origin_node(S_capture.SOURCES,porigin_{node}) = ({expression})',
                   f'$code_expression(pcode.EXPRESSIONS,pcpath_{node}) = eps',
                   f'$compiled_read(S_capture,porigin_{node}) = eps',
                   f'$compiled_identity_value(S_capture,porigin_{node}) = eps',
                   f'$constant_at(ppool.CONSTANTS,pcpath_{node}) = eps',
                   f'$compiled_precision(S_capture,(porigin_{node})) = (14)']
    marker = '  -- PhpStep: S_capture ~> S_dispatch\n'
    assert body.count(marker) == 1
    body = body.replace(marker, ''.join('  -- if ' + line + '\n' for line in checks) + marker)
    derived = []
    for node, expression in pruned:
        shadow = ('NExprBinaryOpConcat expression_c expression_tail eps'
                  if reference and node == 'bc_right'
                  else f'NScalarString (BYTES text_{dict(bc_left="b",bc_right="c",de_left="d",de_right="e",c="c",tail="tail")[node]}) eps')
        derived += [f'S_shadow_tree_{node} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{node} ({shadow})) :: pcunit.OCCURRENCES]]]',
                    f'~$string_read_allocated_base(S_shadow_tree_{node},porigin_base,pvalue_base)',
                    f'$string_read_plan(S_shadow_tree_{node}) = eps']
    derived += lines(r'''
S_pruned_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_bc_left 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_pruned_precision,porigin_base,pvalue_base)
$string_read_raw_capture(S_pruned_precision,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
$string_read_literal_bytes(expression_integer) = eps
$string_read_literal_bytes(NExprBinaryOpConcat expression_integer expression_de_left metadata_inner_suffix) = eps
''')
    body += ''.join('  -- if ' + line + '\n' for line in derived)
    main = body.split('def $main() = true\n', 1)[1]
    count = len(main.splitlines())
    derived_count = len(main[main.index('  -- if S_later ='):].splitlines())
    assert 'text_inner_suffix' not in main and 'text_suffix' not in main
    return body, count, derived_count


def render_reference(program, filename_b64):
    return render(program, filename_b64, reference=True)
