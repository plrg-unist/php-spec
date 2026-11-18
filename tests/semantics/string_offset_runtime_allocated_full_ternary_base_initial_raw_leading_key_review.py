"""Quiet full ternaries retain the selected allocated header and saved key."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_literal_concat_chain_base_initial_raw_leading_key_review import render as render_chain
from string_offset_runtime_allocated_float_producer_cast_base_initial_raw_leading_key_review import render as render_float


def render(program, filename_b64, reference=False):
    renderer = render_float if reference else render_chain
    body, _, _ = renderer(program, filename_b64, reference=reference)
    true_arm, false_arm = ('expression_skipped', 'expression_chain') if reference else ('expression_chain', 'expression_skipped')
    chosen, skipped = (2, 1) if reference else (1, 2)
    integer = 0 if reference else 1
    truth = str(not reference).lower()
    root = [f'$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary expression_condition {true_arm} {false_arm} metadata_base)',
            '$origin_child((porigin_base),[PCFIELD 0]) = (porigin_condition)',
            f'$origin_child((porigin_base),[PCFIELD {chosen}]) = (porigin_chain)',
            f'$origin_child((porigin_base),[PCFIELD {skipped}]) = (porigin_skipped)',
            '$origin_node(S_capture.SOURCES,porigin_skipped) = (expression_skipped)',
            '$compiled_read(S_capture,porigin_skipped) = eps']
    if reference:
        start = body.index('  -- if $origin_node(S_capture.SOURCES,porigin_base) = (NExprBinaryOpCoalesce')
        end = body.index('  -- if $lookup(S_capture.ENV,$ptascii("alias"))', start)
        body = body[:start] + ''.join('  -- if ' + check + '\n' for check in root) + body[end:]
    else:
        old = 'porigin_chain = porigin_base'
        assert body.count(old) == 1
        body = body.replace(old, '\n  -- if '.join(root))
    checks = lines(r'''
expression_condition = NExprCastInt expression_condition_atom metadata_condition
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
''')
    checks.insert(1, f'expression_condition_atom = NScalarInt (INTEGER {integer}) metadata_condition_atom')
    checks += [f'$compiled_read(S_capture,porigin_condition_atom) = (PINT {integer})',
               f'$compiled_identity_value(S_capture,porigin_condition_atom) = (PINT {integer})',
               f'$string_read_runtime_value(S_capture,porigin_condition) = (PINT {integer})',
               f'$truth_value(S_capture,PINT {integer},z_base) = S_capture[.RESULT = KNOWN (PBOOL {truth})]',
               '~$string_read_allocated_value(S_capture,porigin_base,pvalue_base)',
               '~$string_read_allocated_base(S_capture,porigin_skipped,pvalue_base)']
    checks = [check for check in checks if '  -- if ' + check + '\n' not in body]
    marker = '  -- PhpStep: S_capture ~> S_dispatch\n'
    assert body.count(marker) == 1
    body = body.replace(marker, ''.join('  -- if ' + check + '\n' for check in checks) + marker)
    derived = []
    nodes = ('condition',) if reference else ('base', 'condition')
    for node in nodes:
        for label, line, flag in (('line', '0', 'false'), ('folded', f'z_{node}', 'true')):
            name = f'S_ternary_{node}_{label}'
            derived += [f'{name} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} {line} {flag}) :: pcode.EXPRESSIONS]]]',
                        f'~$string_read_allocated_base({name},porigin_base,pvalue_base)', f'$string_read_plan({name}) = eps']
    for node in ('condition', 'condition_atom'):
        name = f'S_ternary_{node}_precision'
        derived += [f'{name} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                    f'~$string_read_allocated_base({name},porigin_base,pvalue_base)', f'$string_read_plan({name}) = eps']
    derived += lines(r'''
$origin_child((porigin_skipped),[PCFIELD 0]) = (porigin_skipped_cast)
$origin_node(S_capture.SOURCES,porigin_skipped_cast) = (NExprCastString expression_skipped_integer metadata_skipped_cast)
porigin_skipped_cast = PORIGIN n_unit pcpath_skipped_cast
S_skipped_descendant = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_skipped_cast (NExprCastString expression_skipped_integer eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_skipped_descendant,porigin_chain,pvalue_base)
~$string_read_allocated_base(S_skipped_descendant,porigin_base,pvalue_base)
$string_read_plan(S_skipped_descendant) = eps
S_unused_skipped = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_skipped 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_skipped (PINT 77)) :: (PCCPRECISION pcpath_skipped 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_unused_skipped,porigin_base,pvalue_base)
$string_read_plan(S_unused_skipped) = (pstringread)
''')
    body += ''.join('  -- if ' + check + '\n' for check in derived)
    main = body.split('def $main() = true\n', 1)[1]
    derived_start = main.index('  -- if S_later =')
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())
