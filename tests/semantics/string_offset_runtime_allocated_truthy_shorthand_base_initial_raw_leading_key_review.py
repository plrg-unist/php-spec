"""Truthy allocated shorthand conditions preserve their selected headers."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_literal_concat_chain_base_initial_raw_leading_key_review import render as render_chain
from string_offset_runtime_allocated_float_producer_cast_base_initial_raw_leading_key_review import render as render_float


def render(program, filename_b64, reference=False):
    renderer = render_float if reference else render_chain
    body, _, _ = renderer(program, filename_b64, reference=reference)
    root = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary expression_chain ABSENT expression_skipped metadata_base)
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_chain)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_absent)
$origin_node(S_capture.SOURCES,porigin_absent) = eps
$compiled_read(S_capture,porigin_absent) = eps
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_skipped)
$origin_node(S_capture.SOURCES,porigin_skipped) = (expression_skipped)
$compiled_read(S_capture,porigin_skipped) = eps
''')
    if reference:
        start = body.index('  -- if $origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce')
        end = body.index('  -- if $lookup(S_capture.ENV,$ptascii("alias"))', start)
        body = body[:start] + ''.join('  -- if ' + check + '\n' for check in root) + body[end:]
    else:
        old = 'porigin_chain = porigin_base'
        assert body.count(old) == 1
        body = body.replace(old, '\n  -- if '.join(root))
    checks = lines(r'''
porigin_absent = PORIGIN n_unit pcpath_absent
porigin_skipped = PORIGIN n_unit pcpath_skipped
expression_skipped = NExprTernary expression_skipped_condition expression_skipped_true expression_skipped_false metadata_skipped
expression_skipped_condition = NExprCastInt expression_skipped_atom metadata_skipped_condition
expression_skipped_atom = NScalarInt (INTEGER 1) metadata_skipped_atom
expression_skipped_true = NScalarString (BYTES text_skipped_true) metadata_skipped_true
expression_skipped_false = NScalarString (BYTES text_skipped_false) metadata_skipped_false
$base64(text_skipped_true) = $ptascii("XYZ")
$base64(text_skipped_false) = $ptascii("abc")
$origin_child((porigin_skipped),[PCFIELD 0]) = (porigin_skipped_condition)
$origin_child((porigin_skipped),[PCFIELD 1]) = (porigin_skipped_true)
$origin_child((porigin_skipped),[PCFIELD 2]) = (porigin_skipped_false)
$origin_child((porigin_skipped_condition),[PCFIELD 0]) = (porigin_skipped_atom)
$origin_node(S_capture.SOURCES,porigin_skipped_condition) = (expression_skipped_condition)
$origin_node(S_capture.SOURCES,porigin_skipped_true) = (expression_skipped_true)
$origin_node(S_capture.SOURCES,porigin_skipped_false) = (expression_skipped_false)
$origin_node(S_capture.SOURCES,porigin_skipped_atom) = (expression_skipped_atom)
porigin_skipped_atom = PORIGIN n_unit pcpath_skipped_atom
$code_expression(pcode.EXPRESSIONS,pcpath_base) = ((z_base,false))
$(z_base > 0)
$compiled_read(S_capture,porigin_base) = eps
$string_read_allocated_base(S_capture,porigin_chain,pvalue_base)
$truth(S_capture,pvalue_base)
$truth_value(S_capture,pvalue_base,z_base) = S_capture[.RESULT = KNOWN (PBOOL true)]
~$string_read_allocated_value(S_capture,porigin_base,pvalue_base)
$string_read_runtime_value(S_capture,porigin_base) = eps
''')
    marker = '  -- PhpStep: S_capture ~> S_dispatch\n'
    assert body.count(marker) == 1
    body = body.replace(marker, ''.join('  -- if ' + check + '\n' for check in checks) + marker)
    derived = []
    if not reference:
        for label, line, flag in (('line', '0', 'false'), ('folded', 'z_base', 'true')):
            state = f'S_short_root_{label}'
            derived += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_base {line} {flag}) :: pcode.EXPRESSIONS]]]',
                        f'~$string_read_allocated_base({state},porigin_base,pvalue_base)', f'$string_read_plan({state}) = eps']
    derived += lines(r'''
S_skipped_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_skipped_atom (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_skipped_source,porigin_chain,pvalue_base)
~$string_read_allocated_base(S_skipped_source,porigin_base,pvalue_base)
$string_read_plan(S_skipped_source) = eps
S_skipped_noise = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_skipped 0 true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_skipped (PINT 77)) :: (PCCPRECISION pcpath_skipped 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_skipped_noise,porigin_base,pvalue_base)
$string_read_plan(S_skipped_noise) = (pstringread)
S_absent_noise = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_absent 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_absent (PINT 77)) :: (PCCPRECISION pcpath_absent 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_absent_noise,porigin_base,pvalue_base)
$string_read_plan(S_absent_noise) = (pstringread)
''')
    body += ''.join('  -- if ' + check + '\n' for check in derived)
    main = body.split('def $main() = true\n', 1)[1]
    derived_start = main.index('  -- if S_later =')
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())
