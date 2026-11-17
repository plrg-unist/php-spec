"""Independent typed scalar-suffix authority and saved-reference checks."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_literal_concat_chain_base_initial_raw_leading_key_peer_review import render as render_reference


def render(program, filename_b64):
    body, _, _ = render_reference(program, filename_b64)
    body = body.replace('$ptascii("10bcde")', '$ptascii("10b23-41")')
    body = body.replace('$ptascii("10bc")', '$ptascii("10b23-41")')
    body = body.replace('$ptascii("bc")', '$ptascii("b23-41")')
    body = body.replace('$ptascii("de")', '$ptascii("")')
    body = body.replace('([99])', '([50])').replace('([100])', '([51])')
    body = body.replace(';R:c;K:4;A:', ';R:2;K:4;A:')
    definitions = lines(r'''
expression_bc = NExprBinaryOpConcat expression_b expression_pair2 metadata_bc
expression_b = NScalarString (BYTES text_b) metadata_b
expression_pair2 = NExprBinaryOpConcat expression_2 expression_pair_plus metadata_pair2
expression_2 = NScalarInt (INTEGER 2) metadata_2
expression_pair_plus = NExprBinaryOpConcat expression_plus expression_pair_minus metadata_pair_plus
expression_plus = NExprUnaryPlus expression_3 metadata_plus
expression_3 = NScalarInt (INTEGER 3) metadata_3
expression_pair_minus = NExprBinaryOpConcat expression_minus expression_pair_true metadata_pair_minus
expression_minus = NExprUnaryMinus expression_4 metadata_minus
expression_4 = NScalarInt (INTEGER 4) metadata_4
expression_pair_true = NExprBinaryOpConcat expression_true expression_pair_false metadata_pair_true
expression_true = NExprConstFetch name_true metadata_true
name_true = NNameFullyQualified (BYTES text_true) metadata_name_true
expression_pair_false = NExprBinaryOpConcat expression_false expression_null metadata_pair_false
expression_false = NExprConstFetch name_false metadata_false
name_false = NName (BYTES text_false) metadata_name_false
expression_null = NExprConstFetch name_null metadata_null
name_null = NName (BYTES text_null) metadata_name_null
expression_de = NExprBinaryOpConcat expression_empty_false expression_empty_null metadata_de
expression_empty_false = NExprConstFetch name_empty_false metadata_empty_false
name_empty_false = NName (BYTES text_empty_false) metadata_name_empty_false
expression_empty_null = NExprConstFetch name_empty_null metadata_empty_null
name_empty_null = NNameFullyQualified (BYTES text_empty_null) metadata_name_empty_null
$base64(text_b) = $ptascii("b")
$base64(text_true) = $ptascii("TrUe")
$base64(text_false) = $ptascii("FaLsE")
$base64(text_null) = $ptascii("NuLl")
$base64(text_empty_false) = $ptascii("false")
$base64(text_empty_null) = $ptascii("null")
''')
    old = '  -- if expression_bc = NScalarString (BYTES text_bc) metadata_bc\n'
    assert body.count(old) == 1
    body = body.replace(old, ''.join('  -- if ' + check + '\n' for check in definitions))
    for prefix in ('expression_de = NScalarString ', '$base64(text_bc)', '$base64(text_de)'):
        body = '\n'.join(line for line in body.split('\n')
                         if not line.startswith('  -- if ' + prefix))
    body = body.replace('NScalarString (BYTES text_bc) eps',
                        'NExprBinaryOpConcat expression_b expression_pair2 eps')
    body = body.replace('NScalarString (BYTES text_de) eps',
                        'NExprBinaryOpConcat expression_empty_false expression_empty_null eps')
    checks = lines(r'''
$string_read_literal_bytes(expression_bc) = eps
$string_read_literal_bytes(expression_de) = eps
$string_read_folded_concat_bytes(expression_bc) = ($ptascii("b23-41"))
$string_read_folded_concat_bytes(expression_de) = (eps)
$string_read_runtime_value(S_capture,porigin_bc) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("b23-41")))
$string_read_runtime_value(S_capture,porigin_de) = (PSTRING_CARRIER INTERNED_STRING eps)
$string_same(pvalue_inner,pvalue_base) = (false)
S_empty_prefix = S_capture[.STRINGDATA = S_capture.STRINGDATA[0:3]]
$string_concat(S_empty_prefix,pvalue_inner,PSTRING_CARRIER INTERNED_STRING eps,false,true) = S_empty_prefix[.STRINGDATA = S_capture.STRINGDATA][.RESULT = KNOWN pvalue_base]
$string_concat(S_empty_prefix,pvalue_inner,PSTRING_CARRIER INTERNED_STRING eps,false,false) = S_empty_prefix[.RESULT = KNOWN pvalue_inner]
$string_read_folded_concat_bytes(expression_atom) = ($ptascii("10"))
$string_read_runtime_value(S_capture,porigin_atom) = (PINT 10)
$string_read_runtime_value(S_chain_bad_atom_type,porigin_atom) = eps
$string_read_folded_concat_bytes(NScalarFloat (FLOAT "3ff0000000000000") metadata_bc) = eps
$string_read_folded_concat_bytes(NExprBinaryOpConcat expression_b (NScalarFloat (FLOAT "3ff0000000000000") metadata_bc) metadata_bc) = eps
$string_read_folded_concat_bytes(expression_cast) = eps
$string_read_folded_concat_bytes(NScalarInt (INTEGER 9223372036854775808) metadata_bc) = eps
$string_read_folded_concat_bytes(NExprUnaryMinus (NScalarInt (INTEGER $(-9223372036854775808)) metadata_bc) metadata_bc) = eps
''')
    links = dict(b=('bc', 0), pair2=('bc', 1),
                 **{'2': ('pair2', 0)}, pair_plus=('pair2', 1),
                 plus=('pair_plus', 0), pair_minus=('pair_plus', 1),
                 **{'3': ('plus', 0)}, minus=('pair_minus', 0),
                 pair_true=('pair_minus', 1), **{'4': ('minus', 0)},
                 true=('pair_true', 0), pair_false=('pair_true', 1),
                 name_true=('true', 0), false=('pair_false', 0),
                 null=('pair_false', 1), name_false=('false', 0),
                 name_null=('null', 0), empty_false=('de', 0),
                 empty_null=('de', 1), name_empty_false=('empty_false', 0),
                 name_empty_null=('empty_null', 0))
    values = dict(b='PSTRING ($ptascii("b"))', pair2='PSTRING ($ptascii("23-41"))',
                  **{'2': 'PINT 2'}, pair_plus='PSTRING ($ptascii("3-41"))',
                  plus='PINT 3', **{'3': 'PINT 3'}, pair_minus='PSTRING ($ptascii("-41"))',
                  minus='PINT $(-4)', **{'4': 'PINT 4'}, pair_true='PSTRING ($ptascii("1"))',
                  true='PBOOL true', pair_false='PSTRING eps', false='PBOOL false',
                  null='PNULL', empty_false='PBOOL false', empty_null='PNULL')
    for node, (parent, field) in links.items():
        source = node if node.startswith('name_') else 'expression_' + node
        checks += [f'$origin_child((porigin_{parent}),[PCFIELD {field}]) = (porigin_{node})',
                   f'porigin_{node} = PORIGIN n_unit pcpath_{node}',
                   f'$origin_node(S_capture.SOURCES,porigin_{node}) = ({source})',
                   f'$compiled_precision(S_capture,(porigin_{node})) = (14)']
        if node in values:
            value = values[node]
            checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{node}) = ((z_{node},true))',
                       f'$(z_{node} > 0)', f'$compiled_read(S_capture,porigin_{node}) = ({value})',
                       f'$compiled_identity_value(S_capture,porigin_{node}) = ({value})',
                       f'$constant_at(ppool.CONSTANTS,pcpath_{node}) = ({value})']
        else:
            checks += [f'$code_expression(pcode.EXPRESSIONS,pcpath_{node}) = eps',
                       f'$compiled_read(S_capture,porigin_{node}) = eps',
                       f'$compiled_identity_value(S_capture,porigin_{node}) = eps',
                       f'$constant_at(ppool.CONSTANTS,pcpath_{node}) = eps']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    derived = []
    for node in links:
        derived += [f'S_scalar_shadow_{node} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{node} (NScalarString (BYTES "") eps)) :: pcunit.OCCURRENCES]]]',
                    f'~$string_read_allocated_base(S_scalar_shadow_{node},porigin_base,pvalue_base)',
                    f'$string_read_plan(S_scalar_shadow_{node}) = eps']
    for node in ('pair2', 'pair_plus', 'plus', 'pair_minus', 'minus',
                 'pair_true', 'true', 'pair_false', 'false', 'null',
                 'empty_false', 'empty_null'):
        derived += [f'S_scalar_pool_{node} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_{node} (PSTRING ($ptascii("wrong")))) :: ppool.CONSTANTS]]]',
                    f'~$string_read_allocated_base(S_scalar_pool_{node},porigin_base,pvalue_base)',
                    f'$string_read_raw_capture(S_scalar_pool_{node},poperand,pvalue_base) = eps']
    derived += lines(r'''
expression_integer_chain = NExprBinaryOpConcat expression_inner expression_atom metadata_chain
pvalue_integer_rhs = PSTRING_CARRIER (REQUEST_STRING 3) ($ptascii("10b23-4110"))
S_integer_rhs = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base (NExprBinaryOpCoalesce expression_integer_chain expression_right metadata_base)) :: (PCOCCURRENCE pcpath_chain expression_integer_chain) :: (PCOCCURRENCE pcpath_de expression_atom) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_de (PINT 10)) :: ppool.CONSTANTS]]][.STRINGDATA = S_capture.STRINGDATA[0:3] ++ [$ptascii("10b23-4110")]][.RESULT = KNOWN pvalue_integer_rhs]
$string_carrier_valid(S_integer_rhs,pvalue_integer_rhs)
$string_read_allocated_value(S_integer_rhs,porigin_inner,pvalue_inner)
$string_read_folded_concat_bytes(expression_atom) = ($ptascii("10"))
$concat_constant(S_integer_rhs,(porigin_de)) = true
$string_read_runtime_value(S_integer_rhs,porigin_de) = (PINT 10)
$string_concat(S_integer_rhs[.STRINGDATA = S_integer_rhs.STRINGDATA[0:3]],pvalue_inner,PSTRING_CARRIER INTERNED_STRING ($ptascii("10")),false,true) = S_integer_rhs[.RESULT = KNOWN pvalue_integer_rhs]
~$string_read_allocated_value(S_integer_rhs,porigin_chain,pvalue_integer_rhs)
~$string_read_allocated_base(S_integer_rhs,porigin_base,pvalue_integer_rhs)
$string_read_raw_capture(S_integer_rhs,poperand,pvalue_integer_rhs) = eps
$string_read_plan(S_integer_rhs) = eps
S_name_precision = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_name_true 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_name_precision,porigin_base,pvalue_base)
$string_read_raw_capture(S_name_precision,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
S_literal_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_2 (PSTRING ($ptascii("unneeded")))) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_literal_pool,porigin_base,pvalue_base)
$string_read_raw_capture(S_literal_pool,poperand,pvalue_base) = ((pvalue_raw,pstringread.KEYCELL))
''')
    body += ''.join('  -- if ' + check + '\n' for check in derived)
    main = body.split('def $main() = true\n', 1)[1]
    assert 'text_bc' not in main and 'text_de' not in main
    derived_start = main.index('  -- if S_unmarked =')
    return body, len(main.splitlines()), len(main[derived_start:].splitlines())
