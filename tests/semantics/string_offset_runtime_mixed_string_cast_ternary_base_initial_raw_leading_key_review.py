"""Mixed arms retain the selected header and leave the skipped raw pool undemanded."""

from string_offset_initial_raw_leading_key_review import render as render_literal
from string_offset_retained_carrier_protocol import lines


def render(program, filename_b64):
    body, count, derived = render_literal(program, filename_b64)
    for old, new in (
            ('$compiled_read(S_capture,porigin_base) = (PSTRING ($ptascii("abc")))', '$compiled_read(S_capture,porigin_base) = eps'),
            ('$compiled_string_value(S_capture,porigin_base,PSTRING ($ptascii("abc"))) = pkeyread.BASE', '$string_read_runtime_value(S_capture,porigin_base) = (pkeyread.BASE)'),
            ('STRING_LEADING 1}', 'STRING_LEADING 0}'),
            ('$string_read_raw_leading(pkeyread.BASE,pkeyread.VALUE) = (1)', '$string_read_raw_leading(pkeyread.BASE,pkeyread.VALUE) = (0)'),
            ('$string_read_raw_saved(S_capture,pstringread) = (1)', '$string_read_raw_saved(S_capture,pstringread) = (0)'),
            ('$string_read_raw_saved(S,pstringread) = (1)', '$string_read_raw_saved(S,pstringread) = (0)')):
        assert body.count(old) == 1
        body = body.replace(old, new)
    body = body.replace('abc', 'b').replace('1x', '0x').replace('-0x', '-1x')
    checks = lines(r'''
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary expression_cond expression_left expression_right metadata)
expression_cond = NExprCastBool expression_condition_child metadata_cond
expression_condition_child = NScalarInt (INTEGER 1) metadata_condition_child
expression_left = NExprCastString expression_inner metadata_left
expression_inner = NExprCastString expression_child metadata_inner
expression_child = NScalarString (BYTES text_child) metadata_child
expression_right = NScalarString (BYTES text_right) metadata_right
$base64(text_child) = $ptascii("b")
$base64(text_right) = $ptascii("unused")
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_condition_child)
$origin_child((porigin_base),[PCFIELD 1]) = (porigin_left)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_right)
$origin_child((porigin_left),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_child)
$string_read_runtime_value(S_capture,porigin_cond) = (PBOOL true)
$truth_value(S_capture,PBOOL true,12) = S_capture[.RESULT = KNOWN (PBOOL true)]
$string_read_runtime_value(S_capture,porigin_left) = (pkeyread.BASE)
$string_read_runtime_value(S_capture,porigin_inner) = (pkeyread.BASE)
$compiled_read(S_capture,porigin_condition_child) = (PINT 1)
$compiled_read(S_capture,porigin_child) = (PSTRING ($ptascii("b")))
$compiled_read(S_capture,porigin_right) = (PSTRING ($ptascii("unused")))
$string_read_raw_known_base(S_capture,porigin_base,pkeyread.BASE)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("b")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("b")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("X")))
S_budget_mixed = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("X")))]
$string_read_runtime_value(S_budget_mixed,porigin_base) = eps
$string_read_raw_known_base(S_budget_mixed,porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_budget_mixed,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("X")))
''')
    for label in ('base', 'cond', 'condition_child', 'left', 'inner', 'child', 'right'):
        checks.append(f'porigin_{label} = PORIGIN n_unit pcpath_{label}')
        if label != 'base':
            checks.append(f'$origin_node(S_capture.SOURCES,porigin_{label}) = (expression_{label})')
        if label == 'right':
            continue
        checks.append(f'$compiled_precision(S_capture,(porigin_{label})) = (14)')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} 17) :: ppool.CONSTANTS]]')]
        if label not in ('condition_child', 'child'):
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = eps')
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('constant', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 12 true) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            name = f'S_bad_mixed_{label}_{kind}'
            checks += [f'{name} = S_capture[{update}]',
                       f'$string_read_runtime_value({name},porigin_base) = eps',
                       f'~$string_read_raw_known_base({name},porigin_base,pkeyread.BASE)']
    for label, update in (
            ('child_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_child (PSTRING ($ptascii("X")))) :: ppool.CONSTANTS]]'),
            ('child_tag', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_child (PINT 98)) :: ppool.CONSTANTS]]'),
            ('condition_pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_condition_child (PINT 0)) :: ppool.CONSTANTS]]')):
        checks += [f'S_bad_mixed_{label} = S_capture[{update}]',
                   f'$string_read_runtime_value(S_bad_mixed_{label},porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_mixed_{label},porigin_base,pkeyread.BASE)']
    for label, node in (
            ('base', 'NExprBinaryOpConcat expression_left expression_right metadata'),
            ('cond', 'NExprCastBool expression_condition_child eps'),
            ('condition_child', 'NScalarInt (INTEGER 1) eps'),
            ('left', 'NExprCastString expression_inner eps'),
            ('inner', 'NExprCastString expression_child eps'),
            ('child', 'NScalarString (BYTES text_child) eps'),
            ('right', 'NScalarString (BYTES text_right) eps')):
        checks += [f'S_bad_mixed_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_mixed_{label}_source,porigin_base,pkeyread.BASE)']
    for label, update in (
            ('code', '.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 0 false) :: pcode.EXPRESSIONS]]'),
            ('precision', '.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_right 17) :: ppool.CONSTANTS]]'),
            ('pool', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PSTRING ($ptascii("bad")))) :: ppool.CONSTANTS]]'),
            ('header', '.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_right (PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("unused")))) :: ppool.CONSTANTS]]')):
        checks += [f'S_skipped_mixed_{label} = S_capture[{update}]',
                   f'$string_read_runtime_value(S_skipped_mixed_{label},porigin_base) = (pkeyread.BASE)',
                   f'$string_read_raw_known_base(S_skipped_mixed_{label},porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_budget_forged_mixed = S_bad_mixed_child_pool[.COMPLETION = BUDGET][.RESULT = KNOWN pkeyread.BASE]
~$string_read_raw_known_base(S_budget_forged_mixed,porigin_base,pkeyread.BASE)
expression_right_bool = NExprCastBool expression_child metadata_right
expression_bool_root = NExprTernary expression_cond expression_left expression_right_bool metadata
S_right_bool = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_bool_root) :: (PCOCCURRENCE pcpath_right expression_right_bool) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_right_bool,porigin_base) = (pkeyread.BASE)
~$string_read_raw_known_base(S_right_bool,porigin_base,pkeyread.BASE)
expression_short_root = NExprTernary expression_cond ABSENT expression_right metadata
S_short = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_short_root) :: pcunit.OCCURRENCES]]]
$string_read_runtime_value(S_short,porigin_base) = (PBOOL true)
~$string_read_raw_known_base(S_short,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
