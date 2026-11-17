"""Independent saved-reference checks for folded string-only CONCAT suffixes."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_literal_concat_chain_base_initial_raw_leading_key_peer_review import render as render_reference


def render(program, filename_b64):
    body, _, _ = render_reference(program, filename_b64)
    body = body.replace('$ptascii("10bc")', '$ptascii("10bcde")')
    body = body.replace('$ptascii("bc")', '$ptascii("bcde")')
    body = body.replace('$ptascii("de")', '$ptascii("")')
    definitions = lines(r'''
expression_bc = NExprBinaryOpConcat expression_b expression_nested metadata_bc
expression_nested = NExprBinaryOpConcat expression_c expression_tail metadata_nested
expression_de = NExprBinaryOpConcat expression_empty_left expression_empty_right metadata_de
expression_b = NScalarString (BYTES text_b) metadata_b
expression_c = NScalarString (BYTES text_c) metadata_c
expression_tail = NScalarString (BYTES text_tail) metadata_tail
expression_empty_left = NScalarString (BYTES text_empty_left) metadata_empty_left
expression_empty_right = NScalarString (BYTES text_empty_right) metadata_empty_right
$base64(text_b) = $ptascii("b")
$base64(text_c) = $ptascii("c")
$base64(text_tail) = $ptascii("de")
$base64(text_empty_left) = eps
$base64(text_empty_right) = eps
''')
    old = '  -- if expression_bc = NScalarString (BYTES text_bc) metadata_bc\n'
    assert body.count(old) == 1
    body = body.replace(old, ''.join('  -- if ' + check + '\n' for check in definitions))
    for prefix in ('expression_de = NScalarString ', '$base64(text_bc)', '$base64(text_de)'):
        body = '\n'.join(line for line in body.split('\n')
                         if not line.startswith('  -- if ' + prefix))
    body = body.replace('NScalarString (BYTES text_bc) eps',
                        'NExprBinaryOpConcat expression_b expression_nested eps')
    body = body.replace('NScalarString (BYTES text_de) eps',
                        'NExprBinaryOpConcat expression_empty_left expression_empty_right eps')
    old = '$compiled_identity_value(S_capture,porigin_bc) = (PSTRING ($ptascii("bcde")))'
    assert body.count(old) == 1
    body = body.replace(old, '$compiled_identity_value(S_capture,porigin_bc) = eps')
    checks = lines(r'''
$string_read_literal_bytes(expression_bc) = ($ptascii("bcde"))
$string_read_literal_bytes(expression_de) = (eps)
$string_read_runtime_value(S_capture,porigin_bc) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("bcde")))
$string_read_runtime_value(S_capture,porigin_de) = (PSTRING_CARRIER INTERNED_STRING eps)
$origin_child((porigin_bc),[PCFIELD 0]) = (porigin_b)
$origin_child((porigin_bc),[PCFIELD 1]) = (porigin_nested)
$origin_child((porigin_nested),[PCFIELD 0]) = (porigin_c)
$origin_child((porigin_nested),[PCFIELD 1]) = (porigin_tail)
$origin_child((porigin_de),[PCFIELD 0]) = (porigin_empty_left)
$origin_child((porigin_de),[PCFIELD 1]) = (porigin_empty_right)
$string_same(pvalue_inner,pvalue_base) = (false)
S_empty_prefix = S_capture[.STRINGDATA = S_capture.STRINGDATA[0:3]]
$string_concat(S_empty_prefix,pvalue_inner,PSTRING_CARRIER INTERNED_STRING eps,false,true) = S_empty_prefix[.STRINGDATA = S_capture.STRINGDATA][.RESULT = KNOWN pvalue_base]
$string_concat(S_empty_prefix,pvalue_inner,PSTRING_CARRIER INTERNED_STRING eps,false,false) = S_empty_prefix[.RESULT = KNOWN pvalue_inner]
~$string_read_allocated_value(S_capture,porigin_chain,pvalue_inner)
$string_read_literal_bytes(expression_atom) = eps
$string_read_folded_concat_bytes(expression_atom) = ($ptascii("10"))
$string_read_literal_bytes(NExprBinaryOpConcat expression_atom expression_empty_left metadata_bc) = eps
$string_read_folded_concat_bytes(NExprBinaryOpConcat expression_atom expression_empty_left metadata_bc) = ($ptascii("10"))
''')
    pruned = dict(b='expression_b', nested='expression_nested', c='expression_c',
                  tail='expression_tail', empty_left='expression_empty_left',
                  empty_right='expression_empty_right')
    for node, expression in pruned.items():
        checks += [f'porigin_{node} = PORIGIN n_unit pcpath_{node}',
                   f'$origin_node(S_capture.SOURCES,porigin_{node}) = ({expression})',
                   f'$code_expression(pcode.EXPRESSIONS,pcpath_{node}) = eps',
                   f'$compiled_read(S_capture,porigin_{node}) = eps',
                   f'$compiled_identity_value(S_capture,porigin_{node}) = eps',
                   f'$constant_at(ppool.CONSTANTS,pcpath_{node}) = eps',
                   f'$compiled_precision(S_capture,(porigin_{node})) = (14)']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    derived = []
    for node in pruned:
        shadow = ('NExprBinaryOpConcat expression_c expression_tail eps'
                  if node == 'nested' else
                  f'NScalarString (BYTES text_{node}) eps')
        derived += [f'S_fold_shadow_{node} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{node} ({shadow})) :: pcunit.OCCURRENCES]]]',
                    f'~$string_read_allocated_base(S_fold_shadow_{node},porigin_base,pvalue_base)',
                    f'$string_read_plan(S_fold_shadow_{node}) = eps']
    derived += lines(r'''
S_pruned_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_c 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_pruned_precision,porigin_base,pvalue_base)
$string_read_raw_capture(S_pruned_precision,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
''')
    body += ''.join('  -- if ' + check + '\n' for check in derived)
    main = body.split('def $main() = true\n', 1)[1]
    assert 'text_bc' not in main and 'text_de' not in main
    derived_start = main.index('  -- if S_unmarked =')
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())
