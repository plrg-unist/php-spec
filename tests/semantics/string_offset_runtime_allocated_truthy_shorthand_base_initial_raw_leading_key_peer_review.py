"""Independent truthy owning shorthand selection and condition refusals."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_truthy_shorthand_base_initial_raw_leading_key_review import render as render_author


def prefix(program, filename_b64, reference):
    body, _, _ = render_author(program, filename_b64, reference=reference)
    return body[:body.index('  -- if S_later =')]


def render(program, filename_b64, direct_program, direct_filename_b64, control_program, control_filename_b64):
    body = prefix(program, filename_b64, True)
    checks = lines(r'''
porigin_absent = PORIGIN n_unit pcpath_absent
porigin_skipped = PORIGIN n_unit pcpath_skipped
porigin_skipped_condition = PORIGIN n_unit pcpath_skipped_condition
porigin_skipped_false = PORIGIN n_unit pcpath_skipped_false
''')
    for node in ('base', 'chain', 'inner', 'cast'):
        for label, line, flag in [('line', '0', 'false'), ('folded', f'z_{node}', 'true')]:
            state = f'S_peer_{node}_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} {line} {flag}) :: pcode.EXPRESSIONS]]]',
                       f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                       f'$string_read_plan({state}) = eps']
    for node in ('base', 'chain', 'inner', 'cast', 'integer'):
        state = f'S_peer_precision_{node}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)']
    for node, expression in (
            ('chain', 'NExprBinaryOpConcat expression_inner expression_suffix eps'),
            ('inner', 'NExprBinaryOpConcat expression_cast expression_inner_suffix eps'),
            ('integer', 'NExprUnaryMinus expression_atom eps'),
            ('atom', 'NScalarFloat (FLOAT "4025000000000000") eps')):
        state = f'S_peer_source_{node}'
        checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{node} ({expression})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)']
    checks += lines(r'''
$string_read_allocated_base(S_peer_source_chain,porigin_chain,pvalue_base)
S_peer_skip_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_skipped_atom (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_skip_source,porigin_chain,pvalue_base)
~$string_read_allocated_base(S_peer_skip_source,porigin_base,pvalue_base)
$string_read_plan(S_peer_skip_source) = eps
S_peer_skip_facts = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_skipped 0 true) :: (CODEEXPR pcpath_skipped_condition 0 false) :: (CODEEXPR pcpath_skipped_atom 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_skipped (PINT 77)) :: (PCCPRECISION pcpath_skipped 17) :: (PCONSTANT pcpath_skipped_atom (PINT 0)) :: (PCCPRECISION pcpath_skipped_atom 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_peer_skip_facts,porigin_base,pvalue_base)
$string_read_plan(S_peer_skip_facts) = (pstringread)
S_peer_absent_facts = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_absent 0 true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_absent (PINT 77)) :: (PCCPRECISION pcpath_absent 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_peer_absent_facts,porigin_base,pvalue_base)
$string_read_plan(S_peer_absent_facts) = (pstringread)
S_peer_root_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base (PSTRING ($ptascii("wrong")))) :: ppool.CONSTANTS]]]
$compiled_read(S_peer_root_pool,porigin_base) = eps
$string_read_allocated_base(S_peer_root_pool,porigin_base,pvalue_base)
S_peer_condition_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_chain (PINT 0)) :: ppool.CONSTANTS]]]
$compiled_read(S_peer_condition_pool,porigin_chain) = eps
$string_read_allocated_base(S_peer_condition_pool,porigin_base,pvalue_base)
expression_cv = NExprVariable (BYTES "Z290") metadata_chain
expression_cv_base = NExprTernary expression_cv ABSENT expression_skipped metadata_base
pcoccurrence_cv* = $pcwalk([PCOCCURRENCE pcpath_base expression_cv_base])
S_peer_cv = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_cv* ++ pcunit.OCCURRENCES]]][.STORE[n_got] = DEFINED pvalue_base]
S_peer_cv_read = $resolve_at(S_peer_cv,VARIABLE ($ptascii("got")) z_key,z_key)
S_peer_cv_read.RESULT = KNOWN pvalue_base
S_peer_cv_read.EVENTS = S_peer_cv.EVENTS
$string_carrier_valid(S_peer_cv,pvalue_base)
~$string_read_allocated_base(S_peer_cv,porigin_chain,pvalue_base)
~$string_read_allocated_base(S_peer_cv,porigin_base,pvalue_base)
expression_false_atom = NScalarFloat (FLOAT "0000000000000000") metadata_inner
expression_false_condition = NExprCastString expression_false_atom metadata_chain
expression_false_base = NExprTernary expression_false_condition ABSENT expression_skipped metadata_base
pcoccurrence_false* = $pcwalk([PCOCCURRENCE pcpath_base expression_false_base])
pvalue_false = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("0"))
S_peer_false = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_false* ++ pcunit.OCCURRENCES]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_inner z_inner true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_inner (PFLOAT 0)) :: ppool.CONSTANTS]]][.STRINGDATA = [$ptascii("512"),$ptascii("0")]][.RESULT = KNOWN pvalue_false]
$compiled_identity_value(S_peer_false,porigin_inner) = (PFLOAT 0)
$string_carrier_valid(S_peer_false,pvalue_false)
$string_read_allocated_value(S_peer_false,porigin_chain,pvalue_false)
$string_read_allocated_base(S_peer_false,porigin_chain,pvalue_false)
~$truth(S_peer_false,pvalue_false)
$truth_value(S_peer_false,pvalue_false,z_base) = S_peer_false[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_peer_false,porigin_chain) = eps
~$string_read_allocated_base(S_peer_false,porigin_base,pvalue_false)
$string_read_raw_capture(S_peer_false,poperand,pvalue_false) = eps
expression_interned_atom = NScalarInt (INTEGER 1) metadata_inner
expression_interned_condition = NExprCastString expression_interned_atom metadata_chain
expression_interned_base = NExprTernary expression_interned_condition ABSENT expression_skipped metadata_base
pcoccurrence_interned* = $pcwalk([PCOCCURRENCE pcpath_base expression_interned_base])
pvalue_interned = PSTRING_CARRIER INTERNED_STRING ($ptascii("1"))
S_peer_interned = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_interned* ++ pcunit.OCCURRENCES]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_inner z_inner true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_inner (PINT 1)) :: ppool.CONSTANTS]]][.RESULT = KNOWN pvalue_interned]
$string_read_runtime_value(S_peer_interned,porigin_chain) = (pvalue_interned)
$truth(S_peer_interned,pvalue_interned)
$truth_value(S_peer_interned,pvalue_interned,z_base) = S_peer_interned[.RESULT = KNOWN (PBOOL true)]
~$string_read_allocated_base(S_peer_interned,porigin_chain,pvalue_interned)
~$string_read_allocated_base(S_peer_interned,porigin_base,pvalue_interned)
expression_nan_atom = NScalarFloat (FLOAT "7ff8000000000000") metadata_inner
expression_nan_condition = NExprCastString expression_nan_atom metadata_chain
expression_nan_base = NExprTernary expression_nan_condition ABSENT expression_skipped metadata_base
pcoccurrence_nan* = $pcwalk([PCOCCURRENCE pcpath_base expression_nan_base])
n_nan = $hex_bits("7ff8000000000000",0)
pvalue_nan = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("NAN"))
S_peer_nan = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_nan* ++ pcunit.OCCURRENCES]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_inner z_inner true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_inner (PFLOAT n_nan)) :: ppool.CONSTANTS]]][.STRINGDATA = [$ptascii("512"),$ptascii("NAN")]][.RESULT = KNOWN pvalue_nan]
$compiled_read(S_peer_nan,porigin_inner) = (PFLOAT n_nan)
$number_bool(NFLOAT n_nan) = (true,true)
$string_read_runtime_value(S_peer_nan,porigin_inner) = eps
$string_carrier_valid(S_peer_nan,pvalue_nan)
~$string_read_allocated_value(S_peer_nan,porigin_chain,pvalue_nan)
~$string_read_allocated_base(S_peer_nan,porigin_base,pvalue_nan)
S_peer_clone = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("-10.5bcde")]]
pvalue_clone = PSTRING_CARRIER (REQUEST_STRING 4) ($ptascii("-10.5bcde"))
$string_carrier_valid(S_peer_clone,pvalue_clone)
~$string_read_allocated_base(S_peer_clone,porigin_base,pvalue_clone)
$string_read_raw_capture(S_peer_clone[.RESULT = KNOWN pvalue_clone],poperand,pvalue_clone) = eps
S_peer_suffix = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("callback"),$ptascii("-10.5bcde")]]
$heap_graph(S_peer_suffix) = $heap_graph(S)
$string_read_raw_saved(S_peer_suffix,pstringread) = (3)
$string_read_ready(S_peer_suffix,pstringread)
$string_read_resume(S_peer_suffix,pstringread) = S_peer_suffix[.TODO = ptask_tail*][.RESULT = KNOWN pvalue_byte][.BASE = BASE_VALUE (KNOWN PNULL)]
$string_read_raw_saved(S,pstringread[.READ.OWNERS = BASE_VALUE (KNOWN PNULL)]) = eps
$string_read_raw_saved(S,pstringread[.KEYCELL = eps]) = eps
S_peer_abrupt = S_capture[.COMPLETION = UNSUPPORTED "peer-control"]
~$string_read_allocated_value(S_peer_abrupt,porigin_chain,pvalue_base)
$string_read_allocated_base(S_peer_abrupt,porigin_chain,pvalue_base)
$string_read_allocated_base(S_peer_abrupt,porigin_base,pvalue_base)
S_peer_nul = S_capture[.STRINGDATA = [$ptascii("512"),$ptascii("-10.5"),$ptascii("-10.5bc"),[45,49,48,46,53,98,99,0,100,101]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING 3) ([45,49,48,46,53,98,99,0,100,101])
$string_carrier_valid(S_peer_nul,pvalue_nul)
~$string_read_allocated_base(S_peer_nul,porigin_base,pvalue_nul)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    direct = prefix(direct_program, direct_filename_b64, False).split('def $main() = true\n', 1)[1]
    control = prefix(control_program, control_filename_b64, True).split('def $main() = true\n', 1)[1]
    old = 'NExprTernary expression_chain ABSENT expression_skipped metadata_base'
    assert control.count(old) == 1
    control = control.replace(old, 'NExprTernary expression_coalesce ABSENT expression_skipped metadata_base')
    old = '$origin_child((porigin_base),[PCFIELD 0]) = (porigin_chain)'
    assert control.count(old) == 1
    replacement = lines(r'''
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_coalesce)
$origin_node(S_capture.SOURCES,porigin_coalesce) = (expression_coalesce)
expression_coalesce = NExprBinaryOpCoalesce expression_chain expression_coalesce_skip metadata_coalesce
$origin_child((porigin_coalesce),[PCFIELD 0]) = (porigin_chain)
$origin_child((porigin_coalesce),[PCFIELD 1]) = (porigin_coalesce_skip)
''')
    control = control.replace(old, '\n  -- if '.join(replacement))
    composed = lines(r'''
porigin_coalesce = PORIGIN n_unit pcpath_coalesce
$code_expression(pcode.EXPRESSIONS,pcpath_coalesce) = ((z_coalesce,false))
$(z_coalesce > 0)
$compiled_precision(S_capture,(porigin_coalesce)) = (14)
$compiled_read(S_capture,porigin_coalesce) = eps
~$string_read_allocated_value(S_capture,porigin_coalesce,pvalue_base)
$string_read_runtime_value(S_capture,porigin_coalesce) = eps
$string_read_allocated_base(S_capture,porigin_coalesce,pvalue_base)
$string_read_allocated_base(S_capture,porigin_base,pvalue_base)
$origin_node(S_capture.SOURCES,porigin_coalesce_skip) = (NExprTernary expression_coalesce_guard expression_coalesce_yes expression_coalesce_no metadata_coalesce_skip)
$origin_child((porigin_coalesce_skip),[PCFIELD 2]) = (porigin_coalesce_no)
$origin_node(S_capture.SOURCES,porigin_coalesce_no) = (NScalarString (BYTES text_coalesce_no) metadata_coalesce_no)
porigin_coalesce_no = PORIGIN n_unit pcpath_coalesce_no
porigin_coalesce_skip = PORIGIN n_unit pcpath_coalesce_skip
S_peer_inner_skip_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_coalesce_no (NScalarString (BYTES text_coalesce_no) eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_inner_skip_source,porigin_coalesce,pvalue_base)
~$string_read_allocated_base(S_peer_inner_skip_source,porigin_base,pvalue_base)
$string_read_plan(S_peer_inner_skip_source) = eps
S_peer_inner_skip_facts = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_coalesce_skip 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_coalesce_skip (PINT 77)) :: (PCCPRECISION pcpath_coalesce_skip 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_peer_inner_skip_facts,porigin_base,pvalue_base)
$string_read_plan(S_peer_inner_skip_facts) = (pstringread)
''')
    control += ''.join('  -- if ' + check + '\n' for check in composed)
    extra = 'dec $peer_direct_original() : bool\ndef $peer_direct_original() = true\n' + direct
    extra += '\ndec $peer_selected_coalesce() : bool\ndef $peer_selected_coalesce() = true\n' + control
    body = body.replace('dec $main() : bool', extra + '\ndec $main() : bool')
    body += '  -- if $peer_direct_original()\n  -- if $peer_selected_coalesce()\n'
    main = body.split('def $main() = true\n', 1)[1]
    return body, len(main.splitlines()) + len(direct.splitlines()) + len(control.splitlines()), len(checks) + len(composed)
