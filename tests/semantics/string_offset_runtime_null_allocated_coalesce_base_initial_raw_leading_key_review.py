"""Quiet NULL selection preserves an allocated RHS and its saved raw offset."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_literal_concat_chain_base_initial_raw_leading_key_review import render as render_chain
from string_offset_runtime_allocated_float_producer_cast_base_initial_raw_leading_key_review import render as render_float


def render(program, filename_b64, reference=False):
    renderer = render_float if reference else render_chain
    body, _, _ = renderer(program, filename_b64, reference=reference)
    root = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce expression_left expression_chain metadata_base)
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_left)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_chain)
$origin_node(S_capture.SOURCES,porigin_left) = (expression_left)
$compiled_read(S_capture,porigin_left) = eps
''')
    if reference:
        start = body.index('  -- if $origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce')
        end = body.index('  -- if $lookup(S_capture.ENV,$ptascii("alias"))', start)
        body = body[:start] + ''.join('  -- if ' + check + '\n' for check in root) + body[end:]
        old = '\n'.join('  -- if ' + check for check in lines(r'''
porigin_skipped = PORIGIN n_unit pcpath_skipped
S_skipped = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_skipped 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_skipped,porigin_base,pvalue_base)
$string_read_raw_capture(S_skipped,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
''')) + '\n'
        assert body.count(old) == 1
        new = old.replace('porigin_skipped', 'porigin_left').replace('pcpath_skipped', 'pcpath_left')
        new = new.replace('$string_read_allocated_base(S_skipped,porigin_base,pvalue_base)', '~$string_read_allocated_base(S_skipped,porigin_base,pvalue_base)')
        new = new.replace('$string_read_raw_capture(S_skipped,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))', '$string_read_raw_capture(S_skipped,poperand,pvalue_base) = eps')
        body = body.replace(old, new)
    else:
        old = 'porigin_chain = porigin_base'
        assert body.count(old) == 1
        body = body.replace(old, '\n  -- if '.join(root))
    checks = lines(r'''
expression_left = NExprTernary expression_condition expression_null expression_false metadata_left
expression_condition = NExprCastInt expression_condition_atom metadata_condition
expression_condition_atom = NScalarInt (INTEGER 1) metadata_condition_atom
expression_null = NExprConstFetch name_null metadata_null
expression_false = NExprConstFetch name_false metadata_false
name_null = NName (BYTES text_null) metadata_null_name
name_false = NName (BYTES text_false) metadata_false_name
$ptlc($base64(text_null)) = $ptascii("null")
$ptlc($base64(text_false)) = $ptascii("false")
~$coalesce_quiet_operand(expression_left)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_condition)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_null)
$origin_child((porigin_left),[PCFIELD 2]) = (porigin_false)
$origin_child((porigin_condition),[PCFIELD 0]) = (porigin_condition_atom)
$origin_child((porigin_null),[PCFIELD 0]) = (porigin_null_name)
$origin_child((porigin_false),[PCFIELD 0]) = (porigin_false_name)
$string_read_runtime_value(S_capture,porigin_left) = (PNULL)
$string_read_runtime_value(S_capture,porigin_condition) = (PINT 1)
$string_read_runtime_value(S_capture,porigin_null) = (PNULL)
$string_read_runtime_value(S_capture,porigin_false) = (PBOOL false)
$string_read_allocated_value(S_capture,porigin_chain,pvalue_base)
~$string_read_allocated_value(S_capture,porigin_base,pvalue_base)
$string_read_runtime_value(S_capture,porigin_base) = eps
|S_capture.STRINGDATA| = 4
''')
    for node in ('left', 'condition', 'condition_atom', 'null', 'false', 'null_name', 'false_name'):
        checks += [f'porigin_{node} = PORIGIN n_unit pcpath_{node}']
        if node not in ('null_name', 'false_name'):
            checks += [f'$compiled_precision(S_capture,(porigin_{node})) = (14)']
    for node in ('base', 'left', 'condition'):
        checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{node}) = ((z_{node},false))',
                   f'$(z_{node} > 0)', f'$compiled_read(S_capture,porigin_{node}) = eps']
    marker = '  -- PhpStep: S_capture ~> S_dispatch\n'
    assert body.count(marker) == 1
    body = body.replace(marker, ''.join('  -- if ' + check + '\n' for check in checks) + marker)
    derived = []
    for node in ('base', 'left', 'condition'):
        for label, flag, line in [('line', 'false', '0'), ('folded', 'true', f'z_{node}')]:
            state = f'S_null_{node}_{label}'
            derived += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} {line} {flag}) :: pcode.EXPRESSIONS]]]',
                        f'~$string_read_allocated_base({state},porigin_base,pvalue_base)', f'$string_read_plan({state}) = eps']
    for node in ('left', 'condition', 'condition_atom', 'null'):
        state = f'S_null_{node}_precision'
        derived += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                    f'~$string_read_allocated_base({state},porigin_base,pvalue_base)']
    for node, expression in [('left', 'NExprTernary expression_condition expression_null expression_false eps'),
                             ('condition', 'NExprCastInt expression_condition_atom eps'),
                             ('condition_atom', 'NScalarInt (INTEGER 1) eps'),
                             ('null_name', 'NName (BYTES text_null) eps'),
                             ('false_name', 'NName (BYTES text_false) eps')]:
        state = 'S_null_source_' + node
        derived += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{node} ({expression})) :: pcunit.OCCURRENCES]]]',
                    f'~$string_read_allocated_base({state},porigin_base,pvalue_base)', f'$string_read_plan({state}) = eps']
        if node == 'false_name':
            derived += [f'$string_read_runtime_value({state},porigin_left) = (PNULL)']
    for label, value in [('false', 'PBOOL false'), ('zero', 'PINT 0')]:
        state = 'S_nonnull_' + label
        derived += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_null ({value})) :: ppool.CONSTANTS]]]',
                    f'$string_read_runtime_value({state},porigin_left) = ({value})',
                    f'$string_read_allocated_value({state},porigin_chain,pvalue_base)',
                    f'~$string_read_allocated_base({state},porigin_base,pvalue_base)', f'$string_read_plan({state}) = eps']
    for label, update in [('code', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_false 0 false) :: pcode.EXPRESSIONS]]'),
                          ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_false 17) :: ppool.CONSTANTS]]'),
                          ('pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_false (PINT 77)) :: ppool.CONSTANTS]]'),
                          ('root_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base (PINT 77)) :: ppool.CONSTANTS]]')]:
        state = 'S_unused_' + label
        derived += [f'{state} = S_capture[{update}]', f'$string_read_allocated_base({state},porigin_base,pvalue_base)',
                    f'$string_read_plan({state}) = (pstringread)']
    derived += lines(r'''
S_forged_compiled_null = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left z_left true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left PNULL) :: ppool.CONSTANTS]]]
$compiled_read(S_forged_compiled_null,porigin_left) = (PNULL)
$string_read_runtime_value(S_forged_compiled_null,porigin_left) = eps
~$string_read_allocated_base(S_forged_compiled_null,porigin_base,pvalue_base)
expression_compiled_null_base = NExprBinaryOpCoalesce expression_null expression_chain metadata_base
pcoccurrence_compiled_null* = $pcwalk([PCOCCURRENCE pcpath_base expression_compiled_null_base])
S_compiled_null = S_forged_compiled_null[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_compiled_null* ++ pcunit.OCCURRENCES]]]
$compiled_identity_value(S_compiled_null,porigin_left) = (PNULL)
$string_read_runtime_value(S_compiled_null,porigin_left) = (PNULL)
$string_read_allocated_base(S_compiled_null,porigin_base,pvalue_base)
$string_read_plan(S_compiled_null) = (pstringread)
S_budget_null = S_capture[.COMPLETION = BUDGET]
$string_read_runtime_value(S_budget_null,porigin_left) = eps
$string_read_allocated_base(S_budget_null,porigin_base,pvalue_base)
$origin_child((pkeyread.SITE),[PCFIELD 1]) = (porigin_key)
$origin_node(S_capture.SOURCES,porigin_key) = (expression_cv)
expression_cv_base = NExprBinaryOpCoalesce expression_cv expression_chain metadata_base
pcoccurrence_cv* = $pcwalk([PCOCCURRENCE pcpath_base expression_cv_base])
S_cv_left = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_cv* ++ pcunit.OCCURRENCES]]][.STORE[n_key] = DEFINED PNULL]
S_cv_read = $resolve_at(S_cv_left,poperand,z_key)
S_cv_read.RESULT = KNOWN PNULL
$coalesce_quiet_operand(expression_cv)
$string_read_allocated_value(S_cv_left,porigin_chain,pvalue_base)
~$string_read_allocated_base(S_cv_left,porigin_base,pvalue_base)
expression_cv_right_base = NExprBinaryOpCoalesce expression_left expression_cv metadata_base
pcoccurrence_cv_right* = $pcwalk([PCOCCURRENCE pcpath_base expression_cv_right_base])
S_cv_right = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_cv_right* ++ pcunit.OCCURRENCES]]][.STORE[n_key] = DEFINED pvalue_base]
S_cv_right_read = $resolve_at(S_cv_right,poperand,z_key)
S_cv_right_read.RESULT = KNOWN pvalue_base
~$string_read_allocated_value(S_cv_right,porigin_chain,pvalue_base)
~$string_read_allocated_base(S_cv_right,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in derived)
    main = body.split('def $main() = true\n', 1)[1]
    derived_start = main.index('  -- if S_later =')
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())
