"""Independent composite-left CONCAT prefix, SOURCE and saved-owner review."""

from string_offset_retained_carrier_protocol import lines
from string_offset_runtime_allocated_composite_left_concat_base_initial_raw_leading_key_review import render as render_author


def prefix(program, filename_b64, reference=True):
    body, _, _ = render_author(program, filename_b64, reference=reference)
    return body[:body.index('  -- if S_later =')]


def render(program, filename_b64, direct_program, direct_filename_b64, control_program, control_filename_b64):
    body = prefix(program, filename_b64)
    start = body.index('def $retained_frontier(S, 0) = true\n')
    end = body.index('def $retained_frontier(S, 1)', start)
    body = body[:start] + '''def $retained_frontier(S, 0) = true
  -- if S.TODO = (KEY_READ_DIM poperand z KEY_R) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue_base
  -- if pvalue_base <- [PSTRING_CARRIER (REQUEST_STRING 2) ($ptascii("0YZ")),PSTRING_CARRIER (REQUEST_STRING 4) ($ptascii("-10.5bcdefg"))]
  -- if poperand = VARIABLE ($ptascii("key")) z
''' + body[end:]
    checks = []
    for node in ('base', 'left', 'selected', 'chain', 'inner', 'cast'):
        for label, line, folded in (('line', '0', 'false'), ('folded', f'z_{node}', 'true')):
            state = f'S_peer_{node}_{label}'
            checks += [f'{state} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{node} {line} {folded}) :: pcode.EXPRESSIONS]]]',
                       f'~$string_read_allocated_value({state},porigin_base,pvalue_base)',
                       f'$string_read_plan({state}) = eps']
    for node in ('base', 'left', 'right', 'selected', 'chain', 'inner', 'cast', 'number', 'atom'):
        state = 'S_peer_precision_' + node
        # The folded negative FLOAT uses NUMBER's precision, not its raw atom's.
        refusal = '' if node == 'atom' else '~'
        checks += [f'{state} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{node} 17) :: ppool.CONSTANTS]]]',
                   f'{refusal}$string_read_allocated_value({state},porigin_base,pvalue_base)']
    checks += lines(r'''
expression_outer_skipped = NExprTernary expression_unused_condition expression_unused_true expression_unused_false metadata_unused
$origin_child((porigin_outer_skipped),[PCFIELD 0]) = (porigin_unused_condition)
$origin_child((porigin_unused_condition),[PCFIELD 0]) = (porigin_unused_atom)
porigin_unused_atom = PORIGIN n_unit pcpath_unused_atom
$origin_node(S_capture.SOURCES,porigin_unused_atom) = (NScalarInt (INTEGER 1) metadata_unused_atom)
S_peer_unused_descendant = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_unused_atom (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_unused_descendant,porigin_left,pvalue_left)
$string_read_allocated_value(S_peer_unused_descendant,porigin_base,pvalue_base)
$string_read_plan(S_peer_unused_descendant) = (pstringread)
S_peer_left_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_left (NExprBinaryOpCoalesce expression_selected expression_outer_skipped eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_left_source,porigin_left,pvalue_left)
~$string_read_allocated_value(S_peer_left_source,porigin_base,pvalue_base)
S_peer_unused_root = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_outer_skipped (NExprTernary expression_unused_condition expression_unused_true expression_unused_false eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_unused_root,porigin_selected,pvalue_left)
~$string_read_allocated_base(S_peer_unused_root,porigin_left,pvalue_left)
~$string_read_allocated_value(S_peer_unused_root,porigin_base,pvalue_base)
S_peer_unused_read = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_outer_skipped 0 true) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_outer_skipped PNULL) :: ppool.CONSTANTS]]]
$compiled_read(S_peer_unused_read,porigin_outer_skipped) = (PNULL)
$string_read_allocated_base(S_peer_unused_read,porigin_selected,pvalue_left)
~$string_read_allocated_base(S_peer_unused_read,porigin_left,pvalue_left)
~$string_read_allocated_value(S_peer_unused_read,porigin_base,pvalue_base)
expression_skipped = NExprTernary expression_skipped_condition expression_skipped_true expression_skipped_false metadata_skipped
$origin_child((porigin_skipped),[PCFIELD 0]) = (porigin_skipped_condition)
$origin_child((porigin_skipped_condition),[PCFIELD 0]) = (porigin_skipped_atom)
porigin_skipped_atom = PORIGIN n_unit pcpath_skipped_atom
$origin_node(S_capture.SOURCES,porigin_skipped_atom) = (NScalarInt (INTEGER 1) metadata_skipped_atom)
S_peer_skipped_descendant = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_skipped_atom (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_value(S_peer_skipped_descendant,porigin_chain,pvalue_left)
~$string_read_allocated_base(S_peer_skipped_descendant,porigin_selected,pvalue_left)
~$string_read_allocated_value(S_peer_skipped_descendant,porigin_base,pvalue_base)
S_peer_root_pool = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_base PNULL) :: ppool.CONSTANTS]]]
$compiled_read(S_peer_root_pool,porigin_base) = eps
$string_read_allocated_value(S_peer_root_pool,porigin_base,pvalue_base)
S_peer_abrupt = S_capture[.COMPLETION = UNSUPPORTED "peer-control"]
~$string_read_allocated_value(S_peer_abrupt,porigin_base,pvalue_base)
$string_read_allocated_base(S_peer_abrupt,porigin_base,pvalue_base)
S_peer_constant = S_capture[.CONSTCONTEXT = ({ORIGIN porigin_base,LINE z_key,FACTS eps})]
~$string_read_allocated_value(S_peer_constant,porigin_base,pvalue_base)
~$string_read_allocated_base(S_peer_constant,porigin_base,pvalue_base)
expression_cv = NExprVariable (BYTES "Z290") metadata_left
expression_cv_base = NExprBinaryOpConcat expression_cv expression_right metadata_base
pcoccurrence_peer_cv* = $pcwalk([PCOCCURRENCE pcpath_base expression_cv_base])
S_peer_cv = S_capture[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_peer_cv* ++ pcunit.OCCURRENCES]]][.STORE[n_got] = DEFINED pvalue_left]
S_peer_cv_read = $resolve_at(S_peer_cv,VARIABLE ($ptascii("got")) z_key,z_key)
S_peer_cv_read.RESULT = KNOWN pvalue_left
S_peer_cv_read.EVENTS = S_peer_cv.EVENTS
~$string_read_allocated_base(S_peer_cv,porigin_left,pvalue_left)
~$string_read_allocated_value(S_peer_cv,porigin_base,pvalue_base)
''')
    left_nodes = ('left', 'selected', 'chain', 'inner', 'cast', 'number', 'atom', 'inner_suffix', 'suffix')
    entries = ' :: '.join(f'(PCCPRECISION pcpath_{node} 17)' for node in left_nodes)
    checks += [f'S_peer_left17 = S_capture[.PRECISIONINI = $ptascii("17")][.PRECISIONMODIFIED = true][.POOLS = [ppool[.CONSTANTS = {entries} :: ppool.CONSTANTS]]]',
               '$precision_value(S_peer_left17) = 17',
               '$string_read_allocated_base(S_peer_left17,porigin_left,pvalue_left)',
               '~$string_read_allocated_value(S_peer_left17,porigin_base,pvalue_base)',
               'S_peer_all17 = S_peer_left17[.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_base 17) :: (PCCPRECISION pcpath_right 17) :: ' + entries + ' :: ppool.CONSTANTS]]]',
               '$string_read_allocated_value(S_peer_all17,porigin_base,pvalue_base)']
    checks += lines(r'''
S_peer_prefix = S_capture[.STRINGDATA = [$ptascii("512"),$ptascii("-10.5"),$ptascii("-10.5bc"),$ptascii("wrong"),$ptascii("-10.5bcdefg")]]
$string_carrier_valid(S_peer_prefix,pvalue_base)
~$string_carrier_valid(S_peer_prefix,pvalue_left)
~$string_read_allocated_value(S_peer_prefix,porigin_base,pvalue_base)
$string_read_raw_capture(S_peer_prefix,poperand,pvalue_base) = eps
S_peer_later = S[.STRINGDATA = S.STRINGDATA ++ [$ptascii("callback"),$ptascii("-10.5bcdefg")]]
$heap_graph(S_peer_later) = $heap_graph(S)
$string_read_raw_saved(S_peer_later,pstringread) = (9)
$string_read_ready(S_peer_later,pstringread)
$string_read_resume(S_peer_later,pstringread) = S_peer_later[.TODO = ptask_tail*][.RESULT = KNOWN pvalue_byte][.BASE = BASE_VALUE (KNOWN PNULL)]
pvalue_duplicate = PSTRING_CARRIER (REQUEST_STRING 6) ($ptascii("-10.5bcdefg"))
$string_carrier_valid(S_peer_later,pvalue_duplicate)
$string_same(pvalue_base,pvalue_duplicate) = (false)
$string_read_raw_saved(S_peer_later,pstringread[.READ.BASE = pvalue_duplicate]) = eps
~$string_read_provider_ready(S_peer_later,pstringread[.READ.BASE = pvalue_duplicate])
$string_read_raw_saved(S,pstringread[.READ.OWNERS = BASE_VALUE (KNOWN pvalue_left)]) = eps
$string_read_raw_saved(S,pstringread[.KEYCELL = eps]) = eps
S_peer_nul = S_capture[.STRINGDATA = [$ptascii("512"),$ptascii("-10.5"),$ptascii("-10.5bc"),$ptascii("-10.5bcde"),[45,49,48,46,53,98,99,100,101,0,102,103]]]
pvalue_nul = PSTRING_CARRIER (REQUEST_STRING 4) ([45,49,48,46,53,98,99,100,101,0,102,103])
$string_carrier_valid(S_peer_nul,pvalue_nul)
$string_read_allocated_leading(S_peer_nul,pvalue_nul,pvalue_raw) = eps
~$string_read_allocated_value(S_peer_nul,porigin_base,pvalue_nul)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    direct = prefix(direct_program, direct_filename_b64, False).split('def $main() = true\n', 1)[1]
    control = prefix(control_program, control_filename_b64).split('def $main() = true\n', 1)[1]
    control = control.replace('$origin_child((porigin_left),', '$origin_child((porigin_nn),')
    old = 'expression_left = NExprBinaryOpCoalesce expression_selected expression_outer_skipped metadata_left'
    assert control.count(old) == 1
    replacement = lines(r'''
expression_left = NExprBinaryOpCoalesce expression_null expression_nn metadata_null_coalesce
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_null)
$origin_child((porigin_left),[PCFIELD 1]) = (porigin_nn)
$origin_node(S_capture.SOURCES,porigin_null) = (expression_null)
$origin_node(S_capture.SOURCES,porigin_nn) = (expression_nn)
expression_nn = NExprBinaryOpCoalesce expression_selected expression_outer_skipped metadata_left
''')
    control = control.replace(old, '\n  -- if '.join(replacement))
    composed = lines(r'''
