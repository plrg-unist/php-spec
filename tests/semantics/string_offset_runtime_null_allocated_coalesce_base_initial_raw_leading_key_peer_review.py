"""Independent NULL selection, exact allocation and compiled-left controls."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_null_allocated_coalesce_base_initial_raw_leading_key_review import render as render_author


def prefix(program, filename_b64):
    body, _, _ = render_author(program, filename_b64, reference=True)
    return body[:body.index('  -- if S_later =')]


def render(program, filename_b64, control_program, control_filename_b64):
    body = prefix(program, filename_b64)
    checks = []
    for node in ('base', 'left', 'condition', 'chain', 'inner', 'cast'):
        for label, line, folded in (('line', '0', 'false'), ('folded', f'z_{node}', 'true')):
            state = f'S_peer_{node}_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} {line} {folded}) :: pcode.EXPRESSIONS]]]',
                       f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                       f'$string_read_plan({state}) = eps']
    for node in ('base', 'left', 'condition', 'condition_atom', 'null', 'chain', 'inner', 'cast', 'integer'):
        state = f'S_peer_precision_{node}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                   f'$string_read_plan({state}) = eps']
    for node, expression in (
            ('left', 'NExprTernary expression_condition expression_null expression_false eps'),
            ('condition', 'NExprCastInt expression_condition_atom eps'),
            ('condition_atom', 'NScalarInt (INTEGER 1) eps'),
            ('null_name', 'NName (BYTES text_null) eps'),
            ('false_name', 'NName (BYTES text_false) eps'),
            ('chain', 'NExprBinaryOpConcat expression_inner expression_suffix eps'),
            ('cast', 'NExprCastString expression_integer eps'),
            ('atom', 'NScalarFloat (FLOAT "4025000000000000") eps')):
        state = f'S_peer_source_{node}'
        checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{node} ({expression})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                   f'$string_read_plan({state}) = eps']
        if node == 'false_name':
            checks += [f'$string_read_runtime_value({state},porigin_left) = (PNULL)']
    for label, update in (
            ('skipped_code', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_false 0 false) :: pcode.EXPRESSIONS]]'),
            ('skipped_precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_false 17) :: ppool.CONSTANTS]]'),
            ('skipped_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_false (PINT 77)) :: ppool.CONSTANTS]]'),
            ('unused_root_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base PNULL) :: ppool.CONSTANTS]]')):
        state = f'S_peer_{label}'
        checks += [f'{state} = S_capture[{update}]',
                   f'$string_read_allocated_base({state},porigin_base,pvalue_base)',
                   f'$string_read_plan({state}) = (pstringread)']
    for label, value in (('false', 'PBOOL false'), ('zero', 'PINT 0'), ('float_zero', 'PFLOAT 0')):
        state = f'S_peer_nonnull_{label}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_null ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value({state},porigin_left) = ({value})',
                   f'$string_read_allocated_value({state},porigin_chain,pvalue_base)',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)']
    checks += lines(r'''
expression_empty = NScalarString (BYTES "") metadata_null
expression_empty_left = NExprTernary expression_condition expression_empty expression_false metadata_left
expression_empty_base = NExprBinaryOpCoalesce expression_empty_left expression_chain metadata_base
pcoccurrence_empty* = $pcwalk([PCOCCURRENCE pcpath_base expression_empty_base])
S_peer_empty = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_empty* ++ pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_null (PSTRING eps)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_peer_empty,porigin_left) = (PSTRING_CARRIER INTERNED_STRING eps)
$truth_value(S_peer_empty,PSTRING_CARRIER INTERNED_STRING eps,z_left) = S_peer_empty[.RESULT = KNOWN (PBOOL false)]
$string_read_allocated_value(S_peer_empty,porigin_chain,pvalue_base)
~$string_read_allocated_base(S_peer_empty,porigin_base,pvalue_base)
$string_read_plan(S_peer_empty) = eps
S_peer_forged_null = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_left z_left true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_left PNULL) :: ppool.CONSTANTS]]]
$compiled_read(S_peer_forged_null,porigin_left) = (PNULL)
$string_read_runtime_value(S_peer_forged_null,porigin_left) = eps
~$string_read_allocated_base(S_peer_forged_null,porigin_base,pvalue_base)
$origin_node(S_capture.SOURCES,porigin_key) = (expression_cv)
$coalesce_quiet_operand(expression_cv)
expression_cv_base = NExprBinaryOpCoalesce expression_cv expression_chain metadata_base
pcoccurrence_cv* = $pcwalk([PCOCCURRENCE pcpath_base expression_cv_base])
S_peer_cv = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_cv* ++ pcunit.OCCURRENCES]]][.STORE[n_key] = DEFINED PNULL]
S_peer_cv_read = $resolve_at(S_peer_cv,poperand,z_key)
S_peer_cv_read.RESULT = KNOWN PNULL
$string_read_allocated_value(S_peer_cv,porigin_chain,pvalue_base)
~$string_read_allocated_base(S_peer_cv,porigin_base,pvalue_base)
expression_cv_right_base = NExprBinaryOpCoalesce expression_left expression_cv metadata_base
pcoccurrence_cv_right* = $pcwalk([PCOCCURRENCE pcpath_base expression_cv_right_base])
S_peer_cv_right = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_cv_right* ++ pcunit.OCCURRENCES]]][.STORE[n_key] = DEFINED pvalue_base]
S_peer_cv_right_read = $resolve_at(S_peer_cv_right,poperand,z_key)
S_peer_cv_right_read.RESULT = KNOWN pvalue_base
~$string_read_allocated_value(S_peer_cv_right,porigin_chain,pvalue_base)
~$string_read_allocated_base(S_peer_cv_right,porigin_base,pvalue_base)
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
$string_read_raw_saved(S,pstringread[.KEYREF = false]) = (3)
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
S_peer_abrupt = S_capture[.COMPLETION = UNSUPPORTED "peer-control"]
$string_read_runtime_value(S_peer_abrupt,porigin_left) = eps
~$string_read_allocated_value(S_peer_abrupt,porigin_chain,pvalue_base)
$string_read_allocated_base(S_peer_abrupt,porigin_base,pvalue_base)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    control = prefix(control_program, control_filename_b64).split('def $main() = true\n', 1)[1]
    control = control.replace('$compiled_read(S_capture,porigin_left) = eps',
                              '$compiled_read(S_capture,porigin_left) = (PNULL)')
    start = control.index('  -- if expression_left = NExprTernary')
    end = control.index('  -- PhpStep: S_capture ~> S_dispatch', start)
    control_checks = lines(r'''
expression_left = NExprConstFetch name_literal metadata_literal
name_literal = NName (BYTES text_literal) metadata_literal_name
$ptlc($base64(text_literal)) = $ptascii("null")
porigin_left = PORIGIN n_unit pcpath_left
$code_expression(pcode.EXPRESSIONS,pcpath_left) = ((z_literal,true))
$(z_literal > 0)
$compiled_precision(S_capture,(porigin_left)) = (14)
$compiled_identity_value(S_capture,porigin_left) = (PNULL)
$string_read_runtime_value(S_capture,porigin_left) = (PNULL)
~$coalesce_quiet_operand(expression_left)
$string_read_allocated_base(S_capture,porigin_base,pvalue_base)
|S_capture.STRINGDATA| = 4
''')
    control = control[:start] + ''.join('  -- if ' + check + '\n' for check in control_checks) + control[end:]
    body = body.replace('dec $main() : bool',
                        'dec $peer_literal_null() : bool\ndef $peer_literal_null() = true\n' + control + '\ndec $main() : bool')
    body += '  -- if $peer_literal_null()\n'
    main = body.split('def $main() = true\n', 1)[1]
    return body, len(main.splitlines()) + len(control.splitlines()), len(checks)
