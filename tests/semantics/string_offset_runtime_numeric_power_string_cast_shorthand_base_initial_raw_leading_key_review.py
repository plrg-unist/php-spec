"""A quiet completed emitted FLOAT power selects the recursive string-cast fallback."""

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
expression_cond = NExprBinaryOpPow expression_cond_leaf expression_cond_right metadata_cond
expression_cond_leaf = NExprCastDouble expression_cond_inner metadata_cond_leaf
expression_cond_inner = NScalarInt (INTEGER 0) metadata_cond_inner
expression_cond_right = NScalarInt (INTEGER 1) metadata_cond_right
expression_right = NExprCastString expression_inner metadata_right
expression_inner = NExprCastString expression_leaf metadata_inner
expression_leaf = NScalarString (BYTES text_leaf) metadata_leaf
$base64(text_leaf) = $ptascii("b")
$origin_child((porigin_base),[PCFIELD 0]) = (porigin_cond)
$origin_child((porigin_cond),[PCFIELD 0]) = (porigin_cond_leaf)
$origin_child((porigin_cond),[PCFIELD 1]) = (porigin_cond_right)
$origin_child((porigin_cond_leaf),[PCFIELD 0]) = (porigin_cond_inner)
$origin_child((porigin_base),[PCFIELD 2]) = (porigin_right)
$origin_child((porigin_right),[PCFIELD 0]) = (porigin_inner)
$origin_child((porigin_inner),[PCFIELD 0]) = (porigin_leaf)
$compiled_read(S_capture,porigin_cond) = eps
$compiled_read(S_capture,porigin_cond_leaf) = eps
$compiled_read(S_capture,porigin_cond_inner) = (PINT 0)
$compiled_read(S_capture,porigin_cond_right) = (PINT 1)
$string_read_runtime_value(S_capture,porigin_cond_right) = (PINT 1)
$string_read_runtime_value(S_capture,porigin_cond_leaf) = (PFLOAT 0)
$power_prepare(NFLOAT 0,NINT 1) = POWERDONE (NFLOAT 0) false
$binary_apply(S_capture,POWER,PFLOAT 0,PINT 1,12) = S_capture[.RESULT = KNOWN (PFLOAT 0)]
$string_read_runtime_value(S_capture,porigin_cond) = (PFLOAT 0)
$truth_value(S_capture,PFLOAT 0,12) = S_capture[.RESULT = KNOWN (PBOOL false)]
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
S_budget_numeric_power_cast = S_capture[.COMPLETION = BUDGET][.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("X")))]
$string_read_runtime_value(S_budget_numeric_power_cast,porigin_base) = eps
$string_read_raw_known_base(S_budget_numeric_power_cast,porigin_base,pkeyread.BASE)
~$string_read_raw_known_base(S_budget_numeric_power_cast,porigin_base,PSTRING_CARRIER INTERNED_STRING ($ptascii("X")))
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
            name = f'S_bad_numeric_power_cast_{label}_{kind}'
            checks += [f'{name} = S_capture[{update}]',
                       f'$string_read_runtime_value({name},porigin_base) = eps',
                       f'~$string_read_raw_known_base({name},porigin_base,pkeyread.BASE)']
        if label in ('cond_inner', 'cond_right', 'leaf'):
            checks += [f'S_zero_line_numeric_power_cast_{label} = S_capture[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_{label} 0 true) :: pcode.EXPRESSIONS]]]',
                       f'$string_read_runtime_value(S_zero_line_numeric_power_cast_{label},porigin_base) = (pkeyread.BASE)',
                       f'$string_read_raw_known_base(S_zero_line_numeric_power_cast_{label},porigin_base,pkeyread.BASE)']
        if label == 'base':
            continue
        node = {'cond':'NExprBinaryOpPow expression_cond_leaf expression_cond_right eps',
                'cond_leaf':'NExprCastDouble expression_cond_inner eps',
                'cond_inner':'NScalarInt (INTEGER 0) eps',
                'cond_right':'NScalarInt (INTEGER 1) eps',
                'right':'NExprCastString expression_inner eps',
                'inner':'NExprCastString expression_leaf eps',
                'leaf':'NScalarString (BYTES text_leaf) eps'}[label]
        checks += [f'S_bad_numeric_power_cast_{label}_source = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_{label} ({node})) :: pcunit.OCCURRENCES]]]',
                   f'~$string_read_raw_known_base(S_bad_numeric_power_cast_{label}_source,porigin_base,pkeyread.BASE)']
    for label, value in (('bytes', 'PSTRING ($ptascii("X"))'), ('type', 'PINT 98'),
                         ('header', 'PSTRING_CARRIER (REQUEST_STRING 0) ($ptascii("b"))')):
        checks += [f'S_bad_numeric_power_cast_leaf_{label} = S_capture[.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_leaf ({value})) :: ppool.CONSTANTS]]]',
                   f'$string_read_runtime_value(S_bad_numeric_power_cast_leaf_{label},porigin_base) = eps',
                   f'~$string_read_raw_known_base(S_bad_numeric_power_cast_leaf_{label},porigin_base,pkeyread.BASE)']
    checks += lines(r'''
S_budget_forged_numeric_power_cast = S_bad_numeric_power_cast_leaf_bytes[.COMPLETION = BUDGET][.RESULT = KNOWN pkeyread.BASE]
~$string_read_raw_known_base(S_budget_forged_numeric_power_cast,porigin_base,pkeyread.BASE)
''')

    checks += lines(r'''
expression_zero_right = NScalarInt (INTEGER 0) metadata_cond_right
expression_zero_cond = NExprBinaryOpPow expression_cond_leaf expression_zero_right metadata_cond
expression_zero_base = NExprTernary expression_zero_cond ABSENT expression_right metadata
S_zero_exponent = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_zero_base) :: (PCOCCURRENCE pcpath_cond expression_zero_cond) :: (PCOCCURRENCE pcpath_cond_right expression_zero_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond_right (PINT 0)) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_zero_exponent,porigin_cond_right) = (PINT 0)
$power_prepare(NFLOAT 0,NINT 0) = POWERDONE (NFLOAT 4607182418800017408) false
$string_read_runtime_value(S_zero_exponent,porigin_cond) = (PFLOAT 4607182418800017408)
$string_read_runtime_value(S_zero_exponent,porigin_base) = (PFLOAT 4607182418800017408)
~$string_read_raw_known_base(S_zero_exponent,porigin_base,pkeyread.BASE)
S_skip_power = S_zero_exponent[.CODE = [pcode[.EXPRESSIONS = (CODEEXPR pcpath_right 0 false) :: pcode.EXPRESSIONS]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond_right (PINT 0)) :: (PCCPRECISION pcpath_right 17) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_skip_power,porigin_right) = eps
$string_read_runtime_value(S_skip_power,porigin_base) = (PFLOAT 4607182418800017408)
~$string_read_raw_known_base(S_skip_power,porigin_base,pkeyread.BASE)
expression_negative_right = NScalarInt (INTEGER (-1)) metadata_cond_right
expression_negative_cond = NExprBinaryOpPow expression_cond_leaf expression_negative_right metadata_cond
expression_negative_base = NExprTernary expression_negative_cond ABSENT expression_right metadata
S_negative_exponent = S_capture[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_base expression_negative_base) :: (PCOCCURRENCE pcpath_cond expression_negative_cond) :: (PCOCCURRENCE pcpath_cond_right expression_negative_right) :: pcunit.OCCURRENCES]]][.POOLS = [ppool[.CONSTANTS = (PCONSTANT pcpath_cond_right (PINT (-1))) :: ppool.CONSTANTS]]]
$string_read_runtime_value(S_negative_exponent,porigin_cond_right) = (PINT (-1))
$power_prepare(NFLOAT 0,NINT (-1)) = POWERDONE (NFLOAT 9218868437227405312) true
$string_read_runtime_value(S_negative_exponent,porigin_cond) = eps
$string_read_runtime_value(S_negative_exponent,porigin_base) = eps
~$string_read_raw_known_base(S_negative_exponent,porigin_base,pkeyread.BASE)
S_negative_power_budget = S_negative_exponent[.COMPLETION = BUDGET][.RESULT = KNOWN pkeyread.BASE]
~$string_read_raw_known_base(S_negative_power_budget,porigin_base,pkeyread.BASE)
''')
    body += ''.join('  -- if ' + check + '\n' for check in checks)
    return body, count + len(checks), derived + len(checks)
