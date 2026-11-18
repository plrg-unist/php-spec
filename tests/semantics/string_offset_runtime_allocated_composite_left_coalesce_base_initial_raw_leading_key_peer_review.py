"""Independent composite-left COALESCE recursion and unchanged guard checks."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_composite_left_coalesce_base_initial_raw_leading_key_review import render as render_author


def prefix(program, filename_b64, reference):
    body, _, _ = render_author(program, filename_b64, reference=reference)
    return body[:body.index('  -- if S_later =')]


def render(program, filename_b64, direct_program, direct_filename_b64, control_program, control_filename_b64):
    body = prefix(program, filename_b64, True)
    checks = []
    for node in ('base', 'left', 'chain', 'inner', 'cast'):
        for label, line, flag in [('line', '0', 'false'), ('folded', f'z_{node}', 'true')]:
            state = f'S_peer_{node}_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} {line} {flag}) :: pcode.EXPRESSIONS]]]',
                       f'~$string_read_allocated_base({state},porigin_base,pvalue_base)',
                       f'$string_read_plan({state}) = eps']
    for node in ('base', 'left', 'chain', 'inner', 'cast', 'integer'):
        state = f'S_peer_precision_{node}'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'~$string_read_allocated_base({state},porigin_base,pvalue_base)']
    checks += lines(r'''
porigin_skipped = PORIGIN n_unit pcpath_skipped
porigin_right = PORIGIN n_unit pcpath_right
S_peer_left_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_left (NExprTernary expression_chain ABSENT expression_skipped eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_left_source,porigin_left,pvalue_base)
~$string_read_allocated_base(S_peer_left_source,porigin_base,pvalue_base)
$string_read_plan(S_peer_left_source) = eps
S_peer_selected_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_chain (NExprBinaryOpConcat expression_inner expression_suffix eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_selected_source,porigin_chain,pvalue_base)
~$string_read_allocated_base(S_peer_selected_source,porigin_left,pvalue_base)
~$string_read_allocated_base(S_peer_selected_source,porigin_base,pvalue_base)
S_peer_left_skipped_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_skipped_atom (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_left_skipped_source,porigin_chain,pvalue_base)
~$string_read_allocated_base(S_peer_left_skipped_source,porigin_left,pvalue_base)
~$string_read_allocated_base(S_peer_left_skipped_source,porigin_base,pvalue_base)
S_peer_right_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right (NExprTernary expression_right_condition expression_right_true expression_right_false eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_right_source,porigin_left,pvalue_base)
~$string_read_allocated_base(S_peer_right_source,porigin_base,pvalue_base)
$string_read_plan(S_peer_right_source) = eps
S_peer_right_descendant = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_right_atom (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_right_descendant,porigin_base,pvalue_base)
$string_read_plan(S_peer_right_descendant) = (pstringread)
S_peer_right_noise = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PINT 77)) :: (PCCPRECISION pcpath_right 17) :: ppool.CONSTANTS]]]
$compiled_read(S_peer_right_noise,porigin_right) = eps
$string_read_allocated_base(S_peer_right_noise,porigin_base,pvalue_base)
$string_read_plan(S_peer_right_noise) = (pstringread)
S_peer_right_read = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 0 true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right PNULL) :: ppool.CONSTANTS]]]
$compiled_read(S_peer_right_read,porigin_right) = (PNULL)
$string_read_allocated_base(S_peer_right_read,porigin_left,pvalue_base)
~$string_read_allocated_base(S_peer_right_read,porigin_base,pvalue_base)
$string_read_plan(S_peer_right_read) = eps
S_peer_root_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base PNULL) :: ppool.CONSTANTS]]]
$compiled_read(S_peer_root_pool,porigin_base) = eps
$string_read_allocated_base(S_peer_root_pool,porigin_base,pvalue_base)
expression_cv = NExprVariable (BYTES "Z290") metadata_left
expression_cv_base = NExprBinaryOpCoalesce expression_cv expression_right metadata_base
pcoccurrence_cv* = $pcwalk([PCOCCURRENCE pcpath_base expression_cv_base])
S_peer_cv = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_cv* ++ pcunit.OCCURRENCES]]][.STORE[n_got] = DEFINED pvalue_base]
S_peer_cv_read = $resolve_at(S_peer_cv,VARIABLE ($ptascii("got")) z_key,z_key)
S_peer_cv_read.RESULT = KNOWN pvalue_base
S_peer_cv_read.EVENTS = S_peer_cv.EVENTS
$string_carrier_valid(S_peer_cv,pvalue_base)
~$string_read_allocated_base(S_peer_cv,porigin_left,pvalue_base)
~$string_read_allocated_base(S_peer_cv,porigin_base,pvalue_base)
$string_read_raw_capture(S_peer_cv,poperand,pvalue_base) = eps
''')
    precision_entries = ' :: '.join(f'(PCCPRECISION pcpath_{name} 17)' for name in ('left', 'chain', 'inner', 'cast', 'integer', 'atom', 'inner_suffix', 'suffix'))
    checks += [f'S_peer_left17 = S_capture[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true][.POOLS = [ppool[.CONSTANTS = {precision_entries} :: ppool.CONSTANTS]]]',
               '$precision_value(S_peer_left17) = 17',
               '$string_read_allocated_base(S_peer_left17,porigin_left,pvalue_base)',
               '$compiled_precision(S_peer_left17,(porigin_base)) = (14)',
               '~$string_read_allocated_base(S_peer_left17,porigin_base,pvalue_base)',
               'S_peer_all17 = S_peer_left17[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_base 17) :: ' + precision_entries + ' :: ppool.CONSTANTS]]]',
               '$string_read_allocated_base(S_peer_all17,porigin_base,pvalue_base)']
    checks += lines(r'''
S_peer_abrupt = S_capture[.COMPLETION = UNSUPPORTED "peer-control"]
~$string_read_allocated_value(S_peer_abrupt,porigin_chain,pvalue_base)
$string_read_allocated_base(S_peer_abrupt,porigin_left,pvalue_base)
$string_read_allocated_base(S_peer_abrupt,porigin_base,pvalue_base)
S_peer_clone = S_capture[.STRINGDATA = S_capture.STRINGDATA ++ [$ptascii("-10.5bcde")]]
pvalue_clone = PSTRING_CARRIER (REQUEST_STRING 4) ($ptascii("-10.5bcde"))
$string_carrier_valid(S_peer_clone,pvalue_clone)
~$string_read_allocated_base(S_peer_clone,porigin_left,pvalue_clone)
~$string_read_allocated_base(S_peer_clone,porigin_base,pvalue_clone)
$string_read_raw_capture(S_peer_clone[.RESULT = KNOWN pvalue_clone],poperand,pvalue_clone) = eps
~$string_read_allocated_base(S_capture,porigin_base,PNULL)
~$string_read_allocated_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("-10.5bcde")))
S_peer_suffix = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("callback"),$ptascii("-10.5bcde")]]
$heap_graph(S_peer_suffix) = $heap_graph(S)
$string_read_raw_saved(S_peer_suffix,pstringread) = (3)
$string_read_ready(S_peer_suffix,pstringread)
$string_read_resume(S_peer_suffix,pstringread) = S_peer_suffix[.TODO = ptask_tail*][.RESULT = KNOWN pvalue_byte][.BASE = BASE_VALUE (KNOWN PNULL)]
$string_read_raw_saved(S,pstringread[.READ.OWNERS = BASE_VALUE (KNOWN PNULL)]) = eps
$string_read_raw_saved(S,pstringread[.KEYCELL = eps]) = eps
S_peer_nul = S_capture[.STRINGDATA = [$ptascii("512"),$ptascii("-10.5"),$ptascii("-10.5bc"),[45,49,48,46,53,98,99,0,100,101]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING 3) ([45,49,48,46,53,98,99,0,100,101])
$string_carrier_valid(S_peer_nul,pvalue_nul)
~$string_read_allocated_base(S_peer_nul,porigin_base,pvalue_nul)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    direct = prefix(direct_program, direct_filename_b64, False).split('def $main() = true\n', 1)[1]
    control = prefix(control_program, control_filename_b64, True).split('def $main() = true\n', 1)[1]
    control = control.replace('$origin_child((porigin_left),', '$origin_child((porigin_inner_left),')
    old = 'expression_left = NExprTernary expression_chain ABSENT expression_skipped metadata_left'
    assert control.count(old) == 1
    replacement = lines(r'''
expression_left = NExprBinaryOpCoalesce expression_inner_left expression_inner_right metadata_inner_coalesce
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_inner_left)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_inner_right)
$origin_node(S_capture.SOURCES,porigin_inner_left) = (expression_inner_left)
expression_inner_left = NExprTernary expression_chain ABSENT expression_skipped metadata_left
''')
    control = control.replace(old, '\n  -- if '.join(replacement))
    composed = lines(r'''
porigin_inner_left = PORIGIN n_unit pcpath_inner_left
$code_expression(pcode.EXPRESSIONS,pcpath_inner_left) = ((z_inner_left,false))
$(z_inner_left > 0)
$compiled_precision(S_capture,(porigin_inner_left)) = (14)
$compiled_read(S_capture,porigin_inner_left) = eps
~$string_read_allocated_value(S_capture,porigin_inner_left,pvalue_base)
$string_read_allocated_base(S_capture,porigin_inner_left,pvalue_base)
~$string_read_allocated_value(S_capture,porigin_left,pvalue_base)
$string_read_allocated_base(S_capture,porigin_left,pvalue_base)
$string_read_allocated_base(S_capture,porigin_base,pvalue_base)
$origin_node(S_capture.SOURCES,porigin_inner_right) = (NExprTernary expression_inner_condition expression_inner_yes expression_inner_no metadata_inner_right)
$origin_child((porigin_inner_right),[PCFIELD 0]) = (porigin_inner_guard)
$origin_child((porigin_inner_guard),[PCFIELD 0]) = (porigin_inner_atom)
$origin_node(S_capture.SOURCES,porigin_inner_atom) = (NScalarInt (INTEGER 1) metadata_inner_atom)
porigin_inner_right = PORIGIN n_unit pcpath_inner_right
porigin_inner_atom = PORIGIN n_unit pcpath_inner_atom
S_peer_inner_right_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_inner_right (NExprTernary expression_inner_condition expression_inner_yes expression_inner_no eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_inner_right_source,porigin_inner_left,pvalue_base)
~$string_read_allocated_base(S_peer_inner_right_source,porigin_left,pvalue_base)
~$string_read_allocated_base(S_peer_inner_right_source,porigin_base,pvalue_base)
S_peer_inner_descendant = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_inner_atom (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_inner_descendant,porigin_left,pvalue_base)
$string_read_allocated_base(S_peer_inner_descendant,porigin_base,pvalue_base)
''')
    control += ''.join('  -- if ' + check + '\n' for check in composed)
    extra = 'dec $peer_direct_original() : bool\ndef $peer_direct_original() = true\n' + direct
    extra += '\ndec $peer_nested_coalesce() : bool\ndef $peer_nested_coalesce() = true\n' + control
    body = body.replace('dec $main() : bool', extra + '\ndec $main() : bool')
    body += '  -- if $peer_direct_original()\n  -- if $peer_nested_coalesce()\n'
    main = body.split('def $main() = true\n', 1)[1]
    return body, len(main.splitlines()) + len(direct.splitlines()) + len(control.splitlines()), len(checks) + len(composed)
