"""Independent typed integer-cast provenance and saved-reference checks."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_literal_concat_chain_base_initial_raw_leading_key_peer_review import render as render_reference


def render(program, filename_b64):
    body, _, _ = render_reference(program, filename_b64)
    for old, new in (('10bcde', '-10bcde'), ('10bc', '-10bc'), ('10', '-10')):
        body = body.replace('$ptascii("' + old + '")', '$ptascii("' + new + '")')
    body = body.replace('PINT 10', 'PINT $(-10)')
    body = body.replace('([99])', '([98])').replace('([100])', '([99])')
    body = body.replace(';R:c;K:4;A:', ';R:b;K:4;A:')
    old = '  -- if expression_atom = NScalarInt (INTEGER 10) metadata_atom\n'
    assert body.count(old) == 1
    body = body.replace(old, ''.join('  -- if ' + check + '\n' for check in lines(r'''
expression_atom = NExprUnaryMinus expression_operand metadata_atom
expression_operand = NScalarInt (INTEGER 10) metadata_operand
''')))
    old = 'NScalarInt (INTEGER 10) eps'
    assert body.count(old) == 1
    body = body.replace(old, 'NExprUnaryMinus expression_operand eps')
    checks = lines(r'''
$origin_child((porigin_atom),[PCFIELD 0]) = (porigin_operand)
porigin_operand = PORIGIN n_unit pcpath_operand
$origin_node(S_capture.SOURCES,porigin_operand) = (expression_operand)
$code_expression(pcode.EXPRESSIONS,pcpath_operand) = ((z_operand,true))
$(z_operand > 0)
$compiled_read(S_capture,porigin_operand) = (PINT 10)
$compiled_identity_value(S_capture,porigin_operand) = (PINT 10)
$constant_at(ppool.CONSTANTS,pcpath_operand) = (PINT 10)
$compiled_precision(S_capture,(porigin_operand)) = (14)
$string_read_runtime_value(S_capture,porigin_atom) = (PINT $(-10))
$pcwalk([PCOCCURRENCE pcpath_atom expression_atom]) = [PCOCCURRENCE pcpath_atom expression_atom,PCOCCURRENCE pcpath_operand expression_operand]
$origin_child((pkeyread.SITE),[PCFIELD 1]) = (porigin_key)
$string_read_runtime_value(S_capture,porigin_key) = eps
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    derived = lines(r'''
S_key_integer = S_capture[.STORE[n_old] = DEFINED (PINT 10)]
$heap_valid($heap_graph(S_key_integer))
$string_read_runtime_value(S_key_integer,porigin_key) = eps
S_operand_shadow = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_operand (NScalarInt (INTEGER 10) eps)) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_operand_shadow,porigin_atom) = (PINT $(-10))
~$string_read_allocated_value(S_operand_shadow,porigin_cast,pvalue_cast)
~$string_read_allocated_base(S_operand_shadow,porigin_base,pvalue_base)
$string_read_raw_capture(S_operand_shadow,poperand,pvalue_base) = eps
$string_read_plan(S_operand_shadow) = eps
S_operand_unused = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_operand (PSTRING ($ptascii("unneeded")))) :: (PCCPRECISION pcpath_operand 17) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_operand_unused,porigin_atom) = (PINT $(-10))
$string_read_allocated_base(S_operand_unused,porigin_base,pvalue_base)
$string_read_raw_capture(S_operand_unused,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
expression_float = NScalarFloat (FLOAT "c024000000000000") metadata_atom
expression_float_cast = NExprCastString expression_float metadata_cast
expression_float_inner = NExprBinaryOpConcat expression_float_cast expression_bc metadata_inner
expression_float_chain = NExprBinaryOpConcat expression_float_inner expression_de metadata_chain
expression_float_base = NExprBinaryOpCoalesce expression_float_chain expression_right metadata_base
pcoccurrence_float* = $pcwalk([PCOCCURRENCE pcpath_base expression_float_base])
n_float = $hex_bits("c024000000000000",0)
S_float = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_float* ++ pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PFLOAT n_float)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_float,porigin_atom) = (PFLOAT n_float)
$compiled_precision(S_float,(porigin_atom)) = (14)
~$string_read_allocated_value(S_float,porigin_cast,pvalue_cast)
~$string_read_allocated_base(S_float,porigin_base,pvalue_base)
$string_read_raw_capture(S_float,poperand,pvalue_base) = eps
$string_read_plan(S_float) = eps
''')
    body += ''.join('  -- if ' + check + '\n' for check in derived)
    main = body.split('def $main() = true\n', 1)[1]
    assert program in body
    derived_start = main.index('  -- if S_unmarked =')
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())
