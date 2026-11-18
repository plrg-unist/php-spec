"""Independent NULL-selected composite BASE, authority and saved-owner controls."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_null_allocated_composite_rhs_coalesce_base_initial_raw_leading_key_review import render as render_author


def prefix(program, filename_b64, reference=True):
    body, _, _ = render_author(program, filename_b64, reference=reference)
    return body[:body.index('  -- if S_later =')]


def render(program, filename_b64, direct_program, direct_filename_b64, control_program, control_filename_b64):
    body = prefix(program, filename_b64)
    checks = lines(r'''
$code_expression(pcode.EXPRESSIONS,pcpath_null) = ((z_null,false))
$(z_null > 0)
$code_expression(pcode.EXPRESSIONS,pcpath_null_condition) = ((z_null_condition,false))
$(z_null_condition > 0)
''')
    for node in ('base', 'null', 'null_condition', 'rhs', 'selected', 'chain', 'inner', 'cast'):
        for label, line, folded in (('line', '0', 'false'), ('folded', f'z_{node}', 'true')):
            state = f'S_peer_{node}_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} {line} {folded}) :: pcode.EXPRESSIONS]]]',
                       f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                       f'$string_read_plan({state}) = eps']
    for node in ('base', 'null', 'null_condition', 'null_value', 'rhs', 'selected', 'chain', 'inner', 'cast', 'integer'):
        state = f'S_peer_precision_{node}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                   f'$string_read_plan({state}) = eps']
    checks += lines(r'''
expression_rhs_skipped = NExprTernary expression_rhs_condition expression_rhs_true expression_rhs_false metadata_rhs_skipped
$origin_child((porigin_rhs_skipped),[PCFIELD 0]) = (porigin_rhs_condition)
$origin_child((porigin_rhs_condition),[PCFIELD 0]) = (porigin_rhs_atom)
porigin_rhs_atom = PORIGIN n_unit pcpath_rhs_atom
$origin_node(S_capture.SOURCES,porigin_rhs_atom) = (NScalarInt (INTEGER 1) metadata_rhs_atom)
S_peer_rhs_descendant = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_rhs_atom (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_rhs_descendant,porigin_rhs,pvalue_base)
~$string_read_allocated_base(S_peer_rhs_descendant,porigin_base,pvalue_base)
$string_read_plan(S_peer_rhs_descendant) = eps
S_peer_rhs_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_rhs (NExprBinaryOpCoalesce expression_selected expression_rhs_skipped eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_rhs_source,porigin_rhs,pvalue_base)
~$string_read_allocated_base(S_peer_rhs_source,porigin_base,pvalue_base)
S_peer_null_name = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_null_name (NName (BYTES text_null) eps)) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_peer_null_name,porigin_null) = (PNULL)
$string_read_allocated_base(S_peer_null_name,porigin_rhs,pvalue_base)
~$string_read_allocated_base(S_peer_null_name,porigin_base,pvalue_base)
S_peer_selected_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_selected (NExprTernary expression_chain ABSENT expression_skipped eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_selected_source,porigin_selected,pvalue_base)
~$string_read_allocated_base(S_peer_selected_source,porigin_rhs,pvalue_base)
~$string_read_allocated_base(S_peer_selected_source,porigin_base,pvalue_base)
S_peer_unused = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_rhs_skipped 0 false) :: (CODEEXPR pcpath_null_false 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_rhs_skipped (PINT 77)) :: (PCCPRECISION pcpath_rhs_skipped 17) :: (PCCPRECISION pcpath_null_false 17) :: ppool.CONSTANTS]]]
$compiled_read(S_peer_unused,porigin_rhs_skipped) = eps
$string_read_allocated_base(S_peer_unused,porigin_base,pvalue_base)
$string_read_plan(S_peer_unused) = (pstringread)
S_peer_abrupt = S_capture[.COMPLETION = UNSUPPORTED "peer-control"]
$string_read_runtime_value(S_peer_abrupt,porigin_null) = eps
~$string_read_allocated_value(S_peer_abrupt,porigin_chain,pvalue_base)
$string_read_allocated_base(S_peer_abrupt,porigin_rhs,pvalue_base)
$string_read_allocated_base(S_peer_abrupt,porigin_base,pvalue_base)
S_peer_forged_null = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_null z_null true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_null PNULL) :: ppool.CONSTANTS]]]
$compiled_read(S_peer_forged_null,porigin_null) = (PNULL)
$string_read_runtime_value(S_peer_forged_null,porigin_null) = eps
$string_read_allocated_base(S_peer_forged_null,porigin_rhs,pvalue_base)
~$string_read_allocated_base(S_peer_forged_null,porigin_base,pvalue_base)
''')
    for label, value in (('false', 'PBOOL false'), ('zero', 'PINT 0'), ('float_zero', 'PFLOAT 0'), ('negative_zero', 'PFLOAT 9223372036854775808')):
        state = 'S_peer_nonnull_' + label
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_null_value ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value({state},porigin_null) = ({value})',
                   f'$string_read_allocated_base({state},porigin_rhs,pvalue_base)',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)']
    for label, encoded, value in (('empty', '', 'eps'), ('zero_string', 'MA==', '$ptascii("0")')):
        checks += [f'expression_peer_{label} = NScalarString (BYTES "{encoded}") metadata_null_value',
                   f'expression_peer_{label}_null = NExprTernary expression_null_condition expression_peer_{label} expression_null_false metadata_null',
                   f'expression_peer_{label}_base = NExprBinaryOpCoalesce expression_peer_{label}_null expression_rhs metadata_base',
                   f'pcoccurrence_peer_{label}* = $pcwalk([PCOCCURRENCE pcpath_base expression_peer_{label}_base])',
                   f'S_peer_{label} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_peer_{label}* ++ pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_null_value (PSTRING {value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_peer_{label},porigin_null) = (PSTRING_CARRIER INTERNED_STRING ({value}))',
                   f'$truth_value(S_peer_{label},PSTRING_CARRIER INTERNED_STRING ({value}),z_base) = S_peer_{label}[.RESULT = KNOWN (PBOOL false)]',
                   f'$string_read_allocated_base(S_peer_{label},porigin_rhs,pvalue_base)',
                   f'~$string_read_allocated_base(S_peer_{label},porigin_base,pvalue_base)',
                   f'$string_read_plan(S_peer_{label}) = eps']
    precision_nodes = ('rhs', 'selected', 'chain', 'inner', 'cast', 'integer', 'atom', 'inner_suffix', 'suffix')
    entries = ' :: '.join(f'(PCCPRECISION pcpath_{node} 17)' for node in precision_nodes)
    checks += [f'S_peer_rhs17 = S_capture[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true][.POOLS = [ppool[.CONSTANTS = {entries} :: ppool.CONSTANTS]]]',
               '$precision_value(S_peer_rhs17) = 17',
               '$string_read_allocated_base(S_peer_rhs17,porigin_rhs,pvalue_base)',
               '$compiled_precision(S_peer_rhs17,(porigin_base)) = (14)',
               '~$string_read_allocated_base(S_peer_rhs17,porigin_base,pvalue_base)']
    checks += lines(r'''
S_peer_suffix = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("callback"),$ptascii("-10.5bcde")]]
$heap_graph(S_peer_suffix) = $heap_graph(S)
$string_read_raw_saved(S_peer_suffix,pstringread) = (3)
$string_read_ready(S_peer_suffix,pstringread)
$string_read_resume(S_peer_suffix,pstringread) = S_peer_suffix[.TODO = ptask_tail*][.RESULT = KNOWN pvalue_byte][.BASE = BASE_VALUE (KNOWN PNULL)]
pvalue_duplicate = PSTRING_CARRIER (REQUEST_STRING 5) ($ptascii("-10.5bcde"))
$string_carrier_valid(S_peer_suffix,pvalue_duplicate)
$string_same(pvalue_base,pvalue_duplicate) = (false)
$string_read_raw_saved(S_peer_suffix,pstringread[.READ.BASE = pvalue_duplicate]) = eps
~$string_read_provider_ready(S_peer_suffix,pstringread[.READ.BASE = pvalue_duplicate])
$string_read_raw_saved(S,pstringread[.READ.OWNERS = BASE_VALUE (KNOWN PNULL)]) = eps
$string_read_raw_saved(S,pstringread[.KEYCELL = eps]) = eps
S_peer_duplicate = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("-10.5bcde")]]
pvalue_duplicate_entry = PSTRING_CARRIER (REQUEST_STRING 4) ($ptascii("-10.5bcde"))
$string_carrier_valid(S_peer_duplicate,pvalue_duplicate_entry)
~$string_read_allocated_base(S_peer_duplicate,porigin_base,pvalue_duplicate_entry)
$string_read_raw_capture(S_peer_duplicate[.RESULT = KNOWN pvalue_duplicate_entry],poperand,pvalue_duplicate_entry) = eps
S_peer_nul = S_capture[.STRINGDATA = [$ptascii("512"),$ptascii("-10.5"),$ptascii("-10.5bc"),[45,49,48,46,53,98,99,0,100,101]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING 3) ([45,49,48,46,53,98,99,0,100,101])
$string_carrier_valid(S_peer_nul,pvalue_nul)
~$string_read_allocated_base(S_peer_nul,porigin_base,pvalue_nul)
$string_read_raw_capture(S_peer_nul[.RESULT = KNOWN pvalue_nul],poperand,pvalue_nul) = eps
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    direct = prefix(direct_program, direct_filename_b64, False).split('def $main() = true\n', 1)[1]
    control = prefix(control_program, control_filename_b64).split('def $main() = true\n', 1)[1]
    control = control.replace('$origin_child((porigin_selected),', '$origin_child((porigin_inner_selected),')
    old = 'expression_selected = NExprTernary expression_chain ABSENT expression_skipped metadata_selected'
    assert control.count(old) == 1
    replacement = lines(r'''
expression_selected = NExprBinaryOpCoalesce expression_inner_null expression_inner_selected metadata_inner_coalesce
$origin_child((porigin_selected),[PCFIELD 0]) = (porigin_inner_null)
$origin_child((porigin_selected),[PCFIELD 1]) = (porigin_inner_selected)
$origin_node(S_capture.SOURCES,porigin_inner_null) = (expression_inner_null)
$origin_node(S_capture.SOURCES,porigin_inner_selected) = (expression_inner_selected)
expression_inner_selected = NExprTernary expression_chain ABSENT expression_skipped metadata_selected
''')
    control = control.replace(old, '\n  -- if '.join(replacement))
    composed = lines(r'''
porigin_inner_null = PORIGIN n_unit pcpath_inner_null
porigin_inner_selected = PORIGIN n_unit pcpath_inner_selected
$compiled_read(S_capture,porigin_inner_null) = (PNULL)
$string_read_runtime_value(S_capture,porigin_inner_null) = (PNULL)
$compiled_precision(S_capture,(porigin_inner_null)) = (14)
$compiled_precision(S_capture,(porigin_inner_selected)) = (14)
$code_expression(pcode.EXPRESSIONS,pcpath_inner_selected) = ((z_inner_selected,false))
$(z_inner_selected > 0)
$compiled_read(S_capture,porigin_inner_selected) = eps
~$string_read_allocated_value(S_capture,porigin_inner_selected,pvalue_base)
$string_read_allocated_base(S_capture,porigin_inner_selected,pvalue_base)
~$string_read_allocated_value(S_capture,porigin_selected,pvalue_base)
$string_read_allocated_base(S_capture,porigin_selected,pvalue_base)
$string_read_allocated_base(S_capture,porigin_rhs,pvalue_base)
$string_read_allocated_base(S_capture,porigin_base,pvalue_base)
$origin_node(S_capture.SOURCES,porigin_inner_null) = (NExprConstFetch (NName (BYTES text_inner_null) metadata_inner_null_name) metadata_inner_null)
$origin_child((porigin_inner_null),[PCFIELD 0]) = (porigin_inner_null_name)
porigin_inner_null_name = PORIGIN n_unit pcpath_inner_null_name
S_peer_inner_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_inner_null_name (NName (BYTES text_inner_null) eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_inner_source,porigin_inner_selected,pvalue_base)
~$string_read_allocated_base(S_peer_inner_source,porigin_selected,pvalue_base)
~$string_read_allocated_base(S_peer_inner_source,porigin_base,pvalue_base)
''')
    control += ''.join('  -- if ' + check + '\n' for check in composed)
    extra = 'dec $peer_direct_original() : bool\ndef $peer_direct_original() = true\n' + direct
    extra += '\ndec $peer_nested_null() : bool\ndef $peer_nested_null() = true\n' + control
    body = body.replace('dec $main() : bool', extra + '\ndec $main() : bool')
    body += '  -- if $peer_direct_original()\n  -- if $peer_nested_null()\n'
    main = body.split('def $main() = true\n', 1)[1]
    return body, len(main.splitlines()) + len(direct.splitlines()) + len(control.splitlines()), len(checks) + len(composed)
