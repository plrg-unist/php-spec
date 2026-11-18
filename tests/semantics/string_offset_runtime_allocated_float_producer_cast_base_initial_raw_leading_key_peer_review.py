"""Independent finite FLOAT allocation, precision and saved-key checks."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_literal_concat_chain_base_initial_raw_leading_key_peer_review import render as render_reference


def render(program, filename_b64):
    body, _, _ = render_reference(program, filename_b64)
    for old, new in (("10bcde", "-10.5bcde"), ("10bc", "-10.5bc"), ("10", "-10.5")):
        body = body.replace('$ptascii("' + old + '")', '$ptascii("' + new + '")')
    body = body.replace("PINT 10", "PFLOAT 13845472629420457984")
    body = body.replace("([99])", "([46])").replace("([100])", "([53])")
    body = body.replace(";R:c;K:4;A:", ";R:.;K:4;A:")
    old = "expression_atom = NScalarInt (INTEGER 10) metadata_atom"
    assert body.count(old) == 1
    body = body.replace(old, "expression_atom = NExprUnaryMinus expression_operand metadata_atom")
    body = body.replace("NScalarInt (INTEGER 10) eps", "NExprUnaryMinus expression_operand eps")
    checks = lines(r'''
expression_operand = NScalarFloat (FLOAT "4025000000000000") metadata_operand
$origin_child((porigin_atom),[PCFIELD 0]) = (porigin_operand)
porigin_operand = PORIGIN n_unit pcpath_operand
$origin_node(S_capture.SOURCES,porigin_operand) = (expression_operand)
$compiled_read(S_capture,porigin_operand) = (PFLOAT 4622100592565682176)
$compiled_identity_value(S_capture,porigin_operand) = (PFLOAT 4622100592565682176)
$compiled_precision(S_capture,(porigin_operand)) = (14)
$code_expression(pcode.EXPRESSIONS,pcpath_operand) = ((z_operand,true))
$(z_operand > 0)
$precision_value(S_capture) = 14
$string_read_runtime_value(S_capture,porigin_atom) = (PFLOAT 13845472629420457984)
$pcwalk([PCOCCURRENCE pcpath_atom expression_atom]) = [PCOCCURRENCE pcpath_atom expression_atom,PCOCCURRENCE pcpath_operand expression_operand]
$number_text(NFLOAT 13845472629420457984,14) = ($ptascii("-10.5"),false)
$number_text(NFLOAT 13845472629420457984,17) = ($ptascii("-10.5"),false)
$origin_child((pkeyread.SITE),[PCFIELD 1]) = (porigin_key)
$string_read_runtime_value(S_capture,porigin_key) = eps
S_operand_shadow = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_operand (NScalarFloat (FLOAT "4025000000000000") eps)) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_operand_shadow,porigin_atom) = (PFLOAT 13845472629420457984)
~$string_read_allocated_value(S_operand_shadow,porigin_cast,pvalue_cast)
~$string_read_allocated_base(S_operand_shadow,porigin_base,pvalue_base)
$string_read_raw_capture(S_operand_shadow,poperand,pvalue_base) = eps
$string_read_plan(S_operand_shadow) = eps
S_operand_unused = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_operand (PSTRING ($ptascii("unused")))) :: (PCCPRECISION pcpath_operand 17) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_operand 0 false) :: pcode.EXPRESSIONS]]]
$string_read_runtime_value(S_operand_unused,porigin_atom) = (PFLOAT 13845472629420457984)
$string_read_allocated_base(S_operand_unused,porigin_base,pvalue_base)
$string_read_raw_capture(S_operand_unused,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
S_live_precision = S_capture[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]
$precision_value(S_live_precision) = 17
~$string_read_allocated_value(S_live_precision,porigin_cast,pvalue_cast)
~$string_read_allocated_base(S_live_precision,porigin_base,pvalue_base)
$string_read_raw_capture(S_live_precision,poperand,pvalue_base) = eps
$string_read_plan(S_live_precision) = eps
S_post_precision = S[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]
$string_read_raw_saved(S_post_precision,pstringread) = eps
~$string_read_source(S_post_precision,pstringread)
S_matched_precision = S_live_precision[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_cast 17) :: (PCCPRECISION pcpath_atom 17) :: ppool.CONSTANTS]]]
$string_read_allocated_value(S_matched_precision,porigin_cast,pvalue_cast)
S_wrong_bits = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PFLOAT 4622100592565682176)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_wrong_bits,porigin_atom) = eps
~$string_read_allocated_value(S_wrong_bits,porigin_cast,pvalue_cast)
S_abrupt = S_capture[.COMPLETION = UNSUPPORTED "control"]
~$string_read_allocated_value(S_abrupt,porigin_cast,pvalue_cast)
''')
    # These fresh states also check the four affected historical integer-peer
    # expectations, without executing that earlier source or its 453 checks.
    for name, bits, word in (("promoted", "c024000000000000", "-10"),
                             ("digit", "4014000000000000", "5"),
                             ("infinity", "7ff0000000000000", "INF"),
                             ("nan", "7ff8000000000000", "NAN")):
        checks += [
            f'expression_{name} = NScalarFloat (FLOAT "{bits}") metadata_atom',
            f'expression_{name}_cast = NExprCastString expression_{name} metadata_cast',
            f'expression_{name}_inner = NExprBinaryOpConcat expression_{name}_cast expression_bc metadata_inner',
            f'expression_{name}_chain = NExprBinaryOpConcat expression_{name}_inner expression_de metadata_chain',
            f'expression_{name}_base = NExprBinaryOpCoalesce expression_{name}_chain expression_right metadata_base',
            f'pcoccurrence_{name}* = $pcwalk([PCOCCURRENCE pcpath_base expression_{name}_base])',
            f'n_{name} = $hex_bits("{bits}",0)',
            f'pvalue_{name}_cast = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("{word}"))',
            f'pvalue_{name}_base = PSTRING_CARRIER (REQUEST_STRING 3) ($ptascii("{word}bcde"))',
            f'S_{name} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_{name}* ++ pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PFLOAT n_{name})) :: ppool.CONSTANTS]]][.STRINGDATA = [$ptascii("512"),$ptascii("{word}"),$ptascii("{word}bc"),$ptascii("{word}bcde")]][.RESULT = KNOWN pvalue_{name}_base]',
            f'$compiled_read(S_{name},porigin_atom) = (PFLOAT n_{name})',
            f'$compiled_identity_value(S_{name},porigin_atom) = ' + ('eps' if name == "nan" else f'(PFLOAT n_{name})'),
            f'$string_carrier_valid(S_{name},pvalue_{name}_cast)',
            f'$string_carrier_valid(S_{name},pvalue_{name}_base)']
        if name in ("promoted", "digit", "infinity"):
            checks += [
                f'$string_read_runtime_value(S_{name},porigin_atom) = (PFLOAT n_{name})',
                f'$string_read_allocated_value(S_{name},porigin_cast,pvalue_{name}_cast)',
                f'$string_read_allocated_base(S_{name},porigin_base,pvalue_{name}_base)',
                f'$string_read_raw_capture(S_{name},poperand,pvalue_{name}_base) = ((pvalue_raw,pstringread.KEYCELL))',
                f'$string_read_plan(S_{name}) = (pstringread[.READ.BASE = pvalue_{name}_base][.READ.OWNERS = BASE_VALUE (KNOWN pvalue_{name}_base)])']
        else:
            checks += [
                f'~$string_read_allocated_value(S_{name},porigin_cast,pvalue_{name}_cast)',
                f'~$string_read_allocated_base(S_{name},porigin_base,pvalue_{name}_base)',
                f'$string_read_raw_capture(S_{name},poperand,pvalue_{name}_base) = eps',
                f'$string_read_plan(S_{name}) = eps']
    checks += lines(r'''
$string_read_runtime_value(S_infinity,porigin_atom) = (PFLOAT n_infinity)
$string_read_runtime_value(S_nan,porigin_atom) = eps
$float_decode(n_infinity) = INFINITE 0
$float_decode(n_nan) = NOTNUMBER n_nan
S_digit_prefix = S_digit[.STRINGDATA = [$ptascii("512")]]
$cast_apply(S_digit_prefix,CASTSTRING,PFLOAT n_digit,18) = S_digit_prefix[.STRINGDATA = [$ptascii("512"),$ptascii("5")]][.RESULT = KNOWN pvalue_digit_cast]
$cast_apply(S_digit_prefix,CASTSTRING,PINT 5,18) = S_digit_prefix[.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("5")))]
$string_same(pvalue_digit_cast,PSTRING_CARRIER INTERNED_STRING ($ptascii("5"))) = (false)
~$string_read_allocated_value(S_digit,porigin_cast,PSTRING_CARRIER INTERNED_STRING ($ptascii("5")))
expression_digit_integer = NScalarInt (INTEGER 5) metadata_atom
expression_digit_integer_cast = NExprCastString expression_digit_integer metadata_cast
expression_digit_integer_inner = NExprBinaryOpConcat expression_digit_integer_cast expression_bc metadata_inner
expression_digit_integer_chain = NExprBinaryOpConcat expression_digit_integer_inner expression_de metadata_chain
expression_digit_integer_base = NExprBinaryOpCoalesce expression_digit_integer_chain expression_right metadata_base
pcoccurrence_digit_integer* = $pcwalk([PCOCCURRENCE pcpath_base expression_digit_integer_base])
S_digit_integer = S_digit[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_digit_integer* ++ pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PINT 5)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_digit_integer,porigin_atom) = (PINT 5)
~$string_read_allocated_value(S_digit_integer,porigin_cast,pvalue_digit_cast)
''')
    body += "".join("  -- if " + check + "\n" for check in checks)
    main = body.split("def $main() = true\n", 1)[1]
    assert program in body
    derived_start = main.index("  -- if S_unmarked =")
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())
