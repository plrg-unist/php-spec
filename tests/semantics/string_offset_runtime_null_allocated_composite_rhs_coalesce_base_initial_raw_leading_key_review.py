"""Quiet NULL selection composes with an allocated composite RHS BASE."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_direct_allocated_string_base_initial_raw_leading_key_review import render as render_direct
from string_offset_runtime_allocated_truthy_shorthand_base_initial_raw_leading_key_review import render as render_truthy


def render(program, filename_b64, reference=False):
    root = lines(r'''
expression_base = NExprBinaryOpCoalesce expression_null expression_rhs metadata_base
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_null)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_rhs)
$origin_node(S_capture.SOURCES,porigin_null) = (expression_null)
$origin_node(S_capture.SOURCES,porigin_rhs) = (expression_rhs)
''')
    if reference:
        body, _, _ = render_truthy(program, filename_b64, reference=True)
        start = body.index('  -- if $origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary')
        end = body.index('  -- if $lookup(S_capture.ENV,$ptascii("alias"))', start)
        root = ['$origin_node(S_capture.SOURCES,porigin_base) = (expression_base)'] + root + lines(r'''
expression_rhs = NExprBinaryOpCoalesce expression_selected expression_rhs_skipped metadata_rhs
$origin_child((porigin_rhs),[PCFIELD 0]) = (porigin_selected)
$origin_child((porigin_rhs),[PCFIELD 1]) = (porigin_rhs_skipped)
$origin_node(S_capture.SOURCES,porigin_selected) = (expression_selected)
$origin_node(S_capture.SOURCES,porigin_rhs_skipped) = (expression_rhs_skipped)
expression_selected = NExprTernary expression_chain ABSENT expression_skipped metadata_selected
$origin_child((porigin_selected),[PCFIELD 0]) = (porigin_chain)
$origin_child((porigin_selected),[PCFIELD 1]) = (porigin_absent)
$origin_node(S_capture.SOURCES,porigin_absent) = eps
$compiled_read(S_capture,porigin_absent) = eps
$origin_child((porigin_selected),[PCFIELD 2]) = (porigin_skipped)
$origin_node(S_capture.SOURCES,porigin_skipped) = (expression_skipped)
$compiled_read(S_capture,porigin_skipped) = eps
''')
        body = body[:start] + ''.join('  -- if ' + check + '\n' for check in root) + body[end:]
    else:
        body, _, _ = render_direct(program, filename_b64)
        body = body.replace('$ptascii("10")', '$ptascii("0")')
        body = body.replace('([49])', '([48])').replace('R:1;K:', 'R:0;K:')
        body = body.replace('PINT 10', 'PFLOAT 0')
        body = body.replace('expression_integer = NScalarInt (INTEGER 10) metadata_integer',
                            'expression_integer = NScalarFloat (FLOAT "0000000000000000") metadata_integer')
        old = 'porigin_cast = porigin_base\n  -- if expression_cast = expression_base'
        root += lines(r'''
expression_rhs = NExprTernary expression_condition expression_cast expression_rhs_skipped metadata_rhs
$origin_child((porigin_rhs),[PCFIELD 0]) = (porigin_condition)
$origin_child((porigin_rhs),[PCFIELD 1]) = (porigin_cast)
$origin_child((porigin_rhs),[PCFIELD 2]) = (porigin_rhs_skipped)
$origin_node(S_capture.SOURCES,porigin_condition) = (expression_condition)
$origin_node(S_capture.SOURCES,porigin_cast) = (expression_cast)
$origin_node(S_capture.SOURCES,porigin_rhs_skipped) = (expression_rhs_skipped)
porigin_selected = porigin_cast
expression_selected = expression_cast
''')
        assert body.count(old) == 1
        body = body.replace(old, '\n  -- if '.join(root))
        late_root = ''.join('  -- if ' + check + '\n' for check in root)
        assert body.count(late_root) == 1
        body = body.replace(late_root, '')
        marker = '  -- PhpStep: S_capture ~> S_dispatch\n'
        assert body.count(marker) == 1
        body = body.replace(marker, late_root + marker)
    checks = lines(r'''
~$coalesce_quiet_operand(expression_null)
$string_read_runtime_value(S_capture,porigin_null) = (PNULL)
$string_read_allocated_base(S_capture,porigin_rhs,pvalue_base)
~$string_read_allocated_value(S_capture,porigin_rhs,pvalue_base)
$string_read_runtime_value(S_capture,porigin_rhs) = eps
$string_read_allocated_base(S_capture,porigin_selected,pvalue_base)
~$string_read_allocated_value(S_capture,porigin_base,pvalue_base)
pvalue_base =/= PNULL
''')
    if reference:
        checks += lines(r'''
expression_null = NExprTernary expression_null_condition expression_null_value expression_null_false metadata_null
expression_null_condition = NExprCastInt (NScalarInt (INTEGER 1) metadata_null_atom) metadata_null_condition
$origin_child((porigin_null),[PCFIELD 0]) = (porigin_null_condition)
$origin_child((porigin_null),[PCFIELD 1]) = (porigin_null_value)
$origin_child((porigin_null),[PCFIELD 2]) = (porigin_null_false)
$origin_node(S_capture.SOURCES,porigin_null_value) = (expression_null_value)
$origin_node(S_capture.SOURCES,porigin_null_false) = (expression_null_false)
$compiled_read(S_capture,porigin_null) = eps
$string_read_runtime_value(S_capture,porigin_null_condition) = (PINT 1)
~$string_read_allocated_value(S_capture,porigin_selected,pvalue_base)
$truth(S_capture,pvalue_base)
''')
    else:
        checks += lines(r'''
expression_null_value = expression_null
porigin_null_value = porigin_null
expression_condition = NExprCastInt (NScalarInt (INTEGER 1) metadata_condition_atom) metadata_condition
$string_read_runtime_value(S_capture,porigin_condition) = (PINT 1)
$compiled_read(S_capture,porigin_null) = (PNULL)
$string_read_allocated_value(S_capture,porigin_selected,pvalue_base)
~$truth(S_capture,pvalue_base)
''')
    checks += lines(r'''
expression_null_value = NExprConstFetch (NName (BYTES text_null) metadata_null_name) metadata_null_value
$ptlc($base64(text_null)) = $ptascii("null")
$origin_child((porigin_null_value),[PCFIELD 0]) = (porigin_null_name)
$origin_node(S_capture.SOURCES,porigin_null_name) = (NName (BYTES text_null) metadata_null_name)
$compiled_read(S_capture,porigin_null_value) = (PNULL)
''')
    nodes = ['null', 'rhs', 'selected', 'null_value', 'null_name', 'rhs_skipped']
    if reference:
        nodes += ['null_condition', 'null_false']
    else:
        nodes += ['condition']
    for node in nodes:
        checks += [f'porigin_{node} = PORIGIN n_unit pcpath_{node}']
        if node not in ('null_name', 'rhs_skipped'):
            checks += [f'$compiled_precision(S_capture,(porigin_{node})) = (14)']
    for node in ('rhs', 'selected'):
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{node}) = ((z_{node},false))',
                   f'$(z_{node} > 0)', f'$compiled_read(S_capture,porigin_{node}) = eps']
    marker = '  -- PhpStep: S_capture ~> S_dispatch\n'
    assert body.count(marker) == 1
    body = body.replace(marker, ''.join('  -- if ' + check + '\n' for check in checks) + marker)
    derived = []
    for node in ('null', 'rhs', 'selected'):
        state = f'S_composite_{node}_precision'
        derived += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                    f'~$string_read_allocated_base({state},porigin_base,pvalue_base)', f'$string_read_plan({state}) = eps']
    for node in ('rhs', 'selected'):
        for label, flag, line in [('line', 'false', '0'), ('folded', 'true', f'z_{node}')]:
            state = f'S_composite_{node}_{label}'
            derived += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} {line} {flag}) :: pcode.EXPRESSIONS]]]',
                        f'~$string_read_allocated_base({state},porigin_base,pvalue_base)', f'$string_read_plan({state}) = eps']
    derived += lines(r'''
S_null_name_shadow = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_null_name (NName (BYTES text_null) eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_null_name_shadow,porigin_rhs,pvalue_base)
~$string_read_allocated_base(S_null_name_shadow,porigin_base,pvalue_base)
$string_read_plan(S_null_name_shadow) = eps
S_rhs_source_shadow = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_rhs_skipped expression_null_value) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_rhs_source_shadow,porigin_selected,pvalue_base)
~$string_read_allocated_base(S_rhs_source_shadow,porigin_base,pvalue_base)
$string_read_plan(S_rhs_source_shadow) = eps
S_budget_null_composite = S_capture[.COMPLETION = BUDGET]
$string_read_allocated_base(S_budget_null_composite,porigin_base,pvalue_base)
$string_read_plan(S_budget_null_composite) = (pstringread)
''')
    for label, value in [('false', 'PBOOL false'), ('zero', 'PINT 0'), ('float_zero', 'PFLOAT 0'),
                         ('negative_zero', 'PFLOAT 9223372036854775808')]:
        state = 'S_composite_nonnull_' + label
        derived += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_null_value ({value})) :: ppool.CONSTANTS]]]',
                    f'$string_read_runtime_value({state},porigin_null) = ({value})',
                    f'$string_read_allocated_base({state},porigin_rhs,pvalue_base)',
                    f'~$string_read_allocated_base({state},porigin_base,pvalue_base)', f'$string_read_plan({state}) = eps']
    if not reference:
        derived += lines(r'''
S_zero_live_precision = S_capture[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true]
$precision_value(S_zero_live_precision) = 17
~$string_read_allocated_base(S_zero_live_precision,porigin_rhs,pvalue_base)
~$string_read_allocated_base(S_zero_live_precision,porigin_base,pvalue_base)
$string_read_plan(S_zero_live_precision) = eps
''')
    body += ''.join('  -- if ' + check + '\n' for check in derived)
    main = body.split('def $main() = true\n', 1)[1]
    derived_start = main.index('  -- if S_later =')
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())
