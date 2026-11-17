"""Quiet finite FLOAT casts retain their own allocation and precision proof."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_literal_concat_chain_base_initial_raw_leading_key_review import render as render_chain


def render(program, filename_b64, reference=False):
    body, _, _ = render_chain(program, filename_b64, reference=reference)
    formatted = "-10.5" if reference else "10.5"
    bits = 13845472629420457984 if reference else 4622100592565682176
    for old in ("10bcde", "10bc", "10"):
        body = body.replace('$ptascii("' + old + '")', '$ptascii("' + formatted + old[2:] + '")')
    body = body.replace("PINT 10", "PFLOAT " + str(bits))
    if reference:
        body = body.replace("([99])", "([46])").replace("([100])", "([53])")
        body = body.replace("R:c;K:4;", "R:.;K:4;")
    old = "expression_integer = NScalarInt (INTEGER 10) metadata_integer"
    assert body.count(old) == 1
    raw = 'NScalarFloat (FLOAT "4025000000000000")'
    replacement = ("NExprUnaryMinus expression_atom" if reference else raw)
    body = body.replace(old, "expression_integer = " + replacement + " metadata_integer")
    body = body.replace("NScalarInt (INTEGER 10) eps", replacement + " eps")
    checks = lines(r'''
$precision_value(S_capture) = 14
$float_decode(4622100592565682176) = FINITE 0 n_float_num n_float_den
$number_text(NFLOAT 4622100592565682176,14) = ($ptascii("10.5"),false)
$origin_child((pkeyread.SITE),[PCFIELD 1]) = (porigin_key)
$string_read_runtime_value(S_capture,porigin_key) = eps
''') + [f"$string_read_runtime_value(S_capture,porigin_integer) = (PFLOAT {bits})"]
    if reference:
        checks += lines(r'''
expression_atom = NScalarFloat (FLOAT "4025000000000000") metadata_atom
$origin_child((porigin_integer),[PCFIELD 0]) = (porigin_atom)
porigin_atom = PORIGIN n_unit pcpath_atom
$origin_node(S_capture.SOURCES,porigin_atom) = (expression_atom)
$compiled_read(S_capture,porigin_atom) = (PFLOAT 4622100592565682176)
$compiled_identity_value(S_capture,porigin_atom) = (PFLOAT 4622100592565682176)
$compiled_precision(S_capture,(porigin_atom)) = (14)
$code_expression(pcode.EXPRESSIONS,pcpath_atom) = ((z_atom,true))
$(z_atom > 0)
''')
    marker = "  -- PhpStep: S_capture ~> S_dispatch\n"
    assert body.count(marker) == 1
    body = body.replace(marker, "".join("  -- if " + check + "\n" for check in checks) + marker)
    derived = lines(r'''
S_live_precision = S_capture[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]
$precision_value(S_live_precision) = 17
~$string_read_allocated_value(S_live_precision,porigin_cast,pvalue_cast)
$string_read_plan(S_live_precision) = eps
S_post_precision = S[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]
$string_read_raw_saved(S_post_precision,pstringread) = eps
S_abrupt = S_capture[.COMPLETION = UNSUPPORTED "control"]
~$string_read_allocated_value(S_abrupt,porigin_cast,pvalue_cast)
''')
    if reference:
        derived += lines(r'''
S_atom_shadow = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_atom (NScalarFloat (FLOAT "4025000000000000") eps)) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_atom_shadow,porigin_integer) = (PFLOAT 13845472629420457984)
~$string_read_allocated_value(S_atom_shadow,porigin_cast,pvalue_cast)
~$string_read_allocated_base(S_atom_shadow,porigin_base,pvalue_base)
S_atom_unused = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PINT 123)) :: (PCCPRECISION pcpath_atom 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_atom_unused,porigin_base,pvalue_base)
''')
    body += "".join("  -- if " + check + "\n" for check in derived)
    main = body.split("def $main() = true\n", 1)[1]
    derived_start = main.index("  -- if S_later =")
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())
