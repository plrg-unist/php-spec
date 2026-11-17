"""A quiet emitted integer modulo selects the recursive string-cast fallback."""

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
$origin_node(S_capture.SOURCES,porigin_base) = (NExprTernary expression_cond ABSENT expression_right metadata)
expression_cond = NExprBinaryOpMod expression_cond_leaf expression_cond_right metadata_cond
expression_cond_leaf = NExprCastInt expression_cond_inner metadata_cond_leaf
expression_cond_inner = NExprConstFetch (NName (BYTES text_null) metadata_null) metadata_cond_inner
expression_cond_right = NScalarInt (INTEGER 2) metadata_cond_right
expression_right = NExprCastString expression_inner metadata_right
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_leaf) = $ptascii("b")
$base64(text_null) = $ptascii("null")
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_cond_leaf)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_cond_right)
$origin_child((porigin_cond_leaf),[PCFIELD 0]) = (porigin_cond_inner)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_right)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
$compiled_read(S_capture,porigin_cond) = eps
$compiled_read(S_capture,porigin_cond_leaf) = eps
$compiled_read(S_capture,porigin_cond_inner) = (PNULL)
$compiled_read(S_capture,porigin_cond_right) = (PINT 2)
$string_read_runtime_value(S_capture,porigin_cond_right) = (PINT 2)
$string_read_runtime_value(S_capture,porigin_cond_leaf) = (PINT 0)
$binary_apply(S_capture,MODULO,PINT 0,PINT 2,12) = S_capture[.RESULT = KNOWN (PINT 0)]
$string_read_runtime_value(S_capture,porigin_cond) = (PINT 0)
$truth_value(S_capture,PINT 0,12) = S_capture[.RESULT = KNOWN (PBOOL false)]
$string_read_runtime_value(S_capture,porigin_right) = (pkeyread.BASE)
$string_read_runtime_value(S_capture,porigin_inner) = (pkeyread.BASE)
$compiled_read(S_capture,porigin_leaf) = (PSTRING ($ptascii("b")))
$string_read_raw_known_base(S_capture,porigin_base,pkeyread.BASE)
S_capture.CODE = [pcode]
S_capture.POOLS = [ppool]
S_capture.SOURCES = [pcunit]
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING ($ptascii("b")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("b")))
~$string_read_raw_known_base(S_capture,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("X")))
S_budget_integer_binary_cast = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("X")))]
$string_read_runtime_value(S_budget_integer_binary_cast,porigin_base) = eps
$string_read_raw_known_base(S_budget_integer_binary_cast,porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_budget_integer_binary_cast,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("X")))
''')
    for label in ('base', 'cond', 'cond_leaf', 'cond_inner', 'cond_right', 'right', 'inner', 'leaf'):
        checks.append(f'porigin_{label} = PORIGIN n_unit pcpath_{label}')
        if label != 'base':
            checks.append(f'$origin_node(S_capture.SOURCES,porigin_{label}) = (expression_{label})')
        checks.append(f'$compiled_precision(S_capture,(porigin_{label})) = (14)')
        updates = [('precision', f'.POOLS = [ppool[.CONSTANTS = (PCCPRECISION pcpath_{label} 17) :: ppool.CONSTANTS]]')]
        if label not in ('cond_inner', 'cond_right', 'leaf'):
            checks.append(f'$compiled_read(S_capture,porigin_{label}) = eps')
            updates += [('line', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 false) :: pcode.EXPRESSIONS]]'),
                        ('constant', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 12 true) :: pcode.EXPRESSIONS]]')]
        else:
            updates += [('emitted', f'.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 12 false) :: pcode.EXPRESSIONS]]')]
        for kind, update in updates:
            name = f'S_bad_integer_binary_cast_{label}_{kind}'
            checks += [f'{name} = S_capture[{update}]',
                       f'$string_read_runtime_value({name},porigin_base) = eps',
                       f'~$string_read_raw_known_base({name},porigin_base,pkeyread.BASE)']
        if label in ('cond_inner', 'cond_right', 'leaf'):
            checks += [f'S_zero_line_integer_binary_cast_{label} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 true) :: pcode.EXPRESSIONS]]]',
                       f'$string_read_runtime_value(S_zero_line_integer_binary_cast_{label},porigin_base) = (pkeyread.BASE)',
                       f'$string_read_raw_known_base(S_zero_line_integer_binary_cast_{label},porigin_base,pkeyread.BASE)']
        if label == 'base':
            continue
        node = {'cond':'NExprBinaryOpMod expression_cond_leaf expression_cond_right eps',
                'cond_leaf':'NExprCastInt expression_cond_inner eps',
                'cond_inner':'NExprConstFetch (NName (BYTES text_null) metadata_null) eps',
                'cond_right':'NScalarInt (INTEGER 2) eps',
                'right':'NExprCastString expression_inner eps',
                'inner':'NExprCastString expression_leaf eps',
                'leaf':'NScalarString (BYTES text_leaf) eps'}[label]
        checks += [f'S_bad_integer_binary_cast_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_integer_binary_cast_{label}_source,porigin_base,pkeyread.BASE)']
    for label, value in (('bytes', 'PSTRING ($ptascii("X"))'), ('type', 'PINT 98'),
                         ('header', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("b"))')):
        checks += [f'S_bad_integer_binary_cast_leaf_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_bad_integer_binary_cast_leaf_{label},porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_integer_binary_cast_leaf_{label},porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_budget_forged_integer_binary_cast = S_bad_integer_binary_cast_leaf_bytes[.COMPLETION = BUDGET][.RESULT = KNOWN pkeyread.BASE]
~$string_read_raw_known_base(S_budget_forged_integer_binary_cast,porigin_base,pkeyread.BASE)
''')

    checks += lines(r'''
expression_zero_right = NScalarInt (INTEGER 0) metadata_cond_right
expression_zero_cond = NExprBinaryOpMod expression_cond_leaf expression_zero_right metadata_cond
expression_zero_base = NExprTernary expression_zero_cond ABSENT expression_right metadata
S_zero_mod = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_zero_base) :: (PCOCCURRENCE pcpath_cond expression_zero_cond) :: (PCOCCURRENCE pcpath_cond_right expression_zero_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond_right (PINT 0)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_zero_mod,porigin_cond_right) = (PINT 0)
$string_read_runtime_value(S_zero_mod,porigin_cond) = eps
$string_read_runtime_value(S_zero_mod,porigin_base) = eps
~$string_read_raw_known_base(S_zero_mod,porigin_base,pkeyread.BASE)
S_zero_mod_budget = S_zero_mod[.COMPLETION = BUDGET][.RESULT = KNOWN pkeyread.BASE]
~$string_read_raw_known_base(S_zero_mod_budget,porigin_base,pkeyread.BASE)
''')
    for label, raw, value in (
            ('fractional', 'NScalarFloat (FLOAT "3ff8000000000000") metadata_cond_right', 'PFLOAT 4609434218613702656'),
            ('leading', 'NScalarString (BYTES "Mng=") metadata_cond_right', 'PSTRING ($ptascii("2x"))')):
        checks += [f'expression_{label}_right = {raw}',
                   f'expression_{label}_cond = NExprBinaryOpMod expression_cond_leaf expression_{label}_right metadata_cond',
                   f'expression_{label}_base = NExprTernary expression_{label}_cond ABSENT expression_right metadata',
                   f'S_{label}_mod = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_cond_right expression_{label}_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond_right ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_{label}_mod,porigin_cond_right) = (' + ('PSTRING_CARRIER INTERNED_STRING ($ptascii("2x"))' if label == 'leading' else value) + ')',
                   f'$string_read_runtime_value(S_{label}_mod,porigin_cond) = eps',
                   f'$string_read_runtime_value(S_{label}_mod,porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_{label}_mod,porigin_base,pkeyread.BASE)']
    for label, raw in (('truthy', 'Yg=='), ('falsey', 'MA==')):
        value = '$ptascii("b")' if label == 'truthy' else '$ptascii("0")'
        checks += [f'expression_{label}_left = NScalarString (BYTES "{raw}") metadata_cond_leaf',
                   f'expression_{label}_right = NScalarString (BYTES "{raw}") metadata_cond_right',
                   f'expression_{label}_cond = NExprBinaryOpBitwiseOr expression_{label}_left expression_{label}_right metadata_cond',
                   f'expression_{label}_base = NExprTernary expression_{label}_cond ABSENT expression_right metadata',
                   f'S_{label}_string = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_{label}_base) :: (PCOCCURRENCE pcpath_cond expression_{label}_cond) :: (PCOCCURRENCE pcpath_cond_leaf expression_{label}_left) :: (PCOCCURRENCE pcpath_cond_right expression_{label}_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond_leaf (PSTRING ({value}))) :: (PCONSTANT pcpath_cond_right (PSTRING ({value}))) :: ppool.CONSTANTS]]][.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_cond_leaf 12 true) :: pcode.EXPRESSIONS]]]',
                   f'$string_read_runtime_value(S_{label}_string,porigin_cond) = (PSTRING_CARRIER INTERNED_STRING ({value}))',
                   f'$string_read_runtime_value(S_{label}_string,porigin_base) = (pkeyread.BASE)',
                   f'~$string_read_raw_known_base(S_{label}_string,porigin_base,pkeyread.BASE)']
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
