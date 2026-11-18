"""Falsey nonowning shorthand conditions select allocated fallback headers."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_literal_concat_chain_base_initial_raw_leading_key_review import render as render_chain
from string_offset_runtime_allocated_float_producer_cast_base_initial_raw_leading_key_review import render as render_float


def render(program, filename_b64, reference=False):
    renderer = render_float if reference else render_chain
    body, _, _ = renderer(program, filename_b64, reference=reference)
    root = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary expression_condition ABSENT expression_chain metadata_base)
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_condition)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_chain)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_skipped)
$origin_node(S_capture.SOURCES,porigin_skipped) = eps
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
    condition = 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))' if reference else 'PINT 0'
    cast = 'CASTSTRING' if reference else 'CASTINT'
    node = 'NExprCastString' if reference else 'NExprCastInt'
    checks = [f'expression_condition = {node} expression_condition_atom metadata_condition'] + lines(r'''
expression_condition_atom = NScalarInt (INTEGER 0) metadata_condition_atom
$origin_node(S_capture.SOURCES,porigin_condition) = (expression_condition)
$origin_child((porigin_condition),[PCFIELD 0]) = (porigin_condition_atom)
$origin_node(S_capture.SOURCES,porigin_condition_atom) = (expression_condition_atom)
porigin_condition = PORIGIN n_unit pcpath_condition
porigin_condition_atom = PORIGIN n_unit pcpath_condition_atom
porigin_skipped = PORIGIN n_unit pcpath_skipped
$compiled_precision(S_capture,(porigin_condition)) = (14)
$compiled_precision(S_capture,(porigin_condition_atom)) = (14)
$code_expression(pcode.EXPRESSIONS,pcpath_base) = ((z_base,false))
$(z_base > 0)
$compiled_read(S_capture,porigin_base) = eps
$code_expression(pcode.EXPRESSIONS,pcpath_condition) = ((z_condition,false))
$(z_condition > 0)
$compiled_read(S_capture,porigin_condition) = eps
$code_expression(pcode.EXPRESSIONS,pcpath_condition_atom) = ((z_condition_atom,true))
$(z_condition_atom > 0)
$compiled_read(S_capture,porigin_condition_atom) = (PINT 0)
$compiled_identity_value(S_capture,porigin_condition_atom) = (PINT 0)
''') + [f'pvalue_condition = {condition}',
        '$string_read_runtime_value(S_capture,porigin_condition) = (pvalue_condition)',
        'pvalue_condition =/= PNULL', '~$truth(S_capture,pvalue_condition)',
        '$truth_value(S_capture,pvalue_condition,z_base) = S_capture[.RESULT = KNOWN (PBOOL false)]',
        f'$cast_apply(S_capture,{cast},PINT 0,z_condition) = S_capture[.RESULT = KNOWN pvalue_condition]',
        '~$string_read_allocated_value(S_capture,porigin_base,pvalue_base)',
        '$string_read_runtime_value(S_capture,porigin_base) = eps']
    checks = [check for check in checks if '  -- if ' + check + '\n' not in body]
    marker = '  -- PhpStep: S_capture ~> S_dispatch\n'
    assert body.count(marker) == 1
    body = body.replace(marker, ''.join('  -- if ' + check + '\n' for check in checks) + marker)
    derived = []
    nodes = ('condition',) if reference else ('base', 'condition')
    for name in nodes:
        for label, line, flag in (('line', '0', 'false'), ('folded', f'z_{name}', 'true')):
            state = f'S_short_{name}_{label}'
            derived += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{name} {line} {flag}) :: pcode.EXPRESSIONS]]]',
                        f'~$string_read_allocated_base({state},porigin_base,pvalue_base)', f'$string_read_plan({state}) = eps']
    for name in ('condition', 'condition_atom'):
        state = f'S_short_{name}_precision'
        derived += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{name} 17) :: ppool.CONSTANTS]]]',
                    f'~$string_read_allocated_base({state},porigin_base,pvalue_base)', f'$string_read_plan({state}) = eps']
    derived += [f'S_condition_shadow = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_condition ({node} expression_condition_atom eps)) :: pcunit.OCCURRENCES]]]',
                '$string_read_runtime_value(S_condition_shadow,porigin_condition) = (pvalue_condition)',
                '$string_read_allocated_base(S_condition_shadow,porigin_chain,pvalue_base)',
                '~$string_read_allocated_base(S_condition_shadow,porigin_base,pvalue_base)',
                '$string_read_plan(S_condition_shadow) = eps'] + lines(r'''
S_absent_noise = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_skipped 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_skipped (PINT 77)) :: (PCCPRECISION pcpath_skipped 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_absent_noise,porigin_base,pvalue_base)
$string_read_plan(S_absent_noise) = (pstringread)
''')
    body += ''.join('  -- if ' + check + '\n' for check in derived)
    main = body.split('def $main() = true\n', 1)[1]
    derived_start = main.index('  -- if S_later =')
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())
