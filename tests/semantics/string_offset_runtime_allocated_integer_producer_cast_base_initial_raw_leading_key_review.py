"""Quiet integer VALUE and full child SOURCE authenticate allocated string casts."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_literal_concat_chain_base_initial_raw_leading_key_review import render as render_chain


def render(program, filename_b64, reference=False):
    body, _, _ = render_chain(program, filename_b64, reference=reference)
    unary = 'Minus' if reference else 'Plus'
    value = 'PINT $(-10)' if reference else 'PINT 10'
    if reference:
        for old in ('10bcde', '10bc', '10'):
            body = body.replace('$ptascii("' + old + '")', '$ptascii("-' + old + '")')
        body = body.replace('PINT 10', value)
        body = body.replace('([99])', '([98])').replace('([100])', '([99])')
        body = body.replace('R:c;K:4;', 'R:b;K:4;')
    old = 'expression_integer = NScalarInt (INTEGER 10) metadata_integer'
    assert body.count(old) == 1
    body = body.replace(old, f'expression_integer = NExprUnary{unary} expression_atom metadata_integer\n'
                        '  -- if expression_atom = NScalarInt (INTEGER 10) metadata_atom')
    body = body.replace('NScalarInt (INTEGER 10) eps',
                        f'NExprUnary{unary} expression_atom eps')
    checks = lines(r'''
$origin_child((porigin_integer),[PCFIELD 0]) = (porigin_atom)
porigin_atom = PORIGIN n_unit pcpath_atom
$origin_node(S_capture.SOURCES,porigin_atom) = (expression_atom)
$compiled_read(S_capture,porigin_atom) = (PINT 10)
$compiled_identity_value(S_capture,porigin_atom) = (PINT 10)
$compiled_precision(S_capture,(porigin_atom)) = (14)
$code_expression(pcode.EXPRESSIONS,pcpath_atom) = ((z_atom,true))
$(z_atom > 0)
$origin_child((pkeyread.SITE),[PCFIELD 1]) = (porigin_key)
$string_read_runtime_value(S_capture,porigin_key) = eps
''') + [f'$string_read_runtime_value(S_capture,porigin_integer) = ({value})']
    marker = '  -- PhpStep: S_capture ~> S_dispatch\n'
    assert body.count(marker) == 1
    body = body.replace(marker, ''.join('  -- if ' + check + '\n' for check in checks) + marker)
    derived = lines(r'''
S_atom_shadow = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_atom (NScalarInt (INTEGER 10) eps)) :: pcunit.OCCURRENCES]]]
''') + [f'$string_read_runtime_value(S_atom_shadow,porigin_integer) = ({value})']
    derived += lines(r'''
~$string_read_allocated_value(S_atom_shadow,porigin_cast,pvalue_cast)
~$string_read_allocated_base(S_atom_shadow,porigin_base,pvalue_base)
$string_read_raw_capture(S_atom_shadow,poperand,pvalue_base) = eps
$string_read_plan(S_atom_shadow) = eps
S_atom_missing = S_capture[.SOURCES = [pcunit[.OCCURRENCES = [(PCOCCURRENCE pcpath_cast (NExprCastString expression_integer metadata_cast)),(PCOCCURRENCE pcpath_integer expression_integer)]]]]
''') + [f'$string_read_runtime_value(S_atom_missing,porigin_integer) = ({value})']
    derived += lines(r'''
~$string_read_allocated_value(S_atom_missing,porigin_cast,pvalue_cast)
S_atom_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_atom 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_atom_precision,porigin_base,pvalue_base)
$string_read_raw_capture(S_atom_precision,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
S_atom_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_atom (PINT 123)) :: ppool.CONSTANTS]]]
''') + [f'$string_read_runtime_value(S_atom_pool,porigin_integer) = ({value})']
    derived += lines(r'''
$string_read_allocated_base(S_atom_pool,porigin_base,pvalue_base)
S_integer_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_integer (PINT 123)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_integer_pool,porigin_integer) = eps
~$string_read_allocated_base(S_integer_pool,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in derived)
    main = body.split('def $main() = true\n', 1)[1]
    derived_start = main.index('  -- if S_later =')
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())


def render_reference(program, filename_b64):
    return render(program, filename_b64, reference=True)
