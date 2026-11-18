"""Independent falsey shorthand selection, ownership and BASE composition."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_falsey_shorthand_base_initial_raw_leading_key_review import render as render_author


def prefix(program, filename_b64, reference):
    body, _, _ = render_author(program, filename_b64, reference=reference)
    return body[:body.index('  -- if S_later =')]


def render(program, filename_b64, int_program, int_filename_b64, control_program, control_filename_b64):
    body = prefix(program, filename_b64, True)
    checks = ['porigin_skipped = PORIGIN n_unit pcpath_skipped']
    for node in ('base', 'condition', 'chain', 'inner', 'cast'):
        for label, line, flag in [('line', '0', 'false'), ('folded', f'z_{node}', 'true')]:
            state = f'S_peer_{node}_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} {line} {flag}) :: pcode.EXPRESSIONS]]]',
                       f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                       f'$string_read_plan({state}) = eps']
    for node in ('base', 'condition', 'condition_atom', 'chain', 'inner', 'cast', 'integer'):
        state = f'S_peer_precision_{node}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)']
    for node, expression in (
            ('condition', 'NExprCastString expression_condition_atom eps'),
            ('condition_atom', 'NScalarInt (INTEGER 0) eps'),
            ('chain', 'NExprBinaryOpConcat expression_inner expression_suffix eps'),
            ('integer', 'NExprUnaryMinus expression_atom eps'),
            ('atom', 'NScalarFloat (FLOAT "4025000000000000") eps')):
        state = f'S_peer_source_{node}'
        checks += [f'{state} = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{node} ({expression})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)']
    checks += lines(r'''
S_peer_absent_facts = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_skipped 0 true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_skipped (PINT 77)) :: (PCCPRECISION pcpath_skipped 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_peer_absent_facts,porigin_base,pvalue_base)
$string_read_plan(S_peer_absent_facts) = (pstringread)
S_peer_root_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base (PSTRING ($ptascii("wrong")))) :: ppool.CONSTANTS]]]
$compiled_read(S_peer_root_pool,porigin_base) = eps
$string_read_allocated_base(S_peer_root_pool,porigin_base,pvalue_base)
S_peer_cond_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_condition (PINT 1)) :: ppool.CONSTANTS]]]
$compiled_read(S_peer_cond_pool,porigin_condition) = eps
$string_read_runtime_value(S_peer_cond_pool,porigin_condition) = (PSTRING_CARRIER INTERNED_STRING ($ptascii("0")))
$string_read_allocated_base(S_peer_cond_pool,porigin_base,pvalue_base)
expression_cv = NExprVariable (BYTES "Z290") metadata_condition
expression_cv_condition_base = NExprTernary expression_cv ABSENT expression_chain metadata_base
pcoccurrence_cv_condition* = $pcwalk([PCOCCURRENCE pcpath_base expression_cv_condition_base])
S_peer_cv_condition = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_cv_condition* ++ pcunit.OCCURRENCES]]][.STORE[n_got] = DEFINED (PINT 0)]
S_peer_cv_read = $resolve_at(S_peer_cv_condition,VARIABLE ($ptascii("got")) z_key,z_key)
S_peer_cv_read.RESULT = KNOWN (PINT 0)
S_peer_cv_read.EVENTS = S_peer_cv_condition.EVENTS
$string_read_runtime_value(S_peer_cv_condition,porigin_condition) = eps
$string_read_allocated_base(S_peer_cv_condition,porigin_chain,pvalue_base)
~$string_read_allocated_base(S_peer_cv_condition,porigin_base,pvalue_base)
expression_cv_selected_base = NExprTernary expression_condition ABSENT expression_cv metadata_base
pcoccurrence_cv_selected* = $pcwalk([PCOCCURRENCE pcpath_base expression_cv_selected_base])
S_peer_cv_selected = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_cv_selected* ++ pcunit.OCCURRENCES]]][.STORE[n_got] = DEFINED pvalue_base]
S_peer_cv_selected_read = $resolve_at(S_peer_cv_selected,VARIABLE ($ptascii("got")) z_key,z_key)
S_peer_cv_selected_read.RESULT = KNOWN pvalue_base
$string_carrier_valid(S_peer_cv_selected,pvalue_base)
~$string_read_allocated_base(S_peer_cv_selected,porigin_chain,pvalue_base)
~$string_read_allocated_base(S_peer_cv_selected,porigin_base,pvalue_base)
expression_nan = NScalarFloat (FLOAT "7ff8000000000000") metadata_condition
expression_nan_base = NExprTernary expression_nan ABSENT expression_chain metadata_base
pcoccurrence_nan* = $pcwalk([PCOCCURRENCE pcpath_base expression_nan_base])
n_nan = $hex_bits("7ff8000000000000",0)
S_peer_nan = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_nan* ++ pcunit.OCCURRENCES]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_condition z_condition true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_condition (PFLOAT n_nan)) :: ppool.CONSTANTS]]]
$number_bool(NFLOAT n_nan) = (true,true)
$string_read_runtime_value(S_peer_nan,porigin_condition) = eps
$truth_value(S_peer_nan,PFLOAT n_nan,z_base) =/= S_peer_nan[.RESULT = KNOWN (PBOOL true)]
$string_read_allocated_base(S_peer_nan,porigin_chain,pvalue_base)
~$string_read_allocated_base(S_peer_nan,porigin_base,pvalue_base)
expression_truthy_atom = NScalarInt (INTEGER 1) metadata_condition_atom
expression_truthy_condition = NExprCastString expression_truthy_atom metadata_condition
expression_truthy_base = NExprTernary expression_truthy_condition ABSENT expression_chain metadata_base
pcoccurrence_truthy* = $pcwalk([PCOCCURRENCE pcpath_base expression_truthy_base])
S_peer_truthy = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_truthy* ++ pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_condition_atom (PINT 1)) :: ppool.CONSTANTS]]]
pvalue_truthy = PSTRING_CARRIER INTERNED_STRING ($ptascii("1"))
$string_read_runtime_value(S_peer_truthy,porigin_condition) = (pvalue_truthy)
$truth(S_peer_truthy,pvalue_truthy)
$truth_value(S_peer_truthy,pvalue_truthy,z_base) = S_peer_truthy[.RESULT = KNOWN (PBOOL true)]
$string_read_allocated_base(S_peer_truthy,porigin_chain,pvalue_base)
~$string_read_allocated_base(S_peer_truthy,porigin_base,pvalue_base)
$string_read_raw_capture(S_peer_truthy,poperand,pvalue_base) = eps
expression_owned_atom = NScalarFloat (FLOAT "0000000000000000") metadata_condition_atom
expression_owned_condition = NExprCastString expression_owned_atom metadata_condition
expression_owned_base = NExprTernary expression_owned_condition ABSENT expression_chain metadata_base
pcoccurrence_owned* = $pcwalk([PCOCCURRENCE pcpath_base expression_owned_base])
pvalue_owned_condition = PSTRING_CARRIER (REQUEST_STRING 1) ($ptascii("0"))
pvalue_owned_base = PSTRING_CARRIER (REQUEST_STRING 4) ($ptascii("-10.5bcde"))
S_peer_owned = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_owned* ++ pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_condition_atom (PFLOAT 0)) :: ppool.CONSTANTS]]][.STRINGDATA = [$ptascii("512"),$ptascii("0"),$ptascii("-10.5"),$ptascii("-10.5bc"),$ptascii("-10.5bcde")]][.RESULT = KNOWN pvalue_owned_base]
$compiled_identity_value(S_peer_owned,porigin_condition_atom) = (PFLOAT 0)
$string_carrier_valid(S_peer_owned,pvalue_owned_condition)
$string_read_allocated_value(S_peer_owned,porigin_condition,pvalue_owned_condition)
~$truth(S_peer_owned,pvalue_owned_condition)
$truth_value(S_peer_owned,pvalue_owned_condition,z_base) = S_peer_owned[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_peer_owned,porigin_condition) = eps
$string_read_allocated_base(S_peer_owned,porigin_chain,pvalue_owned_base)
~$string_read_allocated_base(S_peer_owned,porigin_base,pvalue_owned_base)
$string_read_raw_capture(S_peer_owned,poperand,pvalue_owned_base) = eps
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
$string_read_runtime_value(S_peer_abrupt,porigin_condition) = eps
$string_read_allocated_base(S_peer_abrupt,porigin_base,pvalue_base)
S_peer_nul = S_capture[.STRINGDATA = [$ptascii("512"),$ptascii("-10.5"),$ptascii("-10.5bc"),[45,49,48,46,53,98,99,0,100,101]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING 3) ([45,49,48,46,53,98,99,0,100,101])
$string_carrier_valid(S_peer_nul,pvalue_nul)
~$string_read_allocated_base(S_peer_nul,porigin_base,pvalue_nul)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    true = prefix(int_program, int_filename_b64, False).split('def $main() = true\n', 1)[1]
    control = prefix(control_program, control_filename_b64, True).split('def $main() = true\n', 1)[1]
    old = 'NExprTernary expression_condition ABSENT expression_chain metadata_base'
    assert control.count(old) == 1
    control = control.replace(old, 'NExprTernary expression_condition ABSENT expression_coalesce metadata_base')
    old = '$origin_child((porigin_base),[PCFIELD 2]) = (porigin_chain)'
    assert control.count(old) == 1
    replacement = lines(r'''
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_coalesce)
$origin_node(S_capture.SOURCES,porigin_coalesce) = (expression_coalesce)
expression_coalesce = NExprBinaryOpCoalesce expression_chain expression_fallback metadata_coalesce
$origin_child((porigin_coalesce),[PCFIELD 0]) = (porigin_chain)
$origin_child((porigin_coalesce),[PCFIELD 1]) = (porigin_fallback)
''')
    control = control.replace(old, '\n  -- if '.join(replacement))
    composed = lines(r'''
porigin_coalesce = PORIGIN n_unit pcpath_coalesce
$code_expression(pcode.EXPRESSIONS,pcpath_coalesce) = ((z_coalesce,false))
$(z_coalesce > 0)
$compiled_precision(S_capture,(porigin_coalesce)) = (14)
$compiled_read(S_capture,porigin_coalesce) = eps
~$string_read_allocated_value(S_capture,porigin_coalesce,pvalue_base)
$string_read_allocated_base(S_capture,porigin_coalesce,pvalue_base)
$string_read_allocated_base(S_capture,porigin_base,pvalue_base)
$origin_node(S_capture.SOURCES,porigin_fallback) = (NExprTernary expression_guard expression_yes expression_no metadata_fallback)
$origin_child((porigin_fallback),[PCFIELD 2]) = (porigin_fallback_no)
$origin_node(S_capture.SOURCES,porigin_fallback_no) = (NScalarString (BYTES text_no) metadata_no)
porigin_fallback_no = PORIGIN n_unit pcpath_fallback_no
porigin_fallback = PORIGIN n_unit pcpath_fallback
S_peer_inner_skip_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_fallback_no (NScalarString (BYTES text_no) eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_inner_skip_source,porigin_coalesce,pvalue_base)
~$string_read_allocated_base(S_peer_inner_skip_source,porigin_base,pvalue_base)
$string_read_plan(S_peer_inner_skip_source) = eps
S_peer_inner_skip_facts = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_fallback 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_fallback (PINT 77)) :: (PCCPRECISION pcpath_fallback 17) :: ppool.CONSTANTS]]]
$string_read_allocated_base(S_peer_inner_skip_facts,porigin_base,pvalue_base)
$string_read_plan(S_peer_inner_skip_facts) = (pstringread)
''')
    control += ''.join('  -- if ' + check + '\n' for check in composed)
    extra = 'dec $peer_int_original() : bool\ndef $peer_int_original() = true\n' + true
    extra += '\ndec $peer_selected_coalesce() : bool\ndef $peer_selected_coalesce() = true\n' + control
    body = body.replace('dec $main() : bool', extra + '\ndec $main() : bool')
    body += '  -- if $peer_int_original()\n  -- if $peer_selected_coalesce()\n'
    main = body.split('def $main() = true\n', 1)[1]
    return body, len(main.splitlines()) + len(true.splitlines()) + len(control.splitlines()), len(checks) + len(composed)
