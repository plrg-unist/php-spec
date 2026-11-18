"""Nonnull COALESCE preserves certified composite-left allocated headers."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_direct_allocated_string_base_initial_raw_leading_key_review import render as render_direct
from string_offset_runtime_allocated_truthy_shorthand_base_initial_raw_leading_key_review import render as render_truthy


def render(program, filename_b64, reference=False):
    if reference:
        body, _, _ = render_truthy(program, filename_b64, reference=True)
        body = body.replace('$origin_child((porigin_base),', '$origin_child((porigin_left),')
        old = '$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary expression_chain ABSENT expression_skipped metadata_base)'
        new = '\n  -- if '.join(lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_left expression_right metadata_base)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
expression_left = NExprTernary expression_chain ABSENT expression_skipped metadata_left
'''))
        assert body.count(old) == 1
        body = body.replace(old, new)
    else:
        body, _, _ = render_direct(program, filename_b64)
        body = body.replace('$ptascii("10")', '$ptascii("0")')
        body = body.replace('([49])', '([48])').replace('R:1;K:', 'R:0;K:')
        body = body.replace('PINT 10', 'PFLOAT 0')
        body = body.replace('expression_integer = NScalarInt (INTEGER 10) metadata_integer',
                            'expression_integer = NScalarFloat (FLOAT "0000000000000000") metadata_integer')
        old = 'porigin_cast = porigin_base\n  -- if expression_cast = expression_base'
        new = '\n  -- if '.join(lines(r'''
expression_base = NExprBinaryOpCoalesce expression_left expression_right metadata_base
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
expression_left = NExprTernary expression_condition expression_cast expression_left_skipped metadata_left
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_condition)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_cast)
$origin_child((porigin_left),[PCFIELD 2]) = (porigin_left_skipped)
$origin_node(S_capture.SOURCES,porigin_cast) = (expression_cast)
$origin_node(S_capture.SOURCES,porigin_left_skipped) = (expression_left_skipped)
'''))
        assert body.count(old) == 1
        body = body.replace(old, new)
    root = lines(r'''
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_right)
''')
    if reference:
        marker = '  -- if $origin_node(S_capture.SOURCES,porigin_base) = '
        start = body.index(marker)
        body = body[:start] + ''.join('  -- if ' + check + '\n' for check in root) + body[start:]
    else:
        late_root = '  -- if ' + new + '\n'
        assert body.count(late_root) == 1
        body = body.replace(late_root, '')
        marker = '  -- PhpStep: S_capture ~> S_dispatch\n'
        assert body.count(marker) == 1
        body = body.replace(marker, ''.join('  -- if ' + check + '\n' for check in root) + late_root + marker)
    checks = lines(r'''
porigin_left = PORIGIN n_unit pcpath_left
porigin_right = PORIGIN n_unit pcpath_right
$origin_node(S_capture.SOURCES,porigin_right) = (expression_right)
expression_right = NExprTernary expression_right_condition expression_right_true expression_right_false metadata_right
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_right_condition)
$origin_child((porigin_right_condition),[PCFIELD 0]) = (porigin_right_atom)
porigin_right_atom = PORIGIN n_unit pcpath_right_atom
$origin_node(S_capture.SOURCES,porigin_right_atom) = (NScalarInt (INTEGER 1) metadata_right_atom)
$string_read_literal_bytes(expression_right) = eps
$compiled_read(S_capture,porigin_right) = eps
$compiled_precision(S_capture,(porigin_left)) = (14)
$code_expression(pcode.EXPRESSIONS,pcpath_left) = ((z_left,false))
$(z_left > 0)
$compiled_read(S_capture,porigin_left) = eps
$string_read_allocated_base(S_capture,porigin_left,pvalue_base)
~$string_read_allocated_value(S_capture,porigin_left,pvalue_base)
$string_read_runtime_value(S_capture,porigin_left) = eps
~$string_read_allocated_value(S_capture,porigin_base,pvalue_base)
pvalue_base =/= PNULL
''')
    if not reference:
        checks += lines(r'''
expression_condition = NExprCastInt (NScalarInt (INTEGER 1) metadata_condition_atom) metadata_condition
$origin_node(S_capture.SOURCES,porigin_condition) = (expression_condition)
$string_read_runtime_value(S_capture,porigin_condition) = (PINT 1)
$string_read_allocated_value(S_capture,porigin_cast,pvalue_base)
~$truth(S_capture,pvalue_base)
$truth_value(S_capture,pvalue_base,z_base) = S_capture[.RESULT = KNOWN (PBOOL false)]
''')
    marker = '  -- PhpStep: S_capture ~> S_dispatch\n'
    assert body.count(marker) == 1
    body = body.replace(marker, ''.join('  -- if ' + check + '\n' for check in checks) + marker)
    derived = lines(r'''
S_right_shadow = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right (NExprTernary expression_right_condition expression_right_true expression_right_false eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_right_shadow,porigin_left,pvalue_base)
~$string_read_allocated_base(S_right_shadow,porigin_base,pvalue_base)
$string_read_plan(S_right_shadow) = eps
S_right_descendant = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right_atom (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_right_descendant,porigin_base,pvalue_base)
$string_read_plan(S_right_descendant) = (pstringread)
S_right_noise = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PINT 77)) :: (PCCPRECISION pcpath_right 17) :: ppool.CONSTANTS]]]
$compiled_read(S_right_noise,porigin_right) = eps
$string_read_allocated_base(S_right_noise,porigin_base,pvalue_base)
$string_read_plan(S_right_noise) = (pstringread)
S_right_read = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 0 true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right PNULL) :: ppool.CONSTANTS]]]
$compiled_read(S_right_read,porigin_right) = (PNULL)
$string_read_allocated_base(S_right_read,porigin_left,pvalue_base)
~$string_read_allocated_base(S_right_read,porigin_base,pvalue_base)
$string_read_plan(S_right_read) = eps
S_left_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_left 17) :: ppool.CONSTANTS]]]
~$string_read_allocated_base(S_left_precision,porigin_base,pvalue_base)
$string_read_plan(S_left_precision) = eps
''')
    if not reference:
        derived += lines(r'''
S_zero_live_precision = S_capture[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]
$precision_value(S_zero_live_precision) = 17
~$string_read_allocated_base(S_zero_live_precision,porigin_left,pvalue_base)
~$string_read_allocated_base(S_zero_live_precision,porigin_base,pvalue_base)
$string_read_plan(S_zero_live_precision) = eps
''')
    body += ''.join('  -- if ' + check + '\n' for check in derived)
    main = body.split('def $main() = true\n', 1)[1]
    derived_start = main.index('  -- if S_later =')
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())