porigin_null = PORIGIN n_unit pcpath_null
porigin_nn = PORIGIN n_unit pcpath_nn
$compiled_read(S_capture,porigin_null) = (PNULL)
$string_read_runtime_value(S_capture,porigin_null) = (PNULL)
$compiled_precision(S_capture,(porigin_null)) = (14)
$compiled_precision(S_capture,(porigin_nn)) = (14)
$code_expression(pcode.EXPRESSIONS,pcpath_nn) = ((z_nn,false))
$(z_nn > 0)
$compiled_read(S_capture,porigin_nn) = eps
~$string_read_allocated_value(S_capture,porigin_nn,pvalue_left)
$string_read_allocated_base(S_capture,porigin_nn,pvalue_left)
$string_read_allocated_base(S_capture,porigin_left,pvalue_left)
$string_read_allocated_value(S_capture,porigin_base,pvalue_base)
expression_outer_skipped = NExprTernary expression_unused_condition expression_unused_true expression_unused_false metadata_unused
$origin_child((porigin_outer_skipped),[PCFIELD 0]) = (porigin_unused_condition)
$origin_child((porigin_unused_condition),[PCFIELD 0]) = (porigin_unused_atom)
porigin_unused_atom = PORIGIN n_unit pcpath_unused_atom
$origin_node(S_capture.SOURCES,porigin_unused_atom) = (NScalarInt (INTEGER 1) metadata_unused_atom)
S_peer_null_descendant = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_unused_atom (NScalarInt (INTEGER 1) eps)) :: pcunit.OCCURRENCES]]]
$string_read_allocated_base(S_peer_null_descendant,porigin_nn,pvalue_left)
~$string_read_allocated_base(S_peer_null_descendant,porigin_left,pvalue_left)
~$string_read_allocated_value(S_peer_null_descendant,porigin_base,pvalue_base)
''')
    control += ''.join('  -- if ' + check + '\n' for check in composed)
    extra = 'dec $peer_direct_original() : bool\ndef $peer_direct_original() = true\n' + direct
    extra += '\ndec $peer_null_left() : bool\ndef $peer_null_left() = true\n' + control
    body = body.replace('dec $main() : bool', extra + '\ndec $main() : bool')
    body += '  -- if $peer_direct_original()\n  -- if $peer_null_left()\n'
    main = body.split('def $main() = true\n', 1)[1]
    return body, len(main.splitlines()) + len(direct.splitlines()) + len(control.splitlines()), len(checks) + len(composed)
