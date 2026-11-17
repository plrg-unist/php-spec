"""An outer STRING cast preserves a certified nonnull COALESCE child."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_literal_concat_chain_base_initial_raw_leading_key_review import render as render_chain
from string_offset_runtime_allocated_float_producer_cast_base_initial_raw_leading_key_review import render as render_float


def render(program, filename_b64, reference=False):
    renderer = render_float if reference else render_chain
    body, _, _ = renderer(program, filename_b64, reference=reference)
    root = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprCastString expression_coalesce metadata_base)
expression_coalesce = NExprBinaryOpCoalesce expression_chain expression_skipped metadata_coalesce
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_coalesce)
$origin_node(S_capture.SOURCES,porigin_coalesce) = (expression_coalesce)
''')
    if reference:
        old = '$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_chain expression_skipped metadata_base)'
        assert body.count(old) == 1
        body = body.replace(old, '\n  -- if '.join(root))
        for index, child in [(0, 'chain'), (1, 'skipped')]:
            old = f'$origin_child((porigin_base),[PCFIELD {index}]) = (porigin_{child})'
            assert body.count(old) == 1
            body = body.replace(old, old.replace('(porigin_base)', '(porigin_coalesce)'))
    else:
        root += lines(r'''
$origin_child((porigin_coalesce),[PCFIELD 0]) = (porigin_chain)
$origin_child((porigin_coalesce),[PCFIELD 1]) = (porigin_skipped)
$origin_node(S_capture.SOURCES,porigin_skipped) = (expression_skipped)
$compiled_read(S_capture,porigin_skipped) = eps
''')
        old = 'porigin_chain = porigin_base'
        assert body.count(old) == 1
        body = body.replace(old, '\n  -- if '.join(root))
    checks = lines(r'''
porigin_coalesce = PORIGIN n_unit pcpath_coalesce
porigin_skipped = PORIGIN n_unit pcpath_skipped
$string_read_literal_bytes(expression_skipped) = eps
$string_read_allocated_base(S_capture,porigin_coalesce,pvalue_base)
~$string_read_allocated_value(S_capture,porigin_coalesce,pvalue_base)
$string_read_allocated_value(S_capture,porigin_base,pvalue_base)
|S_capture.STRINGDATA| = 4
''')
    for node in ['coalesce'] + ([] if reference else ['base']):
        checks += [f'$compiled_precision(S_capture,(porigin_{node})) = (14)',
                   f'$code_expression(pcode.EXPRESSIONS,pcpath_{node}) = ((z_{node},false))',
                   f'$(z_{node} > 0)', f'$compiled_read(S_capture,porigin_{node}) = eps',
                   f'$compiled_identity_value(S_capture,porigin_{node}) = eps']
    checks += ['$cast_apply(S_capture,CASTSTRING,pvalue_base,z_base) = S_capture[.RESULT = KNOWN pvalue_base]']
    marker = '  -- PhpStep: S_capture ~> S_dispatch\n'
    assert body.count(marker) == 1
    body = body.replace(marker, ''.join('  -- if ' + check + '\n' for check in checks) + marker)
    derived = lines(r'''
$origin_child((porigin_skipped),[PCFIELD 0]) = (porigin_skipped_condition)
porigin_skipped_condition = PORIGIN n_unit pcpath_skipped_condition
$origin_node(S_capture.SOURCES,porigin_skipped_condition) = (NExprCastInt expression_skipped_atom metadata_skipped_condition)
S_skipped_descendant = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_skipped_condition (NExprCastInt expression_skipped_atom eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_skipped_descendant,porigin_coalesce,pvalue_base)
~$string_read_allocated_base(S_skipped_descendant,porigin_base,pvalue_base)
$string_read_plan(S_skipped_descendant) = eps
S_coalesce_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_coalesce (PSTRING ($ptascii("unused")))) :: ppool.CONSTANTS]]]
$compiled_read(S_coalesce_pool,porigin_coalesce) = eps
$string_read_allocated_base(S_coalesce_pool,porigin_base,pvalue_base)
$string_read_plan(S_coalesce_pool) = (pstringread)
S_coalesce_shadow = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_coalesce (NExprBinaryOpCoalesce expression_chain expression_skipped eps)) :: pcunit.OCCURRENCES]]]
~$string_read_allocated_base(S_coalesce_shadow,porigin_base,pvalue_base)
$string_read_plan(S_coalesce_shadow) = eps
S_skipped_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_skipped 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_skipped_precision,porigin_base,pvalue_base)
$string_read_plan(S_skipped_precision) = (pstringread)
''')
    for node in ['coalesce'] + ([] if reference else ['base']):
        for label, flag, line in [('line', 'false', '0'), ('folded', 'true', f'z_{node}')]:
            state = f'S_{node}_{label}'
            derived += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} {line} {flag}) :: pcode.EXPRESSIONS]]]',
                        f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                        f'$string_read_plan({state}) = eps']
    derived += lines(r'''
S_coalesce_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_coalesce 17) :: ppool.CONSTANTS]]]
~$string_read_allocated_base(S_coalesce_precision,porigin_base,pvalue_base)
$string_read_plan(S_coalesce_precision) = eps
expression_null_coalesce = NExprBinaryOpCoalesce (NExprConstFetch (NName (BYTES "bnVsbA==") eps) eps) expression_chain metadata_coalesce
expression_null_base = NExprCastString expression_null_coalesce metadata_base
pcoccurrence_null* = $pcwalk([PCOCCURRENCE pcpath_base expression_null_base])
S_null_selected = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_null* ++ pcunit.OCCURRENCES]]]
~$string_read_allocated_base(S_null_selected,porigin_coalesce,pvalue_base)
~$string_read_allocated_base(S_null_selected,porigin_base,pvalue_base)
$string_read_plan(S_null_selected) = eps
''')
    body += ''.join('  -- if ' + check + '\n' for check in derived)
    main = body.split('def $main() = true\n', 1)[1]
    derived_start = main.index('  -- if S_later =')
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())


def render_reference(program, filename_b64):
    return render(program, filename_b64, reference=True)
